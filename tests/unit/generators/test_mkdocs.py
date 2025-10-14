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

    def test_mkdocs_generator_validate_project(self, tmp_path):
        """Test validate_project() method."""
        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Validate project
        result = generator.validate_project()

        # Verify validation passes
        assert result.is_valid
        assert len(result.errors) == 0

    def test_mkdocs_generator_validate_project_missing_files(self, tmp_path):
        """Test validate_project() detects missing files."""
        # Create generator without initializing
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Validate without creating files
        result = generator.validate_project()

        # Verify validation fails
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_mkdocs_generator_update_docs_empty_features(self, tmp_path):
        """Test update_docs() with empty features list."""
        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Initialize project first
        generator.init_project()

        # Update with empty features list
        generator.update_docs([], incremental=False)

        # Verify index.md still exists
        index_md = tmp_path / "docs" / "index.md"
        assert index_md.exists()

    def test_mkdocs_generator_update_docs_with_features(self, tmp_path):
        """Test update_docs() with actual features."""
        from speckit_docs.models import Feature, FeatureStatus

        # Create mock spec.md files
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()

        feature_dir = specs_dir / "001-test-feature"
        feature_dir.mkdir()
        spec_file = feature_dir / "spec.md"
        spec_file.write_text("# Test Feature\n\nThis is a test feature.")

        # Create Feature object
        feature = Feature(
            id="001",
            name="test-feature",
            directory_path=feature_dir,
            spec_file=spec_file,
            status=FeatureStatus.DRAFT,
        )

        # Create generator
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Update with feature
        generator.update_docs([feature], incremental=False)

        # Verify feature doc was created
        feature_doc = tmp_path / "docs" / "test-feature.md"
        assert feature_doc.exists()

    def test_mkdocs_generator_get_feature_doc_path_flat(self, tmp_path):
        """Test get_feature_doc_path() for FLAT structure."""
        from speckit_docs.models import Feature, FeatureStatus

        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        feature = Feature(
            id="001",
            name="my-feature",
            directory_path=tmp_path / "specs" / "001-my-feature",
            spec_file=tmp_path / "specs" / "001-my-feature" / "spec.md",
            status=FeatureStatus.DRAFT,
        )

        path = generator.get_feature_doc_path(feature, "FLAT")
        assert path == tmp_path / "docs" / "my-feature.md"

    def test_mkdocs_generator_get_feature_doc_path_comprehensive(self, tmp_path):
        """Test get_feature_doc_path() for COMPREHENSIVE structure."""
        from speckit_docs.models import Feature, FeatureStatus

        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        feature = Feature(
            id="001",
            name="my-feature",
            directory_path=tmp_path / "specs" / "001-my-feature",
            spec_file=tmp_path / "specs" / "001-my-feature" / "spec.md",
            status=FeatureStatus.DRAFT,
        )

        path = generator.get_feature_doc_path(feature, "COMPREHENSIVE")
        assert path == tmp_path / "docs" / "features" / "my-feature.md"

    def test_mkdocs_generator_migrate_flat_to_comprehensive(self, tmp_path):
        """Test migration from FLAT to COMPREHENSIVE structure."""
        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Create FLAT structure with some feature files
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        (docs_dir / "index.md").write_text("# Index")
        (docs_dir / "feature1.md").write_text("# Feature 1")
        (docs_dir / "feature2.md").write_text("# Feature 2")

        # Run migration
        generator._migrate_flat_to_comprehensive()

        # Verify features were moved
        features_dir = docs_dir / "features"
        assert features_dir.exists()
        assert (features_dir / "feature1.md").exists()
        assert (features_dir / "feature2.md").exists()

        # Verify index.md stayed in place
        assert (docs_dir / "index.md").exists()

    def test_mkdocs_generator_build_docs_mkdocs_not_installed(self, tmp_path, monkeypatch):
        """Test build_docs() when mkdocs is not installed."""
        import subprocess

        from speckit_docs.utils.validation import BuildError

        config = GeneratorConfig(tool="mkdocs", project_name="Test Project")
        generator = MkDocsGenerator(config, tmp_path)

        # Initialize project first
        generator.init_project()

        # Mock subprocess.run to raise FileNotFoundError
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("mkdocs not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Should raise BuildError with helpful message
        import pytest

        with pytest.raises(BuildError) as exc_info:
            generator.build_docs()

        assert "mkdocsコマンドが見つかりません" in str(exc_info.value)

    def test_mkdocs_generator_build_timeout(self, tmp_path, monkeypatch):
        """Test build_docs() when build times out."""
        import subprocess
        from speckit_docs.utils.validation import BuildError
        
        config = GeneratorConfig(tool="mkdocs", project_name="Test")
        generator = MkDocsGenerator(config, tmp_path)
        generator.init_project()
        
        # Mock subprocess.run to raise TimeoutExpired
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd=args[0], timeout=300)
        
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        # Should raise BuildError about timeout
        import pytest
        with pytest.raises(BuildError) as exc_info:
            generator.build_docs()
        
        assert "タイムアウト" in str(exc_info.value)

    def test_mkdocs_generator_build_generic_error(self, tmp_path, monkeypatch):
        """Test build_docs() when unexpected error occurs."""
        import subprocess
        from speckit_docs.utils.validation import BuildError
        
        config = GeneratorConfig(tool="mkdocs", project_name="Test")
        generator = MkDocsGenerator(config, tmp_path)
        generator.init_project()
        
        # Mock subprocess.run to raise generic exception
        def mock_run(*args, **kwargs):
            raise RuntimeError("Unexpected build error")
        
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        # Should raise BuildError
        import pytest
        with pytest.raises(BuildError) as exc_info:
            generator.build_docs()
        
        assert "エラーが発生しました" in str(exc_info.value)

    def test_mkdocs_generator_build_mkdocs_not_found(self, tmp_path, monkeypatch):
        """Test build_docs() when mkdocs command is not found."""
        import subprocess
        from speckit_docs.utils.validation import BuildError
        
        config = GeneratorConfig(tool="mkdocs", project_name="Test")
        generator = MkDocsGenerator(config, tmp_path)
        generator.init_project()
        
        # Mock subprocess.run to raise FileNotFoundError
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("mkdocs not found")
        
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        # Should raise BuildError with message about mkdocs
        import pytest
        with pytest.raises(BuildError) as exc_info:
            generator.build_docs()
        
        assert "mkdocs" in str(exc_info.value).lower()

    def test_mkdocs_generator_template_not_found(self, tmp_path, monkeypatch):
        """Test generate_config() when template is not found."""
        from jinja2 import TemplateNotFound
        from speckit_docs.utils.validation import DocumentationProjectError
        
        config = GeneratorConfig(tool="mkdocs", project_name="Test")
        generator = MkDocsGenerator(config, tmp_path)
        
        # Mock jinja_env.get_template to raise TemplateNotFound
        def mock_get_template(name):
            raise TemplateNotFound(name)
        
        monkeypatch.setattr(generator.jinja_env, "get_template", mock_get_template)
        
        # Should raise SpecKitDocsError
        import pytest
        with pytest.raises(DocumentationProjectError):
            generator.generate_config(
                project_name="Test",
                author="Test",
                version="1.0.0"
            )
