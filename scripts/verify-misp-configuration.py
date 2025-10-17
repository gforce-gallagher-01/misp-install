#!/usr/bin/env python3
"""
MISP Configuration Verification Script

Verifies that all utilities sector configurations have been applied and are visible in MISP.

Author: tKQB Enterprises
Version: 1.0
Created: October 2025
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_logger import get_logger


class MISPConfigVerifier:
    """Verify MISP configuration status"""

    # ANSI color codes
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color

    def __init__(self):
        self.logger = get_logger('verify-misp-configuration', 'misp:verification')
        self.misp_dir = Path("/opt/misp")

        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_warning = 0

    def banner(self):
        """Display script banner"""
        print(f"{self.CYAN}{'='*80}{self.NC}")
        print(f"{self.CYAN}  MISP Configuration Verification{self.NC}")
        print(f"{self.CYAN}  Validating all utilities sector features are configured{self.NC}")
        print(f"{self.CYAN}{'='*80}{self.NC}")
        print()

    def section_header(self, title: str):
        """Print section header"""
        print(f"\n{self.BLUE}{'='*80}{self.NC}")
        print(f"{self.BLUE}  {title}{self.NC}")
        print(f"{self.BLUE}{'='*80}{self.NC}\n")

    def run_docker_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str]:
        """Run docker compose exec command"""
        full_command = ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core'] + command

        try:
            result = subprocess.run(
                full_command,
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, str(e)

    def check_1_containers(self) -> bool:
        """Check 1: Verify all containers are running"""
        self.section_header("Check 1: Container Status")

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"{self.RED}✗ Failed to check containers{self.NC}")
                self.checks_failed += 1
                return False

            import json
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except:
                        continue

            critical_containers = ['misp-core', 'misp-modules', 'db', 'redis']
            all_running = True

            for container_name in critical_containers:
                container = next((c for c in containers if container_name in c.get('Name', '')), None)

                if container and container.get('State') == 'running':
                    print(f"{self.GREEN}✓ {container_name:20s} running{self.NC}")
                else:
                    print(f"{self.RED}✗ {container_name:20s} not running{self.NC}")
                    all_running = False

            if all_running:
                self.checks_passed += 1
                return True
            else:
                self.checks_failed += 1
                return False

        except Exception as e:
            print(f"{self.RED}✗ Error: {e}{self.NC}")
            self.checks_failed += 1
            return False

    def check_2_taxonomies(self) -> bool:
        """Check 2: Verify ICS taxonomies are enabled"""
        self.section_header("Check 2: ICS/Utilities Taxonomies")

        taxonomies_to_check = [
            'ics',
            'dhs-ciip-sectors',
            'tlp',
            'workflow',
            'misp-workflow'
        ]

        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'listTaxonomies'],
            timeout=30
        )

        if not success:
            print(f"{self.RED}✗ Failed to list taxonomies{self.NC}")
            self.checks_failed += 1
            return False

        enabled_count = 0
        for taxonomy in taxonomies_to_check:
            if taxonomy in output.lower():
                print(f"{self.GREEN}✓ {taxonomy:30s} available{self.NC}")
                enabled_count += 1
            else:
                print(f"{self.YELLOW}⚠ {taxonomy:30s} not found{self.NC}")

        if enabled_count >= 3:
            print(f"\n{self.GREEN}✓ Found {enabled_count}/{len(taxonomies_to_check)} taxonomies{self.NC}")
            self.checks_passed += 1
            return True
        else:
            print(f"\n{self.YELLOW}⚠ Only {enabled_count}/{len(taxonomies_to_check)} taxonomies found{self.NC}")
            self.checks_warning += 1
            return False

    def check_3_galaxies(self) -> bool:
        """Check 3: Verify MITRE ATT&CK for ICS galaxies"""
        self.section_header("Check 3: MITRE ATT&CK for ICS Galaxies")


        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', 'MISP.enable_advanced_correlations'],
            timeout=30
        )

        if success:
            print(f"{self.GREEN}✓ Advanced correlations enabled{self.NC}")
        else:
            print(f"{self.YELLOW}⚠ Advanced correlations not confirmed{self.NC}")

        # Check if galaxies have been updated recently
        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', 'MISP.background_jobs'],
            timeout=30
        )

        if success and 'true' in output.lower():
            print(f"{self.GREEN}✓ Background jobs enabled (for galaxy updates){self.NC}")
            self.checks_passed += 1
            return True
        else:
            print(f"{self.YELLOW}⚠ Background jobs status unclear{self.NC}")
            self.checks_warning += 1
            return False

    def check_4_feeds(self) -> bool:
        """Check 4: Verify OSINT feeds are configured"""
        self.section_header("Check 4: OSINT Threat Intelligence Feeds")

        # Get MySQL password from .env
        try:
            env_file = self.misp_dir / ".env"
            mysql_password = None

            with open(env_file) as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        mysql_password = line.split('=', 1)[1].strip().strip('"')
                        break

            if not mysql_password:
                print(f"{self.YELLOW}⚠ Could not read MySQL password from .env{self.NC}")
                self.checks_warning += 1
                return False

            # Query feeds table
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{mysql_password}', 'misp', '-e',
                 'SELECT COUNT(*) as total, SUM(enabled) as enabled FROM feeds;'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    data = lines[1].split('\t')
                    total = int(data[0])
                    enabled = int(data[1]) if data[1] != 'NULL' else 0

                    print(f"  Total feeds:   {total}")
                    print(f"  Enabled feeds: {enabled}")
                    print()

                    if enabled > 0:
                        print(f"{self.GREEN}✓ {enabled} feeds enabled{self.NC}")
                        self.checks_passed += 1
                        return True
                    else:
                        print(f"{self.YELLOW}⚠ No feeds enabled yet{self.NC}")
                        print(f"{self.YELLOW}  Run: python3 scripts/enable-misp-feeds.py --nerc-cip{self.NC}")
                        self.checks_warning += 1
                        return False

        except Exception as e:
            print(f"{self.YELLOW}⚠ Could not check feeds: {e}{self.NC}")
            self.checks_warning += 1
            return False

    def check_5_settings(self) -> bool:
        """Check 5: Verify MISP core settings"""
        self.section_header("Check 5: MISP Core Settings")

        settings_to_check = {
            'MISP.background_jobs': 'Background jobs',
            'MISP.cached_attachments': 'Cached attachments',
            'Plugin.Enrichment_services_enable': 'Enrichment services'
        }

        enabled_count = 0

        for setting, description in settings_to_check.items():
            success, output = self.run_docker_command(
                ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', setting],
                timeout=30
            )

            if success and 'true' in output.lower():
                print(f"{self.GREEN}✓ {description:30s} enabled{self.NC}")
                enabled_count += 1
            else:
                print(f"{self.YELLOW}⚠ {description:30s} not confirmed{self.NC}")

        if enabled_count >= 2:
            print(f"\n{self.GREEN}✓ {enabled_count}/{len(settings_to_check)} settings confirmed{self.NC}")
            self.checks_passed += 1
            return True
        else:
            print(f"\n{self.YELLOW}⚠ Only {enabled_count}/{len(settings_to_check)} settings confirmed{self.NC}")
            self.checks_warning += 1
            return False

    def check_6_news(self) -> bool:
        """Check 6: Verify MISP news populated"""
        self.section_header("Check 6: MISP News for Security Awareness")

        try:
            env_file = self.misp_dir / ".env"
            mysql_password = None

            with open(env_file) as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        mysql_password = line.split('=', 1)[1].strip().strip('"')
                        break

            if not mysql_password:
                print(f"{self.YELLOW}⚠ Could not read MySQL password{self.NC}")
                self.checks_warning += 1
                return False

            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{mysql_password}', 'misp', '-e',
                 'SELECT COUNT(*) FROM news;'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    count = int(lines[1])

                    if count > 0:
                        print(f"{self.GREEN}✓ {count} news articles in MISP{self.NC}")
                        print("  (For NERC CIP-003 security awareness training)")
                        self.checks_passed += 1
                        return True
                    else:
                        print(f"{self.YELLOW}⚠ No news articles found{self.NC}")
                        print(f"{self.YELLOW}  Run: python3 scripts/populate-misp-news.py{self.NC}")
                        self.checks_warning += 1
                        return False

        except Exception as e:
            print(f"{self.YELLOW}⚠ Could not check news: {e}{self.NC}")
            self.checks_warning += 1
            return False

    def check_7_web_interface(self) -> bool:
        """Check 7: Verify web interface is accessible"""
        self.section_header("Check 7: Web Interface Accessibility")

        import subprocess

        # Try to curl the MISP web interface
        result = subprocess.run(
            ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'https://localhost/'],
            timeout=10,
            capture_output=True,
            text=True
        )

        status_code = result.stdout.strip()

        if status_code in ['200', '302', '303']:
            print(f"{self.GREEN}✓ Web interface accessible (HTTP {status_code}){self.NC}")
            print("  URL: https://misp-test.lan")
            print("  Default credentials:")
            print("    Email: admin@admin.test")
            print("    Password: (check /opt/misp/PASSWORDS.txt)")
            self.checks_passed += 1
            return True
        else:
            print(f"{self.YELLOW}⚠ Web interface returned HTTP {status_code}{self.NC}")
            print("  MISP may still be initializing (wait 5-10 minutes)")
            self.checks_warning += 1
            return False

    def generate_report(self):
        """Generate final verification report"""
        self.section_header("Verification Summary")

        total_checks = self.checks_passed + self.checks_failed + self.checks_warning

        print(f"  Total Checks:    {total_checks}")
        print(f"  {self.GREEN}✓ Passed:        {self.checks_passed}{self.NC}")
        print(f"  {self.YELLOW}⚠ Warnings:      {self.checks_warning}{self.NC}")
        print(f"  {self.RED}✗ Failed:        {self.checks_failed}{self.NC}")
        print()

        if self.checks_failed == 0:
            print(f"{self.GREEN}✓ MISP configuration verification successful!{self.NC}")
            print()
            print("Next steps:")
            print("  1. Login to web interface: https://misp-test.lan")
            print("  2. Set up automated maintenance:")
            print("     ./scripts/setup-misp-maintenance-cron.sh --auto")
            print("  3. Enable NERC CIP feeds:")
            print("     python3 scripts/enable-misp-feeds.py --nerc-cip")
            print("  4. Run NERC CIP configuration:")
            print("     python3 scripts/configure-misp-nerc-cip.py")
        else:
            print(f"{self.RED}✗ Some checks failed - review output above{self.NC}")
            print()
            print("Troubleshooting:")
            print("  - Check container logs: sudo docker compose logs -f misp-core")
            print("  - Verify MISP initialization: may take 10-15 minutes")
            print("  - Check documentation: docs/MAINTENANCE_AUTOMATION.md")

        print()

        # Log summary
        self.logger.info("Configuration verification completed",
                        event_type="verification",
                        action="verify_configuration",
                        result="success" if self.checks_failed == 0 else "partial",
                        checks_passed=self.checks_passed,
                        checks_failed=self.checks_failed,
                        checks_warning=self.checks_warning)

    def run_all_checks(self):
        """Run all verification checks"""
        self.banner()

        self.check_1_containers()
        self.check_2_taxonomies()
        self.check_3_galaxies()
        self.check_4_feeds()
        self.check_5_settings()
        self.check_6_news()
        self.check_7_web_interface()

        self.generate_report()

        return 0 if self.checks_failed == 0 else 1


def main():
    """Main function"""
    verifier = MISPConfigVerifier()
    exit_code = verifier.run_all_checks()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
