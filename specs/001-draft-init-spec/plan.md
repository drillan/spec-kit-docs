# Implementation Plan: spec-kit-docs - AI-Driven Documentation Generation for spec-kit Projects

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

spec-kit-docsは、spec-kitプロジェクトの仕様ファイル（spec.md、plan.md、tasks.md）から、SphinxまたはMkDocs形式の包括的なドキュメントを自動生成するツールです。主な機能：

1. **LLM駆動のドキュメント変換**（デフォルト有効）: Functional Requirements等の技術的な仕様をエンドユーザーフレンドリーな自然言語に変換
2. **インクリメンタル更新**: Git diffベースで変更された機能のみを更新し、LLM変換結果をキャッシュして再利用
3. **マルチフォーマットサポート**: SphinxとMkDocsの両方に対応し、Strategy Patternで拡張可能
4. **spec-kit統合**: スラッシュコマンド（`/doc-init`、`/doc-update`）経由でClaude Code環境から直接実行

技術的アプローチ：
- AIエージェント（Claude Code）がLLM変換とユーザー対話を担当
- バックエンドスクリプト（Python）が非対話的にドキュメント生成を実行
- `.claude/.cache/llm-transforms.json`にMD5ハッシュベースのキャッシュを永続化

## Technical Context

**Language/Version**: Python 3.11+ （spec-kit前提条件との互換性）

**Primary Dependencies**:
- **CLIフレームワーク**: typer 0.9+ （本家spec-kitとの一貫性）
- **ドキュメントツール**: Sphinx 7.0+ with myst-parser 2.0+、MkDocs 1.5+ with mkdocs-material 9.0+
- **パッケージリソース管理**: importlib.resources（Python 3.9+標準ライブラリ）
- **Git操作**: GitPython 3.1+ （変更検出とブランチ情報取得）
- **テンプレートエンジン**: Jinja2 3.1+ （設定ファイル生成）
- **Markdown解析**: markdown-it-py 3.0+ （spec.md等の解析、MyST互換性）
- **spec-kit依存**: specify-cli @ git+https://github.com/github/spec-kit.git （型定義とユーティリティの共有）

**Storage**: ファイルシステムのみ（ドキュメントプロジェクトとspec-kitメタデータの読み書き）。データベース不要。

**Testing**: pytest 8.0+、pytest-cov 4.0+ （単体テスト・統合テスト・契約テスト）

**Target Platform**: Linux/macOS/WSL2 （spec-kitと同じプラットフォーム要件）

**Project Type**: single （CLI tool + ライブラリ）

**Performance Goals**:
- ドキュメント生成時間: 小規模プロジェクト（10機能未満）は10秒以内、中規模プロジェクト（10-50機能）は60秒以内
- LLM変換: キャッシュ再利用率95%以上（Git diff統合により達成）
- インストール時間: 10秒以内

**Constraints**:
- LLM変換のコンテンツサイズ上限: 1機能あたり10,000トークン
- 非対話的実行: バックエンドスクリプトは標準入力を使用せず、コマンドライン引数のみで動作
- エラーハンドリング: フォールバック動作禁止（憲章準拠）、明示的なエラー返却必須

**Scale/Scope**:
- 想定プロジェクトサイズ: 50機能まで
- 生成ページ数: 数百ページ規模のドキュメント
- ユーザー数: spec-kitエコシステムの全ユーザー（オープンソースツール）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles (from CLAUDE.md)

#### I. Test-First Development (TDD必須)
✅ **PASS**: 仕様にUser Story 7で詳細な受け入れテストシナリオを定義。実装前にテスト作成を要求。

#### II. Non-Interactive Execution
✅ **PASS**: FR-017、FR-018でバックエンドスクリプト（doc_init.py、doc_update.py）が標準入力を使用せず、コマンドライン引数のみで動作することを明記。

#### III. Error Handling (C002)
✅ **PASS**: FR-035ですべてのエラーを`SpecKitDocsError`例外として発生させ、エラーメッセージに「ファイルパス」「エラー種類」「推奨アクション」を含めることを要求。FR-038a-cでLLM変換エラー時の明示的エラー返却を規定（フォールバック禁止）。

#### IV. DRY Principle & Code Reuse (C012)
✅ **PASS**: CLAUDE.mdで「特に本家spec-kitのtyperパターン（`typer.confirm()`、`typer.Option()`等）を再利用する」と明記。重複実装を避ける方針を確立。

#### V. Lint & Format (ruff必須、black禁止)
✅ **PASS**: FR-036でruffの使用を明示（`select = ["E", "F", "W", "I"]`、`line-length = 100`、`target-version = "py311"`）。blackは禁止。

#### VI. Type Hints Required
✅ **PASS**: CLAUDE.mdで「すべての関数とメソッドに型ヒントを付ける（mypy互換）」を要求。

### Architectural Principles

#### Strategy Pattern (Generator)
✅ **PASS**: CLAUDE.mdでBaseGeneratorパターンを定義。Sphinx/MkDocs実装が4つの必須メソッドを実装（`initialize()`, `generate_feature_page()`, `update_navigation()`, `validate()`）。

#### Parser Separation (Separation of Concerns)
✅ **PASS**: プロジェクト構造でパーサー（parsers/）、ジェネレーター（generators/）、エンティティを明確に分離。

### Gates Summary

| Check | Status | Notes |
|-------|--------|-------|
| TDD Required | ✅ PASS | User Story 7で詳細なテストシナリオ定義済み |
| Non-Interactive | ✅ PASS | FR-017, FR-018で明示 |
| Error Handling | ✅ PASS | FR-035, FR-038a-c準拠 |
| DRY & Reuse | ✅ PASS | spec-kit typerパターン再利用方針 |
| Ruff Required | ✅ PASS | FR-036で設定明示 |
| Type Hints | ✅ PASS | CLAUDE.mdで必須化 |
| Strategy Pattern | ✅ PASS | BaseGenerator定義済み |
| Parser Separation | ✅ PASS | 構造で分離済み |

**Result**: All gates PASS ✅ - Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```
specs/001-draft-init-spec/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
spec-kit-docs/                        # プロジェクトルート
├── src/
│   └── speckit_docs/                 # メインパッケージ
│       ├── cli/                      # CLIエントリポイント
│       │   ├── __init__.py
│       │   └── main.py               # typer app定義
│       ├── commands/                 # コマンドテンプレート（importlib.resources経由）
│       │   ├── doc-init.md
│       │   └── doc-update.md
│       ├── scripts/                  # バックエンドスクリプト
│       │   ├── doc_init.py           # /doc-init実装
│       │   └── doc_update.py         # /doc-update実装
│       ├── generators/               # ドキュメントジェネレータ（Strategy Pattern）
│       │   ├── base.py               # BaseGenerator抽象ベースクラス
│       │   ├── sphinx.py             # SphinxGenerator実装
│       │   └── mkdocs.py             # MkDocsGenerator実装
│       ├── parsers/                  # spec-kit仕様解析
│       │   ├── spec_parser.py        # spec.md解析
│       │   ├── plan_parser.py        # plan.md解析
│       │   └── tasks_parser.py       # tasks.md解析
│       ├── utils/                    # ユーティリティ
│       │   ├── git.py                # Git diff検出
│       │   ├── fs.py                 # ファイルシステム操作
│       │   ├── template.py           # Jinja2テンプレート処理
│       │   └── cache.py              # LLM変換キャッシュ管理
│       └── exceptions.py             # SpecKitDocsError例外定義
├── tests/
│   ├── contract/                     # 契約テスト（CLIインターフェース）
│   │   ├── test_install_command.py
│   │   ├── test_doc_init_command.py
│   │   └── test_doc_update_command.py
│   ├── integration/                  # 統合テスト（実際のspec-kitプロジェクト使用）
│   │   ├── test_sphinx_generation.py
│   │   └── test_mkdocs_generation.py
│   └── unit/                         # 単体テスト
│       ├── test_generators/
│       ├── test_parsers/
│       └── test_utils/
├── pyproject.toml                    # プロジェクト設定、依存関係管理
├── .specify/                         # spec-kitメタデータ
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   └── tasks-template.md
│   └── scripts/                      # spec-kit標準スクリプト
└── specs/                            # 機能仕様
    └── 001-draft-init-spec/          # この機能の仕様
```

**Structure Decision**: Single project構造を採用。spec-kit-docsはCLIツール兼ライブラリであり、バックエンド/フロントエンドの分離は不要。src/speckit_docs/配下にモジュールを配置し、明確な責務分担（parsers/、generators/、utils/）を実現。

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

N/A - All gates passed without violations.

## Phase 0: Research (Completed)

**Status**: ✅ Completed
**Artifacts**: `research.md` (existing)

研究フェーズは完了済み。以下の技術決定を記録：
- CLI Framework: typer 0.9+ （spec-kit一貫性）
- Documentation Generators: Sphinx 7.0+ + MkDocs 1.5+ （Strategy Pattern）
- Markdown Parser: markdown-it-py 3.0+ （MyST互換）
- Git Operations: GitPython 3.1+ （インクリメンタル更新）
- Template Engine: Jinja2 3.1+ （設定ファイル生成）
- LLM Cache: JSON + MD5 （高速、人間可読）
- Error Handling: SpecKitDocsError （構造化メッセージ）
- Testing: pytest 8.0+ （TDD準拠）
- LLM Default: デフォルト有効（opt-out via `--no-llm-transform`）
- Execution Model: 非対話的（憲章準拠）

すべての技術選定は代替案との比較、根拠、ベストプラクティスを記録済み。

## Phase 1: Design & Contracts (Completed)

**Status**: ✅ Completed
**Artifacts**:
- `data-model.md` (existing)
- `contracts/` directory (existing)
- `quickstart.md` (existing)
- `CLAUDE.md` updated (agent context)

### data-model.md
主要エンティティを定義：
- **SpecKitProject**: プロジェクトルート、設定、specsディレクトリ
- **Feature**: 機能ID、ブランチ名、spec.md/plan.md/tasks.md
- **BaseGenerator**: 抽象ベースクラス（Strategy Pattern）
- **SphinxGenerator / MkDocsGenerator**: 具体的実装
- **SpecParser / PlanParser / TasksParser**: Markdown解析
- **LLMTransformCache**: キャッシュ管理（MD5ハッシュ、JSON永続化）
- **SpecKitDocsError**: 構造化エラー

### contracts/
CLIインターフェース契約を定義：
- `install-command.md`: `speckit-docs install` 契約
- `doc-init-command.md`: `/doc-init` 契約
- `doc-update-command.md`: `/doc-update` 契約

各契約は入力（引数、環境変数）、出力（stdout/stderr）、終了コード、エラーケースを明示。

### quickstart.md
ユーザーオンボーディングガイド：
1. インストール手順（`uv tool install`）
2. プロジェクト初期化（`/doc-init`）
3. ドキュメント更新（`/doc-update`）
4. トラブルシューティング

### Agent Context Update
`CLAUDE.md`を更新：
- 最終更新日: 2025-10-16
- 追加技術: Python 3.11+、ファイルシステムのみ（データベース不要）
- プロジェクトタイプ: single （CLI tool + ライブラリ）

## Constitution Check (Post-Design Re-evaluation)

*GATE: Re-check after Phase 1 design completion*

### Re-evaluation Results

| Check | Status | Notes |
|-------|--------|-------|
| TDD Required | ✅ PASS | テスト構造定義済み（contract/integration/unit） |
| Non-Interactive | ✅ PASS | data-model.mdでバックエンドスクリプトの引数ベース実行を確認 |
| Error Handling | ✅ PASS | SpecKitDocsErrorエンティティ定義済み、構造化メッセージ対応 |
| DRY & Reuse | ✅ PASS | BaseGeneratorパターンで重複実装回避 |
| Ruff Required | ✅ PASS | pyproject.tomlで設定明示済み |
| Type Hints | ✅ PASS | data-model.mdのエンティティ定義で型ヒント必須化 |
| Strategy Pattern | ✅ PASS | BaseGenerator/SphinxGenerator/MkDocsGenerator実装確認 |
| Parser Separation | ✅ PASS | parsers/generators/utils明確分離 |

**Result**: All gates PASS ✅ - Design compliant with constitution.

**新規リスク**: なし。すべての設計決定が憲章原則に準拠。

## Next Steps

1. **Phase 2**: `/speckit.tasks`コマンドを実行してtasks.mdを生成
2. **Implementation**: `/speckit.implement`コマンドでタスクを順次実行
3. **Testing**: TDDサイクルに従い、各タスク実装前にテストを作成

**注意**: tasks.mdは既に存在していますが、最新のspec.md（LLM変換デフォルト有効化）とplan.mdを反映させるため、`/speckit.tasks`の再実行を推奨。

