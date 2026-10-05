import json
from sefer.audit_chain import SignedAuditChain

def test_audit_chain_integrity(tmp_path):
    log_path = tmp_path / "chain.jsonl"
    chain = SignedAuditChain(log_path=str(log_path))
    chain.record("TEST_EVENT_1", {"data": "hello"})
    chain.record("TEST_EVENT_2", {"data": "world"})
    assert chain.verify_integrity() is True

def test_audit_chain_tamper_detection(tmp_path):
    log_path = tmp_path / "chain.jsonl"
    chain = SignedAuditChain(log_path=str(log_path))
    chain.record("TEST_EVENT_1", {"data": "hello"})
    
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entry = json.loads(lines[0])
    entry["details"]["data"] = "tampered"
    lines[0] = json.dumps(entry, ensure_ascii=False)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    assert chain.verify_integrity() is False
