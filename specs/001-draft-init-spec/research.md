# Research Report: spec-kit-docs技術選択とベストプラクティス

**作成日**: 2025-10-18
**対象**: spec-kit-docs AI駆動型ドキュメント生成システム
**目的**: Technical Contextの各技術選択に対するベストプラクティスと代替案の調査

---

## 1. CLIフレームワーク: typer vs argparse

### Decision: typer

**Rationale**:
- 本家spec-kitがtyperを使用しており、spec-kit-docsは`specify-cli`に依存
- 既にtyperが依存ツリーに存在（追加の依存関係なし）
- 型ヒントのネイティブサポート（`int`, `str`, `bool`等）でmypy互換
- `typer.confirm()`, `typer.Option()`等のパターンを本家spec-kitから再利用可能（DRY原則）

**Alternatives Considered**:
- **argparse** (Python標準ライブラリ):
  - 利点: 外部依存なし
  - 欠点: (1) 本家spec-kitとの一貫性欠如、(2) 型ヒント未サポート（手動バリデーション必要）、(3) 憲章Core Principle I「spec-kit Integration First」違反
  - **却下理由**: 既にtyperに間接依存しており、一貫性が優先される

**Best Practices**:
1. **型ヒントの活用**: `def command(option: int = typer.Option(...))`形式で型安全性を保証
2. **typer.confirm()でユーザー確認**: 既存ファイル上書き時の確認に使用（本家spec-kitパターン）
3. **デフォルト値の明示**: `typer.Option(default=...)`でデフォルト動作を明確化
4. **ヘルプテキスト**: `typer.Option(help="...")`で各オプションの説明を提供

**References**:
- spec-kit本家の`specify-cli`実装（typerパターン）
- typer公式ドキュメント: https://typer.tiangolo.com/

---

## 2. ドキュメントツール: Sphinx vs MkDocs

### Decision: Sphinx 7.0+ with myst-parser 2.0+ と MkDocs 1.5+ の両方をサポート

**Rationale**:
- **Sphinx**: Python プロジェクトの標準、強力な拡張性、API リファレンス生成に適している
- **MkDocs**: シンプルで高速、Markdown ネイティブ、デプロイが容易
- ユーザーに選択肢を提供し、プロジェクトのニーズに応じて選べるようにする

**Sphinx Best Practices**:
1. **myst-parserの使用**: reStructuredTextではなくMarkdownをデフォルトにする
   - 理由: spec-kitのすべてのソースファイル（spec.md、plan.md、tasks.md）がMarkdown
   - フォーマット統一により変換ロジック不要
   - ユーザーの学習コスト削減
2. **conf.pyの最小化**: 必要な拡張のみ有効化（`extensions = ["myst_parser"]`）
3. **toctree構造**: フラット構造（5機能以下）または包括的構造（6機能以上）を自動判定
4. **テーマ選択**: `sphinx_rtd_theme`（Read the Docs）をデフォルト

**MkDocs Best Practices**:
1. **mkdocs.ymlの簡素化**: 最小限の設定（`site_name`, `nav`, `theme`のみ）
2. **テーマ選択**: `material`テーマをデフォルト（モダンなデザイン、検索機能、レスポンシブ）
3. **ナビゲーション構造**: Sphinxと同様にフラット/包括的構造を自動判定
4. **プラグイン**: MVPではプラグイン不使用（シンプルさ優先）

**Alternatives Considered**:
- **Docusaurus** (React-based):
  - 利点: モダンなUI、React統合
  - 欠点: (1) Node.js依存（Pythonプロジェクトとの不整合）、(2) MVPスコープ超過
  - **将来検討**: Phase 2で追加可能（Extensibility & Modularity原則により容易）

**References**:
- Sphinx公式: https://www.sphinx-doc.org/
- MyST Parser: https://myst-parser.readthedocs.io/
- MkDocs公式: https://www.mkdocs.org/
- Material for MkDocs: https://squidfunk.github.io/mkdocs-material/

---

## 3. Markdown解析: markdown-it-py

### Decision: markdown-it-py 3.0+

**Rationale**:
- MyST Parser（Sphinx）の内部で使用されているため、既存依存関係
- CommonMark準拠、拡張性が高い
- Pythonネイティブ（C拡張不要）

**Best Practices**:
1. **構造化パース**: spec.mdをAST（Abstract Syntax Tree）としてパース
   - 見出しレベル（`##`, `###`）の検出
   - セクション境界の正確な判定
2. **多言語対応**: 正規表現で日本語・英語の見出しパターンを検出
   - 例: `## 前提条件 | ## Prerequisites`
3. **エラーハンドリング**: 不正なMarkdown構文を検出し、明確なエラーメッセージを返す

**Implementation Approach for spec.md Minimal Extraction**:
既存の`MarkdownParser`クラス（`src/speckit_docs/parsers/markdown_parser.py`）を再利用する方針を採用します：

- **Decision**: markdown-it-pyを使用した構造化マークダウン解析アプローチ + 既存のMarkdownParserクラスを再利用
- **Rationale**:
  1. プロジェクトは既に`markdown-it-py>=3.0`に依存しており、追加の依存関係は不要
  2. `MarkdownParser`クラスが既に存在し、セクション抽出機能を提供（`models.py:116-183`のSectionクラス）
  3. Markdown ASTパーサーは正規表現ベースの実装より約5倍高速
  4. コードブロック内の見出しのような構文、ネストされた構造、エッジケースを正確に処理
  5. 既存のテストスイート（`tests/unit/parsers/test_markdown_parser.py`）に427個のテストが存在

**Alternatives Considered for spec.md Extraction**:
- **正規表現ベースの抽出**:
  - メリット: シンプルな実装
  - デメリット: コードブロック内の見出しを誤検出、ネストされた構造の処理が困難、パフォーマンス劣化
  - **却下理由**: 現状の`llm_transform.py:446-542`の正規表現実装は部分一致で誤検出の可能性があり、可読性が低い

**Alternatives Considered**:
- **mistune**:
  - 利点: 高速
  - 欠点: MyST Parserとの互換性不明、既存依存関係にない
  - **却下理由**: markdown-it-pyが既に依存関係に含まれる
- **正規表現のみ**:
  - 利点: 外部依存なし
  - 欠点: (1) ネストした見出しの処理が複雑、(2) エラー検出が困難
  - **却下理由**: markdown-it-pyでより堅牢な解析が可能

**References**:
- markdown-it-py: https://markdown-it-py.readthedocs.io/

---

## 4. LLM統合: anthropic SDK

### Decision: anthropic 0.28+

**Rationale**:
- Claude APIの公式SDK
- 型ヒント完備（mypy互換）
- Session 2025-10-17決定: LLM変換は常に有効（フォールバックなし）

**Best Practices**:
1. **責務分担**: AIエージェント（Claude Code）がLLM変換を実行、バックエンドスクリプトは変換済みコンテンツを受け取る
   - Claude Code環境ではユーザーはANTHROPIC_API_KEYを意識不要
   - スクリプトは決定的（同じ入力→同じ出力）でテスト容易
2. **トークン制限**: 1機能あたり10,000トークン以内に制限
   - 超過時は明確なエラーメッセージで中断（フォールバック禁止）
3. **品質チェック**: LLM生成コンテンツの検証
   - 空文字列チェック
   - 最小文字数チェック（50文字以上）
   - エラーパターンマッチング（`error`, `failed`, `申し訳`等）
   - Markdown構文チェック（markdown-it-pyでパース）
4. **エラーハンドリング**: すべてのLLMエラーは明確なメッセージで中断（憲章C002準拠）

**Alternatives Considered**:
- **OpenAI SDK** (GPT-4等):
  - 利点: 他のLLMモデルも選択可能
  - 欠点: (1) spec-kitエコシステムがClaude Code前提、(2) Claude APIとの一貫性欠如
  - **却下理由**: spec-kit-docsはClaude Code環境で使用されることが前提
- **LLM統合なし**:
  - 利点: 実装シンプル、コスト不要
  - 欠点: (1) ユーザー価値低下（技術仕様のコピーのみ）、(2) Session 2025-10-16決定で却下済み
  - **却下理由**: LLM変換がspec-kit-docsの主要価値提案

**References**:
- Anthropic SDK: https://docs.anthropic.com/claude/reference/client-sdks

---

## 5. Git操作: GitPython

### Decision: GitPython 3.1+

**Rationale**:
- Pythonネイティブ、Git操作の標準ライブラリ
- ブランチ情報取得、変更検出（git diff）に使用
- 型ヒントサポート

**Best Practices**:
1. **変更検出**: `git diff --name-only HEAD~1 HEAD`で変更されたファイルを検出
   - `--quick`フラグ指定時のみ実行
   - Git履歴がない場合はフル更新にフォールバック
2. **ブランチ情報**: `repo.active_branch.name`で現在のブランチを取得
   - 機能番号（001、002等）の抽出に使用
3. **エラーハンドリング**: Git リポジトリでない場合は明確なエラーメッセージ
   - 「.gitディレクトリが見つかりません。Gitリポジトリで実行してください」

**Alternatives Considered**:
- **subprocess + git コマンド**:
  - 利点: 外部依存なし
  - 欠点: (1) エラーハンドリングが複雑、(2) プラットフォーム依存性、(3) 型ヒント未サポート
  - **却下理由**: GitPythonでより堅牢な実装が可能
- **dulwich** (Pure Python Git implementation):
  - 利点: Gitコマンド不要
  - 欠点: (1) GitPythonより低レベル、(2) 複雑な操作が困難
  - **却下理由**: GitPythonで十分

**References**:
- GitPython: https://gitpython.readthedocs.io/

---

## 6. テンプレートエンジン: Jinja2

### Decision: Jinja2 3.1+

**Rationale**:
- Pythonテンプレートエンジンの標準
- Sphinx/MkDocsの設定ファイル生成に使用
- 変数置換、条件分岐、ループをサポート

**Best Practices**:
1. **設定ファイルテンプレート**: `conf.py.jinja`, `mkdocs.yml.jinja`
   - プロジェクト名、著者名、バージョン等を変数として埋め込み
2. **自動エスケープ無効化**: 設定ファイルは実行可能なPythonコード（conf.py）またはYAML（mkdocs.yml）なので、HTMLエスケープ不要
3. **テンプレートディレクトリ**: `src/speckit_docs/templates/`に配置、importlib.resourcesでアクセス

**Alternatives Considered**:
- **文字列フォーマット** (`str.format()`, f-strings):
  - 利点: 外部依存なし
  - 欠点: (1) 条件分岐・ループ未サポート、(2) 複雑なテンプレートが困難
  - **却下理由**: 設定ファイルには条件分岐（ツール別設定）が必要
- **mako**:
  - 利点: Jinja2より高速
  - 欠点: (1) Jinja2より普及度低い、(2) 追加の学習コスト
  - **却下理由**: Jinja2がPythonエコシステムの標準

**References**:
- Jinja2: https://jinja.palletsprojects.com/

---

## 7. パッケージリソース管理: importlib.resources

### Decision: importlib.resources (Python 3.9+標準ライブラリ)

**Rationale**:
- コマンドテンプレート（speckit.doc-init.md等）とスクリプトをPythonパッケージに含める
- オフライン環境でも動作（pip install後にネットワーク不要）
- Python標準のパッケージングベストプラクティスに準拠

**Best Practices**:
1. **リソース配置**: `src/speckit_docs/commands/`, `src/speckit_docs/scripts/`
2. **アクセス方法**:
   ```python
   from importlib.resources import files

   template_path = files("speckit_docs.commands").joinpath("speckit.doc-init.md")
   with template_path.open("r", encoding="utf-8") as f:
       content = f.read()
   ```
3. **コピー処理**: リソースを読み込み、ユーザープロジェクトの`.claude/commands/`にコピー

**Alternatives Considered**:
- **GitHub Raw URL ダウンロード** (spec-kit本家パターン):
  - 利点: 常に最新版を取得
  - 欠点: (1) オンライン環境必須、(2) 少数ファイル（2つのコマンド定義）には過剰
  - **却下理由**: パッケージに含める方がシンプル
- **pkg_resources** (setuptools):
  - 利点: 古いPythonバージョンでも動作
  - 欠点: (1) Python 3.9+が前提なのでimportlib.resourcesで十分、(2) pkg_resourcesは非推奨
  - **却下理由**: importlib.resourcesがモダン

**References**:
- importlib.resources: https://docs.python.org/3/library/importlib.resources.html

---

## 8. テストフレームワーク: pytest

### Decision: pytest 8.0+ with pytest-cov 4.0+

**Rationale**:
- Pythonテストフレームワークの標準
- フィクスチャ、パラメータ化テスト、モック機能が強力
- pytest-covでカバレッジ測定

**Best Practices**:
1. **TDD必須**: Red-Green-Refactorサイクル
   - Red: テストを書き、失敗することを確認
   - Green: テストを通過する最小限の実装
   - Refactor: コードを改善し、テスト通過を維持
2. **テストディレクトリ構造**:
   ```
   tests/
   ├── contract/      # CLIインターフェース契約テスト
   ├── integration/   # 実際のspec-kitプロジェクト使用
   └── unit/          # 単体テスト（パーサー、ジェネレータ等）
   ```
3. **カバレッジ目標**: 主要コードパス90%以上
4. **モック戦略**: AIエージェント部分（LLM変換）はモック、バックエンドスクリプトは実際の変換済みコンテンツでテスト

**Alternatives Considered**:
- **unittest** (Python標準ライブラリ):
  - 利点: 外部依存なし
  - 欠点: (1) フィクスチャ機能が弱い、(2) 冗長なボイラープレート
  - **却下理由**: pytestでより簡潔なテストが可能

**References**:
- pytest: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/

---

## 9. コードリント・フォーマット: ruff

### Decision: ruff (blackは禁止)

**Rationale**:
- 高速（Rust実装）
- linterとformatterを統合
- 憲章FR-036で明示的に要求

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
select = ["E", "F", "W", "I"]  # エラー、致命的エラー、警告、import順序
line-length = 100
target-version = "py311"

[tool.ruff.lint]
ignore = []
```

**Best Practices**:
1. **ローカル実行**: `uv run ruff check .`（CI/CDパイプラインは構築しない）
2. **コミット前チェック**: 手動で実行（憲章C006）
3. **型ヒント**: ruffとmypyの両方を使用

**Alternatives Considered**:
- **black**:
  - 欠点: 憲章FR-036で明示的に禁止
  - **却下理由**: 憲章違反
- **flake8**:
  - 欠点: (1) ruffより低速、(2) formatter未統合
  - **却下理由**: ruffで十分

**References**:
- ruff: https://docs.astral.sh/ruff/

---

## 10. 型チェック: mypy

### Decision: mypy (型ヒント必須)

**Rationale**:
- Pythonの標準型チェッカー
- 憲章C006で堅牢コード品質が要求される
- typer、anthropic SDKと型ヒント互換

**Best Practices**:
1. **すべての関数に型ヒント**: 引数と戻り値
   ```python
   def parse_spec(spec_file: Path) -> SpecContent:
       ...
   ```
2. **データクラスの活用**: `@dataclass(frozen=True)`で不変エンティティ
3. **ジェネリクス**: `List[Feature]`, `Dict[str, str]`等
4. **strictモード**: `pyproject.toml`で`strict = true`（可能な限り）

**Alternatives Considered**:
- **pyright** (Microsoft):
  - 利点: より高速
  - 欠点: (1) mypyがPythonエコシステムの標準、(2) typerとの統合実績
  - **却下理由**: mypyで十分

**References**:
- mypy: https://mypy.readthedocs.io/

---

## Research Conclusion

すべてのTechnical Contextの技術選択について調査を完了しました。各選択は以下の基準を満たしています：

1. **憲章準拠**: Core Principles（I-V）とCritical Rules（C001-C014）に準拠
2. **spec-kit統合**: 本家spec-kitとの一貫性を最優先
3. **実用性**: MVPスコープ内で実装可能
4. **拡張性**: 将来のフェーズでDocusaurus等の追加が容易

Phase 1（設計）に進む準備が整いました。
