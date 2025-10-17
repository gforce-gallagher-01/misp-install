#!/usr/bin/env python3
"""
Create utilities sector-specific threat intelligence events in MISP.

This script creates sample ICS/OT threat intelligence data for testing
the utilities sector dashboard widgets.

Events Created:
1. Industroyer2 Power Grid Attack (2022)
2. TRITON Safety System Attack (2017)
3. PIPEDREAM ICS Malware Discovery (2022)
4. Havex Energy Sector Campaign (2014)
5. BlackEnergy Ukraine Grid Attack (2015)
6. APT33 Energy Targeting (ongoing)
7. Dragonfly 2.0 Energy Campaign (2017)
8. XENOTIME Safety System Targeting (2018)
9. Sandworm ICS Attacks (ongoing)
10. MERCURY Water Sector Targeting (2021)
11. Critical Modbus TCP/IP Vulnerability (CVE-2023-1234)
12. Schneider SCADA Authentication Bypass (CVE-2023-5678)
13. Siemens S7 PLC Memory Corruption (CVE-2023-9012)
14. Allen-Bradley PLC Code Injection (CVE-2023-3456)
15. GE Digital CIMPLICITY RCE (CVE-2023-7890)
16. Water Treatment Plant SCADA Breach (2021)
17. Municipal Water System Ransomware (2022)
18. Wastewater Facility HMI Compromise (2023)
19. Hydroelectric Dam Control System Probe (2020)
20. Bureau of Reclamation Dam System Targeting (2022)

Author: tKQB Enterprises
Version: 1.0.0
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import urllib3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_logger import get_logger
from lib.misp_api_helpers import get_api_key, get_misp_url, mask_api_key
from event_templates import EVENT_TEMPLATES

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize logger
logger = get_logger('create-utilities-sector-intelligence', 'misp:threat_intel')


class UtilitiesSectorIntelligence:
    """Create utilities sector threat intelligence events"""

    def __init__(self, misp_url: str, api_key: str):
        """Initialize with MISP connection details"""
        self.misp_url = misp_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.verify_ssl = False

        logger.info("Initialized utilities sector intelligence creator",
                   misp_url=misp_url,
                   api_key_masked=mask_api_key(api_key))

    def _get_recent_date(self, days_ago: int) -> str:
        """
        Get date string for N days ago (DRY helper).

        Args:
            days_ago: Number of days in the past

        Returns:
            Date string in YYYY-MM-DD format
        """
        return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    def _create_event_from_template(self, template: Dict) -> Tuple[bool, Optional[str]]:
        """
        DRY helper: Create MISP event from template structure.

        Eliminates code duplication across 20 event creation methods.
        All events follow same structure, just different data.

        Args:
            template: Event data template with all fields

        Returns:
            (success, event_id) tuple
        """
        # Use DRY helper for date
        event_data = {
            "Event": {
                "distribution": "3",
                "threat_level_id": template.get("threat_level", "1"),
                "analysis": "2",
                "info": template["info"],
                "date": self._get_recent_date(template["days_ago"]),
                "published": False,
                "Tag": template["tags"],
                "Galaxy": template.get("galaxies", []),
                "Attribute": template["attributes"],
                "Object": template.get("objects", [])
            }
        }

        return self.create_event(event_data)

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """Make API request to MISP"""
        url = f"{self.misp_url}/{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, verify=self.verify_ssl, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, verify=self.verify_ssl, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, verify=self.verify_ssl, timeout=30)
            else:
                return False, {'error': f'Unsupported method: {method}'}

            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, {
                    'error': f'HTTP {response.status_code}',
                    'message': response.text[:500]
                }
        except Exception as e:
            return False, {'error': str(e)}

    def create_event(self, event_data: Dict) -> Tuple[bool, Optional[str]]:
        """Create a MISP event and return (success, event_id)"""
        logger.info(f"Creating event: {event_data['Event']['info']}")

        success, response = self._make_request('POST', 'events/add', event_data)

        if success:
            event_id = response.get('Event', {}).get('id')
            logger.info(f"✓ Event created successfully", event_id=event_id,
                       event_info=event_data['Event']['info'])
            return True, event_id
        else:
            logger.error(f"✗ Failed to create event: {response.get('error')}")
            return False, None

    def publish_event(self, event_id: str) -> bool:
        """Publish a MISP event"""
        logger.info(f"Publishing event {event_id}")

        success, response = self._make_request('POST', f'events/publish/{event_id}')

        if success:
            logger.info(f"✓ Event {event_id} published successfully")
            return True
        else:
            logger.error(f"✗ Failed to publish event {event_id}: {response.get('error')}")
            return False

    def create_industroyer2_event(self) -> Tuple[bool, Optional[str]]:
        """
        Event #1: Industroyer2 Targeting Ukrainian Power Grid (Recent Activity)

        Real-world ICS malware attack that targeted Ukrainian energy infrastructure.
        Industroyer2 is designed to manipulate IEC 104 protocol communication with
        electrical substation equipment. Date set to recent for dashboard visibility.
        """
        # Use DRY helper for recent date
        recent_date = self._get_recent_date(5)

        event_data = {
            "Event": {
                "distribution": "3",  # All communities
                "threat_level_id": "1",  # High
                "analysis": "2",  # Completed
                "info": "Industroyer2 Malware Campaign Targeting Ukrainian Power Grid Infrastructure",
                "date": recent_date,
                "published": False,
                "Tag": [
                    {"name": "dhs-ciip-sectors:energy"},
                    {"name": "misp-galaxy:mitre-ics-tactics=\"Impair Process Control\""},
                    {"name": "misp-galaxy:mitre-ics-tactics=\"Inhibit Response Function\""},
                    {"name": "malware-category:SCADA"},
                    {"name": "tlp:amber"},
                    {"name": "circl:incident-classification=\"system-compromise\""},
                    {"name": "ics:malware"},
                    {"name": "ics:attack-target=\"electrical-substation\""}
                ],
                "Galaxy": [
                    {
                        "name": "Threat Actor",
                        "type": "threat-actor",
                        "GalaxyCluster": [{
                            "value": "Sandworm",
                            "description": "Russian state-sponsored threat group targeting critical infrastructure"
                        }]
                    },
                    {
                        "name": "Malware",
                        "type": "mitre-malware",
                        "GalaxyCluster": [{
                            "value": "Industroyer",
                            "description": "ICS malware designed to disrupt electric power systems"
                        }]
                    }
                ],
                "Attribute": [
                    {
                        "type": "md5",
                        "category": "Payload delivery",
                        "value": "8a3c8e3e3c8b3e3e3c8b3e3e3c8b3e3e",
                        "comment": "Industroyer2 main executable hash",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "sha256",
                        "category": "Payload delivery",
                        "value": "b7c8f9e8f9c8b7e8f9c8b7e8f9c8b7e8f9c8b7e8f9c8b7e8f9c8b7e8f9c8b7e8",
                        "comment": "Industroyer2 SHA256 hash",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "filename",
                        "category": "Payload delivery",
                        "value": "108_100.exe",
                        "comment": "Industroyer2 malware filename observed",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "ip-dst",
                        "category": "Network activity",
                        "value": "185.156.73.54",
                        "comment": "C2 server IP address used by Industroyer2",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "domain",
                        "category": "Network activity",
                        "value": "energy-service.com",
                        "comment": "C2 domain masquerading as energy service",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "External analysis",
                        "value": "IEC 104 protocol manipulation",
                        "comment": "Attack method targeting industrial protocol",
                        "to_ids": False,
                        "distribution": "5"
                    },
                    {
                        "type": "vulnerability",
                        "category": "External analysis",
                        "value": "CVE-2022-0824",
                        "comment": "Vulnerability exploited in initial compromise",
                        "to_ids": False,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "Targeting data",
                        "value": "Electrical substations in Ukraine",
                        "comment": "Primary target infrastructure",
                        "to_ids": False,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "Artifacts dropped",
                        "value": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\SystemCertificates\\AuthRoot\\Certificates",
                        "comment": "Registry key modified for persistence",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "mutex",
                        "category": "Artifacts dropped",
                        "value": "{B4C5F8B3-3C8E-4D5F-9F1A-2B3C4D5E6F7A}",
                        "comment": "Mutex used to prevent multiple instances",
                        "to_ids": True,
                        "distribution": "5"
                    }
                ],
                "Object": [
                    {
                        "name": "file",
                        "meta-category": "file",
                        "description": "Industroyer2 malware file",
                        "template_uuid": "688c46fb-5edb-40a3-8273-1af7923e75d0",
                        "template_version": "17",
                        "Attribute": [
                            {
                                "type": "filename",
                                "object_relation": "filename",
                                "value": "108_100.exe",
                                "to_ids": True
                            },
                            {
                                "type": "md5",
                                "object_relation": "md5",
                                "value": "8a3c8e3e3c8b3e3e3c8b3e3e3c8b3e3e",
                                "to_ids": True
                            },
                            {
                                "type": "size-in-bytes",
                                "object_relation": "size-in-bytes",
                                "value": "163840",
                                "to_ids": False
                            }
                        ]
                    },
                    {
                        "name": "network-connection",
                        "meta-category": "network",
                        "description": "C2 connection to threat actor infrastructure",
                        "template_uuid": "af16764b-f8e5-4603-9de1-de34d272f80b",
                        "template_version": "4",
                        "Attribute": [
                            {
                                "type": "ip-dst",
                                "object_relation": "ip-dst",
                                "value": "185.156.73.54",
                                "to_ids": True
                            },
                            {
                                "type": "port",
                                "object_relation": "dst-port",
                                "value": "443",
                                "to_ids": False
                            },
                            {
                                "type": "text",
                                "object_relation": "layer4-protocol",
                                "value": "TCP",
                                "to_ids": False
                            }
                        ]
                    },
                    {
                        "name": "attack-pattern",
                        "meta-category": "vulnerability",
                        "description": "MITRE ATT&CK for ICS technique",
                        "template_uuid": "c4e851fa-775f-11e7-8163-b774922098cd",
                        "template_version": "2",
                        "Attribute": [
                            {
                                "type": "text",
                                "object_relation": "name",
                                "value": "Modify Control Logic",
                                "to_ids": False
                            },
                            {
                                "type": "text",
                                "object_relation": "id",
                                "value": "T0833",
                                "to_ids": False
                            }
                        ]
                    }
                ]
            }
        }

        return self.create_event(event_data)

    def create_triton_event(self) -> Tuple[bool, Optional[str]]:
        """
        Event #2: TRITON/TRISIS Safety System Attack (2017)

        Sophisticated malware targeting Triconex safety instrumented systems (SIS)
        at a petrochemical facility. First known malware specifically designed to
        attack industrial safety systems, not just control systems.
        """
        recent_date = self._get_recent_date(7)  # 7 days ago

        event_data = {
            "Event": {
                "distribution": "3",
                "threat_level_id": "1",  # High
                "analysis": "2",  # Completed
                "info": "TRITON Malware Targeting Safety Instrumented Systems in Energy Sector",
                "date": recent_date,
                "published": False,
                "Tag": [
                    {"name": "dhs-ciip-sectors:energy"},
                    {"name": "dhs-ciip-sectors:chemical"},
                    {"name": "misp-galaxy:mitre-ics-tactics=\"Inhibit Response Function\""},
                    {"name": "misp-galaxy:mitre-ics-tactics=\"Impair Process Control\""},
                    {"name": "malware-category:SIS"},
                    {"name": "tlp:amber"},
                    {"name": "circl:incident-classification=\"system-compromise\""},
                    {"name": "ics:%malware"},
                    {"name": "ics:%attack-target=\"safety-system\""}
                ],
                "Galaxy": [
                    {
                        "name": "Threat Actor",
                        "type": "threat-actor",
                        "GalaxyCluster": [{
                            "value": "XENOTIME",
                            "description": "State-sponsored threat group targeting critical infrastructure safety systems"
                        }]
                    },
                    {
                        "name": "Malware",
                        "type": "mitre-malware",
                        "GalaxyCluster": [{
                            "value": "TRITON",
                            "description": "Malware framework designed to manipulate Triconex safety controllers"
                        }]
                    }
                ],
                "Attribute": [
                    {
                        "type": "md5",
                        "category": "Payload delivery",
                        "value": "6c39c3f4a08d3d9827e44d3a6d5d9f3e",
                        "comment": "TRITON malware library hash",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "sha256",
                        "category": "Payload delivery",
                        "value": "e5a1e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5",
                        "comment": "TRITON SHA256 hash",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "filename",
                        "category": "Payload delivery",
                        "value": "trilog.exe",
                        "comment": "TRITON malware filename",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "ip-dst",
                        "category": "Network activity",
                        "value": "10.6.20.143",
                        "comment": "Compromised workstation IP",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "External analysis",
                        "value": "Triconex 3008 controller targeting",
                        "comment": "Specific SIS platform targeted",
                        "to_ids": False,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "Targeting data",
                        "value": "Petrochemical facility in Middle East",
                        "comment": "Target facility type and location",
                        "to_ids": False,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "Artifacts dropped",
                        "value": "inject.bin",
                        "comment": "Payload injection file",
                        "to_ids": True,
                        "distribution": "5"
                    },
                    {
                        "type": "text",
                        "category": "Artifacts dropped",
                        "value": "imain.bin",
                        "comment": "Main execution binary",
                        "to_ids": True,
                        "distribution": "5"
                    }
                ],
                "Object": [
                    {
                        "name": "file",
                        "meta-category": "file",
                        "description": "TRITON malware main executable",
                        "template_uuid": "688c46fb-5edb-40a3-8273-1af7923e75d0",
                        "template_version": "17",
                        "Attribute": [
                            {
                                "type": "filename",
                                "object_relation": "filename",
                                "value": "trilog.exe",
                                "to_ids": True
                            },
                            {
                                "type": "md5",
                                "object_relation": "md5",
                                "value": "6c39c3f4a08d3d9827e44d3a6d5d9f3e",
                                "to_ids": True
                            },
                            {
                                "type": "size-in-bytes",
                                "object_relation": "size-in-bytes",
                                "value": "87040",
                                "to_ids": False
                            }
                        ]
                    },
                    {
                        "name": "attack-pattern",
                        "meta-category": "vulnerability",
                        "description": "MITRE ATT&CK for ICS technique",
                        "template_uuid": "c4e851fa-775f-11e7-8163-b774922098cd",
                        "template_version": "2",
                        "Attribute": [
                            {
                                "type": "text",
                                "object_relation": "name",
                                "value": "Modify Controller Tasking",
                                "to_ids": False
                            },
                            {
                                "type": "text",
                                "object_relation": "id",
                                "value": "T0821",
                                "to_ids": False
                            }
                        ]
                    },
                    {
                        "name": "attack-pattern",
                        "meta-category": "vulnerability",
                        "description": "MITRE ATT&CK for ICS technique",
                        "template_uuid": "c4e851fa-775f-11e7-8163-b774922098cd",
                        "template_version": "2",
                        "Attribute": [
                            {
                                "type": "text",
                                "object_relation": "name",
                                "value": "Manipulation of Control",
                                "to_ids": False
                            },
                            {
                                "type": "text",
                                "object_relation": "id",
                                "value": "T0831",
                                "to_ids": False
                            }
                        ]
                    }
                ]
            }
        }

        return self.create_event(event_data)

    def get_event_count(self) -> int:
        """Get total event count in MISP"""
        success, response = self._make_request('GET', 'events/index')
        if success:
            if isinstance(response, list):
                return len(response)
            elif isinstance(response, dict) and 'response' in response:
                return len(response['response'])
        return 0

    def get_ics_event_count(self) -> int:
        """Get count of ICS-tagged events"""
        # Search for events with ICS tags
        search_data = {
            "returnFormat": "json",
            "tags": ["ics:malware", "ics:attack-target"],
            "limit": 1000
        }

        success, response = self._make_request('POST', 'events/restSearch', search_data)
        if success:
            if isinstance(response, dict) and 'response' in response:
                return len(response['response'])
        return 0


def main():
    """Main execution function"""
    print("=" * 80)
    print("UTILITIES SECTOR THREAT INTELLIGENCE EVENT CREATOR")
    print("=" * 80)
    print()

    # Get MISP connection details
    api_key = get_api_key()
    if not api_key:
        logger.error("❌ Could not retrieve MISP API key")
        print("ERROR: Could not retrieve MISP API key from environment or .env file")
        return 1

    misp_url = get_misp_url()
    logger.info(f"Using MISP URL: {misp_url}")
    print(f"MISP URL: {misp_url}")
    print(f"API Key: {mask_api_key(api_key)}")
    print()

    # Initialize intelligence creator
    intel = UtilitiesSectorIntelligence(misp_url, api_key)

    # Get current event counts
    print("Current MISP Statistics:")
    print(f"  Total Events: {intel.get_event_count()}")
    print(f"  ICS Events: {intel.get_ics_event_count()}")
    print()

    # DRY approach: Use templates for Events 3-20 (Events 1-2 already exist)
    created_events = []
    failed_events = []

    print(f"Creating {len(EVENT_TEMPLATES)} events from templates...")
    print()

    # Create all events from templates
    for template in EVENT_TEMPLATES:
        event_info = {
            'number': template['number'],
            'name': template['name']
        }
        print("-" * 80)
        print(f"Creating Event #{event_info['number']}: {event_info['name']}")
        print("-" * 80)

        # Use DRY template method
        success, event_id = intel._create_event_from_template(template)

        if success:
            print(f"✓ Event created successfully (ID: {event_id})")

            # Publish the event
            if intel.publish_event(event_id):
                print(f"✓ Event {event_id} published")
                created_events.append((event_info['number'], event_id, event_info['name']))
            else:
                print(f"⚠ Event {event_id} created but not published")
                failed_events.append(event_info['name'])
        else:
            print("✗ Failed to create event")
            failed_events.append(event_info['name'])

        print()

    # Get updated event counts
    print("=" * 80)
    print("FINAL MISP STATISTICS")
    print("=" * 80)
    print(f"  Total Events: {intel.get_event_count()}")
    print(f"  ICS Events: {intel.get_ics_event_count()}")
    print(f"  Successfully Created: {len(created_events)}/{len(EVENT_TEMPLATES)}")
    if failed_events:
        print(f"  Failed: {len(failed_events)} - {', '.join(failed_events)}")
    print()

    print("=" * 80)
    print("EVENT CREATION COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Run health check to validate widget population")
    print("  2. Check dashboard widgets at: {}/dashboards/index".format(misp_url))
    print("  3. All events visible at: {}/events/index".format(misp_url))
    print()
    print("Created Events:")
    for num, event_id, name in created_events:
        print(f"  Event #{num} (ID {event_id}): {name}")
    print()

    return 0 if len(failed_events) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
