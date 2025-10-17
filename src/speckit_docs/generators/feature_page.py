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
        transformed_content_map: dict[str, dict[str, str]],
    ) -> list[Path]:
        """
        Generate feature pages for all features.

        Args:
            features: List of Feature objects to generate pages for
            transformed_content_map: Required mapping of feature directory names to LLM-transformed content
                Format: {"001-user-auth": {"spec_content": "..."}}
                (FR-038e, FR-038f: LLM transformation is always executed)

        Raises:
            SpecKitDocsError: If transformed_content_map is None or missing required feature keys

        Returns:
            List of generated page file paths

        FR-013: FLAT structure - pages in docs/ root
        FR-014: COMPREHENSIVE structure - pages in docs/features/
        FR-038f: LLM-transformed content integration
        """
        generated_pages: list[Path] = []

        for feature in features:
            # FR-038e: transformed_content_map is always provided (required parameter)
            # FR-038b: No fallback - raise error if content missing
            feature_key = f"{feature.id}-{feature.name}"

            if feature_key not in transformed_content_map:
                from ..exceptions import SpecKitDocsError
                raise SpecKitDocsError(
                    f"機能 '{feature_key}' のLLM変換済みコンテンツが見つかりません。",
                    "コマンドテンプレート /speckit.doc-update の Step 1（LLM変換実行）を確認してください。"
                )

            transformed = transformed_content_map[feature_key]

            if not transformed.get("spec_content"):
                from ..exceptions import SpecKitDocsError
                raise SpecKitDocsError(
                    f"機能 '{feature_key}' のspec_contentが空です。",
                    "LLM変換処理を確認してください。"
                )

            # Use LLM-transformed content only (FR-038, FR-038b)
            spec_doc = Document(
                file_path=feature.spec_file,
                type=DocumentType.SPEC,
                content=transformed["spec_content"],
                sections=self.markdown_parser.parse(transformed["spec_content"]),
            )

            # Session 2025-10-17: plan.md and tasks.md are excluded from end-user documentation
            # FR-016 (deleted), FR-017 (deleted): Developer-facing information is available
            # via links in the Feature Files section
            plan_doc = None
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
