"""Unit tests for doc_update.py (T025)."""

from pathlib import Path

import pytest

from speckit_docs.scripts.doc_update import main


class TestDocUpdate:
    """Tests for doc_update main function."""

    def test_doc_update_sphinx_basic(self, tmp_path, monkeypatch):
        """Test basic documentation update for Sphinx."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create spec-kit features
        (tmp_path / "specs" / "001-feature-one").mkdir(parents=True)
        (tmp_path / "specs" / "001-feature-one" / "spec.md").write_text(
            "# Feature One\n\n## Overview\n\nFirst feature"
        )

        (tmp_path / "specs" / "002-feature-two").mkdir(parents=True)
        (tmp_path / "specs" / "002-feature-two" / "spec.md").write_text(
            "# Feature Two\n\n## Overview\n\nSecond feature"
        )

        # Run doc_update (full mode to avoid git dependency)
        result = main(incremental=False)

        # Verify success
        assert result == 0

        # Verify feature pages were created
        assert (docs_dir / "feature-one.md").exists()
        assert (docs_dir / "feature-two.md").exists()

        # Verify content
        content1 = (docs_dir / "feature-one.md").read_text()
        assert "Feature One" in content1
        assert "First feature" in content1

        # Verify navigation was updated
        index_content = (docs_dir / "index.md").read_text()
        assert "feature-one" in index_content
        assert "feature-two" in index_content

    def test_doc_update_mkdocs_basic(self, tmp_path, monkeypatch):
        """Test basic documentation update for MkDocs."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create MkDocs docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create mkdocs.yml
        (tmp_path / "mkdocs.yml").write_text(
            """site_name: Test Project
nav:
  - Home: index.md
"""
        )

        # Create spec-kit feature
        (tmp_path / "specs" / "001-test-feature").mkdir(parents=True)
        (tmp_path / "specs" / "001-test-feature" / "spec.md").write_text(
            "# Test Feature\n\n## Requirements"
        )

        # Run doc_update (full mode)
        result = main(incremental=False)

        # Verify success
        assert result == 0

        # Verify feature page was created
        assert (docs_dir / "test-feature.md").exists()

        # Verify navigation was updated in mkdocs.yml
        mkdocs_content = (tmp_path / "mkdocs.yml").read_text()
        assert "test-feature.md" in mkdocs_content

    def test_doc_update_comprehensive_structure(self, tmp_path, monkeypatch):
        """Test documentation update with COMPREHENSIVE structure."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs with COMPREHENSIVE structure
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")
        (docs_dir / "features").mkdir()  # Indicates COMPREHENSIVE structure

        # Create spec-kit feature
        (tmp_path / "specs" / "001-test-feature").mkdir(parents=True)
        (tmp_path / "specs" / "001-test-feature" / "spec.md").write_text(
            "# Test Feature"
        )

        # Run doc_update (full mode)
        result = main(incremental=False)

        # Verify success
        assert result == 0

        # Verify feature page was created in features/ subdirectory
        assert (docs_dir / "features" / "test-feature.md").exists()
        assert not (docs_dir / "test-feature.md").exists()

    def test_doc_update_with_plan_and_tasks(self, tmp_path, monkeypatch):
        """Test documentation update includes plan.md and tasks.md."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create spec-kit feature with all files
        feature_dir = tmp_path / "specs" / "001-complete-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# Complete Feature\n\n## Overview")
        (feature_dir / "plan.md").write_text("# Plan\n\n## Architecture\n\nLayered")
        (feature_dir / "tasks.md").write_text("# Tasks\n\n## T001: First Task")

        # Run doc_update (full mode)
        result = main(incremental=False)

        # Verify success
        assert result == 0

        # Verify page includes all content
        page_content = (docs_dir / "complete-feature.md").read_text()
        assert "Complete Feature" in page_content
        assert "Architecture" in page_content or "Layered" in page_content
        assert "T001" in page_content or "Tasks" in page_content

    def test_doc_update_no_docs_directory(self, tmp_path, monkeypatch):
        """Test error when docs/ directory doesn't exist."""
        # Setup project structure without docs/
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Run doc_update
        result = main(incremental=False)

        # Should return error code
        assert result != 0

    def test_doc_update_no_features(self, tmp_path, monkeypatch):
        """Test error when no features found in specs/."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # No specs/ directory or empty
        (tmp_path / "specs").mkdir()

        # Run doc_update
        result = main(incremental=False)

        # Should return error code
        assert result != 0

    def test_doc_update_full_mode(self, tmp_path, monkeypatch):
        """Test that --full mode processes all features."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create multiple features
        for i in range(1, 4):
            feature_dir = tmp_path / f"specs/{i:03d}-feature-{i}"
            feature_dir.mkdir(parents=True)
            (feature_dir / "spec.md").write_text(f"# Feature {i}")

        # Run doc_update in full mode
        result = main(incremental=False)

        # Verify success
        assert result == 0

        # Verify all feature pages were created
        assert (docs_dir / "feature-1.md").exists()
        assert (docs_dir / "feature-2.md").exists()
        assert (docs_dir / "feature-3.md").exists()
