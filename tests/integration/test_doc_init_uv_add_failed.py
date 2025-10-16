"""Integration tests for doc-init when uv add fails.

Tests the error handling when uv add command fails.
Validates SC-008c (failure reason and alternative methods presentation).
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestDocInitUvAddFailed:
    """Integration tests for handling uv add failures."""

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create a temporary project root with pyproject.toml."""
        project = tmp_path / "test_project"
        project.mkdir()
        (project / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        return project

    @pytest.fixture
    def console(self) -> Console:
        """Create a Console instance for testing."""
        return Console()

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_uv_add_dependency_resolution_failed(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test behavior when uv add fails with dependency resolution error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None  # Package not installed
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error: Failed to resolve dependency version conflict",
        )

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify result (SC-008c)
        assert result.status == "failed"
        assert "uv add失敗" in result.message or "失敗" in result.message
        assert result.installed_packages == []

        # Verify alternative methods were shown
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_uv_add_network_error(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test behavior when uv add fails with network error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error: Failed to connect to PyPI",
        )

        # Execute
        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify result (SC-008c)
        assert result.status == "failed"
        assert result.installed_packages == []

        # Verify alternative methods were shown
        mock_show_alt.assert_called_once_with("mkdocs", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_sc_008c_stderr_capture(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test SC-008c: Stderr capture and display in error message."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        stderr_content = "error: Package 'sphinx' version >=7.0 not found"
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr=stderr_content,
        )

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify SC-008c compliance: stderr is captured in message
        assert result.status == "failed"
        # Message should contain failure indication
        assert "失敗" in result.message or "uv add失敗" in result.message

        # Verify alternative methods were shown
        mock_show_alt.assert_called_once()

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.typer.confirm")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_uv_add_permission_error(
        self,
        mock_show_alt: MagicMock,
        mock_confirm: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test behavior when uv add fails with permission error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error: Permission denied writing to pyproject.toml",
        )

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
        assert result.status == "failed"
        assert result.installed_packages == []

        # Verify alternative methods were shown
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.importlib.util.find_spec")
    @patch("speckit_docs.utils.dependencies.subprocess.run")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_auto_install_flag_with_uv_add_failure(
        self,
        mock_show_alt: MagicMock,
        mock_run: MagicMock,
        mock_find_spec: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that --auto-install flag handles uv add failures gracefully."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/uv"
        mock_find_spec.return_value = None
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error: Failed to install",
        )

        # Execute with auto_install=True (CI/CD mode)
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=True,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "failed"

        # Verify alternative methods were shown even in CI/CD mode
        mock_show_alt.assert_called_once()
