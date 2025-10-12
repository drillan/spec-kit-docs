"""Git integration utilities for speckit-docs."""

from pathlib import Path
from typing import List, Optional

try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError
except ImportError:
    Repo = None
    InvalidGitRepositoryError = Exception

from .validation import GitValidationError


class GitRepository:
    """Wrapper for Git repository operations using GitPython."""

    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize Git repository wrapper.

        Args:
            repo_path: Path to repository root (defaults to current directory)

        Raises:
            GitValidationError: If GitPython is not installed or repo is invalid
        """
        if Repo is None:
            raise GitValidationError(
                "GitPython がインストールされていません。",
                "'uv pip install GitPython' を実行してインストールしてください。",
            )

        if repo_path is None:
            repo_path = Path.cwd()

        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            raise GitValidationError(
                f"{repo_path} はGitリポジトリではありません。",
                "'git init' を実行してGitリポジトリを初期化してください。",
            )

        self.repo_path = Path(self.repo.working_dir)

    def get_changed_files(
        self, base_ref: str = "HEAD~1", target_ref: str = "HEAD", path_filter: Optional[str] = None
    ) -> List[Path]:
        """
        Get list of changed files between two commits.

        Args:
            base_ref: Base reference (default: HEAD~1)
            target_ref: Target reference (default: HEAD)
            path_filter: Optional path filter (e.g., ".specify/specs/")

        Returns:
            List of changed file paths relative to repository root
        """
        try:
            # Get diff between base and target
            diff_index = self.repo.commit(base_ref).diff(target_ref)

            changed_files = []
            for diff_item in diff_index:
                # Get the file path (a_path for deletions, b_path for additions/modifications)
                file_path = diff_item.b_path or diff_item.a_path
                if file_path:
                    full_path = self.repo_path / file_path

                    # Apply path filter if specified
                    if path_filter:
                        if not str(full_path).startswith(str(self.repo_path / path_filter)):
                            continue

                    changed_files.append(full_path)

            return changed_files

        except Exception as e:
            # If there's no previous commit (initial commit), return empty list
            if "HEAD~1" in base_ref and len(list(self.repo.iter_commits())) < 2:
                return []
            raise GitValidationError(
                f"Git diff の取得に失敗しました: {str(e)}", "Gitリポジトリの状態を確認してください。"
            )

    def get_changed_spec_files(self) -> List[Path]:
        """
        Get list of changed spec.md files in .specify/specs/.

        Returns:
            List of changed spec.md file paths
        """
        changed_files = self.get_changed_files(path_filter=".specify/specs/")

        # Filter for spec.md files
        spec_files = [f for f in changed_files if f.name == "spec.md"]

        return spec_files

    def has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes in the working directory.

        Returns:
            True if there are uncommitted changes, False otherwise
        """
        return self.repo.is_dirty() or len(self.repo.untracked_files) > 0

    def get_user_name(self) -> str:
        """
        Get Git user.name configuration.

        Returns:
            Git user name, or "Unknown Author" if not configured
        """
        try:
            return self.repo.config_reader().get_value("user", "name")
        except Exception:
            return "Unknown Author"

    def get_user_email(self) -> str:
        """
        Get Git user.email configuration.

        Returns:
            Git user email, or empty string if not configured
        """
        try:
            return self.repo.config_reader().get_value("user", "email")
        except Exception:
            return ""


def get_changed_features(repo_path: Optional[Path] = None) -> List[Path]:
    """
    Get list of feature directories with changed spec.md files.

    Args:
        repo_path: Optional repository path (defaults to current directory)

    Returns:
        List of feature directory paths (e.g., [.specify/specs/001-user-auth/])
    """
    git_repo = GitRepository(repo_path)
    spec_files = git_repo.get_changed_spec_files()

    # Extract feature directories (parent of spec.md)
    feature_dirs = [spec_file.parent for spec_file in spec_files]

    return feature_dirs
