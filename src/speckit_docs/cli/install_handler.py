"""Install handler for spec-kit-docs CLI."""

from importlib.resources import files
from pathlib import Path

import typer
from rich.console import Console

from ..exceptions import SpecKitDocsError

console = Console()


def validate_speckit_project(project_dir: Path = Path(".")) -> bool:
    """
    Validate that the current directory is a spec-kit project.

    Args:
        project_dir: Path to project directory (defaults to current directory)

    Returns:
        True if validation succeeds

    Raises:
        SpecKitDocsError: If project is not a valid spec-kit project
    """
    specify_dir = project_dir / ".specify"
    claude_dir = project_dir / ".claude"

    if not specify_dir.exists():
        raise SpecKitDocsError(
            "spec-kitプロジェクトではありません。",
            "最初に 'specify init' を実行してください。",
        )

    if not claude_dir.exists():
        raise SpecKitDocsError(
            ".claude/ディレクトリが見つかりません。",
            "spec-kitプロジェクトを正しく初期化してください。",
        )

    return True


def _copy_package_files(
    source_package_path: str, dest_dir: Path, force: bool
) -> list[Path]:
    """
    Copy files from a package directory to destination directory.

    Args:
        source_package_path: Dotted path to package (e.g., "speckit_docs.commands")
        dest_dir: Destination directory path
        force: Skip confirmation and overwrite existing files

    Returns:
        List of copied file paths
    """
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Get package files using importlib.resources
    package = files(source_package_path)
    copied_files: list[Path] = []

    # Iterate through all files in the package directory
    for resource in package.iterdir():
        if resource.is_file():
            dest_file = dest_dir / resource.name
            source_content = resource.read_text()

            # Check if file exists and handle confirmation
            if dest_file.exists() and not force:
                if not typer.confirm(
                    f"ファイル {dest_file} は既に存在します。上書きしますか？"
                ):
                    console.print(f"[yellow]スキップ: {dest_file}[/yellow]")
                    continue

            # Write file content
            dest_file.write_text(source_content)
            copied_files.append(dest_file)
            console.print(f"[green]✓[/green] コピー完了: {dest_file}")

    return copied_files


def copy_command_templates(force: bool = False) -> list[Path]:
    """
    Copy command template files to .claude/commands/ directory.

    Args:
        force: Skip confirmation and overwrite existing files

    Returns:
        List of copied file paths
    """
    dest_dir = Path(".claude") / "commands"
    return _copy_package_files("speckit_docs.commands", dest_dir, force)


def copy_backend_scripts(force: bool = False) -> list[Path]:
    """
    Copy backend script files to .specify/scripts/docs/ directory.

    Args:
        force: Skip confirmation and overwrite existing files

    Returns:
        List of copied file paths
    """
    dest_dir = Path(".specify") / "scripts" / "docs"
    return _copy_package_files("speckit_docs.scripts", dest_dir, force)


def install_handler(force: bool = False) -> None:
    """
    Handle the install command.

    Args:
        force: Skip confirmation and overwrite existing files

    Raises:
        SpecKitDocsError: If project validation fails
    """
    # Validate project
    validate_speckit_project()

    # Copy command templates (T010)
    console.print("\n[bold]コマンドテンプレートをコピー中...[/bold]")
    cmd_files = copy_command_templates(force=force)
    console.print(f"[green]✓[/green] {len(cmd_files)} 個のコマンドテンプレートをコピーしました\n")

    # Copy backend scripts (T011)
    console.print("[bold]バックエンドスクリプトをコピー中...[/bold]")
    script_files = copy_backend_scripts(force=force)
    console.print(f"[green]✓[/green] {len(script_files)} 個のスクリプトをコピーしました\n")

    console.print("[bold green]インストール完了！[/bold green]")
