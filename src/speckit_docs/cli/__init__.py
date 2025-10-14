"""CLI module for speckit-docs."""

import typer
from rich.console import Console

app = typer.Typer(
    name="speckit-docs",
    help="AI-driven documentation generation system for spec-kit projects",
    no_args_is_help=True,
)
console = Console()


@app.command()
def install(
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip confirmation and overwrite existing files",
    ),
) -> None:
    """
    Install spec-kit-docs commands into the current project.

    This command copies command definitions (.claude/commands/) and
    backend scripts (.specify/scripts/docs/) to the current project.
    """
    from .install_handler import install_handler

    install_handler(force=force)


if __name__ == "__main__":
    app()
