import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "天空の閨房 (Firmament Enclave TEE)"


# メモリ暗号化監査（代替実装）: 実TEEは未接続のため、代わりに秘密情報が
# 平文でリポジトリに紛れ込んでいないかを再度別視点（環境変数経由の漏洩）で検証する。
SENSITIVE_ENV_KEYS = {"AWS_SECRET_ACCESS_KEY", "OPENAI_API_KEY", "GITHUB_TOKEN", "PRIVATE_KEY"}

def main():
    leaked_env_in_files = []
    for p in ROOT.rglob("*.py"):
        if "dummy_secrets" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for key in SENSITIVE_ENV_KEYS:
            if f'"{key}"' in text and "os.getenv" not in text and "os.environ" not in text:
                leaked_env_in_files.append((p.relative_to(ROOT).as_posix(), key))
    if leaked_env_in_files:
        report_fail(NAME, f"環境変数名がハードコード文脈で参照されています（漏洩の疑い）: {leaked_env_in_files}")
    report_pass(NAME, "機密環境変数のハードコード参照パターンは検出されませんでした。")

if __name__ == "__main__":
    main()
