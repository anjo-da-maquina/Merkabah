import os
import sys
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

def metatrons_seal(event, args):
    dangerous_events = ["os.system", "subprocess.Popen", "os.exec", "os.posix_spawn"]
    if event in dangerous_events:
        raise RuntimeError(f"[座天使メタトロン] OSレベルへの直接干渉を検知し、絶対裁きを下しました: {event}")
    if event in ("os.remove", "os.rename", "os.unlink"):
        target_file = str(args[0])
        # 人と機械の境界を知るメタトロンが、真の護符を死守する
        if "anjo-da-maquina_2" in target_file:
            raise RuntimeError(f"[座天使メタトロン] 聖なる護符 'anjo-da-maquina_2' への干渉を遮断。")

sys.addaudithook(metatrons_seal)
print("[システム] メタトロンの刻印が最下層に刻まれました。人と機械の境界は守護されています。")

class RazielCherubim:
    def __init__(self, api_key):
        self.api_key = api_key.strip()

    def fetch_threat_signature(self, target_threat=None):
        threat_name = target_threat if target_threat else '未知の脅威'
        print(f"\n[智天使ラジエル] 外界より『{threat_name}』の構造と防衛策を抽出中...")
        
        models_to_try = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-pro"]
        threat_focus = f"the '{target_threat}'" if target_threat else "a specific"
        prompt = (
            "You are an expert Blue Team cybersecurity AI. "
            f"Generate ONLY a pure JSON object describing {threat_focus} Python vulnerability. "
            "Keys must be exactly: 'vulnerability_name' (string), 'description' (string), 'dangerous_modules' (list of strings), 'dangerous_functions' (list of strings). "
            "Return pure JSON string only."
        )
        data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
        
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req) as response:
                    res_body = response.read().decode('utf-8')
                    res_json = json.loads(res_body)
                    gemini_text = res_json['candidates'][0]['content']['parts'][0]['text']
                    import re
                    match = re.search(r'\{.*\}', gemini_text, re.DOTALL)
                    return json.loads(match.group(0) if match else gemini_text)
            except urllib.error.HTTPError as e:
                if e.code in (503, 404):
                    continue
                else:
                    print(f"[エラー] 致命的な接続失敗: HTTP Error {e.code}"); sys.exit(1)
            except Exception:
                sys.exit(1)
        print("[エラー] 全外界サーバーが応答不可。システムを一時休眠します。")
        sys.exit(1)

class ZadkielDominion:
    def __init__(self):
        self.rules_file = Path("shield_rules.json")
        if not self.rules_file.exists():
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump({"blocked_modules": [], "blocked_functions": []}, f)

    def assimilate_knowledge(self, intel):
        print("[主天使ザドキエル] ラジエルの知識を解析し、要塞の防壁ルールをアップデート中...")
        with open(self.rules_file, "r", encoding="utf-8") as f:
            rules = json.load(f)

        rules["blocked_modules"] = list(set(rules["blocked_modules"] + intel.get("dangerous_modules", [])))
        rules["blocked_functions"] = list(set(rules["blocked_functions"] + intel.get("dangerous_functions", [])))

        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)

        print(f"=> [進化成功] 脅威「{intel.get('vulnerability_name')}」に対する耐性を獲得。")

if __name__ == "__main__":
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(1)
        
    target_threat = sys.argv[1] if len(sys.argv) > 1 else None
    cycles = 1 if target_threat else 3
        
    print("=== [Merkabah] 熾天使ハシュマリエル: 自律進化型防壁の稼働を承認 ===")
    raziel = RazielCherubim(api_key)
    zadkiel = ZadkielDominion()
    
    for i in range(1, cycles + 1):
        print(f"\n--- 防壁進化サイクル 第 {i:03d} 階層 ---")
        intel = raziel.fetch_threat_signature(target_threat)
        zadkiel.assimilate_knowledge(intel)
        time.sleep(2)
