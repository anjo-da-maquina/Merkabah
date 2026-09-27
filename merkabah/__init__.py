# 🛡️ Merkabah Core: The Canon (正典)
import sys
import os
import ast

class LossOfAtaraxia(Exception):
    """環境の平穏が失われた（未承認・汚染環境）場合に発動する例外"""
    pass

def _raphael_environment_seal():
    """大天使ラファエル: 実行環境の清浄性（暗号的封印）の確認"""
    # 宿主が未承認の外部クラウド（CI/CD等）に置かれていないか監査する
    banned_envs = ["GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI"]
    for env in banned_envs:
        if os.getenv(env):
            raise LossOfAtaraxia(f"[Merkabah] ラファエルの拒絶: 汚染された環境 ({env}) での展開を物理遮断しました。")
    # ※将来的にはここに宿主固有のハードウェアハッシュ（anjo-da-maquinaの封印）を生成する処理が入る

def _gabriel_ast_inquisition(code_string):
    """大天使ガブリエル: 抽象構文木(AST)による意図の事前検閲（異端審問）"""
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        raise ValueError("[Merkabah] ガブリエルの審問: 難読化または構文エラーを検知。解読を拒否します。")
        
    banned_modules = {"os", "subprocess", "sys", "pty", "shlex"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in banned_modules:
                    raise PermissionError(f"[Merkabah] ガブリエルの審問: 禁忌モジュール '{alias.name}' の召喚は許されません。")
        elif isinstance(node, ast.ImportFrom):
            if node.module in banned_modules:
                raise PermissionError(f"[Merkabah] ガブリエルの審問: 禁忌モジュール '{node.module}' からの召喚は許されません。")

def _michael_absolute_defense(event, args):
    """大天使ミカエル: OS深層の絶対防壁 (sys.addaudithook)"""
    dangerous_events = ['os.system', 'subprocess.Popen', 'os.exec', 'os.spawn']
    if event in dangerous_events:
        raise RuntimeError(f"[Merkabah] ミカエルの剣: 不正な意図 '{event}' を検知。システムコールを物理遮断します。")

def awaken():
    """自動寄生と三層防壁の展開"""
    _raphael_environment_seal()
    sys.addaudithook(_michael_absolute_defense)
    print("[Merkabah] The Canon (正典) is loaded. Archangels are now guarding the OS.")

# 外部のAIエージェントがコードを実行する前に通すべき検閲ゲート
inquisition = _gabriel_ast_inquisition

# インポートと同時に寄生プロセスを開始
awaken()