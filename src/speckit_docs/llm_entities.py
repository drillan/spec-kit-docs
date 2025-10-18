"""LLM integration entities for speckit-docs.

Session 2025-10-17: Entities for README/QUICKSTART integration,
inconsistency detection, section prioritization, and spec.md extraction.

Session 2025-10-18: Phase 2 entities added (TargetAudienceResult,
SectionClassification, InconsistencyDetectionResultV2, SectionPriority).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# LLM Transform Types
LLMTransformType = Literal[
    "inconsistency_detection",
    "section_priority",
    "spec_md_extraction",
    "readme_only",
    "quickstart_only",
]


@dataclass(frozen=True)
class Inconsistency:
    """Represents an inconsistency item between README and QUICKSTART.

    Attributes:
        type: Inconsistency type (technology_stack, features, or purpose)
        readme_claim: Claim from README.md
        quickstart_claim: Claim from QUICKSTART.md
        severity: Severity level (critical or minor)
    """

    type: Literal["technology_stack", "features", "purpose"]
    readme_claim: str
    quickstart_claim: str
    severity: Literal["critical", "minor"]


@dataclass(frozen=True)
class InconsistencyDetectionResult:
    """README/QUICKSTART inconsistency detection result.

    Attributes:
        is_consistent: Whether the files are consistent
        inconsistencies: List of inconsistency items
        summary: Analysis result summary
    """

    is_consistent: bool
    inconsistencies: list[Inconsistency]
    summary: str

    def __post_init__(self) -> None:
        """Validation rules."""
        if not self.is_consistent and len(self.inconsistencies) == 0:
            raise ValueError("is_consistent=False but inconsistencies list is empty")


@dataclass(frozen=True)
class LLMSection:
    """Represents a Markdown section for LLM transformation.

    Note: This is different from models.Section which is for document parsing.
    This entity is specifically for LLM transform workflow.

    Attributes:
        file: File name (README.md or QUICKSTART.md)
        heading: Heading text (e.g., "## Installation")
        level: Heading level (h2 or h3)
        content: Section body content
        token_count: Token count (estimated as len(content) // 4)
    """

    file: Literal["README.md", "QUICKSTART.md"]
    heading: str
    level: Literal["h2", "h3"]
    content: str
    token_count: int

    def __post_init__(self) -> None:
        """Validation rules."""
        if self.token_count < 0:
            raise ValueError(f"token_count must be non-negative: {self.token_count}")
        if not self.heading.strip():
            raise ValueError("heading must not be empty")


@dataclass(frozen=True)
class PrioritizedSection:
    """Represents a section with priority information.

    Attributes:
        section: Original section
        priority: Priority rank (1 is highest)
        reason: Reason for priority (provided by LLM)
    """

    section: LLMSection
    priority: int
    reason: str


@dataclass(frozen=True)
class SectionPriorityResult:
    """Section prioritization result.

    Attributes:
        prioritized_sections: List of prioritized sections (sorted by priority)
        total_sections: Total number of sections
        included_sections: Number of sections included within 10,000 token limit
        excluded_sections: List of sections excluded due to token limit
    """

    prioritized_sections: list[PrioritizedSection]
    total_sections: int
    included_sections: int
    excluded_sections: list[LLMSection]

    def __post_init__(self) -> None:
        """Validation rules."""
        if self.total_sections != self.included_sections + len(self.excluded_sections):
            raise ValueError(
                f"total_sections ({self.total_sections}) != "
                f"included_sections ({self.included_sections}) + "
                f"excluded_sections ({len(self.excluded_sections)})"
            )


@dataclass(frozen=True)
class LLMTransformResult:
    """LLM transformation result.

    Used for inconsistency detection, section prioritization, and spec.md extraction.

    Attributes:
        transform_type: Type of transformation
        source_content: Original content (README.md, QUICKSTART.md, spec.md, etc.)
        transformed_content: LLM-transformed content
        token_count: Token count of transformed content (estimated)
        inconsistency_result: Inconsistency detection result (only for transform_type="inconsistency_detection")
        section_priority_result: Section prioritization result (only for transform_type="section_priority")
    """

    transform_type: LLMTransformType
    source_content: str
    transformed_content: str
    token_count: int
    inconsistency_result: InconsistencyDetectionResult | None = None
    section_priority_result: SectionPriorityResult | None = None

    def __post_init__(self) -> None:
        """Validation rules."""
        if self.token_count > 10000:
            raise ValueError(
                f"transformed_content exceeds 10,000 token limit: {self.token_count}"
            )

        # Validate result presence based on transform_type
        if (
            self.transform_type == "inconsistency_detection"
            and self.inconsistency_result is None
        ):
            raise ValueError(
                "inconsistency_result is required when transform_type='inconsistency_detection'"
            )
        if (
            self.transform_type == "section_priority"
            and self.section_priority_result is None
        ):
            raise ValueError(
                "section_priority_result is required when transform_type='section_priority'"
            )


# ============================================================================
# Phase 2 Entities (Session 2025-10-18): FR-038-target/classify/stats/integ
# ============================================================================


@dataclass(frozen=True)
class TargetAudienceResult:
    """Target audience detection result (FR-038-target).

    Attributes:
        file_path: Path to the analyzed file
        audience_type: Target audience type
        confidence: Confidence score (0.0-1.0, optional)
        reasoning: LLM reasoning for the decision (optional)
    """

    file_path: Path
    audience_type: Literal["end_user", "developer", "both"]
    confidence: float | None = None
    reasoning: str | None = None

    def __post_init__(self) -> None:
        """Validation rules."""
        if self.audience_type not in ["end_user", "developer", "both"]:
            raise ValueError(
                f"audience_type must be one of ['end_user', 'developer', 'both'], got {self.audience_type}"
            )
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass(frozen=True)
class SectionClassification:
    """Section classification result (FR-038-classify).

    Attributes:
        file_path: Path to the file containing this section
        heading: Section heading (e.g., "## Installation")
        section_type: Section type
        confidence: Confidence score (0.0-1.0, optional)
    """

    file_path: Path
    heading: str
    section_type: Literal["end_user", "developer", "both"]
    confidence: float | None = None

    def __post_init__(self) -> None:
        """Validation rules."""
        if self.section_type not in ["end_user", "developer", "both"]:
            raise ValueError(
                f"section_type must be one of ['end_user', 'developer', 'both'], got {self.section_type}"
            )
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass(frozen=True)
class InconsistencyDetectionResultV2:
    """README/QUICKSTART inconsistency detection result v2 (FR-038-integ-a).

    Note: This is a new version with file paths, different from InconsistencyDetectionResult.

    Attributes:
        readme_path: Path to README.md
        quickstart_path: Path to QUICKSTART.md
        is_consistent: Whether the files are consistent
        inconsistencies: List of inconsistency descriptions
        reasoning: LLM reasoning for the decision (optional)
    """

    readme_path: Path
    quickstart_path: Path
    is_consistent: bool
    inconsistencies: list[str]
    reasoning: str | None = None

    def __post_init__(self) -> None:
        """Validation rules."""
        if not self.is_consistent and len(self.inconsistencies) == 0:
            raise ValueError(
                "inconsistencies list must not be empty when is_consistent is False"
            )


@dataclass(frozen=True)
class SectionPriority:
    """Section priority result (FR-038-integ-b).

    Attributes:
        file_path: Path to the file containing this section
        heading: Section heading
        priority: Priority rank (1 is highest)
        content: Section body content
        token_count: Token count of the section
    """

    file_path: Path
    heading: str
    priority: int
    content: str
    token_count: int

    def __post_init__(self) -> None:
        """Validation rules."""
        if self.priority < 1:
            raise ValueError(f"priority must be >= 1, got {self.priority}")
        if self.token_count < 1:
            raise ValueError(f"token_count must be >= 1, got {self.token_count}")
