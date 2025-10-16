"""Jinja2 template loading and rendering utilities."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template


def load_template(template_dir: Path, template_name: str) -> Template:
    """Load a Jinja2 template from the specified directory.

    Args:
        template_dir: Directory containing templates
        template_name: Name of the template file

    Returns:
        Loaded Jinja2 template

    Raises:
        FileNotFoundError: If template directory or file does not exist
    """
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template directory does not exist: {template_dir}")

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,  # Markdown templates don't need HTML escaping
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template_path = template_dir / template_name
    if not template_path.is_file():
        raise FileNotFoundError(f"Template file does not exist: {template_path}")

    return env.get_template(template_name)


def render_template(template: Template, context: dict[str, Any]) -> str:
    """Render a Jinja2 template with the given context.

    Args:
        template: Jinja2 template to render
        context: Template context variables

    Returns:
        Rendered template string
    """
    return template.render(context)


def load_and_render_template(
    template_dir: Path, template_name: str, context: dict[str, Any]
) -> str:
    """Load and render a Jinja2 template in one step.

    Args:
        template_dir: Directory containing templates
        template_name: Name of the template file
        context: Template context variables

    Returns:
        Rendered template string

    Raises:
        FileNotFoundError: If template directory or file does not exist
    """
    template = load_template(template_dir, template_name)
    return render_template(template, context)
