#!/usr/bin/env python3
"""
MISP Feed Status Checker
Version: 1.0
Date: 2025-10-14

Purpose:
    Check which MISP feeds are currently enabled vs available.
    Helps verify feed configuration after running configure-misp-nerc-cip.py

Usage:
    python3 scripts/check-misp-feeds.py
    python3 scripts/check-misp-feeds.py --show-all    # Show all feeds (enabled and disabled)
    python3 scripts/check-misp-feeds.py --nerc-only   # Show only NERC CIP recommended feeds

Output:
    - Summary of enabled vs disabled feeds
    - Detailed list of feed names and status
    - Highlights NERC CIP recommended feeds

Requirements:
    - MISP must be running (docker containers up)
    - /opt/misp directory must exist
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Import centralized modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from misp_logger import get_logger
from lib.database_manager import DatabaseManager

# NERC CIP recommended feeds (from configure-misp-nerc-cip.py)
NERC_CIP_FEEDS = [
    "CIRCL OSINT Feed",
    "Abuse.ch URLhaus",
    "Abuse.ch ThreatFox",
    "Abuse.ch Feodo Tracker",
    "Abuse.ch SSL Blacklist",
    "OpenPhish url",
    "Phishtank online valid phishing",
    "Bambenek Consulting - C2 All Indicator Feed",
    "Botvrij.eu",
    "Blocklist.de",
    "DigitalSide Threat-Intel",
    "Cybercrime-Tracker - All",
    "MalwareBazaar Recent Additions",
    "Dataplane.org - sipquery",
    "Dataplane.org - vncrfb",
]


class MISPFeedChecker:
    """Check MISP feed status"""

    def __init__(self, show_all: bool = False, nerc_only: bool = False):
        self.misp_dir = Path("/opt/misp")
        self.show_all = show_all
        self.nerc_only = nerc_only
        self.logger = get_logger('check-misp-feeds', 'misp:feeds')

        # Use centralized DatabaseManager
        self.db_manager = DatabaseManager(self.misp_dir)
        self.mysql_password = self.db_manager.get_mysql_password() or 'misp'

    def check_docker_running(self) -> bool:
        """Check if MISP containers are running"""
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                check=True
            )

            # Parse JSON output (one JSON object per line)
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    containers.append(json.loads(line))

            # Check if misp-core is running
            for container in containers:
                if 'misp-core' in container.get('Name', '') and container.get('State') == 'running':
                    return True

            return False

        except subprocess.CalledProcessError:
            return False
        except json.JSONDecodeError:
            return False

    def get_feeds(self) -> List[Dict]:
        """Get list of all feeds from MISP"""
        try:
            # Use MISP CLI to get feeds list
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 '/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', 'MISP.feeds_list'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                check=True
            )

            # Try to parse JSON output
            # Note: MISP CLI might return non-JSON output, so we'll use a different approach

            # Alternative: Query feeds via database
            db_result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 'SELECT id, name, enabled, url, source_format FROM feeds ORDER BY name;'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                check=True
            )

            # Parse MySQL output
            feeds = []
            lines = db_result.stdout.strip().split('\n')

            if len(lines) <= 1:
                # No feeds or just header
                return []

            # Skip header line
            for line in lines[1:]:
                if line.strip():
                    # Split by tabs (MySQL default)
                    parts = line.split('\t')
                    if len(parts) >= 5:
                        feeds.append({
                            'id': parts[0],
                            'name': parts[1],
                            'enabled': parts[2] == '1',
                            'url': parts[3],
                            'source_format': parts[4]
                        })

            return feeds

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get feeds: {e.stderr}",
                            event_type="feed_check",
                            action="get_feeds",
                            result="failed")
            return []
        except Exception as e:
            self.logger.error(f"Error getting feeds: {e}",
                            event_type="feed_check",
                            action="get_feeds",
                            result="failed")
            return []

    def analyze_feeds(self, feeds: List[Dict]) -> Dict:
        """Analyze feed status"""
        enabled_feeds = [f for f in feeds if f['enabled']]
        disabled_feeds = [f for f in feeds if not f['enabled']]

        # Check NERC CIP recommended feeds
        nerc_enabled = []
        nerc_disabled = []

        for feed in feeds:
            feed_name = feed['name']
            # Check if feed name matches any NERC CIP recommendation
            for nerc_feed in NERC_CIP_FEEDS:
                if nerc_feed.lower() in feed_name.lower():
                    if feed['enabled']:
                        nerc_enabled.append(feed)
                    else:
                        nerc_disabled.append(feed)
                    break

        return {
            'total': len(feeds),
            'enabled': len(enabled_feeds),
            'disabled': len(disabled_feeds),
            'enabled_feeds': enabled_feeds,
            'disabled_feeds': disabled_feeds,
            'nerc_enabled': nerc_enabled,
            'nerc_disabled': nerc_disabled,
            'nerc_total': len(nerc_enabled) + len(nerc_disabled)
        }

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")

    def print_feed(self, feed: Dict, is_nerc: bool = False):
        """Print feed details"""
        status = "✓ ENABLED " if feed['enabled'] else "✗ DISABLED"
        nerc_marker = " [NERC CIP]" if is_nerc else ""

        print(f"{status}{nerc_marker}")
        print(f"  Name:   {feed['name']}")
        print(f"  ID:     {feed['id']}")
        print(f"  Format: {feed['source_format']}")
        print(f"  URL:    {feed['url'][:80]}...")
        print()

    def run(self):
        """Main execution"""
        self.print_header("MISP Feed Status Checker")

        # Check if Docker is running
        print("Checking MISP status...")
        if not self.check_docker_running():
            print("❌ ERROR: MISP containers are not running")
            print("\nStart MISP with:")
            print("  cd /opt/misp && sudo docker compose up -d")
            self.logger.error("MISP containers not running",
                            event_type="feed_check",
                            action="check_docker",
                            result="failed")
            return 1

        print("✓ MISP is running\n")

        # Get feeds
        print("Querying MISP feeds...")
        feeds = self.get_feeds()

        if not feeds:
            print("⚠️  No feeds found or unable to query feeds")
            print("\nThis could mean:")
            print("  1. No feeds are configured yet")
            print("  2. Database query failed")
            print("  3. MISP needs to be restarted")
            return 1

        print(f"✓ Found {len(feeds)} total feeds\n")

        # Analyze feeds
        analysis = self.analyze_feeds(feeds)

        # Print summary
        self.print_header("Feed Summary")
        print(f"Total Feeds:     {analysis['total']}")
        print(f"Enabled:         {analysis['enabled']} ({analysis['enabled']/analysis['total']*100:.1f}%)")
        print(f"Disabled:        {analysis['disabled']} ({analysis['disabled']/analysis['total']*100:.1f}%)")
        print()
        print(f"NERC CIP Recommended Feeds:")
        print(f"  Enabled:       {len(analysis['nerc_enabled'])}/{len(NERC_CIP_FEEDS)}")
        print(f"  Disabled:      {len(analysis['nerc_disabled'])}/{len(NERC_CIP_FEEDS)}")
        print(f"  Not Found:     {len(NERC_CIP_FEEDS) - analysis['nerc_total']}")

        # Show enabled NERC CIP feeds
        if analysis['nerc_enabled']:
            self.print_header("Enabled NERC CIP Feeds")
            for feed in analysis['nerc_enabled']:
                self.print_feed(feed, is_nerc=True)

        # Show disabled NERC CIP feeds
        if analysis['nerc_disabled']:
            self.print_header("Disabled NERC CIP Feeds (Should Enable)")
            for feed in analysis['nerc_disabled']:
                self.print_feed(feed, is_nerc=True)

        # Show missing NERC CIP feeds
        found_nerc_names = [f['name'] for f in analysis['nerc_enabled'] + analysis['nerc_disabled']]
        missing_nerc = []
        for nerc_feed in NERC_CIP_FEEDS:
            found = False
            for found_name in found_nerc_names:
                if nerc_feed.lower() in found_name.lower():
                    found = True
                    break
            if not found:
                missing_nerc.append(nerc_feed)

        if missing_nerc:
            self.print_header("Missing NERC CIP Feeds (Not Available)")
            print("These feeds are recommended but not found in MISP:")
            for feed_name in missing_nerc:
                print(f"  • {feed_name}")
            print("\nNote: These feeds may need to be added manually or might be")
            print("      available under different names in your MISP version.")

        # Show all enabled feeds (if requested)
        if self.show_all and not self.nerc_only:
            self.print_header("All Enabled Feeds")
            for feed in analysis['enabled_feeds']:
                is_nerc = any(nerc.lower() in feed['name'].lower() for nerc in NERC_CIP_FEEDS)
                self.print_feed(feed, is_nerc=is_nerc)

        # Show all disabled feeds (if requested)
        if self.show_all and not self.nerc_only:
            self.print_header("All Disabled Feeds")
            for feed in analysis['disabled_feeds']:
                is_nerc = any(nerc.lower() in feed['name'].lower() for nerc in NERC_CIP_FEEDS)
                self.print_feed(feed, is_nerc=is_nerc)

        # Show next steps
        if analysis['nerc_disabled'] or missing_nerc:
            self.print_header("Next Steps")
            print("To enable feeds:")
            print("  1. Open MISP web interface: https://misp.lan")
            print("  2. Navigate to: Sync Actions > List Feeds")
            print("  3. Click 'Enable' for each feed you want to activate")
            print("  4. Click 'Fetch and Store' to download feed data")
            print()
            print("To automate feed enablement, see:")
            print("  docs/NERC_CIP_CONFIGURATION.md - Section on feed management")

        # Log summary
        self.logger.info(f"Feed check complete: {analysis['enabled']}/{analysis['total']} enabled",
                        event_type="feed_check",
                        action="complete",
                        result="success",
                        total_feeds=analysis['total'],
                        enabled_feeds=analysis['enabled'],
                        nerc_enabled=len(analysis['nerc_enabled']))

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Check MISP feed status',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/check-misp-feeds.py                # Show summary and NERC CIP feeds
  python3 scripts/check-misp-feeds.py --show-all     # Show all feeds (enabled and disabled)
  python3 scripts/check-misp-feeds.py --nerc-only    # Show only NERC CIP feeds
        """
    )
    parser.add_argument('--show-all', action='store_true',
                       help='Show all feeds (enabled and disabled)')
    parser.add_argument('--nerc-only', action='store_true',
                       help='Show only NERC CIP recommended feeds')

    args = parser.parse_args()

    checker = MISPFeedChecker(show_all=args.show_all, nerc_only=args.nerc_only)
    return checker.run()


if __name__ == '__main__':
    sys.exit(main())
