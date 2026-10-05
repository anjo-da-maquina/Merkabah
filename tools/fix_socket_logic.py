import re
with open("sefer/__init__.py", "r", encoding="utf-8") as f:
    code = f.read()

# 既存のsocket.connectブロックを正規表現で抽出し、堅牢なループ処理に置き換える
old_code_match = re.search(r'    if event == "socket\.connect":.*?        return', code, re.DOTALL)
if old_code_match:
    new_code = """    if event == "socket.connect":
        for arg in args:
            if isinstance(arg, tuple) and len(arg) >= 1 and isinstance(arg[0], str):
                if arg[0] not in policy.get("allowed_hosts", set()):
                    raise RuntimeError(f"[Sefer] Tripwire: Unauthorized network connection to '{arg[0]}'.")
        return"""
    
    with open("sefer/__init__.py", "w", encoding="utf-8") as f:
        f.write(code.replace(old_code_match.group(0), new_code))
    print("[+] Socket evaluation logic hardened.")
else:
    print("[-] Could not find the socket.connect block to replace.")
