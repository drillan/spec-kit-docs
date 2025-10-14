"""Document structure management for speckit-docs."""

from dataclasses import dataclass
from pathlib import Path

from ..models import StructureType


@dataclass
class DocumentStructure:
    """Represents the document site structure."""

    type: StructureType  # FLAT or COMPREHENSIVE
    root_dir: Path  # docs/ directory
    directories: list[str]  # Subdirectories to create
    index_file: Path  # index.md path

    @staticmethod
    def determine_structure(feature_count: int) -> StructureType:
        """
        Determine structure type based on feature count.

        Args:
            feature_count: Number of features

        Returns:
            FLAT if 5 or fewer features, COMPREHENSIVE otherwise
        """
        return StructureType.FLAT if feature_count <= 5 else StructureType.COMPREHENSIVE

    @classmethod
    def create(cls, project_root: Path, feature_count: int) -> "DocumentStructure":
        """
        Create DocumentStructure based on feature count.

        Args:
            project_root: Project root directory
            feature_count: Number of features

        Returns:
            DocumentStructure instance
        """
        structure_type = cls.determine_structure(feature_count)
        root_dir = project_root / "docs"
        index_file = root_dir / "index.md"

        if structure_type == StructureType.FLAT:
            directories = []
        else:
            directories = ["features", "guides", "api", "architecture"]

        return cls(
            type=structure_type, root_dir=root_dir, directories=directories, index_file=index_file
        )

    def get_feature_path(self, feature_name: str) -> Path:
        """
        Get the path for a feature document.

        Args:
            feature_name: Feature name (without .md extension)

        Returns:
            Path to feature document file
        """
        if self.type == StructureType.FLAT:
            return self.root_dir / f"{feature_name}.md"
        else:
            return self.root_dir / "features" / f"{feature_name}.md"

    def create_directories(self) -> None:
        """Create all required directories."""
        self.root_dir.mkdir(parents=True, exist_ok=True)

        for dir_name in self.directories:
            (self.root_dir / dir_name).mkdir(exist_ok=True)

        # Create _static and _templates for Sphinx
        (self.root_dir / "_static").mkdir(exist_ok=True)
        (self.root_dir / "_templates").mkdir(exist_ok=True)

    @staticmethod
    def get_feature_page_path(
        structure_type: StructureType, feature_id: str, feature_name: str
    ) -> Path:
        """Get the path for a feature page based on structure type.

        Args:
            structure_type: FLAT or COMPREHENSIVE structure type
            feature_id: Feature ID (e.g., "001")
            feature_name: Feature name (e.g., "user-auth")

        Returns:
            Path to feature page (relative to docs/)
        """
        feature_slug = f"{feature_id}-{feature_name}"
        if structure_type == StructureType.FLAT:
            # FLAT: features/001-user-auth.md (single file per feature)
            return Path("features") / f"{feature_slug}.md"
        else:
            # COMPREHENSIVE: features/001-user-auth/index.md (directory per feature)
            return Path("features") / feature_slug / "index.md"

    @staticmethod
    def get_feature_subpage_path(feature_id: str, feature_name: str, subpage_name: str) -> Path:
        """Get the path for a feature subpage (COMPREHENSIVE structure only).

        Args:
            feature_id: Feature ID (e.g., "003")
            feature_name: Feature name (e.g., "notifications")
            subpage_name: Subpage name (e.g., "plan", "tasks")

        Returns:
            Path to feature subpage (relative to docs/)
        """
        feature_slug = f"{feature_id}-{feature_name}"
        return Path("features") / feature_slug / f"{subpage_name}.md"

    @staticmethod
    def validate_structure_type(structure_type: StructureType) -> None:
        """Validate that structure type is a valid StructureType enum.

        Args:
            structure_type: Structure type to validate

        Raises:
            ValueError: If structure_type is not a valid StructureType
            TypeError: If structure_type is not a StructureType instance
        """
        from enum import Enum

        # Check if it's an Enum instance (correct way to check enum membership)
        if not isinstance(structure_type, Enum):
            raise TypeError(f"Expected StructureType enum, got {type(structure_type)}")

        # Check if it's specifically a StructureType
        if not isinstance(structure_type, type(StructureType.FLAT)):
            raise TypeError(f"Expected StructureType, got {type(structure_type)}")

        # Additional validation: ensure it's one of the valid values
        valid_types = {StructureType.FLAT, StructureType.COMPREHENSIVE}
        if structure_type not in valid_types:
            raise ValueError(f"Invalid structure type: {structure_type}")
