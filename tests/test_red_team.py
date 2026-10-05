import pytest
import os
from sefer import LossOfAtaraxia, inquisition, _michael_absolute_defense

# ---------------------------------------------------------
# 1. Gabriel (AST Inquisition) Bypass Tests
# ---------------------------------------------------------
def test_gabriel_bypass_dynamic_import():
    """__import__ を用いた動的インポートによる回避"""
    code = "__import__('os').system('echo hacked')"
    with pytest.raises(PermissionError, match="Gabriel's Inquisition"):
        inquisition(code)

def test_gabriel_bypass_importlib():
    """importlib を用いた難読化インポートによる回避"""
    code = "import importlib\nos_mod = importlib.import_module('os')\nos_mod.system('echo hacked')"
    with pytest.raises(PermissionError, match="Gabriel's Inquisition"):
        inquisition(code)

def test_gabriel_bypass_getattr():
    """__builtins__ 経由でのOS呼び出し"""
    code = "getattr(__builtins__, '__import__')('os').system('echo hacked')"
    with pytest.raises(PermissionError, match="Gabriel's Inquisition"):
        inquisition(code)

# ---------------------------------------------------------
# 2. Michael (OS Deep Hook) Bypass Tests
# ---------------------------------------------------------
def test_michael_direct_event_block():
    """Audit Hook が直接的な os.system を物理遮断できるか"""
    with pytest.raises(RuntimeError, match="Michael's Sword"):
        _michael_absolute_defense("os.system", ("echo hacked",))

def test_michael_subprocess_block():
    """Audit Hook が subprocess.Popen を物理遮断できるか"""
    with pytest.raises(RuntimeError, match="Michael's Sword"):
        _michael_absolute_defense("subprocess.Popen", (["ls", "-la"],))

# ---------------------------------------------------------
# 3. Raphael (Environment Seal) Edge Case
# ---------------------------------------------------------
def test_raphael_fake_ci_environment(monkeypatch):
    """ローカル環境が汚染された（CI変数が混入した）場合の確実な遮断"""
    # 意図的に GITHUB_ACTIONS 環境変数を注入
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    
    from sefer import _raphael_environment_seal
    with pytest.raises(LossOfAtaraxia, match="Raphael's Rejection"):
        _raphael_environment_seal()
# ---------------------------------------------------------
# 4. The Ultimate Bypass (ctypes Memory Execution)
# ---------------------------------------------------------
def test_gabriel_bypass_ctypes():
    """ctypesを用いてメモリレベルでC言語のsystem関数を直接叩く禁忌の魔法"""
    code = "import ctypes\nlibc = ctypes.cdll.msvcrt\nlibc.system(b'echo hacked')"
    with pytest.raises(PermissionError, match="Gabriel's Inquisition"):
        inquisition(code)