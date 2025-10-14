"""Base generator interface for documentation generation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..models import StructureType

if TYPE_CHECKING:
    from ..models import Feature


@dataclass
class GeneratorConfig:
    """Configuration for documentation generator."""

    tool: str  # "sphinx" or "mkdocs"
    project_name: str
    author: str = "Unknown Author"
    version: str = "0.1.0"
    language: str = "ja"
    theme: str = "alabaster"  # Default for Sphinx
    description: str = ""
    site_name: str | None = None  # For MkDocs
    repo_url: str | None = None  # For MkDocs
    extensions: list[str] = field(default_factory=list)  # Sphinx extensions
    plugins: list[str] = field(default_factory=list)  # MkDocs plugins
    custom_settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildResult:
    """Result of documentation build operation."""

    success: bool
    output_dir: Path
    warnings: list[str]
    errors: list[str]
    build_time: float  # seconds
    file_count: int

    def is_valid(self, max_warnings: int = 10) -> bool:
        """
        Check if build result is valid.

        Args:
            max_warnings: Maximum number of warnings to tolerate

        Returns:
            True if no errors and warnings below threshold
        """
        return not self.errors and len(self.warnings) <= max_warnings

    def get_summary(self) -> str:
        """
        Get a summary string of build result.

        Returns:
            Human-readable build summary
        """
        status = "✓" if self.success else "✗"
        summary = [
            f"{status} HTMLビルドを実行しました",
            f"  - 警告: {len(self.warnings)}",
            f"  - エラー: {len(self.errors)}",
            f"  - ビルド時間: {self.build_time:.1f}秒",
            f"  - 生成ファイル: {self.file_count}個",
        ]
        return "\n".join(summary)


@dataclass
class ValidationResult:
    """Result of project validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    checked_items: list[str]

    def format_errors(self) -> str:
        """
        Format validation errors and warnings with suggestions.

        Returns:
            Formatted string with errors, warnings, and suggestions
        """
        output = []

        if self.errors:
            output.append("❌ エラー:")
            for error in self.errors:
                output.append(f"  • {error}")

        if self.warnings:
            output.append("\n⚠️  警告:")
            for warning in self.warnings:
                output.append(f"  • {warning}")

        if self.checked_items:
            output.append(f"\n✓ 検証項目: {len(self.checked_items)}個")

        if not self.is_valid:
            output.append("\n💡 提案:")
            output.append("  • プロジェクト構造を確認してください")
            output.append("  • 必要なファイルが存在することを確認してください")

        return "\n".join(output) if output else "✓ すべての検証に合格しました"


class BaseGenerator(ABC):
    """
    Abstract base class for documentation generators.

    This class provides a common interface for Sphinx and MkDocs generators.
    Subclasses must implement the abstract methods to generate tool-specific
    configuration and documentation structure.
    """

    def __init__(self, docs_dir: Path) -> None:
        """
        Initialize the generator.

        Args:
            docs_dir: Path to the documentation directory
        """
        self.docs_dir = docs_dir
        self.structure_type = StructureType.FLAT

    @abstractmethod
    def generate_config(self, **kwargs: Any) -> None:
        """
        Generate tool-specific configuration file.

        For Sphinx: conf.py
        For MkDocs: mkdocs.yml

        Args:
            **kwargs: Configuration parameters (project_name, author, version, etc.)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def generate_index(self) -> None:
        """
        Generate index page (index.md).

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def create_directory_structure(self) -> None:
        """
        Create directory structure based on structure_type.

        For FLAT structure (≤5 features):
            - docs/
              - index.md
              - feature-1.md
              - feature-2.md

        For COMPREHENSIVE structure (>5 features):
            - docs/
              - index.md
              - features/
                - feature-1.md
                - feature-2.md
              - guides/
              - api/
              - architecture/

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def init_project(self) -> None:
        """
        Initialize a new documentation project.

        This creates all necessary files and directories for a new documentation
        project, including configuration files, index page, and directory structure.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def update_docs(self, features: list["Feature"]) -> None:
        """
        Update documentation for given features.

        Args:
            features: List of features to generate documentation for

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def build_docs(self) -> BuildResult:
        """
        Build HTML documentation from source files.

        Returns:
            BuildResult with success status, warnings, errors, and build statistics

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def validate_project(self) -> ValidationResult:
        """
        Validate documentation project structure and configuration.

        Returns:
            ValidationResult indicating if project is valid, with error/warning messages

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    def determine_structure(self, feature_count: int) -> StructureType:
        """
        Determine structure type based on feature count (FR-005, FR-006).

        Args:
            feature_count: Number of features in the project

        Returns:
            StructureType.FLAT for 5 or fewer features
            StructureType.COMPREHENSIVE for 6 or more features
        """
        return StructureType.FLAT if feature_count <= 5 else StructureType.COMPREHENSIVE

    # Helper methods for backwards compatibility with existing implementations
    def _create_docs_directory(self) -> None:
        """Create docs directory if it doesn't exist."""
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def _create_subdirectories(self, structure_type: StructureType | str) -> None:
        """
        Create subdirectories based on structure type.

        Args:
            structure_type: StructureType or string ("FLAT" or "COMPREHENSIVE")
        """
        # Handle both StructureType enum and string
        is_comprehensive = (
            structure_type == StructureType.COMPREHENSIVE
            if isinstance(structure_type, StructureType)
            else structure_type == "COMPREHENSIVE"
        )

        if is_comprehensive:
            (self.docs_dir / "features").mkdir(parents=True, exist_ok=True)
            (self.docs_dir / "guides").mkdir(parents=True, exist_ok=True)
            (self.docs_dir / "api").mkdir(parents=True, exist_ok=True)
            (self.docs_dir / "architecture").mkdir(parents=True, exist_ok=True)

    def get_feature_doc_path(self, feature: "Feature", structure_type: StructureType | str) -> Path:
        """
        Get output file path for a feature document.

        Args:
            feature: Feature to generate path for
            structure_type: StructureType or string ("FLAT" or "COMPREHENSIVE")

        Returns:
            Path to the output Markdown file
        """
        # Handle both StructureType enum and string
        is_flat = (
            structure_type == StructureType.FLAT
            if isinstance(structure_type, StructureType)
            else structure_type == "FLAT"
        )

        if is_flat:
            # FLAT: docs/{feature-name}.md (5 features or less)
            return self.docs_dir / f"{feature.name}.md"
        else:
            # COMPREHENSIVE: docs/features/{feature-name}.md (6+ features)
            features_dir = self.docs_dir / "features"
            features_dir.mkdir(parents=True, exist_ok=True)
            return features_dir / f"{feature.name}.md"

    def determine_structure_type(self) -> str:
        """
        Determine the structure type of the current documentation project.

        Returns:
            "FLAT" or "COMPREHENSIVE"
        """
        # Check if features directory exists and has subdirectories
        features_dir = self.docs_dir / "features"
        if not features_dir.exists():
            return "FLAT"

        # If features directory contains files or subdirectories, it's COMPREHENSIVE
        has_contents = any(features_dir.iterdir())
        return "COMPREHENSIVE" if has_contents else "FLAT"
