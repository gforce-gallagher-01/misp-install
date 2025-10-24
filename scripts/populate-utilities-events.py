#!/usr/bin/env python3
"""
Populate MISP with 31 ICS/OT threat intelligence events for utilities sector.

This script creates demonstration events with proper threat-actor attribution
for use with the Threat Actor Dashboard widgets.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta

import requests
import urllib3

from lib.colors import Colors
from lib.misp_api_helpers import get_api_key, get_misp_url
from scripts.event_templates import ENHANCED_TAGS_BY_EVENT, EVENT_TEMPLATES

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_events():
    """Create all 31 ICS/OT events with threat-actor tags"""

    # Get API credentials
    api_key = get_api_key()
    misp_url = get_misp_url()

    if not api_key or not misp_url:
        print(Colors.error("✗ Could not get MISP API credentials"))
        return False

    headers = {
        'Authorization': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    print("\n" + "="*60)
    print(Colors.info("POPULATING ICS/OT THREAT INTELLIGENCE EVENTS"))
    print("="*60)
    print(f"MISP URL: {misp_url}")
    print(f"Events to create: {len(EVENT_TEMPLATES)}")
    print()

    created_count = 0
    skipped_count = 0
    failed_count = 0

    for template in EVENT_TEMPLATES:
        event_num = template['number']

        # Calculate event date (distributed over last 20 days)
        days_ago = template['days_ago']
        event_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

        # Get enhanced tags (includes threat-actor tags)
        enhanced_tags = ENHANCED_TAGS_BY_EVENT.get(event_num, template['tags'])

        # Build event payload (unpublished initially - MISP won't accept published empty events)
        event_payload = {
            "Event": {
                "info": template['info'],
                "threat_level_id": 2,  # Medium
                "analysis": 1,  # Initial
                "distribution": 3,  # All communities
                "date": event_date,
                "published": False,  # Create unpublished, then publish after adding attributes
                "Tag": enhanced_tags
            }
        }

        try:
            # Create event via API
            response = requests.post(
                f"{misp_url}/events/add",
                headers=headers,
                json=event_payload,
                verify=False,
                timeout=30
            )

            if response.status_code in [200, 201]:
                result = response.json()
                event_id = result.get('Event', {}).get('id', 'unknown')
                created_count += 1

                # Add attributes if specified
                if 'attributes' in template and template['attributes']:
                    for attr in template['attributes']:
                        attr_payload = {
                            "Attribute": {
                                **attr,
                                "event_id": event_id
                            }
                        }
                        requests.post(
                            f"{misp_url}/attributes/add/{event_id}",
                            headers=headers,
                            json=attr_payload,
                            verify=False,
                            timeout=10
                        )

                # Publish the event now that it has attributes/tags
                requests.post(
                    f"{misp_url}/events/publish/{event_id}",
                    headers=headers,
                    verify=False,
                    timeout=10
                )

                print(f"{Colors.success('✓')} Event {event_num}: {template['info'][:60]}... (ID: {event_id})")

            elif response.status_code == 403:
                print(f"{Colors.warning('⚠')} Event {event_num}: Permission denied (403)")
                failed_count += 1

            elif response.status_code == 400:
                # Might already exist
                print(f"{Colors.info('→')} Event {event_num}: Already exists or validation error")
                skipped_count += 1

            else:
                print(f"{Colors.error('✗')} Event {event_num}: Failed ({response.status_code})")
                failed_count += 1

        except Exception as e:
            print(f"{Colors.error('✗')} Event {event_num}: Error - {str(e)[:50]}")
            failed_count += 1

    print()
    print("="*60)
    print(Colors.info("SUMMARY"))
    print("="*60)
    print(f"  {Colors.success('✓')} Created: {created_count}")
    print(f"  {Colors.info('→')} Skipped: {skipped_count}")
    print(f"  {Colors.error('✗')} Failed: {failed_count}")
    print()

    if created_count > 0:
        print(Colors.success(f"✓ Successfully populated {created_count} ICS/OT threat intelligence events"))
        return True
    elif skipped_count > 0 and failed_count == 0:
        print(Colors.info("→ All events already exist"))
        return True
    else:
        print(Colors.error("✗ Event population failed"))
        return False


if __name__ == '__main__':
    success = create_events()
    sys.exit(0 if success else 1)
