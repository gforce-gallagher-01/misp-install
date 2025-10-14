#!/usr/bin/env python3
"""
Add Threat Intelligence Feeds to MISP
Version: 2.0
Date: 2025-10-14

Purpose:
    Add comprehensive threat intelligence feeds to MISP, including:
    - ICS/OT/NERC CIP specific feeds (utilities sector)
    - General threat intelligence feeds (malware, phishing, botnets)

    These feeds provide IOCs (indicators of compromise) for threat detection.

Usage:
    python3 scripts/add-threat-feeds.py --api-key YOUR_KEY
    python3 scripts/add-threat-feeds.py  # Auto-detect API key
    python3 scripts/add-threat-feeds.py --profile ics-ot  # Only ICS/OT feeds
    python3 scripts/add-threat-feeds.py --profile general  # Only general feeds
    python3 scripts/add-threat-feeds.py --profile all  # All feeds (default)

Feed Categories:
    ICS/OT Feeds (4):
        - abuse.ch URLhaus: Malware distribution URLs
        - abuse.ch Feodo Tracker: Botnet C2 servers
        - Blocklist.de All: Attack sources
        - OpenPhish URL Feed: Phishing URLs

    General Threat Intel Feeds (5):
        - abuse.ch ThreatFox: Recent malware IOCs
        - abuse.ch SSL Blacklist: Malicious SSL certificates
        - abuse.ch MalwareBazaar: Recent malware samples
        - PhishTank: Community-verified phishing URLs
        - abuse.ch Feodo Tracker (Full): Complete botnet tracker
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_api import get_api_key, get_misp_client, test_connection
from misp_logger import get_logger

# ICS/OT threat intelligence feeds (utilities/energy sector)
ICS_OT_FEEDS = [
    {
        'name': 'abuse.ch URLhaus',
        'provider': 'abuse.ch',
        'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'URLhaus malicious URLs for malware distribution',
        'category': 'ics-ot'
    },
    {
        'name': 'abuse.ch Feodo Tracker',
        'provider': 'abuse.ch',
        'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Feodo/Emotet/Dridex botnet C2 servers',
        'category': 'ics-ot'
    },
    {
        'name': 'Blocklist.de All',
        'provider': 'Blocklist.de',
        'url': 'https://lists.blocklist.de/lists/all.txt',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Attack sources (SSH, Mail, Apache, etc.)',
        'category': 'ics-ot'
    },
    {
        'name': 'OpenPhish URL Feed',
        'provider': 'OpenPhish',
        'url': 'https://openphish.com/feed.txt',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Phishing URLs',
        'category': 'ics-ot'
    }
]

# General threat intelligence feeds (malware, phishing, botnets)
GENERAL_FEEDS = [
    {
        'name': 'abuse.ch ThreatFox',
        'provider': 'abuse.ch',
        'url': 'https://threatfox.abuse.ch/export/json/recent/',
        'source_format': 'misp',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Recent IOCs from various malware families',
        'category': 'general'
    },
    {
        'name': 'abuse.ch SSL Blacklist',
        'provider': 'abuse.ch',
        'url': 'https://sslbl.abuse.ch/blacklist/sslblacklist.csv',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Malicious SSL certificates',
        'category': 'general'
    },
    {
        'name': 'abuse.ch MalwareBazaar Recent',
        'provider': 'abuse.ch',
        'url': 'https://mb-api.abuse.ch/downloads/sha256_recent/',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Recent malware samples (SHA256 hashes)',
        'category': 'general'
    },
    {
        'name': 'PhishTank',
        'provider': 'PhishTank',
        'url': 'http://data.phishtank.com/data/online-valid.csv',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Community-verified phishing URLs',
        'category': 'general'
    },
    {
        'name': 'abuse.ch Feodo Tracker (Full)',
        'provider': 'abuse.ch',
        'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist.csv',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Complete botnet C2 IP blocklist',
        'category': 'general'
    }
]


def get_feeds_by_profile(profile: str) -> List[Dict]:
    """Get feeds based on profile selection"""
    if profile == 'ics-ot':
        return ICS_OT_FEEDS
    elif profile == 'general':
        return GENERAL_FEEDS
    elif profile == 'all':
        return ICS_OT_FEEDS + GENERAL_FEEDS
    else:
        raise ValueError(f"Unknown profile: {profile}. Use: ics-ot, general, or all")


def main():
    parser = argparse.ArgumentParser(
        description='Add threat intelligence feeds to MISP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add all feeds (ICS/OT + General)
  python3 scripts/add-threat-feeds.py --profile all

  # Add only ICS/OT feeds (utilities sector)
  python3 scripts/add-threat-feeds.py --profile ics-ot

  # Add only general threat intel feeds
  python3 scripts/add-threat-feeds.py --profile general

  # Preview without making changes
  python3 scripts/add-threat-feeds.py --profile all --dry-run
        """
    )
    parser.add_argument('--api-key', type=str, help='MISP API key')
    parser.add_argument('--profile', type=str, default='all',
                       choices=['ics-ot', 'general', 'all'],
                       help='Feed profile to install (default: all)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview without adding feeds')
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: No API key found")
        print("  - Set MISP_API_KEY environment variable, or")
        print("  - Use --api-key parameter")
        return 1

    # Get logger
    logger = get_logger('add-threat-feeds', 'misp:feed')

    # Test connection
    session = get_misp_client(api_key=api_key)
    success, message = test_connection(session)
    if not success:
        print(f"ERROR: {message}")
        return 1

    print(f"✓ {message}\n")
    print("="*80)
    print(f"  Adding Threat Intelligence Feeds (Profile: {args.profile.upper()})")
    print("="*80)

    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    # Get feeds based on profile
    try:
        feeds_to_add = get_feeds_by_profile(args.profile)
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1

    print(f"\nFeeds to add: {len(feeds_to_add)}")

    # Show categories
    if args.profile == 'all':
        ics_count = len([f for f in feeds_to_add if f['category'] == 'ics-ot'])
        gen_count = len([f for f in feeds_to_add if f['category'] == 'general'])
        print(f"  - ICS/OT feeds: {ics_count}")
        print(f"  - General feeds: {gen_count}")

    added = 0
    skipped = 0
    failed = 0

    for feed in feeds_to_add:
        print(f"\n{feed['name']}:")
        print(f"  Provider: {feed['provider']}")
        print(f"  URL: {feed['url']}")
        print(f"  Category: {feed['category']}")

        if args.dry_run:
            print("  [DRY RUN] Would add feed")
            added += 1
            continue

        feed_data = {
            'Feed': {
                'name': feed['name'],
                'provider': feed['provider'],
                'url': feed['url'],
                'source_format': feed['source_format'],
                'enabled': feed['enabled'],
                'distribution': feed['distribution'],
                'default': feed['default']
            }
        }

        response = session.post(f'{session.misp_url}/feeds/add', json=feed_data)

        if response.status_code == 200:
            result = response.json()
            if 'Feed' in result:
                feed_id = result['Feed'].get('id')
                print(f"  ✓ Added successfully (ID: {feed_id})")
                logger.info(f"Feed added: {feed['name']}",
                          event_type="feed_add",
                          action="add",
                          result="success",
                          feed_name=feed['name'],
                          feed_id=feed_id,
                          category=feed['category'],
                          profile=args.profile)
                added += 1
            else:
                print(f"  ⚠️  Already exists or duplicate")
                skipped += 1
        else:
            print(f"  ✗ Failed: HTTP {response.status_code}")
            logger.error(f"Feed add failed: {feed['name']}",
                       event_type="feed_add",
                       action="add",
                       result="failed",
                       feed_name=feed['name'],
                       category=feed['category'])
            failed += 1

    print("\n" + "="*80)
    print("  Summary")
    print("="*80)
    print(f"✅ Added: {added}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")

    if added > 0 and not args.dry_run:
        print("\nNext Steps:")
        print("  1. Feeds are queued for background fetching")
        print("  2. Check status: Global Actions > List Feeds")
        print("  3. Manual fetch: Click 'Fetch and store' for each feed")
        print("  4. View data: Event Index to see imported IOCs")
        print("\nAutomated fetch:")
        print("  python3 scripts/fetch-all-feeds.py")

    logger.info(f"Feed addition complete: {added} added, {skipped} skipped, {failed} failed",
               event_type="feed_add",
               action="complete",
               result="success",
               added=added,
               skipped=skipped,
               failed=failed,
               profile=args.profile)

    return 0


if __name__ == '__main__':
    sys.exit(main())
