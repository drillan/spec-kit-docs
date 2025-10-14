#!/usr/bin/env python3
"""
doc_init.py - Initialize documentation project for spec-kit

This script initializes a Sphinx or MkDocs documentation project
for a spec-kit project.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from speckit_docs.generators.base import BaseGenerator, GeneratorConfig
from speckit_docs.generators.mkdocs import MkDocsGenerator
from speckit_docs.generators.sphinx import SphinxGenerator
from speckit_docs.parsers.document_structure import DocumentStructure
from speckit_docs.parsers.feature_scanner import FeatureScanner
from speckit_docs.utils.prompts import confirm_overwrite
from speckit_docs.utils.validation import (
    GitValidationError,
    ProjectValidationError,
    validate_git_repo,
    validate_speckit_project,
)


def main() -> int:
    """Main entry point for doc-init command."""
    parser = argparse.ArgumentParser(
        description="Initialize documentation project for spec-kit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--type",
        choices=["sphinx", "mkdocs"],
        help="Documentation tool (sphinx or mkdocs)",
    )

    parser.add_argument(
        "--project-name",
        type=str,
        help="Project name (default: current directory name)",
    )

    parser.add_argument(
        "--author",
        type=str,
        help="Author name (default: Git user.name or 'Unknown Author')",
    )

    parser.add_argument(
        "--version",
        type=str,
        help="Initial version (default: 0.1.0)",
    )

    parser.add_argument(
        "--language",
        type=str,
        help="Documentation language (default: ja)",
    )

    parser.add_argument(
        "--site-name",
        type=str,
        help="Site name for MkDocs (default: same as project name)",
    )

    parser.add_argument(
        "--repo-url",
        type=str,
        help="Repository URL for MkDocs (default: Git remote origin URL or empty)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing docs/ directory without confirmation",
    )

    parser.add_argument(
        "--no-interaction",
        action="store_true",
        help="Disable interactive mode (use defaults)",
    )

    args = parser.parse_args()

    try:
        # Step 1: Validate spec-kit project
        print("✓ spec-kitプロジェクトを検証中...")
        validate_speckit_project()
        print("✓ spec-kitプロジェクトを検出しました")

        # Step 2: Validate Git repository
        print("✓ Gitリポジトリを検証中...")
        validate_git_repo()

        # Step 3: Check for existing docs directory
        docs_dir = Path.cwd() / "docs"
        if docs_dir.exists():
            # If --force is specified, proceed without confirmation
            if args.force:
                print("✓ --force フラグが指定されました。既存の docs/ を上書きします。")
            else:
                # Interactive confirmation (or fail in non-interactive mode)
                if not confirm_overwrite(docs_dir, interactive=not args.no_interaction):
                    if args.no_interaction:
                        print("\n✗ エラー: docs/ ディレクトリが既に存在します。")
                        print(
                            "💡 提案: --force フラグを追加するか、手動で docs/ を削除してください。"
                        )
                        return 1
                    else:
                        print("\n中止しました。")
                        return 0
            print()

        # Step 4: Scan features
        print("✓ 機能をスキャン中...")
        scanner = FeatureScanner()
        features = scanner.scan(require_spec=True)
        feature_count = len(features)
        print(f"✓ {feature_count}つの機能を発見しました")

        # Step 5: Determine document structure
        structure = DocumentStructure.determine_structure(feature_count)
        structure_name = "フラット" if structure.value == "FLAT" else "包括的"
        print(f"✓ ドキュメント構造: {structure_name} ({feature_count}機能)")

        # Step 6: Get configuration
        # Priority: CLI args > Interactive prompts > Defaults
        interactive = not args.no_interaction

        # Import individual prompt functions
        from speckit_docs.utils.prompts import (
            prompt_author,
            prompt_language,
            prompt_project_name,
            prompt_tool_selection,
            prompt_version,
        )

        # Get each config value (CLI args take priority)
        tool = args.type if args.type else prompt_tool_selection(interactive=interactive)
        project_name = (
            args.project_name if args.project_name else prompt_project_name(interactive=interactive)
        )
        author = args.author if args.author else prompt_author(interactive=interactive)
        version = args.version if args.version else prompt_version(interactive=interactive)
        language = args.language if args.language else prompt_language(interactive=interactive)

        # MkDocs-specific settings (FR-003b)
        custom_settings = {}
        if tool == "mkdocs":
            # Site name: default to project name
            site_name = args.site_name if args.site_name else project_name
            custom_settings["site_name"] = site_name

            # Repository URL: default to Git remote origin URL or empty string
            if args.repo_url:
                repo_url = args.repo_url
            else:
                # Try to get Git remote origin URL
                try:
                    import subprocess

                    result = subprocess.run(
                        ["git", "remote", "get-url", "origin"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    repo_url = result.stdout.strip()
                except Exception:
                    repo_url = ""  # Default to empty string if Git remote not found

            if repo_url:  # Only add if non-empty
                custom_settings["repo_url"] = repo_url

        # Create GeneratorConfig
        config = GeneratorConfig(
            tool=tool,
            project_name=project_name,
            author=author,
            version=version,
            language=language,
            custom_settings=custom_settings,
        )

        # Step 7: Initialize project
        print(f"\n✓ {config.tool.capitalize()}プロジェクトを初期化中...")

        generator: BaseGenerator
        if config.tool == "sphinx":
            generator = SphinxGenerator(config)
        else:
            generator = MkDocsGenerator(config)

        generator.init_project(structure_type=structure.value)

        print(f"✓ {config.tool.capitalize()}プロジェクトを初期化しました")

        # Step 8: Show generated files
        print("\n生成されたファイル:")
        if config.tool == "sphinx":
            print("  - docs/conf.py")
            print("  - docs/index.md")
            print("  - docs/Makefile")
            print("  - docs/make.bat")
        else:
            print("  - mkdocs.yml")  # MkDocs config is in project root
            print("  - docs/index.md")

        # Step 9: Show next steps
        print("\n次のステップ:")
        print("  1. /speckit.doc-update を実行してドキュメントを生成")

        if config.tool == "sphinx":
            print("  2. cd docs && make html でHTMLをビルド")
            print("  3. docs/_build/html/index.html をブラウザで開く")
        else:
            print("  2. cd docs && mkdocs serve でプレビュー")
            print("  3. ブラウザで http://127.0.0.1:8000 を開く")

        return 0

    except ProjectValidationError as e:
        print(f"\n✗ エラー: {e.message}")
        print(f"\n💡 提案: {e.suggestion}")
        return 1

    except GitValidationError as e:
        print(f"\n✗ エラー: {e.message}")
        print(f"\n💡 提案: {e.suggestion}")
        return 1

    except Exception as e:
        print(f"\n✗ エラー: {str(e)}")
        print("\n予期しないエラーが発生しました。")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
