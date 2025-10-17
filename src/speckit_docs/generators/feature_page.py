"""
FeaturePageGenerator - Generate documentation pages for all features.

FR-013: FLAT structure page generation
FR-014: COMPREHENSIVE structure page generation
FR-015: Spec content extraction
FR-016: Plan architecture sections
FR-017: Tasks summary
"""

from pathlib import Path

from ..models import (
    Document,
    DocumentType,
    Feature,
    GeneratorTool,
    StructureType,
)
from ..parsers.markdown_parser import MarkdownParser
from .document import DocumentGenerator


class FeaturePageGenerator:
    """Generate feature documentation pages for all features."""

    def __init__(
        self,
        docs_dir: Path,
        structure_type: StructureType,
        tool: GeneratorTool,
    ) -> None:
        """
        Initialize FeaturePageGenerator.

        Args:
            docs_dir: Documentation directory path
            structure_type: FLAT or COMPREHENSIVE structure
            tool: SPHINX or MKDOCS
        """
        self.docs_dir = docs_dir
        self.structure_type = structure_type
        self.tool = tool
        self.document_generator = DocumentGenerator()
        self.markdown_parser = MarkdownParser()

    def generate_pages(
        self,
        features: list[Feature],
        transformed_content_map: dict[str, dict[str, str]] | None = None,
    ) -> list[Path]:
        """
        Generate feature pages for all features.

        Args:
            features: List of Feature objects to generate pages for
            transformed_content_map: Optional mapping of feature directory names to transformed content
                Format: {"001-user-auth": {"spec_content": "...", "plan_content": "...", "tasks_content": "..."}}
                (T073, FR-038f)

        Returns:
            List of generated page file paths

        FR-013: FLAT structure - pages in docs/ root
        FR-014: COMPREHENSIVE structure - pages in docs/features/
        FR-038f: LLM-transformed content integration
        """
        generated_pages: list[Path] = []

        for feature in features:
            # Check if LLM-transformed content is available (T073)
            feature_key = f"{feature.id}-{feature.name}"
            transformed = transformed_content_map.get(feature_key) if transformed_content_map else None

            if transformed and transformed.get("spec_content"):
                # Use LLM-transformed content (FR-038f)
                spec_doc = Document(
                    file_path=feature.spec_file,
                    type=DocumentType.SPEC,
                    content=transformed["spec_content"],
                    sections=self.markdown_parser.parse(transformed["spec_content"]),
                )
            else:
                # Use original content (T072, FR-038g)
                spec_doc = self._parse_document(feature.spec_file, DocumentType.SPEC)

            # Parse plan.md (optional, FR-016) with LLM-transformed content if available
            if transformed and transformed.get("plan_content") and feature.plan_file:
                plan_doc = Document(
                    file_path=feature.plan_file,
                    type=DocumentType.PLAN,
                    content=transformed["plan_content"],
                    sections=self.markdown_parser.parse(transformed["plan_content"]),
                )
            elif feature.plan_file and feature.plan_file.exists():
                plan_doc = self._parse_document(feature.plan_file, DocumentType.PLAN)
            else:
                plan_doc = None

            # Parse tasks.md (optional, FR-017) with LLM-transformed content if available
            if transformed and transformed.get("tasks_content") and feature.tasks_file:
                tasks_doc = Document(
                    file_path=feature.tasks_file,
                    type=DocumentType.TASKS,
                    content=transformed["tasks_content"],
                    sections=self.markdown_parser.parse(transformed["tasks_content"]),
                )
            elif feature.tasks_file and feature.tasks_file.exists():
                tasks_doc = self._parse_document(feature.tasks_file, DocumentType.TASKS)
            else:
                tasks_doc = None

            # Generate page content
            page_content = self.document_generator.generate_feature_page(
                feature, spec_doc, plan_doc, tasks_doc
            )

            # Determine filename (descriptive name without ID prefix, FR-013, FR-014)
            page_filename = f"{feature.name}.md"

            # Determine location based on structure type
            if self.structure_type == StructureType.FLAT:
                # FR-013: FLAT structure - place in docs/ root
                page_path = self.docs_dir / page_filename
            else:
                # FR-014: COMPREHENSIVE structure - place in docs/features/
                page_path = self.docs_dir / "features" / page_filename

            # Create parent directory if needed
            page_path.parent.mkdir(parents=True, exist_ok=True)

            # Write page to file
            page_path.write_text(page_content)

            generated_pages.append(page_path)

        return generated_pages

    def _parse_document(self, file_path: Path, doc_type: DocumentType) -> Document:
        """
        Parse a markdown document file.

        Args:
            file_path: Path to the markdown file
            doc_type: Type of document (SPEC, PLAN, or TASKS)

        Returns:
            Document object with parsed content and sections
        """
        content = file_path.read_text()
        sections = self.markdown_parser.parse(content)

        return Document(
            file_path=file_path,
            type=doc_type,
            content=content,
            sections=sections,
        )
