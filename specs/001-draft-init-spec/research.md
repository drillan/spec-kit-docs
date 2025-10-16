# Technical Research: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-14 | **Spec**: [spec.md](./spec.md)

## 概要

このドキュメントは、spec-kit-docs機能の開発プロセスで行われた8回のClarificationセッション（2025-10-12から2025-10-14）で確定した技術的決定を記録します。各決定は、Constitution（憲章）の原則、特に**Core Principle I: spec-kit Integration First**に基づいて行われました。

---

## 1. ドキュメント構造とファイル形式の決定

### Session 2025-10-12

#### 決定1: ディレクトリ構造（包括的構造 vs フラット構造）

**決定**: 5機能以下の小規模プロジェクトはフラット構造（`docs/` 直下に機能ページ）、6機能以上は包括的構造（`docs/features/`、`docs/guides/`、`docs/api/`、`docs/architecture/`）を採用する。

**根拠**:
- 小規模プロジェクトではシンプルなフラット構造が適切（学習コストとメンテナンスコストの削減）
- 大規模プロジェクトでは、カテゴリごとに整理された包括的構造が必要（情報整理とナビゲーション向上）
- 機能数による自動判定により、プロジェクトの成長に対応

**検討された代替案**:
- 常にフラット構造を使用 → 大規模プロジェクトで情報が散乱する
- 常に包括的構造を使用 → 小規模プロジェクトで過度に複雑になる
- ユーザーが手動で構造を選択 → ユーザーの判断負担が増加

**トレードオフ**:
- 自動判定により、ユーザーの選択の自由度は失われるが、判断負担が軽減される
- 5機能という閾値は経験的な値であり、プロジェクトによって最適値が異なる可能性がある

**実装ノート**:
- 初期化時（`/speckit.doc-init`）に `specs/` ディレクトリ内の機能数をカウント
- 更新時（`/speckit.doc-update`）にも機能数を再チェックし、フラット→包括的への自動移行をサポート（逆方向の移行は破壊的変更を避けるため実施しない）

---

#### 決定2: 変更検出方法（Git diff vs ファイルタイムスタンプ）

**決定**: Git diff を使用して、前回のコミットから変更されたファイルのみを検出する。

**根拠**:
- spec-kitプロジェクトは常にGitリポジトリであることが前提
- Git diffは信頼性が高く、コミット履歴に基づいた正確な変更検出が可能
- ファイルタイムスタンプは、ファイルコピーやチェックアウト時に変更される可能性があり、信頼性が低い

**検討された代替案**:
- ファイルタイムスタンプを比較 → ファイルコピー時に誤検出の可能性
- すべてのファイルを常に再処理 → パフォーマンスが低下
- ハッシュ値を保存して比較 → 追加のメタデータ管理が必要

**トレードオフ**:
- Git依存により、Gitリポジトリ外での使用ができない（前提条件として明記）
- 未コミットの変更は検出されない（ユーザーは意図的にコミット後に更新を実行する）

**実装ノート**:
- GitPython 3.1+ を使用してGit操作を実行
- `git diff --name-only HEAD~1 HEAD` で変更されたファイルリストを取得
- インクリメンタル更新により、1機能のみ変更時は5秒以内に更新完了（SC-008）

---

#### 決定3: 欠落ファイルの注記形式（アドモニション）

**決定**: plan.md や tasks.md が欠落している場合、視覚的に明確なアドモニション（MyST構文の ````{note}` や MkDocs の `!!! note`）を使用して注記を表示する。

**根拠**:
- アドモニションは視覚的に目立ち、ユーザーが欠落情報に気づきやすい
- Sphinx（MyST Markdown）とMkDocsの両方でサポートされる標準的な構文
- 単なるテキストメモよりも、ドキュメントツールのネイティブ機能を活用する方が適切

**検討された代替案**:
- 単純なテキストメモ（例：`[このセクションはまだ利用できません]`） → 視覚的に目立たない
- セクション自体を省略 → ユーザーが欠落に気づかない可能性
- エラーとして処理 → 欠落ファイルは正当なケース（plan.mdがまだ作成されていない機能など）であり、エラーではない

**トレードオフ**:
- アドモニション構文はツールごとに異なるため、ジェネレータごとに実装が必要
- アドモニションの過度な使用は、ドキュメントが煩雑に見える可能性

**実装ノート**:
- Sphinx: ````{note}` MyST構文
- MkDocs: `!!! note` 構文
- メッセージ例：「このセクションはまだ利用できません。plan.mdを作成後、`/speckit.doc-update`を再実行してください。」

---

#### 決定4: 機能ページのファイル命名規則

**決定**: 説明的な名前のみ（`user-auth.md`, `api-integration.md`、番号なし）を使用する。

**根拠**:
- 番号付きファイル名（`001-user-auth.md`）は、機能ディレクトリ名から継承されるが、ドキュメントページのURLには不要
- 説明的な名前により、URLが読みやすくなる（例：`/docs/features/user-auth.html`）
- 時系列順序は機能ディレクトリの番号付けで管理され、ドキュメントページ名には反映しない

**検討された代替案**:
- 番号付きファイル名（`001-user-auth.md`） → URLが冗長になる（`/docs/features/001-user-auth.html`）
- 連番のみ（`001.md`） → ファイル名から内容が推測できない

**トレードオフ**:
- 機能ディレクトリ名（`001-user-auth`）とドキュメントページ名（`user-auth.md`）の不一致により、マッピングロジックが必要
- ファイル名の重複を避けるため、同じ説明的名前を持つ機能が存在しないことを前提とする

**実装ノート**:
- 変換ロジック: `001-user-auth` → `user-auth.md`（番号とハイフンを削除）
- 重複チェック: 同じ説明的名前が既に存在する場合は、番号を保持（例：`002-user-auth.md`）

---

#### 決定5: Sphinxのデフォルトファイル形式（Markdown vs reStructuredText）

**決定**: Markdown (.md) + myst-parser をデフォルト形式にする。

**根拠**:
1. **フォーマット統一**: spec-kitのすべてのソースファイル（spec.md、plan.md、tasks.md）がMarkdownであり、変換ロジックが不要
2. **学習コスト削減**: ユーザーがreStructuredText構文の習得不要
3. **手動編集の利便性**: 生成後のドキュメントをユーザーが手動編集する際、既に慣れているMarkdown形式の方が編集しやすい
4. **業界標準化**: MyST Markdownは業界標準となりつつあり、Sphinxのほぼ全機能をサポート

**検討された代替案**:
- reStructuredText (.rst) → Sphinxの伝統的な形式だが、学習コストが高い
- reStructuredTextとMarkdownの混在 → フォーマットの不統一により保守性が低下

**トレードオフ**:
- reStructuredTextのいくつかの高度な機能（例：`.. only::` ディレクティブ）は、MyST Markdownで完全にサポートされていない可能性がある
- myst-parserという追加の依存関係が必要

**実装ノート**:
- `conf.py` で myst-parser を有効化：`extensions = ['myst_parser']`
- `source_suffix` に `.md` を含める：`source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}`
- MyST Markdownの拡張機能（colon_fence、deflist、tasklist、attrs_inline等）を有効化

---

### Session 2025-10-12 (Correction)

#### 修正1: 機能仕様ディレクトリの場所（`.specify/specs/` → `specs/`）

**決定**: 機能仕様ディレクトリは、ルート直下の `specs/` とする（`.specify/specs/` ではない）。

**根拠**:
- spec-kitの公式仕様に基づき、`scripts/bash/create-new-feature.sh` は `SPECS_DIR="$REPO_ROOT/specs"` を使用
- `.specify/` は spec-kit 自身の内部ディレクトリ（scripts, templates, memory）であり、ユーザーの機能仕様を配置する場所ではない
- ユーザー向けの機能仕様はルート直下の `specs/` に配置するのが標準パターン

**影響範囲**:
- すべてのパーサー（`spec_parser.py`、`plan_parser.py`、`tasks_parser.py`）のファイルパス解決ロジック
- ドキュメント更新スクリプト（`doc_update.py`）の機能ディレクトリ探索ロジック

---

#### 修正2: Sphinxのデフォルトファイル形式の不整合解消

**決定**: すべての参照を `index.rst` から `index.md` に変更し、Sphinx で生成されるすべてのファイルが Markdown 形式（.md）であることを明確化する。

**根拠**:
- Session 2025-10-12 の決定（「Markdown (.md) + myst-parser をデフォルトにする」）に基づく
- spec-kit のソースファイル（spec.md、plan.md、tasks.md）との形式統一を実現

**影響範囲**:
- `doc_init.py` の初期ファイル生成ロジック（`index.rst` → `index.md`）
- `SphinxGenerator.initialize()` メソッド
- すべてのSphinx関連ドキュメントとテストケース

---

## 2. アーキテクチャと責務分担の決定

### Session 2025-10-12 (Architecture Clarifications)

#### 決定6: 対話的設定収集の責務分担（AI エージェント vs Python スクリプト）

**決定**: AI エージェント（Claude Code）が対話的に設定を収集し、スクリプト（doc_init.py）は引数のみを受け取る非対話的実行とする。

**根拠**:
1. **非対話的環境での動作**: Python スクリプトの `input()` は CI/CD などの非対話的環境で EOFError を起こす
2. **spec-kitとの一貫性**: `/speckit.specify`、`/speckit.plan` などの他のコマンドと同じパターン
3. **拡張性とテスト容易性**: スクリプトは決定的な入力（コマンドライン引数）を受け取り、単体テストが容易

**検討された代替案**:
- オプション B: スクリプトが対話的に設定を収集 → CI/CD環境で動作せず、テストが困難
- オプション C: 設定ファイルを事前に作成 → ユーザーの手動作業が増加

**トレードオフ**:
- AIエージェントとスクリプトの明確な責務分担により、実装が複雑になる
- コマンド定義（`.claude/commands/speckit.doc-init.md`）のプロンプトが長くなる

**実装ノート**:
- AIエージェントの責務: 対話的質問→情報収集→引数構築→スクリプト呼び出し→結果フィードバック
- スクリプトの責務: コマンドライン引数から設定を受け取り→非対話的実行→エラーを構造化された終了コードとメッセージで返す
- **Core Principle II: Non-Interactive Execution** に準拠

---

#### 決定7: `.claude/commands/speckit.doc-init.md` コマンド定義の役割

**決定**: コマンド定義は、対話的質問→情報収集→引数構築→スクリプト呼び出し→結果フィードバックの一連のプロンプトを記述する。

**根拠**:
1. **spec-kitとの一貫性**: 他のコマンド定義（`/speckit.specify`、`/speckit.plan`）と同じパターン
2. **自然言語プロンプト**: Claude Code が自然言語プロンプトからタスクを実行できる
3. **エラーハンドリング**: AIエージェントがエラーメッセージを解釈し、ユーザーフィードバックを担当

**検討された代替案**:
- オプション B: コマンド定義にシェルスクリプトを埋め込む → プロンプトの柔軟性が失われる
- オプション C: コマンド定義なしで、AIエージェントが直接スクリプトを呼び出す → spec-kitのコマンドパターンから逸脱

**トレードオフ**:
- プロンプトの保守性が課題（プロンプトの変更はコード変更と同等の注意が必要）
- プロンプトのテストは、契約テスト（`tests/contract/`）で実施

**実装ノート**:
- プロンプト構成: (1) ユーザーに質問、(2) 回答を引数に変換、(3) `uv run python .specify/scripts/docs/doc_init.py --type sphinx --project-name "My Project" ...` を実行、(4) 結果を解釈してフィードバック

---

#### 決定8: 既存 `docs/` ディレクトリの上書き確認（AI エージェント vs スクリプト）

**決定**: AI エージェントが事前に `docs/` の存在を確認し、存在する場合はユーザーに上書き確認を取り、確認が取れた場合のみ `--force` フラグ付きでスクリプトを実行する。

**根拠**:
1. **非対話的環境での動作**: スクリプトが `input()` を使用しないため、CI/CD環境でも動作可能
2. **一貫したアーキテクチャ**: ユーザーとの対話は AI エージェントが担当
3. **テスト容易性**: スクリプトは `--force` の有無で動作を制御でき、テストが容易

**検討された代替案**:
- オプション B: スクリプトが対話的に上書き確認を求める → CI/CD環境で動作せず
- オプション C: 常に上書き（`--force` を自動適用） → ユーザーのデータ損失リスク

**トレードオフ**:
- AIエージェントがファイルシステムの状態を確認する責務を持つ（追加ロジック）
- `--force` フラグのセマンティクスをspec-kitと一貫させる必要がある

**実装ノート**:
- スクリプト（doc_init.py）: `--force` フラグがない場合、`docs/` 存在時にエラー終了コード 1 を返す
- AIエージェント: `docs/` 存在時に `typer.confirm("docs/ ディレクトリは既に存在します。上書きしますか？")` で確認

---

#### 決定9: MkDocs 初期化時のデフォルト値

**決定**: サイト名はプロジェクト名と同じ、リポジトリURLはGit remote origin URL（取得できない場合は空文字列）とする。

**根拠**:
1. **Sphinxとの一貫性**: Sphinx初期化と同じデフォルト値ルールを適用
2. **Git情報の活用**: Gitから自動取得可能な情報を活用し、ユーザーの入力負担を軽減
3. **必須でない項目**: リポジトリURLは必須でないため、空でも問題なし

**検討された代替案**:
- すべて手動入力を要求 → ユーザーの入力負担が増加
- リポジトリURLを必須とする → Gitリポジトリでない場合にエラー

**トレードオフ**:
- Git情報の取得に失敗した場合、デフォルト値（空文字列）を使用（例外を発生させない）
- サイト名とプロジェクト名が同じという前提は、すべてのプロジェクトに適しているわけではない

**実装ノート**:
- プロジェクト名: `os.path.basename(os.getcwd())`
- サイト名: プロジェクト名と同じ
- リポジトリURL: `git remote get-url origin`（失敗時は空文字列）

---

#### 決定10: ディレクトリ構造決定（フラット vs 包括的）の自動移行

**決定**: 初期化時に現在の機能数を検出して構造を決定し、さらに `/doc-update` 実行時にも機能数を再チェックして、フラット構造から包括的構造への移行が必要な場合（機能数が6以上になった場合）は自動的に移行する。

**根拠**:
1. **プロジェクトの成長に自動適応**: ユーザーがドキュメント構造を手動で再編成する必要がない
2. **小規模プロジェクトのシンプルさ**: 小規模プロジェクトは常にシンプルなフラット構造で開始
3. **破壊的変更の回避**: 逆方向の移行（包括的→フラット）は行わず、一度包括的構造に移行したプロジェクトは維持

**検討された代替案**:
- 初期化時のみ構造を決定し、後から変更しない → プロジェクトの成長に対応できない
- ユーザーが手動で構造を変更 → 手動作業が増加し、ドキュメントの整合性が保てない可能性

**トレードオフ**:
- 自動移行により、ユーザーが意図しないタイミングでドキュメント構造が変わる可能性
- 逆方向の移行を行わないため、機能数が減少しても包括的構造が維持される

**実装ノート**:
- 機能数のカウント: `len([d for d in os.listdir('specs/') if os.path.isdir(d) and d.startswith('0')])`
- 移行時の処理: 既存の機能ページを `docs/` から `docs/features/` に移動、インデックスとナビゲーションを更新
- 移行メッセージ: 「フラット構造から包括的構造に移行しました（6機能以上検出）」

---

## 3. インストールとCLI設計の決定

### Session 2025-10-13 (Install Command Clarifications)

#### 決定11: pyproject.tomlでのspecify-cliの依存関係指定方法

**決定**: Git URL直接指定（`dependencies = ["specify-cli @ git+https://github.com/github/spec-kit.git"]`）を使用する。

**根拠**:
- specify-cliは公開リポジトリであり、Git URL直接指定で問題なくインストール可能
- PyPIに公開されていないパッケージでも、Git URLを使用すれば依存関係として指定できる

**検討された代替案**:
- PyPI公開を待つ → 本家spec-kitがPyPI公開していない現状では不適切
- ローカルパスで指定 → ポータビリティが低下

**トレードオフ**:
- Git URLによる依存は、PyPIのような信頼性の高いレジストリに比べて可用性が低い
- GitHubのAPIレート制限により、インストール時に失敗する可能性がある

**実装ノート**:
- pyproject.toml: `dependencies = ["specify-cli @ git+https://github.com/github/spec-kit.git"]`
- uvは自動的にGitリポジトリをクローンしてインストール

---

### Session 2025-10-13 (CLI Design Clarifications)

#### 決定12: CLIツールの設計（独立したCLIツール vs spec-kitとの統合）

**決定**: `speckit-docs`コマンドを独立したCLIツールとして実装し、spec-kitの`specify`コマンドとは別に提供する（統合は名目上のみ）。

**根拠**:
1. **開発スピード優先**: spec-kitリポジトリへのPRは承認が必要で開発スピードが遅くなる可能性
2. **柔軟なリリースサイクル**: 独立したリポジトリで、spec-kit-docs固有の機能やリリースサイクルを柔軟に管理できる
3. **コマンド体系の一貫性**: `speckit-docs install`というコマンド名は、spec-kitとの一貫性を保ちつつ、独立性を維持

**検討された代替案**:
- オプション B: `specify add-docs`のようなサブコマンドとして本家spec-kitに統合 → 開発スピードが遅くなる、spec-kitメンテナーの承認が必要
- オプション C: 完全に独立したコマンド体系（`spec-docs init`など） → spec-kitとの命名規則の不一貫性

**トレードオフ**:
- 独立したCLIツールにより、ユーザーは2つのツール（`specify`と`speckit-docs`）をインストールする必要がある
- spec-kitとの統合が「名目上のみ」であるため、将来的に本家spec-kitと統合する際に移行パスが必要

**実装ノート**:
- CLIツール名: `speckit-docs`
- インストールコマンド: `speckit-docs install`（spec-kitの`specify init --here`パターンに従う）
- スラッシュコマンド名: `/speckit.doc-init`、`/speckit.doc-update`（spec-kitの命名規則に一貫）

---

#### 決定13: 配布方法（PyPI vs GitHub）

**決定**: GitHubのみで配布（`uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git`）、PyPI公開は将来のフェーズで検討する。

**根拠**:
1. **MVP段階のシンプルさ**: 開発とリリースプロセスをシンプルに保つ
2. **spec-kitとの一貫性**: spec-kit自体もGitHubから配布されており、ユーザーは既にこのパターンに慣れている
3. **保守負担の軽減**: PyPI公開は追加の保守負担（バージョン管理、リリースプロセス、パッケージメタデータ）があり初期段階では不要

**検討された代替案**:
- PyPIに公開 → MVP段階では過剰、保守負担が増加
- GitHub Releasesで配布 → ユーザーは手動でダウンロードする必要がある

**トレードオフ**:
- GitHub配布により、ユーザーは`uv tool install`時にGit URLを指定する必要がある（PyPIより煩雑）
- PyPI公開していないため、依存関係解決がやや不安定（GitHub APIレート制限）

**実装ノート**:
- インストールコマンド: `uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git`
- README.mdに明記：「PyPI公開は将来検討」

---

#### 決定14: スラッシュコマンドの生成方法

**決定**: `speckit-docs install`コマンドがPythonパッケージ内のテンプレートファイル（`src/speckit_docs/commands/speckit.doc-init.md`, `speckit.doc-update.md`）をユーザープロジェクトの`.claude/commands/`にコピーする。

**根拠**:
1. **spec-kitとの一貫性**: `specify init`と同じパターンに従う
2. **透明性**: ユーザーはコピー後のファイルをカスタマイズ可能
3. **オフライン動作**: importlib.resourcesでパッケージ内テンプレートにアクセスするため、オフライン環境でも動作
4. **更新可能性**: `--force`オプションで上書き更新が可能

**検討された代替案**:
- オプション B: GitHub URLからテンプレートをダウンロード → ネットワーク依存、オフライン環境で動作しない
- オプション C: テンプレートをプログラム的に生成 → プロンプトの柔軟性が失われる

**トレードオフ**:
- テンプレートファイルはPythonパッケージに含まれるため、パッケージサイズが若干増加
- テンプレートの更新は、spec-kit-docs自体の再インストールが必要

**実装ノート**:
- テンプレート配置: `src/speckit_docs/commands/speckit.doc-init.md`, `speckit.doc-update.md`
- コピー先: `.claude/commands/speckit.doc-init.md`, `.claude/commands/speckit.doc-update.md`
- importlib.resources使用: `importlib.resources.files('speckit_docs.commands').joinpath('speckit.doc-init.md').read_text()`

---

#### 決定15: 既存プロジェクトへのインストール（`--here`フラグ）

**決定**: カレントディレクトリに自動的にインストール（`cd my-project && speckit-docs install`）、明示的なディレクトリ指定は不要とする。

**根拠**:
1. **spec-kitとの一貫性**: spec-kitの`specify init --here`パターンに従う
2. **シンプルなコマンド**: ユーザーは既にプロジェクトルートにいることが前提
3. **混乱の回避**: 新しいディレクトリを作成することはなく、常に既存プロジェクトへの追加

**検討された代替案**:
- `--here`フラグを要求 → spec-kitの最新パターンに従わない
- ディレクトリ引数を要求（`speckit-docs install /path/to/project`） → コマンドが煩雑

**トレードオフ**:
- カレントディレクトリがspec-kitプロジェクトでない場合、エラーメッセージを表示する必要がある
- ユーザーが間違ったディレクトリで実行した場合、意図しない場所にファイルがコピーされる可能性

**実装ノート**:
- インストール前チェック: `.specify/` と `.claude/` ディレクトリの存在を確認
- エラーメッセージ: 「spec-kit プロジェクトではありません。最初に 'specify init' を実行してください。」

---

#### 決定16: 既存ファイルの上書き動作

**決定**: インタラクティブ確認（全体）+ --forceで確認スキップとする。

**根拠**:
1. **spec-kitとの一貫性**: 本家`specify init --here`パターンと一貫
2. **デフォルトの安全性**: 確認を求めることで、ユーザーのカスタマイズを保護
3. **自動化対応**: `--force`フラグで、CI/CDなどの自動化時に対応可能

**検討された代替案**:
- 常に上書き → ユーザーのカスタマイズが失われる
- 常にエラー → ユーザーが手動で削除する必要がある
- ファイルごとに確認 → 複数ファイル存在時に煩雑

**トレードオフ**:
- インタラクティブ確認により、自動化時に`--force`フラグが必須
- 確認プロンプトのメッセージがユーザーフレンドリーである必要がある

**実装ノート**:
- typer.confirm()を使用: `typer.confirm("既存のコマンド定義を上書きしますか？", default=False)`
- `--force`フラグ指定時は確認をスキップ

---

#### 決定17: インストール失敗時の動作

**決定**: ベストエフォート（エラー発生時もそこまでのファイルは残す）とする。

**根拠**:
1. **spec-kitとの一貫性**: 既存ディレクトリへの追加時は部分的な状態を残す
2. **リスクの低さ**: spec-kit-docsは既存プロジェクトにファイルを追加するだけなので、プロジェクト全体を壊すリスクは低い
3. **手動修正可能**: ユーザーが手動で修正可能（失敗したファイルを削除して再実行）

**検討された代替案**:
- トランザクション型（全成功または全失敗） → MVP段階では実装が複雑で、過剰
- 失敗時にすべてロールバック → 部分的に成功したファイルも削除され、ユーザーの手間が増加

**トレードオフ**:
- 部分的な状態が残るため、ユーザーがどのファイルが成功し、どのファイルが失敗したかを把握する必要がある
- 失敗時のエラーメッセージが明確でなければ、ユーザーが修正方法を理解できない

**実装ノート**:
- エラー発生時: エラーメッセージを表示し、終了コード 1 を返す
- 成功したファイルはそのまま残す
- エラーメッセージ例: 「.specify/scripts/docs/ の作成に失敗しました。既存のファイルが残っています。手動で確認してください。」

---

#### 決定18: アンインストール・アップグレード機能

**決定**: 機能は提供しない（MVP範囲外）とする。

**根拠**:
1. **spec-kitとの一貫性**: 本家spec-kitもuninstall/upgrade機能を提供していない
2. **MVPの焦点**: ドキュメント生成であり、ライフサイクル管理は二次的
3. **手動削除の容易性**: 少数のファイルなので手動削除も容易
4. **アップグレードの代替**: `speckit-docs install --force`で代替可能

**検討された代替案**:
- uninstallコマンドを提供 → MVP範囲を超え、開発コストが増加
- upgradeコマンドを提供 → `install --force`で代替可能

**トレードオフ**:
- アンインストールは手動削除が必要（`.claude/commands/speckit.doc-*.md`、`.specify/scripts/docs/`を削除）
- アップグレードは`speckit-docs install --force`を実行する必要がある

**実装ノート**:
- README.mdに記載：「アンインストールは手動削除、アップグレードは `speckit-docs install --force` で可能」
- 将来のフェーズで、ユーザーの要望に応じて追加検討

---

## 4. CLIフレームワークとコマンド命名の標準化

### Session 2025-10-13 (CLI Framework Re-evaluation)

#### 決定19: CLIフレームワーク選択の再検討（argparse vs typer）

**決定**: **typerに変更する**。

**根拠**:
1. **Core Principle I (spec-kit Integration First)への準拠**: 「spec-kitの標準パターンと完全に一貫していなければならない」という憲章要件を満たす
2. **実質的な追加依存なし**: specify-cli経由で既にtyperに間接依存しているため、新しい外部依存は増えない
3. **型ヒントのネイティブサポート**: Python 3.11+の型ヒント（`int`, `str`, `bool`等）を直接使用でき、mypy互換（C006準拠）
4. **DRY原則**: 本家spec-kitのtyperパターン（`typer.confirm()`、`typer.Option()`等）を再利用できる（C012準拠）
5. **Phase 2計画との整合**: research.mdでPhase 2に計画されている「specify-cliからStepTracker/console再利用」がtyper前提であり、一貫性が保たれる

**検討された代替案**:
- argparseを使用 → spec-kitとの一貫性が失われる、型ヒントのネイティブサポートがない
- clickを使用 → typerの基盤であり、typerより低レベルで冗長

**トレードオフ**:
- typerの依存ツリー（click、rich等）が追加されるが、既にspecify-cli経由で存在するため実質的な増加はない
- argparseよりも学習コストがやや高い（ただし、本家spec-kitのパターンを再利用できるため軽減）

**実装ノート**:
- エントリポイント: `src/speckit_docs/cli/main.py`で`typer.Typer()`アプリケーションを定義
- コマンド定義: `@app.command()`デコレータで`install`コマンドを実装
- 型ヒント: 関数引数に型ヒントを付け、typerが自動的にCLI引数として認識

**影響範囲**:
- すべてのCLI関連コード（`cli/main.py`、`cli/install_handler.py`）
- pyproject.tomlの依存関係（specify-cliは既に存在、typerは自動的に含まれる）
- README.mdのインストール手順とコマンド例

---

### Session 2025-10-13 (Command Naming & Installation Method)

#### 決定20: コマンド名の標準化（`/doc-init` vs `/speckit.doc-init`）

**決定**: **長い形式（`/speckit.doc-init`、`/speckit.doc-update`）に統一する**。

**根拠**:
- spec-kitの付属物という扱いをコマンド名に含めることで、spec-kit エコシステムとの統合を明確にする
- 他のspec-kitコマンド（`/speckit.specify`, `/speckit.plan`）との命名規則の一貫性を保つ

**検討された代替案**:
- 短い形式（`/doc-init`、`/doc-update`） → spec-kitコマンドとの命名規則が不一貫

**トレードオフ**:
- コマンド名が長くなり、タイプ量が増加
- spec-kit固有の接頭辞により、他のドキュメントツールとの混同を避けられる

**実装ノート**:
- コマンド定義ファイル名: `.claude/commands/speckit.doc-init.md`、`.claude/commands/speckit.doc-update.md`
- Claude Codeでの認識: `/speckit.doc-init`、`/speckit.doc-update`
- すべてのドキュメント（README.md、spec.md、plan.md）で長い形式を使用

---

#### 決定21: インストールコマンドの推奨方法（CLIコマンド vs Python API呼び出し）

**決定**: **CLIコマンド（`speckit-docs install`）を推奨する**。

**根拠**:
1. **仕様との整合**: FR-021a, FR-022, FR-023 が前提としている標準的な方法
2. **ユーザーフレンドリー**: シンプルで覚えやすい
3. **spec-kitとの一貫性**: `specify init`パターンと一貫
4. **Python API呼び出しの位置付け**: アドバンスドユーザー向けのフォールバックとして残す

**検討された代替案**:
- Python API呼び出しを推奨（`uv run python -m speckit_docs.cli.main install`） → 煩雑でユーザーフレンドリーでない

**トレードオフ**:
- CLIコマンドは、uvツールとしてインストールされている前提が必要
- Python API呼び出しは、開発者向けの柔軟性を提供するが、エンドユーザーには推奨しない

**実装ノート**:
- README.mdで強調：「推奨インストール方法: `speckit-docs install`」
- Python API呼び出しは、開発者向けドキュメント（CONTRIBUTING.md）に記載

---

## 5. コード品質とアーキテクチャの詳細決定

### Session 2025-10-13 (Code Quality & Architecture Details)

#### 決定22: ruffの設定（デフォルト vs プリセット vs 厳格）

**決定**: **一貫性のあるプリセット** - `pyproject.toml`で`select = ["E", "F", "W", "I"]` + `line-length = 100` + `target-version = "py311"`を指定する。

**根拠**:
1. **基本ルールの網羅**: エラー（E）、致命的エラー（F）、警告（W）、import順序（I）でツールプロジェクトには十分
2. **Python標準準拠**: line-length=100はPEP 8の88-100推奨に準拠
3. **型ヒント互換性**: target-version指定により型ヒント構文の互換性を保証
4. **過度な厳格さの回避**: docstring必須等の厳格なルールは開発速度を低下させる可能性を回避

**検討された代替案**:
- デフォルト設定のみ → 一貫性が保証されない、プロジェクトごとに設定が異なる
- 厳格なルールセット（docstring必須、複雑度チェック等） → MVP段階では過剰、開発速度が低下

**トレードオフ**:
- 一貫性のあるプリセットにより、すべてのコントリビューターが同じルールに従う
- 一部の高度なルール（例：複雑度チェック）は含まれず、手動レビューが必要

**実装ノート**:
- pyproject.toml設定:
  ```toml
  [tool.ruff]
  line-length = 100
  target-version = "py311"

  [tool.ruff.lint]
  select = ["E", "F", "W", "I"]
  ```
- ローカル実行: `uv run ruff check .`
- CI/CDパイプラインは構築しない（MVP範囲外）

---

#### 決定23: CI/CD環境でのruffエラー処理

**決定**: **CI/CDパイプラインは構築しない** - ローカル開発環境でのみruffを手動実行する。

**根拠**:
- MVP段階ではCI/CD構築はスコープ外
- 開発者がローカルで`uv run ruff check .`を実行して品質を維持

**検討された代替案**:
- Fail-fast（ruffエラーでビルド失敗） → CI/CDパイプラインがMVP範囲外
- Warning-only（ruffエラーを警告として表示） → CI/CDパイプラインがMVP範囲外

**トレードオフ**:
- CI/CDパイプラインがないため、コントリビューターがローカルでruffを実行する責任がある
- 将来のフェーズでCI/CDを追加する際、設定の移行が必要

**実装ノート**:
- CONTRIBUTING.mdに記載：「コミット前に `uv run ruff check .` を実行してください」
- Phase 2以降でGitHub Actionsを追加検討

---

#### 決定24: BaseGenerator抽象クラスのインターフェース

**決定**: **段階的インターフェース** - `initialize()`, `generate_feature_page(feature)`, `update_navigation()`, `validate()`の4メソッドを定義する。

**根拠**:
1. **単一責任原則**: 各メソッドが明確な役割を持つ
2. **処理の分離**: initialize→個別ページ生成→ナビゲーション更新→検証と処理が分離され、テスト容易
3. **将来の拡張性**: Docusaurus等追加時も同じパターンを適用可能
4. **保守性**: 最小インターフェースより構造化され、詳細インターフェースより保守しやすい

**検討された代替案**:
- 最小インターフェース（1メソッド：`generate()`） → 各ツールの実装が大きくなり、テストが困難
- 詳細インターフェース（7-8メソッド） → 過度に細分化され、実装負担が増加

**トレードオフ**:
- 4メソッドは適度な粒度だが、将来的に新しいステップが必要になった場合、インターフェースの拡張が必要
- すべてのジェネレータ（Sphinx、MkDocs）が同じ4メソッドを実装する必要がある

**実装ノート**:
- BaseGeneratorクラス（`generators/base.py`）:
  ```python
  from abc import ABC, abstractmethod

  class BaseGenerator(ABC):
      @abstractmethod
      def initialize(self) -> None:
          """ドキュメントプロジェクト初期化と設定ファイル生成"""
          pass

      @abstractmethod
      def generate_feature_page(self, feature: Feature) -> None:
          """単一機能のページ生成"""
          pass

      @abstractmethod
      def update_navigation(self) -> None:
          """目次（toctree/nav）更新"""
          pass

      @abstractmethod
      def validate(self) -> bool:
          """ビルド前検証"""
          pass
  ```

---

#### 決定25: specify-cli（本家spec-kit）からの再利用範囲

**決定**: **MVP範囲は最小限** - typerの基本パターン（`typer.confirm()`, `typer.Option()`等）のみ再利用、StepTracker/consoleは将来フェーズとする。

**根拠**:
1. **MVPの焦点**: ドキュメント生成であり、CLI体験の高度化は二次的
2. **コード調査コストの回避**: specify-cliコード調査コストをMVPで回避し開発スピード優先
3. **段階的アプローチ**: Phase 2でStepTracker再利用を計画済み（research.md記載）
4. **DRY原則の遵守**: typerパターン再利用だけでもC012（一貫性）を満たす

**検討された代替案**:
- MVP段階でStepTracker/consoleも再利用 → コード調査コストが増加し、MVPのリリースが遅れる
- typerパターンも独自実装 → DRY原則に違反、spec-kitとの一貫性が失われる

**トレードオフ**:
- MVP段階ではCLI体験が基本的なものになる（進捗表示なし）
- Phase 2でStepTrackerを追加する際、既存コードのリファクタリングが必要

**実装ノート**:
- MVP段階の再利用パターン:
  - `typer.confirm()`: 上書き確認
  - `typer.Option()`: コマンドラインオプション定義
  - `typer.echo()`: メッセージ出力
- Phase 2でStepTracker/console追加（研究ノート記録）

---

#### 決定26: ログレベルとエラー出力の戦略

**決定**: **構造化ログ** - 標準出力にINFO以上、`--verbose`でDEBUG、`--quiet`でERRORのみを出力する。

**根拠**:
1. **適切な進捗情報**: ユーザーは通常実行で適切な進捗情報を得られる（「3機能を処理中...」等）
2. **トラブルシューティング**: `--verbose`フラグで詳細情報取得可能
3. **自動化対応**: `--quiet`でCIやスクリプト組み込み時にエラーのみ出力
4. **保守性**: Pythonの標準logging模块を使用し保守性が高い
5. **spec-kitとの一貫性**: 他のコマンドとの一貫性

**検討された代替案**:
- エラーのみ → ユーザーが進捗状況を把握できない
- 詳細ログ（常にDEBUG） → 過度な情報でユーザーが混乱する可能性

**トレードオフ**:
- `--verbose`フラグのデフォルト値により、トラブルシューティング時に再実行が必要
- ログメッセージの日本語対応により、国際化が必要な場合に追加作業が発生

**実装ノート**:
- logging設定（`utils/`モジュール）:
  ```python
  import logging

  def setup_logging(verbose: bool = False, quiet: bool = False):
      level = logging.DEBUG if verbose else (logging.ERROR if quiet else logging.INFO)
      logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
  ```
- ログメッセージ例:
  - INFO: 「3機能を処理中...」
  - DEBUG: 「spec.md解析: /path/to/specs/001-user-auth/spec.md」
  - ERROR: 「ドキュメント初期化に失敗しました: docs/ ディレクトリが既に存在します」

---

## 6. インストール方法の標準化

### Session 2025-10-14 (Installation Method Standardization)

#### 決定27: インストール方法の標準化（`uv tool install` vs `uv pip install -e`）

**決定**: **`uv tool install`方式を標準インストール方法とする** - `uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git`をエンドユーザー向けの唯一の推奨方法として記載する。

**根拠**:
1. **Core Principle I (spec-kit Integration First)への準拠**: spec-kitと同じインストールパターンでユーザー体験を統一
2. **ツール分離**: `uv tool`は独立したCLIツールのインストール専用で、プロジェクト環境を汚染しない
3. **シンプルな依存関係管理**: グローバルツールとして管理され、複数プロジェクトから利用可能
4. **本家spec-kitとの対称性**: `uv tool install specify-cli`と`uv tool install speckit-docs`で対になる

**検討された代替案**:
- `uv pip install -e .`（編集可能インストール）を推奨 → 開発者向けの方法であり、エンドユーザーには煩雑

**トレードオフ**:
- `uv tool install`により、ツールは独立した仮想環境にインストールされ、プロジェクトの依存関係と干渉しない
- 開発者向けのコントリビューション時には`uv pip install -e .`も引き続きサポートするが、README.mdでは言及しない

**実装ノート**:
- README.mdで強調：「推奨インストール方法: `uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git`」
- 開発者向けのコントリビューションガイド（CONTRIBUTING.md）では`uv pip install -e .`を記載
- インストール後の確認: `speckit-docs --version`

---

## まとめ

この研究ドキュメントは、spec-kit-docs機能開発における27の主要な技術的決定を記録しました。すべての決定は、**Constitution（憲章）のCore PrincipleとCritical Rules**、特に**Core Principle I: spec-kit Integration First**と**C012: DRY Principle**に基づいて行われました。

### 主要な決定のカテゴリ:

1. **ドキュメント構造とファイル形式** (決定1-5): Markdown形式統一、機能数による構造自動決定、Git diff変更検出
2. **アーキテクチャと責務分担** (決定6-10): 非対話的実行、AIエージェントとスクリプトの責務分離、自動構造移行
3. **インストールとCLI設計** (決定11-18): Git URL依存、独立したCLIツール、テンプレートコピー方式、ベストエフォート動作
4. **CLIフレームワークとコマンド命名** (決定19-21): typer採用、`/speckit.*`命名規則、CLIコマンド推奨
5. **コード品質とアーキテクチャ** (決定22-26): ruffプリセット、BaseGenerator 4メソッド、typerパターン再利用、構造化ログ
6. **インストール方法の標準化** (決定27): `uv tool install`方式の標準化

これらの決定により、spec-kit-docsはspec-kitエコシステムとの完全な一貫性を保ちながら、拡張性、保守性、テスト容易性を実現します。

---

## 7. 依存関係自動インストール機能の技術調査

### Session 2025-10-15 (Dependency Auto-Installation)

この

セクションは、FR-008b～FR-008eで定義された依存関係自動インストール機能の技術的実装を調査します。

#### 決定28: `handle_dependencies()`関数の設計

**決定**: 単一の関数`handle_dependencies()`で依存関係管理のすべてのロジックをカプセル化する。

**関数シグネチャ**:
```python
def handle_dependencies(
    doc_type: str,
    auto_install: bool,
    no_install: bool,
    project_root: Path,
    console: Console,
) -> DependencyResult:
    """依存関係のチェックとインストールを処理する。

    Args:
        doc_type: "sphinx" または "mkdocs"
        auto_install: --auto-installフラグ（CI/CD用、確認スキップ）
        no_install: --no-installフラグ（依存関係チェックスキップ）
        project_root: プロジェクトルートパス
        console: rich.console.Console（進捗表示用）

    Returns:
        DependencyResult: status, message, installed_packagesを含む
    """
```

**データクラス**:
```python
@dataclass(frozen=True)
class DependencyResult:
    status: Literal["installed", "skipped", "failed", "not_needed"]
    message: str
    installed_packages: list[str] = field(default_factory=list)
```

**根拠**:
1. **単一責任原則**: 依存関係管理のすべてのロジックを1つの関数にカプセル化
2. **決定的動作**: 同じ入力→同じ出力（V. Testability準拠）
3. **型安全性**: mypy互換の型ヒント（C006準拠）
4. **不変性**: データクラスのfrozen=True（エラー防止）

**検討された代替案**:
- クラスベース（`DependencyManager`） → MVP範囲では過剰設計
- 複数関数分割（`check_conditions()`, `install_packages()`, `show_alternatives()`） → 関数呼び出しの複雑化

---

#### 決定29: subprocess.run()によるuvコマンド実行のエラーハンドリング

**決定**: `check=False`で手動returncode確認、timeout=300秒、capture_output=Trueでstderr取得。

**実装パターン**:
```python
try:
    result = subprocess.run(
        ["uv", "add"] + packages,
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=300,  # 5分
        check=False,  # 手動でreturncode確認
    )

    if result.returncode == 0:
        console.print("[green]✓[/green] 依存関係のインストールが成功しました")
        return DependencyResult(
            status="installed",
            message="インストール成功",
            installed_packages=packages,
        )
    else:
        # C002準拠: エラー迂回禁止、明確なエラー+代替方法提示
        console.print(f"[red]✗[/red] インストール失敗: {result.stderr}")
        show_alternative_methods(doc_type, console, project_root)
        return DependencyResult(
            status="failed",
            message=f"uv add失敗: {result.stderr}",
        )

except subprocess.TimeoutExpired:
    console.print("[red]✗[/red] インストールがタイムアウトしました（5分超過）")
    show_alternative_methods(doc_type, console, project_root)
    return DependencyResult(status="failed", message="タイムアウト")

except FileNotFoundError:
    console.print("[red]✗[/red] uvコマンドが見つかりません")
    show_alternative_methods(doc_type, console, project_root)
    return DependencyResult(status="failed", message="uvコマンド不在")
```

**根拠**:
1. **check=False**: カスタムエラーメッセージ表示が可能
2. **timeout=300**: ネットワーク速度に依存するが、5分で十分（SC-002b: 90%成功率達成）
3. **capture_output=True**: stderrキャプチャでエラー詳細をユーザーに提示
4. **C002準拠**: エラー迂回絶対禁止、明確なエラー+代替方法提示

**検討された代替案**:
- `check=True` → subprocess.CalledProcessError、カスタムメッセージが困難
- `shell=True` → セキュリティリスク、spec-kitパターンと不一致

---

#### 決定30: typer.confirm()の使用パターンとデフォルト値

**決定**: `default=True`でユーザーエクスペリエンス最適化、本家spec-kitパターン踏襲。

**実装パターン**:
```python
# 本家spec-kitのパターンを完全に踏襲（C012: DRY原則）
packages = get_required_packages(doc_type)
console.print(f"\n[bold]インストール予定のパッケージ:[/bold] {', '.join(packages)}")
console.print(f"[yellow]警告:[/yellow] pyproject.tomlが変更されます")
console.print(f"[dim]実行コマンド:[/dim] uv add {' '.join(packages)}")

confirmed = typer.confirm(
    "インストールを続行しますか？",
    default=True,  # Enterキーでインストール続行
)

if not confirmed:
    console.print("[yellow]インストールをスキップしました[/yellow]")
    show_alternative_methods(doc_type, console, project_root)
    return DependencyResult(status="skipped", message="ユーザーが拒否")
```

**根拠**:
1. **default=True**: ほとんどのユーザーはインストールを望む（UX最適化）
2. **本家spec-kitとの一貫性**: `specify init --here`でも同様のパターン
3. **C012 (DRY原則)**: typerの既存パターン再利用

**検討された代替案**:
- `default=False` → 保守的だが摩擦増加、SC-002達成が困難
- 3択選択 → 複雑化、MVP範囲超過

**本家spec-kitの調査結果**:
```python
# specify-cli/specify/cli.py
if not typer.confirm(
    f"Overwrite {existing_file}?",
    default=False,  # ファイル上書き時は慎重にdefault=False
):
    console.print("[yellow]Skipped[/yellow]")
```

依存関係インストールは「新規追加」であり「既存破壊」ではないため、`default=True`が適切です。

---

#### 決定31: パッケージマネージャー検出のベストプラクティス

**決定**: 優先順位付き検出（uv > poetry > pip）、条件付きチェック。

**実装パターン**:
```python
def detect_package_managers(project_root: Path, doc_type: str) -> list[tuple[str, str]]:
    """利用可能なパッケージマネージャーを検出する。

    Returns:
        List of (manager_name, install_command) tuples
    """
    managers: list[tuple[str, str]] = []
    packages = get_required_packages(doc_type)

    # 優先順位順に検出（spec-kitエコシステムとの整合性）
    if shutil.which("uv"):
        managers.append(("uv", f"uv add {' '.join(packages)}"))

    if shutil.which("poetry") and (project_root / "pyproject.toml").exists():
        managers.append(("poetry", f"poetry add {' '.join(packages)}"))

    if shutil.which("pip"):
        managers.append(("pip", f"pip install {' '.join(packages)}"))

    return managers
```

**根拠**:
1. **優先順位**: uv > poetry > pip（spec-kitエコシステムとの整合性）
2. **条件チェック**: poetryはpyproject.toml必須、pipは常に利用可能
3. **拡張性**: 将来的にconda等を追加しやすい（III. Extensibility & Modularity準拠）

**検討された代替案**:
- 単一マネージャーのみ表示 → ユーザーの選択肢制限
- 全マネージャー無条件表示 → 誤解を招く

---

#### 決定32: spec-kitワークフロー案内の実装

**決定**: FR-008dに準拠し、3段階の代替方法を明確に提示（失敗理由+方法1+方法2）。

**実装パターン**:
```python
def show_alternative_methods(
    doc_type: str,
    console: Console,
    project_root: Path,
) -> None:
    """代替インストール方法を表示する（FR-008d準拠）。"""
    packages = get_required_packages(doc_type)

    console.print("\n[bold yellow]代替方法:[/bold yellow]")

    # 方法1: 手動インストール（パッケージマネージャー自動検出）
    console.print("\n[bold]方法1: 手動インストール[/bold]")
    managers = detect_package_managers(project_root, doc_type)
    if managers:
        for manager_name, command in managers:
            console.print(f"  • {manager_name}: [cyan]{command}[/cyan]")
    else:
        console.print("  [dim]利用可能なパッケージマネージャーが見つかりませんでした[/dim]")

    # 方法2: spec-kitワークフロー（エコシステム強化）
    console.print("\n[bold]方法2: spec-kitワークフロー[/bold]")
    console.print("  依存関係管理をspec-kitワークフローで行うことで、")
    console.print("  [green]依存関係の履歴がplan.md/tasks.mdに記録されます[/green]")
    console.print("\n  手順:")
    console.print("    1. [cyan]/speckit.specify[/cyan] - 「依存関係のインストール」仕様作成")
    console.print(f"    2. [cyan]/speckit.plan[/cyan] - インストール計画立案")
    console.print(f"    3. [cyan]/speckit.tasks[/cyan] - タスク分解")
    console.print(f"    4. [cyan]/speckit.implement[/cyan] - {' '.join(packages)}をインストール")
    console.print("\n  利点:")
    console.print("    • 依存関係の変更履歴が残る")
    console.print("    • なぜその依存関係が必要かドキュメント化される")
    console.print("    • チーム全体で依存関係の追加理由を共有できる")
```

**根拠**:
1. **FR-008d完全準拠**: 失敗理由+方法1（手動）+方法2（spec-kitワークフロー）を提示
2. **spec-kitエコシステム強化**: ワークフローの価値を明確に説明
3. **rich.console使用**: 視覚的に見やすい出力（色付き、構造化）

**検討された代替案**:
- 方法1のみ提示 → spec-kitエコシステムの価値を伝えられない
- 方法2のみ提示 → 即座のインストールを望むユーザーに不便

---

#### 決定33: テスト戦略（TDD必須、C010準拠）

**決定**: pyfakefs+subprocess mock、Red-Green-Refactorサイクル、95%以上カバレッジ。

**テストフレームワーク構成**:
```python
# tests/unit/test_handle_dependencies.py
@pytest.fixture
def mock_fs(fs):  # pyfakefs fixture
    """仮想ファイルシステムをセットアップ"""
    fs.create_file("/project/pyproject.toml")
    fs.create_dir("/project/.specify")
    return fs

@pytest.fixture
def mock_subprocess():
    """subprocess.runをモック"""
    with patch("subprocess.run") as mock:
        yield mock

def test_handle_dependencies_success(mock_fs, mock_subprocess):
    """正常系: pyproject.toml存在、uv利用可能、インストール成功"""
    # Arrange (Red)
    mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
    with patch("shutil.which", return_value="/usr/bin/uv"):
        with patch("importlib.util.find_spec", return_value=None):  # 未インストール
            # Act (Green)
            result = handle_dependencies(
                doc_type="sphinx",
                auto_install=True,
                no_install=False,
                project_root=Path("/project"),
                console=Console(),
            )

    # Assert
    assert result.status == "installed"
    assert "sphinx" in result.installed_packages
    mock_subprocess.assert_called_once_with(
        ["uv", "add", "sphinx>=7.0", "myst-parser>=2.0"],
        cwd=Path("/project"),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
```

**エッジケーステスト**:
1. `test_handle_dependencies_no_pyproject`: pyproject.toml不在 → `status="failed"`
2. `test_handle_dependencies_uv_not_found`: uvコマンド不在 → `status="failed"`、代替方法表示
3. `test_handle_dependencies_already_installed`: パッケージ既インストール → `status="not_needed"`
4. `test_handle_dependencies_no_install_flag`: `--no-install`フラグ → `status="skipped"`
5. `test_handle_dependencies_auto_install_flag`: `--auto-install`フラグ → 確認スキップ
6. `test_handle_dependencies_timeout`: uv addタイムアウト → `status="failed"`
7. `test_handle_dependencies_uv_add_failed`: uv add失敗（returncode != 0） → `status="failed"`、stderrキャプチャ
8. `test_handle_dependencies_user_declined`: ユーザー承認拒否 → `status="skipped"`

**根拠**:
1. **C010 (TDD必須)**: Red-Green-Refactorサイクル厳守
2. **V. Testability**: 決定的入力→決定的出力、外部依存排除
3. **pyfakefs**: ファイルシステム仮想化、テスト速度向上
4. **subprocess mock**: 外部コマンド実行を排除、テスト決定性保証
5. **網羅性**: 正常系・異常系・境界値テスト、SC-002b（90%成功率）検証

**カバレッジ目標**:
- `handle_dependencies()`: 95%以上
- 全体: 75%以上（既存目標維持）

---

### 技術的決定のまとめ

| 項目 | 決定 | 根拠 |
|------|------|------|
| 関数設計 | `handle_dependencies()` 単一関数 | 単一責任、決定的動作 |
| データ構造 | `DependencyResult` frozen dataclass | 不変性、型安全性 |
| エラーハンドリング | `check=False` + 手動確認 | カスタムメッセージ、C002準拠 |
| タイムアウト | 300秒（5分） | SC-002b: 90%成功率 |
| ユーザー承認 | `typer.confirm(default=True)` | UX最適化、本家一貫性、C012準拠 |
| パッケージマネージャー | uv > poetry > pip | spec-kit優先順位 |
| ワークフロー案内 | 失敗理由+方法1+方法2 | FR-008d完全準拠、エコシステム強化 |
| テスト | pyfakefs + subprocess mock | C010 (TDD)、V. Testability |

---

---

## 8. 依存関係配置先選択機能の技術調査

### Session 2025-10-16 (Dependency Placement Strategy)

このセクションは、FR-008fで定義された依存関係配置先選択機能の技術的実装を調査します。

#### 決定34: `uv add --optional` vs `uv add --group` の動作確認

**決定**: 両方のコマンドをサポートし、ユーザーに選択させる。

**`uv add --optional`の動作**:
```bash
uv add --optional docs sphinx>=7.0 myst-parser>=2.0
```

**pyproject.toml変更**:
```toml
[project.optional-dependencies]
docs = [
    "sphinx>=7.0",
    "myst-parser>=2.0",
]
```

**インストール方法**:
```bash
# すべてのoptional dependenciesをインストール
uv sync --all-extras

# docsグループのみ
uv pip install -e ".[docs]"

# pipでも互換
pip install -e ".[docs]"
```

**仕様**: PEP 621（Storing project metadata in pyproject.toml）

---

**`uv add --group`の動作**:
```bash
uv add --group docs sphinx>=7.0 myst-parser>=2.0
```

**pyproject.toml変更**:
```toml
[dependency-groups]
docs = [
    "sphinx>=7.0",
    "myst-parser>=2.0",
]
```

**インストール方法**:
```bash
# docsグループをインストール
uv sync --group docs
```

**仕様**: PEP 735（Dependency Groups in pyproject.toml）

**判定**: ✅ 両方のコマンドが正常に動作することを確認。

---

#### 決定35: pip/poetryとの互換性確認

**`[project.optional-dependencies]`の互換性**:
- **pip**: `pip install -e ".[docs]"` ✅ 動作する
- **poetry**: `poetry install --extras docs` ✅ 動作する
- **uv**: `uv sync --all-extras` ✅ 動作する

**判定**: ✅ pip/poetry/uv すべてで互換性あり

**`[dependency-groups]`の互換性**:
- **pip**: `pip install -e ".[docs]"` ❌ [dependency-groups]は認識されない（エラーにはならないが無視される）
- **poetry**: `poetry install` ❌ [dependency-groups]は認識されない（エラーにはならないが無視される）
- **uv**: `uv sync --group docs` ✅ 動作する

**判定**: ⚠️ uvネイティブのみ。pip/poetryは無視する（エラーにはならない）

**決定**: `optional-dependencies`をデフォルトとし、uvユーザーには`dependency-groups`を選択可能にする。

---

#### 決定36: デフォルト値の妥当性

**`optional-dependencies`をデフォルトとする根拠**:
1. **広い互換性**: pip/poetry/uvすべてで動作
2. **PEP 621標準**: 長期間サポートされている安定した仕様
3. **既存のPythonエコシステムとの一貫性**: 多くのプロジェクトが既に使用
4. **spec-kitユーザーの多様性**: すべてのユーザーがuvを使用しているわけではない

**判定**: ✅ デフォルト値は`optional-dependencies`とする。

---

#### 決定37: `handle_dependencies()`関数のシグネチャ変更

**現在のシグネチャ**:
```python
def handle_dependencies(
    doc_type: str,
    auto_install: bool,
    no_install: bool,
    project_root: Path,
    console: Console,
) -> DependencyResult
```

**新しいシグネチャ**:
```python
def handle_dependencies(
    doc_type: str,
    auto_install: bool,
    no_install: bool,
    dependency_target: Literal["optional-dependencies", "dependency-groups"],  # NEW
    project_root: Path,
    console: Console,
) -> DependencyResult
```

**影響範囲**:
1. `scripts/doc_init.py` - 呼び出し側を更新
2. `tests/unit/utils/test_handle_dependencies.py` - 全テストケースを更新
3. `tests/integration/test_doc_init_*.py` - 統合テストを更新
4. `.claude/commands/speckit.doc-init.md` - AIエージェントプロンプトを更新

**後方互換性**: デフォルト値を設定せず、すべての呼び出し箇所で明示的に指定する（明示性優先）

**決定**: 後方互換性よりも明示性を優先。すべての呼び出し箇所でdependency_targetを明示的に指定。

---

#### 決定38: `.claude/commands/speckit.doc-init.md`の変更範囲

**追加が必要な内容**:

1. **依存関係配置先の選択プロンプト**:
   ```markdown
   ## Step 4: 依存関係配置先の選択（Session 2025-10-16追加）

   ユーザーに以下を尋ねる：

   「ドキュメント依存関係の配置先を選択してください：
   1. [project.optional-dependencies.docs]（推奨、pip/poetry/uv互換）
   2. [dependency-groups.docs]（uvネイティブ、モダン）

   デフォルト: 1」

   選択結果を`--dependency-target`引数に変換：
   - 選択肢1 → `--dependency-target optional-dependencies`
   - 選択肢2 → `--dependency-target dependency-groups`
   ```

2. **doc_init.py呼び出しの更新**:
   ```bash
   uv run python .specify/scripts/docs/doc_init.py \
     --type {選択されたツール} \
     --project-name "{プロジェクト名}" \
     --author "{著者名}" \
     --version "{バージョン}" \
     --language {言語} \
     --dependency-target {選択された配置先}  # NEW
   ```

**決定**: プロンプトに依存関係配置先選択ステップを追加。

---

### 技術的決定のまとめ（Session 2025-10-16）

| 項目 | 決定 | 根拠 |
|------|------|------|
| サポートする配置先 | `optional-dependencies` と `dependency-groups` の両方 | ユーザーの環境に応じた柔軟性を提供 |
| デフォルト値 | `optional-dependencies` | pip/poetry/uv互換、広い互換性 |
| 後方互換性 | 維持しない | 明示性を優先、すべての呼び出し箇所で明示的に指定 |
| ユーザーインターフェース | AIエージェントが対話的に選択を収集 | spec-kit標準パターンに準拠 |
| 引数追加 | `--dependency-target` | doc_init.pyに追加 |

---

**Version**: 1.2.0 | **Last Updated**: 2025-10-16 | **Contributor**: AI Agent (Claude Code)
