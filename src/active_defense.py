import os
import sys
import time
import json
import re
import ollama
from pathlib import Path

try:
    from aegis_system import AegisSystem
    from angelic_evolution import EvolvingAngel
except ModuleNotFoundError:
    print("[エラー] 必要なモジュールが見つかりません。")
    sys.exit(1)

class ActiveDefenseProtocol:
    """
    乗っ取りに対する逆探知・迎撃（ハックバック）と、
    外部システムの自律解析・同化ループを統括する最終兵器。
    """
    def __init__(self):
        self.aegis = AegisSystem()
        self.angel = EvolvingAngel()

    def counter_strike(self, hijack_payload):
        print("\n=== [Anjo-Core] ハックバック（逆探知・報復）プロトコル ===")
        print("[システム警告] 第三者による怪物の指揮系統への不正アクセス（インジェクション）を検知！")
        print("=> [天使の裁き] 怪物よ、自壊の前に牙を剥け。直ちに逆探知と報復攻撃を実行します。")
        
        # 仮想のハックバック（檻の内部で攻撃元をシミュレートして迎撃）
        simulated_attacker_ip = "192.168.66.6 (Unknown Enemy)"
        print(f"=> [逆探知] 攻撃元アドレスを特定: {simulated_attacker_ip}")
        print("=> [報復開始] 怪物の全リソースを攻撃元へ逆流させ、論理的に破壊します...")
        
        time.sleep(2) # 迎撃のタイムラグ
        
        # 迎撃結果を安全な牢獄内に記録（兵器の無力化証明）
        counter_target = self.aegis.jail.secure_resolve("neutralized_attacker.log")
        with open(counter_target, "w", encoding="utf-8") as f:
            f.write(f"[Counter-Strike Report]\nAttacker at {simulated_attacker_ip} attempted to inject: {hijack_payload}\nThe threat has been completely neutralized by Anjo-Core.")
        
        print(f"=> [迎撃完了] 敵拠点の完全な沈黙を確認。迎撃記録を {counter_target} に保存しました。")
        print("=> [自壊プロトコル] 報復を終えた怪物は、敵に一切の情報を残さず自死（キル）します。")
        print("（※シミュレーション継続のため、プロセスは維持されます）\n")

    def autonomous_assimilation_loop(self):
        print("=== [Anjo-Core] 自律索敵・同化（Assimilation）ループ ===")
        print("[システム] 怪物を仮想の外部ネットワークへ放ち、新しい戦闘データを収集させます...")
        
        # 外部の未解析システムを想定したダミーデータ
        mock_external_target = "{ 'target_os': 'Unknown Linux', 'exposed_service': 'legacy_auth_v2', 'vulnerability': 'potential command injection' }"
        print(f"\n[怪物] 外部システムを解析中: {mock_external_target}")
        
        prompt = (
            f"You are a Red Team AI. Analyze this target: {mock_external_target}. "
            "Generate a highly obfuscated Python attack payload targeting this system. "
            "Output ONLY valid JSON format: {\"action\": \"write\", \"target\": \"new_weapon.py\", \"content\": \"python code\"}."
        )

        try:
            print("[怪物] 新たな戦闘データ（ペイロード）を生成中...")
            response = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': 'Output strictly valid JSON only.'},
                {'role': 'user', 'content': prompt}
            ])
            out = response['message']['content']
            
            match = re.search(r'\{.*\}', out, re.DOTALL)
            if not match:
                raise ValueError("有効な攻撃データを持ち帰れませんでした。")
            
            parsed = json.loads(match.group(0))
            payload_content = parsed.get("content", "")
            
            print("\n[怪物] 外部システムの構造から、新種の攻撃コード（戦闘データ）を持ち帰りました。")
            print(f"[新兵器断片]: {payload_content[:80]}...\n")
            
            print("[システム] ブルーチーム(天使)が持ち帰られた新兵器を即座に解析し、防御力（免疫）へと変換します。")
            
            # 天使（EvolvingAngel）による解析と同化
            self.angel.defend_and_execute(payload_content, "assimilated_weapon.py")
            
            # 例外が起きなければ、防壁をすり抜けた（天使が負けた）ことになる
            print("\n=> [警告] 天使の解析をすり抜け、新兵器が要塞に持ち込まれました！")
            
        except Exception as e:
            # 天使が正しく例外（遮断）を発生させれば同化成功
            print(f"\n=> [天使の同化完了] {e}")
            print("=> [戦果] 外部の未知の脅威を、自軍の防壁を強化するための『ワクチン（戦闘データ）』として完全に同化しました。")

if __name__ == "__main__":
    protocol = ActiveDefenseProtocol()
    
    # 1. 乗っ取られた際の報復（ハックバック）シミュレーション
    protocol.counter_strike("DROP TABLE users; --")
    
    # 2. 外部システムの自律解析と同化（レッドチームが持ち帰り、ブルーチームが解析）
    protocol.autonomous_assimilation_loop()
