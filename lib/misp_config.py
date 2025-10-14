#!/usr/bin/env python3
"""
MISP Configuration Constants
Version: 1.0
Date: 2025-10-14

Purpose:
    Centralized configuration constants for MISP installation and management.
    Eliminates duplicate path definitions across scripts.

Usage:
    from lib.misp_config import MISPConfig

    config = MISPConfig()
    print(config.MISP_DIR)          # /opt/misp
    print(config.LOGS_DIR)          # /opt/misp/logs
    print(config.ENV_FILE)          # /opt/misp/.env
    print(config.PASSWORDS_FILE)    # /opt/misp/PASSWORDS.txt
"""

from pathlib import Path
from typing import Optional


class MISPConfig:
    """Centralized MISP configuration paths and constants"""

    def __init__(self, misp_dir: Optional[str] = None):
        """Initialize MISP configuration

        Args:
            misp_dir: Custom MISP directory path (defaults to /opt/misp)
        """
        # Base MISP directory
        self.MISP_DIR = Path(misp_dir) if misp_dir else Path("/opt/misp")

        # Common file paths
        self.ENV_FILE = self.MISP_DIR / ".env"
        self.PASSWORDS_FILE = self.MISP_DIR / "PASSWORDS.txt"
        self.DOCKER_COMPOSE_FILE = self.MISP_DIR / "docker-compose.yml"

        # Directory paths
        self.LOGS_DIR = self.MISP_DIR / "logs"
        self.SSL_DIR = self.MISP_DIR / "ssl"
        self.DATA_DIR = self.MISP_DIR / "data"

        # Default MISP URL (can be overridden)
        self.DEFAULT_MISP_URL = "https://misp-test.lan"

        # Common constants
        self.MISP_SYSTEM_USER = "misp-owner"  # v5.4 dedicated user

    def exists(self) -> bool:
        """Check if MISP directory exists"""
        return self.MISP_DIR.exists()

    def is_installed(self) -> bool:
        """Check if MISP appears to be installed"""
        return (self.MISP_DIR.exists() and
                self.DOCKER_COMPOSE_FILE.exists() and
                self.ENV_FILE.exists())

    def __repr__(self) -> str:
        """String representation"""
        return f"MISPConfig(MISP_DIR={self.MISP_DIR})"


# Global default instance for convenience
DEFAULT_CONFIG = MISPConfig()
