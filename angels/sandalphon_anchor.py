import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "サンダルフォンの錨 (Sandalphon Anchor)"


# 証跡のブロックチェーン化（ロールバック検知）: 前回実行時に記録した
# チェックポイント(index, hash)が、現在のログの同じindex位置に
# そのまま存在するかを検証する。履歴の巻き戻し・改ざんを検知する。
def main():
    log_path = ROOT / "sefer" / "audit_chain.jsonl"
    entries = []
    if log_path.exists():
        import json as _json
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(_json.loads(line))

    checkpoint = load_state("sandalphon_anchor")
    if checkpoint:
        idx = checkpoint["index"]
        expected_hash = checkpoint["hash"]
        matching = [e for e in entries if e.get("index") == idx]
        if not matching or matching[0].get("hash") != expected_hash:
            report_fail(NAME, f"アンカーされたチェックポイント(index={idx})のハッシュが一致しません。履歴の巻き戻し・改ざんの疑い。")

    if entries:
        last = entries[-1]
        save_state("sandalphon_anchor", {"index": last["index"], "hash": last["hash"]})
        report_pass(NAME, f"最新チェックポイント(index={last['index']})をアンカーしました。")
    else:
        report_pass(NAME, "監査証跡が空のため、アンカー対象なし。")

if __name__ == "__main__":
    main()
