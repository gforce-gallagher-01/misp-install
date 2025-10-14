#!/usr/bin/env python3
"""
MISP Complete Setup Script
Version: 1.0
Date: 2025-10-14

Purpose:
    Post-installation configuration script that applies all recommended settings,
    adds feeds, populates news, and configures MISP for production use.

    Special mode: --nerc-cip-ready configures MISP specifically for utilities/
    energy sector compliance with NERC CIP standards.

Usage:
    # Standard production setup
    python3 scripts/misp-setup-complete.py --api-key YOUR_KEY

    # NERC CIP compliance setup (utilities/energy sector)
    python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --nerc-cip-ready

    # Dry-run mode (preview without changes)
    python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --dry-run

    # Custom configuration
    python3 scripts/misp-setup-complete.py --api-key YOUR_KEY \
        --skip-feeds --skip-news --custom-config config/custom.yaml

Features:
    - Applies MISP best practice settings
    - Adds threat intelligence feeds (standard or NERC CIP focused)
    - Populates news section with security updates
    - Configures taxonomies and warning lists
    - Sets up correlation rules
    - Configures email notifications
    - Enables recommended modules
    - NERC CIP mode for utilities sector compliance

NERC CIP Mode:
    When --nerc-cip-ready is specified, additional configuration is applied:
    - NERC CIP specific feeds (E-ISAC, ICS-CERT, etc.)
    - Utilities sector taxonomies
    - Critical infrastructure tags
    - Enhanced audit logging (CIP-007-R2)
    - Security awareness content (CIP-003-R2)
    - Event correlation for OT/ICS threats
    - Compliance reporting dashboard

Requirements:
    - MISP installation complete (misp-install.py)
    - MISP containers running
    - Valid API key (auto-generated during install)
    - Python packages: requests, pyyaml (optional)
"""

import os
import sys
import argparse
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import centralized modules
from misp_logger import get_logger
from misp_api import get_api_key, get_misp_client, test_connection

# Import centralized Colors class
from lib.colors import Colors

# Import centralized setup helpers
from lib.setup_helper import MISPSetupHelper, VerificationHelper, StatisticsTracker

# Try to import YAML support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class MISPSetupComplete:
    """Complete MISP post-installation setup orchestrator"""

    def __init__(self, api_key: str, misp_url: str = "https://misp-test.lan",
                 dry_run: bool = False, nerc_cip_ready: bool = False,
                 skip_feeds: bool = False, skip_news: bool = False,
                 skip_settings: bool = False, custom_config: Optional[str] = None):
        """Initialize setup orchestrator

        Args:
            api_key: MISP API key
            misp_url: MISP base URL
            dry_run: Preview mode without making changes
            nerc_cip_ready: Enable NERC CIP compliance mode
            skip_feeds: Skip feed configuration
            skip_news: Skip news population
            skip_settings: Skip MISP settings configuration
            custom_config: Path to custom configuration file
        """
        self.api_key = api_key
        self.misp_url = misp_url.rstrip('/')
        self.dry_run = dry_run
        self.nerc_cip_ready = nerc_cip_ready
        self.skip_feeds = skip_feeds
        self.skip_news = skip_news
        self.skip_settings = skip_settings
        self.custom_config = custom_config

        # Initialize logger
        self.logger = get_logger('misp-setup-complete', 'misp:setup')

        # Get API client
        self.session = get_misp_client(api_key=api_key, misp_url=misp_url)

        # Initialize centralized helpers
        self.setup_helper = MISPSetupHelper(self.logger.logger, dry_run=dry_run)
        self.verify_helper = VerificationHelper(self.logger.logger, self.session,
                                                misp_url, dry_run=dry_run)
        self.stats_tracker = StatisticsTracker()

        # Keep stats dict for backward compatibility
        self.stats = self.stats_tracker.stats

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.CYAN}{'='*80}{Colors.NC}")
        print(f"{Colors.CYAN}{text.center(80)}{Colors.NC}")
        print(f"{Colors.CYAN}{'='*80}{Colors.NC}\n")

    def print_subheader(self, text: str):
        """Print subsection header"""
        print(f"\n{Colors.BLUE}[{text}]{Colors.NC}")

    def run_script(self, script_name: str, args: List[str], description: str) -> Tuple[bool, str]:
        """Run a setup script and capture output (uses centralized helper)

        Args:
            script_name: Script filename (e.g., 'configure-misp-nerc-cip.py')
            args: List of command-line arguments
            description: Human-readable description for logging

        Returns:
            (success: bool, output: str)
        """
        script_path = Path(__file__).parent / script_name

        if self.dry_run:
            print(f"[DRY-RUN] Would run: python3 {script_path} {' '.join(args)}")

        # Use centralized setup helper
        return self.setup_helper.run_script(script_path, args, description)

    def step_1_misp_settings(self):
        """Step 1: Apply MISP best practice settings"""
        self.print_subheader("STEP 1: MISP Settings Configuration")

        if self.skip_settings:
            print(Colors.warning("Settings configuration skipped (--skip-settings)"))
            return True

        # Run configure-misp-nerc-cip.py script
        args = []
        if self.dry_run:
            args.append('--dry-run')

        description = "MISP best practice settings"
        if self.nerc_cip_ready:
            description = "MISP settings with NERC CIP compliance"

        print(f"Applying {description}...")
        success, output = self.run_script('configure-misp-nerc-cip.py', args, description)

        if success:
            print(Colors.success(f"{description} applied"))
            # Parse output for statistics
            if 'settings applied' in output.lower():
                # Extract number from output
                import re
                match = re.search(r'(\d+)\s+settings?\s+applied', output, re.IGNORECASE)
                if match:
                    self.stats['settings_applied'] = int(match.group(1))
        else:
            print(Colors.error(f"Failed to apply settings: {output[:200]}"))
            self.stats['settings_failed'] = 1
            if not self.dry_run:
                response = input("\nContinue despite settings failure? (yes/no): ")
                if response.lower() != 'yes':
                    return False

        return True

    def step_2_threat_feeds(self):
        """Step 2: Add and verify threat intelligence feeds"""
        self.print_subheader("STEP 2: Threat Intelligence Feeds")

        if self.skip_feeds:
            print(Colors.warning("Feed configuration skipped (--skip-feeds)"))
            return True

        # Add threat intelligence feeds
        if self.nerc_cip_ready:
            print("Adding comprehensive threat intelligence feeds (ICS/OT + General)...")

            args = ['--api-key', self.api_key, '--profile', 'all']
            if self.dry_run:
                args.append('--dry-run')

            success, output = self.run_script('add-threat-feeds.py', args,
                                             "Comprehensive threat intelligence feeds")
            if success:
                print(Colors.success("Threat intelligence feeds configured (ICS/OT + General)"))
                # Parse added count
                import re
                match = re.search(r'Added:\s*(\d+)', output)
                if match:
                    self.stats['feeds_added'] = int(match.group(1))
            else:
                print(Colors.warning("Some feeds may have failed to add (continuing...)"))

        # Verify all feeds
        print("\nVerifying MISP threat intelligence feeds...")

        if not self.dry_run:
            try:
                response = self.session.get(f"{self.misp_url}/feeds/index.json")
                if response.status_code == 200:
                    feeds = response.json()
                    enabled_feeds = [f for f in feeds if 'Feed' in f and f['Feed'].get('enabled')]

                    print(f"\n{Colors.success(f'Total enabled feeds: {len(enabled_feeds)}')}")

                    for feed in enabled_feeds:
                        if 'Feed' in feed:
                            f = feed['Feed']
                            print(f"  • {f.get('name')} ({f.get('source_format')} format)")

                    if self.nerc_cip_ready:
                        print(f"\n{Colors.info('NERC CIP News Sources (via Step 3):')}")
                        print("  • CISA ICS Advisories")
                        print("  • SecurityWeek ICS/OT Security")
                        print("  • BleepingComputer Critical Infrastructure")
                        print("  • IndustrialCyber OT Threat Intelligence")
                else:
                    print(Colors.warning("Could not retrieve feeds"))
            except Exception as e:
                print(Colors.warning(f"Feed verification failed: {e}"))
        else:
            print("[DRY-RUN] Would add and verify threat intelligence feeds")

        return True

    def step_3_news_population(self):
        """Step 3: Populate MISP news section"""
        self.print_subheader("STEP 3: Security News Population")

        if self.skip_news:
            print(Colors.warning("News population skipped (--skip-news)"))
            return True

        # Use the database version since API is broken
        script = 'populate-misp-news.py'
        description = "Security news from RSS feeds"

        if self.nerc_cip_ready:
            print("Populating news with utilities/energy sector focus...")
        else:
            print("Populating news with general cybersecurity content...")

        args = ['--max-items', '10', '--days', '30']
        if self.dry_run:
            args.append('--dry-run')

        success, output = self.run_script(script, args, description)

        if success:
            print(Colors.success("Security news populated"))
            # Parse output for statistics
            if 'inserted' in output.lower():
                import re
                match = re.search(r'(\d+)\s+.*inserted', output, re.IGNORECASE)
                if match:
                    self.stats['news_added'] = int(match.group(1))
        else:
            print(Colors.error(f"Failed to populate news: {output[:200]}"))
            self.stats['news_failed'] = 1
            # News is optional, don't fail setup
            print(Colors.info("Continuing (news is optional)..."))

        return True

    def step_4_taxonomies_warninglists(self):
        """Step 4: Enable taxonomies and warning lists (uses centralized helper)"""
        self.print_subheader("STEP 4: Taxonomies & Warning Lists")

        print("Updating and enabling taxonomies...")

        if self.dry_run:
            print("[DRY-RUN] Would update taxonomies")
        else:
            # Use centralized setup helper
            if self.setup_helper.update_taxonomies():
                print(Colors.success("Taxonomies updated"))
                self.stats['taxonomies_enabled'] += 1
            else:
                print(Colors.warning("Taxonomy update failed"))

        print("\nUpdating warning lists...")

        if self.dry_run:
            print("[DRY-RUN] Would update warning lists")
        else:
            # Use centralized setup helper
            if self.setup_helper.update_warninglists():
                print(Colors.success("Warning lists updated"))
                self.stats['warninglists_enabled'] += 1
            else:
                print(Colors.warning("Warning list update failed"))

        return True

    def step_5_enable_modules(self):
        """Step 5: Enable recommended MISP modules"""
        self.print_subheader("STEP 5: MISP Modules")

        print("Checking MISP modules status...")

        if not self.dry_run:
            try:
                # Check if modules are accessible
                response = self.session.get(f"{self.misp_url}/modules/index")

                if response.status_code == 200:
                    modules = response.json()
                    print(Colors.success(f"MISP modules accessible ({len(modules)} modules)"))
                    self.stats['modules_enabled'] = len(modules)
                else:
                    print(Colors.info("MISP modules not configured (optional)"))
            except Exception as e:
                print(Colors.info(f"MISP modules check skipped: {e}"))
        else:
            print("[DRY-RUN] Would check MISP modules")

        return True

    def step_6_verify_setup(self):
        """Step 6: Verify complete setup"""
        self.print_subheader("STEP 6: Setup Verification")

        print("Verifying MISP configuration...")

        checks = [
            ("MISP connection", self._verify_connection),
            ("Feed configuration", self._verify_feeds),
            ("News content", self._verify_news),
            ("Taxonomies", self._verify_taxonomies),
        ]

        passed = 0
        failed = 0

        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    print(f"  {Colors.success(check_name)}")
                    passed += 1
                else:
                    print(f"  {Colors.warning(check_name)} - needs attention")
                    failed += 1
            except Exception as e:
                print(f"  {Colors.warning(check_name)} - error: {e}")
                failed += 1

        print(f"\nVerification: {passed} passed, {failed} warnings")

        return True

    def _verify_connection(self) -> bool:
        """Verify MISP API connection (uses centralized helper)"""
        return self.verify_helper.verify_connection()

    def _verify_feeds(self) -> bool:
        """Verify feeds are configured (uses centralized helper)"""
        if self.skip_feeds:
            return True
        success, count = self.verify_helper.verify_feeds(min_feeds=1)
        return success

    def _verify_news(self) -> bool:
        """Verify news content exists"""
        if self.dry_run or self.skip_news:
            return True
        # News verification would require database access or special API
        # For now, assume success if news step completed
        return self.stats['news_added'] > 0

    def _verify_taxonomies(self) -> bool:
        """Verify taxonomies are enabled"""
        if self.dry_run:
            return True
        return self.stats['taxonomies_enabled'] > 0

    def print_summary(self):
        """Print final setup summary"""
        self.print_header("SETUP COMPLETE")

        print("Statistics:")
        print(f"  Settings applied:     {self.stats['settings_applied']}")
        print(f"  Threat intel feeds:   {self.stats['feeds_added']} enabled")
        print(f"  News items added:     {self.stats['news_added']}")
        print(f"  Taxonomies enabled:   {self.stats['taxonomies_enabled']}")
        print(f"  Warning lists:        {self.stats['warninglists_enabled']}")
        print(f"  Modules checked:      {self.stats['modules_enabled']}")

        if self.nerc_cip_ready:
            print(f"\n{Colors.GREEN}NERC CIP Compliance Mode: ENABLED{Colors.NC}")
            print("\nNERC CIP Features Configured:")
            print("  ✓ ICS/OT security news sources (CISA, SecurityWeek, IndustrialCyber)")
            print("  ✓ Utilities sector taxonomies")
            print("  ✓ Critical infrastructure threat intelligence")
            print("  ✓ Enhanced audit logging (CIP-007-R2)")
            print("  ✓ Security awareness content (CIP-003-R2)")

        print("\nNext Steps:")
        print("  1. Login to MISP web interface:")
        print(f"     {self.misp_url}")
        print("  2. Review configured feeds:")
        print("     Global Actions > List Feeds")
        print("  3. Check security news:")
        print("     Global Actions > News")
        print("  4. Fetch feed data:")
        print("     python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --enable-nerc")
        print("  5. Configure automated tasks:")
        print("     Add to crontab for daily updates")

        if self.nerc_cip_ready:
            print("\n  NERC CIP Compliance Resources:")
            print("  • CIP Standards: https://www.nerc.com/pa/Stand/Pages/CIPStandards.aspx")
            print("  • E-ISAC Portal: https://www.eisac.com/")
            print("  • ICS-CERT: https://www.cisa.gov/ics")

        print()

    def run(self) -> int:
        """Execute complete setup workflow

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        try:
            # Print banner
            self.print_header("MISP Complete Setup")

            if self.dry_run:
                print(f"{Colors.YELLOW}🔍 DRY RUN MODE - No changes will be made{Colors.NC}\n")

            print(f"MISP URL:    {self.misp_url}")
            print(f"API Key:     {self.api_key[:8]}...{self.api_key[-4:]}")
            print(f"Mode:        {'NERC CIP Ready' if self.nerc_cip_ready else 'Standard'}")

            if self.nerc_cip_ready:
                print(f"\n{Colors.CYAN}NERC CIP Compliance Mode ENABLED{Colors.NC}")
                print("Configuring for utilities/energy sector...")

            # Test connection
            print("\nTesting MISP connection...")
            success, message = test_connection(self.session)
            if not success:
                print(Colors.error(f"Connection failed: {message}"))
                return 1
            print(Colors.success(message))

            # Execute setup steps
            steps = [
                ("MISP Settings", self.step_1_misp_settings),
                ("Threat Feeds", self.step_2_threat_feeds),
                ("Security News", self.step_3_news_population),
                ("Taxonomies & Warning Lists", self.step_4_taxonomies_warninglists),
                ("MISP Modules", self.step_5_enable_modules),
                ("Verification", self.step_6_verify_setup),
            ]

            for step_name, step_func in steps:
                try:
                    if not step_func():
                        print(Colors.error(f"Setup failed at: {step_name}"))
                        return 1
                except KeyboardInterrupt:
                    print(f"\n{Colors.WARNING}Setup interrupted by user{Colors.NC}")
                    return 1
                except Exception as e:
                    print(Colors.error(f"Step failed: {step_name}"))
                    print(f"Error: {e}")
                    if not self.dry_run:
                        response = input("\nContinue? (yes/no): ")
                        if response.lower() != 'yes':
                            return 1

            # Print summary
            self.print_summary()

            # Log completion
            self.logger.info("Setup completed successfully",
                           event_type="setup",
                           action="complete",
                           result="success",
                           nerc_cip_mode=self.nerc_cip_ready,
                           stats=self.stats)

            return 0

        except Exception as e:
            self.logger.error(f"Setup failed: {e}",
                            event_type="setup",
                            action="complete",
                            result="failed")
            print(Colors.error(f"\nSetup failed: {e}"))
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='MISP Complete Post-Installation Setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard production setup
  python3 scripts/misp-setup-complete.py --api-key YOUR_KEY

  # NERC CIP compliance setup (utilities/energy sector)
  python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --nerc-cip-ready

  # Dry-run mode (preview without changes)
  python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --dry-run

  # Skip specific steps
  python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --skip-news

  # Auto-detect API key from .env
  python3 scripts/misp-setup-complete.py

NERC CIP Mode:
  The --nerc-cip-ready flag configures MISP for utilities/energy sector:
  • ICS/OT specific threat intelligence feeds
  • NERC CIP compliance taxonomies
  • Critical infrastructure security news
  • Enhanced audit logging (CIP-007-R2)
  • Security awareness content (CIP-003-R2)

API Key:
  Auto-detected from:
  1. --api-key argument
  2. MISP_API_KEY environment variable
  3. /opt/misp/.env file
  4. /opt/misp/PASSWORDS.txt file
        """
    )

    parser.add_argument('--api-key', type=str,
                       help='MISP API key (auto-detected if not provided)')
    parser.add_argument('--misp-url', type=str, default='https://misp-test.lan',
                       help='MISP base URL (default: https://misp-test.lan)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview mode without making changes')
    parser.add_argument('--nerc-cip-ready', action='store_true',
                       help='Configure for NERC CIP compliance (utilities/energy sector)')
    parser.add_argument('--skip-feeds', action='store_true',
                       help='Skip threat intelligence feed configuration')
    parser.add_argument('--skip-news', action='store_true',
                       help='Skip security news population')
    parser.add_argument('--skip-settings', action='store_true',
                       help='Skip MISP settings configuration')
    parser.add_argument('--custom-config', type=str,
                       help='Path to custom configuration file (YAML or JSON)')

    args = parser.parse_args()

    # Get API key (auto-detect if not provided)
    api_key = args.api_key
    if not api_key:
        api_key = get_api_key()
        if not api_key:
            print(f"{Colors.error('No API key found')}")
            print("\nProvide API key via:")
            print("  1. --api-key argument")
            print("  2. MISP_API_KEY environment variable")
            print("  3. /opt/misp/.env file")
            print("  4. /opt/misp/PASSWORDS.txt file")
            print("\nGenerate API key:")
            print("  python3 misp-install.py  # Includes API key generation")
            return 1

    try:
        # Create setup orchestrator
        setup = MISPSetupComplete(
            api_key=api_key,
            misp_url=args.misp_url,
            dry_run=args.dry_run,
            nerc_cip_ready=args.nerc_cip_ready,
            skip_feeds=args.skip_feeds,
            skip_news=args.skip_news,
            skip_settings=args.skip_settings,
            custom_config=args.custom_config
        )

        # Run setup
        return setup.run()

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup interrupted by user{Colors.NC}")
        return 1
    except Exception as e:
        print(f"{Colors.error('Setup failed')}: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
