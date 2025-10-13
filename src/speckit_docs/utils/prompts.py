"""Interactive prompts for CLI commands."""

from pathlib import Path


def prompt_tool_selection(interactive: bool = True) -> str:
    """
    Prompt user to select documentation tool.

    Args:
        interactive: If False, return default without prompting

    Returns:
        "sphinx" or "mkdocs"
    """
    if not interactive:
        return "sphinx"  # Default to Sphinx

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


def prompt_project_name(interactive: bool = True) -> str:
    """
    Prompt user for project name.

    Args:
        interactive: If False, return default without prompting

    Returns:
        Project name (defaults to current directory name)
    """
    default_name = Path.cwd().name

    if not interactive:
        return default_name

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


def prompt_author(interactive: bool = True) -> str:
    """
    Prompt user for author name.

    Args:
        interactive: If False, return default without prompting

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

    if not interactive:
        return default_author

    author = (
        input(f"\n著者名を入力してください [{default_author}]: ").strip() or default_author
    )

    # If empty, use "Unknown Author"
    if not author:
        author = "Unknown Author"

    return author


def prompt_version(interactive: bool = True) -> str:
    """
    Prompt user for version number.

    Args:
        interactive: If False, return default without prompting

    Returns:
        Version number (defaults to 0.1.0)
    """
    default_version = "0.1.0"

    if not interactive:
        return default_version

    version = (
        input(f"\n初期バージョン番号を入力してください [{default_version}]: ").strip()
        or default_version
    )

    return version


def prompt_language(interactive: bool = True) -> str:
    """
    Prompt user for documentation language.

    Args:
        interactive: If False, return default without prompting

    Returns:
        Language code (defaults to "ja")
    """
    default_language = "ja"

    if not interactive:
        return default_language

    language = (
        input(f"\nドキュメント言語を入力してください [{default_language}]: ").strip()
        or default_language
    )

    return language


def get_all_config_interactive(tool: str | None = None, interactive: bool = True) -> dict:
    """
    Get all configuration through interactive prompts.

    Args:
        tool: Optional pre-selected tool ("sphinx" or "mkdocs")
        interactive: If False, use defaults without prompting

    Returns:
        Dictionary with configuration values
    """
    config = {}

    # Tool selection
    if tool is None:
        config["tool"] = prompt_tool_selection(interactive=interactive)
    else:
        config["tool"] = tool

    # Project metadata
    config["project_name"] = prompt_project_name(interactive=interactive)
    config["author"] = prompt_author(interactive=interactive)
    config["version"] = prompt_version(interactive=interactive)
    config["language"] = prompt_language(interactive=interactive)

    return config


def confirm_overwrite(path: Path, interactive: bool = True) -> bool:
    """
    Prompt user to confirm overwriting an existing directory.

    Args:
        path: Path to check
        interactive: If False, return False (do not overwrite)

    Returns:
        True if user confirms, False otherwise
    """
    if not interactive:
        return False  # Default: do not overwrite in non-interactive mode

    print(f"\n⚠️  警告: {path} が既に存在します。")

    while True:
        choice = input("上書きしますか？ (yes/no) [no]: ").strip().lower() or "no"

        if choice in ["yes", "y"]:
            return True
        elif choice in ["no", "n"]:
            return False
        else:
            print("エラー: 'yes' または 'no' を入力してください。")
