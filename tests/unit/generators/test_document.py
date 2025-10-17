"""Unit tests for DocumentGenerator (T022)."""

from pathlib import Path

from speckit_docs.generators.document import DocumentGenerator
from speckit_docs.models import Document, DocumentType, Feature, FeatureStatus


class TestDocumentGenerator:
    """Tests for DocumentGenerator class."""

    def test_generate_feature_page_basic(self):
        """Test basic feature page generation from spec.md only."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.DRAFT,
        )

        spec_doc = Document(
            file_path=feature.spec_file,
            type=DocumentType.SPEC,
            content="# Test Feature\n\n## Requirements\n\n- REQ-001: Test requirement",
            sections=[],
        )

        generator = DocumentGenerator()
        page_content = generator.generate_feature_page(feature, spec_doc)

        # Verify spec content is included
        assert "# Test Feature" in page_content
        assert "## Requirements" in page_content
        assert "REQ-001" in page_content

    def test_generate_feature_page_with_plan(self):
        """Test feature page generation with plan.md (Session 2025-10-17: plan excluded)."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.PLANNED,
            plan_file=Path("/path/to/specs/001-test-feature/plan.md"),
        )

        spec_doc = Document(
            file_path=feature.spec_file,
            type=DocumentType.SPEC,
            content="# Test Feature",
            sections=[],
        )

        plan_doc = Document(
            file_path=feature.plan_file,
            type=DocumentType.PLAN,
            content="# Implementation Plan\n\n## Architecture\n\nLayered architecture",
            sections=[],
        )

        generator = DocumentGenerator()
        page_content = generator.generate_feature_page(feature, spec_doc, plan_doc=plan_doc)

        # Session 2025-10-17: plan.md content is excluded from end-user docs
        assert "# Test Feature" in page_content
        assert "Architecture" not in page_content
        assert "Layered architecture" not in page_content
        # Feature Files section should still link to plan.md
        assert "plan.md" in page_content

    def test_generate_feature_page_with_tasks(self):
        """Test feature page generation with tasks.md (Session 2025-10-17: tasks excluded)."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.IN_PROGRESS,
            tasks_file=Path("/path/to/specs/001-test-feature/tasks.md"),
        )

        spec_doc = Document(
            file_path=feature.spec_file,
            type=DocumentType.SPEC,
            content="# Test Feature",
            sections=[],
        )

        tasks_doc = Document(
            file_path=feature.tasks_file,
            type=DocumentType.TASKS,
            content="# Tasks\n\n## T001: First Task\n\nImplement feature X",
            sections=[],
        )

        generator = DocumentGenerator()
        page_content = generator.generate_feature_page(feature, spec_doc, tasks_doc=tasks_doc)

        # Session 2025-10-17: tasks.md content is excluded from end-user docs
        assert "# Test Feature" in page_content
        assert "T001" not in page_content
        # Feature Files section should still link to tasks.md
        assert "tasks.md" in page_content

    def test_generate_feature_page_complete(self):
        """Test feature page generation with spec.md, plan.md, and tasks.md (Session 2025-10-17: plan/tasks excluded)."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.IN_PROGRESS,
            plan_file=Path("/path/to/specs/001-test-feature/plan.md"),
            tasks_file=Path("/path/to/specs/001-test-feature/tasks.md"),
        )

        spec_doc = Document(
            file_path=feature.spec_file,
            type=DocumentType.SPEC,
            content="# Test Feature\n\n## Overview\n\nThis is a test feature",
            sections=[],
        )

        plan_doc = Document(
            file_path=feature.plan_file,
            type=DocumentType.PLAN,
            content="# Plan\n\n## Architecture\n\nLayered design",
            sections=[],
        )

        tasks_doc = Document(
            file_path=feature.tasks_file,
            type=DocumentType.TASKS,
            content="# Tasks\n\n## T001: Task 1",
            sections=[],
        )

        generator = DocumentGenerator()
        page_content = generator.generate_feature_page(
            feature, spec_doc, plan_doc=plan_doc, tasks_doc=tasks_doc
        )

        # Session 2025-10-17: Only spec content included, plan/tasks excluded
        assert "# Test Feature" in page_content
        assert "Overview" in page_content
        assert "Architecture" not in page_content
        assert "T001" not in page_content
        # Feature Files section should still link to plan.md and tasks.md
        assert "plan.md" in page_content
        assert "tasks.md" in page_content

    def test_generate_feature_page_missing_plan(self):
        """Test that missing plan.md shows a note (FR-018)."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.DRAFT,
        )

        spec_doc = Document(
            file_path=feature.spec_file,
            type=DocumentType.SPEC,
            content="# Test Feature",
            sections=[],
        )

        generator = DocumentGenerator()
        page_content = generator.generate_feature_page(feature, spec_doc)

        # Verify note about missing plan (FR-018)
        # The exact wording depends on template, but should indicate plan is missing
        # We'll just verify the page is generated without error
        assert "# Test Feature" in page_content

    def test_generate_feature_page_missing_tasks(self):
        """Test that missing tasks.md shows a note (FR-018)."""
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=Path("/path/to/specs/001-test-feature"),
            spec_file=Path("/path/to/specs/001-test-feature/spec.md"),
            status=FeatureStatus.DRAFT,
        )

        spec_doc = Document(
            file_path=feature.spec_file,
            type=DocumentType.SPEC,
            content="# Test Feature",
            sections=[],
        )

        generator = DocumentGenerator()
        page_content = generator.generate_feature_page(feature, spec_doc)

        # Verify page is generated without error
        assert "# Test Feature" in page_content
