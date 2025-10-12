#!/usr/bin/env python3
"""
MISP Automated Backup Script
tKQB Enterprises Edition
Version: 1.0

Backup Strategy:
- Sunday: Full backup (keep 8 weeks)
- Monday-Saturday: Incremental backup (deleted after next Sunday)
- Automatic rotation and cleanup
- Email notifications (optional)
- Verification checks

Usage:
  python3 misp-backup-cron.py [--full] [--dry-run] [--notify]
  
Cron Setup:
  # Run nightly at 2 AM
  0 2 * * * /usr/bin/python3 /opt/misp/scripts/misp-backup-cron.py >> /var/log/misp-install/backup-cron.log 2>&1
"""

import os
import sys
import subprocess
import logging
import json
import shutil
import fcntl
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# ==========================================
# Configuration
# ==========================================

class BackupConfig:
    """Centralized backup configuration"""

    # Directories
    MISP_DIR = Path("/opt/misp")
    BACKUP_BASE_DIR = Path.home() / "misp-backups"
    FULL_BACKUP_DIR = BACKUP_BASE_DIR / "full"
    INCREMENTAL_BACKUP_DIR = BACKUP_BASE_DIR / "incremental"
    LOG_DIR = Path("/var/log/misp-install")

    # Retention
    FULL_BACKUP_WEEKS = 8  # Keep 8 weeks of Sunday backups

    # Lock file
    LOCK_FILE = Path.home() / ".misp-install" / "misp-backup.lock"
    
    # Email notifications (set to None to disable)
    EMAIL_ENABLED = False
    EMAIL_FROM = "misp-backup@example.com"
    EMAIL_TO = ["youremail@yourdomain.com"]
    SMTP_SERVER = "localhost"
    SMTP_PORT = 25
    SMTP_USER = None  # Set if authentication required
    SMTP_PASSWORD = None
    
    # What to backup
    FILES_TO_BACKUP = [
        '.env',
        'PASSWORDS.txt',
        'docker-compose.yml',
        'docker-compose.override.yml'
    ]
    
    DIRS_TO_BACKUP = [
        'ssl'
    ]

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
    try:
        BackupConfig.LOG_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
    except PermissionError:
        # Fallback to user's home directory if /var/log is not writable
        BackupConfig.LOG_DIR = Path.home() / ".misp-install" / "logs"
        BackupConfig.LOG_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = BackupConfig.LOG_DIR / f"misp-backup-{timestamp}.log"
    
    logger = logging.getLogger('MISP-Backup')
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(fh_formatter)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(message)s')
    ch.setFormatter(ch_formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    logger.info(f"Logging to: {log_file}")
    
    return logger

# ==========================================
# Lock Manager
# ==========================================

class LockManager:
    """Prevent concurrent backup runs"""
    
    def __init__(self, lock_file: Path, logger: logging.Logger):
        self.lock_file = lock_file
        self.logger = logger
        self.lock_fd = None
    
    def acquire(self) -> bool:
        """Acquire lock"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
            return True
        except IOError:
            self.logger.error("Another backup is already running")
            return False
    
    def release(self):
        """Release lock"""
        if self.lock_fd:
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
            self.lock_fd.close()
            if self.lock_file.exists():
                self.lock_file.unlink()

# ==========================================
# Notification Manager
# ==========================================

class NotificationManager:
    """Send email notifications"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = BackupConfig
    
    def send_notification(self, subject: str, body: str, is_error: bool = False):
        """Send email notification"""
        if not self.config.EMAIL_ENABLED:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_FROM
            msg['To'] = ', '.join(self.config.EMAIL_TO)
            msg['Subject'] = f"[MISP Backup] {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            
            if self.config.SMTP_USER:
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Notification sent: {subject}")
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")

# ==========================================
# Backup Manager
# ==========================================

class MISPBackupManager:
    """Main backup management class"""
    
    def __init__(self, logger: logging.Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
        self.config = BackupConfig
        self.notifier = NotificationManager(logger)
        
        # Create directories
        self.config.FULL_BACKUP_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
        self.config.INCREMENTAL_BACKUP_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
    
    def is_sunday(self) -> bool:
        """Check if today is Sunday (0 = Monday, 6 = Sunday)"""
        return datetime.now().weekday() == 6
    
    def get_backup_type(self) -> str:
        """Determine backup type based on day"""
        return "full" if self.is_sunday() else "incremental"
    
    def create_backup_name(self, backup_type: str) -> str:
        """Generate backup directory name"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        day_name = datetime.now().strftime("%A").lower()
        
        if backup_type == "full":
            return f"full-{timestamp}"
        else:
            return f"incremental-{day_name}-{timestamp}"
    
    def get_mysql_password(self) -> Optional[str]:
        """Extract MySQL password from .env file"""
        env_file = self.config.MISP_DIR / '.env'
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            self.logger.error(f"Could not read MySQL password: {e}")
        
        return None
    
    def backup_database(self, backup_dir: Path) -> bool:
        """Backup MySQL database"""
        self.logger.info("Backing up database...")
        
        mysql_password = self.get_mysql_password()
        if not mysql_password:
            self.logger.error("MySQL password not found")
            return False
        
        db_file = backup_dir / "misp_database.sql"
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would backup database to: {db_file}")
            return True
        
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysqldump', '-umisp', f'-p{mysql_password}', 
                 '--single-transaction', '--quick', '--lock-tables=false', 'misp'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                timeout=600
            )
            
            if result.returncode == 0:
                with open(db_file, 'wb') as f:
                    f.write(result.stdout)
                
                size_mb = db_file.stat().st_size / (1024 * 1024)
                self.logger.info(f"✓ Database backed up ({size_mb:.1f} MB)")
                return True
            else:
                self.logger.error(f"Database backup failed: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def backup_files(self, backup_dir: Path) -> bool:
        """Backup configuration files"""
        self.logger.info("Backing up configuration files...")
        
        success = True
        
        # Backup files
        for file in self.config.FILES_TO_BACKUP:
            src = self.config.MISP_DIR / file
            dst = backup_dir / file
            
            if src.exists():
                try:
                    if self.dry_run:
                        self.logger.info(f"[DRY RUN] Would backup: {file}")
                    else:
                        shutil.copy2(src, dst)
                        self.logger.info(f"✓ Backed up: {file}")
                except Exception as e:
                    self.logger.error(f"Failed to backup {file}: {e}")
                    success = False
            else:
                self.logger.warning(f"Not found: {file}")
        
        # Backup directories
        for dir_name in self.config.DIRS_TO_BACKUP:
            src = self.config.MISP_DIR / dir_name
            dst = backup_dir / dir_name
            
            if src.exists():
                try:
                    if self.dry_run:
                        self.logger.info(f"[DRY RUN] Would backup directory: {dir_name}")
                    else:
                        shutil.copytree(src, dst)
                        self.logger.info(f"✓ Backed up directory: {dir_name}")
                except Exception as e:
                    self.logger.error(f"Failed to backup {dir_name}: {e}")
                    success = False
            else:
                self.logger.warning(f"Not found: {dir_name}")
        
        return success
    
    def get_version_info(self) -> Dict:
        """Get current MISP version information"""
        versions = {}
        
        try:
            # Get MISP version
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 'cat', '/var/www/MISP/VERSION.json'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10,
                stderr=subprocess.DEVNULL
            )
            
            if result.returncode == 0:
                version_data = json.loads(result.stdout.strip())
                versions['misp'] = f"v{version_data['major']}.{version_data['minor']}.{version_data['hotfix']}"
        except:
            pass
        
        return versions
    
    def create_metadata(self, backup_dir: Path, backup_type: str) -> bool:
        """Create backup metadata file"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "backup_type": backup_type,
            "backup_path": str(backup_dir),
            "misp_dir": str(self.config.MISP_DIR),
            "versions": self.get_version_info(),
            "day_of_week": datetime.now().strftime("%A"),
            "hostname": os.uname().nodename
        }
        
        metadata_file = backup_dir / "metadata.json"
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create metadata: {metadata_file}")
            return True
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create metadata: {e}")
            return False
    
    def verify_backup(self, backup_dir: Path) -> bool:
        """Verify backup integrity"""
        self.logger.info("Verifying backup...")
        
        checks = []
        
        # Check database file exists and has content
        db_file = backup_dir / "misp_database.sql"
        if db_file.exists() and db_file.stat().st_size > 1024:  # At least 1KB
            checks.append(True)
            self.logger.info(f"✓ Database backup verified ({db_file.stat().st_size / (1024*1024):.1f} MB)")
        else:
            checks.append(False)
            self.logger.error("✗ Database backup missing or too small")
        
        # Check critical files
        critical_files = ['.env', 'PASSWORDS.txt']
        for file in critical_files:
            file_path = backup_dir / file
            if file_path.exists():
                checks.append(True)
                self.logger.info(f"✓ {file} present")
            else:
                checks.append(False)
                self.logger.error(f"✗ {file} missing")
        
        # Check metadata
        metadata_file = backup_dir / "metadata.json"
        if metadata_file.exists():
            checks.append(True)
            self.logger.info("✓ Metadata present")
        else:
            checks.append(False)
            self.logger.error("✗ Metadata missing")
        
        return all(checks)
    
    def get_backup_size(self, backup_dir: Path) -> int:
        """Calculate total backup size in bytes"""
        total = 0
        for entry in backup_dir.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    
    def create_backup(self, backup_type: str) -> Optional[Path]:
        """Create a full or incremental backup"""
        self.logger.info(Colors.info("\n" + "="*60))
        self.logger.info(Colors.info(f"CREATING {backup_type.upper()} BACKUP"))
        self.logger.info(Colors.info("="*60 + "\n"))
        
        # Determine backup directory
        if backup_type == "full":
            parent_dir = self.config.FULL_BACKUP_DIR
        else:
            parent_dir = self.config.INCREMENTAL_BACKUP_DIR
        
        # Create backup name
        backup_name = self.create_backup_name(backup_type)
        backup_dir = parent_dir / backup_name
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create backup at: {backup_dir}")
        else:
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database
        if not self.backup_database(backup_dir):
            self.logger.error("Database backup failed")
            return None
        
        # Backup files
        if not self.backup_files(backup_dir):
            self.logger.error("File backup had errors")
            # Continue anyway - partial backup is better than none
        
        # Create metadata
        self.create_metadata(backup_dir, backup_type)
        
        # Verify backup
        if not self.dry_run:
            if not self.verify_backup(backup_dir):
                self.logger.error("Backup verification failed")
                return None
            
            # Calculate and log size
            size_bytes = self.get_backup_size(backup_dir)
            size_mb = size_bytes / (1024 * 1024)
            self.logger.info(f"\nTotal backup size: {size_mb:.1f} MB")
        
        self.logger.info(Colors.success(f"\n✓ {backup_type.capitalize()} backup completed: {backup_name}"))
        
        return backup_dir
    
    def cleanup_old_full_backups(self):
        """Remove full backups older than retention period"""
        self.logger.info(Colors.info("\nCleaning up old full backups..."))
        
        backups = sorted(self.config.FULL_BACKUP_DIR.glob("full-*"))
        
        if len(backups) <= self.config.FULL_BACKUP_WEEKS:
            self.logger.info(f"Only {len(backups)} full backups, keeping all")
            return
        
        # Keep newest N backups, delete the rest
        to_delete = backups[:-self.config.FULL_BACKUP_WEEKS]
        
        for backup in to_delete:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would delete: {backup.name}")
            else:
                try:
                    shutil.rmtree(backup)
                    self.logger.info(f"✓ Deleted old backup: {backup.name}")
                except Exception as e:
                    self.logger.error(f"Failed to delete {backup.name}: {e}")
        
        remaining = len(backups) - len(to_delete)
        self.logger.info(f"Keeping {remaining} most recent full backups")
    
    def cleanup_old_incrementals(self):
        """Remove all incremental backups (after Sunday full backup)"""
        self.logger.info(Colors.info("\nCleaning up incremental backups..."))
        
        backups = list(self.config.INCREMENTAL_BACKUP_DIR.glob("incremental-*"))
        
        if not backups:
            self.logger.info("No incremental backups to clean")
            return
        
        deleted_count = 0
        for backup in backups:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would delete: {backup.name}")
                deleted_count += 1
            else:
                try:
                    shutil.rmtree(backup)
                    self.logger.info(f"✓ Deleted: {backup.name}")
                    deleted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to delete {backup.name}: {e}")
        
        self.logger.info(f"Deleted {deleted_count} incremental backups")
    
    def list_backups(self):
        """List all current backups"""
        self.logger.info(Colors.info("\n" + "="*60))
        self.logger.info(Colors.info("CURRENT BACKUPS"))
        self.logger.info(Colors.info("="*60 + "\n"))
        
        # Full backups
        full_backups = sorted(self.config.FULL_BACKUP_DIR.glob("full-*"), reverse=True)
        self.logger.info(f"Full Backups ({len(full_backups)}):")
        
        for backup in full_backups:
            size_bytes = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
            size_mb = size_bytes / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            self.logger.info(f"  {backup.name} - {size_mb:.1f} MB - {mtime.strftime('%Y-%m-%d %H:%M')}")
        
        # Incremental backups
        inc_backups = sorted(self.config.INCREMENTAL_BACKUP_DIR.glob("incremental-*"), reverse=True)
        self.logger.info(f"\nIncremental Backups ({len(inc_backups)}):")
        
        for backup in inc_backups:
            size_bytes = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
            size_mb = size_bytes / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            self.logger.info(f"  {backup.name} - {size_mb:.1f} MB - {mtime.strftime('%Y-%m-%d %H:%M')}")
    
    def run(self, force_full: bool = False) -> bool:
        """Run backup process"""
        # Determine backup type
        backup_type = "full" if (force_full or self.is_sunday()) else "incremental"
        
        self.logger.info(Colors.info(f"Starting {backup_type} backup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
        
        # Create backup
        backup_dir = self.create_backup(backup_type)
        
        if not backup_dir:
            return False
        
        # Cleanup if this was a Sunday backup
        if backup_type == "full":
            self.cleanup_old_full_backups()
            self.cleanup_old_incrementals()
        
        # List current backups
        self.list_backups()
        
        return True

# ==========================================
# Main Function
# ==========================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MISP Automated Backup Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Backup Strategy:
  Sunday:    Full backup (keep 8 weeks)
  Mon-Sat:   Incremental backup (deleted after next Sunday)

Examples:
  # Automatic backup (full on Sunday, incremental otherwise)
  python3 misp-backup-cron.py
  
  # Force full backup
  python3 misp-backup-cron.py --full
  
  # Dry run (test without making changes)
  python3 misp-backup-cron.py --dry-run
  
  # Send email notification
  python3 misp-backup-cron.py --notify

Cron Setup:
  # Edit crontab
  crontab -e

  # Add this line (runs at 2 AM daily)
  0 2 * * * /usr/bin/python3 /opt/misp/scripts/misp-backup-cron.py >> /var/log/misp-install/backup-cron.log 2>&1
        """
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Force full backup regardless of day')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test run without making changes')
    parser.add_argument('--notify', action='store_true',
                       help='Send email notification (if configured)')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info(Colors.info("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        MISP Automated Backup Script v1.0                ║
║            tKQB Enterprises Edition                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""))
    
    if args.dry_run:
        logger.info(Colors.warning("🔍 DRY RUN MODE - No changes will be made\n"))
    
    # Check if MISP directory exists
    if not BackupConfig.MISP_DIR.exists():
        logger.error(Colors.error(f"MISP directory not found: {BackupConfig.MISP_DIR}"))
        sys.exit(1)
    
    # Acquire lock
    lock = LockManager(BackupConfig.LOCK_FILE, logger)
    if not lock.acquire():
        logger.error(Colors.error("Another backup is already running"))
        sys.exit(1)
    
    try:
        # Create backup manager
        backup_mgr = MISPBackupManager(logger, dry_run=args.dry_run)
        
        # Run backup
        success = backup_mgr.run(force_full=args.full)
        
        # Send notification if requested
        if args.notify or BackupConfig.EMAIL_ENABLED:
            backup_type = "full" if (args.full or backup_mgr.is_sunday()) else "incremental"
            
            if success:
                subject = f"{backup_type.capitalize()} Backup Completed Successfully"
                body = f"""MISP {backup_type} backup completed successfully.

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Hostname: {os.uname().nodename}
Backup Location: {BackupConfig.BACKUP_BASE_DIR}

Check logs for details: {BackupConfig.LOG_DIR}
"""
            else:
                subject = f"{backup_type.capitalize()} Backup FAILED"
                body = f"""MISP {backup_type} backup FAILED!

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Hostname: {os.uname().nodename}

ACTION REQUIRED: Check logs immediately!
Log Location: {BackupConfig.LOG_DIR}
"""
            
            backup_mgr.notifier.send_notification(subject, body, is_error=not success)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Backup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(Colors.error(f"\n❌ Unexpected error: {e}"))
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        lock.release()

if __name__ == "__main__":
    main()