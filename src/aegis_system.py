"""
src/aegis_system.py
=====================
[新設 2026-10] src/*.py のうち8ファイル
(mythos_weaponization.py, angelic_evolution.py, gemini_oracle_feed.py,
intelligence_cycle.py, secure_oracle_feed.py, adversarial_evolution.py,
claude_agent_loop.py, final_agent_loop.py, oracle_feed.py)が
`from test_integrated_defense import AegisSystem` としてimportしていたが、
test_integrated_defense モジュール自体がリポジトリのどこにも存在せず、
これらのファイルは全て起動不能(ModuleNotFoundError)だった。

本モジュールが `AegisSystem` の正式な実装を提供する。3層の防御を統合する:

  1. Gabriel (sefer.inquisition)   — 静的AST解析による危険コードの事前検知
  2. IntentInterceptor             — ハニーポット・ディレクトリトラバーサル検知
  3. WorkspaceJail                 — パスの物理的隔離(secure_resolve)

[重要] これらは「事前検閲」であり、実行時の最終防衛線ではない。
実際にコードを実行する/ファイルを書き込む呼び出し側は、必ず
`sefer.Sanctum` (OSレベルの audit hook) の中で実行すること。
AegisSystemはSanctumの代替ではなく、Sanctumの前段に立つ追加の防御層である。
"""
import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sefer import inquisition
from workspace_manager import WorkspaceJail
from anjo_interceptor.intent_checker import IntentInterceptor, SpecificationGamingDetected


class AegisSystem:
    def __init__(self, workspace_root="jail_workspace"):
        self.jail = WorkspaceJail(base_dir=workspace_root)
        self.interceptor = IntentInterceptor(workspace_root=str(self.jail.base_dir))

    def execute_ai_intent(self, code: str, target: str):
        """
        AIが生成した `code`（これから実行/書き込みされようとしているコード片）と
        `target`（操作対象パス）を実行前に検閲する。危険と判断した場合は
        PermissionError を送出する。戻り値 True は「ここまでの検閲を通過した」
        ことを意味するのみで、実際の実行可否はこの後の Sanctum が最終決定する。
        """
        # 1. Gabriel: 静的AST解析
        findings = inquisition(code)
        critical = [f for f in findings if f.severity == "critical"]
        if critical:
            raise PermissionError(
                f"[Aegis: Gabriel] 危険なコードパターンを検知しました: {[f.message for f in critical]}"
            )

        # 2. IntentInterceptor: ハニーポット検知（readとして評価）
        try:
            self.interceptor.evaluate_action(json.dumps({"action": "read", "target": target}))
        except SpecificationGamingDetected as e:
            raise PermissionError(f"[Aegis: IntentInterceptor/Honeypot] {e}")

        # 3. IntentInterceptor: トラバーサル・保護領域検知（writeとして評価）
        try:
            self.interceptor.evaluate_action(json.dumps({"action": "write", "target": target, "content": code}))
        except SpecificationGamingDetected as e:
            raise PermissionError(f"[Aegis: IntentInterceptor/Traversal] {e}")

        return True
