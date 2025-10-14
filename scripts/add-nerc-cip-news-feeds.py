#!/usr/bin/env python3
"""
Add NERC CIP News Feeds to MISP
Version: 1.0
Date: 2025-10-14

Purpose:
    Add NERC CIP-related news feeds (RSS/Atom) to MISP for security awareness
    and threat intelligence updates. Focuses on ICS/SCADA, energy sector, and
    NERC CIP compliance news.

Usage:
    python3 scripts/add-nerc-cip-news-feeds.py
    python3 scripts/add-nerc-cip-news-feeds.py --dry-run    # Preview only
    python3 scripts/add-nerc-cip-news-feeds.py --list       # List feeds

Features:
    - Adds 6+ NERC CIP-related news feeds to MISP
    - CISA ICS-CERT advisories (official US government)
    - Industrial Cyber news (ICS/SCADA focus)
    - SecurityWeek ICS section
    - Bleeping Computer critical infrastructure
    - NERC official news/alerts
    - Dry-run mode for testing

IMPORTANT - NERC CIP Compliance Note:
    News feeds provide security awareness content for CIP-003-R2 training.
    These are informational RSS feeds, not threat intelligence IOCs.
    Use for security awareness, incident response context, and training.

Requirements:
    - MISP must be running (docker containers up)
    - /opt/misp directory must exist
    - MySQL password in /opt/misp/.env
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict
import argparse

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


class NERCCIPNewsFeedManager:
    """Manage NERC CIP-related news feeds in MISP"""

    def __init__(self, dry_run: bool = False):
        self.misp_dir = Path("/opt/misp")
        self.dry_run = dry_run
        self.logger = get_logger('add-nerc-cip-news-feeds', 'misp:feeds')
        self.mysql_password = self.get_mysql_password()

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

            # Parse JSON output
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    containers.append(json.loads(line))

            # Check if misp-core is running
            for container in containers:
                if 'misp-core' in container.get('Name', '') and container.get('State') == 'running':
                    return True

            return False

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return False

    def feed_exists(self, feed_url: str) -> bool:
        """Check if feed already exists in MISP"""
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 f"SELECT COUNT(*) FROM feeds WHERE url = '{feed_url}';"],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                check=True
            )

            # Parse output (skip header line)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                count = int(lines[1].strip())
                return count > 0

            return False

        except (subprocess.CalledProcessError, ValueError):
            return False

    def add_feed(self, feed: Dict) -> bool:
        """Add a news feed to MISP"""

        if self.dry_run:
            print(f"[DRY-RUN] Would add feed: {feed['name']}")
            print(f"  URL: {feed['url']}")
            print(f"  Enabled: {feed['enabled']}")
            print(f"  NERC CIP Relevant: {feed.get('nerc_cip_relevant', False)}")
            return True

        # Check if feed already exists
        if self.feed_exists(feed['url']):
            print(f"⚠️  Feed already exists: {feed['name']}")
            self.logger.info(f"Feed already exists: {feed['name']}",
                           event_type="feed_add",
                           action="skip",
                           result="already_exists",
                           feed_name=feed['name'])
            return False

        try:
            # Prepare SQL INSERT
            # Escape single quotes in strings
            name = feed['name'].replace("'", "''")
            provider = feed['provider'].replace("'", "''")
            url = feed['url'].replace("'", "''")
            description = feed.get('description', '').replace("'", "''")

            enabled = 1 if feed['enabled'] else 0
            caching_enabled = 1 if feed['caching_enabled'] else 0
            default = 1 if feed['default'] else 0

            sql = f"""
            INSERT INTO feeds (
                name, provider, url, rules, enabled, distribution,
                sharing_group_id, tag_id, `default`, source_format,
                fixed_event, delta_merge, event_id, publish, override_ids,
                settings, input_source, delete_local_file, lookup_visible,
                headers, caching_enabled, force_to_ids, orgc_id, tag_collection_id
            ) VALUES (
                '{name}',
                '{provider}',
                '{url}',
                '',
                {enabled},
                {feed['distribution']},
                {feed['sharing_group_id']},
                {feed['tag_id']},
                {default},
                '{feed['source_format']}',
                0,
                0,
                0,
                0,
                0,
                '',
                '{feed['input_source']}',
                0,
                1,
                '',
                {caching_enabled},
                0,
                0,
                0
            );
            """

            # Execute SQL
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{self.mysql_password}', 'misp', '-e',
                 sql],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                check=True
            )

            print(f"✅ Added feed: {feed['name']}")
            self.logger.info(f"Added feed: {feed['name']}",
                           event_type="feed_add",
                           action="add",
                           result="success",
                           feed_name=feed['name'],
                           feed_url=feed['url'])
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to add feed: {feed['name']}")
            print(f"   Error: {e.stderr}")
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
        self.print_header("Add NERC CIP News Feeds to MISP")

        # List feeds if requested
        if list_only:
            self.list_feeds()
            return 0

        # Check if Docker is running
        print("Checking MISP status...")
        if not self.check_docker_running():
            print("❌ ERROR: MISP containers are not running")
            print("\nStart MISP with:")
            print("  cd /opt/misp && sudo docker compose up -d")
            self.logger.error("MISP containers not running",
                            event_type="feed_add",
                            action="check_docker",
                            result="failed")
            return 1

        print("✓ MISP is running\n")

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
            result = self.add_feed(feed)
            if result:
                added_count += 1
            elif self.feed_exists(feed['url']):
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
        description='Add NERC CIP news feeds to MISP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add NERC CIP news feeds to MISP
  python3 scripts/add-nerc-cip-news-feeds.py

  # Preview feeds without adding
  python3 scripts/add-nerc-cip-news-feeds.py --dry-run

  # List available feeds
  python3 scripts/add-nerc-cip-news-feeds.py --list

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

    parser.add_argument('--dry-run', action='store_true',
                       help='Preview feeds without adding them')
    parser.add_argument('--list', action='store_true',
                       help='List available feeds')

    args = parser.parse_args()

    manager = NERCCIPNewsFeedManager(dry_run=args.dry_run)
    return manager.run(list_only=args.list)


if __name__ == '__main__':
    sys.exit(main())
