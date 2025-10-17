"""
Backup management for MISP installation
Centralized backup operations using database_manager and docker_manager

This module provides unified backup/restore operations including:
- Configuration file backup/restore
- SSL certificate backup/restore
- Database backup/restore (via database_manager)
- Docker container status capture
- Backup listing and management
"""

import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from lib.colors import Colors

# Add parent directory for database_manager import
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from lib.database_manager import DatabaseManager
from lib.docker_manager import DockerCommandRunner


class BackupManager:
    """Manages backups of MISP installation using centralized managers"""

    def __init__(self, logger: logging.Logger, misp_dir: Path = Path("/opt/misp"),
                 backup_dir: Optional[Path] = None):
        """Initialize backup manager

        Args:
            logger: Logger instance
            misp_dir: MISP installation directory
            backup_dir: Backup directory. Defaults to ~/misp-backups
        """
        self.logger = logger
        self.misp_dir = Path(misp_dir)

        if backup_dir is None:
            backup_dir = Path.home() / "misp-backups"

        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

        # Initialize centralized managers
        self.db_manager = DatabaseManager(self.misp_dir)
        self.docker = DockerCommandRunner(logger)

    def create_backup(self, misp_dir: Path) -> Optional[Path]:
        """Create backup of existing MISP installation

        Args:
            misp_dir: MISP installation directory

        Returns:
            Path to backup directory or None if failed
        """
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

            # Backup database using DatabaseManager
            try:
                db_file = backup_path / "misp_database.sql"
                if self.db_manager.backup_database(db_file):
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

    def list_backups(self) -> list:
        """List all available backups

        Returns:
            List of backup directory paths
        """
        if not self.backup_dir.exists():
            return []

        backups = sorted(
            [d for d in self.backup_dir.iterdir() if d.is_dir() and d.name.startswith("misp-backup-")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        return backups

    def get_latest_backup(self) -> Optional[Path]:
        """Get most recent backup

        Returns:
            Path to latest backup or None
        """
        backups = self.list_backups()
        if backups:
            return backups[0]
        return None

    def restore_backup(self, backup_path: Path, misp_dir: Path) -> bool:
        """Restore backup to MISP directory

        Args:
            backup_path: Path to backup directory
            misp_dir: MISP installation directory

        Returns:
            True if successful
        """
        if not backup_path.exists():
            self.logger.error(Colors.error(f"Backup not found: {backup_path}"))
            return False

        self.logger.info(Colors.info(f"Restoring backup from: {backup_path}"))

        try:
            # Restore .env
            if (backup_path / ".env").exists():
                shutil.copy2(backup_path / ".env", misp_dir / ".env")
                self.logger.info("  ✓ Restored .env")

            # Restore PASSWORDS.txt
            if (backup_path / "PASSWORDS.txt").exists():
                shutil.copy2(backup_path / "PASSWORDS.txt", misp_dir / "PASSWORDS.txt")
                self.logger.info("  ✓ Restored PASSWORDS.txt")

            # Restore SSL certificates
            if (backup_path / "ssl").exists():
                ssl_dest = misp_dir / "ssl"
                if ssl_dest.exists():
                    shutil.rmtree(ssl_dest)
                shutil.copytree(backup_path / "ssl", ssl_dest)
                self.logger.info("  ✓ Restored SSL certificates")

            # Restore database using DatabaseManager
            if (backup_path / "misp_database.sql").exists():
                self.logger.info("  Restoring database...")
                if self.db_manager.restore_database(backup_path / "misp_database.sql"):
                    self.logger.info("  ✓ Restored database")
                else:
                    self.logger.warning("  ⚠ Database restore failed (might not be running)")
                    self.logger.info(f"  Manual restore: docker compose exec -T db mysql -umisp -p[password] misp < {backup_path / 'misp_database.sql'}")

            self.logger.info(Colors.success("Restore completed"))
            return True

        except Exception as e:
            self.logger.error(Colors.error(f"Restore failed: {e}"))
            return False

    def delete_backup(self, backup_path: Path) -> bool:
        """Delete a backup

        Args:
            backup_path: Path to backup directory

        Returns:
            True if successful
        """
        try:
            if backup_path.exists():
                shutil.rmtree(backup_path)
                self.logger.info(Colors.success(f"Deleted backup: {backup_path}"))
                return True
            else:
                self.logger.warning(f"Backup not found: {backup_path}")
                return False
        except Exception as e:
            self.logger.error(Colors.error(f"Failed to delete backup: {e}"))
            return False
