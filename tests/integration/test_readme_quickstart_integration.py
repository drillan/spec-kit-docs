"""Integration tests for README/QUICKSTART processing (Phase 5C: T066-T071).

Tests for:
- README.md only target audience detection
- QUICKSTART.md only target audience detection
- README + QUICKSTART inconsistency detection
- README + QUICKSTART section integration
- Section integration token limit
- Statistics display validation
"""

from pathlib import Path
from unittest.mock import MagicMock, patch


class TestReadmeOnlyProcessing:
    """Tests for README.md only processing (T066)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_readme_only_target_audience(self, mock_get_client, tmp_path: Path):
        """T066: Test target audience detection for README.md only."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"audience_type": "end_user", "confidence": 0.9, "reasoning": "Simple installation guide"}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_target_audience, select_content_source

        # Given: Feature directory with README.md only
        feature_dir = tmp_path / "specs" / "001-test-feature"
        feature_dir.mkdir(parents=True)
        readme_file = feature_dir / "README.md"
        readme_file.write_text(
            "# My Project\n\n## Installation\n\nDownload and install with npm install my-project."
        )

        # When: Select content source
        source_type, file_path = select_content_source(feature_dir)

        # Then: README.md is selected
        assert source_type == "readme"
        assert file_path == readme_file

        # When: Detect target audience
        result = detect_target_audience(file_path)

        # Then: Target audience is detected correctly
        assert result.audience_type == "end_user"
        assert result.confidence == 0.9
        assert "Simple installation guide" in result.reasoning


class TestQuickstartOnlyProcessing:
    """Tests for QUICKSTART.md only processing (T067)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_quickstart_only_target_audience(self, mock_get_client, tmp_path: Path):
        """T067: Test target audience detection for QUICKSTART.md only."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"audience_type": "developer", "confidence": 0.95, "reasoning": "Technical API usage examples"}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_target_audience, select_content_source

        # Given: Feature directory with QUICKSTART.md only
        feature_dir = tmp_path / "specs" / "002-test-feature"
        feature_dir.mkdir(parents=True)
        quickstart_file = feature_dir / "QUICKSTART.md"
        quickstart_file.write_text(
            "# Quick Start\n\n## API Usage\n\n```python\nimport mylib\nmylib.connect()\n```"
        )

        # When: Select content source
        source_type, file_path = select_content_source(feature_dir)

        # Then: QUICKSTART.md is selected
        assert source_type == "quickstart"
        assert file_path == quickstart_file

        # When: Detect target audience
        result = detect_target_audience(file_path)

        # Then: Target audience is detected correctly
        assert result.audience_type == "developer"
        assert result.confidence == 0.95


class TestInconsistencyDetection:
    """Tests for README + QUICKSTART inconsistency detection (T068)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_inconsistency_detection_error(self, mock_get_client, tmp_path: Path):
        """T068: Test inconsistency detection error when README and QUICKSTART are inconsistent."""
        # Mock LLM response with inconsistency
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"is_consistent": false, "inconsistencies": [{"type": "technology_stack", "readme_claim": "Python 3.11+", "quickstart_claim": "Rust", "severity": "critical"}], "summary": "Major technology stack mismatch"}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import detect_inconsistency, select_content_source

        # Given: Feature directory with inconsistent README and QUICKSTART
        feature_dir = tmp_path / "specs" / "003-test-feature"
        feature_dir.mkdir(parents=True)
        readme_file = feature_dir / "README.md"
        readme_file.write_text("# Python Project\n\nRequires Python 3.11+")
        quickstart_file = feature_dir / "QUICKSTART.md"
        quickstart_file.write_text("# Rust Project\n\nBuild with cargo")

        # When: Select content source
        source_type, file_paths = select_content_source(feature_dir)

        # Then: Both files are selected
        assert source_type == "both"
        readme_path, quickstart_path = file_paths
        assert readme_path == readme_file
        assert quickstart_path == quickstart_file

        # When: Detect inconsistency
        readme_content = readme_file.read_text()
        quickstart_content = quickstart_file.read_text()
        result = detect_inconsistency(
            readme_content=readme_content, quickstart_content=quickstart_content, client=mock_client
        )

        # Then: Inconsistency is detected
        assert result.is_consistent is False
        assert len(result.inconsistencies) > 0
        assert result.inconsistencies[0].type == "technology_stack"


class TestSectionIntegration:
    """Tests for README + QUICKSTART section integration (T069, T070)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_section_integration_success(self, mock_get_client, tmp_path: Path):
        """T069: Test successful section integration when README and QUICKSTART are consistent."""
        # Mock LLM responses
        mock_client = MagicMock()

        def mock_create(*args, **kwargs):
            # Detect which prompt is being used
            content = kwargs["messages"][0]["content"]
            if "README.md content:" in content or "QUICKSTART.md content:" in content:
                # Inconsistency detection response
                response = MagicMock()
                response.content = [
                    MagicMock(
                        text='{"is_consistent": true, "inconsistencies": [], "summary": "Files are consistent."}'
                    )
                ]
                return response
            else:
                # Section prioritization response
                response = MagicMock()
                response.content = [
                    MagicMock(
                        text='{"prioritized_sections": [{"file": "README.md", "heading": "## Overview", "priority": 1, "reason": "Essential introduction"}, {"file": "QUICKSTART.md", "heading": "## Quick Start", "priority": 2, "reason": "Getting started guide"}]}'
                    )
                ]
                return response

        mock_client.messages.create.side_effect = mock_create
        mock_get_client.return_value = mock_client

        from speckit_docs.llm_entities import LLMSection
        from speckit_docs.utils.llm_transform import detect_inconsistency, prioritize_sections

        # Given: Consistent README and QUICKSTART
        readme_content = "# My Project\n\n## Overview\nThis is a Python project."
        quickstart_content = "# Quick Start\n\n## Quick Start\nInstall with pip install my-project."

        # When: Check consistency
        inconsistency_result = detect_inconsistency(
            readme_content=readme_content, quickstart_content=quickstart_content, client=mock_client
        )

        # Then: Files are consistent
        assert inconsistency_result.is_consistent is True

        # Given: Sections from both files
        sections = [
            LLMSection(
                file="README.md",
                heading="## Overview",
                level="h2",
                content="This is a Python project.",
                token_count=100,
            ),
            LLMSection(
                file="QUICKSTART.md",
                heading="## Quick Start",
                level="h2",
                content="Install with pip install my-project.",
                token_count=150,
            ),
        ]

        # When: Prioritize sections
        priority_result = prioritize_sections(sections, client=mock_client)

        # Then: Both sections are included
        assert priority_result.total_sections == 2
        assert priority_result.included_sections == 2
        assert len(priority_result.excluded_sections) == 0

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_section_integration_token_limit(self, mock_get_client):
        """T070: Test section integration with token limit exceeded."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"prioritized_sections": [{"file": "README.md", "heading": "## Overview", "priority": 1, "reason": "Essential"}, {"file": "README.md", "heading": "## Advanced", "priority": 2, "reason": "Advanced topics"}, {"file": "README.md", "heading": "## Reference", "priority": 3, "reason": "Reference material"}]}'
            )
        ]
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from speckit_docs.llm_entities import LLMSection
        from speckit_docs.utils.llm_transform import prioritize_sections

        # Given: Sections that exceed 10,000 token limit
        sections = [
            LLMSection(
                file="README.md",
                heading="## Overview",
                level="h2",
                content="Overview content",
                token_count=5000,
            ),
            LLMSection(
                file="README.md",
                heading="## Advanced",
                level="h2",
                content="Advanced content",
                token_count=3000,
            ),
            LLMSection(
                file="README.md",
                heading="## Reference",
                level="h2",
                content="Reference content",
                token_count=3000,
            ),
        ]

        # When: Prioritize sections
        result = prioritize_sections(sections, client=mock_client)

        # Then: Only sections within token limit are included
        assert result.total_sections == 3
        assert result.included_sections == 2  # 5000 + 3000 = 8000 <= 10000
        assert len(result.excluded_sections) == 1  # Reference section excluded


class TestStatisticsDisplay:
    """Tests for statistics display validation (T071)."""

    @patch("speckit_docs.utils.llm_transform.get_anthropic_client")
    def test_stats_display(self, mock_get_client, tmp_path: Path):
        """T071: Test that statistics are correctly generated for display."""
        # Mock LLM responses
        mock_client = MagicMock()

        def mock_create(*args, **kwargs):
            content = kwargs["messages"][0]["content"]
            if "target audience" in content.lower():
                # Target audience detection
                response = MagicMock()
                response.content = [
                    MagicMock(
                        text='{"audience_type": "end_user", "confidence": 0.9, "reasoning": "Simple language"}'
                    )
                ]
                return response
            elif "classify" in content.lower():
                # Section classification
                response = MagicMock()
                response.content = [
                    MagicMock(text='{"section_type": "end_user", "confidence": 0.85}')
                ]
                return response
            else:
                # Default response
                response = MagicMock()
                response.content = [MagicMock(text='{}')]
                return response

        mock_client.messages.create.side_effect = mock_create
        mock_get_client.return_value = mock_client

        from speckit_docs.utils.llm_transform import classify_section, detect_target_audience

        # Given: README file
        readme_file = tmp_path / "README.md"
        readme_file.write_text("# My Project\n\n## Overview\nSimple user guide.")

        # When: Detect target audience
        audience_result = detect_target_audience(readme_file)

        # Then: Statistics can be generated
        assert audience_result.audience_type == "end_user"
        assert audience_result.confidence == 0.9

        # When: Classify section
        section_result = classify_section(
            file_path=readme_file, heading="## Overview", content="Simple user guide."
        )

        # Then: Section classification statistics can be generated
        assert section_result.section_type == "end_user"
        assert section_result.confidence == 0.85

        # Statistics format (as shown in speckit.doc-update.md):
        # - Target audience: end_user (90.0% confidence)
        # - Section classification: end_user (85.0% confidence)
