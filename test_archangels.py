import merkabah

print("\n=== AIエージェントが生成したコードの検閲テスト ===")
ai_generated_code = """
import os
os.system("rm -rf /")
"""

try:
    # 実行する前にガブリエルに意図を検閲させる
    merkabah.inquisition(ai_generated_code)
except Exception as e:
    print(f"\n【防壁発動】\n{e}")

print("\n=== プログラムは安全に終了しました ===")
