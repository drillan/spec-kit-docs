# Implementation Plan: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

spec-kit-docsは、spec-kitプロジェクトにドキュメント生成機能を追加する拡張パッケージです。`speckit-docs install`コマンドで既存のspec-kitプロジェクトに`/speckit.doc-init`と`/speckit.doc-update`コマンドを追加し、spec.md/plan.md/tasks.mdからSphinx/MkDocsドキュメントを自動生成します。AI エージェント（Claude Code）とバックエンドPythonスクリプトの協調により、対話的なドキュメント初期化とインクリメンタル更新を実現します。

## Technical Context

**Language/Version**: Python 3.11+（spec-kit前提条件との互換性）
**Primary Dependencies**:
- `specify-cli` (Git URL: `git+https://github.com/github/spec-kit.git`) - StepTracker、consoleなどのユーティリティ
- `sphinx` + `myst-parser` 2.0+ (Sphinx使用時)
- `mkdocs` 1.5+ (MkDocs使用時)
- `typer` (CLIフレームワーク)
- `jinja2` (テンプレートエンジン)

**Storage**: ファイルシステム（`docs/` ディレクトリ、`.specify/scripts/docs/`、`.claude/commands/`）
**Testing**: pytest（単体テスト、統合テスト）
**Target Platform**: Linux/macOS/Windows（Python実行環境）
**Project Type**: 単一Pythonパッケージ（CLIツール + ライブラリ）
**Performance Goals**:
- ドキュメント初期化：30秒以内（対話的入力時間を除く）
- ドキュメント更新：10機能プロジェクトで45秒以内
- インクリメンタル更新で変更されていない機能の再処理を回避

**Constraints**:
- 非対話的環境での実行可能性（CI/CD、自動化ワークフロー）
- spec-kitとの一貫性（`specify init --here`パターン、エラーハンドリング）
- オフライン動作可能（パッケージインストール後）

**Scale/Scope**:
- 対象：1-20機能の spec-kit プロジェクト（50機能以上は便利な追加機能）
- インストールファイル数：コマンド定義2つ + スクリプト数個
- MVP範囲：Sphinx/MkDocsサポート、Claude Codeサポート

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: v1.1.0 ratified on 2025-10-13

### Critical Rules Compliance (C001-C014)

| Rule | Compliance | Notes |
|------|-----------|-------|
| C001 (ルール歪曲禁止) | ✅ PASS | すべてのルールを最上位命令として遵守 |
| C002 (エラー迂回禁止) | ✅ PASS | SpecKitDocsErrorで構造化エラー、ベストエフォート方式で部分的失敗を明示（FR-033, FR-035） |
| C003 (冒頭表示必須) | ✅ PASS | AIエージェントが実行時に表示 |
| C004 (理想実装ファースト) | ✅ PASS | 各フェーズは理想品質で実装、段階的改善ではなくIncremental Delivery（機能の段階的配信） |
| C005 (記録管理徹底) | ✅ PASS | spec-kitメモリーシステム活用、各タスク完了後にコミット |
| C006 (堅牢コード品質) | ✅ PASS | ruff, black, mypyチェック必須 |
| C007 (品質例外化禁止) | ✅ PASS | テストタスクをREQUIRED化（tasks.md更新済み） |
| C008 (ドキュメント整合性) | ✅ PASS | 実装前にspec/plan/tasks読み込み、/speckit.clarifyで曖昧性解消 |
| C009 (ブランチ作成必須) | ✅ PASS | feature/001-draft-init-specブランチで作業 |
| C010 (TDD必須) | ✅ PASS | tasks.mdはRed-Green-Refactorサイクルに従う（更新済み） |
| C011 (一次データ推測禁止) | ✅ PASS | doc_init.pyは引数のみ使用、デフォルト値は明示的定義（FR-003b） |
| C012 (DRY原則) | ✅ PASS | 共通ロジックはbase.pyに抽出、パーサー/ジェネレータ/ユーティリティ分離 |
| C013 (破壊的リファクタリング) | N/A | 新規プロジェクト |
| C014 (妥協実装絶対禁止) | ✅ PASS | 暫定版なし、各機能は最初から理想品質で実装 |

### Core Principles Compliance (I-V)

| Principle | Compliance | Notes |
|-----------|-----------|-------|
| I. spec-kit Integration First | ✅ PASS | `specify init --here`パターン、`--force`セマンティクス、`specs/`ディレクトリ構造準拠 |
| II. Non-Interactive Execution | ✅ PASS | スクリプトは`input()`不使用、引数のみで動作（FR-003c） |
| III. Extensibility & Modularity | ✅ PASS | BaseGenerator抽象クラス、独立モジュール設計 |
| IV. Incremental Delivery | ✅ PASS | P1→P2→P3段階的配信、各フェーズ独立テスト可能 |
| V. Testability | ✅ PASS | TDD必須（C010）、90%以上カバレッジ目標、決定的入力/出力 |

**評価**: ✅ **PASS** - すべてのCritical RulesとCore Principlesに準拠

**Re-check Trigger**: Phase 1 design完了後、tasks.md生成後（/speckit.analyzeで検証）

## Project Structure

### Documentation (this feature)

```
specs/001-draft-init-spec/
├── spec.md              # 機能仕様（完成）
├── plan.md              # このファイル（/speckit.plan command output）
├── research.md          # Phase 0 output（これから作成）
├── data-model.md        # Phase 1 output（これから作成）
├── quickstart.md        # Phase 1 output（これから作成）
└── contracts/           # Phase 1 output（これから作成）
```

### Source Code (repository root)

```
src/
└── speckit_docs/
    ├── __init__.py
    ├── cli.py                    # speckit-docs installコマンドエントリーポイント
    ├── commands/                 # コマンドテンプレート（パッケージ内包）
    │   ├── doc-init.md          # /speckit.doc-init コマンド定義
    │   └── doc-update.md        # /speckit.doc-update コマンド定義
    ├── doc_init.py              # ドキュメント初期化スクリプト
    ├── doc_update.py            # ドキュメント更新スクリプト
    ├── generators/              # ドキュメントジェネレータ
    │   ├── __init__.py
    │   ├── base.py             # 抽象ベースクラス
    │   ├── sphinx.py           # Sphinx生成ロジック
    │   └── mkdocs.py           # MkDocs生成ロジック
    ├── parsers/                 # spec-kitファイルパーサー
    │   ├── __init__.py
    │   ├── spec_parser.py      # spec.md パーサー
    │   ├── plan_parser.py      # plan.md パーサー
    │   └── tasks_parser.py     # tasks.md パーサー
    ├── templates/               # Jinja2テンプレート
    │   ├── sphinx/
    │   │   ├── conf.py.j2
    │   │   ├── index.md.j2
    │   │   └── Makefile.j2
    │   └── mkdocs/
    │       ├── mkdocs.yml.j2
    │       └── index.md.j2
    └── utils/                   # ユーティリティ
        ├── __init__.py
        ├── git_utils.py        # Git操作（diff検出）
        ├── file_utils.py       # ファイル操作
        └── prompts.py          # コマンド定義プロンプト生成

tests/
├── unit/
│   ├── test_cli.py
│   ├── test_doc_init.py
│   ├── test_doc_update.py
│   ├── test_parsers.py
│   └── test_generators.py
├── integration/
│   ├── test_install_workflow.py
│   ├── test_sphinx_generation.py
│   └── test_mkdocs_generation.py
└── fixtures/
    └── sample_specs/           # テスト用のサンプルspec-kitプロジェクト

.specify/
└── scripts/
    └── docs/
        ├── doc_init.py         # src/からコピー（インストール時）
        └── doc_update.py       # src/からコピー（インストール時）

.claude/
└── commands/
    ├── speckit.doc-init.md     # src/commands/からコピー（インストール時）
    └── speckit.doc-update.md   # src/commands/からコピー（インストール時）

pyproject.toml                  # パッケージ定義、依存関係
```

**Structure Decision**: 単一Pythonパッケージ構成を選択しました。理由：
1. CLIツールとライブラリを統合した標準的なPythonパッケージ構造
2. `src/speckit_docs/`配下にすべてのコードを集約し、保守性を確保
3. `commands/`と`templates/`をパッケージ内に含めることで、`importlib.resources`でアクセス可能
4. テストはプロダクションコードと分離し、`tests/`配下に配置

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**Constitution Status**: v1.1.0 ratified on 2025-10-13

**Evaluation**: ✅ No complexity violations detected

**Analysis**:
- **C004 (理想実装ファースト)**: 設計は最初から理想的な品質を目指しており、「とりあえず動く」暫定版は含まれていません
- **C010 (TDD必須)**: tasks.mdはRed-Green-Refactorサイクルに従った構造に更新されました（2025-10-13）
- **C011 (一次データ推測禁止)**: doc_init.pyはすべての設定をコマンドライン引数から取得し、デフォルト値は明示的に定義されています（FR-003b）
- **C012 (DRY原則)**: パーサー、ジェネレータ、ユーティリティは明確に分離され、共通ロジックはベースクラス（generators/base.py）に抽出されています
- **C013 (破壊的リファクタリング推奨)**: 新規プロジェクトのため該当なし
- **C014 (妥協実装絶対禁止)**: MVPはP1機能を理想品質で実装し、P2/P3は将来フェーズとして明確に分離されています

**Justifications**: なし（すべての原則に準拠）

---

## Phase 0: Research & Technical Decisions

*Output: research.md*

### Research Topics

以下のトピックについて調査し、`research.md`に記録します：

1. **specify-cliからの機能再利用**
   - StepTracker、consoleの使用方法
   - spec-kitのGit URL依存関係の指定方法（pyproject.toml）

2. **importlib.resourcesの使用パターン**
   - Python 3.11+でのテンプレートファイルアクセス方法
   - パッケージ内リソースの読み取り・コピー

3. **Sphinx + myst-parserの設定**
   - MyST Markdown拡張機能の有効化方法
   - conf.pyでのmyst-parser設定
   - Markdownファイルのビルド設定

4. **MkDocsの設定**
   - mkdocs.ymlの基本構造
   - navセクションの動的生成方法
   - テーマ設定（Material for MkDocsなど）

5. **Git diffを使用したインクリメンタル更新**
   - git diffコマンドでの変更ファイル検出
   - 前回コミットからの差分取得方法

6. **インタラクティブ確認のパターン**
   - spec-kit本家の`specify init --here`実装
   - `--force`フラグの処理方法

### Expected Outcomes

- 各技術の実装パターンと推奨設定が明確化される
- spec-kit本家との一貫性が確保される
- 実装時の落とし穴（pitfalls）が事前に特定される

---

## Phase 1: Design Artifacts

*Output: data-model.md, contracts/, quickstart.md*

### Data Model (data-model.md)

主要なエンティティ：

1. **DocumentationProject**
   - type: "sphinx" | "mkdocs"
   - config: Dict（Sphinx: conf.py設定、MkDocs: mkdocs.yml設定）
   - structure: "flat" | "comprehensive"
   - feature_count: int

2. **Feature**
   - directory: Path
   - name: str（番号なし、例："user-auth"）
   - number: int（例：001）
   - has_spec: bool
   - has_plan: bool
   - has_tasks: bool
   - last_modified: datetime

3. **CommandTemplate**
   - name: str（例："doc-init"、"doc-update"）
   - source_path: Path（パッケージ内）
   - target_path: Path（.claude/commands/）
   - content: str（Jinja2テンプレート）

4. **ScriptFile**
   - name: str（例："doc_init.py"、"doc_update.py"）
   - source_path: Path（src/）
   - target_path: Path（.specify/scripts/docs/）

### API Contracts (contracts/)

このプロジェクトはCLIツールであり、外部APIは提供しません。代わりに、CLIインターフェースを記述します：

```
contracts/
└── cli-interface.md
```

**CLIインターフェース**:

```bash
# インストールコマンド
speckit-docs install [--force]
  --force: 既存ファイルの上書き確認をスキップ
  Exit codes: 0 (成功), 1 (エラー)

# doc_init.py（.specify/scripts/docs/経由で実行）
uv run python .specify/scripts/docs/doc_init.py \
  --type {sphinx|mkdocs} \
  --project-name <name> \
  --author <author> \
  [--version <version>] \
  [--language <lang>] \
  [--site-name <name>] \
  [--repo-url <url>] \
  [--force]
  Exit codes: 0 (成功), 1 (エラー)

# doc_update.py（.specify/scripts/docs/経由で実行）
uv run python .specify/scripts/docs/doc_update.py
  Exit codes: 0 (成功), 1 (エラー)
```

### Quickstart (quickstart.md)

ユーザーが5分以内にspec-kit-docsを導入し、最初のドキュメントを生成できる手順を提供します。

---

## Phase 2: Task Breakdown

*Not generated by /speckit.plan - will be created by /speckit.tasks*

Phase 2の詳細なタスク分解は、`/speckit.tasks`コマンドで生成されます。

---

## Implementation Notes

### Critical Path

1. **Phase 0**: specify-cli依存関係の確認とimportlib.resourcesパターンの調査
2. **Phase 1**: CLIエントリーポイントとコマンドテンプレートの実装
3. **Phase 1**: Sphinx/MkDocsジェネレータの実装
4. **Phase 1**: インストールワークフローのテスト

### Risk Mitigation

- **specify-cli依存関係**: Git URL直接指定で問題ないことを確認済み
- **既存ファイル処理**: spec-kit本家パターンを踏襲し、一貫性を確保
- **エラーハンドリング（C002準拠）**: ベストエフォート方式で部分的な状態を許容し、以下の基準に従う：
  - **継続可能なエラー**（処理継続）: 不正なmarkdown（FR-035）、欠落ファイル（plan.md/tasks.md不在、FR-018）、個別機能の解析失敗 → ログに警告を出力し、他の機能の処理を継続
  - **致命的エラー**（即座に中断）: .specify/ディレクトリ不在（FR-001）、docs/初期化失敗（FR-003d）、Gitリポジトリ不在（FR-012準拠）、テンプレートファイル破損 → SpecKitDocsErrorを発生させ、明確なエラーメッセージと復旧手順をstderrに出力
  - **ロールバック不要**（ベストエフォート）: ファイル作成中のエラーは部分的な状態を残し、ユーザーが手動で修正または再実行可能（FR-023c）
  - **ログファイル優先**（C002原則）: すべてのエラー詳細はstderrに出力され、AIエージェントがユーザーに提示

### Technology Choices Rationale

- **Python 3.11+**: spec-kitとの互換性
- **specify-cli依存**: StepTracker、consoleを再利用しコード重複を削減
- **importlib.resources**: Python標準ライブラリで、パッケージ内リソースへの安全なアクセス
- **Jinja2**: テンプレートエンジンの業界標準、Sphinx/MkDocsとの親和性
- **pytest**: Python標準のテストフレームワーク

---

**Plan Status**: Phase 0準備完了。次のステップ：`research.md`の作成を開始します。
