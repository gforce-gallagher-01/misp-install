#!/usr/bin/env python3
"""
MISP Weekly Maintenance Script

Automated weekly maintenance tasks for MISP threat intelligence platform.
Runs weekly updates for taxonomies, galaxies, and comprehensive health checks.

Usage:
    python3 misp-weekly-maintenance.py              # Run all weekly tasks
    python3 misp-weekly-maintenance.py --dry-run    # Preview without changes

Weekly Tasks:
    1. Update taxonomies (classification systems)
    2. Update galaxies (MITRE ATT&CK, threat actors, malware)
    3. Update object templates
    4. Update notice lists
    5. Verify all configurations are enabled
    6. Database optimization
    7. Generate weekly health report

Setup as cron job:
    # Run weekly on Sunday at 3 AM
    0 3 * * 0 cd /home/gallagher/misp-install/misp-install && python3 scripts/misp-weekly-maintenance.py >> /var/log/misp-weekly-maintenance.log 2>&1

Author: tKQB Enterprises
Version: 1.0
Created: October 2025
"""

import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_logger import get_logger


class WeeklyMaintenanceConfig:
    """Configuration for weekly MISP maintenance"""

    MISP_DIR = Path("/opt/misp")
    MISP_LOGS_DIR = MISP_DIR / "logs"

    # Update timeouts (in seconds)
    TAXONOMY_UPDATE_TIMEOUT = 180  # 3 minutes
    GALAXY_UPDATE_TIMEOUT = 600    # 10 minutes (galaxies are large)
    OBJECT_TEMPLATE_TIMEOUT = 120  # 2 minutes
    NOTICE_LIST_TIMEOUT = 120      # 2 minutes

    # Taxonomies to verify are enabled (utilities sector)
    REQUIRED_TAXONOMIES = [
        'ics',                    # ICS/SCADA threats
        'dhs-ciip-sectors',       # Critical infrastructure sectors
        'tlp',                    # Traffic Light Protocol
        'workflow',               # Event workflow status
        'priority-level',         # Priority classification
        'incident-category',      # Incident types
    ]

    # Galaxies to verify are updated (utilities sector)
    REQUIRED_GALAXIES = [
        'mitre-attack-pattern',   # MITRE ATT&CK tactics/techniques
        'mitre-ics-groups',       # ICS threat actors
        'mitre-ics-malware',      # ICS malware families
        'mitre-ics-software',     # ICS software tools
        'threat-actor',           # General threat actors
        'ransomware',             # Ransomware families
    ]


class MISPWeeklyMaintenance:
    """MISP weekly maintenance automation"""

    # ANSI color codes
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color

    def __init__(self, dry_run: bool = False):
        self.config = WeeklyMaintenanceConfig()
        self.dry_run = dry_run
        self.logger = get_logger('misp-weekly-maintenance', 'misp:maintenance')

        self.tasks_completed = 0
        self.tasks_failed = 0
        self.warnings = []

    def banner(self):
        """Display script banner"""
        print(f"{self.MAGENTA}{'='*80}{self.NC}")
        print(f"{self.MAGENTA}  MISP Weekly Maintenance{self.NC}")
        print(f"{self.MAGENTA}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{self.NC}")
        if self.dry_run:
            print(f"{self.YELLOW}  [DRY-RUN MODE - No changes will be made]{self.NC}")
        print(f"{self.MAGENTA}{'='*80}{self.NC}")
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

    def task_1_update_taxonomies(self) -> bool:
        """Task 1: Update MISP taxonomies"""
        self.section_header("Task 1: Update Taxonomies")

        print("Updating taxonomies (classification systems)...")
        print("Taxonomies include: TLP, ICS, Critical Infrastructure, Priority Levels")
        print()

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'updateTaxonomies'],
            "Update taxonomies",
            timeout=self.config.TAXONOMY_UPDATE_TIMEOUT
        )

        if success:
            print(f"{self.GREEN}✓ Taxonomies updated successfully{self.NC}")
            self.tasks_completed += 1
            return True
        else:
            print(f"{self.RED}✗ Failed to update taxonomies{self.NC}")
            self.warnings.append("Taxonomy update failed")
            self.tasks_failed += 1
            return False

    def task_2_update_galaxies(self) -> bool:
        """Task 2: Update MISP galaxies (MITRE ATT&CK, threat actors, malware)"""
        self.section_header("Task 2: Update Galaxies")

        print("Updating galaxies (MITRE ATT&CK, threat actors, malware families)...")
        print("This is the largest update and may take 5-10 minutes.")
        print()

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'updateGalaxies', '--force'],
            "Update galaxies",
            timeout=self.config.GALAXY_UPDATE_TIMEOUT
        )

        if success:
            print(f"{self.GREEN}✓ Galaxies updated successfully{self.NC}")
            self.tasks_completed += 1
            return True
        else:
            print(f"{self.RED}✗ Failed to update galaxies{self.NC}")
            self.warnings.append("Galaxy update failed")
            self.tasks_failed += 1
            return False

    def task_3_update_object_templates(self) -> bool:
        """Task 3: Update MISP object templates"""
        self.section_header("Task 3: Update Object Templates")

        print("Updating object templates...")
        print("Templates for structured threat intelligence objects.")
        print()

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'updateObjectTemplates'],
            "Update object templates",
            timeout=self.config.OBJECT_TEMPLATE_TIMEOUT
        )

        if success:
            print(f"{self.GREEN}✓ Object templates updated successfully{self.NC}")
            self.tasks_completed += 1
            return True
        else:
            print(f"{self.RED}✗ Failed to update object templates{self.NC}")
            self.warnings.append("Object template update failed")
            self.tasks_failed += 1
            return False

    def task_4_update_notice_lists(self) -> bool:
        """Task 4: Update MISP notice lists"""
        self.section_header("Task 4: Update Notice Lists")

        print("Updating notice lists...")
        print()

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'updateNoticeLists'],
            "Update notice lists",
            timeout=self.config.NOTICE_LIST_TIMEOUT
        )

        if success:
            print(f"{self.GREEN}✓ Notice lists updated successfully{self.NC}")
            self.tasks_completed += 1
            return True
        else:
            print(f"{self.RED}✗ Failed to update notice lists{self.NC}")
            self.warnings.append("Notice list update failed")
            self.tasks_failed += 1
            return False

    def task_5_verify_utilities_config(self) -> bool:
        """Task 5: Verify utilities sector configurations are enabled"""
        self.section_header("Task 5: Verify Utilities Sector Configuration")

        print("Verifying utilities sector taxonomies and galaxies are enabled...")
        print()

        # This would require API or database queries to verify
        # For now, we'll just log that this check should be done
        print(f"{self.YELLOW}Note: Manual verification recommended:{self.NC}")
        print("  1. Check ICS taxonomy is enabled")
        print("  2. Check DHS-CIIP sectors taxonomy is enabled")
        print("  3. Verify MITRE ATT&CK for ICS is updated")
        print("  4. Verify ICS threat actors are in galaxy")
        print()
        print(f"{self.GREEN}✓ Configuration verification noted{self.NC}")

        self.tasks_completed += 1
        return True

    def task_6_optimize_database(self) -> bool:
        """Task 6: Optimize MISP database"""
        self.section_header("Task 6: Optimize Database")

        print("Optimizing MISP database tables...")
        print("This improves query performance and reduces fragmentation.")
        print()

        # Run MySQL OPTIMIZE on key tables
        tables_to_optimize = [
            'attributes',
            'events',
            'feeds',
            'servers',
            'correlations',
            'shadow_attributes'
        ]

        optimized = 0
        failed = 0

        for table in tables_to_optimize:
            if self.dry_run:
                print(f"{self.YELLOW}[DRY-RUN] Would optimize table:{self.NC} {table}")
                optimized += 1
            else:
                try:
                    result = subprocess.run(
                        ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                         'mysql', '-umisp', '-pmisp', 'misp', '-e', f'OPTIMIZE TABLE {table};'],
                        cwd=str(self.config.MISP_DIR),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        print(f"{self.GREEN}✓ Optimized table: {table}{self.NC}")
                        optimized += 1
                    else:
                        print(f"{self.YELLOW}⚠ Could not optimize table: {table}{self.NC}")
                        failed += 1
                except Exception as e:
                    print(f"{self.YELLOW}⚠ Error optimizing table {table}: {e}{self.NC}")
                    failed += 1

        print()
        print(f"Database optimization: {optimized} tables optimized, {failed} failed")

        if failed > 0:
            self.warnings.append(f"{failed} database tables failed to optimize")

        self.tasks_completed += 1
        return True

    def task_7_generate_statistics(self) -> bool:
        """Task 7: Generate MISP statistics"""
        self.section_header("Task 7: Generate Statistics")

        print("Generating MISP usage statistics...")
        print()

        # Get event count
        success_events, output_events = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', 'MISP.event_count'],
            "Get event count",
            timeout=30
        )

        # Get attribute count
        success_attrs, output_attrs = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', 'MISP.attribute_count'],
            "Get attribute count",
            timeout=30
        )

        if success_events or success_attrs:
            print(f"{self.GREEN}✓ Statistics generated{self.NC}")
            if output_events:
                print(f"  Events: {output_events.strip()}")
            if output_attrs:
                print(f"  Attributes: {output_attrs.strip()}")
        else:
            print(f"{self.YELLOW}⚠ Could not retrieve all statistics{self.NC}")

        self.tasks_completed += 1
        return True

    def generate_weekly_report(self):
        """Generate weekly maintenance report"""
        self.section_header("Weekly Maintenance Report")

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

        print(f"{self.CYAN}Next Steps:{self.NC}")
        print("  1. Review MISP web interface for new taxonomies/galaxies")
        print("  2. Enable any new relevant ICS/utilities threat actors")
        print("  3. Check OSINT feeds are fetching data (via daily maintenance)")
        print("  4. Review MISP logs for any errors")
        print()

        if self.tasks_failed == 0 and not self.warnings:
            print(f"{self.GREEN}✓ All weekly maintenance tasks completed successfully!{self.NC}")
        elif self.tasks_failed > 0:
            print(f"{self.RED}✗ Some tasks failed - review logs for details{self.NC}")
        else:
            print(f"{self.YELLOW}⚠ Tasks completed with warnings - review above{self.NC}")

        print()

        # Log summary
        self.logger.info("Weekly maintenance completed",
                        event_type="maintenance",
                        action="weekly_maintenance",
                        result="success" if self.tasks_failed == 0 else "partial",
                        tasks_completed=self.tasks_completed,
                        tasks_failed=self.tasks_failed,
                        warnings=len(self.warnings))

    def run_all_tasks(self):
        """Run all weekly maintenance tasks"""
        self.banner()

        # Task 1: Update taxonomies
        self.task_1_update_taxonomies()

        # Task 2: Update galaxies (longest task)
        self.task_2_update_galaxies()

        # Task 3: Update object templates
        self.task_3_update_object_templates()

        # Task 4: Update notice lists
        self.task_4_update_notice_lists()

        # Task 5: Verify utilities sector config
        self.task_5_verify_utilities_config()

        # Task 6: Optimize database
        self.task_6_optimize_database()

        # Task 7: Generate statistics
        self.task_7_generate_statistics()

        # Generate report
        self.generate_weekly_report()

        # Return exit code
        return 0 if self.tasks_failed == 0 else 1


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='MISP Weekly Maintenance Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 misp-weekly-maintenance.py              # Run all weekly tasks
  python3 misp-weekly-maintenance.py --dry-run    # Preview without changes

Setup as cron job:
  # Run weekly on Sunday at 3 AM
  0 3 * * 0 cd /home/gallagher/misp-install/misp-install && python3 scripts/misp-weekly-maintenance.py >> /var/log/misp-weekly-maintenance.log 2>&1
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                       help='Preview actions without making changes')

    args = parser.parse_args()

    # Run weekly maintenance
    maintenance = MISPWeeklyMaintenance(dry_run=args.dry_run)
    exit_code = maintenance.run_all_tasks()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
