"""Unit tests for speckit_docs.exceptions module."""

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
