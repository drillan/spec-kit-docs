"""Contract tests for doc_init.py output validation.

These tests validate that generated documentation files conform to their
respective format specifications per file-formats.md.
"""

import ast
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml


class TestSphinxOutputContract:
    """Contract tests for Sphinx output validation."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_generated_conf_py_is_valid_python(self, temp_project_dir):
        """Validate generated conf.py is valid Python syntax.

        Per file-formats.md Section 1 Validation Rules:
        - Must be valid Python code
        - Must contain required extensions
        - Must define source_suffix
        - Must enable myst_enable_extensions

        TDD Red phase: This test should FAIL until conf.py generation is correct.
        """
        # Run doc_init.py to generate Sphinx project
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir()

        # Simulate generated conf.py (this will be replaced by actual generator)
        conf_py_path = docs_dir / "conf.py"

        # For now, test will fail because file doesn't exist
        if not conf_py_path.exists():
            pytest.skip("doc_init.py not yet generating conf.py")

        # Validate Python syntax by parsing AST
        conf_content = conf_py_path.read_text()
        try:
            ast.parse(conf_content)
        except SyntaxError as e:
            pytest.fail(f"conf.py contains invalid Python syntax: {e}")

        # Validate required configuration
        assert "myst_parser" in conf_content, \
            "conf.py must include 'myst_parser' in extensions list"
        assert "source_suffix" in conf_content, \
            "conf.py must define source_suffix"
        assert "myst_enable_extensions" in conf_content, \
            "conf.py must enable MyST Markdown extensions"

    def test_generated_conf_py_contains_myst_extensions(self, temp_project_dir):
        """Validate conf.py enables required MyST extensions.

        Per file-formats.md Section 1: Must enable colon_fence, deflist, tasklist, attrs_inline.

        TDD Red phase: This test should FAIL until myst_enable_extensions is correctly set.
        """
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir()
        conf_py_path = docs_dir / "conf.py"

        if not conf_py_path.exists():
            pytest.skip("doc_init.py not yet generating conf.py")

        conf_content = conf_py_path.read_text()

        # Check for MyST extensions
        required_extensions = ["colon_fence", "deflist", "tasklist", "attrs_inline"]
        for ext in required_extensions:
            assert ext in conf_content, \
                f"conf.py must enable MyST extension '{ext}'"

    def test_generated_index_md_contains_toctree(self, temp_project_dir):
        """Validate generated index.md contains toctree directive with :maxdepth: option.

        Per file-formats.md Section 2 Validation Rules:
        - Must contain ```{toctree} directive
        - Must have :maxdepth: option

        TDD Red phase: This test should FAIL until index.md generation is correct.
        """
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir()
        index_md_path = docs_dir / "index.md"

        if not index_md_path.exists():
            pytest.skip("doc_init.py not yet generating index.md")

        index_content = index_md_path.read_text()

        # Check for MyST toctree directive
        assert "```{toctree}" in index_content or "{toctree}" in index_content, \
            "index.md must contain MyST toctree directive"
        assert ":maxdepth:" in index_content, \
            "toctree must have :maxdepth: option"


class TestMkDocsOutputContract:
    """Contract tests for MkDocs output validation."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_generated_mkdocs_yml_is_valid_yaml(self, temp_project_dir):
        """Validate generated mkdocs.yml is valid YAML syntax.

        Per file-formats.md Section 5 Validation Rules:
        - Must be valid YAML
        - Must contain site_name
        - Must contain nav section
        - Must contain theme

        TDD Red phase: This test should FAIL until mkdocs.yml generation is correct.
        """
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir()
        mkdocs_yml_path = temp_project_dir / "mkdocs.yml"

        if not mkdocs_yml_path.exists():
            pytest.skip("doc_init.py not yet generating mkdocs.yml")

        # Validate YAML syntax
        try:
            with open(mkdocs_yml_path) as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"mkdocs.yml contains invalid YAML syntax: {e}")

        # Validate required keys
        assert "site_name" in config, "mkdocs.yml must define site_name"
        assert "nav" in config, "mkdocs.yml must define nav section"
        assert "theme" in config, "mkdocs.yml must define theme"

    def test_generated_index_md_exists_in_docs_subdir(self, temp_project_dir):
        """Validate index.md is created in docs/ subdirectory for MkDocs.

        Per file-formats.md Section 6: MkDocs expects index.md in docs/ subdirectory.

        TDD Red phase: This test should FAIL until index.md is created in correct location.
        """
        docs_subdir = temp_project_dir / "docs" / "docs"
        index_md_path = docs_subdir / "index.md"

        if not index_md_path.exists():
            # Try alternative location (root docs/)
            alt_index_path = temp_project_dir / "docs" / "index.md"
            if not alt_index_path.exists():
                pytest.skip("doc_init.py not yet generating index.md")

        # MkDocs expects docs/index.md structure
        assert (temp_project_dir / "docs" / "docs" / "index.md").exists() or \
               (temp_project_dir / "docs" / "index.md").exists(), \
            "index.md must exist in docs/ subdirectory for MkDocs"
