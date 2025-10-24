#!/usr/bin/env python3
"""
Configure MISP Dashboard with Utilities Sector Widgets
Automatically adds widgets to the admin user's dashboard via REST API

Usage:
    python3 configure-dashboard.py [--api-key KEY] [--misp-url URL]

Author: tKQB Enterprises
Version: 1.0
Date: 2025-10-16
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from urllib3.exceptions import InsecureRequestWarning

from misp_api import get_api_key, get_misp_url, test_connection

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def create_dashboard_config():
    """
    Create dashboard configuration with Utilities Sector widgets

    Layout optimized for MISP dashboard grid (user-tested sizing):
    - Left column (x=1, width=2): Event Stream, Trending Attributes, Trending Tags
    - Right column (x=3, width=6): Utilities Threat Heat Map

    Returns:
        list: Dashboard configuration with widget definitions
    """
    dashboard = [
        # Left column, top: Recent Events
        {
            "widget": "EventStreamWidget",
            "config": {
                "limit": "5"
            },
            "position": {
                "x": "1",
                "y": "0",
                "width": "2",
                "height": "5"
            }
        },

        # Left column, middle: Trending Attributes
        {
            "widget": "TrendingAttributesWidget",
            "config": {
                "limit": "10",
                "days": "7"
            },
            "position": {
                "x": "1",
                "y": "5",
                "width": "2",
                "height": "2"
            }
        },

        # Left column, bottom: Trending Tags
        {
            "widget": "TrendingTagsWidget",
            "config": {
                "limit": "10",
                "days": "7"
            },
            "position": {
                "x": "1",
                "y": "7",
                "width": "2",
                "height": "6"
            }
        },

        # Right column: Utilities Threat Heat Map (large)
        {
            "widget": "UtilitiesThreatHeatMapWidget",
            "config": {
                "timeframe": "7d",
                "limit": "1000",
                "sector_tag": "ics:sector"
            },
            "position": {
                "x": "3",
                "y": "0",
                "width": "6",
                "height": "9"
            }
        }
    ]

    return dashboard


def import_dashboard(misp_url, api_key, dashboard_config):
    """
    Import dashboard configuration via MISP API

    Args:
        misp_url (str): MISP instance URL
        api_key (str): API authentication key
        dashboard_config (list): Dashboard widget configuration

    Returns:
        bool: True if successful, False otherwise
    """
    endpoint = f"{misp_url}/dashboards/import"

    headers = {
        "Authorization": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps(dashboard_config)

    try:
        print("Importing dashboard configuration...")
        print(f"  Endpoint: {endpoint}")
        print(f"  Widgets: {len(dashboard_config)}")

        response = requests.post(
            endpoint,
            headers=headers,
            data=payload,
            verify=False,
            timeout=30
        )

        if response.status_code == 200:
            print("✓ Dashboard imported successfully!")
            return True
        else:
            print("✗ Failed to import dashboard")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Error importing dashboard: {e}")
        return False


def export_dashboard(misp_url, api_key):
    """
    Export current dashboard configuration

    Args:
        misp_url (str): MISP instance URL
        api_key (str): API authentication key

    Returns:
        dict: Current dashboard configuration or None
    """
    endpoint = f"{misp_url}/dashboards/export"

    headers = {
        "Authorization": api_key,
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            endpoint,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Warning: Could not export current dashboard (status {response.status_code})")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Warning: Error exporting dashboard: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Configure MISP dashboard with Utilities Sector widgets"
    )
    parser.add_argument(
        "--api-key",
        help="MISP API key (auto-detected if not provided)"
    )
    parser.add_argument(
        "--misp-url",
        help="MISP URL (auto-detected if not provided)"
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Only export current dashboard, don't import"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup current dashboard before importing"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("MISP Dashboard Configuration Tool")
    print("Utilities Sector Widgets")
    print("=" * 60)
    print()

    # Get API credentials
    api_key = args.api_key or get_api_key()
    misp_url = args.misp_url or get_misp_url()

    if not api_key:
        print("✗ Error: Could not find MISP API key")
        print("  Provide via --api-key or set MISP_API_KEY environment variable")
        return 1

    if not misp_url:
        print("✗ Error: Could not find MISP URL")
        print("  Provide via --misp-url or set MISP_URL environment variable")
        return 1

    print(f"MISP URL: {misp_url}")
    print(f"API Key:  {api_key[:10]}...{api_key[-4:]}")
    print()

    # Test connection
    print("Testing connection...")
    if not test_connection(misp_url, api_key):
        print("✗ Failed to connect to MISP")
        return 1
    print("✓ Connected to MISP successfully")
    print()

    # Export current dashboard if requested
    if args.export_only or args.backup:
        print("Exporting current dashboard...")
        current_dashboard = export_dashboard(misp_url, api_key)

        if current_dashboard:
            backup_file = Path("dashboard-backup.json")
            with open(backup_file, 'w') as f:
                json.dump(current_dashboard, f, indent=2)
            print(f"✓ Dashboard backed up to: {backup_file}")

            if args.export_only:
                print()
                print("Current dashboard configuration:")
                print(json.dumps(current_dashboard, indent=2))
                return 0
        print()

    # Create and import dashboard
    dashboard_config = create_dashboard_config()

    print("Dashboard Configuration:")
    print(f"  Total widgets: {len(dashboard_config)}")
    print()
    for idx, widget in enumerate(dashboard_config, 1):
        print(f"  {idx}. {widget['title']}")
        print(f"     Widget: {widget['widget']}")
        print(f"     Size: {widget['width']}x{widget['height']}")
    print()

    # Import dashboard
    success = import_dashboard(misp_url, api_key, dashboard_config)

    print()
    if success:
        print("=" * 60)
        print("✓ Dashboard configured successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Log into MISP web interface")
        print("2. Navigate to Dashboard")
        print("3. Your widgets should now be visible")
        print()
        print("Note: If widgets don't appear, you may need to:")
        print("- Refresh the page (Ctrl+R)")
        print("- Clear browser cache")
        print("- Check MISP logs for errors")
        return 0
    else:
        print("=" * 60)
        print("✗ Failed to configure dashboard")
        print("=" * 60)
        print()
        print("Troubleshooting:")
        print("1. Verify widget is installed:")
        print("   sudo docker exec misp-misp-core-1 ls -la \\")
        print("     /var/www/MISP/app/Lib/Dashboard/Custom/")
        print()
        print("2. Check MISP logs:")
        print("   sudo docker exec misp-misp-core-1 tail -50 \\")
        print("     /var/www/MISP/app/tmp/logs/error.log")
        print()
        print("3. Test API manually:")
        print(f"   curl -k -H 'Authorization: {api_key}' \\")
        print(f"     {misp_url}/dashboards/export")
        return 1


if __name__ == "__main__":
    sys.exit(main())
