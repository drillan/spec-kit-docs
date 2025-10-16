"""Unit tests for DependencyTarget dataclass.

Tests for FR-008f (Session 2025-10-16): Dependency placement strategy.
Validates DependencyTarget dataclass constraints and validation rules.
"""

import pytest

from speckit_docs.utils.dependencies import DependencyTarget


class TestDependencyTargetValid:
    """Test valid DependencyTarget instantiation."""

    def test_optional_dependencies_valid(self) -> None:
        """Test creating DependencyTarget for optional-dependencies."""
        target = DependencyTarget(
            target_type="optional-dependencies",
            uv_flag="--optional",
            section_path="[project.optional-dependencies.docs]",
        )
        assert target.target_type == "optional-dependencies"
        assert target.uv_flag == "--optional"
        assert target.section_path == "[project.optional-dependencies.docs]"

    def test_dependency_groups_valid(self) -> None:
        """Test creating DependencyTarget for dependency-groups."""
        target = DependencyTarget(
            target_type="dependency-groups",
            uv_flag="--group",
            section_path="[dependency-groups.docs]",
        )
        assert target.target_type == "dependency-groups"
        assert target.uv_flag == "--group"
        assert target.section_path == "[dependency-groups.docs]"


class TestDependencyTargetInvalidTargetType:
    """Test DependencyTarget validation for invalid target_type."""

    def test_invalid_target_type(self) -> None:
        """Test ValueError raised for invalid target_type."""
        with pytest.raises(ValueError, match="Invalid target_type"):
            DependencyTarget(
                target_type="invalid-type",  # type: ignore
                uv_flag="--optional",
                section_path="[project.optional-dependencies.docs]",
            )

    def test_empty_target_type(self) -> None:
        """Test ValueError raised for empty target_type."""
        with pytest.raises(ValueError, match="Invalid target_type"):
            DependencyTarget(
                target_type="",  # type: ignore
                uv_flag="--optional",
                section_path="[project.optional-dependencies.docs]",
            )


class TestDependencyTargetUvFlagMismatch:
    """Test DependencyTarget validation for uv_flag mismatch."""

    def test_optional_dependencies_wrong_flag(self) -> None:
        """Test ValueError when optional-dependencies has wrong uv_flag."""
        with pytest.raises(ValueError, match="optional-dependencies requires --optional flag"):
            DependencyTarget(
                target_type="optional-dependencies",
                uv_flag="--group",  # Wrong flag
                section_path="[project.optional-dependencies.docs]",
            )

    def test_dependency_groups_wrong_flag(self) -> None:
        """Test ValueError when dependency-groups has wrong uv_flag."""
        with pytest.raises(ValueError, match="dependency-groups requires --group flag"):
            DependencyTarget(
                target_type="dependency-groups",
                uv_flag="--optional",  # Wrong flag
                section_path="[dependency-groups.docs]",
            )

    def test_optional_dependencies_invalid_flag(self) -> None:
        """Test ValueError when optional-dependencies has completely invalid flag."""
        with pytest.raises(ValueError, match="optional-dependencies requires --optional flag"):
            DependencyTarget(
                target_type="optional-dependencies",
                uv_flag="--invalid",
                section_path="[project.optional-dependencies.docs]",
            )


class TestDependencyTargetImmutability:
    """Test DependencyTarget immutability (frozen=True)."""

    def test_cannot_modify_target_type(self) -> None:
        """Test that target_type cannot be modified after creation."""
        target = DependencyTarget(
            target_type="optional-dependencies",
            uv_flag="--optional",
            section_path="[project.optional-dependencies.docs]",
        )
        with pytest.raises(AttributeError):
            target.target_type = "dependency-groups"  # type: ignore

    def test_cannot_modify_uv_flag(self) -> None:
        """Test that uv_flag cannot be modified after creation."""
        target = DependencyTarget(
            target_type="optional-dependencies",
            uv_flag="--optional",
            section_path="[project.optional-dependencies.docs]",
        )
        with pytest.raises(AttributeError):
            target.uv_flag = "--group"  # type: ignore

    def test_cannot_modify_section_path(self) -> None:
        """Test that section_path cannot be modified after creation."""
        target = DependencyTarget(
            target_type="optional-dependencies",
            uv_flag="--optional",
            section_path="[project.optional-dependencies.docs]",
        )
        with pytest.raises(AttributeError):
            target.section_path = "[dependency-groups.docs]"  # type: ignore
