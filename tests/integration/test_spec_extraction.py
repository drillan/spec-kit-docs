"""spec.md最小限抽出機能の統合テスト

実際のspec.mdファイルを使用してエンドツーエンドのテストを実行します。
"""

from pathlib import Path

import pytest

from speckit_docs.exceptions import SpecKitDocsError
from speckit_docs.utils.spec_extractor import extract_spec_minimal

# 実際のプロジェクトspec.md
REAL_SPEC = Path(__file__).parent.parent.parent / "specs" / "001-draft-init-spec" / "spec.md"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_specs"
MALFORMED_SPEC = FIXTURES_DIR / "malformed_spec.md"


# T017: エンドツーエンドテスト
def test_extract_from_real_spec():
    """本プロジェクトのspec.mdから抽出し、Clarificationsが除外されることを確認

    期待される動作:
    - spec/001-draft-init-spec/spec.mdから抽出できる
    - ユーザーストーリーの目的が複数件抽出される
    - 前提条件セクションが抽出される
    - スコープ境界セクションが抽出される
    - Clarificationsセクションが除外される（結果に含まれない）
    - トークン数が約4,500トークン程度（10,000トークン以内）
    """
    # spec.mdが存在することを確認
    assert REAL_SPEC.exists(), f"Real spec.md not found: {REAL_SPEC}"

    result = extract_spec_minimal(REAL_SPEC)

    # ユーザーストーリーの目的が存在
    assert len(result.user_story_purposes) > 0

    # 具体的なコンテンツの確認
    # ユーザーストーリー7（LLMによるユーザーフレンドリーなドキュメント生成）が含まれる
    story_titles = [p.story_title for p in result.user_story_purposes]
    assert any("LLM" in title or "ユーザーフレンドリー" in title for title in story_titles)

    # 前提条件セクションが存在
    assert result.prerequisites
    assert len(result.prerequisites) > 20

    # スコープ境界セクションが存在
    assert result.scope_boundaries
    assert len(result.scope_boundaries) > 20

    # Clarificationsセクションが除外されている
    # （結果のMarkdown出力にClarificationsが含まれないことを確認）
    markdown = result.to_markdown()
    assert "Clarifications" not in markdown
    assert "Q1:" not in markdown  # Clarificationsの質問形式
    assert "A1:" not in markdown  # Clarificationsの回答形式

    # トークン数が妥当な範囲（最小限抽出なので500-10,000トークン以内）
    assert 500 <= result.total_token_count <= 10000
    print(f"Extracted token count: {result.total_token_count}")

    # ソースファイルが正しい
    assert result.source_file == REAL_SPEC


# T018: エラーシナリオテスト
def test_extract_from_malformed_spec():
    """不正な構造のspec.mdでエラーハンドリングを検証

    期待される動作:
    - malformed_spec.md（ユーザーストーリーの目的が空）から抽出を試みる
    - SpecKitDocsErrorが発生
    - error_typeが適切に設定される
    - エラーメッセージが明確で実行可能なアクションが含まれる
    - file_pathが正しく設定される
    """
    # malformed_spec.mdが存在することを確認
    assert MALFORMED_SPEC.exists(), f"Malformed spec.md not found: {MALFORMED_SPEC}"

    with pytest.raises(SpecKitDocsError) as exc_info:
        extract_spec_minimal(MALFORMED_SPEC)

    error = exc_info.value

    # エラータイプが設定されている
    assert error.error_type in [
        "Missing Required Sections",
        "Content Extraction Error",
        "Token Limit Exceeded",
    ]

    # エラーメッセージが明確
    assert error.message
    assert len(error.message) > 10

    # 推奨アクション（suggestion）が含まれる
    assert error.suggestion
    assert len(error.suggestion) > 10

    # ファイルパスが正しい
    assert error.file_path == MALFORMED_SPEC

    # エラーメッセージに具体的な情報が含まれる
    # （ファイルパス、エラー内容、推奨アクションのいずれか）
    error_str = str(error)
    assert (
        str(MALFORMED_SPEC) in error_str
        or "empty" in error_str.lower()
        or "欠如" in error_str
        or "missing" in error_str.lower()
    )
