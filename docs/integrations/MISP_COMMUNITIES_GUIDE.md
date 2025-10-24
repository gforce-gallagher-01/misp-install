# MISP Communities Guide - Utilities Sector Focus

**Date**: 2025-10-17
**Purpose**: Guide for joining and integrating with MISP threat intelligence sharing communities
**Target Audience**: Utilities sector organizations running MISP

---

## Table of Contents

1. [Overview](#overview)
2. [Recommended Communities](#recommended-communities)
3. [ICS-CSIRT.io (Primary Recommendation)](#ics-csirtio)
4. [Additional Communities](#additional-communities)
5. [ISACs for Utilities Sector](#isacs-for-utilities-sector)
6. [How to Join](#how-to-join)
7. [Integration Guide](#integration-guide)
8. [What to Share](#what-to-share)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What are MISP Communities?

MISP communities are groups of organizations sharing threat intelligence through interconnected MISP instances. Benefits include:

- ✅ **Real-time threat intelligence** from peer organizations
- ✅ **Sector-specific IOCs** relevant to your industry
- ✅ **Collaborative defense** against common adversaries
- ✅ **Early warning** of emerging threats
- ✅ **Reduced false positives** through community validation

### Why Join a Community?

**Standalone MISP**:
- Only your organization's threat data
- Limited visibility into external threats
- No community validation

**Community MISP**:
- Shared intelligence from 10s-100s of organizations
- Sector-specific threat visibility
- Community-validated IOCs
- Cross-sector correlation

### Traffic Light Protocol (TLP)

All communities use TLP for information sharing:

- **TLP:CLEAR** (formerly WHITE) - Unlimited disclosure
- **TLP:GREEN** - Community sharing
- **TLP:AMBER** - Limited disclosure
- **TLP:AMBER+STRICT** - Organization only
- **TLP:RED** - Personal/eyes only

---

## Recommended Communities

### For Utilities Sector Organizations

| Community | Focus | Cost | Best For |
|-----------|-------|------|----------|
| **ICS-CSIRT.io** ⭐ | ICS/SCADA | Free | All utilities |
| **E-ISAC** | Electric utilities | Membership fee | Electric power |
| **WaterISAC** | Water/wastewater | Membership fee | Water utilities |
| **SecureGRID Alliance** | Multi-sector | Free | Grid operators |
| **CIRCL Private Sector** | Various sectors | Contact | European orgs |

---

## ICS-CSIRT.io

### Primary Recommendation for Utilities Sector ⭐

**Why ICS-CSIRT.io is Ideal**:
1. ✅ **Free membership** (in exchange for threat data sharing)
2. ✅ **ICS/SCADA focus** (directly relevant to utilities)
3. ✅ **MISP instance access** (full threat intelligence platform)
4. ✅ **OpenCVE access** (vulnerability tracking for ICS)
5. ✅ **International community** (global threat visibility)
6. ✅ **No commercial/government affiliation** (neutral platform)

### What You Get

**MISP Instance**:
- Dedicated ICS/SCADA threat intelligence
- Community-curated IOCs
- API access for automation
- Bi-directional synchronization

**OpenCVE Platform**:
- ICS-specific CVE tracking
- Vendor security advisory monitoring
- Automated vulnerability alerts
- Custom watchlists

**Community Benefits**:
- Peer collaboration
- Incident response support
- Threat analysis assistance
- Best practices sharing

### Contact Information

- **Email**: info@ics-csirt.io
- **Website**: https://misp.ics-csirt.io/
- **Sector**: Industrial Control Systems
- **Membership**: Free (requires data contribution)

### How to Join

See **[ICS-CSIRT_MEMBERSHIP_EMAIL.md](ICS-CSIRT_MEMBERSHIP_EMAIL.md)** for complete membership request template and instructions.

**Quick Steps**:
1. Email info@ics-csirt.io with membership request
2. Provide organization details and ICS environment info
3. Commit to sharing threat intelligence
4. Receive MISP and OpenCVE credentials
5. Configure synchronization with your MISP instance

---

## Additional Communities

### SecureGRID Alliance

**Focus**: Cross-organization threat information linking
**Sector**: Energy, utilities, critical infrastructure
**Cost**: Free to join

**Benefits**:
- Cooperative threat sharing framework
- Free membership
- Grid operator focus

**How to Join**: Visit SecureGRID Alliance website for application

---

### CIRCL Private Sector (Luxembourg)

**Focus**: Various sectors including critical infrastructure
**Operator**: CIRCL.lu (Computer Incident Response Center Luxembourg)
**Cost**: Contact for details

**Benefits**:
- Well-established community
- Professional CSIRT support
- European focus

**Contact**: info@circl.lu

---

### INFINITUMIT SOC

**Focus**: Various sectors
**Region**: Poland
**Type**: Commercial SOC provider

**Note**: Commercial service, not purely community-driven

---

## ISACs for Utilities Sector

### Electricity ISAC (E-ISAC)

**Focus**: Electric utilities sector
**Website**: https://www.eisac.com/
**Membership**: Paid (pricing varies by organization size)

**Benefits**:
- Electric sector-specific threat intelligence
- ICS-CERT advisories
- Incident coordination
- Security awareness training
- May offer MISP integration

**Who Should Join**: Electric power generation, transmission, and distribution companies

---

### WaterISAC

**Focus**: Water and wastewater utilities
**Website**: https://www.waterisac.org/
**Membership**: Paid

**Benefits**:
- Water sector threat intelligence
- Regulatory compliance support
- Incident response coordination
- Training and exercises

**Who Should Join**: Water treatment facilities, wastewater utilities, water districts

---

### ICS-ISAC

**Focus**: All industrial control systems
**Partnership**: EastWest Institute
**Scope**: Global critical infrastructure

**Benefits**:
- Cross-sector ICS threat intelligence
- International collaboration
- Government partnership
- Portal for multi-national sharing

---

## How to Join

### General Membership Process

1. **Identify Target Community**
   - Match your sector (electric, water, gas, etc.)
   - Consider geographic region
   - Evaluate cost vs. benefit

2. **Prepare Application**
   - Organization details
   - Security contact information
   - ICS/SCADA environment overview
   - Commitment to data sharing

3. **Submit Request**
   - Email or web form
   - Provide required documentation
   - Agree to terms of service

4. **Wait for Approval**
   - Review period: 3-14 days typically
   - May require additional information
   - Background verification possible

5. **Receive Credentials**
   - MISP instance URL
   - API key for automation
   - Community guidelines

6. **Configure Integration**
   - Add sync server to your MISP
   - Set up push/pull rules
   - Test synchronization

---

## Integration Guide

### Adding a Community Sync Server

#### Via MISP Web UI

1. Navigate to **Sync Actions → List Servers**
2. Click **Add Server**
3. Configure:
   - **Base URL**: Community MISP URL (e.g., https://misp.ics-csirt.io)
   - **Instance Name**: Friendly name
   - **Authkey**: API key from community
   - **Remote Org ID**: Organization ID (provided by community)
   - **Push**: Enable to share your data
   - **Pull**: Enable to receive community data
   - **Self Signed**: Check if using self-signed certs

4. **Save**

#### Via API

```bash
MISP_API_KEY="your-api-key"
COMMUNITY_URL="https://misp.ics-csirt.io"
COMMUNITY_API_KEY="community-provided-key"

curl -k -H "Authorization: $MISP_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST "https://misp-test.lan/servers/add" \
  -d "{
    \"url\": \"$COMMUNITY_URL\",
    \"authkey\": \"$COMMUNITY_API_KEY\",
    \"name\": \"ICS-CSIRT.io\",
    \"push\": true,
    \"pull\": true,
    \"remote_org_id\": 1,
    \"push_rules\": \"\",
    \"pull_rules\": \"\"
  }"
```

#### Via MISP CLI

```bash
sudo docker exec misp-misp-core-1 \
  /var/www/MISP/app/Console/cake Server add \
  "$COMMUNITY_URL" "$COMMUNITY_API_KEY" "ICS-CSIRT.io" 1
```

---

### Configuring Push/Pull Rules

**Push Rules** (What you share):
```json
{
  "tags": {
    "OR": ["ics:", "scada:", "utilities:"],
    "NOT": ["internal-only", "tlp:red"]
  },
  "orgs": {
    "OR": ["your-org-uuid"]
  }
}
```

**Pull Rules** (What you receive):
```json
{
  "tags": {
    "OR": ["ics:", "scada:", "utilities:", "energy:"],
    "NOT": ["tlp:red"]
  }
}
```

---

### Automated Synchronization

#### Set Up Cron Jobs

```bash
# Pull from community every 6 hours
0 */6 * * * /var/www/MISP/app/Console/cake Server pull 1 admin@misp.lan

# Push to community every 6 hours (offset by 3 hours)
0 3,9,15,21 * * * /var/www/MISP/app/Console/cake Server push 1 admin@misp.lan
```

#### Docker Environment

```bash
# Add to host cron
sudo crontab -e

# Add these lines
0 */6 * * * docker exec misp-misp-core-1 /var/www/MISP/app/Console/cake Server pull 1 admin@misp.lan
0 3,9,15,21 * * * docker exec misp-misp-core-1 /var/www/MISP/app/Console/cake Server push 1 admin@misp.lan
```

---

## What to Share

### High-Value Intelligence for ICS/Utilities Communities

#### 1. Indicators of Compromise (IOCs)

**Network Indicators**:
- Malicious IP addresses targeting OT networks
- C2 domains used by ICS malware
- DNS queries associated with reconnaissance
- Network traffic patterns (Modbus, DNP3, IEC 104 anomalies)

**File Indicators**:
- Industrial malware hashes (TRITON, INDUSTROYER, etc.)
- Malicious HMI project files
- Weaponized PLC firmware
- Phishing attachments targeting utilities sector

**Email Indicators**:
- Phishing sender addresses
- Subject line patterns
- Malicious URLs in utilities-themed campaigns

#### 2. Vulnerabilities

**ICS-Specific CVEs**:
- Exploited vulnerabilities in your environment
- 0-days discovered in ICS equipment
- Proof-of-concept exploits for utilities sector systems

**Vendor Security Advisories**:
- Siemens, Schneider Electric, Rockwell, ABB, GE, Honeywell
- HMI/SCADA vulnerabilities
- PLC/RTU security patches

#### 3. Threat Actor Intelligence

**APT Campaigns**:
- DRAGONFLY/Energetic Bear activity
- SANDWORM/ELECTRUM targeting
- APT33 (HOLMIUM) operations
- XENOTIME/TRITON actor TTPs
- Volt Typhoon infrastructure targeting

**Ransomware Campaigns**:
- LockBit, ALPHV/BlackCat, Cl0p
- Utilities sector targeting
- Industrial control system impacts

#### 4. Tactics, Techniques, and Procedures (TTPs)

**MITRE ATT&CK for ICS**:
- Initial Access methods observed
- Lateral Movement techniques
- Persistence mechanisms
- Impact techniques (Loss of Control, Manipulation of Control)

#### 5. Incident Reports

**Security Events**:
- Network intrusions (anonymized)
- Phishing campaign statistics
- Malware detections
- Lessons learned

**Best Practices**:
- Anonymize organization-specific details
- Focus on technical indicators
- Share mitigation strategies
- Document timeline of events

---

### What NOT to Share

#### Restricted Information

- ❌ **Specific facility locations** or GPS coordinates
- ❌ **Network diagrams** showing topology
- ❌ **Authentication credentials** or API keys
- ❌ **Personally Identifiable Information** (PII)
- ❌ **Proprietary control system logic**
- ❌ **Information violating NDAs** or confidentiality agreements
- ❌ **Data restricted by regulations** (CUI, FOUO, etc.)
- ❌ **Victim attribution** without consent

#### Privacy Best Practices

**Sanitize Data**:
- Remove internal IP addresses (use RFC 1918 examples)
- Redact hostnames revealing facility details
- Anonymize user accounts and email addresses
- Generalize geographic references ("Midwest utility" not "City XYZ")

**Use TLP Markings**:
- Mark sensitive data appropriately
- Default to TLP:AMBER for utilities sector data
- Use TLP:AMBER+STRICT for organization-specific context
- Only use TLP:CLEAR for publicly available information

---

## Best Practices

### Effective Community Participation

#### 1. Start Small, Scale Up

**Week 1-2**: Pull only (receive threat intelligence)
**Week 3-4**: Test pushing non-sensitive indicators
**Month 2+**: Full bi-directional sharing

#### 2. Quality Over Quantity

**Do**:
- ✅ Share validated, high-fidelity IOCs
- ✅ Provide context for indicators
- ✅ Tag data appropriately (TLP, sector, threat type)
- ✅ Include MITRE ATT&CK mappings
- ✅ Add references (ICS-CERT advisories, vendor bulletins)

**Don't**:
- ❌ Share unvalidated or low-confidence indicators
- ❌ Flood community with bulk auto-imports
- ❌ Submit false positives without verification
- ❌ Share data without proper TLP marking

#### 3. Engage with Community

**Participation**:
- Comment on shared events with additional context
- Correlate indicators with your observations
- Ask questions and seek clarification
- Share lessons learned from incidents

#### 4. Maintain Operational Security

**OPSEC Considerations**:
- Review data before sharing
- Follow your organization's information sharing policy
- Obtain management approval for sensitive disclosures
- Document what you share and why

#### 5. Monitor Community Intelligence

**Daily**:
- Review new IOCs relevant to your sector
- Check for critical ICS-CERT advisories
- Monitor threat actor campaigns targeting utilities

**Weekly**:
- Analyze trending threats in community
- Update detection rules based on community IOCs
- Review your contributions for quality

**Monthly**:
- Assess value received vs. contributed
- Adjust push/pull rules as needed
- Participate in community discussions

---

## Troubleshooting

### Sync Server Issues

#### Problem: "Connection refused"

**Cause**: Community MISP instance unreachable

**Solution**:
```bash
# Test connectivity
curl -k https://misp.ics-csirt.io

# Check firewall rules
sudo iptables -L OUTPUT | grep -i misp

# Verify DNS resolution
nslookup misp.ics-csirt.io
```

#### Problem: "Authentication failed"

**Cause**: Invalid or expired API key

**Solution**:
1. Contact community administrator
2. Request new API key
3. Update sync server configuration
4. Test with manual API call:
```bash
curl -k -H "Authorization: YOUR_API_KEY" \
  https://misp.ics-csirt.io/servers/getPyMISPVersion.json
```

#### Problem: "No events syncing"

**Cause**: Push/pull rules filtering all events

**Solution**:
1. Review push/pull rules
2. Temporarily disable rules to test
3. Check event tags match rule criteria
4. Verify TLP settings allow sharing

---

### Permission Issues

#### Problem: "User does not have permission to sync"

**Cause**: User role lacks sync permissions

**Solution**:
1. Navigate to: **Administration → List Roles**
2. Edit user's role
3. Enable "Sync Actions" permission
4. Enable "REST API" permission
5. Save and retry sync

---

### Performance Issues

#### Problem: Sync taking too long

**Cause**: Large event dataset

**Solution**:
```bash
# Limit initial sync to recent events
/var/www/MISP/app/Console/cake Server pull 1 admin@misp.lan --filter last=7d

# Incrementally expand timeframe
/var/www/MISP/app/Console/cake Server pull 1 admin@misp.lan --filter last=30d
```

#### Problem: MISP performance degraded after sync

**Cause**: Too many correlations

**Solution**:
1. Disable auto-correlation temporarily
2. Run manual correlation during off-hours:
```bash
/var/www/MISP/app/Console/cake Admin updateCorrelations
```
3. Optimize database:
```bash
/var/www/MISP/app/Console/cake Admin updateDatabase
```

---

## Monitoring and Metrics

### Track Community Contribution

#### Dashboard Metrics

Create custom widgets to monitor:
- Events received from communities (last 7/30 days)
- Events shared to communities (last 7/30 days)
- Top IOC types received
- Community-sourced detections

#### Measuring Value

**Quantitative Metrics**:
- Number of IOCs received
- Number of malware samples shared
- Correlation hits with internal data
- Blocked threats based on community IOCs

**Qualitative Metrics**:
- Early warning of sector-specific campaigns
- Validation of internal threat hunting
- Peer collaboration on incident response
- Knowledge gained from community discussions

---

## Community Etiquette

### Do's

- ✅ **Respond promptly** to community requests for information
- ✅ **Provide context** when sharing indicators
- ✅ **Give credit** to original sources
- ✅ **Follow TLP markings** strictly
- ✅ **Report issues** to community administrators
- ✅ **Participate actively** in discussions
- ✅ **Thank contributors** for valuable intelligence

### Don'ts

- ❌ **Don't share unverified information** as fact
- ❌ **Don't violate TLP restrictions**
- ❌ **Don't re-share without permission**
- ❌ **Don't spam** the community
- ❌ **Don't engage in vendor promotion**
- ❌ **Don't attribute attacks** without evidence
- ❌ **Don't share others' sensitive data**

---

## Compliance Considerations

### Regulatory Requirements

**NERC CIP** (Electric Utilities):
- CIP-008: Incident reporting may require community coordination
- CIP-013: Supply chain risk requires threat intelligence
- Consider community sharing in compliance programs

**TSA Security Directives** (Pipelines):
- Cybersecurity incident reporting
- Threat information sharing requirements

**State/Local Regulations**:
- Review data sharing restrictions
- Obtain legal approval for cross-border sharing
- Document community participation in security programs

---

## Resources

### MISP Documentation
- **Official Docs**: https://www.misp-project.org/
- **API Documentation**: https://www.misp-project.org/openapi/
- **Community List**: https://www.misp-project.org/communities/

### ICS Security Resources
- **ICS-CERT Advisories**: https://www.cisa.gov/ics
- **MITRE ATT&CK for ICS**: https://attack.mitre.org/matrices/ics/
- **NIST ICS Security**: https://www.nist.gov/programs-projects/securing-industrial-control-systems

### Information Sharing Standards
- **TLP**: https://www.cisa.gov/tlp
- **STIX/TAXII**: https://oasis-open.github.io/cti-documentation/
- **FIRST**: https://www.first.org/

---

## Summary

### Quick Start Checklist

- [ ] Choose target community (recommended: ICS-CSIRT.io)
- [ ] Prepare membership application
- [ ] Send request email
- [ ] Receive credentials
- [ ] Add sync server to MISP
- [ ] Configure push/pull rules
- [ ] Test synchronization
- [ ] Set up automated sync cron jobs
- [ ] Share first threat intelligence
- [ ] Monitor community contributions

### Success Criteria

**Within 30 Days**:
- ✅ Successfully syncing with at least one community
- ✅ Receiving sector-relevant threat intelligence
- ✅ Contributing validated IOCs
- ✅ Automated sync running on schedule

**Within 90 Days**:
- ✅ Active participation in community discussions
- ✅ Detecting threats based on community intelligence
- ✅ Contributing incident learnings
- ✅ Measurable security improvements

---

**Document Version**: 1.0
**Date**: 2025-10-17
**Maintainer**: tKQB Enterprises
**Related Documentation**:
- ICS-CSIRT_MEMBERSHIP_EMAIL.md
- INSTALLATION.md
- API_USAGE.md
- FEED_MANAGEMENT_COMPLETE.md
