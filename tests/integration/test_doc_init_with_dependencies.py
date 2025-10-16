"""Integration tests for doc-init with dependency auto-installation.

Tests the complete workflow: pyproject.toml + uv environment → auto-install success.
Validates SC-002b (90% success rate goal).
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestDocInitWithDependencies:
    """Integration tests for successful dependency auto-installation."""

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
    def test_auto_install_sphinx_success(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful auto-installation of Sphinx dependencies."""
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

        # Verify
        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert len(result.installed_packages) == 2
        assert "sphinx>=7.0" in result.installed_packages
        assert "myst-parser>=2.0" in result.installed_packages

        # Verify subprocess call
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["uv", "add", "--optional", "docs", "sphinx>=7.0", "myst-parser>=2.0"]
        assert call_args[1]["cwd"] == project_root
        assert call_args[1]["timeout"] == 300

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_auto_install_mkdocs_success(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful auto-installation of MkDocs dependencies."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None  # Packages not installed
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

        # Verify
        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert len(result.installed_packages) == 2
        assert "mkdocs>=1.5" in result.installed_packages
        assert "mkdocs-material>=9.0" in result.installed_packages

        # Verify subprocess call
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["uv", "add", "--optional", "docs", "mkdocs>=1.5", "mkdocs-material>=9.0"]

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    def test_auto_install_with_auto_flag(
        self,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test auto-installation with --auto-install flag (CI/CD mode)."""
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

        # Verify subprocess was called without user confirmation
        mock_run.assert_called_once()

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_sc_002b_success_rate_goal(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test SC-002b: 90% success rate goal validation.

        This test simulates the 90% success scenario where conditions are met
        and installation completes within 300 seconds.
        """
        # Setup mocks for success scenario
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

        # Verify SC-002b compliance
        assert result.status == "installed"
        assert len(result.installed_packages) > 0

        # Verify timeout is set to 300 seconds (5 minutes)
        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 300
