"""Unit tests for typer CLI application."""

from typer.testing import CliRunner

from speckit_docs.cli import app

runner = CliRunner()


class TestCLIBasics:
    """Basic tests for CLI application."""

    def test_app_help(self):
        """Test that --help flag works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # With single command, help shows the command directly
        assert "install" in result.stdout.lower()

    def test_app_shows_usage(self):
        """Test that usage information is shown."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Should show usage information
        assert "usage" in result.stdout.lower() or "options" in result.stdout.lower()


class TestInstallCommand:
    """Tests for install command."""

    def test_install_command_exists(self):
        """Test that install command exists and has help."""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "install" in result.stdout.lower()

    def test_install_command_has_force_option(self):
        """Test that install command has --force option."""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "--force" in result.stdout

    def test_install_command_description(self):
        """Test that install command has proper description."""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        # Should mention what it does
        assert "command" in result.stdout.lower()
