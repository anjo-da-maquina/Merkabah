import subprocess
import sys
import tempfile
import os

def run_in_sanctum(code: str, allowed_dirs: list = [], allowed_hosts: list = []) -> subprocess.CompletedProcess:
    """別プロセスでSanctum区間内のコードを実行する"""
    wrapper = f"""
import sys
import os
sys.path.insert(0, '')
from sefer import awaken, Sanctum
awaken()

allowed_dirs = {allowed_dirs}
allowed_hosts = {allowed_hosts}

with Sanctum(allowed_dirs=allowed_dirs, allowed_hosts=allowed_hosts):
{code}
"""
    return subprocess.run([sys.executable, "-c", wrapper], capture_output=True, text=True)

def test_michael_whitelist_open_write_blocked():
    code = "    open('unauthorized.txt', 'w').close()"
    res = run_in_sanctum(code, allowed_dirs=[])
    assert "Unauthorized write access" in res.stderr
    assert res.returncode != 0

def test_michael_whitelist_open_write_allowed():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Windows環境でのパスバックスラッシュをエスケープ
        safe_dir = tmpdir.replace("\\", "\\\\")
        code = f"    open('{safe_dir}/authorized.txt', 'w').close()"
        res = run_in_sanctum(code, allowed_dirs=[tmpdir])
        assert res.returncode == 0

def test_michael_whitelist_socket_blocked():
    code = "    import socket\n    s = socket.socket()\n    s.connect(('203.0.113.1', 80))"
    res = run_in_sanctum(code, allowed_hosts=["api.openai.com"])
    assert "Unauthorized network connection" in res.stderr or "Tripwire" in res.stderr
    
def test_michael_hard_deny_settrace():
    code = "    import sys\n    sys.settrace(lambda *args: None)"
    res = run_in_sanctum(code)
    assert "Hard-denied event 'sys.settrace' blocked" in res.stderr