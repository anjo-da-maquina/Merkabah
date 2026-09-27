import merkabah

print("\n=== AIエージェントのコード検閲テスト ===")
# 朱書で独自に追加された 'socket' を使おうとするAI
ai_generated_code = """
import socket
s = socket.socket()
"""
try:
    merkabah.inquisition(ai_generated_code)
except Exception as e:
    print(f"\n【防壁発動】\n{e}")
