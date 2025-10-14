#!/usr/bin/env python3
"""
Add ICS/OT Threat Intelligence Feeds to MISP
Version: 1.0
Date: 2025-10-14

Purpose:
    Add threat intelligence feeds specifically relevant for ICS/OT/NERC CIP environments.
    These feeds provide actual IOCs (indicators of compromise) for threat detection.

Usage:
    python3 scripts/add-ics-ot-threat-feeds.py --api-key YOUR_KEY
    python3 scripts/add-ics-ot-threat-feeds.py  # Auto-detect API key

Feeds Added:
    - abuse.ch URLhaus: Malicious URLs used for malware distribution
    - abuse.ch Feodo Tracker: Botnet C2 servers (Feodo/Emotet/Dridex)
    - Blocklist.de: SSH, Mail, Apache attack sources
    - OpenPhish: Phishing URLs targeting organizations
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_api import get_api_key, get_misp_client, test_connection
from misp_logger import get_logger

# ICS/OT threat intelligence feeds
ICS_OT_FEEDS = [
    {
        'name': 'abuse.ch URLhaus',
        'provider': 'abuse.ch',
        'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'URLhaus malicious URLs for malware distribution'
    },
    {
        'name': 'abuse.ch Feodo Tracker',
        'provider': 'abuse.ch',
        'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Feodo/Emotet/Dridex botnet C2 servers'
    },
    {
        'name': 'Blocklist.de All',
        'provider': 'Blocklist.de',
        'url': 'https://lists.blocklist.de/lists/all.txt',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Attack sources (SSH, Mail, Apache, etc.)'
    },
    {
        'name': 'OpenPhish URL Feed',
        'provider': 'OpenPhish',
        'url': 'https://openphish.com/feed.txt',
        'source_format': 'csv',
        'enabled': True,
        'distribution': 3,
        'default': True,
        'description': 'Phishing URLs'
    }
]


def main():
    parser = argparse.ArgumentParser(
        description='Add ICS/OT threat intelligence feeds to MISP'
    )
    parser.add_argument('--api-key', type=str, help='MISP API key')
    parser.add_argument('--dry-run', action='store_true', help='Preview without adding')
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("ERROR: No API key found")
        return 1

    # Get logger
    logger = get_logger('add-ics-ot-feeds', 'misp:feed')

    # Test connection
    session = get_misp_client(api_key=api_key)
    success, message = test_connection(session)
    if not success:
        print(f"ERROR: {message}")
        return 1

    print(f"✓ {message}\n")
    print("="*80)
    print("  Adding ICS/OT Threat Intelligence Feeds")
    print("="*80)

    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    added = 0
    skipped = 0
    failed = 0

    for feed in ICS_OT_FEEDS:
        print(f"\n{feed['name']}:")
        print(f"  Provider: {feed['provider']}")
        print(f"  URL: {feed['url']}")
        
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
                          feed_id=feed_id)
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
                       feed_name=feed['name'])
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

    logger.info(f"Feed addition complete: {added} added, {skipped} skipped, {failed} failed",
               event_type="feed_add",
               action="complete",
               result="success",
               added=added,
               skipped=skipped,
               failed=failed)

    return 0


if __name__ == '__main__':
    sys.exit(main())
