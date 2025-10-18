"""LLM transformation utilities for speckit-docs.

Session 2025-10-17: Utilities for README/QUICKSTART integration,
inconsistency detection, section prioritization, and spec.md extraction.

Implementation tasks:
- T062: Content source selection (README.md → QUICKSTART.md → spec.md priority)
- T063: spec.md minimal extraction (using markdown-it-py)
- T064: Token count check (10,000 token limit)
- T065: Inconsistency detection (using LLM API)
- T066: Section-level parsing (using markdown-it-py)
- T067: Section prioritization (using LLM API)
- T068: Section integration (within 10,000 tokens)
"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    from anthropic import Anthropic, APIError, APITimeoutError, RateLimitError
    from anthropic.types import TextBlock
else:
    try:
        from anthropic import (
            Anthropic,
            APIError,
            APITimeoutError,
            RateLimitError,
        )
        from anthropic.types import TextBlock
    except ImportError:
        # Anthropic is optional for non-LLM workflows
        Anthropic = None  # type: ignore[assignment,misc]
        APIError = Exception  # type: ignore[assignment,misc]
        APITimeoutError = Exception  # type: ignore[assignment,misc]
        RateLimitError = Exception  # type: ignore[assignment,misc]
        TextBlock = Any  # type: ignore[assignment,misc]

from markdown_it import MarkdownIt

from speckit_docs.exceptions import SpecKitDocsError
from speckit_docs.llm_entities import (
    Inconsistency,
    InconsistencyDetectionResult,
    LLMSection,
    LLMTransformResult,
    PrioritizedSection,
    SectionClassification,
    SectionPriorityResult,
    TargetAudienceResult,
)


# T064: Token count estimation (characters // 4)
def estimate_token_count(text: str) -> int:
    """Estimate token count for text.

    Args:
        text: Text to estimate token count for

    Returns:
        Estimated token count (len(text) // 4)
    """
    return len(text) // 4


# T062: Content source selection
def select_content_source(feature_dir: Path) -> tuple[Literal["readme", "quickstart", "both", "spec"], Path | tuple[Path, Path]]:
    """Select content source based on priority: README.md → QUICKSTART.md → spec.md.

    Priority:
    1. README.md only → "readme"
    2. QUICKSTART.md only → "quickstart"
    3. Both README.md and QUICKSTART.md → "both"
    4. Neither → spec.md minimal extraction → "spec"

    Args:
        feature_dir: Feature directory path (e.g., specs/001-feature-name/)

    Returns:
        Tuple of (source_type, file_path(s))
        - ("readme", readme_path)
        - ("quickstart", quickstart_path)
        - ("both", (readme_path, quickstart_path))
        - ("spec", spec_path)

    Raises:
        SpecKitDocsError: If no content source is available
    """
    readme_file = feature_dir / "README.md"
    quickstart_file = feature_dir / "QUICKSTART.md"
    spec_file = feature_dir / "spec.md"

    readme_exists = readme_file.is_file()
    quickstart_exists = quickstart_file.is_file()

    if readme_exists and quickstart_exists:
        return ("both", (readme_file, quickstart_file))
    elif readme_exists:
        return ("readme", readme_file)
    elif quickstart_exists:
        return ("quickstart", quickstart_file)
    elif spec_file.is_file():
        return ("spec", spec_file)
    else:
        raise SpecKitDocsError(
            message=f"No content source found in {feature_dir}. Expected README.md, QUICKSTART.md, or spec.md.",
            suggestion=f"Create at least one of README.md, QUICKSTART.md, or spec.md in {feature_dir}.",
            file_path=feature_dir,
            error_type="Missing Content Source"
        )


# T066: Section-level parsing (using markdown-it-py)
def parse_markdown_sections(
    markdown_content: str, filename: Literal["README.md", "QUICKSTART.md"]
) -> list[LLMSection]:
    """Parse Markdown content into sections using markdown-it-py.

    Args:
        markdown_content: Markdown content to parse
        filename: Filename ("README.md" or "QUICKSTART.md")

    Returns:
        List of LLMSection objects

    Raises:
        SpecKitDocsError: If parsing fails
    """
    try:
        md = MarkdownIt()
        tokens = md.parse(markdown_content)
        sections = []
        current_heading = None
        current_level = None
        current_content: list[str] = []

        for token in tokens:
            if token.type == "heading_open" and token.tag in ["h2", "h3"]:
                # Save previous section
                if current_heading and current_level:
                    content = "".join(current_content)
                    sections.append(
                        LLMSection(
                            file=filename,
                            heading=current_heading,
                            level=cast(Literal["h2", "h3"], current_level),
                            content=content,
                            token_count=estimate_token_count(content),
                        )
                    )
                # Start new section
                current_level = token.tag
                current_content = []
            elif token.type == "heading_close":
                pass  # Skip closing tags
            elif token.type == "inline" and current_level is None:
                # This is the heading text before a section starts
                current_heading = token.content
            elif current_level is not None:
                # Accumulate section content
                current_content.append(token.content or "")

        # Save last section
        if current_heading and current_level:
            content = "".join(current_content)
            sections.append(
                LLMSection(
                    file=filename,
                    heading=current_heading,
                    level=cast(Literal["h2", "h3"], current_level),
                    content=content,
                    token_count=estimate_token_count(content),
                )
            )

        return sections

    except Exception as e:
        raise SpecKitDocsError(
            message=f"Failed to parse {filename}: {e}",
            suggestion=f"Check that {filename} is valid Markdown and contains h2/h3 headings.",
            file_path=filename,
            error_type="Markdown Parse Error"
        )


# T065: Inconsistency detection (using LLM API)
INCONSISTENCY_DETECTION_PROMPT = """
You are a technical documentation analyzer. Your task is to detect inconsistencies between two documentation files.

**README.md content:**
{readme_content}

**QUICKSTART.md content:**
{quickstart_content}

**Analysis criteria:**
1. Do these files describe the same project?
2. Are there any critical inconsistencies (technology stack conflicts, contradictory feature descriptions, different project purposes)?

**Acceptable differences:**
- Notation variations (e.g., "Python" vs "python")
- Different levels of detail
- Complementary information

**Unacceptable inconsistencies:**
- Different technology stacks (e.g., "Python project" vs "Rust project")
- Contradictory feature descriptions
- Different project purposes

**Response format (JSON):**
{{
  "is_consistent": true/false,
  "inconsistencies": [
    {{
      "type": "technology_stack" | "features" | "purpose",
      "readme_claim": "...",
      "quickstart_claim": "...",
      "severity": "critical" | "minor"
    }}
  ],
  "summary": "Brief explanation of the analysis result"
}}
"""


# T061: Target audience detection (FR-038-target)
TARGET_AUDIENCE_PROMPT = """
You are a technical documentation analyst. Your task is to determine the target audience of a document.

**Document content:**
{document_content}

**Audience types:**
- "end_user": Non-technical users (customers, product managers, sales teams)
- "developer": Technical users (developers, engineers, DevOps)
- "both": Mixed audience (both technical and non-technical)

**Analysis criteria:**
- Technical terminology density
- Code examples presence
- Assumed background knowledge
- Tone and language complexity

**Response format (JSON):**
{{
  "audience_type": "end_user" | "developer" | "both",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation for the decision"
}}
"""


def detect_target_audience(
    file_path: Path,
    timeout_seconds: int = 30,
) -> TargetAudienceResult:
    """Detect target audience of a document (FR-038-target).

    Args:
        file_path: Path to the document file
        timeout_seconds: Timeout in seconds (default: 30)

    Returns:
        TargetAudienceResult

    Raises:
        SpecKitDocsError: If LLM API call fails or file cannot be read
    """
    if Anthropic is None:
        raise SpecKitDocsError(
            message="anthropic package is not installed.",
            suggestion="Install it with: uv add anthropic",
            file_path=file_path,
            error_type="Missing Dependency",
        )

    # Read file content
    try:
        content = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SpecKitDocsError(
            message=f"File not found: {file_path}",
            suggestion="Check that the file path is correct.",
            file_path=file_path,
            error_type="File Not Found",
        )

    client = get_anthropic_client()

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": TARGET_AUDIENCE_PROMPT.format(document_content=content[:8000]),
                }
            ],
            timeout=timeout_seconds,
        )

        # Extract text from first content block (always TextBlock for our prompts)
        text_block = cast("TextBlock", response.content[0])
        result_json = json.loads(text_block.text)
        return TargetAudienceResult(
            file_path=file_path,
            audience_type=result_json["audience_type"],
            confidence=result_json.get("confidence"),
            reasoning=result_json.get("reasoning"),
        )

    except RateLimitError as e:
        raise SpecKitDocsError(
            message=f"Anthropic API rate limit exceeded: {e}.",
            suggestion="Please wait a few minutes and retry later.",
            file_path=file_path,
            error_type="LLM API call failed",
        )
    except APITimeoutError as e:
        raise SpecKitDocsError(
            message=f"Anthropic API timeout after {timeout_seconds} seconds: {e}.",
            suggestion="Please check your network connection and retry.",
            file_path=file_path,
            error_type="LLM API call failed",
        )
    except APIError as e:
        raise SpecKitDocsError(
            message=f"Anthropic API error: {e}.",
            suggestion="Please check your API key and account status. Set ANTHROPIC_API_KEY environment variable.",
            file_path=file_path,
            error_type="LLM API call failed",
        )


# T062: Section classification (FR-038-classify)
SECTION_CLASSIFICATION_PROMPT = """
You are a technical documentation analyst. Your task is to classify a documentation section.

**Section heading:** {heading}

**Section content:**
{content}

**Section types:**
- "end_user": For non-technical users (installation guides, quick starts, FAQs)
- "developer": For technical users (API references, architecture diagrams, code examples)
- "both": Relevant to both audiences (overview, features, troubleshooting)

**Analysis criteria:**
- Technical depth
- Code examples presence
- Assumed background knowledge
- Practical vs theoretical focus

**Response format (JSON):**
{{
  "section_type": "end_user" | "developer" | "both",
  "confidence": 0.0-1.0
}}
"""


def classify_section(
    file_path: Path,
    heading: str,
    content: str,
    timeout_seconds: int = 30,
) -> SectionClassification:
    """Classify a documentation section (FR-038-classify).

    Args:
        file_path: Path to the file containing this section
        heading: Section heading (e.g., "## Installation")
        content: Section body content
        timeout_seconds: Timeout in seconds (default: 30)

    Returns:
        SectionClassification

    Raises:
        SpecKitDocsError: If LLM API call fails
    """
    if Anthropic is None:
        raise SpecKitDocsError(
            message="anthropic package is not installed.",
            suggestion="Install it with: uv add anthropic",
            file_path=file_path,
            error_type="Missing Dependency",
        )

    client = get_anthropic_client()

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": SECTION_CLASSIFICATION_PROMPT.format(
                        heading=heading,
                        content=content[:4000],
                    ),
                }
            ],
            timeout=timeout_seconds,
        )

        # Extract text from first content block (always TextBlock for our prompts)
        text_block = cast("TextBlock", response.content[0])
        result_json = json.loads(text_block.text)
        return SectionClassification(
            file_path=file_path,
            heading=heading,
            section_type=result_json["section_type"],
            confidence=result_json.get("confidence"),
        )

    except RateLimitError as e:
        raise SpecKitDocsError(
            message=f"Anthropic API rate limit exceeded: {e}.",
            suggestion="Please wait a few minutes and retry later.",
            file_path=file_path,
            error_type="LLM API call failed",
        )
    except APITimeoutError as e:
        raise SpecKitDocsError(
            message=f"Anthropic API timeout after {timeout_seconds} seconds: {e}.",
            suggestion="Please check your network connection and retry.",
            file_path=file_path,
            error_type="LLM API call failed",
        )
    except APIError as e:
        raise SpecKitDocsError(
            message=f"Anthropic API error: {e}.",
            suggestion="Please check your API key and account status. Set ANTHROPIC_API_KEY environment variable.",
            file_path=file_path,
            error_type="LLM API call failed",
        )


def detect_inconsistency(
    readme_content: str,
    quickstart_content: str,
    client: "Anthropic",
    timeout_seconds: int = 30,
) -> InconsistencyDetectionResult:
    """Detect inconsistencies between README.md and QUICKSTART.md.

    Args:
        readme_content: README.md content
        quickstart_content: QUICKSTART.md content
        client: Anthropic API client
        timeout_seconds: Timeout in seconds (default: 30)

    Returns:
        InconsistencyDetectionResult

    Raises:
        SpecKitDocsError: If LLM API call fails
    """
    if Anthropic is None:
        raise SpecKitDocsError(
            "anthropic package is not installed.",
            "Install it with: uv add anthropic"
        )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": INCONSISTENCY_DETECTION_PROMPT.format(
                        readme_content=readme_content,
                        quickstart_content=quickstart_content,
                    ),
                }
            ],
            timeout=timeout_seconds,
        )

        # Extract text from first content block (always TextBlock for our prompts)
        text_block = cast("TextBlock", response.content[0])
        result_json = json.loads(text_block.text)
        return InconsistencyDetectionResult(
            is_consistent=result_json["is_consistent"],
            inconsistencies=[
                Inconsistency(**item) for item in result_json["inconsistencies"]
            ],
            summary=result_json["summary"],
        )

    except RateLimitError as e:
        raise SpecKitDocsError(
            f"Anthropic API rate limit exceeded: {e}.",
            "Please wait a few minutes and retry later."
        )
    except APITimeoutError as e:
        raise SpecKitDocsError(
            f"Anthropic API timeout after {timeout_seconds} seconds: {e}.",
            "Please check your network connection and retry."
        )
    except APIError as e:
        raise SpecKitDocsError(
            f"Anthropic API error: {e}.",
            "Please check your API key and account status. Set ANTHROPIC_API_KEY environment variable."
        )


# T067: Section prioritization (using LLM API)
SECTION_PRIORITY_PROMPT = """
You are a technical documentation organizer. Your task is to prioritize documentation sections for end-user comprehension.

**Sections from README.md and QUICKSTART.md:**
{sections_list}

**Prioritization criteria:**
1. End-user importance (non-technical users should understand the project)
2. Logical reading order (overview → installation → usage → advanced topics)
3. Essential information first

**Response format (JSON):**
{{
  "prioritized_sections": [
    {{
      "file": "README.md",
      "heading": "## Overview",
      "priority": 1,
      "reason": "Essential introduction for all users"
    }},
    {{
      "file": "QUICKSTART.md",
      "heading": "## Quick Start",
      "priority": 2,
      "reason": "Immediate hands-on guide"
    }}
  ]
}}
"""


def prioritize_sections(
    sections: list[LLMSection], client: "Anthropic", timeout_seconds: int = 45
) -> SectionPriorityResult:
    """Prioritize sections using LLM API.

    Args:
        sections: List of sections to prioritize
        client: Anthropic API client
        timeout_seconds: Timeout in seconds (default: 45)

    Returns:
        SectionPriorityResult

    Raises:
        SpecKitDocsError: If LLM API call fails
    """
    if Anthropic is None:
        raise SpecKitDocsError(
            "anthropic package is not installed.",
            "Install it with: uv add anthropic"
        )

    try:
        section_list = [
            {"file": s.file, "heading": s.heading, "content_preview": s.content[:200]}
            for s in sections
        ]

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": SECTION_PRIORITY_PROMPT.format(
                        sections_list=json.dumps(section_list, ensure_ascii=False)
                    ),
                }
            ],
            timeout=timeout_seconds,
        )

        # Extract text from first content block (always TextBlock for our prompts)
        text_block = cast("TextBlock", response.content[0])
        result_json = json.loads(text_block.text)

        # Map sections by (file, heading) for lookup
        section_map = {(s.file, s.heading): s for s in sections}
        prioritized = []
        prioritized_keys = set()

        for item in result_json["prioritized_sections"]:
            key = (item["file"], item["heading"])
            if key in section_map:
                prioritized.append(
                    PrioritizedSection(
                        section=section_map[key],
                        priority=item["priority"],
                        reason=item["reason"],
                    )
                )
                prioritized_keys.add(key)

        # Sort by priority
        prioritized.sort(key=lambda x: x.priority)

        # T068: Section integration (within 10,000 tokens)
        total_tokens = 0
        included_sections = 0
        excluded_sections = []

        for ps in prioritized:
            if total_tokens + ps.section.token_count <= 10000:
                total_tokens += ps.section.token_count
                included_sections += 1
            else:
                excluded_sections.append(ps.section)

        # Add sections not included in prioritized list to excluded
        for section in sections:
            key = (section.file, section.heading)
            if key not in prioritized_keys:
                excluded_sections.append(section)

        return SectionPriorityResult(
            prioritized_sections=prioritized[:included_sections],
            total_sections=len(sections),
            included_sections=included_sections,
            excluded_sections=excluded_sections,
        )

    except RateLimitError as e:
        raise SpecKitDocsError(
            f"Anthropic API rate limit exceeded: {e}.",
            "Please wait a few minutes and retry later."
        )
    except APITimeoutError as e:
        raise SpecKitDocsError(
            f"Anthropic API timeout after {timeout_seconds} seconds: {e}.",
            "Please check your network connection and retry."
        )
    except APIError as e:
        raise SpecKitDocsError(
            f"Anthropic API error: {e}.",
            "Please check your API key and account status. Set ANTHROPIC_API_KEY environment variable."
        )


# Anthropic API client initialization
def get_anthropic_client() -> "Anthropic":
    """Get Anthropic API client.

    Returns:
        Anthropic API client

    Raises:
        SpecKitDocsError: If ANTHROPIC_API_KEY environment variable is not set
    """
    if Anthropic is None:
        raise SpecKitDocsError(
            "anthropic package is not installed.",
            "Install it with: uv add anthropic"
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SpecKitDocsError(
            "ANTHROPIC_API_KEY environment variable is not set.",
            "Set it to your Anthropic API key: export ANTHROPIC_API_KEY='sk-...'"
        )
    return Anthropic(api_key=api_key)


# T063: spec.md minimal extraction
# T030: 古い低レベルトークン処理によるextract_spec_minimal()を削除
# 新しい実装はsrc/speckit_docs/utils/spec_extractor.pyに移動済み
# この関数は spec_extractor.extract_spec_minimal() を使用してください


# T069: LLM transformation quality check
def validate_transformed_content(
    transformed_content: str, source_type: str
) -> tuple[bool, str | None]:
    """Validate LLM-transformed content quality.

    Quality checks:
    1. Not empty string
    2. Minimum 50 characters
    3. No error patterns (e.g., "I cannot", "I'm unable", "error occurred")
    4. Valid Markdown (basic linting)

    Args:
        transformed_content: LLM-transformed content to validate
        source_type: Source type for error messages (e.g., "README.md", "spec.md")

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid

    Raises:
        SpecKitDocsError: If validation fails with critical errors
    """
    # Check 1: Empty string
    if not transformed_content or not transformed_content.strip():
        return (
            False,
            f"LLM変換結果が空文字列です（ソース: {source_type}）。変換を再実行してください。",
        )

    # Check 2: Minimum 50 characters
    if len(transformed_content.strip()) < 50:
        return (
            False,
            f"LLM変換結果が短すぎます（{len(transformed_content.strip())}文字、最小50文字必要）（ソース: {source_type}）。",
        )

    # Check 3: Error patterns
    error_patterns = [
        "I cannot",
        "I'm unable",
        "I can't",
        "error occurred",
        "failed to",
        "申し訳ございません",
        "エラーが発生",
    ]
    content_lower = transformed_content.lower()
    for pattern in error_patterns:
        if pattern.lower() in content_lower:
            return (
                False,
                f"LLM変換結果にエラーパターン「{pattern}」が含まれています（ソース: {source_type}）。変換を再実行してください。",
            )

    # Check 4: Basic Markdown validation
    # Check for unclosed code blocks
    code_block_count = transformed_content.count("```")
    if code_block_count % 2 != 0:
        return (
            False,
            f"Markdownコードブロックが閉じられていません（ソース: {source_type}）。",
        )

    # Check for unclosed inline code
    inline_code_count = transformed_content.count("`")
    # Single backticks should be even (opening and closing)
    # Triple backticks are already checked above
    single_backtick_count = inline_code_count - (code_block_count * 3)
    if single_backtick_count % 2 != 0:
        return (
            False,
            f"Markdownインラインコードが閉じられていません（ソース: {source_type}）。",
        )

    # All checks passed
    return (True, None)


# T065 + T066 + T067 + T068: README/QUICKSTART integration
def integrate_readme_quickstart(
    readme_file: Path, quickstart_file: Path, client: "Anthropic"
) -> LLMTransformResult:
    """Integrate README.md and QUICKSTART.md content.

    Args:
        readme_file: README.md file path
        quickstart_file: QUICKSTART.md file path
        client: Anthropic API client

    Returns:
        LLMTransformResult

    Raises:
        SpecKitDocsError: If inconsistency is detected or LLM API call fails
    """
    # 1. Read files
    readme_content = readme_file.read_text()
    quickstart_content = quickstart_file.read_text()

    # 2. Detect inconsistencies
    inconsistency_result = detect_inconsistency(
        readme_content, quickstart_content, client
    )

    # 3. Raise error if inconsistencies found
    if not inconsistency_result.is_consistent:
        critical_count = len(
            [i for i in inconsistency_result.inconsistencies if i.severity == "critical"]
        )
        inconsistency_details = "\n".join(
            f"  • {i.type}: README says '{i.readme_claim}' but QUICKSTART says '{i.quickstart_claim}'"
            for i in inconsistency_result.inconsistencies[:3]  # Show first 3
        )
        raise SpecKitDocsError(
            f"Inconsistency detected between {readme_file} and {quickstart_file}:\n"
            f"{inconsistency_result.summary}\n"
            f"Critical inconsistencies: {critical_count}\n"
            f"Examples:\n{inconsistency_details}",
            "Resolve inconsistencies in README.md and QUICKSTART.md, then retry."
        )

    # 4. Parse sections
    readme_sections = parse_markdown_sections(readme_content, "README.md")
    quickstart_sections = parse_markdown_sections(quickstart_content, "QUICKSTART.md")
    all_sections = readme_sections + quickstart_sections

    # 5. Prioritize sections
    priority_result = prioritize_sections(all_sections, client)

    # 6. Integrate sections in priority order
    integrated_content = "\n\n".join(
        [
            f"{ps.section.heading}\n\n{ps.section.content}"
            for ps in priority_result.prioritized_sections
        ]
    )

    # 7. Return result
    return LLMTransformResult(
        transform_type="section_priority",
        source_content=readme_content + "\n\n---\n\n" + quickstart_content,
        transformed_content=integrated_content,
        token_count=sum(
            ps.section.token_count for ps in priority_result.prioritized_sections
        ),
        section_priority_result=priority_result,
    )
