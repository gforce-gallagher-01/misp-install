"""
Configuration management for MISP installation
"""

import json
import os
import socket
import subprocess
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def get_system_hostname() -> str:
    """
    Get the system's fully qualified domain name (FQDN).

    Tries multiple methods to get the best hostname:
    1. hostname -f (FQDN)
    2. socket.getfqdn()
    3. socket.gethostname()

    Returns:
        str: System hostname/FQDN
    """
    try:
        # Try hostname -f command first (most reliable on Linux)
        result = subprocess.run(['hostname', '-f'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            hostname = result.stdout.strip()
            # Only return if it's a valid FQDN (contains a dot)
            if '.' in hostname:
                return hostname
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    try:
        # Try Python's socket.getfqdn()
        hostname = socket.getfqdn()
        if hostname and hostname != 'localhost' and '.' in hostname:
            return hostname
    except Exception:
        pass

    try:
        # Fallback to socket.gethostname()
        hostname = socket.gethostname()
        if hostname and hostname != 'localhost':
            return hostname
    except Exception:
        pass

    # Ultimate fallback
    return "misp.local"


class Environment(Enum):
    """Installation environment types"""
    DEV = "development"
    STAGING = "staging"
    PROD = "production"


@dataclass
class SystemRequirements:
    """System requirements for MISP installation"""
    min_disk_gb: int = 20
    min_ram_gb: int = 4
    min_cpu_cores: int = 2
    required_ports: list = None

    def __post_init__(self):
        if self.required_ports is None:
            self.required_ports = [80, 443]


@dataclass
class PerformanceTuning:
    """Performance tuning parameters"""
    php_memory_limit: str = "2048M"
    php_max_execution_time: int = 300
    workers: int = 0  # 0 = auto-calculate

    def __post_init__(self):
        if self.workers == 0:
            # Auto-calculate based on CPU cores
            self.workers = max(2, os.cpu_count() or 2)


@dataclass
class MISPConfig:
    """MISP installation configuration"""
    server_ip: str = "192.168.20.193"
    domain: str = ""  # Auto-detected if empty
    admin_email: str = "admin@yourcompany.com"
    admin_org: str = "tKQB Enterprises"
    admin_password: str = ""
    mysql_password: str = ""
    gpg_passphrase: str = ""
    encryption_key: str = ""
    environment: str = Environment.PROD.value
    base_url: str = ""
    performance: Optional[Dict] = None

    def __post_init__(self):
        # Auto-detect hostname if not specified
        if not self.domain:
            self.domain = get_system_hostname()

        if not self.base_url:
            self.base_url = f"https://{self.domain}"

        if self.performance is None:
            self.performance = asdict(PerformanceTuning())

    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'MISPConfig':
        """Create config from dictionary"""
        # Filter out comment fields (keys starting with _)
        filtered_data = {k: v for k, v in data.items() if not k.startswith('_')}
        return cls(**filtered_data)

    @classmethod
    def from_yaml(cls, filepath: str) -> 'MISPConfig':
        """Load config from YAML file"""
        if not HAS_YAML:
            raise ImportError("PyYAML required for YAML config files")
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, filepath: str) -> 'MISPConfig':
        """Load config from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_yaml(self, filepath: str):
        """Save config to YAML file"""
        if not HAS_YAML:
            self.save_json(filepath.replace('.yaml', '.json'))
            return
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    def save_json(self, filepath: str):
        """Save config to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
