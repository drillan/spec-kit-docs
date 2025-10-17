"""Contract tests for /speckit.doc-update command output validation.

These tests validate that generated documentation excludes developer-facing
information (plan.md, tasks.md) per Session 2025-10-17 Content Filtering Strategy.
"""

import shutil
import tempfile
from pathlib import Path

import pytest


class TestDocUpdateContentFiltering:
    """Contract tests for Session 2025-10-17 Content Filtering Strategy."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with spec-kit structure."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)

        # Create spec-kit directory structure
        specs_dir = project_path / "specs" / "001-test-feature"
        specs_dir.mkdir(parents=True)

        # Create spec.md with user-friendly content
        spec_content = """# Test Feature Specification

## Overview
This is a user-friendly description of the feature.

## User Stories
- As a user, I want to use this feature
- So that I can accomplish my goals
"""
        (specs_dir / "spec.md").write_text(spec_content)

        # Create plan.md with developer-only content
        plan_content = """# Implementation Plan

## Phase 0: Research
- Investigate existing patterns
- Review architecture constraints

## Phase 1: Design
- Create data models
- Define API contracts
"""
        (specs_dir / "plan.md").write_text(plan_content)

        # Create tasks.md with developer-only content
        tasks_content = """# Implementation Tasks

## Phase 5: Core Implementation
- [ ] T001 [P1] [Core] Implement data model
- [ ] T002 [P1] [Core] Create API endpoints
- [ ] T003 [P2] [Test] Add unit tests

## Checkpoint
After T001-T003, verify core functionality works.
"""
        (specs_dir / "tasks.md").write_text(tasks_content)

        yield project_path
        shutil.rmtree(temp_dir)

    def test_generated_doc_excludes_plan_and_tasks_sections(self, temp_project_dir):
        """Verify generated documentation excludes Implementation Plan and Tasks sections.

        Session 2025-10-17 Content Filtering Strategy:
        - plan.md and tasks.md content must NOT appear in end-user documentation
        - Only spec.md content (LLM-transformed) should be included
        - Feature Files section with links to original files should remain

        TDD Red phase: This test should FAIL until T085-T086 are implemented.
        """
        from speckit_docs.generators.document import DocumentGenerator
        from speckit_docs.generators.feature_page import FeaturePageGenerator
        from speckit_docs.models import Feature, FeatureStatus, GeneratorConfig, GeneratorTool
        from speckit_docs.parsers.markdown_parser import MarkdownParser

        # Create feature object
        specs_dir = temp_project_dir / "specs" / "001-test-feature"
        feature = Feature(
            id="001",
            name="test-feature",
            status=FeatureStatus.DRAFT,
            directory_path=specs_dir,
            spec_file=specs_dir / "spec.md",
            plan_file=specs_dir / "plan.md",
            tasks_file=specs_dir / "tasks.md",
        )

        # Create generators
        from speckit_docs.models import StructureType

        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        feature_page_generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        # Generate feature pages
        pages = feature_page_generator.generate_pages([feature])
        assert len(pages) == 1, "Should generate exactly one page"

        # Read generated content from file
        generated_content = pages[0].read_text()

        # Verify Implementation Plan section is NOT present
        assert (
            "## Implementation Plan" not in generated_content
        ), "Generated doc must NOT contain '## Implementation Plan' section"

        # Verify Implementation Tasks section is NOT present
        assert (
            "## Implementation Tasks" not in generated_content
        ), "Generated doc must NOT contain '## Implementation Tasks' section"

    def test_generated_doc_excludes_plan_specific_content(self, temp_project_dir):
        """Verify plan.md-specific strings do not appear in generated documentation.

        Session 2025-10-17 Content Filtering Strategy:
        - No plan.md-specific content (Phase 0, Phase 1, etc.) should leak into docs
        - Validates that plan_doc is set to None in FeaturePageGenerator

        TDD Red phase: This test should FAIL until T086 is implemented.
        """
        from speckit_docs.generators.document import DocumentGenerator
        from speckit_docs.generators.feature_page import FeaturePageGenerator
        from speckit_docs.models import Feature, FeatureStatus, GeneratorConfig, GeneratorTool
        from speckit_docs.parsers.markdown_parser import MarkdownParser

        # Create feature object
        specs_dir = temp_project_dir / "specs" / "001-test-feature"
        feature = Feature(
            id="001",
            name="test-feature",
            status=FeatureStatus.DRAFT,
            directory_path=specs_dir,
            spec_file=specs_dir / "spec.md",
            plan_file=specs_dir / "plan.md",
            tasks_file=specs_dir / "tasks.md",
        )

        # Create generators
        from speckit_docs.models import StructureType

        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        feature_page_generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        # Generate feature pages
        pages = feature_page_generator.generate_pages([feature])
        # Read generated content from file
        generated_content = pages[0].read_text()

        # Verify plan.md-specific strings are NOT present
        plan_specific_strings = ["Phase 0", "Phase 1", "Constitution Check", "Research"]
        for plan_string in plan_specific_strings:
            assert (
                plan_string not in generated_content
            ), f"Generated doc must NOT contain plan.md-specific string '{plan_string}'"

    def test_generated_doc_excludes_tasks_specific_content(self, temp_project_dir):
        """Verify tasks.md-specific strings do not appear in generated documentation.

        Session 2025-10-17 Content Filtering Strategy:
        - No tasks.md-specific content (T001, Checkpoint, etc.) should leak into docs
        - Validates that tasks_doc is set to None in FeaturePageGenerator

        TDD Red phase: This test should FAIL until T086 is implemented.
        """
        from speckit_docs.generators.document import DocumentGenerator
        from speckit_docs.generators.feature_page import FeaturePageGenerator
        from speckit_docs.models import Feature, FeatureStatus, GeneratorConfig, GeneratorTool
        from speckit_docs.parsers.markdown_parser import MarkdownParser

        # Create feature object
        specs_dir = temp_project_dir / "specs" / "001-test-feature"
        feature = Feature(
            id="001",
            name="test-feature",
            status=FeatureStatus.DRAFT,
            directory_path=specs_dir,
            spec_file=specs_dir / "spec.md",
            plan_file=specs_dir / "plan.md",
            tasks_file=specs_dir / "tasks.md",
        )

        # Create generators
        from speckit_docs.models import StructureType

        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        feature_page_generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        # Generate feature pages
        pages = feature_page_generator.generate_pages([feature])
        # Read generated content from file
        generated_content = pages[0].read_text()

        # Verify tasks.md-specific strings are NOT present
        tasks_specific_strings = ["T001", "T002", "T003", "Checkpoint", "[ ] "]
        for tasks_string in tasks_specific_strings:
            assert (
                tasks_string not in generated_content
            ), f"Generated doc must NOT contain tasks.md-specific string '{tasks_string}'"

    def test_generated_doc_includes_feature_files_section(self, temp_project_dir):
        """Verify Feature Files section with links to original spec files is preserved.

        Session 2025-10-17 Content Filtering Strategy:
        - Developer-facing information remains accessible via Feature Files section
        - Links to spec.md, plan.md, tasks.md should be present

        TDD Red phase: This test should PASS even after T085-T086 (Feature Files preserved).
        """
        from speckit_docs.generators.document import DocumentGenerator
        from speckit_docs.generators.feature_page import FeaturePageGenerator
        from speckit_docs.models import Feature, FeatureStatus, GeneratorConfig, GeneratorTool
        from speckit_docs.parsers.markdown_parser import MarkdownParser

        # Create feature object
        specs_dir = temp_project_dir / "specs" / "001-test-feature"
        feature = Feature(
            id="001",
            name="test-feature",
            status=FeatureStatus.DRAFT,
            directory_path=specs_dir,
            spec_file=specs_dir / "spec.md",
            plan_file=specs_dir / "plan.md",
            tasks_file=specs_dir / "tasks.md",
        )

        # Create generators
        from speckit_docs.models import StructureType

        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        feature_page_generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        # Generate feature pages
        pages = feature_page_generator.generate_pages([feature])
        # Read generated content from file
        generated_content = pages[0].read_text()

        # Verify Feature Files section exists
        assert (
            "## Feature Files" in generated_content
        ), "Generated doc must contain '## Feature Files' section"

        # Verify links to original spec files
        assert (
            "spec.md" in generated_content
        ), "Feature Files section must link to spec.md"
        assert (
            "plan.md" in generated_content
        ), "Feature Files section must link to plan.md"
        assert (
            "tasks.md" in generated_content
        ), "Feature Files section must link to tasks.md"

    def test_generated_doc_includes_spec_content_only(self, temp_project_dir):
        """Verify generated documentation includes spec.md content (user-friendly).

        Session 2025-10-17 Content Filtering Strategy:
        - spec.md content (LLM-transformed) should be the primary content
        - User Stories, Overview, etc. from spec.md should appear

        TDD Red phase: This test should PASS (spec.md content is preserved).
        """
        from speckit_docs.generators.document import DocumentGenerator
        from speckit_docs.generators.feature_page import FeaturePageGenerator
        from speckit_docs.models import Feature, FeatureStatus, GeneratorConfig, GeneratorTool
        from speckit_docs.parsers.markdown_parser import MarkdownParser

        # Create feature object
        specs_dir = temp_project_dir / "specs" / "001-test-feature"
        feature = Feature(
            id="001",
            name="test-feature",
            status=FeatureStatus.DRAFT,
            directory_path=specs_dir,
            spec_file=specs_dir / "spec.md",
            plan_file=specs_dir / "plan.md",
            tasks_file=specs_dir / "tasks.md",
        )

        # Create generators
        from speckit_docs.models import StructureType

        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        feature_page_generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        # Generate feature pages
        pages = feature_page_generator.generate_pages([feature])
        # Read generated content from file
        generated_content = pages[0].read_text()

        # Verify spec.md content is present
        assert (
            "## Specification" in generated_content
        ), "Generated doc must contain '## Specification' section"
        assert (
            "user-friendly description" in generated_content
        ), "Generated doc must include spec.md content"
        assert (
            "User Stories" in generated_content
        ), "Generated doc must include spec.md User Stories"
