"""spec.md最小限抽出機能

このモジュールはspec.mdから必要な情報のみを抽出します:
- ユーザーストーリーの目的セクション
- 前提条件セクション
- スコープ境界の「スコープ外」部分

Clarificationsセクション（技術的Q&A）は除外されます。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UserStoryPurpose:
    """単一のユーザーストーリーの「目的」部分を表すエンティティ

    Attributes:
        story_title: ユーザーストーリーの見出しテキスト
                    例: "ユーザーストーリー1: ドキュメント初期化"
        purpose_text: 「**目的**:」から抽出されたテキスト（最小10文字）
        story_number: ユーザーストーリー番号（抽出可能な場合）
                     例: 1, 2, 3
    """

    story_title: str
    purpose_text: str
    story_number: int | None = None

    def __post_init__(self) -> None:
        """バリデーション

        Raises:
            ValueError: purpose_textが空または空白のみの場合
        """
        if not self.purpose_text or not self.purpose_text.strip():
            raise ValueError(
                f"purpose_text must not be empty or whitespace-only: '{self.purpose_text}'"
            )
        if len(self.purpose_text.strip()) < 10:
            raise ValueError(
                f"purpose_text must be at least 10 characters: '{self.purpose_text}' "
                f"(length: {len(self.purpose_text.strip())})"
            )


@dataclass(frozen=True)
class SpecExtractionResult:
    """spec.md最小限抽出の結果を表すエンティティ

    Attributes:
        user_story_purposes: ユーザーストーリーの目的セクションのリスト（最小1件）
        prerequisites: 前提条件セクション全体（Markdown）
        scope_boundaries: スコープ境界の「スコープ外」部分（Markdown）
        total_token_count: 抽出されたコンテンツの総トークン数（0-10000）
        source_file: 抽出元のspec.mdファイルパス
    """

    user_story_purposes: list[UserStoryPurpose]
    prerequisites: str
    scope_boundaries: str
    total_token_count: int
    source_file: Path

    def __post_init__(self) -> None:
        """バリデーション

        Raises:
            ValueError: バリデーションエラー時
        """
        if not self.user_story_purposes:
            raise ValueError("user_story_purposes must contain at least one item")

        if not self.prerequisites or not self.prerequisites.strip():
            raise ValueError(
                f"prerequisites must not be empty or whitespace-only: '{self.prerequisites}'"
            )

        if not self.scope_boundaries or not self.scope_boundaries.strip():
            raise ValueError(
                f"scope_boundaries must not be empty or whitespace-only: '{self.scope_boundaries}'"
            )

        if not (0 <= self.total_token_count <= 10000):
            raise ValueError(
                f"total_token_count must be in range 0-10000: {self.total_token_count}"
            )

    def to_markdown(self) -> str:
        """抽出結果をMarkdown形式で出力

        Returns:
            Markdown形式の文字列
        """
        sections = []

        # ユーザーストーリーの目的
        sections.append("## ユーザーストーリーの目的\n")
        for i, purpose in enumerate(self.user_story_purposes, 1):
            sections.append(f"### {purpose.story_title}\n")
            sections.append(f"{purpose.purpose_text}\n")

        # 前提条件
        sections.append("\n## 前提条件\n")
        sections.append(f"{self.prerequisites}\n")

        # スコープ境界
        sections.append("\n## スコープ境界\n")
        sections.append(f"{self.scope_boundaries}\n")

        # メタデータ
        sections.append("\n---\n")
        sections.append(f"_Extracted from: {self.source_file}_  \n")
        sections.append(f"_Total tokens: {self.total_token_count}_\n")

        return "\n".join(sections)


def extract_spec_minimal(spec_file: Path) -> SpecExtractionResult:
    """spec.mdから最小限のコンテンツを抽出してLLM変換用に準備

    以下を抽出します:
    - ユーザーストーリーの「目的」セクション
    - 前提条件セクション
    - スコープ境界（「スコープ外」部分）

    Args:
        spec_file: spec.mdファイルへのパス

    Returns:
        SpecExtractionResult: 抽出されたコンテンツとトークン数

    Raises:
        SpecKitDocsError: 抽出失敗時または10,000トークン超過時
            - error_type="Missing Required Sections": 必須セクションが見つからない
            - error_type="Token Limit Exceeded": 抽出コンテンツ > 10,000トークン
            - error_type="Content Extraction Error": その他の抽出失敗

    Implementation:
        1. MarkdownParserを使用してspec.mdを解析
        2. ユーザーストーリーの目的を抽出（正規表現: **目的**: パターン）
        3. 前提条件セクションを抽出（## 前提条件 or ## Prerequisites）
        4. スコープ境界を抽出（## スコープ境界 -> **スコープ外**）
        5. トークン数をカウントして10,000未満を検証
        6. SpecExtractionResultを返す
    """
    from speckit_docs.exceptions import SpecKitDocsError
    from speckit_docs.parsers.markdown_parser import MarkdownParser
    from speckit_docs.utils.llm_transform import estimate_token_count

    # 1. spec.mdファイルを読み込む
    if not spec_file.exists():
        raise SpecKitDocsError(
            message=f"spec.md file not found: {spec_file}",
            suggestion=f"Check that the file exists at: {spec_file}",
            file_path=spec_file,
            error_type="Content Extraction Error",
        )

    content = spec_file.read_text(encoding="utf-8")

    # 2. MarkdownParserを使用して解析
    parser = MarkdownParser(enable_myst=False)
    sections = parser.parse(content)

    # 3. ユーザーストーリーの目的を抽出
    user_story_purposes = _extract_user_story_purposes(sections, spec_file)

    # 4. 前提条件セクションを抽出
    prerequisites = _extract_prerequisites(sections, spec_file)

    # 5. スコープ境界を抽出
    scope_boundaries = _extract_scope_boundaries(sections, spec_file)

    # 6. トークン数をカウント
    total_content = "\n".join(
        [p.purpose_text for p in user_story_purposes] + [prerequisites, scope_boundaries]
    )
    total_token_count = estimate_token_count(total_content)

    # 7. トークン数制限を検証
    if total_token_count > 10000:
        raise SpecKitDocsError(
            message=f"Extracted content exceeds 10,000 token limit: {total_token_count} tokens.",
            suggestion="Please reduce spec.md content in User Story Purpose, Prerequisites, or Scope sections.",
            file_path=spec_file,
            error_type="Token Limit Exceeded",
        )

    # 8. SpecExtractionResultを返す
    return SpecExtractionResult(
        user_story_purposes=user_story_purposes,
        prerequisites=prerequisites,
        scope_boundaries=scope_boundaries,
        total_token_count=total_token_count,
        source_file=spec_file,
    )


def _extract_user_story_purposes(sections: list[Any], spec_file: Path) -> list[UserStoryPurpose]:
    """ユーザーストーリーの「目的」セクションを抽出

    Args:
        sections: MarkdownParser.parse()の戻り値
        spec_file: spec.mdファイルパス（エラーメッセージ用）

    Returns:
        UserStoryPurposeのリスト

    Raises:
        SpecKitDocsError: ユーザーストーリーが見つからない、または目的が空の場合
    """
    import re

    from speckit_docs.exceptions import SpecKitDocsError

    purposes: list[UserStoryPurpose] = []

    def _search_user_stories(sections_list: list[Any]) -> None:
        """ネストされたセクションを再帰的に検索"""
        for section in sections_list:
            # "ユーザーストーリー" or "User Story" を含むセクションを検索
            if ("ユーザーストーリー" in section.title or "User Story" in section.title) and section.level == 3:
                # **目的**: or **Purpose**: パターンを抽出
                purpose_match = re.search(r"\*\*目的\*\*:\s*(.+?)(?=\n\n|\*\*|$)", section.content, re.DOTALL)

                if not purpose_match:
                    # 英語パターンも試す
                    purpose_match = re.search(r"\*\*Purpose\*\*:\s*(.+?)(?=\n\n|\*\*|$)", section.content, re.DOTALL)

                if not purpose_match:
                    raise SpecKitDocsError(
                        message=f"User story '{section.title}' does not contain '**目的**:' or '**Purpose:**' section.",
                        suggestion="Check that each user story has a '**目的**:' (Purpose) section.",
                        file_path=spec_file,
                        error_type="Content Extraction Error",
                    )

                purpose_text = purpose_match.group(1).strip()

                if not purpose_text or len(purpose_text) < 10:
                    raise SpecKitDocsError(
                        message=f"User story '{section.title}' has empty or too short purpose: '{purpose_text}'",
                        suggestion="Ensure each user story has a meaningful purpose (at least 10 characters).",
                        file_path=spec_file,
                        error_type="Content Extraction Error",
                    )

                # ユーザーストーリー番号を抽出（オプショナル）
                story_number_match = re.search(r"(\d+)", section.title)
                story_number = int(story_number_match.group(1)) if story_number_match else None

                purposes.append(
                    UserStoryPurpose(
                        story_title=section.title,
                        purpose_text=purpose_text,
                        story_number=story_number,
                    )
                )

            # サブセクションも再帰的に検索
            if hasattr(section, 'subsections') and section.subsections:
                _search_user_stories(section.subsections)

    _search_user_stories(sections)

    if not purposes:
        raise SpecKitDocsError(
            message=f"{spec_file} does not contain any User Story sections (### ユーザーストーリーN: ...).",
            suggestion="Check that spec.md follows the recommended structure with User Stories.",
            file_path=spec_file,
            error_type="Missing Required Sections",
        )

    return purposes


def _extract_prerequisites(sections: list[Any], spec_file: Path) -> str:
    """前提条件セクション全体を抽出

    Args:
        sections: MarkdownParser.parse()の戻り値
        spec_file: spec.mdファイルパス（エラーメッセージ用）

    Returns:
        前提条件セクションのMarkdown文字列

    Raises:
        SpecKitDocsError: 前提条件セクションが見つからない場合
    """
    from speckit_docs.exceptions import SpecKitDocsError

    def _search_prerequisites(sections_list: list[Any]) -> str | None:
        """ネストされたセクションを再帰的に検索"""
        for section in sections_list:
            if ("前提条件" in section.title or "Prerequisites" in section.title) and section.level == 2:
                prerequisites: str = str(section.content).strip()

                # contentが空の場合、サブセクションから内容を収集
                if not prerequisites or len(prerequisites) < 20:
                    if hasattr(section, 'subsections') and section.subsections:
                        subsection_contents: list[str] = []
                        for subsec in section.subsections:
                            if subsec.content.strip():
                                subsection_contents.append(subsec.content.strip())

                        if subsection_contents:
                            prerequisites = "\n\n".join(subsection_contents)
                        else:
                            raise SpecKitDocsError(
                                message=f"Prerequisites section and its subsections are empty or too short: '{prerequisites}'",
                                suggestion="Ensure the Prerequisites section has meaningful content (at least 20 characters).",
                                file_path=spec_file,
                                error_type="Content Extraction Error",
                            )
                    else:
                        raise SpecKitDocsError(
                            message=f"Prerequisites section is empty or too short: '{prerequisites}'",
                            suggestion="Ensure the Prerequisites section has meaningful content (at least 20 characters).",
                            file_path=spec_file,
                            error_type="Content Extraction Error",
                        )

                return prerequisites

            # サブセクションも再帰的に検索
            if hasattr(section, 'subsections') and section.subsections:
                result: str | None = _search_prerequisites(section.subsections)
                if result:
                    return result

        return None

    result = _search_prerequisites(sections)

    if not result:
        raise SpecKitDocsError(
            message=f"{spec_file} does not contain expected sections: Missing '## 前提条件' or '## Prerequisites'.",
            suggestion="Check that spec.md follows the recommended structure (User Stories, Prerequisites, Scope).",
            file_path=spec_file,
            error_type="Missing Required Sections",
        )

    return result


def _extract_scope_boundaries(sections: list[Any], spec_file: Path) -> str:
    """スコープ境界の「スコープ外」部分を抽出

    Args:
        sections: MarkdownParser.parse()の戻り値
        spec_file: spec.mdファイルパス（エラーメッセージ用）

    Returns:
        スコープ外セクションのMarkdown文字列

    Raises:
        SpecKitDocsError: スコープ境界セクションが見つからない場合
    """
    import re

    from speckit_docs.exceptions import SpecKitDocsError

    def _search_scope_boundaries(sections_list: list[Any]) -> str | None:
        """ネストされたセクションを再帰的に検索"""
        for section in sections_list:
            if ("スコープ境界" in section.title or "Scope" in section.title) and section.level == 2:
                # サブセクションから「スコープ外」を検索
                if hasattr(section, 'subsections') and section.subsections:
                    for subsection in section.subsections:
                        if ("スコープ外" in subsection.title or "Out of Scope" in subsection.title):
                            scope_boundaries: str = str(subsection.content).strip()

                            if not scope_boundaries or len(scope_boundaries) < 20:
                                raise SpecKitDocsError(
                                    message=f"Scope Boundaries (Out of Scope) is empty or too short: '{scope_boundaries}'",
                                    suggestion="Ensure the Out of Scope section has meaningful content (at least 20 characters).",
                                    file_path=spec_file,
                                    error_type="Content Extraction Error",
                                )

                            return scope_boundaries

                # サブセクションが見つからない場合、section.contentから抽出を試みる
                out_of_scope_match = re.search(
                    r"\*\*スコープ外.*?\*\*[:\s]*(.+?)(?=\n##|\Z)", section.content, re.DOTALL | re.IGNORECASE
                )

                if not out_of_scope_match:
                    # 英語パターンも試す
                    out_of_scope_match = re.search(
                        r"\*\*Out of Scope.*?\*\*[:\s]*(.+?)(?=\n##|\Z)", section.content, re.DOTALL | re.IGNORECASE
                    )

                if out_of_scope_match:
                    scope_boundaries = out_of_scope_match.group(1).strip()

                    if not scope_boundaries or len(scope_boundaries) < 20:
                        raise SpecKitDocsError(
                            message=f"Scope Boundaries (Out of Scope) is empty or too short: '{scope_boundaries}'",
                            suggestion="Ensure the Out of Scope section has meaningful content (at least 20 characters).",
                            file_path=spec_file,
                            error_type="Content Extraction Error",
                        )

                    return scope_boundaries

                # どちらのパターンも見つからない場合はエラー
                raise SpecKitDocsError(
                    message="Scope Boundaries section does not contain '**スコープ外**' or '**Out of Scope**' subsection.",
                    suggestion="Check that the Scope Boundaries section has an Out of Scope subsection.",
                    file_path=spec_file,
                    error_type="Content Extraction Error",
                )

            # サブセクションも再帰的に検索
            if hasattr(section, 'subsections') and section.subsections:
                result: str | None = _search_scope_boundaries(section.subsections)
                if result:
                    return result

        return None

    result = _search_scope_boundaries(sections)

    if not result:
        raise SpecKitDocsError(
            message=f"{spec_file} does not contain expected sections: Missing '## スコープ境界' or '## Scope Boundaries'.",
            suggestion="Check that spec.md follows the recommended structure with Scope Boundaries section.",
            file_path=spec_file,
            error_type="Missing Required Sections",
        )

    return result
