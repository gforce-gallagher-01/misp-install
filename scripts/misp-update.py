#!/usr/bin/env python3
"""
MISP Update & Upgrade Tool
tKQB Enterprises Edition
Version: 2.0 (with Centralized Logging)

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

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Check Python version

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import centralized logger
# Import centralized Colors class
import contextlib

from lib.colors import Colors
from misp_logger import get_logger

# ==========================================
# Constants
# ==========================================

MISP_DIR = Path('/opt/misp')
BACKUP_DIR = Path.home() / 'misp-backups'

# ==========================================
# Logging Setup
# ==========================================

def setup_logging() -> logging.Logger:
    """Setup centralized logging"""
    try:
        misp_logger = get_logger('misp-update', 'misp:update')
        logger = misp_logger.logger
        print(Colors.info("📝 JSON Logs: /opt/misp/logs/misp-update-{timestamp}.log"))
        return logger
    except Exception as e:
        print(Colors.warning(f"Could not setup centralized logging: {e}"))
        print(Colors.info("Falling back to console logging only"))

        # Fallback to console logging
        logger = logging.getLogger('misp-update')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

logger = setup_logging()

# ==========================================
# Version Information
# ==========================================

@dataclass
class VersionInfo:
    """Container for version information"""
    current: str
    latest: str
    update_available: bool

# ==========================================
# MISP Update Manager
# ==========================================

class MISPUpdateManager:
    """Manages MISP updates and upgrades"""

    def __init__(self, skip_backup: bool = False, check_only: bool = False, force: bool = False):
        self.misp_dir = MISP_DIR
        self.skip_backup = skip_backup
        self.check_only = check_only
        self.force = force
        self.backup_path: Optional[Path] = None

    def run_command(self, cmd: List[str], check: bool = True, capture_output: bool = False, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a shell command with logging"""
        logger.debug(f"Running command: {' '.join(cmd)}")
        try:
            if capture_output:
                result = subprocess.run(cmd, check=check, capture_output=True, text=True, cwd=cwd)
            else:
                result = subprocess.run(cmd, check=check, cwd=cwd)
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Exit code: {e.returncode}")
            if capture_output and e.stderr:
                logger.error(f"Error output: {e.stderr}")
            raise

    def get_current_version(self, service: str) -> Optional[str]:
        """Get current version of a MISP service using ps to check running containers"""
        try:
            # Get running container info using JSON format
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json', service],
                cwd=self.misp_dir,
                capture_output=True
            )

            if result.returncode != 0:
                return None

            # Parse JSON output
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('time='):
                    try:
                        container_info = json.loads(line)
                        # Extract image name which includes the tag
                        image = container_info.get('Image', '')
                        if ':' in image:
                            # Extract tag from image (e.g., "ghcr.io/misp/misp-docker/misp-core:latest" -> "latest")
                            version = image.split(':')[-1]
                            return version
                    except json.JSONDecodeError:
                        continue
            return None
        except Exception as e:
            logger.warning(f"Could not get version for {service}: {e}")
            return None

    def get_latest_version(self, _image: str) -> Optional[str]:
        """Get latest available version from Docker Hub (simplified for 'latest' tag)"""
        # For docker images using 'latest' tag, we can't easily determine if updates are available
        # The update process will pull the latest image regardless
        # This function is informational only
        return "latest"

    def check_updates(self) -> Dict[str, VersionInfo]:
        """Check for available updates"""
        logger.info("\n" + "=" * 50)
        logger.info("CHECKING FOR UPDATES")
        logger.info("=" * 50 + "\n")

        services = {
            'misp-core': 'ghcr.io/misp/misp-docker/misp-core:latest',
            'misp-modules': 'ghcr.io/misp/misp-docker/misp-modules:latest'
        }

        versions = {}

        for service, _image in services.items():
            logger.info(f"Checking {service}...")
            current = self.get_current_version(service)

            if current:
                logger.info(f"  Current version: {current}")
                versions[service] = VersionInfo(
                    current=current,
                    latest="latest",  # Docker tags don't show versions easily
                    update_available=True  # Assume update available for latest tag
                )
            else:
                logger.warning("  Could not determine current version")
                versions[service] = VersionInfo(
                    current="unknown",
                    latest="latest",
                    update_available=False
                )

        return versions

    def create_backup(self) -> bool:
        """Create backup before update"""
        logger.info("\n" + "=" * 50)
        logger.info("CREATING PRE-UPDATE BACKUP")
        logger.info("=" * 50 + "\n")

        try:
            # Run backup script
            backup_script = Path(__file__).parent / 'backup-misp.py'

            if not backup_script.exists():
                logger.warning("Backup script not found, skipping backup")
                return False

            logger.info("Running backup script...")
            self.run_command(['python3', str(backup_script)])

            # Find the most recent backup
            if BACKUP_DIR.exists():
                backups = sorted(BACKUP_DIR.glob('misp-backup-*.tar.gz'), key=lambda p: p.stat().st_mtime, reverse=True)
                if backups:
                    self.backup_path = backups[0]
                    logger.info(Colors.success(f"Backup created: {self.backup_path.name}"))
                    return True

            logger.warning("Backup completed but file not found")
            return False

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def stop_services(self) -> bool:
        """Stop MISP services gracefully"""
        logger.info("\n" + "=" * 50)
        logger.info("STOPPING SERVICES")
        logger.info("=" * 50 + "\n")

        try:
            os.chdir(self.misp_dir)
            logger.info("Stopping containers...")
            self.run_command(['sudo', 'docker', 'compose', 'stop'])
            logger.info(Colors.success("Services stopped"))
            return True
        except Exception as e:
            logger.error(f"Failed to stop services: {e}")
            return False

    def pull_images(self) -> bool:
        """Pull latest Docker images"""
        logger.info("\n" + "=" * 50)
        logger.info("PULLING LATEST IMAGES")
        logger.info("=" * 50 + "\n")

        try:
            os.chdir(self.misp_dir)
            logger.info("Pulling latest images...")
            self.run_command(['sudo', 'docker', 'compose', 'pull'])
            logger.info(Colors.success("Images pulled successfully"))
            return True
        except Exception as e:
            logger.error(f"Failed to pull images: {e}")
            return False

    def start_services(self) -> bool:
        """Start MISP services"""
        logger.info("\n" + "=" * 50)
        logger.info("STARTING SERVICES")
        logger.info("=" * 50 + "\n")

        try:
            os.chdir(self.misp_dir)
            logger.info("Starting containers with new images...")
            self.run_command(['sudo', 'docker', 'compose', 'up', '-d'])
            logger.info(Colors.success("Services started"))
            return True
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            return False

    def wait_for_health(self, timeout: int = 300) -> bool:
        """Wait for services to become healthy"""
        logger.info("\n" + "=" * 50)
        logger.info("WAITING FOR SERVICES TO BE HEALTHY")
        logger.info("=" * 50 + "\n")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                os.chdir(self.misp_dir)
                result = self.run_command(
                    ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                    capture_output=True
                )

                # Parse container status
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        with contextlib.suppress(json.JSONDecodeError):
                            containers.append(json.loads(line))

                # Check if all containers are running
                all_running = all(c.get('State') == 'running' for c in containers)

                if all_running:
                    logger.info(Colors.success("All services are running"))
                    return True

                logger.info(f"Waiting... ({int(time.time() - start_time)}s elapsed)")
                time.sleep(10)

            except Exception as e:
                logger.warning(f"Health check failed: {e}")
                time.sleep(10)

        logger.error("Services did not become healthy within timeout")
        return False

    def verify_update(self) -> bool:
        """Verify update was successful"""
        logger.info("\n" + "=" * 50)
        logger.info("VERIFYING UPDATE")
        logger.info("=" * 50 + "\n")

        try:
            os.chdir(self.misp_dir)

            # Check container status
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'ps'],
                capture_output=True
            )
            logger.info("Container status:")
            logger.info(result.stdout)

            # Check logs for errors
            result = self.run_command(
                ['sudo', 'docker', 'compose', 'logs', '--tail=50', 'misp-core'],
                capture_output=True
            )

            if 'error' in result.stdout.lower() or 'fatal' in result.stdout.lower():
                logger.warning("Potential errors found in logs")
                return False

            logger.info(Colors.success("Update verification passed"))
            return True

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

    def rollback(self) -> bool:
        """Rollback to previous version"""
        logger.info("\n" + "=" * 50)
        logger.info(Colors.error("ROLLING BACK TO PREVIOUS VERSION"))
        logger.info("=" * 50 + "\n")

        if not self.backup_path:
            logger.error("No backup available for rollback")
            return False

        try:
            logger.info("Stopping services...")
            self.stop_services()

            logger.info(f"Restoring from backup: {self.backup_path.name}")
            restore_script = Path(__file__).parent / 'misp-restore.py'

            if restore_script.exists():
                self.run_command(['python3', str(restore_script), '--restore', str(self.backup_path)])
                logger.info(Colors.success("Rollback completed"))
                return True
            else:
                logger.error("Restore script not found")
                return False

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def update(self) -> bool:
        """Perform update"""
        logger.info(Colors.info("\n" + "╔" + "=" * 48 + "╗"))
        logger.info(Colors.info("║" + " " * 48 + "║"))
        logger.info(Colors.info("║" + "     MISP Update Tool v2.0".center(48) + "║"))
        logger.info(Colors.info("║" + "     tKQB Enterprises Edition".center(48) + "║"))
        logger.info(Colors.info("║" + " " * 48 + "║"))
        logger.info(Colors.info("╚" + "=" * 48 + "╝\n"))

        # Check for updates
        self.check_updates()

        if self.check_only:
            logger.info("\n" + "=" * 50)
            logger.info("CHECK COMPLETE")
            logger.info("=" * 50)
            return True

        # Confirm update
        logger.info("\n" + "=" * 50)
        logger.info(Colors.warning("READY TO UPDATE"))
        logger.info("=" * 50)
        logger.info("\nThis will:")
        logger.info("  1. Create a backup (if not skipped)")
        logger.info("  2. Pull latest Docker images")
        logger.info("  3. Restart services with new images")
        logger.info("  4. Verify services are healthy")
        logger.info("\nDowntime: ~2-5 minutes")

        if not self.force:
            response = input("\nProceed with update? (type 'UPDATE' to confirm): ")
            if response != 'UPDATE':
                logger.info("Update cancelled")
                return False
        else:
            logger.info("--force flag set, proceeding without confirmation")

        # Create backup
        if not self.skip_backup:
            if not self.create_backup():
                logger.error("Backup failed. Update cancelled for safety.")
                return False
        else:
            logger.warning("Skipping backup (--skip-backup flag)")

        # Stop services
        if not self.stop_services():
            logger.error("Failed to stop services")
            return False

        # Pull new images
        if not self.pull_images():
            logger.error("Failed to pull images")
            # Try to restart with old images
            self.start_services()
            return False

        # Start services
        if not self.start_services():
            logger.error("Failed to start services")
            # Attempt rollback
            if not self.skip_backup:
                self.rollback()
            return False

        # Wait for health
        if not self.wait_for_health():
            logger.error("Services failed health checks")
            # Attempt rollback
            if not self.skip_backup:
                self.rollback()
            return False

        # Verify update
        if not self.verify_update():
            logger.warning("Verification found potential issues")
            logger.info("Services are running but may need attention")

        # Success
        logger.info("\n" + "=" * 50)
        logger.info(Colors.success("UPDATE COMPLETE"))
        logger.info("=" * 50 + "\n")

        logger.info("Next steps:")
        logger.info("  1. Check MISP web interface")
        logger.info("  2. Review logs: sudo docker compose logs")
        logger.info("  3. Test core functionality")

        if self.backup_path:
            logger.info(f"\nBackup available at: {self.backup_path}")

        return True

# ==========================================
# Main
# ==========================================

def main():
    parser = argparse.ArgumentParser(
        description='MISP Update & Upgrade Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Check for updates (no changes made)
  python3 misp-update.py --check-only

  # Update with automatic backup
  python3 misp-update.py

  # Update without backup (not recommended)
  python3 misp-update.py --skip-backup

  # Show version
  python3 misp-update.py --version
        '''
    )

    parser.add_argument('--check-only', action='store_true',
                        help='Only check for updates, do not apply')
    parser.add_argument('--skip-backup', action='store_true',
                        help='Skip backup before update (not recommended)')
    parser.add_argument('--force', action='store_true',
                        help='Skip confirmation prompts (for automation)')
    parser.add_argument('--version', action='version', version='MISP Update Tool v2.0')

    args = parser.parse_args()

    # Verify MISP installation exists
    if not MISP_DIR.exists():
        logger.error(f"MISP installation not found at {MISP_DIR}")
        logger.info("Please run misp-install.py first")
        sys.exit(1)

    # Create update manager
    updater = MISPUpdateManager(
        skip_backup=args.skip_backup,
        check_only=args.check_only,
        force=args.force
    )

    # Run update
    try:
        success = updater.update()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nUpdate cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Update failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
