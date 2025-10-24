# MISP for NERC CIP Compliance - Energy Utilities Configuration Guide

**Version:** 1.0
**Date:** October 14, 2025
**Industry:** Electric Utilities (Solar/Wind/Battery)
**Compliance:** NERC CIP Low & Medium Impact BES Cyber Systems

---

## Overview

This guide provides MISP configuration specific to electric utilities operating solar, wind, and battery energy storage systems under NERC CIP compliance requirements. The focus is on ICS/SCADA threat intelligence relevant to Bulk Electric System (BES) Cyber Systems.

**Key Difference from IT Security:**
- ICS/SCADA systems have different threat models than IT systems
- Availability is more critical than confidentiality (operational priority)
- Threat actors targeting critical infrastructure (nation-state, hacktivists)
- Legacy protocols (Modbus, DNP3, IEC 61850) have limited security
- Patch cycles measured in months/years, not days

---

## NERC CIP 2025 Requirements Relevant to Threat Intelligence

### CIP-003-9: Cybersecurity - Security Management Controls
- **R2**: Cyber security awareness program
- **Requirement**: Personnel must be aware of current cyber threats to BES systems

**MISP Role**: Source of threat intelligence for security awareness training

### CIP-005-7: Electronic Security Perimeter(s)
- **R1**: Electronic Security Perimeter (ESP) identification
- **R2**: Electronic Access Controls at Electronic Access Points (EAPs)

**MISP Role**: IOCs for blocking malicious IPs/domains at EAPs

### CIP-010-4: Configuration Change Management and Vulnerability Assessments
- **R3**: Vulnerability assessments at least once every 15 calendar months

**MISP Role**: Vulnerability intelligence for ICS/SCADA systems

### CIP-013-2: Cyber Security - Supply Chain Risk Management
- **R1.2.5**: Threat intelligence notifications from vendors

**MISP Role**: Central repository for vendor threat notifications

### CIP-015-1: Internal Network Security Monitoring (NEW - June 2025)
- **R1**: Internal network security monitoring within ESPs
- **Requirement**: Detect malicious communications on ICS networks

**MISP Role**: IOCs for internal network monitoring and detection rules

---

## ICS/SCADA Specific Threat Intelligence Sources

### 1. CISA ICS Advisories (PRIMARY SOURCE)

**Source**: https://www.cisa.gov/topics/industrial-control-systems
**Format**: Web-based advisories (no direct API)
**Update Frequency**: As threats are discovered
**Relevance**: ⭐⭐⭐⭐⭐ (Essential for NERC CIP)

**Content:**
- ICS-CERT Advisories (vulnerability disclosures)
- ICS Medical Advisories
- Known Exploited Vulnerabilities (KEV) Catalog
- Cybersecurity Advisories with IOCs

**Integration Method:**
1. **Manual Method**: Weekly review of CISA ICS advisories, manually add to MISP
2. **Semi-Automated**: RSS feed monitoring + manual entry
3. **Future Automation**: Web scraping script (see scripts/cisa-ics-importer.py)

**Vendors Covered:**
- Siemens (SCADA, PLCs, HMIs)
- Schneider Electric (Modicon, EcoStruxure)
- ABB (Grid automation, SCADA)
- GE (Grid Solutions, iFIX SCADA)
- Emerson (DeltaV, Ovation DCS)
- Rockwell Automation (ControlLogix, FactoryTalk)
- Honeywell (Experion, PlantCruise)

### 2. ICS-CERT Recommended Practices

**Source**: https://www.cisa.gov/resources-tools/resources/ics-recommended-practices
**Purpose**: Defense-in-depth strategies for ICS security
**Relevance**: ⭐⭐⭐⭐ (Best practices for NERC CIP)

**Key Documents:**
- "Recommended Practices for Patch Management of Control Systems"
- "Industrial Control Systems Security Incident Response"
- "Improving Industrial Control Systems Cybersecurity"

### 3. E-ISAC (Electricity Information Sharing and Analysis Center)

**Source**: https://www.eisac.com/
**Format**: Member portal (requires membership)
**Update Frequency**: Real-time alerts
**Relevance**: ⭐⭐⭐⭐⭐ (Industry-specific threat intelligence)

**Membership:**
- Available to NERC-registered entities
- Fee-based (varies by entity size)
- Provides early warning of threats targeting electric sector

**Content:**
- Electric sector threat alerts
- Indicator sharing (IOCs specific to utilities)
- Incident reports from peer utilities
- Sector-wide threat briefings

**Integration with MISP:**
- E-ISAC members receive threat intelligence reports
- Manually import IOCs into MISP
- Future: Explore STIX/TAXII feed from E-ISAC (if available)

### 4. Dragos WorldView Threat Intelligence (Commercial)

**Source**: https://www.dragos.com/
**Format**: Commercial platform + MISP integration
**Relevance**: ⭐⭐⭐⭐⭐ (ICS-specific, designed for utilities)

**Content:**
- ICS-specific threat groups (ELECTRUM, KAMACITE, etc.)
- ICS malware analysis (TRISIS, INDUSTROYER, etc.)
- Vulnerability intelligence for ICS products
- Activity group tracking targeting energy sector

**MISP Integration:**
- Dragos provides MISP feeds for customers
- Direct IOC export to MISP format
- Recommended for medium-impact BES Cyber Systems

**Cost**: Enterprise pricing (contact sales)

### 5. Mandiant ICS Threat Intelligence (Commercial)

**Source**: https://www.mandiant.com/
**Relevance**: ⭐⭐⭐⭐ (APT tracking, incident response)

**Specialization:**
- Nation-state threat actors targeting critical infrastructure
- APT group attribution and TTPs
- Incident response services for utilities

### 6. MITRE ATT&CK for ICS

**Source**: https://attack.mitre.org/matrices/ics/
**Format**: Open framework (already in MISP galaxies)
**Relevance**: ⭐⭐⭐⭐⭐ (Essential for understanding ICS TTPs)

**Content:**
- ICS-specific tactics, techniques, and procedures
- Mapped to ICS Kill Chain
- Case studies of ICS attacks

**Already Configured**: MISP galaxies include MITRE ATT&CK ICS

### 7. STIX/TAXII Feeds for Energy Sector

**Potential Sources:**
- DHS AIS (Automated Indicator Sharing) - Free for critical infrastructure
- FS-ISAC (Financial Services) - Cross-sector sharing
- MS-ISAC (Multi-State) - Government/critical infrastructure

**Integration**: MISP has native STIX/TAXII support

---

## Recommended MISP Feeds for NERC CIP Utilities

### Critical Priority Feeds (Enable Immediately)

These feeds have direct relevance to ICS/SCADA threats:

```python
# Add to scripts/configure-misp-ready.py

NERC_CIP_FEEDS = [
    # ICS/SCADA Malware Feeds
    "CIRCL OSINT Feed",                    # Includes ICS malware IOCs
    "Abuse.ch URLhaus",                    # Malware distribution URLs
    "Abuse.ch ThreatFox",                  # IOCs from ICS malware families
    "Abuse.ch SSL Blacklist",              # Malicious SSL certs (C2 detection)

    # APT Groups Targeting Critical Infrastructure
    "MITRE ATT&CK ICS",                    # Already in galaxies (no feed needed)

    # Botnet C2 (affects ICS networks)
    "Abuse.ch Feodo Tracker",              # Botnet C2 infrastructure
    "Bambenek Consulting - C2 All Indicator Feed",

    # IP Reputation (protect Electronic Access Points)
    "Blocklist.de",                        # SSH/RDP brute force (common at EAPs)
    "Botvrij.eu",                          # General malicious IPs

    # Phishing (NERC CIP-003 security awareness)
    "OpenPhish url",                       # Phishing targeting utilities employees
    "Phishtank online valid phishing",

    # General Threat Intelligence
    "DigitalSide Threat-Intel",            # Comprehensive threat data
    "Cybercrime-Tracker - All",            # Various cybercrime infrastructure
]
```

### Medium Priority Feeds (Consider for Medium-Impact Sites)

```python
ADDITIONAL_FEEDS = [
    # Tor Exit Nodes (anomalous for ICS networks)
    "Tor exit nodes",

    # Exploit Kits
    "MalwareBazaar Recent Additions",

    # VPN/Remote Access Monitoring
    "Dataplane.org - sipquery",            # SIP attacks
    "Dataplane.org - vncrfb",              # VNC brute force
]
```

### NOT Recommended for ICS Networks

❌ **Cryptocurrency mining feeds** - Low relevance to ICS
❌ **Generic IT malware feeds** - Too noisy, false positives on ICS
❌ **Consumer-focused feeds** - Not aligned with BES Cyber Systems

---

## NERC CIP News Feeds for Security Awareness

### RSS/Atom News Feeds (Distinct from Threat Intelligence)

MISP can subscribe to RSS/Atom news feeds to provide **security awareness content** for NERC CIP-003-R2 compliance. These are different from threat intelligence IOC feeds - they provide news articles and advisories for training purposes.

**Script**: `scripts/add-nerc-cip-news-feeds.py`

**Usage**:
```bash
# List available news feeds
python3 scripts/add-nerc-cip-news-feeds.py --list

# Test with dry-run mode
python3 scripts/add-nerc-cip-news-feeds.py --dry-run

# Add feeds to MISP
python3 scripts/add-nerc-cip-news-feeds.py
```

### Available News Feeds

**1. CISA ICS Advisories** (PRIMARY - Enabled by default)
- **URL**: https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml
- **Use Case**: CIP-010-R3 (Vulnerability Assessment), CIP-003-R2 (Security Awareness)
- **Content**: Official ICS/SCADA vulnerabilities, solar inverters, wind turbines, battery BMS
- **Update Frequency**: As threats are discovered
- **Relevance**: ⭐⭐⭐⭐⭐ Essential for NERC CIP compliance

**2. SecurityWeek - ICS/SCADA News** (Enabled by default)
- **URL**: https://www.securityweek.com/category/ics-ot-security/feed/
- **Use Case**: CIP-003-R2 (Security Awareness Training), CIP-008-R1 (Incident Response)
- **Content**: Industry news about ICS/SCADA threats, vulnerabilities, and attacks
- **Update Frequency**: Daily
- **Relevance**: ⭐⭐⭐⭐ Good for security awareness

**3. Bleeping Computer - Critical Infrastructure** (Enabled by default)
- **URL**: https://www.bleepingcomputer.com/feed/tag/critical-infrastructure/
- **Use Case**: CIP-003-R2 (Security Awareness), CIP-008-R1 (Incident Response context)
- **Content**: Breaking news on critical infrastructure attacks and ransomware
- **Update Frequency**: Daily
- **Relevance**: ⭐⭐⭐⭐ High relevance to energy sector

**4. Industrial Cyber - News** (Enabled by default)
- **URL**: https://industrialcyber.co/feed/
- **Use Case**: CIP-003-R2 (Security Awareness), CIP-010-R3 (Vulnerability context)
- **Content**: ICS/OT cybersecurity news, product launches, industry trends
- **Update Frequency**: Daily
- **Relevance**: ⭐⭐⭐ Industry awareness

**5. NERC - News & Events** (Disabled by default)
- **URL**: https://www.nerc.com/news/Pages/default.aspx (RSS auto-detected)
- **Use Case**: CIP-003-R2 (Security Awareness), regulatory updates
- **Content**: NERC regulatory announcements, reliability standards updates
- **Relevance**: ⭐⭐⭐ Compliance awareness

**6. Darkreading - ICS/SCADA** (Disabled by default)
- **URL**: https://www.darkreading.com/rss/ics-ot.xml
- **Use Case**: CIP-003-R2 (Security Awareness)
- **Content**: ICS/OT security analysis and commentary
- **Relevance**: ⭐⭐ Optional

**7. The Hacker News - ICS Security** (Disabled by default)
- **URL**: https://feeds.feedburner.com/TheHackersNews?format=xml
- **Use Case**: CIP-003-R2 (Security Awareness)
- **Content**: General cybersecurity news (filter for ICS/SCADA manually)
- **Relevance**: ⭐⭐ Optional

### Configuration Details

**Distribution Level**: All news feeds are configured with:
- `distribution: 0` (Your organization only)
- Complies with CIP-011-R1 (BCSI Protection)
- News content stays internal until reviewed

**Enabled Feeds**: 4 feeds enabled by default (CISA, SecurityWeek, Bleeping Computer, Industrial Cyber)

**Disabled Feeds**: 3 feeds disabled (NERC, Darkreading, Hacker News) - enable manually if desired

### NERC CIP Use Cases

**CIP-003-R2: Security Awareness Training**
- Query MISP news feeds for last 15 months of ICS/SCADA news
- Generate security awareness training materials
- Include recent attack trends, vulnerabilities, and incidents
- Document training with MISP query results

**CIP-008-R1: Incident Response Context**
- Reference news feeds during incident investigations
- Understand broader threat landscape
- Correlate local incidents with industry trends

**CIP-010-R3: Vulnerability Assessment**
- Use CISA ICS advisories to identify vulnerabilities
- Cross-reference with asset inventory
- Prioritize patching based on exploited vulnerabilities

### Important Notes

⚠️ **News Feeds ≠ Threat Intelligence IOCs**
- News feeds provide **context and awareness**
- IOC feeds provide **actionable indicators** (IPs, domains, hashes)
- Use both together for comprehensive security program

⚠️ **BCSI Protection**
- News content may contain sensitive information
- Default distribution: "Your organization only"
- Review before sharing externally

⚠️ **Feed Maintenance**
- Check feed status monthly: `python3 scripts/check-misp-feeds.py`
- Update feeds manually or via cron job
- Remove feeds that become inactive or irrelevant

---

## NERC CIP-Specific MISP Configuration

### Taxonomies to Enable

Enable these MISP taxonomies for NERC CIP compliance:

1. **TLP (Traffic Light Protocol)** - Required for sharing controls
   - TLP:RED - Confidential (internal only)
   - TLP:AMBER - Limited distribution (E-ISAC members)
   - TLP:GREEN - Community (utilities sector)
   - TLP:WHITE - Public

2. **ICS/SCADA Classification**
   - Enable: `misp-taxonomy/ics`
   - Tags: ics-asset-type, ics-protocol, ics-impact

3. **NERC CIP Asset Classification**
   - Custom taxonomy (create in MISP):
     - `nerc-cip:low-impact`
     - `nerc-cip:medium-impact`
     - `nerc-cip:high-impact`
     - `nerc-cip:eacms` (Electronic Access Control/Monitoring Systems)
     - `nerc-cip:pacs` (Physical Access Control Systems)

4. **MITRE ATT&CK for ICS**
   - Already in galaxies
   - Map threats to ICS tactics (Initial Access, Execution, Persistence, etc.)

### Event Templates for NERC CIP

Create custom event templates:

1. **ICS Vulnerability Disclosure**
   - Vendor, product, CVE, patch availability
   - Affected BES Cyber Systems
   - Mitigation steps per NERC CIP-010 R3

2. **Supply Chain Security Alert (CIP-013)**
   - Vendor notification
   - Third-party risk assessment
   - Action required (patch, configuration change, etc.)

3. **Electronic Security Perimeter Breach (CIP-005)**
   - IOCs detected at EAP
   - Blocked IP/domain/URL
   - Related threat actor (if known)

4. **Internal Network Security Event (CIP-015)**
   - Malicious communication detected inside ESP
   - Protocol-level indicators (Modbus, DNP3, IEC 61850)
   - Affected assets (RTUs, PLCs, HMIs)

---

## NERC CIP Compliance Use Cases

### Use Case 1: CIP-003 Security Awareness Training

**Requirement**: Cyber security awareness at least once every 15 calendar months

**MISP Application:**
1. Query MISP for recent ICS threats (last 15 months)
2. Generate report of threats targeting solar/wind/battery systems
3. Include in security awareness training materials
4. Document training with MISP query as evidence

**Audit Evidence**: MISP query results + training records

### Use Case 2: CIP-005 Electronic Access Point Monitoring

**Requirement**: Monitor and log access at Electronic Access Points

**MISP Application:**
1. Export malicious IP/domain list from MISP feeds
2. Import into firewall/IDS at EAPs (Palo Alto, Fortinet, Cisco)
3. Block/alert on matches
4. Log all alerts for NERC CIP audits

**Tools Integration:**
- Firewall: External Dynamic List (EDL) from MISP
- IDS/IPS: Snort/Suricata rules from MISP IOCs
- SIEM: Forward MISP logs for correlation

**Audit Evidence**: Firewall logs showing blocked IPs from MISP

### Use Case 3: CIP-010 Vulnerability Assessment

**Requirement**: Vulnerability assessments every 15 calendar months

**MISP Application:**
1. Query MISP for vulnerabilities affecting your ICS vendors
2. Cross-reference with asset inventory (RTUs, PLCs, HMIs, SCADA)
3. Prioritize patching based on exploited vulnerabilities (KEV)
4. Document findings in vulnerability assessment report

**Audit Evidence**: MISP vulnerability report + remediation plan

### Use Case 4: CIP-013 Supply Chain Risk Management

**Requirement**: Vendor threat intelligence notifications

**MISP Application:**
1. Create MISP events for vendor security bulletins
2. Track vendor vulnerabilities and patches
3. Document vendor response times
4. Demonstrate due diligence in supply chain security

**Audit Evidence**: MISP events tagged with `nerc-cip:supply-chain`

### Use Case 5: CIP-015 Internal Network Security Monitoring (NEW)

**Requirement**: Detect malicious communications inside ESPs

**MISP Application:**
1. Export IOCs from MISP (IPs, domains, file hashes)
2. Import into internal network monitoring tools:
   - Dragos Platform
   - Nozomi Networks
   - Claroty
   - Darktrace (AI-based)
3. Alert on matches to known ICS malware (TRISIS, INDUSTROYER, etc.)
4. Log all detections for NERC CIP compliance

**Protocol-Specific Detection:**
- Modbus: Unusual function codes from MISP IOCs
- DNP3: Unauthorized control commands
- IEC 61850: GOOSE/MMS message anomalies

**Audit Evidence**: Internal network monitoring logs with MISP IOC matches

---

## NERC CIP-Specific Settings

Add to `scripts/configure-misp-ready.py`:

```python
NERC_CIP_SETTINGS = {
    # Incident Response Alignment
    "MISP.incident_response": True,

    # Extended Data Retention (CIP-008 incident response plan)
    "MISP.event_retention": "7_years",  # Align with NERC CIP audit cycles

    # Sharing Controls (CIP-011 information protection)
    "MISP.default_distribution": "Your organization only",

    # API Access for ICS Tools
    "MISP.rest_client_enable_arbitrary_certs": False,  # Require valid certs
    "MISP.api_auth_required": True,

    # Correlation Settings (ICS-specific)
    "MISP.correlation_engine": "Default",
    "MISP.enable_advanced_correlations": True,

    # Taxonomies
    "MISP.enable_taxonomy": True,
    "MISP.taxonomy_visible": True,
}
```

---

## Recommended Additional Tools for NERC CIP

### Network Security Monitoring (CIP-015 Compliance)

**Commercial Tools:**
1. **Dragos Platform** - ICS-specific threat detection
2. **Nozomi Networks** - OT network visibility
3. **Claroty** - Industrial cybersecurity platform
4. **Forescout** - Device visibility and control

**Open Source Alternatives:**
1. **Malcolm** - CISA's network traffic analysis tool
2. **Zeek (formerly Bro)** - Network security monitor with ICS protocol analyzers
3. **Suricata** - IDS/IPS with ICS protocol support

**Integration**: All can consume IOCs from MISP via API or file export

### Vulnerability Management (CIP-010 Compliance)

**Tools:**
1. **Tenable.sc** - Vulnerability scanner with ICS support
2. **Rapid7 InsightVM** - ICS asset discovery
3. **Qualys VMDR** - Vulnerability management

**Integration**: Import vulnerability data into MISP for tracking

### Asset Inventory (CIP-002 Compliance)

**Tools:**
1. **CISA CSET (Cyber Security Evaluation Tool)** - Free
2. **ITIC Asset Inventory Tool** - NERC CIP-focused
3. **Lansweeper** - IT/OT asset discovery

**Integration**: Export asset inventory, correlate with MISP IOCs

---

## Incident Response Plan Integration

### NERC CIP-008: Incident Reporting and Response Planning

**Required Elements:**
1. Incident response plan
2. Testing at least once every 36 calendar months
3. Update within 90 days of testing or incident

**MISP Integration:**

**1. Create Incident Response Event Template**
```json
{
  "event_type": "nerc-cip-incident",
  "threat_level": "High",
  "analysis": "Initial",
  "distribution": "Your organization only",
  "tags": [
    "nerc-cip:incident-response",
    "nerc-cip:reportable-cyber-security-incident",
    "tlp:red"
  ]
}
```

**2. Reportable Cyber Security Incident Criteria**

Per NERC CIP-008, report to E-ISAC within 1 hour:
- Compromised BES Cyber System
- Suspected malicious event that could impact BES reliability

**MISP Workflow:**
1. Detect incident (CIP-015 monitoring)
2. Create MISP event with IOCs
3. Tag as `nerc-cip:reportable`
4. Share with E-ISAC (if member)
5. Document response actions in MISP
6. Update incident response plan based on lessons learned

---

## Data Retention Requirements

### NERC CIP Retention Periods

| Standard | Data Type | Retention Period |
|----------|-----------|------------------|
| CIP-002 | Asset inventory | Current + 3 years |
| CIP-003 | Security policies | Current + 3 years |
| CIP-005 | EAP logs | 90 calendar days |
| CIP-007 | Security event logs | 90 calendar days |
| CIP-008 | Incident records | Current + 3 years |
| CIP-010 | Vulnerability assessments | Current + 3 years |

**MISP Configuration:**
- Set event retention to minimum 3 years
- Export quarterly backups for long-term storage
- Document retention policy in MISP instance

---

## Security Considerations for NERC CIP

### CIP-011: Information Protection

**Requirement**: Protect BES Cyber System Information (BCSI)

**MISP is BCSI**: Contains sensitive information about BES Cyber Systems:
- Asset inventory data
- Vulnerability information
- Network architecture (indirectly)
- Incident response procedures

**Protection Requirements:**
1. **Access Control**: Role-based access to MISP
2. **Encryption**: TLS for all connections (HTTPS)
3. **Reuse/Disposal**: Secure deletion when decommissioning
4. **Information Access Management**: Log all MISP access

**Audit Considerations:**
- MISP access logs = CIP-011 audit evidence
- Document who has access to MISP
- Review access quarterly (align with CIP-004 access reviews)

### CIP-007: Systems Security Management

**Requirement**: Malicious code prevention, security event monitoring

**MISP Server Security:**
1. Patch MISP within 35 days of patch availability (CIP-007 R2)
2. Enable logging of all MISP activity (CIP-007 R4)
3. Implement antivirus on MISP host (CIP-007 R3)
4. Disable unnecessary services (CIP-007 R1)

---

## Quick Start: NERC CIP Production-Ready Setup

### Phase 1: Core Configuration (Week 1)

```bash
# 1. Install MISP (already done)
python3 misp-install.py --config config/nerc-cip-config.json

# 2. Run NERC CIP-specific configuration
python3 scripts/configure-misp-nerc-cip.py

# This script will:
# - Enable ICS/SCADA feeds
# - Configure NERC CIP taxonomies
# - Set up event templates
# - Configure retention policies (3 years)
# - Enable audit logging
```

### Phase 2: Feed Activation (Week 2)

1. Access MISP web interface: `https://misp.yourdomain.com`
2. Navigate to: **Sync Actions > List Feeds**
3. Enable recommended feeds (see list above)
4. Click **Fetch and store all feed data** for each enabled feed
5. Schedule daily feed updates (cron job)

### Phase 3: Integration with EAP Security (Week 3-4)

1. Export malicious IP list from MISP
2. Import into firewall at Electronic Access Points
3. Configure blocking/alerting rules
4. Test with known malicious IP

### Phase 4: Incident Response Integration (Week 5-6)

1. Create incident response event templates
2. Train SOC team on MISP workflow
3. Document process in Incident Response Plan (CIP-008)
4. Conduct tabletop exercise

### Phase 5: Audit Documentation (Ongoing)

1. Document MISP usage in NERC CIP compliance evidence
2. Export MISP reports quarterly
3. Include in annual vulnerability assessment (CIP-010)
4. Update security awareness training materials (CIP-003)

---

## NERC CIP Audit Checklist

Use this checklist during NERC CIP audits:

### Evidence from MISP

- [ ] **CIP-003-R2**: Security awareness training materials (MISP threat reports)
- [ ] **CIP-005-R2**: Electronic Access Point logs (MISP IOC blocks)
- [ ] **CIP-007-R4**: Security event logs (MISP access logs)
- [ ] **CIP-008-R1**: Incident response procedures (MISP incident templates)
- [ ] **CIP-010-R3**: Vulnerability assessment results (MISP vulnerability queries)
- [ ] **CIP-011-R1**: BCSI protection procedures (MISP access controls)
- [ ] **CIP-013-R1**: Supply chain security (MISP vendor notifications)
- [ ] **CIP-015-R1**: Internal network monitoring (MISP IOC detections)

### MISP Configuration Evidence

- [ ] Access control matrix (who can access MISP)
- [ ] User access review logs (quarterly)
- [ ] Patch management records (CIP-007)
- [ ] Backup logs (disaster recovery)
- [ ] Data retention policy documentation

---

## Solar/Wind/Battery-Specific Considerations

### Distributed Energy Resources (DERs)

**2025 Update**: DERs now subject to stricter NERC CIP controls

**MISP Use Cases:**
- Solar inverter vulnerabilities (SMA, Fronius, Enphase)
- Battery management system (BMS) threats
- Wind turbine controller exploits (Vestas, GE, Siemens)

**Vendor-Specific Intelligence:**
- Track CVEs for your specific inverter/controller models
- Create MISP events for vendor security bulletins
- Share with other utilities via E-ISAC

### Energy Management Systems (EMS)

**Common EMS Platforms:**
- GE Grid Solutions (e-terra, ADMS)
- Schneider Electric (ADMS, DMS)
- ABB (Network Manager SCADA)
- Siemens (Spectrum Power)

**MISP Configuration:**
- Tag events with EMS vendor
- Monitor CISA ICS advisories for your EMS platform
- Track patches and vulnerabilities

### Communications Networks

**NERC CIP-005**: Protect communications between substations

**Common Protocols:**
- DNP3 (Distributed Network Protocol)
- IEC 61850 (Substation automation)
- Modbus TCP (PLCs, RTUs)
- SEL Fast Messaging (Schweitzer Engineering Labs)

**MISP IOCs:**
- Malformed DNP3 packets
- IEC 61850 GOOSE message attacks
- Modbus function code abuse

---

## Cost Estimates

### Free/Open Source Only

**Components:**
- MISP (free, open source)
- CISA ICS advisories (free)
- Open OSINT feeds (free)
- Manual import of E-ISAC alerts (if member)

**Total Cost**: $0 + labor (manual processes)

**Suitable For**: NERC CIP Low-Impact sites

### With E-ISAC Membership

**Components:**
- MISP (free)
- E-ISAC membership ($5,000 - $25,000/year depending on size)
- CISA ICS advisories (free)
- Open OSINT feeds (free)

**Total Cost**: $5K - $25K/year + labor

**Suitable For**: NERC CIP Medium-Impact sites

### With Commercial ICS Threat Intel

**Components:**
- MISP (free)
- E-ISAC membership ($5K - $25K/year)
- Dragos WorldView ($50K - $150K/year)
- Internal network monitoring tool ($100K - $300K)

**Total Cost**: $155K - $475K/year

**Suitable For**: NERC CIP High-Impact sites, large utilities

---

## Next Steps

### Immediate (This Week)

1. ✅ Enable ICS/SCADA-specific feeds in MISP
2. ✅ Create NERC CIP custom taxonomies
3. ✅ Set up event templates for incident response
4. Document MISP as part of CIP-008 incident response plan

### Short-Term (Next 30 Days)

1. Apply for E-ISAC membership (if not already member)
2. Integrate MISP IOCs with Electronic Access Point firewalls
3. Train SOC team on MISP for ICS incident response
4. Schedule quarterly vulnerability assessment using MISP

### Medium-Term (Next 90 Days)

1. Evaluate commercial ICS threat intelligence (Dragos, Mandiant)
2. Implement internal network monitoring (CIP-015 compliance)
3. Conduct tabletop exercise using MISP threat scenarios
4. Document MISP usage for upcoming NERC CIP audit

### Long-Term (Next Year)

1. Automate CISA ICS advisory imports
2. Integrate MISP with SIEM (when ready for Splunk/Security Onion)
3. Participate in sector-wide threat intelligence sharing (via E-ISAC)
4. Expand MISP to cover IT/OT convergence threats

---

## Additional Resources

### NERC CIP Compliance
- NERC Reliability Standards: https://www.nerc.com/pa/Stand/Pages/default.aspx
- NERC Compliance Guidance: https://www.nerc.com/pa/comp/Pages/default.aspx
- NERC CIP-015-1 Implementation Guide: (Available Q4 2025)

### ICS/SCADA Security
- CISA ICS: https://www.cisa.gov/topics/industrial-control-systems
- NIST SP 800-82 Rev 3: Guide to ICS Security
- IEC 62443: Industrial Security Standards

### Threat Intelligence
- E-ISAC: https://www.eisac.com/
- MISP Project: https://www.misp-project.org/
- MITRE ATT&CK ICS: https://attack.mitre.org/matrices/ics/

### Training
- SANS ICS515: ICS Cybersecurity
- SANS ICS410: ICS/SCADA Security Essentials
- INL NCCIC Training: https://ics-cert-training.inl.gov/

---

**Document Owner**: tKQB Enterprises
**Last Updated**: October 14, 2025
**Version**: 1.0 (Initial Release)

---

## Appendix A: Glossary

**BES**: Bulk Electric System
**BCSI**: BES Cyber System Information
**CIP**: Critical Infrastructure Protection
**DER**: Distributed Energy Resource
**EAP**: Electronic Access Point
**EACMS**: Electronic Access Control or Monitoring Systems
**E-ISAC**: Electricity Information Sharing and Analysis Center
**EMS**: Energy Management System
**ESP**: Electronic Security Perimeter
**ICS**: Industrial Control System
**INSM**: Internal Network Security Monitoring
**IOC**: Indicator of Compromise
**KEV**: Known Exploited Vulnerabilities
**NERC**: North American Electric Reliability Corporation
**OT**: Operational Technology
**PACS**: Physical Access Control System
**RTU**: Remote Terminal Unit
**SCADA**: Supervisory Control and Data Acquisition
**TLP**: Traffic Light Protocol
