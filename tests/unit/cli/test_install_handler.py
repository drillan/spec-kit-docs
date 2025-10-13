"""Unit tests for install_handler module."""

from pathlib import Path

import pytest

from speckit_docs.cli.install_handler import install_handler, validate_speckit_project
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
