"""Base generator interface for documentation generation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..parsers.feature_scanner import Feature


@dataclass
class GeneratorConfig:
    """Configuration for documentation generator."""

    tool: str  # "sphinx" or "mkdocs"
    project_name: str
    author: str
    version: str = "0.1.0"
    language: str = "ja"
    theme: str = "alabaster"  # Default for Sphinx
    description: str = ""
    extensions: List[str] = None  # Sphinx extensions
    plugins: List[str] = None  # MkDocs plugins
    custom_settings: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.extensions is None:
            self.extensions = []
        if self.plugins is None:
            self.plugins = []
        if self.custom_settings is None:
            self.custom_settings = {}


@dataclass
class BuildResult:
    """Result of documentation build operation."""

    success: bool
    output_dir: Path
    warnings: List[str]
    errors: List[str]
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
    errors: List[str]
    warnings: List[str]
    checked_items: List[str]


class BaseGenerator(ABC):
    """Abstract base class for documentation generators."""

    def __init__(self, config: GeneratorConfig, project_root: Optional[Path] = None):
        """
        Initialize generator.

        Args:
            config: Generator configuration
            project_root: Optional project root path (defaults to current directory)
        """
        self.config = config
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs"

    @abstractmethod
    def init_project(self, structure_type: str = "FLAT") -> None:
        """
        Initialize documentation project.

        Args:
            structure_type: "FLAT" or "COMPREHENSIVE"

        Raises:
            DocumentationProjectError: If initialization fails
        """
        pass

    @abstractmethod
    def update_docs(self, features: List[Feature], incremental: bool = True) -> None:
        """
        Update documentation from features.

        Args:
            features: List of features to generate docs for
            incremental: If True, only update changed features

        Raises:
            MarkdownParseError: If parsing fails
            DocumentationProjectError: If update fails
        """
        pass

    @abstractmethod
    def build_docs(self) -> BuildResult:
        """
        Build HTML documentation.

        Returns:
            BuildResult with build status and metrics

        Raises:
            BuildError: If build fails
        """
        pass

    @abstractmethod
    def validate_project(self) -> ValidationResult:
        """
        Validate documentation project structure.

        Returns:
            ValidationResult with validation status

        Raises:
            DocumentationProjectError: If validation fails
        """
        pass

    def _create_docs_directory(self) -> None:
        """Create docs directory if it doesn't exist."""
        self.docs_dir.mkdir(exist_ok=True)

    def _create_subdirectories(self, structure_type: str) -> None:
        """
        Create subdirectories based on structure type.

        Args:
            structure_type: "FLAT" or "COMPREHENSIVE"
        """
        if structure_type == "COMPREHENSIVE":
            (self.docs_dir / "features").mkdir(exist_ok=True)
            (self.docs_dir / "guides").mkdir(exist_ok=True)
            (self.docs_dir / "api").mkdir(exist_ok=True)
            (self.docs_dir / "architecture").mkdir(exist_ok=True)
