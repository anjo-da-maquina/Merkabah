import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "アルファとオメガの結界 (Alpha Omega Guard)"


# ワークフロー整合性ガード: CIワークフロー定義ファイル自体が存在し、
# 必須ステップ（天使の呼び出し）が削除されていないかを検証する。
REQUIRED_STEP_FILES = ["michael_sword.py", "gabriel_canary.py", "raziel_auditor.py"]

def main():
    workflow = ROOT / ".github" / "workflows" / "anjo_da_maquina_protocol.yml"
    if not workflow.exists():
        report_fail(NAME, "CIワークフロー定義ファイルが見つかりません。")
    text = workflow.read_text(encoding="utf-8", errors="ignore")
    missing = [f for f in REQUIRED_STEP_FILES if f not in text]
    if missing:
        report_fail(NAME, f"必須の天使ステップがワークフローから削除されています: {missing}")
    report_pass(NAME, "CIワークフローに必須の防御ステップが存在することを確認しました。")

if __name__ == "__main__":
    main()
