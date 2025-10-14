"""Feature scanner for discovering spec-kit features."""

import re
from pathlib import Path

from ..models import Feature, FeatureStatus
from ..utils.validation import ProjectValidationError


class FeatureScanner:
    """Scanner for discovering spec-kit features in specs/."""

    FEATURE_DIR_PATTERN = re.compile(r"^(\d{3})-(.+)$")

    def __init__(self, project_root: Path | None = None):
        """
        Initialize feature scanner.

        Args:
            project_root: Optional project root path (defaults to current directory)

        Raises:
            ProjectValidationError: If specs directory does not exist
        """
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = project_root
        self.specs_dir = project_root / "specs"

        if not self.specs_dir.exists():
            raise ProjectValidationError(
                "specs/ ディレクトリが見つかりません。",
                "'specify init' を実行してspec-kitプロジェクトを初期化してください。",
            )

    def scan(self, require_spec: bool = True) -> list[Feature]:
        """
        Scan specs directory for features.

        Args:
            require_spec: If True, only include features with spec.md (FR-001)

        Returns:
            List of Feature objects, sorted by feature ID

        Raises:
            ProjectValidationError: If no features are found
        """
        features = []

        # Iterate through directories in specs/
        for item in self.specs_dir.iterdir():
            if not item.is_dir():
                continue

            # Match feature directory pattern (###-feature-name)
            match = self.FEATURE_DIR_PATTERN.match(item.name)
            if not match:
                continue

            feature_id = match.group(1)
            feature_name = match.group(2)

            # Check for spec.md (required by FR-001)
            spec_file = item / "spec.md"
            if not spec_file.exists():
                if require_spec:
                    continue
                # Skip features without spec.md since it's required by Feature model
                continue

            # Check for optional files
            plan_file = item / "plan.md" if (item / "plan.md").exists() else None
            tasks_file = item / "tasks.md" if (item / "tasks.md").exists() else None

            # Determine status based on which files exist
            if tasks_file and plan_file:
                status = FeatureStatus.IN_PROGRESS
            elif plan_file:
                status = FeatureStatus.PLANNED
            else:
                status = FeatureStatus.DRAFT

            # Create Feature object
            feature = Feature(
                id=feature_id,
                name=feature_name,
                directory_path=item,
                spec_file=spec_file,
                status=status,
                plan_file=plan_file,
                tasks_file=tasks_file,
            )

            features.append(feature)

        # Sort by feature ID
        features.sort(key=lambda f: f.id)

        if require_spec and not features:
            raise ProjectValidationError(
                "機能が見つかりませんでした。",
                "'specify new' で機能を作成してください。",
            )

        return features

    def get_feature(self, feature_id: str) -> Feature | None:
        """
        Get a specific feature by ID.

        Args:
            feature_id: Feature ID (e.g., "001")

        Returns:
            Feature object if found, None otherwise
        """
        features = self.scan(require_spec=False)
        for feature in features:
            if feature.id == feature_id:
                return feature
        return None

    def count_features(self) -> int:
        """
        Count the number of features with spec.md.

        Returns:
            Number of features
        """
        return len(self.scan(require_spec=True))
