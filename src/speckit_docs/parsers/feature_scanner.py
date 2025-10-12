"""Feature scanner for discovering spec-kit features."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..utils.validation import ProjectValidationError


@dataclass
class Feature:
    """Represents a spec-kit feature."""

    id: str  # Feature number (e.g., "001")
    name: str  # Feature name (e.g., "user-auth")
    directory_path: Path  # Absolute path to feature directory
    spec_file: Optional[Path] = None  # Path to spec.md (required)
    plan_file: Optional[Path] = None  # Path to plan.md (optional)
    tasks_file: Optional[Path] = None  # Path to tasks.md (optional)
    priority: Optional[str] = None  # Priority (e.g., "P1", "P2", "P3")

    @property
    def file_name(self) -> str:
        """
        Get the file name for this feature (without number prefix).

        Returns:
            Feature name suitable for file naming (e.g., "user-auth.md")
        """
        return f"{self.name}.md"

    @property
    def title(self) -> str:
        """
        Get a human-readable title for this feature.

        Returns:
            Title with capitalized words (e.g., "User Auth")
        """
        # Replace hyphens with spaces and capitalize each word
        return " ".join(word.capitalize() for word in self.name.split("-"))


class FeatureScanner:
    """Scanner for discovering spec-kit features in specs/."""

    FEATURE_DIR_PATTERN = re.compile(r"^(\d{3})-(.+)$")

    def __init__(self, project_root: Optional[Path] = None):
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

    def scan(self, require_spec: bool = True) -> List[Feature]:
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
            if require_spec and not spec_file.exists():
                continue

            # Check for optional files
            plan_file = item / "plan.md" if (item / "plan.md").exists() else None
            tasks_file = item / "tasks.md" if (item / "tasks.md").exists() else None

            # Create Feature object
            feature = Feature(
                id=feature_id,
                name=feature_name,
                directory_path=item,
                spec_file=spec_file if spec_file.exists() else None,
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

    def get_feature(self, feature_id: str) -> Optional[Feature]:
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
