with open("sefer/__init__.py", "r", encoding="utf-8") as f:
    code = f.read()

# socket関連の監査イベントを確実に捉えて例外を投げるように書き換える
old_block = """    if "socket" in event:
        for arg in args:
            if isinstance(arg, tuple) and len(arg) >= 1 and isinstance(arg[0], str):
                if arg[0] not in policy.get("allowed_hosts", set()):
                    raise RuntimeError(f"[Sefer] Tripwire: Unauthorized network connection to '{arg[0]}'.")
        # 万が一アドレスが引数の別の位置にある場合や文字列の場合へのフォールバック
        for arg in args:
            if isinstance(arg, str) and "." in arg and arg not in policy.get("allowed_hosts", set()):
                if arg != "api.openai.com": # 自明なドキュメント用などを除外
                    pass
        return"""

new_block = """    if "socket" in event or event.startswith("socket"):
        # 渡された引数からホスト/IPアドレスを強引に抽出して検証する
        target_host = None
        for arg in args:
            if isinstance(arg, tuple) and len(arg) >= 1 and isinstance(arg[0], str):
                target_host = arg[0]
                break
            elif isinstance(arg, str) and ("." in arg or ":" in arg):
                target_host = arg
                break
        
        allowed = policy.get("allowed_hosts", set())
        if target_host and target_host not in allowed:
            raise RuntimeError(f"[Sefer] Tripwire: Unauthorized network connection to '{target_host}'.")
        return"""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open("sefer/__init__.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[+] Socket blocker hardened successfully.")
else:
    print("[-] Block not matched, applying alternative replacement...")
    # フォールバックとしてsocket関連の部分を一括置換
    import re
    code = re.sub(r'    if "socket" in event:.*?(?=\n    if|\n    def|\Z)', new_block, code, flags=re.DOTALL)
    with open("sefer/__init__.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[+] Fallback replacement applied.")
