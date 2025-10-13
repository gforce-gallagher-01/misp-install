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
# Color Output (for terminal display only)
# ==========================================

class Colors:
    GREEN = '\033[0;32m'
    NC = '\033[0m'

    @staticmethod
    def colored(text: str, color: str) -> str:
        return f"{color}{text}{Colors.NC}"

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
        self.start_time = time.time()

        # Initialize centralized logger
        self.logger = get_logger('backup-misp', 'misp:backup')

        self.logger.info(
            "Backup initiated",
            event_type="backup",
            action="start",
            backup_name=self.backup_name
        )

    def check_misp_dir(self) -> bool:
        """Check if MISP directory exists"""
        if not self.config.MISP_DIR.exists():
            self.logger.error(
                f"MISP directory not found: {self.config.MISP_DIR}",
                event_type="backup",
                action="check_dir",
                file_path=str(self.config.MISP_DIR)
            )
            return False
        return True

    def create_backup_dir(self):
        """Create backup directory"""
        self.logger.info(
            f"Creating backup directory",
            event_type="backup",
            action="create_dir",
            file_path=str(self.backup_dir)
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

    def backup_configuration(self):
        """Backup configuration files"""
        self.logger.info(
            "Backing up configuration files",
            event_type="backup",
            phase="backup_config"
        )

        files = ['.env', 'PASSWORDS.txt', 'docker-compose.yml', 'docker-compose.override.yml']

        for file in files:
            src = self.config.MISP_DIR / file
            if src.exists():
                shutil.copy2(src, self.backup_dir / file)
                self.logger.success(
                    f"Backed up {file}",
                    event_type="backup",
                    action="backup_file",
                    component="config",
                    file_path=file
                )
            else:
                self.logger.warning(
                    f"{file} not found",
                    event_type="backup",
                    action="backup_file",
                    component="config",
                    file_path=file
                )

    def backup_ssl_certificates(self):
        """Backup SSL certificates

        SECURITY: SSL files are owned by misp-owner. We copy them with sudo
        and then set ownership to current user for backup portability.
        """
        self.logger.info("Backing up SSL certificates", event_type="backup", phase="backup_ssl")

        ssl_dir = self.config.MISP_DIR / "ssl"
        if ssl_dir.exists():
            try:
                # Use sudo to copy SSL files (owned by misp-owner)
                subprocess.run(
                    ['sudo', 'cp', '-r', str(ssl_dir), str(self.backup_dir / "ssl")],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
                # Fix ownership of copied files to current user for backup portability
                # SECURITY NOTE: Backup files should be owned by user running backup, not misp-owner
                current_user = os.environ.get('USER', os.getlogin())
                subprocess.run(
                    ['sudo', 'chown', '-R', f'{current_user}:{current_user}', str(self.backup_dir / "ssl")],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                self.logger.success("Backed up SSL certificates", event_type="backup", action="backup_ssl", component="ssl")
            except Exception as e:
                self.logger.warning(f"Failed to backup SSL: {e}", event_type="backup", action="backup_ssl", component="ssl", error_message=str(e))
        else:
            self.logger.warning("SSL directory not found", event_type="backup", action="backup_ssl", component="ssl")

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
        self.logger.info("Backing up MySQL database", event_type="backup", phase="backup_database")

        if not self.is_container_running('db'):
            self.logger.warning("Database container is not running, skipping database backup", event_type="backup", action="check_container", container="db")
            return False

        mysql_password = self.get_mysql_password()
        if not mysql_password:
            self.logger.warning("MySQL password not found in .env", event_type="backup", action="get_password", component="database")
            return False

        self.logger.info("Dumping database (this may take a few minutes)", event_type="backup", action="dump_database", component="database")

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
                self.logger.success(f"Database backed up successfully ({size_mb:.1f} MB)", event_type="backup", action="backup_database", component="database", bytes=int(size_mb * 1024 * 1024))
                return True
            else:
                self.logger.error("Database backup failed", event_type="backup", action="backup_database", component="database")
                return False

        except Exception as e:
            self.logger.error(f"Database backup failed: {e}", event_type="backup", action="backup_database", component="database", error_message=str(e))
            return False

    def backup_attachments(self):
        """Backup MISP attachments"""
        self.logger.info("Backing up MISP attachments", event_type="backup", phase="backup_attachments")

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
                self.logger.warning("Attachments directory not accessible", event_type="backup", action="check_attachments", component="attachments")
                return

            self.logger.info("Copying attachments from container", event_type="backup", action="copy_attachments", component="attachments")

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
                self.logger.success(f"Attachments backed up successfully ({size_mb:.1f} MB)", event_type="backup", action="backup_attachments", component="attachments", bytes=int(size_mb * 1024 * 1024))
            else:
                self.logger.warning("Could not backup attachments (container might not be running)", event_type="backup", action="backup_attachments", component="attachments")

        except Exception as e:
            self.logger.warning(f"Attachments backup failed: {e}", event_type="backup", action="backup_attachments", component="attachments", error_message=str(e))

    def create_backup_metadata(self):
        """Create backup metadata file"""
        self.logger.info("Creating backup metadata", event_type="backup", phase="create_metadata")

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

        self.logger.success("Backup metadata created", event_type="backup", action="create_metadata")

    def compress_backup(self) -> bool:
        """Compress backup directory"""
        self.logger.info("Compressing backup", event_type="backup", phase="compress")

        try:
            with tarfile.open(self.archive_path, "w:gz") as tar:
                tar.add(self.backup_dir, arcname=self.backup_name)

            # Remove uncompressed directory
            shutil.rmtree(self.backup_dir)

            archive_size_mb = self.archive_path.stat().st_size / (1024 * 1024)
            self.logger.success(f"Backup compressed: {self.archive_path.name} ({archive_size_mb:.1f} MB)", event_type="backup", action="compress", backup_name=self.archive_path.name, bytes=int(archive_size_mb * 1024 * 1024))

            print()
            print("=" * 50)
            print(Colors.colored("BACKUP COMPLETED SUCCESSFULLY", Colors.GREEN))
            print("=" * 50)
            print(f"Location: {self.archive_path}")
            print(f"Size: {archive_size_mb:.1f} MB")
            print()

            return True

        except Exception as e:
            self.logger.error(f"Failed to compress backup: {e}", event_type="backup", action="compress", error_message=str(e))
            return False

    def verify_backup(self) -> bool:
        """Verify backup archive integrity"""
        self.logger.info("Verifying backup integrity", event_type="backup", phase="verify")

        try:
            with tarfile.open(self.archive_path, "r:gz") as tar:
                tar.getmembers()  # Try to read archive

            self.logger.success("Backup archive is valid", event_type="backup", action="verify")
            return True

        except Exception as e:
            self.logger.error(f"Backup archive is corrupted: {e}", event_type="backup", action="verify", error_message=str(e))
            return False

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        self.logger.info(f"Cleaning up backups older than {self.config.RETENTION_DAYS} days", event_type="backup", phase="cleanup")

        cutoff_date = datetime.now() - timedelta(days=self.config.RETENTION_DAYS)
        deleted_count = 0

        for backup_file in self.config.BACKUP_BASE_DIR.glob("misp-backup-*.tar.gz"):
            try:
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.logger.warning(f"Could not delete {backup_file.name}: {e}", event_type="backup", action="delete_old", file_path=backup_file.name, error_message=str(e))

        if deleted_count > 0:
            self.logger.success(f"Deleted {deleted_count} old backup(s)", event_type="backup", action="cleanup", count=deleted_count)
        else:
            self.logger.info("No old backups to delete", event_type="backup", action="cleanup", count=0)

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

            duration = time.time() - self.start_time
            self.logger.success("Backup process completed!", event_type="backup", action="complete", duration=duration, backup_name=self.backup_name)
            return True

        except KeyboardInterrupt:
            print()
            self.logger.warning("Backup interrupted by user", event_type="backup", action="interrupt")
            return False
        except Exception as e:
            self.logger.error(f"Backup failed: {e}", event_type="backup", action="complete", error_message=str(e))
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
