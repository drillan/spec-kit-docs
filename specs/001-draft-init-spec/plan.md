# Implementation Plan: spec-kit-docs - 依存関係配置先選択機能の追加

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md` (Session 2025-10-16 clarifications)

**Note**: This plan focuses on FR-008f (dependency placement strategy) added in Session 2025-10-16.

## Summary

Session 2025-10-16の`/speckit.clarify`で明確化されたFR-008f（依存関係配置先選択機能）を実装します。この機能により、`/doc-init`コマンド実行時にユーザーがドキュメント依存関係の配置先を選択できるようになります：

1. **`[project.optional-dependencies.docs]`** (推奨) - pip/poetry/uv互換、PEP 621標準
2. **`[dependency-groups.docs]`** - uvネイティブ、PEP 735準拠

この選択により、ドキュメント生成ツール（Sphinx/MkDocs）がメインアプリケーションの依存関係（`[project.dependencies]`）から分離され、アーキテクチャ的に正しい構造が実現されます。

## Technical Context

**Language/Version**: Python 3.11+（spec-kit前提条件との互換性）

**Primary Dependencies**:
- **CLIフレームワーク**: typer 0.12+（本家spec-kitとの一貫性）
- **ドキュメントツール**: Sphinx 7.0+ with myst-parser 2.0+、MkDocs 1.5+ with mkdocs-material 9.0+
- **パッケージリソース管理**: importlib.resources（Python 3.9+標準ライブラリ）
- **Git操作**: GitPython 3.1+（変更検出とブランチ情報取得）
- **テンプレートエンジン**: Jinja2 3.1+（設定ファイル生成）
- **Markdown解析**: markdown-it-py 3.0+（spec.md等の解析、MyST互換性）
- **spec-kit依存**: specify-cli @ git+https://github.com/github/spec-kit.git（typer依存ツリーを含む）
- **YAML処理**: ruamel.yaml 0.18+（mkdocs.yml解析・生成）

**Storage**: N/A（ファイルシステムのみ使用）

**Testing**: pytest 8.0+、pytest-cov 4.0+（単体テスト・統合テスト）、pyfakefs 5.0+（ファイルシステムモック）

**Target Platform**: Linux/macOS/WSL2（spec-kitと同じプラットフォーム要件）

**Project Type**: Single（CLIツールとライブラリのハイブリッド）

**Performance Goals**:
- `/speckit.doc-init`: 30秒以内にドキュメントプロジェクト初期化（対話時間除く）
- 依存関係配置先選択: 1秒以内に選択プロンプト表示

**Constraints**:
- 非対話的実行必須（CI/CD対応のため`input()`禁止）
- spec-kit Integration First（Core Principle I準拠）
- オフライン動作（importlib.resources使用）

**Scale/Scope**:
- MVP範囲: 依存関係配置先選択機能の追加
- 2つの配置先選択肢（optional-dependencies、dependency-groups）
- 既存の自動インストール機能との統合

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. spec-kit Integration First**:
- typerフレームワーク使用（本家spec-kitと一貫）
- `typer.Option()`で配置先選択フラグを追加（本家パターン再利用）
- AIエージェントが対話的に選択を収集し、スクリプトは引数のみを受け取る（spec-kit標準パターン）
- 判定: **準拠** - spec-kitの標準パターンを完全に踏襲

✅ **II. Non-Interactive Execution**:
- doc_init.pyは`input()`使用禁止
- 配置先選択は`--dependency-target`引数で受け取る
- デフォルト値は`optional-dependencies`（引数省略時）
- 判定: **準拠** - 非対話的実行を保証

✅ **III. Extensibility & Modularity**:
- 配置先選択機能は`handle_dependencies()`関数に統合
- 新しい配置先（例：conda環境）追加が容易
- 判定: **準拠** - モジュラー設計

✅ **IV. Incremental Delivery**:
- MVP範囲: 配置先選択機能のみ追加
- 既存の依存関係自動インストール機能を破壊しない
- 判定: **準拠** - MVP優先アプローチ

✅ **V. Testability**:
- TDD必須: テストファースト実装
- `handle_dependencies(dependency_target="optional-dependencies")`のようにテスト可能
- pyfakefsでファイルシステムモック
- 判定: **準拠** - テスト容易な設計

### Critical Rules Compliance

✅ **C001 (ルール歪曲禁止)**: すべてのルールを逐語的に遵守
✅ **C002 (エラー迂回絶対禁止)**: 不正な`--dependency-target`値はエラー、継続不可
✅ **C004 (理想実装ファースト)**: 段階的改善ではなく、最初から理想的な配置先選択実装
✅ **C006 (堅牢コード品質)**: ruff/mypy/pytest必須
✅ **C008 (ドキュメント整合性)**: FR-008f完全準拠
✅ **C010 (TDD必須)**: Red-Green-Refactorサイクル
✅ **C011 (Data Accuracy)**: `--dependency-target`値の明示的検証、デフォルト値明記
✅ **C012 (DRY原則)**: typer.Option()再利用、重複実装なし
✅ **C014 (No-Compromise Implementation)**: 妥協なし、理想実装のみ

### Gates Status

🟢 **All Gates Passed** - Phase 0 research開始可能

## Project Structure

### Documentation (this feature)

```
specs/001-draft-init-spec/
├── spec.md              # Feature specification (updated in Session 2025-10-16)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - Technical research (to be created)
├── data-model.md        # Phase 1 output - Entity definitions (to be created)
├── contracts/           # Phase 1 output - API contracts (to be created)
│   └── handle_dependencies.md  # handle_dependencies() function contract update
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

```
spec-kit-docs/                  # プロジェクトルート
├── src/
│   └── speckit_docs/           # メインパッケージ
│       ├── cli/                # CLIエントリポイント
│       │   ├── __init__.py     # typer app定義
│       │   └── install_handler.py  # installコマンド実装
│       ├── commands/           # コマンドテンプレート（importlib.resources）
│       │   ├── speckit.doc-init.md  # AIエージェントプロンプト（配置先選択追加予定）
│       │   └── speckit.doc-update.md
│       ├── scripts/            # バックエンドスクリプト
│       │   ├── doc_init.py     # 依存関係配置先選択機能を追加（Session 2025-10-16）
│       │   └── doc_update.py
│       ├── generators/         # ドキュメントジェネレータ
│       │   ├── base.py         # BaseGenerator抽象クラス
│       │   ├── sphinx.py       # SphinxGenerator
│       │   └── mkdocs.py       # MkDocsGenerator
│       ├── parsers/            # spec-kit仕様解析
│       │   ├── spec_parser.py
│       │   ├── plan_parser.py
│       │   └── tasks_parser.py
│       ├── utils/              # ユーティリティ
│       │   ├── git.py
│       │   ├── fs.py
│       │   ├── template.py
│       │   └── dependencies.py # 依存関係管理（handle_dependencies関数を更新）
│       │       ├── handle_dependencies(dependency_target: str)  # 引数追加
│       │       ├── detect_package_managers()
│       │       ├── show_alternative_methods()
│       │       └── get_required_packages()
│       └── exceptions.py       # SpecKitDocsError例外定義
├── tests/
│   ├── contract/               # 契約テスト（CLIインターフェース）
│   ├── integration/            # 統合テスト（実際のspec-kitプロジェクト使用）
│   │   ├── test_doc_init_optional_dependencies.py  # 新規: optional-dependenciesテスト
│   │   └── test_doc_init_dependency_groups.py      # 新規: dependency-groupsテスト
│   └── unit/                   # 単体テスト
│       └── utils/
│           └── test_handle_dependencies.py  # 既存テストを更新
├── pyproject.toml              # プロジェクト設定
├── .specify/                   # spec-kitメタデータ
└── specs/                      # 機能仕様
    └── 001-draft-init-spec/    # この機能の仕様
```

**Structure Decision**: Single project構造を採用。speckit-docsは独立したCLIツールであり、frontend/backend分離は不要。既存の構造を維持し、`utils/dependencies.py`の`handle_dependencies()`関数と`.claude/commands/speckit.doc-init.md`のみを更新します。

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

該当なし - すべてのConstitution原則に準拠

## Phase 0: Research (NEEDS EXECUTION)

### Research Questions

以下の技術的不明点をresearch.mdで解決します：

1. **`uv add --optional` vs `uv add --group`の動作確認**:
   - 実際のコマンド動作とpyproject.toml変更の違いを確認
   - 両方のコマンドが成功するか検証
   - エラーケース（存在しないグループ名等）の調査

2. **pip/poetryとの互換性確認**:
   - `[project.optional-dependencies.docs]`がpip/poetryで正しく動作するか
   - `[dependency-groups.docs]`がpip/poetryで無視されるか（エラーにならないか）

3. **デフォルト値の妥当性**:
   - `optional-dependencies`をデフォルトとする根拠
   - spec-kitユーザーの95%がuv使用という仮定の検証

4. **既存実装への影響範囲**:
   - `handle_dependencies()`関数のシグネチャ変更がテストに与える影響
   - `.claude/commands/speckit.doc-init.md`の変更範囲

**Output**: research.md

## Phase 1: Design & Contracts (NEEDS EXECUTION)

### Data Model Updates

`data-model.md`に以下のエンティティを追加：

```python
@dataclass(frozen=True)
class DependencyTarget:
    """Represents where dependencies should be added in pyproject.toml.

    Attributes:
        target_type: "optional-dependencies" or "dependency-groups"
        uv_flag: "--optional" or "--group"
        section_path: Path in pyproject.toml (e.g., "[project.optional-dependencies.docs]")
    """
    target_type: Literal["optional-dependencies", "dependency-groups"]
    uv_flag: str
    section_path: str

    def __post_init__(self) -> None:
        """Validate DependencyTarget constraints."""
        if self.target_type not in ["optional-dependencies", "dependency-groups"]:
            raise ValueError(f"Invalid target_type: {self.target_type}")

        if self.target_type == "optional-dependencies" and self.uv_flag != "--optional":
            raise ValueError("optional-dependencies requires --optional flag")

        if self.target_type == "dependency-groups" and self.uv_flag != "--group":
            raise ValueError("dependency-groups requires --group flag")
```

### API Contracts

`contracts/handle_dependencies.md`を更新：

**Signature**:
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

**Contract**:
- **Preconditions**:
  - `doc_type` must be "sphinx" or "mkdocs"
  - `dependency_target` must be "optional-dependencies" or "dependency-groups"
  - `project_root` must be a valid directory
- **Postconditions**:
  - If `dependency_target == "optional-dependencies"`: `uv add --optional docs {packages}` executed
  - If `dependency_target == "dependency-groups"`: `uv add --group docs {packages}` executed
  - Returns `DependencyResult` with appropriate status
- **Error Handling**:
  - Raises `ValueError` if `dependency_target` is invalid
  - Returns `DependencyResult(status="failed")` if `uv add` fails

**Output**: contracts/handle_dependencies.md

### Quickstart Example

`quickstart.md`に以下のユーザーフローを追加：

```markdown
## 依存関係配置先の選択

`/doc-init`実行時、依存関係の配置先を選択できます：

### Option 1: optional-dependencies (推奨)
- pip/poetry/uv互換
- `uv sync --all-extras`でインストール

### Option 2: dependency-groups
- uvネイティブ、モダン
- `uv sync --group docs`でインストール

選択はAIエージェントが対話的に尋ねます。
```

**Output**: quickstart.md

## Phase 2: Implementation (NOT EXECUTED BY /speckit.plan)

フェーズ2は`/speckit.tasks`コマンドでtasks.mdを生成し、`/speckit.implement`で実装します。

### Expected Tasks (Preview)

1. **T001**: `utils/dependencies.py`の`handle_dependencies()`に`dependency_target`引数を追加
2. **T002**: `DependencyTarget`データクラスを`utils/dependencies.py`に追加
3. **T003**: `.claude/commands/speckit.doc-init.md`に依存関係配置先選択プロンプトを追加
4. **T004**: `scripts/doc_init.py`に`--dependency-target`引数を追加
5. **T005**: 単体テスト（`test_handle_dependencies.py`）を更新
6. **T006**: 統合テスト（`test_doc_init_optional_dependencies.py`、`test_doc_init_dependency_groups.py`）を追加
7. **T007**: ドキュメント（README.md、spec.md）を更新

---

**Next Command**: `/speckit.tasks` (after Phase 0 and Phase 1 completion)
