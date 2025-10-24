#!/usr/bin/env python3
"""
Fix ThreatFox Feed Caching
Forces proper caching for feed ID 7 (abuse.ch ThreatFox)
"""

import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

MISP_URL = "https://misp-test.lan"
MISP_API_KEY = "pIQlqidOv5HANZDlBqxAcO4ixyHRaVe2mC6nXBXm"
FEED_ID = 7  # ThreatFox

HEADERS = {
    'Authorization': MISP_API_KEY,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

print("=" * 80)
print("THREATFOX FEED TROUBLESHOOTING")
print("=" * 80)
print()

# Step 1: Get current feed details
print("[1] Fetching ThreatFox feed details...")
try:
    response = requests.get(
        f"{MISP_URL}/feeds/view/{FEED_ID}",
        headers=HEADERS,
        verify=False
    )
    if response.status_code == 200:
        data = response.json()
        feed = data.get('Feed', {})
        print(f"✓ Feed Name: {feed.get('name', 'Unknown')}")
        print(f"  Provider: {feed.get('provider', 'Unknown')}")
        print(f"  URL: {feed.get('url', 'Unknown')}")
        print(f"  Enabled: {feed.get('enabled', False)}")
        print(f"  Caching Enabled: {feed.get('caching_enabled', False)}")
        print(f"  Source Format: {feed.get('source_format', 'Unknown')}")
        print(f"  Lookup Visible: {feed.get('lookup_visible', False)}")
        print(f"  Fixed Event: {feed.get('fixed_event', False)}")
        print()
    else:
        print(f"✗ Failed to get feed details: HTTP {response.status_code}")
        print()
except Exception as e:
    print(f"✗ Error: {e}")
    print()

# Step 2: Toggle caching (disable then re-enable to force refresh)
print("[2] Toggling caching to force refresh...")
try:
    # Disable caching first
    response = requests.post(
        f"{MISP_URL}/feeds/toggleSelected/caching_enabled/disable/{FEED_ID}",
        headers=HEADERS,
        verify=False
    )
    print(f"  Disabled caching: HTTP {response.status_code}")
    time.sleep(2)

    # Re-enable caching
    response = requests.post(
        f"{MISP_URL}/feeds/toggleSelected/caching_enabled/enable/{FEED_ID}",
        headers=HEADERS,
        verify=False
    )
    print(f"  Re-enabled caching: HTTP {response.status_code}")
    time.sleep(2)
    print()
except Exception as e:
    print(f"✗ Error toggling: {e}")
    print()

# Step 3: Force fetch from feed
print("[3] Fetching feed data (this may take 30-60 seconds)...")
try:
    response = requests.get(
        f"{MISP_URL}/feeds/fetchFromFeed/{FEED_ID}/all",
        headers=HEADERS,
        verify=False,
        timeout=120
    )
    print(f"  Fetch completed: HTTP {response.status_code}")
    if response.status_code == 200:
        print("  ✓ Feed data fetched successfully")
    else:
        print(f"  Response: {response.text[:200]}")
    print()
except Exception as e:
    print(f"✗ Fetch error: {e}")
    print()

# Step 4: Verify cache file exists
print("[4] Verifying cache file creation...")
import subprocess
try:
    result = subprocess.run(
        ["sudo", "docker", "exec", "misp-misp-core-1", "ls", "-lh", "/var/www/MISP/app/tmp/cache/feeds/"],
        capture_output=True,
        text=True
    )
    cache_files = result.stdout
    if "misp_feed_7" in cache_files:
        print("  ✓ Feed 7 cache file found!")
        for line in cache_files.split('\n'):
            if 'misp_feed_7' in line:
                print(f"    {line.strip()}")
    else:
        print("  ⚠️  No cache file for feed 7 yet")
        print("  This may be normal for MISP manifest feeds")
    print()
except Exception as e:
    print(f"✗ Error checking cache: {e}")
    print()

# Step 5: Check feed status again
print("[5] Final feed status check...")
try:
    response = requests.get(
        f"{MISP_URL}/feeds/view/{FEED_ID}",
        headers=HEADERS,
        verify=False
    )
    if response.status_code == 200:
        data = response.json()
        feed = data.get('Feed', {})
        print(f"  Enabled: {feed.get('enabled', False)}")
        print(f"  Caching Enabled: {feed.get('caching_enabled', False)}")
        print(f"  Events Cached: {feed.get('event_count', 0) if 'event_count' in feed else 'N/A'}")
        print()
    else:
        print(f"✗ Failed: HTTP {response.status_code}")
        print()
except Exception as e:
    print(f"✗ Error: {e}")
    print()

print("=" * 80)
print("TROUBLESHOOTING COMPLETE")
print("=" * 80)
print()
print("Note: MISP manifest feeds (like ThreatFox) may not create traditional")
print("cache files. They use event-based caching instead. Check the MISP UI")
print("at: https://misp-test.lan/feeds/index to verify feed status.")
print()
