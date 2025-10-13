"""Unit tests for NavigationUpdater (T024)."""

from speckit_docs.generators.navigation import NavigationUpdater
from speckit_docs.models import GeneratorTool


class TestNavigationUpdater:
    """Tests for NavigationUpdater class."""

    def test_update_sphinx_toctree(self, tmp_path):
        """Test Sphinx toctree update (FR-013)."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        # Create initial index.md
        index_content = """# Welcome

This is the index page.

<!-- FEATURES_TOCTREE_START -->
<!-- FEATURES_TOCTREE_END -->
"""
        (docs_dir / "index.md").write_text(index_content)

        # Create feature pages
        (docs_dir / "feature-one.md").write_text("# Feature One")
        (docs_dir / "feature-two.md").write_text("# Feature Two")

        feature_pages = [
            docs_dir / "feature-one.md",
            docs_dir / "feature-two.md",
        ]

        updater = NavigationUpdater(docs_dir, GeneratorTool.SPHINX)
        updater.update_navigation(feature_pages)

        # Verify toctree was added
        updated_content = (docs_dir / "index.md").read_text()
        assert "```{toctree}" in updated_content
        assert "feature-one" in updated_content
        assert "feature-two" in updated_content

    def test_update_sphinx_toctree_comprehensive(self, tmp_path):
        """Test Sphinx toctree update with comprehensive structure."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "features").mkdir()

        # Create initial index.md
        (docs_dir / "index.md").write_text("# Welcome\n\n")

        # Create feature pages in features/ subdirectory
        (docs_dir / "features" / "feature-one.md").write_text("# Feature One")
        (docs_dir / "features" / "feature-two.md").write_text("# Feature Two")

        feature_pages = [
            docs_dir / "features" / "feature-one.md",
            docs_dir / "features" / "feature-two.md",
        ]

        updater = NavigationUpdater(docs_dir, GeneratorTool.SPHINX)
        updater.update_navigation(feature_pages)

        # Verify toctree uses relative paths
        updated_content = (docs_dir / "index.md").read_text()
        assert "features/feature-one" in updated_content
        assert "features/feature-two" in updated_content

    def test_update_mkdocs_nav(self, tmp_path):
        """Test MkDocs nav update (FR-014)."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        # Create initial mkdocs.yml
        mkdocs_content = """site_name: Test Project
theme:
  name: material
nav:
  - Home: index.md
"""
        (tmp_path / "mkdocs.yml").write_text(mkdocs_content)

        # Create feature pages
        (docs_dir / "feature-one.md").write_text("# Feature One")
        (docs_dir / "feature-two.md").write_text("# Feature Two")

        feature_pages = [
            docs_dir / "feature-one.md",
            docs_dir / "feature-two.md",
        ]

        updater = NavigationUpdater(docs_dir, GeneratorTool.MKDOCS)
        updater.update_navigation(feature_pages)

        # Verify nav was updated
        updated_content = (tmp_path / "mkdocs.yml").read_text()
        assert "feature-one.md" in updated_content
        assert "feature-two.md" in updated_content
        assert "Features:" in updated_content

    def test_update_mkdocs_nav_comprehensive(self, tmp_path):
        """Test MkDocs nav update with comprehensive structure."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "features").mkdir()

        # Create initial mkdocs.yml
        mkdocs_content = """site_name: Test Project
nav:
  - Home: index.md
"""
        (tmp_path / "mkdocs.yml").write_text(mkdocs_content)

        # Create feature pages in features/ subdirectory
        (docs_dir / "features" / "feature-one.md").write_text("# Feature One")

        feature_pages = [
            docs_dir / "features" / "feature-one.md",
        ]

        updater = NavigationUpdater(docs_dir, GeneratorTool.MKDOCS)
        updater.update_navigation(feature_pages)

        # Verify nav uses relative paths
        updated_content = (tmp_path / "mkdocs.yml").read_text()
        assert "features/feature-one.md" in updated_content

    def test_update_navigation_empty_list(self, tmp_path):
        """Test that empty feature list doesn't break navigation."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        # Create initial index.md
        (docs_dir / "index.md").write_text("# Welcome\n\n")

        updater = NavigationUpdater(docs_dir, GeneratorTool.SPHINX)
        updater.update_navigation([])

        # Should complete without error
        assert (docs_dir / "index.md").exists()

    def test_update_sphinx_replaces_existing_toctree(self, tmp_path):
        """Test that existing toctree is replaced, not duplicated."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        # Create index.md with existing toctree
        index_content = """# Welcome

<!-- FEATURES_TOCTREE_START -->
```{toctree}
:maxdepth: 2
:caption: Features

old-feature
```
<!-- FEATURES_TOCTREE_END -->
"""
        (docs_dir / "index.md").write_text(index_content)

        # Create new feature page
        (docs_dir / "new-feature.md").write_text("# New Feature")

        feature_pages = [docs_dir / "new-feature.md"]

        updater = NavigationUpdater(docs_dir, GeneratorTool.SPHINX)
        updater.update_navigation(feature_pages)

        # Verify old toctree was replaced
        updated_content = (docs_dir / "index.md").read_text()
        assert "new-feature" in updated_content
        assert "old-feature" not in updated_content
        assert updated_content.count("```{toctree}") == 1  # No duplication
