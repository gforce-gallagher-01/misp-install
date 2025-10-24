## Task 3.6: Document ICS Monitoring Tool Integration

**CIP Standard**: CIP-015 R1 (BES Cyber System Categorization - Internal Network Monitoring)
**Estimated Time**: 5-6 hours
**Priority**: MEDIUM

### Research Objectives

1. Identify ICS network monitoring tools (Dragos, Claroty, Nozomi, Armis, etc.)
2. Research ICS alert types and threat detection capabilities
3. Define MISP integration for ICS threat intelligence
4. Document bidirectional data flow (MISP → ICS tool, ICS tool → MISP)

### Deliverables

#### 1. ICS Monitoring Platform Assessment

**Template**: Copy and complete this assessment

```markdown
# ICS Monitoring Platform Assessment

## Current ICS Monitoring Tools

**Do we have dedicated ICS/OT network monitoring?**: [ ] Yes  [ ] No  [ ] Planned

**If yes, which vendor?**:
- [ ] Dragos Platform
- [ ] Claroty CTD (Continuous Threat Detection)
- [ ] Nozomi Networks Guardian
- [ ] Armis (Agentless Device Security)
- [ ] Forescout
- [ ] Tenable.ot (formerly Indegy)
- [ ] Other: _______________________________

**Platform Administrator**: _______________________________

## Deployment Architecture

**Monitoring method**:
- [ ] Passive network TAP (monitor-only, no inline)
- [ ] SPAN/mirror port on switch
- [ ] Agent-based (installed on systems)
- [ ] Hybrid (TAP + agents)

**Monitored networks**:
- [ ] Substation SCADA networks
- [ ] Control center networks
- [ ] Engineering/maintenance networks
- [ ] Corporate-to-OT DMZ

**Number of monitored assets**: _______ ICS devices

## Threat Detection Capabilities

**What does ICS monitoring tool detect?**:
- [ ] Unauthorized devices on ICS network
- [ ] Malware/anomalous behavior
- [ ] Configuration changes on PLCs/RTUs
- [ ] Unauthorized remote access
- [ ] Abnormal ICS protocol traffic (Modbus, DNP3, IEC 61850)
- [ ] Vulnerability scanning against ICS devices
- [ ] Firmware version tracking

**Alert volume**: _______ alerts per day (average)

## Integration Capabilities

**Does ICS monitoring tool have MISP integration?**: [ ] Yes  [ ] No  [ ] Unknown

**If yes, integration type**:
- [ ] Bi-directional (MISP ↔ ICS tool)
- [ ] ICS tool → MISP (send alerts to MISP)
- [ ] MISP → ICS tool (import IOCs from MISP)

**API access available?**: [ ] Yes  [ ] No

**Supported export formats**:
- [ ] STIX/TAXII
- [ ] JSON
- [ ] CSV
- [ ] Syslog
- [ ] SNMP traps
```

#### 2. ICS Threat Intelligence Sharing Design

Document how MISP and ICS monitoring tool will exchange data:

```markdown
# MISP ↔ ICS Monitoring Tool Integration

## Data Flow 1: MISP → ICS Tool (Threat Intelligence Import)

**Use Case**: Share ICS-specific IOCs from MISP to ICS monitoring tool

**IOCs to Share**:
- Known ICS malware hashes (TRISIS, INDUSTROYER, PIPEDREAM, etc.)
- Malicious ICS protocol commands (e.g., DNP3 Direct Operate, Modbus Force Coil)
- Known attack tools (NMAP, Metasploit, ICS exploitation frameworks)
- Suspicious asset names (e.g., "SHODAN-SCANNER", "KALI-LINUX")

**Integration Method**:

### Option 1: STIX/TAXII (If ICS tool supports it)

Many ICS monitoring tools support STIX/TAXII for threat intel exchange:

- **Dragos Platform**: Supports TAXII 2.0/2.1
- **Claroty CTD**: Supports STIX import
- **Nozomi Networks**: Supports TAXII feed subscription

**MISP TAXII Server Configuration**:
```
MISP → Sync Actions → TAXII Servers → Add TAXII Server

Server URL: https://ics-monitoring-tool.company.local/taxii2/
Authentication: [API key or username/password]
Collection: ICS-Threat-Intelligence

Export settings:
- Only export events tagged with: `ics`, `cip-015`, `sector:energy`
- Publish to TAXII: Every 1 hour
```

### Option 2: Custom PyMISP Script

If ICS tool has REST API but no STIX support:

```python
#!/usr/bin/env python3
"""
Export ICS-specific IOCs from MISP to ICS monitoring tool
"""
from pymisp import PyMISP
import requests

# MISP connection
misp = PyMISP('https://misp-test.lan', 'API_KEY', ssl=False)

# Query MISP for ICS-related IOCs
search_params = {
    'published': True,
    'tags': ['ics', 'sector:energy', 'misp-galaxy:mitre-ics-tactics'],
    'type_attribute': ['md5', 'sha256', 'ip-dst', 'domain'],
    'to_ids': True
}

results = misp.search('attributes', **search_params)

# Convert to ICS tool API format (example for Dragos)
dragos_indicators = []
for attr in results['Attribute']:
    dragos_indicators.append({
        'type': attr['type'],
        'value': attr['value'],
        'context': attr.get('comment', ''),
        'source': 'MISP',
        'confidence': 'high'
    })

# Push to ICS monitoring tool via API
response = requests.post(
    'https://ics-tool.company.local/api/v1/indicators',
    json={'indicators': dragos_indicators},
    headers={'Authorization': 'Bearer ICS_TOOL_API_KEY'}
)

print(f"Exported {len(dragos_indicators)} ICS IOCs to monitoring tool")
```

**Deployment**: Run every hour via cron

## Data Flow 2: ICS Tool → MISP (Alert Import)

**Use Case**: Create MISP events for critical ICS alerts

**Alerts to Import**:
- Malware detected on ICS device
- Unauthorized device on ICS network
- Suspicious ICS protocol commands
- Firmware change on PLC/RTU
- Unauthorized remote access to HMI

**Integration Method**:

### Option 1: Syslog → MISP

ICS monitoring tool sends syslog to MISP server:

1. Configure ICS tool to send high-severity alerts via syslog to MISP server
2. MISP server runs syslog listener script
3. Script parses alert and creates MISP event via API

```python
#!/usr/bin/env python3
"""
Parse ICS monitoring tool syslog and create MISP events
"""
import socketserver
from pymisp import PyMISP, MISPEvent
import json
import re

misp = PyMISP('https://misp-test.lan', 'API_KEY', ssl=False)

class SyslogHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip())

        # Parse syslog message (example format)
        # <134>Oct 24 15:30:00 dragos-platform: CRITICAL: Malware detected on device PLC-ALPHA-01 (IP: 192.168.10.20) - Hash: 5d41402abc4b2a76b9719d911017c592

        if 'CRITICAL' in data:
            # Create MISP event
            event = MISPEvent()
            event.info = f"ICS Alert: {data}"
            event.distribution = 0  # Your organization only
            event.threat_level_id = 1  # High
            event.analysis = 0  # Initial

            # Add tags
            event.add_tag('cip-015:internal-monitoring')
            event.add_tag('tlp:amber')
            event.add_tag('sector:energy')

            # Extract IOCs from syslog message
            ip_match = re.search(r'IP:\s+(\d+\.\d+\.\d+\.\d+)', data)
            if ip_match:
                event.add_attribute('ip-dst', ip_match.group(1), comment='Affected ICS device')

            hash_match = re.search(r'Hash:\s+([0-9a-f]{32})', data)
            if hash_match:
                event.add_attribute('md5', hash_match.group(1), comment='Malware hash', to_ids=True)

            # Publish event to MISP
            misp.add_event(event, pythonify=True)
            print(f"Created MISP event from ICS alert")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 514
    server = socketserver.UDPServer((HOST, PORT), SyslogHandler)
    print(f"Listening for ICS alerts on UDP {PORT}")
    server.serve_forever()
```

### Option 2: API Polling

MISP polls ICS monitoring tool API for new alerts:

```python
#!/usr/bin/env python3
"""
Poll ICS monitoring tool API and create MISP events for new alerts
"""
import requests
from pymisp import PyMISP, MISPEvent
from datetime import datetime, timedelta

misp = PyMISP('https://misp-test.lan', 'API_KEY', ssl=False)

# Query ICS tool for alerts from last hour
last_hour = (datetime.now() - timedelta(hours=1)).isoformat()
response = requests.get(
    'https://ics-tool.company.local/api/v1/alerts',
    params={'severity': 'critical', 'since': last_hour},
    headers={'Authorization': 'Bearer ICS_TOOL_API_KEY'}
)

alerts = response.json()

for alert in alerts:
    # Create MISP event for each critical alert
    event = MISPEvent()
    event.info = f"ICS Alert: {alert['title']}"
    event.add_attribute('text', alert['description'], category='Other')
    event.add_attribute('ip-dst', alert['source_ip'], comment='Affected device')
    event.add_tag('cip-015:internal-monitoring')

    misp.add_event(event, pythonify=True)

print(f"Imported {len(alerts)} ICS alerts to MISP")
```

**Deployment**: Run every 15 minutes via cron

## ICS Threat Intelligence Use Cases

### Use Case 1: Known ICS Malware Detection

**Scenario**: E-ISAC publishes alert about new ICS malware (e.g., "INDUSTROYER3")

**Workflow**:
1. Security analyst creates MISP event with INDUSTROYER3 IOCs:
   - Malware hashes
   - C2 domains
   - ICS protocol signatures
2. MISP exports IOCs to ICS monitoring tool (via STIX/API)
3. ICS monitoring tool updates detection signatures
4. If INDUSTROYER3 detected, ICS tool creates alert
5. Alert imported to MISP as new incident event
6. Incident response playbook triggered (Task 3.4)

### Use Case 2: ICS Vulnerability Exploitation Detection

**Scenario**: ICS vendor publishes patch for critical vulnerability (tracked in MISP per Task 3.2)

**Workflow**:
1. MISP event contains vulnerability details:
   - CVE-2024-12345 in Siemens SIMATIC
   - Exploitation via Modbus TCP port 502
2. ICS monitoring tool imports vulnerability context from MISP
3. ICS monitoring tool creates detection rule:
   - Monitor Modbus traffic to affected PLCs
   - Alert on suspicious commands matching exploit pattern
4. If exploitation attempt detected, alert sent to MISP
5. MISP links alert to original vulnerability event
6. Compliance team has audit trail: Vulnerability published → Patch tracked → Exploitation attempt detected and blocked

### Use Case 3: Insider Threat Detection

**Scenario**: ICS monitoring tool detects unusual configuration change on PLC

**Workflow**:
1. ICS tool alert: "PLC-ALPHA-01 logic modified from unauthorized workstation (IP: 192.168.10.99)"
2. Alert imported to MISP as security event
3. MISP enrichment:
   - Query asset inventory: Who owns 192.168.10.99?
   - Query user database: Was this user authorized to modify PLC?
   - Query SIEM: Any other suspicious activity from this user?
4. If insider threat confirmed, escalate to incident response
5. CIP-004 R3 compliance: Personnel access revoked, documented in MISP
```

---

