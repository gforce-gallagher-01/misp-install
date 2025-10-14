#!/usr/bin/env python3
"""
MISP News Auto-Population Script
Version: 1.0
Date: 2025-10-14

Purpose:
    Automatically populate MISP "Global Actions > News" section with content from
    RSS/Atom news feeds, filtered specifically for utilities/energy sector relevance.

Usage:
    python3 scripts/populate-misp-news.py
    python3 scripts/populate-misp-news.py --dry-run           # Preview without inserting
    python3 scripts/populate-misp-news.py --max-items 10     # Limit number of articles
    python3 scripts/populate-misp-news.py --days 7           # Only fetch articles from last 7 days

Features:
    - Fetches RSS/Atom feeds from MISP feeds database
    - Filters content for utilities/energy sector keywords
    - Inserts relevant articles into MISP news table
    - Prevents duplicate entries (checks title + date)
    - Associates news items with admin user
    - Supports dry-run mode for preview
    - Logs all operations to /opt/misp/logs/

Filtering Keywords (Utilities Sector):
    - Energy, utility, electric, power, grid, solar, wind, battery
    - SCADA, ICS, OT, industrial control, substation, transmission
    - NERC, BES (Bulk Electric System), CIP
    - Hydroelectric, nuclear, natural gas, renewable

IMPORTANT - NERC CIP Compliance Note:
    This script supports CIP-003-R2 (Security Awareness Training) by providing
    timely security news relevant to energy utilities. Articles are automatically
    filtered to focus on critical infrastructure security.

Requirements:
    - MISP must be running (docker containers up)
    - /opt/misp directory must exist
    - Python packages: feedparser (install with: pip3 install feedparser)
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
from datetime import datetime, timedelta
import re

# Import centralized logger
sys.path.insert(0, str(Path(__file__).parent.parent))
from misp_logger import get_logger

# Try to import feedparser
try:
    import feedparser
except ImportError:
    print("ERROR: feedparser library not found")
    print("Install with: pip3 install feedparser")
    sys.exit(1)

# Utilities sector filtering keywords
UTILITIES_KEYWORDS = [
    # Energy sector
    'energy', 'utility', 'utilities', 'electric', 'electricity', 'power',
    'grid', 'solar', 'wind', 'battery', 'hydroelectric', 'nuclear',
    'natural gas', 'renewable', 'transmission', 'distribution',

    # Industrial control systems
    'scada', 'ics', 'industrial control', 'ot', 'operational technology',
    'hmi', 'plc', 'rtu', 'dcs', 'distributed control',

    # Critical infrastructure
    'critical infrastructure', 'substation', 'transformer', 'generation',
    'load balancing', 'frequency regulation', 'voltage control',

    # NERC CIP specific
    'nerc', 'nerc cip', 'bes', 'bulk electric system', 'cip-',
    'reliability standard', 'compliance',

    # Energy companies/organizations
    'e-isac', 'department of energy', 'doe', 'ferc',
]


class MISPNewsPopulator:
    """Populate MISP news from RSS feeds"""

    def __init__(self, dry_run: bool = False, max_items: int = 20, days: int = 30):
        self.misp_dir = Path("/opt/misp")
        self.dry_run = dry_run
        self.max_items = max_items
        self.days = days
        self.logger = get_logger('populate-misp-news', 'misp:news')
        self.mysql_password = self.get_mysql_password()
        self.admin_user_id = None

    def get_mysql_password(self) -> str:
        """Get MySQL password from .env file"""
        env_file = self.misp_dir / ".env"
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        return line.split('=', 1)[1].strip()
            return 'misp'  # Default fallback
        except Exception:
            return 'misp'  # Default fallback

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

    def get_admin_user_id(self) -> int:
        """Get admin user ID for associating news items"""
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 'SELECT id FROM users WHERE role_id = 1 LIMIT 1;'],
                cwd=str(self.misp_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=True
            )

            # Parse MySQL output (tab-separated)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                user_id = int(lines[1].strip())
                return user_id

            # Fallback: return 1 (likely admin)
            return 1

        except Exception as e:
            self.logger.warning(f"Could not get admin user ID, using default: {e}",
                              event_type="news_population",
                              action="get_admin_user",
                              result="failed")
            return 1

    def get_rss_feeds(self) -> List[Dict]:
        """Get list of RSS/Atom news feeds (hardcoded NERC CIP sources)"""
        # Hardcoded RSS feed sources for utilities/energy sector
        # These are independent of MISP's threat intel feeds system
        feeds = [
            {
                'id': 'cisa-ics',
                'name': 'CISA ICS Advisories',
                'url': 'https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml'
            },
            {
                'id': 'securityweek-ics',
                'name': 'SecurityWeek - ICS/SCADA News',
                'url': 'https://www.securityweek.com/category/ics-ot-security/feed/'
            },
            {
                'id': 'bleeping-infra',
                'name': 'Bleeping Computer - Critical Infrastructure',
                'url': 'https://www.bleepingcomputer.com/feed/tag/critical-infrastructure/'
            },
            {
                'id': 'industrialcyber',
                'name': 'Industrial Cyber - News',
                'url': 'https://industrialcyber.co/feed/'
            }
        ]

        self.logger.info(f"Using {len(feeds)} hardcoded RSS feed sources",
                        event_type="news_population",
                        action="get_feeds",
                        result="success",
                        feed_count=len(feeds))

        return feeds

    def is_utilities_relevant(self, title: str, summary: str) -> bool:
        """Check if article is relevant to utilities/energy sector"""
        text = (title + " " + summary).lower()

        # Check for any utilities keywords
        for keyword in UTILITIES_KEYWORDS:
            if keyword.lower() in text:
                return True

        return False

    def is_duplicate(self, title: str, date_created: int) -> bool:
        """Check if news item already exists in database"""
        try:
            # Escape single quotes in title for SQL
            safe_title = title.replace("'", "''")

            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 f"SELECT COUNT(*) FROM news WHERE title = '{safe_title}' AND date_created = {date_created};"],
                cwd=str(self.misp_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=True
            )

            # Parse count
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                count = int(lines[1].strip())
                return count > 0

            return False

        except Exception:
            # If we can't check, assume it's new to avoid blocking
            return False

    def fetch_feed_articles(self, feed: Dict, cutoff_date: datetime) -> List[Dict]:
        """Fetch and parse RSS/Atom feed articles"""
        try:
            self.logger.info(f"Fetching feed: {feed['name']}",
                           event_type="news_population",
                           action="fetch_feed",
                           feed_name=feed['name'])

            # Parse feed
            parsed = feedparser.parse(feed['url'])

            if parsed.bozo and not parsed.entries:
                self.logger.warning(f"Feed parse error: {feed['name']}",
                                  event_type="news_population",
                                  action="parse_feed",
                                  result="failed",
                                  feed_name=feed['name'])
                return []

            articles = []
            for entry in parsed.entries:
                # Extract title and summary
                title = entry.get('title', 'No Title')
                summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')

                # Parse published date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    # Use current time if no date available
                    pub_date = datetime.now()

                # Skip if older than cutoff
                if pub_date < cutoff_date:
                    continue

                # Filter for utilities sector relevance
                if not self.is_utilities_relevant(title, summary):
                    continue

                # Convert to Unix timestamp
                date_created = int(pub_date.timestamp())

                # Check for duplicates
                if self.is_duplicate(title, date_created):
                    continue

                # Build message (summary + link)
                message = summary[:500]  # Limit summary length
                if link:
                    message += f"\n\nSource: {link}"
                message += f"\n\nFeed: {feed['name']}"

                articles.append({
                    'title': title,
                    'message': message,
                    'date_created': date_created,
                    'feed_name': feed['name']
                })

            return articles

        except Exception as e:
            self.logger.error(f"Error fetching feed {feed['name']}: {e}",
                            event_type="news_population",
                            action="fetch_feed",
                            result="failed",
                            feed_name=feed['name'])
            return []

    def insert_news_item(self, article: Dict) -> bool:
        """Insert news item into MISP database"""
        try:
            # Escape single quotes for SQL
            safe_title = article['title'].replace("'", "''")
            safe_message = article['message'].replace("'", "''")

            sql = f"""
            INSERT INTO news (
                title, message, user_id, date_created
            ) VALUES (
                '{safe_title}',
                '{safe_message}',
                {self.admin_user_id},
                {article['date_created']}
            );
            """

            if self.dry_run:
                print(f"\n[DRY RUN] Would insert:")
                print(f"  Title: {article['title'][:80]}...")
                print(f"  Date: {datetime.fromtimestamp(article['date_created']).strftime('%Y-%m-%d %H:%M')}")
                print(f"  Feed: {article['feed_name']}")
                return True

            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 sql],
                cwd=str(self.misp_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=True
            )

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to insert news item: {e.stderr}",
                            event_type="news_population",
                            action="insert_news",
                            result="failed",
                            title=article['title'][:80])
            return False
        except Exception as e:
            self.logger.error(f"Error inserting news item: {e}",
                            event_type="news_population",
                            action="insert_news",
                            result="failed",
                            title=article['title'][:80])
            return False

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")

    def run(self):
        """Main execution"""
        self.print_header("MISP News Auto-Population")

        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made\n")

        # Check if Docker is running
        print("Checking MISP status...")
        if not self.check_docker_running():
            print("❌ ERROR: MISP containers are not running")
            print("\nStart MISP with:")
            print("  cd /opt/misp && sudo docker compose up -d")
            self.logger.error("MISP containers not running",
                            event_type="news_population",
                            action="check_docker",
                            result="failed")
            return 1

        print("✓ MISP is running\n")

        # Get admin user ID
        print("Getting admin user ID...")
        self.admin_user_id = self.get_admin_user_id()
        print(f"✓ Using user ID: {self.admin_user_id}\n")

        # Get RSS feeds
        print("Fetching RSS/Atom news feeds...")
        feeds = self.get_rss_feeds()

        if not feeds:
            print("⚠️  No RSS/Atom feeds found or enabled")
            print("\nRun this script first:")
            print("  python3 scripts/add-nerc-cip-news-feeds.py")
            return 1

        print(f"✓ Found {len(feeds)} active news feeds\n")

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=self.days)
        print(f"Fetching articles from last {self.days} days (since {cutoff_date.strftime('%Y-%m-%d')})")
        print(f"Filtering for utilities/energy sector keywords\n")

        # Fetch and process articles from all feeds
        all_articles = []
        for feed in feeds:
            articles = self.fetch_feed_articles(feed, cutoff_date)
            all_articles.extend(articles)
            print(f"  • {feed['name']}: {len(articles)} relevant articles")

        print(f"\n✓ Found {len(all_articles)} total utilities-relevant articles\n")

        if not all_articles:
            print("⚠️  No new utilities-relevant articles found")
            print("\nThis could mean:")
            print("  1. No recent news matching utilities/energy keywords")
            print("  2. All recent articles already added to MISP")
            print("  3. Feeds are not updating")
            return 0

        # Limit number of items
        if len(all_articles) > self.max_items:
            print(f"Limiting to {self.max_items} most recent articles\n")
            # Sort by date (most recent first)
            all_articles.sort(key=lambda x: x['date_created'], reverse=True)
            all_articles = all_articles[:self.max_items]

        # Insert articles
        self.print_header(f"{'Previewing' if self.dry_run else 'Inserting'} Articles")

        success_count = 0
        failed_count = 0

        for article in all_articles:
            if self.insert_news_item(article):
                success_count += 1
            else:
                failed_count += 1

        # Summary
        self.print_header("Summary")
        print(f"Total articles processed:  {len(all_articles)}")
        if self.dry_run:
            print(f"Would insert:              {success_count}")
        else:
            print(f"Successfully inserted:     {success_count}")
            print(f"Failed:                    {failed_count}")
        print()

        if not self.dry_run and success_count > 0:
            print("✓ News items added to MISP")
            print("\nView in MISP:")
            print("  1. Login to MISP web interface")
            print("  2. Navigate to: Global Actions > News")
            print("  3. See the latest utilities/energy sector security news")
            print()
            print("Automation:")
            print("  Add to crontab for daily updates:")
            print("  0 8 * * * cd /home/gallagher/misp-install/misp-install && python3 scripts/populate-misp-news.py")

        # Log summary
        self.logger.info(f"News population complete: {success_count}/{len(all_articles)} inserted",
                        event_type="news_population",
                        action="complete",
                        result="success",
                        total_articles=len(all_articles),
                        inserted=success_count,
                        failed=failed_count,
                        dry_run=self.dry_run)

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Populate MISP news from RSS feeds (utilities sector only)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal run - add new articles
  python3 scripts/populate-misp-news.py

  # Preview without inserting (dry run)
  python3 scripts/populate-misp-news.py --dry-run

  # Limit to 10 most recent articles
  python3 scripts/populate-misp-news.py --max-items 10

  # Only fetch articles from last 7 days
  python3 scripts/populate-misp-news.py --days 7

  # Combine options
  python3 scripts/populate-misp-news.py --dry-run --days 14 --max-items 5

Automation (crontab):
  # Daily at 8 AM
  0 8 * * * cd /home/gallagher/misp-install/misp-install && python3 scripts/populate-misp-news.py

  # Twice daily (8 AM and 6 PM)
  0 8,18 * * * cd /home/gallagher/misp-install/misp-install && python3 scripts/populate-misp-news.py
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                       help='Preview articles without inserting into database')
    parser.add_argument('--max-items', type=int, default=20,
                       help='Maximum number of articles to insert (default: 20)')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days to look back for articles (default: 30)')

    args = parser.parse_args()

    populator = MISPNewsPopulator(
        dry_run=args.dry_run,
        max_items=args.max_items,
        days=args.days
    )

    return populator.run()


if __name__ == '__main__':
    sys.exit(main())
