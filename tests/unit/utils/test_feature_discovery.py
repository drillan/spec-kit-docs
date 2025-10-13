"""Unit tests for FeatureDiscoverer (T015)."""

from pathlib import Path

import pytest

from speckit_docs.models import FeatureStatus
from speckit_docs.utils.feature_discovery import FeatureDiscoverer


class TestFeatureDiscoverer:
    """Tests for FeatureDiscoverer class."""

    def test_discover_features_basic(self, tmp_path):
        """Test discovering features from specs/ directory."""
        # Create specs directory structure
        (tmp_path / "specs" / "001-user-auth").mkdir(parents=True)
        (tmp_path / "specs" / "001-user-auth" / "spec.md").write_text("# User Auth")
        (tmp_path / "specs" / "002-api-integration").mkdir(parents=True)
        (tmp_path / "specs" / "002-api-integration" / "spec.md").write_text(
            "# API Integration"
        )

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify
        assert len(features) == 2
        assert features[0].id == "001"
        assert features[0].name == "user-auth"
        assert features[0].spec_file.exists()
        assert features[1].id == "002"
        assert features[1].name == "api-integration"
        assert features[1].spec_file.exists()

    def test_discover_features_with_plan_and_tasks(self, tmp_path):
        """Test discovering features with plan.md and tasks.md files."""
        # Create feature with all files
        feature_dir = tmp_path / "specs" / "001-user-auth"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# User Auth")
        (feature_dir / "plan.md").write_text("# Plan")
        (feature_dir / "tasks.md").write_text("# Tasks")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify
        assert len(features) == 1
        assert features[0].plan_file is not None
        assert features[0].plan_file.exists()
        assert features[0].tasks_file is not None
        assert features[0].tasks_file.exists()

    def test_discover_features_without_plan_and_tasks(self, tmp_path):
        """Test discovering features without plan.md and tasks.md."""
        # Create feature with only spec.md
        feature_dir = tmp_path / "specs" / "001-user-auth"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# User Auth")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify
        assert len(features) == 1
        assert features[0].plan_file is None
        assert features[0].tasks_file is None

    def test_discover_features_skips_without_spec(self, tmp_path):
        """Test that directories without spec.md are skipped."""
        # Create directory without spec.md
        (tmp_path / "specs" / "001-invalid").mkdir(parents=True)
        # Create valid directory
        (tmp_path / "specs" / "002-valid").mkdir(parents=True)
        (tmp_path / "specs" / "002-valid" / "spec.md").write_text("# Valid")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify only valid feature is discovered
        assert len(features) == 1
        assert features[0].id == "002"

    def test_discover_features_skips_files(self, tmp_path):
        """Test that files in specs/ directory are skipped."""
        # Create specs directory with file
        (tmp_path / "specs").mkdir(parents=True)
        (tmp_path / "specs" / "README.md").write_text("# README")
        # Create valid directory
        (tmp_path / "specs" / "001-valid").mkdir()
        (tmp_path / "specs" / "001-valid" / "spec.md").write_text("# Valid")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify only directory is discovered
        assert len(features) == 1

    def test_discover_features_empty_specs_dir(self, tmp_path):
        """Test discovering features from empty specs/ directory."""
        # Create empty specs directory
        (tmp_path / "specs").mkdir()

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify no features found
        assert len(features) == 0

    def test_discover_features_no_specs_dir(self, tmp_path):
        """Test discovering features when specs/ directory doesn't exist."""
        # Don't create specs directory

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify no features found
        assert len(features) == 0

    def test_discover_features_sorted_by_id(self, tmp_path):
        """Test that features are sorted by directory name."""
        # Create features in random order
        (tmp_path / "specs" / "003-third").mkdir(parents=True)
        (tmp_path / "specs" / "003-third" / "spec.md").write_text("# Third")
        (tmp_path / "specs" / "001-first").mkdir(parents=True)
        (tmp_path / "specs" / "001-first" / "spec.md").write_text("# First")
        (tmp_path / "specs" / "002-second").mkdir(parents=True)
        (tmp_path / "specs" / "002-second" / "spec.md").write_text("# Second")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify sorted order
        assert len(features) == 3
        assert features[0].id == "001"
        assert features[1].id == "002"
        assert features[2].id == "003"

    def test_discover_features_status_is_draft(self, tmp_path):
        """Test that discovered features have DRAFT status."""
        # Create feature
        (tmp_path / "specs" / "001-feature").mkdir(parents=True)
        (tmp_path / "specs" / "001-feature" / "spec.md").write_text("# Feature")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify status
        assert len(features) == 1
        assert features[0].status == FeatureStatus.DRAFT

    def test_discover_features_directory_path(self, tmp_path):
        """Test that feature directory_path is set correctly."""
        # Create feature
        feature_dir = tmp_path / "specs" / "001-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# Feature")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify directory_path
        assert len(features) == 1
        assert features[0].directory_path == feature_dir

    def test_discover_features_name_without_prefix(self, tmp_path):
        """Test feature name extraction without numeric prefix."""
        # Create feature with name-only directory
        (tmp_path / "specs" / "feature-name").mkdir(parents=True)
        (tmp_path / "specs" / "feature-name" / "spec.md").write_text("# Feature")

        # Discover features
        discoverer = FeatureDiscoverer(tmp_path)
        features = discoverer.discover_features()

        # Verify id and name
        assert len(features) == 1
        assert features[0].id == "feature"
        assert features[0].name == "name"
