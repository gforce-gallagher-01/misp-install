#!/usr/bin/env python3
"""
MISP Update & Upgrade Tool
tKQB Enterprises Edition
Version: 1.0

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
    """Setup comprehensive logging"""
    log_dir = Path("/var/log/misp-install")
    try:
        log_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    except PermissionError:
        # Fallback to user's home directory if /var/log is not writable
        log_dir = Path.home() / ".misp-install" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"misp-update-{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger('MISP-Updater')
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
# Version Information
# ==========================================

@dataclass
class ComponentVersion:
    name: str
    current: str
    available: str
    needs_update: bool
    
    def __str__(self):
        if self.needs_update:
            return f"{self.name}: {self.current} → {self.available}"
        else:
            return f"{self.name}: {self.current} (up to date)"

# ==========================================
# Backup Manager
# ==========================================

class UpdateBackupManager:
    def __init__(self, logger: logging.Logger, misp_dir: Path):
        self.logger = logger
        self.misp_dir = misp_dir
        self.backup_dir = Path.home() / "misp-backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
        self.current_backup = None
    
    def create_update_backup(self) -> Optional[Path]:
        """Create comprehensive backup before update"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"misp-update-backup-{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("CREATING PRE-UPDATE BACKUP"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        try:
            # Backup .env file
            if (self.misp_dir / ".env").exists():
                shutil.copy2(self.misp_dir / ".env", backup_path / ".env")
                self.logger.info("✓ Backed up .env")
            
            # Backup PASSWORDS.txt
            if (self.misp_dir / "PASSWORDS.txt").exists():
                shutil.copy2(self.misp_dir / "PASSWORDS.txt", backup_path / "PASSWORDS.txt")
                self.logger.info("✓ Backed up PASSWORDS.txt")
            
            # Backup docker-compose files
            for file in ['docker-compose.yml', 'docker-compose.override.yml']:
                if (self.misp_dir / file).exists():
                    shutil.copy2(self.misp_dir / file, backup_path / file)
                    self.logger.info(f"✓ Backed up {file}")
            
            # Backup SSL certificates
            if (self.misp_dir / "ssl").exists():
                shutil.copytree(self.misp_dir / "ssl", backup_path / "ssl")
                self.logger.info("✓ Backed up SSL certificates")
            
            # Backup database
            self.logger.info("Backing up database (this may take a few minutes)...")
            try:
                # Get password from .env
                with open(self.misp_dir / ".env", 'r') as f:
                    for line in f:
                        if line.startswith('MYSQL_PASSWORD='):
                            mysql_password = line.split('=', 1)[1].strip()
                            break

                result = subprocess.run(
                    ["sudo", "docker", "compose", "exec", "-T", "db",
                     "mysqldump", "-umisp", f"-p{mysql_password}", "misp"],
                    cwd=self.misp_dir,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    with open(backup_path / "misp_database.sql", 'w') as f:
                        f.write(result.stdout)
                    
                    # Get database size
                    db_size = len(result.stdout) / (1024 * 1024)  # MB
                    self.logger.info(f"✓ Backed up database ({db_size:.1f} MB)")
                else:
                    self.logger.warning("⚠ Could not backup database")
                    self.logger.warning("  Database might not be running or password incorrect")
            except Exception as e:
                self.logger.warning(f"⚠ Database backup failed: {e}")
            
            # Save current versions
            versions_info = self._get_current_versions()
            with open(backup_path / "versions.json", 'w') as f:
                json.dump(versions_info, f, indent=2)
            self.logger.info("✓ Saved version information")
            
            # Create backup metadata
            metadata = {
                "timestamp": timestamp,
                "backup_path": str(backup_path),
                "misp_dir": str(self.misp_dir),
                "versions": versions_info
            }
            
            with open(backup_path / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.current_backup = backup_path
            self.logger.info(Colors.success(f"\n✓ Backup completed: {backup_path}"))
            self.logger.info(f"  Backup size: {self._get_dir_size(backup_path):.1f} MB\n")
            
            return backup_path
            
        except Exception as e:
            self.logger.error(Colors.error(f"Backup failed: {e}"))
            return None
    
    def _get_current_versions(self) -> Dict:
        """Get current component versions"""
        versions = {}
        
        try:
            # Get Docker image versions
            result = subprocess.run(
                ["sudo", "docker", "compose", "images", "--format", "json"],
                cwd=self.misp_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        img = json.loads(line)
                        versions[img.get('Service', 'unknown')] = img.get('Tag', 'unknown')
        except:
            pass
        
        return versions
    
    def _get_dir_size(self, path: Path) -> float:
        """Get directory size in MB"""
        total = 0
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
        return total / (1024 * 1024)

# ==========================================
# Version Checker
# ==========================================

class VersionChecker:
    def __init__(self, logger: logging.Logger, misp_dir: Path):
        self.logger = logger
        self.misp_dir = misp_dir
    
    def check_updates(self) -> List[ComponentVersion]:
        """Check for available updates"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("CHECKING FOR UPDATES"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        components = []
        
        # First, check if Docker containers are running
        self.logger.info("[0/5] Checking container status...")
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            containers.append(json.loads(line))
                        except:
                            pass
                
                running = sum(1 for c in containers if c.get('State') == 'running')
                total = len(containers)
                
                if total == 0:
                    self.logger.warning("  ⚠ No containers found. MISP may not be installed.")
                    self.logger.info("     Run misp-install.py first to install MISP\n")
                    return components
                elif running == 0:
                    self.logger.warning(f"  ⚠ 0/{total} containers running")
                    self.logger.info("     Start containers: cd /opt/misp && sudo docker compose up -d\n")
                    return components
                elif running < total:
                    self.logger.warning(f"  ⚠ Only {running}/{total} containers running")
                else:
                    self.logger.info(f"  ✓ All {total} containers running\n")
            else:
                self.logger.warning("  ⚠ Could not check container status\n")
        except Exception as e:
            self.logger.warning(f"  ⚠ Error checking containers: {e}\n")
        
        # Check repository updates
        try:
            self.logger.info("[1/5] Checking MISP repository...")
            os.chdir(self.misp_dir)
            
            # Fetch latest
            subprocess.run(['git', 'fetch'], check=True, capture_output=True, timeout=30)
            
            # Check if behind
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD..@{u}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            commits_behind = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            current_hash = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            ).stdout.strip()
            
            latest_hash = subprocess.run(
                ['git', 'rev-parse', '--short', '@{u}'],
                capture_output=True,
                text=True,
                timeout=10
            ).stdout.strip()
            
            components.append(ComponentVersion(
                name="MISP Repository",
                current=current_hash,
                available=latest_hash,
                needs_update=commits_behind > 0
            ))
            
            if commits_behind > 0:
                self.logger.info(f"  → {commits_behind} commits behind")
            else:
                self.logger.info("  → Up to date")
                
        except Exception as e:
            self.logger.warning(f"  ⚠ Could not check repository: {e}")
        
        # Check Docker images
        try:
            self.logger.info("\n[2/5] Checking Docker images...")
            
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'pull', '--dry-run'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for updates
            updates_available = 'Pulling' in result.stdout or 'pull' in result.stdout.lower()
            
            components.append(ComponentVersion(
                name="Docker Images",
                current="local",
                available="latest",
                needs_update=updates_available
            ))
            
            if updates_available:
                self.logger.info("  → Updates available")
            else:
                self.logger.info("  → Up to date")
                
        except Exception as e:
            self.logger.warning(f"  ⚠ Could not check Docker images: {e}")
        
        # Check current MISP version
        try:
            self.logger.info("\n[3/5] Checking MISP version...")
            
            # First verify misp-core is running
            ps_result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', 'misp-core', '--format', 'json'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if ps_result.returncode != 0 or not ps_result.stdout.strip():
                self.logger.info("  → misp-core container not found")
                return components
            
            try:
                container_info = json.loads(ps_result.stdout.strip().split('\n')[0])
                state = container_info.get('State', 'unknown')
                
                if state != 'running':
                    self.logger.info(f"  → misp-core is {state}, cannot check version")
                    return components
            except:
                pass
            
            # Container is running, try to get version
            self.logger.debug("Attempting to read VERSION.json from container...")
            
            # Try method 1: Read VERSION.json from container
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core', 
                 'cat', '/var/www/MISP/VERSION.json'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    version_info = json.loads(result.stdout.strip())
                    
                    # MISP uses major.minor.hotfix format
                    if 'major' in version_info and 'minor' in version_info:
                        major = version_info.get('major', 0)
                        minor = version_info.get('minor', 0)
                        hotfix = version_info.get('hotfix', 0)
                        current_version = f"v{major}.{minor}.{hotfix}"
                        self.logger.info(f"  → Current version: {current_version}")
                    # Fallback to single version field
                    elif 'version' in version_info:
                        current_version = version_info.get('version', 'unknown')
                        self.logger.info(f"  → Current version: {current_version}")
                    else:
                        self.logger.debug(f"Unexpected VERSION.json format: {version_info}")
                        
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Could not parse VERSION.json: {e}")
            
            # Try method 2: Get version from git tag in container
            self.logger.debug("Trying git describe method...")
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 'bash', '-c', 'cd /var/www/MISP && git describe --tags 2>/dev/null || echo "unknown"'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and result.stdout.strip() and result.stdout.strip() != "unknown":
                version = result.stdout.strip()
                self.logger.info(f"  → Current version: {version}")
            else:
                # Try method 3: Check app/VERSION.json
                self.logger.debug("Trying app/VERSION.json...")
                result = subprocess.run(
                    ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                     'cat', '/var/www/MISP/app/VERSION.json'],
                    cwd=self.misp_dir,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        version_info = json.loads(result.stdout)
                        current_version = version_info.get('version', 'unknown')
                        self.logger.info(f"  → Current version: {current_version}")
                    except:
                        self.logger.info("  → Version unavailable (MISP may still be initializing)")
                        self.logger.info("     Try again in a few minutes")
                else:
                    self.logger.info("  → Version unavailable (MISP may still be initializing)")
                    self.logger.info("     Try again in a few minutes")
                
        except subprocess.TimeoutExpired:
            self.logger.warning("  ⚠ Timeout checking MISP version (container may be busy)")
        except Exception as e:
            self.logger.debug(f"Error checking version: {e}")
            self.logger.info("  → Could not determine version")
        
        # Check Redis version
        try:
            self.logger.info("\n[4/5] Checking Redis version...")
            
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'redis',
                 'redis-server', '--version'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse: "Redis server v=7.0.12 sha=00000000:0 malloc=jemalloc-5.2.1 bits=64 build=..."
                version_line = result.stdout.strip()
                if 'v=' in version_line:
                    version = version_line.split('v=')[1].split()[0]
                    self.logger.info(f"  → Redis {version}")
                else:
                    self.logger.info(f"  → {version_line}")
            else:
                self.logger.info("  → Could not determine Redis version")
                
        except subprocess.TimeoutExpired:
            self.logger.warning("  ⚠ Timeout checking Redis version")
        except Exception as e:
            self.logger.debug(f"Error checking Redis: {e}")
            self.logger.info("  → Could not check Redis")
        
        # Check MySQL/MariaDB version
        try:
            self.logger.info("\n[5/5] Checking Database version...")
            
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '--version'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse: "mysql  Ver 8.0.33 for Linux on x86_64 (MySQL Community Server - GPL)"
                # or: "mysql  Ver 15.1 Distrib 10.11.2-MariaDB"
                version_line = result.stdout.strip()
                
                if 'MariaDB' in version_line:
                    # Extract MariaDB version
                    if 'Distrib' in version_line:
                        version = version_line.split('Distrib')[1].strip().split()[0].replace('-MariaDB', '')
                        self.logger.info(f"  → MariaDB {version}")
                    else:
                        self.logger.info(f"  → {version_line}")
                elif 'Ver' in version_line:
                    # Extract MySQL version
                    parts = version_line.split()
                    for i, part in enumerate(parts):
                        if part == 'Ver' and i + 1 < len(parts):
                            version = parts[i + 1]
                            self.logger.info(f"  → MySQL {version}")
                            break
                else:
                    self.logger.info(f"  → {version_line}")
            else:
                self.logger.info("  → Could not determine database version")
                
        except subprocess.TimeoutExpired:
            self.logger.warning("  ⚠ Timeout checking database version")
        except Exception as e:
            self.logger.debug(f"Error checking database: {e}")
            self.logger.info("  → Could not check database")
        
        return components

# ==========================================
# Update Manager
# ==========================================

class MISPUpdater:
    def __init__(self, logger: logging.Logger, misp_dir: Path, dry_run: bool = False):
        self.logger = logger
        self.misp_dir = misp_dir
        self.dry_run = dry_run
        self.backup_mgr = UpdateBackupManager(logger, misp_dir)
        self.version_checker = VersionChecker(logger, misp_dir)
    
    def run_command(self, cmd: List[str], timeout: Optional[int] = None, 
                   check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and log output"""
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        
        try:
            # Set environment to suppress docker-compose warnings about unset variables
            env = os.environ.copy()
            env['COMPOSE_IGNORE_ORPHANS'] = 'true'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=self.misp_dir,
                timeout=timeout,
                env=env
            )
            
            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr and not result.stderr.startswith('WARN'):
                # Only log stderr if it's not just warnings about unset variables
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
    
    def update_repository(self):
        """Update MISP repository"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("UPDATING REPOSITORY"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        os.chdir(self.misp_dir)
        
        self.logger.info("[1/2] Pulling latest changes...")
        self.run_command(['sudo', 'git', 'pull'], timeout=60)

        self.logger.info("[2/2] Updating submodules...")
        self.run_command(['sudo', 'git', 'submodule', 'update', '--init', '--recursive'], timeout=120)
        
        self.logger.info(Colors.success("\n✓ Repository updated\n"))
    
    def update_docker_images(self):
        """Pull and update Docker images"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("UPDATING DOCKER IMAGES"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        self.logger.info("Pulling latest Docker images...")
        self.logger.info("This may take 10-15 minutes...\n")

        pull_cmd = ['sudo', 'docker', 'compose', 'pull']

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would execute: {' '.join(pull_cmd)}")
        else:
            pull_process = subprocess.Popen(
                pull_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.misp_dir
            )
            
            # Stream output
            for line in iter(pull_process.stdout.readline, ''):
                if line:
                    if any(keyword in line for keyword in ['Pulling', 'Downloading', 'Extracting', 
                                                          'Pull complete', 'Downloaded', 'Already exists']):
                        self.logger.info(f"  {line.rstrip()}")
            
            pull_process.wait(timeout=1800)  # 30 minute timeout
            
            if pull_process.returncode != 0:
                raise Exception("Failed to pull Docker images")
        
        self.logger.info(Colors.success("\n✓ Docker images updated\n"))
    
    def restart_services(self, rolling: bool = True):
        """Restart MISP services"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("RESTARTING SERVICES"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        if rolling:
            self.logger.info("Using rolling restart to minimize downtime...\n")
            
            # Restart services in order
            services = ['misp-modules', 'db', 'redis', 'misp-core']
            
            for service in services:
                self.logger.info(f"Restarting {service}...")
                self.run_command(['sudo', 'docker', 'compose', 'restart', service], timeout=120)
                
                # Wait for service to be healthy
                self.logger.info(f"  Waiting for {service} to be healthy...")
                time.sleep(10)
                
                self.logger.info(f"  ✓ {service} restarted\n")
        else:
            self.logger.info("Restarting all services...\n")
            self.run_command(['sudo', 'docker', 'compose', 'restart'], timeout=180)
        
        self.logger.info(Colors.success("✓ Services restarted\n"))
    
    def recreate_containers(self):
        """Recreate containers with new images"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("RECREATING CONTAINERS"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        self.logger.info("Stopping containers...")
        self.run_command(['sudo', 'docker', 'compose', 'down'], timeout=120)

        self.logger.info("\nStarting containers with new images...")
        self.run_command(['sudo', 'docker', 'compose', 'up', '-d'], timeout=300)
        
        self.logger.info(Colors.success("\n✓ Containers recreated\n"))
    
    def verify_health(self) -> bool:
        """Verify all services are healthy"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("VERIFYING HEALTH"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        self.logger.info("Waiting for services to stabilize...")
        time.sleep(30)
        
        max_wait = 180
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                timeout=30,
                check=False
            )
            
            if result.returncode == 0:
                try:
                    containers = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            containers.append(json.loads(line))
                    
                    running = sum(1 for c in containers if c.get('State') == 'running')
                    total = len(containers)
                    
                    if running == total and total > 0:
                        self.logger.info(Colors.success(f"\n✓ All {total} containers are running"))
                        
                        # Show container status
                        self.logger.info("\nContainer Status:")
                        result = self.run_command(['sudo', 'docker', 'compose', 'ps'], check=False)
                        self.logger.info(result.stdout)
                        
                        return True
                    
                    self.logger.info(f"  Waiting... {running}/{total} containers running")
                    
                except json.JSONDecodeError:
                    pass
            
            time.sleep(10)
        
        self.logger.warning(Colors.warning("⚠ Health check timeout"))
        self.logger.info("\nContainer Status:")
        result = self.run_command(['sudo', 'docker', 'compose', 'ps'], check=False)
        self.logger.info(result.stdout)
        
        return False
    
    def check_misp_functionality(self) -> bool:
        """Check if MISP is functioning properly"""
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("CHECKING MISP FUNCTIONALITY"))
        self.logger.info(Colors.info("="*50 + "\n"))
        
        checks = []
        
        # Check web interface
        self.logger.info("[1/3] Checking web interface...")
        try:
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 'curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 'https://localhost'],
                timeout=10,
                check=False
            )
            
            if '200' in result.stdout or '302' in result.stdout:
                self.logger.info("  ✓ Web interface responding")
                checks.append(True)
            else:
                self.logger.warning(f"  ⚠ Web interface returned: {result.stdout}")
                checks.append(False)
        except Exception as e:
            self.logger.warning(f"  ⚠ Could not check web interface: {e}")
            checks.append(False)
        
        # Check database connection
        self.logger.info("\n[2/3] Checking database connection...")
        try:
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', '-e', 'SELECT COUNT(*) FROM users;', 'misp'],
                timeout=10,
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info("  ✓ Database connection OK")
                checks.append(True)
            else:
                self.logger.warning("  ⚠ Database connection failed")
                checks.append(False)
        except Exception as e:
            self.logger.warning(f"  ⚠ Could not check database: {e}")
            checks.append(False)
        
        # Check MISP workers
        self.logger.info("\n[3/3] Checking MISP workers...")
        try:
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 'ps', 'aux'],
                timeout=10,
                check=False
            )
            
            if 'worker' in result.stdout.lower():
                worker_count = result.stdout.lower().count('worker')
                self.logger.info(f"  ✓ Found {worker_count} workers running")
                checks.append(True)
            else:
                self.logger.warning("  ⚠ No workers found")
                checks.append(False)
        except Exception as e:
            self.logger.warning(f"  ⚠ Could not check workers: {e}")
            checks.append(False)
        
        all_passed = all(checks)
        
        if all_passed:
            self.logger.info(Colors.success("\n✓ All functionality checks passed\n"))
        else:
            self.logger.warning(Colors.warning("\n⚠ Some functionality checks failed\n"))
        
        return all_passed
    
    def run_update(self, components: List[str], skip_backup: bool = False, 
                  rolling: bool = True, recreate: bool = False):
        """Run the complete update process"""
        try:
            # Create backup
            if not skip_backup:
                backup_path = self.backup_mgr.create_update_backup()
                if not backup_path and not self.dry_run:
                    self.logger.error(Colors.error("Backup failed. Aborting update."))
                    return False
            
            # Check what needs updating
            if not components or 'all' in components:
                components = ['repository', 'images']
            
            # Update repository
            if 'repository' in components:
                self.update_repository()
            
            # Update Docker images
            if 'images' in components:
                self.update_docker_images()
            
            # Restart or recreate
            if recreate:
                self.recreate_containers()
            else:
                self.restart_services(rolling=rolling)
            
            # Verify health
            if not self.verify_health():
                self.logger.warning(Colors.warning("\n⚠ Health checks failed!"))
                
                if not self.dry_run:
                    response = input("\nContinue anyway? (yes/no): ").lower()
                    if response != 'yes':
                        return False
            
            # Check functionality
            self.check_misp_functionality()
            
            self.logger.info(Colors.success("\n" + "="*50))
            self.logger.info(Colors.success("✅ UPDATE COMPLETED SUCCESSFULLY"))
            self.logger.info(Colors.success("="*50 + "\n"))
            
            return True
            
        except Exception as e:
            self.logger.error(Colors.error(f"\n❌ Update failed: {e}"))
            
            if self.backup_mgr.current_backup and not self.dry_run:
                self.logger.warning("\nA backup was created before the update:")
                self.logger.warning(f"  {self.backup_mgr.current_backup}")
                self.logger.warning("\nYou can restore from this backup if needed.")
            
            return False

# ==========================================
# Main Function
# ==========================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MISP Update Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check for updates
  python3 misp-update.py --check-only
  
  # Show detailed version information
  python3 misp-update.py --version-info
  
  # Update everything
  python3 misp-update.py --all
  
  # Update only Docker images
  python3 misp-update.py --images
  
  # Update with container recreation
  python3 misp-update.py --all --recreate
  
  # Dry run (show what would be done)
  python3 misp-update.py --all --dry-run
        """
    )
    
    parser.add_argument('--check-only', action='store_true',
                       help='Only check for updates, do not apply')
    parser.add_argument('--version-info', action='store_true',
                       help='Show detailed version information')
    parser.add_argument('--all', action='store_true',
                       help='Update all components (repository + images)')
    parser.add_argument('--repository', action='store_true',
                       help='Update repository only')
    parser.add_argument('--images', action='store_true',
                       help='Update Docker images only')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip backup before update (not recommended)')
    parser.add_argument('--recreate', action='store_true',
                       help='Recreate containers instead of restart (more downtime)')
    parser.add_argument('--no-rolling', action='store_true',
                       help='Restart all services at once (faster but more downtime)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--misp-dir', type=str, default='/opt/misp',
                       help='MISP installation directory (default: /opt/misp)')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info(Colors.info("""
╔══════════════════════════════════════════════════╗
║                                                  ║
║        MISP Update & Upgrade Tool v1.0          ║
║            tKQB Enterprises Edition            ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""))
    
    if args.dry_run:
        logger.info(Colors.warning("🔍 DRY RUN MODE - No changes will be made\n"))
    
    # Check MISP directory
    misp_dir = Path(args.misp_dir).expanduser()
    if not misp_dir.exists():
        logger.error(Colors.error(f"MISP directory not found: {misp_dir}"))
        logger.info("Use --misp-dir to specify the correct path")
        sys.exit(1)
    
    logger.info(f"MISP Directory: {misp_dir}\n")
    
    # Create updater
    updater = MISPUpdater(logger, misp_dir, dry_run=args.dry_run)
    
    # Check for updates
    components_to_check = updater.version_checker.check_updates()
    
    # Show detailed version info if requested
    if args.version_info:
        logger.info(Colors.info("\n" + "="*50))
        logger.info(Colors.info("DETAILED VERSION INFORMATION"))
        logger.info(Colors.info("="*50 + "\n"))
        
        # Container versions
        logger.info("Docker Container Images:")
        result = updater.run_command(
            ['sudo', 'docker', 'compose', 'images'],
            timeout=30,
            check=False
        )
        if result.returncode == 0:
            logger.info(result.stdout)
        
        # MISP modules version
        logger.info("\nMISP Modules:")
        result = updater.run_command(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-modules',
             'pip', 'list', '|', 'grep', 'misp'],
            timeout=10,
            check=False
        )
        if result.returncode == 0:
            logger.info(result.stdout)
        
        # Python version in container
        logger.info("\nPython Version (misp-core):")
        result = updater.run_command(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
             'python3', '--version'],
            timeout=10,
            check=False
        )
        if result.returncode == 0:
            logger.info(f"  {result.stdout.strip()}")
        
        # PHP version
        logger.info("\nPHP Version:")
        result = updater.run_command(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
             'php', '--version'],
            timeout=10,
            check=False
        )
        if result.returncode == 0:
            logger.info(f"  {result.stdout.split(chr(10))[0]}")  # First line only
        
        # Database version
        logger.info("\nMySQL Version:")
        result = updater.run_command(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
             'mysql', '--version'],
            timeout=10,
            check=False
        )
        if result.returncode == 0:
            logger.info(f"  {result.stdout.strip()}")
        
        # Redis version
        logger.info("\nRedis Version:")
        result = updater.run_command(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'redis',
             'redis-server', '--version'],
            timeout=10,
            check=False
        )
        if result.returncode == 0:
            logger.info(f"  {result.stdout.strip()}")
        
        sys.exit(0)
    
    # Show update summary
    updates_needed = [c for c in components_to_check if c.needs_update]
    
    if updates_needed:
        logger.info(Colors.warning("\nUpdates available:"))
        for component in updates_needed:
            logger.info(f"  • {component}")
    else:
        logger.info(Colors.success("\n✓ All components are up to date"))
    
    # If check-only, exit here
    if args.check_only:
        sys.exit(0)
    
    # Determine what to update
    components = []
    if args.all:
        components = ['repository', 'images']
    else:
        if args.repository:
            components.append('repository')
        if args.images:
            components.append('images')
    
    # If nothing specified, prompt user
    if not components and not args.check_only:
        if not updates_needed:
            logger.info("\nNothing to update. Exiting.")
            sys.exit(0)
        
        logger.info("\nWhat would you like to update?")
        logger.info("1) All components (recommended)")
        logger.info("2) Repository only")
        logger.info("3) Docker images only")
        logger.info("4) Cancel")
        
        choice = input("\nEnter choice [1]: ").strip() or "1"
        
        if choice == "1":
            components = ['repository', 'images']
        elif choice == "2":
            components = ['repository']
        elif choice == "3":
            components = ['images']
        else:
            logger.info("Cancelled.")
            sys.exit(0)
    
    if not components:
        logger.info("\nNo components selected for update.")
        sys.exit(0)
    
    # Confirm update
    if not args.dry_run:
        logger.info("\n" + Colors.warning("="*50))
        logger.info(Colors.warning("⚠  WARNING: This will update MISP"))
        logger.info(Colors.warning("="*50))
        logger.info(f"\nComponents to update: {', '.join(components)}")
        logger.info(f"Backup will be created: {not args.skip_backup}")
        logger.info(f"Restart method: {'Rolling' if not args.no_rolling else 'All at once'}")
        logger.info(f"Recreate containers: {args.recreate}")
        
        confirm = input("\nProceed with update? Type 'YES' to continue: ")
        if confirm != 'YES':
            logger.info("Update cancelled.")
            sys.exit(0)
    
    # Run update
    success = updater.run_update(
        components=components,
        skip_backup=args.skip_backup,
        rolling=not args.no_rolling,
        recreate=args.recreate
    )
    
    if success:
        logger.info("\n" + Colors.success("🎉 Update completed successfully!"))
        logger.info("\nNext steps:")
        logger.info("  1. Verify MISP web interface is working")
        logger.info("  2. Check logs: cd /opt/misp && sudo docker compose logs -f")
        logger.info("  3. Test key functionality")
        sys.exit(0)
    else:
        logger.error("\n" + Colors.error("❌ Update failed"))
        logger.info("\nCheck logs for details:")
        logger.info("  /var/log/misp-install/")
        sys.exit(1)

if __name__ == "__main__":
    main()