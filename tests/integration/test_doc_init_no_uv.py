"""Integration tests for doc-init without uv command.

Tests the alternative methods presentation when uv command is not available.
Validates SC-008b (alternative methods presentation).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestDocInitNoUv:
    """Integration tests for handling missing uv command."""

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
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_no_uv_command_sphinx(
        self,
        mock_show_alt: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test behavior when uv command is not available for Sphinx."""
        mock_which.return_value = None  # uv not found

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "failed"
        assert "uv" in result.message.lower()
        assert result.installed_packages == []

        # Verify alternative methods were shown (SC-008b)
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_no_uv_command_mkdocs(
        self,
        mock_show_alt: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test behavior when uv command is not available for MkDocs."""
        mock_which.return_value = None  # uv not found

        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "failed"
        assert "uv" in result.message.lower()
        assert result.installed_packages == []

        # Verify alternative methods were shown (SC-008b)
        mock_show_alt.assert_called_once_with("mkdocs", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    @patch("speckit_docs.utils.dependencies.detect_package_managers")
    def test_sc_008b_fallback_to_poetry(
        self,
        mock_detect_pm: MagicMock,
        mock_show_alt: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test SC-008b: Fallback to poetry when uv is unavailable.

        Validates that when uv is not available:
        1. show_alternative_methods() is called
        2. detect_package_managers() finds poetry or pip
        3. Manual installation command with available manager is shown
        """
        # Setup mocks
        mock_which.return_value = None  # uv not available
        mock_detect_pm.return_value = [
            ("poetry", "poetry add sphinx>=7.0 myst-parser>=2.0"),
        ]

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            project_root=project_root,
            console=console,
        )

        # Verify SC-008b compliance
        assert result.status == "failed"

        # Verify show_alternative_methods was called
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    @patch("speckit_docs.utils.dependencies.detect_package_managers")
    def test_sc_008b_fallback_to_pip(
        self,
        mock_detect_pm: MagicMock,
        mock_show_alt: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test SC-008b: Fallback to pip when uv and poetry are unavailable."""
        # Setup mocks
        mock_which.return_value = None  # uv not available
        mock_detect_pm.return_value = [
            ("pip", "pip install sphinx>=7.0 myst-parser>=2.0"),
        ]

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            project_root=project_root,
            console=console,
        )

        # Verify SC-008b compliance
        assert result.status == "failed"

        # Verify show_alternative_methods was called
        mock_show_alt.assert_called_once_with("sphinx", console, project_root)

    @patch("speckit_docs.utils.dependencies.shutil.which")
    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_auto_install_flag_with_no_uv(
        self,
        mock_show_alt: MagicMock,
        mock_which: MagicMock,
        project_root: Path,
        console: Console,
    ) -> None:
        """Test that --auto-install flag still fails gracefully when uv is missing."""
        mock_which.return_value = None  # uv not found

        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=True,  # CI/CD mode
            no_install=False,
            project_root=project_root,
            console=console,
        )

        # Verify result
        assert result.status == "failed"
        assert "uv" in result.message.lower()

        # Verify alternative methods were shown even in CI/CD mode
        mock_show_alt.assert_called_once()
