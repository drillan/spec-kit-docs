"""Interactive prompts for CLI commands."""

import os
from pathlib import Path
from typing import Optional


def prompt_tool_selection() -> str:
    """
    Prompt user to select documentation tool.

    Returns:
        "sphinx" or "mkdocs"
    """
    print("\nどのドキュメント生成ツールを使用しますか？")
    print("1) Sphinx (推奨 - MyST Markdown対応)")
    print("2) MkDocs (シンプル)")

    while True:
        choice = input("選択 [1]: ").strip() or "1"

        if choice == "1":
            return "sphinx"
        elif choice == "2":
            return "mkdocs"
        else:
            print("エラー: 1 または 2 を選択してください。")


def prompt_project_name() -> str:
    """
    Prompt user for project name.

    Returns:
        Project name (defaults to current directory name)
    """
    default_name = Path.cwd().name

    while True:
        name = input(f"\nプロジェクト名を入力してください [{default_name}]: ").strip() or default_name

        # Validate: no special characters
        if "/" in name or "\\" in name or ":" in name:
            print("エラー: プロジェクト名に特殊文字 (/, \\, :) は使用できません。")
            continue

        if not name:
            print("エラー: プロジェクト名は必須です。")
            continue

        return name


def prompt_author() -> str:
    """
    Prompt user for author name.

    Returns:
        Author name (defaults to Git user.name)
    """
    # Try to get Git user name
    try:
        import subprocess

        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        default_author = result.stdout.strip()
    except Exception:
        default_author = "Unknown Author"

    author = (
        input(f"\n著者名を入力してください [{default_author}]: ").strip() or default_author
    )

    # If empty, use "Unknown Author"
    if not author:
        author = "Unknown Author"

    return author


def prompt_version() -> str:
    """
    Prompt user for version number.

    Returns:
        Version number (defaults to 0.1.0)
    """
    default_version = "0.1.0"

    version = (
        input(f"\n初期バージョン番号を入力してください [{default_version}]: ").strip()
        or default_version
    )

    return version


def prompt_language() -> str:
    """
    Prompt user for documentation language.

    Returns:
        Language code (defaults to "ja")
    """
    default_language = "ja"

    language = (
        input(f"\nドキュメント言語を入力してください [{default_language}]: ").strip()
        or default_language
    )

    return language


def get_all_config_interactive(tool: Optional[str] = None) -> dict:
    """
    Get all configuration through interactive prompts.

    Args:
        tool: Optional pre-selected tool ("sphinx" or "mkdocs")

    Returns:
        Dictionary with configuration values
    """
    config = {}

    # Tool selection
    if tool is None:
        config["tool"] = prompt_tool_selection()
    else:
        config["tool"] = tool

    # Project metadata
    config["project_name"] = prompt_project_name()
    config["author"] = prompt_author()
    config["version"] = prompt_version()
    config["language"] = prompt_language()

    return config


def confirm_overwrite(path: Path) -> bool:
    """
    Prompt user to confirm overwriting an existing directory.

    Args:
        path: Path to check

    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n⚠️  警告: {path} が既に存在します。")

    while True:
        choice = input("上書きしますか？ (yes/no) [no]: ").strip().lower() or "no"

        if choice in ["yes", "y"]:
            return True
        elif choice in ["no", "n"]:
            return False
        else:
            print("エラー: 'yes' または 'no' を入力してください。")
