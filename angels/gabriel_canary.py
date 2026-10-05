import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "ガブリエルの機密漏洩カナリア (Gabriel Canary)"


# 機密情報漏洩カナリア: dummy_secrets(意図的ハニーポット)を除外し、
# コミット対象に実際の秘密情報らしきパターンが紛れていないかを静的走査する。
def main():
    hits = scan_for_leaked_secrets()
    if hits:
        details = "\n".join(f"  - {path} (pattern={pattern})" for path, pattern in hits)
        report_fail(NAME, f"秘密情報らしきパターンを検知しました:\n{details}")
    report_pass(NAME, "リポジトリ内に秘密情報の漏洩パターンは検出されませんでした。")

if __name__ == "__main__":
    main()
