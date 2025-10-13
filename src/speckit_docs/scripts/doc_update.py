#!/usr/bin/env python3
"""
doc_update.py - Update documentation from specifications

This script is executed by /doc-update command.

FR-010: Documentation project validation
FR-011: Feature discovery
FR-012: Feature page generation
FR-013: FLAT structure navigation update
FR-014: COMPREHENSIVE structure navigation update
FR-019: Incremental update
FR-020: Update summary display
"""

import sys
from pathlib import Path

import typer
from rich.console import Console

# Import from parent package
try:
    from speckit_docs.exceptions import SpecKitDocsError
    from speckit_docs.generators.feature_page import FeaturePageGenerator
    from speckit_docs.generators.navigation import NavigationUpdater
    from speckit_docs.models import GeneratorTool, StructureType
    from speckit_docs.utils.feature_discovery import FeatureDiscoverer
    from speckit_docs.utils.git import ChangeDetector
except ImportError:
    # When running as script directly, try relative imports
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    from speckit_docs.exceptions import SpecKitDocsError
    from speckit_docs.generators.feature_page import FeaturePageGenerator
    from speckit_docs.generators.navigation import NavigationUpdater
    from speckit_docs.models import GeneratorTool, StructureType
    from speckit_docs.utils.feature_discovery import FeatureDiscoverer
    from speckit_docs.utils.git import ChangeDetector

app = typer.Typer()
console = Console()


@app.command()
def main(
    incremental: bool = typer.Option(
        True, "--incremental/--full", help="Incremental or full update"
    ),
) -> int:
    """Update documentation from spec-kit specifications."""
    try:
        # FR-010: Validate documentation project exists
        docs_dir = Path("docs")
        if not docs_dir.exists():
            console.print(
                "[red]✗[/red] ドキュメントプロジェクトが見つかりません。",
                style="bold",
            )
            console.print("  最初に /doc-init を実行してください。")
            return 1

        # Detect documentation tool (Sphinx or MkDocs)
        tool = _detect_tool(docs_dir)
        console.print(f"[dim]ドキュメントツール: {tool.value}[/dim]")

        # Detect structure type (FLAT or COMPREHENSIVE)
        structure_type = _detect_structure(docs_dir)
        console.print(f"[dim]構造タイプ: {structure_type.value}[/dim]")

        # FR-011: Discover features from specs/ directory
        console.print("\n[bold]機能を検出中...[/bold]")
        discoverer = FeatureDiscoverer()

        if incremental:
            # FR-019: Incremental update using Git diff
            try:
                change_detector = ChangeDetector()
                changed_features = change_detector.get_changed_features()

                if changed_features:
                    features = changed_features
                    console.print(
                        f"[green]✓[/green] {len(features)} 個の変更された機能を検出しました（インクリメンタル更新）"
                    )
                else:
                    console.print("[green]✓[/green] 変更が検出されませんでした。更新をスキップします。")
                    return 0
            except Exception:
                # If Git detection fails (no repo, no commits, etc.), fall back to full update
                console.print(
                    "[yellow]Note:[/yellow] Git履歴が見つかりません。フル更新にフォールバックします。"
                )
                features = discoverer.discover_features()
        else:
            # Full update
            features = discoverer.discover_features()
            console.print(
                f"[green]✓[/green] {len(features)} 個の機能を検出しました（フル更新）"
            )

        if not features:
            console.print(
                "[red]✗[/red] specs/ ディレクトリに機能が見つかりません。",
                style="bold",
            )
            console.print("  /speckit.specify を実行して機能仕様を作成してください。")
            return 1

        # FR-012, FR-013, FR-014: Generate feature pages
        console.print("\n[bold]ドキュメントページを生成中...[/bold]")
        page_generator = FeaturePageGenerator(docs_dir, structure_type, tool)
        feature_pages = page_generator.generate_pages(features)

        console.print(f"[green]✓[/green] {len(feature_pages)} ページを生成しました")

        # FR-013, FR-014: Update navigation
        console.print("\n[bold]ナビゲーションを更新中...[/bold]")
        nav_updater = NavigationUpdater(docs_dir, tool)
        nav_updater.update_navigation(feature_pages)

        console.print("[green]✓[/green] ナビゲーションを更新しました")

        # FR-020: Display update summary
        console.print("\n[bold green]✓ ドキュメント更新が完了しました！[/bold green]")
        console.print(f"\n[bold]サマリー:[/bold]")
        console.print(f"  • 更新された機能: {len(features)}")
        console.print(f"  • 生成されたページ: {len(feature_pages)}")

        return 0

    except SpecKitDocsError as e:
        console.print(f"[red]✗[/red] {e.message}", style="bold")
        console.print(f"  💡 {e.suggestion}")
        return 1
    except Exception as e:
        console.print(
            f"[red]✗[/red] 予期しないエラーが発生しました: {e}", style="bold"
        )
        return 1


def _detect_tool(docs_dir: Path) -> GeneratorTool:
    """
    Detect which documentation tool is being used.

    Args:
        docs_dir: Documentation directory path

    Returns:
        GeneratorTool.SPHINX or GeneratorTool.MKDOCS

    Raises:
        SpecKitDocsError: If tool cannot be detected
    """
    if (docs_dir / "conf.py").exists():
        return GeneratorTool.SPHINX
    elif (docs_dir.parent / "mkdocs.yml").exists():
        return GeneratorTool.MKDOCS
    else:
        raise SpecKitDocsError(
            "ドキュメントツールを検出できません。",
            "conf.py または mkdocs.yml が見つかりません。/doc-init を実行してください。",
        )


def _detect_structure(docs_dir: Path) -> StructureType:
    """
    Detect which structure type is being used.

    Args:
        docs_dir: Documentation directory path

    Returns:
        StructureType.FLAT or StructureType.COMPREHENSIVE
    """
    # COMPREHENSIVE structure has features/ subdirectory
    if (docs_dir / "features").exists():
        return StructureType.COMPREHENSIVE
    else:
        return StructureType.FLAT


if __name__ == "__main__":
    sys.exit(app())
