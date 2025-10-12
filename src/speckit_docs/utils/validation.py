"""Validation utilities and custom error classes for speckit-docs."""

from pathlib import Path
from typing import Optional


class SpecKitDocsError(Exception):
    """Base exception for speckit-docs with error message and suggestion."""

    def __init__(self, message: str, suggestion: str):
        """
        Initialize error with message and suggestion.

        Args:
            message: Error description
            suggestion: Suggested next steps to resolve the error
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"{message}\n\n💡 提案: {suggestion}")


class ProjectValidationError(SpecKitDocsError):
    """Raised when spec-kit project validation fails."""

    pass


class GitValidationError(SpecKitDocsError):
    """Raised when Git repository validation fails."""

    pass


class DocumentationProjectError(SpecKitDocsError):
    """Raised when documentation project validation fails."""

    pass


class MarkdownParseError(SpecKitDocsError):
    """Raised when Markdown parsing fails."""

    pass


class BuildError(SpecKitDocsError):
    """Raised when documentation build fails."""

    pass


def validate_speckit_project(project_root: Optional[Path] = None) -> Path:
    """
    Validate that the current directory is a spec-kit project.

    Args:
        project_root: Optional project root path (defaults to current directory)

    Returns:
        Path to .specify directory

    Raises:
        ProjectValidationError: If .specify directory does not exist
    """
    if project_root is None:
        project_root = Path.cwd()

    specify_dir = project_root / ".specify"

    if not specify_dir.exists():
        raise ProjectValidationError(
            "spec-kitプロジェクトではありません。",
            "最初に 'specify init' を実行してspec-kitプロジェクトを初期化してください。",
        )

    if not specify_dir.is_dir():
        raise ProjectValidationError(
            ".specify が存在しますが、ディレクトリではありません。",
            ".specify ファイルを削除して 'specify init' を再実行してください。",
        )

    return specify_dir


def validate_git_repo(project_root: Optional[Path] = None) -> Path:
    """
    Validate that the current directory is a Git repository.

    Args:
        project_root: Optional project root path (defaults to current directory)

    Returns:
        Path to .git directory

    Raises:
        GitValidationError: If .git directory does not exist
    """
    if project_root is None:
        project_root = Path.cwd()

    git_dir = project_root / ".git"

    if not git_dir.exists():
        raise GitValidationError(
            "Gitリポジトリではありません。",
            "'git init' を実行してGitリポジトリを初期化してください。",
        )

    return git_dir


def validate_docs_project(
    project_root: Optional[Path] = None, require_sphinx: bool = False, require_mkdocs: bool = False
) -> Path:
    """
    Validate that documentation project exists.

    Args:
        project_root: Optional project root path (defaults to current directory)
        require_sphinx: If True, require Sphinx project (conf.py)
        require_mkdocs: If True, require MkDocs project (mkdocs.yml)

    Returns:
        Path to docs directory

    Raises:
        DocumentationProjectError: If docs directory or config files do not exist
    """
    if project_root is None:
        project_root = Path.cwd()

    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        raise DocumentationProjectError(
            "ドキュメントプロジェクトが初期化されていません。",
            "最初に /speckit.doc-init を実行してドキュメントプロジェクトを初期化してください。",
        )

    if require_sphinx:
        conf_py = docs_dir / "conf.py"
        if not conf_py.exists():
            raise DocumentationProjectError(
                "Sphinx設定ファイル (conf.py) が見つかりません。",
                "/speckit.doc-init を再実行してSphinxプロジェクトを初期化してください。",
            )

    if require_mkdocs:
        mkdocs_yml = docs_dir / "mkdocs.yml"
        if not mkdocs_yml.exists():
            raise DocumentationProjectError(
                "MkDocs設定ファイル (mkdocs.yml) が見つかりません。",
                "/speckit.doc-init を再実行してMkDocsプロジェクトを初期化してください。",
            )

    return docs_dir


def detect_docs_tool(project_root: Optional[Path] = None) -> Optional[str]:
    """
    Detect which documentation tool is configured (Sphinx or MkDocs).

    Args:
        project_root: Optional project root path (defaults to current directory)

    Returns:
        "sphinx", "mkdocs", or None if neither is detected
    """
    if project_root is None:
        project_root = Path.cwd()

    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        return None

    if (docs_dir / "conf.py").exists():
        return "sphinx"

    if (docs_dir / "mkdocs.yml").exists():
        return "mkdocs"

    return None
