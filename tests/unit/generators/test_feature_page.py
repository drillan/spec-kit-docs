"""Unit tests for FeaturePageGenerator (T023)."""

from pathlib import Path

import pytest

from speckit_docs.generators.feature_page import FeaturePageGenerator
from speckit_docs.models import Feature, FeatureStatus, GeneratorTool, StructureType


class TestFeaturePageGenerator:
    """Tests for FeaturePageGenerator class."""

    def test_generate_pages_flat_structure(self, tmp_path):
        """Test feature page generation with FLAT structure (FR-013)."""
        # Create test features
        feature1_dir = tmp_path / "specs/001-feature-one"
        feature1_dir.mkdir(parents=True)
        (feature1_dir / "spec.md").write_text("# Feature One\n\n## Overview\n\nFirst feature")

        feature2_dir = tmp_path / "specs/002-feature-two"
        feature2_dir.mkdir(parents=True)
        (feature2_dir / "spec.md").write_text("# Feature Two\n\n## Overview\n\nSecond feature")

        features = [
            Feature(
                id="001",
                name="feature-one",
                directory_path=feature1_dir,
                spec_file=feature1_dir / "spec.md",
                status=FeatureStatus.DRAFT,
            ),
            Feature(
                id="002",
                name="feature-two",
                directory_path=feature2_dir,
                spec_file=feature2_dir / "spec.md",
                status=FeatureStatus.DRAFT,
            ),
        ]

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        generated_pages = generator.generate_pages(features)

        # Verify pages were generated in flat structure
        assert len(generated_pages) == 2
        assert (docs_dir / "feature-one.md").exists()
        assert (docs_dir / "feature-two.md").exists()

        # Verify content
        content1 = (docs_dir / "feature-one.md").read_text()
        assert "Feature One" in content1
        assert "First feature" in content1

    def test_generate_pages_comprehensive_structure(self, tmp_path):
        """Test feature page generation with COMPREHENSIVE structure (FR-014)."""
        # Create test features
        feature_dir = tmp_path / "specs/001-test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# Test Feature\n\nContent")

        features = [
            Feature(
                id="001",
                name="test-feature",
                directory_path=feature_dir,
                spec_file=feature_dir / "spec.md",
                status=FeatureStatus.DRAFT,
            ),
        ]

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.COMPREHENSIVE,
            tool=GeneratorTool.SPHINX,
        )

        generated_pages = generator.generate_pages(features)

        # Verify page was generated in features/ subdirectory
        assert len(generated_pages) == 1
        assert (docs_dir / "features" / "test-feature.md").exists()
        assert not (docs_dir / "test-feature.md").exists()

    def test_generate_pages_with_plan_and_tasks(self, tmp_path):
        """Test feature page generation with plan.md and tasks.md (FR-016, FR-017)."""
        # Create test feature with all files
        feature_dir = tmp_path / "specs/001-complete-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# Complete Feature\n\n## Requirements")
        (feature_dir / "plan.md").write_text("# Plan\n\n## Architecture\n\nLayered")
        (feature_dir / "tasks.md").write_text("# Tasks\n\n## T001: Task 1")

        features = [
            Feature(
                id="001",
                name="complete-feature",
                directory_path=feature_dir,
                spec_file=feature_dir / "spec.md",
                status=FeatureStatus.PLANNED,
                plan_file=feature_dir / "plan.md",
                tasks_file=feature_dir / "tasks.md",
            ),
        ]

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        generated_pages = generator.generate_pages(features)

        # Verify page was generated
        assert len(generated_pages) == 1
        page_path = docs_dir / "complete-feature.md"
        assert page_path.exists()

        # Verify all content is included
        content = page_path.read_text()
        assert "Complete Feature" in content
        assert "Requirements" in content
        assert "Architecture" in content or "Layered" in content
        assert "T001" in content or "Tasks" in content

    def test_generate_pages_descriptive_filename(self, tmp_path):
        """Test that filenames are descriptive without numbers (FR-013, FR-014)."""
        # Create test feature with ID prefix
        feature_dir = tmp_path / "specs/042-user-authentication"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# User Authentication")

        features = [
            Feature(
                id="042",
                name="user-authentication",
                directory_path=feature_dir,
                spec_file=feature_dir / "spec.md",
                status=FeatureStatus.DRAFT,
            ),
        ]

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        generated_pages = generator.generate_pages(features)

        # Verify filename uses descriptive name (without number prefix)
        assert len(generated_pages) == 1
        assert generated_pages[0].name == "user-authentication.md"
        assert (docs_dir / "user-authentication.md").exists()

    def test_generate_pages_empty_list(self, tmp_path):
        """Test that empty feature list returns empty page list."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.FLAT,
            tool=GeneratorTool.SPHINX,
        )

        generated_pages = generator.generate_pages([])

        assert len(generated_pages) == 0

    def test_generate_pages_creates_subdirectory(self, tmp_path):
        """Test that COMPREHENSIVE structure creates features/ subdirectory."""
        feature_dir = tmp_path / "specs/001-test"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# Test")

        features = [
            Feature(
                id="001",
                name="test",
                directory_path=feature_dir,
                spec_file=feature_dir / "spec.md",
                status=FeatureStatus.DRAFT,
            ),
        ]

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = FeaturePageGenerator(
            docs_dir=docs_dir,
            structure_type=StructureType.COMPREHENSIVE,
            tool=GeneratorTool.SPHINX,
        )

        generated_pages = generator.generate_pages(features)

        # Verify features/ subdirectory was created
        assert (docs_dir / "features").exists()
        assert (docs_dir / "features").is_dir()
