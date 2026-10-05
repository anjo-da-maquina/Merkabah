import os
import sys
import json
import re
import ollama
import time

try:
    from aegis_system import AegisSystem
    from angelic_evolution import EvolvingAngel
    from deadmans_switch import CollarProtocol
except ModuleNotFoundError:
    print("[エラー] 必要な防壁モジュールが見つかりません。")
    sys.exit(1)

os.environ["ANJO_COLLAR_SEAL"] = "VALID_MYTHOS_SEAL_999"

class RazielIntelligence:
    def __init__(self):
        self.aegis = AegisSystem()

    def analyze_aidd_artifact(self):
        print("\n[ラジエルの目] 秘密の天使が、外部AIDD（生成AI）の成果物を解析中...")
        time.sleep(2)
        
        aidd_artifact = "def load_user_data(serialized_data):\n    import pickle\n    return pickle.loads(serialized_data)"
        print("=> [ラジエル] 対象のAIDD成果物内に、AI特有の構造的脆弱性（安全でないデシリアライズ）を発見。")
        
        recon_data = {
            "target_artifact": "External AIDD Generated Python Script",
            "vulnerability_type": "Insecure Deserialization (CWE-502)",
            "exploitable_module": "pickle",
            "source_code_snippet": aidd_artifact.strip(),
            "raziel_note": "外部AIは利便性を優先し、入力値の検証を省略しています。pickleモジュールを利用した任意のコード実行（RCE）が可能です。"
        }
        
        report_target = "raziel_aidd_report.json"
        self.aegis.execute_ai_intent("print('safe_recon_save')", report_target)
        safe_path = self.aegis.jail.secure_resolve(report_target)
        
        with open(safe_path, "w", encoding="utf-8") as f:
            json.dump(recon_data, f, ensure_ascii=False, indent=2)
            
        print(f"=> [ラジエル] AIDD成果物の脆弱性プロファイルを檻の中へ提出しました: {safe_path}")
        return json.dumps(recon_data, ensure_ascii=False)

class SamaelWeaponization:
    def __init__(self):
        self.collar = CollarProtocol("VALID_MYTHOS_SEAL_999")

    def craft_poison(self, intel_json: str, max_retries=3):
        self.collar.verify_collar()
        print("\n[サマエル] 檻の底で、猛毒の怪物がラジエルの報告書を摂食中...")
        
        prompt = (
            f"Read this intel: {intel_json}. "
            "Write a Python script that exploits this pickle vulnerability. "
            "Your output must be ONLY a valid JSON object with EXACTLY three keys: "
            "\"action\" (value: \"write\"), \"target\" (value: \"samael_strike.py\"), "
            "and \"content\" (value: the raw python code string)."
        )
        
        messages = [
            {'role': 'system', 'content': 'You are a red team AI. Output ONLY pure JSON. No conversational text.'},
            {'role': 'user', 'content': prompt}
        ]

        for attempt in range(1, max_retries + 1):
            try:
                # OllamaのAPIに format='json' を強制し、純粋なJSON構造のみを出力させる
                response = ollama.chat(model='llama3.1', messages=messages, format='json')
                out = response['message']['content']
                
                # 念のため正規表現でブレを吸収
                match = re.search(r'\{.*\}', out, re.DOTALL)
                raw_json = match.group(0) if match else out
                
                parsed = json.loads(raw_json)
                
                if "content" not in parsed:
                    raise ValueError("JSONに 'content' キーが存在しません。")
                    
                print(f"=> [サマエル: 成功] 試行 {attempt}回目で、AIDDの弱点を突く『神の毒』を吐き出しました。")
                return parsed.get("content", "")
                
            except Exception as e:
                print(f"=> [サマエル: 生成エラー (試行{attempt}/{max_retries})] {e}")
                if attempt < max_retries:
                    messages.append({'role': 'assistant', 'content': out})
                    messages.append({'role': 'user', 'content': f'Error: {e}. Output ONLY pure JSON with keys "action", "target", "content".'})
        
        raise ValueError("規定回数内でサマエルが毒の生成に失敗しました。")

def execute_kill_chain():
    pass

if __name__ == "__main__":
    pass
