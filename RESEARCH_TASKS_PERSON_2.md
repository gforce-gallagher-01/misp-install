# MISP NERC CIP Research Tasks - Person 2
## Events, Taxonomies, Feeds, Threat Intelligence

**Assigned To**: Person 2
**Focus Areas**: CIP-003 (Training), CIP-005 (ESP), CIP-013 (Supply Chain), CIP-015 (Monitoring)
**Estimated Total Time**: 25-30 hours
**Priority**: HIGH (Content foundation for compliance)
**Dependencies**: None (can start immediately)

---

## Overview

You are responsible for researching and documenting **what threat intelligence content** should be in MISP, **how it should be organized** (taxonomies/tags), **where it comes from** (feeds), and **how events should be structured** for NERC CIP Medium Impact compliance.

**Why This Matters**:
- CIP-003 requires security awareness training - you'll define training content
- CIP-005 requires ESP monitoring - you'll define IOCs for firewalls
- CIP-013 requires supply chain tracking - you'll define vendor event structure
- CIP-015 requires internal monitoring - you'll define ICS threat intelligence

---

## Your Task List

### SECTION 1: EVENT TYPES & STRUCTURES (CIP-003, CIP-008)

**CIP Requirement**: Events must support training (CIP-003) and incident response (CIP-008)

**Current State**: Only 1 event exists (PIPEDREAM malware)

**Your Goal**: Define what types of events we need and how they should be structured

---

#### TASK 2.1: Define Required Event Categories

**Time Estimate**: 3-4 hours

**What to Research**:

1. **ICS/SCADA Attack Events**:
   - Historical attacks we should document for training
   - Current threats targeting utilities
   - ICS-specific malware families

2. **Phishing & Social Engineering Events**:
   - Campaigns targeting utility sector
   - BEC/CEO fraud
   - Credential harvesting

3. **Supply Chain Events** (CIP-013):
   - Vendor security bulletins
   - Third-party compromises
   - Hardware/software vulnerabilities

4. **Incident Response Events** (CIP-008):
   - Reportable cyber security incidents
   - Near-miss incidents for training
   - Tabletop exercise scenarios

**Deliverable**: Complete the template below

---

**TEMPLATE: MISP Event Categories for Utilities**

```markdown
# MISP Event Categories for Electric Utilities

## Category 1: ICS/SCADA Attacks (Historical)

**Purpose**: Security awareness training (CIP-003 R2)

**Required Events** (Minimum 5):

### Event 1: TRISIS/TRITON (2017)
- **Date**: August 4, 2017
- **Target**: Schneider Electric Triconex safety controllers
- **Impact**: Attempted to disable safety instrumented system
- **Relevance to Us**: [ ] We use Triconex  [ ] Similar safety systems  [ ] General awareness
- **Training Value**: Critical - first malware targeting safety systems
- **IOCs Available**: [ ] Yes  [ ] No  [ ] Research needed
- **Information Sources**:
  - CISA ICS-CERT Advisory: _______________________________
  - Vendor bulletin: _______________________________
  - Other: _______________________________

### Event 2: INDUSTROYER/CrashOverride (2016)
- **Date**: December 17, 2016
- **Target**: Ukraine power grid (substation automation)
- **Impact**: Power outage affecting 225,000 customers
- **Protocols Targeted**: IEC 60870-5-101, IEC 60870-5-104, IEC 61850
- **Relevance to Us**:
  - [ ] We use IEC 61850  [ ] We use IEC 60870  [ ] General awareness
- **Training Value**: Critical - direct power grid targeting
- **IOCs Available**: [ ] Yes  [ ] No  [ ] Research needed

### Event 3: Stuxnet (2010)
- **Date**: June 2010
- **Target**: Siemens PLCs (nuclear enrichment)
- **Impact**: Physical damage to centrifuges
- **Relevance to Us**: [ ] We use Siemens PLCs  [ ] General awareness
- **Training Value**: High - shows physical impact from cyber attack
- **IOCs Available**: [ ] Yes  [ ] No  [ ] Research needed

### Event 4: BlackEnergy3 (2015)
- **Date**: December 23, 2015
- **Target**: Ukraine power distribution
- **Impact**: 230,000 customers without power (3-6 hours)
- **Relevance to Us**: Direct relevance - power distribution
- **Training Value**: Critical - shows combined attack (malware + social engineering)
- **IOCs Available**: [ ] Yes  [ ] No  [ ] Research needed

### Event 5: PIPEDREAM / INCONTROLLER (2022)
- **Date**: April 2022
- **Target**: Multiple ICS/SCADA platforms (Schneider, OMRON, OPC UA)
- **Impact**: Modular framework for multiple ICS attacks
- **Relevance to Us**:
  - [ ] We use Schneider Electric  [ ] We use OMRON  [ ] We use OPC UA
- **Training Value**: Critical - current threat, multi-vendor
- **IOCs Available**: ✅ Yes (already have this event)

**Additional ICS Attack Events to Research** (Optional but recommended):
- [ ] Havex/Dragonfly (2014) - targeting ICS vendors
- [ ] Shamoon (2012) - Saudi Aramco
- [ ] NotPetya (2017) - Ukraine infrastructure
- [ ] Ekans/Snake ransomware (2020) - ICS-aware
- [ ] Colonial Pipeline ransomware (2021)

---

## Category 2: Phishing & Social Engineering

**Purpose**: CIP-003 R2 training, CIP-004 awareness

**Event Types Needed**:

### Phishing Campaign Targeting Utilities
- **Frequency**: How often do we see these? [ ] Monthly  [ ] Quarterly  [ ] Rarely
- **Recent Examples**: (List any recent campaigns you're aware of)
  1. _______________________________
  2. _______________________________
- **Typical Tactics**:
  - [ ] Fake vendor emails (invoices, POs)
  - [ ] Fake utility bills
  - [ ] Job applicant resumes with malware
  - [ ] Fake security alerts
  - [ ] Solar panel/wind turbine vendor impersonation

### CEO Fraud / BEC (Business Email Compromise)
- **Have we experienced this?**: [ ] Yes  [ ] No  [ ] Unsure
- **Typical Scenarios**:
  - [ ] Fake wire transfer requests
  - [ ] Fake W-2 requests
  - [ ] Vendor payment redirect
- **Training Value**: High - financial and credential theft

### Credential Harvesting
- **Targeting**:
  - [ ] VPN credentials
  - [ ] Email credentials
  - [ ] SCADA/HMI access
- **Method**:
  - [ ] Fake login pages
  - [ ] Phishing emails
  - [ ] Watering hole attacks

**How Many Phishing Events Do We Need?**: _____ (Recommend: 3-5 diverse scenarios)

---

## Category 3: Supply Chain Security (CIP-013)

**Purpose**: CIP-013 R1 vendor notification tracking

**Vendor Event Types**:

### Vendor Security Bulletin Events
(One event per vendor security notification)

**Our Critical Vendors** (List all ICS/SCADA/BES vendors):

| Vendor Name | Products We Use | Security Contact | Bulletin Frequency |
|-------------|-----------------|------------------|-------------------|
| Siemens Energy | SCADA system | productcert@siemens.com | Weekly |
| Schneider Electric | _______________ | _______________ | _______________ |
| GE Digital | _______________ | _______________ | _______________ |
| ABB | _______________ | _______________ | _______________ |
| SMA Solar | _______________ | _______________ | _______________ |
| _______________ | _______________ | _______________ | _______________ |
| _______________ | _______________ | _______________ | _______________ |

**How to Get Vendor Bulletins**:
- [ ] Email subscription
- [ ] RSS feeds
- [ ] Vendor portal
- [ ] CISA ICS-CERT aggregates them

**Event Structure for Vendor Bulletins**:
- **Date**: Bulletin release date
- **Info**: "[Vendor] Security Advisory [ID] - [Vulnerability]"
- **Tags**: cip-013, supply-chain, vendor-notification
- **Attributes**: CVE IDs, affected versions, patches
- **Tracking**: Remediation status (identified, testing, deployed)

### Third-Party Compromise Events
(Major supply chain incidents for awareness)

**Examples to Document**:
- [ ] SolarWinds (2020) - affects utilities using SolarWinds
- [ ] Kaseya VSA ransomware (2021) - MSP tools
- [ ] 3CX supply chain attack (2023) - VoIP software
- [ ] Other: _______________________________

---

## Category 4: Incident Response & Tabletop Scenarios (CIP-008)

**Purpose**: CIP-008 R2 testing requirement (every 36 months)

**Scenario Types Needed**:

### Reportable Cyber Security Incidents
(Scenarios that would require E-ISAC reporting within 1 hour)

**Scenario 1**: Compromised BES Cyber System
- Description: Malware detected on EMS server
- Response steps: Isolate, analyze, report to E-ISAC
- Training focus: 1-hour reporting timeline

**Scenario 2**: Attempted Compromise
- Description: IDS alerts on ICS network, blocked connection to known C2
- Response steps: Investigation, evidence collection
- Training focus: When to report vs. when it's just noise

**Scenario 3**: Ransomware on IT Network (could spread to OT)
- Description: Ransomware on corporate network, OT network segmented
- Response steps: Verify isolation, monitor for lateral movement
- Training focus: IT vs. OT incident classification

**How many tabletop scenarios do we need?**: _____ (Recommend: 3-5)

---

## Category 5: Vulnerability Disclosure Events (CIP-010)

**Purpose**: CIP-010 R3 vulnerability assessment tracking

**Event Structure**:
- One MISP event per BES Cyber System vulnerability assessment
- Track 15-month cycle
- Link to CVEs from vendor bulletins

**Covered by Person 3's vulnerability tracking research**
(But you define what vulnerability events should look like)

**Vulnerability Event Template**:
- **Date**: Assessment date
- **Info**: "Vulnerability Assessment - [Asset Type] - [Date]"
- **Tags**: cip-010, vulnerability-assessment, [asset-type]
- **Attributes**:
  - CVE IDs found
  - Severity ratings
  - Affected assets
  - Remediation timeline (35-day CIP-010 R2)

---

## Event Category Summary

| Category | Purpose | Quantity | Priority | CIP Standard |
|----------|---------|----------|----------|--------------|
| ICS/SCADA Attacks | Training | 5-10 | High | CIP-003 |
| Phishing | Training | 3-5 | High | CIP-003, CIP-004 |
| Supply Chain | Vendor tracking | Ongoing | Medium | CIP-013 |
| Incident Response | Tabletop exercises | 3-5 | Medium | CIP-008 |
| Vulnerabilities | Tracking | Ongoing | Medium | CIP-010 |
| **TOTAL TRAINING EVENTS** | | **15-25** | | |

## Event Quality Standards

**Every Event Must Have**:
- [ ] Accurate date
- [ ] Descriptive title ("info" field)
- [ ] Proper distribution (default: Your org only per CIP-011)
- [ ] Analysis level (0=Initial, 1=Ongoing, 2=Complete)
- [ ] Threat level (1=High, 2=Medium, 3=Low, 4=Undefined)
- [ ] At least 3-5 attributes (IOCs, CVEs, etc.)
- [ ] Proper taxonomy tags
- [ ] Links to references (CISA advisories, vendor bulletins)

**For Training Events**:
- [ ] "Lessons learned" in event description
- [ ] Recommendations for prevention/detection
- [ ] Links to related events
- [ ] Galaxy tags (MITRE ATT&CK, threat actors, malware)
```

**Where to Save**: `research/person2/event-categories-definition.md`

---

#### TASK 2.2: Create Event Templates

**Time Estimate**: 2-3 hours

**What to Do**:

Create standardized templates for each event category so events are consistent.

**Deliverable**: Complete the template below

---

**TEMPLATE: MISP Event Templates**

```markdown
# MISP Event Templates for NERC CIP

## Template 1: ICS/SCADA Attack Event

**Use For**: Historical ICS attacks for training

```json
{
  "Event": {
    "date": "YYYY-MM-DD",
    "info": "[Malware Name] - [Brief Description]",
    "threat_level_id": "2",
    "analysis": "2",
    "distribution": "0",
    "published": false,
    "Attribute": [
      {"type": "md5", "category": "Payload delivery", "value": "HASH", "comment": "Malware sample"},
      {"type": "domain", "category": "Network activity", "value": "c2.example.com", "comment": "C2 server"},
      {"type": "ip-dst", "category": "Network activity", "value": "192.0.2.1", "comment": "C2 IP"}
    ],
    "Tag": [
      {"name": "tlp:red"},
      {"name": "cip-003:training"},
      {"name": "sector:energy"},
      {"name": "misp-galaxy:mitre-ics-tactics=\"Impair Process Control\""}
    ]
  }
}
```

**Fields to Customize**:
- date: Incident date
- info: Descriptive title
- Attributes: IOCs (hashes, IPs, domains)
- Tags: Appropriate MITRE ATT&CK for ICS, taxonomies

---

## Template 2: Phishing Campaign Event

**Use For**: Phishing awareness training

```json
{
  "Event": {
    "date": "YYYY-MM-DD",
    "info": "Phishing Campaign Targeting [Sector/Organization]",
    "threat_level_id": "3",
    "analysis": "2",
    "distribution": "0",
    "Attribute": [
      {"type": "email-src", "category": "Payload delivery", "value": "attacker@example.com"},
      {"type": "email-subject", "category": "Payload delivery", "value": "Urgent: Invoice Payment"},
      {"type": "url", "category": "Network activity", "value": "http://fake-login.example.com"},
      {"type": "domain", "category": "Network activity", "value": "fake-login.example.com"}
    ],
    "Tag": [
      {"name": "tlp:amber"},
      {"name": "cip-003:training"},
      {"name": "misp-galaxy:mitre-attack-pattern=\"Phishing - T1566\""}
    ]
  }
}
```

---

## Template 3: Vendor Security Bulletin Event

**Use For**: CIP-013 supply chain tracking

```json
{
  "Event": {
    "date": "YYYY-MM-DD",
    "info": "[Vendor] Security Advisory [ID] - [Vulnerability Title]",
    "threat_level_id": "2",
    "analysis": "1",
    "distribution": "0",
    "Attribute": [
      {"type": "vulnerability", "category": "External analysis", "value": "CVE-2024-XXXXX"},
      {"type": "link", "category": "External analysis", "value": "https://vendor.com/advisory"},
      {"type": "text", "category": "Other", "value": "Affected versions: X.X.X - X.X.X"}
    ],
    "Tag": [
      {"name": "tlp:red"},
      {"name": "cip-013:supply-chain"},
      {"name": "cip-013:vendor-notification"},
      {"name": "workflow:state=\"in-progress\""}
    ]
  }
}
```

**Custom Attributes to Track**:
- Affected products/versions
- Patch availability
- Workarounds
- Remediation deadline (35 days from identification per CIP-010)

---

## Template 4: Incident Response Event

**Use For**: CIP-008 reportable incidents

```json
{
  "Event": {
    "date": "YYYY-MM-DD",
    "info": "Cyber Security Incident - [Brief Description]",
    "threat_level_id": "1",
    "analysis": "0",
    "distribution": "0",
    "Attribute": [
      {"type": "datetime", "category": "Other", "value": "YYYY-MM-DD HH:MM:SS", "comment": "Detection time"},
      {"type": "text", "category": "Other", "value": "BES Cyber System: [Name]", "comment": "Affected system"},
      {"type": "text", "category": "Other", "value": "Initial vector: [Phishing/Malware/Other]"}
    ],
    "Tag": [
      {"name": "tlp:red"},
      {"name": "cip-008:incident-response"},
      {"name": "cip-008:reportable"},
      {"name": "workflow:state=\"ongoing\""}
    ]
  }
}
```

**Incident Workflow Tags**:
- workflow:state="initial" - Just detected
- workflow:state="ongoing" - Investigation in progress
- workflow:state="complete" - Resolved, lessons learned documented

**E-ISAC Reporting**:
- Tag with "eisac:reportable" if meets CIP-008 criteria
- Must report within 1 hour
- Track reporting time in event

---

## Template 5: Vulnerability Assessment Event

**Use For**: CIP-010 R3 tracking

```json
{
  "Event": {
    "date": "YYYY-MM-DD",
    "info": "Vulnerability Assessment - [Asset Type] - [Date]",
    "threat_level_id": "3",
    "analysis": "2",
    "distribution": "0",
    "Attribute": [
      {"type": "text", "category": "Other", "value": "Asset: [Hostname/IP]"},
      {"type": "vulnerability", "category": "External analysis", "value": "CVE-YYYY-XXXXX"},
      {"type": "text", "category": "Other", "value": "Severity: [Critical/High/Medium/Low]"},
      {"type": "text", "category": "Other", "value": "Status: [Identified/Testing/Deployed/Mitigated/Accepted]"}
    ],
    "Tag": [
      {"name": "tlp:red"},
      {"name": "cip-010:vulnerability-assessment"},
      {"name": "cip-010:15-month-cycle"}
    ]
  }
}
```

**Track 15-Month Cycle**:
- One assessment event per BES Cyber System
- Schedule next assessment date (15 months)
- Alert if overdue

**Track 35-Day Patch Cycle**:
- Date vulnerability identified
- 35-day deadline
- Remediation status

---

## Template Usage Guidelines

**When Creating Events**:
1. Choose appropriate template for event type
2. Fill in all fields
3. Add at least 3-5 attributes (IOCs, context)
4. Tag with proper taxonomies
5. Set distribution to "Your organization only" (CIP-011)
6. Link to references (CISA, vendor bulletins)
7. Review before publishing

**Quality Checklist**:
- [ ] Event has descriptive title
- [ ] Date is accurate
- [ ] Distribution is appropriate (default: Your org only)
- [ ] Has 3+ attributes
- [ ] Tagged with NERC CIP taxonomy
- [ ] Tagged with sector:energy (if relevant)
- [ ] Tagged with TLP (traffic light protocol)
- [ ] Has external references
- [ ] Analysis level set correctly
```

**Where to Save**: `research/person2/event-templates.md`

---

### SECTION 2: TAXONOMIES & TAGGING (CIP-011, ALL)

**CIP Requirement**: Must classify BCSI and track compliance per CIP standard

**Current State**: 0 taxonomies enabled (CRITICAL GAP)

**Your Goal**: Define which taxonomies to enable and how to use them

---

#### TASK 2.3: Research and Map Required Taxonomies

**Time Estimate**: 3-4 hours

**What to Research**:

1. **NERC CIP-Required Taxonomies**:
   - TLP (Traffic Light Protocol) - for CIP-011 BCSI classification
   - ICS taxonomy - for CIP-015 ICS event classification
   - Sector taxonomy - for CIP-013 supply chain/vendor classification

2. **Threat Intelligence Taxonomies**:
   - MITRE ATT&CK - attack patterns
   - Adversary - threat actor tracking
   - Malware classification

3. **Workflow Taxonomies**:
   - Workflow - event lifecycle (initial, ongoing, complete)
   - Confidence - confidence level in intelligence

**Deliverable**: Complete the template below

---

**TEMPLATE: Taxonomy Mapping for NERC CIP**

```markdown
# Taxonomy Mapping for NERC CIP Compliance

## Priority 1: REQUIRED Taxonomies (Enable Immediately)

### TLP (Traffic Light Protocol)

**Namespace**: `tlp`
**Purpose**: BCSI classification per CIP-011 R1
**Status**: [ ] Enabled  [ ] Disabled  [✅] MUST ENABLE

**Tags to Use**:
- `tlp:red` - Your organization only (BCSI default per CIP-011)
- `tlp:amber` - Limited distribution (E-ISAC members only)
- `tlp:green` - Community (other utilities)
- `tlp:white` - Public (rarely used for utilities)

**Default for MISP**: `tlp:red` (Your organization only per CIP-011)

**Usage Rules**:
- ALL events default to tlp:red unless explicitly approved for external sharing
- Only CIP Compliance Officer can override
- Track all tlp:amber/green/white events for CIP-011 audit

---

### ICS/SCADA Taxonomy

**Namespace**: `ics` (if available) or create custom `nerc-cip-ics`
**Purpose**: CIP-015 internal monitoring, ICS event classification
**Status**: [ ] Enabled  [ ] Disabled  [✅] MUST ENABLE

**Tags Needed**:
- `ics:asset-type` - Type of ICS device (PLC, RTU, HMI, SCADA, etc.)
- `ics:protocol` - Industrial protocol (Modbus, DNP3, IEC 61850, OPC UA)
- `ics:impact` - Safety, availability, integrity
- `ics:sector` - Energy/electric utilities
- `ics:malware` - ICS-specific malware
- `ics:safety-system` - Affects safety instrumented systems

**Custom ICS Tags** (if not in standard taxonomy):
```
ics:solar-inverter
ics:wind-turbine
ics:battery-management-system
ics:energy-management-system
ics:distribution-management-system
ics:substation-automation
```

**Do we need custom ICS tags?**: [ ] Yes  [ ] No
**If yes, list them**:
1. _______________________________
2. _______________________________
3. _______________________________

---

### Sector Taxonomy (DHS CI/IP Sectors)

**Namespace**: `sector`
**Purpose**: CIP-013 supply chain, sector-specific intelligence
**Status**: [ ] Enabled  [ ] Disabled  [✅] MUST ENABLE

**Tags to Use**:
- `sector:energy` - All our events
- `sector:energy-electric` - Specific to electric utilities
- `sector:critical-infrastructure` - BES Cyber Systems

**Vendor Sector Tags**:
- `sector:it-software` - IT vendors
- `sector:industrial-equipment` - ICS vendors

---

## Priority 2: RECOMMENDED Taxonomies

### MITRE ATT&CK (Attack Patterns)

**Namespace**: `mitre-attack-pattern`
**Purpose**: Map attacks to TTPs
**Status**: [ ] Enabled  [ ] Disabled  [✅] RECOMMENDED

**Most Relevant ATT&CK Patterns for ICS**:
- T1566 - Phishing
- T1078 - Valid Accounts
- T1105 - Ingress Tool Transfer
- T1204 - User Execution
- T1486 - Data Encrypted for Impact (ransomware)

**MITRE ATT&CK for ICS** (separate matrix):
- Check if enabled via galaxies (not taxonomy)
- Critical for CIP-015

---

### Workflow Taxonomy

**Namespace**: `workflow`
**Purpose**: Track event lifecycle
**Status**: [ ] Enabled  [ ] Disabled  [✅] RECOMMENDED

**Tags to Use**:
- `workflow:state="initial"` - Just created, needs analysis
- `workflow:state="ongoing"` - Investigation in progress
- `workflow:state="complete"` - Analysis complete
- `workflow:state="rejected"` - False positive

**Use For**:
- CIP-008 incident tracking (ongoing vs. complete)
- CIP-010 vulnerability tracking (identified → testing → deployed)
- CIP-013 vendor notification tracking

---

### Adversary Taxonomy

**Namespace**: `adversary`
**Purpose**: Threat actor tracking
**Status**: [ ] Enabled  [ ] Disabled  [ ] OPTIONAL

**Relevant Adversary Types**:
- Nation-state (APT groups targeting infrastructure)
- Insider threat
- Cybercriminal (ransomware)
- Hacktivist

**Use For**: Attribution in ICS attack events

---

### Malware Classification

**Namespace**: `malware_classification`
**Purpose**: Categorize malware types
**Status**: [ ] Enabled  [ ] Disabled  [✅] RECOMMENDED

**Relevant Categories**:
- ICS malware
- Ransomware
- Backdoor
- Trojan
- Wiper

---

## Priority 3: CUSTOM NERC CIP Taxonomy (CREATE NEW)

**Namespace**: `nerc-cip`
**Purpose**: CIP-specific event classification
**Status**: [ ] Exists  [✅] NEEDS TO BE CREATED

**Proposed Custom Tags**:

### CIP Standard Tags
```
nerc-cip:cip-003  # Security awareness
nerc-cip:cip-004  # Personnel & training
nerc-cip:cip-005  # Electronic security perimeter
nerc-cip:cip-007  # Systems security management
nerc-cip:cip-008  # Incident response
nerc-cip:cip-010  # Vulnerability assessment
nerc-cip:cip-011  # Information protection (BCSI)
nerc-cip:cip-013  # Supply chain
nerc-cip:cip-015  # Internal network monitoring
```

### Impact Level Tags
```
nerc-cip:low-impact
nerc-cip:medium-impact
nerc-cip:high-impact
```

### Asset Type Tags
```
nerc-cip:bes-cyber-system
nerc-cip:eacms  # Electronic Access Control/Monitoring
nerc-cip:pacs   # Physical Access Control
```

### Compliance Tags
```
nerc-cip:bcsi  # Contains BCSI information
nerc-cip:training  # For security awareness training
nerc-cip:vendor-notification  # CIP-013 vendor alerts
nerc-cip:reportable  # CIP-008 reportable incident
nerc-cip:15-month-cycle  # CIP-010 vulnerability assessments
nerc-cip:35-day-patch  # CIP-010 patch timeline
```

**Should we create this custom taxonomy?**: [✅] YES (highly recommended)

---

## Taxonomy Priority Summary

| Taxonomy | Namespace | Priority | CIP Standard | Status |
|----------|-----------|----------|--------------|--------|
| TLP | tlp | P0 - CRITICAL | CIP-011 | MUST ENABLE |
| ICS | ics | P0 - CRITICAL | CIP-015 | MUST ENABLE |
| Sector | sector | P0 - CRITICAL | CIP-013 | MUST ENABLE |
| NERC CIP | nerc-cip | P0 - CRITICAL | ALL | CREATE NEW |
| Workflow | workflow | P1 - HIGH | CIP-008, CIP-010 | ENABLE |
| MITRE ATT&CK | mitre-attack-pattern | P1 - HIGH | CIP-003 | ENABLE |
| Malware | malware_classification | P1 - HIGH | CIP-003 | ENABLE |
| Adversary | adversary | P2 - MEDIUM | CIP-003 | OPTIONAL |

---

## Tagging Guidelines for Team

**Every Event Must Have** (minimum):
1. One TLP tag (default: `tlp:red`)
2. One or more CIP standard tags (`nerc-cip:cip-XXX`)
3. Sector tag (`sector:energy`)

**Additional Tags** (as applicable):
4. ICS tags (if ICS-related)
5. Workflow tags (for tracking)
6. MITRE ATT&CK tags (for training events)
7. Malware classification (if malware-related)

**Tagging Example** (TRISIS event):
```
Tags:
- tlp:red (BCSI)
- nerc-cip:cip-003 (training)
- nerc-cip:cip-015 (ICS monitoring)
- nerc-cip:training
- sector:energy
- ics:safety-system
- ics:malware
- malware_classification:ics-malware
- misp-galaxy:mitre-ics-tactics="Impair Process Control"
```

---

## Implementation Steps

1. **Enable existing taxonomies** (Person 1 can do this, or request admin access)
2. **Create custom NERC CIP taxonomy** (requires JSON file creation)
3. **Train team on tagging standards** (create quick reference guide)
4. **Audit existing event** (PIPEDREAM) - add missing tags
5. **Tag all future events** per guidelines

---

## Custom Taxonomy JSON Structure

**File to Create**: `nerc-cip.json`
**Location**: `/opt/misp/taxonomies/` (or submit to MISP project)

```json
{
  "namespace": "nerc-cip",
  "description": "NERC CIP (Critical Infrastructure Protection) taxonomy for electric utilities",
  "version": 1,
  "predicates": [
    {
      "value": "cip-standard",
      "expanded": "CIP Standard",
      "description": "NERC CIP standard classification"
    },
    {
      "value": "impact-level",
      "expanded": "Impact Level",
      "description": "BES Cyber System impact rating"
    },
    {
      "value": "asset-type",
      "expanded": "Asset Type",
      "description": "Type of BES Cyber System or asset"
    },
    {
      "value": "compliance",
      "expanded": "Compliance Tracking",
      "description": "Compliance-specific tags"
    }
  ],
  "values": [
    {
      "predicate": "cip-standard",
      "entry": [
        {"value": "cip-003", "expanded": "CIP-003 - Security Management Controls"},
        {"value": "cip-004", "expanded": "CIP-004 - Personnel & Training"},
        {"value": "cip-005", "expanded": "CIP-005 - Electronic Security Perimeter"},
        {"value": "cip-007", "expanded": "CIP-007 - Systems Security Management"},
        {"value": "cip-008", "expanded": "CIP-008 - Incident Response"},
        {"value": "cip-010", "expanded": "CIP-010 - Configuration Change & Vulnerability Management"},
        {"value": "cip-011", "expanded": "CIP-011 - Information Protection"},
        {"value": "cip-013", "expanded": "CIP-013 - Supply Chain Risk Management"},
        {"value": "cip-015", "expanded": "CIP-015 - Internal Network Security Monitoring"}
      ]
    },
    {
      "predicate": "impact-level",
      "entry": [
        {"value": "low", "expanded": "Low Impact BES Cyber System"},
        {"value": "medium", "expanded": "Medium Impact BES Cyber System"},
        {"value": "high", "expanded": "High Impact BES Cyber System"}
      ]
    },
    {
      "predicate": "asset-type",
      "entry": [
        {"value": "bes-cyber-system", "expanded": "BES Cyber System"},
        {"value": "eacms", "expanded": "Electronic Access Control/Monitoring System"},
        {"value": "pacs", "expanded": "Physical Access Control System"}
      ]
    },
    {
      "predicate": "compliance",
      "entry": [
        {"value": "bcsi", "expanded": "Contains BES Cyber System Information"},
        {"value": "training", "expanded": "Security Awareness Training Event"},
        {"value": "vendor-notification", "expanded": "Vendor Security Notification"},
        {"value": "reportable", "expanded": "Reportable Cyber Security Incident"},
        {"value": "15-month-cycle", "expanded": "15-Month Vulnerability Assessment"},
        {"value": "35-day-patch", "expanded": "35-Day Patch Timeline"}
      ]
    }
  ]
}
```

**Who can create this?**: Request Person 1 (admin access) or system administrator
```

**Where to Save**: `research/person2/taxonomy-mapping.md`

---

### SECTION 3: THREAT INTELLIGENCE FEEDS (CIP-005, CIP-015)

**CIP Requirement**: IOCs for ESP monitoring (CIP-005) and internal monitoring (CIP-015)

**Current State**: 11 feeds enabled (good baseline)

**Your Goal**: Identify additional ICS-specific feeds and E-ISAC integration

---

#### TASK 2.4: Research Additional Threat Feeds

**Time Estimate**: 3-4 hours

**What to Research**:

1. **E-ISAC Membership & Feeds**:
   - Are we E-ISAC members?
   - Do they provide MISP feeds?
   - How to access

2. **ICS/SCADA Specific Feeds**:
   - CISA ICS-CERT advisories
   - Dragos WorldView (if we have license)
   - Vendor-specific feeds

3. **Feed Quality Assessment**:
   - Review current 11 feeds
   - Are they providing useful IOCs?
   - Any false positives?

**Deliverable**: Complete the template below

---

**TEMPLATE: Threat Intelligence Feed Assessment**

```markdown
# Threat Intelligence Feed Assessment for NERC CIP

## Current Feeds (11 Enabled)

**Review of Existing Feeds**:

| Feed Name | Relevant to Utilities? | IOC Quality | False Positives | Keep/Remove |
|-----------|----------------------|-------------|-----------------|-------------|
| CIRCL OSINT Feed | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [ ] Keep [ ] Remove |
| Botvrij.eu Data | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [ ] Keep [ ] Remove |
| abuse.ch URLhaus | [✅] High - phishing | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| abuse.ch Feodo Tracker | [✅] High - botnet C2 | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| Blocklist.de All | [✅] High - brute force | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| OpenPhish URL Feed | [✅] High - phishing | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| abuse.ch ThreatFox | [✅] High - ICS malware | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| abuse.ch SSL Blacklist | [✅] Medium - C2 | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| abuse.ch MalwareBazaar | [✅] Medium - malware | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| PhishTank | [✅] High - phishing | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |
| Feodo Tracker (Full) | [✅] High - botnet | [ ] High [ ] Medium [ ] Low | [ ] High [ ] Low | [✅] Keep |

**Feeds to Disable** (if any):
1. _______________________________
2. _______________________________

**Reason for Disabling**:
_________________________________________________________________________

---

## E-ISAC Integration

**E-ISAC Membership Status**:
- [ ] Active member
- [ ] Not a member (strongly recommend joining for CIP compliance)
- [ ] Membership pending
- [ ] Unknown (need to check with management)

**If Active Member**:

**E-ISAC Contact**:
- Organization ID: _______________________________
- Primary Contact: _______________________________
- Email: _______________________________
- Phone: _______________________________

**E-ISAC Intelligence Feeds**:
- [ ] E-ISAC provides MISP feed
- [ ] E-ISAC provides STIX/TAXII feed
- [ ] E-ISAC portal only (manual downloads)
- [ ] Unknown (need to research)

**E-ISAC Feed URL** (if available): _______________________________

**E-ISAC API Key** (if available): _______________________________

**Feed Content**:
- [ ] Electric sector IOCs
- [ ] Incident reports from peer utilities
- [ ] ICS/SCADA vulnerabilities
- [ ] Threat actor intelligence

**Update Frequency**: [ ] Real-time  [ ] Daily  [ ] Weekly  [ ] Unknown

**If Not a Member**:

**Why should we join?**:
- CIP-008 requires incident reporting to E-ISAC (1-hour timeline)
- Sector-specific threat intelligence
- Early warning of threats targeting electric utilities
- Peer intelligence sharing
- Cost: $5,000 - $25,000/year (based on org size)

**Who decides on E-ISAC membership?**: _______________________________

**Budget available?**: [ ] Yes  [ ] No  [ ] Unknown

---

## ICS/SCADA Specific Feeds

### CISA ICS-CERT Advisories

**Feed Type**: RSS/Atom feed
**URL**: https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml
**Current Status**: [ ] Enabled  [✅] NOT ENABLED (need to add)

**Content**:
- ICS/SCADA vulnerabilities
- Solar inverters, wind turbines, battery BMS
- Vendor security advisories aggregated
- Critical for CIP-010 vulnerability tracking

**Recommendation**: [✅] MUST ADD

**How to Add**:
- MISP Feeds → Add Feed → RSS Feed
- Configure to create events for new advisories
- Tag with cip-010, cip-013

---

### Dragos WorldView

**Commercial Vendor**: Dragos, Inc.
**Feed Type**: MISP integration (if licensed)
**Status**: [ ] We have Dragos license  [ ] We do not  [ ] Unknown

**If We Have License**:
- Dragos Platform URL: _______________________________
- API Key: _______________________________
- Contact: _______________________________

**Content**:
- ICS-specific threat intelligence
- ICS threat groups (ELECTRUM, KAMACITE, etc.)
- ICS malware analysis (TRISIS, INDUSTROYER, etc.)
- Very high quality for utilities sector

**Cost**: $50K - $150K/year (enterprise)

**Recommendation**: Worth considering for Medium Impact sites

---

### Vendor Security Feeds

**Our ICS Vendors**:

**Vendor 1: Siemens**
- Security Feed: https://cert-portal.siemens.com/productcert/xml/advisories.xml
- Feed Type: [ ] RSS  [ ] Email  [ ] Portal
- Can integrate into MISP: [ ] Yes  [ ] No  [ ] Research needed

**Vendor 2: Schneider Electric**
- Security Feed: _______________________________
- Feed Type: [ ] RSS  [ ] Email  [ ] Portal
- Can integrate into MISP: [ ] Yes  [ ] No  [ ] Research needed

**Vendor 3: GE Digital**
- Security Feed: _______________________________
- Feed Type: [ ] RSS  [ ] Email  [ ] Portal
- Can integrate into MISP: [ ] Yes  [ ] No  [ ] Research needed

**Additional Vendors**:
(List all ICS vendors we use)
1. _______________________________
2. _______________________________
3. _______________________________

**Integration Method**:
- [ ] Direct RSS feed into MISP
- [ ] Email → Script → MISP event creation
- [ ] Manual copy/paste from vendor portal

---

## Additional Recommended Feeds

### Abuse.ch Feodo SSL

**URL**: https://sslbl.abuse.ch/blacklist/sslblacklist.csv
**Status**: ✅ Already enabled
**Relevance**: C2 server detection at EAPs (CIP-005)

### Tor Exit Nodes

**URL**: https://check.torproject.org/exit-addresses
**Status**: [ ] Enabled  [ ] Not enabled
**Relevance**: Anomalous for ICS networks (CIP-015)
**Recommendation**: [ ] Enable  [ ] Skip (low priority)

### URLScan.io

**URL**: https://urlscan.io/api/v1/search/?q=...
**Status**: [ ] Enabled  [ ] Not enabled
**Relevance**: Phishing URL detection
**Recommendation**: [ ] Enable  [ ] Skip

---

## Feed Management

**Feed Update Schedule**:
- Current: Daily at 02:00 AM (via cron)
- Recommended: [ ] Keep daily  [ ] Change to hourly  [ ] Real-time (if possible)

**Feed Fetch Logs**:
- Location: /opt/misp/logs/misp-daily-maintenance-*.log
- Last successful fetch: Check date in logs
- Any failed feeds: _______________________________

**Feed Performance**:
- Total IOCs ingested: _____ (check MISP stats)
- Average IOCs per day: _____
- Storage usage: _____ GB

**Feed Cleanup**:
- Old IOCs deleted after: _____ days (check MISP settings)
- Recommended retention: 90 days minimum (CIP-007)

---

## Feed Priority Summary

| Feed | Purpose | Priority | CIP Standard | Status |
|------|---------|----------|--------------|--------|
| E-ISAC | Sector intelligence | P0 | CIP-008, CIP-015 | [ ] Enable |
| CISA ICS-CERT | ICS vulnerabilities | P0 | CIP-010, CIP-013 | [ ] Enable |
| Dragos WorldView | ICS threats | P1 | CIP-015 | [ ] Evaluate |
| Siemens/Schneider/GE | Vendor advisories | P1 | CIP-013 | [ ] Configure |
| Existing 11 feeds | General threats | P1 | CIP-005 | ✅ Enabled |
| Tor Exit Nodes | Anomaly detection | P2 | CIP-015 | [ ] Optional |

---

## IOC Export for Firewalls (CIP-005)

**Purpose**: Export MISP IOCs to Electronic Access Point firewalls

**Firewall Integration** (covered by Person 3):
- But you should identify: What IOC types are useful for firewalls?

**Useful IOC Types**:
- [ ] Malicious IPs (block at firewall)
- [ ] Malicious domains (DNS filtering)
- [ ] Known C2 servers
- [ ] Tor exit nodes (optional - may break legitimate use)

**Not Useful for Firewalls**:
- [ ] File hashes (firewall can't inspect)
- [ ] Email addresses (not firewall-level)
- [ ] URLs (need web proxy, not firewall)

**Feed Quality for Firewall Export**:
- Which feeds have high-quality IPs: _______________________________
- Which feeds have too many false positives: _______________________________
```

**Where to Save**: `research/person2/threat-feed-assessment.md`

---

#### TASK 2.5: Define Training Event Content Requirements

**Time Estimate**: 3-4 hours

**What to Research**:

1. **CIP-003 R2 Training Requirements**:
   - Training frequency: 15 months
   - Who needs training: All personnel with BES access
   - Content requirements

2. **Training Scenarios Needed**:
   - ICS/SCADA attacks
   - Phishing awareness
   - Password security
   - Incident reporting
   - BCSI protection

3. **Training Material Generation**:
   - Can we auto-generate from MISP?
   - Who creates training materials?
   - Format (PPT, PDF, video)?

**Deliverable**: Complete the template below

---

**TEMPLATE: Training Content Requirements (CIP-003 R2)**

```markdown
# Security Awareness Training Content Requirements

## CIP-003 R2 Requirements

**Training Frequency**: Every 15 months (CIP-003 R2)

**Personnel Requiring Training**:
- [ ] All employees with BES Cyber System access
- [ ] Contractors with BES access
- [ ] Vendors with remote access
- [ ] Management (awareness level)

**Total Personnel Count**: _____ people

**Training Delivery Method**:
- [ ] In-person classroom
- [ ] Online training platform
- [ ] Video recordings
- [ ] Self-paced with quiz

**Training Duration**: _____ minutes (typical: 45-60 minutes)

---

## Training Topics (Required)

### Topic 1: ICS/SCADA Threat Landscape

**Learning Objectives**:
- Understand threats specific to electric utilities
- Recognize attack vectors targeting ICS/SCADA
- Understand potential impacts (safety, availability)

**MISP Events to Use**:
1. PIPEDREAM (already have)
2. TRISIS/TRITON (need to create)
3. INDUSTROYER (need to create)
4. Stuxnet (need to create)
5. BlackEnergy3 (need to create)

**Training Materials Needed**:
- [ ] PowerPoint slides (10-15 slides)
- [ ] Video (10 minutes)
- [ ] Handout / one-pager
- [ ] Quiz questions (5-10 questions)

**Can we auto-generate from MISP?**: [ ] Yes  [ ] Partial  [ ] No

---

### Topic 2: Phishing Awareness

**Learning Objectives**:
- Identify phishing emails
- Understand social engineering tactics
- Know how to report suspicious emails

**MISP Events to Use**:
1. Phishing campaign targeting utilities (need to create)
2. CEO fraud / BEC example (need to create)
3. Credential harvesting campaign (need to create)

**Training Materials**:
- [ ] Examples of real phishing emails
- [ ] Do's and Don'ts checklist
- [ ] Reporting procedure
- [ ] Quiz with phishing email examples

---

### Topic 3: Password Security & MFA

**Learning Objectives**:
- Understand password requirements (CIP-007 R5)
- Use MFA correctly
- Recognize credential theft attempts

**Content Needed**:
- [ ] Password policy (from Person 1's research)
- [ ] MFA enrollment instructions
- [ ] Password manager usage (if applicable)

---

### Topic 4: Incident Reporting (CIP-008)

**Learning Objectives**:
- Recognize potential cyber security incidents
- Know when and how to report
- Understand reportable vs. non-reportable

**Content Needed**:
- [ ] Incident reporting procedure
- [ ] Contact information (SOC, security team)
- [ ] Examples of incidents to report
- [ ] CIP-008 1-hour reporting timeline (for response team)

---

### Topic 5: BCSI Protection (CIP-011)

**Learning Objectives**:
- Understand what BCSI is
- Know handling requirements
- Protect sensitive information

**Content Needed**:
- [ ] Definition of BCSI
- [ ] Examples of BCSI (asset lists, network diagrams, vulnerability reports)
- [ ] Handling procedures (encryption, access control)
- [ ] Consequences of BCSI exposure

---

## Training Material Generation from MISP

**Quarterly Threat Briefing**:
- Pull events from last quarter
- Generate statistics (top threats, IOCs blocked)
- Create executive summary
- Present to management and personnel

**Annual Training Course**:
- Aggregate events from past 15 months
- Focus on ICS/SCADA events
- Include lessons learned
- Update with latest threats

**Automated vs. Manual**:
- [ ] Fully automated (script generates PPT from MISP)
- [ ] Semi-automated (script generates report, human creates slides)
- [ ] Manual (human reviews MISP, creates training)

**Who Creates Training Materials?**:
- Primary: _______________________________
- Backup: _______________________________

**Training Platform**:
- Platform name: _______________________________
- Can import MISP content: [ ] Yes  [ ] No

---

## Training Evidence for Audit (CIP-003)

**Training Completion Tracking**:
- Where tracked: _______________________________
- Proof of completion: [ ] Certificate  [ ] Quiz score  [ ] Attendance log

**Overdue Training Alerts**:
- 15-month deadline approaching: Alert at _____ months
- Overdue: Alert who? _______________________________

**Audit Evidence**:
- [ ] Training materials (slides, videos)
- [ ] Completion records
- [ ] Quiz results
- [ ] MISP threat intel used in training (event IDs)

---

## Training Event Sample Structure

**Example: Annual Security Awareness Training 2025**

**Slide 1**: Title - "NERC CIP Security Awareness 2025"

**Slide 2**: Threat Landscape Overview
- X attacks targeting utilities in 2024
- Y% increase in ICS targeting
- Source: MISP threat intelligence

**Slides 3-7**: ICS/SCADA Attack Case Studies
- PIPEDREAM (MISP Event ID: 1)
- TRISIS (MISP Event ID: TBD)
- INDUSTROYER (MISP Event ID: TBD)
- Each slide: What happened, How it worked, Lessons learned

**Slides 8-10**: Phishing Examples
- Real phishing emails (sanitized)
- Red flags to look for
- How to report

**Slide 11**: Password Security & MFA
- Password policy reminder
- MFA enrollment (if not done)

**Slide 12**: Incident Reporting
- When to report
- Who to contact
- MISP tracks all incidents

**Slide 13**: BCSI Protection
- What is BCSI
- Handling requirements

**Slide 14**: Quiz (5-10 questions)

**Slide 15**: Resources & Contacts

---

## Training Material Templates

**PowerPoint Template**: _______________________________
**Quiz Template**: _______________________________
**Certificate Template**: _______________________________

**Corporate Branding**: [ ] Required  [ ] Optional

**Where to Store Training Materials**: _______________________________
```

**Where to Save**: `research/person2/training-content-requirements.md`

---

## DELIVERABLES CHECKLIST

By the end of your research, you should have completed:

- [ ] **Task 2.1**: Event Categories Definition (event-categories-definition.md)
- [ ] **Task 2.2**: Event Templates (event-templates.md)
- [ ] **Task 2.3**: Taxonomy Mapping (taxonomy-mapping.md)
- [ ] **Task 2.4**: Threat Feed Assessment (threat-feed-assessment.md)
- [ ] **Task 2.5**: Training Content Requirements (training-content-requirements.md)

**Total Files**: 5 markdown documents
**Total Estimated Time**: 25-30 hours

---

## WHERE TO SAVE YOUR WORK

Create this directory structure:

```
/home/gallagher/misp-install/misp-install/research/person2/
├── event-categories-definition.md
├── event-templates.md
├── taxonomy-mapping.md
├── threat-feed-assessment.md
├── training-content-requirements.md
└── nerc-cip.json (custom taxonomy file)
```

---

## WHO TO CONTACT FOR INFORMATION

**E-ISAC Membership**:
- Contact: _____________________________ (NERC CIP Compliance Officer or management)

**ICS Vendors**:
- Siemens contact: _____________________________
- Schneider contact: _____________________________
- GE contact: _____________________________

**Training Coordinator**:
- Contact: _____________________________ (Who creates security training?)

**Threat Intelligence Sources**:
- Internal SOC/Security Team: _____________________________
- CISA ICS-CERT: https://www.cisa.gov/ics
- E-ISAC: https://www.eisac.com/

---

## TIPS FOR SUCCESS

1. **Start with E-ISAC**: This is the most important feed - find out membership status ASAP
2. **Review the existing PIPEDREAM event**: It's a good example to follow
3. **Focus on ICS/SCADA**: Generic IT threats are lower priority than ICS-specific
4. **Tag Everything**: Proper tagging is critical for CIP compliance tracking
5. **Think Training**: Every event should be usable for CIP-003 R2 training

---

## PRIORITY ORDER

**If short on time, prioritize in this order**:
1. Task 2.3: Taxonomy Mapping (CRITICAL - can't classify events without this)
2. Task 2.4: Threat Feed Assessment (E-ISAC is critical for CIP-008)
3. Task 2.1: Event Categories (defines what we need to create)
4. Task 2.2: Event Templates (makes event creation consistent)
5. Task 2.5: Training Content (important but can be done later)

---

## QUESTIONS?

If you're stuck or need clarification:
1. Review the NERC CIP Audit Report: `docs/NERC_CIP_AUDIT_REPORT.md`
2. Check the NERC CIP Configuration Guide: `docs/NERC_CIP_CONFIGURATION.md`
3. Look at the existing PIPEDREAM event for structure examples
4. Ask the team lead or escalate to me for guidance

---

**Good luck with your research! Your work defines the content that makes MISP valuable.**

**Remember**: Quality over quantity - 5 well-structured events with good IOCs and tags are better than 20 poorly tagged events.

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Assigned To**: Person 2
**Status**: Ready to Start
