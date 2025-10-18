# Data Model: spec.md最小限抽出

**作成日**: 2025-10-17
**対象**: spec.mdから必要な情報のみを抽出する機能のデータモデル

## エンティティ

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

## 実装ファイル

- **新規**: `src/speckit_docs/utils/spec_extractor.py` - 抽出ロジック
- **修正**: `src/speckit_docs/utils/llm_transform.py:446-542` - 既存実装を改善
- **既存**: `src/speckit_docs/parsers/markdown_parser.py` - Markdownパーサー（再利用）
- **既存**: `src/speckit_docs/models.py:116-183` - Sectionクラス（再利用）
- **既存**: `src/speckit_docs/exceptions.py` - SpecKitDocsError（再利用）

---

## テスト戦略

### 単体テスト（`tests/unit/utils/test_spec_extractor.py`）

1. **正常系**: 有効なspec.mdから正しく抽出できること
2. **必須セクション欠如**: エラーが発生すること
3. **トークン数超過**: エラーが発生すること
4. **多言語対応**: 日本語/英語の見出しを検出できること
5. **空コンテンツ**: 空文字列でエラーが発生すること

### 統合テスト（`tests/integration/test_spec_extraction.py`）

1. **実際のspec.md**: 本プロジェクトの`specs/001-draft-init-spec/spec.md`を使用
2. **エンドツーエンド**: 抽出 → LLM変換 → ドキュメント生成の全フロー
3. **エラーシナリオ**: 不正な構造のspec.mdでエラーハンドリングを検証
