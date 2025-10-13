"""
NavigationUpdater - Update documentation navigation.

FR-013: Sphinx toctree update
FR-014: MkDocs nav update
"""

import re
from pathlib import Path

import yaml

from ..models import GeneratorTool


class NavigationUpdater:
    """Update navigation for Sphinx toctree or MkDocs nav."""

    def __init__(self, docs_dir: Path, tool: GeneratorTool) -> None:
        """
        Initialize NavigationUpdater.

        Args:
            docs_dir: Documentation directory path
            tool: SPHINX or MKDOCS
        """
        self.docs_dir = docs_dir
        self.tool = tool

    def update_navigation(self, feature_pages: list[Path]) -> None:
        """
        Update navigation (Sphinx toctree or MkDocs nav).

        Args:
            feature_pages: List of generated feature page paths

        FR-013: Update Sphinx toctree in index.md
        FR-014: Update MkDocs nav in mkdocs.yml
        """
        if self.tool == GeneratorTool.SPHINX:
            self._update_sphinx_toctree(feature_pages)
        elif self.tool == GeneratorTool.MKDOCS:
            self._update_mkdocs_nav(feature_pages)

    def _update_sphinx_toctree(self, feature_pages: list[Path]) -> None:
        """
        Update Sphinx index.md with toctree directive.

        Args:
            feature_pages: List of feature page paths

        FR-013: Generate MyST toctree directive
        """
        index_path = self.docs_dir / "index.md"

        if not index_path.exists():
            # Create minimal index if it doesn't exist
            index_path.write_text("# Documentation\n\n")

        index_content = index_path.read_text()

        # Build toctree block
        toctree_lines = [
            "```{toctree}",
            ":maxdepth: 2",
            ":caption: Features",
            "",
        ]

        for page in sorted(feature_pages):
            # Get relative path from docs_dir and remove .md extension
            relative_path = page.relative_to(self.docs_dir).with_suffix("")
            toctree_lines.append(str(relative_path))

        toctree_lines.append("```")
        toctree_block = "\n".join(toctree_lines)

        # Replace existing toctree or append new one
        toctree_marker_start = "<!-- FEATURES_TOCTREE_START -->"
        toctree_marker_end = "<!-- FEATURES_TOCTREE_END -->"

        if toctree_marker_start in index_content:
            # Replace existing toctree between markers
            pattern = (
                rf"{re.escape(toctree_marker_start)}.*?{re.escape(toctree_marker_end)}"
            )
            replacement = f"{toctree_marker_start}\n{toctree_block}\n{toctree_marker_end}"
            updated_content = re.sub(
                pattern, replacement, index_content, flags=re.DOTALL
            )
        else:
            # Append new toctree with markers
            updated_content = (
                f"{index_content}\n\n"
                f"{toctree_marker_start}\n"
                f"{toctree_block}\n"
                f"{toctree_marker_end}\n"
            )

        index_path.write_text(updated_content)

    def _update_mkdocs_nav(self, feature_pages: list[Path]) -> None:
        """
        Update MkDocs mkdocs.yml nav section.

        Args:
            feature_pages: List of feature page paths

        FR-014: Update mkdocs.yml nav with feature pages
        """
        mkdocs_yml = self.docs_dir.parent / "mkdocs.yml"

        if not mkdocs_yml.exists():
            raise FileNotFoundError(f"mkdocs.yml not found at {mkdocs_yml}")

        # Load existing config
        with open(mkdocs_yml) as f:
            config = yaml.safe_load(f)

        if config is None:
            config = {}

        # Ensure nav exists
        if "nav" not in config:
            config["nav"] = []

        # Build feature nav items
        feature_nav_items = []
        for page in sorted(feature_pages):
            # Get relative path from docs_dir
            relative_path = page.relative_to(self.docs_dir)

            # Create friendly title from filename
            title = page.stem.replace("-", " ").title()

            feature_nav_items.append({title: str(relative_path)})

        # Find and replace Features section, or append it
        features_section_found = False
        for i, item in enumerate(config["nav"]):
            if isinstance(item, dict) and "Features" in item:
                # Replace existing Features section
                config["nav"][i] = {"Features": feature_nav_items}
                features_section_found = True
                break

        if not features_section_found:
            # Append new Features section
            config["nav"].append({"Features": feature_nav_items})

        # Write updated config
        with open(mkdocs_yml, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
