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
