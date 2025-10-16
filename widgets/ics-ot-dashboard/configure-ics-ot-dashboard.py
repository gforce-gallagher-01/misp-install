#!/usr/bin/env python3
"""
Configure ICS/OT Threat Intelligence Dashboard
Adds all 5 ICS/OT widgets to MISP dashboard

Usage:
    python3 configure-ics-ot-dashboard.py [--api-key KEY] [--misp-url URL]

Author: tKQB Enterprises
Version: 1.0
Date: 2025-10-16
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from misp_api import get_api_key, get_misp_url, test_connection
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def create_ics_ot_dashboard_config():
    """
    Create ICS/OT dashboard with all 5 widgets

    Layout:
    Row 1: MITRE ATT&CK (left), Vulnerability Feed (right)
    Row 2: Industrial Malware (left), SCADA IOC Monitor (right)
    Row 3: Asset Targeting Analysis (full width)

    Returns:
        list: Dashboard configuration
    """
    dashboard = [
        # Row 1 Left: MITRE ATT&CK for ICS
        {
            "widget": "MITREAttackICSWidget",
            "config": {
                "timeframe": "7d",
                "limit": "15",
                "tactic_filter": ""
            },
            "position": {
                "x": "0",
                "y": "0",
                "width": "6",
                "height": "5"
            }
        },

        # Row 1 Right: ICS Vulnerability Feed
        {
            "widget": "ICSVulnerabilityFeedWidget",
            "config": {
                "timeframe": "7d",
                "limit": "10",
                "severity_filter": ""
            },
            "position": {
                "x": "6",
                "y": "0",
                "width": "6",
                "height": "5"
            }
        },

        # Row 2 Left: Industrial Malware
        {
            "widget": "IndustrialMalwareWidget",
            "config": {
                "timeframe": "30d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "5",
                "width": "6",
                "height": "5"
            }
        },

        # Row 2 Right: SCADA IOC Monitor
        {
            "widget": "SCADAIOCMonitorWidget",
            "config": {
                "timeframe": "7d",
                "limit": "15",
                "ioc_type": "all"
            },
            "position": {
                "x": "6",
                "y": "5",
                "width": "6",
                "height": "5"
            }
        },

        # Row 3: Asset Targeting Analysis (full width)
        {
            "widget": "AssetTargetingAnalysisWidget",
            "config": {
                "timeframe": "7d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "10",
                "width": "12",
                "height": "5"
            }
        }
    ]

    return dashboard


def import_dashboard(misp_url, api_key, dashboard_config):
    """Import dashboard via MISP API"""
    endpoint = f"{misp_url}/dashboards/import"

    headers = {
        "Authorization": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps(dashboard_config)

    try:
        print(f"Importing ICS/OT dashboard...")
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
            print(f"✗ Failed to import dashboard")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Configure ICS/OT Threat Intelligence Dashboard"
    )
    parser.add_argument("--api-key", help="MISP API key")
    parser.add_argument("--misp-url", help="MISP URL")
    parser.add_argument("--backup", action="store_true", default=True)

    args = parser.parse_args()

    print("=" * 60)
    print("ICS/OT Threat Intelligence Dashboard")
    print("=" * 60)
    print()

    api_key = args.api_key or get_api_key()
    misp_url = args.misp_url or get_misp_url()

    if not api_key or not misp_url:
        print("✗ Error: Could not find API key or MISP URL")
        return 1

    print(f"MISP URL: {misp_url}")
    print(f"API Key:  {api_key[:10]}...{api_key[-4:]}")
    print()

    if not test_connection(misp_url, api_key):
        print("✗ Failed to connect to MISP")
        return 1
    print("✓ Connected to MISP")
    print()

    dashboard_config = create_ics_ot_dashboard_config()

    print("Dashboard Layout:")
    print("┌────────────────────────────────────────┐")
    print("│ MITRE ATT&CK │ ICS Vulnerabilities    │")
    print("│ (6×5)        │ (6×5)                  │")
    print("├────────────────────────────────────────┤")
    print("│ Industrial   │ SCADA IOC Monitor      │")
    print("│ Malware(6×5) │ (6×5)                  │")
    print("├────────────────────────────────────────┤")
    print("│ Asset Targeting Analysis               │")
    print("│ (12×5)                                 │")
    print("└────────────────────────────────────────┘")
    print()

    for idx, widget in enumerate(dashboard_config, 1):
        pos = widget['position']
        print(f"{idx}. {widget['widget']}: {pos['width']}×{pos['height']}")
    print()

    success = import_dashboard(misp_url, api_key, dashboard_config)

    if success:
        print()
        print("=" * 60)
        print("✓ ICS/OT Dashboard Configured!")
        print("=" * 60)
        print()
        print("All 5 widgets added:")
        print("  1. MITRE ATT&CK for ICS Techniques")
        print("  2. ICS Vulnerability Feed")
        print("  3. Industrial Malware Families")
        print("  4. SCADA IOC Monitor")
        print("  5. Asset Targeting Analysis")
        print()
        print("Refresh MISP dashboard to see changes")
        return 0
    else:
        print("✗ Failed to configure dashboard")
        return 1


if __name__ == "__main__":
    sys.exit(main())
