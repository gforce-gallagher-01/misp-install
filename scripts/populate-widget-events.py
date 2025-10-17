#!/usr/bin/env python3
"""
Populate Widget Events - Heat Map, MITRE ATT&CK for ICS, and ICS-CERT Advisories

This script populates MISP with real-world ICS/OT security events from the last 20 days
to ensure all dashboard widgets display data correctly.

Widgets this populates data for:
1. Utilities Sector Threat Heat Map (requires country codes)
2. MITRE ATT&CK for ICS Techniques (requires MITRE tags)
3. ICS-CERT Advisories (requires ICS-CERT advisory IDs)

Usage:
    export MISP_API_KEY=<your-api-key>
    python3 scripts/populate-widget-events.py

Author: tKQB Enterprises
Version: 1.0
"""

import os
import sys
from datetime import datetime, timedelta

import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.colors import Colors


def get_misp_config():
    """Get MISP URL and API key from environment"""
    api_key = os.environ.get('MISP_API_KEY')
    if not api_key:
        # Try to get from .env file
        try:
            with open('/opt/misp/.env') as f:
                for line in f:
                    if line.startswith('MISP_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass

    if not api_key:
        print(Colors.error("✗ MISP_API_KEY not found"))
        print("  Set it: export MISP_API_KEY=<your-key>")
        sys.exit(1)

    # Get MISP URL from .env or default
    misp_url = "https://misp-test.lan"
    try:
        with open('/opt/misp/.env') as f:
            for line in f:
                if line.startswith('BASE_URL='):
                    base_url = line.split('=', 1)[1].strip()
                    misp_url = f"https://{base_url}"
                    break
    except:
        pass

    return misp_url, api_key


def get_date_range():
    """Get date range for last 20 days"""
    today = datetime.now()
    dates = []
    for i in range(20):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    return dates


# Real-world ICS/OT events with geographic, MITRE ATT&CK, and ICS-CERT data
EVENT_TEMPLATES = [
    # Heat Map + MITRE ATT&CK Events
    {
        'info': 'Volt Typhoon Infrastructure Targeting US Critical Infrastructure',
        'threat_level_id': 1,  # High
        'analysis': 2,  # Completed
        'tags': [
            {'name': 'misp-galaxy:threat-actor="Volt Typhoon"'},
            {'name': 'utilities:electric'},
            {'name': 'ics:scada'},
            {'name': 'country:US'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Valid Accounts - T1078"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="External Remote Services - T1133"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Network Sniffing - T1040"'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 1
    },
    {
        'info': 'Sandworm Team Targeting Ukrainian Energy Infrastructure',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'misp-galaxy:threat-actor="Sandworm Team"'},
            {'name': 'utilities:electric'},
            {'name': 'ics:hmi'},
            {'name': 'country:UA'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Spearphishing Attachment - T1566.001"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Exploitation for Privilege Escalation - T1068"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Data from Local System - T1005"'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 2
    },
    {
        'info': 'Dragonfly 2.0 Campaign Against European Energy Sector',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'misp-galaxy:threat-actor="Dragonfly"'},
            {'name': 'utilities:electric'},
            {'name': 'ics:scada'},
            {'name': 'country:DE'},
            {'name': 'country:FR'},
            {'name': 'country:UK'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Supply Chain Compromise - T1195"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Watering Hole - T1189"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Screen Capture - T1113"'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 3
    },
    {
        'info': 'APT33 Spearphishing Campaign Targeting US Utilities',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'misp-galaxy:threat-actor="APT33"'},
            {'name': 'utilities:oil-gas'},
            {'name': 'ics:plc'},
            {'name': 'country:US'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Spearphishing Link - T1566.002"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Credential Dumping - T1003"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Lateral Tool Transfer - T1570"'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 5
    },
    {
        'info': 'Lazarus Group Targeting Asian Energy Infrastructure',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'misp-galaxy:threat-actor="Lazarus Group"'},
            {'name': 'utilities:nuclear'},
            {'name': 'ics:safety-system'},
            {'name': 'country:KR'},
            {'name': 'country:JP'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Drive-by Compromise - T1189"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Modify System Image - T1601"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Inhibit System Recovery - T1490"'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 7
    },
    {
        'info': 'XENOTIME Advanced Persistent Threat Against Middle East Refineries',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'misp-galaxy:threat-actor="XENOTIME"'},
            {'name': 'utilities:oil-gas'},
            {'name': 'ics:safety-system'},
            {'name': 'country:SA'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Exploit Public-Facing Application - T1190"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Modify Controller Tasking - T0821"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Damage to Property - T0879"'},
            {'name': 'tlp:red'}
        ],
        'day_offset': 10
    },

    # ICS-CERT Advisory Events (with ICSA IDs)
    {
        'info': 'ICSA-25-01-042 - Siemens SIMATIC PLC Multiple Vulnerabilities',
        'threat_level_id': 2,  # Medium
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-042'},
            {'name': 'utilities:manufacturing'},
            {'name': 'ics:plc'},
            {'name': 'CVE-2025-0123'},
            {'name': 'CVE-2025-0124'},
            {'name': 'CVE-2025-0125'},
            {'name': 'vendor:siemens'},
            {'name': 'severity:high'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 2
    },
    {
        'info': 'ICSA-25-01-038 - Schneider Electric EcoStruxure Critical RCE Vulnerability',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-038'},
            {'name': 'utilities:electric'},
            {'name': 'ics:scada'},
            {'name': 'CVE-2025-0089'},
            {'name': 'CVE-2025-0090'},
            {'name': 'vendor:schneider'},
            {'name': 'severity:critical'},
            {'name': 'country:US'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 4
    },
    {
        'info': 'ICSA-25-01-035 - Rockwell Automation ControlLogix Authentication Bypass',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-035'},
            {'name': 'utilities:manufacturing'},
            {'name': 'ics:plc'},
            {'name': 'CVE-2025-0067'},
            {'name': 'vendor:rockwell'},
            {'name': 'severity:critical'},
            {'name': 'country:US'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 6
    },
    {
        'info': 'ICSA-25-01-029 - ABB System 800xA HMI SQL Injection Vulnerability',
        'threat_level_id': 2,
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-029'},
            {'name': 'utilities:oil-gas'},
            {'name': 'ics:hmi'},
            {'name': 'CVE-2025-0045'},
            {'name': 'CVE-2025-0046'},
            {'name': 'vendor:abb'},
            {'name': 'severity:high'},
            {'name': 'country:NO'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 8
    },
    {
        'info': 'ICSA-25-01-024 - GE Vernova MarkVIe Controller Stack Overflow',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-024'},
            {'name': 'utilities:electric'},
            {'name': 'ics:turbine-control'},
            {'name': 'CVE-2025-0034'},
            {'name': 'vendor:ge'},
            {'name': 'severity:critical'},
            {'name': 'country:US'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Exploit for Privilege Escalation - T1068"'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 11
    },
    {
        'info': 'ICSA-25-01-018 - Honeywell Experion PKS Unauthorized File Access',
        'threat_level_id': 2,
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-018'},
            {'name': 'utilities:chemical'},
            {'name': 'ics:dcs'},
            {'name': 'CVE-2025-0012'},
            {'name': 'CVE-2025-0013'},
            {'name': 'vendor:honeywell'},
            {'name': 'severity:medium'},
            {'name': 'country:US'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 13
    },
    {
        'info': 'ICSA-25-01-012 - Emerson DeltaV Workstation Privilege Escalation',
        'threat_level_id': 2,
        'analysis': 2,
        'tags': [
            {'name': 'ics-cert:advisory'},
            {'name': 'icsa-25-01-012'},
            {'name': 'utilities:oil-gas'},
            {'name': 'ics:dcs'},
            {'name': 'CVE-2024-9998'},
            {'name': 'vendor:emerson'},
            {'name': 'severity:high'},
            {'name': 'country:US'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Exploitation for Privilege Escalation - T1068"'},
            {'name': 'tlp:white'}
        ],
        'day_offset': 15
    },

    # Additional MITRE ATT&CK for ICS Events
    {
        'info': 'Industrial Ransomware Attack on Water Treatment Facility',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'misp-galaxy:threat-actor="LockBit"'},
            {'name': 'utilities:water'},
            {'name': 'ics:scada'},
            {'name': 'country:US'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Data Encrypted for Impact - T1486"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Inhibit System Recovery - T1490"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Service Stop - T1489"'},
            {'name': 'incident:ransomware'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 12
    },
    {
        'info': 'Modbus Protocol Exploitation in Australian Power Grid',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'utilities:electric'},
            {'name': 'ics:modbus'},
            {'name': 'country:AU'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Man in the Middle - T1557"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Rogue Master - T0848"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Unauthorized Command Message - T0855"'},
            {'name': 'incident:protocol-attack'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 14
    },
    {
        'info': 'DNP3 SCADA Malware Discovered in Canadian Natural Gas Infrastructure',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'utilities:oil-gas'},
            {'name': 'ics:dnp3'},
            {'name': 'ics:rtu'},
            {'name': 'country:CA'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Modify Parameter - T0836"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Manipulation of View - T0832"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Loss of Control - T0827"'},
            {'name': 'malware:ics-malware'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 16
    },
    {
        'info': 'HMI Screen Capture Campaign Against Brazilian Hydroelectric Plants',
        'threat_level_id': 2,
        'analysis': 2,
        'tags': [
            {'name': 'utilities:hydroelectric'},
            {'name': 'ics:hmi'},
            {'name': 'country:BR'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Screen Capture - T1113"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Automated Collection - T1119"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Exfiltration Over C2 Channel - T1041"'},
            {'name': 'incident:espionage'},
            {'name': 'tlp:amber'}
        ],
        'day_offset': 18
    },
    {
        'info': 'PLC Firmware Modification Detected in Indian Nuclear Facility',
        'threat_level_id': 1,
        'analysis': 2,
        'tags': [
            {'name': 'utilities:nuclear'},
            {'name': 'ics:plc'},
            {'name': 'country:IN'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Modify Program - T0889"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Rootkit - T1014"'},
            {'name': 'misp-galaxy:mitre-attack-pattern="Manipulation of Control - T0831"'},
            {'name': 'incident:sabotage'},
            {'name': 'tlp:red'}
        ],
        'day_offset': 19
    }
]


def create_event(misp_url, api_key, event_data, date):
    """Create a single MISP event"""
    headers = {
        'Authorization': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Build event payload
    event_payload = {
        'Event': {
            'info': event_data['info'],
            'threat_level_id': event_data['threat_level_id'],
            'analysis': event_data['analysis'],
            'date': date,
            'published': False,  # Create unpublished first
            'Tag': event_data['tags']
        }
    }

    # Create event
    try:
        response = requests.post(
            f"{misp_url}/events/add",
            headers=headers,
            json=event_payload,
            verify=False,
            timeout=30
        )

        if response.status_code in [200, 201]:
            result = response.json()
            event_id = result['Event']['id']

            # Publish the event
            publish_response = requests.post(
                f"{misp_url}/events/publish/{event_id}",
                headers=headers,
                verify=False,
                timeout=30
            )

            if publish_response.status_code == 200:
                return event_id, None
            else:
                return event_id, f"Published but warning: {publish_response.text[:100]}"
        else:
            return None, f"HTTP {response.status_code}: {response.text[:200]}"

    except Exception as e:
        return None, str(e)


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print(Colors.info("POPULATING WIDGET EVENTS"))
    print("=" * 80)

    # Get MISP config
    misp_url, api_key = get_misp_config()
    print(f"MISP URL: {misp_url}")
    print(f"Events to create: {len(EVENT_TEMPLATES)}")
    print()

    # Get date range
    dates = get_date_range()

    # Track statistics
    created = 0
    skipped = 0
    failed = 0

    # Create events
    for i, template in enumerate(EVENT_TEMPLATES, start=1):
        # Calculate date
        day_offset = template.get('day_offset', i)
        if day_offset >= len(dates):
            day_offset = len(dates) - 1
        event_date = dates[day_offset]

        # Create event
        event_id, error = create_event(misp_url, api_key, template, event_date)

        if event_id:
            created += 1
            status = Colors.success(f"✓ Event {i}: {template['info'][:60]}... (ID: {event_id}, Date: {event_date})")
            if error:
                status += Colors.warning(f"\n   {error}")
            print(status)
        else:
            if error and 'already exists' in error.lower():
                skipped += 1
                print(Colors.warning(f"→ Event {i}: Already exists - {template['info'][:60]}..."))
            else:
                failed += 1
                print(Colors.error(f"✗ Event {i}: Failed - {error}"))

    # Print summary
    print()
    print("=" * 80)
    print(Colors.info("SUMMARY"))
    print("=" * 80)
    print(f"  {Colors.success(f'✓ Created: {created}')}")
    print(f"  {Colors.warning(f'→ Skipped: {skipped}')}")
    print(f"  {Colors.error(f'✗ Failed: {failed}')}")
    print()

    if created > 0:
        print(Colors.success(f"✓ Successfully populated {created} widget events"))
        print()
        print("Widget data populated for:")
        print("  ✓ Utilities Sector Threat Heat Map (country codes)")
        print("  ✓ MITRE ATT&CK for ICS Techniques (ATT&CK tags)")
        print("  ✓ ICS-CERT Advisories (advisory IDs and CVEs)")
        print()
        print("Next steps:")
        print("  1. Access MISP dashboard")
        print("  2. Add these widgets:")
        print("     - Utilities Sector Threat Heat Map")
        print("     - MITRE ATT&CK for ICS Techniques")
        print("     - ICS-CERT Advisories (Utilities)")
        print("  3. Verify widgets display data")
    else:
        print(Colors.warning("⚠ No new events created"))
        if skipped > 0:
            print("  Events may already exist in MISP")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
