"""
Database Manager Module
Centralized MySQL/MariaDB database operations for MISP

This module provides a unified interface for all database operations,
eliminating duplicate code across scripts and ensuring consistent
database access patterns.

Usage:
    from lib.database_manager import DatabaseManager

    db = DatabaseManager()

    # Get MySQL password
    password = db.get_mysql_password()

    # Check database health
    if db.check_database():
        print("Database is accessible")

    # Execute SQL query
    result = db.execute_sql("SELECT COUNT(*) FROM events;")

    # Backup database
    db.backup_database(Path("/tmp/backup.sql"))

    # Restore database
    db.restore_database(Path("/tmp/backup.sql"))
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# Add scripts directory to path for imports
_script_dir = Path(__file__).parent.parent / "scripts"
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from misp_logger import get_logger  # noqa: E402


class DatabaseManager:
    """Manages MySQL database operations for MISP"""

    def __init__(self, misp_dir: Path = Path('/opt/misp')):
        """Initialize database manager

        Args:
            misp_dir: Path to MISP installation directory
        """
        self.misp_dir = Path(misp_dir)
        self.logger = get_logger('database-manager', 'misp:database')
        self._mysql_password = None

    def get_mysql_password(self) -> Optional[str]:
        """Get MySQL password from .env file

        Returns:
            MySQL password or None if not found
        """
        if self._mysql_password:
            return self._mysql_password

        env_file = self.misp_dir / ".env"
        if not env_file.exists():
            self.logger.warning(
                f".env file not found: {env_file}",
                event_type="database",
                action="get_password",
                result="failed"
            )
            return None

        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        self._mysql_password = line.split('=', 1)[1].strip()
                        return self._mysql_password
        except Exception as e:
            self.logger.error(
                f"Failed to read .env file: {e}",
                event_type="database",
                action="get_password",
                error_message=str(e)
            )

        return None

    def check_database(self) -> bool:
        """Check if database is accessible

        Returns:
            True if database can be reached, False otherwise
        """
        mysql_password = self.get_mysql_password()
        if not mysql_password:
            return False

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{mysql_password}',
                 '-e', 'SELECT 1;'],
                cwd=self.misp_dir,
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.debug(
                    "Database is accessible",
                    event_type="database",
                    action="check_database",
                    result="success"
                )
                return True
            else:
                self.logger.warning(
                    "Database check failed",
                    event_type="database",
                    action="check_database",
                    result="failed"
                )
                return False

        except Exception as e:
            self.logger.debug(
                f"Database check error: {e}",
                event_type="database",
                action="check_database",
                error_message=str(e)
            )
            return False

    def wait_for_database(self, max_attempts: int = 30, delay: int = 2) -> bool:
        """Wait for database to be ready

        Args:
            max_attempts: Maximum number of attempts
            delay: Delay in seconds between attempts

        Returns:
            True if database becomes ready, False if timeout
        """
        self.logger.info(
            f"Waiting for database (max {max_attempts * delay}s)",
            event_type="database",
            action="wait_for_database"
        )

        for attempt in range(max_attempts):
            if self.check_database():
                self.logger.success(
                    f"Database ready after {attempt * delay}s",
                    event_type="database",
                    action="wait_for_database",
                    result="success",
                    duration=attempt * delay
                )
                return True

            if attempt < max_attempts - 1:
                time.sleep(delay)

        self.logger.error(
            "Database did not become ready",
            event_type="database",
            action="wait_for_database",
            result="timeout"
        )
        return False

    def execute_sql(self, sql: str, database: str = "misp") -> subprocess.CompletedProcess:
        """Execute SQL command

        Args:
            sql: SQL query to execute
            database: Database name (default: misp)

        Returns:
            CompletedProcess with query results

        Raises:
            subprocess.CalledProcessError: If SQL execution fails
        """
        mysql_password = self.get_mysql_password()
        if not mysql_password:
            raise ValueError("MySQL password not found")

        result = subprocess.run(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
             'mysql', '-umisp', f'-p{mysql_password}', database, '-e', sql],
            cwd=self.misp_dir,
            capture_output=True,
            text=True,
            timeout=300,
            check=True
        )

        return result

    def backup_database(self, output_file: Path) -> bool:
        """Create database backup using mysqldump

        Args:
            output_file: Path to save backup file

        Returns:
            True if backup successful, False otherwise
        """
        mysql_password = self.get_mysql_password()
        if not mysql_password:
            self.logger.error(
                "MySQL password not found",
                event_type="database",
                action="backup_database",
                result="failed"
            )
            return False

        self.logger.info(
            f"Backing up database to {output_file}",
            event_type="database",
            action="backup_database",
            file_path=str(output_file)
        )

        try:
            with open(output_file, 'w') as f:
                result = subprocess.run(
                    ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                     'mysqldump', '-umisp', f'-p{mysql_password}',
                     '--single-transaction', '--quick', '--lock-tables=false', 'misp'],
                    cwd=self.misp_dir,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    timeout=600
                )

            if result.returncode == 0:
                size_mb = output_file.stat().st_size / (1024 * 1024)
                self.logger.success(
                    f"Database backed up successfully ({size_mb:.1f} MB)",
                    event_type="database",
                    action="backup_database",
                    result="success",
                    bytes=int(size_mb * 1024 * 1024)
                )
                return True
            else:
                self.logger.error(
                    "Database backup failed",
                    event_type="database",
                    action="backup_database",
                    result="failed"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Database backup failed: {e}",
                event_type="database",
                action="backup_database",
                error_message=str(e)
            )
            return False

    def restore_database(self, backup_file: Path) -> bool:
        """Restore database from backup

        Args:
            backup_file: Path to backup SQL file

        Returns:
            True if restore successful, False otherwise
        """
        mysql_password = self.get_mysql_password()
        if not mysql_password:
            self.logger.error(
                "MySQL password not found",
                event_type="database",
                action="restore_database",
                result="failed"
            )
            return False

        if not backup_file.exists():
            self.logger.error(
                f"Backup file not found: {backup_file}",
                event_type="database",
                action="restore_database",
                result="failed"
            )
            return False

        self.logger.info(
            f"Restoring database from {backup_file}",
            event_type="database",
            action="restore_database",
            file_path=str(backup_file)
        )

        try:
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            self.logger.info(
                f"Restoring database ({size_mb:.1f} MB)...",
                event_type="database",
                action="restore_database",
                bytes=int(size_mb * 1024 * 1024)
            )

            with open(backup_file, 'r') as f:
                result = subprocess.run(
                    ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                     'mysql', '-umisp', f'-p{mysql_password}', 'misp'],
                    cwd=self.misp_dir,
                    stdin=f,
                    capture_output=True,
                    timeout=600
                )

            if result.returncode == 0:
                self.logger.success(
                    "Database restored successfully",
                    event_type="database",
                    action="restore_database",
                    result="success"
                )
                return True
            else:
                self.logger.error(
                    "Database restore failed",
                    event_type="database",
                    action="restore_database",
                    result="failed"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Database restore failed: {e}",
                event_type="database",
                action="restore_database",
                error_message=str(e)
            )
            return False

    def get_table_count(self, table: str) -> Optional[int]:
        """Get row count for a table

        Args:
            table: Table name

        Returns:
            Row count or None if query fails
        """
        try:
            result = self.execute_sql(f"SELECT COUNT(*) FROM {table};")
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return int(lines[1].strip())
        except Exception as e:
            self.logger.warning(
                f"Failed to get count for table {table}: {e}",
                event_type="database",
                action="get_table_count",
                table=table
            )

        return None

    def table_exists(self, table: str) -> bool:
        """Check if table exists in database

        Args:
            table: Table name

        Returns:
            True if table exists, False otherwise
        """
        try:
            result = self.execute_sql(f"SHOW TABLES LIKE '{table}';")
            return table in result.stdout
        except Exception:
            return False
