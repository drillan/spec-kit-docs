# Data Model: spec-kit-docs AI駆動型ドキュメント生成システム

**作成日**: 2025-10-18（初版: 2025-10-17）
**対象**: spec-kit-docs全体のデータモデル
**範囲**: ドキュメント初期化・更新・LLM変換のエンティティと関係

---

## コアエンティティ

### SpecKitProject

spec-kitプロジェクトを表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `root_dir` | `Path` | プロジェクトルートディレクトリ | 必須、`.specify/`が存在すること |
| `specs_dir` | `Path` | `specs/`ディレクトリパス | 必須、存在すること |
| `features` | `list[Feature]` | 機能リスト | 任意 |
| `doc_tool` | `DocTool \| None` | 選択されたドキュメントツール | 任意（初期化後にセット） |

**ライフサイクル**:
1. `speckit-docs install`で`.specify/`と`.claude/commands/`を確認
2. `/speckit.doc-init`で`doc_tool`をセット
3. `/speckit.doc-update`で`features`を読み込み

**バリデーション**:
- `root_dir`に`.specify/`ディレクトリが存在すること
- `specs_dir`がルート直下の`specs/`であること（`.specify/specs/`ではない）

---

### Feature

単一の機能仕様を表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `feature_id` | `str` | 機能ID（例: `001-draft-init-spec`） | 必須、`###-*`形式 |
| `feature_dir` | `Path` | 機能ディレクトリパス（例: `specs/001-*/`） | 必須、存在すること |
| `spec_file` | `Path \| None` | spec.mdファイルパス | 任意 |
| `plan_file` | `Path \| None` | plan.mdファイルパス | 任意 |
| `tasks_file` | `Path \| None` | tasks.mdファイルパス | 任意 |
| `readme_file` | `Path \| None` | README.mdファイルパス | 任意 |
| `quickstart_file` | `Path \| None` | QUICKSTART.mdファイルパス | 任意 |
| `contracts_dir` | `Path \| None` | contracts/ディレクトリパス | 任意 |
| `status` | `FeatureStatus` | 実装ステータス | 必須 |

**ライフサイクル**:
1. `specs/`ディレクトリをスキャンして生成
2. Git diff（`--quick`モード）で変更検出
3. LLM変換ワークフローに渡される

**バリデーション**:
- `feature_id`は3桁の数字で始まること（`###-*`形式）
- `spec_file`は少なくとも1つのファイルが存在すること（推奨）

---

### FeatureStatus

機能の実装ステータスを表す列挙型。

**値**:
- `implemented`: mainブランチにマージ済み
- `in_progress`: ブランチとして存在（未マージ）
- `planned`: ブランチなし（仕様のみ存在）

**使用箇所**:
- Git リポジトリの状態から自動判定（FR-030、P3機能）
- MVP範囲外（将来実装）

---

### BaseGenerator

ドキュメントジェネレーターの抽象ベースクラス。

**メソッド**:

```python
class BaseGenerator(ABC):
    @abstractmethod
    def initialize(
        self,
        project_name: str,
        author: str,
        version: str,
        language: str
    ) -> None:
        """ドキュメントプロジェクトの初期化と設定ファイル生成"""
        ...

    @abstractmethod
    def generate_feature_page(
        self,
        feature: Feature,
        transformed_content: str
    ) -> None:
        """単一機能のページ生成"""
        ...

    @abstractmethod
    def update_navigation(self, features: list[Feature]) -> None:
        """目次（toctree/nav）の更新"""
        ...

    @abstractmethod
    def validate(self) -> bool:
        """ビルド前検証"""
        ...
```

**実装クラス**:
- `SphinxGenerator` (`src/speckit_docs/generators/sphinx.py`)
- `MkDocsGenerator` (`src/speckit_docs/generators/mkdocs.py`)

**ライフサイクル**:
1. `/speckit.doc-init`で`initialize()`呼び出し
2. `/speckit.doc-update`で各機能に対して`generate_feature_page()`呼び出し
3. すべてのページ生成後、`update_navigation()`呼び出し
4. `validate()`でビルド前検証

---

### DocTool

ドキュメントツールの種類を表す列挙型。

**値**:
- `sphinx`: Sphinx 7.0+ with myst-parser
- `mkdocs`: MkDocs 1.5+

**使用箇所**:
- `/speckit.doc-init`でユーザーが選択
- `BaseGenerator`の実装クラスを決定

---

## LLM変換関連エンティティ

### SpecExtractionResult

spec.md最小限抽出の結果を表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_story_purposes` | `list[UserStoryPurpose]` | ユーザーストーリーの目的セクションのリスト | 必須、最小1件 |
| `prerequisites` | `str` | 前提条件セクション全体（Markdown） | 必須、空文字列禁止 |
| `scope_boundaries` | `str` | スコープ境界の「スコープ外」部分（Markdown） | 必須、空文字列禁止 |
| `total_token_count` | `int` | 抽出されたコンテンツの総トークン数 | 必須、0-10000の範囲 |
| `source_file` | `Path` | 抽出元のspec.mdファイルパス | 必須 |

**ライフサイクル**:
1. `extract_spec_minimal()`関数で生成
2. LLM変換ワークフローに渡される
3. 変換後は破棄（永続化しない）

**関係**:
- `UserStoryPurpose`エンティティを1個以上含む

---

### UserStoryPurpose

単一のユーザーストーリーの「目的」部分を表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `story_title` | `str` | ユーザーストーリーの見出しテキスト | 必須、例："ユーザーストーリー1: ドキュメント初期化" |
| `purpose_text` | `str` | 「**目的**:」から抽出されたテキスト | 必須、最小10文字 |
| `story_number` | `int \| None` | ユーザーストーリー番号（抽出可能な場合） | 任意、例：1, 2, 3 |

**ライフサイクル**:
1. `MarkdownParser`で見出しを検出
2. 正規表現で`**目的**:`部分を抽出
3. `SpecExtractionResult`に格納

**バリデーション**:
- `purpose_text`が空文字列または空白のみの場合はエラー
- `story_title`に"ユーザーストーリー"または"User Story"が含まれることを推奨（警告）

---

### Section

既存のエンティティ（`models.py:116-183`）。Markdownセクション構造を表す。

**使用箇所**:
- `MarkdownParser.parse()`メソッドの戻り値
- セクション見出しとコンテンツの抽出に使用

**主要属性**（既存）:
- `title: str` - セクション見出し
- `level: int` - 見出しレベル（2 for ##, 3 for ###）
- `content: str` - セクション本文
- `subsections: list[Section]` - ネストされたサブセクション

**関係**:
- `extract_spec_minimal()`で`MarkdownParser.parse()`から取得
- ユーザーストーリー、前提条件、スコープ境界の識別に使用

---

## 関数シグネチャ

### extract_spec_minimal

```python
def extract_spec_minimal(spec_file: Path) -> SpecExtractionResult:
    """Extract minimal content from spec.md for LLM transformation.
    
    Extracts:
    - User story "Purpose" sections
    - Prerequisites section
    - Scope boundaries (Out of Scope)
    
    Args:
        spec_file: Path to spec.md file
    
    Returns:
        SpecExtractionResult: Extracted content with token count
    
    Raises:
        SpecKitDocsError: If extraction fails or content exceeds 10,000 tokens
            - error_type="Missing Required Sections": Required sections not found
            - error_type="Token Limit Exceeded": Extracted content > 10,000 tokens
            - error_type="Content Extraction Error": Other extraction failures
    
    Implementation:
        1. Parse spec.md using MarkdownParser
        2. Extract user story purposes (regex: **目的**: pattern)
        3. Extract prerequisites section (## 前提条件 or ## Prerequisites)
        4. Extract scope boundaries (## スコープ境界 -> **スコープ外**)
        5. Count tokens and validate < 10,000
        6. Return SpecExtractionResult
    """
```

### estimate_token_count

既存の関数（`llm_transform.py:81-101`）。トークン数を推定する。

```python
def estimate_token_count(text: str) -> int:
    """Estimate token count for text.
    
    Args:
        text: Text to estimate
    
    Returns:
        Estimated token count (characters / 4)
    """
```

---

## データフロー

```
spec.md (input)
    ↓
MarkdownParser.parse()
    ↓
List[Section] (見出し構造)
    ↓
extract_spec_minimal() 
    ├─ ユーザーストーリー検出 → List[UserStoryPurpose]
    ├─ 前提条件検出 → str (Markdown)
    └─ スコープ境界検出 → str (Markdown)
    ↓
SpecExtractionResult
    ├─ total_token_count < 10,000 (検証)
    └─ to_markdown() → str
    ↓
LLM変換ワークフロー (Claude API)
    ↓
transformed_content (output)
```

---

## バリデーションルール

### 1. 必須セクションの存在チェック

- ユーザーストーリーの目的: 最低1件存在すること
- 前提条件セクション: `## 前提条件`または`## Prerequisites`が存在すること
- スコープ境界セクション: `## スコープ境界`が存在すること

**エラー**: いずれかが欠如している場合、`SpecKitDocsError`（error_type="Missing Required Sections"）

### 2. トークン数制限

- 抽出後の総トークン数: 最大10,000トークン（FR-038a）
- 推奨: 約4,500トークン

**エラー**: 10,000トークン超過時、`SpecKitDocsError`（error_type="Token Limit Exceeded"）

### 3. コンテンツの最小長

- ユーザーストーリーの目的: 最低10文字
- 前提条件: 最低20文字
- スコープ境界: 最低20文字

**エラー**: 空文字列または極端に短い場合、警告またはエラー

---

## エラーハンドリング（C002準拠）

すべてのエラーは`SpecKitDocsError`として発生し、以下の情報を含む：

```python
@dataclass(frozen=True)
class SpecKitDocsError(Exception):
    message: str          # エラーの詳細
    suggestion: str       # ユーザーへの推奨アクション
    file_path: Path       # エラー発生元のファイルパス
    error_type: str       # エラーの種類
```

**例1: 必須セクション欠如**
```python
SpecKitDocsError(
    message="specs/001-draft-init-spec/spec.md does not contain expected sections: Missing '## 前提条件'.",
    suggestion="Check that spec.md follows the recommended structure (User Stories, Prerequisites, Scope).",
    file_path=Path("specs/001-draft-init-spec/spec.md"),
    error_type="Missing Required Sections"
)
```

**例2: トークン数超過**
```python
SpecKitDocsError(
    message="Extracted content exceeds 10,000 token limit: 12500 tokens.",
    suggestion="Please reduce spec.md content in User Story Purpose, Prerequisites, or Scope sections.",
    file_path=Path("specs/001-draft-init-spec/spec.md"),
    error_type="Token Limit Exceeded"
)
```

---

---

## ドキュメント生成関連エンティティ

### DocumentationSite

生成されたドキュメントサイトの構造を表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `docs_dir` | `Path` | docs/ディレクトリパス | 必須、存在すること |
| `tool` | `DocTool` | 使用されたドキュメントツール | 必須 |
| `pages` | `list[FeaturePage]` | 機能ページリスト | 任意 |
| `navigation` | `Navigation` | ナビゲーション構造 | 必須 |

**ライフサイクル**:
1. `/speckit.doc-init`で初期化
2. `/speckit.doc-update`でページ追加・更新
3. `validate()`でビルド前検証

---

### FeaturePage

単一機能のドキュメントページを表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `feature_id` | `str` | 機能ID | 必須 |
| `file_path` | `Path` | ページファイルパス（例: `docs/draft-init-spec.md`） | 必須 |
| `title` | `str` | ページタイトル | 必須 |
| `content` | `str` | ページ本文（LLM変換済みコンテンツ） | 必須 |
| `source_link` | `str` | 元のspec.mdへのリンク | 必須 |

**ライフサイクル**:
1. `BaseGenerator.generate_feature_page()`で生成
2. Jinja2テンプレートでレンダリング
3. docs/ディレクトリに書き込み

---

### Navigation

ドキュメントサイトのナビゲーション構造を表すエンティティ。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `tool` | `DocTool` | ドキュメントツール | 必須 |
| `structure_type` | `StructureType` | フラットまたは包括的 | 必須 |
| `entries` | `list[NavEntry]` | ナビゲーションエントリ | 任意 |

**StructureType**:
- `flat`: 5機能以下（シンプルなリスト）
- `comprehensive`: 6機能以上（`features/`、`guides/`、`api/`、`architecture/`）

**ライフサイクル**:
1. `/speckit.doc-init`で`structure_type`を決定（機能数検出）
2. `/speckit.doc-update`で`entries`を更新
3. フラット→包括的への自動移行（機能数が6以上になった場合）

---

## エラーハンドリング関連エンティティ

### SpecKitDocsError

すべてのエラーを表す例外クラス（憲章C002準拠）。

**属性**:

```python
@dataclass(frozen=True)
class SpecKitDocsError(Exception):
    message: str          # エラーの詳細
    suggestion: str       # ユーザーへの推奨アクション
    file_path: Path       # エラー発生元のファイルパス
    error_type: str       # エラーの種類
```

**エラー種類**:
- `"Missing Required Sections"`: spec.mdの必須セクション欠如
- `"Token Limit Exceeded"`: LLM変換対象コンテンツのトークン数超過
- `"LLM Transformation Error"`: LLM変換失敗
- `"Quality Check Failed"`: LLM生成コンテンツの品質チェック不合格
- `"File Not Found"`: 必要なファイルが見つからない
- `"Invalid Project Structure"`: spec-kitプロジェクトではない

**使用箇所**:
- すべてのエラーハンドリング（フォールバック禁止、憲章C002準拠）
- AIエージェント（Claude Code）への構造化されたエラー情報の提供

---

## 実装ファイル

### 新規作成予定

- `src/speckit_docs/models.py` - コアエンティティ（SpecKitProject、Feature等）
- `src/speckit_docs/generators/base.py` - BaseGenerator抽象クラス
- `src/speckit_docs/generators/sphinx.py` - SphinxGenerator実装
- `src/speckit_docs/generators/mkdocs.py` - MkDocsGenerator実装
- `src/speckit_docs/utils/spec_extractor.py` - spec.md最小限抽出ロジック
- `src/speckit_docs/llm_entities.py` - LLM統合エンティティ（Session 2025-10-17追加）

### 既存ファイル（再利用）

- `src/speckit_docs/parsers/markdown_parser.py` - Markdownパーサー
- `src/speckit_docs/exceptions.py` - SpecKitDocsError
- `src/speckit_docs/utils/llm_transform.py` - LLM変換ユーティリティ

---

## エンティティ関係図

```
SpecKitProject
    ├─ features: List[Feature]
    │   ├─ spec_file: Path
    │   ├─ readme_file: Path
    │   └─ quickstart_file: Path
    ├─ doc_tool: DocTool (sphinx | mkdocs)
    └─ DocumentationSite
        ├─ tool: DocTool
        ├─ pages: List[FeaturePage]
        │   ├─ content: str (LLM変換済み)
        │   └─ source_link: str → Feature.spec_file
        └─ navigation: Navigation
            ├─ structure_type: StructureType (flat | comprehensive)
            └─ entries: List[NavEntry]

Feature
    └─ (LLM変換ワークフロー)
        ├─ コンテンツソース選択
        │   ├─ README.md + QUICKSTART.md → 不整合検出 → セクション統合
        │   ├─ README.md のみ → そのまま使用
        │   ├─ QUICKSTART.md のみ → そのまま使用
        │   └─ いずれもなし → spec.md最小限抽出
        │       └─ SpecExtractionResult
        │           ├─ user_story_purposes: List[UserStoryPurpose]
        │           ├─ prerequisites: str
        │           ├─ scope_boundaries: str
        │           └─ total_token_count: int
        ├─ Claude API → LLM変換
        ├─ 品質チェック（FR-038c）
        └─ transformed_content: str → FeaturePage.content

BaseGenerator (抽象クラス)
    ├─ SphinxGenerator → docs/ (Sphinx構造)
    │   ├─ conf.py (Jinja2テンプレート)
    │   ├─ index.md (toctree)
    │   └─ [feature-id].md
    └─ MkDocsGenerator → docs/ (MkDocs構造)
        ├─ mkdocs.yml (Jinja2テンプレート、nav更新)
        └─ [feature-id].md
```

---

## テスト戦略

### 単体テスト

- `tests/unit/models/test_entities.py` - エンティティのバリデーション
- `tests/unit/generators/test_base_generator.py` - BaseGeneratorインターフェース
- `tests/unit/generators/test_sphinx_generator.py` - SphinxGenerator実装
- `tests/unit/generators/test_mkdocs_generator.py` - MkDocsGenerator実装
- `tests/unit/utils/test_spec_extractor.py` - spec.md最小限抽出ロジック

### 統合テスト

- `tests/integration/test_doc_init.py` - ドキュメント初期化（Sphinx/MkDocs両方）
- `tests/integration/test_doc_update.py` - ドキュメント更新（LLM変換含む）
- `tests/integration/test_spec_extraction.py` - spec.md抽出エンドツーエンド

### 契約テスト

- `tests/contract/test_cli_install.py` - `speckit-docs install`コマンド
- `tests/contract/test_cli_commands.py` - `/speckit.doc-init`, `/speckit.doc-update`

---

## データ整合性ルール

### 1. 機能ID一貫性

- `Feature.feature_id`は`specs/`ディレクトリ名と一致すること
- 生成されるページファイル名は`feature_id`から番号を除いた形式（例: `001-draft-init-spec` → `draft-init-spec.md`）

### 2. コンテンツソース優先順位

LLM変換ワークフロー（FR-038）に従った優先順位を維持：
1. README.md + QUICKSTART.md（両方存在）→ 不整合検出 → セクション統合
2. README.mdのみ → そのまま使用
3. QUICKSTART.mdのみ → そのまま使用
4. いずれもなし → spec.md最小限抽出

### 3. トークン制限

- spec.md最小限抽出: 約4,500トークン（推奨）、最大10,000トークン
- README.md/QUICKSTART.md: 1機能あたり最大10,000トークン
- 超過時は明確なエラーで中断（フォールバック禁止）

### 4. エラーハンドリング一貫性

- すべてのエラーは`SpecKitDocsError`として発生
- エラーメッセージには「ファイルパス」「エラー種類」「推奨アクション」を含む
- フォールバック動作は行わない（憲章C002準拠）

---

## Phase 2エンティティ（README/QUICKSTART統合強化）

*Session 2025-10-18追加: FR-038-target, FR-038-classify, FR-038-stats, FR-038-integ-a, FR-038-integ-b対応*

### TargetAudienceResult

ターゲット読者判定結果を表すエンティティ（FR-038-target）。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_path` | `Path` | 判定対象ファイルパス | 必須 |
| `audience_type` | `str` | ターゲット読者タイプ | 必須、"end_user", "developer", "both"のいずれか |
| `confidence` | `float \| None` | 判定の信頼度（0.0-1.0） | 任意 |
| `reasoning` | `str \| None` | LLMの判定理由 | 任意 |

**例**:
```python
TargetAudienceResult(
    file_path=Path("specs/001-draft-init-spec/README.md"),
    audience_type="developer",
    confidence=0.85,
    reasoning="Technical terminology and code examples indicate developer audience"
)
```

---

### SectionClassification

セクション分類結果を表すエンティティ（FR-038-classify）。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_path` | `Path` | セクションが属するファイルパス | 必須 |
| `heading` | `str` | セクション見出し（例: "## Installation"） | 必須 |
| `section_type` | `str` | セクションタイプ | 必須、"end_user", "developer", "both"のいずれか |
| `confidence` | `float \| None` | 分類の信頼度（0.0-1.0） | 任意 |

**例**:
```python
SectionClassification(
    file_path=Path("specs/001-draft-init-spec/README.md"),
    heading="## Developer Setup",
    section_type="developer",
    confidence=0.95
)
```

---

### InconsistencyDetectionResult

不整合検出結果を表すエンティティ（FR-038-integ-a）。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `readme_path` | `Path` | README.mdファイルパス | 必須 |
| `quickstart_path` | `Path` | QUICKSTART.mdファイルパス | 必須 |
| `is_consistent` | `bool` | 一貫性があるか | 必須 |
| `inconsistencies` | `list[str]` | 不整合のリスト | 任意（一貫性がない場合は必須） |
| `reasoning` | `str \| None` | LLMの判定理由 | 任意 |

**例（不整合あり）**:
```python
InconsistencyDetectionResult(
    readme_path=Path("specs/001-draft-init-spec/README.md"),
    quickstart_path=Path("specs/001-draft-init-spec/QUICKSTART.md"),
    is_consistent=False,
    inconsistencies=[
        "README.md describes Python project, QUICKSTART.md describes Rust project",
        "Different main features listed"
    ],
    reasoning="Major technology stack mismatch detected"
)
```

**例（一貫性あり）**:
```python
InconsistencyDetectionResult(
    readme_path=Path("specs/001-draft-init-spec/README.md"),
    quickstart_path=Path("specs/001-draft-init-spec/QUICKSTART.md"),
    is_consistent=True,
    inconsistencies=[],
    reasoning="Both files describe the same Python documentation tool with complementary details"
)
```

---

### SectionPriority

セクション優先順位を表すエンティティ（FR-038-integ-b）。

**属性**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_path` | `Path` | セクションが属するファイルパス | 必須 |
| `heading` | `str` | セクション見出し | 必須 |
| `priority` | `int` | 優先順位（1が最優先） | 必須、1以上 |
| `content` | `str` | セクション本文 | 必須 |
| `token_count` | `int` | セクションのトークン数 | 必須、1以上 |

**例**:
```python
SectionPriority(
    file_path=Path("specs/001-draft-init-spec/README.md"),
    heading="## Quick Start",
    priority=1,
    content="To get started with spec-kit-docs...",
    token_count=450
)
```

---

### Phase 2エンティティ関係図

```
README.md ────┐
              │
              ├──> InconsistencyDetectionResult ──> (一貫性あり) ──> Section統合
              │                                  └──> (不整合) ──> Error
QUICKSTART.md ┘

README.md/QUICKSTART.md ──> TargetAudienceResult ──> FR-038-stats統計表示
                        └──> SectionClassification* ──> FR-038-stats統計表示

Section統合 ──> markdown-it-py解析 ──> SectionPriority* ──> トークン制限内で選択 ──> 最終コンテンツ
```

---

### Phase 2データ整合性ルール

#### 5. ターゲット読者判定の一貫性

- `TargetAudienceResult.audience_type`は"end_user", "developer", "both"のみ
- 統計情報（FR-038-stats）には判定結果を含めるが、セクション優先順位には影響しない

#### 6. セクション分類の独立性

- `SectionClassification.section_type`の結果は統計情報のみに使用
- LLMセクション優先順位判定（FR-038-integ-b）とは独立（Session 2025-10-18 Q3, Q5）

#### 7. 不整合検出の厳格性

- `InconsistencyDetectionResult.is_consistent == False`の場合、処理を中断
- 許容される差異: 表記揺れ、詳細度の違い、補完的な情報
- 不整合とみなす: 異なる技術スタック、矛盾する機能説明、異なるプロジェクト目的

#### 8. セクション優先順位のトークン制限

- セクション統合時、`SectionPriority.priority`順にセクションを追加
- 累積トークン数が10,000を超える前にストップ
- 除外されたセクションは警告メッセージで表示
