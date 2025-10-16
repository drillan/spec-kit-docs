"""Data models for speckit-docs.

This module defines core data structures used throughout the application,
including enumerations and entity classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class FeatureStatus(Enum):
    """Status of a feature in the spec-kit project.

    Attributes:
        DRAFT: Feature is in draft state
        PLANNED: Feature has been planned
        IN_PROGRESS: Feature implementation is in progress
        COMPLETED: Feature implementation is completed
    """

    DRAFT = "draft"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DocumentType(Enum):
    """Type of document in a feature.

    Attributes:
        SPEC: Specification document (spec.md)
        PLAN: Implementation plan document (plan.md)
        TASKS: Task breakdown document (tasks.md)
    """

    SPEC = "spec"
    PLAN = "plan"
    TASKS = "tasks"


class GitStatus(Enum):
    """Git status of a file.

    Attributes:
        UNTRACKED: File is not tracked by Git
        MODIFIED: File has been modified
        STAGED: File has been staged for commit
        COMMITTED: File has been committed
    """

    UNTRACKED = "untracked"
    MODIFIED = "modified"
    STAGED = "staged"
    COMMITTED = "committed"


class StructureType(Enum):
    """Documentation structure type.

    Attributes:
        FLAT: Flat structure for projects with ≤5 features
        COMPREHENSIVE: Comprehensive structure for projects with >5 features
    """

    FLAT = "flat"
    COMPREHENSIVE = "comprehensive"


class GeneratorTool(Enum):
    """Documentation generator tool.

    Attributes:
        SPHINX: Sphinx documentation generator
        MKDOCS: MkDocs documentation generator
    """

    SPHINX = "sphinx"
    MKDOCS = "mkdocs"


# Entity Classes


@dataclass(frozen=True)
class Feature:
    """Represents a feature specification in a spec-kit project.

    Corresponds to a directory in `.specify/specs/###-feature-name/`.

    Attributes:
        id: Feature number (e.g., "001", "002")
        name: Feature name (e.g., "user-auth", "draft-init-spec")
        directory_path: Absolute path to feature directory
        spec_file: Path to spec.md file (required)
        status: Feature status
        plan_file: Path to plan.md file (optional)
        tasks_file: Path to tasks.md file (optional)
        priority: Priority level (e.g., "P1", "P2", "P3")
        metadata: Additional metadata (creation date, update date, tags, etc.)
    """

    id: str
    name: str
    directory_path: Path
    spec_file: Path
    status: FeatureStatus
    plan_file: Path | None = None
    tasks_file: Path | None = None
    priority: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    """Represents a Markdown section within a document.

    A section includes a heading and its content, and can contain nested subsections.

    Attributes:
        title: Section title (heading text)
        level: Heading level (1-6, number of # symbols)
        content: Section body in Markdown (excluding heading)
        line_start: Starting line number in document
        line_end: Ending line number in document
        subsections: Child sections (recursive structure)
    """

    title: str
    level: int
    content: str
    line_start: int
    line_end: int
    subsections: list["Section"] = field(default_factory=list)

    def to_sphinx_md(self) -> str:
        """Convert section to Sphinx Markdown (MyST) format.

        Generates Markdown with heading and content, recursively including
        all subsections.

        Returns:
            Sphinx-compatible Markdown string
        """
        # Generate heading with appropriate number of # symbols
        heading = "#" * self.level + " " + self.title

        # Start with heading and content
        parts = [heading]
        if self.content.strip():
            parts.append(self.content.strip())

        # Add subsections recursively
        for subsection in self.subsections:
            parts.append(subsection.to_sphinx_md())

        return "\n\n".join(parts)

    def to_mkdocs_md(self) -> str:
        """Convert section to MkDocs Markdown format.

        Generates Markdown with heading and content, recursively including
        all subsections. Currently identical to Sphinx format as both use
        standard Markdown for basic sections.

        Returns:
            MkDocs-compatible Markdown string
        """
        # For basic sections, MkDocs uses the same Markdown as Sphinx
        # Differences mainly appear in admonitions and special directives
        heading = "#" * self.level + " " + self.title

        parts = [heading]
        if self.content.strip():
            parts.append(self.content.strip())

        for subsection in self.subsections:
            parts.append(subsection.to_mkdocs_md())

        return "\n\n".join(parts)


@dataclass
class Document:
    """Represents an individual Markdown document within a feature.

    Can be spec.md, plan.md, or tasks.md.

    Attributes:
        file_path: Absolute path to document file
        type: Document type (SPEC, PLAN, or TASKS)
        content: Raw document content (Markdown)
        sections: Parsed section list
        last_modified: File last modification timestamp
        git_status: Git status of the file
    """

    file_path: Path
    type: DocumentType
    content: str
    sections: list[Section] = field(default_factory=list)
    last_modified: datetime | None = None
    git_status: GitStatus = GitStatus.UNTRACKED


@dataclass(frozen=True)
class SpecKitProject:
    """Represents a spec-kit project.

    Attributes:
        root_dir: Project root directory absolute path
        specify_dir: .specify/ directory absolute path
        specs_dir: specs/ directory absolute path
        git_repo: Whether it's a Git repository
    """

    root_dir: Path
    specify_dir: Path
    specs_dir: Path
    git_repo: bool

    def __post_init__(self) -> None:
        """Validation rules."""
        if not self.root_dir.is_dir():
            raise ValueError(f"Project root directory does not exist: {self.root_dir}")
        if not self.specify_dir.is_dir():
            raise ValueError(f".specify/ directory does not exist: {self.specify_dir}")
        if not self.specs_dir.is_dir():
            raise ValueError(f"specs/ directory does not exist: {self.specs_dir}")


@dataclass(frozen=True)
class DocumentationSite:
    """Represents a generated documentation site.

    Attributes:
        root_dir: Documentation root directory (e.g., {project}/docs/)
        tool_type: Documentation tool (Sphinx/MkDocs)
        structure_type: Documentation structure (FLAT/COMPREHENSIVE)
        project_name: Project name
        author: Author name (for Sphinx)
        version: Version (for Sphinx)
        language: Language (for Sphinx, default: ja)
        site_name: Site name (for MkDocs)
        repo_url: Repository URL (for MkDocs)
        feature_pages: List of generated feature page paths
    """

    root_dir: Path
    tool_type: GeneratorTool
    structure_type: StructureType
    project_name: str
    author: str | None = None
    version: str | None = None
    language: str = "ja"
    site_name: str | None = None
    repo_url: str | None = None
    feature_pages: list[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validation rules."""
        if not self.root_dir.is_dir():
            raise ValueError(f"Documentation root directory does not exist: {self.root_dir}")
        if not self.project_name:
            raise ValueError("Project name cannot be empty")

        # Sphinx-specific validation
        if self.tool_type == GeneratorTool.SPHINX:
            conf_py = self.root_dir / "conf.py"
            if not conf_py.is_file():
                raise ValueError(f"Sphinx conf.py not found: {conf_py}")

        # MkDocs-specific validation
        if self.tool_type == GeneratorTool.MKDOCS:
            mkdocs_yml = self.root_dir / "mkdocs.yml"
            if not mkdocs_yml.is_file():
                raise ValueError(f"MkDocs mkdocs.yml not found: {mkdocs_yml}")

    @property
    def features_dir(self) -> Path | None:
        """Feature pages directory (COMPREHENSIVE structure only)."""
        if self.structure_type == StructureType.COMPREHENSIVE:
            return self.root_dir / "features"
        return None


@dataclass
class GeneratorConfig:
    """Configuration for documentation generator.

    Used to configure Sphinx or MkDocs documentation generation.

    Attributes:
        tool: Documentation generator tool (SPHINX or MKDOCS)
        project_name: Project name for documentation
        author: Author name
        version: Project version string
        language: Documentation language code (e.g., "en", "ja")
        theme: Theme name (e.g., "alabaster", "furo" for Sphinx; "material" for MkDocs)
        extensions: List of extensions to enable (Sphinx extensions or MkDocs plugins)
        plugins: List of plugins to enable (primarily for MkDocs)
        custom_settings: Additional custom settings as key-value pairs
    """

    tool: GeneratorTool
    project_name: str
    author: str
    version: str
    language: str = "en"
    theme: str | None = None
    extensions: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)
    custom_settings: dict[str, Any] = field(default_factory=dict)

    def to_sphinx_conf(self) -> dict[str, Any]:
        """Convert configuration to Sphinx conf.py dictionary.

        Returns:
            Dictionary with Sphinx configuration values
        """
        conf: dict[str, Any] = {
            "project": self.project_name,
            "author": self.author,
            "version": self.version,
            "language": self.language,
            "extensions": self.extensions,
        }

        # Add theme if specified
        if self.theme:
            conf["html_theme"] = self.theme

        # Merge custom settings
        conf.update(self.custom_settings)

        return conf

    def to_mkdocs_yaml(self) -> dict[str, Any]:
        """Convert configuration to MkDocs YAML dictionary.

        Returns:
            Dictionary with MkDocs configuration values
        """
        mkdocs_config: dict[str, Any] = {
            "site_name": self.project_name,
            "site_author": self.author,
            "theme": {"name": self.theme or "material"},
            "plugins": self.plugins if self.plugins else ["search"],
        }

        # Merge custom settings
        mkdocs_config.update(self.custom_settings)

        return mkdocs_config
