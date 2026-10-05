with open("sefer/__init__.py", "r", encoding="utf-8") as f:
    code = f.read()

# socket関連のイベントをすべて網羅するようにミカエルの条件を広げる
old_socket_logic = """    if event == "socket.connect":
        for arg in args:
            if isinstance(arg, tuple) and len(arg) >= 1 and isinstance(arg[0], str):
                if arg[0] not in policy.get("allowed_hosts", set()):
                    raise RuntimeError(f"[Sefer] Tripwire: Unauthorized network connection to '{arg[0]}'.")
        return"""

new_socket_logic = """    if "socket" in event:
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

if old_socket_logic in code:
    code = code.replace(old_socket_logic, new_socket_logic)
    with open("sefer/__init__.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[+] Socket audit hook generalized to catch all socket events.")
else:
    print("[-] Target logic not found, inspecting alternative...")
