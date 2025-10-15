"""Unit tests for DependencyResult data class."""

import pytest

from speckit_docs.utils.dependencies import DependencyResult


class TestDependencyResult:
    """Test DependencyResult data class validation rules."""

    def test_valid_installed_status_with_packages(self) -> None:
        """Test valid DependencyResult with installed status and packages."""
        result = DependencyResult(
            status="installed",
            message="インストール成功",
            installed_packages=["sphinx>=7.0", "myst-parser>=2.0"],
        )
        assert result.status == "installed"
        assert result.message == "インストール成功"
        assert len(result.installed_packages) == 2

    def test_valid_skipped_status(self) -> None:
        """Test valid DependencyResult with skipped status."""
        result = DependencyResult(
            status="skipped",
            message="ユーザーが拒否",
            installed_packages=[],
        )
        assert result.status == "skipped"
        assert result.message == "ユーザーが拒否"
        assert result.installed_packages == []

    def test_valid_failed_status(self) -> None:
        """Test valid DependencyResult with failed status."""
        result = DependencyResult(
            status="failed",
            message="pyproject.toml不在",
            installed_packages=[],
        )
        assert result.status == "failed"
        assert result.message == "pyproject.toml不在"
        assert result.installed_packages == []

    def test_valid_not_needed_status(self) -> None:
        """Test valid DependencyResult with not_needed status."""
        result = DependencyResult(
            status="not_needed",
            message="すべてのパッケージがインストール済み",
            installed_packages=[],
        )
        assert result.status == "not_needed"
        assert result.message == "すべてのパッケージがインストール済み"
        assert result.installed_packages == []

    def test_invalid_status_raises_error(self) -> None:
        """Test that invalid status raises ValueError in __post_init__."""
        with pytest.raises(ValueError, match="Invalid status: invalid"):
            DependencyResult(
                status="invalid",  # type: ignore[arg-type]
                message="test",
                installed_packages=[],
            )

    def test_installed_status_with_empty_packages_raises_error(self) -> None:
        """Test that installed status with empty packages raises ValueError."""
        with pytest.raises(
            ValueError, match="installed_packages must not be empty when status is 'installed'"
        ):
            DependencyResult(
                status="installed",
                message="インストール成功",
                installed_packages=[],
            )

    def test_frozen_immutability(self) -> None:
        """Test that DependencyResult is immutable (frozen=True)."""
        result = DependencyResult(
            status="installed",
            message="インストール成功",
            installed_packages=["sphinx>=7.0"],
        )
        with pytest.raises(AttributeError):
            result.status = "failed"  # type: ignore[misc]

    def test_default_empty_packages(self) -> None:
        """Test that installed_packages defaults to empty list."""
        result = DependencyResult(
            status="skipped",
            message="--no-install指定のためスキップ",
        )
        assert result.installed_packages == []
