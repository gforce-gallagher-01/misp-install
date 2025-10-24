#!/usr/bin/env python3
"""
Configure ALL MISP Dashboards - Master Configuration
Includes ALL widgets from all dashboard sets

Usage:
    python3 configure-all-dashboards.py [--api-key KEY] [--misp-url URL]

Author: tKQB Enterprises
Version: 1.0
Date: 2025-10-16
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from urllib3.exceptions import InsecureRequestWarning

from misp_api import get_api_key, get_misp_url, test_connection

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def create_complete_dashboard_config():
    """
    Create complete dashboard with ALL widgets from all sets

    Dashboard 1: Utilities Sector Overview (5 widgets)
    Dashboard 2: ICS/OT Threat Intelligence (5 widgets)
    Dashboard 3: Threat Actor Dashboard (5 widgets)
    Dashboard 4: Utilities Feed Dashboard (5 widgets)
    Dashboard 5: Organizational Contribution (5 widgets)

    Total: 25 widgets

    Returns:
        list: Complete dashboard configuration
    """
    dashboard = [
        # === UTILITIES SECTOR OVERVIEW DASHBOARD (5 widgets) ===

        # Row 1: Stats + ICS Protocols
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

        # Row 2: Infrastructure Breakdown + NERC CIP
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
        {
            "widget": "NERCCIPComplianceWidget",
            "config": {
                "timeframe": "7d",
                "cip_standards": [],
                "limit": "10"
            },
            "position": {
                "x": "6",
                "y": "3",
                "width": "6",
                "height": "5"
            }
        },

        # Row 3: Threat Heat Map (full width)
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
        },

        # === ICS/OT THREAT INTELLIGENCE DASHBOARD (5 widgets) ===

        # Row 4: MITRE ATT&CK + Vulnerabilities
        {
            "widget": "MITREAttackICSWidget",
            "config": {
                "timeframe": "7d",
                "limit": "15",
                "tactic_filter": ""
            },
            "position": {
                "x": "0",
                "y": "17",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "ICSVulnerabilityFeedWidget",
            "config": {
                "timeframe": "7d",
                "limit": "10",
                "severity_filter": ""
            },
            "position": {
                "x": "6",
                "y": "17",
                "width": "6",
                "height": "5"
            }
        },

        # Row 5: Industrial Malware + SCADA IOC
        {
            "widget": "IndustrialMalwareWidget",
            "config": {
                "timeframe": "30d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "22",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "SCADAIOCMonitorWidget",
            "config": {
                "timeframe": "7d",
                "limit": "15",
                "ioc_type": "all"
            },
            "position": {
                "x": "6",
                "y": "22",
                "width": "6",
                "height": "5"
            }
        },

        # Row 6: Asset Targeting (full width)
        {
            "widget": "AssetTargetingAnalysisWidget",
            "config": {
                "timeframe": "7d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "27",
                "width": "12",
                "height": "5"
            }
        },

        # === THREAT ACTOR DASHBOARD (5 widgets) ===

        # Row 7: APT Groups + Campaign Tracking
        {
            "widget": "APTGroupsUtilitiesWidget",
            "config": {
                "timeframe": "365d",
                "limit": "15"
            },
            "position": {
                "x": "0",
                "y": "32",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "CampaignTrackingWidget",
            "config": {
                "timeframe": "90d",
                "limit": "10"
            },
            "position": {
                "x": "6",
                "y": "32",
                "width": "6",
                "height": "5"
            }
        },

        # Row 8: Nation-State Attribution + TTPs
        {
            "widget": "NationStateAttributionWidget",
            "config": {
                "timeframe": "365d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "37",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "TTPsUtilitiesWidget",
            "config": {
                "timeframe": "365d",
                "limit": "15"
            },
            "position": {
                "x": "6",
                "y": "37",
                "width": "6",
                "height": "5"
            }
        },

        # Row 9: Historical Incidents (full width)
        {
            "widget": "HistoricalIncidentsWidget",
            "config": {
                "timeframe": "10y",
                "limit": "15",
                "sector_filter": "utilities"
            },
            "position": {
                "x": "0",
                "y": "42",
                "width": "12",
                "height": "5"
            }
        },

        # === UTILITIES FEED DASHBOARD (5 widgets) ===

        # Row 10: ICS-CERT Advisory + CISA Alerts
        {
            "widget": "ICSCERTAdvisoryWidget",
            "config": {
                "timeframe": "30d",
                "limit": "15",
                "severity_filter": "all"
            },
            "position": {
                "x": "0",
                "y": "47",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "CISAUtilitiesAlertsWidget",
            "config": {
                "timeframe": "30d",
                "limit": "10",
                "alert_type": "all"
            },
            "position": {
                "x": "6",
                "y": "47",
                "width": "6",
                "height": "5"
            }
        },

        # Row 11: Vendor Bulletins + Zero-Day Tracker
        {
            "widget": "VendorSecurityBulletinsWidget",
            "config": {
                "timeframe": "90d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "52",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "ICSZeroDayTrackerWidget",
            "config": {
                "timeframe": "90d",
                "limit": "10",
                "min_cvss": "7.0"
            },
            "position": {
                "x": "6",
                "y": "52",
                "width": "6",
                "height": "5"
            }
        },

        # Row 12: Feed Health Monitor (full width)
        {
            "widget": "FeedHealthMonitorWidget",
            "config": {
                "timeframe": "7d",
                "show_inactive": "false"
            },
            "position": {
                "x": "0",
                "y": "57",
                "width": "12",
                "height": "5"
            }
        },

        # === ORGANIZATIONAL CONTRIBUTION DASHBOARD (5 widgets) ===

        # Row 13: ISAC Rankings + Sharing Metrics
        {
            "widget": "ISACContributionRankingsWidget",
            "config": {
                "timeframe": "90d",
                "limit": "15"
            },
            "position": {
                "x": "0",
                "y": "62",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "SectorSharingMetricsWidget",
            "config": {
                "timeframe": "30d",
                "compare_previous": "true"
            },
            "position": {
                "x": "6",
                "y": "62",
                "width": "6",
                "height": "5"
            }
        },

        # Row 14: Regional Cooperation (full width)
        {
            "widget": "RegionalCooperationHeatMapWidget",
            "config": {
                "timeframe": "90d",
                "metric": "events"
            },
            "position": {
                "x": "0",
                "y": "67",
                "width": "12",
                "height": "9"
            }
        },

        # Row 15: Subsector Contribution + Monthly Trends
        {
            "widget": "SubsectorContributionWidget",
            "config": {
                "timeframe": "90d",
                "limit": "10"
            },
            "position": {
                "x": "0",
                "y": "76",
                "width": "6",
                "height": "5"
            }
        },
        {
            "widget": "MonthlyContributionTrendWidget",
            "config": {
                "months": "12",
                "metric": "events"
            },
            "position": {
                "x": "6",
                "y": "76",
                "width": "6",
                "height": "5"
            }
        }
    ]

    return dashboard


def import_dashboard(misp_url, api_key, dashboard_config):
    """Import complete dashboard via MISP API"""
    endpoint = f"{misp_url}/dashboards/import"

    headers = {
        "Authorization": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps(dashboard_config)

    try:
        print("Importing complete dashboard...")
        print(f"  Total widgets: {len(dashboard_config)}")

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
            print(f"✗ Failed: Status {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Configure ALL MISP Dashboards (Master Configuration)"
    )
    parser.add_argument("--api-key", help="MISP API key")
    parser.add_argument("--misp-url", help="MISP URL")

    args = parser.parse_args()

    print("=" * 60)
    print("COMPLETE DASHBOARD CONFIGURATION")
    print("All Widget Sets Combined")
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
        print("✗ Failed to connect")
        return 1
    print("✓ Connected")
    print()

    dashboard_config = create_complete_dashboard_config()

    print("Dashboard Layout (Scrollable):")
    print()
    print("=== UTILITIES SECTOR OVERVIEW ===")
    print("┌────────────────────────────────┐")
    print("│ Stats │ ICS Protocols         │")
    print("├────────────────────────────────┤")
    print("│ Infrastructure│ NERC CIP       │")
    print("├────────────────────────────────┤")
    print("│ Threat Heat Map (12×9)        │")
    print("└────────────────────────────────┘")
    print()
    print("=== ICS/OT THREAT INTELLIGENCE ===")
    print("┌────────────────────────────────┐")
    print("│ MITRE ATT&CK │ Vulnerabilities│")
    print("├────────────────────────────────┤")
    print("│ Malware      │ SCADA IOCs     │")
    print("├────────────────────────────────┤")
    print("│ Asset Targeting (12×5)        │")
    print("└────────────────────────────────┘")
    print()
    print("=== THREAT ACTOR DASHBOARD ===")
    print("┌────────────────────────────────┐")
    print("│ APT Groups   │ Campaign Track │")
    print("├────────────────────────────────┤")
    print("│ Nation-State │ TTPs           │")
    print("├────────────────────────────────┤")
    print("│ Historical Incidents (12×5)   │")
    print("└────────────────────────────────┘")
    print()
    print("=== UTILITIES FEED DASHBOARD ===")
    print("┌────────────────────────────────┐")
    print("│ ICS-CERT     │ CISA Alerts    │")
    print("├────────────────────────────────┤")
    print("│ Vendor Bills │ Zero-Day Track │")
    print("├────────────────────────────────┤")
    print("│ Feed Health Monitor (12×5)    │")
    print("└────────────────────────────────┘")
    print()
    print("=== ORGANIZATIONAL CONTRIBUTION ===")
    print("┌────────────────────────────────┐")
    print("│ ISAC Rank    │ Share Metrics  │")
    print("├────────────────────────────────┤")
    print("│ Regional Cooperation (12×9)   │")
    print("├────────────────────────────────┤")
    print("│ Subsector    │ Monthly Trend  │")
    print("└────────────────────────────────┘")
    print()
    print(f"Total: {len(dashboard_config)} widgets")
    print()

    success = import_dashboard(misp_url, api_key, dashboard_config)

    if success:
        print()
        print("=" * 60)
        print("✓ Complete Dashboard Configured!")
        print("=" * 60)
        print()
        print("Dashboard 1: Utilities Sector Overview (5)")
        print("  ✓ UtilitiesSectorStatsWidget")
        print("  ✓ ICSProtocolsTargetedWidget")
        print("  ✓ CriticalInfrastructureBreakdownWidget")
        print("  ✓ NERCCIPComplianceWidget")
        print("  ✓ UtilitiesThreatHeatMapWidget")
        print()
        print("Dashboard 2: ICS/OT Threat Intelligence (5)")
        print("  ✓ MITREAttackICSWidget")
        print("  ✓ ICSVulnerabilityFeedWidget")
        print("  ✓ IndustrialMalwareWidget")
        print("  ✓ SCADAIOCMonitorWidget")
        print("  ✓ AssetTargetingAnalysisWidget")
        print()
        print("Dashboard 3: Threat Actor Dashboard (5)")
        print("  ✓ APTGroupsUtilitiesWidget")
        print("  ✓ CampaignTrackingWidget")
        print("  ✓ NationStateAttributionWidget")
        print("  ✓ TTPsUtilitiesWidget")
        print("  ✓ HistoricalIncidentsWidget")
        print()
        print("Dashboard 4: Utilities Feed Dashboard (5)")
        print("  ✓ ICSCERTAdvisoryWidget")
        print("  ✓ CISAUtilitiesAlertsWidget")
        print("  ✓ VendorSecurityBulletinsWidget")
        print("  ✓ ICSZeroDayTrackerWidget")
        print("  ✓ FeedHealthMonitorWidget")
        print()
        print("Dashboard 5: Organizational Contribution (5)")
        print("  ✓ ISACContributionRankingsWidget")
        print("  ✓ SectorSharingMetricsWidget")
        print("  ✓ RegionalCooperationHeatMapWidget")
        print("  ✓ SubsectorContributionWidget")
        print("  ✓ MonthlyContributionTrendWidget")
        print()
        print("Refresh MISP to see all 25 widgets!")
        return 0
    else:
        print("✗ Configuration failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
