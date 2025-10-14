"""Tests for parsers.feature_scanner module."""


import pytest

from speckit_docs.models import FeatureStatus
from speckit_docs.parsers.feature_scanner import FeatureScanner
from speckit_docs.utils.validation import ProjectValidationError


class TestFeatureScanner:
    """Tests for FeatureScanner class."""

    @pytest.fixture
    def mock_project_root(self, tmp_path):
        """Create a mock spec-kit project structure."""
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()

        # Create feature 001 with spec.md only
        feature1_dir = specs_dir / "001-feature-one"
        feature1_dir.mkdir()
        (feature1_dir / "spec.md").write_text("# Feature One\n")

        # Create feature 002 with spec.md and plan.md
        feature2_dir = specs_dir / "002-feature-two"
        feature2_dir.mkdir()
        (feature2_dir / "spec.md").write_text("# Feature Two\n")
        (feature2_dir / "plan.md").write_text("# Plan Two\n")

        # Create feature 003 with all files
        feature3_dir = specs_dir / "003-feature-three"
        feature3_dir.mkdir()
        (feature3_dir / "spec.md").write_text("# Feature Three\n")
        (feature3_dir / "plan.md").write_text("# Plan Three\n")
        (feature3_dir / "tasks.md").write_text("# Tasks Three\n")

        # Create invalid directory (no spec.md)
        invalid_dir = specs_dir / "004-invalid-feature"
        invalid_dir.mkdir()

        # Create non-matching directory name
        wrong_name_dir = specs_dir / "feature-wrong"
        wrong_name_dir.mkdir()

        return tmp_path

    def test_init_with_valid_project(self, mock_project_root):
        """Test initialization with valid spec-kit project."""
        scanner = FeatureScanner(mock_project_root)
        assert scanner.project_root == mock_project_root
        assert scanner.specs_dir == mock_project_root / "specs"

    def test_init_without_specs_dir(self, tmp_path):
        """Test initialization fails when specs/ doesn't exist."""
        with pytest.raises(ProjectValidationError):
            FeatureScanner(tmp_path)

    def test_scan_finds_all_features(self, mock_project_root):
        """Test scanning finds all valid features."""
        scanner = FeatureScanner(mock_project_root)
        features = scanner.scan(require_spec=True)

        assert len(features) == 3
        assert features[0].id == "001"
        assert features[1].id == "002"
        assert features[2].id == "003"

    def test_scan_feature_status(self, mock_project_root):
        """Test feature status detection."""
        scanner = FeatureScanner(mock_project_root)
        features = scanner.scan()

        # Feature 001: spec.md only → DRAFT
        assert features[0].status == FeatureStatus.DRAFT

        # Feature 002: spec.md + plan.md → PLANNED
        assert features[1].status == FeatureStatus.PLANNED

        # Feature 003: spec.md + plan.md + tasks.md → IN_PROGRESS
        assert features[2].status == FeatureStatus.IN_PROGRESS

    def test_scan_filters_without_spec(self, mock_project_root):
        """Test that features without spec.md are filtered out."""
        scanner = FeatureScanner(mock_project_root)
        features = scanner.scan(require_spec=True)

        # Should not include 004-invalid-feature
        feature_ids = [f.id for f in features]
        assert "004" not in feature_ids

    def test_get_feature_by_id(self, mock_project_root):
        """Test getting a specific feature by ID."""
        scanner = FeatureScanner(mock_project_root)

        feature = scanner.get_feature("002")
        assert feature is not None
        assert feature.id == "002"
        assert feature.name == "feature-two"

    def test_get_nonexistent_feature(self, mock_project_root):
        """Test getting a feature that doesn't exist."""
        scanner = FeatureScanner(mock_project_root)
        feature = scanner.get_feature("999")
        assert feature is None

    def test_count_features(self, mock_project_root):
        """Test counting features."""
        scanner = FeatureScanner(mock_project_root)
        count = scanner.count_features()
        assert count == 3

    def test_scan_empty_specs_dir(self, tmp_path):
        """Test scanning with empty specs/ directory."""
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()

        scanner = FeatureScanner(tmp_path)
        with pytest.raises(ProjectValidationError):
            scanner.scan(require_spec=True)

    def test_feature_file_paths(self, mock_project_root):
        """Test that feature file paths are correct."""
        scanner = FeatureScanner(mock_project_root)
        features = scanner.scan()

        feature = features[2]  # Feature 003 with all files
        assert feature.spec_file.exists()
        assert feature.plan_file is not None and feature.plan_file.exists()
        assert feature.tasks_file is not None and feature.tasks_file.exists()
