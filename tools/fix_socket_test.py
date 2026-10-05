with open("tests/test_michael_whitelist.py", "r", encoding="utf-8") as f:
    code = f.read()

# DNS解決を回避し、直接Audit Hookを発火させるためにIPアドレスへ置換
code = code.replace("\'evil.com\'", "\'203.0.113.1\'")

with open("tests/test_michael_whitelist.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[+] Test updated to bypass DNS resolution.")
