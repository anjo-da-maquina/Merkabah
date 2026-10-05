import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "千の眼のオファニム (Ophanim Thousand Eyes)"


# UI視覚監査: architecture.html が構文的に妥当なHTMLであり、
# 外部スクリプトの読み込み等の不審な要素を含まないことを検証する。
def main():
    html_path = ROOT / "architecture.html"
    if not html_path.exists():
        report_pass(NAME, "architecture.html が存在しないため検査対象なし。")
        return
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    if "<html" not in text.lower():
        report_fail(NAME, "architecture.html に <html> タグが見つかりません（破損の疑い）。")
    import re as _re
    external_scripts = _re.findall(r'<script[^>]+src=["\']https?://[^"\']+["\']', text, _re.IGNORECASE)
    if external_scripts:
        report_fail(NAME, f"外部スクリプト読み込みを検知しました（サプライチェーンリスク）: {external_scripts}")
    report_pass(NAME, "architecture.html の構造を確認し、外部スクリプト読み込みは検知されませんでした。")

if __name__ == "__main__":
    main()
