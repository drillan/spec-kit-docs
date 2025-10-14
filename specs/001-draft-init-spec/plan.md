# Implementation Plan: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

spec-kit-docsは、spec-kitプロジェクトの仕様ファイル（spec.md、plan.md、tasks.md）から、SphinxまたはMkDocsドキュメントを自動生成・更新するCLIツールです。MVP（フェーズ1）では、基本的なドキュメント初期化（`/speckit.doc-init`）とインクリメンタル更新（`/speckit.doc-update`）、既存プロジェクトへのインストール機能を提供します。本家spec-kitとの一貫性を最優先し、非対話的実行モデル、Strategy PatternによるGenerator抽象化、TDD必須の開発プロセスを採用します。

## Technical Context

**Language/Version**: Python 3.11+（spec-kit前提条件との互換性）
**Primary Dependencies**:
- **CLIフレームワーク**: typer（本家spec-kitとの一貫性、Session 2025-10-13決定によりargparseから変更）
- **ドキュメントツール**: Sphinx 7.0+ with myst-parser 2.0+、MkDocs 1.5+
- **パッケージリソース管理**: importlib.resources（Python 3.9+標準ライブラリ）
- **Git操作**: GitPython 3.1+（変更検出とブランチ情報取得）
- **テンプレートエンジン**: Jinja2 3.1+（設定ファイル生成）
- **Markdown解析**: markdown-it-py 3.0+（spec.md等の解析、MyST互換性）
- **spec-kit依存**: specify-cli @ git+https://github.com/github/spec-kit.git（型定義とユーティリティの共有、typer依存ツリーを含む）

**Storage**: N/A（ファイルシステムのみ使用、データベース不要）
**Testing**: pytest 8.0+、pytest-cov 4.0+（単体テスト・統合テスト・契約テスト）
**Target Platform**: Linux/macOS/WSL2（spec-kitと同じプラットフォーム要件）
**Project Type**: Single project（CLIツール、Pythonパッケージ）
**Performance Goals**:
- ドキュメント初期化（`/speckit.doc-init`）: 30秒以内（対話的入力時間を除く）
- ドキュメント更新（`/speckit.doc-update`）: 5機能のプロジェクトで45秒以内（フル更新時）、1機能のみ変更時は5秒以内（インクリメンタル更新）

**Constraints**:
- 非対話的実行: バックエンドスクリプト（doc_init.py、doc_update.py）は標準入力（stdin）を使用せず、コマンドライン引数のみで動作
- spec-kit Integration First: 本家spec-kitの`specify init --here`パターン、`--force`フラグセマンティクス、エラーハンドリング（ベストエフォート方式）と完全に一貫
- Markdown形式統一: Sphinxでもデフォルトは.md（myst-parser使用）、spec.md/plan.md/tasks.mdとのフォーマット統一

**Scale/Scope**:
- MVP対象: 1-20機能のspec-kitプロジェクト
- サポートドキュメントツール: Sphinx（MyST Markdown）、MkDocs（Material theme）
- 拡張性: 将来的にDocusaurus、VitePressなど追加可能な設計

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. spec-kit Integration First** | ✅ PASS | - `uv tool install`方式を標準インストール方法として採用（Session 2025-10-14決定）<br>- `speckit-docs install`コマンドは`specify init --here`パターンに従う<br>- コマンド命名規則`/speckit.doc-init`、`/speckit.doc-update`で一貫<br>- エラーハンドリングはベストエフォート方式（部分的成功状態を許容） |
| **II. Non-Interactive Execution** | ✅ PASS | - doc_init.py、doc_update.pyは`input()`を使用しない<br>- すべての設定はコマンドライン引数またはデフォルト値から取得<br>- 対話的情報収集はAIエージェント（Claude Code）が担当 |
| **III. Extensibility & Modularity** | ✅ PASS | - BaseGeneratorクラス（4メソッド: `initialize()`, `generate_feature_page()`, `update_navigation()`, `validate()`）<br>- SphinxGenerator、MkDocsGeneratorが独立モジュールとして実装<br>- パーサー（parsers/）とジェネレータ（generators/）を明確に分離 |
| **IV. Incremental Delivery** | ✅ PASS | - MVP（P1）: ドキュメント初期化・更新、インストール機能のみ<br>- P2: エンティティ統合・API統合<br>- P3: 対象者別フィルタリング、バージョン履歴追跡<br>- 各ユーザーストーリーは独立してテスト可能 |
| **V. Testability** | ✅ PASS | - TDD必須（C010）: Red-Green-Refactorサイクル<br>- pytest 8.0+で単体テスト・統合テスト・契約テスト<br>- 目標カバレッジ: 90%以上<br>- 決定的な入力（コマンドライン引数）→決定的な出力 |

### Critical Rules Compliance

| Rule | Status | Notes |
|------|--------|-------|
| **C001: ルール歪曲禁止・最上位命令遵守** | ✅ PASS | すべてのルールを厳密に遵守 |
| **C002: エラー迂回絶対禁止・主観判断排除** | ✅ PASS | すべてのエラーは`SpecKitDocsError`例外として発生、エラーメッセージに「ファイルパス」「エラー種類」「推奨アクション」を含める |
| **C003: 冒頭表示必須** | ✅ PASS | 実装時にチャット冒頭で原則を表示 |
| **C004: 理想実装ファースト原則** | ✅ PASS | 各機能（P1、P2、P3）は理想品質で実装、「とりあえず動く」実装は禁止 |
| **C005: 記録管理徹底** | ✅ PASS | コミットメッセージ、コメント、spec-kitメモリーシステム（`.specify/memory/`）を活用 |
| **C006: 堅牢コード品質** | ✅ PASS | ruff（linter/formatter）、mypy（type checker）を使用、コミット前チェック必須 |
| **C007: 品質例外化禁止** | ✅ PASS | 時間制約・進捗圧力を理由とした品質妥協は禁止 |
| **C008: ドキュメント整合性絶対遵守** | ✅ PASS | 実装前にspec.md、plan.md、tasks.mdを確認、仕様曖昧時は実装停止 |
| **C009: 実装計画ブランチ作成必須** | ✅ PASS | 現在のブランチ: `001-draft-init-spec`、mainブランチへの直接コミット禁止 |
| **C010: テスト駆動開発必須** | ✅ PASS | Red-Green-Refactorサイクル、実装前テスト作成プロトコル |
| **C011: Data Accuracy** | ✅ PASS | 一次データ推測禁止、環境変数未設定時は明示的エラー |
| **C012: DRY Principle** | ✅ PASS | 本家spec-kitのtyperパターン（`typer.confirm()`、`typer.Option()`）を再利用、重複実装禁止 |
| **C013: Refactoring Standards** | ✅ PASS | V2クラス作成禁止、既存クラス修正優先 |
| **C014: No-Compromise Implementation** | ✅ PASS | 妥協実装絶対禁止、各フェーズ（P1、P2、P3）で理想品質実装 |

**Overall Gate Status**: ✅ **PASS** - 憲章違反なし、Phase 0 research開始可能

## Project Structure

### Documentation (this feature)

```
specs/001-draft-init-spec/
├── spec.md              # 機能仕様書（既存、8 Clarificationセッション完了）
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command) - 次のステップで生成
├── data-model.md        # Phase 1 output (/speckit.plan command) - Phase 0後に生成
├── quickstart.md        # Phase 1 output (/speckit.plan command) - Phase 0後に生成
├── contracts/           # Phase 1 output (/speckit.plan command) - Phase 0後に生成
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/
├── speckit_docs/                # メインパッケージ
│   ├── __init__.py
│   ├── cli/                     # CLIエントリポイント
│   │   ├── __init__.py
│   │   ├── main.py              # typer.Typer()アプリケーション、entry point
│   │   └── install_handler.py  # speckit-docs installコマンド実装
│   ├── commands/                # コマンドテンプレート（importlib.resources経由）
│   │   ├── speckit.doc-init.md # /speckit.doc-initプロンプト定義
│   │   └── speckit.doc-update.md # /speckit.doc-updateプロンプト定義
│   ├── scripts/                 # バックエンドスクリプト（非対話的実行）
│   │   ├── __init__.py
│   │   ├── doc_init.py          # ドキュメント初期化（コマンドライン引数のみ）
│   │   └── doc_update.py        # ドキュメント更新（コマンドライン引数のみ）
│   ├── generators/              # ドキュメントジェネレータ（Strategy Pattern）
│   │   ├── __init__.py
│   │   ├── base.py              # BaseGenerator抽象クラス（4メソッド）
│   │   ├── sphinx.py            # SphinxGenerator実装
│   │   └── mkdocs.py            # MkDocsGenerator実装
│   ├── parsers/                 # spec-kit仕様解析
│   │   ├── __init__.py
│   │   ├── spec_parser.py       # spec.md解析
│   │   ├── plan_parser.py       # plan.md解析
│   │   └── tasks_parser.py      # tasks.md解析
│   ├── utils/                   # ユーティリティ
│   │   ├── __init__.py
│   │   ├── git.py               # Git操作（GitPython使用）
│   │   ├── fs.py                # ファイルシステム操作
│   │   └── template.py          # Jinja2テンプレートエンジン
│   └── exceptions.py            # SpecKitDocsError例外定義

tests/
├── contract/                    # 契約テスト（CLIインターフェース検証）
│   ├── __init__.py
│   ├── test_cli_install.py      # speckit-docs installコマンドテスト
│   ├── test_doc_init.py         # doc_init.pyスクリプトテスト
│   └── test_doc_update.py       # doc_update.pyスクリプトテスト
├── integration/                 # 統合テスト（実際のspec-kitプロジェクト使用）
│   ├── __init__.py
│   ├── test_sphinx_workflow.py  # Sphinx初期化→更新ワークフロー
│   └── test_mkdocs_workflow.py  # MkDocs初期化→更新ワークフロー
└── unit/                        # 単体テスト
    ├── __init__.py
    ├── test_generators_base.py  # BaseGeneratorテスト
    ├── test_generators_sphinx.py # SphinxGeneratorテスト
    ├── test_generators_mkdocs.py # MkDocsGeneratorテスト
    ├── test_parsers_spec.py     # spec_parserテスト
    ├── test_parsers_plan.py     # plan_parserテスト
    ├── test_parsers_tasks.py    # tasks_parserテスト
    ├── test_utils_git.py        # Gitユーティリティテスト
    ├── test_utils_fs.py         # ファイルシステムユーティリティテスト
    └── test_utils_template.py   # テンプレートエンジンテスト
```

**Structure Decision**: Single project（CLIツール）構造を選択。理由：
1. spec-kit-docsは単一のPythonパッケージとして配布される独立したCLIツール
2. フロントエンド・バックエンド分離は不要（バックエンドスクリプトもPythonパッケージに含まれる）
3. spec-kitの`specify-cli`パッケージと同じ構造パターンに従う（一貫性）

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**該当なし** - すべての憲章原則とクリティカルルールに準拠しており、正当化が必要な違反はありません。

---

## Phase 0: Research (完了)

**Status**: ✅ Completed

**Artifacts**:
- [research.md](./research.md) - 27の技術的決定を記録（8 Clarificationセッションから抽出）

**Key Research Findings**:
1. **CLIフレームワーク**: typer採用（本家spec-kitとの一貫性、argparseから変更）
2. **ドキュメントツール**: Sphinx（MyST Markdown）、MkDocs（Material theme）
3. **インストール方法**: `uv tool install`標準化（Session 2025-10-14決定）
4. **アーキテクチャパターン**: BaseGenerator（4メソッド: `initialize()`, `generate_feature_page()`, `update_navigation()`, `validate()`）
5. **非対話的実行**: バックエンドスクリプトは`input()`を使用せず、コマンドライン引数のみで動作
6. **コード品質**: ruff（E, F, W, I）、mypy、pytest、TDD必須
7. **Git変更検出**: GitPython 3.1+でインクリメンタル更新

**Unknowns Resolved**: すべての技術的不明点が解決されました（「NEEDS CLARIFICATION」なし）。

---

## Phase 1: Design & Contracts (完了)

**Status**: ✅ Completed

**Artifacts**:
- [data-model.md](./data-model.md) - 9つのエンティティ定義（SpecKitProject、Feature、Entity、APIEndpoint、DocumentationSite、Audience、SynthesisResult、FeatureStatus、BaseGenerator）
- [quickstart.md](./quickstart.md) - エンドユーザー向けクイックスタートガイド
- contracts/ - **省略**（CLIツールのためAPI契約不要）

**Key Design Decisions**:
1. **Entities**: すべてPython 3.11+型ヒント、`@dataclass(frozen=True)`で不変性保証
2. **BaseGenerator**: 抽象クラスとして4つの必須メソッドを定義（Strategy Pattern）
3. **Error Handling**: `SpecKitDocsError`例外で統一、エラーメッセージに「ファイルパス」「エラー種類」「推奨アクション」を含める
4. **Testing**: TDD必須、Red-Green-Refactorサイクル、90%以上のカバレッジ目標

**Agent Context Update**: ✅ Completed - CLAUDE.md更新済み（Python 3.11+、依存関係追加）

**Constitution Check Re-evaluation**: ✅ **PASS** - Phase 1デザイン後も憲章違反なし

---

## Next Steps

このプランニングフェーズ（`/speckit.plan`）は完了しました。次のステップ：

1. **タスク生成**: `/speckit.tasks`コマンドを実行してtasks.mdを生成
2. **実装開始**: tasks.mdに従ってMVP（P1）機能を実装
   - US3: speckit-docs install（インストールコマンド）
   - US1: /speckit.doc-init（ドキュメント初期化）
   - US2: /speckit.doc-update（ドキュメント更新）
3. **TDD適用**: 各タスクでRed-Green-Refactorサイクルを遵守
4. **品質ゲート**: ruff、mypy、pytestすべて通過後にコミット

**Estimated Implementation Time**: MVP（P1）は約2-3週間と見積もり（TDD、品質ゲート遵守含む）
