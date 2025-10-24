#!/usr/bin/env python3
"""
MISP Feed Management Script
Enables, caches, and validates all feeds
"""

import sys
import time

import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certs
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# MISP Configuration
MISP_URL = "https://misp-test.lan"
MISP_API_KEY = "pIQlqidOv5HANZDlBqxAcO4ixyHRaVe2mC6nXBXm"

HEADERS = {
    'Authorization': MISP_API_KEY,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def get_all_feeds():
    """Get all feeds from MISP"""
    print("📡 Fetching all feeds...")
    try:
        response = requests.get(
            f"{MISP_URL}/feeds/index",
            headers=HEADERS,
            verify=False
        )
        response.raise_for_status()
        data = response.json()

        # Handle different response formats
        if isinstance(data, list):
            feeds = data
        elif isinstance(data, dict):
            feeds = data.get('response', data.get('Feed', []))
        else:
            feeds = []

        print(f"✓ Found {len(feeds)} feeds\n")
        return feeds
    except Exception as e:
        print(f"✗ Failed to get feeds: {e}")
        import traceback
        traceback.print_exc()
        return []

def enable_feed(feed_id):
    """Enable a specific feed"""
    try:
        response = requests.post(
            f"{MISP_URL}/feeds/enable/{feed_id}",
            headers=HEADERS,
            verify=False
        )
        return response.status_code == 200
    except Exception as e:
        print(f"  ✗ Failed to enable feed {feed_id}: {e}")
        return False

def enable_caching(feed_id):
    """Enable caching for a specific feed"""
    try:
        response = requests.post(
            f"{MISP_URL}/feeds/cacheFeeds/{feed_id}",
            headers=HEADERS,
            verify=False
        )
        return response.status_code == 200
    except Exception as e:
        print(f"  ✗ Failed to enable caching for feed {feed_id}: {e}")
        return False

def cache_feed(feed_id):
    """Fetch and cache feed data"""
    try:
        response = requests.get(
            f"{MISP_URL}/feeds/fetchFromFeed/{feed_id}",
            headers=HEADERS,
            verify=False,
            timeout=300  # 5 minute timeout for large feeds
        )
        return response.status_code == 200
    except Exception as e:
        print(f"  ✗ Failed to cache feed {feed_id}: {e}")
        return False

def print_feed_summary(feeds):
    """Print summary of feed status"""
    enabled_count = 0
    disabled_count = 0
    cached_count = 0
    uncached_count = 0

    for feed_wrapper in feeds:
        feed = feed_wrapper.get('Feed', {})
        if feed.get('enabled', False):
            enabled_count += 1
        else:
            disabled_count += 1

        if feed.get('caching_enabled', False):
            cached_count += 1
        else:
            uncached_count += 1

    print("=" * 80)
    print("FEED STATUS SUMMARY")
    print("=" * 80)
    print(f"Total Feeds:      {len(feeds)}")
    print(f"  Enabled:        {enabled_count}")
    print(f"  Disabled:       {disabled_count}")
    print(f"  Caching On:     {cached_count}")
    print(f"  Caching Off:    {uncached_count}")
    print("=" * 80)
    print()

def main():
    print("=" * 80)
    print("MISP FEED MANAGEMENT - ENABLE, CACHE, AND VALIDATE")
    print("=" * 80)
    print()

    # Step 1: Get all feeds
    feeds = get_all_feeds()
    if not feeds:
        print("✗ No feeds found or unable to fetch feeds")
        return 1

    print_feed_summary(feeds)

    # Step 2: Enable all disabled feeds
    print("=" * 80)
    print("STEP 1: ENABLING ALL FEEDS")
    print("=" * 80)

    disabled_feeds = []
    for feed_wrapper in feeds:
        feed = feed_wrapper.get('Feed', {})
        if not feed.get('enabled', False):
            disabled_feeds.append(feed)

    if disabled_feeds:
        print(f"Found {len(disabled_feeds)} disabled feeds\n")
        for feed in disabled_feeds:
            feed_id = feed.get('id')
            feed_name = feed.get('name', 'Unknown')
            print(f"  [{feed_id}] Enabling: {feed_name}...")
            if enable_feed(feed_id):
                print("      ✓ Enabled")
            else:
                print("      ✗ Failed to enable")
            time.sleep(0.5)  # Rate limiting
    else:
        print("✓ All feeds already enabled")
    print()

    # Step 3: Enable caching for all feeds
    print("=" * 80)
    print("STEP 2: ENABLING CACHING FOR ALL FEEDS")
    print("=" * 80)

    uncached_feeds = []
    for feed_wrapper in feeds:
        feed = feed_wrapper.get('Feed', {})
        if not feed.get('caching_enabled', False):
            uncached_feeds.append(feed)

    if uncached_feeds:
        print(f"Found {len(uncached_feeds)} feeds without caching\n")
        for feed in uncached_feeds:
            feed_id = feed.get('id')
            feed_name = feed.get('name', 'Unknown')
            print(f"  [{feed_id}] Enabling caching: {feed_name}...")
            if enable_caching(feed_id):
                print("      ✓ Caching enabled")
            else:
                print("      ✗ Failed to enable caching")
            time.sleep(0.5)
    else:
        print("✓ All feeds already have caching enabled")
    print()

    # Step 4: Cache all feeds (fetch data)
    print("=" * 80)
    print("STEP 3: CACHING ALL FEEDS (FETCHING DATA)")
    print("=" * 80)
    print(f"⚠️  This will take several minutes for {len(feeds)} feeds...")
    print()

    success_count = 0
    failed_count = 0

    for i, feed_wrapper in enumerate(feeds, 1):
        feed = feed_wrapper.get('Feed', {})
        feed_id = feed.get('id')
        feed_name = feed.get('name', 'Unknown')
        feed_provider = feed.get('provider', 'Unknown')

        print(f"[{i}/{len(feeds)}] Caching: {feed_name} ({feed_provider})...")
        if cache_feed(feed_id):
            print("    ✓ Cached successfully")
            success_count += 1
        else:
            print("    ✗ Failed to cache")
            failed_count += 1

        time.sleep(1)  # Rate limiting between feeds

    print()
    print("=" * 80)
    print("CACHING COMPLETE")
    print("=" * 80)
    print(f"  Successful:  {success_count}")
    print(f"  Failed:      {failed_count}")
    print("=" * 80)
    print()

    # Step 5: Validate feed status
    print("=" * 80)
    print("STEP 4: VALIDATING FINAL FEED STATUS")
    print("=" * 80)
    print()

    feeds_after = get_all_feeds()
    if not feeds_after:
        print("✗ Unable to fetch feeds for validation")
        return 1

    print_feed_summary(feeds_after)

    # Detailed validation
    print("=" * 80)
    print("DETAILED FEED STATUS")
    print("=" * 80)

    all_enabled = True
    all_cached = True

    for feed_wrapper in feeds_after:
        feed = feed_wrapper.get('Feed', {})
        feed_id = feed.get('id')
        feed_name = feed.get('name', 'Unknown')
        enabled = feed.get('enabled', False)
        caching = feed.get('caching_enabled', False)

        status_icons = []
        if enabled:
            status_icons.append('✓ Enabled')
        else:
            status_icons.append('✗ Disabled')
            all_enabled = False

        if caching:
            status_icons.append('✓ Cached')
        else:
            status_icons.append('✗ No Cache')
            all_cached = False

        print(f"[{feed_id}] {feed_name}")
        print(f"     {' | '.join(status_icons)}")

    print()
    print("=" * 80)
    print("VALIDATION RESULT")
    print("=" * 80)

    if all_enabled and all_cached:
        print("✓ ALL FEEDS ENABLED AND CACHING")
        print("✓ Feed management complete!")
        return 0
    else:
        if not all_enabled:
            print("⚠️  Some feeds are still disabled")
        if not all_cached:
            print("⚠️  Some feeds don't have caching enabled")
        print()
        print("⚠️  Manual intervention may be required for failed feeds")
        return 1

if __name__ == '__main__':
    sys.exit(main())
