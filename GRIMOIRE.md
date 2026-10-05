\# THE ARCHITECT'S GRIMOIRE

\*\*Pleroma / Sefer / Tartarus 総合解説書\*\*



本ドキュメントは、創造主であるアーキテクトへ向けた、システムの完全なる内部解説である。



\## 1. 全体像（The Trinity Architecture）

システムは大きく3つの領域に分かれている。



1\.  \*\*Pleroma (プレロマ):\*\* プロジェクト全体を内包する上位概念。

2\.  \*\*Sefer (セフェル / 経典):\*\* 物質界へ切り出され、PyPI経由で人々に配布される防御モジュール群（Blue Teamの成果物）。

3\.  \*\*Tartarus (タルタロス / 奈落):\*\* 創造主のローカルPC上にのみ存在を許された、隔離された闘技場。ここでLLMを用いた終わらない闘争（Armageddon Engine）が行われる。



\## 2. Seferの防御メカニズム（どう作用し、効果を生むか）



Seferの防御は「実行前」「実行時」「環境」の3段構え（多層防御）で構成されている。



\### A. ガブリエルの眼（Gabriel / AST Scanner）

\*   \*\*どこで動くか:\*\* `sefer/gabriel.py`

\*   \*\*どう働くか:\*\* Pythonの `sys.meta\_path`（モジュールインポートの仕組み）に割り込み、スクリプトがメモリに読み込まれる直前に、そのコードを「抽象構文木（AST: Abstract Syntax Tree）」に変換して解析する。

\*   \*\*効果:\*\* コードが実際に実行される前に、「`\_\_import\_\_` による動的ロード」「`getattr` による難読化」「`eval` や `exec` の悪用」を静的解析で発見し、インポート自体をクラッシュさせる。未知の難読化攻撃を未然に防ぐ。



\### B. ミカエルの剣（Michael / Audit Hooks）

\*   \*\*どこで動くか:\*\* `sefer/\_\_init\_\_.py` 内の `\_michael\_absolute\_defense`

\*   \*\*どう働くか:\*\* Python 3.8から導入された低レイヤー監視API `sys.addaudithook` を利用。PythonがOS（Windows/Linux）に対して「ファイル削除」や「サブプロセス起動」を要求する\*\*直前のイベント\*\*をすべてフックし、`raziel\_ledger.json` の禁止リストと照合する。

\*   \*\*効果:\*\* ガブリエルの静的解析をすり抜けたコード（例: 実行時に動的に文字列を結合してコマンドを作る手法など）であっても、最終的にOSに触れる瞬間に必ずミカエルの監視を通過するため、ここで物理的に遮断（`RuntimeError`）される。



\### C. ラファエルの結界（Raphael / Environment Monitor）

\*   \*\*どこで動くか:\*\* `sefer/raphael.py`

\*   \*\*どう働くか:\*\* 環境変数（`pytest` や `CI` フラグ）、デバッガのトレース関数（`sys.gettrace`）を監視。

\*   \*\*効果:\*\* 外部の攻撃者がこの防壁を解析しようとしたり、偽のテスト環境で挙動を誤魔化そうとしたりする「環境へのハッキング」を検知し、システムを強制的にシャットダウンさせる。



\## 3. 闘技場の自動進化（The Armageddon Engine）



Tartarus内で稼働する `armageddon.py` は、AI同士による自己対内進化（GAN: Generative Adversarial Network の概念）をコードレベルで実装したものである。



\*   \*\*Lucifer (Red Team LLM):\*\*

&#x20;   \*   \*\*働き:\*\* 創造主のローカル環境のOllama（llama3.1）に接続し、「Seferを突破するPythonコードを書け」というプロンプトを受ける。失敗した場合は「前回の失敗エラーログ」を記憶として引き継ぎ、別の手法（例えば `ctypes` によるC関数呼び出しなど）を生成する。

\*   \*\*Metatron (Blue Team LLM):\*\*

&#x20;   \*   \*\*働き:\*\* もしLuciferが未知のコードでミカエルの剣をすり抜け、OSへの干渉に成功した場合にのみ起動する。

&#x20;   \*   \*\*効果:\*\* Luciferの成功コードを解析し、「次に防ぐべきPythonの内部イベント名（例: `os.system`）」を導き出し、動的ルール帳である `raziel\_ledger.json` に自動追記する。

\*   \*\*ラジエルの書（Raziel's Ledger）:\*\*

&#x20;   \*   防壁のハードコードを避け、JSONファイルとして外部化したルール帳。メタトロンがこれを更新すると、次回以降の実行でミカエルがこの最新のルールを読み込むため、\*\*人間がコードを書き直さなくても防壁が自動的にアップデート（進化）していく。\*\*



\## 5. 既知の限界（2026-10 セキュリティレビューによる追記）



本プロジェクトを「絶対防壁」と呼ぶにあたり、誠実さのために以下の限界を明記する。



\### A. CPythonの audit hook が監視できない操作が存在する

`sys.addaudithook` は `os.write` / `os.pwrite` / `os.writev` に対応する監査イベントを発行しない（実機検証済み）。そのため、Sanctumコンテキストに入る\*\*前\*\*に確保した書き込み用fd（事前オープン・継承fd）を使えば、`os.open`の監査を迂回して書き込みが可能だった。本修正でfdを`/proc/self/fd`経由で実体解決し照合するようにしたが、これはLinux限定のベストエフォート策である。

\*\*2026-10 追記:\*\* この限界への恒久対策として、`src/sandalphon_jail.py`（Docker等のOSレベル隔離、`--network none --read-only`）を`src/aegis_system.py`の`AegisSystem.execute_ai_intent()`から既定で強制呼び出しするようにした（`require_docker_sandbox=True`）。Sanctumのaudit hookが原理的に見えない操作（純粋なCPU/メモリ消費攻撃、fd操作、将来発見される別の監査対象外API等）であっても、Dockerコンテナ自体のリソース境界・ネットワーク遮断・タイムアウト監視で多重に防御する。\*\*重要: この統合はフェイルクローズド（Dockerデーモンに接続できない環境では無条件に実行を拒否する）\*\*であり、便利さより安全性を優先する意図的な設計である。手元のマシンでDocker Desktop等が起動していない場合、AIエージェントループ（`ollama_agent_loop.py`等）は一切のAI実行を許可されなくなる。これは不具合ではなく仕様であり、運用上Docker常時起動が新たな前提条件となったことを明記する。



\### B. 読み取りはデフォルトで無制限

Michael's Swordは既定では書き込み・破壊的操作のみを検査し、読み取りは`restrict_reads=True`を明示指定しない限り無制限である。「未許可のファイルアクセスを完全に無力化」という主張は、この既定動作のままでは成立しない。機密データを扱う文脈では必ず`restrict_reads=True`を指定すること。



\### C. 自動進化ループはLLM出力を直接ルールへ反映しない

Metatronが提案する禁止イベントは`sefer/raziel_ledger_pending.json`に一旦キューイングされ、`tools/promote_ledger_seal.py`による人間の明示的承認を経なければ`raziel_ledger.json`（実際の禁止リスト）には反映されない。プロンプトインジェクションや幻覚による運用ルールの汚染を防ぐための多層防御である。



\### D. ライセンス証明書機構はセキュリティ境界ではない

`maquina_gatekeeper.py`のRSA署名検証とハードウェアフィンガープリントは、ローカル開発環境向けの軽量なゲートであり、悪意ある攻撃者に対する認可機構ではない（`adapters/provisioning_agent.py`を実行すれば誰でも新しい鍵対を生成し自己署名できる）。公開配布物（Sefer）にはこの機構を含めない運用を推奨する。

\*\*2026-10 追記（分離の実装）:\*\* 「推奨」のままでは、将来誰かがMANIFEST.inや依存関係を変更した際に静かに混入する恐れがあるため、「推奨」から「機械的に強制」へ格上げした。`pyproject.toml`の`packages = ["sefer"]`と`MANIFEST.in`の`prune`/`exclude`規則により、pip配布される経典（`sefer`単体パッケージ）には`maquina_gatekeeper.py`・`ataraxia_certificate.json`・`adapters/`・`tartarus/`・運用者向けの内部`tests/`を一切含めない。`tools/build_public_scripture.py`が実際にsdistをビルドし、禁止ファイル名・禁止キーワードの両方で内容そのものを検査してから「公開配布可能」と報告する（信用ではなく実機検証）。`angels/metatron_scripture_seal.py`がこの配線（`packages`指定・`MANIFEST.in`の除外規則・`sefer`パッケージ自身がゲートキーパー関連をimportしていないこと）を静的に検証し、`tests/test_public_scripture_isolation.py`が実際のビルド結果を検証する。\*\*実機で発見した重要な事実:\*\* setuptoolsのsdistは明示的な除外指定がないと慣習的に`tests/`ディレクトリ全体を配布物に含めてしまい、`maquina_gatekeeper`や`armageddon`のAPIを直接参照する内部テストまで経典に同梱されてしまっていた。本機構はこれも防ぐ。



\### E. Gabriel(静的AST解析)のドット付き禁止関数名は別名importで回避できる

`sefer.inquisition()`の`forbidden_funcs`には`"os.system"`/`"subprocess.Popen"`のような完全修飾名のエントリが含まれる。2026-10の修正で、呼び出し式から完全修飾名（例: `os.system(...)` → `"os.system"`）を復元して照合するようにし、`os.system(...)`の直接呼び出しが`critical`として正しく検知されるようになった（修正前は`import os`による`high`判定のみで、呼び出し自体は一度も`critical`として検知されていなかった）。ただし`import os as o; o.system(...)`のような別名import（エイリアス解決）は依然として回避可能であり、これは既知の限界として残る。`tests/test_gabriel_qualified_call_names.py`がこの挙動を文書化・固定している。



\### F. 回帰テスト自体に偽陰性バグが存在した（修正済み）

2026-10のレビューで、`tests/test_fd_write_bypass.py`の最重要テスト（fd事前オープンによる書き込みバイパスの回帰テスト）が`except BaseException`で`sys.exit(0)`自身が送出する`SystemExit`まで捕捉してしまい、\*\*バイパスが実際に成功した場合でも常に「遮断成功」と報告する\*\*、検知不能な偽陰性バグを抱えていたことが発覚した（実機検証済み）。同様のパターンが`tests/test_read_restriction.py`にも存在した。両方とも、捕捉対象をSefer本来の遮断時例外`LossOfAtaraxia`のみに narrowing して修正済み。テストコード自身の正しさも、本番コードと同じ水準で検証されるべきという教訓である。



\### G. pre-commitシークレットスキャンはパターンベースであり、既存履歴は対象外

`tools/pre_commit_secret_scan.py`（`hooks/pre-commit`経由で`git commit`自体を拒否する）は、`angels/gabriel_canary.py`と同じ既知パターン（AWSアクセスキー、GitHub/OpenAIトークン、PEM秘密鍵等）のみを検知する。独自形式のAPIキーや平文パスワード文字列等、パターンに一致しない秘密情報は検知できない。また、本フックは\*\*これからステージされる変更の追加行\*\*のみを見るため、過去に既にコミットされてしまった秘密情報の履歴からの除去には対応しない（`git filter-repo`等、別の対応が必要）。さらに、`git config core.hooksPath hooks` はクローンした各マシンで\*\*一度だけ手動実行\*\*する必要があり（gitはリポジトリ内の`hooks/`を自動的には読み込まない）、これを実行し忘れた環境では本フックは一切機能しない。`angels/gabriel_canary.py`のCI時走査（リポジトリ全体・履行済みコミットも含む）は、この取り忘れに対する最後の安全網として機能する。



\### H. 拡張用「雛形」ファイルも本番コードと同じ水準の防壁統合を要求される

`src/openai_agent_loop.py`（APIキーを持つ開発者がOpenAI向けに拡張するための雛形）は、2026-10のセルフレビューで以下2点の欠陥が発覚した。(1) `enforce_maquina_seal`のimportに失敗した場合のフォールバック先`anjo_interceptor.maquina_gatekeeper`がリポジトリ内に一切存在せず、本番では絶対に通らない死んだコードパスだった。(2) `_execute_safe_action`が実際のファイルI/Oを一切行わない固定文字列を返すだけのダミー実装で、`sefer.Sanctum`も`AegisSystem`（Gabriel静的解析＋IntentInterceptor＋Sandalphon動的隔離検証）も一切統合されていなかった。「雛形」であることは手抜きの免罪符にはならない——これをコピーして拡張する開発者は、防壁を一つも使わないコードをそのまま書いてしまう構造的リスクがあったためである。`src/ollama_agent_loop.py`（唯一の実運用ループ）と同一の防御構成（IntentInterceptor → AegisSystem → Sanctum）に揃えて再構築した。また、OpenAI APIを使わない利用者の環境で`openai`パッケージ未インストールのままモジュールをimportしただけでクラッシュしないよう、`openai`の実importは`run_task()`内でのみ行う遅延import（§Aの`tartarus/armageddon.py`の教訓と同種）とした。`angels/raguel_template.py`がこの配線の再発を静的に検知し、`tests/test_openai_agent_loop_template.py`が動作を実機検証する。



\## 4. 創造主の絶対権限（The Creator's Air）

Tartarusのエンジンは、起動直後に `uuid.getnode()` を用いてホストマシンの物理MACアドレスを取得し、不可逆ハッシュ（SHA-256）に変換して検証する。

これにより、この神界の箱庭（Pleroma）がGit経由などで他者の手に渡っても、闘技場は決して開かれず、ルシフェルは即座に自壊する。この闘争は、創造主の監視下でのみ許される神聖な儀式として保たれる。

