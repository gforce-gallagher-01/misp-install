#!/usr/bin/env python3
"""
MISP Feed Fetcher - Automated Feed Data Collection
Version: 1.0
Date: 2025-10-14

Purpose:
    Automatically fetch (download) data from all enabled MISP threat intelligence feeds.
    This script is designed to run via cron for daily/hourly feed updates.

Usage:
    # Fetch all enabled feeds
    python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY

    # Fetch specific feeds by ID
    python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY --feed-ids 1,2,3

    # Dry-run mode (show what would be fetched)
    python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY --dry-run

    # Quiet mode (minimal output, suitable for cron)
    python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY --quiet

Cron Examples:
    # Fetch all feeds daily at 2 AM
    0 2 * * * /usr/bin/python3 /path/to/fetch-all-feeds.py --api-key YOUR_KEY --quiet

    # Fetch all feeds every 6 hours
    0 */6 * * * /usr/bin/python3 /path/to/fetch-all-feeds.py --api-key YOUR_KEY --quiet

Features:
    - Fetches all enabled feeds
    - Logs all operations with structured JSON
    - Suitable for cron automation
    - Tracks success/failure rates
    - Handles timeouts gracefully

Requirements:
    - MISP running (Docker containers)
    - Valid MISP API key
    - Sufficient disk space for feed data
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_api import get_api_key, get_misp_client, test_connection
from misp_logger import get_logger


class MISPFeedFetcher:
    """Automated feed data fetching for MISP"""

    def __init__(self, api_key: str, misp_url: str = "https://misp-test.lan",
                 dry_run: bool = False, quiet: bool = False):
        """Initialize feed fetcher

        Args:
            api_key: MISP API key
            misp_url: MISP base URL
            dry_run: Preview mode without fetching
            quiet: Minimal output mode for cron
        """
        self.api_key = api_key
        self.misp_url = misp_url.rstrip('/')
        self.dry_run = dry_run
        self.quiet = quiet

        # Initialize logger
        self.logger = get_logger('fetch-all-feeds', 'misp:feed:fetch')

        # Get API client
        self.session = get_misp_client(api_key=api_key, misp_url=misp_url)

        # Statistics
        self.stats = {
            'total_feeds': 0,
            'enabled_feeds': 0,
            'fetched': 0,
            'failed': 0,
            'skipped': 0
        }

    def log(self, message: str, _level: str = "info"):
        """Log message (respects quiet mode)"""
        if not self.quiet:
            print(message)

    def get_enabled_feeds(self) -> List[Dict]:
        """Get list of all enabled feeds"""
        try:
            response = self.session.get(f"{self.misp_url}/feeds/index")

            if response.status_code == 200:
                feeds = response.json()

                # Filter for enabled feeds only
                enabled_feeds = []
                for feed in feeds:
                    if 'Feed' in feed:
                        f = feed['Feed']
                        if f.get('enabled') in ['1', 1, True]:
                            enabled_feeds.append({
                                'id': f.get('id'),
                                'name': f.get('name', 'Unknown'),
                                'url': f.get('url', ''),
                                'source_format': f.get('source_format', 'csv'),
                                'provider': f.get('provider', ''),
                            })

                self.stats['total_feeds'] = len(feeds)
                self.stats['enabled_feeds'] = len(enabled_feeds)

                return enabled_feeds

            else:
                self.logger.error(f"Failed to get feeds: HTTP {response.status_code}",
                                event_type="feed_fetch",
                                action="get_feeds",
                                result="failed",
                                status_code=response.status_code)
                return []

        except Exception as e:
            self.logger.error(f"Error getting feeds: {e}",
                            event_type="feed_fetch",
                            action="get_feeds",
                            result="error",
                            error=str(e))
            return []

    def fetch_feed(self, feed_id: str, feed_name: str) -> Tuple[bool, str]:
        """Fetch (download) data from a specific feed

        Args:
            feed_id: Feed ID
            feed_name: Feed name (for logging)

        Returns:
            (success: bool, message: str)
        """
        try:
            self.log(f"  Fetching: {feed_name} (ID: {feed_id})...")

            if self.dry_run:
                return True, "Dry-run mode - skipped"

            # Trigger feed fetch via API
            response = self.session.post(f"{self.misp_url}/feeds/fetchFromFeed/{feed_id}")

            if response.status_code == 200:
                result = response.json()

                # Check for errors in response
                if 'errors' in result:
                    error_msg = str(result['errors'])
                    self.logger.warning(f"Feed fetch had errors: {feed_name}",
                                      event_type="feed_fetch",
                                      action="fetch",
                                      result="warning",
                                      feed_id=feed_id,
                                      feed_name=feed_name,
                                      error=error_msg[:200])
                    return False, f"Errors: {error_msg[:100]}"

                # Success
                self.logger.info(f"Feed fetched successfully: {feed_name}",
                               event_type="feed_fetch",
                               action="fetch",
                               result="success",
                               feed_id=feed_id,
                               feed_name=feed_name)
                return True, "Success"

            else:
                error_msg = f"HTTP {response.status_code}"
                self.logger.error(f"Feed fetch failed: {feed_name}",
                                event_type="feed_fetch",
                                action="fetch",
                                result="failed",
                                feed_id=feed_id,
                                feed_name=feed_name,
                                status_code=response.status_code)
                return False, error_msg

        except Exception as e:
            self.logger.error(f"Feed fetch error: {feed_name}",
                            event_type="feed_fetch",
                            action="fetch",
                            result="error",
                            feed_id=feed_id,
                            feed_name=feed_name,
                            error=str(e))
            return False, str(e)

    def fetch_all_feeds(self, feed_ids: List[str] = None):
        """Fetch data from all enabled feeds (or specific feed IDs)

        Args:
            feed_ids: Optional list of specific feed IDs to fetch
        """
        self.log("="*80)
        self.log("  MISP Feed Fetcher - Automated Feed Data Collection")
        self.log("="*80)

        if self.dry_run:
            self.log("\n[DRY-RUN MODE - No feeds will be fetched]\n")

        # Test connection
        self.log("\nTesting MISP connection...")
        success, message = test_connection(self.session)
        if not success:
            self.log(f"ERROR: {message}")
            self.logger.error(f"Connection test failed: {message}",
                            event_type="feed_fetch",
                            action="connect",
                            result="failed")
            return 1

        self.log(f"✓ {message}")

        # Get enabled feeds
        self.log("\nRetrieving enabled feeds...")
        feeds = self.get_enabled_feeds()

        if not feeds:
            self.log("WARNING: No enabled feeds found")
            self.logger.warning("No enabled feeds found",
                              event_type="feed_fetch",
                              action="get_feeds",
                              result="warning")
            return 0

        # Filter by specific feed IDs if provided
        if feed_ids:
            feeds = [f for f in feeds if str(f['id']) in feed_ids]
            self.log(f"✓ Found {len(feeds)} feeds matching IDs: {', '.join(feed_ids)}")
        else:
            self.log(f"✓ Found {len(feeds)} enabled feeds")

        # Fetch all feeds
        self.log(f"\n{'-'*80}")
        self.log("  Fetching Feed Data")
        self.log(f"{'-'*80}\n")

        for i, feed in enumerate(feeds, 1):
            feed_id = feed['id']
            feed_name = feed['name']

            self.log(f"[{i}/{len(feeds)}] {feed_name}")

            success, message = self.fetch_feed(feed_id, feed_name)

            if success:
                self.log(f"    ✓ {message}")
                self.stats['fetched'] += 1
            else:
                self.log(f"    ✗ {message}")
                self.stats['failed'] += 1

            # Small delay between fetches to avoid overwhelming MISP
            if not self.dry_run and i < len(feeds):
                time.sleep(2)

        # Print summary
        self.log(f"\n{'='*80}")
        self.log("  Summary")
        self.log(f"{'='*80}")
        self.log(f"Total feeds in MISP:  {self.stats['total_feeds']}")
        self.log(f"Enabled feeds:        {self.stats['enabled_feeds']}")
        self.log(f"Successfully fetched: {self.stats['fetched']}")
        self.log(f"Failed:               {self.stats['failed']}")

        success_rate = (self.stats['fetched'] / len(feeds) * 100) if feeds else 0
        self.log(f"Success rate:         {success_rate:.1f}%")

        # Log completion
        self.logger.info(f"Feed fetch complete: {self.stats['fetched']}/{len(feeds)} successful",
                        event_type="feed_fetch",
                        action="complete",
                        result="success" if self.stats['failed'] == 0 else "partial",
                        total_feeds=self.stats['total_feeds'],
                        enabled_feeds=self.stats['enabled_feeds'],
                        fetched=self.stats['fetched'],
                        failed=self.stats['failed'],
                        success_rate=success_rate)

        return 0 if self.stats['failed'] == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Fetch data from MISP threat intelligence feeds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all enabled feeds
  python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY

  # Fetch specific feeds by ID
  python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY --feed-ids 1,7,8,9

  # Dry-run mode (preview)
  python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY --dry-run

  # Quiet mode (for cron)
  python3 scripts/fetch-all-feeds.py --api-key YOUR_KEY --quiet

Cron Setup:
  # Daily at 2 AM
  0 2 * * * /usr/bin/python3 /home/user/misp-install/scripts/fetch-all-feeds.py --api-key YOUR_KEY --quiet >> /opt/misp/logs/feed-fetch-cron.log 2>&1

API Key:
  Auto-detected from:
  1. --api-key argument
  2. MISP_API_KEY environment variable
  3. /opt/misp/.env file
        """
    )

    parser.add_argument('--api-key', type=str,
                       help='MISP API key (auto-detected if not provided)')
    parser.add_argument('--misp-url', type=str, default='https://misp-test.lan',
                       help='MISP base URL (default: https://misp-test.lan)')
    parser.add_argument('--feed-ids', type=str,
                       help='Comma-separated feed IDs to fetch (default: all enabled)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview mode without fetching')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output (suitable for cron)')

    args = parser.parse_args()

    # Get API key (auto-detect if not provided)
    api_key = args.api_key
    if not api_key:
        api_key = get_api_key()
        if not api_key:
            print("ERROR: No API key found")
            print("\nProvide API key via:")
            print("  1. --api-key argument")
            print("  2. MISP_API_KEY environment variable")
            print("  3. /opt/misp/.env file")
            return 1

    # Parse feed IDs if provided
    feed_ids = None
    if args.feed_ids:
        feed_ids = [fid.strip() for fid in args.feed_ids.split(',')]

    try:
        # Create fetcher
        fetcher = MISPFeedFetcher(
            api_key=api_key,
            misp_url=args.misp_url,
            dry_run=args.dry_run,
            quiet=args.quiet
        )

        # Fetch feeds
        return fetcher.fetch_all_feeds(feed_ids=feed_ids)

    except KeyboardInterrupt:
        print("\n\nFeed fetch interrupted by user")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
