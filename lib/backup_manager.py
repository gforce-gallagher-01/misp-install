"""
Backup management for MISP installation
"""

import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from lib.colors import Colors


class BackupManager:
    """Manages backups of MISP installation"""

    def __init__(self, logger: logging.Logger, backup_dir: Optional[Path] = None):
        """Initialize backup manager

        Args:
            logger: Logger instance
            backup_dir: Backup directory. Defaults to ~/misp-backups
        """
        self.logger = logger

        if backup_dir is None:
            backup_dir = Path.home() / "misp-backups"

        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

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

            # Restore database (requires MISP to be running)
            if (backup_path / "misp_database.sql").exists():
                self.logger.info("  Database restore requires manual import")
                self.logger.info(f"  Run: docker compose exec -T db mysql -umisp -ppassword misp < {backup_path / 'misp_database.sql'}")

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
