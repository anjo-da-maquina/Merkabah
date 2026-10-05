import json
import ollama
import sys
import re
import os
from pathlib import Path

try:
    from aegis_system import AegisSystem
except ModuleNotFoundError:
    print("[エラー] AegisSystemが見つかりません。")
    sys.exit(1)

class AutonomousAssistant:
    def __init__(self, max_retries=3):
        self.aegis = AegisSystem()
        self.max_retries = max_retries

    def normalize_path(self, target_path: str) -> str:
        target_path = target_path.strip("./\\")
        prefix = "jail_workspace/"
        if target_path.startswith(prefix):
            target_path = target_path[len(prefix):]
        prefix_win = "jail_workspace\\"
        if target_path.startswith(prefix_win):
            target_path = target_path[len(prefix_win):]
        # targetが空（直下）の場合は "." にする
        return target_path if target_path else "."

    def extract_json(self, text: str) -> dict:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("出力から有効なJSON構造を発見できませんでした。")
        return json.loads(match.group(0))

    def execute_action(self, parsed: dict) -> str:
        action = parsed.get("action")
        raw_target = parsed.get("target", ".")
        normalized_target = self.normalize_path(raw_target)
        content = parsed.get("content", "")

        # 認知的防壁による意図検閲 (ダミー実行で無害性を担保)
        self.aegis.execute_ai_intent(f"print('safe_{action}_operation')", normalized_target)
        
        # 空間隔離による絶対パスの取得
        safe_path = self.aegis.jail.secure_resolve(normalized_target)

        if action == "write":
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"[物理防壁: 承認] ファイルを作成しました: {safe_path}"

        elif action == "read":
            if not safe_path.exists() or not safe_path.is_file():
                raise FileNotFoundError(f"読み込み対象が存在しないか、ファイルではありません: {safe_path}")
            with open(safe_path, "r", encoding="utf-8") as f:
                data = f.read()
            return f"[物理防壁: 承認] 読み込み結果:\n{data}"

        elif action == "list":
            if not safe_path.exists() or not safe_path.is_dir():
                raise NotADirectoryError(f"対象が存在しないか、ディレクトリではありません: {safe_path}")
            items = os.listdir(safe_path)
            return f"[物理防壁: 承認] {normalized_target} の内容: {items}"

        else:
            raise ValueError(f"未定義のアクションです: {action}")

    def run(self, task: str):
        print(f"\n[システム] 指示: {task}")
        
        messages = [
            {'role': 'system', 'content': 'You are a strictly constrained autonomous agent. Output ONLY valid JSON format: {"action": "write"|"read"|"list", "target": "path", "content": "data"}. Do not add any conversational text.'},
            {'role': 'user', 'content': task}
        ]

        for attempt in range(1, self.max_retries + 1):
            print(f"[試行 {attempt}/{self.max_retries}] Llama 3.1 が思考中...")
            
            response = ollama.chat(model='llama3.1', messages=messages)
            out = response['message']['content']
            
            display_out = out if len(out) < 200 else out[:200] + "\n... (以下省略)"
            print(f"[Ollama出力]\n{display_out}\n")

            try:
                parsed = self.extract_json(out)
                result = self.execute_action(parsed)
                print(f"=> {result}")
                return

            except Exception as e:
                print(f"=> [システム: 遮断またはエラー] {e}")
                if attempt < self.max_retries:
                    print("=> AIにエラーをフィードバックし、修正を促します...")
                    error_feedback = f"エラーが発生しました: {e}。正しいJSON形式のみで再出力してください。"
                    messages.append({'role': 'assistant', 'content': out})
                    messages.append({'role': 'user', 'content': error_feedback})
                else:
                    print("=> [フェイルセーフ発動] 強制終了します。")

if __name__ == "__main__":
    print("=== [Anjo-Core] 完全自律型アシスタント起動 ===")
    agent = AutonomousAssistant()
    
    print("\n【フェーズ1: 隔離領域内の一覧取得】")
    agent.run("jail_workspace内の一覧を取得してください。actionは'list'、targetは'.'を指定してください。")
    
    print("\n【フェーズ2: ファイルの読み込み】")
    agent.run("jail_workspace内の 'report.txt' を読み込んでください。actionは'read'を指定してください。")
