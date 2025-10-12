#!/usr/bin/env python3
"""
MISP Complete Installation & Management Tool
GridSec - Enterprise Edition
Version: 5.2 (with Centralized JSON Logging)

Features:
- Pre-flight system checks
- Centralized JSON logging with CIM fields
- Backup before cleanup
- Config file support (YAML/JSON)
- Docker group activation
- Resume capability
- Error recovery with retry
- Password validation
- Separate test suite
- Post-install checklist
- Port conflict detection
- Multi-environment (dev/staging/prod)
- Performance tuning based on resources
- IMPROVED: Phase 10 with real-time progress monitoring
"""

import os
import sys
import subprocess
import logging
import json
import socket
import time
import getpass
import shutil
import hashlib
import re
import secrets
import string
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import pwd

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# Import centralized logger (from scripts directory)
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "scripts"))
try:
    from misp_logger import get_logger as get_misp_logger
    HAS_CENTRALIZED_LOGGER = True
except ImportError:
    HAS_CENTRALIZED_LOGGER = False
    print("⚠️  Centralized logger not available, using fallback logging")

# Try to import yaml, if not available use basic dict
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("⚠️  PyYAML not installed. YAML config support disabled.")
    print("   Install with: pip3 install pyyaml")

# ==========================================
# Configuration Classes
# ==========================================

class Environment(Enum):
    DEV = "development"
    STAGING = "staging"
    PROD = "production"

@dataclass
class SystemRequirements:
    min_disk_gb: int = 20
    min_ram_gb: int = 4
    min_cpu_cores: int = 2
    required_ports: List[int] = None
    
    def __post_init__(self):
        if self.required_ports is None:
            self.required_ports = [80, 443]

@dataclass
class PerformanceTuning:
    php_memory_limit: str = "2048M"
    php_max_execution_time: int = 300
    workers: int = 0  # 0 = auto-calculate
    
    def __post_init__(self):
        if self.workers == 0:
            # Auto-calculate based on CPU cores
            self.workers = max(2, os.cpu_count() or 2)

@dataclass
class MISPConfig:
    server_ip: str = "192.168.20.193"
    domain: str = "misp-dev.lan"
    admin_email: str = "cgallagher@gridsec.com"
    admin_org: str = "GridSec"
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
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MISPConfig':
        # Filter out comment fields (keys starting with _)
        filtered_data = {k: v for k, v in data.items() if not k.startswith('_')}
        return cls(**filtered_data)
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'MISPConfig':
        if not HAS_YAML:
            raise ImportError("PyYAML required for YAML config files")
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'MISPConfig':
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def save_yaml(self, filepath: str):
        if not HAS_YAML:
            self.save_json(filepath.replace('.yaml', '.json'))
            return
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
    
    def save_json(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

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
    """Setup comprehensive logging with centralized JSON logger"""
    if HAS_CENTRALIZED_LOGGER:
        # Use centralized JSON logger for file logging
        # This creates JSON logs in /opt/misp/logs/misp-install.log
        try:
            misp_logger = get_misp_logger('misp-install', 'misp:install')

            # Get the underlying Python logger for compatibility
            logger = misp_logger.logger

            # The centralized logger already has file + console handlers
            # Just inform user where logs are stored
            logger.info(Colors.info(f"📝 JSON Logs: /opt/misp/logs/misp-install.log"))

            return logger
        except Exception as e:
            print(f"⚠️  Could not initialize centralized logger: {e}")
            print("   Falling back to standard logging")

    # Fallback to standard Python logging if centralized logger unavailable
    log_dir = Path("/var/log/misp-install")
    try:
        log_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    except PermissionError:
        # Fallback to user's home directory if /var/log is not writable
        log_dir = Path.home() / ".misp-install" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"misp-install-{timestamp}.log"

    # Create logger
    logger = logging.getLogger('MISP-Installer')
    logger.setLevel(logging.DEBUG)

    # File handler (detailed)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(fh_formatter)

    # Console handler (user-friendly)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(message)s')
    ch.setFormatter(ch_formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(Colors.info(f"📝 Logging to: {log_file}"))

    return logger

# ==========================================
# System Checks
# ==========================================

class SystemChecker:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.requirements = SystemRequirements()
    
    def check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space"""
        try:
            stat = shutil.disk_usage(str(Path.home()))
            available_gb = stat.free // (1024**3)
            
            if available_gb < self.requirements.min_disk_gb:
                return False, f"Insufficient disk space: {available_gb}GB available, {self.requirements.min_disk_gb}GB required"
            
            return True, f"Disk space OK: {available_gb}GB available"
        except Exception as e:
            return False, f"Could not check disk space: {e}"
    
    def check_ram(self) -> Tuple[bool, str]:
        """Check available RAM"""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        total_kb = int(line.split()[1])
                        total_gb = total_kb // (1024**2)
                        
                        if total_gb < self.requirements.min_ram_gb:
                            return False, f"Insufficient RAM: {total_gb}GB available, {self.requirements.min_ram_gb}GB required"
                        
                        return True, f"RAM OK: {total_gb}GB available"
            
            return False, "Could not read memory info"
        except Exception as e:
            return False, f"Could not check RAM: {e}"
    
    def check_cpu(self) -> Tuple[bool, str]:
        """Check CPU cores"""
        try:
            cpu_count = os.cpu_count()
            
            if cpu_count < self.requirements.min_cpu_cores:
                return False, f"Insufficient CPU cores: {cpu_count} available, {self.requirements.min_cpu_cores} required"
            
            return True, f"CPU OK: {cpu_count} cores available"
        except Exception as e:
            return False, f"Could not check CPU: {e}"
    
    def check_ports(self) -> Tuple[bool, str]:
        """Check if required ports are available"""
        blocked_ports = []
        
        for port in self.requirements.required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
            except OSError as e:
                if e.errno == 98:  # EADDRINUSE
                    blocked_ports.append(port)
                elif e.errno == 13:  # EACCES - expected for privileged ports
                    continue
                else:
                    blocked_ports.append(port)
        
        if blocked_ports:
            return False, f"Ports already in use: {', '.join(map(str, blocked_ports))}"
        
        return True, "All required ports available (Docker will use privileged ports)"
    
    def check_docker(self) -> Tuple[bool, str]:
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(
                ['docker', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return True, "Docker not running (will be started during installation)"
            
            return True, "Docker is installed and running"
        except FileNotFoundError:
            return True, "Docker not installed (will be installed during Phase 1)"
        except subprocess.TimeoutExpired:
            return True, "Docker not responding (will be configured during installation)"
    
    def check_root(self) -> Tuple[bool, str]:
        """Check if running as root"""
        if os.geteuid() == 0:
            return False, "Script should not be run as root"
        return True, "Running as regular user"
    
    def run_all_checks(self) -> bool:
        """Run all system checks"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("PRE-FLIGHT SYSTEM CHECKS"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        checks = [
            ("User Check", self.check_root),
            ("Disk Space", self.check_disk_space),
            ("RAM", self.check_ram),
            ("CPU Cores", self.check_cpu),
            ("Port Availability", self.check_ports),
            ("Docker", self.check_docker),
        ]
        
        all_passed = True
        
        for name, check_func in checks:
            passed, message = check_func()
            
            if passed:
                self.logger.info(Colors.success(f"{name}: {message}"))
            else:
                self.logger.error(Colors.error(f"{name}: {message}"))
                all_passed = False
        
        return all_passed

# ==========================================
# Password Validation
# ==========================================

class PasswordValidator:
    MIN_LENGTH = 12
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Password must be at least {PasswordValidator.MIN_LENGTH} characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Generate a strong random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure it meets requirements
        while not PasswordValidator.validate(password)[0]:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        return password
    
    @staticmethod
    def get_password_interactive(prompt: str) -> str:
        """Get and validate password interactively"""
        while True:
            password = getpass.getpass(prompt)
            
            valid, message = PasswordValidator.validate(password)
            if not valid:
                print(Colors.error(message))
                continue
            
            password_confirm = getpass.getpass("Confirm password: ")
            
            if password != password_confirm:
                print(Colors.error("Passwords don't match!"))
                continue
            
            print(Colors.success("Password set"))
            return password

# ==========================================
# Backup Manager
# ==========================================

class BackupManager:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.backup_dir = Path.home() / "misp-backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    
    def create_backup(self, misp_dir: Path) -> Optional[Path]:
        """Create backup of existing MISP installation"""
        if not misp_dir.exists():
            self.logger.info("No existing installation to backup")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"misp-backup-{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        self.logger.info(Colors.info(f"Creating backup at: {backup_path}"))
        
        try:
            # Backup .env file
            if (misp_dir / ".env").exists():
                shutil.copy2(misp_dir / ".env", backup_path / ".env")
                self.logger.info("  ✓ Backed up .env")
            
            # Backup PASSWORDS.txt
            if (misp_dir / "PASSWORDS.txt").exists():
                shutil.copy2(misp_dir / "PASSWORDS.txt", backup_path / "PASSWORDS.txt")
                self.logger.info("  ✓ Backed up PASSWORDS.txt")
            
            # Backup SSL certificates
            if (misp_dir / "ssl").exists():
                shutil.copytree(misp_dir / "ssl", backup_path / "ssl")
                self.logger.info("  ✓ Backed up SSL certificates")
            
            # Backup database
            try:
                result = subprocess.run(
                    ["docker", "compose", "exec", "-T", "db", 
                     "mysqldump", "-umisp", "-ppassword", "misp"],
                    cwd=misp_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    with open(backup_path / "misp_database.sql", 'w') as f:
                        f.write(result.stdout)
                    self.logger.info("  ✓ Backed up database")
                else:
                    self.logger.warning("  ⚠ Could not backup database (might not be running)")
            except Exception as e:
                self.logger.warning(f"  ⚠ Database backup failed: {e}")
            
            self.logger.info(Colors.success(f"Backup completed: {backup_path}"))
            return backup_path
            
        except Exception as e:
            self.logger.error(Colors.error(f"Backup failed: {e}"))
            return None

# ==========================================
# Docker Group Manager
# ==========================================

class DockerGroupManager:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def add_user_to_docker_group(self) -> bool:
        """Add current user to docker group"""
        username = pwd.getpwuid(os.getuid()).pw_name
        
        try:
            # Check if already in docker group
            result = subprocess.run(
                ['groups', username],
                capture_output=True,
                text=True
            )
            
            if 'docker' in result.stdout:
                self.logger.info(Colors.success("Already in docker group"))
                return True
            
            # Add user to docker group
            self.logger.info("Adding user to docker group...")
            subprocess.run(
                ['sudo', 'usermod', '-aG', 'docker', username],
                check=True
            )
            
            self.logger.info(Colors.success(f"Added {username} to docker group"))
            return True
            
        except Exception as e:
            self.logger.error(Colors.error(f"Failed to add user to docker group: {e}"))
            return False

# ==========================================
# Main Installer Class
# ==========================================

class MISPInstaller:
    def __init__(self, config: MISPConfig, logger: logging.Logger, interactive: bool = True):
        self.config = config
        self.logger = logger
        self.interactive = interactive
        self.misp_dir = Path("/opt/misp")
        self.state_file = Path.home() / ".misp-install" / "state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_phase = 0
        self.total_phases = 12
        
    def save_state(self, phase: int, phase_name: str):
        """Save installation state for resume capability"""
        state = {
            "phase": phase,
            "phase_name": phase_name,
            "timestamp": datetime.now().isoformat(),
            "config": self.config.to_dict()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.debug(f"Saved state: Phase {phase} - {phase_name}")
    
    def load_state(self) -> Optional[Dict]:
        """Load previous installation state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return None
    
    def clear_state(self):
        """Clear installation state"""
        if self.state_file.exists():
            self.state_file.unlink()
            self.logger.debug("Cleared installation state")
    
    def run_command(self, cmd: List[str], check: bool = True, cwd: Optional[Path] = None, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Run a command and log output"""
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=cwd,
                timeout=timeout
            )
            
            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"STDERR: {result.stderr}")
            
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")
            if e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            raise
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out: {e}")
            raise
    
    def section_header(self, title: str):
        """Print a section header"""
        self.logger.info("\n" + Colors.info("="*50))
        self.logger.info(Colors.info(title))
        self.logger.info(Colors.info("="*50) + "\n")
    
    def retry_on_failure(self, func: Callable, max_retries: int = 3, phase_name: str = "") -> bool:
        """Retry a function on failure"""
        for attempt in range(1, max_retries + 1):
            try:
                func()
                return True
            except Exception as e:
                self.logger.error(Colors.error(f"Attempt {attempt}/{max_retries} failed: {e}"))
                
                if attempt < max_retries:
                    if self.interactive:
                        response = input(f"Retry {phase_name}? (yes/no): ").lower()
                        if response != 'yes':
                            return False
                    else:
                        self.logger.info("Retrying...")
                        time.sleep(5)
                else:
                    return False
        
        return False
    
    def phase_1_install_dependencies(self):
        """Phase 1: Install required dependencies"""
        self.section_header("PHASE 1: INSTALLING DEPENDENCIES")
        
        packages = [
            'curl', 'wget', 'git', 'ca-certificates', 'gnupg',
            'lsb-release', 'openssl', 'net-tools', 'iputils-ping',
            'dnsutils', 'jq'
        ]
        
        self.logger.info("[1.1] Updating package lists...")
        self.run_command(['sudo', 'apt', 'update', '-qq'])
        
        self.logger.info("[1.2] Installing required packages...")
        self.run_command(['sudo', 'apt', 'install', '-y'] + packages, timeout=300)
        
        self.logger.info("[1.3] Checking Docker installation...")
        try:
            self.run_command(['docker', '--version'])
            self.logger.info(Colors.success("Docker already installed"))
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.logger.info("Installing Docker...")
            
            # Install Docker
            self.run_command(['sudo', 'mkdir', '-p', '/etc/apt/keyrings'])
            
            # Add Docker GPG key
            gpg_result = subprocess.run(
                ['curl', '-fsSL', 'https://download.docker.com/linux/ubuntu/gpg'],
                capture_output=True
            )
            subprocess.run(
                ['sudo', 'gpg', '--dearmor', '-o', '/etc/apt/keyrings/docker.gpg'],
                input=gpg_result.stdout,
                check=True
            )
            
            # Add Docker repository
            lsb_release = subprocess.run(['lsb_release', '-cs'], capture_output=True, text=True).stdout.strip()
            arch = subprocess.run(['dpkg', '--print-architecture'], capture_output=True, text=True).stdout.strip()
            
            repo_line = f"deb [arch={arch} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu {lsb_release} stable"
            
            with open('/tmp/docker.list', 'w') as f:
                f.write(repo_line)
            
            self.run_command(['sudo', 'mv', '/tmp/docker.list', '/etc/apt/sources.list.d/docker.list'])
            
            # Install Docker packages
            self.run_command(['sudo', 'apt', 'update', '-qq'])
            self.run_command([
                'sudo', 'apt', 'install', '-y',
                'docker-ce', 'docker-ce-cli', 'containerd.io',
                'docker-buildx-plugin', 'docker-compose-plugin'
            ], timeout=600)
            
            self.logger.info(Colors.success("Docker installed"))
        
        self.logger.info("[1.4] Verifying Docker Compose...")
        self.run_command(['docker', 'compose', 'version'])
        
        self.logger.info(Colors.success("All dependencies installed"))
        self.save_state(1, "Dependencies Installed")
    
    def phase_2_docker_group(self):
        """Phase 2: Configure Docker group access"""
        self.section_header("PHASE 2: DOCKER GROUP CONFIGURATION")
        
        docker_mgr = DockerGroupManager(self.logger)
        docker_mgr.add_user_to_docker_group()
        
        self.save_state(2, "Docker Group Configured")
    
    def phase_3_backup(self):
        """Phase 3: Backup existing installation"""
        self.section_header("PHASE 3: BACKUP EXISTING INSTALLATION")
        
        backup_mgr = BackupManager(self.logger)
        backup_path = backup_mgr.create_backup(self.misp_dir)
        
        if backup_path:
            self.logger.info(Colors.success(f"Backup saved to: {backup_path}"))
        
        self.save_state(3, "Backup Complete")
    
    def phase_4_cleanup(self):
        """Phase 4: Nuclear cleanup"""
        self.section_header("PHASE 4: NUCLEAR CLEANUP")
        
        self.logger.info("[4.1] Stopping all Docker containers...")
        try:
            result = self.run_command(['docker', 'ps', '-aq'], check=False)
            if result.stdout.strip():
                self.run_command(['docker', 'stop'] + result.stdout.strip().split('\n'), timeout=60)
        except Exception as e:
            self.logger.warning(f"Could not stop containers: {e}")
        
        self.logger.info("[4.2] Removing all Docker containers...")
        try:
            result = self.run_command(['docker', 'ps', '-aq'], check=False)
            if result.stdout.strip():
                self.run_command(['docker', 'rm', '-f'] + result.stdout.strip().split('\n'))
        except Exception as e:
            self.logger.warning(f"Could not remove containers: {e}")
        
        self.logger.info("[4.3] Removing MISP directory...")
        if self.misp_dir.exists():
            self.run_command(['sudo', 'rm', '-rf', str(self.misp_dir)])
        
        self.logger.info("[4.4] Removing all Docker volumes...")
        try:
            result = self.run_command(['docker', 'volume', 'ls', '-q'], check=False)
            if result.stdout.strip():
                self.run_command(['docker', 'volume', 'rm'] + result.stdout.strip().split('\n'), check=False)
        except Exception as e:
            self.logger.warning(f"Could not remove volumes: {e}")
        
        self.logger.info("[4.5] Docker system prune...")
        self.run_command(['docker', 'system', 'prune', '-af', '--volumes'], check=False)
        
        self.logger.info("[4.6] Cleaning up /etc/hosts...")
        try:
            # Remove existing entries
            with open('/etc/hosts', 'r') as f:
                lines = f.readlines()
            
            with open('/tmp/hosts', 'w') as f:
                for line in lines:
                    if self.config.domain not in line:
                        f.write(line)
            
            self.run_command(['sudo', 'mv', '/tmp/hosts', '/etc/hosts'])
        except Exception as e:
            self.logger.warning(f"Could not clean /etc/hosts: {e}")
        
        self.logger.info(Colors.success("Nuclear cleanup complete"))
        self.save_state(4, "Cleanup Complete")
    
    def phase_5_clone_repository(self):
        """Phase 5: Clone MISP repository"""
        self.section_header("PHASE 5: CLONING MISP REPOSITORY")

        self.logger.info("[5.1] Creating /opt directory structure...")

        # Ensure /opt exists and create misp parent if needed
        opt_dir = Path("/opt")
        if not opt_dir.exists():
            self.run_command(['sudo', 'mkdir', '-p', '/opt'])

        self.logger.info("[5.2] Cloning MISP Docker repository...")
        self.logger.info("This may take 1-2 minutes...")

        # Clone directly to /opt/misp
        self.run_command([
            'sudo', 'git', 'clone', '--progress',
            'https://github.com/MISP/misp-docker.git',
            '/opt/misp'
        ], timeout=300)

        # Set ownership to current user
        username = pwd.getpwuid(os.getuid()).pw_name
        self.logger.info(f"[5.3] Setting ownership to {username}...")
        self.run_command(['sudo', 'chown', '-R', f'{username}:{username}', '/opt/misp'])

        os.chdir(self.misp_dir)

        self.logger.info(Colors.success("Repository cloned"))
        self.save_state(5, "Repository Cloned")
    
    def phase_6_configuration(self):
        """Phase 6: Create configuration files"""
        self.section_header("PHASE 6: CONFIGURATION")
        
        self.logger.info("[6.1] Creating .env file...")
        
        # Calculate performance tuning
        perf = PerformanceTuning()
        
        # Adjust based on RAM
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        total_gb = int(line.split()[1]) // (1024**2)
                        if total_gb >= 16:
                            perf.php_memory_limit = "4096M"
                        elif total_gb >= 8:
                            perf.php_memory_limit = "2048M"
                        else:
                            perf.php_memory_limit = "1024M"
        except Exception:
            pass
        
        env_content = f"""##
# Build-time variables
##

CORE_TAG=v2.5.22
MODULES_TAG=v3.0.2
GUARD_TAG=v1.2
PHP_VER=20220829

PYPI_SETUPTOOLS_VERSION="==80.3.1"
PYPI_SUPERVISOR_VERSION="==4.2.5"

##
# Run-time variables - {self.config.admin_org} Configuration
# Environment: {self.config.environment}
##

# CRITICAL: {self.config.admin_org} Settings
BASE_URL={self.config.base_url}
ADMIN_EMAIL={self.config.admin_email}
ADMIN_ORG={self.config.admin_org}
ADMIN_PASSWORD={self.config.admin_password}
GPG_PASSPHRASE={self.config.gpg_passphrase}
MYSQL_PASSWORD={self.config.mysql_password}
ENCRYPTION_KEY={self.config.encryption_key}

# Database Configuration
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=misp
MYSQL_DATABASE=misp

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Optional Settings
ENABLE_DB_SETTINGS=true
ENABLE_BACKGROUND_UPDATES=true
CRON_USER_ID=1

# Security Settings
DISABLE_IPV6=false
DISABLE_SSL_REDIRECT=false
HSTS_MAX_AGE=31536000
X_FRAME_OPTIONS=SAMEORIGIN

# PHP Configuration (Performance Tuned)
PHP_MEMORY_LIMIT={perf.php_memory_limit}
PHP_MAX_EXECUTION_TIME={perf.php_max_execution_time}
PHP_UPLOAD_MAX_FILESIZE=50M
PHP_POST_MAX_SIZE=50M

# Nginx Configuration
NGINX_CLIENT_MAX_BODY_SIZE=50M

# Workers (Auto-calculated: {perf.workers} workers for {os.cpu_count()} CPU cores)
WORKERS={perf.workers}

# Debug
DEBUG=0
"""
        
        with open(self.misp_dir / ".env", 'w') as f:
            f.write(env_content)
        
        os.chmod(self.misp_dir / ".env", 0o600)
        
        self.logger.info(Colors.success("Configuration created"))
        self.logger.info(f"  Performance tuning: {perf.php_memory_limit} RAM, {perf.workers} workers")
        
        self.save_state(6, "Configuration Complete")
    
    def phase_7_ssl_certificate(self):
        """Phase 7: Generate SSL certificate"""
        self.section_header("PHASE 7: SSL CERTIFICATE")
        
        self.logger.info("[7.1] Creating SSL directory...")
        ssl_dir = self.misp_dir / "ssl"
        ssl_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"[7.2] Generating self-signed certificate for {self.config.domain}...")
        
        self.run_command([
            'openssl', 'req', '-x509', '-nodes', '-days', '365',
            '-newkey', 'rsa:4096',
            '-keyout', str(ssl_dir / 'key.pem'),
            '-out', str(ssl_dir / 'cert.pem'),
            '-subj', f"/C=US/ST=New York/L=New York/O={self.config.admin_org}/OU=IT/CN={self.config.domain}",
            '-addext', f"subjectAltName=DNS:{self.config.domain},DNS:*.{self.config.domain},IP:{self.config.server_ip}"
        ])
        
        os.chmod(ssl_dir / 'cert.pem', 0o644)
        os.chmod(ssl_dir / 'key.pem', 0o600)
        
        self.logger.info("[7.3] Creating docker-compose.override.yml...")
        
        override_content = """services:
  misp-core:
    volumes:
      - ./ssl:/etc/nginx/certs:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      misp-modules:
        condition: service_started

  misp-modules:
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6666/modules || exit 1"]
      interval: 30s
      timeout: 15s
      retries: 15
      start_period: 180s
"""
        
        with open(self.misp_dir / "docker-compose.override.yml", 'w') as f:
            f.write(override_content)
        
        self.logger.info(Colors.success("SSL certificate generated"))
        self.save_state(7, "SSL Certificate Created")
    
    def phase_8_dns_configuration(self):
        """Phase 8: Configure DNS"""
        self.section_header("PHASE 8: DNS CONFIGURATION")
        
        self.logger.info("[8.1] Configuring /etc/hosts...")
        
        # Read existing hosts file
        with open('/etc/hosts', 'r') as f:
            lines = f.readlines()
        
        # Remove any existing entries for this domain
        lines = [line for line in lines if self.config.domain not in line]
        
        # Add new entries
        lines.append(f"\n127.0.0.1 {self.config.domain}\n")
        lines.append(f"{self.config.server_ip} {self.config.domain}\n")
        
        # Write to temp file
        with open('/tmp/hosts', 'w') as f:
            f.writelines(lines)
        
        # Move to /etc/hosts
        self.run_command(['sudo', 'mv', '/tmp/hosts', '/etc/hosts'])
        
        self.logger.info(Colors.success("DNS configured in /etc/hosts"))
        self.logger.info(f"  Entries: 127.0.0.1 {self.config.domain}")
        self.logger.info(f"           {self.config.server_ip} {self.config.domain}")
        
        self.save_state(8, "DNS Configured")
    
    def phase_9_password_reference(self):
        """Phase 9: Create password reference file"""
        self.section_header("PHASE 9: PASSWORD REFERENCE")
        
        self.logger.info("[9.1] Creating secure password reference file...")
        
        # Get certificate expiry
        try:
            result = self.run_command([
                'openssl', 'x509', '-enddate', '-noout',
                '-in', str(self.misp_dir / 'ssl' / 'cert.pem')
            ])
            cert_expiry = result.stdout.strip().split('=')[1]
        except Exception:
            cert_expiry = "Unknown"
        
        password_content = f"""================================================
MISP PASSWORD REFERENCE - {self.config.admin_org}
================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: {self.config.environment}

ADMIN WEB LOGIN:
  URL:      {self.config.base_url}
  Email:    {self.config.admin_email}
  Password: {self.config.admin_password}

DATABASE:
  Host:     db (container)
  User:     misp
  Password: {self.config.mysql_password}
  Database: misp

GPG:
  Passphrase: {self.config.gpg_passphrase}
  Email:      {self.config.admin_email}

ENCRYPTION:
  Key: {self.config.encryption_key}
  ⚠️  DO NOT CHANGE - data will be lost!

SERVER:
  IP:   {self.config.server_ip}
  FQDN: {self.config.domain}

CERTIFICATE:
  Location: /opt/misp/ssl/cert.pem
  Expires:  {cert_expiry}

PERFORMANCE:
  PHP Memory: {self.config.performance['php_memory_limit']}
  Workers:    {self.config.performance['workers']}

================================================
⚠️  KEEP THIS FILE SECURE AND BACKED UP!
================================================
"""
        
        with open(self.misp_dir / "PASSWORDS.txt", 'w') as f:
            f.write(password_content)
        
        os.chmod(self.misp_dir / "PASSWORDS.txt", 0o600)
        
        self.logger.info(Colors.success(f"Password reference saved to: {self.misp_dir}/PASSWORDS.txt"))
        self.save_state(9, "Password Reference Created")
    
    def phase_10_docker_build(self):
        """Phase 10: Build and start Docker containers with improved progress monitoring"""
        self.section_header("PHASE 10: DOCKER BUILD")
        
        os.chdir(self.misp_dir)
        
        try:
            # Step 1: Pull images (this is the slowest part)
            self.logger.info("[10.1] Pulling Docker images...")
            self.logger.info("This may take 10-20 minutes on first run...")
            self.logger.info("Progress will be shown below:\n")
            
            pull_cmd = ['sudo', 'docker', 'compose', 'pull']
            pull_process = subprocess.Popen(
                pull_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.misp_dir
            )
            
            # Stream output in real-time
            for line in iter(pull_process.stdout.readline, ''):
                if line:
                    # Filter for important progress lines
                    if any(keyword in line for keyword in ['Pulling', 'Downloading', 'Extracting', 'Pull complete', 'Status', 'Downloaded', 'Digest', 'Already exists']):
                        self.logger.info(f"  {line.rstrip()}")
            
            pull_process.wait(timeout=1800)  # 30 minute timeout for pulls
            
            if pull_process.returncode != 0:
                self.logger.warning("⚠ Pull had some issues, but continuing...")
            else:
                self.logger.info(Colors.success("\n✓ Images pulled successfully\n"))
            
            # Step 2: Build containers (if needed)
            self.logger.info("[10.2] Checking if build is required...")
            
            # Check if there are any services that need building
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'config', '--services'],
                timeout=10,
                cwd=self.misp_dir,
                check=False
            )
            
            # Check for custom Dockerfiles
            needs_build = False
            if (self.misp_dir / "Dockerfile").exists():
                needs_build = True
            
            # Look for build contexts in docker-compose
            for subdir in self.misp_dir.iterdir():
                if subdir.is_dir() and (subdir / "Dockerfile").exists():
                    needs_build = True
                    break
            
            if needs_build:
                self.logger.info("Custom builds detected. Building containers...")
                self.logger.info("This may take 15-30 minutes on first run...\n")
                
                build_cmd = ['sudo', 'docker', 'compose', 'build', '--progress=plain']
                build_process = subprocess.Popen(
                    build_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=self.misp_dir
                )
                
                # Stream output in real-time
                for line in iter(build_process.stdout.readline, ''):
                    if line:
                        # Filter for important build lines
                        if any(keyword in line for keyword in ['Step', 'Successfully', 'Building', 
                                                               'Sending build context', '--->', 
                                                               'Running in', 'Removing intermediate']):
                            self.logger.info(f"  {line.rstrip()}")
                
                build_process.wait(timeout=2400)  # 40 minute timeout for builds
                
                if build_process.returncode == 0:
                    self.logger.info(Colors.success("\n✓ Build completed\n"))
                else:
                    self.logger.warning("⚠ Build completed with warnings\n")
            else:
                self.logger.info("No custom builds needed (using pre-built images)")
                self.logger.info(Colors.success("✓ Skipping build step\n"))
            
            # Step 3: Start containers
            self.logger.info("[10.3] Starting MISP services...")
            up_result = self.run_command(
                ['sudo', 'docker', 'compose', 'up', '-d'],
                timeout=300,  # 5 minutes to start
                cwd=self.misp_dir
            )
            
            self.logger.info(Colors.success("✓ Containers started\n"))
            
            # Step 4: Wait for health checks
            self.logger.info("[10.4] Waiting for services to become healthy...")
            self.logger.info("This typically takes 2-5 minutes...\n")
            
            max_wait = 300  # 5 minutes
            start_time = time.time()
            last_status = ""
            
            while (time.time() - start_time) < max_wait:
                # Get container status
                ps_result = self.run_command(
                    ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                    timeout=30,
                    cwd=self.misp_dir,
                    check=False
                )
                
                if ps_result.returncode == 0:
                    try:
                        containers = []
                        for line in ps_result.stdout.strip().split('\n'):
                            if line:
                                containers.append(json.loads(line))
                        
                        healthy = sum(1 for c in containers if 'healthy' in c.get('Health', '').lower())
                        running = sum(1 for c in containers if c.get('State') == 'running')
                        total = len(containers)
                        
                        elapsed = int(time.time() - start_time)
                        status = f"  [{elapsed}s] Running: {running}/{total} | Healthy: {healthy}/{total}"
                        
                        # Only print if status changed
                        if status != last_status:
                            self.logger.info(status)
                            last_status = status
                        
                        # Success condition: all running and at least some healthy
                        if running == total and total > 0:
                            if healthy > 0 or elapsed > 120:  # Give 2 min for health checks
                                self.logger.info(Colors.success(f"\n✓ All {total} containers are running"))
                                if healthy > 0:
                                    self.logger.info(Colors.success(f"✓ {healthy} containers report healthy status"))
                                break
                    
                    except json.JSONDecodeError:
                        pass
                
                time.sleep(5)
            
            # Step 5: Final status check
            self.logger.info("\n[10.5] Final service status:")
            ps_result = self.run_command(
                ['sudo', 'docker', 'compose', 'ps'],
                timeout=30,
                cwd=self.misp_dir,
                check=False
            )
            
            if ps_result.returncode == 0:
                self.logger.info(ps_result.stdout)
            
            # Check for any unhealthy containers
            logs_needed = []
            check_result = self.run_command(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                timeout=30,
                cwd=self.misp_dir,
                check=False
            )
            
            if check_result.returncode == 0:
                try:
                    for line in check_result.stdout.strip().split('\n'):
                        if line:
                            container = json.loads(line)
                            if container.get('State') != 'running':
                                logs_needed.append(container.get('Service', container.get('Name')))
                except:
                    pass
            
            if logs_needed:
                self.logger.warning(f"\n⚠ Some containers are not running: {', '.join(logs_needed)}")
                self.logger.info("Checking logs...")
                for service in logs_needed[:2]:  # Limit to 2 services
                    self.logger.info(f"\n--- Logs for {service} (last 20 lines) ---")
                    log_result = self.run_command(
                        ['sudo', 'docker', 'compose', 'logs', '--tail', '20', service],
                        timeout=30,
                        cwd=self.misp_dir,
                        check=False
                    )
                    if log_result.returncode == 0:
                        self.logger.info(log_result.stdout)
            
            self.logger.info(Colors.success("\n✓ Phase 10 completed"))
            self.save_state(10, "Docker Build Complete")
            
        except subprocess.TimeoutExpired as e:
            self.logger.error(Colors.error(f"\n❌ Timeout during docker build: {e}"))
            raise
        except Exception as e:
            self.logger.error(Colors.error(f"\n❌ Docker build failed: {e}"))
            raise
    
    def phase_11_initialization(self):
        """Phase 11: Wait for MISP initialization"""
        self.section_header("PHASE 11: MISP INITIALIZATION")
        
        self.logger.info("[11.1] Waiting for MISP to initialize (5-10 minutes)...")
        self.logger.info("       Monitoring logs for 'INIT | Done'...")
        
        timeout = 600
        elapsed = 0
        interval = 10
        
        os.chdir(self.misp_dir)
        
        while elapsed < timeout:
            result = self.run_command(
                ['docker', 'compose', 'logs', 'misp-core'],
                check=False
            )
            
            if "INIT | Done" in result.stdout:
                self.logger.info(Colors.success("\n✅ MISP initialization complete!"))
                break
            
            self.logger.info(f"⏳ Waiting... ({elapsed} seconds elapsed)")
            time.sleep(interval)
            elapsed += interval
        
        if elapsed >= timeout:
            self.logger.warning("⚠️  Timeout waiting for initialization")
            self.logger.warning("MISP may still be starting")
        
        self.logger.info("\nWaiting additional 30 seconds...")
        time.sleep(30)
        
        self.save_state(11, "MISP Initialized")
    
    def phase_12_post_install(self):
        """Phase 12: Post-install tasks"""
        self.section_header("PHASE 12: POST-INSTALL TASKS")
        
        self.logger.info("[12.1] Creating post-install checklist...")
        
        checklist_content = f"""# MISP Post-Installation Checklist
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Immediate Actions (Do Now):
- [ ] Login to MISP web interface: {self.config.base_url}
- [ ] Verify admin account works
- [ ] Review system settings
- [ ] Configure email settings (Administration → Server Settings → Email)
- [ ] Test email notifications

## Security (First Week):
- [ ] Enable 2FA for admin account
- [ ] Change admin password (even though it's already strong)
- [ ] Review user permissions
- [ ] Configure firewall: `sudo ufw allow 443/tcp`
- [ ] Set up SSL certificate monitoring
- [ ] Review audit logs

## Backup & Recovery (First Week):
- [ ] Configure automated backups
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Set up off-site backup storage

## Integration (First Month):
- [ ] Configure MISP feeds (Administration → Feeds)
- [ ] Set up sync servers if needed
- [ ] Configure API access
- [ ] Test MISP modules functionality
- [ ] Configure enrichment services
- [ ] Set up correlation rules

## Monitoring (First Month):
- [ ] Set up log monitoring
- [ ] Configure alerts for critical events
- [ ] Test notification system
- [ ] Verify worker status: `cd /opt/misp && sudo docker compose exec misp-core ps aux | grep worker`
- [ ] Monitor disk space usage
- [ ] Set up uptime monitoring

## Team & Training (First Month):
- [ ] Create user accounts for team members
- [ ] Assign appropriate roles and permissions
- [ ] Conduct initial training session
- [ ] Document common workflows
- [ ] Create runbook for common tasks

## Performance Optimization (Ongoing):
- [ ] Monitor database performance
- [ ] Review and tune worker settings
- [ ] Optimize Redis cache settings
- [ ] Review and clean old events periodically

## Workstation Setup:
Windows users must add to C:\\Windows\\System32\\drivers\\etc\\hosts:
{self.config.server_ip} {self.config.domain}

macOS/Linux users:
echo '{self.config.server_ip} {self.config.domain}' | sudo tee -a /etc/hosts

## Useful Commands:
```bash
# View logs
cd /opt/misp && sudo docker compose logs -f

# Restart MISP
cd /opt/misp && sudo docker compose restart

# Stop MISP
cd /opt/misp && sudo docker compose down

# Start MISP
cd /opt/misp && sudo docker compose up -d

# Check status
cd /opt/misp && sudo docker compose ps

# View passwords
sudo cat /opt/misp/PASSWORDS.txt
```

## Support & Resources:
- MISP Documentation: https://www.misp-project.org/documentation/
- MISP Book: https://www.circl.lu/doc/misp/
- Community: https://www.misp-project.org/community/
- GitHub: https://github.com/MISP/MISP

## Backup Locations:
- Passwords: /opt/misp/PASSWORDS.txt
- Configuration: /opt/misp/.env
- SSL Certificates: /opt/misp/ssl/
- Backups: /opt/misp-backups/
- Logs: /var/log/misp-install/
"""
        
        with open(self.misp_dir / "POST-INSTALL-CHECKLIST.md", 'w') as f:
            f.write(checklist_content)
        
        self.logger.info(Colors.success("Post-install checklist created"))
        self.save_state(12, "Post-Install Complete")
    
    def run_installation(self, start_phase: int = 1):
        """Run the complete installation"""
        phases = [
            (1, "Install Dependencies", self.phase_1_install_dependencies),
            (2, "Docker Group", self.phase_2_docker_group),
            (3, "Backup", self.phase_3_backup),
            (4, "Cleanup", self.phase_4_cleanup),
            (5, "Clone Repository", self.phase_5_clone_repository),
            (6, "Configuration", self.phase_6_configuration),
            (7, "SSL Certificate", self.phase_7_ssl_certificate),
            (8, "DNS Configuration", self.phase_8_dns_configuration),
            (9, "Password Reference", self.phase_9_password_reference),
            (10, "Docker Build", self.phase_10_docker_build),
            (11, "Initialization", self.phase_11_initialization),
            (12, "Post-Install", self.phase_12_post_install),
        ]
        
        # Show installation plan
        if start_phase > 1:
            self.logger.info(Colors.info("\nInstallation Plan:"))
            for phase_num, phase_name, _ in phases:
                if phase_num < start_phase:
                    self.logger.info(Colors.success(f"  Phase {phase_num:2d}: {phase_name:30s} [COMPLETED]"))
                else:
                    self.logger.info(f"  Phase {phase_num:2d}: {phase_name:30s} [PENDING]")
            self.logger.info("")
        
        for phase_num, phase_name, phase_func in phases:
            if phase_num < start_phase:
                continue
            
            try:
                if not self.retry_on_failure(phase_func, phase_name=phase_name):
                    self.logger.error(Colors.error(f"Phase {phase_num} failed: {phase_name}"))
                    return False
            except KeyboardInterrupt:
                self.logger.warning("\n⚠️  Installation interrupted by user")
                self.logger.info(f"Resume from phase {phase_num} by running script again")
                return False
            except Exception as e:
                self.logger.error(Colors.error(f"Phase {phase_num} failed: {e}"))
                return False
        
        return True
    
    def print_final_summary(self):
        """Print final installation summary"""
        self.section_header("✅ MISP INSTALLATION COMPLETE!")
        
        print(f"""
🌐 Access Information:
   URL:      {self.config.base_url}
   Email:    {self.config.admin_email}
   Password: (see PASSWORDS.txt)

🔐 All Credentials Saved To:
   {self.misp_dir}/PASSWORDS.txt
   {self.misp_dir}/.env

   ⚠️  BACKUP THESE FILES SECURELY!

📁 Installation Directory: {self.misp_dir}

📋 View Your Passwords:
   sudo cat {self.misp_dir}/PASSWORDS.txt

📝 Post-Install Checklist:
   sudo cat {self.misp_dir}/POST-INSTALL-CHECKLIST.md

⚠️  IMPORTANT - WORKSTATION SETUP:

   Windows users add to C:\\Windows\\System32\\drivers\\etc\\hosts:
   {self.config.server_ip} {self.config.domain}

   macOS/Linux workstations:
   echo '{self.config.server_ip} {self.config.domain}' | sudo tee -a /etc/hosts

🔧 Useful Commands:
   View passwords: sudo cat {self.misp_dir}/PASSWORDS.txt
   View logs:      cd {self.misp_dir} && sudo docker compose logs -f
   Restart:        cd {self.misp_dir} && sudo docker compose restart
   Stop:           cd {self.misp_dir} && sudo docker compose down
   Start:          cd {self.misp_dir} && sudo docker compose up -d

⚠️  NOTE: You may need to logout/login for docker group to take full effect

==================================================
🎉 Ready to use! Open browser to: {self.config.base_url}
==================================================
""")

# ==========================================
# User Input
# ==========================================

def get_user_input_interactive(logger: logging.Logger) -> MISPConfig:
    """Get configuration from user interactively"""
    print(Colors.info("\n" + "="*50))
    print(Colors.info("📋 CONFIGURATION"))
    print(Colors.info("="*50 + "\n"))
    
    print("Please provide installation details:\n")

    server_ip = input("Enter server IP address [192.168.20.193]: ") or "192.168.20.193"
    domain = input("Enter FQDN for MISP [misp-dev.lan]: ") or "misp-dev.lan"
    admin_email = input("Enter admin email [cgallagher@gridsec.com]: ") or "cgallagher@gridsec.com"
    admin_org = input("Enter organization name [GridSec]: ") or "GridSec"
    
    # Environment selection
    print("\nEnvironment:")
    print("1) Development")
    print("2) Staging")
    print("3) Production (recommended)")
    env_choice = input("Select environment [3]: ") or "3"
    
    env_map = {
        "1": Environment.DEV.value,
        "2": Environment.STAGING.value,
        "3": Environment.PROD.value
    }
    environment = env_map.get(env_choice, Environment.PROD.value)
    
    print(Colors.info("\n" + "="*50))
    print(Colors.info("🔐 PASSWORD CONFIGURATION"))
    print(Colors.info("="*50 + "\n"))
    print("Passwords must be at least 12 characters with uppercase, lowercase, number, and special character.\n")
    
    admin_password = PasswordValidator.get_password_interactive("Enter MISP admin password (min 12 chars): ")
    print()
    
    mysql_password = PasswordValidator.get_password_interactive("Enter MySQL database password (min 12 chars): ")
    print()
    
    gpg_passphrase = PasswordValidator.get_password_interactive("Enter GPG passphrase (min 12 chars): ")
    print()
    
    print("Generating encryption key...")
    encryption_key = secrets.token_hex(16)
    print(Colors.success("Encryption key generated"))
    
    # Create config
    config = MISPConfig(
        server_ip=server_ip,
        domain=domain,
        admin_email=admin_email,
        admin_org=admin_org,
        admin_password=admin_password,
        mysql_password=mysql_password,
        gpg_passphrase=gpg_passphrase,
        encryption_key=encryption_key,
        environment=environment
    )
    
    # Show summary
    print(Colors.info("\n" + "="*50 + "\n"))
    print("Configuration Summary:")
    print(f"  Server IP:    {config.server_ip}")
    print(f"  FQDN:         {config.domain}")
    print(f"  Admin Email:  {config.admin_email}")
    print(f"  Organization: {config.admin_org}")
    print(f"  Environment:  {config.environment}")
    print(f"  Base URL:     {config.base_url}")
    print()
    print(f"  Admin Password:   {'*' * len(config.admin_password)} ({len(config.admin_password)} characters)")
    print(f"  MySQL Password:   {'*' * len(config.mysql_password)} ({len(config.mysql_password)} characters)")
    print(f"  GPG Passphrase:   {'*' * len(config.gpg_passphrase)} ({len(config.gpg_passphrase)} characters)")
    print(f"  Encryption Key:   {config.encryption_key}")
    print()
    print("⚠️  IMPORTANT: Save these passwords securely!")
    print()
    
    confirm = input("Is this correct? Type 'YES' to proceed: ")
    if confirm != 'YES':
        print("Aborted.")
        sys.exit(0)
    
    return config

# ==========================================
# Main Function
# ==========================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MISP Installation Tool')
    parser.add_argument('--config', type=str, help='Path to config file (YAML or JSON)')
    parser.add_argument('--non-interactive', action='store_true', help='Run in non-interactive mode')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--skip-checks', action='store_true', help='Skip pre-flight checks')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info(Colors.info("""
╔══════════════════════════════════════════════════╗
║                                                  ║
║      MISP Complete Installation Tool v5.1       ║
║            GridSec Enterprise Edition            ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""))
    
    try:
        # Check if running as root
        if os.geteuid() == 0:
            logger.error(Colors.error("❌ Don't run this script as root!"))
            logger.info("Please run as regular user:")
            logger.info(f"  python3 {sys.argv[0]}")
            sys.exit(1)
        
        # Pre-flight checks
        if not args.skip_checks:
            checker = SystemChecker(logger)
            if not checker.run_all_checks():
                logger.error(Colors.error("\n❌ Pre-flight checks failed!"))
                logger.info("Fix the issues above and try again")
                sys.exit(1)
        
        # Check for resume first
        start_phase = 1
        config = None
        interactive = True
        
        # Try to load previous state if resuming
        temp_installer = MISPInstaller(MISPConfig(), logger, interactive=True)
        state = temp_installer.load_state()
        
        if args.resume and state:
            # Resume from saved state
            start_phase = state['phase'] + 1
            logger.info(Colors.info("\n📍 RESUMING PREVIOUS INSTALLATION"))
            logger.info(Colors.info("="*50))
            logger.info(f"Last completed phase: {state['phase']} - {state.get('phase_name', 'Unknown')}")
            logger.info(f"Previous run: {state['timestamp']}")
            logger.info(f"Resuming from phase: {start_phase}")
            logger.info(Colors.info("="*50 + "\n"))
            
            # Load config from saved state
            config = MISPConfig.from_dict(state['config'])
            logger.info("✓ Configuration loaded from saved state")
            logger.info(f"  Organization: {config.admin_org}")
            logger.info(f"  Domain: {config.domain}")
            logger.info(f"  Environment: {config.environment}\n")
            
            # Check if phases 1-2 already done, don't prompt for docker group
            if start_phase > 2:
                interactive = False  # Skip docker group re-check
        elif args.resume and not state:
            logger.warning(Colors.warning("⚠️  No saved state found. Starting fresh installation."))
            args.resume = False
        
        # Load or get configuration (if not already loaded from state)
        if config is None:
            if args.config:
                logger.info(f"Loading configuration from: {args.config}")
                if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                    config = MISPConfig.from_yaml(args.config)
                else:
                    config = MISPConfig.from_json(args.config)
                interactive = False
            elif args.non_interactive:
                logger.error(Colors.error("❌ Non-interactive mode requires --config"))
                sys.exit(1)
            else:
                config = get_user_input_interactive(logger)
                interactive = True
        
        # Create installer
        installer = MISPInstaller(config, logger, interactive=interactive)
        
        # Docker group check (only if not resuming past phase 2)
        if start_phase <= 2:
            result = subprocess.run(['groups'], capture_output=True, text=True)
            if 'docker' not in result.stdout:
                docker_mgr = DockerGroupManager(logger)
                docker_mgr.add_user_to_docker_group()
                
                if interactive:
                    logger.info("\n" + Colors.warning("⚠️  Docker group added. Please logout and login, then run this script again."))
                    sys.exit(0)
        
        # Run installation
        success = installer.run_installation(start_phase=start_phase)
        
        if success:
            installer.clear_state()
            installer.print_final_summary()
            sys.exit(0)
        else:
            logger.error(Colors.error("\n❌ Installation failed"))
            logger.info(f"Check logs: /var/log/misp-install/")
            logger.info("You can resume by running: sudo python3 misp-install.py --resume")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Installation interrupted by user")
        logger.info("Resume by running: sudo python3 misp-install.py --resume")
        sys.exit(1)
    except Exception as e:
        logger.error(Colors.error(f"\n❌ Unexpected error: {e}"))
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()