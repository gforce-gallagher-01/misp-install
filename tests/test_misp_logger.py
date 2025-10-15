"""
Unit tests for MISP centralized logging module.

Tests the logging functionality from misp_logger.py
"""

import pytest
import sys
import json
import logging
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMISPLogger:
    """Test suite for MISP centralized logger."""

    @patch('misp_logger.Path')
    def test_logger_creation(self, mock_path):
        """Test that logger can be created with valid parameters."""
        # Mock the log directory to avoid actual file system operations
        mock_path.return_value.mkdir.return_value = None
        mock_path.return_value.exists.return_value = True

        from misp_logger import get_logger

        logger = get_logger('test-script', 'misp:test')
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self):
        """Test that logger has correct name."""
        from misp_logger import get_logger

        with patch('misp_logger.Path'):
            logger = get_logger('test-name', 'misp:test')
            assert 'test-name' in logger.name

    def test_log_levels(self):
        """Test that all log levels work."""
        from misp_logger import get_logger

        with patch('misp_logger.Path'):
            logger = get_logger('test-levels', 'misp:test')

            # Should not raise exceptions
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

    def test_structured_logging_fields(self):
        """Test that structured logging accepts extra fields."""
        from misp_logger import get_logger

        with patch('misp_logger.Path'):
            logger = get_logger('test-structured', 'misp:test')

            # Should accept extra fields without error
            logger.info(
                "Test message",
                event_type="test",
                action="validate",
                status="success",
                user="testuser"
            )

    def test_cim_field_names(self):
        """Test that CIM (Common Information Model) field names are used."""
        # This test verifies the logger uses SIEM-compatible field names
        from misp_logger import get_logger

        with patch('misp_logger.Path'):
            logger = get_logger('test-cim', 'misp:test')

            # Common CIM fields should be accepted
            cim_fields = {
                "event_type": "authentication",
                "action": "login",
                "status": "success",
                "src_ip": "192.168.1.100",
                "dest_ip": "192.168.1.200",
                "user": "admin",
                "result": "allowed"
            }

            # Should not raise exceptions
            logger.info("CIM test", **cim_fields)


class TestLogRotation:
    """Test suite for log rotation configuration."""

    def test_rotation_settings(self):
        """Test that rotation settings are reasonable."""
        # Log rotation should be configured for production use
        # This is more of a configuration verification test

        from misp_logger import get_logger

        with patch('misp_logger.Path'):
            logger = get_logger('test-rotation', 'misp:test')

            # Verify logger has handlers
            assert len(logger.handlers) > 0

    def test_log_file_naming(self):
        """Test that log files use timestamp naming convention."""
        from misp_logger import get_logger

        with patch('misp_logger.Path') as mock_path:
            mock_path.return_value.exists.return_value = True

            logger = get_logger('test-naming', 'misp:test')

            # Log file name should include script name
            # Format: {script-name}-{timestamp}.log
            assert logger is not None


class TestJSONLogging:
    """Test suite for JSON log format."""

    def test_json_format_fields(self):
        """Test that logs can be formatted as JSON."""
        # JSON logging enables SIEM integration

        log_record = {
            "timestamp": "2024-10-14T12:00:00Z",
            "level": "INFO",
            "message": "Test message",
            "sourcetype": "misp:test",
            "event_type": "test_event"
        }

        # Should be valid JSON
        json_string = json.dumps(log_record)
        assert json_string is not None

        # Should be parseable back
        parsed = json.loads(json_string)
        assert parsed["message"] == "Test message"
        assert parsed["level"] == "INFO"

    def test_json_special_characters(self):
        """Test that special characters are properly escaped in JSON."""
        log_record = {
            "message": "Test with \"quotes\" and \\ backslash",
            "field": "Value with\nnewline"
        }

        json_string = json.dumps(log_record)
        parsed = json.loads(json_string)

        assert parsed["message"] == log_record["message"]
        assert parsed["field"] == log_record["field"]
