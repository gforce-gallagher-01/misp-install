#!/usr/bin/env python3
"""
Add NERC CIP News Feeds to MISP (API Version)
Version: 2.0
Date: 2025-10-14

Purpose:
    Add NERC CIP-related news feeds (RSS/Atom) to MISP for security awareness
    and threat intelligence updates using MISP REST API.

    This is the API-based version that replaces direct database access.

Usage:
    python3 scripts/add-nerc-cip-news-feeds-api.py --api-key YOUR_KEY
    python3 scripts/add-nerc-cip-news-feeds-api.py --api-key YOUR_KEY --dry-run
    python3 scripts/add-nerc-cip-news-feeds-api.py --api-key YOUR_KEY --list

Features:
    - Uses MISP REST API (no database access)
    - Adds 6+ NERC CIP-related news feeds to MISP
    - CISA ICS-CERT advisories (official US government)
    - Industrial Cyber news (ICS/SCADA focus)
    - SecurityWeek ICS section
    - Bleeping Computer critical infrastructure
    - Dry-run mode for testing
    - Duplicate detection via API

IMPORTANT - NERC CIP Compliance Note:
    News feeds provide security awareness content for CIP-003-R2 training.
    These are informational RSS feeds, not threat intelligence IOCs.
    Use for security awareness, incident response context, and training.

Requirements:
    - MISP must be running (docker containers up)
    - MISP API key with proper permissions
    - Python packages: requests
"""

import subprocess
import sys
import json
import requests
import urllib3
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import centralized logger
sys.path.insert(0, str(Path(__file__).parent.parent))
from misp_logger import get_logger

# NERC CIP-Related News Feeds
NERC_CIP_NEWS_FEEDS = [
    {
        "name": "CISA ICS Advisories",
        "provider": "US CISA",
        "url": "https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml",
        "source_format": "csv",  # MISP will auto-detect RSS/Atom
        "input_source": "network",
        "enabled": True,
        "caching_enabled": True,
        "distribution": 0,  # Your organization only
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": True,
        "description": "Official CISA Industrial Control Systems advisories. Critical for NERC CIP compliance - covers ICS/SCADA vulnerabilities, solar inverters, wind turbines, battery BMS, substation automation.",
        "use_case": "CIP-010-R3 (Vulnerability Assessment), CIP-003-R2 (Security Awareness)"
    },
    {
        "name": "CISA ICS Medical Advisories",
        "provider": "US CISA",
        "url": "https://www.cisa.gov/cybersecurity-advisories/ics-medical-advisories.xml",
        "source_format": "csv",
        "input_source": "network",
        "enabled": False,  # Medical sector, lower priority for energy
        "caching_enabled": True,
        "distribution": 0,
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": False,
        "description": "CISA ICS advisories for medical devices. Lower priority for energy sector but may have cross-sector relevance."
    },
    {
        "name": "CISA All Cybersecurity Advisories",
        "provider": "US CISA",
        "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "source_format": "csv",
        "input_source": "network",
        "enabled": False,  # Too broad, use ICS-specific instead
        "caching_enabled": True,
        "distribution": 0,
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": False,
        "description": "All CISA cybersecurity advisories (not just ICS). Very broad feed - consider using ICS-specific feed instead."
    },
    {
        "name": "SecurityWeek - ICS/SCADA News",
        "provider": "SecurityWeek",
        "url": "https://www.securityweek.com/category/ics-ot-security/feed/",
        "source_format": "csv",
        "input_source": "network",
        "enabled": True,
        "caching_enabled": True,
        "distribution": 0,
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": True,
        "description": "SecurityWeek ICS/OT security news. Industry news about ICS/SCADA threats, vulnerabilities, and attacks. Good for security awareness training.",
        "use_case": "CIP-003-R2 (Security Awareness Training), CIP-008-R1 (Incident Response context)"
    },
    {
        "name": "Bleeping Computer - Critical Infrastructure",
        "provider": "Bleeping Computer",
        "url": "https://www.bleepingcomputer.com/feed/tag/critical-infrastructure/",
        "source_format": "csv",
        "input_source": "network",
        "enabled": True,
        "caching_enabled": True,
        "distribution": 0,
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": True,
        "description": "Bleeping Computer critical infrastructure news. Covers ransomware attacks on utilities, ICS malware, and critical infrastructure threats.",
        "use_case": "CIP-003-R2 (Security Awareness), CIP-008-R1 (Incident Response trends)"
    },
    {
        "name": "Industrial Cyber - News",
        "provider": "Industrial Cyber",
        "url": "https://industrialcyber.co/feed/",
        "source_format": "csv",
        "input_source": "network",
        "enabled": True,
        "caching_enabled": True,
        "distribution": 0,
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": True,
        "description": "Industrial Cyber news - dedicated ICS/SCADA/OT security news. Excellent coverage of energy sector threats, NERC advisories, and ICS vulnerabilities.",
        "use_case": "CIP-003-R2 (Security Awareness), Industry threat landscape"
    },
    {
        "name": "NERC - News & Events",
        "provider": "NERC",
        "url": "https://www.nerc.com/news/Pages/default.aspx",  # May not have RSS
        "source_format": "csv",
        "input_source": "network",
        "enabled": False,  # Check if RSS available
        "caching_enabled": True,
        "distribution": 0,
        "sharing_group_id": 0,
        "tag_id": 0,
        "default": False,
        "nerc_cip_relevant": True,
        "description": "NERC official news and events. Note: May not have RSS feed - check NERC website for feed availability.",
        "use_case": "NERC CIP standard updates, compliance guidance"
    }
]


class NERCCIPNewsFeedManagerAPI:
    """Manage NERC CIP-related news feeds in MISP using REST API"""

    def __init__(self, api_key: str, misp_url: str = "https://misp-test.lan", dry_run: bool = False):
        self.misp_url = misp_url.rstrip('/')
        self.api_key = api_key
        self.dry_run = dry_run
        self.logger = get_logger('add-nerc-cip-news-feeds-api', 'misp:feeds')

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
                               event_type="feed_add",
                               action="connect",
                               result="success")
                print(f"✓ Connected to MISP {version}\n")
                return True
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

        except Exception as e:
            self.logger.error(f"Failed to connect to MISP: {e}",
                            event_type="feed_add",
                            action="connect",
                            result="failed")
            print(f"❌ Failed to connect to MISP: {e}")
            raise

    def get_existing_feeds(self) -> List[Dict]:
        """Get list of existing feeds from MISP via API"""
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
                if isinstance(feeds_data, dict) and 'Feed' in feeds_data:
                    return feeds_data['Feed']
                elif isinstance(feeds_data, list):
                    return feeds_data
                else:
                    return []
            else:
                self.logger.warning(f"Could not fetch feeds: HTTP {response.status_code}",
                                  event_type="feed_add",
                                  action="get_feeds",
                                  result="failed")
                return []

        except Exception as e:
            self.logger.warning(f"Error fetching feeds: {e}",
                              event_type="feed_add",
                              action="get_feeds",
                              result="failed")
            return []

    def feed_exists(self, feed_url: str, existing_feeds: List[Dict]) -> Optional[Dict]:
        """Check if feed already exists by URL"""
        for feed in existing_feeds:
            # Handle both {'Feed': {...}} and direct feed object
            feed_data = feed.get('Feed', feed)
            if feed_data.get('url') == feed_url:
                return feed_data
        return None

    def add_feed(self, feed: Dict, existing_feeds: List[Dict]) -> bool:
        """Add a news feed to MISP via API"""

        if self.dry_run:
            print(f"[DRY-RUN] Would add feed: {feed['name']}")
            print(f"  URL: {feed['url']}")
            print(f"  Enabled: {feed['enabled']}")
            print(f"  NERC CIP Relevant: {feed.get('nerc_cip_relevant', False)}")
            return True

        # Check if feed already exists
        existing = self.feed_exists(feed['url'], existing_feeds)
        if existing:
            print(f"⚠️  Feed already exists: {feed['name']}")
            print(f"    ID: {existing.get('id')}")
            self.logger.info(f"Feed already exists: {feed['name']}",
                           event_type="feed_add",
                           action="skip",
                           result="already_exists",
                           feed_name=feed['name'])
            return False

        try:
            # Prepare API request data
            data = {
                'name': feed['name'],
                'provider': feed['provider'],
                'url': feed['url'],
                'source_format': feed['source_format'],
                'input_source': feed['input_source'],
                'enabled': feed['enabled'],
                'caching_enabled': feed['caching_enabled'],
                'distribution': feed['distribution'],
                'sharing_group_id': feed['sharing_group_id'],
                'tag_id': feed['tag_id'],
                'default': feed['default']
            }

            # POST to /feeds/add
            response = requests.post(
                f"{self.misp_url}/feeds/add",
                headers=self.headers,
                json=data,
                verify=False,
                timeout=30
            )

            if response.status_code in [200, 201]:
                result_data = response.json()
                feed_id = None

                # Extract feed ID from response
                if isinstance(result_data, dict):
                    if 'Feed' in result_data:
                        feed_id = result_data['Feed'].get('id')
                    elif 'id' in result_data:
                        feed_id = result_data['id']

                print(f"✅ Added feed: {feed['name']}")
                if feed_id:
                    print(f"   Feed ID: {feed_id}")

                self.logger.info(f"Added feed: {feed['name']}",
                               event_type="feed_add",
                               action="add",
                               result="success",
                               feed_name=feed['name'],
                               feed_url=feed['url'],
                               feed_id=feed_id)
                return True
            else:
                print(f"❌ Failed to add feed: {feed['name']}")
                print(f"   HTTP {response.status_code}: {response.text[:200]}")
                self.logger.error(f"Failed to add feed: {feed['name']}",
                                event_type="feed_add",
                                action="add",
                                result="failed",
                                feed_name=feed['name'],
                                status_code=response.status_code,
                                response=response.text[:200])
                return False

        except Exception as e:
            print(f"❌ Failed to add feed: {feed['name']}")
            print(f"   Error: {e}")
            self.logger.error(f"Failed to add feed: {feed['name']}",
                            event_type="feed_add",
                            action="add",
                            result="failed",
                            feed_name=feed['name'],
                            error=str(e))
            return False

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")

    def list_feeds(self):
        """List available NERC CIP news feeds"""
        self.print_header("NERC CIP News Feeds Available")

        print("These RSS/Atom feeds provide security news for NERC CIP compliance:")
        print("- CIP-003-R2: Security awareness training content")
        print("- CIP-008-R1: Incident response context and trends")
        print("- CIP-010-R3: Vulnerability assessment information")
        print()

        # NERC CIP Relevant feeds
        nerc_feeds = [f for f in NERC_CIP_NEWS_FEEDS if f.get('nerc_cip_relevant')]
        other_feeds = [f for f in NERC_CIP_NEWS_FEEDS if not f.get('nerc_cip_relevant')]

        print(f"NERC CIP Relevant Feeds ({len(nerc_feeds)}):")
        print("─" * 80)
        for feed in nerc_feeds:
            status = "✓ Enabled" if feed['enabled'] else "○ Disabled"
            print(f"\n{status} - {feed['name']}")
            print(f"  Provider: {feed['provider']}")
            print(f"  URL: {feed['url']}")
            print(f"  Description: {feed.get('description', 'N/A')}")
            if 'use_case' in feed:
                print(f"  Use Case: {feed['use_case']}")

        if other_feeds:
            print(f"\n\nOther Feeds ({len(other_feeds)}):")
            print("─" * 80)
            for feed in other_feeds:
                status = "✓ Enabled" if feed['enabled'] else "○ Disabled"
                print(f"\n{status} - {feed['name']}")
                print(f"  Provider: {feed['provider']}")
                print(f"  URL: {feed['url']}")
                print(f"  Description: {feed.get('description', 'N/A')}")

    def run(self, list_only: bool = False):
        """Main execution"""
        self.print_header("Add NERC CIP News Feeds to MISP (API Version)")

        # List feeds if requested
        if list_only:
            self.list_feeds()
            return 0

        # Get existing feeds from API
        print("Fetching existing feeds from MISP...")
        existing_feeds = self.get_existing_feeds()
        print(f"✓ Found {len(existing_feeds)} existing feeds\n")

        # Add feeds
        feeds_to_add = [f for f in NERC_CIP_NEWS_FEEDS if f['enabled']]

        if self.dry_run:
            print(f"[DRY-RUN] Would add {len(feeds_to_add)} feeds:\n")
        else:
            print(f"Adding {len(feeds_to_add)} NERC CIP news feeds...\n")

        added_count = 0
        skipped_count = 0
        failed_count = 0

        for feed in feeds_to_add:
            result = self.add_feed(feed, existing_feeds)
            if result:
                added_count += 1
            elif self.feed_exists(feed['url'], existing_feeds):
                skipped_count += 1
            else:
                failed_count += 1

        # Summary
        self.print_header("Summary")
        if self.dry_run:
            print(f"[DRY-RUN] Would add {added_count} feeds")
        else:
            print(f"✅ Added: {added_count}")
            print(f"⚠️  Skipped (already exist): {skipped_count}")
            print(f"❌ Failed: {failed_count}")
            print()

        # Next steps
        self.print_header("Next Steps")
        print("1. Login to MISP web interface: https://misp.lan")
        print("2. Navigate to: Sync Actions > List Feeds")
        print("3. Find the newly added news feeds")
        print("4. Click 'Fetch and Store' to download initial content")
        print()
        print("Note: News feeds provide context, not threat intelligence IOCs")
        print("Use for:")
        print("  • CIP-003-R2: Security awareness training materials")
        print("  • CIP-008-R1: Incident response context")
        print("  • CIP-010-R3: Vulnerability assessment information")
        print()

        # Log summary
        self.logger.info(f"Feed addition complete: {added_count} added, {skipped_count} skipped, {failed_count} failed",
                        event_type="feed_add",
                        action="complete",
                        result="success",
                        added_count=added_count,
                        skipped_count=skipped_count,
                        failed_count=failed_count)

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Add NERC CIP news feeds to MISP using REST API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add NERC CIP news feeds to MISP
  python3 scripts/add-nerc-cip-news-feeds-api.py --api-key YOUR_KEY

  # Preview feeds without adding
  python3 scripts/add-nerc-cip-news-feeds-api.py --api-key YOUR_KEY --dry-run

  # List available feeds
  python3 scripts/add-nerc-cip-news-feeds-api.py --api-key YOUR_KEY --list

API Key Setup:
  1. Login to MISP web interface
  2. Navigate to: Global Actions > My Profile > Auth Keys
  3. Click "Add authentication key"
  4. Set "Allowed IPs" to include Docker network (172.0.0.0/8) or leave blank
  5. Copy the generated key

Available News Feeds:
  • CISA ICS Advisories (Official US Government)
  • SecurityWeek ICS/SCADA News
  • Bleeping Computer Critical Infrastructure
  • Industrial Cyber News (ICS/SCADA focus)
  • NERC Official News

NERC CIP Use Cases:
  CIP-003-R2: Security awareness training content
  CIP-008-R1: Incident response context and trends
  CIP-010-R3: Vulnerability assessment information
        """
    )

    parser.add_argument('--api-key', type=str, required=True,
                       help='MISP API key')
    parser.add_argument('--misp-url', type=str, default='https://misp-test.lan',
                       help='MISP URL (default: https://misp-test.lan)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview feeds without adding them')
    parser.add_argument('--list', action='store_true',
                       help='List available feeds')

    args = parser.parse_args()

    try:
        manager = NERCCIPNewsFeedManagerAPI(
            api_key=args.api_key,
            misp_url=args.misp_url,
            dry_run=args.dry_run
        )
        return manager.run(list_only=args.list)

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
