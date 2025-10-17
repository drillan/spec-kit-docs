"""Unit tests for speckit_docs.exceptions module."""

from pathlib import Path

import pytest

from speckit_docs.exceptions import SpecKitDocsError


def test_speckit_docs_error_message():
    """Test that SpecKitDocsError stores message and suggestion correctly."""
    error = SpecKitDocsError("Test error", "Test suggestion")
    assert error.message == "Test error"
    assert error.suggestion == "Test suggestion"
    assert "Test error" in str(error)
    assert "Test suggestion" in str(error)


def test_speckit_docs_error_string_representation():
    """Test that SpecKitDocsError produces correct string representation."""
    error = SpecKitDocsError("Connection failed", "Check your network settings")
    error_str = str(error)

    assert "Connection failed" in error_str
    assert "Check your network settings" in error_str
    assert "💡 Suggestion:" in error_str


def test_speckit_docs_error_is_exception():
    """Test that SpecKitDocsError is an Exception subclass."""
    error = SpecKitDocsError("Test", "Test")
    assert isinstance(error, Exception)


def test_speckit_docs_error_can_be_raised():
    """Test that SpecKitDocsError can be raised and caught."""
    with pytest.raises(SpecKitDocsError) as exc_info:
        raise SpecKitDocsError("Something went wrong", "Try again")

    assert exc_info.value.message == "Something went wrong"
    assert exc_info.value.suggestion == "Try again"


def test_speckit_docs_error_with_file_path():
    """Test C002-compliant error with file path (T078)."""
    test_file = Path("/path/to/spec.md")
    error = SpecKitDocsError(
        message="File not found",
        suggestion="Create the file in the specs directory",
        file_path=test_file,
    )

    assert error.file_path == test_file
    error_str = str(error)

    # Verify C002 compliance: file path included
    assert "📁 File:" in error_str
    assert str(test_file) in error_str
    assert "File not found" in error_str
    assert "💡 Suggestion:" in error_str


def test_speckit_docs_error_with_error_type():
    """Test C002-compliant error with error type (T078)."""
    error = SpecKitDocsError(
        message="Invalid configuration format",
        suggestion="Check the YAML syntax",
        error_type="Configuration Error",
    )

    assert error.error_type == "Configuration Error"
    error_str = str(error)

    # Verify C002 compliance: error type included
    assert "❌ Error Type:" in error_str
    assert "Configuration Error" in error_str
    assert "Invalid configuration format" in error_str


def test_speckit_docs_error_with_all_fields():
    """Test C002-compliant error with all fields (T078)."""
    test_file = Path("/specs/001-feature/spec.md")
    error = SpecKitDocsError(
        message="Missing required section 'User Stories'",
        suggestion="Add a User Stories section to your spec.md",
        file_path=test_file,
        error_type="Missing Content",
    )

    assert error.file_path == test_file
    assert error.error_type == "Missing Content"
    error_str = str(error)

    # Verify C002 compliance: all fields included
    assert "❌ Error Type: Missing Content" in error_str
    assert f"📁 File: {test_file}" in error_str
    assert "Missing required section 'User Stories'" in error_str
    assert "💡 Suggestion: Add a User Stories section to your spec.md" in error_str


def test_speckit_docs_error_with_string_file_path():
    """Test that string file paths are converted to Path objects."""
    error = SpecKitDocsError(
        message="Test error",
        suggestion="Test suggestion",
        file_path="/path/to/file.md",
    )

    assert isinstance(error.file_path, Path)
    assert str(error.file_path) == "/path/to/file.md"


def test_speckit_docs_error_backward_compatibility():
    """Test that old-style error creation still works (backward compatibility)."""
    # Old-style: only message and suggestion
    error = SpecKitDocsError("Old style error", "Old style suggestion")

    assert error.message == "Old style error"
    assert error.suggestion == "Old style suggestion"
    assert error.file_path is None
    assert error.error_type is None

    error_str = str(error)
    assert "Old style error" in error_str
    assert "💡 Suggestion: Old style suggestion" in error_str
    # Should not have C002 fields when not provided
    assert "❌ Error Type:" not in error_str
    assert "📁 File:" not in error_str
