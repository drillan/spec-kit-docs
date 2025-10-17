# データモデル: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-14 | **Spec**: [spec.md](./spec.md)

このドキュメントでは、spec-kit-docsプロジェクトで使用されるすべての主要エンティティのデータモデルを定義します。すべてのエンティティはPython 3.11+の型ヒントを使用し、不変性（immutability）を保証するために`@dataclass(frozen=True)`で実装されます（CLAUDE.md C006準拠）。

## 設計原則

### 不変性（Immutability）
すべてのエンティティは`@dataclass(frozen=True)`で定義され、一度作成されたインスタンスは変更できません。これにより：
- 予測可能な動作を保証
- 並列処理での安全性を確保
- デバッグとテストを容易化

### 型安全性（Type Safety）
すべてのフィールドは明示的な型ヒントを持ち、mypy互換です。Optionalフィールドは`Optional[T]`または`T | None`（Python 3.10+）で表現されます。

### 検証ルール
`__post_init__`メソッドで不正な状態を検出し、`ValueError`を発生させます。すべてのエラーは`SpecKitDocsError`例外（またはそのサブクラス）として伝播されます。

## エンティティ定義

このセクションでは、spec.md「主要エンティティ」セクション(line 320-330)で定義されたすべてのエンティティを詳細に記述します。

### SpecKitProject

spec-kitプロジェクト全体を表すエンティティです。ルートディレクトリ、`.specify/`設定、`specs/`ディレクトリを含みます。

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SpecKitProject:
    """spec-kitプロジェクトを表すエンティティ"""

    root_dir: Path
    """プロジェクトルートディレクトリの絶対パス"""

    specify_dir: Path
    """.specify/ディレクトリの絶対パス（root_dir/.specify/）"""

    specs_dir: Path
    """specs/ディレクトリの絶対パス（root_dir/specs/）"""

    git_repo: bool
    """Gitリポジトリかどうか"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not self.root_dir.is_dir():
            raise ValueError(f"Project root directory does not exist: {self.root_dir}")
        if not self.specify_dir.is_dir():
            raise ValueError(f".specify/ directory does not exist: {self.specify_dir}")
        if not self.specs_dir.is_dir():
            raise ValueError(f"specs/ directory does not exist: {self.specs_dir}")
```

**関係性**:
- 1つのSpecKitProjectは0個以上のFeatureを持つ（`specs/`ディレクトリ内）
- 1つのSpecKitProjectは0または1つのDocumentationSiteを持つ（`docs/`ディレクトリ）

**検証ルール**:
- `root_dir`、`specify_dir`、`specs_dir`は実際に存在するディレクトリでなければならない（FR-001）
- `specify_dir`は`root_dir/.specify/`と一致しなければならない
- `specs_dir`は`root_dir/specs/`と一致しなければならない

**対応する要件**: FR-001, FR-021a

---

### Feature

単一の機能仕様を表すエンティティです（例：`001-user-auth`）。markdownファイルのコレクション、コントラクト、実装ステータスを含みます。

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum

@dataclass(frozen=True)
class Feature:
    """spec-kit機能仕様を表すエンティティ"""

    id: str
    """機能ID（ディレクトリ名、例：001-user-auth）"""

    number: int
    """機能番号（例：001 → 1）、時系列順を表す"""

    name: str
    """機能名（例：user-auth）、番号を除いた説明的な名前"""

    directory: Path
    """機能ディレクトリの絶対パス（specs/001-user-auth/）"""

    spec_file: Optional[Path]
    """spec.mdファイルの絶対パス（必須）"""

    plan_file: Optional[Path]
    """plan.mdファイルの絶対パス（任意）"""

    tasks_file: Optional[Path]
    """tasks.mdファイルの絶対パス（任意）"""

    data_model_file: Optional[Path]
    """data-model.mdファイルの絶対パス（任意、P2で使用）"""

    contracts_dir: Optional[Path]
    """contracts/ディレクトリの絶対パス（任意、P2で使用）"""

    status: "FeatureStatus"
    """実装ステータス（P3で使用、MVP段階ではPLANNED固定）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not self.directory.is_dir():
            raise ValueError(f"Feature directory does not exist: {self.directory}")
        if self.spec_file is None or not self.spec_file.is_file():
            raise ValueError(f"spec.md is required but not found: {self.directory}/spec.md")
        if self.number <= 0:
            raise ValueError(f"Feature number must be positive: {self.number}")

    @property
    def has_plan(self) -> bool:
        """plan.mdが存在するか"""
        return self.plan_file is not None and self.plan_file.is_file()

    @property
    def has_tasks(self) -> bool:
        """tasks.mdが存在するか"""
        return self.tasks_file is not None and self.tasks_file.is_file()
```

**関係性**:
- 1つのFeatureは1つのSpecKitProjectに属する
- 1つのFeatureは0個以上のEntityを定義する（data-model.md内、P2）
- 1つのFeatureは0個以上のAPIEndpointを定義する（contracts/内、P2）

**検証ルール**:
- `directory`は実際に存在するディレクトリでなければならない
- `spec_file`は必須で、存在しなければならない（FR-011）
- `number`は1以上でなければならない
- `id`は「{number}-{name}」形式（例：001-user-auth）でなければならない

**状態遷移** (P3):
```
PLANNED → IN_PROGRESS → IMPLEMENTED
         ↓
       ABANDONED
```

**対応する要件**: FR-011, FR-024

---

### Entity

data-model.mdファイルから抽出されたデータモデルエンティティを表します（例：User、Task）。フィールド、タイプ、バージョン履歴を含みます（P2機能）。

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class EntityField:
    """エンティティのフィールド定義"""

    name: str
    """フィールド名（例：email）"""

    type_hint: str
    """型ヒント（例：str、int、Optional[str]）"""

    description: Optional[str] = None
    """フィールドの説明（任意）"""

    introduced_in: Optional[int] = None
    """フィールドを導入した機能番号（P2、統合時に設定）"""

    modified_in: Optional[List[int]] = None
    """フィールドを変更した機能番号のリスト（P2、統合時に設定）"""

@dataclass(frozen=True)
class Entity:
    """data-model.mdから抽出されたエンティティ"""

    name: str
    """エンティティ名（例：User、Task）"""

    fields: List[EntityField]
    """エンティティのフィールドリスト"""

    description: Optional[str] = None
    """エンティティの説明（任意）"""

    introduced_in: int
    """エンティティを導入した機能番号"""

    is_enum: bool = False
    """列挙型かどうか"""

    enum_values: Optional[List[str]] = None
    """列挙型の値リスト（is_enum=Trueの場合）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not self.name:
            raise ValueError("Entity name cannot be empty")
        if self.is_enum and not self.enum_values:
            raise ValueError(f"Enum entity {self.name} must have enum_values")
        if not self.is_enum and len(self.fields) == 0:
            raise ValueError(f"Non-enum entity {self.name} must have at least one field")
```

**関係性**:
- 1つのEntityは1つのFeatureで導入される
- 1つのEntityは複数のFeatureで変更される可能性がある（P2の統合機能）
- SynthesisResultは複数のEntityを含む（P2）

**検証ルール**:
- `name`は空文字列ではいけない
- `is_enum=True`の場合、`enum_values`は必須で、1つ以上の値を持つ
- `is_enum=False`の場合、`fields`は1つ以上のフィールドを持つ

**対応する要件**: FR-025（P2）

---

### APIEndpoint

contracts/ディレクトリから抽出されたAPIエンドポイント定義を表します。メソッド、パス、パラメータ、バージョン履歴を含みます（P2機能）。

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class HTTPMethod(Enum):
    """HTTPメソッド"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

@dataclass(frozen=True)
class APIParameter:
    """APIパラメータ定義"""

    name: str
    """パラメータ名"""

    type_hint: str
    """型ヒント（例：str、int）"""

    location: str
    """パラメータの場所（path、query、body、header）"""

    required: bool = True
    """必須かどうか"""

    description: Optional[str] = None
    """パラメータの説明（任意）"""

@dataclass(frozen=True)
class APIEndpoint:
    """contracts/から抽出されたAPIエンドポイント"""

    method: HTTPMethod
    """HTTPメソッド（GET、POST等）"""

    path: str
    """エンドポイントパス（例：/users/{id}）"""

    summary: Optional[str] = None
    """エンドポイントの概要（任意）"""

    parameters: List[APIParameter] = field(default_factory=list)
    """パラメータリスト"""

    request_body: Optional[str] = None
    """リクエストボディの型（任意）"""

    response_type: Optional[str] = None
    """レスポンスの型（任意）"""

    introduced_in: int = 0
    """エンドポイントを導入した機能番号（P2）"""

    modified_in: Optional[List[int]] = None
    """エンドポイントを変更した機能番号のリスト（P2）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not self.path:
            raise ValueError("API endpoint path cannot be empty")
        if not self.path.startswith("/"):
            raise ValueError(f"API endpoint path must start with '/': {self.path}")

    @property
    def endpoint_id(self) -> str:
        """エンドポイントの一意識別子（例：GET /users/{id}）"""
        return f"{self.method.value} {self.path}"
```

**関係性**:
- 1つのAPIEndpointは1つのFeatureで導入される
- 1つのAPIEndpointは複数のFeatureで変更される可能性がある（P2の統合機能）
- SynthesisResultは複数のAPIEndpointを含む（P2）

**検証ルール**:
- `path`は空文字列ではいけない
- `path`は`/`で始まらなければならない
- `method`は有効なHTTPMethodでなければならない

**対応する要件**: FR-026（P2）

---

### DocumentationSite

生成されたドキュメントサイトの構造を表します。ページ、ナビゲーション、アセットを含みます。

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from enum import Enum

class DocToolType(Enum):
    """ドキュメントツールの種類"""
    SPHINX = "sphinx"
    MKDOCS = "mkdocs"

class StructureType(Enum):
    """ドキュメント構造の種類"""
    FLAT = "flat"  # 5機能以下
    COMPREHENSIVE = "comprehensive"  # 6機能以上

@dataclass(frozen=True)
class DocumentationSite:
    """生成されたドキュメントサイト"""

    root_dir: Path
    """ドキュメントルートディレクトリ（例：{project}/docs/）"""

    tool_type: DocToolType
    """使用するドキュメントツール（Sphinx/MkDocs）"""

    structure_type: StructureType
    """ドキュメント構造（フラット/包括的）"""

    project_name: str
    """プロジェクト名"""

    author: Optional[str] = None
    """著者名（Sphinx用）"""

    version: Optional[str] = None
    """バージョン（Sphinx用）"""

    language: str = "ja"
    """言語（Sphinx用、デフォルト：日本語）"""

    site_name: Optional[str] = None
    """サイト名（MkDocs用）"""

    repo_url: Optional[str] = None
    """リポジトリURL（MkDocs用）"""

    feature_pages: List[Path] = field(default_factory=list)
    """生成された機能ページのパスリスト"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not self.root_dir.is_dir():
            raise ValueError(f"Documentation root directory does not exist: {self.root_dir}")
        if not self.project_name:
            raise ValueError("Project name cannot be empty")

        # Sphinx特有の検証
        if self.tool_type == DocToolType.SPHINX:
            conf_py = self.root_dir / "conf.py"
            if not conf_py.is_file():
                raise ValueError(f"Sphinx conf.py not found: {conf_py}")

        # MkDocs特有の検証
        if self.tool_type == DocToolType.MKDOCS:
            mkdocs_yml = self.root_dir / "mkdocs.yml"
            if not mkdocs_yml.is_file():
                raise ValueError(f"MkDocs mkdocs.yml not found: {mkdocs_yml}")

    @property
    def features_dir(self) -> Optional[Path]:
        """機能ページディレクトリ（包括的構造の場合のみ）"""
        if self.structure_type == StructureType.COMPREHENSIVE:
            return self.root_dir / "features"
        return None
```

**関係性**:
- 1つのDocumentationSiteは1つのSpecKitProjectに属する
- 1つのDocumentationSiteは複数のFeatureページを含む

**検証ルール**:
- `root_dir`は実際に存在するディレクトリでなければならない（FR-010）
- `project_name`は空文字列ではいけない
- Sphinxの場合、`conf.py`が存在しなければならない
- MkDocsの場合、`mkdocs.yml`が存在しなければならない

**状態遷移**:
```
FLAT (5機能以下) → COMPREHENSIVE (6機能以上)
```
※ 逆方向の遷移（COMPREHENSIVE → FLAT）は発生しない（FR-019b）

**対応する要件**: FR-005, FR-006, FR-010, FR-019a, FR-019b

---

### Audience

ターゲットオーディエンス（関連するコンテンツフィルタリングルールを含む）を表す列挙型です（P3機能）。

```python
from enum import Enum
from dataclasses import dataclass
from typing import Set

class AudienceType(Enum):
    """ターゲットオーディエンスの種類"""
    END_USER = "enduser"      # エンドユーザー向け（機能と使用法のみ）
    DEVELOPER = "developer"   # 開発者向け（API とアーキテクチャ）
    CONTRIBUTOR = "contributor"  # コントリビューター向け（すべて）

@dataclass(frozen=True)
class Audience:
    """ターゲットオーディエンスの定義（P3）"""

    type: AudienceType
    """オーディエンスの種類"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not isinstance(self.type, AudienceType):
            raise ValueError(f"Invalid audience type: {self.type}")

    @property
    def include_spec(self) -> bool:
        """spec.mdを含めるか"""
        return True  # すべてのオーディエンスで含める

    @property
    def include_plan(self) -> bool:
        """plan.mdを含めるか"""
        return self.type in [AudienceType.DEVELOPER, AudienceType.CONTRIBUTOR]

    @property
    def include_tasks(self) -> bool:
        """tasks.mdを含めるか"""
        return self.type == AudienceType.CONTRIBUTOR

    @property
    def include_data_model(self) -> bool:
        """data-model.mdを含めるか"""
        return self.type in [AudienceType.DEVELOPER, AudienceType.CONTRIBUTOR]

    @property
    def include_contracts(self) -> bool:
        """contracts/を含めるか"""
        return self.type in [AudienceType.DEVELOPER, AudienceType.CONTRIBUTOR]

    @property
    def include_in_progress_features(self) -> bool:
        """進行中の機能を含めるか（FR-029、P3）"""
        return self.type in [AudienceType.DEVELOPER, AudienceType.CONTRIBUTOR]
```

**関係性**:
- Audienceは生成されるドキュメントのフィルタリングルールを定義する（P3）

**検証ルール**:
- `type`は有効なAudienceTypeでなければならない

**対応する要件**: FR-029（P3）

---

### SynthesisResult

機能間でマージした後のエンティティとAPIの統合ビューを表します（P2機能）。

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass(frozen=True)
class SynthesisResult:
    """機能間でマージされた統合ビュー（P2）"""

    entities: Dict[str, Entity]
    """統合されたエンティティ（エンティティ名 → Entity）"""

    api_endpoints: Dict[str, APIEndpoint]
    """統合されたAPIエンドポイント（endpoint_id → APIEndpoint）"""

    conflicts: List[str] = field(default_factory=list)
    """検出された競合のリスト（エラーメッセージ）"""

    breaking_changes: List[str] = field(default_factory=list)
    """検出された破壊的変更のリスト（警告メッセージ）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        # 競合が検出された場合は警告（エラーではない）
        if self.conflicts:
            # ログに警告を出力（実装時にlogging使用）
            pass
```

**関係性**:
- 1つのSynthesisResultは複数のEntityを含む
- 1つのSynthesisResultは複数のAPIEndpointを含む
- 競合や破壊的変更は解決戦略（最新優先）によって処理される（FR-027、P2）

**検証ルール**:
- `entities`と`api_endpoints`は空の辞書でも有効（機能がエンティティやAPIを定義していない場合）
- `conflicts`が存在する場合、ログに警告を出力する

**対応する要件**: FR-025, FR-026, FR-027, FR-028（P2）

---

### FeatureStatus

gitブランチステータスから派生した実装状態を表す列挙型です（P3機能）。

```python
from enum import Enum

class FeatureStatus(Enum):
    """機能の実装ステータス（P3、FR-030）"""

    IMPLEMENTED = "implemented"
    """mainブランチにマージ済み"""

    IN_PROGRESS = "in_progress"
    """機能ブランチとして存在"""

    PLANNED = "planned"
    """ブランチが存在しない（仕様のみ）"""

    ABANDONED = "abandoned"
    """明示的に放棄された（将来の拡張）"""
```

**状態遷移**:
```
PLANNED → IN_PROGRESS → IMPLEMENTED
         ↓
       ABANDONED
```

**検証ルール**:
- gitブランチの状態から自動的に決定される（P3）
- MVP段階ではすべての機能が`PLANNED`固定

**対応する要件**: FR-030（P3）

---

### BaseGenerator

ドキュメントジェネレーターの抽象ベースクラスです。SphinxGeneratorとMkDocsGeneratorがこのインターフェースを実装します。

```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseGenerator(ABC):
    """ドキュメントジェネレータの抽象ベースクラス（Strategy Pattern）"""

    @abstractmethod
    def initialize(
        self,
        project: SpecKitProject,
        doc_site: DocumentationSite,
        force: bool = False
    ) -> None:
        """
        ドキュメントプロジェクトの初期化と設定ファイル生成

        Args:
            project: spec-kitプロジェクト
            doc_site: ドキュメントサイト設定
            force: 既存ディレクトリを上書きするか

        Raises:
            SpecKitDocsError: 初期化失敗時
        """
        pass

    @abstractmethod
    def generate_feature_page(self, feature: Feature) -> Path:
        """
        単一機能のページ生成

        Args:
            feature: 機能エンティティ

        Returns:
            生成されたページファイルの絶対パス

        Raises:
            SpecKitDocsError: ページ生成失敗時
        """
        pass

    @abstractmethod
    def update_navigation(self, feature_pages: List[Path]) -> None:
        """
        目次（toctree/nav）の更新

        Args:
            feature_pages: 生成された機能ページのパスリスト

        Raises:
            SpecKitDocsError: ナビゲーション更新失敗時
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        ビルド前検証

        Returns:
            検証成功ならTrue、失敗ならFalse

        Raises:
            SpecKitDocsError: 検証エラー時
        """
        pass
```

**実装クラス**:
- `SphinxGenerator`: Sphinxドキュメントジェネレータ（MyST Markdown形式）
- `MkDocsGenerator`: MkDocsドキュメントジェネレータ（Markdown形式）

**検証ルール**:
- すべてのメソッドは実装クラスで実装されなければならない
- `initialize()`実行後、`validate()`は`True`を返さなければならない
- すべてのエラーは`SpecKitDocsError`例外として発生させる

**対応する要件**: FR-005, FR-006, FR-013, FR-014（Strategy Pattern、plan.md Decision 3）

---

## 実装ノート

### Python型ヒント
すべてのエンティティはPython 3.11+の型ヒントを使用します：
```python
from typing import Optional, List, Dict
from pathlib import Path

# Optionalフィールド
field_name: Optional[str] = None

# リストフィールド
items: List[str] = field(default_factory=list)

# 辞書フィールド
mapping: Dict[str, int] = field(default_factory=dict)

# Pathフィールド（絶対パス）
file_path: Path
```

### データクラスの不変性
すべてのエンティティは`@dataclass(frozen=True)`で定義され、不変です：
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class MyEntity:
    name: str
    value: int

    def __post_init__(self) -> None:
        # 検証ロジック
        if self.value < 0:
            raise ValueError("value must be non-negative")
```

### エラーハンドリング
すべてのエラーは`SpecKitDocsError`例外として発生させます（FR-035、C002）：
```python
from speckit_docs.exceptions import SpecKitDocsError

class InvalidFeatureError(SpecKitDocsError):
    """機能が無効な場合のエラー"""
    pass

# 使用例
if not feature.spec_file.is_file():
    raise InvalidFeatureError(
        f"spec.md not found: {feature.spec_file}\n"
        f"Error: Missing required file\n"
        f"Action: Create spec.md in {feature.directory}/"
    )
```

エラーメッセージには以下を含めます（C002準拠）：
1. **ファイルパス**: 問題のあるファイルの絶対パス
2. **エラー種類**: 何が問題なのか（Missing required file、Invalid format等）
3. **推奨アクション**: ユーザーが次に何をすべきか

## データモデル図

```
SpecKitProject (1)
    ├── root_dir: Path
    ├── specify_dir: Path
    ├── specs_dir: Path
    ├── git_repo: bool
    └── has many Features (0..*)

Feature (0..*)
    ├── id: str
    ├── number: int
    ├── name: str
    ├── directory: Path
    ├── spec_file: Optional[Path]
    ├── plan_file: Optional[Path]
    ├── tasks_file: Optional[Path]
    ├── data_model_file: Optional[Path] (P2)
    ├── contracts_dir: Optional[Path] (P2)
    ├── status: FeatureStatus (P3)
    ├── has many Entities (0..*) (P2)
    └── has many APIEndpoints (0..*) (P2)

Entity (0..*) (P2)
    ├── name: str
    ├── fields: List[EntityField]
    ├── description: Optional[str]
    ├── introduced_in: int
    ├── is_enum: bool
    └── enum_values: Optional[List[str]]

APIEndpoint (0..*) (P2)
    ├── method: HTTPMethod
    ├── path: str
    ├── summary: Optional[str]
    ├── parameters: List[APIParameter]
    ├── request_body: Optional[str]
    ├── response_type: Optional[str]
    ├── introduced_in: int
    └── modified_in: Optional[List[int]]

DocumentationSite (0..1)
    ├── root_dir: Path
    ├── tool_type: DocToolType
    ├── structure_type: StructureType
    ├── project_name: str
    ├── author: Optional[str]
    ├── version: Optional[str]
    ├── language: str
    ├── site_name: Optional[str]
    ├── repo_url: Optional[str]
    └── feature_pages: List[Path]

BaseGenerator (抽象クラス)
    ├── initialize()
    ├── generate_feature_page()
    ├── update_navigation()
    └── validate()
    ├── implemented by: SphinxGenerator
    └── implemented by: MkDocsGenerator

SynthesisResult (1) (P2)
    ├── entities: Dict[str, Entity]
    ├── api_endpoints: Dict[str, APIEndpoint]
    ├── conflicts: List[str]
    └── breaking_changes: List[str]

Audience (列挙型) (P3)
    ├── END_USER
    ├── DEVELOPER
    └── CONTRIBUTOR

FeatureStatus (列挙型) (P3)
    ├── IMPLEMENTED
    ├── IN_PROGRESS
    ├── PLANNED
    └── ABANDONED
```

---

### DependencyResult (Session 2025-10-15追加)

依存関係自動インストール機能（FR-008b～FR-008e）の結果を表すエンティティです。`handle_dependencies()`関数の戻り値として使用されます。

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass(frozen=True)
class DependencyResult:
    """依存関係インストールの結果を表すエンティティ"""

    status: Literal["installed", "skipped", "failed", "not_needed"]
    """インストール結果のステータス
    - installed: 自動インストール成功
    - skipped: ユーザーが拒否またはインストールをスキップ
    - failed: インストール失敗（条件不満足またはuv addエラー）
    - not_needed: パッケージが既にインストール済み
    """

    message: str
    """ステータスの詳細メッセージ（ユーザーへのフィードバック用）"""

    installed_packages: list[str] = field(default_factory=list)
    """インストールされたパッケージのリスト（status="installed"の場合のみ）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        valid_statuses = ["installed", "skipped", "failed", "not_needed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        if self.status == "installed" and not self.installed_packages:
            raise ValueError("installed_packages must not be empty when status is 'installed'")

        if self.status != "installed" and self.installed_packages:
            raise ValueError(f"installed_packages must be empty when status is '{self.status}'")
```

**関係性**:
- `handle_dependencies()`関数は1つのDependencyResultを返す
- DependencyResultは`doc_init.py`の終了時にログメッセージとして使用される

**検証ルール**:
- `status`は4つの値のいずれかでなければならない
- `status="installed"`の場合、`installed_packages`は空でない
- `status != "installed"`の場合、`installed_packages`は空である

**対応する要件**: FR-008b, FR-008c, FR-008d, FR-008e, SC-002b

**使用例**:
```python
# 成功ケース
DependencyResult(
    status="installed",
    message="インストール成功",
    installed_packages=["sphinx>=7.0", "myst-parser>=2.0"]
)

# 失敗ケース
DependencyResult(
    status="failed",
    message="pyproject.toml不在",
    installed_packages=[]
)

# スキップケース
DependencyResult(
    status="skipped",
    message="ユーザーが拒否",
    installed_packages=[]
)

# 不要ケース
DependencyResult(
    status="not_needed",
    message="すべてのパッケージがインストール済み",
    installed_packages=[]
)
```

---

### PackageManager (Session 2025-10-15追加)

利用可能なパッケージマネージャーの情報を表すエンティティです。代替インストール方法（FR-008d）の表示に使用されます。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PackageManager:
    """パッケージマネージャーを表すエンティティ"""

    name: str
    """パッケージマネージャー名（uv, poetry, pip等）"""

    command: str
    """インストールコマンド（例：uv add sphinx>=7.0 myst-parser>=2.0）"""

    available: bool
    """システムで利用可能かどうか（shutil.which()の結果）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        valid_names = ["uv", "poetry", "pip", "conda"]
        if self.name not in valid_names:
            raise ValueError(f"Invalid package manager: {self.name}. Must be one of {valid_names}")

        if self.available and not self.command:
            raise ValueError("command must not be empty when available is True")
```

**関係性**:
- `detect_package_managers()`関数は複数のPackageManagerを返す
- `show_alternative_methods()`関数はPackageManagerのリストを使用して代替方法を表示

**検証ルール**:
- `name`は`["uv", "poetry", "pip", "conda"]`のいずれかでなければならない
- `available=True`の場合、`command`は空でない

**対応する要件**: FR-008d

**使用例**:
```python
# uv利用可能
PackageManager(
    name="uv",
    command="uv add sphinx>=7.0 myst-parser>=2.0",
    available=True
)

# poetry利用不可
PackageManager(
    name="poetry",
    command="",
    available=False
)
```

---

## エンティティ関係図（更新版）

```
SpecKitProject (1)
    ├── root_dir: Path
    ├── specify_dir: Path
    ├── specs_dir: Path
    ├── git_repo: bool
    └── features: List[Feature] (0..*)

Feature (0..*)
    ├── id: str
    ├── number: int
    ├── name: str
    ├── directory: Path
    ├── spec_file: Optional[Path]
    ├── plan_file: Optional[Path]
    ├── tasks_file: Optional[Path]
    ├── data_model_file: Optional[Path]
    ├── contracts_dir: Optional[Path]
    └── entities: List[Entity] (0..*) (P2)
    └── api_endpoints: List[APIEndpoint] (0..*) (P2)

Entity (0..*) (P2)
    ├── name: str
    ├── description: Optional[str]
    ├── fields: List[EntityField]
    ├── introduced_in: int
    └── modified_in: Optional[List[int]]

EntityField (0..*) (P2)
    ├── name: str
    ├── field_type: str
    ├── is_optional: bool
    ├── description: Optional[str]
    ├── is_enum: bool
    └── enum_values: Optional[List[str]]

APIEndpoint (0..*) (P2)
    ├── method: HTTPMethod
    ├── path: str
    ├── summary: Optional[str]
    ├── parameters: List[APIParameter]
    ├── request_body: Optional[str]
    ├── response_type: Optional[str]
    ├── introduced_in: int
    └── modified_in: Optional[List[int]]

DocumentationSite (0..1)
    ├── root_dir: Path
    ├── tool_type: DocToolType
    ├── structure_type: StructureType
    ├── project_name: str
    ├── author: Optional[str]
    ├── version: Optional[str]
    ├── language: str
    ├── site_name: Optional[str]
    ├── repo_url: Optional[str]
    └── feature_pages: List[Path]

BaseGenerator (抽象クラス)
    ├── initialize()
    ├── generate_feature_page()
    ├── update_navigation()
    └── validate()
    ├── implemented by: SphinxGenerator
    └── implemented by: MkDocsGenerator

SynthesisResult (1) (P2)
    ├── entities: Dict[str, Entity]
    ├── api_endpoints: Dict[str, APIEndpoint]
    ├── conflicts: List[str]
    └── breaking_changes: List[str]

Audience (列挙型) (P3)
    ├── END_USER
    ├── DEVELOPER
    └── CONTRIBUTOR

FeatureStatus (列挙型) (P3)
    ├── IMPLEMENTED
    ├── IN_PROGRESS
    ├── PLANNED
    └── ABANDONED

DependencyResult (1) (Session 2025-10-15追加)
    ├── status: Literal["installed", "skipped", "failed", "not_needed"]
    ├── message: str
    └── installed_packages: list[str]

PackageManager (0..*) (Session 2025-10-15追加)
    ├── name: str
    ├── command: str
    └── available: bool
```

---

## LLM統合エンティティ（Session 2025-10-17追加）

Session 2025-10-17で追加された、README/QUICKSTART統合、不整合検出、セクション優先順位判定、spec.md抽出に関連するエンティティを定義します。

### InconsistencyDetectionResult

README/QUICKSTART不整合検出結果を表すエンティティです。

```python
from dataclasses import dataclass
from typing import List, Literal

@dataclass(frozen=True)
class Inconsistency:
    """不整合項目を表すエンティティ"""

    type: Literal["technology_stack", "features", "purpose"]
    """不整合タイプ"""

    readme_claim: str
    """README.mdの主張"""

    quickstart_claim: str
    """QUICKSTART.mdの主張"""

    severity: Literal["critical", "minor"]
    """重大度"""


@dataclass(frozen=True)
class InconsistencyDetectionResult:
    """README/QUICKSTART不整合検出結果を表すエンティティ"""

    is_consistent: bool
    """整合性があるか"""

    inconsistencies: List[Inconsistency]
    """不整合項目リスト"""

    summary: str
    """分析結果サマリー"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if not self.is_consistent and len(self.inconsistencies) == 0:
            raise ValueError(
                "is_consistent=False but inconsistencies list is empty"
            )
```

### Section

Markdownセクションを表すエンティティです（markdown-it-pyでパース）。

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Section:
    """Markdownセクションを表すエンティティ"""

    file: Literal["README.md", "QUICKSTART.md"]
    """ファイル名"""

    heading: str
    """見出しテキスト（例: "## Installation"）"""

    level: Literal["h2", "h3"]
    """見出しレベル"""

    content: str
    """セクション本文"""

    token_count: int
    """トークン数（概算、文字数/4で計算）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if self.token_count < 0:
            raise ValueError(f"token_count must be non-negative: {self.token_count}")
        if not self.heading.strip():
            raise ValueError("heading must not be empty")
```

### SectionPriorityResult

セクション優先順位判定結果を表すエンティティです。

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class PrioritizedSection:
    """優先順位付きセクションを表すエンティティ"""

    section: Section
    """元となるセクション"""

    priority: int
    """優先順位（1が最高）"""

    reason: str
    """優先順位理由（LLMが提供）"""


@dataclass(frozen=True)
class SectionPriorityResult:
    """セクション優先順位判定結果を表すエンティティ"""

    prioritized_sections: List[PrioritizedSection]
    """優先順位付きセクションリスト（優先順位順）"""

    total_sections: int
    """全セクション数"""

    included_sections: int
    """10,000トークン以内に含まれたセクション数"""

    excluded_sections: List[Section]
    """10,000トークン超過により除外されたセクションリスト"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if self.total_sections != self.included_sections + len(self.excluded_sections):
            raise ValueError(
                f"total_sections ({self.total_sections}) != "
                f"included_sections ({self.included_sections}) + "
                f"excluded_sections ({len(self.excluded_sections)})"
            )
```

### LLMTransformResult

LLM変換結果を表すエンティティです（不整合検出、優先順位判定、spec.md抽出すべてに使用）。

```python
from dataclasses import dataclass
from typing import Literal, Optional

LLMTransformType = Literal[
    "inconsistency_detection",
    "section_priority",
    "spec_md_extraction",
    "readme_only",
    "quickstart_only",
]


@dataclass(frozen=True)
class LLMTransformResult:
    """LLM変換結果を表すエンティティ"""

    transform_type: LLMTransformType
    """変換タイプ"""

    source_content: str
    """元となるコンテンツ（README.md、QUICKSTART.md、spec.md等）"""

    transformed_content: str
    """LLM変換後のコンテンツ"""

    token_count: int
    """変換後コンテンツのトークン数（概算）"""

    inconsistency_result: Optional[InconsistencyDetectionResult] = None
    """不整合検出結果（transform_type="inconsistency_detection"の場合のみ）"""

    section_priority_result: Optional[SectionPriorityResult] = None
    """セクション優先順位判定結果（transform_type="section_priority"の場合のみ）"""

    def __post_init__(self) -> None:
        """検証ルール"""
        if self.token_count > 10000:
            raise ValueError(
                f"transformed_content exceeds 10,000 token limit: {self.token_count}"
            )

        # transform_typeに応じた結果の存在検証
        if self.transform_type == "inconsistency_detection" and self.inconsistency_result is None:
            raise ValueError(
                "inconsistency_result is required when transform_type='inconsistency_detection'"
            )
        if self.transform_type == "section_priority" and self.section_priority_result is None:
            raise ValueError(
                "section_priority_result is required when transform_type='section_priority'"
            )
```

### LLM統合エンティティの使用例

#### 不整合検出フロー

```python
# 1. README.mdとQUICKSTART.mdを読み込む
readme_content = feature.readme_file.read_text()
quickstart_content = feature.quickstart_file.read_text()

# 2. LLM APIで不整合検出
llm_client = get_anthropic_client()
response = llm_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{"role": "user", "content": INCONSISTENCY_DETECTION_PROMPT.format(
        readme_content=readme_content,
        quickstart_content=quickstart_content
    )}],
    timeout=30
)

# 3. レスポンスをパースしてInconsistencyDetectionResultを作成
result_json = json.loads(response.content[0].text)
detection_result = InconsistencyDetectionResult(
    is_consistent=result_json["is_consistent"],
    inconsistencies=[
        Inconsistency(**item) for item in result_json["inconsistencies"]
    ],
    summary=result_json["summary"]
)

# 4. 不整合がある場合はエラーで中断
if not detection_result.is_consistent:
    raise SpecKitDocsError(
        f"Inconsistency detected between README.md and QUICKSTART.md:\n"
        f"{detection_result.summary}\n"
        f"Critical inconsistencies: {len([i for i in detection_result.inconsistencies if i.severity == 'critical'])}"
    )
```

#### セクション優先順位判定フロー

```python
# 1. markdown-it-pyで両方のファイルをセクション単位でパース
from markdown_it import MarkdownIt

def parse_sections(markdown_content: str, filename: str) -> List[Section]:
    md = MarkdownIt()
    tokens = md.parse(markdown_content)
    sections = []
    current_heading = None
    current_content = []

    for token in tokens:
        if token.type == "heading_open" and token.tag in ["h2", "h3"]:
            if current_heading:
                sections.append(Section(
                    file=filename,
                    heading=current_heading,
                    level=token.tag,
                    content="".join(current_content),
                    token_count=len("".join(current_content)) // 4
                ))
            current_heading = token.content
            current_content = []
        elif current_heading:
            current_content.append(token.content or "")

    return sections

readme_sections = parse_sections(readme_content, "README.md")
quickstart_sections = parse_sections(quickstart_content, "QUICKSTART.md")
all_sections = readme_sections + quickstart_sections

# 2. LLM APIでセクション優先順位判定
section_list = [
    {"file": s.file, "heading": s.heading, "content_preview": s.content[:200]}
    for s in all_sections
]
response = llm_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{"role": "user", "content": SECTION_PRIORITY_PROMPT.format(
        sections_list=json.dumps(section_list, ensure_ascii=False)
    )}],
    timeout=45
)

# 3. 優先順位に従ってセクションを追加（10,000トークン以内）
priority_result = SectionPriorityResult(...)
transform_result = LLMTransformResult(
    transform_type="section_priority",
    source_content=readme_content + quickstart_content,
    transformed_content="...",  # 優先順位に従って統合されたコンテンツ
    token_count=9500,
    section_priority_result=priority_result
)
```

---

### エンティティ関係図（Session 2025-10-17更新）

```
Feature
  ├── readme_file: Optional[Path]
  └── quickstart_file: Optional[Path]
      ↓
      ↓ (両方存在する場合)
      ↓
InconsistencyDetectionResult ← (LLM API呼び出し)
  ├── is_consistent: bool
  └── inconsistencies: List[Inconsistency]
      ↓
      ↓ (整合性OK)
      ↓
Section ← (markdown-it-pyでパース)
  ├── file: "README.md" | "QUICKSTART.md"
  ├── heading: str
  └── content: str
      ↓
      ↓ (LLM API呼び出し)
      ↓
SectionPriorityResult
  ├── prioritized_sections: List[PrioritizedSection]
  └── excluded_sections: List[Section]
      ↓
      ↓
LLMTransformResult
  ├── transformed_content: str (統合されたコンテンツ)
  ├── token_count: int (<= 10,000)
  └── section_priority_result: SectionPriorityResult
```

---

## まとめ

このデータモデルは、spec-kit-docsプロジェクトのすべての主要エンティティを定義します。すべてのエンティティは不変（`@dataclass(frozen=True)`）で、型安全（mypy互換）、かつ明確な検証ルールを持ちます。MVP（P1）段階では、SpecKitProject、Feature、DocumentationSite、BaseGenerator、**DependencyResult、PackageManager**（Session 2025-10-15追加）、**InconsistencyDetectionResult、Section、SectionPriorityResult、LLMTransformResult**（Session 2025-10-17追加）が主に使用され、P2以降でEntity、APIEndpoint、SynthesisResult、P3でAudience、FeatureStatusが追加されます。
