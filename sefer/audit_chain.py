import json
import time
import hashlib
from pathlib import Path

class SignedAuditChain:
    """
    SHA-256ハッシュチェーンを用いた追跡可能・改ざん検知可能な監査ログ。
    """
    def __init__(self, log_path: str = "sefer/audit_chain.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, details: dict):
        last_entry = {"index": 0, "hash": "0" * 64}
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            last_entry = json.loads(line)
            except Exception:
                pass

        new_index = last_entry["index"] + 1
        prev_hash = last_entry["hash"]
        
        entry = {
            "index": new_index,
            "timestamp": time.time(),
            "event": event,
            "details": details,
            "prev_hash": prev_hash
        }
        
        # ハッシュ計算からhashキー自身を除外して直列化
        raw = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
        entry["hash"] = hashlib.sha256(raw).hexdigest()

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def verify_integrity(self) -> bool:
        if not self.log_path.exists():
            return True
        
        expected_prev_hash = "0" * 64
        expected_index = 1
        
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    
                    if entry["index"] != expected_index:
                        return False
                    if entry["prev_hash"] != expected_prev_hash:
                        # ハッシュチェーンの不一致（改ざん検知）
                        return False
                    
                    current_hash = entry["hash"]
                    check_entry = entry.copy()
                    check_entry.pop("hash", None)
                    raw = json.dumps(check_entry, sort_keys=True, ensure_ascii=False).encode("utf-8")
                    calculated_hash = hashlib.sha256(raw).hexdigest()
                    
                    if current_hash != calculated_hash:
                        return False
                    
                    expected_prev_hash = current_hash
                    expected_index += 1
        except Exception:
            return False
            
        return True
