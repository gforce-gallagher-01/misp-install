"""
Configuration management for MISP installation
"""

import json
import os
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


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
    domain: str = "misp-dev.lan"
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
