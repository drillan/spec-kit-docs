"""Tests for parsers.document module."""

import tempfile
from pathlib import Path

import pytest

from speckit_docs.parsers.document import Document
from speckit_docs.parsers.markdown_parser import MarkdownParser


class TestDocument:
    """Tests for Document class."""

    @pytest.fixture
    def sample_markdown_file(self):
        """Create a sample Markdown file for testing."""
        content = """# Test Document

## Section 1

This is the content of section 1.

### Subsection 1.1

Subsection content.

## Section 2

More content here.
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            path = Path(f.name)

        yield path
        path.unlink()

    def test_parse_basic_document(self, sample_markdown_file):
        """Test parsing a basic Markdown document."""
        doc = Document.parse(sample_markdown_file)

        assert doc.file_path == sample_markdown_file
        assert doc.title == "Test Document"
        assert len(doc.sections) > 0

    def test_parse_with_custom_parser(self, sample_markdown_file):
        """Test parsing with a custom parser instance."""
        parser = MarkdownParser(enable_myst=True)
        doc = Document.parse(sample_markdown_file, parser=parser)

        assert doc is not None
        assert doc.title == "Test Document"

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            Document.parse(Path("/nonexistent/file.md"))

    def test_last_modified(self, sample_markdown_file):
        """Test last_modified property."""
        doc = Document.parse(sample_markdown_file)
        assert doc.last_modified > 0

    def test_is_changed(self, sample_markdown_file):
        """Test is_changed method."""
        doc = Document.parse(sample_markdown_file)

        # Should be changed since timestamp 0
        assert doc.is_changed(0)

        # Should not be changed since future timestamp
        import time
        future_timestamp = time.time() + 1000
        assert not doc.is_changed(future_timestamp)

    def test_to_sphinx_md(self, sample_markdown_file):
        """Test conversion to Sphinx MyST Markdown."""
        doc = Document.parse(sample_markdown_file)
        sphinx_md = doc.to_sphinx_md()

        assert isinstance(sphinx_md, str)
        assert len(sphinx_md) > 0

    def test_to_mkdocs_md(self, sample_markdown_file):
        """Test conversion to MkDocs Markdown."""
        doc = Document.parse(sample_markdown_file)
        mkdocs_md = doc.to_mkdocs_md()

        assert isinstance(mkdocs_md, str)
        assert len(mkdocs_md) > 0

    def test_find_section(self, sample_markdown_file):
        """Test find_section method."""
        doc = Document.parse(sample_markdown_file)

        # Find by title
        section = doc.find_section("Section 1")
        if section:
            assert section.title == "Section 1"

    def test_get_all_sections(self, sample_markdown_file):
        """Test get_all_sections method."""
        doc = Document.parse(sample_markdown_file)
        all_sections = doc.get_all_sections()

        assert isinstance(all_sections, list)
        # Should include both top-level sections and subsections
        assert len(all_sections) >= 2
