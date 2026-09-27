# 🛡️ Merkabah Core: The Canon (正典)
import sys
import os
import ast
import json
import importlib.util

class LossOfAtaraxia(Exception): pass

# --- 1. The Rubrics (朱書) の読み込み ---
rubrics = {"banned_modules": [], "banned_events": []}
if os.path.exists("rubric.json"):
    try:
        # Windows特有のBOMを自動浄化して読み込む
        with open("rubric.json", "r", encoding="utf-8-sig") as f:
            rubrics.update(json.load(f))
        print("[Merkabah] The Rubrics (朱書) is loaded. Local doctrines applied.")
    except Exception as e:
        print(f"[Merkabah] Failed to read The Rubrics: {e}")

# --- 2. 正典の絶対戒律 + 朱書の統合 ---
BANNED_ENV = ["GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI"]
BANNED_MODULES = {"os", "subprocess", "sys", "pty", "shlex"}.union(rubrics.get("banned_modules", []))
BANNED_EVENTS = ['os.system', 'subprocess.Popen', 'os.exec', 'os.spawn'] + rubrics.get("banned_events", [])

def _raphael_environment_seal():
    for env in BANNED_ENV:
        if os.getenv(env):
            raise LossOfAtaraxia(f"[Merkabah] ラファエルの拒絶: 汚染環境 ({env}) を遮断。")

def _gabriel_ast_inquisition(code_string):
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        raise ValueError("[Merkabah] ガブリエルの審問: 構文エラーにつき解読不能。拒否します。")
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in BANNED_MODULES:
                    raise PermissionError(f"[Merkabah] ガブリエルの審問: 禁忌 '{alias.name}' は朱書により禁じられています。")
        elif isinstance(node, ast.ImportFrom):
            if node.module in BANNED_MODULES:
                raise PermissionError(f"[Merkabah] ガブリエルの審問: 禁忌 '{node.module}' は朱書により禁じられています。")

def _michael_absolute_defense(event, args):
    if event in BANNED_EVENTS:
        raise RuntimeError(f"[Merkabah] ミカエルの剣: 不正な意図 '{event}' を物理遮断します。")

# --- 3. The Homilies (講話) の読み込み ---
def _listen_to_homilies():
    """ユーザー独自の拡張検閲プログラム (MOD) の実行"""
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
                    mod.preach() # 講話（カスタム処理）の実行
            except Exception as e:
                print(f"[Merkabah] 異端の講話を破棄しました ({filename}): {e}")

def awaken():
    _raphael_environment_seal()
    _listen_to_homilies()
    sys.addaudithook(_michael_absolute_defense)
    print("[Merkabah] The Canon (正典) is fully active with local doctrines.")

inquisition = _gabriel_ast_inquisition
awaken()