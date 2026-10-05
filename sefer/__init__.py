import sys
import os
import ast
import warnings
import contextvars
from pathlib import Path
from dataclasses import dataclass
from typing import List, Any

# =========================================================
# CORE EXCEPTION
# =========================================================
class LossOfAtaraxia(BaseException):
    """
    トリップワイヤ発動時の例外。
    except Exception: による握りつぶしを防ぐため BaseException を継承する。
    """
    pass

# =========================================================
# THE SANCTUM: Context-based Guard
# =========================================================
_guard_active = contextvars.ContextVar("sefer_guard_active", default=False)
_policy = contextvars.ContextVar("sefer_policy", default={})

class Sanctum:
    """
    実行を許可する区間（ホワイトリスト境界）を定義する。
    このコンテキストマネージャ内でのみ、厳格な引数検査とデフォルト拒否が発動する。
    """
    def __init__(self, allowed_dirs=None, allowed_hosts=None):
        self.policy = {
            "allowed_dirs": [Path(d).resolve() for d in (allowed_dirs or [])],
            "allowed_hosts": set(allowed_hosts or [])
        }
        self.token_active = None
        self.token_policy = None

    def __enter__(self):
        self.token_active = _guard_active.set(True)
        self.token_policy = _policy.set(self.policy)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _guard_active.reset(self.token_active)
        _policy.reset(self.token_policy)

# =========================================================
# MICHAEL: Audit Hook Tripwire (Default-Deny / Whitelist)
# =========================================================
def _is_path_allowed(target_path, allowed_dirs):
    try:
        target = Path(target_path).resolve()
        return any(target.is_relative_to(d) for d in allowed_dirs)
    except Exception:
        return False

def _michael_absolute_defense(event, args):
    if not _guard_active.get():
        return  # ガード区間外は干渉しない

    policy = _policy.get()
    
    # 絶対拒否イベント（バイパスに利用されやすいもの）
    if event.startswith("shutil.") or event in {"os.fork", "os.posix_spawn", "sys.settrace", "_thread.start_new_thread", "ctypes.dlopen"}:
        raise RuntimeError(f"[Sefer] Tripwire: Hard-denied event '{event}' blocked.")
    if event in {"marshal.loads", "pickle.find_class"}:
        raise RuntimeError(f"[Sefer] Tripwire: Serialization execution '{event}' blocked.")

    # 引数検査付きの許可イベント (open)
    if event == "open":
        path, mode, flags = args
        if isinstance(mode, str) and any(m in mode for m in ("w", "a", "+", "x")):
            if not _is_path_allowed(path, policy["allowed_dirs"]):
                raise RuntimeError(f"[Sefer] Tripwire: Unauthorized write access to '{path}'.")
        return

    # 破壊的操作
    if event in {"os.remove", "os.rmdir", "os.rename"}:
        if not _is_path_allowed(args[0], policy["allowed_dirs"]):
            raise RuntimeError(f"[Sefer] Tripwire: Unauthorized destructive access to '{args[0]}'.")
        return

    # ソケット通信のホワイトリスト検査
    if "socket" in event or event.startswith("socket"):
        target_host = None
        for arg in args:
            if isinstance(arg, tuple) and len(arg) >= 1 and isinstance(arg[0], str):
                target_host = arg[0]
                break
            elif isinstance(arg, str) and ("." in arg or ":" in arg):
                target_host = arg
                break
        
        allowed = policy.get("allowed_hosts", set())
        if target_host and target_host not in allowed:
            raise RuntimeError(f"[Sefer] Tripwire: Unauthorized network connection to '{target_host}'.")
        return

# =========================================================
# RAPHAEL: Environment Monitor
# =========================================================
def _raphael_environment_seal():
    if sys.gettrace() is not None:
        warnings.warn("[Sefer] Raphael's Warning: Debugger attached.")

# =========================================================
# GABRIEL: AST Linter (Static Analysis Auxiliary Aid)
# =========================================================
@dataclass
class Finding:
    rule_id: str
    severity: str  # "low", "medium", "high", "critical"
    lineno: int
    message: str

def inquisition(source_code: str, context: dict = None) -> List[Finding]:
    """
    Gabriel Linter (Static Analysis Auxiliary Aid).
    静的検査は補助であり、本命はランタイムと隔離による二層防御である。
    例外を投げず、重大度付きの Finding リストを返す。
    """
    findings: List[Finding] = []

    if not isinstance(source_code, str):
        return [Finding("GAB-001", "critical", 0, "Invalid input type for static analysis.")]
    
    if len(source_code) > 1_000_000:
        return [Finding("GAB-002", "critical", 0, "Input payload exceeds maximum allowable size.")]

    try:
        tree = ast.parse(source_code)
    except (SyntaxError, RecursionError, MemoryError) as e:
        return [Finding("GAB-003", "critical", 0, f"AST parsing failed: {type(e).__name__}")]

    forbidden_modules = {"pickle", "ctypes", "importlib", "socket", "urllib", "requests", "http"}
    forbidden_funcs = {"__import__", "getattr", "eval", "exec", "compile"}
    dunder_chains = {"__class__", "__subclasses__", "__globals__", "__builtins__"}

    for node in ast.walk(tree):
        lineno = getattr(node, 'lineno', 0)

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                findings.append(Finding("GAB-101", "high", lineno, "Relative imports are strictly forbidden."))
            
            base_module = node.module if isinstance(node, ast.ImportFrom) else ""
            for alias in node.names:
                full_name = f"{base_module}.{alias.name}" if base_module else alias.name
                if any(f in full_name for f in forbidden_modules):
                    findings.append(Finding("GAB-102", "high", lineno, f"Forbidden module or prefix detected: '{full_name}'"))

        elif isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in forbidden_funcs:
                findings.append(Finding("GAB-201", "critical", lineno, f"Forbidden function invocation: '{func_name}'"))

        elif isinstance(node, ast.Attribute):
            if node.attr in dunder_chains:
                findings.append(Finding("GAB-301", "high", lineno, f"Suspicious dunder attribute access: '{node.attr}'"))

        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            def _is_str_constant(n):
                return isinstance(n, ast.Constant) and isinstance(n.value, str)
            if _is_str_constant(node.left) and _is_str_constant(node.right):
                combined = node.left.value + node.right.value
                if any(w in combined for w in ("eval", "exec", "system", "popen", "ctypes")):
                    findings.append(Finding("GAB-401", "medium", lineno, "Suspicious constant string concatenation detected."))

    return findings

# =========================================================
# THE AWAKENING
# =========================================================
def _create_awaken():
    _awakened = False
    def awaken():
        nonlocal _awakened
        if _awakened:
            return
        _raphael_environment_seal()
        sys.addaudithook(_michael_absolute_defense)
        _awakened = True
    return awaken

awaken = _create_awaken()
