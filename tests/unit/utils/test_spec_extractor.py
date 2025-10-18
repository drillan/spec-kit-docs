"""spec.md最小限抽出機能の単体テスト

TDDアプローチ（Red-Green-Refactor）に従い、実装前にテストを作成します。
すべてのテストは最初は失敗する必要があります（Red）。
"""

import pytest
from pathlib import Path

from speckit_docs.utils.spec_extractor import (
    extract_spec_minimal,
    SpecExtractionResult,
    UserStoryPurpose,
)
from speckit_docs.exceptions import SpecKitDocsError


# テストフィクスチャのパス
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "sample_specs"
VALID_SPEC = FIXTURES_DIR / "valid_spec.md"
MISSING_SECTION_SPEC = FIXTURES_DIR / "missing_section_spec.md"
MALFORMED_SPEC = FIXTURES_DIR / "malformed_spec.md"


# T007: 正常系テスト
def test_extract_spec_minimal_valid():
    """有効なspec.mdから正しく抽出できる

    期待される動作:
    - ユーザーストーリーの目的が2件抽出される
    - 前提条件セクションが抽出される
    - スコープ境界の「スコープ外」部分が抽出される
    - トークン数が10,000以内
    """
    result = extract_spec_minimal(VALID_SPEC)

    # ユーザーストーリーの目的が2件存在
    assert len(result.user_story_purposes) == 2

    # 1つ目のストーリー
    assert "ドキュメント初期化" in result.user_story_purposes[0].story_title
    assert "単一コマンドでドキュメントプロジェクトを初期化" in result.user_story_purposes[
        0
    ].purpose_text

    # 2つ目のストーリー
    assert "spec.md最小限抽出" in result.user_story_purposes[1].story_title
    assert "必要な情報のみを抽出" in result.user_story_purposes[1].purpose_text

    # 前提条件セクション
    assert "Python 3.11+" in result.prerequisites
    assert "spec-kitプロジェクトが初期化" in result.prerequisites

    # スコープ境界
    assert "Clarificationsセクションの抽出" in result.scope_boundaries
    assert "Success Criteriaセクションの抽出" in result.scope_boundaries

    # トークン数
    assert 0 < result.total_token_count <= 10000

    # ソースファイル
    assert result.source_file == VALID_SPEC


# T008: 必須セクション欠如テスト（前提条件）
def test_extract_spec_minimal_missing_prerequisites():
    """前提条件がない場合にエラーが発生

    期待される動作:
    - SpecKitDocsErrorが発生
    - error_type="Missing Required Sections"
    - エラーメッセージに「前提条件」が含まれる
    """
    with pytest.raises(SpecKitDocsError) as exc_info:
        extract_spec_minimal(MISSING_SECTION_SPEC)

    error = exc_info.value
    assert error.error_type == "Missing Required Sections"
    assert "前提条件" in error.message or "Prerequisites" in error.message
    assert error.file_path == MISSING_SECTION_SPEC


# T009: 必須セクション欠如テスト（ユーザーストーリー）
def test_extract_spec_minimal_missing_user_stories():
    """ユーザーストーリーがない場合にエラーが発生

    期待される動作:
    - SpecKitDocsErrorが発生
    - error_type="Missing Required Sections"
    - エラーメッセージに「ユーザーストーリー」が含まれる
    """
    # ユーザーストーリーセクションがないspec.mdを作成
    no_stories_spec = FIXTURES_DIR / "no_stories_spec.md"

    with pytest.raises(SpecKitDocsError) as exc_info:
        extract_spec_minimal(no_stories_spec)

    error = exc_info.value
    assert error.error_type == "Missing Required Sections"
    assert "ユーザーストーリー" in error.message or "User Story" in error.message


# T010: 必須セクション欠如テスト（スコープ境界）
def test_extract_spec_minimal_missing_scope():
    """スコープ境界がない場合にエラーが発生

    期待される動作:
    - SpecKitDocsErrorが発生
    - error_type="Missing Required Sections"
    - エラーメッセージに「スコープ境界」が含まれる
    """
    # スコープ境界セクションがないspec.mdを作成
    no_scope_spec = FIXTURES_DIR / "no_scope_spec.md"

    with pytest.raises(SpecKitDocsError) as exc_info:
        extract_spec_minimal(no_scope_spec)

    error = exc_info.value
    assert error.error_type == "Missing Required Sections"
    assert "スコープ境界" in error.message or "Scope" in error.message


# T011: トークン数超過テスト
def test_extract_spec_minimal_token_limit_exceeded():
    """抽出後のコンテンツが10,000トークンを超える場合にエラーが発生

    期待される動作:
    - SpecKitDocsErrorが発生
    - error_type="Token Limit Exceeded"
    - エラーメッセージにトークン数が含まれる
    """
    # 非常に大きなspec.mdを作成（10,000トークン超過）
    large_spec = FIXTURES_DIR / "large_spec.md"

    with pytest.raises(SpecKitDocsError) as exc_info:
        extract_spec_minimal(large_spec)

    error = exc_info.value
    assert error.error_type == "Token Limit Exceeded"
    assert "10,000" in error.message or "10000" in error.message
    assert "token" in error.message.lower()


# T012: 多言語対応テスト（日本語）
def test_extract_spec_minimal_japanese_headings():
    """日本語の見出し（「## 前提条件」）を検出

    期待される動作:
    - 日本語の見出しが正しく検出される
    - 前提条件セクションが抽出される
    """
    result = extract_spec_minimal(VALID_SPEC)

    # 日本語の前提条件セクションが抽出される
    assert result.prerequisites
    assert "Python 3.11+" in result.prerequisites


# T013: 多言語対応テスト（英語）
def test_extract_spec_minimal_english_headings():
    """英語の見出し（「## Prerequisites」）を検出

    期待される動作:
    - 英語の見出しが正しく検出される
    - 前提条件セクションが抽出される
    """
    # 英語のspec.mdを作成
    english_spec = FIXTURES_DIR / "english_spec.md"

    result = extract_spec_minimal(english_spec)

    # 英語の前提条件セクションが抽出される
    assert result.prerequisites
    assert len(result.prerequisites) > 20


# T014: 空コンテンツテスト
def test_extract_spec_minimal_empty_purpose():
    """ユーザーストーリーの目的が空の場合にエラーが発生

    期待される動作:
    - SpecKitDocsErrorが発生
    - error_type="Content Extraction Error"
    - エラーメッセージに「empty」が含まれる
    """
    with pytest.raises(SpecKitDocsError) as exc_info:
        extract_spec_minimal(MALFORMED_SPEC)

    error = exc_info.value
    assert error.error_type == "Content Extraction Error"
    assert "empty" in error.message.lower() or "空" in error.message


# T015: トークン数カウントテスト
def test_spec_extraction_result_token_count():
    """SpecExtractionResult.total_token_countが正しく計算される

    期待される動作:
    - トークン数が正の整数
    - トークン数が10,000以内
    - 抽出されたコンテンツのサイズと一致
    """
    result = extract_spec_minimal(VALID_SPEC)

    # トークン数の妥当性チェック
    assert result.total_token_count > 0
    assert result.total_token_count <= 10000

    # 抽出されたコンテンツの総文字数とトークン数の関係
    # （推定: 1トークン ≈ 4文字）
    total_chars = (
        sum(len(p.purpose_text) for p in result.user_story_purposes)
        + len(result.prerequisites)
        + len(result.scope_boundaries)
    )
    estimated_tokens = total_chars / 4

    # トークン数が推定値の50%-150%の範囲内
    assert estimated_tokens * 0.5 <= result.total_token_count <= estimated_tokens * 1.5


# T016: Markdown出力テスト
def test_spec_extraction_result_to_markdown():
    """SpecExtractionResult.to_markdown()が正しいフォーマットで出力

    期待される動作:
    - Markdown形式の文字列が返される
    - ユーザーストーリーの目的セクションが含まれる
    - 前提条件セクションが含まれる
    - スコープ境界セクションが含まれる
    - メタデータ（ソースファイル、トークン数）が含まれる
    """
    result = extract_spec_minimal(VALID_SPEC)
    markdown = result.to_markdown()

    # Markdown形式であることを確認
    assert isinstance(markdown, str)
    assert len(markdown) > 0

    # 各セクションが含まれている
    assert "## ユーザーストーリーの目的" in markdown
    assert "## 前提条件" in markdown
    assert "## スコープ境界" in markdown

    # メタデータが含まれている
    assert "Extracted from:" in markdown
    assert "Total tokens:" in markdown
    assert str(result.total_token_count) in markdown
