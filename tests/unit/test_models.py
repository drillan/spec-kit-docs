"""Unit tests for speckit_docs.models module."""

from datetime import datetime
from pathlib import Path

import pytest

from speckit_docs.models import (
    Document,
    DocumentType,
    Feature,
    FeatureStatus,
    GeneratorTool,
    GitStatus,
    Section,
    StructureType,
)


class TestFeatureStatus:
    """Tests for FeatureStatus enum."""

    def test_feature_status_values(self):
        """Test that FeatureStatus has correct values."""
        assert FeatureStatus.DRAFT.value == "draft"
        assert FeatureStatus.PLANNED.value == "planned"
        assert FeatureStatus.IN_PROGRESS.value == "in_progress"
        assert FeatureStatus.COMPLETED.value == "completed"

    def test_feature_status_members(self):
        """Test that FeatureStatus has all expected members."""
        expected_members = {"DRAFT", "PLANNED", "IN_PROGRESS", "COMPLETED"}
        actual_members = {member.name for member in FeatureStatus}
        assert actual_members == expected_members


class TestDocumentType:
    """Tests for DocumentType enum."""

    def test_document_type_values(self):
        """Test that DocumentType has correct values."""
        assert DocumentType.SPEC.value == "spec"
        assert DocumentType.PLAN.value == "plan"
        assert DocumentType.TASKS.value == "tasks"

    def test_document_type_members(self):
        """Test that DocumentType has all expected members."""
        expected_members = {"SPEC", "PLAN", "TASKS"}
        actual_members = {member.name for member in DocumentType}
        assert actual_members == expected_members


class TestGitStatus:
    """Tests for GitStatus enum."""

    def test_git_status_values(self):
        """Test that GitStatus has correct values."""
        assert GitStatus.UNTRACKED.value == "untracked"
        assert GitStatus.MODIFIED.value == "modified"
        assert GitStatus.STAGED.value == "staged"
        assert GitStatus.COMMITTED.value == "committed"

    def test_git_status_members(self):
        """Test that GitStatus has all expected members."""
        expected_members = {"UNTRACKED", "MODIFIED", "STAGED", "COMMITTED"}
        actual_members = {member.name for member in GitStatus}
        assert actual_members == expected_members


class TestStructureType:
    """Tests for StructureType enum."""

    def test_structure_type_values(self):
        """Test that StructureType has correct values."""
        assert StructureType.FLAT.value == "flat"
        assert StructureType.COMPREHENSIVE.value == "comprehensive"

    def test_structure_type_members(self):
        """Test that StructureType has all expected members."""
        expected_members = {"FLAT", "COMPREHENSIVE"}
        actual_members = {member.name for member in StructureType}
        assert actual_members == expected_members


class TestGeneratorTool:
    """Tests for GeneratorTool enum."""

    def test_generator_tool_values(self):
        """Test that GeneratorTool has correct values."""
        assert GeneratorTool.SPHINX.value == "sphinx"
        assert GeneratorTool.MKDOCS.value == "mkdocs"

    def test_generator_tool_members(self):
        """Test that GeneratorTool has all expected members."""
        expected_members = {"SPHINX", "MKDOCS"}
        actual_members = {member.name for member in GeneratorTool}
        assert actual_members == expected_members


class TestFeature:
    """Tests for Feature dataclass."""

    def test_feature_creation(self):
        """Test that Feature can be created with required attributes."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.DRAFT,
        )
        assert feature.id == "001"
        assert feature.name == "test-feature"
        assert feature.directory_path == Path("/path/to/specs/001-test-feature")
        assert feature.spec_file == Path("/path/to/specs/001-test-feature/spec.md")
        assert feature.status == FeatureStatus.DRAFT

    def test_feature_with_optional_files(self):
        """Test that Feature can have optional plan and tasks files."""
        feature = Feature(
            id="002",
            name="another-feature",
            directory_path=Path("/path/to/specs/002-another-feature"),
            spec_file=Path("/path/to/specs/002-another-feature/spec.md"),
            status=FeatureStatus.IN_PROGRESS,
            plan_file=Path("/path/to/specs/002-another-feature/plan.md"),
            tasks_file=Path("/path/to/specs/002-another-feature/tasks.md"),
            priority="P1",
        )
        assert feature.plan_file == Path("/path/to/specs/002-another-feature/plan.md")
        assert feature.tasks_file == Path("/path/to/specs/002-another-feature/tasks.md")
        assert feature.priority == "P1"

    def test_feature_with_metadata(self):
        """Test that Feature can store metadata."""
        feature = Feature(
            id="003",
            name="feature-with-meta",
            directory_path=Path("/path/to/specs/003-feature-with-meta"),
            spec_file=Path("/path/to/specs/003-feature-with-meta/spec.md"),
            status=FeatureStatus.COMPLETED,
            metadata={"created": "2025-01-01", "tags": ["api", "backend"]},
        )
        assert feature.metadata["created"] == "2025-01-01"
        assert "api" in feature.metadata["tags"]

    def test_feature_is_frozen(self):
        """Test that Feature is immutable (frozen)."""
        feature = Feature(
            id="004",
            name="immutable-feature",
            directory_path=Path("/path/to/specs/004-immutable-feature"),
            spec_file=Path("/path/to/specs/004-immutable-feature/spec.md"),
            status=FeatureStatus.DRAFT,
        )
        with pytest.raises(AttributeError):
            feature.id = "999"  # Should raise error because frozen=True


class TestDocument:
    """Tests for Document dataclass."""

    def test_document_creation(self):
        """Test that Document can be created with required attributes."""
        doc = Document(
            file_path=Path("/path/to/spec.md"),
            type=DocumentType.SPEC,
            content="# Test Specification\n\nContent here.",
        )
        assert doc.file_path == Path("/path/to/spec.md")
        assert doc.type == DocumentType.SPEC
        assert doc.content == "# Test Specification\n\nContent here."
        assert doc.sections == []
        assert doc.last_modified is None
        assert doc.git_status == GitStatus.UNTRACKED

    def test_document_with_sections(self):
        """Test that Document can have sections."""
        section = Section(
            title="Introduction", level=1, content="Intro text", line_start=1, line_end=5
        )
        doc = Document(
            file_path=Path("/path/to/plan.md"),
            type=DocumentType.PLAN,
            content="# Plan\n\n## Introduction\n\nIntro text",
            sections=[section],
        )
        assert len(doc.sections) == 1
        assert doc.sections[0].title == "Introduction"

    def test_document_with_git_status(self):
        """Test that Document can have different git statuses."""
        doc = Document(
            file_path=Path("/path/to/tasks.md"),
            type=DocumentType.TASKS,
            content="# Tasks",
            git_status=GitStatus.MODIFIED,
            last_modified=datetime(2025, 1, 1, 12, 0),
        )
        assert doc.git_status == GitStatus.MODIFIED
        assert doc.last_modified == datetime(2025, 1, 1, 12, 0)


class TestSection:
    """Tests for Section dataclass."""

    def test_section_creation(self):
        """Test that Section can be created with required attributes."""
        section = Section(
            title="Overview",
            level=1,
            content="This is an overview section.",
            line_start=1,
            line_end=10,
        )
        assert section.title == "Overview"
        assert section.level == 1
        assert section.content == "This is an overview section."
        assert section.line_start == 1
        assert section.line_end == 10
        assert section.subsections == []

    def test_section_with_subsections(self):
        """Test that Section can have nested subsections (recursive structure)."""
        subsection1 = Section(
            title="Subsection 1",
            level=2,
            content="Content of subsection 1",
            line_start=5,
            line_end=8,
        )
        subsection2 = Section(
            title="Subsection 2",
            level=2,
            content="Content of subsection 2",
            line_start=9,
            line_end=12,
        )
        parent_section = Section(
            title="Parent Section",
            level=1,
            content="Parent content",
            line_start=1,
            line_end=15,
            subsections=[subsection1, subsection2],
        )
        assert len(parent_section.subsections) == 2
        assert parent_section.subsections[0].title == "Subsection 1"
        assert parent_section.subsections[1].title == "Subsection 2"

    def test_section_deeply_nested(self):
        """Test that Section supports deeply nested structures."""
        level3_section = Section(
            title="Level 3",
            level=3,
            content="Deepest level",
            line_start=10,
            line_end=12,
        )
        level2_section = Section(
            title="Level 2",
            level=2,
            content="Middle level",
            line_start=5,
            line_end=15,
            subsections=[level3_section],
        )
        level1_section = Section(
            title="Level 1",
            level=1,
            content="Top level",
            line_start=1,
            line_end=20,
            subsections=[level2_section],
        )

        assert len(level1_section.subsections) == 1
        assert len(level1_section.subsections[0].subsections) == 1
        assert level1_section.subsections[0].subsections[0].title == "Level 3"


class TestGeneratorConfig:
    """Tests for GeneratorConfig dataclass."""

    def test_generator_config_creation_sphinx(self):
        """Test that GeneratorConfig can be created for Sphinx projects."""
        from speckit_docs.models import GeneratorConfig

        config = GeneratorConfig(
            tool=GeneratorTool.SPHINX,
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
        )
        assert config.tool == GeneratorTool.SPHINX
        assert config.project_name == "Test Project"
        assert config.author == "Test Author"
        assert config.version == "1.0.0"

    def test_generator_config_creation_mkdocs(self):
        """Test that GeneratorConfig can be created for MkDocs projects."""
        from speckit_docs.models import GeneratorConfig

        config = GeneratorConfig(
            tool=GeneratorTool.MKDOCS,
            project_name="MkDocs Project",
            author="MkDocs Author",
            version="2.0.0",
        )
        assert config.tool == GeneratorTool.MKDOCS
        assert config.project_name == "MkDocs Project"

    def test_generator_config_with_optional_fields(self):
        """Test that GeneratorConfig supports optional fields."""
        from speckit_docs.models import GeneratorConfig

        config = GeneratorConfig(
            tool=GeneratorTool.SPHINX,
            project_name="Test",
            author="Author",
            version="1.0.0",
            language="ja",
            theme="furo",
            extensions=["myst_parser", "sphinx.ext.autodoc"],
            plugins=["search", "minify"],
            custom_settings={"html_theme_options": {"sidebar_hide_name": True}},
        )
        assert config.language == "ja"
        assert config.theme == "furo"
        assert "myst_parser" in config.extensions
        assert "search" in config.plugins
        assert config.custom_settings["html_theme_options"]["sidebar_hide_name"] is True

    def test_generator_config_to_sphinx_conf(self):
        """Test that GeneratorConfig can be converted to Sphinx conf.py dict."""
        from speckit_docs.models import GeneratorConfig

        config = GeneratorConfig(
            tool=GeneratorTool.SPHINX,
            project_name="Sphinx Test",
            author="Sphinx Author",
            version="3.0.0",
            language="en",
            theme="alabaster",
            extensions=["myst_parser"],
        )
        conf_dict = config.to_sphinx_conf()
        assert conf_dict["project"] == "Sphinx Test"
        assert conf_dict["author"] == "Sphinx Author"
        assert conf_dict["version"] == "3.0.0"
        assert conf_dict["language"] == "en"
        assert conf_dict["html_theme"] == "alabaster"
        assert "myst_parser" in conf_dict["extensions"]

    def test_generator_config_to_mkdocs_yaml(self):
        """Test that GeneratorConfig can be converted to MkDocs YAML dict."""
        from speckit_docs.models import GeneratorConfig

        config = GeneratorConfig(
            tool=GeneratorTool.MKDOCS,
            project_name="MkDocs Test",
            author="MkDocs Author",
            version="4.0.0",
            theme="material",
            plugins=["search", "tags"],
        )
        mkdocs_dict = config.to_mkdocs_yaml()
        assert mkdocs_dict["site_name"] == "MkDocs Test"
        assert mkdocs_dict["site_author"] == "MkDocs Author"
        assert mkdocs_dict["theme"]["name"] == "material"
        assert "search" in mkdocs_dict["plugins"]
        assert "tags" in mkdocs_dict["plugins"]
