"""Unit tests for generator classes.

This module tests SphinxGenerator and MkDocsGenerator classes per TDD Red phase.
Tests are written before implementation to verify expected behavior.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

# Try to import generators - will fail in RED phase (expected)
try:
    from speckit_docs.generators import GeneratorConfig
    from speckit_docs.generators.mkdocs import MkDocsGenerator
    from speckit_docs.generators.sphinx import SphinxGenerator

    GENERATORS_AVAILABLE = True
except ImportError:
    GENERATORS_AVAILABLE = False

    # Define placeholder classes for test collection
    class SphinxGenerator:
        pass

    class MkDocsGenerator:
        pass

    class GeneratorConfig:
        pass


# Skip all tests if generators not yet implemented (TDD RED phase)
pytestmark = pytest.mark.skipif(
    not GENERATORS_AVAILABLE, reason="Generators not yet implemented - TDD RED phase"
)


class TestSphinxGenerator:
    """Test suite for SphinxGenerator class."""

    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory for docs/ output."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sphinx_config(self):
        """Create a test configuration for Sphinx."""
        return GeneratorConfig(
            tool="sphinx",
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
        )

    def test_init_project_creates_conf_py(self, temp_docs_dir, sphinx_config):
        """Test that init_project() creates conf.py with myst_parser configuration.

        Per file-formats.md Section 1: conf.py must contain myst_parser extension.
        TDD Red phase: This test should FAIL until SphinxGenerator.init_project() is implemented.
        """
        # Create project_root that contains docs/
        project_root = temp_docs_dir.parent
        generator = SphinxGenerator(sphinx_config, project_root)
        generator.init_project()

        conf_py_path = generator.docs_dir / "conf.py"
        assert conf_py_path.exists(), "conf.py should be created"

        conf_content = conf_py_path.read_text()
        assert "myst_parser" in conf_content, "conf.py must include myst_parser extension"
        assert "source_suffix" in conf_content, "conf.py must define source_suffix"
        assert "myst_enable_extensions" in conf_content, "conf.py must enable MyST extensions"

    def test_init_project_creates_index_md(self, temp_docs_dir, sphinx_config):
        """Test that init_project() creates index.md with proper structure.

        Per file-formats.md Section 2: index.md must be Markdown format with MyST syntax.
        TDD Red phase: This test should FAIL until SphinxGenerator.init_project() is implemented.
        """
        project_root = temp_docs_dir.parent
        generator = SphinxGenerator(sphinx_config, project_root)
        generator.init_project()

        index_md_path = generator.docs_dir / "index.md"
        assert index_md_path.exists(), "index.md should be created"

        index_content = index_md_path.read_text()
        assert (
            "# Test Project" in index_content or "Test Project" in index_content
        ), "index.md should contain project name"

    def test_init_project_creates_makefile(self, temp_docs_dir, sphinx_config):
        """Test that init_project() creates Makefile for building docs.

        Per file-formats.md Section 3: Makefile for Unix-like systems.
        TDD Red phase: This test should FAIL until SphinxGenerator.init_project() is implemented.
        """
        project_root = temp_docs_dir.parent
        generator = SphinxGenerator(sphinx_config, project_root)
        generator.init_project()

        makefile_path = generator.docs_dir / "Makefile"
        assert makefile_path.exists(), "Makefile should be created"

        makefile_content = makefile_path.read_text()
        assert "html" in makefile_content, "Makefile must support html target"

    def test_init_project_creates_make_bat(self, temp_docs_dir, sphinx_config):
        """Test that init_project() creates make.bat for Windows.

        Per file-formats.md Section 4: make.bat for Windows systems.
        TDD Red phase: This test should FAIL until SphinxGenerator.init_project() is implemented.
        """
        project_root = temp_docs_dir.parent
        generator = SphinxGenerator(sphinx_config, project_root)
        generator.init_project()

        make_bat_path = generator.docs_dir / "make.bat"
        assert make_bat_path.exists(), "make.bat should be created"


class TestMkDocsGenerator:
    """Test suite for MkDocsGenerator class."""

    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory for docs/ output."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mkdocs_config(self):
        """Create a test configuration for MkDocs."""
        return GeneratorConfig(
            tool="mkdocs",
            project_name="Test Project",
            site_name="Test Site",
            repo_url="https://github.com/test/repo",
        )

    def test_init_project_creates_mkdocs_yml(self, temp_docs_dir, mkdocs_config):
        """Test that init_project() creates mkdocs.yml with correct structure.

        Per file-formats.md Section 5: mkdocs.yml must contain site_name, nav, theme.
        TDD Red phase: This test should FAIL until MkDocsGenerator.init_project() is implemented.
        """
        project_root = temp_docs_dir.parent
        generator = MkDocsGenerator(mkdocs_config, project_root)
        generator.init_project()

        mkdocs_yml_path = project_root / "mkdocs.yml"
        assert mkdocs_yml_path.exists(), "mkdocs.yml should be created"

        mkdocs_content = mkdocs_yml_path.read_text()
        assert "site_name:" in mkdocs_content, "mkdocs.yml must define site_name"
        assert "nav:" in mkdocs_content, "mkdocs.yml must define nav section"
        assert "theme:" in mkdocs_content, "mkdocs.yml must define theme"

    def test_init_project_creates_index_md(self, temp_docs_dir, mkdocs_config):
        """Test that init_project() creates docs/index.md.

        Per file-formats.md Section 6: index.md must be in docs/ subdirectory for MkDocs.
        TDD Red phase: This test should FAIL until MkDocsGenerator.init_project() is implemented.
        """
        project_root = temp_docs_dir.parent
        generator = MkDocsGenerator(mkdocs_config, project_root)
        generator.init_project()

        index_md_path = generator.docs_dir / "index.md"
        assert index_md_path.exists(), "docs/index.md should be created"

        index_content = index_md_path.read_text()
        assert (
            "Test Project" in index_content or "Test Site" in index_content
        ), "index.md should contain project/site name"
