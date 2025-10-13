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
