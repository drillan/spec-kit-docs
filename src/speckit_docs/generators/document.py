"""
DocumentGenerator - Generate feature documentation pages.

FR-012: Feature page generation
FR-015: Spec content extraction
FR-016: Plan architecture sections
FR-017: Tasks summary
FR-018: Missing file notes
"""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader

from ..models import Document, DocumentType, Feature


class DocumentGenerator:
    """Generate feature documentation pages from spec-kit documents."""

    def __init__(self) -> None:
        """Initialize DocumentGenerator with Jinja2 environment."""
        self.env = Environment(
            loader=PackageLoader("speckit_docs", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_feature_page(
        self,
        feature: Feature,
        spec_doc: Document,
        plan_doc: Optional[Document] = None,
        tasks_doc: Optional[Document] = None,
    ) -> str:
        """
        Generate a feature documentation page from spec, plan, and tasks documents.

        Args:
            feature: Feature object containing metadata
            spec_doc: Specification document (required)
            plan_doc: Plan document (optional, FR-016)
            tasks_doc: Tasks document (optional, FR-017)

        Returns:
            Generated Markdown content for the feature page

        FR-012: Generate comprehensive feature page
        FR-015: Extract all sections from spec.md
        FR-016: Include architecture from plan.md if available
        FR-017: Include task summary from tasks.md if available
        FR-018: Show notes for missing files
        """
        template = self.env.get_template("feature-page.md.jinja2")

        content = template.render(
            feature=feature,
            spec_content=spec_doc.content,
            plan_content=plan_doc.content if plan_doc else None,
            tasks_content=tasks_doc.content if tasks_doc else None,
            missing_plan=plan_doc is None,
            missing_tasks=tasks_doc is None,
        )

        return content
