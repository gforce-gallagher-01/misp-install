#!/usr/bin/env python3
"""
MISP Centralized Logging Module
tKQB Enterprises - Standardized JSON Logging with Rotation
Version: 1.0

Provides consistent JSON logging across all MISP management scripts using
Common Information Model (CIM)-inspired field names for better log analysis.

Features:
- JSON-formatted structured logging
- Automatic log rotation (5 files, 20MB each)
- CIM-inspired field names for SIEM compatibility
- Centralized log directory (/opt/misp/logs)
- Console output with color coding
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import socket
import getpass

# ==========================================
# Configuration
# ==========================================

class LogConfig:
    """Centralized logging configuration"""
    LOG_DIR = Path("/opt/misp/logs")
    MAX_BYTES = 20 * 1024 * 1024  # 20MB per file
    BACKUP_COUNT = 5  # Keep 5 rotated files
    LOG_FORMAT_JSON = True
    LOG_FORMAT_CONSOLE = True  # Color-coded console output


# ==========================================
# CIM-Inspired Field Schema
# ==========================================

class CIMFields:
    """
    Common Information Model inspired field names for SIEM compatibility.
    Based on Splunk CIM and industry standards.
    """

    # Core fields (always present)
    TIMESTAMP = "time"           # ISO 8601 timestamp
    HOST = "host"                # Hostname
    SOURCE = "source"            # Source script/module
    SOURCETYPE = "sourcetype"    # Log source type
    SEVERITY = "severity"        # Log severity level
    MESSAGE = "message"          # Human-readable message

    # Event classification
    EVENT_ID = "event_id"        # Unique event identifier
    EVENT_TYPE = "event_type"    # Type of event (backup, restore, install, etc.)
    ACTION = "action"            # Action performed
    STATUS = "status"            # Status (success, failure, warning, info)

    # Actor information
    USER = "user"                # Username

    # System information
    PROCESS = "process"          # Process name
    PROCESS_ID = "pid"           # Process ID

    # Performance metrics
    DURATION = "duration"        # Duration in seconds
    BYTES = "bytes"              # Bytes processed
    COUNT = "count"              # Count of items

    # Error information
    ERROR_CODE = "error_code"    # Error code
    ERROR_MESSAGE = "error_message"  # Error message
    EXCEPTION = "exception"      # Exception details

    # Additional context
    PHASE = "phase"              # Installation/operation phase
    COMPONENT = "component"      # Component being operated on
    FILE_PATH = "file_path"      # File path
    FILE_SIZE = "file_size"      # File size in bytes

    # Docker specific
    CONTAINER = "container"      # Container name
    IMAGE = "image"              # Docker image

    # Backup specific
    BACKUP_TYPE = "backup_type"  # full, incremental
    BACKUP_NAME = "backup_name"  # Backup filename


# ==========================================
# Color Output for Console
# ==========================================

class Colors:
    """ANSI color codes for console output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

    SEVERITY_COLORS = {
        'CRITICAL': RED,
        'ERROR': RED,
        'WARNING': YELLOW,
        'INFO': BLUE,
        'SUCCESS': GREEN,
        'DEBUG': CYAN,
    }


# ==========================================
# JSON Formatter
# ==========================================

class CIMJSONFormatter(logging.Formatter):
    """Custom JSON formatter with CIM field names"""

    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with CIM fields"""

        # Base CIM fields
        log_entry = {
            CIMFields.TIMESTAMP: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            CIMFields.HOST: self.hostname,
            CIMFields.USER: self.username,
            CIMFields.SOURCE: record.name,
            CIMFields.SOURCETYPE: getattr(record, 'sourcetype', 'misp:script'),
            CIMFields.SEVERITY: record.levelname,
            CIMFields.MESSAGE: record.getMessage(),
            CIMFields.PROCESS: record.processName,
            CIMFields.PROCESS_ID: record.process,
        }

        # Add custom fields from extra parameter
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry[CIMFields.EXCEPTION] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


# ==========================================
# Console Formatter
# ==========================================

class ColoredConsoleFormatter(logging.Formatter):
    """Colored console output formatter"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console"""

        severity = record.levelname
        color = Colors.SEVERITY_COLORS.get(severity, Colors.NC)

        # Get message
        message = record.getMessage()

        # Add custom fields if present
        if hasattr(record, 'extra_fields'):
            extras = record.extra_fields
            if CIMFields.EVENT_TYPE in extras:
                message = f"[{extras[CIMFields.EVENT_TYPE]}] {message}"
            if CIMFields.COMPONENT in extras:
                message = f"{message} (component={extras[CIMFields.COMPONENT]})"

        return f"{color}[{severity}] {message}{Colors.NC}"


# ==========================================
# MISP Logger
# ==========================================

class MISPLogger:
    """
    Centralized logger for MISP management scripts.

    Usage:
        logger = MISPLogger(script_name='backup-misp', sourcetype='misp:backup')
        logger.info("Starting backup", event_type="backup", action="start")
        logger.success("Backup completed", backup_name="misp-backup-20250112.tar.gz")
        logger.error("Backup failed", error_message="Permission denied")
    """

    def __init__(self, script_name: str, sourcetype: str = 'misp:script',
                 log_to_file: bool = True, log_to_console: bool = True):
        """
        Initialize MISP logger.

        Args:
            script_name: Name of the script (e.g., 'backup-misp')
            sourcetype: Source type for SIEM (e.g., 'misp:backup')
            log_to_file: Enable file logging
            log_to_console: Enable console logging
        """
        self.script_name = script_name
        self.sourcetype = sourcetype

        # Create logger
        self.logger = logging.getLogger(script_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Setup file logging
        if log_to_file:
            self._setup_file_handler()

        # Setup console logging
        if log_to_console:
            self._setup_console_handler()

    def _setup_file_handler(self):
        """Setup rotating file handler with JSON formatting - with graceful fallback"""

        log_dir = LogConfig.LOG_DIR

        # Try to create log directory
        try:
            # First try normal mkdir
            log_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # If permission denied, try with sudo
            try:
                import subprocess
                subprocess.run(['sudo', 'mkdir', '-p', str(log_dir)],
                             check=True, capture_output=True)
                # Try to set ownership to current user
                import pwd
                username = pwd.getpwuid(os.getuid()).pw_name
                subprocess.run(['sudo', 'chown', '-R', f'{username}:{username}', str(log_dir)],
                             check=False, capture_output=True)
                subprocess.run(['sudo', 'chmod', '775', str(log_dir)],
                             check=False, capture_output=True)
            except Exception as e:
                # If sudo also fails, print warning and skip file logging
                print(f"⚠️  Could not create log directory {log_dir}: {e}")
                print(f"⚠️  File logging disabled - console only")
                return

        # Set appropriate permissions (if needed - ACLs may already handle this)
        try:
            os.chmod(log_dir, 0o755)
        except PermissionError:
            # Permission denied is expected when ACLs are configured and directory is owned by www-data
            # ACLs provide the necessary permissions, so this is not an error
            pass
        except Exception as e:
            # Log only unexpected errors
            print(f"⚠️  Unexpected error setting permissions on {log_dir}: {e}")

        # Create rotating file handler with timestamp in filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{self.script_name}-{timestamp}.log"

        try:
            # Create file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=LogConfig.MAX_BYTES,
                backupCount=LogConfig.BACKUP_COUNT,
                encoding='utf-8'
            )

            # Set JSON formatter - ALWAYS JSON, NEVER plain text
            file_handler.setFormatter(CIMJSONFormatter())
            file_handler.setLevel(logging.DEBUG)

            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️  Could not create log file {log_file}: {e}")
            print(f"⚠️  File logging disabled - console only")

    def _setup_console_handler(self):
        """Setup console handler with colored output"""

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredConsoleFormatter())
        console_handler.setLevel(logging.INFO)

        self.logger.addHandler(console_handler)

    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with extra fields"""

        # Create extra fields dict
        extra_fields = {
            CIMFields.EVENT_ID: kwargs.pop('event_id', None),
            CIMFields.EVENT_TYPE: kwargs.pop('event_type', None),
            CIMFields.ACTION: kwargs.pop('action', None),
            CIMFields.STATUS: kwargs.pop('status', None),
            CIMFields.COMPONENT: kwargs.pop('component', None),
            CIMFields.PHASE: kwargs.pop('phase', None),
            CIMFields.DURATION: kwargs.pop('duration', None),
            CIMFields.BYTES: kwargs.pop('bytes', None),
            CIMFields.COUNT: kwargs.pop('count', None),
            CIMFields.ERROR_CODE: kwargs.pop('error_code', None),
            CIMFields.ERROR_MESSAGE: kwargs.pop('error_message', None),
            CIMFields.FILE_PATH: kwargs.pop('file_path', None),
            CIMFields.FILE_SIZE: kwargs.pop('file_size', None),
            CIMFields.CONTAINER: kwargs.pop('container', None),
            CIMFields.IMAGE: kwargs.pop('image', None),
            CIMFields.BACKUP_TYPE: kwargs.pop('backup_type', None),
            CIMFields.BACKUP_NAME: kwargs.pop('backup_name', None),
        }

        # Remove None values
        extra_fields = {k: v for k, v in extra_fields.items() if v is not None}

        # Add any remaining kwargs
        extra_fields.update(kwargs)

        # Add sourcetype
        extra = {
            'sourcetype': self.sourcetype,
            'extra_fields': extra_fields
        }

        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, status='debug', **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, status='info', **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message"""
        # Map SUCCESS to INFO level but with success status
        self._log(logging.INFO, message, status='success', **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, status='warning', **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, status='error', **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, status='critical', **kwargs)


# ==========================================
# Convenience Functions
# ==========================================

def get_logger(script_name: str, sourcetype: str = None, **kwargs) -> MISPLogger:
    """
    Convenience function to get a configured MISP logger.

    Args:
        script_name: Name of the script
        sourcetype: Source type (defaults to 'misp:{script_name}')
        **kwargs: Additional arguments for MISPLogger

    Returns:
        Configured MISPLogger instance
    """
    if sourcetype is None:
        sourcetype = f"misp:{script_name.replace('-', '_').replace('.py', '')}"

    return MISPLogger(script_name=script_name, sourcetype=sourcetype, **kwargs)


# ==========================================
# Testing
# ==========================================

if __name__ == "__main__":
    """Test the logging module"""

    print("Testing MISP Logger...")
    print()

    # Create test logger
    logger = get_logger('test-script', 'misp:test')

    # Test various log levels
    logger.info("Starting test operation", event_type="test", action="start")
    logger.debug("Debug information", component="test_module")
    logger.success("Operation completed successfully", duration=1.5, count=100)
    logger.warning("Warning message", component="backup")
    logger.error("Error occurred", error_message="File not found", error_code="ENOENT")

    # Test with various CIM fields
    logger.info(
        "Backup started",
        event_type="backup",
        action="create",
        backup_type="full",
        backup_name="misp-backup-20250112.tar.gz",
        phase="backup_database"
    )

    logger.success(
        "Backup completed",
        event_type="backup",
        action="complete",
        backup_name="misp-backup-20250112.tar.gz",
        file_size=67700000,
        duration=45.2
    )

    print()
    print(f"Logs written to: {LogConfig.LOG_DIR}/test-script.log")
    print()

    # Show sample log entries
    log_file = LogConfig.LOG_DIR / "test-script.log"
    if log_file.exists():
        print("Sample JSON log entries:")
        print("=" * 80)
        with open(log_file, 'r') as f:
            for line in f.readlines()[-3:]:
                print(json.dumps(json.loads(line), indent=2))
                print("-" * 80)
