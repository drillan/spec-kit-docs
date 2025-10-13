"""Feature discovery utilities for spec-kit projects."""

from pathlib import Path

from ..models import Feature, FeatureStatus


class FeatureDiscoverer:
    """Discover features from specs/ directory in a spec-kit project."""

    def __init__(self, repo_path: Path = Path(".")) -> None:
        """
        Initialize the feature discoverer.

        Args:
            repo_path: Path to the repository root (defaults to current directory)
        """
        self.repo_path = repo_path
        self.specs_dir = repo_path / "specs"

    def discover_features(self) -> list[Feature]:
        """
        Discover all features in the specs/ directory.

        Returns:
            List of Feature objects sorted by directory name

        Note:
            - Only directories with spec.md are considered features
            - Features are sorted by directory name (natural sort)
            - All discovered features have DRAFT status by default
        """
        if not self.specs_dir.exists():
            return []

        features: list[Feature] = []

        for feature_dir in sorted(self.specs_dir.iterdir()):
            # Skip files, only process directories
            if not feature_dir.is_dir():
                continue

            # Skip directories without spec.md
            spec_file = feature_dir / "spec.md"
            if not spec_file.exists():
                continue

            # Extract feature ID and name from directory name
            # Format: "NNN-feature-name" → id="NNN", name="feature-name"
            dir_name = feature_dir.name
            parts = dir_name.split("-", 1)
            feature_id = parts[0] if len(parts) > 0 else dir_name
            feature_name = parts[1] if len(parts) > 1 else dir_name

            # Check for optional files
            plan_file = feature_dir / "plan.md"
            tasks_file = feature_dir / "tasks.md"

            # Create Feature object
            feature = Feature(
                id=feature_id,
                name=feature_name,
                directory_path=feature_dir,
                spec_file=spec_file,
                status=FeatureStatus.DRAFT,
                plan_file=plan_file if plan_file.exists() else None,
                tasks_file=tasks_file if tasks_file.exists() else None,
            )
            features.append(feature)

        return features
