#!/usr/bin/env python3
"""
MISP Automated Backup Script
tKQB Enterprises Edition
Version: 2.0 (with Centralized Logging)

Backup Strategy:
- Sunday: Full backup (keep 8 weeks)
- Monday-Saturday: Incremental backup (deleted after next Sunday)
- Automatic rotation and cleanup
- Email notifications (optional)
- Verification checks

Usage:
  python3 misp-backup-cron.py [--full] [--dry-run] [--notify]
  
Cron Setup:
  # Run nightly at 2 AM
  0 2 * * * /usr/bin/python3 /opt/misp/scripts/misp-backup-cron.py >> /var/log/misp-install/backup-cron.log 2>&1
"""

import os
import sys
import subprocess
import logging
import json
import shutil
import fcntl
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# Import centralized logger
from misp_logger import get_logger

# Import centralized Colors class
from lib.colors import Colors

# ==========================================
# Configuration
# ==========================================

class BackupConfig:
    """Centralized backup configuration"""

    # Directories
    MISP_DIR = Path("/opt/misp")
    BACKUP_BASE_DIR = Path.home() / "misp-backups"
    FULL_BACKUP_DIR = BACKUP_BASE_DIR / "full"
    INCREMENTAL_BACKUP_DIR = BACKUP_BASE_DIR / "incremental"
    LOG_DIR = Path("/var/log/misp-install")

    # Retention
    FULL_BACKUP_WEEKS = 8  # Keep 8 weeks of Sunday backups

    # Lock file
    LOCK_FILE = Path.home() / ".misp-install" / "misp-backup.lock"
    
    # Email notifications (set to None to disable)
    EMAIL_ENABLED = False
    EMAIL_FROM = "misp-backup@example.com"
    EMAIL_TO = ["youremail@yourdomain.com"]
    SMTP_SERVER = "localhost"
    SMTP_PORT = 25
    SMTP_USER = None  # Set if authentication required
    SMTP_PASSWORD = None
    
    # What to backup
    FILES_TO_BACKUP = [
        '.env',
        'PASSWORDS.txt',
        'docker-compose.yml',
        'docker-compose.override.yml'
    ]
    
    DIRS_TO_BACKUP = [
        'ssl'
    ]

# ==========================================
# Logging Setup
# ==========================================

def setup_logging() -> logging.Logger:
    """Setup centralized logging"""
    misp_logger = get_logger('misp-backup-cron', 'misp:backup_cron')
    logger = misp_logger.logger
    logger.info(f"📝 JSON Logs: /opt/misp/logs/misp-backup-cron-{{timestamp}}.log")
    return logger

logger = setup_logging()

