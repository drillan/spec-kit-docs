# spec-kit-docs Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-13

## Active Technologies

**Language**: Python 3.11+ （spec-kit前提条件との互換性）

**Primary Dependencies** (001-draft-init-spec):
- **CLIフレームワーク**: typer（本家spec-kitとの一貫性、Session 2025-10-13決定により argparse から変更）
- **ドキュメントツール**: Sphinx 7.0+ with myst-parser 2.0+、MkDocs 1.5+
- **パッケージリソース管理**: importlib.resources（Python 3.9+標準ライブラリ）
- **Git操作**: GitPython 3.1+（変更検出とブランチ情報取得）
- **テンプレートエンジン**: Jinja2 3.1+（設定ファイル生成）
- **Markdown解析**: markdown-it-py 3.0+（spec.md等の解析、MyST互換性）
- **spec-kit依存**: specify-cli @ git+https://github.com/github/spec-kit.git（型定義とユーティリティの共有、typer依存ツリーを含む）

**Testing**: pytest 8.0+、pytest-cov 4.0+（単体テスト・統合テスト・契約テスト）

**Target Platform**: Linux/macOS/WSL2（spec-kitと同じプラットフォーム要件）

## Project Structure

```
spec-kit-docs/                        # プロジェクトルート
├── src/
│   └── speckit_docs/                 # メインパッケージ
│       ├── cli/                      # CLIエントリポイント
│       ├── commands/                 # コマンドテンプレート（importlib.resources経由）
│       ├── scripts/                  # バックエンドスクリプト
│       ├── generators/               # ドキュメントジェネレータ（base.py, sphinx.py, mkdocs.py）
│       ├── parsers/                  # spec-kit仕様解析（spec_parser.py, plan_parser.py, tasks_parser.py）
│       ├── utils/                    # ユーティリティ（git.py, fs.py, template.py）
│       └── exceptions.py             # SpecKitDocsError例外定義
├── tests/
│   ├── contract/                     # 契約テスト（CLIインターフェース）
│   ├── integration/                  # 統合テスト（実際のspec-kitプロジェクト使用）
│   └── unit/                         # 単体テスト
├── pyproject.toml                    # プロジェクト設定、依存関係管理
├── .specify/                         # spec-kitメタデータ
└── specs/                            # 機能仕様
    └── 001-draft-init-spec/          # この機能の仕様
```

## Commands

**Development**:
```bash
# テストの実行
uv run pytest

# リンターの実行
uv run ruff check .

# 型チェックの実行
uv run mypy src/speckit_docs

# カバレッジレポートの生成
uv run pytest --cov=speckit_docs --cov-report=html
```

**Installation**:
```bash
# spec-kit-docs CLIツールのインストール
uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git

# 既存spec-kitプロジェクトへのインストール
cd your-spec-kit-project
speckit-docs install

# ドキュメントプロジェクトの初期化
/doc-init

# ドキュメントの更新
/doc-update
```

## Code Style

**Python 3.11+**: Follow standard conventions

**Key Conventions**:
- **型ヒント必須**: すべての関数とメソッドに型ヒントを付ける（mypy互換）
- **データクラス優先**: エンティティは`@dataclass(frozen=True)`で定義し、不変性を保つ
- **エラーハンドリング**: すべてのエラーは`SpecKitDocsError`例外として発生させ、エラーメッセージに「ファイルパス」「エラー種類」「推奨アクション」を含める（C002準拠）
- **DRY原則**: 重複実装を避け、既存のユーティリティ、ライブラリ、抽象ベースクラスを確認する。**特に本家spec-kitのtyperパターン（`typer.confirm()`、`typer.Option()`等）を再利用する**（C012準拠）
- **TDD必須**: 実装前にテストを書き、Red-Green-Refactorサイクルに従う（C010準拠）

## Architecture Patterns

**Strategy Pattern (Generator)**: Sphinx/MkDocsの実装に使用。`BaseGenerator`抽象ベースクラスを定義し、`SphinxGenerator`と`MkDocsGenerator`を実装（Extensibility & Modularity原則）

**Parser Separation**: パーサー（読み取り）、ジェネレーター（書き込み）、エンティティ（データ保持）を明確に分離（Separation of Concerns原則）

**Non-Interactive Execution**: バックエンドスクリプト（doc_init.py、doc_update.py）は標準入力（stdin）を使用せず、コマンドライン引数のみで動作（II. Non-Interactive Execution原則）

## Recent Changes
- 001-draft-init-spec: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

- 2025-10-13: **CLIフレームワーク変更決定（argparse → typer）**: Core Principle I（spec-kit Integration First）準拠のため、本家spec-kitとの一貫性を優先。Session 2025-10-13 Clarificationで記録、plan.md、research.md、CLAUDE.mdを更新（001-draft-init-spec）
- 2025-10-13: Constitution Check完了（再評価）、typer採用により C004/C012/C013/C014 への準拠が強化された（001-draft-init-spec）

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
