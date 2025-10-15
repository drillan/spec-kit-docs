"""Dependency management utilities for automatic installation.

This module provides utilities for automatically installing Sphinx/MkDocs dependencies
when pyproject.toml and uv command are available. It follows the informed consent pattern
with user approval before making any changes.

Session 2025-10-15: Implementation of FR-008b through FR-008e
"""

import importlib.util
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import typer
from rich.console import Console


@dataclass(frozen=True)
class DependencyResult:
    """Result of dependency installation attempt.

    Attributes:
        status: One of "installed", "skipped", "failed", "not_needed"
        message: Human-readable status message
        installed_packages: List of successfully installed packages (empty unless status="installed")
    """

    status: Literal["installed", "skipped", "failed", "not_needed"]
    message: str
    installed_packages: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate DependencyResult constraints."""
        valid_statuses = ["installed", "skipped", "failed", "not_needed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

        if self.status == "installed" and not self.installed_packages:
            raise ValueError("installed_packages must not be empty when status is 'installed'")


@dataclass(frozen=True)
class PackageManager:
    """Represents a package manager and its availability.

    Attributes:
        name: Package manager name (uv, poetry, pip, conda)
        command: Installation command template
        available: Whether the package manager is available on the system
    """

    name: str
    command: str
    available: bool

    def __post_init__(self) -> None:
        """Validate PackageManager constraints."""
        valid_names = ["uv", "poetry", "pip", "conda"]
        if self.name not in valid_names:
            raise ValueError(f"Invalid package manager: {self.name}. Must be one of {valid_names}")


def get_required_packages(doc_type: str) -> list[str]:
    """Get the list of required packages for a documentation tool.

    Args:
        doc_type: Documentation tool type ("sphinx" or "mkdocs")

    Returns:
        List of package specifications with version constraints

    Raises:
        ValueError: If doc_type is not "sphinx" or "mkdocs"

    Examples:
        >>> get_required_packages("sphinx")
        ['sphinx>=7.0', 'myst-parser>=2.0']
        >>> get_required_packages("mkdocs")
        ['mkdocs>=1.5', 'mkdocs-material>=9.0']
    """
    if doc_type == "sphinx":
        return ["sphinx>=7.0", "myst-parser>=2.0"]
    elif doc_type == "mkdocs":
        return ["mkdocs>=1.5", "mkdocs-material>=9.0"]
    else:
        raise ValueError(f"Invalid doc_type: {doc_type}. Must be 'sphinx' or 'mkdocs'")


def detect_package_managers(project_root: Path, doc_type: str) -> list[tuple[str, str]]:
    """Detect available package managers and generate installation commands.

    Checks for package managers in priority order: uv > poetry > pip.

    Args:
        project_root: Project root directory (currently unused, for future extensibility)
        doc_type: Documentation tool type ("sphinx" or "mkdocs")

    Returns:
        List of (manager_name, install_command) tuples in priority order.
        Empty list if no package managers are available.

    Examples:
        >>> detect_package_managers(Path("/tmp/project"), "sphinx")
        [('uv', 'uv add sphinx>=7.0 myst-parser>=2.0'),
         ('poetry', 'poetry add sphinx>=7.0 myst-parser>=2.0'),
         ('pip', 'pip install sphinx>=7.0 myst-parser>=2.0')]
    """
    packages = get_required_packages(doc_type)
    package_str = " ".join(packages)

    managers = [
        ("uv", f"uv add {package_str}"),
        ("poetry", f"poetry add {package_str}"),
        ("pip", f"pip install {package_str}"),
    ]

    available = []
    for name, command in managers:
        if shutil.which(name):
            available.append((name, command))

    return available


def show_alternative_methods(doc_type: str, console: Console, project_root: Path) -> None:
    """Display alternative installation methods when auto-install fails.

    Shows two methods:
    1. Manual installation with available package managers
    2. spec-kit workflow explanation

    Implements FR-008d: Clear alternative methods presentation.

    Args:
        doc_type: Documentation tool type ("sphinx" or "mkdocs")
        console: Rich console for output
        project_root: Project root directory
    """
    console.print("\n[yellow]代替のインストール方法:[/yellow]")

    # Method 1: Manual installation
    console.print("\n[bold]方法1: 手動インストール[/bold]")
    managers = detect_package_managers(project_root, doc_type)

    if managers:
        console.print("以下のパッケージマネージャーが利用可能です:")
        for name, command in managers:
            console.print(f"  • {name}: [cyan]{command}[/cyan]")
    else:
        console.print("  [red]利用可能なパッケージマネージャーが見つかりません。[/red]")
        packages = get_required_packages(doc_type)
        console.print(f"  必要なパッケージ: {', '.join(packages)}")

    # Method 2: spec-kit workflow
    console.print("\n[bold]方法2: spec-kitワークフロー[/bold]")
    console.print("  依存関係をspec-kitのワークフローで管理する方法:")
    console.print("  1. [cyan]/speckit.specify[/cyan] - 機能仕様に依存関係要件を記述")
    console.print("  2. [cyan]/speckit.plan[/cyan] - 実装計画に依存関係詳細を含める")
    console.print("  3. [cyan]/speckit.tasks[/cyan] - タスクリストに依存関係インストールタスクを生成")
    console.print("  4. [cyan]/speckit.implement[/cyan] - タスクを実行して依存関係をインストール")
    console.print("\n  [dim]この方法の利点: バージョン管理、テスト、ドキュメント化が自動化されます[/dim]")


def handle_dependencies(
    doc_type: str,
    auto_install: bool,
    no_install: bool,
    project_root: Path,
    console: Console,
) -> DependencyResult:
    """Handle dependency checking and installation.

    Implements FR-008b through FR-008e: Conditional auto-installation with informed consent.

    Args:
        doc_type: Documentation tool type ("sphinx" or "mkdocs")
        auto_install: Skip user confirmation (CI/CD mode)
        no_install: Skip all dependency checks and installation
        project_root: Project root directory (must contain pyproject.toml)
        console: Rich console for progress display

    Returns:
        DependencyResult with status, message, and installed packages

    Raises:
        ValueError: If doc_type is not "sphinx" or "mkdocs"

    Example:
        >>> from pathlib import Path
        >>> from rich.console import Console
        >>> result = handle_dependencies(
        ...     doc_type="sphinx",
        ...     auto_install=False,
        ...     no_install=False,
        ...     project_root=Path("/tmp/project"),
        ...     console=Console(),
        ... )
        >>> assert result.status in ["installed", "skipped", "failed", "not_needed"]
    """
    # Validate doc_type
    if doc_type not in ["sphinx", "mkdocs"]:
        raise ValueError(f"Invalid doc_type: {doc_type}. Must be 'sphinx' or 'mkdocs'")

    # Step 1: Check --no-install flag
    if no_install:
        return DependencyResult(
            status="skipped",
            message="--no-install指定のためスキップ",
            installed_packages=[],
        )

    # Step 2: Check pyproject.toml existence
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        console.print("[red]✗[/red] pyproject.tomlが見つかりません")
        show_alternative_methods(doc_type, console, project_root)
        return DependencyResult(
            status="failed",
            message="pyproject.toml不在",
            installed_packages=[],
        )

    # Step 3: Check uv command availability
    uv_path = shutil.which("uv")
    if not uv_path:
        console.print("[red]✗[/red] uvコマンドが見つかりません")
        show_alternative_methods(doc_type, console, project_root)
        return DependencyResult(
            status="failed",
            message="uvコマンド不在",
            installed_packages=[],
        )

    # Step 4: Check if packages are already installed
    packages = get_required_packages(doc_type)
    all_installed = True
    for package in packages:
        # Extract package name (e.g., "sphinx>=7.0" -> "sphinx")
        package_name = package.split(">=")[0].split("==")[0].split("~=")[0]
        # Replace hyphens with underscores for import names
        import_name = package_name.replace("-", "_")
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            all_installed = False
            break

    if all_installed:
        console.print("[green]✓[/green] すべてのパッケージが既にインストール済みです")
        return DependencyResult(
            status="not_needed",
            message="すべてのパッケージがインストール済み",
            installed_packages=[],
        )

    # Step 5: Get user approval (unless auto_install=True)
    if not auto_install:
        console.print("\n[bold]依存関係の自動インストール[/bold]")
        console.print(f"ドキュメントツール: [cyan]{doc_type}[/cyan]")
        console.print("インストールするパッケージ:")
        for pkg in packages:
            console.print(f"  • {pkg}")
        console.print(f"\n実行コマンド: [cyan]uv add {' '.join(packages)}[/cyan]")
        console.print("[yellow]警告: pyproject.tomlが変更されます[/yellow]")

        confirmed = typer.confirm("\nインストールを続行しますか?", default=True)
        if not confirmed:
            console.print("[yellow]ユーザーがインストールをキャンセルしました[/yellow]")
            show_alternative_methods(doc_type, console, project_root)
            return DependencyResult(
                status="skipped",
                message="ユーザーが拒否",
                installed_packages=[],
            )

    # Step 6: Execute uv add
    console.print("\n[cyan]依存関係をインストール中...[/cyan]")
    try:
        result = subprocess.run(
            ["uv", "add"] + packages,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout (SC-002b)
            check=False,  # Manual returncode checking
        )

        if result.returncode == 0:
            console.print("[green]✓[/green] インストール成功")
            return DependencyResult(
                status="installed",
                message="インストール成功",
                installed_packages=packages,
            )
        else:
            console.print(f"[red]✗[/red] uv addが失敗しました: {result.stderr}")
            show_alternative_methods(doc_type, console, project_root)
            return DependencyResult(
                status="failed",
                message=f"uv add失敗: {result.stderr}",
                installed_packages=[],
            )

    except subprocess.TimeoutExpired:
        console.print("[red]✗[/red] インストールがタイムアウトしました（5分超過）")
        show_alternative_methods(doc_type, console, project_root)
        return DependencyResult(
            status="failed",
            message="タイムアウト",
            installed_packages=[],
        )
    except FileNotFoundError:
        # This should not happen because we checked shutil.which() earlier,
        # but handle it for completeness
        console.print("[red]✗[/red] uvコマンドが見つかりません")
        show_alternative_methods(doc_type, console, project_root)
        return DependencyResult(
            status="failed",
            message="uvコマンド不在",
            installed_packages=[],
        )
