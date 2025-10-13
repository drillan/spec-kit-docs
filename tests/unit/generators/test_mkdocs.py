"""Unit tests for MkDocsGenerator (T018)."""

from speckit_docs.generators.base import GeneratorConfig
from speckit_docs.generators.mkdocs import MkDocsGenerator
from speckit_docs.models import StructureType


class TestMkDocsGenerator:
    """Tests for MkDocsGenerator class."""

    def test_mkdocs_generator_generate_config(self, tmp_path):
        """Test generating MkDocs mkdocs.yml."""
        # Create generator
        config = GeneratorConfig(
            tool="mkdocs",
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
        )
        generator = MkDocsGenerator(config, tmp_path)

        # Generate config
        generator.generate_config(
            project_name="Test Project",
            author="Test Author",
            version="1.0.0",
            language="ja",
        )

        # Verify mkdocs.yml exists (in project root, not docs/)
        mkdocs_yml = tmp_path / "mkdocs.yml"
        assert mkdocs_yml.exists(), "mkdocs.yml should be created"

        # Verify content
        content = mkdocs_yml.read_text()
        assert "Test Project" in content
        assert "Test Author" in content

    def test_mkdocs_generator_generate_index(self, tmp_path):
        """Test generating index.md."""
        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

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

    def test_mkdocs_generator_init_project(self, tmp_path):
        """Test init_project() creates all required MkDocs files."""
        # Create generator
        config = GeneratorConfig(
            tool="mkdocs",
            project_name="Init Test Project",
            author="Init Test Author",
            version="2.0.0",
        )
        generator = MkDocsGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Verify all expected files exist
        assert (tmp_path / "mkdocs.yml").exists(), "mkdocs.yml should be created in project root"
        assert (tmp_path / "docs" / "index.md").exists(), "index.md should be created in docs/"

    def test_mkdocs_generator_init_project_includes_material_theme(self, tmp_path):
        """Test that init_project() includes Material theme configuration (T020)."""
        # Create generator
        config = GeneratorConfig(
            tool="mkdocs",
            project_name="Material Test",
            author="Material Author",
            version="1.0.0",
            theme="material",
        )
        generator = MkDocsGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Read generated mkdocs.yml
        mkdocs_yml_path = tmp_path / "mkdocs.yml"
        assert mkdocs_yml_path.exists()

        content = mkdocs_yml_path.read_text()

        # Verify Material theme is configured
        assert "theme:" in content, "mkdocs.yml must include theme configuration"
        assert "material" in content, "mkdocs.yml must specify Material theme"

    def test_mkdocs_generator_create_directory_structure_flat(self, tmp_path):
        """Test creating FLAT directory structure (≤5 features)."""
        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Create directory structure
        generator.create_directory_structure()

        # Verify docs directory exists
        docs_dir = tmp_path / "docs"
        assert docs_dir.exists()

        # Verify no subdirectories for FLAT structure
        assert not (docs_dir / "features").exists()
        assert not (docs_dir / "guides").exists()

    def test_mkdocs_generator_create_directory_structure_comprehensive(self, tmp_path):
        """Test creating COMPREHENSIVE directory structure (>5 features)."""
        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

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

    def test_mkdocs_generator_structure_type_determination(self, tmp_path):
        """Test that structure type is set based on feature count."""
        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Test with 5 features (FLAT)
        assert generator.determine_structure(5) == StructureType.FLAT

        # Test with 6 features (COMPREHENSIVE)
        assert generator.determine_structure(6) == StructureType.COMPREHENSIVE

    def test_mkdocs_generator_integration(self, tmp_path):
        """Test full MkDocs project initialization."""
        # Create generator
        config = GeneratorConfig(
            tool="mkdocs",
            project_name="Integration Test",
            author="Test Author",
            version="0.1.0",
            language="ja",
        )
        generator = MkDocsGenerator(config, tmp_path)

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
        assert (tmp_path / "mkdocs.yml").exists()
        assert (tmp_path / "docs" / "index.md").exists()
