#!/usr/bin/env python3
"""
MISP Backup Script
tKQB Enterprises - Complete Backup Solution
Version: 3.0 (Python with Centralized Logging)

Simple, standalone backup script for MISP installations.
"""

import os
import sys
import subprocess
import shutil
import tarfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# Import centralized logger
from misp_logger import get_logger

# ==========================================
# Configuration
# ==========================================

class BackupConfig:
    """Backup configuration"""
    MISP_DIR = Path("/opt/misp")
    BACKUP_BASE_DIR = Path.home() / "misp-backups"
    RETENTION_DAYS = 30

# ==========================================
# Backup Manager
# ==========================================

class MISPBackup:
    """Simple MISP backup manager"""

    def __init__(self):
        self.config = BackupConfig()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"misp-backup-{self.timestamp}"
        self.backup_dir = self.config.BACKUP_BASE_DIR / self.backup_name
        self.archive_path = self.config.BACKUP_BASE_DIR / f"{self.backup_name}.tar.gz"

    def log(self, message: str, level: str = "info"):
        """Print colored log message"""
        if level == "error":
            print(Colors.error(message))
        elif level == "success":
            print(Colors.success(message))
        elif level == "warning":
            print(Colors.warning(message))
        else:
            print(Colors.info(message))

    def check_misp_dir(self) -> bool:
        """Check if MISP directory exists"""
        if not self.config.MISP_DIR.exists():
            self.log(f"MISP directory not found: {self.config.MISP_DIR}", "error")
            return False
        return True

    def create_backup_dir(self):
        """Create backup directory"""
        self.log(f"Creating backup directory: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

    def backup_configuration(self):
        """Backup configuration files"""
        self.log("Backing up configuration files...")

        files = ['.env', 'PASSWORDS.txt', 'docker-compose.yml', 'docker-compose.override.yml']

        for file in files:
            src = self.config.MISP_DIR / file
            if src.exists():
                shutil.copy2(src, self.backup_dir / file)
                self.log(f"Backed up {file}", "success")
            else:
                self.log(f"{file} not found", "warning")

    def backup_ssl_certificates(self):
        """Backup SSL certificates"""
        self.log("Backing up SSL certificates...")

        ssl_dir = self.config.MISP_DIR / "ssl"
        if ssl_dir.exists():
            try:
                # Use sudo to copy SSL files due to permission restrictions
                subprocess.run(
                    ['sudo', 'cp', '-r', str(ssl_dir), str(self.backup_dir / "ssl")],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
                # Fix ownership of copied files
                subprocess.run(
                    ['sudo', 'chown', '-R', f'{os.getuid()}:{os.getgid()}', str(self.backup_dir / "ssl")],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                self.log("Backed up SSL certificates", "success")
            except Exception as e:
                self.log(f"Failed to backup SSL: {e}", "warning")
        else:
            self.log("SSL directory not found", "warning")

    def get_mysql_password(self) -> Optional[str]:
        """Get MySQL password from .env file"""
        env_file = self.config.MISP_DIR / ".env"
        if not env_file.exists():
            return None

        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('MYSQL_PASSWORD='):
                    return line.split('=', 1)[1].strip()
        return None

    def is_container_running(self, container: str) -> bool:
        """Check if Docker container is running"""
        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps', container],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )
            return 'Up' in result.stdout
        except Exception:
            return False

    def backup_database(self) -> bool:
        """Backup MySQL database"""
        self.log("Backing up MySQL database...")

        if not self.is_container_running('db'):
            self.log("Database container is not running, skipping database backup", "warning")
            return False

        mysql_password = self.get_mysql_password()
        if not mysql_password:
            self.log("MySQL password not found in .env", "warning")
            return False

        self.log("Dumping database (this may take a few minutes)...")

        db_file = self.backup_dir / "misp_database.sql"

        try:
            with open(db_file, 'w') as f:
                result = subprocess.run(
                    ['docker', 'compose', 'exec', '-T', 'db',
                     'mysqldump', '-umisp', f'-p{mysql_password}',
                     '--single-transaction', '--quick', '--lock-tables=false', 'misp'],
                    cwd=self.config.MISP_DIR,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    timeout=600
                )

            if result.returncode == 0:
                size_mb = db_file.stat().st_size / (1024 * 1024)
                self.log(f"Database backed up successfully ({size_mb:.1f} MB)", "success")
                return True
            else:
                self.log("Database backup failed", "error")
                return False

        except Exception as e:
            self.log(f"Database backup failed: {e}", "error")
            return False

    def backup_attachments(self):
        """Backup MISP attachments"""
        self.log("Backing up MISP attachments...")

        # Check if misp-core container is accessible
        try:
            result = subprocess.run(
                ['docker', 'compose', 'exec', '-T', 'misp-core',
                 'test', '-d', '/var/www/MISP/app/files'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                timeout=10
            )

            if result.returncode != 0:
                self.log("Attachments directory not accessible", "warning")
                return

            self.log("Copying attachments from container...")

            # Create attachments directory
            attach_dir = self.backup_dir / "attachments"
            attach_dir.mkdir(exist_ok=True)

            # Copy attachments from container
            result = subprocess.run(
                ['docker', 'compose', 'cp', 'misp-core:/var/www/MISP/app/files', str(attach_dir) + '/'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                timeout=300
            )

            if result.returncode == 0 and attach_dir.exists():
                # Calculate size
                total_size = sum(f.stat().st_size for f in attach_dir.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                self.log(f"Attachments backed up successfully ({size_mb:.1f} MB)", "success")
            else:
                self.log("Could not backup attachments (container might not be running)", "warning")

        except Exception as e:
            self.log(f"Attachments backup failed: {e}", "warning")

    def create_backup_metadata(self):
        """Create backup metadata file"""
        self.log("Creating backup metadata...")

        # Get container status
        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )
            container_status = result.stdout
        except:
            container_status = "Could not get container status"

        # Get disk usage
        try:
            result = subprocess.run(
                ['df', '-h', str(self.config.MISP_DIR)],
                capture_output=True,
                text=True,
                timeout=5
            )
            disk_usage = result.stdout.split('\n')[1] if result.returncode == 0 else "Unknown"
        except:
            disk_usage = "Unknown"

        # Calculate backup size
        total_size = sum(f.stat().st_size for f in self.backup_dir.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)

        metadata = f"""MISP Backup Information
=======================
Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup Directory: {self.backup_dir}
MISP Directory: {self.config.MISP_DIR}
Hostname: {os.uname().nodename}

Backup Contents:
- Configuration files (.env, docker-compose.yml)
- SSL certificates
- MySQL database dump
- Attachments (if accessible)

Container Status at Backup Time:
{container_status}

Disk Usage:
{disk_usage}

Backup Size: {size_mb:.1f} MB
"""

        metadata_file = self.backup_dir / "backup_info.txt"
        metadata_file.write_text(metadata)

        self.log("Backup metadata created", "success")

    def compress_backup(self) -> bool:
        """Compress backup directory"""
        self.log("Compressing backup...")

        try:
            with tarfile.open(self.archive_path, "w:gz") as tar:
                tar.add(self.backup_dir, arcname=self.backup_name)

            # Remove uncompressed directory
            shutil.rmtree(self.backup_dir)

            archive_size_mb = self.archive_path.stat().st_size / (1024 * 1024)
            self.log(f"Backup compressed: {self.archive_path.name} ({archive_size_mb:.1f} MB)", "success")

            print()
            print("=" * 50)
            print(Colors.colored("BACKUP COMPLETED SUCCESSFULLY", Colors.GREEN))
            print("=" * 50)
            print(f"Location: {self.archive_path}")
            print(f"Size: {archive_size_mb:.1f} MB")
            print()

            return True

        except Exception as e:
            self.log(f"Failed to compress backup: {e}", "error")
            return False

    def verify_backup(self) -> bool:
        """Verify backup archive integrity"""
        self.log("Verifying backup integrity...")

        try:
            with tarfile.open(self.archive_path, "r:gz") as tar:
                tar.getmembers()  # Try to read archive

            self.log("Backup archive is valid", "success")
            return True

        except Exception as e:
            self.log(f"Backup archive is corrupted: {e}", "error")
            return False

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        self.log(f"Cleaning up backups older than {self.config.RETENTION_DAYS} days...")

        cutoff_date = datetime.now() - timedelta(days=self.config.RETENTION_DAYS)
        deleted_count = 0

        for backup_file in self.config.BACKUP_BASE_DIR.glob("misp-backup-*.tar.gz"):
            try:
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.log(f"Could not delete {backup_file.name}: {e}", "warning")

        if deleted_count > 0:
            self.log(f"Deleted {deleted_count} old backup(s)", "success")
        else:
            self.log("No old backups to delete")

    def run(self) -> bool:
        """Run complete backup process"""
        print("=" * 50)
        print("MISP Backup Script")
        print("=" * 50)
        print()

        if not self.check_misp_dir():
            return False

        try:
            self.create_backup_dir()
            self.backup_configuration()
            self.backup_ssl_certificates()
            self.backup_database()
            self.backup_attachments()
            self.create_backup_metadata()

            if not self.compress_backup():
                return False

            if not self.verify_backup():
                return False

            self.cleanup_old_backups()

            print()
            print("To restore this backup, run:")
            print(f"  cd {self.config.BACKUP_BASE_DIR}")
            print(f"  tar -xzf {self.backup_name}.tar.gz")
            print("  # Then use misp-restore.py to restore")
            print()

            self.log("Backup process completed!", "success")
            return True

        except KeyboardInterrupt:
            print()
            self.log("Backup interrupted by user", "warning")
            return False
        except Exception as e:
            self.log(f"Backup failed: {e}", "error")
            import traceback
            traceback.print_exc()
            return False

# ==========================================
# Main
# ==========================================

def main():
    """Main entry point"""
    backup = MISPBackup()
    success = backup.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
