"""Unit tests for LLM entities (T040-T043, T053, T054).

Session 2025-10-17: Tests for README/QUICKSTART integration entities.
Session 2025-10-18: Tests for Phase 2 entities (TargetAudienceResult, etc).
"""

from pathlib import Path

import pytest

from speckit_docs.llm_entities import (
    Inconsistency,
    InconsistencyDetectionResult,
    InconsistencyDetectionResultV2,
    LLMSection,
    LLMTransformResult,
    PrioritizedSection,
    SectionClassification,
    SectionPriority,
    SectionPriorityResult,
    TargetAudienceResult,
)


class TestLLMSection:
    """Tests for LLMSection entity (T053)."""

    def test_llm_section_valid_creation(self):
        """Test valid LLMSection creation."""
        section = LLMSection(
            file="README.md",
            heading="## Installation",
            level="h2",
            content="Install with `pip install foo`",
            token_count=10,
        )

        assert section.file == "README.md"
        assert section.heading == "## Installation"
        assert section.level == "h2"
        assert section.content == "Install with `pip install foo`"
        assert section.token_count == 10

    def test_llm_section_quickstart_h3(self):
        """Test LLMSection with QUICKSTART.md and h3 level."""
        section = LLMSection(
            file="QUICKSTART.md",
            heading="### Quick Start",
            level="h3",
            content="Run the command below",
            token_count=5,
        )

        assert section.file == "QUICKSTART.md"
        assert section.level == "h3"

    def test_llm_section_negative_token_count_error(self):
        """Test LLMSection raises ValueError for negative token_count."""
        with pytest.raises(ValueError, match="token_count must be non-negative"):
            LLMSection(
                file="README.md",
                heading="## Test",
                level="h2",
                content="Test content",
                token_count=-1,
            )

    def test_llm_section_empty_heading_error(self):
        """Test LLMSection raises ValueError for empty heading."""
        with pytest.raises(ValueError, match="heading must not be empty"):
            LLMSection(
                file="README.md",
                heading="   ",  # Whitespace only
                level="h2",
                content="Test content",
                token_count=10,
            )


class TestInconsistency:
    """Tests for Inconsistency entity (T053)."""

    def test_inconsistency_valid_creation(self):
        """Test valid Inconsistency creation."""
        inconsistency = Inconsistency(
            type="technology_stack",
            readme_claim="Uses Python 3.11+",
            quickstart_claim="Requires Python 3.9+",
            severity="critical",
        )

        assert inconsistency.type == "technology_stack"
        assert inconsistency.readme_claim == "Uses Python 3.11+"
        assert inconsistency.quickstart_claim == "Requires Python 3.9+"
        assert inconsistency.severity == "critical"

    def test_inconsistency_minor_severity(self):
        """Test Inconsistency with minor severity."""
        inconsistency = Inconsistency(
            type="features",
            readme_claim="Supports MySQL",
            quickstart_claim="Supports PostgreSQL",
            severity="minor",
        )

        assert inconsistency.severity == "minor"


class TestInconsistencyDetectionResult:
    """Tests for InconsistencyDetectionResult entity (T053)."""

    def test_inconsistency_detection_result_consistent(self):
        """Test InconsistencyDetectionResult for consistent files."""
        result = InconsistencyDetectionResult(
            is_consistent=True,
            inconsistencies=[],
            summary="Files are consistent.",
        )

        assert result.is_consistent is True
        assert len(result.inconsistencies) == 0
        assert result.summary == "Files are consistent."

    def test_inconsistency_detection_result_with_inconsistencies(self):
        """Test InconsistencyDetectionResult with detected inconsistencies."""
        inconsistencies = [
            Inconsistency(
                type="technology_stack",
                readme_claim="Python 3.11+",
                quickstart_claim="Python 3.9+",
                severity="critical",
            ),
            Inconsistency(
                type="features",
                readme_claim="Supports SQLite",
                quickstart_claim="Supports PostgreSQL",
                severity="minor",
            ),
        ]

        result = InconsistencyDetectionResult(
            is_consistent=False,
            inconsistencies=inconsistencies,
            summary="2 inconsistencies detected.",
        )

        assert result.is_consistent is False
        assert len(result.inconsistencies) == 2
        assert result.summary == "2 inconsistencies detected."

    def test_inconsistency_detection_result_validation_error(self):
        """Test InconsistencyDetectionResult raises error for invalid state."""
        with pytest.raises(ValueError, match="is_consistent=False but inconsistencies list is empty"):
            InconsistencyDetectionResult(
                is_consistent=False,
                inconsistencies=[],  # Empty but is_consistent=False
                summary="Inconsistencies found but list is empty.",
            )


class TestPrioritizedSection:
    """Tests for PrioritizedSection entity (T054)."""

    def test_prioritized_section_valid_creation(self):
        """Test valid PrioritizedSection creation."""
        section = LLMSection(
            file="README.md",
            heading="## Installation",
            level="h2",
            content="Install with pip",
            token_count=10,
        )

        prioritized = PrioritizedSection(
            section=section,
            priority=1,
            reason="Essential installation instructions",
        )

        assert prioritized.section == section
        assert prioritized.priority == 1
        assert prioritized.reason == "Essential installation instructions"


class TestSectionPriorityResult:
    """Tests for SectionPriorityResult entity (T054)."""

    def test_section_priority_result_valid_creation(self):
        """Test valid SectionPriorityResult creation."""
        section1 = LLMSection(
            file="README.md",
            heading="## Installation",
            level="h2",
            content="Install with pip",
            token_count=10,
        )
        section2 = LLMSection(
            file="README.md",
            heading="## Usage",
            level="h2",
            content="Run the command",
            token_count=8,
        )
        section3 = LLMSection(
            file="README.md",
            heading="## Advanced",
            level="h2",
            content="Advanced usage",
            token_count=100,
        )

        prioritized_sections = [
            PrioritizedSection(section=section1, priority=1, reason="Essential"),
            PrioritizedSection(section=section2, priority=2, reason="Important"),
        ]

        result = SectionPriorityResult(
            prioritized_sections=prioritized_sections,
            total_sections=3,
            included_sections=2,
            excluded_sections=[section3],
        )

        assert len(result.prioritized_sections) == 2
        assert result.total_sections == 3
        assert result.included_sections == 2
        assert len(result.excluded_sections) == 1

    def test_section_priority_result_validation_error(self):
        """Test SectionPriorityResult raises error for inconsistent counts."""
        section1 = LLMSection(
            file="README.md",
            heading="## Test",
            level="h2",
            content="Test",
            token_count=10,
        )

        prioritized_sections = [
            PrioritizedSection(section=section1, priority=1, reason="Test"),
        ]

        with pytest.raises(ValueError, match="total_sections .* != included_sections"):
            SectionPriorityResult(
                prioritized_sections=prioritized_sections,
                total_sections=5,  # Inconsistent
                included_sections=1,
                excluded_sections=[],  # Should be 4 to match total_sections
            )


class TestLLMTransformResult:
    """Tests for LLMTransformResult entity (T054)."""

    def test_llm_transform_result_readme_only(self):
        """Test LLMTransformResult for readme_only transform type."""
        result = LLMTransformResult(
            transform_type="readme_only",
            source_content="# Original README",
            transformed_content="# Transformed Content",
            token_count=100,
        )

        assert result.transform_type == "readme_only"
        assert result.source_content == "# Original README"
        assert result.transformed_content == "# Transformed Content"
        assert result.token_count == 100
        assert result.inconsistency_result is None
        assert result.section_priority_result is None

    def test_llm_transform_result_spec_md_extraction(self):
        """Test LLMTransformResult for spec_md_extraction transform type."""
        result = LLMTransformResult(
            transform_type="spec_md_extraction",
            source_content="# Original spec.md",
            transformed_content="# Extracted spec content",
            token_count=4500,
        )

        assert result.transform_type == "spec_md_extraction"
        assert result.token_count == 4500

    def test_llm_transform_result_inconsistency_detection(self):
        """Test LLMTransformResult for inconsistency_detection transform type."""
        detection_result = InconsistencyDetectionResult(
            is_consistent=True,
            inconsistencies=[],
            summary="Files are consistent.",
        )

        result = LLMTransformResult(
            transform_type="inconsistency_detection",
            source_content="README + QUICKSTART",
            transformed_content="Merged content",
            token_count=200,
            inconsistency_result=detection_result,
        )

        assert result.transform_type == "inconsistency_detection"
        assert result.inconsistency_result is not None
        assert result.inconsistency_result.is_consistent is True

    def test_llm_transform_result_section_priority(self):
        """Test LLMTransformResult for section_priority transform type."""
        section = LLMSection(
            file="README.md",
            heading="## Test",
            level="h2",
            content="Test content",
            token_count=10,
        )

        priority_result = SectionPriorityResult(
            prioritized_sections=[
                PrioritizedSection(section=section, priority=1, reason="Essential")
            ],
            total_sections=1,
            included_sections=1,
            excluded_sections=[],
        )

        result = LLMTransformResult(
            transform_type="section_priority",
            source_content="Original sections",
            transformed_content="Prioritized sections",
            token_count=50,
            section_priority_result=priority_result,
        )

        assert result.transform_type == "section_priority"
        assert result.section_priority_result is not None

    def test_llm_transform_result_token_count_exceeds_limit(self):
        """Test LLMTransformResult raises error when token_count exceeds 10,000."""
        with pytest.raises(ValueError, match="exceeds 10,000 token limit"):
            LLMTransformResult(
                transform_type="readme_only",
                source_content="Source",
                transformed_content="Transformed",
                token_count=10001,  # Exceeds limit
            )

    def test_llm_transform_result_inconsistency_detection_missing_result(self):
        """Test LLMTransformResult raises error when inconsistency_result is missing."""
        with pytest.raises(
            ValueError,
            match="inconsistency_result is required when transform_type='inconsistency_detection'",
        ):
            LLMTransformResult(
                transform_type="inconsistency_detection",
                source_content="Source",
                transformed_content="Transformed",
                token_count=100,
                # Missing inconsistency_result
            )

    def test_llm_transform_result_section_priority_missing_result(self):
        """Test LLMTransformResult raises error when section_priority_result is missing."""
        with pytest.raises(
            ValueError,
            match="section_priority_result is required when transform_type='section_priority'",
        ):
            LLMTransformResult(
                transform_type="section_priority",
                source_content="Source",
                transformed_content="Transformed",
                token_count=100,
                # Missing section_priority_result
            )


# ============================================================================
# Phase 2 Entity Tests (Session 2025-10-18): T040-T043
# ============================================================================


class TestTargetAudienceResult:
    """Tests for TargetAudienceResult entity (T040)."""

    def test_target_audience_result_basic_creation(self):
        """T040: Test TargetAudienceResult basic creation."""
        result = TargetAudienceResult(
            file_path=Path("specs/001-draft-init-spec/README.md"),
            audience_type="developer",
            confidence=0.85,
            reasoning="Technical terminology and code examples indicate developer audience",
        )

        assert result.file_path == Path("specs/001-draft-init-spec/README.md")
        assert result.audience_type == "developer"
        assert result.confidence == 0.85
        assert "Technical terminology" in result.reasoning

    def test_audience_type_validation(self):
        """T040: Test audience_type constraint (end_user, developer, both)."""
        # Valid types
        for valid_type in ["end_user", "developer", "both"]:
            result = TargetAudienceResult(
                file_path=Path("test.md"),
                audience_type=valid_type,
            )
            assert result.audience_type == valid_type

        # Invalid type should raise ValueError
        with pytest.raises(ValueError, match="audience_type must be one of"):
            TargetAudienceResult(
                file_path=Path("test.md"),
                audience_type="invalid",
            )

    def test_confidence_range_validation(self):
        """T040: Test confidence range (0.0-1.0)."""
        # Valid confidence values
        for confidence in [0.0, 0.5, 1.0]:
            result = TargetAudienceResult(
                file_path=Path("test.md"),
                audience_type="developer",
                confidence=confidence,
            )
            assert result.confidence == confidence

        # Invalid confidence (< 0.0)
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            TargetAudienceResult(
                file_path=Path("test.md"),
                audience_type="developer",
                confidence=-0.1,
            )

        # Invalid confidence (> 1.0)
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            TargetAudienceResult(
                file_path=Path("test.md"),
                audience_type="developer",
                confidence=1.1,
            )

    def test_optional_fields(self):
        """T040: Test optional confidence and reasoning fields."""
        result = TargetAudienceResult(
            file_path=Path("test.md"),
            audience_type="end_user",
        )
        assert result.confidence is None
        assert result.reasoning is None


class TestSectionClassification:
    """Tests for SectionClassification entity (T041)."""

    def test_section_classification_basic_creation(self):
        """T041: Test SectionClassification basic creation."""
        classification = SectionClassification(
            file_path=Path("specs/001-draft-init-spec/README.md"),
            heading="## Developer Setup",
            section_type="developer",
            confidence=0.95,
        )

        assert classification.file_path == Path("specs/001-draft-init-spec/README.md")
        assert classification.heading == "## Developer Setup"
        assert classification.section_type == "developer"
        assert classification.confidence == 0.95

    def test_section_type_validation(self):
        """T041: Test section_type constraint (end_user, developer, both)."""
        # Valid types
        for valid_type in ["end_user", "developer", "both"]:
            classification = SectionClassification(
                file_path=Path("test.md"),
                heading="## Test",
                section_type=valid_type,
            )
            assert classification.section_type == valid_type

        # Invalid type should raise ValueError
        with pytest.raises(ValueError, match="section_type must be one of"):
            SectionClassification(
                file_path=Path("test.md"),
                heading="## Test",
                section_type="invalid",
            )

    def test_confidence_range_validation(self):
        """T041: Test confidence range (0.0-1.0)."""
        # Valid confidence
        classification = SectionClassification(
            file_path=Path("test.md"),
            heading="## Test",
            section_type="both",
            confidence=0.7,
        )
        assert classification.confidence == 0.7

        # Invalid confidence
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            SectionClassification(
                file_path=Path("test.md"),
                heading="## Test",
                section_type="both",
                confidence=1.5,
            )


class TestInconsistencyDetectionResultV2:
    """Tests for InconsistencyDetectionResultV2 entity (T042)."""

    def test_inconsistency_detection_result_consistent(self):
        """T042: Test InconsistencyDetectionResultV2 for consistent docs."""
        result = InconsistencyDetectionResultV2(
            readme_path=Path("specs/001-draft-init-spec/README.md"),
            quickstart_path=Path("specs/001-draft-init-spec/QUICKSTART.md"),
            is_consistent=True,
            inconsistencies=[],
            reasoning="Both files describe the same Python documentation tool",
        )

        assert result.readme_path == Path("specs/001-draft-init-spec/README.md")
        assert result.quickstart_path == Path("specs/001-draft-init-spec/QUICKSTART.md")
        assert result.is_consistent is True
        assert result.inconsistencies == []
        assert "Both files" in result.reasoning

    def test_inconsistency_detection_result_inconsistent(self):
        """T042: Test InconsistencyDetectionResultV2 for inconsistent docs."""
        result = InconsistencyDetectionResultV2(
            readme_path=Path("specs/001-draft-init-spec/README.md"),
            quickstart_path=Path("specs/001-draft-init-spec/QUICKSTART.md"),
            is_consistent=False,
            inconsistencies=[
                "README.md describes Python project, QUICKSTART.md describes Rust project",
                "Different main features listed",
            ],
            reasoning="Major technology stack mismatch detected",
        )

        assert result.is_consistent is False
        assert len(result.inconsistencies) == 2
        assert "Python project" in result.inconsistencies[0]
        assert "Rust project" in result.inconsistencies[0]

    def test_inconsistencies_required_when_not_consistent(self):
        """T042: Test that inconsistencies list is required when is_consistent=False."""
        # Should raise ValueError if inconsistencies is empty when is_consistent=False
        with pytest.raises(
            ValueError, match="inconsistencies list must not be empty when is_consistent is False"
        ):
            InconsistencyDetectionResultV2(
                readme_path=Path("test1.md"),
                quickstart_path=Path("test2.md"),
                is_consistent=False,
                inconsistencies=[],
            )


class TestSectionPriority:
    """Tests for SectionPriority entity (T043)."""

    def test_section_priority_basic_creation(self):
        """T043: Test SectionPriority basic creation."""
        section = SectionPriority(
            file_path=Path("specs/001-draft-init-spec/README.md"),
            heading="## Quick Start",
            priority=1,
            content="To get started with spec-kit-docs...",
            token_count=450,
        )

        assert section.file_path == Path("specs/001-draft-init-spec/README.md")
        assert section.heading == "## Quick Start"
        assert section.priority == 1
        assert section.content == "To get started with spec-kit-docs..."
        assert section.token_count == 450

    def test_priority_validation(self):
        """T043: Test priority must be >= 1."""
        # Valid priority
        section = SectionPriority(
            file_path=Path("test.md"),
            heading="## Test",
            priority=1,
            content="Test content",
            token_count=100,
        )
        assert section.priority == 1

        # Invalid priority (< 1)
        with pytest.raises(ValueError, match="priority must be >= 1"):
            SectionPriority(
                file_path=Path("test.md"),
                heading="## Test",
                priority=0,
                content="Test content",
                token_count=100,
            )

    def test_token_count_validation(self):
        """T043: Test token_count must be >= 1."""
        # Valid token_count
        section = SectionPriority(
            file_path=Path("test.md"),
            heading="## Test",
            priority=1,
            content="Test content",
            token_count=1,
        )
        assert section.token_count == 1

        # Invalid token_count (< 1)
        with pytest.raises(ValueError, match="token_count must be >= 1"):
            SectionPriority(
                file_path=Path("test.md"),
                heading="## Test",
                priority=1,
                content="Test content",
                token_count=0,
            )

    def test_sorting_by_priority(self):
        """T043: Test that sections can be sorted by priority."""
        sections = [
            SectionPriority(
                file_path=Path("test.md"),
                heading="## Low Priority",
                priority=3,
                content="Low",
                token_count=10,
            ),
            SectionPriority(
                file_path=Path("test.md"),
                heading="## High Priority",
                priority=1,
                content="High",
                token_count=10,
            ),
            SectionPriority(
                file_path=Path("test.md"),
                heading="## Medium Priority",
                priority=2,
                content="Medium",
                token_count=10,
            ),
        ]

        sorted_sections = sorted(sections, key=lambda s: s.priority)

        assert sorted_sections[0].priority == 1
        assert sorted_sections[1].priority == 2
        assert sorted_sections[2].priority == 3
