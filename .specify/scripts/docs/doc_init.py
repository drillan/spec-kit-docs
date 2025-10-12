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

from speckit_docs.generators.base import GeneratorConfig
from speckit_docs.generators.mkdocs import MkDocsGenerator
from speckit_docs.generators.sphinx import SphinxGenerator
from speckit_docs.parsers.document_structure import DocumentStructure
from speckit_docs.parsers.feature_scanner import FeatureScanner
from speckit_docs.utils.prompts import confirm_overwrite, get_all_config_interactive
from speckit_docs.utils.validation import (
    GitValidationError,
    ProjectValidationError,
    validate_git_repo,
    validate_speckit_project,
)


def main():
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
            if not args.no_interaction:
                if not confirm_overwrite(docs_dir):
                    print("\n中止しました。")
                    return 0
                print()
            else:
                print("⚠️  警告: docs/ ディレクトリが既に存在します。上書きします。")

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
        if args.no_interaction:
            # Use defaults
            config_dict = {
                "tool": args.type or "sphinx",
                "project_name": Path.cwd().name,
                "author": "Unknown Author",
                "version": "0.1.0",
                "language": "ja",
            }
        else:
            # Interactive prompts
            config_dict = get_all_config_interactive(tool=args.type)

        # Create GeneratorConfig
        config = GeneratorConfig(
            tool=config_dict["tool"],
            project_name=config_dict["project_name"],
            author=config_dict["author"],
            version=config_dict.get("version", "0.1.0"),
            language=config_dict.get("language", "ja"),
        )

        # Step 7: Initialize project
        print(f"\n✓ {config.tool.capitalize()}プロジェクトを初期化中...")

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
            print("  - docs/mkdocs.yml")
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
