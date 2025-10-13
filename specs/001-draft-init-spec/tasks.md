# Implementation Tasks: spec-kit-docs - AI駆動型ドキュメント生成システム

**Feature**: spec-kit-docs
**Branch**: 001-draft-init-spec
**Date**: 2025-10-13
**Status**: Ready for Implementation
**Input**: [spec.md](spec.md) | [plan.md](plan.md) | [data-model.md](data-model.md) | [contracts/cli-interface.md](contracts/cli-interface.md)

**Note**: このタスクリストは `/speckit.tasks` コマンドで生成されました。タスクはユーザーストーリー単位で構成され、各ストーリーは独立してテスト可能です。

---

## Implementation Strategy

### MVP Scope (Phase 1)
このタスクリストは **MVP（P1ユーザーストーリー3つ）** のみをカバーします：
- **US1**: ドキュメントプロジェクトの初期化 (Sphinx/MkDocs)
- **US2**: spec-kit仕様からのドキュメント更新
- **US3**: spec-kit拡張機能としてのインストール

### Incremental Delivery
各ユーザーストーリーは独立した配信単位として実装されます：
- **Checkpoint 1**: US3完了時 → CLIツールのインストールが可能
- **Checkpoint 2**: US1完了時 → ドキュメントプロジェクトの初期化が可能
- **Checkpoint 3**: US2完了時 → MVP完成、基本的なドキュメント生成が可能

### TDD Approach (C010: Required)
すべてのタスクは **Red-Green-Refactor** サイクルに従います：
1. **Red**: テストを書き、失敗することを確認
2. **Green**: テストを通過する最小限の実装
3. **Refactor**: コードを改善し、テストが通過し続けることを確認

---

## Phase 1: Setup & Project Initialization

**Goal**: Python環境、依存関係、プロジェクト構造をセットアップする。

### T001: pyproject.tomlの作成とプロジェクトメタデータ定義 [X]
**File**: `pyproject.toml`
**Type**: Setup
**Story**: Setup
**Priority**: Blocking

**Description**:
プロジェクトメタデータ、依存関係、開発ツール設定を定義する。

**Steps**:
1. `pyproject.toml`を作成
2. プロジェクト名、バージョン、説明、ライセンスを設定
3. Python 3.11+要件を設定
4. 依存関係を定義：
   - **typer** (Session 2025-10-13決定): CLIフレームワーク
   - **Sphinx 7.0+**: Sphinxドキュメント生成
   - **myst-parser 2.0+**: Markdown解析
   - **MkDocs 1.5+**: MkDocsドキュメント生成
   - **markdown-it-py 3.0+**: Markdown解析
   - **Jinja2 3.1+**: テンプレート
   - **GitPython 3.1+**: Git操作
   - **rich**: CLI UI（typer経由で使用）
5. 開発依存関係を定義：pytest, pytest-cov, ruff, black, mypy
6. `[project.scripts]`セクションを定義：
   ```toml
   [project.scripts]
   speckit-docs = "speckit_docs.cli:app"
   ```

**Acceptance Criteria**:
- `pyproject.toml`が存在し、有効なTOML構文である
- `uv pip install -e .`が成功する
- `speckit-docs --help`が実行可能（typer CLIとして動作）

**Estimated Time**: 30分

---

### T002: ディレクトリ構造の作成 [X]
**File**: `src/speckit_docs/`, `tests/`
**Type**: Setup
**Story**: Setup
**Priority**: Blocking

**Description**:
プロジェクトディレクトリ構造を作成し、`__init__.py`を配置する。

**Steps**:
1. 以下のディレクトリを作成：
   ```
   src/speckit_docs/
   ├── __init__.py (バージョン情報)
   ├── cli/
   │   └── __init__.py
   ├── commands/ (テンプレートファイル格納)
   │   └── __init__.py
   ├── scripts/ (バックエンドスクリプト)
   │   └── __init__.py
   ├── generators/
   │   └── __init__.py
   ├── parsers/
   │   └── __init__.py
   ├── utils/
   │   └── __init__.py
   └── exceptions.py

   tests/
   ├── __init__.py
   ├── unit/
   │   └── __init__.py
   ├── integration/
   │   └── __init__.py
   └── contract/
       └── __init__.py
   ```
2. `src/speckit_docs/__init__.py`にバージョン情報を定義：
   ```python
   __version__ = "0.1.0"
   ```

**Acceptance Criteria**:
- すべてのディレクトリが存在し、`__init__.py`が配置されている
- `import speckit_docs`が成功する
- `speckit_docs.__version__`が"0.1.0"を返す

**Estimated Time**: 15分

---

### T003: SpecKitDocsError例外クラスの実装 [X]
**File**: `src/speckit_docs/exceptions.py`
**Type**: Setup
**Story**: Setup
**Priority**: Blocking

**Test File**: `tests/unit/test_exceptions.py`
**TDD**: ✅ Required (C010)

**Description**:
明確なエラーメッセージと提案を提供するカスタム例外クラスを実装する（research.md Decision 8）。

**Steps (Red-Green-Refactor)**:
1. **RED**: `tests/unit/test_exceptions.py`を作成し、テストを書く：
   ```python
   def test_speckit_docs_error_message():
       error = SpecKitDocsError("Test error", "Test suggestion")
       assert error.message == "Test error"
       assert error.suggestion == "Test suggestion"
       assert "Test error" in str(error)
       assert "Test suggestion" in str(error)
   ```
2. テストを実行し、失敗することを確認
3. **GREEN**: `exceptions.py`に最小限の実装：
   ```python
   class SpecKitDocsError(Exception):
       def __init__(self, message: str, suggestion: str):
           self.message = message
           self.suggestion = suggestion
           super().__init__(f"{message}\n\n💡 Suggestion: {suggestion}")
   ```
4. テストを実行し、成功することを確認
5. **REFACTOR**: 必要に応じてリファクタリング

**Acceptance Criteria**:
- テストが通過する
- `SpecKitDocsError`が`message`と`suggestion`属性を持つ
- `str(error)`がメッセージと提案を含む

**Estimated Time**: 20分

---

## Phase 2: Foundational Layer (Blocking Prerequisites)

**Goal**: すべてのユーザーストーリーが依存する基盤機能を実装する。

### T004: Enumerationsの実装 [X]
**File**: `src/speckit_docs/models.py`
**Type**: Foundational
**Story**: Foundational
**Priority**: Blocking

**Test File**: `tests/unit/test_models.py`
**TDD**: ✅ Required (C010)

**Description**:
data-model.mdで定義された列挙型を実装する。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_feature_status_enum():
       assert FeatureStatus.DRAFT.value == "draft"
       assert FeatureStatus.PLANNED.value == "planned"

   def test_generator_tool_enum():
       assert GeneratorTool.SPHINX.value == "sphinx"
       assert GeneratorTool.MKDOCS.value == "mkdocs"
   ```
2. **GREEN**: `models.py`に実装：
   ```python
   from enum import Enum

   class FeatureStatus(Enum):
       DRAFT = "draft"
       PLANNED = "planned"
       IN_PROGRESS = "in_progress"
       COMPLETED = "completed"

   class DocumentType(Enum):
       SPEC = "spec"
       PLAN = "plan"
       TASKS = "tasks"

   class GitStatus(Enum):
       UNTRACKED = "untracked"
       MODIFIED = "modified"
       STAGED = "staged"
       COMMITTED = "committed"

   class StructureType(Enum):
       FLAT = "flat"
       COMPREHENSIVE = "comprehensive"

   class GeneratorTool(Enum):
       SPHINX = "sphinx"
       MKDOCS = "mkdocs"
   ```
3. **REFACTOR**: 必要に応じて改善

**Acceptance Criteria**:
- すべてのテストが通過する
- 各Enumが適切な値を持つ
- mypy型チェックが通過する

**Estimated Time**: 30分

---

### T005: [P] Feature, Document, Sectionエンティティの実装 [X]
**File**: `src/speckit_docs/models.py`
**Type**: Foundational
**Story**: Foundational
**Priority**: Blocking
**Parallelizable**: Yes (T004と並行可能)

**Test File**: `tests/unit/test_models.py`
**TDD**: ✅ Required (C010)

**Description**:
data-model.mdで定義されたコアエンティティをPythonデータクラスとして実装する。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_feature_creation():
       feature = Feature(
           id="001",
           name="test-feature",
           directory_path=Path("/path/to/specs/001-test-feature"),
           spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
           status=FeatureStatus.DRAFT
       )
       assert feature.id == "001"
       assert feature.name == "test-feature"

   def test_document_creation():
       doc = Document(
           file_path=Path("/path/to/spec.md"),
           type=DocumentType.SPEC,
           content="# Test"
       )
       assert doc.type == DocumentType.SPEC
   ```
2. **GREEN**: データクラスを実装：
   ```python
   from dataclasses import dataclass, field
   from pathlib import Path
   from typing import List, Optional
   from datetime import datetime

   @dataclass(frozen=True)
   class Feature:
       id: str
       name: str
       directory_path: Path
       spec_file: Path
       status: FeatureStatus
       plan_file: Optional[Path] = None
       tasks_file: Optional[Path] = None
       priority: Optional[str] = None
       metadata: dict = field(default_factory=dict)

   @dataclass
   class Section:
       title: str
       level: int
       content: str
       line_start: int
       line_end: int
       subsections: List['Section'] = field(default_factory=list)

   @dataclass
   class Document:
       file_path: Path
       type: DocumentType
       content: str
       sections: List[Section] = field(default_factory=list)
       last_modified: Optional[datetime] = None
       git_status: GitStatus = GitStatus.UNTRACKED
   ```
3. **REFACTOR**: 必要に応じて改善

**Acceptance Criteria**:
- すべてのテストが通過する
- データクラスが不変（frozen=True）または適切に設計されている
- mypy型チェックが通過する

**Estimated Time**: 45分

---

### T006: MarkdownParserの実装 [X]
**File**: `src/speckit_docs/parsers/markdown_parser.py`
**Type**: Foundational
**Story**: Foundational
**Priority**: Blocking

**Test File**: `tests/unit/parsers/test_markdown_parser.py`
**TDD**: ✅ Required (C010)

**Description**:
markdown-it-pyを使用してMarkdownを解析し、Sectionツリーを生成する（research.md Decision 5）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_parse_simple_markdown():
       parser = MarkdownParser()
       content = "# Title\n\nParagraph\n\n## Subtitle\n\nMore text"
       sections = parser.parse(content)
       assert len(sections) == 1
       assert sections[0].title == "Title"
       assert sections[0].level == 1
       assert len(sections[0].subsections) == 1

   def test_extract_headings():
       parser = MarkdownParser()
       content = "# H1\n## H2\n### H3"
       headings = parser.extract_headings(content)
       assert len(headings) == 3
   ```
2. **GREEN**: 実装：
   ```python
   from markdown_it import MarkdownIt
   from typing import List
   from ..models import Section

   class MarkdownParser:
       def __init__(self, enable_myst: bool = True):
           self.markdown_it = MarkdownIt()
           self.enable_myst = enable_myst

       def parse(self, content: str) -> List[Section]:
           # markdown-it-pyを使用してトークン解析
           tokens = self.markdown_it.parse(content)
           sections = self._build_section_tree(tokens)
           return sections

       def extract_headings(self, content: str) -> List[dict]:
           tokens = self.markdown_it.parse(content)
           headings = [
               {"level": t.tag[1:], "text": t.content}
               for t in tokens if t.type == "heading_open"
           ]
           return headings

       def _build_section_tree(self, tokens) -> List[Section]:
           # トークンからセクションツリーを構築
           # 実装詳細は省略
           pass
   ```
3. **REFACTOR**: `_build_section_tree`の実装を改善

**Acceptance Criteria**:
- テストが通過する
- 見出しレベル1-6を正しく解析できる
- ネストされたセクションを再帰的に処理できる

**Estimated Time**: 1.5時間

---

### T007: GitRepository & ChangeDetectorの実装 [X]
**File**: `src/speckit_docs/utils/git.py`
**Type**: Foundational
**Story**: Foundational
**Priority**: Blocking

**Test File**: `tests/unit/utils/test_git.py`
**TDD**: ✅ Required (C010)

**Description**:
GitPythonを使用してGit diffで変更検出を実装する（research.md Decision 2, 13）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く（pytestのtmpdir fixture使用）：
   ```python
   def test_get_changed_files(tmp_path, git_repo):
       # git_repoはフィクスチャで初期化済みGitリポジトリ
       detector = ChangeDetector(tmp_path)
       changed_files = detector.get_changed_files("HEAD~1", "HEAD")
       assert isinstance(changed_files, list)

   def test_get_changed_features(tmp_path, spec_kit_project):
       detector = ChangeDetector(tmp_path)
       features = detector.get_changed_features()
       assert all(isinstance(f, Feature) for f in features)
   ```
2. **GREEN**: 実装：
   ```python
   from git import Repo
   from pathlib import Path
   from typing import List
   from ..models import Feature
   from ..exceptions import SpecKitDocsError

   class ChangeDetector:
       def __init__(self, repo_path: Path = Path(".")):
           try:
               self.repo = Repo(repo_path)
           except Exception as e:
               raise SpecKitDocsError(
                   "Gitリポジトリではありません",
                   "git init でリポジトリを初期化してください"
               )

       def get_changed_files(self, base_ref: str = "HEAD~1", target_ref: str = "HEAD") -> List[Path]:
           try:
               diff_index = self.repo.commit(base_ref).diff(target_ref)
               changed_files = [
                   Path(item.b_path or item.a_path)
                   for item in diff_index
               ]
               return changed_files
           except Exception as e:
               raise SpecKitDocsError(
                   f"Git diff取得に失敗: {e}",
                   "git log で履歴を確認してください"
               )

       def get_changed_features(self, base_ref: str = "HEAD~1") -> List[Feature]:
           changed_files = self.get_changed_files(base_ref, "HEAD")
           specs_dir = Path(self.repo.working_dir) / "specs"

           # specs/ディレクトリ内の変更のみフィルタ
           spec_files = [f for f in changed_files if str(f).startswith("specs/") and f.name == "spec.md"]

           # Featureオブジェクトを構築（詳細は省略）
           features = []
           for spec_file in spec_files:
               # Feature構築ロジック
               pass
           return features
   ```
3. **REFACTOR**: エラーハンドリングと初回コミットケースの対応

**Acceptance Criteria**:
- テストが通過する
- Git diffで変更ファイルを正しく検出できる
- `specs/`配下の変更のみをフィルタできる
- 初回コミット（HEAD~1が存在しない）でもエラーにならない

**Estimated Time**: 1.5時間

---

## Phase 3: User Story 3 - spec-kit拡張機能としてのインストール

**Goal**: CLIツールのインストール機能を実装し、`.claude/commands/`と`.specify/scripts/docs/`にファイルをコピーする。

**Story Dependencies**: None (独立して実装可能)
**Independent Test**: 既存spec-kitプロジェクトで`speckit-docs install`を実行し、コマンド定義とスクリプトがコピーされることを確認

### T008: typer CLIアプリケーションの実装
**File**: `src/speckit_docs/cli/__init__.py`
**Type**: US3 - Implementation
**Story**: US3 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/cli/test_cli.py`
**TDD**: ✅ Required (C010)

**Description**:
typer CLIフレームワークを使用してメインアプリケーションとinstallコマンドを実装する（Session 2025-10-13決定、research.md Section 7更新版）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く（typer.testing.CliRunner使用）：
   ```python
   from typer.testing import CliRunner
   from speckit_docs.cli import app

   runner = CliRunner()

   def test_app_help():
       result = runner.invoke(app, ["--help"])
       assert result.exit_code == 0
       assert "speckit-docs" in result.stdout

   def test_install_command_exists():
       result = runner.invoke(app, ["install", "--help"])
       assert result.exit_code == 0
   ```
2. **GREEN**: 実装：
   ```python
   import typer
   from pathlib import Path
   from rich.console import Console

   app = typer.Typer(name="speckit-docs", help="spec-kit documentation generator")
   console = Console()

   @app.command()
   def install(
       force: bool = typer.Option(
           False,
           "--force",
           help="Skip confirmation and overwrite existing files"
       ),
   ):
       """
       Install spec-kit-docs commands into the current project.

       This command copies command definitions (.claude/commands/) and
       backend scripts (.specify/scripts/docs/) to the current project.
       """
       from .install_handler import install_handler
       install_handler(force=force)

   if __name__ == "__main__":
       app()
   ```
3. **REFACTOR**: エラーハンドリングとヘルプメッセージを改善

**Acceptance Criteria**:
- テストが通過する
- `speckit-docs --help`が動作する
- `speckit-docs install --help`が動作する
- typer CLIとして正しく機能する

**Estimated Time**: 1時間

---

### T009: install_handlerの実装（spec-kitプロジェクト検証）
**File**: `src/speckit_docs/cli/install_handler.py`
**Type**: US3 - Implementation
**Story**: US3 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/cli/test_install_handler.py`
**TDD**: ✅ Required (C010)

**Description**:
spec-kitプロジェクト検証ロジックを実装する（FR-021a）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_validate_speckit_project_success(tmp_path):
       # .specify/ と .claude/ を作成
       (tmp_path / ".specify").mkdir()
       (tmp_path / ".claude").mkdir()

       assert validate_speckit_project(tmp_path) == True

   def test_validate_speckit_project_missing_specify(tmp_path):
       with pytest.raises(SpecKitDocsError) as exc_info:
           validate_speckit_project(tmp_path)
       assert "spec-kitプロジェクトではありません" in str(exc_info.value)
   ```
2. **GREEN**: 実装：
   ```python
   from pathlib import Path
   from ..exceptions import SpecKitDocsError

   def validate_speckit_project(project_dir: Path = Path(".")) -> bool:
       specify_dir = project_dir / ".specify"
       claude_dir = project_dir / ".claude"

       if not specify_dir.exists():
           raise SpecKitDocsError(
               "spec-kitプロジェクトではありません",
               "最初に 'specify init' を実行してください"
           )

       if not claude_dir.exists():
           raise SpecKitDocsError(
               ".claude/ディレクトリが見つかりません",
               "spec-kitプロジェクトを正しく初期化してください"
           )

       return True

   def install_handler(force: bool = False):
       # プロジェクト検証
       validate_speckit_project()

       # 以降の処理（T010で実装）
       pass
   ```
3. **REFACTOR**: エラーメッセージを改善

**Acceptance Criteria**:
- テストが通過する
- `.specify/`がない場合、適切なエラーメッセージを表示
- `.claude/`がない場合、適切なエラーメッセージを表示

**Estimated Time**: 45分

---

### T010: [P] コマンドテンプレートファイルのコピー実装
**File**: `src/speckit_docs/cli/install_handler.py`
**Type**: US3 - Implementation
**Story**: US3 (P1 MVP)
**Priority**: High
**Parallelizable**: Yes (T011と並行可能)

**Test File**: `tests/unit/cli/test_install_handler.py`
**TDD**: ✅ Required (C010)

**Description**:
`src/speckit_docs/commands/`からコマンド定義ファイルをコピーする（FR-022, FR-023a）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_copy_command_templates(tmp_path):
       # spec-kitプロジェクト構造を作成
       (tmp_path / ".specify").mkdir()
       (tmp_path / ".claude/commands").mkdir(parents=True)

       copy_command_templates(tmp_path, force=False)

       assert (tmp_path / ".claude/commands/doc-init.md").exists()
       assert (tmp_path / ".claude/commands/doc-update.md").exists()

   def test_copy_command_templates_existing_confirm(tmp_path, monkeypatch):
       # 既存ファイルがある場合の確認テスト
       (tmp_path / ".claude/commands").mkdir(parents=True)
       (tmp_path / ".claude/commands/doc-init.md").write_text("existing")

       # typer.confirm()のモック
       monkeypatch.setattr("typer.confirm", lambda msg: False)

       copy_command_templates(tmp_path, force=False)

       # 拒否された場合、既存ファイルは保持
       assert (tmp_path / ".claude/commands/doc-init.md").read_text() == "existing"
   ```
2. **GREEN**: 実装：
   ```python
   import importlib.resources
   import shutil
   import typer
   from pathlib import Path

   def copy_command_templates(project_dir: Path, force: bool = False) -> None:
       commands_dir = project_dir / ".claude" / "commands"
       commands_dir.mkdir(parents=True, exist_ok=True)

       # importlib.resourcesでパッケージ内テンプレートにアクセス
       templates = importlib.resources.files("speckit_docs.commands")

       for template_name in ["doc-init.md", "doc-update.md"]:
           source = templates / template_name
           dest = commands_dir / template_name

           if dest.exists() and not force:
               console.print(f"[yellow]Warning:[/yellow] {dest.name} already exists")
               response = typer.confirm("Do you want to overwrite?")
               if not response:
                   console.print(f"[yellow]Skipped:[/yellow] {dest.name}")
                   continue

           with importlib.resources.as_file(source) as template_path:
               shutil.copy(template_path, dest)
               console.print(f"[green]✓[/green] Copied {dest.name}")
   ```
3. **REFACTOR**: エラーハンドリング改善

**Acceptance Criteria**:
- テストが通過する
- `doc-init.md`と`doc-update.md`が正しくコピーされる
- 既存ファイルがある場合、確認プロンプトが表示される
- `--force`フラグで確認をスキップできる

**Estimated Time**: 1.5時間

---

### T011: [P] バックエンドスクリプトのコピー実装
**File**: `src/speckit_docs/cli/install_handler.py`
**Type**: US3 - Implementation
**Story**: US3 (P1 MVP)
**Priority**: High
**Parallelizable**: Yes (T010と並行可能)

**Test File**: `tests/unit/cli/test_install_handler.py`
**TDD**: ✅ Required (C010)

**Description**:
`src/speckit_docs/scripts/`からバックエンドスクリプトをコピーする（FR-023）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_copy_backend_scripts(tmp_path):
       (tmp_path / ".specify/scripts/docs").mkdir(parents=True)

       copy_backend_scripts(tmp_path, force=False)

       assert (tmp_path / ".specify/scripts/docs/doc_init.py").exists()
       assert (tmp_path / ".specify/scripts/docs/doc_update.py").exists()
   ```
2. **GREEN**: 実装（T010と同様のパターン）：
   ```python
   def copy_backend_scripts(project_dir: Path, force: bool = False) -> None:
       scripts_dir = project_dir / ".specify" / "scripts" / "docs"
       scripts_dir.mkdir(parents=True, exist_ok=True)

       scripts = importlib.resources.files("speckit_docs.scripts")

       for script_name in ["doc_init.py", "doc_update.py"]:
           source = scripts / script_name
           dest = scripts_dir / script_name

           # コピーロジック（T010と同様）
           if dest.exists() and not force:
               # 確認プロンプト
               pass

           with importlib.resources.as_file(source) as script_path:
               shutil.copy(script_path, dest)
               console.print(f"[green]✓[/green] Copied {dest.name}")
   ```
3. **REFACTOR**: T010とコードの重複を排除（DRY原則 C012）

**Acceptance Criteria**:
- テストが通過する
- `doc_init.py`と`doc_update.py`が正しくコピーされる
- T010と同様の確認ロジックが動作する

**Estimated Time**: 1時間

---

### T012: コマンドテンプレートファイルの作成
**File**: `src/speckit_docs/commands/doc-init.md`, `doc-update.md`
**Type**: US3 - Assets
**Story**: US3 (P1 MVP)
**Priority**: High

**Description**:
Claude Codeが解釈するコマンド定義Markdownファイルを作成する（FR-022a, FR-022b）。**C003（冒頭表示必須）に準拠し、コマンド実行時にCRITICAL原則を表示する**。

**Steps**:
1. `src/speckit_docs/commands/doc-init.md`を作成：
   ```markdown
   # /doc-init - Initialize Documentation Project

   [Active Rules: C001-C014]
   **CRITICAL原則**: ルール歪曲禁止・エラー迂回禁止・理想実装ファースト・記録管理・品質基準遵守・ドキュメント整合性・TDD必須・DRY原則・破壊的リファクタリング推奨・妥協実装絶対禁止

   Execute the following command to initialize a Sphinx or MkDocs documentation project:

   ```bash
   uv run python .specify/scripts/docs/doc_init.py {{ARGS}}
   ```

   Where {{ARGS}} are the user-provided arguments (e.g., `--type sphinx`).

   ## Workflow
   1. Ask the user which documentation tool to use (Sphinx or MkDocs)
   2. Collect project metadata interactively (project name, author, version, language)
   3. Execute the script with appropriate arguments
   4. Display the results to the user
   5. If errors occur, show clear error messages and next steps
   ```
2. `src/speckit_docs/commands/doc-update.md`を作成（同様のパターン、冒頭にC003表示を含める）：
   ```markdown
   # /doc-update - Update Documentation from Specifications

   [Active Rules: C001-C014]
   **CRITICAL原則**: ルール歪曲禁止・エラー迂回禁止・理想実装ファースト・記録管理・品質基準遵守・ドキュメント整合性・TDD必須・DRY原則・破壊的リファクタリング推奨・妥協実装絶対禁止

   Execute the following command to update documentation:

   ```bash
   uv run python .specify/scripts/docs/doc_update.py
   ```

   ## Workflow
   1. Check that docs/ directory exists
   2. Execute the script to update documentation
   3. Display summary of updated features
   4. If errors occur, show clear error messages and next steps
   ```

**Acceptance Criteria**:
- 両方のファイルが存在する
- Markdown構文が正しい
- **C003冒頭表示が両方のファイルに含まれている**
- Claude Codeが解釈可能な形式である

**Estimated Time**: 30分

---

### T013: バックエンドスクリプトのスタブ実装
**File**: `src/speckit_docs/scripts/doc_init.py`, `doc_update.py`
**Type**: US3 - Assets
**Story**: US3 (P1 MVP)
**Priority**: High

**Description**:
T010/T011でコピーされるバックエンドスクリプトのスタブ実装を作成する。

**Steps**:
1. `doc_init.py`のスタブを作成：
   ```python
   #!/usr/bin/env python3
   """
   doc_init.py - Initialize documentation project

   This script is executed by /doc-init command.
   """
   import typer
   from typing import Optional

   app = typer.Typer()

   @app.command()
   def main(
       doc_type: str = typer.Option("sphinx", "--type", help="Documentation tool"),
       project_name: Optional[str] = typer.Option(None, "--project-name"),
       author: Optional[str] = typer.Option(None, "--author"),
       version: str = typer.Option("0.1.0", "--version"),
       language: str = typer.Option("ja", "--language"),
       force: bool = typer.Option(False, "--force"),
   ) -> int:
       """Initialize documentation project."""
       print(f"Initializing {doc_type} project...")
       # 実装はT014以降で追加
       return 0

   if __name__ == "__main__":
       app()
   ```
2. `doc_update.py`のスタブを作成（同様のパターン）

**Acceptance Criteria**:
- スクリプトが実行可能である
- `--help`が動作する
- Exit code 0を返す（現時点ではスタブのみ）

**Estimated Time**: 30分

---

### T014: インストール統合テスト
**File**: `tests/integration/test_install.py`
**Type**: US3 - Integration Test
**Story**: US3 (P1 MVP)
**Priority**: High

**Description**:
End-to-Endでインストール機能をテストする。

**Steps**:
1. テストを作成：
   ```python
   def test_install_end_to_end(tmp_path):
       # spec-kitプロジェクト構造を作成
       (tmp_path / ".specify").mkdir()
       (tmp_path / ".claude").mkdir()

       # installコマンドを実行
       from speckit_docs.cli.install_handler import install_handler
       install_handler(force=True)

       # コマンド定義がコピーされたことを確認
       assert (tmp_path / ".claude/commands/doc-init.md").exists()
       assert (tmp_path / ".claude/commands/doc-update.md").exists()

       # バックエンドスクリプトがコピーされたことを確認
       assert (tmp_path / ".specify/scripts/docs/doc_init.py").exists()
       assert (tmp_path / ".specify/scripts/docs/doc_update.py").exists()

       # スクリプトが実行可能であることを確認
       result = subprocess.run(
           ["python", tmp_path / ".specify/scripts/docs/doc_init.py", "--help"],
           capture_output=True
       )
       assert result.returncode == 0
   ```
2. テストを実行し、すべて通過することを確認

**Acceptance Criteria**:
- 統合テストが通過する
- インストール機能がend-to-endで動作する

**Estimated Time**: 1時間

---

**Checkpoint 1**: ✅ US3完了
- CLIツールのインストールが可能
- コマンド定義とスクリプトが正しくコピーされる
- `speckit-docs install`が動作する

---

## Phase 4: User Story 1 - ドキュメントプロジェクトの初期化

**Goal**: Sphinx/MkDocsドキュメントプロジェクトの初期化機能を実装する。

**Story Dependencies**: Phase 1-3完了（基盤とインストール機能）
**Independent Test**: 既存spec-kitプロジェクトで`/doc-init --type sphinx`を実行し、`docs/`ディレクトリが作成され、ビルド可能なSphinxプロジェクトが生成されることを確認

### T015: FeatureDiscovererの実装
**File**: `src/speckit_docs/utils/feature_discovery.py`
**Type**: US1 - Implementation
**Story**: US1 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/utils/test_feature_discovery.py`
**TDD**: ✅ Required (C010)

**Description**:
`specs/`ディレクトリをスキャンし、機能ディレクトリを発見してFeatureオブジェクトを生成する（FR-011）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_discover_features(tmp_path):
       # specs/ディレクトリ構造を作成
       (tmp_path / "specs/001-user-auth").mkdir(parents=True)
       (tmp_path / "specs/001-user-auth/spec.md").write_text("# User Auth")
       (tmp_path / "specs/002-api-integration").mkdir(parents=True)
       (tmp_path / "specs/002-api-integration/spec.md").write_text("# API Integration")

       discoverer = FeatureDiscoverer(tmp_path)
       features = discoverer.discover_features()

       assert len(features) == 2
       assert features[0].id == "001"
       assert features[0].name == "user-auth"
       assert features[0].spec_file.exists()
   ```
2. **GREEN**: 実装：
   ```python
   from pathlib import Path
   from typing import List
   from ..models import Feature, FeatureStatus

   class FeatureDiscoverer:
       def __init__(self, repo_path: Path = Path(".")):
           self.specs_dir = repo_path / "specs"

       def discover_features(self) -> List[Feature]:
           if not self.specs_dir.exists():
               return []

           features = []
           for feature_dir in sorted(self.specs_dir.iterdir()):
               if not feature_dir.is_dir():
                   continue

               spec_file = feature_dir / "spec.md"
               if not spec_file.exists():
                   continue

               # 機能IDと名前を抽出（例: "001-user-auth" → id="001", name="user-auth"）
               dir_name = feature_dir.name
               parts = dir_name.split("-", 1)
               feature_id = parts[0] if len(parts) > 0 else dir_name
               feature_name = parts[1] if len(parts) > 1 else dir_name

               feature = Feature(
                   id=feature_id,
                   name=feature_name,
                   directory_path=feature_dir,
                   spec_file=spec_file,
                   status=FeatureStatus.DRAFT,
                   plan_file=feature_dir / "plan.md" if (feature_dir / "plan.md").exists() else None,
                   tasks_file=feature_dir / "tasks.md" if (feature_dir / "tasks.md").exists() else None,
               )
               features.append(feature)

           return features
   ```
3. **REFACTOR**: エラーハンドリングとログ追加

**Acceptance Criteria**:
- テストが通過する
- `specs/`ディレクトリ内のすべての機能を発見できる
- spec.mdが存在しない機能はスキップされる

**Estimated Time**: 1時間

---

### T016: BaseGenerator抽象クラスの実装
**File**: `src/speckit_docs/generators/base.py`
**Type**: US1 - Implementation
**Story**: US1 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/generators/test_base.py`
**TDD**: ✅ Required (C010)

**Description**:
ドキュメントジェネレータの抽象ベースクラスを実装する（Core Principle III: Extensibility）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く（具象クラスをモックで作成）：
   ```python
   def test_base_generator_interface():
       class TestGenerator(BaseGenerator):
           def generate_config(self, **kwargs) -> None:
               pass

           def generate_index(self) -> None:
               pass

           def create_directory_structure(self) -> None:
               pass

       generator = TestGenerator(Path("/tmp/docs"))
       assert generator.docs_dir == Path("/tmp/docs")
   ```
2. **GREEN**: 実装：
   ```python
   from abc import ABC, abstractmethod
   from pathlib import Path
   from typing import List
   from ..models import Feature, StructureType, GeneratorTool

   class BaseGenerator(ABC):
       def __init__(self, docs_dir: Path):
           self.docs_dir = docs_dir
           self.structure_type = StructureType.FLAT

       @abstractmethod
       def generate_config(self, **kwargs) -> None:
           """Generate tool-specific configuration file (conf.py or mkdocs.yml)."""
           pass

       @abstractmethod
       def generate_index(self) -> None:
           """Generate index page (index.md)."""
           pass

       @abstractmethod
       def create_directory_structure(self, feature_count: int) -> None:
           """Create directory structure based on feature count."""
           pass

       def determine_structure(self, feature_count: int) -> StructureType:
           """Determine whether to use flat or comprehensive structure (FR-005, FR-006)."""
           return StructureType.FLAT if feature_count <= 5 else StructureType.COMPREHENSIVE
   ```
3. **REFACTOR**: 必要に応じて共通メソッドを追加

**Acceptance Criteria**:
- テストが通過する
- 抽象メソッドが正しく定義されている
- `determine_structure()`が機能数に応じて正しい構造を返す

**Estimated Time**: 1時間

---

### T017: SphinxGeneratorの実装
**File**: `src/speckit_docs/generators/sphinx.py`
**Type**: US1 - Implementation
**Story**: US1 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/generators/test_sphinx.py`
**TDD**: ✅ Required (C010)

**Description**:
Sphinxドキュメントプロジェクトを生成する（FR-005, FR-005a）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_sphinx_generator_create_config(tmp_path):
       generator = SphinxGenerator(tmp_path / "docs")
       generator.generate_config(
           project_name="Test Project",
           author="Test Author",
           version="1.0.0",
           language="ja"
       )

       conf_py = tmp_path / "docs/conf.py"
       assert conf_py.exists()

       content = conf_py.read_text()
       assert "myst_parser" in content
       assert "Test Project" in content
   ```
2. **GREEN**: 実装（Jinja2テンプレート使用）：
   ```python
   from pathlib import Path
   from jinja2 import Environment, PackageLoader
   from .base import BaseGenerator
   from ..models import StructureType

   class SphinxGenerator(BaseGenerator):
       def __init__(self, docs_dir: Path):
           super().__init__(docs_dir)
           self.env = Environment(loader=PackageLoader("speckit_docs", "templates"))

       def generate_config(self, **kwargs) -> None:
           """Generate conf.py with myst-parser configuration (FR-005a)."""
           template = self.env.get_template("sphinx/conf.py.jinja2")
           conf_content = template.render(**kwargs)

           conf_py = self.docs_dir / "conf.py"
           conf_py.write_text(conf_content)

       def generate_index(self) -> None:
           """Generate index.md in Markdown format."""
           template = self.env.get_template("sphinx/index.md.jinja2")
           index_content = template.render(structure_type=self.structure_type)

           index_md = self.docs_dir / "index.md"
           index_md.write_text(index_content)

       def create_directory_structure(self, feature_count: int) -> None:
           """Create directory structure based on feature count (FR-005)."""
           self.structure_type = self.determine_structure(feature_count)

           self.docs_dir.mkdir(parents=True, exist_ok=True)

           if self.structure_type == StructureType.COMPREHENSIVE:
               (self.docs_dir / "features").mkdir(exist_ok=True)
               (self.docs_dir / "guides").mkdir(exist_ok=True)
               (self.docs_dir / "api").mkdir(exist_ok=True)
               (self.docs_dir / "architecture").mkdir(exist_ok=True)
   ```
3. **REFACTOR**: テンプレートファイルを作成（`src/speckit_docs/templates/sphinx/`）

**Acceptance Criteria**:
- テストが通過する
- `conf.py`にmyst-parser設定が含まれる
- `index.md`がMarkdown形式で生成される
- 機能数に応じて正しいディレクトリ構造が作成される

**Estimated Time**: 2時間

---

### T018: MkDocsGeneratorの実装
**File**: `src/speckit_docs/generators/mkdocs.py`
**Type**: US1 - Implementation
**Story**: US1 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/generators/test_mkdocs.py`
**TDD**: ✅ Required (C010)

**Description**:
MkDocsドキュメントプロジェクトを生成する（FR-006）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く（T017と同様のパターン）
2. **GREEN**: 実装（T017と同様、MkDocs用のテンプレートを使用）：
   ```python
   class MkDocsGenerator(BaseGenerator):
       def generate_config(self, **kwargs) -> None:
           """Generate mkdocs.yml."""
           template = self.env.get_template("mkdocs/mkdocs.yml.jinja2")
           config_content = template.render(**kwargs)

           mkdocs_yml = self.docs_dir.parent / "mkdocs.yml"
           mkdocs_yml.write_text(config_content)

       # ... (他のメソッドは T017 と同様)
   ```
3. **REFACTOR**: テンプレートファイルを作成（`src/speckit_docs/templates/mkdocs/`）

**Acceptance Criteria**:
- テストが通過する
- `mkdocs.yml`が正しい形式で生成される
- `docs/index.md`がMarkdown形式で生成される

**Estimated Time**: 1.5時間

---

### T019: Jinja2テンプレートファイルの作成
**File**: `src/speckit_docs/templates/sphinx/conf.py.jinja2`, `index.md.jinja2`, `mkdocs/mkdocs.yml.jinja2`
**Type**: US1 - Assets
**Story**: US1 (P1 MVP)
**Priority**: High

**Description**:
Sphinx/MkDocs設定ファイルのJinja2テンプレートを作成する。

**Steps**:
1. `src/speckit_docs/templates/sphinx/conf.py.jinja2`を作成：
   ```python
   # Configuration file for the Sphinx documentation builder.

   project = "{{ project_name }}"
   copyright = "{{ year }}, {{ author }}"
   author = "{{ author }}"
   version = "{{ version }}"
   release = "{{ version }}"

   extensions = [
       "myst_parser",  # FR-005a: MyST Markdown support
   ]

   source_suffix = {
       ".rst": "restructuredtext",
       ".md": "markdown",
   }

   myst_enable_extensions = [
       "colon_fence",
       "deflist",
       "tasklist",
       "attrs_inline",
   ]

   language = "{{ language }}"

   # ... (他の設定)
   ```
2. `src/speckit_docs/templates/sphinx/index.md.jinja2`を作成
3. `src/speckit_docs/templates/mkdocs/mkdocs.yml.jinja2`を作成

**Acceptance Criteria**:
- すべてのテンプレートファイルが存在する
- Jinja2構文が正しい
- myst-parser設定が含まれている（Sphinx）

**Estimated Time**: 1時間

---

### T020: doc_init.pyの完全実装
**File**: `src/speckit_docs/scripts/doc_init.py`
**Type**: US1 - Implementation
**Story**: US1 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/scripts/test_doc_init.py`
**TDD**: ✅ Required (C010)

**Description**:
T013で作成したスタブを完全実装に置き換える（FR-003a, FR-003b, FR-003c, FR-003d）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_doc_init_sphinx(tmp_path, monkeypatch):
       monkeypatch.chdir(tmp_path)
       (tmp_path / ".specify").mkdir()
       (tmp_path / "specs/001-test").mkdir(parents=True)
       (tmp_path / "specs/001-test/spec.md").write_text("# Test")

       from speckit_docs.scripts.doc_init import main

       result = main(
           doc_type="sphinx",
           project_name="Test Project",
           author="Test Author",
           version="1.0.0",
           language="ja",
           force=False
       )

       assert result == 0
       assert (tmp_path / "docs/conf.py").exists()
       assert (tmp_path / "docs/index.md").exists()
   ```
2. **GREEN**: 実装：
   ```python
   import typer
   from pathlib import Path
   from typing import Optional
   from ..generators.sphinx import SphinxGenerator
   from ..generators.mkdocs import MkDocsGenerator
   from ..utils.feature_discovery import FeatureDiscoverer
   from ..exceptions import SpecKitDocsError
   from datetime import datetime

   app = typer.Typer()

   @app.command()
   def main(
       doc_type: str = typer.Option("sphinx", "--type", help="Documentation tool"),
       project_name: Optional[str] = typer.Option(None, "--project-name"),
       author: Optional[str] = typer.Option(None, "--author"),
       version: str = typer.Option("0.1.0", "--version"),
       language: str = typer.Option("ja", "--language"),
       # MkDocs specific
       site_name: Optional[str] = typer.Option(None, "--site-name"),
       repo_url: Optional[str] = typer.Option(None, "--repo-url"),
       force: bool = typer.Option(False, "--force"),
   ) -> int:
       """Initialize documentation project."""
       try:
           # FR-003b: デフォルト値を設定
           if project_name is None:
               project_name = Path.cwd().name
           if author is None:
               # Git user.name から取得
               import subprocess
               try:
                   author = subprocess.check_output(
                       ["git", "config", "user.name"],
                       text=True
                   ).strip()
               except:
                   author = "Unknown Author"

           # 機能数を取得して構造を決定
           discoverer = FeatureDiscoverer()
           features = discoverer.discover_features()
           feature_count = len(features)

           # docs/ディレクトリの存在確認（FR-003d）
           docs_dir = Path("docs")
           if docs_dir.exists() and not force:
               raise SpecKitDocsError(
                   "docs/ already exists. Use --force to overwrite.",
                   "Run with --force flag or remove docs/ manually"
               )

           # ジェネレータを選択して実行
           if doc_type == "sphinx":
               generator = SphinxGenerator(docs_dir)
               generator.create_directory_structure(feature_count)
               generator.generate_config(
                   project_name=project_name,
                   author=author,
                   version=version,
                   language=language,
                   year=datetime.now().year
               )
               generator.generate_index()

               print(f"✓ Initialized Sphinx project in {docs_dir}")
               print(f"✓ Structure: {generator.structure_type.value}")
               print(f"✓ Feature count: {feature_count}")

           elif doc_type == "mkdocs":
               generator = MkDocsGenerator(docs_dir)
               # ... (同様の処理)

           else:
               raise SpecKitDocsError(
                   f"Unknown documentation tool: {doc_type}",
                   "Use --type sphinx or --type mkdocs"
               )

           # FR-008: パッケージインストール案内
           if doc_type == "sphinx":
               print("\nNext steps:")
               print("1. Install dependencies: uv add sphinx myst-parser")
               print("2. Build documentation: cd docs && make html")

           return 0

       except SpecKitDocsError as e:
           print(f"Error: {e}")
           return 1

   if __name__ == "__main__":
       app()
   ```
3. **REFACTOR**: エラーハンドリングとログ改善

**Acceptance Criteria**:
- テストが通過する
- Sphinx/MkDocsプロジェクトが正しく初期化される
- デフォルト値が正しく設定される（FR-003b）
- `--force`フラグが動作する（FR-003d）

**Estimated Time**: 2時間

---

### T021: US1統合テスト
**File**: `tests/integration/test_doc_init.py`
**Type**: US1 - Integration Test
**Story**: US1 (P1 MVP)
**Priority**: High

**Description**:
End-to-Endでドキュメント初期化機能をテストする。

**Steps**:
1. テストを作成：
   ```python
   def test_doc_init_end_to_end_sphinx(tmp_path):
       # spec-kitプロジェクト構造を作成
       (tmp_path / ".specify").mkdir()
       (tmp_path / ".claude").mkdir()
       (tmp_path / "specs/001-test").mkdir(parents=True)
       (tmp_path / "specs/001-test/spec.md").write_text("# Test Feature")

       # doc_init.py を実行
       result = subprocess.run(
           [
               "uv", "run", "python",
               tmp_path / ".specify/scripts/docs/doc_init.py",
               "--type", "sphinx",
               "--project-name", "Test Project",
               "--author", "Test Author",
               "--force"
           ],
           cwd=tmp_path,
           capture_output=True
       )

       assert result.returncode == 0
       assert (tmp_path / "docs/conf.py").exists()
       assert (tmp_path / "docs/index.md").exists()

       # Sphinxビルドが成功することを確認
       build_result = subprocess.run(
           ["sphinx-build", "-b", "html", ".", "_build/html"],
           cwd=tmp_path / "docs",
           capture_output=True
       )
       assert build_result.returncode == 0
   ```
2. テストを実行し、すべて通過することを確認

**Acceptance Criteria**:
- 統合テストが通過する
- 初期化機能がend-to-endで動作する
- 生成されたドキュメントがビルド可能である（SC-002）

**Estimated Time**: 1.5時間

---

**Checkpoint 2**: ✅ US1完了
- ドキュメントプロジェクトの初期化が可能
- Sphinx/MkDocsの両方をサポート
- `/doc-init`が動作する

---

## Phase 5: User Story 2 - spec-kit仕様からのドキュメント更新

**Goal**: `specs/`ディレクトリからドキュメントを自動生成・更新する機能を実装する。

**Story Dependencies**: Phase 4完了（ドキュメント初期化機能）
**Independent Test**: 3つの機能を持つspec-kitプロジェクトで`/doc-update`を実行し、各機能のドキュメントページが生成され、ナビゲーションが更新されることを確認

### T022: DocumentGeneratorの実装
**File**: `src/speckit_docs/generators/document.py`
**Type**: US2 - Implementation
**Story**: US2 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/generators/test_document.py`
**TDD**: ✅ Required (C010)

**Description**:
Documentエンティティからドキュメントページを生成する（FR-012, FR-015, FR-016, FR-017, FR-018）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く：
   ```python
   def test_document_generator_generate_feature_page():
       feature = Feature(
           id="001",
           name="test-feature",
           directory_path=Path("/path/to/specs/001-test-feature"),
           spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
           status=FeatureStatus.DRAFT
       )

       spec_doc = Document(
           file_path=feature.spec_file,
           type=DocumentType.SPEC,
           content="# Test Feature\n\n## Requirements\n\n- REQ-001: Test requirement"
       )

       generator = DocumentGenerator()
       page_content = generator.generate_feature_page(feature, spec_doc, plan_doc=None, tasks_doc=None)

       assert "# Test Feature" in page_content
       assert "## Requirements" in page_content
   ```
2. **GREEN**: 実装：
   ```python
   from pathlib import Path
   from typing import Optional
   from jinja2 import Environment, PackageLoader
   from ..models import Feature, Document, DocumentType

   class DocumentGenerator:
       def __init__(self):
           self.env = Environment(loader=PackageLoader("speckit_docs", "templates"))

       def generate_feature_page(
           self,
           feature: Feature,
           spec_doc: Document,
           plan_doc: Optional[Document] = None,
           tasks_doc: Optional[Document] = None
       ) -> str:
           """Generate feature documentation page from spec.md, plan.md, tasks.md (FR-015, FR-016, FR-017)."""
           template = self.env.get_template("feature-page.md.jinja2")

           content = template.render(
               feature=feature,
               spec_content=spec_doc.content,
               plan_content=plan_doc.content if plan_doc else None,
               tasks_content=tasks_doc.content if tasks_doc else None,
               missing_plan=plan_doc is None,
               missing_tasks=tasks_doc is None
           )

           return content
   ```
3. **REFACTOR**: テンプレートファイルを作成（`src/speckit_docs/templates/feature-page.md.jinja2`）

**Acceptance Criteria**:
- テストが通過する
- spec.mdからすべてのセクションが抽出される（FR-015）
- plan.mdが存在する場合、アーキテクチャセクションが含まれる（FR-016）
- tasks.mdが存在する場合、タスク概要が含まれる（FR-017）
- 欠落ファイルには注記が表示される（FR-018）

**Estimated Time**: 2時間

---

### T023: FeaturePageGeneratorの実装
**File**: `src/speckit_docs/generators/feature_page.py`
**Type**: US2 - Implementation
**Story**: US2 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/generators/test_feature_page.py`
**TDD**: ✅ Required (C010)

**Description**:
すべての機能のドキュメントページを生成し、適切な場所に配置する（FR-013, FR-014）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く
2. **GREEN**: 実装：
   ```python
   from pathlib import Path
   from typing import List
   from ..models import Feature, StructureType, GeneratorTool
   from ..parsers.markdown_parser import MarkdownParser
   from .document import DocumentGenerator

   class FeaturePageGenerator:
       def __init__(self, docs_dir: Path, structure_type: StructureType, tool: GeneratorTool):
           self.docs_dir = docs_dir
           self.structure_type = structure_type
           self.tool = tool
           self.document_generator = DocumentGenerator()
           self.markdown_parser = MarkdownParser()

       def generate_pages(self, features: List[Feature]) -> List[Path]:
           """Generate feature pages for all features (FR-013, FR-014)."""
           generated_pages = []

           for feature in features:
               # spec.mdを解析
               spec_doc = self._parse_document(feature.spec_file, DocumentType.SPEC)
               plan_doc = self._parse_document(feature.plan_file, DocumentType.PLAN) if feature.plan_file else None
               tasks_doc = self._parse_document(feature.tasks_file, DocumentType.TASKS) if feature.tasks_file else None

               # ドキュメントページを生成
               page_content = self.document_generator.generate_feature_page(
                   feature, spec_doc, plan_doc, tasks_doc
               )

               # ファイル名を決定（FR-013, FR-014）
               page_filename = f"{feature.name}.md"

               # 配置場所を決定（FR-013, FR-014）
               if self.structure_type == StructureType.FLAT:
                   page_path = self.docs_dir / page_filename
               else:
                   page_path = self.docs_dir / "features" / page_filename

               # ファイルに書き込み
               page_path.parent.mkdir(parents=True, exist_ok=True)
               page_path.write_text(page_content)

               generated_pages.append(page_path)

           return generated_pages

       def _parse_document(self, file_path: Path, doc_type: DocumentType) -> Document:
           content = file_path.read_text()
           sections = self.markdown_parser.parse(content)

           return Document(
               file_path=file_path,
               type=doc_type,
               content=content,
               sections=sections
           )
   ```
3. **REFACTOR**: エラーハンドリング追加

**Acceptance Criteria**:
- テストが通過する
- すべての機能のページが生成される
- ファイル名は説明的な名前（番号なし）である（FR-013, FR-014）
- 構造タイプに応じて正しい場所に配置される

**Estimated Time**: 2時間

---

### T024: NavigationUpdaterの実装
**File**: `src/speckit_docs/generators/navigation.py`
**Type**: US2 - Implementation
**Story**: US2 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/generators/test_navigation.py`
**TDD**: ✅ Required (C010)

**Description**:
Sphinx toctreeまたはMkDocs navを更新する（FR-013, FR-014）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く
2. **GREEN**: 実装：
   ```python
   from pathlib import Path
   from typing import List
   from ..models import GeneratorTool

   class NavigationUpdater:
       def __init__(self, docs_dir: Path, tool: GeneratorTool):
           self.docs_dir = docs_dir
           self.tool = tool

       def update_navigation(self, feature_pages: List[Path]) -> None:
           """Update navigation (Sphinx toctree or MkDocs nav) (FR-013, FR-014)."""
           if self.tool == GeneratorTool.SPHINX:
               self._update_sphinx_toctree(feature_pages)
           elif self.tool == GeneratorTool.MKDOCS:
               self._update_mkdocs_nav(feature_pages)

       def _update_sphinx_toctree(self, feature_pages: List[Path]) -> None:
           """Update index.md toctree."""
           index_path = self.docs_dir / "index.md"
           index_content = index_path.read_text()

           # toctreeセクションを生成
           toctree_lines = ["```{toctree}", ":maxdepth: 2", ":caption: Features", ""]
           for page in feature_pages:
               relative_path = page.relative_to(self.docs_dir).with_suffix("")
               toctree_lines.append(str(relative_path))
           toctree_lines.append("```")

           toctree_block = "\n".join(toctree_lines)

           # 既存のtoctreeを置き換え、または追加
           # ... (実装詳細)

       def _update_mkdocs_nav(self, feature_pages: List[Path]) -> None:
           """Update mkdocs.yml nav section."""
           mkdocs_yml = self.docs_dir.parent / "mkdocs.yml"

           # YAML解析とnav更新
           import yaml
           with open(mkdocs_yml) as f:
               config = yaml.safe_load(f)

           # navセクションを更新
           config["nav"] = config.get("nav", [])
           # ... (実装詳細)

           with open(mkdocs_yml, "w") as f:
               yaml.dump(config, f)
   ```
3. **REFACTOR**: YAML処理を安全にする

**Acceptance Criteria**:
- テストが通過する
- Sphinx toctreeが正しく更新される（FR-013）
- MkDocs navが正しく更新される（FR-014）

**Estimated Time**: 2時間

---

### T025: doc_update.pyの完全実装
**File**: `src/speckit_docs/scripts/doc_update.py`
**Type**: US2 - Implementation
**Story**: US2 (P1 MVP)
**Priority**: High

**Test File**: `tests/unit/scripts/test_doc_update.py`
**TDD**: ✅ Required (C010)

**Description**:
T013で作成したスタブを完全実装に置き換える（FR-010, FR-011, FR-012, FR-013, FR-014, FR-020）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く
2. **GREEN**: 実装：
   ```python
   import typer
   from pathlib import Path
   from ..generators.feature_page import FeaturePageGenerator
   from ..generators.navigation import NavigationUpdater
   from ..utils.feature_discovery import FeatureDiscoverer
   from ..exceptions import SpecKitDocsError

   app = typer.Typer()

   @app.command()
   def main() -> int:
       """Update documentation from spec-kit specifications."""
       try:
           # FR-010: docs/ディレクトリの検証
           docs_dir = Path("docs")
           if not docs_dir.exists():
               raise SpecKitDocsError(
                   "Documentation project not found.",
                   "Run /doc-init first to initialize documentation"
               )

           # ドキュメントツールの検出
           tool = _detect_tool(docs_dir)
           structure_type = _detect_structure(docs_dir)

           # FR-011: 機能の発見
           discoverer = FeatureDiscoverer()
           features = discoverer.discover_features()

           if not features:
               raise SpecKitDocsError(
                   "No features found in specs/ directory.",
                   "Run /speckit.specify to create feature specifications"
               )

           # ドキュメント生成
           page_generator = FeaturePageGenerator(docs_dir, structure_type, tool)
           feature_pages = page_generator.generate_pages(features)

           # ナビゲーション更新
           nav_updater = NavigationUpdater(docs_dir, tool)
           nav_updater.update_navigation(feature_pages)

           # FR-020: 更新サマリーを表示
           print(f"✓ Updated documentation for {len(features)} features")
           print(f"✓ Generated {len(feature_pages)} pages")

           return 0

       except SpecKitDocsError as e:
           print(f"Error: {e}")
           return 1

   def _detect_tool(docs_dir: Path) -> GeneratorTool:
       if (docs_dir / "conf.py").exists():
           return GeneratorTool.SPHINX
       elif (docs_dir.parent / "mkdocs.yml").exists():
           return GeneratorTool.MKDOCS
       else:
           raise SpecKitDocsError(
               "Unknown documentation tool.",
               "Could not detect Sphinx or MkDocs"
           )

   def _detect_structure(docs_dir: Path) -> StructureType:
       if (docs_dir / "features").exists():
           return StructureType.COMPREHENSIVE
       else:
           return StructureType.FLAT

   if __name__ == "__main__":
       app()
   ```
3. **REFACTOR**: エラーハンドリングとログ改善

**Acceptance Criteria**:
- テストが通過する
- すべての機能のドキュメントが生成される
- ナビゲーションが更新される
- 更新サマリーが表示される（FR-020）

**Estimated Time**: 2時間

---

### T026: インクリメンタル更新の実装
**File**: `src/speckit_docs/scripts/doc_update.py` (拡張)
**Type**: US2 - Implementation
**Story**: US2 (P1 MVP)
**Priority**: Medium

**Test File**: `tests/unit/scripts/test_incremental_update.py`
**TDD**: ✅ Required (C010)

**Description**:
Git diffを使用して変更された機能のみを更新する（FR-019）。

**Steps (Red-Green-Refactor)**:
1. **RED**: テストを書く
2. **GREEN**: 実装（doc_update.pyにインクリメンタル更新ロジックを追加）：
   ```python
   from ..utils.git import ChangeDetector

   @app.command()
   def main(incremental: bool = typer.Option(True, "--incremental/--full")) -> int:
       # ... (既存のコード)

       if incremental:
           # FR-019: Git diffで変更検出
           change_detector = ChangeDetector()
           changed_features = change_detector.get_changed_features()

           if changed_features:
               features = changed_features
               print(f"✓ Detected {len(features)} changed features (incremental update)")
           else:
               print("✓ No changes detected, skipping update")
               return 0
       else:
           # フル更新
           features = discoverer.discover_features()
           print(f"✓ Full update: {len(features)} features")

       # ... (既存の生成ロジック)
   ```
3. **REFACTOR**: 初回コミットケースの処理

**Acceptance Criteria**:
- テストが通過する
- 変更された機能のみが更新される（FR-019）
- `--full`フラグですべての機能を更新できる
- 更新サマリーに変更数が表示される（FR-020）

**Estimated Time**: 1.5時間

---

### T027: US2統合テスト
**File**: `tests/integration/test_doc_update.py`
**Type**: US2 - Integration Test
**Story**: US2 (P1 MVP)
**Priority**: High

**Description**:
End-to-Endでドキュメント更新機能をテストする。

**Steps**:
1. テストを作成：
   ```python
   def test_doc_update_end_to_end(tmp_path):
       # spec-kitプロジェクト + 初期化済みドキュメントを作成
       # ... (セットアップ)

       # 3つの機能を作成
       for i in range(1, 4):
           feature_dir = tmp_path / f"specs/{i:03d}-feature-{i}"
           feature_dir.mkdir(parents=True)
           (feature_dir / "spec.md").write_text(f"# Feature {i}")

       # doc_update.py を実行
       result = subprocess.run(
           ["uv", "run", "python", tmp_path / ".specify/scripts/docs/doc_update.py"],
           cwd=tmp_path,
           capture_output=True
       )

       assert result.returncode == 0
       assert (tmp_path / "docs/feature-1.md").exists()
       assert (tmp_path / "docs/feature-2.md").exists()
       assert (tmp_path / "docs/feature-3.md").exists()

       # ナビゲーションが更新されていることを確認
       index_content = (tmp_path / "docs/index.md").read_text()
       assert "feature-1" in index_content
   ```
2. テストを実行し、すべて通過することを確認

**Acceptance Criteria**:
- 統合テストが通過する
- 更新機能がend-to-endで動作する
- すべての機能のドキュメントが生成される（SC-008）

**Estimated Time**: 1.5時間

---

**Checkpoint 3**: ✅ US2完了 → **MVP完成**
- spec-kit仕様からのドキュメント更新が可能
- インクリメンタル更新が動作する
- `/doc-update`が動作する
- **基本的なドキュメント生成機能がすべて完成**

---

## Phase 6: Polish & Code Quality

**Goal**: コード品質を保証し、プロダクションレディな状態にする。

### T028: End-to-Endテスト
**File**: `tests/e2e/test_full_workflow.py`
**Type**: Polish - E2E Test
**Story**: MVP Polish
**Priority**: High

**Description**:
実際のspec-kitプロジェクトでフルワークフローをテストする。

**Steps**:
1. 実際のspec-kitプロジェクト構造を作成
2. `speckit-docs install` → `/doc-init` → `/doc-update` の一連の流れをテスト
3. 生成されたドキュメントがビルド可能であることを確認（Sphinx: `make html`、MkDocs: `mkdocs build`）

**Acceptance Criteria**:
- E2Eテストが通過する
- Sphinxドキュメントが正常にビルドされる（SC-002）
- MkDocsドキュメントが正常にビルドされる
- 生成されたHTMLが表示可能である（SC-007）

**Estimated Time**: 2時間

---

### T029: コード品質チェック
**File**: `.github/workflows/ci.yml` (CI設定)
**Type**: Polish - Quality
**Story**: MVP Polish
**Priority**: High

**Description**:
ruff、black、mypyを実行してコード品質を検証する（C006）。

**Steps**:
1. すべてのコードに対してruffを実行し、警告を修正
2. blackでコードをフォーマット
3. mypyで型チェックを実行し、エラーを修正
4. pytest + pytest-covでテストカバレッジを測定（目標90%以上）
5. CI設定ファイルを作成（GitHub Actions）

**Acceptance Criteria**:
- ruffがエラーなしで通過する
- blackフォーマットが適用されている
- mypyが型エラーなしで通過する
- テストカバレッジが90%以上である（主要コードパス）
- CI設定が正しく動作する

**Estimated Time**: 2時間

---

### T030: ドキュメント更新
**File**: `README.md`, `CONTRIBUTING.md`
**Type**: Polish - Documentation
**Story**: MVP Polish
**Priority**: Medium

**Description**:
プロジェクトドキュメントを更新する。

**Steps**:
1. README.mdを更新：
   - インストール手順
   - クイックスタート
   - コマンドリファレンス
   - 制限事項とMVP範囲
2. CONTRIBUTING.mdを作成：
   - 開発環境セットアップ
   - テスト実行方法
   - コード品質基準
   - プルリクエストガイドライン

**Acceptance Criteria**:
- README.mdが完全で最新である
- CONTRIBUTING.mdが開発者向けガイドとして機能する
- すべてのドキュメントがMarkdownリンターを通過する

**Estimated Time**: 1時間

---

**Final Checkpoint**: ✅ MVP完成 & プロダクションレディ
- すべてのP1ユーザーストーリーが実装完了
- コード品質基準をすべて満たす
- ドキュメントが完全
- E2Eテストが通過

---

## Task Summary

### Total Task Count
- **Setup**: 3 tasks (T001-T003)
- **Foundational**: 4 tasks (T004-T007)
- **US3 (Install)**: 7 tasks (T008-T014)
- **US1 (Init)**: 7 tasks (T015-T021)
- **US2 (Update)**: 6 tasks (T022-T027)
- **Polish**: 3 tasks (T028-T030)

**Total**: 30 tasks

### Implementation Timeline Estimate
**Total Estimate**: 42時間（約5.5営業日、1日8時間換算）

**Phase Breakdown**:
- Phase 1 (Setup): 1.25時間
- Phase 2 (Foundational): 4.5時間
- Phase 3 (US3 - Install): 8.75時間
- Phase 4 (US1 - Doc Init): 10.5時間
- Phase 5 (US2 - Doc Update): 12時間
- Phase 6 (Polish): 5時間

---

**Generated**: 2025-10-13
**Last Updated**: 2025-10-13
**Version**: 1.0.0
