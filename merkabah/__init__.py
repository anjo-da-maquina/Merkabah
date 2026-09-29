# 🛡️ Merkabah Core: The Canon (Global Edition)
import sys
import os
import ast
import json
import importlib.util

class LossOfAtaraxia(Exception): pass

# --- 1. The Rubrics ---
rubrics = {"banned_modules": [], "banned_events": []}
if os.path.exists("rubric.json"):
    try:
        with open("rubric.json", "r", encoding="utf-8-sig") as f:
            rubrics.update(json.load(f))
        print("[Merkabah] The Rubrics loaded. Local doctrines applied.")
    except Exception as e:
        print(f"[Merkabah] Failed to read The Rubrics: {e}")

# --- 2. The Canon + Rubrics Integration ---
BANNED_ENV = ["GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI"]
BANNED_MODULES = {"os", "subprocess", "sys", "pty", "shlex"}.union(rubrics.get("banned_modules", []))
BANNED_EVENTS = ['os.system', 'subprocess.Popen', 'os.exec', 'os.spawn'] + rubrics.get("banned_events", [])

def _raphael_environment_seal():
    for env in BANNED_ENV:
        if os.getenv(env):
            raise LossOfAtaraxia(f"[Merkabah] Raphael's Rejection: Polluted environment ({env}) blocked.")

def _gabriel_ast_inquisition(code_string):
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        raise ValueError("[Merkabah] Gabriel's Inquisition: Syntax error. Unreadable intent.")
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in BANNED_MODULES:
                    raise PermissionError(f"[Merkabah] Gabriel's Inquisition: Module '{alias.name}' is forbidden.")
        elif isinstance(node, ast.ImportFrom):
            if node.module in BANNED_MODULES:
                raise PermissionError(f"[Merkabah] Gabriel's Inquisition: Module '{node.module}' is forbidden.")

def _michael_absolute_defense(event, args):
    if event in BANNED_EVENTS:
        raise RuntimeError(f"[Merkabah] Michael's Sword: Unauthorized intent '{event}' physically blocked.")

# --- 3. The Homilies ---
def _listen_to_homilies():
    homilies_dir = "homilies"
    if not os.path.exists(homilies_dir):
        return
    for filename in os.listdir(homilies_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            filepath = os.path.join(homilies_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(f"homilies.{filename[:-3]}", filepath)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "preach"):
                    mod.preach()
            except Exception as e:
                print(f"[Merkabah] Heretical homily discarded ({filename}): {e}")

def awaken():
    _raphael_environment_seal()
    _listen_to_homilies()
    sys.addaudithook(_michael_absolute_defense)
    print("[Merkabah] The Canon is active. Archangels are guarding the OS.")

inquisition = _gabriel_ast_inquisition
awaken()