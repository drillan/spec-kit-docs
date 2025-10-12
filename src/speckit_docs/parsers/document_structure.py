"""Document structure management for speckit-docs."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


class StructureType(Enum):
    """Document structure type."""

    FLAT = "FLAT"  # 5 features or less
    COMPREHENSIVE = "COMPREHENSIVE"  # 6+ features


@dataclass
class DocumentStructure:
    """Represents the document site structure."""

    type: StructureType  # FLAT or COMPREHENSIVE
    root_dir: Path  # docs/ directory
    directories: List[str]  # Subdirectories to create
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
