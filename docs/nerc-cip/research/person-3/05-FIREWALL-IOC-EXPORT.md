## Task 3.5: Research Firewall IOC Export Integration

**CIP Standard**: CIP-005 R2 (Electronic Access Points - Malicious Communications)
**Estimated Time**: 4-5 hours
**Priority**: MEDIUM

### Research Objectives

1. Identify corporate firewall platform and management method
2. Research MISP IOC export capabilities (domains, IPs, URLs)
3. Define automated IOC blacklist updates for perimeter firewalls
4. Document firewall rule change control requirements

### Deliverables

#### 1. Firewall Platform Assessment

**Template**: Copy and complete this assessment

```markdown
# Firewall Platform Assessment

## Perimeter Firewall (Electronic Access Points)

**Firewall Vendor**: [ ] Palo Alto  [ ] Cisco  [ ] Fortinet  [ ] Checkpoint  [ ] Other: _______

**Firewall Model**: _______________________________

**Firewall Administrator**: _______________________________

**Number of Electronic Access Points (EAPs)**: _______ (CIP-005 R1)

## Firewall Management

**Management method**:
- [ ] Individual firewall CLI/GUI (manual)
- [ ] Centralized management platform (Panorama, FMC, FortiManager, etc.)
- [ ] Cloud-managed (Meraki, Prisma Access, etc.)

**Management platform version**: _______________________________

**API access available?**: [ ] Yes  [ ] No  [ ] Unknown

## Current Threat Intelligence Integration

**Does firewall currently consume threat intelligence feeds?**: [ ] Yes  [ ] No

**If yes, which feeds?**:
- [ ] Vendor-provided (Palo Alto Threat Prevention, Cisco Talos, etc.)
- [ ] Commercial threat intel (Recorded Future, ThreatConnect, etc.)
- [ ] Open-source feeds (AlienVault OTX, abuse.ch, etc.)
- [ ] Other: _______________________________

**Update frequency**: [ ] Real-time  [ ] Hourly  [ ] Daily  [ ] Manual

## IOC Blocking Capability

**Can firewall block based on IOC type?**:
- [ ] IP addresses (yes/no)
- [ ] Domain names (yes/no)
- [ ] URLs (yes/no)
- [ ] File hashes (yes/no - if firewall inspects files)

**Current block list size**: _______ entries

**Block list update method**:
- [ ] Manual rule creation
- [ ] API-based (automated)
- [ ] External Dynamic List (EDL) - recommended for MISP integration
- [ ] Other: _______________________________
```

#### 2. MISP IOC Export Configuration

Document how to export IOCs from MISP to firewall:

```markdown
# MISP to Firewall IOC Export

## Export Methods

### Method 1: MISP Feeds (Simplest)

MISP can generate feed files in multiple formats:

**Feed URL Example**:
```
https://misp-test.lan/feeds/view/[feed-id]
```

**Feed formats**:
- CSV (IP addresses, domains)
- JSON (full event data)
- STIX (standardized threat intel format)

**Firewall consumption**:
- Palo Alto: External Dynamic List (EDL) - supports text file with IP/domain per line
- Cisco Firepower: Security Intelligence feed - supports CSV
- Fortinet: Threat Feed - supports CSV

### Method 2: PyMISP Script (Most Flexible)

Python script that queries MISP API and generates firewall-specific format:

```python
#!/usr/bin/env python3
"""
Export malicious IPs and domains from MISP to firewall block list
"""
from pymisp import PyMISP
import csv
from datetime import datetime, timedelta

# MISP connection
misp_url = 'https://misp-test.lan'
misp_key = 'tseZi6l1V0EdXmJQKEjwIGuFSbeLhUKxWuzjCdlT'
misp = PyMISP(misp_url, misp_key, ssl=False)

# Query MISP for IOCs from last 30 days
search_params = {
    'published': True,
    'timestamp': '30d',  # Last 30 days
    'type_attribute': ['ip-dst', 'domain'],  # IPs and domains only
    'to_ids': True  # Only IOCs marked for blocking
}

results = misp.search('attributes', **search_params)

# Extract unique IPs and domains
ips = set()
domains = set()

for event in results['Attribute']:
    if event['type'] == 'ip-dst':
        ips.add(event['value'])
    elif event['type'] == 'domain':
        domains.add(event['value'])

# Export to Palo Alto EDL format (text file, one entry per line)
with open('/var/www/html/firewall/malicious-ips.txt', 'w') as f:
    for ip in sorted(ips):
        f.write(f"{ip}\n")

with open('/var/www/html/firewall/malicious-domains.txt', 'w') as f:
    for domain in sorted(domains):
        f.write(f"{domain}\n")

print(f"Exported {len(ips)} IPs and {len(domains)} domains for firewall blocking")
```

**Deployment**:
- Run script every 15 minutes via cron: `*/15 * * * * /opt/misp/scripts/export-firewall-iocs.py`
- Host EDL files on web server accessible to firewall
- Configure firewall to pull EDL every 15 minutes

### Method 3: MISP-Splunk-Firewall Integration

If using Splunk as SIEM:
1. MISP sends IOCs to Splunk via syslog or API
2. Splunk correlation rule generates firewall block commands
3. Splunk Phantom (SOAR) pushes blocks to firewall via API

## Firewall Configuration

### Palo Alto External Dynamic List (EDL)

```
# Create EDL for malicious IPs
Objects > External Dynamic Lists > Add

Name: MISP-Malicious-IPs
Type: IP List
Source: https://misp-test.lan/firewall/malicious-ips.txt
Check for updates: Every 15 minutes
Certificate Profile: [SSL certificate for MISP]

# Create EDL for malicious domains
Name: MISP-Malicious-Domains
Type: Domain List
Source: https://misp-test.lan/firewall/malicious-domains.txt

# Create security policy rule
Policies > Security > Add

Rule Name: Block MISP IOCs
Source Zone: Any
Destination Zone: Any
Destination Address: MISP-Malicious-IPs
Action: Deny
Log at Session End: Yes
```

### Cisco Firepower Security Intelligence

```
Objects > Security Intelligence > Network Lists and Feeds

Feed Name: MISP Malicious IPs
Feed URL: https://misp-test.lan/firewall/malicious-ips.txt
Update Frequency: Every hour

# Apply to Access Control Policy
Policies > Access Control > Security Intelligence

Action: Block
Networks: [Select MISP Malicious IPs feed]
```

### Fortinet Threat Feed

```
Security Fabric > External Connectors > Create New

Connector Type: IP Address
Name: MISP-Malicious-IPs
URL: https://misp-test.lan/firewall/malicious-ips.txt
Refresh Rate: 15 minutes

# Apply to firewall policy
Policy & Objects > IPv4 Policy > Create New

Name: Block MISP IOCs
Incoming Interface: wan1
Outgoing Interface: any
Source: all
Destination: MISP-Malicious-IPs (External Connector)
Action: Deny
```

## IOC Quality Control

**Important**: Not all MISP events should be blocked at firewall!

**Criteria for firewall blocking** (set `to_ids = true` flag in MISP):
- IOC is high confidence (not speculative)
- IOC is currently active (not historical)
- IOC is externally routable (not RFC 1918 private IPs)
- Blocking IOC will not cause operational impact

**Do NOT export to firewall**:
- Internal IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
- Legitimate services (Google DNS 8.8.8.8, CDN providers)
- Historical IOCs (>90 days old, likely stale)
- Low-confidence indicators

**Quality control checklist**:
- Manual review of IOCs before setting `to_ids = true`
- Automated filtering in export script (exclude private IPs, age filtering)
- Change control approval for initial deployment (not for routine updates)
```

---

