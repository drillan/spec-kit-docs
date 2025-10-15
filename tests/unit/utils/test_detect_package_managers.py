"""Unit tests for detect_package_managers function."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from speckit_docs.utils.dependencies import detect_package_managers


class TestDetectPackageManagers:
    """Test detect_package_managers function."""

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_uv_available_only(self, mock_which: MagicMock) -> None:
        """Test detection when only uv is available."""
        mock_which.side_effect = lambda cmd: "/usr/bin/uv" if cmd == "uv" else None
        result = detect_package_managers(Path("/tmp/project"), "sphinx")

        assert len(result) == 1
        assert result[0] == ("uv", "uv add sphinx>=7.0 myst-parser>=2.0")

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_poetry_available_only(self, mock_which: MagicMock) -> None:
        """Test detection when only poetry is available."""
        mock_which.side_effect = lambda cmd: "/usr/bin/poetry" if cmd == "poetry" else None
        result = detect_package_managers(Path("/tmp/project"), "sphinx")

        assert len(result) == 1
        assert result[0] == ("poetry", "poetry add sphinx>=7.0 myst-parser>=2.0")

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_pip_available_only(self, mock_which: MagicMock) -> None:
        """Test detection when only pip is available."""
        mock_which.side_effect = lambda cmd: "/usr/bin/pip" if cmd == "pip" else None
        result = detect_package_managers(Path("/tmp/project"), "sphinx")

        assert len(result) == 1
        assert result[0] == ("pip", "pip install sphinx>=7.0 myst-parser>=2.0")

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_multiple_managers_available_priority_order(self, mock_which: MagicMock) -> None:
        """Test priority order: uv > poetry > pip."""
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}" if cmd in ["uv", "poetry", "pip"] else None
        result = detect_package_managers(Path("/tmp/project"), "sphinx")

        assert len(result) == 3
        assert result[0][0] == "uv"
        assert result[1][0] == "poetry"
        assert result[2][0] == "pip"

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_no_package_managers_available(self, mock_which: MagicMock) -> None:
        """Test detection when no package managers are available."""
        mock_which.return_value = None
        result = detect_package_managers(Path("/tmp/project"), "mkdocs")

        assert result == []

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_mkdocs_packages(self, mock_which: MagicMock) -> None:
        """Test detection with MkDocs packages."""
        mock_which.side_effect = lambda cmd: "/usr/bin/uv" if cmd == "uv" else None
        result = detect_package_managers(Path("/tmp/project"), "mkdocs")

        assert len(result) == 1
        assert result[0] == ("uv", "uv add mkdocs>=1.5 mkdocs-material>=9.0")

    @patch("speckit_docs.utils.dependencies.shutil.which")
    def test_returns_list_of_tuples(self, mock_which: MagicMock) -> None:
        """Test that function returns a list of (name, command) tuples."""
        mock_which.side_effect = lambda cmd: "/usr/bin/uv" if cmd == "uv" else None
        result = detect_package_managers(Path("/tmp/project"), "sphinx")

        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(isinstance(item[0], str) and isinstance(item[1], str) for item in result)
