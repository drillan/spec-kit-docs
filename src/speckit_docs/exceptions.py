"""Custom exceptions for speckit-docs."""


class SpecKitDocsError(Exception):
    """Base exception class for speckit-docs.

    Attributes:
        message: Error message describing what went wrong
        suggestion: Helpful suggestion for resolving the error
    """

    def __init__(self, message: str, suggestion: str) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong
            suggestion: Helpful suggestion for resolving the error
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"{message}\n\n💡 Suggestion: {suggestion}")
