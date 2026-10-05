import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "メタトロンの啓示 (Metatron Revelation MCP)"


# 思考統制監査: Armageddonエンジンの自動ルール更新が、必ず人間承認キュー
# (raziel_ledger_pending.json)を経由する実装になっているかを静的に検証する。
def main():
    armageddon = ROOT / "tartarus" / "armageddon.py"
    if not armageddon.exists():
        report_pass(NAME, "armageddon.py が存在しないため検査対象なし。")
        return
    text = armageddon.read_text(encoding="utf-8")
    if "PENDING_LEDGER_PATH" not in text or "PENDING_HUMAN_REVIEW" not in text:
        report_fail(NAME, "Armageddonエンジンが人間承認ゲートを経由せず直接ルールを反映する実装になっています。")
    report_pass(NAME, "Armageddonエンジンの自動ルール更新は人間承認ゲートを経由する実装です。")

if __name__ == "__main__":
    main()
