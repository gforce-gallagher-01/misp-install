#!/usr/bin/env python3
"""
MISP Feed Enablement Script
Version: 1.0
Date: 2025-10-14

Purpose:
    Enable MISP threat intelligence feeds by ID or name.
    Supports enabling individual feeds or all NERC CIP recommended feeds.

Usage:
    python3 scripts/enable-misp-feeds.py --id 60                    # Enable by ID
    python3 scripts/enable-misp-feeds.py --name "URLhaus"          # Enable by name
    python3 scripts/enable-misp-feeds.py --nerc-cip                # Enable all NERC CIP feeds
    python3 scripts/enable-misp-feeds.py --all                     # Enable all feeds
    python3 scripts/enable-misp-feeds.py --list                    # List available feeds
    python3 scripts/enable-misp-feeds.py --dry-run --nerc-cip      # Preview changes

Features:
    - Enable feeds by ID or name
    - Bulk enable NERC CIP recommended feeds
    - Automatic feed fetching after enablement
    - Dry-run mode to preview changes
    - Centralized logging with audit trail

Requirements:
    - MISP must be running (docker containers up)
    - /opt/misp directory must exist
    - Database credentials from .env file
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Import centralized logger and modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.database_manager import DatabaseManager
from lib.feed_constants import FEED_NAME_MAPPINGS, NERC_CIP_FEEDS
from lib.misp_config import MISPConfig
from misp_logger import get_logger


class MISPFeedEnabler:
    """Enable MISP feeds"""

    def __init__(self, dry_run: bool = False):
        self.config = MISPConfig()
        self.misp_dir = self.config.MISP_DIR
        self.dry_run = dry_run
        self.logger = get_logger('enable-misp-feeds', 'misp:feeds')

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
            import json
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    containers.append(json.loads(line))

            # Check if misp-core is running
            for container in containers:
                if 'misp-core' in container.get('Name', '') and container.get('State') == 'running':
                    return True

            return False

        except Exception:
            return False

    def get_all_feeds(self) -> List[Dict]:
        """Get list of all feeds from MISP"""
        try:
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
                return []

            # Skip header line
            for line in lines[1:]:
                if line.strip():
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
                            event_type="feed_enable",
                            action="get_feeds",
                            result="failed")
            return []
        except Exception as e:
            self.logger.error(f"Error getting feeds: {e}",
                            event_type="feed_enable",
                            action="get_feeds",
                            result="failed")
            return []

    def find_feed_by_id(self, feed_id: int) -> Optional[Dict]:
        """Find feed by ID"""
        feeds = self.get_all_feeds()
        for feed in feeds:
            if feed['id'] == str(feed_id):
                return feed
        return None

    def find_feeds_by_name(self, name: str) -> List[Dict]:
        """Find feeds by name (partial match, case-insensitive)"""
        feeds = self.get_all_feeds()
        matches = []
        name_lower = name.lower()

        for feed in feeds:
            if name_lower in feed['name'].lower():
                matches.append(feed)

        return matches

    def enable_feed(self, feed_id: int) -> bool:
        """Enable a feed by ID"""
        if self.dry_run:
            print(f"[DRY RUN] Would enable feed ID {feed_id}")
            return True

        try:
            subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 f'UPDATE feeds SET enabled = 1 WHERE id = {feed_id};'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info(f"Enabled feed ID {feed_id}",
                           event_type="feed_enable",
                           action="enable",
                           feed_id=feed_id,
                           result="success")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to enable feed {feed_id}: {e.stderr}",
                            event_type="feed_enable",
                            action="enable",
                            feed_id=feed_id,
                            result="failed")
            return False

    def fetch_feed(self, feed_id: int) -> bool:
        """Fetch feed data (download IOCs)"""
        if self.dry_run:
            print(f"[DRY RUN] Would fetch feed ID {feed_id}")
            return True

        try:
            # Use MISP CLI to fetch feed
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
                 '/var/www/MISP/app/Console/cake', 'Server', 'fetchFeed', str(feed_id)],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.logger.info(f"Fetched feed ID {feed_id}",
                               event_type="feed_enable",
                               action="fetch",
                               feed_id=feed_id,
                               result="success")
                return True
            else:
                self.logger.warning(f"Feed fetch may have failed for ID {feed_id}: {result.stderr}",
                                  event_type="feed_enable",
                                  action="fetch",
                                  feed_id=feed_id,
                                  result="warning")
                return False

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Feed fetch timeout for ID {feed_id} (still running in background)",
                              event_type="feed_enable",
                              action="fetch",
                              feed_id=feed_id,
                              result="timeout")
            return False
        except Exception as e:
            self.logger.error(f"Error fetching feed {feed_id}: {e}",
                            event_type="feed_enable",
                            action="fetch",
                            feed_id=feed_id,
                            result="failed")
            return False

    def find_nerc_cip_feeds(self) -> List[Dict]:
        """Find all available NERC CIP recommended feeds"""
        all_feeds = self.get_all_feeds()
        nerc_matches = []

        for feed in all_feeds:
            feed_name_lower = feed['name'].lower()

            # Check if feed matches any NERC CIP recommendation
            for nerc_feed in NERC_CIP_FEEDS:
                nerc_lower = nerc_feed.lower()

                # Direct match
                if nerc_lower in feed_name_lower:
                    nerc_matches.append(feed)
                    break

                # Check mappings
                for keyword, mapped_names in FEED_NAME_MAPPINGS.items():
                    if keyword in nerc_lower:
                        for mapped_name in mapped_names:
                            if mapped_name.lower() in feed_name_lower:
                                nerc_matches.append(feed)
                                break

        return nerc_matches

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")

    def print_feed(self, feed: Dict):
        """Print feed details"""
        status = "✓ ENABLED " if feed['enabled'] else "✗ DISABLED"
        print(f"{status}")
        print(f"  ID:     {feed['id']}")
        print(f"  Name:   {feed['name']}")
        print(f"  Format: {feed['source_format']}")
        print(f"  URL:    {feed['url'][:60]}...")
        print()

    def run_enable_by_id(self, feed_id: int) -> int:
        """Enable a specific feed by ID"""
        self.print_header(f"Enable Feed by ID: {feed_id}")

        # Check if Docker is running
        if not self.check_docker_running():
            print("❌ ERROR: MISP containers are not running")
            return 1

        # Find feed
        feed = self.find_feed_by_id(feed_id)
        if not feed:
            print(f"❌ ERROR: Feed ID {feed_id} not found")
            return 1

        # Display feed info
        print("Found feed:")
        self.print_feed(feed)

        # Check if already enabled
        if feed['enabled']:
            print("⚠️  Feed is already enabled")
            return 0

        # Enable feed
        print("Enabling feed...")
        if self.enable_feed(feed_id):
            print("✓ Feed enabled successfully")

            # Fetch feed data
            if not self.dry_run:
                print("\nFetching feed data (this may take a few minutes)...")
                if self.fetch_feed(feed_id):
                    print("✓ Feed data fetched successfully")
                else:
                    print("⚠️  Feed fetch may have failed (check logs)")

            return 0
        else:
            print("❌ Failed to enable feed")
            return 1

    def run_enable_by_name(self, name: str) -> int:
        """Enable feeds by name"""
        self.print_header(f"Enable Feeds by Name: {name}")

        # Check if Docker is running
        if not self.check_docker_running():
            print("❌ ERROR: MISP containers are not running")
            return 1

        # Find feeds
        feeds = self.find_feeds_by_name(name)
        if not feeds:
            print(f"❌ ERROR: No feeds found matching '{name}'")
            return 1

        print(f"Found {len(feeds)} feed(s):\n")
        for feed in feeds:
            self.print_feed(feed)

        # Enable each feed
        enabled_count = 0
        for feed in feeds:
            if feed['enabled']:
                print(f"⚠️  Feed '{feed['name']}' (ID {feed['id']}) is already enabled")
                continue

            print(f"Enabling feed '{feed['name']}' (ID {feed['id']})...")
            if self.enable_feed(int(feed['id'])):
                print("✓ Enabled successfully")
                enabled_count += 1

                # Fetch feed data
                if not self.dry_run:
                    print("  Fetching feed data...")
                    if self.fetch_feed(int(feed['id'])):
                        print("  ✓ Fetched successfully")
                    else:
                        print("  ⚠️  Fetch may have failed")
            else:
                print("❌ Failed to enable")

        print(f"\n{'='*80}")
        print(f"Summary: Enabled {enabled_count}/{len(feeds)} feeds")
        print(f"{'='*80}")

        return 0

    def run_enable_nerc_cip(self) -> int:
        """Enable all NERC CIP recommended feeds"""
        self.print_header("Enable NERC CIP Recommended Feeds")

        # Check if Docker is running
        if not self.check_docker_running():
            print("❌ ERROR: MISP containers are not running")
            return 1

        # Find NERC CIP feeds
        nerc_feeds = self.find_nerc_cip_feeds()

        if not nerc_feeds:
            print("⚠️  No NERC CIP recommended feeds found in MISP")
            return 1

        # Separate enabled and disabled
        enabled_feeds = [f for f in nerc_feeds if f['enabled']]
        disabled_feeds = [f for f in nerc_feeds if not f['enabled']]

        print(f"Found {len(nerc_feeds)} NERC CIP feeds:")
        print(f"  Already enabled: {len(enabled_feeds)}")
        print(f"  To enable: {len(disabled_feeds)}")
        print()

        if enabled_feeds:
            print("Already enabled:")
            for feed in enabled_feeds:
                print(f"  ✓ {feed['name']} (ID {feed['id']})")
            print()

        if not disabled_feeds:
            print("✓ All NERC CIP feeds are already enabled!")
            return 0

        print(f"Will enable {len(disabled_feeds)} feeds:\n")
        for feed in disabled_feeds:
            self.print_feed(feed)

        # Enable each feed
        enabled_count = 0
        for feed in disabled_feeds:
            print(f"Enabling: {feed['name']} (ID {feed['id']})...")
            if self.enable_feed(int(feed['id'])):
                print("✓ Enabled successfully")
                enabled_count += 1

                # Fetch feed data
                if not self.dry_run:
                    print("  Fetching feed data...")
                    if self.fetch_feed(int(feed['id'])):
                        print("  ✓ Fetched successfully")
                    else:
                        print("  ⚠️  Fetch may have failed (check logs)")
                    time.sleep(2)  # Brief pause between fetches
            else:
                print("❌ Failed to enable")

        print(f"\n{'='*80}")
        print(f"Summary: Enabled {enabled_count}/{len(disabled_feeds)} NERC CIP feeds")
        print(f"{'='*80}")

        return 0

    def run_list_feeds(self) -> int:
        """List all available feeds"""
        self.print_header("Available MISP Feeds")

        feeds = self.get_all_feeds()
        if not feeds:
            print("⚠️  No feeds found")
            return 1

        enabled_feeds = [f for f in feeds if f['enabled']]
        disabled_feeds = [f for f in feeds if not f['enabled']]

        print(f"Total: {len(feeds)} feeds")
        print(f"Enabled: {len(enabled_feeds)}")
        print(f"Disabled: {len(disabled_feeds)}")

        self.print_header("Enabled Feeds")
        for feed in enabled_feeds:
            self.print_feed(feed)

        self.print_header("Disabled Feeds")
        for feed in disabled_feeds:
            self.print_feed(feed)

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Enable MISP threat intelligence feeds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enable specific feed by ID
  python3 scripts/enable-misp-feeds.py --id 60

  # Enable feeds by name (partial match)
  python3 scripts/enable-misp-feeds.py --name "URLhaus"

  # Enable all NERC CIP recommended feeds
  python3 scripts/enable-misp-feeds.py --nerc-cip

  # List all available feeds
  python3 scripts/enable-misp-feeds.py --list

  # Preview changes without making them
  python3 scripts/enable-misp-feeds.py --nerc-cip --dry-run
        """
    )

    parser.add_argument('--id', type=int, help='Enable feed by ID')
    parser.add_argument('--name', type=str, help='Enable feeds by name (partial match)')
    parser.add_argument('--nerc-cip', action='store_true', help='Enable all NERC CIP recommended feeds')
    parser.add_argument('--all', action='store_true', help='Enable all feeds')
    parser.add_argument('--list', action='store_true', help='List all available feeds')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without making them')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.id, args.name, args.nerc_cip, args.all, args.list]):
        parser.print_help()
        return 1

    enabler = MISPFeedEnabler(dry_run=args.dry_run)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")

    # Execute requested action
    if args.list:
        return enabler.run_list_feeds()
    elif args.id:
        return enabler.run_enable_by_id(args.id)
    elif args.name:
        return enabler.run_enable_by_name(args.name)
    elif args.nerc_cip:
        return enabler.run_enable_nerc_cip()
    elif args.all:
        print("⚠️  --all flag not yet implemented (enable all 88 feeds)")
        print("Use --nerc-cip for NERC CIP recommended feeds")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
