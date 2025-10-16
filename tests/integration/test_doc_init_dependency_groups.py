"""Integration tests for doc-init with dependency-groups placement.

Tests for FR-008f (Session 2025-10-16): Dependency placement strategy.
Validates that dependency_target='dependency-groups' correctly:
1. Uses uv add --group docs {packages}
2. Installs to [dependency-groups.docs] section (SC-002c)
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestDocInitDependencyGroups:
    """Integration tests for dependency-groups placement strategy."""

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

[dependency-groups]

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
    def test_dependency_groups_sphinx_installation(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test Sphinx installation with dependency-groups placement."""
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
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert len(result.installed_packages) == 2
        assert "sphinx>=7.0" in result.installed_packages
        assert "myst-parser>=2.0" in result.installed_packages

        # Verify subprocess call uses --group flag
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "uv"
        assert cmd[1] == "add"
        assert "--group" in cmd
        assert "docs" in cmd
        assert "sphinx>=7.0" in cmd
        assert "myst-parser>=2.0" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_dependency_groups_mkdocs_installation(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test MkDocs installation with dependency-groups placement."""
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
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "installed"
        assert len(result.installed_packages) == 2
        assert "mkdocs>=1.5" in result.installed_packages
        assert "mkdocs-material>=9.0" in result.installed_packages

        # Verify --group flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--group" in cmd
        assert "docs" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    def test_dependency_groups_auto_install_mode(
        self,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test dependency-groups with --auto-install flag (CI/CD mode)."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Execute with auto_install=True
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify
        assert result.status == "installed"
        assert len(result.installed_packages) == 2

        # Verify command uses --group
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--group" in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_sc_002c_dependency_groups_section_placement(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test SC-002c: Verify dependency-groups targets correct pyproject.toml section.

        Success Criterion SC-002c:
        100% correct placement in [dependency-groups.docs] when
        dependency_target='dependency-groups'.
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
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify installation succeeded
        assert result.status == "installed"

        # Verify pyproject.toml section exists
        pyproject_content = (project_root / "pyproject.toml").read_text()
        assert "[dependency-groups]" in pyproject_content

        # Verify uv add command targets correct section
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--group" in cmd
        assert "docs" in cmd

        # Verify NOT using --optional (optional-dependencies)
        assert "--optional" not in cmd

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_dependency_groups_timeout_setting(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that dependency-groups installation respects 300s timeout."""
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
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "installed"

        # Verify timeout is set to 300 seconds
        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 300

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_dependency_groups_uv_native_workflow(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test dependency-groups supports uv-native workflow (PEP 735).

        Verifies that dependency-groups is the modern uv-native approach,
        distinct from optional-dependencies (PEP 621).
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
            dependency_target="dependency-groups",
            project_root=project_root,
            console=console,
        )

        # Verify installation succeeded
        assert result.status == "installed"

        # Verify uv add --group (PEP 735 approach)
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd == [
            "uv",
            "add",
            "--group",
            "docs",
            "sphinx>=7.0",
            "myst-parser>=2.0",
        ]

        # Verify project root and timeout
        assert call_args[1]["cwd"] == project_root
        assert call_args[1]["timeout"] == 300
