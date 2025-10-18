"""Unit tests for Phase 2 LLM transform functions (T048-T060).

Tests for:
- detect_target_audience()
- classify_section()
- detect_inconsistency() (already implemented, tested here)
- prioritize_sections() (already implemented, tested here)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from speckit_docs.llm_entities import (
    SectionClassification,
    TargetAudienceResult,
)


class TestDetectTargetAudience:
    """Tests for detect_target_audience() function (T048-T051)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_target_audience_end_user(self, mock_get_client):
        """T048: Test target audience detection for end-user document."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"audience_type": "end_user", "confidence": 0.9, "reasoning": "Simple language, no technical jargon"}')]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_target_audience

        result = detect_target_audience(Path("tests/fixtures/sample_docs/valid_readme.md"))

        assert isinstance(result, TargetAudienceResult)
        assert result.file_path == Path("tests/fixtures/sample_docs/valid_readme.md")
        assert result.audience_type == "end_user"
        assert result.confidence == 0.9
        assert "Simple language" in result.reasoning

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_target_audience_developer(self, mock_get_client):
        """T049: Test target audience detection for developer document."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"audience_type": "developer", "confidence": 0.95, "reasoning": "Technical terminology, code examples, API references"}')]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_target_audience

        result = detect_target_audience(Path("tests/fixtures/sample_docs/inconsistent_readme.md"))

        assert result.audience_type == "developer"
        assert result.confidence == 0.95

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_target_audience_both(self, mock_get_client):
        """T050: Test target audience detection for mixed audience document."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"audience_type": "both", "confidence": 0.8, "reasoning": "Combines high-level overview with technical details"}')]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_target_audience

        result = detect_target_audience(Path("tests/fixtures/sample_docs/valid_readme.md"))

        assert result.audience_type == "both"
        assert result.confidence == 0.8

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_target_audience_llm_failure(self, mock_get_client):
        """T051: Test error handling when LLM API call fails."""
        # Mock LLM API error
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_target_audience

        with pytest.raises(Exception):
            detect_target_audience(Path("tests/fixtures/sample_docs/valid_readme.md"))


class TestClassifySection:
    """Tests for classify_section() function (T052-T054)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_classify_section_end_user(self, mock_get_client):
        """T052: Test section classification for end-user section."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"section_type": "end_user", "confidence": 0.92}')]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import classify_section

        result = classify_section(
            file_path=Path("tests/fixtures/sample_docs/valid_readme.md"),
            heading="## Quick Start",
            content="Follow these simple steps to get started...",
        )

        assert isinstance(result, SectionClassification)
        assert result.file_path == Path("tests/fixtures/sample_docs/valid_readme.md")
        assert result.heading == "## Quick Start"
        assert result.section_type == "end_user"
        assert result.confidence == 0.92

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_classify_section_developer(self, mock_get_client):
        """T053: Test section classification for developer section."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"section_type": "developer", "confidence": 0.98}')]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import classify_section

        result = classify_section(
            file_path=Path("tests/fixtures/sample_docs/inconsistent_readme.md"),
            heading="## API Reference",
            content="Function signatures and return types...",
        )

        assert result.section_type == "developer"
        assert result.confidence == 0.98

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_classify_section_llm_failure(self, mock_get_client):
        """T054: Test error handling when LLM API call fails."""
        # Mock LLM API error
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import classify_section

        with pytest.raises(Exception):
            classify_section(
                file_path=Path("tests/fixtures/sample_docs/valid_readme.md"),
                heading="## Test",
                content="Test content",
            )


class TestDetectInconsistency:
    """Tests for detect_inconsistency() function (T055-T057)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_inconsistency_consistent(self, mock_get_client):
        """T055: Test inconsistency detection for consistent files."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"is_consistent": true, "inconsistencies": [], "summary": "Files are consistent."}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_inconsistency

        # Note: Existing implementation takes content strings, not paths
        result = detect_inconsistency(
            readme_content="# My Project\n\nA simple project.",
            quickstart_content="# Quick Start\n\nGet started quickly.",
            client=mock_client,
        )

        # The existing implementation returns InconsistencyDetectionResult, not V2
        assert result.is_consistent is True
        assert len(result.inconsistencies) == 0

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_inconsistency_tech_stack_mismatch(self, mock_get_client):
        """T056: Test inconsistency detection for technology stack mismatch."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"is_consistent": false, "inconsistencies": [{"type": "technology_stack", "readme_claim": "Python 3.11+", "quickstart_claim": "Rust", "severity": "critical"}], "summary": "Major technology stack mismatch"}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_inconsistency

        result = detect_inconsistency(
            readme_content="# Python Project\n\nRequires Python 3.11+",
            quickstart_content="# Rust Project\n\nBuild with cargo",
            client=mock_client,
        )

        assert result.is_consistent is False
        assert len(result.inconsistencies) > 0

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_detect_inconsistency_llm_failure(self, mock_get_client):
        """T057: Test error handling when LLM API call fails."""
        # Mock LLM API error
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_inconsistency

        with pytest.raises(Exception):
            detect_inconsistency(
                readme_content="# Test",
                quickstart_content="# Test",
                client=mock_client,
            )


class TestPrioritizeSections:
    """Tests for prioritize_sections() function (T058-T060)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_prioritize_sections_normal(self, mock_get_client):
        """T058: Test section prioritization normal case."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"prioritized_sections": [{"file": "README.md", "heading": "## Quick Start", "priority": 1, "reason": "Essential"}]}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.llm_entities import LLMSection
        from speckit_docs.utils.llm_transform import prioritize_sections

        sections = [
            LLMSection(
                file="README.md",
                heading="## Quick Start",
                level="h2",
                content="Start here",
                token_count=10,
            )
        ]

        result = prioritize_sections(sections, client=mock_client)

        assert result.total_sections == 1
        assert result.included_sections == 1
        assert len(result.excluded_sections) == 0

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_prioritize_sections_token_limit(self, mock_get_client):
        """T059: Test section prioritization with token limit exceeded."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"prioritized_sections": [{"file": "README.md", "heading": "## Quick Start", "priority": 1, "reason": "Essential"}]}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.llm_entities import LLMSection
        from speckit_docs.utils.llm_transform import prioritize_sections

        sections = [
            LLMSection(
                file="README.md",
                heading="## Quick Start",
                level="h2",
                content="Start",
                token_count=5000,
            ),
            LLMSection(
                file="README.md", heading="## Advanced", level="h2", content="Advanced", token_count=3000
            ),
            LLMSection(
                file="README.md", heading="## Reference", level="h2", content="Ref", token_count=3000
            ),
        ]

        result = prioritize_sections(sections, client=mock_client)

        assert result.included_sections == 1
        assert len(result.excluded_sections) == 2

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_prioritize_sections_llm_failure(self, mock_get_client):
        """T060: Test error handling when LLM API call fails."""
        # Mock LLM API error
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        from speckit_docs.llm_entities import LLMSection
        from speckit_docs.utils.llm_transform import prioritize_sections

        sections = [
            LLMSection(
                file="README.md",
                heading="## Test",
                level="h2",
                content="Test content",
                token_count=10,
            )
        ]

        with pytest.raises(Exception):
            prioritize_sections(sections, client=mock_client)
