# Data Model: spec-kit-docs - AI駆動型ドキュメント生成システム

**Feature**: spec-kit-docs
**Date**: 2025-10-12
**Phase**: 1 - Data Model Definition
**Source**: [spec.md](spec.md) | [research.md](research.md)

## Overview

このドキュメントは、spec-kit-docs実装における主要なエンティティとその関係を定義します。実装言語に依存しない論理モデルとして記述し、Pythonでの実装時にクラス、データクラス、または辞書として具体化されます。

## Core Entities

### 1. Feature

spec-kitプロジェクトにおける1つの機能仕様を表現します。`.specify/specs/###-feature-name/`ディレクトリに対応します。

**Attributes**:
- `id` (str): 機能番号（例：`"001"`、`"002"`）
- `name` (str): 機能名（例：`"user-auth"`、`"draft-init-spec"`）
- `directory_path` (Path): 機能ディレクトリへの絶対パス（例：`.specify/specs/001-user-auth/`）
- `spec_file` (Path | None): spec.mdファイルへのパス（必須）
- `plan_file` (Path | None): plan.mdファイルへのパス（オプション）
- `tasks_file` (Path | None): tasks.mdファイルへのパス（オプション）
- `status` (FeatureStatus): 機能のステータス（enum: `DRAFT`, `PLANNED`, `IN_PROGRESS`, `COMPLETED`）
- `priority` (str | None): 優先度（例：`"P1"`, `"P2"`, `"P3"`）- spec.md内のメタデータから抽出
- `metadata` (dict): その他のメタデータ（作成日、更新日、タグ等）

**Relationships**:
- `documents`: Document[] - この機能に含まれるドキュメント（spec.md、plan.md、tasks.md）

**Validation Rules**:
- `spec_file`は必須（存在しない場合はFeatureとして認識しない - FR-001）
- `directory_path`は`.specify/specs/`配下である必要がある
- `id`は3桁の数字である必要がある

**Source Requirements**: FR-001, FR-002, FR-004

---

### 2. Document

Feature内の個別Markdownドキュメント（spec.md、plan.md、tasks.md）を表現します。

**Attributes**:
- `file_path` (Path): ドキュメントファイルへの絶対パス
- `type` (DocumentType): ドキュメント種別（enum: `SPEC`, `PLAN`, `TASKS`）
- `content` (str): ドキュメントの生コンテンツ（Markdown）
- `sections` (List[Section]): 解析されたセクションのリスト
- `last_modified` (datetime): ファイルの最終更新日時
- `git_status` (GitStatus): Gitステータス（enum: `UNTRACKED`, `MODIFIED`, `STAGED`, `COMMITTED`）

**Relationships**:
- `feature`: Feature - 所属する機能

**Methods**:
- `parse()`: Markdown内容を解析して`sections`を生成
- `extract_metadata()`: フロントマターまたはメタデータセクションから情報を抽出
- `is_changed(since: datetime)`: 指定日時以降に変更されたか判定

**Source Requirements**: FR-002, FR-012

---

### 3. Section

Document内の1つのMarkdownセクション（見出しとその配下の内容）を表現します。

**Attributes**:
- `title` (str): セクションタイトル（見出しテキスト）
- `level` (int): 見出しレベル（1-6、`#`の数）
- `content` (str): セクション本体のMarkdown（見出し除く）
- `line_start` (int): ドキュメント内の開始行番号
- `line_end` (int): ドキュメント内の終了行番号
- `subsections` (List[Section]): 子セクション（再帰構造）

**Methods**:
- `to_sphinx_md()`: Sphinx MyST Markdown形式に変換（必要に応じてディレクティブ追加）
- `to_mkdocs_md()`: MkDocs Markdown形式に変換
- `extract_code_blocks()`: コードブロックのリストを抽出

**Source Requirements**: FR-008, FR-013

---

### 4. DocumentStructure

生成するドキュメントサイトの全体構造を表現します。機能数に応じて動的に決定されます（research.md Decision 4）。

**Attributes**:
- `type` (StructureType): 構造タイプ（enum: `FLAT`, `COMPREHENSIVE`）
- `root_dir` (Path): ドキュメントルートディレクトリ（`docs/`）
- `directories` (List[str]): 生成するディレクトリのリスト
- `index_file` (Path): インデックスファイルのパス（`index.md`）

**Flat Structure** (5機能以下):
```
docs/
├── index.md
├── feature-a.md
├── feature-b.md
└── ...
```

**Comprehensive Structure** (6機能以上):
```
docs/
├── index.md
├── features/
│   ├── feature-a.md
│   ├── feature-b.md
│   └── ...
├── guides/
│   └── getting-started.md
├── api/
│   └── reference.md
└── architecture/
    └── overview.md
```

**Methods**:
- `determine_structure(feature_count: int) -> StructureType`: 機能数から構造を決定
- `get_feature_path(feature_name: str) -> Path`: 機能ドキュメントの出力パスを返す

**Source Requirements**: FR-005, Clarifications (5機能閾値)

---

### 5. GeneratorConfig

ドキュメント生成ツール（Sphinx/MkDocs）の設定を表現します。

**Attributes**:
- `tool` (GeneratorTool): 使用するツール（enum: `SPHINX`, `MKDOCS`）
- `project_name` (str): プロジェクト名
- `author` (str): 著者名
- `version` (str): バージョン番号（例：`"0.1.0"`）
- `language` (str): ドキュメント言語（デフォルト: `"ja"`）
- `theme` (str): 使用するテーマ
- `extensions` (List[str]): 拡張機能リスト（Sphinxの場合）
- `plugins` (List[str]): プラグインリスト（MkDocsの場合）
- `custom_settings` (dict): カスタム設定（ツール固有）

**Sphinx-Specific**:
- `extensions`: `['myst_parser', 'sphinx.ext.autodoc', ...]`（FR-005a）
- `source_suffix`: `{'.md': 'markdown', '.rst': 'restructuredtext'}`
- `myst_enable_extensions`: `['colon_fence', 'deflist', 'tasklist', 'attrs_inline']`

**MkDocs-Specific**:
- `theme`: `'material'`（デフォルト）
- `plugins`: `['search', 'awesome-pages']`

**Methods**:
- `to_sphinx_conf()`: Sphinx `conf.py`の内容を生成（Jinja2テンプレート経由）
- `to_mkdocs_yaml()`: MkDocs `mkdocs.yml`の内容を生成（Jinja2テンプレート経由）

**Source Requirements**: FR-005, FR-005a, FR-006, FR-007

---

### 6. Generator (Abstract Interface)

ドキュメント生成を実行する抽象インターフェース。Strategy Patternの基底クラス（research.md Decision 3）。

**Methods** (abstract):
- `init_project(config: GeneratorConfig, structure: DocumentStructure) -> None`: プロジェクト初期化
- `update_docs(features: List[Feature], incremental: bool = True) -> None`: ドキュメント更新
- `build_docs() -> BuildResult`: ドキュメントビルド実行
- `validate_project() -> ValidationResult`: プロジェクト構造検証

**Implementations**:
- `SphinxGenerator`: Sphinx用の実装（Markdown + myst-parser）
- `MkDocsGenerator`: MkDocs用の実装

**Source Requirements**: FR-005, FR-013, FR-018, research.md Decision 3

---

### 7. SphinxGenerator (Concrete Implementation)

Sphinx + myst-parserを使用したドキュメント生成実装。

**Attributes**:
- `config` (GeneratorConfig): Sphinx設定
- `structure` (DocumentStructure): ドキュメント構造
- `template_dir` (Path): Jinja2テンプレートディレクトリ（`templates/sphinx/`）

**Methods**:
- `init_project()`: `conf.py`, `index.md`, `Makefile`, `make.bat`を生成（FR-005）
- `update_docs()`: 各Featureから`.md`ファイルを生成し、`index.md`のtoctreeを更新（FR-013）
- `build_docs()`: `make html`を実行してHTMLを生成（FR-018）
- `validate_project()`: `conf.py`の存在、myst-parser設定を検証

**Specific Logic**:
- FR-005a: `conf.py`にmyst-parser設定を含める
- FR-008: セクション階層をMarkdown見出しレベル（`#`, `##`, `###`）に変換
- FR-013: ファイル命名規則（`001-user-auth` → `user-auth.md`）

**Source Requirements**: FR-005, FR-005a, FR-008, FR-013, FR-018

---

### 8. MkDocsGenerator (Concrete Implementation)

MkDocsを使用したドキュメント生成実装。

**Attributes**:
- `config` (GeneratorConfig): MkDocs設定
- `structure` (DocumentStructure): ドキュメント構造
- `template_dir` (Path): Jinja2テンプレートディレクトリ（`templates/mkdocs/`）

**Methods**:
- `init_project()`: `mkdocs.yml`と`docs/index.md`を生成（FR-006）
- `update_docs()`: 各Featureから`.md`ファイルを生成し、`mkdocs.yml`のnavを更新（FR-014）
- `build_docs()`: `mkdocs build`を実行してHTMLを生成（FR-019）
- `validate_project()`: `mkdocs.yml`の存在を検証

**Source Requirements**: FR-006, FR-014, FR-019

---

### 9. ChangeDetector

Git diffを使用して変更されたファイルを検出します（research.md Decision 2）。

**Attributes**:
- `repo` (GitRepository): GitPythonのリポジトリオブジェクト
- `base_ref` (str): 比較基準（デフォルト: `"HEAD"`）

**Methods**:
- `get_changed_features() -> List[Feature]`: 変更された機能のリストを返す
- `is_file_changed(file_path: Path) -> bool`: 特定ファイルが変更されたか判定
- `get_diff_stats() -> DiffStats`: 変更統計（追加行数、削除行数等）

**Logic**:
- `git diff --name-only HEAD~1 HEAD`で変更ファイルを取得
- `.specify/specs/`配下の変更のみをフィルタリング
- 該当するFeatureオブジェクトを返す

**Source Requirements**: FR-010, research.md Decision 2

---

### 10. MarkdownParser

Markdownファイルを解析してSectionツリーを生成します（research.md Decision 5）。

**Attributes**:
- `markdown_it` (MarkdownIt): markdown-it-pyのパーサーインスタンス
- `enable_myst` (bool): MyST構文のサポート有効化（デフォルト: True）

**Methods**:
- `parse(content: str) -> List[Section]`: Markdownをセクションツリーに解析
- `extract_headings(content: str) -> List[Heading]`: 見出しのリストを抽出
- `extract_code_blocks(content: str) -> List[CodeBlock]`: コードブロックを抽出
- `extract_metadata(content: str) -> dict`: フロントマターまたはメタデータセクションを抽出

**Supported Syntax**:
- CommonMark標準構文
- MyST Markdownディレクティブ（`` ```{note}``, `` ```{warning}``等）
- フロントマター（YAML）

**Source Requirements**: FR-008, FR-012, research.md Decision 5

---

### 11. BuildResult

ドキュメントビルドの結果を表現します。

**Attributes**:
- `success` (bool): ビルド成功/失敗
- `output_dir` (Path): 生成されたHTMLの出力先（Sphinx: `_build/html/`, MkDocs: `site/`）
- `warnings` (List[str]): ビルド警告のリスト
- `errors` (List[str]): ビルドエラーのリスト
- `build_time` (float): ビルド時間（秒）
- `file_count` (int): 生成されたHTMLファイル数

**Methods**:
- `is_valid() -> bool`: エラーなし、かつ警告が閾値以下か判定
- `get_summary() -> str`: ビルド結果のサマリー文字列を生成

**Source Requirements**: FR-018, FR-019, SC-001

---

### 12. ValidationResult

プロジェクト検証の結果を表現します。

**Attributes**:
- `is_valid` (bool): 検証成功/失敗
- `errors` (List[ValidationError]): 検証エラーのリスト
- `warnings` (List[ValidationWarning]): 検証警告のリスト
- `checked_items` (List[str]): チェックした項目のリスト

**ValidationError**:
- `message` (str): エラーメッセージ
- `suggestion` (str): 解決方法の提案（research.md Decision 8）
- `file_path` (Path | None): 関連ファイルパス

**Source Requirements**: FR-033, research.md Decision 8

---

## Enumerations

### FeatureStatus
```python
DRAFT       # spec.mdのみ存在
PLANNED     # plan.mdが存在
IN_PROGRESS # tasks.mdが存在、一部タスク完了
COMPLETED   # 全タスク完了
```

### DocumentType
```python
SPEC   # spec.md
PLAN   # plan.md
TASKS  # tasks.md
```

### GitStatus
```python
UNTRACKED  # Gitで追跡されていない
MODIFIED   # 変更あり
STAGED     # ステージング済み
COMMITTED  # コミット済み
```

### StructureType
```python
FLAT          # フラット構造（5機能以下）
COMPREHENSIVE # 包括的構造（6機能以上）
```

### GeneratorTool
```python
SPHINX  # Sphinx + myst-parser
MKDOCS  # MkDocs
```

## Entity Relationships

```
Project (spec-kitプロジェクト)
  ├─ 1..* Feature
  │    ├─ 1 Document (spec.md) - required
  │    ├─ 0..1 Document (plan.md) - optional
  │    └─ 0..1 Document (tasks.md) - optional
  │
  ├─ 1 DocumentStructure (動的決定)
  │    ├─ type: FLAT | COMPREHENSIVE
  │    └─ directories: List[str]
  │
  ├─ 1 GeneratorConfig
  │    ├─ tool: SPHINX | MKDOCS
  │    └─ settings: dict
  │
  ├─ 1 Generator (SphinxGenerator | MkDocsGenerator)
  │    ├─ uses: GeneratorConfig
  │    ├─ uses: DocumentStructure
  │    └─ generates: BuildResult
  │
  ├─ 1 ChangeDetector (Git統合)
  │    └─ tracks: List[Feature]
  │
  └─ 1 MarkdownParser
       └─ parses: Document → List[Section]
```

## Data Flow

### doc-init フロー
```
User Input (tool, project_name, author)
  → GeneratorConfig 生成
  → Feature Scanner (.specify/specs/ 探索)
  → Feature[] 取得
  → DocumentStructure 決定 (feature_count基準)
  → Generator.init_project()
  → Jinja2 Template レンダリング
  → ファイル書き込み (conf.py / mkdocs.yml, index.md, etc.)
```

### doc-update フロー
```
ChangeDetector.get_changed_features()
  → Feature[] (変更されたもののみ、またはすべて)
  → for each Feature:
       Document.parse() → Section[]
       → MarkdownParser.parse()
       → Section.to_sphinx_md() / to_mkdocs_md()
       → 機能ドキュメント書き込み
  → index更新 (toctree / nav)
  → Generator.build_docs()
  → BuildResult 返却
```

## Storage and Persistence

**File-Based Storage**:
- すべてのデータはファイルシステムに保存（データベース不使用）
- `.specify/specs/`: 入力データ（spec.md, plan.md, tasks.md）
- `docs/`: 生成されたドキュメント（Markdown）
- `_build/html/` or `site/`: 生成されたHTML（ビルド成果物）
- `.git/`: 変更追跡（Git diff）

**No Caching**:
- キャッシュファイルは管理しない（research.md Decision 2）
- Git diffで変更検出するため、別途キャッシュ不要
- 必要に応じてビルド結果（HTML）を再利用可能

## Performance Considerations

**Incremental Processing**:
- 変更されたFeatureのみを再処理（FR-010）
- Git diffで変更ファイルを検出
- 未変更のドキュメントはスキップ

**Batch Size**:
- 典型的なプロジェクト: 1-20機能
- 最適化目標: 50機能まで
- 50機能以上の場合: 進行状況表示（`tqdm`等）

**No Parallelization** (research.md Decision 9):
- 逐次処理で十分（SC-006: 45秒以内で10機能処理）
- I/Oバウンドのため並列化の恩恵が少ない
- シンプルさを優先

## Validation and Error Handling

**Validation Points**:
1. **プロジェクト検証**: `.specify/`ディレクトリの存在、Git初期化
2. **Feature検証**: spec.mdの存在、有効なMarkdown
3. **ビルド検証**: Sphinx/MkDocsのビルドエラー検出

**Error Handling Strategy** (research.md Decision 8):
```python
class SpecKitDocsError(Exception):
    def __init__(self, message: str, suggestion: str):
        self.message = message
        self.suggestion = suggestion
```

- 明確なエラーメッセージ + 次のステップ提案
- コンテキスト情報をログに含める
- ユーザーが解決できる形式で提示

**Source Requirements**: FR-033, research.md Decision 8

## Implementation Notes

**Python 3.11+ Features**:
- `pathlib.Path`: ファイルパス操作
- `dataclasses`: エンティティ定義（`@dataclass`デコレーター）
- `enum.Enum`: 列挙型定義
- Type hints: すべてのメソッドシグネチャに型ヒント

**Third-Party Libraries**:
- `markdown-it-py`: Markdown解析
- `GitPython`: Git操作
- `Jinja2`: テンプレートレンダリング
- `sphinx`, `myst-parser`: Sphinxドキュメント生成
- `mkdocs`: MkDocsドキュメント生成

**Testing Strategy**:
- ユニットテスト: 各エンティティのメソッド
- 統合テスト: end-to-endフロー（init → update → build）
- コントラクトテスト: CLI入出力、ファイルフォーマット

## Summary

このデータモデルは、spec-kit-docsの実装における中核エンティティを定義しています。主要な設計決定：

1. **Feature中心設計**: spec-kitの機能ディレクトリを中心に構造化
2. **Strategy Pattern**: SphinxGenerator/MkDocsGeneratorで拡張可能
3. **Git統合**: ChangeDetectorでインクリメンタル更新を実現
4. **動的構造決定**: DocumentStructureが機能数に応じて最適な構造を選択
5. **Markdown統一**: Document/Section/MarkdownParserでMarkdown→Markdown変換を最小化

次のフェーズでは、これらのエンティティを使用したCLIインターフェース（contracts/）と基本的な使用方法（quickstart.md）を定義します。
