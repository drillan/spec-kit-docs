"""Unit tests for logging utilities (T082 - Coverage improvement)."""

import logging

import pytest

from speckit_docs.utils.logging import (
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    setup_logging,
)


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_default(self):
        """Test default logging setup (INFO level)."""
        setup_logging()

        # Verify root logger level is INFO
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_verbose(self):
        """Test verbose logging setup (DEBUG level)."""
        setup_logging(verbose=True)

        # Verify root logger level is DEBUG
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_quiet(self):
        """Test quiet logging setup (ERROR level only)."""
        setup_logging(quiet=True)

        # Verify root logger level is ERROR
        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR

    def test_setup_logging_verbose_and_quiet_error(self):
        """Test that verbose and quiet cannot both be True."""
        with pytest.raises(ValueError, match="Cannot set both verbose and quiet flags"):
            setup_logging(verbose=True, quiet=True)

    def test_setup_logging_suppresses_third_party_loggers(self):
        """Test that third-party library loggers are suppressed."""
        setup_logging()

        # Verify third-party loggers are set to WARNING
        assert logging.getLogger("urllib3").level == logging.WARNING
        assert logging.getLogger("git").level == logging.WARNING
        assert logging.getLogger("jinja2").level == logging.WARNING


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_different_names(self):
        """Test that different names return different loggers."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name != logger2.name
        assert logger1.name == "module1"
        assert logger2.name == "module2"


class TestLogInfo:
    """Tests for log_info function."""

    def test_log_info_simple_message(self, capsys):
        """Test logging simple INFO message."""
        setup_logging()  # Ensure INFO level
        log_info("Test info message")

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Test info message" in captured.out

    def test_log_info_with_kwargs(self, capsys):
        """Test logging INFO message with additional context."""
        setup_logging()
        log_info("Test message", user="alice", count=42)

        # Verify message and context appear in stdout
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert ("user" in captured.out or "alice" in captured.out)


class TestLogDebug:
    """Tests for log_debug function."""

    def test_log_debug_simple_message(self, capsys):
        """Test logging simple DEBUG message."""
        setup_logging(verbose=True)  # Enable DEBUG level
        log_debug("Test debug message")

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Test debug message" in captured.out

    def test_log_debug_with_kwargs(self, capsys):
        """Test logging DEBUG message with additional context."""
        setup_logging(verbose=True)
        log_debug("Debug message", file="test.py", line=10)

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Debug message" in captured.out


class TestLogError:
    """Tests for log_error function."""

    def test_log_error_simple_message(self, capsys):
        """Test logging simple ERROR message."""
        setup_logging()
        log_error("Test error message")

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Test error message" in captured.out

    def test_log_error_with_kwargs(self, capsys):
        """Test logging ERROR message with additional context."""
        setup_logging()
        log_error("Error occurred", code=500, reason="Internal error")

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Error occurred" in captured.out


class TestLogWarning:
    """Tests for log_warning function."""

    def test_log_warning_simple_message(self, capsys):
        """Test logging simple WARNING message."""
        setup_logging()
        log_warning("Test warning message")

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Test warning message" in captured.out

    def test_log_warning_with_kwargs(self, capsys):
        """Test logging WARNING message with additional context."""
        setup_logging()
        log_warning("Warning message", resource="memory", usage="90%")

        # Verify message appears in stdout
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
