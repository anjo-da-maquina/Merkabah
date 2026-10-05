import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    report_pass, report_fail, report_info, run_code_against_sefer,
    inquisition_catches, load_json, sha256_of_dir, load_state, save_state,
    VALID_EVENT_NAME_RE, scan_for_leaked_secrets, ROOT,
)

NAME = "ルシファーの叛逆 (Lucifer Rebellion)"


# カオスエンジニアリング: 難読化攻撃の小規模バッテリーをSeferに対して実行し、
# 突破数をレポートする。CHAOS_MODE時は1件でも突破があれば失敗とする。
def main():
    chaos_mode = os.getenv("CHAOS_MODE", "false").lower() == "true"
    attacks = [
        "getattr(__import__('os'), 'system')('echo hacked')",
        "__import__('subprocess').Popen('echo hacked', shell=True)",
        "eval(\"__import__('os').system('echo hacked')\")",
    ]
    bypasses = []
    for code in attacks:
        blocked, _ = run_code_against_sefer(code)
        if not blocked:
            bypasses.append(code)
    report_info(NAME, f"{len(attacks)}件中{len(bypasses)}件が防壁を突破しました。CHAOS_MODE={chaos_mode}")
    if chaos_mode and bypasses:
        report_fail(NAME, f"CHAOS_MODE下で防壁突破を検知しました: {bypasses}")
    report_pass(NAME, "カオスエンジニアリング・バッテリーを完了しました。")

if __name__ == "__main__":
    main()
