#!/usr/bin/env python3
"""
doc_update.py - Update documentation from spec-kit features

This script updates Sphinx or MkDocs documentation from spec.md files
in spec-kit features.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from speckit_docs.generators.mkdocs import MkDocsGenerator
from speckit_docs.generators.sphinx import SphinxGenerator
from speckit_docs.parsers.feature_scanner import FeatureScanner
from speckit_docs.utils.validation import (
    DocumentationProjectError,
    GitValidationError,
    ProjectValidationError,
    validate_git_repo,
    validate_speckit_project,
)


def detect_documentation_tool(docs_dir: Path) -> str:
    """
    Detect which documentation tool is being used.

    Args:
        docs_dir: Path to docs directory

    Returns:
        "sphinx" or "mkdocs"

    Raises:
        DocumentationProjectError: If tool cannot be detected
    """
    if (docs_dir / "conf.py").exists():
        return "sphinx"
    elif (docs_dir / "mkdocs.yml").exists():
        return "mkdocs"
    else:
        raise DocumentationProjectError(
            "ドキュメントプロジェクトが見つかりません。",
            "/speckit.doc-init を実行してプロジェクトを初期化してください。",
        )


def main():
    """Main entry point for doc-update command."""
    parser = argparse.ArgumentParser(
        description="Update documentation from spec-kit features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Regenerate all documentation (disable incremental mode)",
    )

    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip HTML build (only generate Markdown files)",
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

        # Step 3: Detect documentation tool
        print("✓ ドキュメントツールを検出中...")
        docs_dir = Path.cwd() / "docs"
        if not docs_dir.exists():
            raise DocumentationProjectError(
                "docs/ ディレクトリが見つかりません。",
                "/speckit.doc-init を実行してプロジェクトを初期化してください。",
            )

        tool = detect_documentation_tool(docs_dir)
        print(f"✓ {tool.capitalize()}プロジェクトを検出しました")

        # Step 4: Scan features
        print("✓ 機能をスキャン中...")
        scanner = FeatureScanner()
        features = scanner.scan(require_spec=True)
        feature_count = len(features)

        if feature_count == 0:
            print("⚠️  警告: spec.md ファイルを持つ機能が見つかりませんでした。")
            print("\n次のステップ:")
            print("  1. specs/ ディレクトリに機能を作成")
            print("  2. 各機能に spec.md を作成")
            print("  3. /speckit.doc-update を再実行")
            return 0

        print(f"✓ {feature_count}つの機能を発見しました")

        # Step 5: Create generator and update docs
        print(f"\n✓ ドキュメントを更新中...")

        # We need a minimal GeneratorConfig - read from existing config
        if tool == "sphinx":
            # Read existing conf.py to get config
            conf_py = docs_dir / "conf.py"
            content = conf_py.read_text()

            # Extract project name
            import re
            project_match = re.search(r"project\s*=\s*['\"](.+?)['\"]", content)
            author_match = re.search(r"author\s*=\s*['\"](.+?)['\"]", content)
            version_match = re.search(r"version\s*=\s*['\"](.+?)['\"]", content)
            language_match = re.search(r"language\s*=\s*['\"](.+?)['\"]", content)

            from speckit_docs.generators.base import GeneratorConfig

            config = GeneratorConfig(
                tool="sphinx",
                project_name=project_match.group(1) if project_match else "Project",
                author=author_match.group(1) if author_match else "Unknown",
                version=version_match.group(1) if version_match else "0.1.0",
                language=language_match.group(1) if language_match else "ja",
            )

            generator = SphinxGenerator(config)

        else:  # mkdocs
            # Read existing mkdocs.yml to get config
            import yaml

            mkdocs_yml = docs_dir / "mkdocs.yml"
            with open(mkdocs_yml) as f:
                config_data = yaml.safe_load(f)

            from speckit_docs.generators.base import GeneratorConfig

            config = GeneratorConfig(
                tool="mkdocs",
                project_name=config_data.get("site_name", "Project"),
                author=config_data.get("site_author", "Unknown"),
                version="0.1.0",
                language=config_data.get("theme", {}).get("language", "ja"),
            )

            generator = MkDocsGenerator(config)

        # Update documentation
        incremental = not args.no_incremental
        generator.update_docs(features, incremental=incremental)

        print(f"✓ ドキュメントを更新しました")

        # Step 6: Show generated files
        print("\n生成されたファイル:")
        features_dir = docs_dir / "features"
        if features_dir.exists():
            for file in sorted(features_dir.rglob("*.md")):
                print(f"  - {file.relative_to(docs_dir)}")

        # Step 7: Build HTML (unless --no-build)
        if not args.no_build:
            print(f"\n✓ HTMLをビルド中...")
            try:
                build_result = generator.build_docs()
                print(build_result.get_summary())

                if build_result.success:
                    print(f"\n✓ HTMLビルドが完了しました")
                    print(f"  出力ディレクトリ: {build_result.output_dir}")

                    # Show next steps
                    print("\n次のステップ:")
                    if tool == "sphinx":
                        print(f"  ブラウザで {build_result.output_dir}/index.html を開く")
                    else:
                        print(f"  ブラウザで {build_result.output_dir}/index.html を開く")
                        print(f"  または 'cd docs && mkdocs serve' でライブプレビュー")
                else:
                    print(f"\n⚠️  HTMLビルド中にエラーが発生しました")
                    if build_result.errors:
                        print("\nエラー:")
                        for error in build_result.errors[:5]:  # Show first 5 errors
                            print(f"  - {error}")
                    if build_result.warnings:
                        print("\n警告:")
                        for warning in build_result.warnings[:5]:  # Show first 5 warnings
                            print(f"  - {warning}")

            except Exception as e:
                print(f"\n⚠️  HTMLビルド中にエラーが発生しました: {e}")
                print("\n次のステップ:")
                if tool == "sphinx":
                    print("  手動でビルド: cd docs && make html")
                else:
                    print("  手動でビルド: cd docs && mkdocs build")

        else:
            # Show next steps when --no-build is used
            print("\n次のステップ:")
            if tool == "sphinx":
                print("  1. cd docs && make html でHTMLをビルド")
                print("  2. docs/_build/html/index.html をブラウザで開く")
            else:
                print("  1. cd docs && mkdocs build でHTMLをビルド")
                print("  2. docs/site/index.html をブラウザで開く")
                print("  または 'cd docs && mkdocs serve' でライブプレビュー")

        return 0

    except ProjectValidationError as e:
        print(f"\n✗ エラー: {e.message}")
        print(f"\n💡 提案: {e.suggestion}")
        return 1

    except GitValidationError as e:
        print(f"\n✗ エラー: {e.message}")
        print(f"\n💡 提案: {e.suggestion}")
        return 1

    except DocumentationProjectError as e:
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
