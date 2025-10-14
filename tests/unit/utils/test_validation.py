"""Tests for utils.validation module."""


import pytest

from speckit_docs.utils.validation import (
    BuildError,
    DocumentationProjectError,
    GitValidationError,
    MarkdownParseError,
    ProjectValidationError,
    SpecKitDocsError,
    detect_docs_tool,
    validate_docs_project,
    validate_git_repo,
    validate_speckit_project,
)


class TestSpecKitDocsError:
    """Tests for SpecKitDocsError base exception."""

    def test_error_with_message_and_suggestion(self):
        """Test error includes both message and suggestion."""
        error = SpecKitDocsError("Something went wrong", "Try this fix")
        assert "Something went wrong" in str(error)
        assert "Try this fix" in str(error)
        assert error.message == "Something went wrong"
        assert error.suggestion == "Try this fix"

    def test_project_validation_error_inheritance(self):
        """Test ProjectValidationError inherits from SpecKitDocsError."""
        error = ProjectValidationError("Project error", "Fix project")
        assert isinstance(error, SpecKitDocsError)

    def test_git_validation_error_inheritance(self):
        """Test GitValidationError inherits from SpecKitDocsError."""
        error = GitValidationError("Git error", "Fix git")
        assert isinstance(error, SpecKitDocsError)

    def test_documentation_project_error_inheritance(self):
        """Test DocumentationProjectError inherits from SpecKitDocsError."""
        error = DocumentationProjectError("Docs error", "Fix docs")
        assert isinstance(error, SpecKitDocsError)

    def test_markdown_parse_error_inheritance(self):
        """Test MarkdownParseError inherits from SpecKitDocsError."""
        error = MarkdownParseError("Parse error", "Fix parsing")
        assert isinstance(error, SpecKitDocsError)

    def test_build_error_inheritance(self):
        """Test BuildError inherits from SpecKitDocsError."""
        error = BuildError("Build error", "Fix build")
        assert isinstance(error, SpecKitDocsError)


class TestValidateSpeckitProject:
    """Tests for validate_speckit_project() function."""

    def test_validate_with_specify_directory(self, tmp_path):
        """Test validation passes when .specify exists."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()

        result = validate_speckit_project(tmp_path)
        assert result == specify_dir

    def test_validate_without_specify_directory(self, tmp_path):
        """Test validation fails when .specify doesn't exist."""
        with pytest.raises(ProjectValidationError) as exc_info:
            validate_speckit_project(tmp_path)

        assert "spec-kitプロジェクトではありません" in str(exc_info.value)

    def test_validate_specify_is_file_not_directory(self, tmp_path):
        """Test validation fails when .specify is a file."""
        specify_file = tmp_path / ".specify"
        specify_file.write_text("not a directory")

        with pytest.raises(ProjectValidationError) as exc_info:
            validate_speckit_project(tmp_path)

        assert "ディレクトリではありません" in str(exc_info.value)


class TestValidateGitRepo:
    """Tests for validate_git_repo() function."""

    def test_validate_with_git_directory(self, tmp_path):
        """Test validation passes when .git exists."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        result = validate_git_repo(tmp_path)
        assert result == git_dir

    def test_validate_without_git_directory(self, tmp_path):
        """Test validation fails when .git doesn't exist."""
        with pytest.raises(GitValidationError) as exc_info:
            validate_git_repo(tmp_path)

        assert "Gitリポジトリではありません" in str(exc_info.value)


class TestValidateDocsProject:
    """Tests for validate_docs_project() function."""

    def test_validate_with_docs_directory(self, tmp_path):
        """Test validation passes when docs/ exists."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        result = validate_docs_project(tmp_path)
        assert result == docs_dir

    def test_validate_without_docs_directory(self, tmp_path):
        """Test validation fails when docs/ doesn't exist."""
        with pytest.raises(DocumentationProjectError) as exc_info:
            validate_docs_project(tmp_path)

        assert "ドキュメントプロジェクトが初期化されていません" in str(exc_info.value)

    def test_validate_sphinx_with_conf_py(self, tmp_path):
        """Test Sphinx validation passes when conf.py exists."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")

        result = validate_docs_project(tmp_path, require_sphinx=True)
        assert result == docs_dir

    def test_validate_sphinx_without_conf_py(self, tmp_path):
        """Test Sphinx validation fails when conf.py doesn't exist."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        with pytest.raises(DocumentationProjectError) as exc_info:
            validate_docs_project(tmp_path, require_sphinx=True)

        assert "conf.py" in str(exc_info.value)

    def test_validate_mkdocs_with_config(self, tmp_path):
        """Test MkDocs validation passes when mkdocs.yml exists."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "mkdocs.yml").write_text("site_name: Test")

        result = validate_docs_project(tmp_path, require_mkdocs=True)
        assert result == docs_dir

    def test_validate_mkdocs_without_config(self, tmp_path):
        """Test MkDocs validation fails when mkdocs.yml doesn't exist."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        with pytest.raises(DocumentationProjectError) as exc_info:
            validate_docs_project(tmp_path, require_mkdocs=True)

        assert "mkdocs.yml" in str(exc_info.value)


class TestDetectDocsTool:
    """Tests for detect_docs_tool() function."""

    def test_detect_sphinx(self, tmp_path):
        """Test detecting Sphinx project."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx")

        result = detect_docs_tool(tmp_path)
        assert result == "sphinx"

    def test_detect_mkdocs(self, tmp_path):
        """Test detecting MkDocs project."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "mkdocs.yml").write_text("site_name: Test")

        result = detect_docs_tool(tmp_path)
        assert result == "mkdocs"

    def test_detect_none_without_docs(self, tmp_path):
        """Test detecting no tool when docs/ doesn't exist."""
        result = detect_docs_tool(tmp_path)
        assert result is None

    def test_detect_none_with_empty_docs(self, tmp_path):
        """Test detecting no tool when docs/ is empty."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        result = detect_docs_tool(tmp_path)
        assert result is None

    def test_detect_sphinx_priority(self, tmp_path):
        """Test Sphinx is detected first when both configs exist."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx")
        (docs_dir / "mkdocs.yml").write_text("site_name: Test")

        result = detect_docs_tool(tmp_path)
        assert result == "sphinx"
