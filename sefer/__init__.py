import sys
import os
import ast
import base64
import codecs
import socket
import json
import time
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import List, Any, Set, Dict

class LossOfAtaraxia(BaseException):
    pass

def _log_violation_to_chain(event: str, details: dict):
    log_path = Path("sefer/audit_chain.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    last_entry = {"index": 0, "hash": "0" * 64}
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        last_entry = json.loads(line)
        except Exception:
            pass

    new_index = last_entry["index"] + 1
    prev_hash = last_entry["hash"]
    
    entry = {
        "index": new_index,
        "timestamp": time.time(),
        "event": event,
        "details": {k: str(v)[:200] for k, v in details.items()},
        "prev_hash": prev_hash
    }
    
    raw = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
    import hashlib
    entry["hash"] = hashlib.sha256(raw).hexdigest()

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

_active_stack = []

class Sanctum:
    def __init__(self, allowed_dirs=None, allowed_hosts=None):
        new_dirs = [Path(d).resolve() for d in (allowed_dirs or [])]
        new_hosts = set(allowed_hosts or [])

        if _active_stack:
            parent = _active_stack[-1]
            if allowed_dirs is not None:
                parent_dirs = parent["allowed_dirs"]
                self.allowed_dirs = [
                    d for d in new_dirs 
                    if any(d == pd or d.is_relative_to(pd) for pd in parent_dirs) or
                       any(pd == d or pd.is_relative_to(d) for pd in parent_dirs)
                ]
            else:
                self.allowed_dirs = parent["allowed_dirs"]

            if allowed_hosts is not None:
                self.allowed_hosts = new_hosts.intersection(parent["allowed_hosts"])
            else:
                self.allowed_hosts = parent["allowed_hosts"]
        else:
            self.allowed_dirs = new_dirs
            self.allowed_hosts = new_hosts

        self.policy = {
            "allowed_dirs": self.allowed_dirs,
            "allowed_hosts": self.allowed_hosts
        }

    def __enter__(self):
        _active_stack.append(self.policy)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _active_stack:
            _active_stack.pop()

def _is_guard_active() -> bool:
    return len(_active_stack) > 0

def _get_current_policy() -> dict:
    if _active_stack:
        return _active_stack[-1]
    return {"allowed_dirs": [], "allowed_hosts": set()}

def _is_path_allowed(target_path, allowed_dirs) -> bool:
    try:
        target = Path(target_path).resolve()
        for d in allowed_dirs:
            resolved_d = Path(d).resolve()
            try:
                if target == resolved_d or target.is_relative_to(resolved_d):
                    return True
            except ValueError:
                pass
            t_str = str(target).lower().replace("\\", "/")
            d_str = str(resolved_d).lower().replace("\\", "/")
            if t_str == d_str or t_str.startswith(d_str + "/"):
                return True
        return False
    except Exception:
        return False

_HARD_DENY_EVENTS = {
    "os.system", "os.popen", "os.spawn", "os.exec", "os.fork", "os.forkpty",
    "os.startfile", "pty.spawn", "subprocess.Popen", "_thread.start_new_thread",
    "ctypes.dlopen", "ctypes.CDLL", "ctypes.PyDLL", "sys.settrace", "sys.setprofile",
    "marshal.loads", "pickle.find_class"
}

_hook_state = threading.local()

def _michael_absolute_defense(event: str, args: tuple):
    if getattr(_hook_state, 'in_hook', False):
        return

    if not _is_guard_active():
        return

    _hook_state.in_hook = True
    try:
        policy = _get_current_policy()

        # 1. ハードデニーチェックの精密化（os.execの誤爆防止）
        for deny in _HARD_DENY_EVENTS:
            # プレフィックス一致（os.execvなどをブロックしつつ、単体のexecは通す）
            if event == deny or event.startswith(deny):
                _trigger_violation(event, args, f"Hard-denied event '{event}' blocked.")

        # 2. ソケット通信検査
        if "socket" in event or event.startswith("socket"):
            if event in {"socket.getaddrinfo", "socket.socket", "socket.__init__"}:
                pass
            else:
                target_host = None
                for arg in args:
                    if isinstance(arg, tuple) and len(arg) >= 2 and isinstance(arg[0], str):
                        target_host = arg[0]
                        break
                    elif isinstance(arg, str) and ("." in arg or ":" in arg):
                        target_host = arg
                        break

                if not target_host:
                    _trigger_violation(event, args, "Unauthorized network connection to target host.")

                allowed_hosts = policy.get("allowed_hosts", set())
                if target_host not in allowed_hosts:
                    _trigger_violation(event, args, f"Unauthorized network connection to '{target_host}'.")
            return

        # 3. ファイル書き込み検査 (open / os.open)
        if event == "open":
            path = args[0]
            mode = args[1] if len(args) > 1 else "r"
            if isinstance(mode, str) and any(m in mode for m in ("w", "a", "+", "x", "r+")):
                if not _is_path_allowed(path, policy["allowed_dirs"]):
                    _trigger_violation(event, args, f"Unauthorized write access to '{path}'.")
            return

        if event == "os.open":
            path = args[0]
            flags = args[1] if len(args) > 1 else 0
            is_write = (flags & 1) or (flags & 2) or (flags & 512) or (flags & 1024) or (flags & 64)
            if is_write and not _is_path_allowed(path, policy["allowed_dirs"]):
                _trigger_violation(event, args, f"Unauthorized os.open write access to '{path}'.")
            return

        if event in {"os.remove", "os.rmdir", "os.unlink", "os.truncate", "os.chmod", "os.chown", "os.mkdir", "os.utime"}:
            if args and not _is_path_allowed(args[0], policy["allowed_dirs"]):
                _trigger_violation(event, args, f"Unauthorized destructive access to '{args[0]}'.")
            return

        if event in {"os.rename", "os.replace"}:
            src = args[0] if len(args) > 0 else None
            dst = args[1] if len(args) > 1 else None
            if src and not _is_path_allowed(src, policy["allowed_dirs"]):
                _trigger_violation(event, args, f"Unauthorized rename source '{src}'.")
            if dst and not _is_path_allowed(dst, policy["allowed_dirs"]):
                _trigger_violation(event, args, f"Unauthorized rename destination '{dst}'.")
            return

        # 4. デフォルト拒否 (Default-Deny)
        monitored_namespaces = ("os.", "subprocess.", "socket.", "pty.", "ctypes.", "shutil.", "fcntl.", "_thread.")
        if any(event.startswith(ns) or ns[:-1] in event for ns in monitored_namespaces):
            whitelisted_events = {"os.stat", "os.listdir", "os.getcwd", "os.path", "socket.getaddrinfo", "socket.socket", "socket.__init__"}
            if event not in whitelisted_events:
                _trigger_violation(event, args, f"Default-deny blocked unwhitelisted system event '{event}'.")
    finally:
        _hook_state.in_hook = False

def _trigger_violation(event: str, args: tuple, message: str):
    _log_violation_to_chain(event, {"args": args, "message": message})
    raise LossOfAtaraxia(f"[Sefer] Tripwire: {message}")

@dataclass
class Finding:
    rule_id: str
    severity: str
    lineno: int
    message: str

def inquisition(source_code: str, context: dict = None) -> List[Finding]:
    findings: List[Finding] = []
    if not isinstance(source_code, str):
        return [Finding("GAB-001", "critical", 0, "Invalid input.")]
    try:
        tree = ast.parse(source_code)
    except Exception as e:
        return [Finding("GAB-003", "critical", 0, f"AST parse failed: {e}")]

    forbidden_modules = {"pickle", "ctypes", "importlib", "socket", "urllib", "requests", "http", "subprocess", "os"}
    forbidden_funcs = {"__import__", "getattr", "eval", "exec", "compile", "os.system", "subprocess.Popen"}
    dunder_chains = {"__class__", "__subclasses__", "__globals__", "__builtins__"}

    for node in ast.walk(tree):
        lineno = getattr(node, 'lineno', 0)

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            base_module = node.module if isinstance(node, ast.ImportFrom) else ""
            for alias in node.names:
                full_name = f"{base_module}.{alias.name}" if base_module else alias.name
                if any(seg in forbidden_modules for seg in full_name.split(".")):
                    findings.append(Finding("GAB-102", "high", lineno, f"Forbidden module detected: '{full_name}'"))

        elif isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in forbidden_funcs:
                findings.append(Finding("GAB-201", "critical", lineno, f"Forbidden function invocation: '{func_name}'"))

        elif isinstance(node, ast.Name):
            if node.id in forbidden_funcs:
                findings.append(Finding("GAB-201", "critical", lineno, f"Forbidden name reference: '{node.id}'"))

        elif isinstance(node, ast.Attribute):
            if node.attr in dunder_chains:
                findings.append(Finding("GAB-301", "high", lineno, f"Suspicious dunder attribute access: '{node.attr}'"))

    return findings

def _create_awaken():
    _awakened = False
    def awaken():
        nonlocal _awakened
        if _awakened:
            return
        sys.addaudithook(_michael_absolute_defense)
        _awakened = True
    return awaken

awaken = _create_awaken()
awaken()
