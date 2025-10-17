"""
DocumentGenerator - Generate feature documentation pages.

FR-012: Feature page generation
FR-015: Spec content extraction (LLM-transformed)
Session 2025-10-17: plan.md and tasks.md excluded from end-user documentation
FR-018: Missing file notes (spec.md only)
"""

from jinja2 import Environment, PackageLoader

from ..models import Document, Feature


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
        plan_doc: Document | None = None,
        tasks_doc: Document | None = None,
    ) -> str:
        """
        Generate a feature documentation page from spec document.

        Args:
            feature: Feature object containing metadata
            spec_doc: Specification document (required, LLM-transformed)
            plan_doc: Deprecated parameter (Session 2025-10-17, always None)
            tasks_doc: Deprecated parameter (Session 2025-10-17, always None)

        Returns:
            Generated Markdown content for the feature page

        FR-012: Generate comprehensive feature page
        FR-015: Extract all sections from spec.md (LLM-transformed)
        Session 2025-10-17: plan.md and tasks.md excluded from end-user documentation
        FR-018: Show notes for missing spec.md
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
