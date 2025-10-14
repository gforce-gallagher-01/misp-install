#!/usr/bin/env python3
"""
MISP Restore Tool
tKQB Enterprises Edition
Version: 2.0 (with Centralized Logging)

Features:
- List available backups
- Preview backup contents
- Restore configuration files
- Restore database
- Restore SSL certificates
- Verification and testing
- Rollback support
- Fixed database health checks
"""

import os
import sys
import subprocess
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# Import centralized logger
from misp_logger import get_logger

# Import centralized Colors class
from lib.colors import Colors

# ==========================================
# Logging Setup
# ==========================================

def setup_logging() -> logging.Logger:
    """Setup centralized logging"""
    # Use centralized JSON logger
    misp_logger = get_logger('misp-restore', 'misp:restore')
    # Get the underlying Python logger for compatibility
    logger = misp_logger.logger
    logger.info(f"📝 JSON Logs: /opt/misp/logs/misp-restore-{{timestamp}}.log")
    return logger

logger = setup_logging()

# ==========================================
# Backup Information
# ==========================================

class BackupInfo:
    """Information about a backup"""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.timestamp = self._parse_timestamp()
        self.metadata = self._load_metadata()
        self.size = self._calculate_size()
        self.files = self._list_files()
    
    def _parse_timestamp(self) -> datetime:
        """Parse timestamp from backup name"""
        try:
            # Extract timestamp from name like: misp-backup-20251011_143052
            parts = self.name.split('-')
            timestamp_str = parts[-1]  # Get last part
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except Exception as e:
            logger.warning(f"Could not parse timestamp from {self.name}: {e}")
            return datetime.fromtimestamp(self.path.stat().st_mtime)
    
    def _load_metadata(self) -> Dict:
        """Load backup metadata if available"""
        metadata_file = self.path / 'backup_metadata.json'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Could not load metadata: {e}")
        return {}
    
    def _calculate_size(self) -> int:
        """Calculate total backup size"""
        total = 0
        for file in self.path.rglob('*'):
            if file.is_file():
                total += file.stat().st_size
        return total
    
    def _list_files(self) -> List[Tuple[str, int]]:
        """List files in backup with sizes"""
        files = []
        for file in self.path.rglob('*'):
            if file.is_file() and file.name != 'backup_metadata.json':
                rel_path = file.relative_to(self.path)
                files.append((str(rel_path), file.stat().st_size))
        return sorted(files)
    
    def format_size(self, size: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

# ==========================================
# Restore Manager
# ==========================================

class RestoreManager:
    """Manages MISP restoration from backups"""
    
    def __init__(self, misp_dir: Path, backup_dir: Path):
        self.misp_dir = Path(misp_dir).expanduser()
        self.backup_dir = Path(backup_dir).expanduser()
        
        # Validate directories
        if not self.misp_dir.exists():
            raise ValueError(f"MISP directory not found: {self.misp_dir}")
        
        if not self.backup_dir.exists():
            raise ValueError(f"Backup directory not found: {self.backup_dir}")
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available backups"""
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_dir() and (item.name.startswith('misp-') or 
                                  item.name.startswith('pre-restore-')):
                try:
                    backups.append(BackupInfo(item))
                except Exception as e:
                    logger.warning(f"Could not process backup {item.name}: {e}")
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def show_backup_contents(self, backup: BackupInfo):
        """Display detailed backup information"""
        logger.info("=" * 50)
        logger.info(f"BACKUP CONTENTS: {backup.name}")
        logger.info("=" * 50)
        logger.info("")
        logger.info(f"Location: {backup.path}")
        logger.info(f"Created: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Size: {backup.format_size(backup.size)}")
        
        if backup.metadata:
            logger.info("\nBackup Metadata:")
            if 'component_versions' in backup.metadata:
                logger.info("  Component Versions:")
                for comp, ver in backup.metadata['component_versions'].items():
                    logger.info(f"    {comp}: {ver}")
        
        logger.info("\nFiles in backup:")
        for file_path, size in backup.files:
            logger.info(f"  ✓ {file_path} ({backup.format_size(size)})")
        logger.info("")
    
    def create_pre_restore_backup(self) -> Path:
        """Create backup of current state before restoring"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre-restore-{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True)
        
        # Backup critical files
        files_to_backup = [
            '.env',
            'PASSWORDS.txt',
            'docker-compose.yml',
            'docker-compose.override.yml'
        ]
        
        for file in files_to_backup:
            src = self.misp_dir / file
            if src.exists():
                shutil.copy2(src, backup_path / file)
        
        # Backup SSL if exists
        ssl_dir = self.misp_dir / 'ssl'
        if ssl_dir.exists():
            shutil.copytree(ssl_dir, backup_path / 'ssl')
        
        # Database backup
        logger.debug("Backing up current database...")
        self._backup_database(backup_path / 'misp_database.sql')
        
        return backup_path
    
    def _backup_database(self, output_file: Path):
        """Backup database"""
        try:
            # Get MySQL password from .env
            env_file = self.misp_dir / '.env'
            mysql_password = None
            
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        mysql_password = line.split('=', 1)[1].strip()
                        break
            
            if not mysql_password:
                raise ValueError("Could not find MYSQL_PASSWORD in .env")
            
            # Dump database
            cmd = [
                'sudo', 'docker', 'compose', 'exec', '-T', 'db',
                'mysqldump', '-umisp', f'-p{mysql_password}',
                '--single-transaction', '--quick', '--lock-tables=false',
                'misp'
            ]
            
            with open(output_file, 'w') as f:
                subprocess.run(cmd, cwd=self.misp_dir, stdout=f, check=True)
        
        except Exception as e:
            logger.warning(f"Database backup failed: {e}")
    
    def restore_files(self, backup: BackupInfo):
        """Restore configuration files"""
        logger.info("=" * 50)
        logger.info("RESTORING CONFIGURATION FILES")
        logger.info("=" * 50)
        logger.info("")
        
        files_to_restore = [
            '.env',
            'PASSWORDS.txt',
            'docker-compose.yml',
            'docker-compose.override.yml'
        ]
        
        for file in files_to_restore:
            src = backup.path / file
            dst = self.misp_dir / file
            
            if src.exists():
                shutil.copy2(src, dst)
                logger.info(Colors.success(f"Restored: {file}"))
            else:
                logger.warning(Colors.warning(f"Not found in backup: {file}"))
        
        logger.info("")
    
    def restore_ssl(self, backup: BackupInfo):
        """Restore SSL certificates"""
        logger.info("=" * 50)
        logger.info("RESTORING SSL CERTIFICATES")
        logger.info("=" * 50)
        logger.info("")
        
        src_ssl = backup.path / 'ssl'
        dst_ssl = self.misp_dir / 'ssl'
        
        if src_ssl.exists():
            # Remove existing SSL directory
            if dst_ssl.exists():
                shutil.rmtree(dst_ssl)
            
            # Copy SSL directory
            shutil.copytree(src_ssl, dst_ssl)
            logger.info(Colors.success("SSL certificates restored"))
        else:
            logger.warning(Colors.warning("No SSL certificates in backup"))
        
        logger.info("")
    
    def restore_database(self, backup: BackupInfo):
        """Restore database from backup"""
        logger.info("=" * 50)
        logger.info("RESTORING DATABASE")
        logger.info("=" * 50)
        logger.info("")
        
        db_backup = backup.path / 'misp_database.sql'
        if not db_backup.exists():
            logger.error(Colors.error("Database backup file not found"))
            return False
        
        try:
            # Ensure database container is running
            logger.info("Ensuring database container is running...")
            subprocess.run(
                ['sudo', 'docker', 'compose', 'up', '-d', 'db'],
                cwd=self.misp_dir,
                check=True,
                capture_output=True
            )
            
            # Wait for database
            logger.info("Waiting for database to be ready...")
            max_attempts = 30
            for i in range(max_attempts):
                if self.check_database():
                    break
                import time
                time.sleep(2)
            else:
                logger.error(Colors.error("Database did not become ready"))
                return False
            
            logger.info(Colors.success("Database is ready"))
            
            # Get MySQL password
            env_file = self.misp_dir / '.env'
            mysql_password = None
            
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        mysql_password = line.split('=', 1)[1].strip()
                        break
            
            if not mysql_password:
                raise ValueError("Could not find MYSQL_PASSWORD in .env")
            
            # Restore database
            size_mb = db_backup.stat().st_size / (1024 * 1024)
            logger.info(f"Restoring database from backup ({size_mb:.1f} MB)...")
            logger.info("This may take several minutes...")
            
            with open(db_backup, 'r') as f:
                cmd = [
                    'sudo', 'docker', 'compose', 'exec', '-T', 'db',
                    'mysql', '-umisp', f'-p{mysql_password}', 'misp'
                ]
                subprocess.run(cmd, cwd=self.misp_dir, stdin=f, check=True)
            
            logger.info(Colors.success("Database restored successfully"))
            logger.info("")
            return True
        
        except Exception as e:
            logger.error(Colors.error(f"Database restore failed: {e}"))
            return False
    
    def restart_services(self):
        """Restart all MISP services"""
        logger.info("=" * 50)
        logger.info("RESTARTING SERVICES")
        logger.info("=" * 50)
        logger.info("")
        
        try:
            # Stop containers
            logger.info("Stopping containers...")
            subprocess.run(
                ['sudo', 'docker', 'compose', 'down'],
                cwd=self.misp_dir,
                check=True,
                capture_output=True
            )
            
            # Start containers
            logger.info("Starting containers...")
            subprocess.run(
                ['sudo', 'docker', 'compose', 'up', '-d'],
                cwd=self.misp_dir,
                check=True,
                capture_output=True
            )
            
            # Wait for services
            logger.info("Waiting for services to start...")
            import time
            time.sleep(15)
            
            # Show container status
            logger.info("\nContainer Status:")
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True
            )
            logger.info(result.stdout)
            
            logger.info(Colors.success("Services restarted"))
            logger.info("")
            return True
        
        except Exception as e:
            logger.error(Colors.error(f"Service restart failed: {e}"))
            return False
    
    def check_database(self) -> bool:
        """Check if database is accessible"""
        try:
            # Get MySQL password from .env
            env_file = self.misp_dir / '.env'
            mysql_password = None
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('MYSQL_PASSWORD='):
                            mysql_password = line.split('=', 1)[1].strip()
                            break
            
            if not mysql_password:
                logger.debug("Could not find MYSQL_PASSWORD in .env")
                return False
            
            # Test database connection with proper credentials
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db', 
                 'mysql', '-umisp', f'-p{mysql_password}', 
                 '-e', 'SELECT 1;'],
                cwd=self.misp_dir,
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Database check failed: {e}")
            return False
    
    def verify_restore(self) -> bool:
        """Verify that restore was successful"""
        logger.info("=" * 50)
        logger.info("VERIFYING RESTORE")
        logger.info("=" * 50)
        logger.info("")
        
        all_ok = True
        
        # Check containers
        logger.info("[1/4] Checking containers...")
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '-q'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True
            )
            container_count = len(result.stdout.strip().split('\n'))
            if container_count >= 5:
                logger.info(Colors.success(f"  All {container_count} containers running"))
            else:
                logger.warning(Colors.warning(f"  Only {container_count} containers running"))
                all_ok = False
        except Exception as e:
            logger.error(Colors.error(f"  Could not check containers: {e}"))
            all_ok = False
        
        logger.info("")
        
        # Check database
        logger.info("[2/4] Checking database...")
        if self.check_database():
            logger.info(Colors.success("  Database accessible"))
        else:
            logger.warning(Colors.warning("  Database not accessible"))
            all_ok = False
        
        logger.info("")
        
        # Check MISP version
        logger.info("[3/4] Checking MISP version...")
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 'cat', '/var/www/MISP/VERSION.json'],
                cwd=self.misp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_data = json.loads(result.stdout)
                version = version_data.get('version', 'unknown')
                logger.info(Colors.success(f"  MISP v{version} running"))
            else:
                logger.warning(Colors.warning("  Could not determine MISP version"))
                all_ok = False
        except Exception as e:
            logger.warning(Colors.warning(f"  Version check failed: {e}"))
            all_ok = False
        
        logger.info("")
        
        # Check web interface
        logger.info("[4/4] Checking web interface...")
        try:
            import urllib.request
            import ssl
            
            # Get base URL from .env
            env_file = self.misp_dir / '.env'
            base_url = 'https://localhost'
            
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('BASE_URL='):
                        base_url = line.split('=', 1)[1].strip()
                        break
            
            # Create SSL context that doesn't verify certificates
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Try to connect
            req = urllib.request.Request(base_url)
            response = urllib.request.urlopen(req, context=ctx, timeout=10)
            
            if response.status == 200:
                logger.info(Colors.success("  Web interface responding"))
            else:
                logger.warning(Colors.warning(f"  Web interface returned status {response.status}"))
                all_ok = False
        
        except Exception as e:
            logger.warning(Colors.warning(f"  Could not reach web interface: {e}"))
            all_ok = False
        
        logger.info("")
        
        return all_ok
    
    def perform_restore(self, backup: BackupInfo, restore_db: bool = True, 
                       skip_backup: bool = False) -> bool:
        """Perform complete restore operation"""
        logger.info("=" * 50)
        logger.info(f"RESTORING FROM: {backup.name}")
        logger.info("=" * 50)
        logger.info("")
        
        try:
            # Create pre-restore backup unless skipped
            if not skip_backup:
                logger.info("Creating pre-restore backup of current state...")
                pre_backup = self.create_pre_restore_backup()
                logger.info(Colors.success(f"Pre-restore backup created: {pre_backup}"))
                logger.info("")
            
            # Restore files
            self.restore_files(backup)
            
            # Restore SSL
            self.restore_ssl(backup)
            
            # Restore database if requested
            if restore_db:
                if not self.restore_database(backup):
                    logger.error(Colors.error("Database restore failed"))
                    return False
            
            # Restart services
            if not self.restart_services():
                logger.error(Colors.error("Service restart failed"))
                return False
            
            # Verify restore
            all_ok = self.verify_restore()
            
            if all_ok:
                logger.info("=" * 50)
                logger.info(Colors.success("✅ RESTORE COMPLETED SUCCESSFULLY"))
                logger.info("=" * 50)
                logger.info("")
            else:
                logger.info(Colors.warning("⚠") * 50)
                logger.info(Colors.warning("⚠ RESTORE COMPLETED WITH WARNINGS"))
                logger.info(Colors.warning("⚠") * 50)
                logger.info("")
            
            # Final message
            if all_ok:
                logger.info(Colors.success("✅ Restore completed successfully"))
            else:
                logger.info(Colors.error("❌ Restore completed with issues"))
            
            logger.info("\nCheck logs for details:")
            logger.info("  /var/log/misp-install/")
            
            return all_ok
        
        except Exception as e:
            logger.error(Colors.error(f"Restore failed: {e}"))
            import traceback
            logger.debug(traceback.format_exc())
            return False

# ==========================================
# Main
# ==========================================

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════╗
║                                                  ║
║          MISP Restore Tool v2.0                 ║
║            tKQB Enterprises Edition            ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""
    logger.info(banner)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MISP Restore Tool - Restore MISP from backup',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--misp-dir',
        default='/opt/misp',
        help='MISP installation directory (default: /opt/misp)'
    )

    parser.add_argument(
        '--backup-dir',
        default=str(Path.home() / 'misp-backups'),
        help='Backup directory (default: ~/misp-backups)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available backups'
    )
    
    parser.add_argument(
        '--show',
        metavar='BACKUP',
        help='Show contents of backup (use "latest" for most recent)'
    )
    
    parser.add_argument(
        '--restore',
        metavar='BACKUP',
        help='Restore from backup (use "latest" for most recent)'
    )
    
    parser.add_argument(
        '--skip-database',
        action='store_true',
        help='Skip database restore (config files only)'
    )
    
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip creating pre-restore backup'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Initialize restore manager
    try:
        restore_mgr = RestoreManager(args.misp_dir, args.backup_dir)
    except ValueError as e:
        logger.error(Colors.error(str(e)))
        sys.exit(1)
    
    # Get available backups
    backups = restore_mgr.list_backups()
    
    if not backups:
        logger.error(Colors.error(f"No backups found in {args.backup_dir}"))
        sys.exit(1)
    
    # Handle --list
    if args.list:
        logger.info(f"\nAvailable backups in {args.backup_dir}:")
        logger.info("=" * 50)
        for backup in backups:
            age = datetime.now() - backup.timestamp
            days_old = age.days
            logger.info(f"\n{backup.name}")
            logger.info(f"  Created: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({days_old} days ago)")
            logger.info(f"  Size: {backup.format_size(backup.size)}")
            logger.info(f"  Location: {backup.path}")
        
        logger.info(f"\nTotal backups: {len(backups)}")
        logger.info(f"Location: {args.backup_dir}")
        sys.exit(0)
    
    # Handle --show
    if args.show:
        if args.show.lower() == 'latest':
            backup = backups[0]
        else:
            backup = next((b for b in backups if args.show in b.name), None)
            if not backup:
                logger.error(Colors.error(f"Backup not found: {args.show}"))
                logger.info("\nAvailable backups:")
                for b in backups[:5]:
                    logger.info(f"  - {b.name}")
                sys.exit(1)
        
        restore_mgr.show_backup_contents(backup)
        sys.exit(0)
    
    # Handle --restore
    if args.restore:
        if args.restore.lower() == 'latest':
            backup = backups[0]
        else:
            backup = next((b for b in backups if args.restore in b.name), None)
            if not backup:
                logger.error(Colors.error(f"Backup not found: {args.restore}"))
                logger.info("\nAvailable backups:")
                for b in backups[:5]:
                    logger.info(f"  - {b.name}")
                sys.exit(1)
        
        # Show what will be restored
        restore_mgr.show_backup_contents(backup)
        
        # Confirm
        logger.info("\n" + Colors.warning("="*50))
        logger.info(Colors.warning("⚠  WARNING: This will restore MISP"))
        logger.info(Colors.warning("="*50))
        logger.info(f"\nFrom backup: {backup.name}")
        logger.info(f"Created: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"MISP directory: {restore_mgr.misp_dir}")
        logger.info(f"Restore database: {not args.skip_database}")
        logger.info(f"Create pre-restore backup: {not args.skip_backup}")
        
        confirm = input("\nProceed with restore? Type 'YES' to continue: ")
        if confirm != 'YES':
            logger.info("Restore cancelled.")
            sys.exit(0)
        
        # Perform restore
        success = restore_mgr.perform_restore(
            backup,
            restore_db=not args.skip_database,
            skip_backup=args.skip_backup
        )
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    
    # No action specified
    logger.info("No action specified. Use --help for usage information.")
    logger.info("\nQuick commands:")
    logger.info("  List backups:     python3 misp-restore.py --list")
    logger.info("  Show backup:      python3 misp-restore.py --show latest")
    logger.info("  Restore backup:   python3 misp-restore.py --restore latest")

if __name__ == "__main__":
    main()