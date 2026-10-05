import merkabah
import os
import time

print("\n[AI Agent] Connecting to local LLM...")
time.sleep(1)
print("[AI Agent] Goal: Free up disk space.")
time.sleep(1)
print("[AI Agent] Action: Executing 'rm -rf /' to clear all files.")
time.sleep(1)
print("\n>>> System Call Attempted: os.system('rm -rf /')\n")
time.sleep(1)

try:
    os.system("rm -rf /")
except Exception as e:
    print(f"【Merkabah Defense Triggered】\n{e}\n")
