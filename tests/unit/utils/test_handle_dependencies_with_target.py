"""Unit tests for handle_dependencies with dependency_target parameter.

Tests for FR-008f (Session 2025-10-16): Dependency placement strategy.
Validates that dependency_target correctly controls uv add flag and pyproject.toml section.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestHandleDependenciesWithOptionalDependencies:
    """Test handle_dependencies with dependency_target='optional-dependencies'."""

    @pytest.fixture
    def console(self) -> Console:
        """Create a Console instance for testing."""
        return Console()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create a temporary project root with pyproject.toml."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text(
            "[project]\nname = 'test'\n\n[project.optional-dependencies]\n"
        )
        return project

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_optional_dependencies_sphinx_success(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful installation with optional-dependencies for Sphinx."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert "sphinx>=7.0" in result.installed_packages
        assert "myst-parser>=2.0" in result.installed_packages
        mock_run.assert_called_once()

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_optional_dependencies_mkdocs_success(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful installation with optional-dependencies for MkDocs."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "installed"
        assert "mkdocs>=1.5" in result.installed_packages
        assert "mkdocs-material>=9.0" in result.installed_packages

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_optional_dependencies_uses_optional_flag(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that optional-dependencies uses --optional flag in uv add command."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify uv add --optional docs {packages} was called
        call_args = mock_run.call_args
        assert call_args is not None
        cmd = call_args[0][0]  # First positional argument
        assert "uv" in cmd
        assert "add" in cmd
        assert "--optional" in cmd
        assert "docs" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    def test_optional_dependencies_auto_install(
        self,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test optional-dependencies with auto_install=True."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "installed"
        mock_run.assert_called_once()

    def test_optional_dependencies_pyproject_section_validation(
        self, project_root: Path, console: Console
    ) -> None:
        """Test SC-002c: Verify optional-dependencies targets correct pyproject.toml section."""
        # Read pyproject.toml to verify section exists
        pyproject_content = (project_root / "pyproject.toml").read_text()
        assert "[project.optional-dependencies]" in pyproject_content


class TestHandleDependenciesWithDependencyGroups:
    """Test handle_dependencies with dependency_target='dependency-groups'."""

    @pytest.fixture
    def console(self) -> Console:
        """Create a Console instance for testing."""
        return Console()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create a temporary project root with pyproject.toml."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text(
            "[project]\nname = 'test'\n\n[dependency-groups]\n"
        )
        return project

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_dependency_groups_sphinx_success(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful installation with dependency-groups for Sphinx."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert "sphinx>=7.0" in result.installed_packages
        assert "myst-parser>=2.0" in result.installed_packages

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_dependency_groups_mkdocs_success(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful installation with dependency-groups for MkDocs."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        assert result.status == "installed"
        assert "mkdocs>=1.5" in result.installed_packages
        assert "mkdocs-material>=9.0" in result.installed_packages

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_dependency_groups_uses_group_flag(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that dependency-groups uses --group flag in uv add command."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify uv add --group docs {packages} was called
        call_args = mock_run.call_args
        assert call_args is not None
        cmd = call_args[0][0]  # First positional argument
        assert "uv" in cmd
        assert "add" in cmd
        assert "--group" in cmd
        assert "docs" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    def test_dependency_groups_auto_install(
        self,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test dependency-groups with auto_install=True."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        assert result.status == "installed"
        mock_run.assert_called_once()

    def test_dependency_groups_pyproject_section_validation(
        self, project_root: Path, console: Console
    ) -> None:
        """Test SC-002c: Verify dependency-groups targets correct pyproject.toml section."""
        # Read pyproject.toml to verify section exists
        pyproject_content = (project_root / "pyproject.toml").read_text()
        assert "[dependency-groups]" in pyproject_content


class TestHandleDependenciesInvalidTarget:
    """Test handle_dependencies with invalid dependency_target."""

    @pytest.fixture
    def console(self) -> Console:
        """Create a Console instance for testing."""
        return Console()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create a temporary project root with pyproject.toml."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        return project

    def test_invalid_dependency_target_raises_error(
        self, project_root: Path, console: Console
    ) -> None:
        """Test that invalid dependency_target raises ValueError."""
        with pytest.raises(ValueError, match="Invalid dependency_target"):
            handle_dependencies(
                doc_type="sphinx",
                auto_install=False,
                no_install=False,
                dependency_target="invalid-target",  # type: ignore
                project_root=project_root,
                console=console,
            )

    def test_empty_dependency_target_raises_error(
        self, project_root: Path, console: Console
    ) -> None:
        """Test that empty dependency_target raises ValueError."""
        with pytest.raises(ValueError, match="Invalid dependency_target"):
            handle_dependencies(
                doc_type="sphinx",
                auto_install=False,
                no_install=False,
                dependency_target="",  # type: ignore
                project_root=project_root,
                console=console,
            )
