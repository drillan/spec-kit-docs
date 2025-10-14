#!/usr/bin/env python3
"""
doc_init.py - Initialize documentation project

This script is executed by /doc-init command.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console

# Import from parent package
try:
    from speckit_docs.exceptions import SpecKitDocsError
    from speckit_docs.generators.base import BaseGenerator, GeneratorConfig
    from speckit_docs.generators.mkdocs import MkDocsGenerator
    from speckit_docs.generators.sphinx import SphinxGenerator
    from speckit_docs.utils.feature_discovery import FeatureDiscoverer
except ImportError:
    # When running as script directly, try relative imports
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    from speckit_docs.exceptions import SpecKitDocsError
    from speckit_docs.generators.base import BaseGenerator, GeneratorConfig
    from speckit_docs.generators.mkdocs import MkDocsGenerator
    from speckit_docs.generators.sphinx import SphinxGenerator
    from speckit_docs.utils.feature_discovery import FeatureDiscoverer

app = typer.Typer()
console = Console()


@app.command()
def main(
    doc_type: str = typer.Option("sphinx", "--type", help="Documentation tool (sphinx/mkdocs)"),
    project_name: str | None = typer.Option(None, "--project-name", help="Project name"),
    author: str | None = typer.Option(None, "--author", help="Author name"),
    version: str = typer.Option("0.1.0", "--version", help="Project version"),
    language: str = typer.Option("ja", "--language", help="Documentation language"),
    force: bool = typer.Option(False, "--force", help="Force overwrite existing files"),
) -> int:
    """Initialize documentation project."""
    try:
        # FR-003b: Set default values
        if project_name is None:
            project_name = Path.cwd().name
            console.print(f"[dim]Using project name: {project_name}[/dim]")

        if author is None:
            # Try to get from git config
            try:
                author = subprocess.check_output(
                    ["git", "config", "user.name"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
                console.print(f"[dim]Using author from git: {author}[/dim]")
            except (subprocess.CalledProcessError, FileNotFoundError):
                author = "Unknown Author"
                console.print("[dim]Using default author: Unknown Author[/dim]")

        # Discover features to determine structure
        console.print("\n[bold]機能を検出中...[/bold]")
        discoverer = FeatureDiscoverer()
        features = discoverer.discover_features()
        feature_count = len(features)
        console.print(f"[green]✓[/green] {feature_count} 個の機能を検出しました")

        # FR-003d: Check if docs/ already exists
        docs_dir = Path("docs")
        if docs_dir.exists() and not force:
            console.print(
                "[red]✗[/red] docs/ ディレクトリが既に存在します。",
                style="bold",
            )
            console.print("  --force フラグを使用するか、docs/ を手動で削除してください。")
            return 1

        # Create generator config
        config = GeneratorConfig(
            tool=doc_type,
            project_name=project_name,
            author=author,
            version=version,
            language=language,
        )

        # Select and initialize generator
        console.print(f"\n[bold]{doc_type.capitalize()} プロジェクトを初期化中...[/bold]")

        generator: BaseGenerator
        if doc_type == "sphinx":
            generator = SphinxGenerator(config, Path.cwd())
        elif doc_type == "mkdocs":
            generator = MkDocsGenerator(config, Path.cwd())
        else:
            console.print(f"[red]✗[/red] 不明なドキュメントツール: {doc_type}")
            console.print("  サポートされているツール: sphinx, mkdocs")
            return 1

        # Determine structure based on feature count
        structure_type = generator.determine_structure(feature_count)
        generator.structure_type = structure_type

        structure_name = "FLAT" if structure_type.value == "FLAT" else "COMPREHENSIVE"
        console.print(f"[dim]構造タイプ: {structure_name} ({feature_count} features)[/dim]")

        # Create directory structure
        generator.create_directory_structure()

        # Generate config files
        generator.generate_config(
            project_name=project_name,
            author=author,
            version=version,
            language=language,
            year=datetime.now().year,
        )

        # Generate index
        generator.generate_index()

        # Success message
        console.print(
            "\n[bold green]✓ ドキュメントプロジェクトの初期化が完了しました！[/bold green]"
        )
        console.print("\n[bold]次のステップ:[/bold]")
        if doc_type == "sphinx":
            console.print("  1. cd docs/")
            console.print("  2. make html")
            console.print("  3. ブラウザで _build/html/index.html を開く")
        else:  # mkdocs
            console.print("  1. mkdocs serve")
            console.print("  2. ブラウザで http://127.0.0.1:8000 を開く")

        return 0

    except SpecKitDocsError as e:
        console.print(f"[red]✗[/red] {e.message}", style="bold")
        console.print(f"  💡 {e.suggestion}")
        return 1
    except Exception as e:
        console.print(f"[red]✗[/red] 予期しないエラーが発生しました: {e}", style="bold")
        return 1


if __name__ == "__main__":
    sys.exit(app())
