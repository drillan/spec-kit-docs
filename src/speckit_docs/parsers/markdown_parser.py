"""Markdown parser using markdown-it-py."""

from typing import Any

try:
    from markdown_it import MarkdownIt
    from markdown_it.tree import SyntaxTreeNode

    MARKDOWN_IT_AVAILABLE = True
except ImportError:
    MarkdownIt = None  # type: ignore[assignment,misc]
    SyntaxTreeNode = None  # type: ignore[assignment,misc]
    MARKDOWN_IT_AVAILABLE = False

from ..exceptions import SpecKitDocsError
from ..models import Section

__all__ = ["MarkdownParser", "Section"]


class MarkdownParser:
    """Parser for Markdown documents using markdown-it-py."""

    def __init__(self, enable_myst: bool = True) -> None:
        """
        Initialize Markdown parser.

        Args:
            enable_myst: Enable MyST Markdown syntax support

        Raises:
            SpecKitDocsError: If markdown-it-py is not installed
        """
        if not MARKDOWN_IT_AVAILABLE:
            raise SpecKitDocsError(
                "markdown-it-py がインストールされていません。",
                "'uv pip install markdown-it-py' を実行してインストールしてください。",
            )

        self.enable_myst = enable_myst  # Store enable_myst attribute

        # Initialize markdown-it parser
        self.md = MarkdownIt("commonmark")
        if enable_myst:
            # Enable MyST extensions
            self.md.enable(["table", "strikethrough"])

    def parse(self, content: str) -> list[Section]:
        """
        Parse Markdown content into a list of sections.

        Args:
            content: Markdown content string

        Returns:
            List of Section objects (top-level sections only)
        """
        if not content.strip():
            return []

        tokens = self.md.parse(content)
        sections: list[Section] = []
        section_stack: list[Section] = []

        pending_heading: dict[str, Any] | None = None
        content_lines: list[str] = content.split("\n")

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                level = int(token.tag[1])  # Extract level from h1, h2, etc.
                line_start = (token.map[0] + 1) if token.map else 1  # 1-based line numbers

                # Get heading text from next inline token
                title = ""
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    title = tokens[i + 1].content

                pending_heading = {
                    "level": level,
                    "title": title,
                    "line_start": line_start,
                }

            elif token.type == "heading_close" and pending_heading:
                # Create the section now
                level = pending_heading["level"]
                title = pending_heading["title"]
                line_start = pending_heading["line_start"]

                # Find content end (next heading or end of document)
                line_end = len(content_lines)
                for j in range(i + 1, len(tokens)):
                    if tokens[j].type == "heading_open":
                        token_map = tokens[j].map
                        if token_map:
                            line_end = token_map[0]
                            break

                # Extract section content
                section_content = "\n".join(content_lines[line_start:line_end]).strip()

                new_section = Section(
                    title=title,
                    level=level,
                    content=section_content,
                    line_start=line_start,
                    line_end=line_end,
                    subsections=[],
                )

                # Handle section hierarchy
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()

                if section_stack:
                    section_stack[-1].subsections.append(new_section)
                else:
                    sections.append(new_section)

                section_stack.append(new_section)
                pending_heading = None

        return sections

    def extract_headings(self, content: str) -> list[dict[str, Any]]:
        """
        Extract all headings from Markdown content.

        Args:
            content: Markdown content string

        Returns:
            List of dicts with 'level', 'text', and 'line' keys
        """
        tokens = self.md.parse(content)
        headings = []

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                level = int(token.tag[1])
                line = (token.map[0] + 1) if token.map else 1  # 1-based line numbers

                # Get heading text from next inline token
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    text = tokens[i + 1].content
                    headings.append({"level": level, "text": text, "line": line})

        return headings

    def extract_code_blocks(self, content: str) -> list[str]:
        """
        Extract code blocks from Markdown content.

        Args:
            content: Markdown content string

        Returns:
            List of code block contents
        """
        import re

        pattern = r"```[\w]*\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        return matches

    def extract_metadata(self, content: str) -> dict[str, str]:
        """
        Extract YAML frontmatter metadata from Markdown content.

        Args:
            content: Markdown content string

        Returns:
            Dictionary of metadata key-value pairs
        """
        import re

        # Match YAML frontmatter (--- ... ---)
        pattern = r"^---\n(.*?)\n---"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return {}

        try:
            import yaml

            metadata = yaml.safe_load(match.group(1))
            return metadata if isinstance(metadata, dict) else {}
        except Exception:
            # If yaml is not available or parsing fails, return empty dict
            return {}
