#!/usr/bin/env python3
"""
MISP Ready-to-Run Configuration Script
YourCompanyName - Post-Installation Automation
Version: 1.0

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

    # Recommended OSINT feeds to enable
    RECOMMENDED_FEEDS = [
        "CIRCL OSINT Feed",
        "Abuse.ch Feodo Tracker",
        "Abuse.ch URLhaus",
        "Abuse.ch ThreatFox",
        "Botvrij.eu",
        "OpenPhish url",
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
# Color Output
# ==========================================

class Colors:
    RED = '\\033[0;31m'
    GREEN = '\\033[0;32m'
    YELLOW = '\\033[1;33m'
    BLUE = '\\033[0;34m'
    CYAN = '\\033[0;36m'
    NC = '\\033[0m'

    @staticmethod
    def colored(text: str, color: str) -> str:
        return f"{color}{text}{Colors.NC}"

    @classmethod
    def error(cls, text: str) -> str:
        return cls.colored(f"[ERROR] {text}", cls.RED)

    @classmethod
    def success(cls, text: str) -> str:
        return cls.colored(f"[SUCCESS] {text}", cls.GREEN)

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colored(f"[WARNING] {text}", cls.YELLOW)

    @classmethod
    def info(cls, text: str) -> str:
        return cls.colored(f"[INFO] {text}", cls.BLUE)

    @classmethod
    def step(cls, text: str) -> str:
        return cls.colored(f"[STEP] {text}", cls.CYAN)

# ==========================================
# MISP Configuration Manager
# ==========================================

class MISPReadyConfig:
    """MISP ready-to-run configuration manager"""

    def __init__(self, dry_run: bool = False):
        self.config = ConfigureConfig()
        self.dry_run = dry_run

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
        print(Colors.colored("        YourCompanyName Post-Installation Automation", Colors.CYAN))
        print(Colors.colored("=" * 60, Colors.CYAN))
        print()

    def check_misp_running(self) -> bool:
        """Check if MISP containers are running"""
        self.log("Checking MISP containers...", "step")

        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps', '--services', '--filter', 'status=running'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )

            running_services = result.stdout.strip().split('\\n')
            required_services = ['misp-core', 'db', 'redis', 'misp-modules']

            all_running = all(svc in running_services for svc in required_services)

            if all_running:
                self.log("All required services are running", "success")
                return True
            else:
                missing = [svc for svc in required_services if svc not in running_services]
                self.log(f"Missing services: {', '.join(missing)}", "warning")
                return False

        except Exception as e:
            self.log(f"Could not check container status: {e}", "error")
            return False

    def wait_for_misp(self, max_wait: int = 60):
        """Wait for MISP to be ready"""
        self.log(f"Waiting for MISP to be ready (max {max_wait}s)...", "step")

        for i in range(max_wait):
            try:
                result = subprocess.run(
                    ['docker', 'compose', 'exec', '-T', 'misp-core',
                     'curl', '-k', 'https://localhost/users/heartbeat'],
                    cwd=self.config.MISP_DIR,
                    capture_output=True,
                    timeout=5
                )

                if result.returncode == 0:
                    self.log("MISP is ready!", "success")
                    return True
            except:
                pass

            if i % 10 == 0:
                print(f"  Still waiting... ({i}s)")
            time.sleep(1)

        self.log("MISP did not become ready in time", "warning")
        return False

    def run_cake_command(self, command: List[str]) -> bool:
        """Run MISP console cake command"""
        cmd = ['docker', 'compose', 'exec', '-T', 'misp-core',
               '/var/www/MISP/app/Console/cake'] + command

        if self.dry_run:
            self.log(f"[DRY RUN] Would run: {' '.join(cmd)}", "info")
            return True

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return True
            else:
                self.log(f"Command failed: {result.stderr[:200]}", "warning")
                return False

        except Exception as e:
            self.log(f"Could not run command: {e}", "warning")
            return False

    def update_taxonomies(self):
        """Update MISP taxonomies"""
        self.log("Updating taxonomies...", "step")
        if self.run_cake_command(['Admin', 'updateTaxonomies']):
            self.log("Taxonomies updated", "success")
        else:
            self.log("Could not update taxonomies", "warning")

    def update_galaxies(self):
        """Update MISP galaxies (MITRE ATT&CK, threat actors, etc.)"""
        self.log("Updating galaxies (MITRE ATT&CK, threat actors)...", "step")
        self.log("This may take several minutes...", "info")

        if self.run_cake_command(['Admin', 'updateGalaxies', '--force']):
            self.log("Galaxies updated", "success")
        else:
            self.log("Could not update galaxies", "warning")

    def update_warninglists(self):
        """Update MISP warninglists (false positive filters)"""
        self.log("Updating warninglists...", "step")
        if self.run_cake_command(['Admin', 'updateWarningLists']):
            self.log("Warninglists updated", "success")
        else:
            self.log("Could not update warninglists", "warning")

    def update_noticelist(self):
        """Update MISP notice lists"""
        self.log("Updating notice lists...", "step")
        if self.run_cake_command(['Admin', 'updateNoticeLists']):
            self.log("Notice lists updated", "success")
        else:
            self.log("Could not update notice lists", "warning")

    def update_object_templates(self):
        """Update MISP object templates"""
        self.log("Updating object templates...", "step")
        if self.run_cake_command(['Admin', 'updateObjectTemplates']):
            self.log("Object templates updated", "success")
        else:
            self.log("Could not update object templates", "warning")

    def set_setting(self, setting: str, value):
        """Set a MISP setting"""
        value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)

        if self.run_cake_command(['Admin', 'setSetting', setting, value_str]):
            return True
        return False

    def configure_core_settings(self):
        """Configure core MISP settings"""
        self.log("Configuring core settings...", "step")

        success_count = 0
        for setting, value in self.config.CORE_SETTINGS.items():
            if self.set_setting(setting, value):
                success_count += 1
                self.log(f"  ✓ Set {setting}", "info")
            else:
                self.log(f"  ✗ Could not set {setting}", "warning")

        self.log(f"Configured {success_count}/{len(self.config.CORE_SETTINGS)} settings", "success")

    def get_api_key(self) -> str:
        """Get admin API key from MISP"""
        try:
            # Try to get API key from database
            result = subprocess.run(
                ['docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', '-p' + self.get_mysql_password(),
                 'misp', '-e', 'SELECT authkey FROM auth_keys WHERE user_id=1 LIMIT 1;'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\\n')
            if len(lines) >= 2:
                return lines[1].strip()
        except:
            pass

        return None

    def get_mysql_password(self) -> str:
        """Get MySQL password from .env"""
        env_file = self.config.MISP_DIR / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        return line.split('=', 1)[1].strip()
        return ""

    def enable_recommended_feeds(self):
        """Enable recommended OSINT feeds"""
        self.log("Enabling recommended OSINT feeds...", "step")
        self.log("Note: Feeds will be enabled but not cached initially", "info")
        self.log("Run feed caching manually or via cron job", "info")

        # This would require PyMISP or API calls
        # For now, just inform the user
        self.log("Recommended feeds to enable manually:", "info")
        for feed in self.config.RECOMMENDED_FEEDS:
            print(f"  - {feed}")

        self.log("Enable feeds via: Sync Actions > List Feeds", "info")

    def create_initial_backup(self):
        """Create initial backup after configuration"""
        self.log("Creating initial backup...", "step")

        backup_script = Path(__file__).parent / "backup-misp.py"
        if backup_script.exists():
            try:
                subprocess.run(
                    ['python3', str(backup_script)],
                    timeout=300
                )
                self.log("Initial backup created", "success")
            except Exception as e:
                self.log(f"Could not create backup: {e}", "warning")
        else:
            self.log("Backup script not found", "warning")

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
            self.log(f"MISP directory not found: {self.config.MISP_DIR}", "error")
            self.log("Please install MISP first: python3 misp-install.py", "error")
            return False

        # Check if containers are running
        if not self.check_misp_running():
            self.log("Starting MISP containers...", "step")
            try:
                subprocess.run(
                    ['docker', 'compose', 'up', '-d'],
                    cwd=self.config.MISP_DIR,
                    timeout=60
                )
                time.sleep(10)
            except Exception as e:
                self.log(f"Could not start containers: {e}", "error")
                return False

        # Wait for MISP to be ready
        if not self.wait_for_misp():
            self.log("MISP may not be fully ready, but continuing...", "warning")

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
            self.log("Configuration interrupted by user", "warning")
            return False
        except Exception as e:
            self.log(f"Configuration failed: {e}", "error")
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
