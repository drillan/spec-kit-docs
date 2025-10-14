"""Unit tests for SphinxGenerator (T017)."""

from pathlib import Path

from speckit_docs.generators.base import GeneratorConfig
from speckit_docs.generators.sphinx import SphinxGenerator
from speckit_docs.models import Feature, FeatureStatus, StructureType


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

    def test_sphinx_generator_validate_project(self, tmp_path):
        """Test validate_project() method."""
        # Create generator
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Validate project
        result = generator.validate_project()

        # Verify validation passes
        assert result.is_valid
        assert len(result.errors) == 0
        assert "conf.py exists" in result.checked_items
        assert "myst_parser configured" in result.checked_items

    def test_sphinx_generator_validate_project_missing_files(self, tmp_path):
        """Test validate_project() detects missing files."""
        # Create generator without initializing
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Validate without creating files
        result = generator.validate_project()

        # Verify validation fails
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_sphinx_generator_update_docs_empty_features(self, tmp_path):
        """Test update_docs() with empty features list."""

        # Create generator
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Initialize project first
        generator.init_project()

        # Update with empty features list
        generator.update_docs([], incremental=False)

        # Verify index.md still exists
        index_md = tmp_path / "docs" / "index.md"
        assert index_md.exists()

    def test_sphinx_generator_update_docs_with_features(self, tmp_path):
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
        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Initialize project
        generator.init_project()

        # Update with feature
        generator.update_docs([feature], incremental=False)

        # Verify feature doc was created
        feature_doc = tmp_path / "docs" / "test-feature.md"
        assert feature_doc.exists()

    def test_sphinx_generator_get_feature_doc_path_flat(self, tmp_path):
        """Test get_feature_doc_path() for FLAT structure."""
        from speckit_docs.models import Feature, FeatureStatus

        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        feature = Feature(
            id="001",
            name="my-feature",
            directory_path=tmp_path / "specs" / "001-my-feature",
            spec_file=tmp_path / "specs" / "001-my-feature" / "spec.md",
            status=FeatureStatus.DRAFT,
        )

        path = generator.get_feature_doc_path(feature, "FLAT")
        assert path == tmp_path / "docs" / "my-feature.md"

    def test_sphinx_generator_get_feature_doc_path_comprehensive(self, tmp_path):
        """Test get_feature_doc_path() for COMPREHENSIVE structure."""
        from speckit_docs.models import Feature, FeatureStatus

        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        feature = Feature(
            id="001",
            name="my-feature",
            directory_path=tmp_path / "specs" / "001-my-feature",
            spec_file=tmp_path / "specs" / "001-my-feature" / "spec.md",
            status=FeatureStatus.DRAFT,
        )

        path = generator.get_feature_doc_path(feature, "COMPREHENSIVE")
        assert path == tmp_path / "docs" / "features" / "my-feature.md"

    def test_sphinx_generator_build_docs_make_not_installed(self, tmp_path, monkeypatch):
        """Test build_docs() when make is not installed."""
        import subprocess

        from speckit_docs.utils.validation import BuildError

        config = GeneratorConfig(tool="sphinx", project_name="Test Project")
        generator = SphinxGenerator(config, tmp_path)

        # Initialize project first
        generator.init_project()

        # Mock subprocess.run to raise FileNotFoundError (make not found)
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("make not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Should raise BuildError with helpful message about make
        import pytest

        with pytest.raises(BuildError) as exc_info:
            generator.build_docs()

        assert "makeコマンドが見つかりません" in str(exc_info.value)

    def test_validate_project_success(self, tmp_path):
        """Test validate_project with valid Sphinx project."""
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        
        # Create necessary files
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "conf.py").write_text("extensions = ['myst_parser']")
        (tmp_path / "docs" / "index.md").write_text("# Test")
        (tmp_path / "docs" / "Makefile").write_text("html:")
        
        result = generator.validate_project()
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert "conf.py exists" in result.checked_items
        assert "myst_parser configured" in result.checked_items

    def test_validate_project_missing_conf(self, tmp_path):
        """Test validate_project with missing conf.py."""
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        
        # Create docs dir but no conf.py
        (tmp_path / "docs").mkdir()
        
        result = generator.validate_project()
        
        assert result.is_valid is False
        assert any("conf.py" in e for e in result.errors)

    def test_sphinx_generator_build_timeout(self, tmp_path, monkeypatch):
        """Test build_docs() when build times out."""
        import subprocess
        from speckit_docs.utils.validation import BuildError
        
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
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

    def test_sphinx_generator_build_generic_error(self, tmp_path, monkeypatch):
        """Test build_docs() when unexpected error occurs."""
        import subprocess
        from speckit_docs.utils.validation import BuildError
        
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
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

    def test_sphinx_generator_template_not_found(self, tmp_path, monkeypatch):
        """Test generate_config() when template is not found."""
        from jinja2 import TemplateNotFound
        from speckit_docs.utils.validation import DocumentationProjectError
        
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        
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

    def test_sphinx_update_index_fallback(self, tmp_path, monkeypatch):
        """Test _update_index() fallback when template not found."""
        from jinja2 import TemplateNotFound
        
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        generator.init_project()
        
        # Create existing index.md
        index_path = tmp_path / "docs" / "index.md"
        index_path.write_text("# Test Project\n\nWelcome\n")
        
        # Mock jinja_env.get_template to raise TemplateNotFound for index template
        original_get_template = generator.jinja_env.get_template
        def mock_get_template(name):
            if "index" in name:
                raise TemplateNotFound(name)
            return original_get_template(name)
        
        monkeypatch.setattr(generator.jinja_env, "get_template", mock_get_template)
        
        # Call update_docs which internally calls _update_index
        features = [
            Feature(
                id="001",
                name="test-feature",
                directory_path=tmp_path / "specs" / "001-test-feature",
                spec_file=tmp_path / "specs" / "001-test-feature" / "spec.md",
                status=FeatureStatus.DRAFT,
            )
        ]
        
        # Create spec file
        (tmp_path / "specs" / "001-test-feature").mkdir(parents=True)
        (tmp_path / "specs" / "001-test-feature" / "spec.md").write_text("# Test")
        
        generator.update_docs(features, incremental=False)
        
        # Verify fallback was used (should have features section)
        content = index_path.read_text()
        assert "## 機能一覧" in content
        assert "test-feature" in content

    def test_sphinx_update_index_fallback_replace_existing(self, tmp_path, monkeypatch):
        """Test _update_index() fallback replaces existing features section."""
        from jinja2 import TemplateNotFound
        
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        generator.init_project()
        
        # Create index with existing features section
        index_path = tmp_path / "docs" / "index.md"
        index_path.write_text("# Test\n\n## 機能一覧\n\n- Old feature\n\n## Other Section\n\nContent")
        
        # Mock template not found
        def mock_get_template(name):
            if "index" in name:
                raise TemplateNotFound(name)
            raise TemplateNotFound(name)  # Fail all templates
        
        monkeypatch.setattr(generator.jinja_env, "get_template", mock_get_template)
        
        # Call _update_index directly
        features_data = [{"title": "New Feature", "file": "new-feature.md"}]
        generator._update_index(features_data, "FLAT")
        
        # Verify old section was replaced
        content = index_path.read_text()
        assert "New Feature" in content
        assert "Old feature" not in content
        assert "## Other Section" in content  # Other sections preserved

    def test_sphinx_migrate_flat_to_comprehensive(self, tmp_path, capsys):
        """Test _migrate_flat_to_comprehensive() migrates feature files."""
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        
        # Create docs directory with feature files
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create files that should be migrated
        (docs_dir / "feature-one.md").write_text("# Feature One")
        (docs_dir / "feature-two.md").write_text("# Feature Two")
        
        # Create files that should NOT be migrated
        (docs_dir / "index.md").write_text("# Index")
        (docs_dir / "conf.py").write_text("# Config")
        (docs_dir / ".gitignore").write_text("*.pyc")
        
        # Run migration
        generator._migrate_flat_to_comprehensive()
        
        # Verify files were moved
        assert (docs_dir / "features" / "feature-one.md").exists()
        assert (docs_dir / "features" / "feature-two.md").exists()
        
        # Verify excluded files stayed in place
        assert (docs_dir / "index.md").exists()
        assert (docs_dir / "conf.py").exists()
        assert (docs_dir / ".gitignore").exists()
        
        # Verify original files were moved (not copied)
        assert not (docs_dir / "feature-one.md").exists()
        assert not (docs_dir / "feature-two.md").exists()
        
        # Verify output message
        captured = capsys.readouterr()
        assert "2個のファイルを移行しました" in captured.out

    def test_sphinx_migrate_flat_to_comprehensive_no_files(self, tmp_path, capsys):
        """Test _migrate_flat_to_comprehensive() when no files to migrate."""
        config = GeneratorConfig(tool="sphinx", project_name="Test")
        generator = SphinxGenerator(config, tmp_path)
        
        # Create empty docs directory (only infrastructure files)
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Index")
        (docs_dir / "conf.py").write_text("# Config")
        
        # Run migration
        generator._migrate_flat_to_comprehensive()
        
        # Verify no files were migrated
        captured = capsys.readouterr()
        assert "移行対象のファイルはありませんでした" in captured.out
