"""
Centralized logging setup for MISP installation
"""

import sys
import logging
from pathlib import Path
from lib.colors import Colors


def setup_logging() -> logging.Logger:
    """Setup comprehensive logging with centralized JSON logger - JSON ONLY

    NOTE: /opt/misp/logs must already exist before calling this function.
    The directory is created in main() before any phases run.

    Returns:
        Configured logger instance
    """

    # Import the centralized MISP logger
    script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(script_dir / "scripts"))
    from misp_logger import get_logger as get_misp_logger

    # CRITICAL: /opt/misp/logs MUST exist - NO FALLBACK
    # This directory is created in Phase 1 (before any logging starts)
    log_dir = Path("/opt/misp/logs")

    if not log_dir.exists():
        print(f"❌ FATAL: /opt/misp/logs directory does not exist")
        print(f"   Logging REQUIRES /opt/misp/logs - NO FALLBACK")
        print(f"   This is a bug - the directory should be created before logging starts")
        sys.exit(1)

    # Use centralized JSON logger for file logging
    # This creates JSON logs in /opt/misp/logs/misp-install-{timestamp}.log
    misp_logger = get_misp_logger('misp-install', 'misp:install')

    # Get the underlying Python logger for compatibility
    logger = misp_logger.logger

    # The centralized logger already has file + console handlers
    # Just inform user where logs are stored
    logger.info(Colors.info(f"📝 JSON Logs: /opt/misp/logs/misp-install-{{timestamp}}.log"))

    return logger


def get_logger(name: str, sourcetype: str = 'misp:general') -> logging.Logger:
    """Get a logger instance with centralized JSON logging

    Args:
        name: Logger name (used in log file naming)
        sourcetype: Sourcetype for SIEM integration (default: misp:general)

    Returns:
        Configured logger instance
    """
    # Import the centralized MISP logger
    script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(script_dir / "scripts"))
    from misp_logger import get_logger as get_misp_logger

    misp_logger = get_misp_logger(name, sourcetype)
    return misp_logger.logger
