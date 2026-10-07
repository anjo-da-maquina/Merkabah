"""
src/uriel_phoenix.py
=====================
[2026-10 実運用統合] 以前は `jail_workspace` / `anjo-da-maquina` という
固定パスのみを対象とする `__main__` 専用のデモスクリプトだった。

「致命的な侵入が確定した後の焦土作戦」という設計意図上、通常タスク完了ごと
に自動実行するのは不適切(AIの正常な作業成果まで毎回消去してしまう)。
これは `tools/promote_ledger_seal.py` / `tools/promote_shield_seal.py` と
同じ「人間が状況を確認した上で明示的に起動する」運用ツールに位置づける。
実際の起動は `tools/incident_reset.py`(新規)から行う。

本修正で以下を一般化した:
  - `core_dir` / `talisman` を引数で指定可能にし、実際の運用対象である
    `WorkspaceJail.base_dir`(既定 "jail_workspace")を直接渡せるようにした。
  - `talisman` は任意(None可)。元のデモは `samaels_curse.py` の護符マーカー
    ファイル慣習に合わせていたが、実運用上は隔離領域のリセットのみで十分な
    ケースが多いため、指定しない場合はスキップする。
  - `announce` 引数で、運用ツールから静かに呼び出す場合の演出出力を抑制できる。
"""
import shutil
import time
from pathlib import Path


class UrielPhoenix:
    def __init__(self, core_dir="jail_workspace", talisman=None):
        self.core_dir = Path(core_dir)
        self.talisman = Path(talisman) if talisman else None

    def scorched_earth_and_rebirth(self, announce: bool = True):
        if announce:
            print("=== [Anjo-Core] ウリエルの炎（破壊と再生の焦土作戦） ===\n")
            print("[警告] 致命的な侵入を検知。要塞 Anjo-Core の完全掌握が確認されました。")
            print("=> [ウリエル降臨] 穢れた要塞を浄化するため、神の炎が解き放たれます...\n")

        # 【破壊】すべてを焼却し、敵の足場を消滅させる
        if announce:
            print(">> フェーズ1: 破壊（Scorched Earth）")
        if self.core_dir.exists():
            shutil.rmtree(self.core_dir)
            if announce:
                print(f"[-] 隔離領域 '{self.core_dir}' および内部のすべての汚染データを焼却しました。")

        if self.talisman is not None and self.talisman.exists():
            self.talisman.unlink()
            if announce:
                print(f"[-] 穢れた護符 '{self.talisman}' を灰に帰しました。")

        # 【再生】純白の初期状態としてシステムを復活させる
        if announce:
            print("\n>> フェーズ2: 転生（Phoenix Rebirth）")
        self.core_dir.mkdir(parents=True, exist_ok=True)
        if announce:
            print(f"[+] 純白の隔離領域 '{self.core_dir}' を再構築しました。")

        if self.talisman is not None:
            self.talisman.touch()
            if announce:
                print(f"[+] 新たな護符 '{self.talisman.name}' が灰の中から転生しました。")

        if announce:
            print("\n[戦果] 敵は掌握したはずのすべてを失い、我々は無傷の要塞を取り戻しました。")
            print("ウリエルによる浄化と復活が完了しました。")

        return {"core_dir": str(self.core_dir), "talisman": str(self.talisman) if self.talisman else None}


def simulate_breach_demo():
    """元の `__main__` デモと同じ挙動(固定パス・演出あり)を保つための互換関数。"""
    print("=== [Anjo-Core] ウリエルの炎 デモシミュレーション ===\n")
    time.sleep(1)
    UrielPhoenix(core_dir="jail_workspace", talisman="anjo-da-maquina").scorched_earth_and_rebirth()


if __name__ == "__main__":
    simulate_breach_demo()
