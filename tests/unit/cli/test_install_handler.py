"""Unit tests for install_handler module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from speckit_docs.cli.install_handler import (
    copy_backend_scripts,
    copy_command_templates,
    install_handler,
    validate_speckit_project,
)
from speckit_docs.exceptions import SpecKitDocsError


class TestValidateSpecKitProject:
    """Tests for validate_speckit_project function."""

    def test_validate_speckit_project_success(self, tmp_path):
        """Test validation succeeds with valid spec-kit project."""
        # Create required directories
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()

        # Should return True
        result = validate_speckit_project(tmp_path)
        assert result is True

    def test_validate_speckit_project_missing_specify(self, tmp_path):
        """Test validation fails when .specify/ is missing."""
        # Only create .claude/
        (tmp_path / ".claude").mkdir()

        with pytest.raises(SpecKitDocsError) as exc_info:
            validate_speckit_project(tmp_path)

        assert "spec-kitプロジェクトではありません" in str(exc_info.value)
        assert "specify init" in str(exc_info.value)

    def test_validate_speckit_project_missing_claude(self, tmp_path):
        """Test validation fails when .claude/ is missing."""
        # Only create .specify/
        (tmp_path / ".specify").mkdir()

        with pytest.raises(SpecKitDocsError) as exc_info:
            validate_speckit_project(tmp_path)

        assert ".claude" in str(exc_info.value)

    def test_validate_speckit_project_both_missing(self, tmp_path):
        """Test validation fails when both directories are missing."""
        with pytest.raises(SpecKitDocsError) as exc_info:
            validate_speckit_project(tmp_path)

        # Should fail on .specify/ first
        assert "spec-kitプロジェクトではありません" in str(exc_info.value)


class TestInstallHandler:
    """Tests for install_handler function."""

    def test_install_handler_validates_project(self, tmp_path, monkeypatch):
        """Test that install_handler validates the project first."""
        # Change to tmp directory
        monkeypatch.chdir(tmp_path)

        # Should raise error because project is not valid
        with pytest.raises(SpecKitDocsError):
            install_handler(force=False)

    def test_install_handler_with_valid_project(self, tmp_path, monkeypatch):
        """Test install_handler with valid project (stub for now)."""
        # Create valid project structure
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        # This should not raise error (will do nothing for now as it's a stub)
        # Full implementation will be in T010-T011
        try:
            install_handler(force=True)
            # If it reaches here, validation passed
            assert True
        except SpecKitDocsError:
            # Validation failed
            pytest.fail("Validation should have passed for valid project")


class TestCopyCommandTemplates:
    """Tests for copy_command_templates function (T010)."""

    def test_copy_command_templates_success(self, tmp_path, monkeypatch):
        """Test copying command templates to .claude/commands/."""
        # Setup project structure
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "commands").mkdir()
        monkeypatch.chdir(tmp_path)

        # Copy templates
        copied_files = copy_command_templates(force=True)

        # Verify files were copied
        assert len(copied_files) == 2
        assert (tmp_path / ".claude" / "commands" / "doc-init.md").exists()
        assert (tmp_path / ".claude" / "commands" / "doc-update.md").exists()

    def test_copy_command_templates_creates_directory(self, tmp_path, monkeypatch):
        """Test that .claude/commands/ is created if it doesn't exist."""
        # Setup project structure without commands directory
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        # Copy templates
        copied_files = copy_command_templates(force=True)

        # Verify directory was created
        assert (tmp_path / ".claude" / "commands").exists()
        assert len(copied_files) == 2

    @patch("typer.confirm")
    def test_copy_command_templates_existing_file_confirmation(
        self, mock_confirm, tmp_path, monkeypatch
    ):
        """Test that existing files require confirmation when force=False."""
        # Setup project structure with existing file
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "commands").mkdir()
        existing_file = tmp_path / ".claude" / "commands" / "doc-init.md"
        existing_file.write_text("existing content")
        monkeypatch.chdir(tmp_path)

        # User confirms overwrite
        mock_confirm.return_value = True

        # Copy templates
        copied_files = copy_command_templates(force=False)

        # Verify confirmation was requested
        assert mock_confirm.called
        assert len(copied_files) == 2

    @patch("typer.confirm")
    def test_copy_command_templates_skip_on_no_confirmation(
        self, mock_confirm, tmp_path, monkeypatch
    ):
        """Test that files are skipped when user declines confirmation."""
        # Setup project structure with existing file
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "commands").mkdir()
        existing_file = tmp_path / ".claude" / "commands" / "doc-init.md"
        existing_file.write_text("existing content")
        monkeypatch.chdir(tmp_path)

        # User declines overwrite
        mock_confirm.return_value = False

        # Copy templates
        copied_files = copy_command_templates(force=False)

        # Verify file was skipped (only 1 file copied)
        assert len(copied_files) == 1
        assert existing_file.read_text() == "existing content"


class TestCopyBackendScripts:
    """Tests for copy_backend_scripts function (T011)."""

    def test_copy_backend_scripts_success(self, tmp_path, monkeypatch):
        """Test copying backend scripts to .specify/scripts/docs/."""
        # Setup project structure
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".specify" / "scripts").mkdir()
        (tmp_path / ".specify" / "scripts" / "docs").mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        # Copy scripts
        copied_files = copy_backend_scripts(force=True)

        # Verify files were copied (includes __init__.py)
        assert len(copied_files) == 3
        assert (tmp_path / ".specify" / "scripts" / "docs" / "doc_init.py").exists()
        assert (tmp_path / ".specify" / "scripts" / "docs" / "doc_update.py").exists()
        assert (tmp_path / ".specify" / "scripts" / "docs" / "__init__.py").exists()

    def test_copy_backend_scripts_creates_directory(self, tmp_path, monkeypatch):
        """Test that .specify/scripts/docs/ is created if it doesn't exist."""
        # Setup project structure without scripts directory
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        # Copy scripts
        copied_files = copy_backend_scripts(force=True)

        # Verify directory was created (includes __init__.py)
        assert (tmp_path / ".specify" / "scripts" / "docs").exists()
        assert len(copied_files) == 3

    @patch("typer.confirm")
    def test_copy_backend_scripts_existing_file_confirmation(
        self, mock_confirm, tmp_path, monkeypatch
    ):
        """Test that existing files require confirmation when force=False."""
        # Setup project structure with existing file
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".specify" / "scripts" / "docs").mkdir(parents=True)
        existing_file = tmp_path / ".specify" / "scripts" / "docs" / "doc_init.py"
        existing_file.write_text("existing content")
        monkeypatch.chdir(tmp_path)

        # User confirms overwrite
        mock_confirm.return_value = True

        # Copy scripts
        copied_files = copy_backend_scripts(force=False)

        # Verify confirmation was requested (includes __init__.py)
        assert mock_confirm.called
        assert len(copied_files) == 3
