#!/usr/bin/env python3
"""
MISP Update & Upgrade Tool
tKQB Enterprises Edition
Version: 2.0 (with Centralized Logging)

Features:
- Automatic backup before upgrade
- Component version checking
- Rolling updates with health checks
- Database migration support
- Rollback capability
- Update verification
- Minimal downtime
- Full logging
"""

import os
import sys
import subprocess
import logging
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# Import centralized logger
from misp_logger import get_logger

# ==========================================
# Color Output
# ==========================================

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'
    
    @staticmethod
    def colored(text: str, color: str) -> str:
        return f"{color}{text}{Colors.NC}"
    
    @classmethod
    def error(cls, text: str) -> str:
        return cls.colored(f"❌ {text}", cls.RED)
    
    @classmethod
    def success(cls, text: str) -> str:
        return cls.colored(f"✓ {text}", cls.GREEN)
    
    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colored(f"⚠ {text}", cls.YELLOW)
    
    @classmethod
    def info(cls, text: str) -> str:
        return cls.colored(text, cls.CYAN)

# ==========================================
# Logging Setup
# ==========================================

def setup_logging() -> logging.Logger:
    """Setup centralized logging"""
    misp_logger = get_logger('misp-update', 'misp:update')
    logger = misp_logger.logger
    logger.info(f"📝 JSON Logs: /opt/misp/logs/misp-update-{{timestamp}}.log")
    return logger

logger = setup_logging()

