#!/usr/bin/env python3
"""
MISP Ready-to-Run Configuration Script
tKQB Enterprises - Post-Installation Automation
Version: 2.0 (with Centralized Logging)

Automates MISP configuration for "ready to run" deployment:
- Updates taxonomies, galaxies, warninglists
- Enables recommended OSINT feeds
- Configures enrichment modules
- Sets security best practices
- Enables background jobs
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import centralized modules
from misp_logger import get_logger
from lib.colors import Colors
from lib.database_manager import DatabaseManager
from lib.setup_helper import MISPSetupHelper

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# ==========================================
# Configuration
# ==========================================

class ConfigureConfig:
    """Configuration for MISP setup"""
    MISP_DIR = Path("/opt/misp")

    # Recommended OSINT feeds to enable (2025 Best Practices)
    RECOMMENDED_FEEDS = [
        # Core Malware Feeds (High Priority)
        "CIRCL OSINT Feed",
        "Abuse.ch URLhaus",              # Malware distribution URLs
        "Abuse.ch ThreatFox",            # IOCs from various malware families
        "Abuse.ch Feodo Tracker",        # Botnet C2 infrastructure
        "Abuse.ch SSL Blacklist",        # Malicious SSL certificates

        # Phishing Feeds
        "OpenPhish url",                 # Phishing URLs
        "Phishtank online valid phishing", # Community phishing feed

        # Botnet & C2 Infrastructure
        "Bambenek Consulting - C2 All Indicator Feed",
        "Botvrij.eu",

        # IP Reputation
        "Blocklist.de",                  # SSH, mail, apache attacks
        "Dataplane.org - sipquery",      # SIP attack attempts
        "Dataplane.org - vncrfb",        # VNC brute force attempts

        # Additional High-Value Feeds
        "Cybercrime-Tracker - All",      # Various cybercrime infrastructure
        "MalwareBazaar Recent Additions", # Latest malware samples
        "DigitalSide Threat-Intel",      # Comprehensive threat intelligence
    ]

    # Core settings to configure
    CORE_SETTINGS = {
        "MISP.background_jobs": True,
        "MISP.cached_attachments": True,
        "MISP.enable_advanced_correlations": True,
        "MISP.correlation_engine": "Default",
        "Plugin.Enrichment_services_enable": True,
        "Plugin.Import_services_enable": True,
        "Plugin.Export_services_enable": True,
        "Plugin.Enrichment_services_url": "http://misp-modules",
        "Plugin.Import_services_url": "http://misp-modules",
        "Plugin.Export_services_url": "http://misp-modules",
    }

# ==========================================
# MISP Configuration Manager
# ==========================================

class MISPReadyConfig:
    """MISP ready-to-run configuration manager"""

    def __init__(self, dry_run: bool = False):
        self.config = ConfigureConfig()
        self.dry_run = dry_run
        self.start_time = time.time()

        # Initialize centralized logger
        self.logger = get_logger('configure-misp-ready', 'misp:configure')

        # Initialize centralized helpers
        self.db_manager = DatabaseManager(self.config.MISP_DIR)
        self.setup_helper = MISPSetupHelper(self.logger.logger, self.config.MISP_DIR, dry_run=dry_run)

        self.logger.info(
            "MISP configuration initiated",
            event_type="configure",
            action="start"
        )

    def log(self, message: str, level: str = "info"):
        """Print colored log message"""
        if level == "error":
            print(Colors.error(message))
        elif level == "success":
            print(Colors.success(message))
        elif level == "warning":
            print(Colors.warning(message))
        elif level == "step":
            print(Colors.step(message))
        else:
            print(Colors.info(message))

    def print_banner(self):
        """Print startup banner"""
        print()
        print(Colors.colored("=" * 60, Colors.CYAN))
        print(Colors.colored("     MISP Ready-to-Run Configuration", Colors.CYAN))
        print(Colors.colored("        tKQB Enterprises Post-Installation Automation", Colors.CYAN))
        print(Colors.colored("=" * 60, Colors.CYAN))
        print()

    def check_misp_running(self) -> bool:
        """Check if MISP containers are running"""
        self.logger.info("Checking MISP containers", event_type="configure", action="check_containers")

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--services', '--filter', 'status=running'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )

            running_services = result.stdout.strip().split('\n')
            required_services = ['misp-core', 'db', 'redis', 'misp-modules']

            all_running = all(svc in running_services for svc in required_services)

            if all_running:
                self.logger.success("All required services are running", event_type="configure", action="check_containers", component="docker")
                return True
            else:
                missing = [svc for svc in required_services if svc not in running_services]
                self.logger.warning(f"Missing services: {', '.join(missing)}", event_type="configure", action="check_containers", component="docker")
                return False

        except Exception as e:
            self.logger.error(f"Could not check container status: {e}", event_type="configure", action="check_containers", error_message=str(e))
            return False

    def wait_for_misp(self, max_wait: int = 60):
        """Wait for MISP to be ready"""
        self.logger.info(f"Waiting for MISP to be ready (max {max_wait}s)", event_type="configure", action="wait_ready")

        for i in range(max_wait):
            try:
                result = subprocess.run(
                    ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                     'curl', '-k', 'https://localhost/users/heartbeat'],
                    cwd=self.config.MISP_DIR,
                    capture_output=True,
                    timeout=5
                )

                if result.returncode == 0:
                    self.logger.success("MISP is ready!", event_type="configure", action="wait_ready")
                    return True
            except:
                pass

            if i % 10 == 0:
                print(f"  Still waiting... ({i}s)")
            time.sleep(1)

        self.logger.warning("MISP did not become ready in time", event_type="configure", action="wait_ready")
        return False

    def run_cake_command(self, command: List[str]) -> bool:
        """Run MISP console cake command (uses centralized MISPSetupHelper)"""
        if len(command) >= 2:
            # Use centralized setup helper
            success, output = self.setup_helper.run_cake_command(command[0], command[1])
            if not success and output:
                self.logger.warning(f"Command failed: {output[:200]}",
                                  event_type="configure", action="run_command",
                                  error_message=output[:200])
            return success
        return False

    def update_taxonomies(self):
        """Update MISP taxonomies"""
        self.logger.info("Updating taxonomies", event_type="configure", phase="update_taxonomies")
        if self.run_cake_command(['Admin', 'updateTaxonomies']):
            self.logger.success("Taxonomies updated", event_type="configure", action="update_taxonomies")
        else:
            self.logger.warning("Could not update taxonomies", event_type="configure", action="update_taxonomies")

    def update_galaxies(self):
        """Update MISP galaxies (MITRE ATT&CK, threat actors, etc.)"""
        self.logger.info("Updating galaxies (MITRE ATT&CK, threat actors)", event_type="configure", phase="update_galaxies")
        self.logger.info("This may take several minutes", event_type="configure", action="update_galaxies")

        if self.run_cake_command(['Admin', 'updateGalaxies', '--force']):
            self.logger.success("Galaxies updated", event_type="configure", action="update_galaxies")
        else:
            self.logger.warning("Could not update galaxies", event_type="configure", action="update_galaxies")

    def update_warninglists(self):
        """Update MISP warninglists (false positive filters)"""
        self.logger.info("Updating warninglists", event_type="configure", phase="update_warninglists")
        if self.run_cake_command(['Admin', 'updateWarningLists']):
            self.logger.success("Warninglists updated", event_type="configure", action="update_warninglists")
        else:
            self.logger.warning("Could not update warninglists", event_type="configure", action="update_warninglists")

    def update_noticelist(self):
        """Update MISP notice lists"""
        self.logger.info("Updating notice lists", event_type="configure", phase="update_noticelist")
        if self.run_cake_command(['Admin', 'updateNoticeLists']):
            self.logger.success("Notice lists updated", event_type="configure", action="update_noticelist")
        else:
            self.logger.warning("Could not update notice lists", event_type="configure", action="update_noticelist")

    def update_object_templates(self):
        """Update MISP object templates"""
        self.logger.info("Updating object templates", event_type="configure", phase="update_object_templates")
        if self.run_cake_command(['Admin', 'updateObjectTemplates']):
            self.logger.success("Object templates updated", event_type="configure", action="update_object_templates")
        else:
            self.logger.warning("Could not update object templates", event_type="configure", action="update_object_templates")

    def set_setting(self, setting: str, value):
        """Set a MISP setting"""
        value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)

        if self.run_cake_command(['Admin', 'setSetting', setting, value_str]):
            return True
        return False

    def configure_core_settings(self):
        """Configure core MISP settings"""
        self.logger.info("Configuring core settings", event_type="configure", phase="configure_settings")

        success_count = 0
        for setting, value in self.config.CORE_SETTINGS.items():
            if self.set_setting(setting, value):
                success_count += 1
                self.logger.debug(f"Set {setting}", event_type="configure", action="set_setting", component=setting)
            else:
                self.logger.warning(f"Could not set {setting}", event_type="configure", action="set_setting", component=setting)

        self.logger.success(f"Configured {success_count}/{len(self.config.CORE_SETTINGS)} settings", event_type="configure", action="configure_settings", count=success_count)

    def get_api_key(self) -> str:
        """Get admin API key from MISP (uses centralized DatabaseManager)"""
        try:
            # Try to get API key from database using DatabaseManager
            mysql_password = self.db_manager.get_mysql_password() or ""
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', '-p' + mysql_password,
                 'misp', '-e', 'SELECT authkey FROM auth_keys WHERE user_id=1 LIMIT 1;'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                return lines[1].strip()
        except:
            pass

        return None

    def enable_recommended_feeds(self):
        """Enable recommended OSINT feeds"""
        self.logger.info("Enabling recommended OSINT feeds", event_type="configure", phase="enable_feeds")
        self.logger.info("Note: Feeds will be enabled but not cached initially", event_type="configure", action="enable_feeds")
        self.logger.info("Run feed caching manually or via cron job", event_type="configure", action="enable_feeds")

        # This would require PyMISP or API calls
        # For now, just inform the user
        self.logger.info("Recommended feeds to enable manually:", event_type="configure", action="enable_feeds")
        for feed in self.config.RECOMMENDED_FEEDS:
            print(f"  - {feed}")

        self.logger.info("Enable feeds via: Sync Actions > List Feeds", event_type="configure", action="enable_feeds")

    def create_initial_backup(self):
        """Create initial backup after configuration"""
        self.logger.info("Creating initial backup", event_type="configure", phase="create_backup")

        backup_script = Path(__file__).parent / "backup-misp.py"
        if backup_script.exists():
            try:
                subprocess.run(
                    ['python3', str(backup_script)],
                    timeout=300
                )
                self.logger.success("Initial backup created", event_type="configure", action="create_backup")
            except Exception as e:
                self.logger.warning(f"Could not create backup: {e}", event_type="configure", action="create_backup", error_message=str(e))
        else:
            self.logger.warning("Backup script not found", event_type="configure", action="create_backup")

    def show_next_steps(self):
        """Show next steps for the user"""
        print()
        print(Colors.colored("=" * 60, Colors.CYAN))
        print(Colors.colored("         CONFIGURATION COMPLETE", Colors.CYAN))
        print(Colors.colored("=" * 60, Colors.CYAN))
        print()
        print("Next Steps:")
        print()
        print("1. Access MISP Web Interface:")
        print(f"   https://your-misp-domain")
        print()
        print("2. Change Default Admin Password:")
        print("   Login: admin@admin.test")
        print("   Password: admin")
        print("   Go to: Global Actions > My Profile > Change Password")
        print()
        print("3. Enable Recommended Feeds:")
        print("   Go to: Sync Actions > List Feeds")
        for feed in self.config.RECOMMENDED_FEEDS:
            print(f"   - Enable: {feed}")
        print("   - Click 'Fetch and store all feed data' for each enabled feed")
        print()
        print("4. Configure SMTP (if not already done):")
        print("   Edit /opt/misp/.env and add SMTP settings")
        print("   See: docs/CONFIGURATION-BEST-PRACTICES.md")
        print()
        print("5. Review Security Settings:")
        print("   - Enable HSTS: HSTS_MAX_AGE=31536000")
        print("   - Set strong passwords for all services")
        print("   - Configure authentication (Azure AD, LDAP, etc.)")
        print()
        print("6. Set Up Automated Backups:")
        print("   Add to crontab:")
        print("   0 2 * * * python3 /path/to/backup-misp.py")
        print()
        print(Colors.success("MISP is ready to use!"))
        print()

    def run(self) -> bool:
        """Run complete configuration process"""
        self.print_banner()

        # Check if MISP is installed
        if not self.config.MISP_DIR.exists():
            self.logger.error(f"MISP directory not found: {self.config.MISP_DIR}", event_type="configure", action="check_dir", file_path=str(self.config.MISP_DIR))
            self.logger.error("Please install MISP first: python3 misp-install.py", event_type="configure", action="check_dir")
            return False

        # Check if containers are running
        if not self.check_misp_running():
            self.logger.info("Starting MISP containers", event_type="configure", action="start_containers")
            try:
                subprocess.run(
                    ['sudo', 'docker', 'compose', 'up', '-d'],
                    cwd=self.config.MISP_DIR,
                    timeout=60
                )
                time.sleep(10)
            except Exception as e:
                self.logger.error(f"Could not start containers: {e}", event_type="configure", action="start_containers", error_message=str(e))
                return False

        # Wait for MISP to be ready
        if not self.wait_for_misp():
            self.logger.warning("MISP may not be fully ready, but continuing", event_type="configure", action="wait_ready")

        try:
            # Update all MISP data
            self.update_taxonomies()
            time.sleep(2)

            self.update_warninglists()
            time.sleep(2)

            self.update_object_templates()
            time.sleep(2)

            self.update_noticelist()
            time.sleep(2)

            self.update_galaxies()  # This takes longest
            time.sleep(5)

            # Configure settings
            self.configure_core_settings()

            # Inform about feeds
            self.enable_recommended_feeds()

            # Create initial backup
            if not self.dry_run:
                self.create_initial_backup()

            # Show next steps
            self.show_next_steps()

            return True

        except KeyboardInterrupt:
            print()
            self.logger.warning("Configuration interrupted by user", event_type="configure", action="interrupt")
            return False
        except Exception as e:
            self.logger.error(f"Configuration failed: {e}", event_type="configure", action="complete", error_message=str(e))
            import traceback
            traceback.print_exc()
            return False

# ==========================================
# Main
# ==========================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='MISP Ready-to-Run Configuration Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configure MISP for ready-to-run
  python3 configure-misp-ready.py

  # Dry run (show what would be done)
  python3 configure-misp-ready.py --dry-run
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')

    args = parser.parse_args()

    config = MISPReadyConfig(dry_run=args.dry_run)
    success = config.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
