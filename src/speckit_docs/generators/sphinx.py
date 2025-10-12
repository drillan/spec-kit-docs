"""Sphinx documentation generator."""

import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..parsers.document_structure import DocumentStructure, StructureType
from ..parsers.feature_scanner import Feature
from ..utils.validation import BuildError, DocumentationProjectError
from .base import BaseGenerator, BuildResult, GeneratorConfig, ValidationResult


class SphinxGenerator(BaseGenerator):
    """Sphinx + myst-parser documentation generator."""

    def __init__(self, config: GeneratorConfig, project_root: Path = None):
        """Initialize Sphinx generator."""
        super().__init__(config, project_root)

        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates" / "sphinx"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def init_project(self, structure_type: str = "FLAT") -> None:
        """
        Initialize Sphinx documentation project.

        Args:
            structure_type: "FLAT" or "COMPREHENSIVE"
        """
        # Create docs directory
        self._create_docs_directory()
        self._create_subdirectories(structure_type)

        # Render conf.py template
        try:
            template = self.jinja_env.get_template("conf.py.j2")
            conf_content = template.render(
                project_name=self.config.project_name,
                author=self.config.author,
                version=self.config.version,
                year=datetime.now().year,
                language=self.config.language,
                theme=self.config.theme,
            )

            conf_path = self.docs_dir / "conf.py"
            conf_path.write_text(conf_content)

        except TemplateNotFound:
            raise DocumentationProjectError(
                "Sphinxテンプレートファイル (conf.py.j2) が見つかりません。",
                "パッケージのインストールを確認してください。",
            )

        # Render index.md template
        try:
            template = self.jinja_env.get_template("index.md.j2")
            index_content = template.render(
                project_name=self.config.project_name,
                description=self.config.description or "このプロジェクトは、spec-kitを使用して開発されています。",
                features=[],  # Will be populated by update_docs
                structure_type=structure_type,
            )

            index_path = self.docs_dir / "index.md"
            index_path.write_text(index_content)

        except TemplateNotFound:
            raise DocumentationProjectError(
                "Sphinxテンプレートファイル (index.md.j2) が見つかりません。",
                "パッケージのインストールを確認してください。",
            )

        # Render Makefile
        try:
            template = self.jinja_env.get_template("Makefile.j2")
            makefile_content = template.render()

            makefile_path = self.docs_dir / "Makefile"
            makefile_path.write_text(makefile_content)

        except TemplateNotFound:
            raise DocumentationProjectError(
                "Sphinxテンプレートファイル (Makefile.j2) が見つかりません。",
                "パッケージのインストールを確認してください。",
            )

        # Render make.bat
        try:
            template = self.jinja_env.get_template("make.bat.j2")
            bat_content = template.render()

            bat_path = self.docs_dir / "make.bat"
            bat_path.write_text(bat_content)

        except TemplateNotFound:
            raise DocumentationProjectError(
                "Sphinxテンプレートファイル (make.bat.j2) が見つかりません。",
                "パッケージのインストールを確認してください。",
            )

        # Create .gitignore
        gitignore_content = """# Sphinx build outputs
_build/
_static/
_templates/

# OS files
.DS_Store
Thumbs.db
"""
        gitignore_path = self.docs_dir / ".gitignore"
        gitignore_path.write_text(gitignore_content)

    def update_docs(self, features: List[Feature], incremental: bool = True) -> None:
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

                # Convert to Sphinx MyST Markdown
                content = doc.to_sphinx_md()

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
                print(f"⚠️  警告: {feature.name} の処理中にエラーが発生しました: {e}")

        # Update index.md with features list
        self._update_index(processed_features, structure_type)

    def _update_index(self, features: List[dict], structure_type: str) -> None:
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
                description=self.config.description or "このプロジェクトは、spec-kitを使用して開発されています。",
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

    def build_docs(self) -> BuildResult:
        """
        Build HTML documentation using Sphinx.

        Returns:
            BuildResult with build status
        """
        start_time = time.time()

        try:
            # Run make html
            result = subprocess.run(
                ["make", "html"],
                cwd=str(self.docs_dir),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            build_time = time.time() - start_time
            output_dir = self.docs_dir / "_build" / "html"

            # Parse output for warnings and errors
            warnings = []
            errors = []

            for line in result.stdout.split("\n") + result.stderr.split("\n"):
                if "WARNING" in line or "warning:" in line:
                    warnings.append(line.strip())
                if "ERROR" in line or "error:" in line:
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
                "Sphinxビルドがタイムアウトしました（5分以上）。",
                "プロジェクトサイズを確認するか、--no-buildフラグを使用してください。",
            )
        except FileNotFoundError:
            raise BuildError(
                "makeコマンドが見つかりません。",
                "Makeがインストールされているか確認してください（Linux/macOS）。Windowsの場合はmake.batを使用してください。",
            )
        except Exception as e:
            raise BuildError(f"ビルド中にエラーが発生しました: {str(e)}", "ビルドログを確認してください。")

    def validate_project(self) -> ValidationResult:
        """
        Validate Sphinx project structure.

        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        checked_items = []

        # Check conf.py exists
        conf_py = self.docs_dir / "conf.py"
        if not conf_py.exists():
            errors.append("conf.py が見つかりません")
        else:
            checked_items.append("conf.py exists")

            # Check conf.py contains myst_parser
            content = conf_py.read_text()
            if "myst_parser" not in content:
                errors.append("conf.py に myst_parser が設定されていません")
            else:
                checked_items.append("myst_parser configured")

        # Check index.md exists
        index_md = self.docs_dir / "index.md"
        if not index_md.exists():
            errors.append("index.md が見つかりません")
        else:
            checked_items.append("index.md exists")

        # Check Makefile exists
        makefile = self.docs_dir / "Makefile"
        if not makefile.exists():
            warnings.append("Makefile が見つかりません（Linux/macOSで必要）")
        else:
            checked_items.append("Makefile exists")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid, errors=errors, warnings=warnings, checked_items=checked_items
        )
