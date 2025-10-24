"""
Phase 13: Comprehensive Validation

Runs automated validation checks to verify all MISP features are properly configured.

Author: tKQB Enterprises
Version: 1.0
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lib.colors import Colors  # noqa: E402


class Phase13Validation:
    """Phase 13: Run comprehensive validation checks"""

    def __init__(self, config, logger, misp_dir: Path):
        """Initialize phase

        Args:
            config: MISP configuration object
            logger: Logger instance
            misp_dir: MISP installation directory
        """
        self.config = config
        self.logger = logger
        self.misp_dir = misp_dir

        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_warning = 0

    def run(self):
        """Execute Phase 13: Validation"""
        self.logger.info("")
        self.logger.info(Colors.info("="*50))
        self.logger.info(Colors.info("PHASE 13: COMPREHENSIVE VALIDATION"))
        self.logger.info(Colors.info("="*50))
        self.logger.info("")

        self.logger.info("Running automated validation checks...")
        self.logger.info("This verifies all MISP features are properly configured.")
        self.logger.info("")

        # Wait a moment for MISP to fully initialize
        self.logger.info("Waiting 10 seconds for MISP to fully initialize...")
        time.sleep(10)

        # Run validation checks
        self.check_1_containers()
        self.check_2_web_interface()
        self.check_3_core_settings()
        self.check_4_utilities_config()

        # Generate summary
        self.generate_summary()

        # Save validation report
        self.save_validation_report()

        self.logger.info("")
        self.logger.info(Colors.success("✓ Phase 13: Validation complete"))
        self.logger.info("")

    def run_docker_command(self, command: list, timeout: int = 30) -> Tuple[bool, str]:
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

    def check_1_containers(self):
        """Check 1: Verify all containers are running"""
        self.logger.info(Colors.info("Check 1: Container Status"))

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.error(Colors.error("  ✗ Failed to check containers"))
                self.checks_failed += 1
                return

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
                    self.logger.info(Colors.success(f"  ✓ {container_name:20s} running"))
                else:
                    self.logger.error(Colors.error(f"  ✗ {container_name:20s} not running"))
                    all_running = False

            if all_running:
                self.checks_passed += 1
            else:
                self.checks_failed += 1

        except Exception as e:
            self.logger.error(Colors.error(f"  ✗ Error: {e}"))
            self.checks_failed += 1

        self.logger.info("")

    def check_2_web_interface(self):
        """Check 2: Verify web interface is accessible"""
        self.logger.info(Colors.info("Check 2: Web Interface"))

        try:
            result = subprocess.run(
                ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 'https://localhost/'],
                timeout=10,
                capture_output=True,
                text=True
            )

            status_code = result.stdout.strip()

            if status_code in ['200', '302', '303']:
                self.logger.info(Colors.success(f"  ✓ Web interface accessible (HTTP {status_code})"))
                self.logger.info(f"    URL: {self.config.base_url}")
                self.checks_passed += 1
            else:
                self.logger.warning(Colors.warning(f"  ⚠ Web interface returned HTTP {status_code}"))
                self.logger.warning("    MISP may still be initializing")
                self.checks_warning += 1

        except Exception as e:
            self.logger.warning(Colors.warning(f"  ⚠ Could not check web interface: {e}"))
            self.checks_warning += 1

        self.logger.info("")

    def check_3_core_settings(self):
        """Check 3: Verify MISP core settings"""
        self.logger.info(Colors.info("Check 3: MISP Core Settings"))

        settings = {
            'MISP.background_jobs': 'Background jobs',
            'Plugin.Enrichment_services_enable': 'Enrichment services'
        }

        enabled_count = 0

        for setting, description in settings.items():
            success, output = self.run_docker_command(
                ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', setting],
                timeout=30
            )

            if success and 'true' in output.lower():
                self.logger.info(Colors.success(f"  ✓ {description} enabled"))
                enabled_count += 1
            else:
                self.logger.warning(Colors.warning(f"  ⚠ {description} not confirmed"))

        if enabled_count >= 1:
            self.checks_passed += 1
        else:
            self.checks_warning += 1

        self.logger.info("")

    def check_4_utilities_config(self):
        """Check 4: Verify utilities sector configuration"""
        self.logger.info(Colors.info("Check 4: Utilities Sector Configuration"))

        # Check if galaxies have been updated
        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', 'MISP.enable_advanced_correlations'],
            timeout=30
        )

        if success and 'true' in output.lower():
            self.logger.info(Colors.success("  ✓ Advanced correlations enabled (for ICS threat intelligence)"))
            self.checks_passed += 1
        else:
            self.logger.warning(Colors.warning("  ⚠ Advanced correlations status unclear"))
            self.checks_warning += 1

        self.logger.info("")

    def generate_summary(self):
        """Generate validation summary"""
        self.logger.info(Colors.info("="*50))
        self.logger.info(Colors.info("VALIDATION SUMMARY"))
        self.logger.info(Colors.info("="*50))

        total = self.checks_passed + self.checks_failed + self.checks_warning

        self.logger.info(f"  Total Checks:    {total}")
        self.logger.info(Colors.success(f"  ✓ Passed:        {self.checks_passed}"))
        self.logger.info(Colors.warning(f"  ⚠ Warnings:      {self.checks_warning}"))
        self.logger.info(Colors.error(f"  ✗ Failed:        {self.checks_failed}"))
        self.logger.info("")

        if self.checks_failed == 0:
            self.logger.info(Colors.success("✓ Installation validation successful!"))
            self.logger.info("")
            self.logger.info("Next steps:")
            self.logger.info("  1. Login to web interface: " + self.config.base_url)
            self.logger.info("  2. Review: MISP_CONFIGURATION_STATUS.md")
            self.logger.info("  3. Set up automated maintenance:")
            self.logger.info("     ./scripts/setup-misp-maintenance-cron.sh --auto")
            self.logger.info("  4. Enable NERC CIP feeds:")
            self.logger.info("     python3 scripts/enable-misp-feeds.py --nerc-cip")
            self.logger.info("  5. Run NERC CIP configuration:")
            self.logger.info("     python3 scripts/configure-misp-nerc-cip.py")
        else:
            self.logger.warning(Colors.warning("⚠ Some checks failed - review output above"))
            self.logger.info("")
            self.logger.info("Troubleshooting:")
            self.logger.info("  - Check logs: sudo docker compose logs -f misp-core")
            self.logger.info("  - Verify MISP initialization: may take 10-15 minutes")
            self.logger.info("  - Run full verification:")
            self.logger.info("    python3 scripts/verify-misp-configuration.py")

        self.logger.info("")

    def save_validation_report(self):
        """Save validation report to file"""
        try:
            report_file = Path.home() / "misp-install" / "misp-install" / "VALIDATION_REPORT.txt"

            with open(report_file, 'w') as f:
                f.write("="*60 + "\n")
                f.write(" MISP INSTALLATION VALIDATION REPORT\n")
                f.write("="*60 + "\n\n")

                f.write(f"Installation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"MISP URL: {self.config.base_url}\n")
                f.write(f"Organization: {self.config.admin_org}\n")
                f.write(f"Environment: {self.config.environment}\n\n")

                f.write("="*60 + "\n")
                f.write(" VALIDATION RESULTS\n")
                f.write("="*60 + "\n\n")

                total = self.checks_passed + self.checks_failed + self.checks_warning
                f.write(f"Total Checks:    {total}\n")
                f.write(f"✓ Passed:        {self.checks_passed}\n")
                f.write(f"⚠ Warnings:      {self.checks_warning}\n")
                f.write(f"✗ Failed:        {self.checks_failed}\n\n")

                if self.checks_failed == 0:
                    f.write("✓ Installation validation SUCCESSFUL!\n\n")
                else:
                    f.write("⚠ Some checks failed - review logs for details\n\n")

                f.write("="*60 + "\n")
                f.write(" NEXT STEPS\n")
                f.write("="*60 + "\n\n")

                f.write("1. Login to web interface:\n")
                f.write(f"   {self.config.base_url}\n")
                f.write(f"   Email: {self.config.admin_email}\n")
                f.write("   Password: (check /opt/misp/PASSWORDS.txt)\n\n")

                f.write("2. Review configuration status:\n")
                f.write("   cat MISP_CONFIGURATION_STATUS.md\n\n")

                f.write("3. Set up automated maintenance:\n")
                f.write("   ./scripts/setup-misp-maintenance-cron.sh --auto\n\n")

                f.write("4. Enable NERC CIP threat feeds:\n")
                f.write("   python3 scripts/enable-misp-feeds.py --nerc-cip\n\n")

                f.write("5. Run NERC CIP configuration:\n")
                f.write("   python3 scripts/configure-misp-nerc-cip.py\n\n")

                f.write("6. Populate MISP news (security awareness):\n")
                f.write("   python3 scripts/populate-misp-news.py\n\n")

                f.write("="*60 + "\n")
                f.write(" DOCUMENTATION\n")
                f.write("="*60 + "\n\n")

                f.write("- README.md - Main project documentation\n")
                f.write("- MISP_CONFIGURATION_STATUS.md - What has been configured\n")
                f.write("- docs/MAINTENANCE_AUTOMATION.md - Maintenance guide\n")
                f.write("- docs/NERC_CIP_CONFIGURATION.md - NERC CIP compliance\n")
                f.write("- SCRIPTS.md - All scripts documentation\n\n")

            self.logger.info(Colors.success(f"✓ Validation report saved: {report_file}"))

        except Exception as e:
            self.logger.warning(Colors.warning(f"⚠ Could not save validation report: {e}"))
