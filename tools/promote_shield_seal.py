"""
Shield Rules 承認プロモーションツール
========================================
[新設 2026-10] `src/angelic_shield.py` の `ZadkielDominion` が
Gemini(LLM)から取得した脅威情報を元に提案した防壁ルール
(`sefer/shield_rules_pending.json`)を、人間が内容を確認した上で
`shield_rules.json`(実際に `src/kamael_judgment.py` が使用する
有効な禁止ルール)へ昇格させるためのツール。

これにより、未検証のLLM出力（プロンプトインジェクション・幻覚を含む）が
そのまま実運用の防御ルールに反映されることを防ぐ。
`tools/promote_ledger_seal.py`(Armageddon Engine向け)と同一のパターン。

使い方:
    python tools/promote_shield_seal.py --list
    python tools/promote_shield_seal.py --approve "<vulnerability_name>"
    python tools/promote_shield_seal.py --reject  "<vulnerability_name>"
"""
import argparse
import json
from pathlib import Path

PLEROMA_DIR = Path(__file__).parent.parent
RULES_PATH = PLEROMA_DIR / "shield_rules.json"
PENDING_RULES_PATH = PLEROMA_DIR / "sefer" / "shield_rules_pending.json"


def _load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_pending():
    pending = _load_json(PENDING_RULES_PATH, [])
    open_items = [p for p in pending if p.get("status") == "PENDING_HUMAN_REVIEW"]
    if not open_items:
        print("承認待ちの提案はありません。")
        return
    for p in open_items:
        print(f"--- {p['vulnerability_name']} (proposed_at={p['proposed_at']}) ---")
        print(f"  説明          : {p.get('description', '')[:200]}")
        print(f"  禁止モジュール案: {p.get('dangerous_modules', [])}")
        print(f"  禁止関数案    : {p.get('dangerous_functions', [])}")
        print()


def _set_status(vuln_name, new_status):
    pending = _load_json(PENDING_RULES_PATH, [])
    found = False
    for p in pending:
        if p["vulnerability_name"] == vuln_name and p.get("status") == "PENDING_HUMAN_REVIEW":
            p["status"] = new_status
            found = True
    if not found:
        print(f"[エラー] 承認待ちの提案に '{vuln_name}' は見つかりませんでした。")
        return None
    with open(PENDING_RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)
    return pending


def approve(vuln_name):
    pending = _set_status(vuln_name, "APPROVED")
    if pending is None:
        return
    proposal = next(p for p in pending if p["vulnerability_name"] == vuln_name and p["status"] == "APPROVED")

    rules = _load_json(RULES_PATH, {"blocked_modules": [], "blocked_functions": []})
    rules["blocked_modules"] = sorted(set(rules.get("blocked_modules", [])) | set(proposal.get("dangerous_modules", [])))
    rules["blocked_functions"] = sorted(set(rules.get("blocked_functions", [])) | set(proposal.get("dangerous_functions", [])))
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)

    print(f"[承認] '{vuln_name}' を shield_rules.json に昇格しました。")


def reject(vuln_name):
    if _set_status(vuln_name, "REJECTED") is not None:
        print(f"[拒否] '{vuln_name}' を拒否しました（shield_rules.jsonには反映されません）。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shield Rules 承認プロモーションツール")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true")
    group.add_argument("--approve", metavar="VULNERABILITY_NAME")
    group.add_argument("--reject", metavar="VULNERABILITY_NAME")
    args = parser.parse_args()

    if args.list:
        list_pending()
    elif args.approve:
        approve(args.approve)
    elif args.reject:
        reject(args.reject)
