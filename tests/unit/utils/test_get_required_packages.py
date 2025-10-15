"""Unit tests for get_required_packages function."""

import pytest

from speckit_docs.utils.dependencies import get_required_packages


class TestGetRequiredPackages:
    """Test get_required_packages function."""

    def test_get_sphinx_packages(self) -> None:
        """Test get_required_packages returns correct packages for Sphinx."""
        packages = get_required_packages("sphinx")
        assert packages == ["sphinx>=7.0", "myst-parser>=2.0"]

    def test_get_mkdocs_packages(self) -> None:
        """Test get_required_packages returns correct packages for MkDocs."""
        packages = get_required_packages("mkdocs")
        assert packages == ["mkdocs>=1.5", "mkdocs-material>=9.0"]

    def test_invalid_doc_type_raises_error(self) -> None:
        """Test that invalid doc_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid doc_type: invalid"):
            get_required_packages("invalid")

    def test_case_sensitive_doc_type(self) -> None:
        """Test that doc_type is case-sensitive."""
        with pytest.raises(ValueError, match="Invalid doc_type: Sphinx"):
            get_required_packages("Sphinx")

    def test_returns_list_of_strings(self) -> None:
        """Test that function returns a list of strings."""
        packages = get_required_packages("sphinx")
        assert isinstance(packages, list)
        assert all(isinstance(pkg, str) for pkg in packages)

    def test_packages_include_version_constraints(self) -> None:
        """Test that all packages include version constraints."""
        sphinx_packages = get_required_packages("sphinx")
        mkdocs_packages = get_required_packages("mkdocs")

        for pkg in sphinx_packages + mkdocs_packages:
            assert ">=" in pkg or "==" in pkg or "~=" in pkg
