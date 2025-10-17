#!/usr/bin/env python3
"""
MISP Advanced Features Health Check
Validates that all v5.6 advanced features are properly configured
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lib.colors import Colors  # noqa: E402
from lib.cron_helpers import has_cron_job, list_cron_jobs  # noqa: E402
from lib.docker_helpers import is_container_running  # noqa: E402
from lib.misp_api_helpers import get_api_key, mask_api_key  # noqa: E402


class AdvancedFeaturesHealthCheck:
    """Health check for all advanced features"""

    def __init__(self):
        self.results = {}
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0

    def header(self, text):
        """Print section header"""
        print(f"\n{Colors.info('='*80)}")
        print(Colors.info(text.center(80)))
        print(f"{Colors.info('='*80)}\n")

    def check(self, name, description):
        """Print check name"""
        self.total_checks += 1
        print(f"{Colors.info('[')} {description:65s} {Colors.info(']')} ", end='', flush=True)

    def pass_check(self, details=None):
        """Mark check as passed"""
        self.passed_checks += 1
        print(Colors.success('✓ PASS'))
        if details:
            print(f"    {details}")

    def fail_check(self, error):
        """Mark check as failed"""
        self.failed_checks += 1
        print(Colors.error('✗ FAIL'))
        print(f"    {Colors.error(f'Error: {error}')}")

    def warn_check(self, warning):
        """Mark check as warning"""
        print(Colors.warning('⚠ WARN'))
        print(f"    {Colors.warning(warning)}")

    def run_command(self, cmd, timeout=10):
        """Run shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_file_exists(self, path, description):
        """Check if file exists"""
        self.check('file_exists', description)
        if os.path.exists(path):
            size = os.path.getsize(path)
            self.pass_check(f"File exists: {path} ({size} bytes)")
            return True
        else:
            self.fail_check(f"File not found: {path}")
            return False

    def check_docker_container(self):
        """Check if MISP container is running using centralized helper"""
        self.check('docker', "MISP Docker container running")
        if is_container_running('misp-misp-core-1'):
            self.pass_check("Container: misp-misp-core-1")
            return True
        else:
            self.fail_check("MISP container not running")
            return False

    # ========================================================================
    # PHASE 11.5: API KEY GENERATION
    # ========================================================================

    def check_api_key(self):
        """Check Phase 11.5: API Key Generation"""
        self.header("PHASE 11.5: API KEY GENERATION")

        # Check .env file has API key using centralized helper
        self.check('api_key_env', "API key in .env file")
        api_key = get_api_key(env_file='/opt/misp/.env')
        if api_key:
            masked = mask_api_key(api_key)
            self.pass_check(f"API Key: {masked}")
        else:
            self.fail_check("MISP_API_KEY not found in .env")

        # Check PASSWORDS.txt has API key
        self.check('api_key_passwords', "API key in PASSWORDS.txt")
        success, stdout, stderr = self.run_command("sudo grep -A 1 'API KEY:' /opt/misp/PASSWORDS.txt | grep -q 'Key:'")
        if success:
            self.pass_check("API key documented in PASSWORDS.txt")
        else:
            self.fail_check("API key not in PASSWORDS.txt")

    # ========================================================================
    # PHASE 11.7: THREAT FEEDS
    # ========================================================================

    def check_threat_feeds(self):
        """Check Phase 11.7: Threat Intelligence Feeds"""
        self.header("PHASE 11.7: COMPREHENSIVE THREAT INTELLIGENCE FEEDS")

        # Get API key using centralized helper
        api_key = get_api_key(env_file='/opt/misp/.env')
        if not api_key:
            self.fail_check("Cannot get API key")
            return

        # Check feeds via API
        self.check('threat_feeds', "Threat intelligence feeds enabled")
        cmd = f"curl -s -k -H 'Authorization: {api_key}' -H 'Accept: application/json' https://misp-test.lan/feeds/index"
        success, stdout, stderr = self.run_command(cmd, timeout=15)

        if success and stdout:
            try:
                data = json.loads(stdout)
                if isinstance(data, list):
                    enabled_feeds = [f for f in data if f.get('Feed', {}).get('enabled')]
                    self.pass_check(f"Total feeds: {len(data)}, Enabled: {len(enabled_feeds)}")
                else:
                    self.warn_check("Unexpected API response format")
            except json.JSONDecodeError:
                self.fail_check("Invalid JSON response from feeds API")
        else:
            self.fail_check("Could not fetch feeds from API")

    # ========================================================================
    # PHASE 11.8: UTILITIES SECTOR
    # ========================================================================

    def check_utilities_sector(self):
        """Check Phase 11.8: Utilities Sector Configuration"""
        self.header("PHASE 11.8: UTILITIES SECTOR THREAT INTELLIGENCE")

        # Check if script exists
        script_path = "/home/gallagher/misp-install/misp-install/scripts/configure-misp-utilities-sector.py"
        self.check_file_exists(script_path, "Utilities sector configuration script exists")

        # Check for utilities-specific taxonomies via API
        api_key = get_api_key(env_file='/opt/misp/.env')
        if not api_key:
            self.fail_check("Cannot get API key")
            return

        # Check taxonomies
        self.check('utilities_taxonomies', "Utilities sector taxonomies enabled")
        cmd = f"curl -s -k -H 'Authorization: {api_key}' -H 'Accept: application/json' https://misp-test.lan/taxonomies/index"
        success, stdout, stderr = self.run_command(cmd, timeout=15)

        if success and stdout:
            try:
                data = json.loads(stdout)
                # Look for ICS/utilities related taxonomies
                ics_taxonomies = [t for t in data if 'ics' in str(t).lower() or 'scada' in str(t).lower() or 'utilities' in str(t).lower()]
                if ics_taxonomies:
                    self.pass_check(f"Found {len(ics_taxonomies)} ICS/utilities taxonomies")
                else:
                    self.warn_check("No ICS/utilities specific taxonomies found")
            except json.JSONDecodeError:
                self.fail_check("Invalid JSON response from taxonomies API")
        else:
            self.fail_check("Could not fetch taxonomies from API")

    # ========================================================================
    # PHASE 11.9: AUTOMATED MAINTENANCE
    # ========================================================================

    def check_automated_maintenance(self):
        """Check Phase 11.9: Automated Maintenance Cron Jobs"""
        self.header("PHASE 11.9: AUTOMATED MAINTENANCE")

        # Check daily maintenance cron using centralized helper
        self.check('daily_cron', "Daily maintenance cron job installed")
        if has_cron_job("misp-daily-maintenance.py"):
            jobs = list_cron_jobs(filter_pattern="misp-daily-maintenance.py")
            if jobs:
                self.pass_check(f"Found: {jobs[0][:60]}...")
            else:
                self.pass_check("Daily maintenance cron installed")
        else:
            self.fail_check("Daily maintenance cron not found")

        # Check weekly optimization cron using centralized helper
        self.check('weekly_cron', "Weekly optimization cron job installed")
        if has_cron_job("weekly"):
            jobs = list_cron_jobs(filter_pattern="weekly")
            if jobs:
                self.pass_check(f"Found: {jobs[0][:60]}...")
            else:
                self.pass_check("Weekly maintenance cron installed")
        else:
            self.fail_check("Weekly optimization cron not found")

        # Check maintenance scripts exist
        self.check_file_exists(
            "/home/gallagher/misp-install/misp-install/scripts/setup-misp-maintenance-cron.sh",
            "Maintenance setup script exists"
        )

        # Check log directory for maintenance logs
        self.check('maintenance_logs', "Maintenance log directory exists")
        if os.path.exists("/var/log/misp-maintenance"):
            log_files = list(Path("/var/log/misp-maintenance").glob("*.log"))
            self.pass_check(f"Log directory exists with {len(log_files)} log files")
        else:
            self.warn_check("Log directory not created yet (normal for new install)")

    # ========================================================================
    # PHASE 11.10: SECURITY NEWS
    # ========================================================================

    def check_security_news(self):
        """Check Phase 11.10: Security News Feeds"""
        self.header("PHASE 11.10: SECURITY NEWS FEEDS")

        # Check news population script
        self.check_file_exists(
            "/home/gallagher/misp-install/misp-install/scripts/populate-misp-news.py",
            "News population script exists"
        )

        # Check news cron job using centralized helper
        self.check('news_cron', "News population cron job installed")
        if has_cron_job("populate-misp-news"):
            jobs = list_cron_jobs(filter_pattern="populate-misp-news")
            if jobs:
                self.pass_check(f"Found: {jobs[0][:60]}...")
            else:
                self.pass_check("News cron installed")
        else:
            self.fail_check("News population cron not found")

        # Check if news has been populated via API
        api_key = get_api_key(env_file='/opt/misp/.env')
        if not api_key:
            self.fail_check("Cannot get API key")
            return

        self.check('news_events', "Security news events populated")
        cmd = f"curl -s -k -H 'Authorization: {api_key}' -H 'Accept: application/json' 'https://misp-test.lan/events/index'"
        success, stdout, stderr = self.run_command(cmd, timeout=15)

        if success and stdout:
            try:
                data = json.loads(stdout)
                # Look for news-related events
                if isinstance(data, list):
                    news_events = [e for e in data if 'news' in str(e).lower() or 'advisory' in str(e).lower()]
                    total_events = len(data)
                    self.pass_check(f"Total events: {total_events}, Potential news events: {len(news_events)}")
                else:
                    self.warn_check("No events found (may be normal for fresh install)")
            except json.JSONDecodeError:
                self.fail_check("Invalid JSON response from events API")
        else:
            self.fail_check("Could not fetch events from API")

    # ========================================================================
    # PHASE 11.11: UTILITIES DASHBOARDS
    # ========================================================================

    def check_utilities_dashboards(self):
        """Check Phase 11.11: Utilities Sector Dashboards"""
        self.header("PHASE 11.11: UTILITIES SECTOR DASHBOARDS (25 WIDGETS)")

        # Check base widget files in container
        self.check('base_widget', "BaseUtilitiesWidget.php exists")
        success, stdout, stderr = self.run_command(
            "sudo docker exec misp-misp-core-1 test -f /var/www/MISP/app/Lib/Dashboard/Custom/BaseUtilitiesWidget.php"
        )
        if success:
            self.pass_check("Base widget class installed")
        else:
            self.fail_check("Base widget class not found")

        self.check('constants_file', "UtilitiesWidgetConstants.php exists")
        success, stdout, stderr = self.run_command(
            "sudo docker exec misp-misp-core-1 test -f /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesWidgetConstants.php"
        )
        if success:
            self.pass_check("Constants file installed")
        else:
            self.fail_check("Constants file not found")

        # Count all widget files
        self.check('widget_count', "All 25 widget files installed")
        success, stdout, stderr = self.run_command(
            "sudo docker exec misp-misp-core-1 ls -1 /var/www/MISP/app/Lib/Dashboard/Custom/ | grep -E 'Widget\\.php$' | grep -v Base | wc -l"
        )
        if success:
            count = int(stdout.strip())
            if count == 25:
                self.pass_check(f"All {count}/25 widgets installed")
            else:
                self.fail_check(f"Only {count}/25 widgets found")
        else:
            self.fail_check("Could not count widgets")

        # List all widgets
        self.check('widget_list', "Widget inventory")
        success, stdout, stderr = self.run_command(
            "sudo docker exec misp-misp-core-1 ls -1 /var/www/MISP/app/Lib/Dashboard/Custom/ | grep -E 'Widget\\.php$' | grep -v Base | sort"
        )
        if success:
            widgets = stdout.strip().split('\n')
            print()  # New line after check
            for widget in widgets[:5]:  # Show first 5
                print(f"      • {widget}")
            if len(widgets) > 5:
                print(f"      • ... and {len(widgets) - 5} more")
            self.passed_checks += 1
        else:
            self.fail_check("Could not list widgets")

        # Check dashboard configuration script
        self.check_file_exists(
            "/home/gallagher/misp-install/misp-install/scripts/configure-all-dashboards.py",
            "Dashboard configuration script exists"
        )

    # ========================================================================
    # ========================================================================
    # ICS THREAT INTELLIGENCE DATA
    # ========================================================================

    def check_ics_threat_intel(self):
        """Check for ICS/OT threat intelligence events"""
        self.header("ICS/OT THREAT INTELLIGENCE DATA")

        # Check 1: ICS-tagged events
        self.check("ics_events", "ICS-tagged events exist")
        try:
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            api_key = get_api_key()
            misp_url = os.environ.get('MISP_URL', 'https://misp-test.lan')
            headers = {
                'Authorization': api_key,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            search_data = {
                "returnFormat": "json",
                "tags": ["ics:malware", "ics:attack-target"],
                "limit": 1000
            }
            response = requests.post(f"{misp_url}/events/restSearch", headers=headers,
                                   json=search_data, verify=False, timeout=30)

            if response.status_code == 200:
                data = response.json()
                count = len(data.get('response', []))
                if count > 0:
                    self.pass_check(f"Found {count} ICS-tagged events")
                else:
                    self.fail_check("No ICS-tagged events found")
            else:
                self.fail_check(f"HTTP {response.status_code}")
        except Exception as e:
            self.fail_check(f"Error: {e}")

        # Check 2: Energy sector events
        self.check("energy_events", "Energy sector events exist")
        try:
            search_data = {
                "returnFormat": "json",
                "tags": ["dhs-ciip-sectors:energy"],
                "limit": 1000
            }
            response = requests.post(f"{misp_url}/events/restSearch", headers=headers,
                                   json=search_data, verify=False, timeout=30)

            if response.status_code == 200:
                data = response.json()
                count = len(data.get('response', []))
                if count > 0:
                    self.pass_check(f"Found {count} energy sector events")
                else:
                    self.fail_check("No energy sector events found")
            else:
                self.fail_check(f"HTTP {response.status_code}")
        except Exception as e:
            self.fail_check(f"Error: {e}")

        # Check 3: Verify sample ICS events have attributes
        self.check("ics_event_attributes", "ICS events contain threat intelligence attributes")
        try:
            # Get the ICS events we found earlier
            search_data = {
                "returnFormat": "json",
                "tags": ["ics:malware"],
                "limit": 10
            }
            response = requests.post(f"{misp_url}/events/restSearch", headers=headers,
                                   json=search_data, verify=False, timeout=30)

            if response.status_code == 200:
                data = response.json()
                events = data.get('response', [])
                if len(events) > 0:
                    # Check first event for attributes
                    event = events[0].get('Event', {})
                    attr_count = len(event.get('Attribute', []))
                    obj_count = len(event.get('Object', []))
                    tag_count = len(event.get('Tag', []))

                    if attr_count > 0 or obj_count > 0:
                        self.pass_check(f"Event {event.get('id')}: {attr_count} attributes, {obj_count} objects, {tag_count} tags")
                    else:
                        self.fail_check("ICS events found but no attributes/objects")
                else:
                    self.fail_check("No ICS malware events found")
            else:
                self.fail_check(f"HTTP {response.status_code}")
        except Exception as e:
            self.fail_check(f"Error: {e}")

    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================

    def run_all_checks(self):
        """Run all health checks"""
        print(Colors.info("\n" + "="*80))
        print(Colors.info("MISP ADVANCED FEATURES HEALTH CHECK".center(80)))
        print(Colors.info("v5.6 Feature Validation".center(80)))
        print(Colors.info("="*80))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{Colors.info(f'Timestamp: {timestamp}')}\n")

        # Pre-check: Docker container
        if not self.check_docker_container():
            print(Colors.error("\n✗ MISP container not running. Cannot perform health checks."))
            return False

        # Run all feature checks
        self.check_api_key()
        self.check_threat_feeds()
        self.check_utilities_sector()
        self.check_automated_maintenance()
        self.check_security_news()
        self.check_utilities_dashboards()
        self.check_ics_threat_intel()

        # Summary
        self.header("HEALTH CHECK SUMMARY")
        print(f"  Total Checks:  {self.total_checks}")
        print(f"  {Colors.success(f'Passed:        {self.passed_checks}')}")
        print(f"  {Colors.error(f'Failed:        {self.failed_checks}')}")

        pass_rate = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"\n  Pass Rate:     {pass_rate:.1f}%")

        if self.failed_checks == 0:
            print(f"\n{Colors.success('✓ ALL ADVANCED FEATURES CONFIGURED SUCCESSFULLY!')}")
            return True
        else:
            print(f"\n{Colors.warning(f'⚠ {self.failed_checks} CHECKS FAILED - SEE DETAILS ABOVE')}")
            return False

if __name__ == "__main__":
    checker = AdvancedFeaturesHealthCheck()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
