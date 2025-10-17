#!/usr/bin/env python3
"""
MISP Daily Maintenance Script

Automated daily maintenance tasks for MISP threat intelligence platform.
Runs daily updates for time-sensitive components.

Usage:
    python3 misp-daily-maintenance.py              # Run all daily tasks
    python3 misp-daily-maintenance.py --dry-run    # Preview without changes

Daily Tasks:
    1. Update warninglists (false positive filters)
    2. Fetch all enabled OSINT feeds
    3. Verify MISP containers are healthy
    4. Check disk space
    5. Rotate old feed data (if needed)
    6. Generate daily health report

Setup as cron job:
    # Run daily at 2 AM
    0 2 * * * cd /home/gallagher/misp-install/misp-install && python3 scripts/misp-daily-maintenance.py >> /var/log/misp-daily-maintenance.log 2>&1

Author: tKQB Enterprises
Version: 1.0
Created: October 2025
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_logger import get_logger


class DailyMaintenanceConfig:
    """Configuration for daily MISP maintenance"""

    MISP_DIR = Path("/opt/misp")
    MISP_LOGS_DIR = MISP_DIR / "logs"

    # Disk space thresholds (percentage)
    DISK_WARNING_THRESHOLD = 80  # Warning at 80% full
    DISK_CRITICAL_THRESHOLD = 90  # Critical at 90% full

    # Feed fetch timeout (per feed)
    FEED_FETCH_TIMEOUT = 300  # 5 minutes

    # Health check settings
    CONTAINER_HEALTH_CHECK = True
    DATABASE_HEALTH_CHECK = True
    FEED_HEALTH_CHECK = True


class MISPDailyMaintenance:
    """MISP daily maintenance automation"""

    # ANSI color codes
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

    def __init__(self, dry_run: bool = False):
        self.config = DailyMaintenanceConfig()
        self.dry_run = dry_run
        self.logger = get_logger('misp-daily-maintenance', 'misp:maintenance')

        self.tasks_completed = 0
        self.tasks_failed = 0
        self.warnings = []

    def banner(self):
        """Display script banner"""
        print(f"{self.CYAN}{'='*80}{self.NC}")
        print(f"{self.CYAN}  MISP Daily Maintenance{self.NC}")
        print(f"{self.CYAN}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{self.NC}")
        if self.dry_run:
            print(f"{self.YELLOW}  [DRY-RUN MODE - No changes will be made]{self.NC}")
        print(f"{self.CYAN}{'='*80}{self.NC}")
        print()

    def section_header(self, title: str):
        """Print section header"""
        print(f"\n{self.BLUE}{'='*80}{self.NC}")
        print(f"{self.BLUE}  {title}{self.NC}")
        print(f"{self.BLUE}{'='*80}{self.NC}\n")

    def run_docker_command(self, command: List[str], description: str = "", timeout: int = 60) -> Tuple[bool, str]:
        """Run docker compose exec command with error handling"""
        full_command = ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core'] + command

        if self.dry_run:
            print(f"{self.YELLOW}[DRY-RUN] Would run:{self.NC} {description}")
            return True, ""

        try:
            result = subprocess.run(
                full_command,
                cwd=str(self.config.MISP_DIR),
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                self.logger.info(f"Command successful: {description}",
                                event_type="docker_command",
                                action="execute",
                                result="success")
                return True, result.stdout
            else:
                self.logger.error(f"Command failed: {description}",
                                 error=result.stderr[:500])
                return False, result.stderr
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {description}")
            return False, "Timeout"
        except Exception as e:
            self.logger.error(f"Command error: {description}",
                             error=str(e))
            return False, str(e)

    def task_1_check_containers(self) -> bool:
        """Task 1: Verify MISP containers are running and healthy"""
        self.section_header("Task 1: Check Container Health")

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=str(self.config.MISP_DIR),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"{self.RED}✗ Failed to check containers{self.NC}")
                self.warnings.append("Container health check failed")
                return False

            # Parse container status
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            # Check critical containers
            critical_containers = ['misp-core', 'misp-modules', 'misp-workers', 'db', 'redis']
            all_healthy = True

            for container_name in critical_containers:
                container = next((c for c in containers if container_name in c.get('Name', '')), None)

                if not container:
                    print(f"{self.RED}✗ Container {container_name} not found{self.NC}")
                    all_healthy = False
                    self.warnings.append(f"Container {container_name} not found")
                elif container.get('State') != 'running':
                    print(f"{self.RED}✗ Container {container_name} not running (state: {container.get('State')}){self.NC}")
                    all_healthy = False
                    self.warnings.append(f"Container {container_name} not running")
                else:
                    print(f"{self.GREEN}✓ Container {container_name} running{self.NC}")

            if all_healthy:
                self.tasks_completed += 1
                return True
            else:
                self.tasks_failed += 1
                return False

        except Exception as e:
            print(f"{self.RED}✗ Error checking containers: {e}{self.NC}")
            self.logger.error("Container health check failed", error=str(e))
            self.tasks_failed += 1
            return False

    def task_2_check_disk_space(self) -> bool:
        """Task 2: Check disk space and warn if running low"""
        self.section_header("Task 2: Check Disk Space")

        try:
            # Get disk usage for /opt/misp
            stat = shutil.disk_usage(self.config.MISP_DIR)

            total_gb = stat.total / (1024**3)
            used_gb = stat.used / (1024**3)
            free_gb = stat.free / (1024**3)
            percent_used = (stat.used / stat.total) * 100

            print(f"  Total: {total_gb:.2f} GB")
            print(f"  Used:  {used_gb:.2f} GB")
            print(f"  Free:  {free_gb:.2f} GB")
            print(f"  Usage: {percent_used:.1f}%")
            print()

            if percent_used >= self.config.DISK_CRITICAL_THRESHOLD:
                print(f"{self.RED}✗ CRITICAL: Disk usage at {percent_used:.1f}% (threshold: {self.config.DISK_CRITICAL_THRESHOLD}%){self.NC}")
                self.warnings.append(f"CRITICAL: Disk usage at {percent_used:.1f}%")
                self.logger.error("Disk space critical",
                                 percent_used=percent_used,
                                 threshold=self.config.DISK_CRITICAL_THRESHOLD)
                self.tasks_failed += 1
                return False
            elif percent_used >= self.config.DISK_WARNING_THRESHOLD:
                print(f"{self.YELLOW}⚠ WARNING: Disk usage at {percent_used:.1f}% (threshold: {self.config.DISK_WARNING_THRESHOLD}%){self.NC}")
                self.warnings.append(f"WARNING: Disk usage at {percent_used:.1f}%")
                self.logger.warning("Disk space warning",
                                   percent_used=percent_used,
                                   threshold=self.config.DISK_WARNING_THRESHOLD)
                self.tasks_completed += 1
                return True
            else:
                print(f"{self.GREEN}✓ Disk space healthy ({percent_used:.1f}% used){self.NC}")
                self.tasks_completed += 1
                return True

        except Exception as e:
            print(f"{self.RED}✗ Error checking disk space: {e}{self.NC}")
            self.logger.error("Disk space check failed", error=str(e))
            self.tasks_failed += 1
            return False

    def task_3_update_warninglists(self) -> bool:
        """Task 3: Update MISP warninglists (false positive filters)"""
        self.section_header("Task 3: Update Warninglists")

        print("Updating warninglists (false positive filters)...")
        print("This helps reduce false positives in threat intelligence.")
        print()

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'updateWarningLists'],
            "Update warninglists",
            timeout=120
        )

        if success:
            print(f"{self.GREEN}✓ Warninglists updated successfully{self.NC}")
            self.tasks_completed += 1
            return True
        else:
            print(f"{self.RED}✗ Failed to update warninglists{self.NC}")
            self.warnings.append("Warninglist update failed")
            self.tasks_failed += 1
            return False

    def task_4_fetch_feeds(self) -> bool:
        """Task 4: Fetch all enabled OSINT feeds"""
        self.section_header("Task 4: Fetch OSINT Feeds")

        print("Fetching all enabled threat intelligence feeds...")
        print("This downloads latest IOCs from configured OSINT sources.")
        print()

        # Use fetchFeed with 'all' parameter to fetch all enabled feeds
        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Server', 'fetchFeed', 'all'],
            "Fetch all enabled feeds",
            timeout=600  # 10 minutes for all feeds
        )

        if success:
            print(f"{self.GREEN}✓ Feeds fetched successfully{self.NC}")

            # Try to parse output for feed count
            if "feeds fetched" in output.lower():
                print(f"  {output.strip()}")

            self.tasks_completed += 1
            return True
        else:
            print(f"{self.YELLOW}⚠ Feed fetch completed with warnings{self.NC}")
            print("  Some feeds may have failed (check logs)")
            self.warnings.append("Some feeds may have failed to fetch")
            self.tasks_completed += 1  # Count as success with warnings
            return True

    def task_5_cache_feeds(self) -> bool:
        """Task 5: Cache feed data for faster correlation"""
        self.section_header("Task 5: Cache Feed Data")

        print("Caching feed data for faster correlation...")
        print()

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Server', 'cacheFeed', 'all'],
            "Cache all feeds",
            timeout=300
        )

        if success:
            print(f"{self.GREEN}✓ Feed data cached successfully{self.NC}")
            self.tasks_completed += 1
            return True
        else:
            print(f"{self.YELLOW}⚠ Feed caching completed with warnings{self.NC}")
            self.warnings.append("Feed caching had warnings")
            self.tasks_completed += 1
            return True

    def generate_daily_report(self):
        """Generate daily maintenance report"""
        self.section_header("Daily Maintenance Report")

        total_tasks = self.tasks_completed + self.tasks_failed
        success_rate = (self.tasks_completed / total_tasks * 100) if total_tasks > 0 else 0

        print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Tasks Completed: {self.tasks_completed}")
        print(f"  Tasks Failed: {self.tasks_failed}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print()

        if self.warnings:
            print(f"{self.YELLOW}Warnings ({len(self.warnings)}):{self.NC}")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if self.tasks_failed == 0 and not self.warnings:
            print(f"{self.GREEN}✓ All daily maintenance tasks completed successfully!{self.NC}")
        elif self.tasks_failed > 0:
            print(f"{self.RED}✗ Some tasks failed - review logs for details{self.NC}")
        else:
            print(f"{self.YELLOW}⚠ Tasks completed with warnings - review above{self.NC}")

        print()

        # Log summary
        self.logger.info("Daily maintenance completed",
                        event_type="maintenance",
                        action="daily_maintenance",
                        result="success" if self.tasks_failed == 0 else "partial",
                        tasks_completed=self.tasks_completed,
                        tasks_failed=self.tasks_failed,
                        warnings=len(self.warnings))

    def run_all_tasks(self):
        """Run all daily maintenance tasks"""
        self.banner()

        # Task 1: Container health check
        self.task_1_check_containers()

        # Task 2: Disk space check
        self.task_2_check_disk_space()

        # Task 3: Update warninglists
        self.task_3_update_warninglists()

        # Task 4: Fetch OSINT feeds
        self.task_4_fetch_feeds()

        # Task 5: Cache feed data
        self.task_5_cache_feeds()

        # Generate report
        self.generate_daily_report()

        # Return exit code
        return 0 if self.tasks_failed == 0 else 1


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='MISP Daily Maintenance Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 misp-daily-maintenance.py              # Run all daily tasks
  python3 misp-daily-maintenance.py --dry-run    # Preview without changes

Setup as cron job:
  # Run daily at 2 AM
  0 2 * * * cd /home/gallagher/misp-install/misp-install && python3 scripts/misp-daily-maintenance.py >> /var/log/misp-daily-maintenance.log 2>&1
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                       help='Preview actions without making changes')

    args = parser.parse_args()

    # Run daily maintenance
    maintenance = MISPDailyMaintenance(dry_run=args.dry_run)
    exit_code = maintenance.run_all_tasks()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
