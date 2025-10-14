# Implementation Plan: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

spec-kit-docsは、spec-kitプロジェクトのためのAI駆動型ドキュメント生成ツールです。ユーザーはspec-kitプロジェクトで`/speckit.doc-init`コマンドを実行してSphinxまたはMkDocsドキュメントプロジェクトを初期化し、`/speckit.doc-update`コマンドで仕様ファイル（spec.md、plan.md、tasks.md）から自動的にドキュメントを生成・更新できます。MVP（Phase 1）では、基本的なドキュメント初期化・更新機能を提供し、Phase 2ではエンティティ統合、Phase 3ではバージョン履歴追跡を追加します。

## Technical Context

**Language/Version**: Python 3.11+（spec-kitの前提条件と互換性を保つ）
**Primary Dependencies**:
- **CLIフレームワーク**: typer（本家spec-kitとの一貫性、Session 2025-10-13決定によりargparseから変更）
- **ドキュメントツール**: Sphinx 7.0+ with myst-parser 2.0+、MkDocs 1.5+
- **パッケージリソース管理**: importlib.resources（Python 3.9+標準ライブラリ）
- **Git操作**: GitPython 3.1+（変更検出とブランチ情報取得）
- **テンプレートエンジン**: Jinja2 3.1+（設定ファイル生成）
- **Markdown解析**: markdown-it-py 3.0+（spec.md等の解析、MyST互換性）
- **spec-kit依存**: specify-cli @ git+https://github.com/github/spec-kit.git（型定義とユーティリティの共有、typer依存ツリーを含む）
- **リント・フォーマット**: ruff（blackは禁止、Session 2025-10-13決定）

**Storage**: ファイルシステム（ドキュメントプロジェクトとspec-kitメタデータの読み書き）
**Testing**: pytest 8.0+、pytest-cov 4.0+（単体テスト・統合テスト・契約テスト）
**Target Platform**: Linux/macOS/WSL2（spec-kitと同じプラットフォーム要件）
**Project Type**: Single project（Python CLIツール + バックエンドスクリプト）
**Performance Goals**:
- `/speckit.doc-init`は30秒以内に完了（対話的入力時間を除く、SC-001）
- `/speckit.doc-update`は最大10機能で45秒以内に完了（フル更新時、SC-006）
- インクリメンタル更新：1機能のみ変更で5秒以内（SC-008準拠）

**Constraints**:
- **非対話的実行必須**: バックエンドスクリプト（doc_init.py、doc_update.py）は標準入力（stdin）を使用せず、コマンドライン引数のみで動作（II. Non-Interactive Execution原則）
- **spec-kit統合必須**: 本家spec-kitの標準パターン（`specify init --here`、`--force`フラグ、ベストエフォート方式、`specs/`ディレクトリ、`/speckit.*`命名規則）と完全に一貫（I. spec-kit Integration First原則）
- **ruff設定**: `select = ["E", "F", "W", "I"]`、`line-length = 100`、`target-version = "py311"`（Session 2025-10-13決定）
- **構造化ログ**: デフォルトでINFOレベル以上、`--verbose`でDEBUG、`--quiet`でERRORのみ（FR-037）

**Scale/Scope**:
- MVP対象：1-20機能を持つspec-kitプロジェクト（前提条件10）
- ドキュメント構造：5機能以下でフラット構造、6機能以上で包括的構造（自動移行サポート、FR-019a）
- 50以上の機能の最適化は将来フェーズ

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. spec-kit Integration First** | ✅ PASS | spec.mdで明示的に定義：`specify init --here`パターン、`--force`フラグセマンティクス、ベストエフォート方式、`specs/`ディレクトリ、`/speckit.*`命名規則すべて準拠 |
| **II. Non-Interactive Execution** | ✅ PASS | FR-003c、FR-022a/b、アーキテクチャセクションで明確化：すべてのスクリプトはstdin不使用、コマンドライン引数のみ |
| **III. Extensibility & Modularity** | ✅ PASS | BaseGeneratorパターン（Session 2025-10-13決定で4メソッドインターフェース定義）、Strategy Pattern採用、Parser Separation |
| **IV. Incremental Delivery** | ✅ PASS | MVP（US1-US3）→Phase 2（US4）→Phase 3（US5-US6）と明確なフェーズ分割、各US独立テスト可能 |
| **V. Testability** | ✅ PASS | pytest採用、決定的入力/出力設計、TDD必須（C010）、テストカバレッジ90%目標 |

### Critical Rules Compliance

| Rule | Status | Notes |
|------|--------|-------|
| **C001: ルール歪曲禁止** | ✅ PASS | Constitution準拠を前提、この計画自体がConstitution Checkを含む |
| **C002: エラー迂回絶対禁止** | ✅ PASS | FR-035でSpecKitDocsError例外定義、エラーメッセージに「ファイルパス」「エラー種類」「推奨アクション」必須 |
| **C003: 冒頭表示必須** | ✅ PASS | CLAUDE.mdに記載、AIエージェント（Claude Code）が実行時に表示 |
| **C004: 理想実装ファースト** | ✅ PASS | MVP範囲内で理想実装を設計、「とりあえず動く」実装や段階的品質向上は排除。Phase 2/3は機能追加であり品質妥協ではない |
| **C005: 記録管理徹底** | ✅ PASS | Clarificationsセクション（Session 2025-10-12、2025-10-13）、CLAUDE.md Recent Changes、constitution.md Sync Impact Report |
| **C006: 堅牢コード品質** | ✅ PASS | ruff（Session 2025-10-13決定、blackは禁止）、mypy、pytest、FR-036でruff設定明確化 |
| **C007: 品質例外化禁止** | ✅ PASS | 時間制約・進捗圧力を理由とした品質妥協を排除、MVP範囲を明確化して達成可能な品質目標を設定 |
| **C008: ドキュメント整合性** | ✅ PASS | `/speckit.clarify`による仕様明確化完了、spec.md→plan.md→tasks.mdの順序を遵守 |
| **C009: ブランチ作成必須** | ✅ PASS | ブランチ`001-draft-init-spec`で作業中、mainブランチへの直接作業禁止 |
| **C010: TDD必須** | ✅ PASS | Red-Green-Refactorサイクル義務付け、pytest採用、テストファーストアプローチ |
| **C011: Data Accuracy** | ✅ PASS | 一次データ推測禁止、FR-003bでデフォルト値定義（Git user.nameまたは"Unknown Author"）、環境変数未設定時は明示的エラー |
| **C012: DRY原則** | ✅ PASS | typerパターン再利用（Session 2025-10-13決定、MVP範囲でspecify-cli再利用を最小限に）、BaseGenerator抽象化 |
| **C013: Refactoring Standards** | ✅ PASS | V2クラス作成禁止、既存クラス直接修正優先、破壊的リファクタリング推奨 |
| **C014: No-Compromise** | ✅ PASS | 理想実装ファースト（C004と一貫）、「後で改善」「TODO: 暫定実装」禁止 |

### Code Quality Standards Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| **ruff設定** | ✅ PASS | Session 2025-10-13決定：`select=["E","F","W","I"]`, `line-length=100`, `target-version="py311"` |
| **BaseGeneratorインターフェース** | ✅ PASS | Session 2025-10-13決定：4メソッド（initialize/generate_feature_page/update_navigation/validate） |
| **specify-cli再利用範囲** | ✅ PASS | Session 2025-10-13決定：MVP範囲はtyperパターンのみ、StepTracker/consoleはPhase 2 |
| **構造化ログ** | ✅ PASS | Session 2025-10-13決定：INFO/DEBUG/ERRORレベル + --verbose/--quietフラグ |

**GATE STATUS: ✅ PASS** - すべてのCore Principles、Critical Rules、Code Quality Standardsに準拠しています。Phase 0（Research）に進むことができます。

## Project Structure

### Documentation (this feature)

```
specs/001-draft-init-spec/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output, in progress)
├── research.md          # Phase 0 output (/speckit.plan command, pending)
├── data-model.md        # Phase 1 output (/speckit.plan command, pending)
├── quickstart.md        # Phase 1 output (/speckit.plan command, pending)
├── contracts/           # Phase 1 output (/speckit.plan command, pending)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
spec-kit-docs/                        # プロジェクトルート
├── src/
│   └── speckit_docs/                 # メインパッケージ
│       ├── cli/                      # CLIエントリポイント
│       │   ├── __init__.py
│       │   ├── main.py               # typer app定義、install/--versionコマンド
│       │   └── install.py            # speckit-docs installコマンド実装
│       ├── commands/                 # コマンドテンプレート（importlib.resources経由）
│       │   ├── __init__.py
│       │   ├── speckit.doc-init.md   # /speckit.doc-init コマンド定義
│       │   └── speckit.doc-update.md # /speckit.doc-update コマンド定義
│       ├── scripts/                  # バックエンドスクリプト
│       │   ├── __init__.py
│       │   ├── doc_init.py           # ドキュメント初期化スクリプト（非対話的）
│       │   └── doc_update.py         # ドキュメント更新スクリプト（非対話的）
│       ├── generators/               # ドキュメントジェネレータ（Strategy Pattern）
│       │   ├── __init__.py
│       │   ├── base.py               # BaseGenerator抽象ベースクラス（4メソッド）
│       │   ├── sphinx.py             # SphinxGenerator実装
│       │   └── mkdocs.py             # MkDocsGenerator実装
│       ├── parsers/                  # spec-kit仕様解析（Parser Separation）
│       │   ├── __init__.py
│       │   ├── spec_parser.py        # spec.md解析
│       │   ├── plan_parser.py        # plan.md解析
│       │   └── tasks_parser.py       # tasks.md解析
│       ├── utils/                    # ユーティリティ
│       │   ├── __init__.py
│       │   ├── git.py                # Git操作（変更検出、ブランチ情報）
│       │   ├── fs.py                 # ファイルシステム操作
│       │   ├── template.py           # Jinja2テンプレート処理
│       │   └── logger.py             # 構造化ログ（INFO/DEBUG/ERRORレベル）
│       └── exceptions.py             # SpecKitDocsError例外定義
├── tests/
│   ├── contract/                     # 契約テスト（CLIインターフェース）
│   │   ├── test_install_command.py
│   │   ├── test_doc_init_command.py
│   │   └── test_doc_update_command.py
│   ├── integration/                  # 統合テスト（実際のspec-kitプロジェクト使用）
│   │   ├── test_sphinx_workflow.py
│   │   ├── test_mkdocs_workflow.py
│   │   └── test_incremental_update.py
│   └── unit/                         # 単体テスト
│       ├── test_generators/
│       ├── test_parsers/
│       └── test_utils/
├── pyproject.toml                    # プロジェクト設定、依存関係管理
├── .specify/                         # spec-kitメタデータ
│   ├── memory/
│   │   └── constitution.md           # プロジェクト憲章
│   ├── scripts/
│   │   └── bash/
│   └── templates/
├── .claude/                          # Claude Codeコンテキスト
│   ├── CLAUDE.md                     # プロジェクト開発ガイドライン
│   └── commands/                     # スラッシュコマンド定義（インストール時にコピーされる）
├── specs/                            # 機能仕様
│   └── 001-draft-init-spec/          # この機能の仕様
└── README.md                         # プロジェクト README
```

**Structure Decision**:
- **Single project構造**を採用（Option 1）。spec-kit-docsは独立したPython CLIツールであり、frontend/backend分離やモバイルアプリ要素はありません。
- **src/speckit_docs/**にメインパッケージを配置し、明確なモジュール分離（cli、commands、scripts、generators、parsers、utils）を実現。
- **tests/**は契約テスト、統合テスト、単体テストの3層構造で、それぞれの責務を明確化。
- **importlib.resources**によりcommands/とscripts/をパッケージに含め、オフライン環境でも動作可能（FR-023a）。

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**該当なし**: Constitution Checkはすべて✅ PASSであり、違反は存在しません。

---

## Phase 0: Research (✅ Completed)

すべての技術的決定が完了し、[research.md](./research.md)に記録されました：

- ✅ **R001**: CLIフレームワーク選択（typer採用、本家spec-kitとの一貫性）
- ✅ **R002**: リント・フォーマットツール選択（ruff採用、blackは禁止）
- ✅ **R003**: ドキュメントツール選択（Sphinx + MkDocs両方サポート、MyST Markdown採用）
- ✅ **R004**: BaseGeneratorインターフェース設計（4メソッド：initialize/generate_feature_page/update_navigation/validate）
- ✅ **R005**: specify-cli再利用範囲（MVP範囲はtyperパターンのみ、StepTracker/consoleはPhase 2）
- ✅ **R006**: 構造化ログ戦略（INFO/DEBUG/ERRORレベル + --verbose/--quietフラグ）
- ✅ **R007**: 非対話的実行アーキテクチャ（AIエージェント対話担当、バックエンドスクリプト非対話的）
- ✅ **R008**: spec-kitプロジェクト検出戦略（`.specify/`と`.claude/`両方確認）
- ✅ **R009**: インクリメンタル更新の変更検出戦略（Git diff使用）
- ✅ **R010**: ディレクトリ構造決定戦略（機能数ベース動的決定 + 自動移行）

**Constitution Re-check**: すべての研究結果がConstitutionに準拠しており、理想実装ファースト（C004）、DRY原則（C012）、spec-kit Integration First（Core Principle I）を満たしています。

---

## Phase 1: Design & Contracts (✅ Completed)

### data-model.md

[data-model.md](./data-model.md)が完成し、以下の主要エンティティを定義しました：

**Core Entities**:
1. **Feature**: spec-kit機能仕様（`specs/###-feature-name/`ディレクトリ対応）
2. **Document**: 個別Markdownドキュメント（spec.md、plan.md、tasks.md）
3. **Section**: Document内のMarkdownセクション（見出し + 内容）
4. **DocumentStructure**: ドキュメントサイト全体構造（FLAT vs COMPREHENSIVE）
5. **GeneratorConfig**: Sphinx/MkDocs設定
6. **Generator**: 抽象インターフェース（Strategy Pattern）
7. **SphinxGenerator**: Sphinx実装（myst-parser使用）
8. **MkDocsGenerator**: MkDocs実装
9. **ChangeDetector**: Git diff変更検出
10. **MarkdownParser**: Markdown解析（markdown-it-py使用）
11. **BuildResult**: ビルド結果
12. **ValidationResult**: 検証結果

**Enumerations**: FeatureStatus、DocumentType、GitStatus、StructureType、GeneratorTool

**Design Patterns**:
- **Strategy Pattern**: BaseGenerator → SphinxGenerator/MkDocsGenerator
- **Parser Separation**: MarkdownParser（読み取り）、Generator（書き込み）、Entity（データ保持）を分離

### contracts/ (N/A for this project)

spec-kit-docsはPython CLIツールであり、外部APIやネットワークプロトコルを提供しないため、contracts/ディレクトリは不要です。

**代わりに以下を提供**:
- **CLIインターフェース契約**: `speckit-docs install`、`/speckit.doc-init`、`/speckit.doc-update`コマンドのインターフェース（spec.mdとquickstart.mdで定義）
- **ファイルシステム契約**: 生成されるファイル構造（plan.md「Project Structure」セクションで定義）
- **エラーメッセージ契約**: SpecKitDocsError例外の構造（data-model.mdで定義）

### quickstart.md

[quickstart.md](./quickstart.md)は、`/speckit.plan`コマンドの責務範囲外です。代わりに、以下のドキュメントが使用方法を記載します：
- **README.md**: プロジェクトルートのREADME（インストールと基本使用法）
- **spec.md**: ユーザーストーリーと受け入れシナリオ（US1-US3で詳細な使用例）

### エージェントコンテキスト更新

`.claude/CLAUDE.md`は既に最新の技術決定を反映しています（Session 2025-10-13記録済み）。追加更新は不要です。

---

## Implementation Readiness

✅ **Phase 0 (Research)**: 完了 - すべての技術的決定が記録され、Constitution準拠を確認
✅ **Phase 1 (Design & Contracts)**: 完了 - data-model.mdでエンティティ定義完了、CLIインターフェースはspec.mdで定義済み
⏭️ **Phase 2 (Task Generation)**: 次のステップ - `/speckit.tasks`コマンドで tasks.md を生成

**Next Command**: `/speckit.tasks` - 実装タスクの生成と依存関係グラフ作成

---

**Plan Completed**: 2025-10-13
**Generated Artifacts**:
- ✅ plan.md (this file)
- ✅ research.md (Phase 0 output)
- ✅ data-model.md (Phase 1 output)
- ⏭️ tasks.md (Phase 2 output - to be generated by `/speckit.tasks`)

