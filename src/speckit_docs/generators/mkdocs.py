"""MkDocs documentation generator."""

import subprocess
import time
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..models import Feature
from ..utils.validation import BuildError, DocumentationProjectError
from .base import BaseGenerator, BuildResult, GeneratorConfig, ValidationResult


class MkDocsGenerator(BaseGenerator):
    """MkDocs documentation generator."""

    def __init__(self, config: GeneratorConfig, project_root: Path | None = None):
        """Initialize MkDocs generator."""
        # Note: BaseGenerator now expects docs_dir, but we maintain compatibility
        # by computing it from project_root
        computed_project_root = project_root or Path.cwd()
        docs_dir = computed_project_root / "docs"
        super().__init__(docs_dir)

        self.config = config
        self.project_root = computed_project_root

        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates" / "mkdocs"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Set default theme for MkDocs
        if self.config.theme == "alabaster":  # Sphinx default
            self.config.theme = "material"  # MkDocs default

    def generate_config(self, **kwargs: Any) -> None:
        """Generate MkDocs mkdocs.yml (T018 stub)."""
        # TODO: T018 will implement this
        pass

    def generate_index(self) -> None:
        """Generate index.md (T018 stub)."""
        # TODO: T018 will implement this
        pass

    def create_directory_structure(self) -> None:
        """Create MkDocs directory structure (T018 stub)."""
        # TODO: T018 will implement this
        pass

    def init_project(self, structure_type: str = "FLAT") -> None:
        """
        Initialize MkDocs documentation project.

        Args:
            structure_type: "FLAT" or "COMPREHENSIVE"
        """
        # Create docs directory
        self._create_docs_directory()
        self._create_subdirectories(structure_type)

        # Render mkdocs.yml template
        try:
            template = self.jinja_env.get_template("mkdocs.yml.j2")
            config_content = template.render(
                project_name=self.config.project_name,
                author=self.config.author,
                description=self.config.description or "A spec-kit project",
                language=self.config.language,
                theme=self.config.theme,
                features=[],  # Will be populated by update_docs
                structure_type=structure_type,
            )

            # MkDocs config goes in project root (standard convention)
            config_path = self.project_root / "mkdocs.yml"
            config_path.write_text(config_content)

        except TemplateNotFound:
            raise DocumentationProjectError(
                "MkDocsテンプレートファイル (mkdocs.yml.j2) が見つかりません。",
                "パッケージのインストールを確認してください。",
            )

        # Render index.md template
        try:
            template = self.jinja_env.get_template("index.md.j2")
            index_content = template.render(
                project_name=self.config.project_name,
                description=self.config.description or "A spec-kit project",
                features=[],  # Will be populated by update_docs
                structure_type=structure_type,
            )

            index_path = self.docs_dir / "index.md"
            index_path.write_text(index_content)

        except TemplateNotFound:
            raise DocumentationProjectError(
                "MkDocsテンプレートファイル (index.md.j2) が見つかりません。",
                "パッケージのインストールを確認してください。",
            )

        # Create .gitignore
        gitignore_content = """# MkDocs build outputs
site/

# OS files
.DS_Store
Thumbs.db
"""
        gitignore_path = self.docs_dir / ".gitignore"
        gitignore_path.write_text(gitignore_content)

    def update_docs(self, features: list[Feature], incremental: bool = True) -> None:
        """
        Update documentation from features.

        Args:
            features: List of features to generate docs for
            incremental: If True, only update changed features (not used in init)
        """
        from ..parsers.document import Document
        from ..parsers.markdown_parser import MarkdownParser

        # Determine structure type
        structure_type = self.determine_structure_type()

        # Create features directory if needed
        features_dir = self.docs_dir / "features"
        features_dir.mkdir(exist_ok=True)

        # Initialize parser
        parser = MarkdownParser(enable_myst=True)

        # Process each feature
        processed_features = []
        for feature in features:
            if feature.spec_file is None or not feature.spec_file.exists():
                # Skip features without spec files
                continue

            try:
                # Parse spec.md into Document
                doc = Document.parse(feature.spec_file, parser)

                # Get output path based on structure type
                output_path = self.get_feature_doc_path(feature, structure_type)

                # Convert to MkDocs Markdown
                content = doc.to_mkdocs_md()

                # Write to output file
                output_path.write_text(content, encoding="utf-8")

                processed_features.append({
                    "id": feature.id,
                    "name": feature.name,
                    "title": doc.title,
                    "file": str(output_path.relative_to(self.docs_dir)),
                })

            except Exception as e:
                # Log error but continue processing other features
                import traceback
                print(f"⚠️  警告: {feature.name} の処理中にエラーが発生しました: {e}")
                traceback.print_exc()

        # Update index.md and mkdocs.yml with features list
        self._update_index(processed_features, structure_type)
        self._update_mkdocs_yml(processed_features, structure_type)

    def _update_index(self, features: list[dict[str, Any]], structure_type: str) -> None:
        """
        Update index.md with features list.

        Args:
            features: List of processed feature info dicts
            structure_type: "FLAT" or "COMPREHENSIVE"
        """
        try:
            template = self.jinja_env.get_template("index.md.j2")
            index_content = template.render(
                project_name=self.config.project_name,
                description=self.config.description or "A spec-kit project",
                features=features,
                structure_type=structure_type,
            )

            index_path = self.docs_dir / "index.md"
            index_path.write_text(index_content)

        except TemplateNotFound:
            # Fallback: manually update index.md
            index_path = self.docs_dir / "index.md"
            if not index_path.exists():
                return

            # Read existing content
            content = index_path.read_text()

            # Build features list
            features_section = "\n## 機能一覧\n\n"
            for feature in features:
                features_section += f"- [{feature['title']}]({feature['file']})\n"

            # Append or replace features section
            if "## 機能一覧" in content:
                # Replace existing section
                import re
                content = re.sub(
                    r"## 機能一覧.*?(?=\n##|\Z)",
                    features_section,
                    content,
                    flags=re.DOTALL
                )
            else:
                # Append to end
                content += "\n" + features_section

            index_path.write_text(content)

    def _update_mkdocs_yml(self, features: list[dict[str, Any]], structure_type: str) -> None:
        """
        Update mkdocs.yml navigation with features list.

        Args:
            features: List of processed feature info dicts
            structure_type: "FLAT" or "COMPREHENSIVE"
        """
        try:
            template = self.jinja_env.get_template("mkdocs.yml.j2")
            config_content = template.render(
                project_name=self.config.project_name,
                author=self.config.author,
                description=self.config.description or "A spec-kit project",
                language=self.config.language,
                theme=self.config.theme,
                features=features,
                structure_type=structure_type,
            )

            config_path = self.project_root / "mkdocs.yml"  # MkDocs config is in project root
            config_path.write_text(config_content)

        except TemplateNotFound:
            # Skip if template not available
            pass

    def build_docs(self) -> BuildResult:
        """
        Build HTML documentation using MkDocs.

        Returns:
            BuildResult with build status
        """
        start_time = time.time()

        try:
            # Run mkdocs build
            result = subprocess.run(
                ["mkdocs", "build"],
                cwd=str(self.docs_dir),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            build_time = time.time() - start_time
            output_dir = self.docs_dir / "site"

            # Parse output for warnings and errors
            warnings = []
            errors = []

            for line in result.stdout.split("\n") + result.stderr.split("\n"):
                if "WARNING" in line or "warning:" in line.lower():
                    warnings.append(line.strip())
                if "ERROR" in line or "error:" in line.lower():
                    errors.append(line.strip())

            # Count generated files
            file_count = len(list(output_dir.rglob("*.html"))) if output_dir.exists() else 0

            success = result.returncode == 0 and not errors

            return BuildResult(
                success=success,
                output_dir=output_dir,
                warnings=warnings,
                errors=errors,
                build_time=build_time,
                file_count=file_count,
            )

        except subprocess.TimeoutExpired:
            raise BuildError(
                "MkDocsビルドがタイムアウトしました（5分以上）。",
                "プロジェクトサイズを確認するか、--no-buildフラグを使用してください。",
            )
        except FileNotFoundError:
            raise BuildError(
                "mkdocsコマンドが見つかりません。",
                "'uv pip install mkdocs' を実行してMkDocsをインストールしてください。",
            )
        except Exception as e:
            raise BuildError(f"ビルド中にエラーが発生しました: {str(e)}", "ビルドログを確認してください。")

    def validate_project(self) -> ValidationResult:
        """
        Validate MkDocs project structure.

        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        checked_items = []

        # Check mkdocs.yml exists
        mkdocs_yml = self.docs_dir / "mkdocs.yml"
        if not mkdocs_yml.exists():
            errors.append("mkdocs.yml が見つかりません")
        else:
            checked_items.append("mkdocs.yml exists")

            # Check mkdocs.yml contains required fields
            content = mkdocs_yml.read_text()
            if "site_name:" not in content:
                errors.append("mkdocs.yml に site_name が設定されていません")
            else:
                checked_items.append("site_name configured")

            if "theme:" not in content:
                warnings.append("mkdocs.yml に theme が設定されていません")
            else:
                checked_items.append("theme configured")

        # Check index.md exists
        index_md = self.docs_dir / "index.md"
        if not index_md.exists():
            errors.append("index.md が見つかりません")
        else:
            checked_items.append("index.md exists")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid, errors=errors, warnings=warnings, checked_items=checked_items
        )
