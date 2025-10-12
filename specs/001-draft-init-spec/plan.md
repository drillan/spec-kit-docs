# Implementation Plan: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

spec-kit-docsは、spec-kitプロジェクトのMarkdown仕様（spec.md、plan.md、tasks.md）から、SphinxまたはMkDocsを使用して統一されたドキュメントサイトを生成するspec-kit拡張機能です。Claude Codeのスラッシュコマンド（`/speckit.doc-init`と`/speckit.doc-update`）として動作し、Pythonスクリプトでドキュメント構造を初期化・更新します。Sphinxの場合はMarkdown + myst-parserをデフォルトとし、フォーマット変換なしで仕様からドキュメントを生成します。

## Technical Context

**Language/Version**: Python 3.11+（spec-kit前提条件との互換性）
**Primary Dependencies**:
  - Core: `pathlib`, `subprocess`, `json`, `argparse`（標準ライブラリ）
  - Sphinx統合: `sphinx` 7.0+, `myst-parser` 2.0+
  - MkDocs統合: `mkdocs` 1.5+
  - Markdown解析: `markdown-it-py`（MyST構文対応）
  - Git操作: `GitPython`（変更検出用）

**Storage**: ファイルシステムのみ（`.specify/specs/`, `docs/`, `.claude/commands/`への読み書き）

**Testing**: `pytest`（ユニット・統合テスト）、ドキュメントビルドテスト（Sphinx `make html`、MkDocs `mkdocs build`）

**Target Platform**:
  - Linux, macOS, Windows（Python実行可能環境）
  - Claude Code実行環境（AI エージェント）
  - spec-kit 0.0.19+互換

**Project Type**: single（CLI toolsとして実装、spec-kit拡張機能）

**Performance Goals**:
  - doc-init: 30秒以内（対話入力除く）
  - doc-update: 45秒以内（10機能プロジェクト、AI統合除く）
  - インクリメンタル更新で変更ファイルのみ再処理

**Constraints**:
  - spec-kitプロジェクト構造に依存（`.specify/`, `.claude/`）
  - Git リポジトリ必須（変更検出）
  - Markdown→Markdownでフォーマット統一（変換ロジック最小化）
  - オフライン動作可能（ドキュメント生成はローカル）

**Scale/Scope**:
  - 対象: 1-20機能の典型的spec-kitプロジェクト
  - 最適化: 50機能まで段階的処理
  - ファイルサイズ: spec.md通常数KB-数十KB
  - 生成ドキュメント: 静的HTML、サーバー不要

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: constitution.mdがまだテンプレートのため、一般的なソフトウェア設計原則でチェックします。

| Principle | Status | Notes |
|-----------|--------|-------|
| Single Responsibility | ✅ PASS | 2つのコマンド（init/update）は明確に分離、各々単一責任 |
| Modularity | ✅ PASS | Sphinx/MkDocsハンドラーは独立モジュール、拡張可能 |
| Testability | ✅ PASS | CLIツール、stdin/stdout、ファイルI/O - モック可能 |
| Dependencies | ✅ PASS | 標準ライブラリ優先、外部依存は最小（Sphinx/MkDocs/GitPython） |
| Error Handling | ✅ PASS | FR-033で明確なエラーメッセージ要件あり |
| Performance | ✅ PASS | SC-001,SC-006で具体的な性能目標（30秒/45秒） |
| Simplicity | ✅ PASS | Markdown→Markdownで変換ロジック不要、YAGNI原則 |

**Violations**: なし

**Design Decision**: spec-kitの既存パターンに従い、Pythonスクリプト + Claude Codeコマンド定義の構成を採用。

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/
├── speckit_docs/
│   ├── __init__.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── doc_init.py          # /speckit.doc-init implementation
│   │   └── doc_update.py        # /speckit.doc-update implementation
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract generator interface
│   │   ├── sphinx.py            # Sphinx + myst-parser generator
│   │   └── mkdocs.py            # MkDocs generator
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── markdown_parser.py   # spec.md/plan.md/tasks.md parser
│   │   └── feature_scanner.py   # .specify/specs/ discovery
│   ├── templates/
│   │   ├── sphinx/
│   │   │   ├── conf.py.j2       # Sphinx conf.py template (myst-parser)
│   │   │   ├── index.md.j2      # Sphinx index.md template
│   │   │   └── Makefile.j2
│   │   └── mkdocs/
│   │       ├── mkdocs.yml.j2    # MkDocs config template
│   │       └── index.md.j2
│   └── utils/
│       ├── __init__.py
│       ├── git.py               # Git diff integration
│       ├── prompts.py           # Interactive prompts
│       └── validation.py        # spec-kit project validation

tests/
├── unit/
│   ├── test_doc_init.py
│   ├── test_doc_update.py
│   ├── test_generators.py
│   └── test_parsers.py
├── integration/
│   ├── test_sphinx_workflow.py  # End-to-end Sphinx test
│   ├── test_mkdocs_workflow.py  # End-to-end MkDocs test
│   └── fixtures/
│       └── sample_speckit_project/
└── contract/
    ├── test_cli_interface.py    # CLI contract tests
    └── test_file_outputs.py     # Generated file format tests
```

**Structure Decision**: Single project構造を採用。spec-kit拡張機能として、`.specify/scripts/docs/`にPythonスクリプトを配置し、`.claude/commands/`に2つのコマンド定義を配置します。Pythonパッケージ（`speckit_docs`）として実装し、`pip install`可能にします。

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**Status**: Constitution Check passed - no violations to justify.
