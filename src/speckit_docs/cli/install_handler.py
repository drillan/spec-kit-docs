"""Install handler for spec-kit-docs CLI."""

from pathlib import Path

from ..exceptions import SpecKitDocsError


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

    # TODO: T010-T011 will implement file copying
    # For now, just validate the project
    pass
