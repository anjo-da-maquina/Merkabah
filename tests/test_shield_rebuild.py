"""
tests/test_shield_rebuild.py
==============================
src/angelic_shield.py / src/kamael_judgment.py の再構築(2026-10)を検証する
回帰テスト。詳細な経緯は両モジュールのdocstring、および
angels/zadkiel_shield_decree.py 参照。

確認する点:
  1. ZadkielDominion.propose_knowledge() が、LLM生出力を即時に
     shield_rules.json へ反映せず、承認待ちキュー(pending file)に
     積むだけであること(人間承認を経ない自動ルール変更の防止)。
  2. tools/promote_shield_seal.py が、承認待ちの提案を正しく
     shield_rules.json へ昇格させること。
  3. KamaelInquisitor が完全修飾名(例: "os.system")で登録された
     禁止関数ルールを正しく検知すること(Gabrielと同種のバグ修正)。
  4. 完全修飾名とバレ名の両方が一致する場合でも、二重報告しないこと。
"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from angelic_shield import ZadkielDominion
import kamael_judgment as kj


def test_propose_knowledge_does_not_mutate_rules_file(tmp_path):
    rules_file = tmp_path / "shield_rules.json"
    pending_file = tmp_path / "shield_rules_pending.json"
    z = ZadkielDominion(rules_file=rules_file, pending_file=pending_file)

    intel = {
        "vulnerability_name": "Fake Vuln",
        "description": "desc",
        "dangerous_modules": ["ctypes"],
        "dangerous_functions": ["os.system"],
    }
    z.propose_knowledge(intel)

    rules = json.loads(rules_file.read_text(encoding="utf-8"))
    assert rules == {"blocked_modules": [], "blocked_functions": []}, (
        "propose_knowledge が shield_rules.json を直接変更してしまっている"
        "(人間承認を経ないルール反映は禁止)"
    )

    pending = json.loads(pending_file.read_text(encoding="utf-8"))
    assert len(pending) == 1
    assert pending[0]["status"] == "PENDING_HUMAN_REVIEW"
    assert pending[0]["vulnerability_name"] == "Fake Vuln"


def test_promote_shield_seal_approval_flow(tmp_path, monkeypatch):
    rules_file = tmp_path / "shield_rules.json"
    pending_file = tmp_path / "shield_rules_pending.json"

    import promote_shield_seal as pss
    monkeypatch.setattr(pss, "RULES_PATH", rules_file)
    monkeypatch.setattr(pss, "PENDING_RULES_PATH", pending_file)

    z = ZadkielDominion(rules_file=rules_file, pending_file=pending_file)
    z.propose_knowledge({
        "vulnerability_name": "Fake Vuln 2",
        "dangerous_modules": ["ctypes"],
        "dangerous_functions": ["os.system", "danger_call"],
    })

    pss.approve("Fake Vuln 2")

    rules = json.loads(rules_file.read_text(encoding="utf-8"))
    assert set(rules["blocked_modules"]) == {"ctypes"}
    assert set(rules["blocked_functions"]) == {"os.system", "danger_call"}

    pending = json.loads(pending_file.read_text(encoding="utf-8"))
    assert pending[0]["status"] == "APPROVED"


def test_kamael_inquisitor_catches_qualified_call_name():
    rules = {"blocked_modules": [], "blocked_functions": ["os.system"]}
    tree_src = "import os\nos.system('echo hacked')\n"
    import ast
    tree = ast.parse(tree_src)
    inquisitor = kj.KamaelInquisitor(rules)
    inquisitor.visit(tree)
    assert any("os.system" in v for v in inquisitor.violations), (
        "完全修飾名 'os.system' がblocked_functionsに登録されていても検知されない"
        "(Gabrielで修正済みの同種バグが再発している)"
    )
    assert len(inquisitor.violations) == 1, "同一呼び出しが重複して報告されている"


def test_kamael_inquisitor_bare_name_still_works_no_regression():
    rules = {"blocked_modules": [], "blocked_functions": ["eval"]}
    import ast
    tree = ast.parse("eval('1+1')\n")
    inquisitor = kj.KamaelInquisitor(rules)
    inquisitor.visit(tree)
    assert any("eval" in v for v in inquisitor.violations)
    assert len(inquisitor.violations) == 1
