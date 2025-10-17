#!/usr/bin/env python3
"""
MISP Complete Uninstallation Script
tKQB Enterprises - Safe MISP Removal
Version: 3.0 (Python with Centralized Logging)

Completely removes MISP installation while preserving backups.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Check Python version

# Import centralized logger
# Import centralized Colors class
from lib.colors import Colors
from misp_logger import get_logger

# ==========================================
# Configuration
# ==========================================

class UninstallConfig:
    """Uninstallation configuration"""
    MISP_DIR = Path("/opt/misp")
    BACKUP_DIR = Path.home() / "misp-backups"
    STATE_FILE = Path.home() / ".misp-install" / "state.json"
    LOG_DIR = Path.home() / ".misp-install" / "logs"

# ==========================================
# Uninstall Manager
# ==========================================

class MISPUninstall:
    """MISP uninstallation manager"""

    def __init__(self, force: bool = False):
        self.config = UninstallConfig()
        self.force = force
        self.start_time = time.time()

        # Initialize centralized logger
        self.logger = get_logger('uninstall-misp', 'misp:uninstall')

        self.logger.info(
            "Uninstallation initiated",
            event_type="uninstall",
            action="start"
        )

    def log(self, message: str, level: str = "info"):
        """Print colored log message and log to centralized logger"""
        # Print colored output for user
        if level == "error":
            print(Colors.error(message))
            self.logger.error(message, event_type="uninstall")
        elif level == "success":
            print(Colors.success(message))
            self.logger.success(message, event_type="uninstall")
        elif level == "warning":
            print(Colors.warning(message))
            self.logger.warning(message, event_type="uninstall")
        else:
            print(Colors.info(message))
            self.logger.info(message, event_type="uninstall")

    def print_banner(self):
        """Print warning banner"""
        print()
        print(Colors.colored("=" * 60, Colors.RED))
        print(Colors.colored("          ⚠️  MISP UNINSTALLATION  ⚠️", Colors.RED))
        print(Colors.colored("  This will COMPLETELY REMOVE your MISP instance", Colors.RED))
        print(Colors.colored("=" * 60, Colors.RED))
        print()
        print("This script will remove:")
        print("  • All MISP Docker containers")
        print("  • All MISP Docker volumes (DATABASE WILL BE DELETED!)")
        print("  • All MISP Docker images")
        print("  • MISP configuration files")
        print(f"  • MISP directory: {self.config.MISP_DIR}")
        print("  • misp-owner system user and home directory")
        print("  • MISP maintenance cron jobs (daily/weekly)")
        print()
        print(Colors.warning(f"NOTE: Backups in {self.config.BACKUP_DIR} will NOT be deleted"))
        print()

    def confirm(self, message: str) -> bool:
        """Ask for confirmation"""
        if self.force:
            return True

        response = input(f"{message} (type 'DELETE' to confirm): ")
        return response == "DELETE"

    def remove_containers(self):
        """Stop and remove MISP containers

        SECURITY: Uses sudo docker compose to ensure containers are properly stopped
        even if they were created by misp-owner user.
        """
        self.log("Stopping MISP containers...")

        if not self.config.MISP_DIR.exists():
            self.log("MISP directory not found", "warning")
            return

        try:
            # Stop and remove containers (with volumes)
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'down', '-v'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                self.log("Containers stopped and removed", "success")
            else:
                self.log(f"Warning: docker compose down returned {result.returncode}", "warning")
                if result.stderr:
                    self.log(f"Error: {result.stderr[:200]}", "warning")
        except Exception as e:
            self.log(f"Could not stop containers: {e}", "warning")

    def remove_images(self):
        """Remove MISP Docker images

        Removes all MISP-related Docker images including tagged and untagged.
        """
        self.log("Removing MISP Docker images...")

        try:
            # Get MISP-related images
            result = subprocess.run(
                ['sudo', 'docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'],
                capture_output=True,
                text=True,
                timeout=30
            )

            images = [img for img in result.stdout.strip().split('\n')
                     if img and ('misp' in img.lower() or 'ghcr.io/misp' in img.lower())]

            if images:
                removed_count = 0
                for image in images:
                    try:
                        result = subprocess.run(
                            ['sudo', 'docker', 'rmi', '-f', image],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            removed_count += 1
                            self.log(f"Removed image: {image}")
                        else:
                            self.log(f"Could not remove image: {image}", "warning")
                    except Exception as e:
                        self.log(f"Error removing {image}: {e}", "warning")

                if removed_count > 0:
                    self.log(f"Removed {removed_count} Docker image(s)", "success")
                else:
                    self.log("Could not remove any images", "warning")
            else:
                self.log("No MISP images found", "info")

        except Exception as e:
            self.log(f"Could not remove images: {e}", "warning")

    def remove_misp_directory(self):
        """Remove MISP directory

        SECURITY: Uses sudo rm to ensure directory is removed even if owned by misp-owner.
        """
        self.log("Removing MISP directory...")

        if not self.config.MISP_DIR.exists():
            self.log("MISP directory not found", "info")
            return

        try:
            # List contents
            contents = list(self.config.MISP_DIR.iterdir())
            self.log(f"Contents to be deleted ({len(contents)} items):")
            for item in contents[:10]:  # Show first 10
                print(f"  - {item.name}")
            if len(contents) > 10:
                print(f"  ... and {len(contents) - 10} more")

            # Remove directory with sudo (may be owned by misp-owner)
            result = subprocess.run(
                ['sudo', 'rm', '-rf', str(self.config.MISP_DIR)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.log("MISP directory removed", "success")
            else:
                self.log(f"Warning removing directory: {result.stderr[:200]}", "warning")
                # Try without sudo as fallback
                try:
                    shutil.rmtree(self.config.MISP_DIR, ignore_errors=True)
                    self.log("MISP directory removed (fallback)", "success")
                except:
                    self.log("Some files may require manual removal", "warning")

        except Exception as e:
            self.log(f"Could not fully remove MISP directory: {e}", "warning")
            self.log("Some files may require manual removal", "warning")

    def remove_state_files(self):
        """Remove installation state files"""
        self.log("Removing installation state files...")

        if self.config.STATE_FILE.exists():
            self.config.STATE_FILE.unlink()
            self.log("State file removed", "success")
        else:
            self.log("No state file found", "info")

    def remove_misp_user(self):
        """Remove misp-owner system user

        SECURITY: Removes the dedicated misp-owner user created by the installation.
        Also removes the user's home directory.
        """
        self.log("Removing misp-owner user...")

        try:
            # Check if user exists
            result = subprocess.run(
                ['id', 'misp-owner'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # User exists, remove it
                result = subprocess.run(
                    ['sudo', 'userdel', '-r', 'misp-owner'],  # -r removes home directory
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.log("misp-owner user removed", "success")
                else:
                    self.log(f"Could not remove misp-owner user: {result.stderr[:200]}", "warning")
            else:
                self.log("misp-owner user not found (not created or already removed)", "info")

        except Exception as e:
            self.log(f"Error checking/removing misp-owner user: {e}", "warning")

    def remove_cron_jobs(self):
        """Remove MISP maintenance cron jobs

        DRY Principle: Uses same removal pattern as setup-misp-maintenance-cron.sh --remove
        """
        self.log("Checking for MISP cron jobs...")

        try:
            # Check if any MISP cron jobs exist
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.log("No crontab found", "info")
                return

            crontab_content = result.stdout

            # Check if MISP maintenance jobs exist
            if 'misp-daily-maintenance' not in crontab_content and 'misp-weekly-maintenance' not in crontab_content:
                self.log("No MISP cron jobs found", "info")
                return

            # Remove MISP maintenance cron jobs
            # Filter out lines containing MISP maintenance jobs
            lines = crontab_content.split('\n')
            filtered_lines = [
                line for line in lines
                if not any(keyword in line for keyword in [
                    'misp-daily-maintenance',
                    'misp-weekly-maintenance',
                    'MISP Daily Maintenance',
                    'MISP Weekly Maintenance'
                ])
            ]

            # Write back filtered crontab
            new_crontab = '\n'.join(filtered_lines)

            # Install new crontab
            result = subprocess.run(
                ['crontab', '-'],
                input=new_crontab,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.log("MISP cron jobs removed", "success")
                self.logger.info("Removed MISP maintenance cron jobs",
                               event_type="uninstall",
                               action="remove_cron")
            else:
                self.log(f"Could not update crontab: {result.stderr[:200]}", "warning")

        except FileNotFoundError:
            self.log("crontab command not found", "warning")
        except Exception as e:
            self.log(f"Error removing cron jobs: {e}", "warning")

    def remove_logs(self, remove: bool = False):
        """Optionally remove logs"""
        if not remove:
            self.log(f"Logs preserved in {self.config.LOG_DIR}", "info")
            return

        self.log("Removing installation logs...")

        # Remove installation logs
        if self.config.LOG_DIR.exists():
            shutil.rmtree(self.config.LOG_DIR, ignore_errors=True)
            self.log("Installation logs removed", "success")
        else:
            self.log("No installation log directory found", "info")

        # Also remove maintenance logs directory
        maintenance_log_dir = Path("/var/log/misp-maintenance")
        if maintenance_log_dir.exists():
            try:
                subprocess.run(
                    ['sudo', 'rm', '-rf', str(maintenance_log_dir)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                self.log("Maintenance logs removed", "success")
            except Exception as e:
                self.log(f"Could not remove maintenance logs: {e}", "warning")

    def show_backup_info(self):
        """Show information about preserved backups"""
        print()
        print(Colors.colored("=" * 60, Colors.CYAN))
        print(Colors.colored("              BACKUP INFORMATION", Colors.CYAN))
        print(Colors.colored("=" * 60, Colors.CYAN))
        print()

        if self.config.BACKUP_DIR.exists():
            backups = list(self.config.BACKUP_DIR.glob("misp-backup-*.tar.gz"))

            if backups:
                print(f"Backups preserved in: {self.config.BACKUP_DIR}")
                print()
                print(f"Available backups ({len(backups)}):")
                for backup in sorted(backups, reverse=True)[:5]:  # Show last 5
                    size_mb = backup.stat().st_size / (1024 * 1024)
                    print(f"  - {backup.name} ({size_mb:.1f} MB)")
                if len(backups) > 5:
                    print(f"  ... and {len(backups) - 5} more")
                print()
                print("To restore MISP from backup:")
                print("  1. Reinstall MISP: python3 misp-install.py")
                print("  2. Restore: python3 misp-restore.py --restore latest")
            else:
                print(Colors.warning("No backups found"))
        else:
            print(Colors.warning("No backup directory found"))

        print()

    def show_summary(self):
        """Show uninstallation summary"""
        print()
        print(Colors.colored("=" * 60, Colors.CYAN))
        print(Colors.colored("         UNINSTALLATION COMPLETE", Colors.CYAN))
        print(Colors.colored("=" * 60, Colors.CYAN))
        print()
        print("The following items have been removed:")
        print("  ✓ MISP containers and volumes")
        print("  ✓ MISP Docker images")
        print("  ✓ MISP directory")
        print("  ✓ misp-owner system user")
        print("  ✓ MISP maintenance cron jobs")
        print("  ✓ Installation state files")
        print()
        print("Preserved items:")
        print(f"  • Backups: {self.config.BACKUP_DIR}")
        if self.config.LOG_DIR.exists():
            print(f"  • Logs: {self.config.LOG_DIR}")
        print()
        print("To reinstall MISP:")
        print("  python3 misp-install.py")
        print()
        print(Colors.success("Thank you for using MISP!"))
        print()

    def run(self, remove_logs: bool = False) -> bool:
        """Run uninstallation process"""
        self.print_banner()

        # First confirmation
        if not self.confirm("Are you absolutely sure you want to uninstall MISP?"):
            print(Colors.success("Aborted. No changes made."))
            return False

        # Final warning
        print()
        print(Colors.error("FINAL WARNING: This will DELETE your MISP database and all configuration!"))

        if not self.confirm("Proceed with uninstallation?"):
            print(Colors.success("Aborted. No changes made."))
            return False

        print()

        try:
            # Execute removal steps
            self.remove_containers()
            self.remove_images()
            self.remove_misp_directory()
            self.remove_misp_user()  # Remove dedicated user
            self.remove_cron_jobs()  # Remove automated maintenance cron jobs
            self.remove_state_files()
            self.remove_logs(remove_logs)

            # Show backup information
            self.show_backup_info()

            # Show summary
            self.show_summary()

            # Log completion
            duration = time.time() - self.start_time
            self.logger.success(
                "Uninstallation completed successfully",
                event_type="uninstall",
                action="complete",
                duration=duration
            )

            return True

        except KeyboardInterrupt:
            print()
            self.log("Uninstallation interrupted by user", "warning")
            self.logger.warning(
                "Uninstallation interrupted by user",
                event_type="uninstall",
                action="interrupt"
            )
            return False
        except Exception as e:
            self.log(f"Uninstallation failed: {e}", "error")
            self.logger.error(
                f"Uninstallation failed: {e}",
                event_type="uninstall",
                action="complete",
                error_message=str(e)
            )
            import traceback
            traceback.print_exc()
            return False

# ==========================================
# Main
# ==========================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MISP Complete Uninstallation Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive uninstall
  python3 uninstall-misp.py

  # Force uninstall without confirmations
  python3 uninstall-misp.py --force

  # Uninstall and remove logs
  python3 uninstall-misp.py --remove-logs
        """
    )

    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts')
    parser.add_argument('--remove-logs', action='store_true',
                       help='Also remove installation logs')

    args = parser.parse_args()

    # Check if running as root
    if os.geteuid() == 0:
        print(Colors.error("Don't run this script as root!"))
        print("Run as regular user: python3 uninstall-misp.py")
        sys.exit(1)

    uninstall = MISPUninstall(force=args.force)
    success = uninstall.run(remove_logs=args.remove_logs)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
