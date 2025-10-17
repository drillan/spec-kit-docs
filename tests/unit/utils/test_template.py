"""Unit tests for template utilities (T082 - Coverage improvement)."""

from pathlib import Path

import pytest
from jinja2 import Template

from speckit_docs.utils.template import (
    load_and_render_template,
    load_template,
    render_template,
)


class TestLoadTemplate:
    """Tests for load_template function."""

    def test_load_template_success(self, tmp_path: Path):
        """Test loading a valid template."""
        # Given: Template directory with a template file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "test.md.jinja2"
        template_file.write_text("# {{ title }}\n\n{{ content }}")

        # When: Load the template
        template = load_template(template_dir, "test.md.jinja2")

        # Then: Should return a Template instance
        assert isinstance(template, Template)

    def test_load_template_directory_not_exist(self, tmp_path: Path):
        """Test error when template directory doesn't exist."""
        # Given: Non-existent directory
        template_dir = tmp_path / "nonexistent"

        # When/Then: Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Template directory does not exist"):
            load_template(template_dir, "test.md.jinja2")

    def test_load_template_file_not_exist(self, tmp_path: Path):
        """Test error when template file doesn't exist."""
        # Given: Template directory without the template file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # When/Then: Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Template file does not exist"):
            load_template(template_dir, "nonexistent.md.jinja2")


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_render_template_simple(self, tmp_path: Path):
        """Test rendering a simple template."""
        # Given: Template with variables
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "test.md.jinja2"
        template_file.write_text("# {{ title }}\n\n{{ content }}")

        template = load_template(template_dir, "test.md.jinja2")
        context = {"title": "Test Title", "content": "Test content"}

        # When: Render the template
        result = render_template(template, context)

        # Then: Should render with variables replaced
        assert "# Test Title" in result
        assert "Test content" in result

    def test_render_template_with_loop(self, tmp_path: Path):
        """Test rendering a template with a loop."""
        # Given: Template with for loop
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "list.md.jinja2"
        template_file.write_text("{% for item in items %}\n- {{ item }}\n{% endfor %}")

        template = load_template(template_dir, "list.md.jinja2")
        context = {"items": ["Item 1", "Item 2", "Item 3"]}

        # When: Render the template
        result = render_template(template, context)

        # Then: Should render all items
        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

    def test_render_template_with_conditional(self, tmp_path: Path):
        """Test rendering a template with conditionals."""
        # Given: Template with if statement
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "conditional.md.jinja2"
        template_file.write_text(
            "{% if show_title %}# {{ title }}{% endif %}\n\n{{ content }}"
        )

        template = load_template(template_dir, "conditional.md.jinja2")

        # When: Render with show_title=True
        result_with_title = render_template(
            template, {"show_title": True, "title": "Title", "content": "Content"}
        )

        # Then: Should include title
        assert "# Title" in result_with_title

        # When: Render with show_title=False
        result_without_title = render_template(
            template, {"show_title": False, "title": "Title", "content": "Content"}
        )

        # Then: Should not include title
        assert "# Title" not in result_without_title
        assert "Content" in result_without_title

    def test_render_template_empty_context(self, tmp_path: Path):
        """Test rendering a template with empty context."""
        # Given: Template with no variables
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "static.md.jinja2"
        template_file.write_text("# Static Title\n\nStatic content")

        template = load_template(template_dir, "static.md.jinja2")

        # When: Render with empty context
        result = render_template(template, {})

        # Then: Should render static content
        assert "# Static Title" in result
        assert "Static content" in result


class TestLoadAndRenderTemplate:
    """Tests for load_and_render_template function."""

    def test_load_and_render_template_success(self, tmp_path: Path):
        """Test loading and rendering in one step."""
        # Given: Template directory with template file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "test.md.jinja2"
        template_file.write_text("# {{ title }}\n\n{{ content }}")

        context = {"title": "Test Title", "content": "Test content"}

        # When: Load and render template
        result = load_and_render_template(template_dir, "test.md.jinja2", context)

        # Then: Should return rendered content
        assert "# Test Title" in result
        assert "Test content" in result

    def test_load_and_render_template_complex(self, tmp_path: Path):
        """Test loading and rendering complex template."""
        # Given: Complex template with multiple features
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "feature.md.jinja2"
        template_content = """# {{ feature.name }}

## Overview
{{ feature.description }}

## Requirements
{% for req in feature.requirements %}
- {{ req.id }}: {{ req.text }}
{% endfor %}
"""
        template_file.write_text(template_content)

        context = {
            "feature": {
                "name": "User Authentication",
                "description": "Secure user login system",
                "requirements": [
                    {"id": "REQ-001", "text": "Users must log in with email"},
                    {"id": "REQ-002", "text": "Passwords must be hashed"},
                ],
            }
        }

        # When: Load and render template
        result = load_and_render_template(template_dir, "feature.md.jinja2", context)

        # Then: Should render all parts correctly
        assert "# User Authentication" in result
        assert "Secure user login system" in result
        assert "REQ-001" in result
        assert "REQ-002" in result

    def test_load_and_render_template_directory_not_exist(self, tmp_path: Path):
        """Test error when directory doesn't exist."""
        # Given: Non-existent directory
        template_dir = tmp_path / "nonexistent"

        # When/Then: Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Template directory does not exist"):
            load_and_render_template(template_dir, "test.md.jinja2", {})

    def test_load_and_render_template_file_not_exist(self, tmp_path: Path):
        """Test error when template file doesn't exist."""
        # Given: Template directory without file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # When/Then: Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Template file does not exist"):
            load_and_render_template(template_dir, "nonexistent.md.jinja2", {})
