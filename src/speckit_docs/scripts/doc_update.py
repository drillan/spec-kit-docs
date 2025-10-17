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
FR-038f: LLM-transformed content integration (T071-T074)
FR-038g: Skip LLM transformation option (T072)
"""

import json
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
    transformed_content: Path = typer.Option(
        ..., "--transformed-content", help="Path to JSON file with LLM-transformed content"
    ),
) -> int:
    """Update documentation from spec-kit specifications.

    Args:
        incremental: Enable incremental update using Git diff
        transformed_content: Path to JSON file containing LLM-transformed content per feature (FR-038e: REQUIRED)

    Note:
        Session 2025-10-17 FR-038e: --transformed-content parameter is now REQUIRED.
        LLM transformation is always executed by the command template before calling this script.
    """
    try:
        # FR-038e: Parameter is now required by typer.Option(...), no manual check needed
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

        # T075: Track all features for skip statistics
        all_features = discoverer.discover_features()
        total_features_count = len(all_features)

        if incremental:
            # FR-019: Incremental update using Git diff
            try:
                change_detector = ChangeDetector()
                changed_features = change_detector.get_changed_features()

                if changed_features:
                    features = changed_features
                    skipped_count = total_features_count - len(features)
                    console.print(
                        f"[green]✓[/green] {len(features)} 個の変更された機能を検出しました（インクリメンタル更新）"
                    )
                    console.print(
                        f"[dim]  {skipped_count} 個の機能をスキップしました（変更なし）[/dim]"
                    )
                else:
                    console.print(
                        "[green]✓[/green] 変更が検出されませんでした。更新をスキップします。"
                    )
                    return 0
            except Exception:
                # If Git detection fails (no repo, no commits, etc.), fall back to full update
                console.print(
                    "[yellow]Note:[/yellow] Git履歴が見つかりません。フル更新にフォールバックします。"
                )
                features = all_features
                skipped_count = 0
        else:
            # Full update
            features = all_features
            skipped_count = 0
            console.print(f"[green]✓[/green] {len(features)} 個の機能を検出しました（フル更新）")

        if not features:
            console.print(
                "[red]✗[/red] specs/ ディレクトリに機能が見つかりません。",
                style="bold",
            )
            console.print("  /speckit.specify を実行して機能仕様を作成してください。")
            return 1

        # T071: Load LLM-transformed content (FR-038e: always provided)
        llm_stats = {"total_features": len(features), "transformed_features": 0, "original_features": 0}

        console.print(f"\n[bold]LLM変換済みコンテンツを読み込み中...[/bold] ({transformed_content})")
        try:
            with open(transformed_content, encoding="utf-8") as f:
                transformed_content_map = json.load(f)

            llm_stats["transformed_features"] = len(transformed_content_map)
            llm_stats["original_features"] = len(features) - llm_stats["transformed_features"]

            console.print(f"[green]✓[/green] {llm_stats['transformed_features']} 件の変換済みコンテンツを読み込みました")
        except FileNotFoundError:
            raise SpecKitDocsError(
                f"LLM変換済みコンテンツファイルが見つかりません: {transformed_content}",
                "コマンドテンプレート /speckit.doc-update の Step 1（LLM変換実行）を確認してください。"
            )
        except json.JSONDecodeError as e:
            raise SpecKitDocsError(
                f"LLM変換済みコンテンツのJSON解析に失敗しました: {e}",
                f"ファイル {transformed_content} のJSON形式を確認してください。"
            )

        # FR-012, FR-013, FR-014: Generate feature pages with optional LLM-transformed content (T073)
        console.print("\n[bold]ドキュメントページを生成中...[/bold]")
        page_generator = FeaturePageGenerator(docs_dir, structure_type, tool)
        feature_pages = page_generator.generate_pages(features, transformed_content_map)

        console.print(f"[green]✓[/green] {len(feature_pages)} ページを生成しました")

        # FR-013, FR-014: Update navigation
        console.print("\n[bold]ナビゲーションを更新中...[/bold]")
        nav_updater = NavigationUpdater(docs_dir, tool)
        nav_updater.update_navigation(feature_pages)

        console.print("[green]✓[/green] ナビゲーションを更新しました")

        # FR-020: Display update summary with LLM transform statistics (T074)
        console.print("\n[bold green]✓ ドキュメント更新が完了しました！[/bold green]")
        console.print("\n[bold]サマリー:[/bold]")
        console.print(f"  • 更新された機能: {len(features)}")
        console.print(f"  • 生成されたページ: {len(feature_pages)}")

        # T075: Display skip statistics (incremental mode only)
        if incremental and 'skipped_count' in locals():
            console.print(f"  • スキップ（変更なし）: {skipped_count}")

        # T074: Display LLM transform statistics
        if transformed_content_map:
            console.print("\n[bold]LLM変換統計:[/bold]")
            console.print(f"  • 合計機能数: {llm_stats['total_features']}")
            console.print(f"  • LLM変換済み: {llm_stats['transformed_features']}")
            console.print(f"  • 元のコンテンツ: {llm_stats['original_features']}")
            if llm_stats["transformed_features"] > 0:
                percentage = (llm_stats["transformed_features"] / llm_stats["total_features"]) * 100
                console.print(f"  • 変換率: {percentage:.1f}%")

        return 0

    except SpecKitDocsError as e:
        console.print(f"[red]✗[/red] {e.message}", style="bold")
        console.print(f"  💡 {e.suggestion}")
        return 1
    except Exception as e:
        console.print(f"[red]✗[/red] 予期しないエラーが発生しました: {e}", style="bold")
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
