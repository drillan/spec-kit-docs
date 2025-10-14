"""Unit tests for BaseGenerator (T016)."""

from pathlib import Path

import pytest

from speckit_docs.generators.base import BaseGenerator
from speckit_docs.models import StructureType


class TestBaseGenerator:
    """Tests for BaseGenerator abstract class."""

    def test_base_generator_interface(self, tmp_path):
        """Test that BaseGenerator can be subclassed with required methods."""

        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            """Concrete implementation for testing."""

            def generate_config(self, **kwargs) -> None:
                """Test implementation of generate_config."""
                pass

            def generate_index(self) -> None:
                """Test implementation of generate_index."""
                pass

            def create_directory_structure(self) -> None:
                """Test implementation of create_directory_structure."""
                pass

            def init_project(self) -> None:
                """Test implementation of init_project."""
                pass

            def update_docs(self, features) -> None:
                """Test implementation of update_docs."""
                pass

            def build_docs(self) -> BuildResult:
                """Test implementation of build_docs."""
                return BuildResult(
                    success=True,
                    output_dir=Path("/tmp"),
                    warnings=[],
                    errors=[],
                    build_time=0.0,
                    file_count=0,
                )

            def validate_project(self) -> ValidationResult:
                """Test implementation of validate_project."""
                return ValidationResult(
                    is_valid=True, errors=[], warnings=[], checked_items=[]
                )

        # Create instance
        docs_dir = tmp_path / "docs"
        generator = TestGenerator(docs_dir)

        # Verify initialization
        assert generator.docs_dir == docs_dir
        assert generator.structure_type == StructureType.FLAT

    def test_base_generator_cannot_be_instantiated(self):
        """Test that BaseGenerator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseGenerator(Path("/tmp/docs"))  # type: ignore

    def test_determine_structure_flat_for_small_projects(self, tmp_path):
        """Test that determine_structure returns FLAT for 5 or fewer features."""

        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        generator = TestGenerator(tmp_path / "docs")

        # Test with different feature counts
        assert generator.determine_structure(0) == StructureType.FLAT
        assert generator.determine_structure(1) == StructureType.FLAT
        assert generator.determine_structure(5) == StructureType.FLAT

    def test_determine_structure_comprehensive_for_large_projects(self, tmp_path):
        """Test that determine_structure returns COMPREHENSIVE for 6+ features."""

        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        generator = TestGenerator(tmp_path / "docs")

        # Test with 6 or more features
        assert generator.determine_structure(6) == StructureType.COMPREHENSIVE
        assert generator.determine_structure(10) == StructureType.COMPREHENSIVE
        assert generator.determine_structure(100) == StructureType.COMPREHENSIVE

    def test_abstract_methods_must_be_implemented(self, tmp_path):
        """Test that subclasses must implement all abstract methods."""

        # Missing generate_config
        class IncompleteGenerator1(BaseGenerator):  # type: ignore
            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteGenerator1(tmp_path / "docs")

        # Missing generate_index
        class IncompleteGenerator2(BaseGenerator):  # type: ignore
            def generate_config(self, **kwargs) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteGenerator2(tmp_path / "docs")

        # Missing create_directory_structure
        class IncompleteGenerator3(BaseGenerator):  # type: ignore
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteGenerator3(tmp_path / "docs")


class TestBuildResult:
    """Tests for BuildResult dataclass."""

    def test_build_result_is_valid_success(self):
        """Test is_valid returns True for successful build."""
        from speckit_docs.generators.base import BuildResult

        result = BuildResult(
            success=True,
            output_dir=Path("/tmp"),
            warnings=[],
            errors=[],
            build_time=1.5,
            file_count=10,
        )
        assert result.is_valid() is True

    def test_build_result_is_valid_with_warnings(self):
        """Test is_valid returns True with acceptable warning count."""
        from speckit_docs.generators.base import BuildResult

        result = BuildResult(
            success=True,
            output_dir=Path("/tmp"),
            warnings=["warning 1", "warning 2"],
            errors=[],
            build_time=1.5,
            file_count=10,
        )
        assert result.is_valid(max_warnings=10) is True

    def test_build_result_is_valid_too_many_warnings(self):
        """Test is_valid returns False with too many warnings."""
        from speckit_docs.generators.base import BuildResult

        warnings = [f"warning {i}" for i in range(15)]
        result = BuildResult(
            success=True,
            output_dir=Path("/tmp"),
            warnings=warnings,
            errors=[],
            build_time=1.5,
            file_count=10,
        )
        assert result.is_valid(max_warnings=10) is False

    def test_build_result_is_valid_with_errors(self):
        """Test is_valid returns False when there are errors."""
        from speckit_docs.generators.base import BuildResult

        result = BuildResult(
            success=False,
            output_dir=Path("/tmp"),
            warnings=[],
            errors=["error 1"],
            build_time=1.5,
            file_count=10,
        )
        assert result.is_valid() is False

    def test_build_result_get_summary(self):
        """Test get_summary returns formatted string."""
        from speckit_docs.generators.base import BuildResult

        result = BuildResult(
            success=True,
            output_dir=Path("/tmp"),
            warnings=["warning 1"],
            errors=[],
            build_time=2.5,
            file_count=25,
        )
        summary = result.get_summary()

        assert "✓" in summary
        assert "警告: 1" in summary
        assert "エラー: 0" in summary
        assert "2.5秒" in summary
        assert "25個" in summary

    def test_build_result_get_summary_failed(self):
        """Test get_summary for failed build."""
        from speckit_docs.generators.base import BuildResult

        result = BuildResult(
            success=False,
            output_dir=Path("/tmp"),
            warnings=[],
            errors=["error 1", "error 2"],
            build_time=1.0,
            file_count=0,
        )
        summary = result.get_summary()

        assert "✗" in summary
        assert "エラー: 2" in summary


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_format_errors_success(self):
        """Test format_errors for successful validation with checked items."""
        from speckit_docs.generators.base import ValidationResult

        result = ValidationResult(
            is_valid=True, errors=[], warnings=[], checked_items=["item1", "item2"]
        )
        formatted = result.format_errors()

        assert "✓" in formatted
        assert "検証項目: 2個" in formatted

    def test_validation_result_format_errors_completely_empty(self):
        """Test format_errors when everything is empty."""
        from speckit_docs.generators.base import ValidationResult

        result = ValidationResult(is_valid=True, errors=[], warnings=[], checked_items=[])
        formatted = result.format_errors()

        assert "すべての検証に合格しました" in formatted

    def test_validation_result_format_errors_with_errors(self):
        """Test format_errors with validation errors."""
        from speckit_docs.generators.base import ValidationResult

        result = ValidationResult(
            is_valid=False,
            errors=["error 1", "error 2"],
            warnings=[],
            checked_items=["item1"],
        )
        formatted = result.format_errors()

        assert "❌ エラー:" in formatted
        assert "error 1" in formatted
        assert "error 2" in formatted
        assert "💡 提案:" in formatted

    def test_validation_result_format_errors_with_warnings(self):
        """Test format_errors with warnings."""
        from speckit_docs.generators.base import ValidationResult

        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["warning 1"],
            checked_items=["item1", "item2"],
        )
        formatted = result.format_errors()

        assert "⚠️  警告:" in formatted
        assert "warning 1" in formatted
        assert "検証項目: 2個" in formatted

    def test_validation_result_format_errors_comprehensive(self):
        """Test format_errors with errors, warnings, and checked items."""
        from speckit_docs.generators.base import ValidationResult

        result = ValidationResult(
            is_valid=False,
            errors=["error 1"],
            warnings=["warning 1"],
            checked_items=["item1", "item2", "item3"],
        )
        formatted = result.format_errors()

        assert "❌ エラー:" in formatted
        assert "⚠️  警告:" in formatted
        assert "検証項目: 3個" in formatted
        assert "💡 提案:" in formatted


class TestBaseGeneratorHelpers:
    """Tests for BaseGenerator helper methods."""

    def test_determine_structure_type_flat(self, tmp_path):
        """Test determine_structure_type returns FLAT when no features dir."""
        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        generator = TestGenerator(docs_dir)
        assert generator.determine_structure_type() == "FLAT"

    def test_determine_structure_type_comprehensive(self, tmp_path):
        """Test determine_structure_type returns COMPREHENSIVE when features dir exists."""
        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        features_dir = docs_dir / "features"
        features_dir.mkdir()
        (features_dir / "test.md").write_text("# Test")

        generator = TestGenerator(docs_dir)
        assert generator.determine_structure_type() == "COMPREHENSIVE"

    def test_create_docs_directory(self, tmp_path):
        """Test _create_docs_directory creates directory."""
        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        docs_dir = tmp_path / "docs"
        generator = TestGenerator(docs_dir)

        generator._create_docs_directory()
        assert docs_dir.exists()
        assert docs_dir.is_dir()

    def test_create_subdirectories_comprehensive(self, tmp_path):
        """Test _create_subdirectories creates all subdirs for COMPREHENSIVE."""
        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        generator = TestGenerator(docs_dir)

        generator._create_subdirectories("COMPREHENSIVE")

        assert (docs_dir / "features").exists()
        assert (docs_dir / "guides").exists()
        assert (docs_dir / "api").exists()
        assert (docs_dir / "architecture").exists()

    def test_create_subdirectories_flat(self, tmp_path):
        """Test _create_subdirectories doesn't create subdirs for FLAT."""
        from speckit_docs.generators.base import BuildResult, ValidationResult

        class TestGenerator(BaseGenerator):
            def generate_config(self, **kwargs) -> None:
                pass

            def generate_index(self) -> None:
                pass

            def create_directory_structure(self) -> None:
                pass

            def init_project(self) -> None:
                pass

            def update_docs(self, features) -> None:
                pass

            def build_docs(self) -> BuildResult:
                return BuildResult(True, Path("/tmp"), [], [], 0.0, 0)

            def validate_project(self) -> ValidationResult:
                return ValidationResult(True, [], [], [])

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        generator = TestGenerator(docs_dir)

        generator._create_subdirectories("FLAT")

        assert not (docs_dir / "features").exists()
        assert not (docs_dir / "guides").exists()
