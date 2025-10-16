"""Integration tests for doc-init with optional-dependencies placement.

Tests for FR-008f (Session 2025-10-16): Dependency placement strategy.
Validates that dependency_target='optional-dependencies' correctly:
1. Uses uv add --optional docs {packages}
2. Installs to [project.optional-dependencies.docs] section (SC-002c)
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestDocInitOptionalDependencies:
    """Integration tests for optional-dependencies placement strategy."""

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create a temporary project root with pyproject.toml."""
        project = tmp_path / "test_project"
        project.mkdir()
        pyproject = project / "pyproject.toml"
        pyproject.write_text(
            """[project]
name = "test-project"
version = "0.1.0"
dependencies = []

[project.optional-dependencies]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
        )
        return project

    @pytest.fixture
    def console(self) -> Console:
        """Create a Console instance for testing."""
        return Console()

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_optional_dependencies_sphinx_installation(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test Sphinx installation with optional-dependencies placement."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None  # Packages not installed
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert len(result.installed_packages) == 2
        assert "sphinx>=7.0" in result.installed_packages
        assert "myst-parser>=2.0" in result.installed_packages

        # Verify subprocess call uses --optional flag
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "uv"
        assert cmd[1] == "add"
        assert "--optional" in cmd
        assert "docs" in cmd
        assert "sphinx>=7.0" in cmd
        assert "myst-parser>=2.0" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_optional_dependencies_mkdocs_installation(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test MkDocs installation with optional-dependencies placement."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Execute
        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "installed"
        assert len(result.installed_packages) == 2
        assert "mkdocs>=1.5" in result.installed_packages
        assert "mkdocs-material>=9.0" in result.installed_packages

        # Verify --optional flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--optional" in cmd
        assert "docs" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    def test_optional_dependencies_auto_install_mode(
        self,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test optional-dependencies with --auto-install flag (CI/CD mode)."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Execute with auto_install=True
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify
        assert result.status == "installed"
        assert len(result.installed_packages) == 2

        # Verify command uses --optional
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--optional" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_sc_002c_optional_dependencies_section_placement(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test SC-002c: Verify optional-dependencies targets correct pyproject.toml section.

        Success Criterion SC-002c:
        100% correct placement in [project.optional-dependencies.docs] when
        dependency_target='optional-dependencies'.
        """
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify installation succeeded
        assert result.status == "installed"

        # Verify pyproject.toml section exists
        pyproject_content = (project_root / "pyproject.toml").read_text()
        assert "[project.optional-dependencies]" in pyproject_content

        # Verify uv add command targets correct section
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--optional" in cmd
        assert "docs" in cmd

        # Verify NOT using --group (dependency-groups)
        assert "--group" not in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_optional_dependencies_timeout_setting(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that optional-dependencies installation respects 300s timeout."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "installed"

        # Verify timeout is set to 300 seconds
        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 300
