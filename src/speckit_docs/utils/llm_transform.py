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
from typing import Literal

try:
    from anthropic import Anthropic, APIError, APITimeoutError, RateLimitError
except ImportError:
    # Anthropic is optional for non-LLM workflows
    Anthropic = None  # type: ignore
    APIError = Exception  # type: ignore
    APITimeoutError = Exception  # type: ignore
    RateLimitError = Exception  # type: ignore

from markdown_it import MarkdownIt

from speckit_docs.exceptions import SpecKitDocsError
from speckit_docs.llm_entities import (
    Inconsistency,
    InconsistencyDetectionResult,
    LLMSection,
    LLMTransformResult,
    PrioritizedSection,
    SectionPriorityResult,
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
            f"No content source found in {feature_dir}. "
            f"Expected README.md, QUICKSTART.md, or spec.md."
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
        current_content = []

        for token in tokens:
            if token.type == "heading_open" and token.tag in ["h2", "h3"]:
                # Save previous section
                if current_heading:
                    content = "".join(current_content)
                    sections.append(
                        LLMSection(
                            file=filename,
                            heading=current_heading,
                            level=current_level,  # type: ignore
                            content=content,
                            token_count=estimate_token_count(content),
                        )
                    )
                # Start new section
                current_level = token.tag  # type: ignore
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
        if current_heading:
            content = "".join(current_content)
            sections.append(
                LLMSection(
                    file=filename,
                    heading=current_heading,
                    level=current_level,  # type: ignore
                    content=content,
                    token_count=estimate_token_count(content),
                )
            )

        return sections

    except Exception as e:
        raise SpecKitDocsError(f"Failed to parse {filename}: {e}")


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
            "anthropic package is not installed. "
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

        result_json = json.loads(response.content[0].text)
        return InconsistencyDetectionResult(
            is_consistent=result_json["is_consistent"],
            inconsistencies=[
                Inconsistency(**item) for item in result_json["inconsistencies"]
            ],
            summary=result_json["summary"],
        )

    except RateLimitError as e:
        raise SpecKitDocsError(
            f"Anthropic API rate limit exceeded: {e}. Please wait and retry later."
        )
    except APITimeoutError as e:
        raise SpecKitDocsError(
            f"Anthropic API timeout after {timeout_seconds} seconds: {e}. "
            f"Please check your network connection."
        )
    except APIError as e:
        raise SpecKitDocsError(
            f"Anthropic API error: {e}. Please check your API key and account status."
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
            "anthropic package is not installed. "
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

        result_json = json.loads(response.content[0].text)

        # Map sections by (file, heading) for lookup
        section_map = {(s.file, s.heading): s for s in sections}
        prioritized = []

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

        return SectionPriorityResult(
            prioritized_sections=prioritized[:included_sections],
            total_sections=len(sections),
            included_sections=included_sections,
            excluded_sections=excluded_sections,
        )

    except RateLimitError as e:
        raise SpecKitDocsError(
            f"Anthropic API rate limit exceeded: {e}. Please wait and retry later."
        )
    except APITimeoutError as e:
        raise SpecKitDocsError(
            f"Anthropic API timeout after {timeout_seconds} seconds: {e}. "
            f"Please check your network connection."
        )
    except APIError as e:
        raise SpecKitDocsError(
            f"Anthropic API error: {e}. Please check your API key and account status."
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
            "anthropic package is not installed. "
            "Install it with: uv add anthropic"
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SpecKitDocsError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please set it to your Anthropic API key. "
            "Example: export ANTHROPIC_API_KEY='sk-...'"
        )
    return Anthropic(api_key=api_key)


# T063: spec.md minimal extraction
def extract_spec_minimal(spec_file: Path) -> str:
    """Extract minimal content from spec.md.

    Extracts:
    - User story "Purpose" sections
    - Prerequisites
    - Scope boundaries

    Estimated token count: ~4,500 tokens

    Args:
        spec_file: spec.md file path

    Returns:
        Extracted minimal content (Markdown)

    Raises:
        SpecKitDocsError: If extraction fails or content exceeds token limit
    """
    try:
        content = spec_file.read_text()
        md = MarkdownIt()
        tokens = md.parse(content)

        extracted_sections = []
        in_user_story = False
        in_purpose = False
        in_prerequisites = False
        in_scope = False
        current_section = []

        for token in tokens:
            # Detect user story sections
            if token.type == "inline" and "ユーザーストーリー" in (token.content or ""):
                in_user_story = True
                current_section = [token.content or ""]
            elif in_user_story and token.type == "inline" and "目的" in (token.content or ""):
                in_purpose = True
                current_section.append(token.content or "")
            elif in_purpose and token.type == "heading_open":
                # Save purpose section
                extracted_sections.append("\n".join(current_section))
                in_purpose = False
                in_user_story = False
                current_section = []
            elif in_purpose:
                current_section.append(token.content or "")

            # Detect prerequisites
            if token.type == "inline" and "前提条件" in (token.content or ""):
                in_prerequisites = True
                current_section = [token.content or ""]
            elif in_prerequisites and token.type == "heading_open":
                extracted_sections.append("\n".join(current_section))
                in_prerequisites = False
                current_section = []
            elif in_prerequisites:
                current_section.append(token.content or "")

            # Detect scope boundaries
            if token.type == "inline" and "スコープ" in (token.content or ""):
                in_scope = True
                current_section = [token.content or ""]
            elif in_scope and token.type == "heading_open":
                extracted_sections.append("\n".join(current_section))
                in_scope = False
                current_section = []
            elif in_scope:
                current_section.append(token.content or "")

        # Save last section if any
        if current_section:
            extracted_sections.append("\n".join(current_section))

        extracted_content = "\n\n".join(extracted_sections)

        # T064: Check token count (should be ~4,500 tokens)
        token_count = estimate_token_count(extracted_content)
        if token_count > 10000:
            raise SpecKitDocsError(
                f"Extracted content exceeds 10,000 token limit: {token_count} tokens. "
                f"Please reduce spec.md content."
            )

        return extracted_content

    except Exception as e:
        raise SpecKitDocsError(f"Failed to extract minimal content from {spec_file}: {e}")


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
        raise SpecKitDocsError(
            f"Inconsistency detected between {readme_file} and {quickstart_file}:\n"
            f"{inconsistency_result.summary}\n"
            f"Critical inconsistencies: {critical_count}\n"
            f"Please resolve inconsistencies and retry."
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
