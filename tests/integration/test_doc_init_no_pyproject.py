"""Integration tests for doc-init without pyproject.toml.

Tests the alternative methods presentation when pyproject.toml is not present.
Validates SC-008b (alternative methods presentation).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from speckit_docs.utils.dependencies import handle_dependencies


class TestDocInitNoPyproject:
    """Integration tests for handling missing pyproject.toml."""

    @pytest.fixture
    def project_root_no_pyproject(self, tmp_path: Path) -> Path:
        """Create a temporary project root WITHOUT pyproject.toml."""
        project = tmp_path / "no_pyproject"
        project.mkdir()
        # No pyproject.toml created
        return project

    @pytest.fixture
    def console(self) -> Console:
        """Create a Console instance for testing."""
        return Console()

    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_no_pyproject_sphinx(
        self,
        mock_show_alt: MagicMock,
        project_root_no_pyproject: Path,
        console: Console,
    ) -> None:
        """Test behavior when pyproject.toml is missing for Sphinx."""
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root_no_pyproject,
            console=console,
        )

        # Verify result
        assert result.status == "failed"
        assert "pyproject.toml" in result.message
        assert result.installed_packages == []

        # Verify alternative methods were shown (SC-008b)
        mock_show_alt.assert_called_once_with(
            "sphinx", console, project_root_no_pyproject
        )

    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_no_pyproject_mkdocs(
        self,
        mock_show_alt: MagicMock,
        project_root_no_pyproject: Path,
        console: Console,
    ) -> None:
        """Test behavior when pyproject.toml is missing for MkDocs."""
        result = handle_dependencies(
            doc_type="mkdocs",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root_no_pyproject,
            console=console,
        )

        # Verify result
        assert result.status == "failed"
        assert "pyproject.toml" in result.message
        assert result.installed_packages == []

        # Verify alternative methods were shown (SC-008b)
        mock_show_alt.assert_called_once_with(
            "mkdocs", console, project_root_no_pyproject
        )

    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    @patch("speckit_docs.utils.dependencies.detect_package_managers")
    def test_sc_008b_alternative_methods_presentation(
        self,
        mock_detect_pm: MagicMock,
        mock_show_alt: MagicMock,
        project_root_no_pyproject: Path,
        console: Console,
    ) -> None:
        """Test SC-008b: Alternative methods presentation.

        Validates that when pyproject.toml is missing:
        1. show_alternative_methods() is called
        2. Available package managers are detected
        3. Both Method 1 (manual install) and Method 2 (spec-kit workflow) are shown
        """
        # Setup mock
        mock_detect_pm.return_value = [
            ("pip", "pip install sphinx>=7.0 myst-parser>=2.0"),
        ]

        # Execute
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=False,
            dependency_target="optional-dependencies",
            project_root=project_root_no_pyproject,
            console=console,
        )

        # Verify SC-008b compliance
        assert result.status == "failed"

        # Verify show_alternative_methods was called with correct arguments
        mock_show_alt.assert_called_once_with(
            "sphinx", console, project_root_no_pyproject
        )

    @patch("speckit_docs.utils.dependencies.show_alternative_methods")
    def test_no_install_flag_skips_check(
        self,
        mock_show_alt: MagicMock,
        project_root_no_pyproject: Path,
        console: Console,
    ) -> None:
        """Test that --no-install flag skips pyproject.toml check."""
        result = handle_dependencies(
            doc_type="sphinx",
            auto_install=False,
            no_install=True,
            dependency_target="optional-dependencies",
            project_root=project_root_no_pyproject,
            console=console,
        )

        # Verify result
        assert result.status == "skipped"
        assert "--no-install" in result.message

        # Verify alternative methods were NOT shown
        mock_show_alt.assert_not_called()
