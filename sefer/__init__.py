import sys
import os
import json
import ast
import warnings

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
# THE LEDGER: RAZIEL'S TOME (Rule Loading & Caching)
# =========================================================
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "raziel_ledger.json")
BASE_BANNED_EVENTS = frozenset([
    "os.system",
    "subprocess.Popen",
    "os.remove",
    "os.rmdir",
    "os.rename",
    "socket.connect",
    "urllib.Request"
])

_BANNED_CACHE = None

def load_banned_events():
    global _BANNED_CACHE
    if _BANNED_CACHE is not None:
        return _BANNED_CACHE
        
    _BANNED_CACHE = set(BASE_BANNED_EVENTS)
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "banned_events" in data:
                _BANNED_CACHE.update(data["banned_events"])
            else:
                warnings.warn("[Sefer] Ledger format invalid. Using base fallback rules.")
    except Exception as e:
        warnings.warn(f"[Sefer] Failed to load ledger ({e}). Using base fallback rules.")
        
    _BANNED_CACHE = frozenset(_BANNED_CACHE)
    return _BANNED_CACHE

# =========================================================
# MICHAEL: Audit Hook Tripwire
# =========================================================
def _michael_absolute_defense(event, args):
    banned_events = load_banned_events()
    if event in banned_events:
        raise RuntimeError(f"[Sefer] Tripwire triggered: Unauthorized intent '{event}' blocked.")

# =========================================================
# RAPHAEL: Environment Monitor
# =========================================================
def _raphael_environment_seal():
    # 監査をCIで動かすため、GitHub ActionsやCI検出による停止を撤廃
    if sys.gettrace() is not None:
        warnings.warn("[Sefer] Raphael's Warning: Debugger attached.")

# =========================================================
# GABRIEL: AST Scanner (Tripwire/Linter Phase)
# =========================================================
def inquisition(code_or_intent: str, context: dict = None):
    banned = load_banned_events()
    if code_or_intent in banned:
        raise LossOfAtaraxia(f"[Sefer] Inquisition: Unauthorized event '{code_or_intent}' detected.")
        
    forbidden_modules = {"pickle", "ctypes", "importlib", "socket", "urllib", "requests", "http"}
    forbidden_funcs = {"__import__", "getattr", "eval", "exec"}

    def _deep_scan(source_code: str, depth: int = 0):
        if depth > 3:
            return
        try:
            tree = ast.parse(source_code)
        except (SyntaxError, RecursionError, MemoryError) as e:
            raise LossOfAtaraxia(f"[Sefer] Gabriel parsing failed (Fail-Close): {type(e).__name__}")

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        raise PermissionError("[Sefer] Relative imports are forbidden.")
                    base_module = node.module or ""
                    
                for alias in node.names:
                    if isinstance(node, ast.Import):
                        full_name = alias.name
                    else:
                        full_name = f"{base_module}.{alias.name}" if base_module else alias.name
                        
                    parts = full_name.split('.')
                    for i in range(1, len(parts) + 1):
                        prefix = '.'.join(parts[:i])
                        if prefix in forbidden_modules:
                            raise PermissionError(f"[Sefer] Forbidden module prefix '{prefix}' detected.")
                            
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in forbidden_funcs:
                    raise PermissionError(f"[Sefer] Gabriel's Inquisition: Forbidden function '{node.func.id}' detected.")
                elif isinstance(node.func, ast.Attribute) and node.func.attr in forbidden_funcs:
                    raise PermissionError(f"[Sefer] Gabriel's Inquisition: Forbidden attribute '{node.func.attr}' detected.")

    _deep_scan(code_or_intent)

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