"""Document representation for parsed Markdown files."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .markdown_parser import MarkdownParser, Section


@dataclass
class Document:
    """Represents a parsed Markdown document from a spec-kit feature."""

    file_path: Path  # Path to the source Markdown file
    title: str  # Document title (from first H1 or filename)
    sections: list[Section]  # Top-level sections
    metadata: dict[str, Any] = field(default_factory=dict)  # YAML frontmatter

    @property
    def last_modified(self) -> float:
        """
        Get the last modification time of the source file.

        Returns:
            Unix timestamp of last modification
        """
        if self.file_path.exists():
            return os.path.getmtime(self.file_path)
        return 0.0

    def is_changed(self, since: float) -> bool:
        """
        Check if document has been modified since a given timestamp.

        Args:
            since: Unix timestamp to compare against

        Returns:
            True if document was modified after the given timestamp
        """
        return self.last_modified > since

    @staticmethod
    def parse(file_path: Path, parser: MarkdownParser | None = None) -> "Document":
        """
        Parse a Markdown file into a Document.

        Args:
            file_path: Path to the Markdown file
            parser: MarkdownParser instance (creates new one if None)

        Returns:
            Document instance with parsed content

        Raises:
            FileNotFoundError: If file does not exist
            MarkdownParseError: If parsing fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Create parser if not provided
        if parser is None:
            parser = MarkdownParser(enable_myst=True)

        # Extract metadata (YAML frontmatter)
        metadata = parser.extract_metadata(content)

        # Parse sections
        sections = parser.parse(content)

        # Determine title
        if "title" in metadata:
            title = metadata["title"]
        elif sections and sections[0].level == 1:
            # Use first H1 as title
            title = sections[0].title
        else:
            # Use filename as fallback
            title = file_path.stem.replace("-", " ").title()

        return Document(
            file_path=file_path,
            title=title,
            sections=sections,
            metadata=metadata,
        )

    def to_sphinx_md(self) -> str:
        """
        Convert document to Sphinx MyST Markdown format.

        Returns:
            Full document content in MyST Markdown
        """
        lines = []

        # Add title if not already in first section
        if not self.sections or self.sections[0].title != self.title:
            lines.append(f"# {self.title}\n")

        # Convert all sections recursively
        for section in self.sections:
            lines.append(self._section_to_markdown(section, "sphinx"))

        return "\n".join(lines)

    def to_mkdocs_md(self) -> str:
        """
        Convert document to MkDocs Markdown format.

        Returns:
            Full document content in MkDocs Markdown
        """
        lines = []

        # Add title if not already in first section
        if not self.sections or self.sections[0].title != self.title:
            lines.append(f"# {self.title}\n")

        # Convert all sections recursively
        for section in self.sections:
            lines.append(self._section_to_markdown(section, "mkdocs"))

        return "\n".join(lines)

    def _section_to_markdown(self, section: Section, format: str) -> str:
        """
        Convert section and its subsections to Markdown.

        Args:
            section: Section to convert
            format: "sphinx" or "mkdocs"

        Returns:
            Section content in Markdown format
        """
        # Convert main section
        heading_prefix = "#" * section.level
        content = f"{heading_prefix} {section.title}\n\n{section.content}"

        # Convert subsections recursively
        if section.subsections:
            subsection_content = []
            for subsection in section.subsections:
                subsection_content.append(self._section_to_markdown(subsection, format))
            content += "\n\n" + "\n\n".join(subsection_content)

        return content

    def find_section(self, title: str, level: int | None = None) -> Section | None:
        """
        Find a section by title (and optionally level).

        Args:
            title: Section title to search for
            level: Optional heading level filter

        Returns:
            First matching Section, or None if not found
        """

        def search(sections: list[Section]) -> Section | None:
            for section in sections:
                if section.title == title and (level is None or section.level == level):
                    return section
                # Search in subsections
                result = search(section.subsections)
                if result:
                    return result
            return None

        return search(self.sections)

    def get_all_sections(self) -> list[Section]:
        """
        Get all sections (flattened list including subsections).

        Returns:
            List of all Section objects in document order
        """
        result: list[Section] = []

        def collect(sections: list[Section]) -> None:
            for section in sections:
                result.append(section)
                collect(section.subsections)

        collect(self.sections)
        return result
