"""
Configuration management for MISP installation
"""

import json
import os
import socket
import subprocess
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, Optional, List

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
    exclude_features: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Auto-detect hostname if not specified
        if not self.domain:
            self.domain = get_system_hostname()

        if not self.base_url:
            self.base_url = f"https://{self.domain}"

        if self.performance is None:
            self.performance = asdict(PerformanceTuning())

        # Initialize exclusion list if None
        if self.exclude_features is None:
            self.exclude_features = []

    def is_feature_excluded(self, feature_id: str) -> bool:
        """Check if a feature should be excluded

        Args:
            feature_id: Feature identifier (e.g., 'api-key', 'threat-feeds')

        Returns:
            True if feature is excluded, False otherwise
        """
        from lib.features import FEATURE_CATEGORIES, validate_feature_id, validate_category

        # Check direct feature exclusion
        if feature_id in self.exclude_features:
            return True

        # Check category exclusion (format: "category:category-name")
        feature_category = FEATURE_CATEGORIES.get(feature_id)
        if feature_category:
            category_exclusion = f"category:{feature_category}"
            if category_exclusion in self.exclude_features:
                return True

        return False

    def get_excluded_features(self) -> List[str]:
        """Get list of excluded features with validation

        Returns:
            List of excluded feature IDs with warnings for invalid entries
        """
        from lib.features import validate_feature_id, validate_category, get_category_features

        excluded = []
        for entry in self.exclude_features:
            if entry.startswith('category:'):
                # Category exclusion
                category = entry.split(':', 1)[1]
                if validate_category(category):
                    excluded.extend(get_category_features(category))
                else:
                    print(f"⚠️  Warning: Invalid category '{category}' in exclusion list")
            else:
                # Individual feature exclusion
                if validate_feature_id(entry):
                    excluded.append(entry)
                else:
                    print(f"⚠️  Warning: Invalid feature '{entry}' in exclusion list")

        return list(set(excluded))  # Remove duplicates

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
