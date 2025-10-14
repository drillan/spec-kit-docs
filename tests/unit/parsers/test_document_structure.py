"""Unit tests for DocumentStructure class."""

import pytest

from speckit_docs.models import StructureType
from speckit_docs.parsers.document_structure import DocumentStructure


class TestDocumentStructureDetermination:
    """Tests for DocumentStructure.determine_structure() method."""

    def test_determine_structure_with_0_features(self):
        """Test that 0 features returns FLAT structure."""
        structure_type = DocumentStructure.determine_structure(feature_count=0)
        assert structure_type == StructureType.FLAT

    def test_determine_structure_with_1_feature(self):
        """Test that 1 feature returns FLAT structure."""
        structure_type = DocumentStructure.determine_structure(feature_count=1)
        assert structure_type == StructureType.FLAT

    def test_determine_structure_with_5_features(self):
        """Test that 5 features returns FLAT structure (boundary)."""
        structure_type = DocumentStructure.determine_structure(feature_count=5)
        assert structure_type == StructureType.FLAT

    def test_determine_structure_with_6_features(self):
        """Test that 6 features returns COMPREHENSIVE structure (boundary)."""
        structure_type = DocumentStructure.determine_structure(feature_count=6)
        assert structure_type == StructureType.COMPREHENSIVE

    def test_determine_structure_with_10_features(self):
        """Test that 10 features returns COMPREHENSIVE structure."""
        structure_type = DocumentStructure.determine_structure(feature_count=10)
        assert structure_type == StructureType.COMPREHENSIVE

    def test_determine_structure_with_50_features(self):
        """Test that 50 features returns COMPREHENSIVE structure."""
        structure_type = DocumentStructure.determine_structure(feature_count=50)
        assert structure_type == StructureType.COMPREHENSIVE


class TestDocumentStructurePathGeneration:
    """Tests for DocumentStructure path generation methods."""

    def test_get_feature_page_path_flat(self):
        """Test feature page path generation for FLAT structure."""
        path = DocumentStructure.get_feature_page_path(
            structure_type=StructureType.FLAT,
            feature_id="001",
            feature_name="user-auth",
        )
        # FLAT: features/001-user-auth.md
        assert "features" in str(path)
        assert "001-user-auth.md" in str(path)

    def test_get_feature_page_path_comprehensive(self):
        """Test feature page path generation for COMPREHENSIVE structure."""
        path = DocumentStructure.get_feature_page_path(
            structure_type=StructureType.COMPREHENSIVE,
            feature_id="002",
            feature_name="api-integration",
        )
        # COMPREHENSIVE: features/002-api-integration/index.md
        assert "features" in str(path)
        assert "002-api-integration" in str(path)
        assert "index.md" in str(path)

    def test_get_feature_subpage_path_comprehensive(self):
        """Test feature subpage path generation for COMPREHENSIVE structure."""
        path = DocumentStructure.get_feature_subpage_path(
            feature_id="003",
            feature_name="notifications",
            subpage_name="plan",
        )
        # COMPREHENSIVE: features/003-notifications/plan.md
        assert "features" in str(path)
        assert "003-notifications" in str(path)
        assert "plan.md" in str(path)


class TestDocumentStructureValidation:
    """Tests for DocumentStructure validation methods."""

    def test_validate_structure_type_valid_flat(self):
        """Test validation with valid FLAT structure type."""
        # Should not raise
        DocumentStructure.validate_structure_type(StructureType.FLAT)

    def test_validate_structure_type_valid_comprehensive(self):
        """Test validation with valid COMPREHENSIVE structure type."""
        # Should not raise
        DocumentStructure.validate_structure_type(StructureType.COMPREHENSIVE)

    def test_validate_structure_type_invalid(self):
        """Test validation with invalid structure type."""
        with pytest.raises((ValueError, TypeError)):
            DocumentStructure.validate_structure_type("invalid_type")  # type: ignore[arg-type]


class TestDocumentStructureCreation:
    """Tests for DocumentStructure.create() factory method."""

    def test_create_flat_structure(self, tmp_path):
        """Test creating FLAT structure with 5 or fewer features."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=3)

        assert structure.type == StructureType.FLAT
        assert structure.root_dir == tmp_path / "docs"
        assert structure.index_file == tmp_path / "docs" / "index.md"
        assert structure.directories == []

    def test_create_comprehensive_structure(self, tmp_path):
        """Test creating COMPREHENSIVE structure with 6+ features."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=10)

        assert structure.type == StructureType.COMPREHENSIVE
        assert structure.root_dir == tmp_path / "docs"
        assert structure.directories == ["features", "guides", "api", "architecture"]

    def test_create_boundary_5_features(self, tmp_path):
        """Test creating structure with exactly 5 features (boundary)."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=5)

        assert structure.type == StructureType.FLAT
        assert structure.directories == []

    def test_create_boundary_6_features(self, tmp_path):
        """Test creating structure with exactly 6 features (boundary)."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=6)

        assert structure.type == StructureType.COMPREHENSIVE
        assert len(structure.directories) == 4


class TestDocumentStructureFeaturePath:
    """Tests for get_feature_path() method."""

    def test_get_feature_path_flat(self, tmp_path):
        """Test get_feature_path() for FLAT structure."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=3)
        path = structure.get_feature_path("user-auth")

        assert path == tmp_path / "docs" / "user-auth.md"
        assert "user-auth.md" in str(path)

    def test_get_feature_path_comprehensive(self, tmp_path):
        """Test get_feature_path() for COMPREHENSIVE structure."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=10)
        path = structure.get_feature_path("api-integration")

        assert path == tmp_path / "docs" / "features" / "api-integration.md"
        assert "features" in str(path)
        assert "api-integration.md" in str(path)


class TestDocumentStructureDirectoryCreation:
    """Tests for create_directories() method."""

    def test_create_directories_flat(self, tmp_path):
        """Test create_directories() for FLAT structure."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=3)
        structure.create_directories()

        # docs/ should exist
        assert structure.root_dir.exists()
        assert structure.root_dir.is_dir()

        # _static and _templates should exist
        assert (structure.root_dir / "_static").exists()
        assert (structure.root_dir / "_templates").exists()

        # Feature subdirectories should NOT exist for FLAT
        assert not (structure.root_dir / "features").exists()
        assert not (structure.root_dir / "guides").exists()

    def test_create_directories_comprehensive(self, tmp_path):
        """Test create_directories() for COMPREHENSIVE structure."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=10)
        structure.create_directories()

        # docs/ should exist
        assert structure.root_dir.exists()

        # All subdirectories should exist
        assert (structure.root_dir / "features").exists()
        assert (structure.root_dir / "guides").exists()
        assert (structure.root_dir / "api").exists()
        assert (structure.root_dir / "architecture").exists()

        # _static and _templates should also exist
        assert (structure.root_dir / "_static").exists()
        assert (structure.root_dir / "_templates").exists()

    def test_create_directories_idempotent(self, tmp_path):
        """Test that create_directories() can be called multiple times."""
        structure = DocumentStructure.create(project_root=tmp_path, feature_count=10)

        # Call twice - should not raise
        structure.create_directories()
        structure.create_directories()

        # All directories should still exist
        assert structure.root_dir.exists()
        assert (structure.root_dir / "features").exists()
