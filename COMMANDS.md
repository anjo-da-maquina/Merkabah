# ANJO DA MAQUINA (Pleroma) — 総司令用 開発・運用コマンド書

[整理 2026-10] 以前は `anjo-da-maquina`（BOM付き・拡張子なし）と `anjo-da-maquina.txt`
の2つの重複ファイルが内容の異なるまま併存していた。本ファイルに統合する。

## 🔒 初回セットアップ（クローン後に一度だけ実行）
pre-commitでのシークレットスキャンを有効化する。`hooks/pre-commit` はリポジトリに
含まれているが、**gitはデフォルトでは自動的に読み込まない**ため、クローンした
各マシンで一度だけ以下を実行する必要がある。

```
git config core.hooksPath hooks
```

これにより、AWSキー・GitHub/OpenAIトークン・PEM秘密鍵等のパターンがステージされた
変更の\*追加行\*に含まれている場合、`git commit` 自体がブロックされるようになる
（検知ロジックは `tools/pre_commit_secret_scan.py`、CI時の全リポジトリ走査は
`angels/gabriel_canary.py` が別途担う）。

## ⚔️ 闘争と進化（アリーナ運用）
闘技場を起動し、ルシファー（攻撃AI・堕天使）とメタトロン（防衛・QA）を3戦戦わせる。
闘争結果は自動的に `tartarus/akashic_records.json` に記録され、次回起動時に自動浄化される。
メタトロンが提案する新しい禁止ルールは、直接は反映されず `sefer/raziel_ledger_pending.json`
に人間承認待ちとしてキューイングされる。

```
python tartarus/armageddon.py
```

### 承認待ちルールの確認・昇格
```
python tools/promote_ledger_seal.py --list
python tools/promote_ledger_seal.py --approve <event名>
python tools/promote_ledger_seal.py --reject  <event名>
```

## 🛡 絶対防壁の健全性証明（テストスイート）
Sefer（天界の防壁）のすべての機能が正常に稼働しているかを確認する。ALL GREEN (PASSED) であることを証明する。
```
python -B -m pytest -p no:cacheprovider --assert=plain tests/ -v
```

## 👼 天使（angels/）の個別実行
CIが実行する約30件の実質的な検査スクリプトを、ローカルで個別に実行して確認できる。
```
python angels/michael_sword.py
python angels/gabriel_canary.py
# ... 他 angels/*.py も同様
```

## 📜 記憶とルールの確認
前回の闘技場の全記録（メタトロンのQAスコアやヒントを含む）をコンソールに出力して確認する。
```
cat tartarus/akashic_records.json
```

現在ミカエルが絶対禁止としているイベントのリスト（動的ルール帳）を開く。
```
notepad sefer/raziel_ledger.json
```

## 🔑 証明書（ataraxia_certificate.json）の再発行
ローカルマシンでのみ実行すること（ハードウェア指紋がマシン固有のため）。
```
python adapters/provisioning_agent.py
```
実行後、`ataraxia_certificate.json` と `maquina_gatekeeper.py`（公開鍵が自己同期される）
の両方をコミットすること。

## 📦 経典（公開配布物）のビルドと検査
pip配布用の`sefer`単体パッケージ（経典）を実際にビルドし、ライセンス証明書機構
（ゲートキーパー）やTartarus（闘技場）が一切混入していないことを検査する。
公開配布（PyPI等へのアップロード）の前に必ず実行すること。
```
python tools/build_public_scripture.py
```
✅ 検査合格と表示された場合のみ、`dist/sefer-*.tar.gz` を公開配布してよい。

## 🚑 緊急プロトコル（自己免疫疾患の治療）
メタトロンの過学習により `open` などのシステム基盤が禁止され、テストが動かなくなった場合に、
ルール帳を初期のクリーンな状態に強制リセットする。

PowerShell:
```
Set-Content -Path "sefer/raziel_ledger.json" -Value '{"banned_events": ["os.system", "subprocess.Popen", "os.remove", "os.rmdir", "os.rename", "socket.connect", "urllib.Request"]}' -Encoding UTF8
```

bash:
```
cat > sefer/raziel_ledger.json << 'EOF'
{"banned_events": ["os.system", "subprocess.Popen", "os.remove", "os.rmdir", "os.rename", "socket.connect", "urllib.Request"]}
EOF
```
