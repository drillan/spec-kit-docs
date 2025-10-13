"""Markdown parser using markdown-it-py."""

from dataclasses import dataclass, field

try:
    from markdown_it import MarkdownIt
    from markdown_it.tree import SyntaxTreeNode
except ImportError:
    MarkdownIt = None
    SyntaxTreeNode = None

from ..utils.validation import MarkdownParseError


@dataclass
class Section:
    """Represents a section in a Markdown document."""

    title: str  # Section title (heading text)
    level: int  # Heading level (1-6)
    content: str  # Section body content (Markdown)
    line_start: int  # Starting line number
    line_end: int  # Ending line number
    subsections: list["Section"] = field(default_factory=list)  # Child sections

    def to_sphinx_md(self) -> str:
        """
        Convert section to Sphinx MyST Markdown format.

        Returns:
            Section content in MyST Markdown format
        """
        # MyST Markdown uses the same heading syntax as standard Markdown
        heading = "#" * self.level + " " + self.title
        return f"{heading}\n\n{self.content}"

    def to_mkdocs_md(self) -> str:
        """
        Convert section to MkDocs Markdown format.

        This includes converting MyST admonitions to MkDocs format.

        Returns:
            Section content in MkDocs Markdown format
        """
        heading = "#" * self.level + " " + self.title

        # Convert MyST admonitions to MkDocs format
        content = self.content

        # Convert ```{note} to !!! note
        import re
        content = re.sub(r'```\{(note|warning|tip|important|caution)\}', r'!!! \1', content)
        content = re.sub(r'```\n', '', content)  # Remove closing ```

        return f"{heading}\n\n{content}"

    def extract_code_blocks(self) -> list[str]:
        """
        Extract code blocks from section content.

        Returns:
            List of code block contents
        """
        import re

        # Match fenced code blocks
        pattern = r'```[\w]*\n(.*?)\n```'
        matches = re.findall(pattern, self.content, re.DOTALL)
        return matches


class MarkdownParser:
    """Parser for Markdown documents using markdown-it-py."""

    def __init__(self, enable_myst: bool = True):
        """
        Initialize Markdown parser.

        Args:
            enable_myst: Enable MyST Markdown syntax support

        Raises:
            MarkdownParseError: If markdown-it-py is not installed
        """
        if MarkdownIt is None:
            raise MarkdownParseError(
                "markdown-it-py がインストールされていません。",
                "'uv pip install markdown-it-py' を実行してインストールしてください。",
            )

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
        tokens = self.md.parse(content)
        sections = []
        current_section = None
        section_stack = []

        current_line = 0
        content_buffer = []

        for token in tokens:
            if token.type == "heading_open":
                # Save previous section if exists
                if current_section:
                    current_section.content = "\n".join(content_buffer).strip()
                    current_section.line_end = current_line
                    content_buffer = []

                # Create new section
                level = int(token.tag[1])  # Extract level from h1, h2, etc.
                current_line = token.map[0] if token.map else current_line

            elif token.type == "inline" and current_section is None:
                # This is a heading text
                title = token.content
                level = int(tokens[tokens.index(token) - 1].tag[1])

                current_section = Section(
                    title=title,
                    level=level,
                    content="",
                    line_start=current_line,
                    line_end=current_line,
                )

                # Handle section hierarchy
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()

                if section_stack:
                    section_stack[-1].subsections.append(current_section)
                else:
                    sections.append(current_section)

                section_stack.append(current_section)

            elif token.type == "heading_close":
                current_line += 1

            elif current_section and token.type != "heading_open":
                # Accumulate content for current section
                if token.content:
                    content_buffer.append(token.content)
                if token.map:
                    current_line = token.map[1]

        # Save last section
        if current_section and content_buffer:
            current_section.content = "\n".join(content_buffer).strip()
            current_section.line_end = current_line

        return sections

    def extract_headings(self, content: str) -> list[dict[str, any]]:
        """
        Extract all headings from Markdown content.

        Args:
            content: Markdown content string

        Returns:
            List of dicts with 'level', 'title', and 'line' keys
        """
        tokens = self.md.parse(content)
        headings = []

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                level = int(token.tag[1])
                line = token.map[0] if token.map else 0

                # Get heading text from next inline token
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    title = tokens[i + 1].content
                    headings.append({"level": level, "title": title, "line": line})

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
        pattern = r'```[\w]*\n(.*?)\n```'
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
        pattern = r'^---\n(.*?)\n---'
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
