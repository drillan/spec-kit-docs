"""Unit tests for MarkdownParser."""

import pytest

from speckit_docs.models import Section
from speckit_docs.parsers.markdown_parser import MarkdownParser


class TestMarkdownParserBasics:
    """Basic tests for MarkdownParser initialization and simple parsing."""

    def test_parser_initialization(self):
        """Test that MarkdownParser can be initialized."""
        parser = MarkdownParser()
        assert parser is not None

    def test_parser_with_myst_disabled(self):
        """Test that MarkdownParser can be initialized with MyST disabled."""
        parser = MarkdownParser(enable_myst=False)
        assert parser.enable_myst is False

    def test_parser_with_myst_enabled(self):
        """Test that MarkdownParser defaults to MyST enabled."""
        parser = MarkdownParser(enable_myst=True)
        assert parser.enable_myst is True


class TestMarkdownParserSimpleParsing:
    """Tests for parsing simple Markdown content."""

    def test_parse_simple_markdown(self):
        """Test parsing a simple Markdown document."""
        parser = MarkdownParser()
        content = "# Title\n\nParagraph\n\n## Subtitle\n\nMore text"
        sections = parser.parse(content)

        assert len(sections) == 1
        assert sections[0].title == "Title"
        assert sections[0].level == 1
        assert len(sections[0].subsections) == 1

    def test_parse_single_heading(self):
        """Test parsing a document with a single heading."""
        parser = MarkdownParser()
        content = "# Main Title\n\nSome content here."
        sections = parser.parse(content)

        assert len(sections) == 1
        assert sections[0].title == "Main Title"
        assert sections[0].level == 1
        assert "Some content here" in sections[0].content

    def test_parse_multiple_top_level_sections(self):
        """Test parsing multiple top-level sections."""
        parser = MarkdownParser()
        content = """# Section 1

Content 1

# Section 2

Content 2"""
        sections = parser.parse(content)

        assert len(sections) == 2
        assert sections[0].title == "Section 1"
        assert sections[1].title == "Section 2"


class TestMarkdownParserHeadingExtraction:
    """Tests for extracting headings from Markdown."""

    def test_extract_headings(self):
        """Test extracting headings from Markdown."""
        parser = MarkdownParser()
        content = "# H1\n## H2\n### H3"
        headings = parser.extract_headings(content)

        assert len(headings) == 3
        assert headings[0]["level"] == 1
        assert headings[0]["text"] == "H1"
        assert headings[1]["level"] == 2
        assert headings[1]["text"] == "H2"
        assert headings[2]["level"] == 3
        assert headings[2]["text"] == "H3"

    def test_extract_headings_all_levels(self):
        """Test extracting all heading levels (1-6)."""
        parser = MarkdownParser()
        content = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6"
        headings = parser.extract_headings(content)

        assert len(headings) == 6
        for i, heading in enumerate(headings):
            assert heading["level"] == i + 1


class TestMarkdownParserNestedSections:
    """Tests for parsing nested sections."""

    def test_parse_nested_sections(self):
        """Test parsing nested sections (hierarchical structure)."""
        parser = MarkdownParser()
        content = """# Main

Main content

## Subsection 1

Sub content 1

## Subsection 2

Sub content 2"""
        sections = parser.parse(content)

        assert len(sections) == 1
        main_section = sections[0]
        assert main_section.title == "Main"
        assert len(main_section.subsections) == 2
        assert main_section.subsections[0].title == "Subsection 1"
        assert main_section.subsections[1].title == "Subsection 2"

    def test_parse_deeply_nested_sections(self):
        """Test parsing deeply nested sections (3 levels)."""
        parser = MarkdownParser()
        content = """# Level 1

L1 content

## Level 2

L2 content

### Level 3

L3 content"""
        sections = parser.parse(content)

        assert len(sections) == 1
        l1 = sections[0]
        assert l1.title == "Level 1"
        assert len(l1.subsections) == 1

        l2 = l1.subsections[0]
        assert l2.title == "Level 2"
        assert len(l2.subsections) == 1

        l3 = l2.subsections[0]
        assert l3.title == "Level 3"
        assert "L3 content" in l3.content


class TestMarkdownParserEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = MarkdownParser()
        sections = parser.parse("")

        assert sections == []

    def test_parse_content_without_headings(self):
        """Test parsing content without any headings."""
        parser = MarkdownParser()
        content = "Just some text\n\nWith paragraphs"
        sections = parser.parse(content)

        assert sections == []

    def test_parse_heading_without_content(self):
        """Test parsing a heading without following content."""
        parser = MarkdownParser()
        content = "# Empty Section"
        sections = parser.parse(content)

        assert len(sections) == 1
        assert sections[0].title == "Empty Section"
        assert sections[0].content == ""


class TestMarkdownParserLineNumbers:
    """Tests for correct line number tracking."""

    def test_line_numbers_single_section(self):
        """Test that line numbers are correctly tracked for a single section."""
        parser = MarkdownParser()
        content = """# Title
Line 2
Line 3
Line 4"""
        sections = parser.parse(content)

        assert sections[0].line_start == 1
        # Line end will depend on implementation

    def test_line_numbers_multiple_sections(self):
        """Test line numbers for multiple sections."""
        parser = MarkdownParser()
        content = """# Section 1
Content line 2
Content line 3

# Section 2
Content line 6"""
        sections = parser.parse(content)

        assert sections[0].line_start == 1
        assert sections[1].line_start == 5


class TestMarkdownParserComplexDocument:
    """Tests for parsing complex real-world documents."""

    def test_parse_spec_kit_like_document(self):
        """Test parsing a document similar to spec-kit spec.md."""
        parser = MarkdownParser()
        content = """# Feature: User Authentication

## Overview

This feature implements user authentication.

## Requirements

### FR-001: Login Form

Users must be able to log in.

### FR-002: Password Reset

Users can reset their password.

## Technical Details

Implementation notes here."""
        sections = parser.parse(content)

        assert len(sections) == 1
        main = sections[0]
        assert main.title == "Feature: User Authentication"
        assert len(main.subsections) == 3  # Overview, Requirements, Technical Details

        requirements = main.subsections[1]
        assert requirements.title == "Requirements"
        assert len(requirements.subsections) == 2  # FR-001, FR-002
