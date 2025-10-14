#!/usr/bin/env python3
"""
MISP Feed Status Checker (API Version)
Version: 2.0
Date: 2025-10-14

Purpose:
    Check which MISP feeds are currently enabled vs available using REST API.
    Helps verify feed configuration after running add-nerc-cip-news-feeds-api.py

    This is the API-based version that replaces direct database access.

Usage:
    python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY
    python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --show-all
    python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --nerc-only
    python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --enable-nerc

Features:
    - Uses MISP REST API (no database access)
    - Lists all feeds with status (enabled/disabled)
    - Highlights NERC CIP recommended feeds
    - Can enable/disable feeds via API
    - Summary statistics

Output:
    - Summary of enabled vs disabled feeds
    - Detailed list of feed names and status
    - Highlights NERC CIP recommended feeds

Requirements:
    - MISP must be running (docker containers up)
    - MISP API key with proper permissions
    - Python packages: requests
"""

import sys
import json
import requests
import urllib3
from pathlib import Path
from typing import Dict, List
import argparse

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import centralized logger
sys.path.insert(0, str(Path(__file__).parent.parent))
from misp_logger import get_logger

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


class MISPFeedCheckerAPI:
    """Check MISP feed status using REST API"""

    def __init__(self, api_key: str, misp_url: str = "https://misp-test.lan",
                 show_all: bool = False, nerc_only: bool = False, enable_nerc: bool = False):
        self.misp_url = misp_url.rstrip('/')
        self.api_key = api_key
        self.show_all = show_all
        self.nerc_only = nerc_only
        self.enable_nerc = enable_nerc
        self.logger = get_logger('check-misp-feeds-api', 'misp:feeds')

        self.headers = {
            'Authorization': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Test API connection
        self.test_connection()

    def test_connection(self) -> bool:
        """Test MISP API connection"""
        try:
            response = requests.get(
                f"{self.misp_url}/servers/getPyMISPVersion.json",
                headers=self.headers,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                version_data = response.json()
                version = version_data.get('version', 'unknown')
                self.logger.info(f"Connected to MISP {version}",
                               event_type="feed_check",
                               action="connect",
                               result="success")
                print(f"✓ Connected to MISP {version}\n")
                return True
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

        except Exception as e:
            self.logger.error(f"Failed to connect to MISP: {e}",
                            event_type="feed_check",
                            action="connect",
                            result="failed")
            print(f"❌ Failed to connect to MISP: {e}")
            raise

    def get_feeds(self) -> List[Dict]:
        """Get list of all feeds from MISP via API"""
        try:
            response = requests.get(
                f"{self.misp_url}/feeds/index",
                headers=self.headers,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                feeds_data = response.json()

                # MISP may return {'Feed': [...]} or just [...]
                feeds = []
                if isinstance(feeds_data, dict) and 'Feed' in feeds_data:
                    feeds_raw = feeds_data['Feed']
                elif isinstance(feeds_data, list):
                    feeds_raw = feeds_data
                else:
                    return []

                # Normalize feed format
                for feed in feeds_raw:
                    # Handle both {'Feed': {...}} and direct feed object
                    feed_data = feed.get('Feed', feed)

                    feeds.append({
                        'id': feed_data.get('id'),
                        'name': feed_data.get('name', 'Unknown'),
                        'enabled': feed_data.get('enabled', '0') in ['1', 1, True],
                        'url': feed_data.get('url', ''),
                        'source_format': feed_data.get('source_format', 'csv'),
                        'provider': feed_data.get('provider', ''),
                        'caching_enabled': feed_data.get('caching_enabled', '0') in ['1', 1, True]
                    })

                return feeds

            else:
                self.logger.error(f"Failed to get feeds: HTTP {response.status_code}",
                                event_type="feed_check",
                                action="get_feeds",
                                result="failed",
                                status_code=response.status_code)
                return []

        except Exception as e:
            self.logger.error(f"Error getting feeds: {e}",
                            event_type="feed_check",
                            action="get_feeds",
                            result="failed",
                            error=str(e))
            return []

    def enable_feed(self, feed_id: str) -> bool:
        """Enable a feed via API"""
        try:
            response = requests.post(
                f"{self.misp_url}/feeds/enable/{feed_id}",
                headers=self.headers,
                verify=False,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return True
            else:
                self.logger.warning(f"Failed to enable feed {feed_id}: HTTP {response.status_code}",
                                  event_type="feed_check",
                                  action="enable_feed",
                                  result="failed",
                                  feed_id=feed_id)
                return False

        except Exception as e:
            self.logger.error(f"Error enabling feed {feed_id}: {e}",
                            event_type="feed_check",
                            action="enable_feed",
                            result="failed",
                            feed_id=feed_id,
                            error=str(e))
            return False

    def disable_feed(self, feed_id: str) -> bool:
        """Disable a feed via API"""
        try:
            response = requests.post(
                f"{self.misp_url}/feeds/disable/{feed_id}",
                headers=self.headers,
                verify=False,
                timeout=30
            )

            if response.status_code in [200, 201]:
                return True
            else:
                self.logger.warning(f"Failed to disable feed {feed_id}: HTTP {response.status_code}",
                                  event_type="feed_check",
                                  action="disable_feed",
                                  result="failed",
                                  feed_id=feed_id)
                return False

        except Exception as e:
            self.logger.error(f"Error disabling feed {feed_id}: {e}",
                            event_type="feed_check",
                            action="disable_feed",
                            result="failed",
                            feed_id=feed_id,
                            error=str(e))
            return False

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
        print(f"  Name:     {feed['name']}")
        print(f"  ID:       {feed['id']}")
        print(f"  Provider: {feed['provider']}")
        print(f"  Format:   {feed['source_format']}")
        if len(feed['url']) > 80:
            print(f"  URL:      {feed['url'][:77]}...")
        else:
            print(f"  URL:      {feed['url']}")
        print()

    def enable_nerc_feeds(self, nerc_disabled: List[Dict]) -> int:
        """Enable all disabled NERC CIP feeds"""
        if not nerc_disabled:
            print("✓ All NERC CIP recommended feeds are already enabled!\n")
            return 0

        self.print_header("Enabling NERC CIP Feeds")
        print(f"Found {len(nerc_disabled)} disabled NERC CIP feeds\n")

        enabled_count = 0
        for feed in nerc_disabled:
            print(f"Enabling: {feed['name']}... ", end='', flush=True)
            if self.enable_feed(feed['id']):
                print("✓")
                enabled_count += 1
                self.logger.info(f"Enabled feed: {feed['name']}",
                               event_type="feed_check",
                               action="enable_feed",
                               result="success",
                               feed_id=feed['id'],
                               feed_name=feed['name'])
            else:
                print("✗ Failed")

        print()
        print(f"✓ Enabled {enabled_count}/{len(nerc_disabled)} NERC CIP feeds")
        return enabled_count

    def run(self):
        """Main execution"""
        self.print_header("MISP Feed Status Checker (API Version)")

        # Get feeds via API
        print("Querying MISP feeds via API...")
        feeds = self.get_feeds()

        if not feeds:
            print("⚠️  No feeds found or unable to query feeds")
            print("\nThis could mean:")
            print("  1. No feeds are configured yet")
            print("  2. API query failed")
            print("  3. API key doesn't have proper permissions")
            return 1

        print(f"✓ Found {len(feeds)} total feeds\n")

        # Analyze feeds
        analysis = self.analyze_feeds(feeds)

        # Enable NERC feeds if requested
        if self.enable_nerc:
            self.enable_nerc_feeds(analysis['nerc_disabled'])
            # Re-fetch feeds to show updated status
            feeds = self.get_feeds()
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
            if analysis['nerc_disabled']:
                print("To enable NERC CIP feeds automatically:")
                print(f"  python3 scripts/check-misp-feeds-api.py --api-key {self.api_key[:8]}... --enable-nerc")
                print()
            print("To enable feeds manually:")
            print("  1. Open MISP web interface: https://misp.lan")
            print("  2. Navigate to: Sync Actions > List Feeds")
            print("  3. Click 'Enable' for each feed you want to activate")
            print("  4. Click 'Fetch and Store' to download feed data")

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
        description='Check MISP feed status using REST API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check feed status
  python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY

  # Show all feeds (enabled and disabled)
  python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --show-all

  # Show only NERC CIP feeds
  python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --nerc-only

  # Enable all NERC CIP feeds automatically
  python3 scripts/check-misp-feeds-api.py --api-key YOUR_KEY --enable-nerc

API Key Setup:
  1. Login to MISP web interface
  2. Navigate to: Global Actions > My Profile > Auth Keys
  3. Click "Add authentication key"
  4. Set "Allowed IPs" to include Docker network (172.0.0.0/8) or leave blank
  5. Copy the generated key
        """
    )

    parser.add_argument('--api-key', type=str, required=True,
                       help='MISP API key')
    parser.add_argument('--misp-url', type=str, default='https://misp-test.lan',
                       help='MISP URL (default: https://misp-test.lan)')
    parser.add_argument('--show-all', action='store_true',
                       help='Show all feeds (enabled and disabled)')
    parser.add_argument('--nerc-only', action='store_true',
                       help='Show only NERC CIP recommended feeds')
    parser.add_argument('--enable-nerc', action='store_true',
                       help='Enable all disabled NERC CIP feeds automatically')

    args = parser.parse_args()

    try:
        checker = MISPFeedCheckerAPI(
            api_key=args.api_key,
            misp_url=args.misp_url,
            show_all=args.show_all,
            nerc_only=args.nerc_only,
            enable_nerc=args.enable_nerc
        )
        return checker.run()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify MISP is running: cd /opt/misp && sudo docker compose ps")
        print("  2. Check API key is valid and IP whitelist includes Docker network")
        print("  3. Verify MISP URL is correct")
        print("  4. Check /opt/misp/logs/ for detailed error logs")
        return 1


if __name__ == '__main__':
    sys.exit(main())
