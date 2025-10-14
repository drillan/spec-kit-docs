"""Tests for utils.prompts module."""

from pathlib import Path

from speckit_docs.utils.prompts import (
    confirm_overwrite,
    get_all_config_interactive,
    prompt_author,
    prompt_language,
    prompt_project_name,
    prompt_tool_selection,
    prompt_version,
)


class TestPrompts:
    """Tests for interactive prompt functions."""

    def test_prompt_tool_selection_non_interactive(self):
        """Test tool selection in non-interactive mode."""
        result = prompt_tool_selection(interactive=False)
        assert result == "sphinx"  # Default

    def test_prompt_project_name_non_interactive(self):
        """Test project name prompt in non-interactive mode."""
        result = prompt_project_name(interactive=False)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_confirm_overwrite_non_interactive(self):
        """Test overwrite confirmation in non-interactive mode."""
        # Non-interactive mode should return False (don't overwrite by default)
        result = confirm_overwrite(Path("/test/file.md"), interactive=False)
        assert result is False

    def test_confirm_overwrite_default_behavior(self):
        """Test overwrite confirmation default behavior."""
        # Non-interactive mode returns False by default
        result = confirm_overwrite(Path("/test/file.md"), interactive=False)
        assert result is False

    def test_prompt_tool_selection_simulated_input(self, monkeypatch):
        """Test tool selection with simulated user input."""
        # Simulate user selecting Sphinx
        inputs = iter(["1"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_tool_selection(interactive=True)
        assert result == "sphinx"

    def test_prompt_tool_selection_mkdocs_input(self, monkeypatch):
        """Test tool selection with MkDocs choice."""
        # Simulate user selecting MkDocs
        inputs = iter(["2"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_tool_selection(interactive=True)
        assert result == "mkdocs"

    def test_prompt_tool_selection_default(self, monkeypatch):
        """Test tool selection with default (empty input)."""
        # Simulate user pressing Enter (default)
        inputs = iter([""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_tool_selection(interactive=True)
        assert result == "sphinx"  # Default is Sphinx

    def test_prompt_tool_selection_invalid_then_valid(self, monkeypatch):
        """Test tool selection with invalid input followed by valid."""
        # Simulate invalid input then valid
        inputs = iter(["3", "1"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_tool_selection(interactive=True)
        assert result == "sphinx"

    def test_prompt_project_name_custom(self, monkeypatch):
        """Test project name prompt with custom input."""
        # Simulate user entering custom project name
        inputs = iter(["My Custom Project"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_project_name(interactive=True)
        assert result == "My Custom Project"

    def test_confirm_overwrite_yes(self, monkeypatch):
        """Test overwrite confirmation with 'yes' input."""
        inputs = iter(["y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = confirm_overwrite(Path("/test/file.md"), interactive=True)
        assert result is True

    def test_confirm_overwrite_no(self, monkeypatch):
        """Test overwrite confirmation with 'no' input."""
        inputs = iter(["n"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = confirm_overwrite(Path("/test/file.md"), interactive=True)
        assert result is False

    def test_prompt_author_non_interactive(self):
        """Test author prompt in non-interactive mode."""
        result = prompt_author(interactive=False)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_prompt_author_custom(self, monkeypatch):
        """Test author prompt with custom input."""
        inputs = iter(["John Doe"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_author(interactive=True)
        assert result == "John Doe"

    def test_prompt_author_default(self, monkeypatch):
        """Test author prompt with default (empty input)."""
        inputs = iter([""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_author(interactive=True)
        # Should use Git config or "Unknown Author"
        assert isinstance(result, str)
        assert len(result) > 0

    def test_prompt_version_non_interactive(self):
        """Test version prompt in non-interactive mode."""
        result = prompt_version(interactive=False)
        assert result == "0.1.0"  # Default

    def test_prompt_version_custom(self, monkeypatch):
        """Test version prompt with custom input."""
        inputs = iter(["1.2.3"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_version(interactive=True)
        assert result == "1.2.3"

    def test_prompt_version_default(self, monkeypatch):
        """Test version prompt with default (empty input)."""
        inputs = iter([""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_version(interactive=True)
        assert result == "0.1.0"

    def test_prompt_language_non_interactive(self):
        """Test language prompt in non-interactive mode."""
        result = prompt_language(interactive=False)
        assert result == "ja"  # Default

    def test_prompt_language_custom(self, monkeypatch):
        """Test language prompt with custom input."""
        inputs = iter(["en"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_language(interactive=True)
        assert result == "en"

    def test_prompt_language_default(self, monkeypatch):
        """Test language prompt with default (empty input)."""
        inputs = iter([""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_language(interactive=True)
        assert result == "ja"

    def test_get_all_config_interactive_non_interactive(self):
        """Test get_all_config_interactive in non-interactive mode."""
        config = get_all_config_interactive(interactive=False)

        assert config["tool"] == "sphinx"
        assert config["version"] == "0.1.0"
        assert config["language"] == "ja"
        assert isinstance(config["project_name"], str)
        assert isinstance(config["author"], str)

    def test_get_all_config_interactive_with_preset_tool(self):
        """Test get_all_config_interactive with pre-selected tool."""
        config = get_all_config_interactive(tool="mkdocs", interactive=False)

        assert config["tool"] == "mkdocs"
        assert config["version"] == "0.1.0"

    def test_prompt_project_name_with_invalid_characters(self, monkeypatch):
        """Test project name validation with invalid characters."""
        # Simulate invalid input (with slash), then valid input
        inputs = iter(["invalid/name", "valid-name"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = prompt_project_name(interactive=True)
        assert result == "valid-name"

    def test_confirm_overwrite_invalid_then_valid(self, monkeypatch):
        """Test overwrite confirmation with invalid input then valid."""
        inputs = iter(["maybe", "yes"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        result = confirm_overwrite(Path("/test/file.md"), interactive=True)
        assert result is True
