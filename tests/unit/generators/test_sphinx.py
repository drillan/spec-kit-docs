"""Unit tests for SphinxGenerator (T017)."""

from speckit_docs.generators.base import GeneratorConfig
from speckit_docs.generators.sphinx import SphinxGenerator
from speckit_docs.models import StructureType


class TestSphinxGenerator:
    """Tests for SphinxGenerator class."""

    def test_sphinx_generator_generate_config(self, tmp_path):
        """Test generating Sphinx conf.py."""
        # Create generator
        config = GeneratorConfig(
            tool="sphinx",
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
        )
        generator = SphinxGenerator(config, tmp_path)

        # Generate config
        generator.generate_config(
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
        )

        # Verify conf.py exists
        conf_py = tmp_path / "docs" / "conf.py"
        assert conf_py.exists(), "conf.py should be created"

        # Verify content
        content = conf_py.read_text()
        assert "Test Project" in content
        assert "Test Author" in content
        assert "1.0.0" in content

    def test_sphinx_generator_generate_index(self, tmp_path):
        """Test generating index.md."""
        # Create generator
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Set structure type
        generator.structure_type = StructureType.FLAT

        # Generate index
        generator.generate_index()

        # Verify index.md exists
        index_md = tmp_path / "docs" / "index.md"
        assert index_md.exists(), "index.md should be created"

        # Verify it's Markdown format
        content = index_md.read_text()
        assert len(content) > 0

    def test_sphinx_generator_init_project(self, tmp_path):
        """Test init_project() creates all required Sphinx files."""
        # Create generator
        config = GeneratorConfig(
            tool="sphinx",
            project_name="Init Test Project",
            author="Init Test Author",
            version="2.0.0",
            language="en",
        )
        generator = SphinxGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Verify all expected files exist
        docs_dir = tmp_path / "docs"
        assert (docs_dir / "conf.py").exists(), "conf.py should be created"
        assert (docs_dir / "index.md").exists(), "index.md should be created"
        assert (docs_dir / "Makefile").exists(), "Makefile should be created"
        assert (docs_dir / "make.bat").exists(), "make.bat should be created"

    def test_sphinx_generator_init_project_includes_myst_parser(self, tmp_path):
        """Test that init_project() includes myst-parser configuration (FR-005a, T019)."""
        # Create generator
        config = GeneratorConfig(
            tool="sphinx",
            project_name="MyST Test",
            author="MyST Author",
            version="1.0.0",
        )
        generator = SphinxGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Read generated conf.py
        conf_py_path = tmp_path / "docs" / "conf.py"
        assert conf_py_path.exists()

        content = conf_py_path.read_text()

        # Verify myst-parser is in extensions
        assert "myst_parser" in content, "conf.py must include myst_parser in extensions"

        # Verify source_suffix configuration for Markdown
        assert "source_suffix" in content, "conf.py must define source_suffix"
        assert ".md" in content or "markdown" in content, "conf.py must support .md files"

    def test_sphinx_generator_create_directory_structure_flat(self, tmp_path):
        """Test creating FLAT directory structure (≤5 features)."""
        # Create generator
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Create directory structure for 5 features
        generator.create_directory_structure()

        # Verify docs directory exists
        docs_dir = tmp_path / "docs"
        assert docs_dir.exists()

        # Verify no subdirectories for FLAT structure
        assert not (docs_dir / "features").exists()
        assert not (docs_dir / "guides").exists()

    def test_sphinx_generator_create_directory_structure_comprehensive(self, tmp_path):
        """Test creating COMPREHENSIVE directory structure (>5 features)."""
        # Create generator
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Set structure type to COMPREHENSIVE
        generator.structure_type = StructureType.COMPREHENSIVE

        # Create directory structure
        generator.create_directory_structure()

        # Verify docs directory exists
        docs_dir = tmp_path / "docs"
        assert docs_dir.exists()

        # Verify subdirectories for COMPREHENSIVE structure
        assert (docs_dir / "features").exists()
        assert (docs_dir / "guides").exists()
        assert (docs_dir / "api").exists()
        assert (docs_dir / "architecture").exists()

    def test_sphinx_generator_structure_type_determination(self, tmp_path):
        """Test that structure type is set based on feature count."""
        # Create generator
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Test with 5 features (FLAT)
        assert generator.determine_structure(5) == StructureType.FLAT

        # Test with 6 features (COMPREHENSIVE)
        assert generator.determine_structure(6) == StructureType.COMPREHENSIVE

    def test_sphinx_generator_integration(self, tmp_path):
        """Test full Sphinx project initialization."""
        # Create generator
        config = GeneratorConfig(
            tool="sphinx",
            project_name="Integration Test",
            author="Test Author",
            version="0.1.0",
            language="ja",
        )
        generator = SphinxGenerator(config, tmp_path)

        # Create directory structure
        generator.create_directory_structure()

        # Generate config
        generator.generate_config(
            project_name=config.project_name,
            author=config.author,
            version=config.version,
            language=config.language,
        )

        # Generate index
        generator.generate_index()

        # Verify all files exist
        docs_dir = tmp_path / "docs"
        assert (docs_dir / "conf.py").exists()
        assert (docs_dir / "index.md").exists()
