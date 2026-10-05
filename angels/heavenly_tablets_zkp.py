import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "天の石板 (Heavenly Tablets ZKP)"


# ZKP生成監査: zk_audit_trail.json から JUnit XML へのエクスポートが
# 正しく機能し、生成物が妥当なXMLであることを検証する。
def main():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "adapters"))
    trail_path = ROOT / "zk_audit_trail.json"
    if not trail_path.exists():
        report_pass(NAME, "zk_audit_trail.json が未生成のため検査対象なし。")
        return
    from adapters.junit_xml_exporter import export_zkp_to_junit
    out_path = ROOT / "zk_audit_report.xml"
    export_zkp_to_junit(json_path=str(trail_path), xml_path=str(out_path))
    import xml.etree.ElementTree as ET
    try:
        ET.parse(out_path)
    except ET.ParseError as e:
        report_fail(NAME, f"生成されたZKP監査レポートが妥当なXMLではありません: {e}")
    report_pass(NAME, "ZKP監査レポート(JUnit XML)の生成・妥当性を確認しました。")

if __name__ == "__main__":
    main()
