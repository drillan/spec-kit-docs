"""Unit tests for handle_dependencies function."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestHandleDependencies:
    """Test handle_dependencies function with 10 comprehensive test cases."""

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

    # Test Case 1: Success - pyproject.toml exists, uv available, installation success
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_success_with_user_confirmation(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test successful installation with user confirmation."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None  # Package not installed
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
        mock_confirm.assert_called_once()
        mock_run.assert_called_once()

    # Test Case 2: Failed - pyproject.toml not present
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_failed_no_pyproject(
        self, mock_show_alt: MagicMock, tmp_path: Path, console: Console
    ) -> None:
        """Test failure when pyproject.toml does not exist."""
        project_root = tmp_path / "no_pyproject"
        project_root.mkdir()

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "failed"
        assert "pyproject.toml" in result.message
        assert result.installed_packages == []
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    # Test Case 3: Failed - uv command not available
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_failed_uv_not_found(
        self,
        mock_show_alt: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test failure when uv command is not available."""
        mock_which.return_value = None

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "failed"
        assert "uv" in result.message.lower()
        assert result.installed_packages == []
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    # Test Case 4: Not needed - packages already installed
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    def test_not_needed_packages_already_installed(
        self,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test when all packages are already installed."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = Mock()  # Package is installed

        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "not_needed"
        assert "インストール済み" in result.message
        assert result.installed_packages == []

    # Test Case 5: Skipped - --no-install flag
    def test_skipped_no_install_flag(self, project_root: Path, console: Console) -> None:
        """Test skip when --no-install flag is specified."""
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=True,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "skipped"
        assert "--no-install" in result.message
        assert result.installed_packages == []

    # Test Case 6: Auto-install - confirmation skipped
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    def test_auto_install_skips_confirmation(
        self,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that --auto-install flag skips user confirmation."""
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
        mock_confirm.assert_not_called()  # Confirmation skipped
        mock_run.assert_called_once()

    # Test Case 7: Failed - uv add timeout
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_failed_timeout(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test failure when uv add times out."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="uv add", timeout=300)

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "failed"
        assert "タイムアウト" in result.message
        assert result.installed_packages == []
        mock_show_alt.assert_called_once()

    # Test Case 8: Failed - uv add failed (returncode != 0)
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_failed_uv_add_error(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test failure when uv add returns non-zero exit code."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Dependency resolution failed")

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "failed"
        assert "uv add失敗" in result.message or "失敗" in result.message
        assert result.installed_packages == []
        mock_show_alt.assert_called_once()

    # Test Case 9: Skipped - user declined confirmation
    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_skipped_user_declined(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test skip when user declines confirmation."""
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = False

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        assert result.status == "skipped"
        assert "ユーザー" in result.message or "拒否" in result.message
        assert result.installed_packages == []
        mock_show_alt.assert_called_once()

    # Test Case 10: ValueError - invalid doc_type
    def test_invalid_doc_type_raises_error(
        self, project_root: Path, console: Console
    ) -> None:
        """Test that invalid doc_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid doc_type: invalid"):
            handle_dependencies(
                doc_type="invalid",
                auto_install=False,
                no_install=False,
                dependency_target="optional-dependencies",
                project_root=project_root,
                console=console,
            )
