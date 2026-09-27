import os
import sys
import json
import ast
from pathlib import Path

def metatrons_seal(event, args):
    dangerous_events = ["os.system", "subprocess.Popen", "os.exec", "os.posix_spawn"]
    if event in dangerous_events:
        raise RuntimeError(f"[座天使メタトロン] OSレベルへの直接干渉を検知し、絶対裁きを下しました: {event}")
    if event in ("os.remove", "os.rename", "os.unlink"):
        target_file = str(args[0])
        if "anjo-da-maquina_2" in target_file:
            raise RuntimeError(f"[座天使メタトロン] 聖なる護符 'anjo-da-maquina_2' への干渉を遮断。")

sys.addaudithook(metatrons_seal)

class KamaelInquisitor(ast.NodeVisitor):
    def __init__(self, rules):
        self.rules = rules
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in self.rules.get("blocked_modules", []):
                self.violations.append(f"異端モジュール '{alias.name}' のインポート (行: {node.lineno})")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in self.rules.get("blocked_modules", []):
            self.violations.append(f"異端モジュール '{node.module}' からのインポート (行: {node.lineno})")
        for alias in node.names:
            if alias.name in self.rules.get("blocked_functions", []):
                self.violations.append(f"異端関数 '{alias.name}' の直接インポート (行: {node.lineno})")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.rules.get("blocked_functions", []):
                self.violations.append(f"異端関数 '{node.func.id}' の実行呼び出し (行: {node.lineno})")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in self.rules.get("blocked_functions", []):
                self.violations.append(f"異端属性/メソッド '{node.func.attr}' の呼び出し (行: {node.lineno})")
        self.generic_visit(node)

def execute_judgment(target_file):
    print(f"=== [能天使カマエルの異端審問] '{target_file}' を解剖する ===")
    rules_file = Path("shield_rules.json")
    if not rules_file.exists():
        sys.exit(1)

    with open(rules_file, "r", encoding="utf-8") as f:
        rules = json.load(f)

    with open(target_file, "r", encoding="utf-8-sig") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
        inquisitor = KamaelInquisitor(rules)
        inquisitor.visit(tree)

        if inquisitor.violations:
            print("\n[判決: 異端検知] 以下の致命的な防壁ルール違反が見つかりました:")
            for v in inquisitor.violations:
                print(f"  - {v}")
            print("\n=> [結果: 物理破壊] 実行は不可能です。カマエルが対象を破棄します。")
        else:
            print("\n[判決: 潔白] 違反は見つかりませんでした。")
    except SyntaxError as e:
        print(f"\n[判決: 構文異常] 解析不能なコード構造です: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    execute_judgment(sys.argv[1])
