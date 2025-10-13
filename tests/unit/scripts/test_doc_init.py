"""Unit tests for doc_init.py (T020)."""

from pathlib import Path

import pytest

from speckit_docs.scripts.doc_init import main


class TestDocInit:
    """Tests for doc_init main function."""

    def test_doc_init_sphinx_basic(self, tmp_path, monkeypatch):
        """Test basic Sphinx project initialization."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        (tmp_path / "specs" / "001-test").mkdir(parents=True)
        (tmp_path / "specs" / "001-test" / "spec.md").write_text("# Test")

        # Run doc_init
        result = main(
            doc_type="sphinx",
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
            force=False,
        )

        # Verify success
        assert result == 0

        # Verify files were created
        assert (tmp_path / "docs" / "conf.py").exists()
        assert (tmp_path / "docs" / "index.md").exists()

        # Verify conf.py content
        conf_content = (tmp_path / "docs" / "conf.py").read_text()
        assert "Test Project" in conf_content
        assert "Test Author" in conf_content
        assert "myst_parser" in conf_content

    def test_doc_init_mkdocs_basic(self, tmp_path, monkeypatch):
        """Test basic MkDocs project initialization."""
        # Setup project structure
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        (tmp_path / "specs" / "001-test").mkdir(parents=True)
        (tmp_path / "specs" / "001-test" / "spec.md").write_text("# Test")

        # Run doc_init
        result = main(
            doc_type="mkdocs",
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
            force=False,
        )

        # Verify success
        assert result == 0

        # Verify files were created
        assert (tmp_path / "mkdocs.yml").exists()
        assert (tmp_path / "docs" / "index.md").exists()

        # Verify mkdocs.yml content
        config_content = (tmp_path / "mkdocs.yml").read_text()
        assert "Test Project" in config_content
        assert "Test Author" in config_content

    def test_doc_init_flat_structure(self, tmp_path, monkeypatch):
        """Test FLAT structure creation for ≤5 features."""
        # Setup project with 3 features
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        for i in range(1, 4):
            feature_dir = tmp_path / "specs" / f"00{i}-feature{i}"
            feature_dir.mkdir(parents=True)
            (feature_dir / "spec.md").write_text(f"# Feature {i}")

        # Run doc_init
        result = main(
            doc_type="sphinx",
            project_name="Test",
            author="Test",
            force=False,
        )

        assert result == 0

        # Verify FLAT structure (no subdirectories)
        docs_dir = tmp_path / "docs"
        assert not (docs_dir / "features").exists()
        assert not (docs_dir / "guides").exists()

    def test_doc_init_comprehensive_structure(self, tmp_path, monkeypatch):
        """Test COMPREHENSIVE structure creation for >5 features."""
        # Setup project with 6 features
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        for i in range(1, 7):
            feature_dir = tmp_path / "specs" / f"00{i}-feature{i}"
            feature_dir.mkdir(parents=True)
            (feature_dir / "spec.md").write_text(f"# Feature {i}")

        # Run doc_init
        result = main(
            doc_type="sphinx",
            project_name="Test",
            author="Test",
            force=False,
        )

        assert result == 0

        # Verify COMPREHENSIVE structure
        docs_dir = tmp_path / "docs"
        assert (docs_dir / "features").exists()
        assert (docs_dir / "guides").exists()
        assert (docs_dir / "api").exists()
        assert (docs_dir / "architecture").exists()

    def test_doc_init_default_project_name(self, tmp_path, monkeypatch):
        """Test that project name defaults to directory name."""
        # Setup
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        (tmp_path / "specs" / "001-test").mkdir(parents=True)
        (tmp_path / "specs" / "001-test" / "spec.md").write_text("# Test")

        # Run without project_name
        result = main(
            doc_type="sphinx",
            project_name=None,  # Should default to tmp_path.name
            author="Test",
            force=False,
        )

        assert result == 0

        # Verify default name was used
        conf_content = (tmp_path / "docs" / "conf.py").read_text()
        assert tmp_path.name in conf_content

    def test_doc_init_force_overwrites(self, tmp_path, monkeypatch):
        """Test that --force overwrites existing docs/."""
        # Setup existing docs/
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "existing.txt").write_text("old content")
        (tmp_path / "specs" / "001-test").mkdir(parents=True)
        (tmp_path / "specs" / "001-test" / "spec.md").write_text("# Test")

        # Run with force
        result = main(
            doc_type="sphinx",
            project_name="Test",
            author="Test",
            force=True,
        )

        assert result == 0

        # Verify new files created
        assert (tmp_path / "docs" / "conf.py").exists()
        assert (tmp_path / "docs" / "index.md").exists()

    def test_doc_init_fails_without_force(self, tmp_path, monkeypatch):
        """Test that existing docs/ without --force returns error."""
        # Setup existing docs/
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()
        (tmp_path / "docs").mkdir()
        (tmp_path / "specs" / "001-test").mkdir(parents=True)
        (tmp_path / "specs" / "001-test" / "spec.md").write_text("# Test")

        # Run without force
        result = main(
            doc_type="sphinx",
            project_name="Test",
            author="Test",
            force=False,
        )

        # Should return error code
        assert result != 0
