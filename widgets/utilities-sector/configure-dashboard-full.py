#!/usr/bin/env python3
"""
Configure MISP Dashboard with ALL 5 Utilities Sector Widgets
Comprehensive dashboard layout optimized for utilities sector monitoring

Usage:
    python3 configure-dashboard-full.py [--api-key KEY] [--misp-url URL]

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


def create_full_dashboard_config():
    """
    Create comprehensive dashboard with all 5 utilities sector widgets

    User-optimized layout:
    Row 1: Stats (narrow left), ICS Protocols (wide right)
    Row 2: Infrastructure Breakdown (left), NERC CIP (right)
    Row 3: Heat Map (full width at bottom - largest widget)

    Returns:
        list: Dashboard configuration with all 5 widgets
    """
    dashboard = [
        # Row 1 Left: Utilities Sector Stats (compact)
        {
            "widget": "UtilitiesSectorStatsWidget",
            "config": {
                "show_24h": True,
                "show_7d": True,
                "show_30d": True
            },
            "position": {
                "x": "0",
                "y": "0",
                "width": "2",
                "height": "3"
            }
        },

        # Row 1 Right: ICS Protocols Targeted (prominent)
        {
            "widget": "ICSProtocolsTargetedWidget",
            "config": {
                "timeframe": "7d",
                "limit": "10",
                "sector_filter": ""
            },
            "position": {
                "x": "2",
                "y": "0",
                "width": "6",
                "height": "3"
            }
        },

        # Row 2 Left: Critical Infrastructure Breakdown
        {
            "widget": "CriticalInfrastructureBreakdownWidget",
            "config": {
                "timeframe": "7d",
                "breakdown_by": "subsector",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "3",
                "width": "6",
                "height": "5"
            }
        },

        # Row 2 Right: NERC CIP Compliance
        {
            "widget": "NERCCIPComplianceWidget",
            "config": {
                "timeframe": "7d",
                "cip_standards": [],  # Empty = monitor all standards
                "limit": "10"
            },
            "position": {
                "x": "6",
                "y": "3",
                "width": "6",
                "height": "5"
            }
        },

        # Row 3: Utilities Threat Heat Map (full width, large)
        {
            "widget": "UtilitiesThreatHeatMapWidget",
            "config": {
                "timeframe": "7d",
                "limit": "1000",
                "sector_tag": "ics:sector"
            },
            "position": {
                "x": "0",
                "y": "8",
                "width": "12",
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
        print("Importing full dashboard configuration...")
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
        description="Configure MISP dashboard with ALL 5 Utilities Sector widgets"
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
        default=True,
        help="Backup current dashboard before importing (default: true)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("MISP Full Dashboard Configuration Tool")
    print("ALL 5 Utilities Sector Widgets")
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
            backup_file = Path("dashboard-backup-full.json")
            with open(backup_file, 'w') as f:
                json.dump(current_dashboard, f, indent=2)
            print(f"✓ Dashboard backed up to: {backup_file}")

            if args.export_only:
                print()
                print("Current dashboard configuration:")
                print(json.dumps(current_dashboard, indent=2))
                return 0
        print()

    # Create and import full dashboard
    dashboard_config = create_full_dashboard_config()

    print("=" * 60)
    print("Full Dashboard Configuration (5 Widgets)")
    print("=" * 60)
    print()
    print("User-Optimized Layout:")
    print("┌────────────────────────────────────────────┐")
    print("│ Stats │ ICS Protocols Targeted           │")
    print("│ (2×3) │ (6×3)                            │")
    print("├────────────────────────────────────────────┤")
    print("│ Infrastructure  │ NERC CIP Compliance    │")
    print("│ Breakdown (6×5) │ (6×5)                  │")
    print("├────────────────────────────────────────────┤")
    print("│ Utilities Threat Heat Map                │")
    print("│ (12×9)                                    │")
    print("│                                           │")
    print("└────────────────────────────────────────────┘")
    print()

    for idx, widget in enumerate(dashboard_config, 1):
        pos = widget['position']
        print(f"{idx}. {widget['widget']}")
        print(f"   Position: x={pos['x']}, y={pos['y']}, size={pos['width']}×{pos['height']}")
    print()

    # Import dashboard
    success = import_dashboard(misp_url, api_key, dashboard_config)

    print()
    if success:
        print("=" * 60)
        print("✓ Full Dashboard Configured Successfully!")
        print("=" * 60)
        print()
        print("All 5 widgets are now in your dashboard:")
        print("  1. Utilities Sector Stats")
        print("  2. Utilities Threat Heat Map")
        print("  3. ICS Protocols Targeted")
        print("  4. Critical Infrastructure Breakdown")
        print("  5. NERC CIP Compliance Events")
        print()
        print("Next steps:")
        print("1. Log into MISP web interface")
        print("2. Navigate to Dashboard")
        print("3. Refresh page (Ctrl+R)")
        print("4. All 5 widgets should be visible")
        print()
        print("Note: Widgets may show 'No Data' until you have")
        print("events with appropriate ICS tags.")
        return 0
    else:
        print("=" * 60)
        print("✗ Failed to configure dashboard")
        print("=" * 60)
        print()
        print("Troubleshooting:")
        print("1. Check widgets are installed:")
        print("   sudo docker exec misp-misp-core-1 ls -la \\")
        print("     /var/www/MISP/app/Lib/Dashboard/Custom/")
        print()
        print("2. Check MISP logs:")
        print("   sudo docker exec misp-misp-core-1 tail -50 \\")
        print("     /var/www/MISP/app/tmp/logs/error.log")
        return 1


if __name__ == "__main__":
    sys.exit(main())
