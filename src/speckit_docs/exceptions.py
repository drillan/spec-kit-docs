"""Custom exceptions for speckit-docs."""

from pathlib import Path


class SpecKitDocsError(Exception):
    """Base exception class for speckit-docs.

    C002-compliant error messages with file path, error type, and suggested action.

    Attributes:
        message: Error message describing what went wrong
        suggestion: Helpful suggestion for resolving the error
        file_path: Optional file path where the error occurred
        error_type: Optional error type classification
    """

    def __init__(
        self,
        message: str,
        suggestion: str,
        file_path: Path | str | None = None,
        error_type: str | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong
            suggestion: Helpful suggestion for resolving the error
            file_path: Optional file path where the error occurred (C002)
            error_type: Optional error type classification (C002)
        """
        self.message = message
        self.suggestion = suggestion
        self.file_path = Path(file_path) if isinstance(file_path, str) else file_path
        self.error_type = error_type

        # Format error message (C002-compliant)
        parts = []

        # Add error type if provided
        if error_type:
            parts.append(f"❌ Error Type: {error_type}")

        # Add file path if provided
        if self.file_path:
            parts.append(f"📁 File: {self.file_path}")

        # Add main message
        parts.append(f"\n{message}")

        # Add suggestion
        parts.append(f"\n💡 Suggestion: {suggestion}")

        super().__init__("\n".join(parts))
