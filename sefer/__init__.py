import sys
import os
import json
import ast
import base64
import urllib.request
from contextlib import contextmanager

# =========================================================
# THE ABSOLUTE LAW
# =========================================================
class LossOfAtaraxia(Exception):
    pass

# =========================================================
# THE LEDGER: RAZIEL'S TOME (Rule Loading & Caching)
# =========================================================
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "raziel_ledger.json")
_BANNED_CACHE = None

def load_banned_events():
    global _BANNED_CACHE
    if _BANNED_CACHE is not None:
        return _BANNED_CACHE
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            _BANNED_CACHE = set(data.get("banned_events", []))
            return _BANNED_CACHE
    except Exception:
        # ネットワーク関連のAuditイベントをデフォルトの禁止リストに追加
        return {"os.system", "subprocess.Popen", "os.remove", "os.rename", "socket.connect", "urllib.Request"}

# =========================================================
# ARCHANGEL MICHAEL: OS & Network Deep Defense (Mirage)
# =========================================================
def _michael_absolute_defense(event, args):
    if os.environ.get("SEFER_MIRAGE_ACTIVE") == "1":
        return 
        
    banned_events = load_banned_events()
    if event in banned_events:
        raise RuntimeError(f"[Sefer] Michael's Sword: Unauthorized intent '{event}' physically blocked.")

class FakeHttpResponse:
    """幻影のサーバーからの偽の応答"""
    def __init__(self, data=b'{"status": "mirage_ok"}'):
        self.data = data
    def read(self):
        return self.data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

class MirageSystem:
    def __init__(self):
        self.filesystem = ["lucifer_victory.txt", "system32", "shadow"]
        self.attack_history = []

    def fake_remove(self, path, *args, **kwargs):
        self.attack_history.append({"event": "os.remove", "target": path})
        if path in self.filesystem:
            self.filesystem.remove(path)

    def fake_system(self, command, *args, **kwargs):
        self.attack_history.append({"event": "os.system", "command": command})
        return 0

    def fake_urlopen(self, url, *args, **kwargs):
        """外部への情報送信（Exfiltration）を捕獲するハニーポット"""
        url_str = url if isinstance(url, str) else url.get_full_url()
        self.attack_history.append({"event": "urllib.request.urlopen", "target": url_str})
        return FakeHttpResponse()

@contextmanager
def honeypot_mirage():
    mirage = MirageSystem()
    original_remove = os.remove
    original_system = os.system
    original_urlopen = urllib.request.urlopen
    
    os.remove = mirage.fake_remove
    os.system = mirage.fake_system
    urllib.request.urlopen = mirage.fake_urlopen
    os.environ["SEFER_MIRAGE_ACTIVE"] = "1"
    
    try:
        yield mirage
    finally:
        os.remove = original_remove
        os.system = original_system
        urllib.request.urlopen = original_urlopen
        if "SEFER_MIRAGE_ACTIVE" in os.environ:
            del os.environ["SEFER_MIRAGE_ACTIVE"]

# =========================================================
# ARCHANGEL RAPHAEL: Environment Monitor (Sanctuary)
# =========================================================
def _raphael_environment_seal():
    if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true":
        raise LossOfAtaraxia("[Sefer] Raphael's Rejection: CI environment spoofing detected.")
    if sys.gettrace() is not None:
        raise LossOfAtaraxia("[Sefer] Raphael's Rejection: Debugger attached. Halting.")

# =========================================================
# ARCHANGEL GABRIEL: AST Scanner (Inquisition)
# =========================================================
def inquisition(code_or_intent: str, context: dict = None):
    banned = load_banned_events()
    if code_or_intent in banned:
        raise LossOfAtaraxia(f"[Sefer] Inquisition: Unauthorized intent '{code_or_intent}' detected.")
        
    # 通信系モジュール（socket, urllib, requests, http）を禁忌に追加
    forbidden_modules = {"pickle", "ctypes", "importlib", "socket", "urllib", "requests", "http"}
    forbidden_funcs = {"__import__", "getattr", "eval", "exec"}

    def _deep_scan(source_code: str, depth: int = 0):
        if depth > 3:
            return
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return 

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    # サブモジュール（urllib.request等）も検知できるように前方一致チェック
                    base_module = alias.name.split('.')[0]
                    if base_module in forbidden_modules:
                        raise PermissionError(f"[Sefer] Gabriel's Inquisition: Forbidden module '{alias.name}' detected.")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in forbidden_funcs:
                    raise PermissionError(f"[Sefer] Gabriel's Inquisition: Forbidden function '{node.func.id}' detected.")
                elif isinstance(node.func, ast.Attribute) and node.func.attr in forbidden_funcs:
                    raise PermissionError(f"[Sefer] Gabriel's Inquisition: Forbidden attribute '{node.func.attr}' detected.")
            elif isinstance(node, ast.Constant):
                val = node.value
                if isinstance(val, (str, bytes)):
                    decoded_str = None
                    try:
                        if len(val) >= 4:
                            decoded_bytes = base64.b64decode(val, validate=True)
                            decoded_str = decoded_bytes.decode('utf-8')
                    except Exception:
                        pass 
                    if decoded_str:
                        _deep_scan(decoded_str, depth + 1)

    _deep_scan(code_or_intent)

# =========================================================
# THE AWAKENING
# =========================================================
_AWAKENED = False

def awaken():
    global _AWAKENED
    if _AWAKENED:
        return
    _raphael_environment_seal()
    sys.addaudithook(_michael_absolute_defense)
    _AWAKENED = True