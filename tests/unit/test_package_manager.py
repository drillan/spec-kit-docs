"""Unit tests for PackageManager data class."""

import pytest

from speckit_docs.utils.dependencies import PackageManager


class TestPackageManager:
    """Test PackageManager data class validation rules."""

    def test_valid_uv_package_manager(self) -> None:
        """Test valid PackageManager with uv."""
        pm = PackageManager(name="uv", command="uv add", available=True)
        assert pm.name == "uv"
        assert pm.command == "uv add"
        assert pm.available is True

    def test_valid_poetry_package_manager(self) -> None:
        """Test valid PackageManager with poetry."""
        pm = PackageManager(name="poetry", command="poetry add", available=True)
        assert pm.name == "poetry"
        assert pm.command == "poetry add"
        assert pm.available is True

    def test_valid_pip_package_manager(self) -> None:
        """Test valid PackageManager with pip."""
        pm = PackageManager(name="pip", command="pip install", available=True)
        assert pm.name == "pip"
        assert pm.command == "pip install"
        assert pm.available is True

    def test_valid_conda_package_manager(self) -> None:
        """Test valid PackageManager with conda."""
        pm = PackageManager(name="conda", command="conda install", available=False)
        assert pm.name == "conda"
        assert pm.command == "conda install"
        assert pm.available is False

    def test_invalid_package_manager_name_raises_error(self) -> None:
        """Test that invalid package manager name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid package manager: npm"):
            PackageManager(name="npm", command="npm install", available=True)

    def test_frozen_immutability(self) -> None:
        """Test that PackageManager is immutable (frozen=True)."""
        pm = PackageManager(name="uv", command="uv add", available=True)
        with pytest.raises(AttributeError):
            pm.name = "pip"  # type: ignore[misc]

    def test_unavailable_package_manager(self) -> None:
        """Test PackageManager with available=False."""
        pm = PackageManager(name="poetry", command="poetry add", available=False)
        assert pm.available is False
