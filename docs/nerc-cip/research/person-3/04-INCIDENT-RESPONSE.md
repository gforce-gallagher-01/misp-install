## Task 3.4: Plan Incident Response Automation

**CIP Standard**: CIP-008 R1 (Incident Reporting and Response Planning)
**Estimated Time**: 6-8 hours
**Priority**: HIGH

### Research Objectives

1. Document CIP-008 requirements (incident response plan, 1-hour E-ISAC reporting)
2. Research E-ISAC reporting requirements and portal access
3. Define how MISP will be used during incident response
4. Design automated playbooks for common incident types
5. Research SOAR integration (Splunk SOAR, IBM Resilient, etc.)

### CIP-008 Requirements Summary

```markdown
# CIP-008 - Incident Reporting and Response Planning

**Key Requirements**:

**R1.1**: Document incident response plan with:
- Roles and responsibilities
- Incident classification criteria
- Response procedures by incident type

**R1.2**: Test incident response plan at least once every 15 calendar months by:
- Performing a paper drill, tabletop exercise, or operational exercise
- Including any lessons learned

**R1.3**: Update incident response plan within 180 days of:
- Completing incident response plan test/exercise
- Changing roles/responsibilities
- Changing incident response procedures

**R2**: Determine if event is a Reportable Cyber Security Incident

**R3.1**: Report Reportable Cyber Security Incidents to E-ISAC within **1 hour** of determination

**R3.2**: Report Reportable Cyber Security Incidents to affected entities (interconnections) within 1 hour

**MISP's Role**:
- Document incidents as MISP events
- Track incident timeline (detection, containment, reporting)
- Generate E-ISAC report automatically
- Store incident response evidence (IOCs, forensics, remediation)
- Track lessons learned
```

### Deliverables

#### 1. E-ISAC Reporting Assessment

**Template**: Copy and complete this assessment

```markdown
# E-ISAC Integration Assessment

## E-ISAC Membership Status

**Are we a member of E-ISAC (Electricity ISAC)?**: [ ] Yes  [ ] No  [ ] Don't know

**If yes**:
- **E-ISAC Portal URL**: https://www.eisac.com (or specific portal link)
- **Primary E-ISAC Contact**: _______________________________
- **E-ISAC Contact Email**: _______________________________
- **E-ISAC Member ID**: _______________________________

**If no**:
- **Action Required**: Join E-ISAC (required for NERC CIP-008 R3 compliance)
- **Membership coordinator contact**: _______________________________

## E-ISAC Reporting Methods

**How do we currently report to E-ISAC?**:
- [ ] Web portal (manual form submission)
- [ ] Email to E-ISAC SOC
- [ ] Phone call to E-ISAC hotline
- [ ] API integration (automated)
- [ ] Not currently reporting (need to implement)

**E-ISAC reporting requirements**:
- **Timeline**: Within 1 hour of determining incident is reportable
- **Information required**:
  - Incident date/time
  - Incident classification (from CIP-008)
  - Affected BES Cyber Systems
  - Impact on BES reliability
  - Known IOCs (IP addresses, domains, malware hashes)
  - Remediation status

## 1-Hour Reporting Compliance

**Current process for 1-hour reporting**:
- [ ] Security Analyst detects incident → Escalates to Incident Manager → Incident Manager files E-ISAC report
- [ ] Automated alert from SIEM → Auto-creates E-ISAC report draft in MISP
- [ ] Not currently automated (manual process every time)

**Average time from detection to E-ISAC report filing**: _______ minutes

**Do we currently meet 1-hour requirement?**: [ ] Yes  [ ] No  [ ] Sometimes

**Pain points in current process**:
- [ ] Determining if incident is "reportable" takes too long
- [ ] Gathering required information takes too long
- [ ] E-ISAC portal is slow/difficult to use
- [ ] After-hours incidents (no one available to file report)
- [ ] Other: _______________________________
```

#### 2. MISP Incident Response Event Structure

Document how MISP will be used during incident response:

```markdown
# MISP Incident Response Event Structure

## Event Type: "Cyber Security Incident"

**Event Template Fields**:
- **Event Info**: "[Incident ID] - [Incident Type] - [Brief Description]"
- **Event Date**: Date/time incident was detected
- **Threat Level**: High (all incidents are high severity)
- **Analysis**:
  - 0 = Initial (incident just detected, investigation ongoing)
  - 1 = Ongoing (containment in progress)
  - 2 = Complete (incident resolved, lessons learned documented)
- **Distribution**: Your organization only (CIP-011 BCSI)

### Required Attributes

**Incident Metadata**:
- Incident ID (e.g., "INC-2024-001")
- Incident Type (see classification below)
- Detection date/time
- Reporting date/time (to E-ISAC)
- Resolution date/time

**Incident Classification** (from CIP-008 R2):
A Reportable Cyber Security Incident is one that has compromised or disrupted:
1. One or more BES Cyber Systems
2. Electronic Access Control or Monitoring Systems (EACMS)
3. Physical Access Control Systems (PACS)

Types:
- [ ] Malware infection
- [ ] Unauthorized access / compromise
- [ ] Denial of service
- [ ] Data theft / exfiltration
- [ ] Configuration change (unauthorized)
- [ ] Failed attempt (no compromise but reportable)

**Affected Systems**:
- List of impacted BES Cyber Systems
- IP addresses / hostnames
- Physical locations (substations, control centers)

**Indicators of Compromise (IOCs)**:
- Malware hashes (MD5, SHA-1, SHA-256)
- C2 domains / IP addresses
- Suspicious file paths
- Malicious email addresses
- Phishing URLs

**Timeline** (CIP-008 compliance tracking):
- Detection time: [YYYY-MM-DD HH:MM:SS]
- Incident Manager notified: [YYYY-MM-DD HH:MM:SS]
- Determined reportable: [YYYY-MM-DD HH:MM:SS]
- E-ISAC report filed: [YYYY-MM-DD HH:MM:SS] **[MUST BE <1 hour from determination]**
- Containment achieved: [YYYY-MM-DD HH:MM:SS]
- Eradication completed: [YYYY-MM-DD HH:MM:SS]
- Systems restored: [YYYY-MM-DD HH:MM:SS]
- Incident closed: [YYYY-MM-DD HH:MM:SS]

**Impact Assessment**:
- Did incident affect BES reliability? (Yes/No)
- If yes, describe impact: [text field]
- Estimated duration of impact: [minutes/hours]
- Load shed / generation loss: [MW] (if applicable)

**Response Actions Taken**:
- Containment measures (isolated systems, blocked IPs, etc.)
- Forensic evidence collected
- Remediation steps
- Lessons learned

**Reporting**:
- E-ISAC report ID
- E-ISAC report filed by: [name]
- E-ISAC confirmation received: [YYYY-MM-DD HH:MM:SS]
- Neighboring utilities notified: [list]

### Required Tags

- `tlp:red` (highly sensitive incident data)
- `cip-008:incident`
- `incident-type:[malware/unauthorized-access/dos/data-theft/config-change]`
- `incident-status:detection` → `containment` → `eradication` → `recovery` → `closed`
- `sector:energy`
- `misp-galaxy:mitre-attack-pattern` (if applicable, e.g., "T1059 - Command Line Interface")

### Example Incident Event JSON

```json
{
  "Event": {
    "date": "2024-10-24",
    "info": "[INC-2024-001] - Malware Infection - Ransomware on HMI Workstation",
    "threat_level_id": "1",
    "analysis": "1",
    "distribution": "0",
    "Attribute": [
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Incident ID: INC-2024-001",
        "comment": "Primary incident tracking number"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Incident Type: Malware infection (ransomware)",
        "comment": "CIP-008 incident classification"
      },
      {
        "type": "datetime",
        "category": "Internal reference",
        "value": "2024-10-24T14:23:00Z",
        "comment": "Detection time: Alert from antivirus"
      },
      {
        "type": "datetime",
        "category": "Internal reference",
        "value": "2024-10-24T14:35:00Z",
        "comment": "Incident Manager notified (12 minutes after detection)"
      },
      {
        "type": "datetime",
        "category": "Internal reference",
        "value": "2024-10-24T14:45:00Z",
        "comment": "Determined reportable: BES Cyber System compromised (22 minutes after detection)"
      },
      {
        "type": "datetime",
        "category": "Internal reference",
        "value": "2024-10-24T15:12:00Z",
        "comment": "E-ISAC report filed (27 minutes after determination - COMPLIANT)"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Affected System: HMI-ALPHA-01 (192.168.10.50) - Substation Alpha",
        "comment": "Compromised BES Cyber System"
      },
      {
        "type": "md5",
        "category": "Payload delivery",
        "value": "5d41402abc4b2a76b9719d911017c592",
        "comment": "Ransomware executable hash"
      },
      {
        "type": "domain",
        "category": "Network activity",
        "value": "c2.ransomware-gang.com",
        "comment": "C2 domain for ransomware"
      },
      {
        "type": "ip-dst",
        "category": "Network activity",
        "value": "203.0.113.45",
        "comment": "C2 IP address"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Impact: HMI workstation taken offline for forensics. No impact to BES operations - backup HMI used.",
        "comment": "Impact assessment"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Containment: 1) Isolated HMI from network. 2) Blocked C2 domain at firewall. 3) Scanned all other systems - no additional infections found.",
        "comment": "Response actions taken"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "E-ISAC Report ID: EISAC-2024-10-24-001",
        "comment": "E-ISAC confirmation number"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Forensics: Memory dump and disk image captured. Investigating initial infection vector.",
        "comment": "Evidence preservation"
      }
    ],
    "Tag": [
      {"name": "tlp:red"},
      {"name": "cip-008:incident"},
      {"name": "incident-type:malware"},
      {"name": "incident-status:containment"},
      {"name": "sector:energy"},
      {"name": "misp-galaxy:ransomware-galaxy:lockbit"}
    ]
  }
}
```

## Incident Classification Decision Tree

Help responders quickly determine if incident is reportable:

```
START: Potential security event detected

Q1: Does the event involve a BES Cyber System, EACMS, or PACS?
  → NO: Not reportable under CIP-008 (may still be handled as IT incident)
  → YES: Continue to Q2

Q2: Was there unauthorized access OR attempted unauthorized access?
  → YES: REPORTABLE → File E-ISAC report within 1 hour
  → NO: Continue to Q3

Q3: Was there disruption or degradation of BES Cyber System functionality?
  → YES: REPORTABLE → File E-ISAC report within 1 hour
  → NO: Continue to Q4

Q4: Was there successful malware infection (even if contained)?
  → YES: REPORTABLE → File E-ISAC report within 1 hour
  → NO: Continue to Q5

Q5: Was there data exfiltration or suspected data theft?
  → YES: REPORTABLE → File E-ISAC report within 1 hour
  → NO: NOT REPORTABLE (but document in MISP for tracking)

RESULT: REPORTABLE INCIDENT
  → Create MISP event immediately
  → Assign Incident Manager
  → Gather required information (IOCs, affected systems, impact)
  → File E-ISAC report (1-hour clock starts when determination made)
```

Store this decision tree in MISP as a training event or reference document.

## E-ISAC Report Generation (Automated)

Design MISP export format for E-ISAC reporting:

**Option 1: Manual (current state)**
- Incident Responder manually fills out E-ISAC web portal form
- Copy/paste information from MISP event

**Option 2: Semi-Automated (quick win)**
- MISP generates pre-filled E-ISAC report text
- Incident Manager copies report text and submits to E-ISAC portal

**Option 3: Fully Automated (future state)**
- MISP integrates with E-ISAC API (if available)
- One-click "File E-ISAC Report" button in MISP
- Automatically submits required fields to E-ISAC portal

**MISP E-ISAC Report Template** (for semi-automated approach):

```
REPORTABLE CYBER SECURITY INCIDENT - NERC CIP-008

Organization: [ORGANIZATION NAME]
E-ISAC Member ID: [MEMBER_ID]

INCIDENT DETAILS:
- Incident ID: [INC-ID from MISP]
- Detection Date/Time: [YYYY-MM-DD HH:MM:SS UTC]
- Report Date/Time: [YYYY-MM-DD HH:MM:SS UTC]

INCIDENT CLASSIFICATION:
- Incident Type: [Malware / Unauthorized Access / DoS / Data Theft / Config Change]
- Affected Asset Type: [BES Cyber System / EACMS / PACS]

AFFECTED SYSTEMS:
- [List from MISP event attributes]

IMPACT ASSESSMENT:
- BES Reliability Impact: [Yes/No]
- [Impact description from MISP]

INDICATORS OF COMPROMISE:
- Malware Hashes: [List MD5/SHA256 from MISP]
- C2 Domains/IPs: [List from MISP]
- Other IOCs: [List from MISP]

RESPONSE ACTIONS:
- Containment: [From MISP event]
- Remediation Status: [Ongoing / Complete]

ADDITIONAL INFORMATION:
- [Any additional context from MISP event]

CONTACT:
- Incident Manager: [Name, Phone, Email]

--- End of Report ---
This report was generated from MISP Event ID: [EVENT_ID]
```

## Incident Response Playbooks

Document automated playbooks for common incident types:

### Playbook 1: Malware Detection on BES Cyber System

**Trigger**: Antivirus alert on domain controller, HMI, or engineering workstation

**Automated Actions** (via SOAR or MISP automation):
1. Create MISP incident event automatically from SIEM alert
2. Populate IOCs: malware hash, file path, affected hostname
3. Check if affected system is BES Cyber System (query asset inventory)
4. If BES Cyber System: Set incident as "Reportable", notify Incident Manager
5. Query MISP for known information about malware hash
6. Generate containment recommendations:
   - Isolate system from network (script to disable switch port)
   - Block malware hash at all EDR agents
   - Block C2 domains/IPs at firewall
7. Start 1-hour countdown timer for E-ISAC reporting

**Manual Steps** (Incident Manager):
1. Review MISP event with auto-populated data
2. Confirm incident is reportable (decision tree)
3. Execute containment actions
4. File E-ISAC report using MISP-generated template
5. Update MISP event with E-ISAC report ID and timeline

### Playbook 2: Unauthorized Access Detected

**Trigger**: Failed login attempts followed by successful login from unusual location

**Automated Actions**:
1. Create MISP incident event from SIEM correlation rule
2. Populate: username, source IP, affected system
3. Check if affected system is BES Cyber System
4. If BES Cyber System: Set incident as "Reportable", notify Incident Manager
5. Query threat intelligence: Is source IP known malicious?
6. Generate containment recommendations:
   - Disable compromised user account
   - Block source IP at firewall
   - Force password reset for all privileged accounts

**Manual Steps**:
1. Review account activity (what did attacker access?)
2. Check for data exfiltration or lateral movement
3. File E-ISAC report
4. Perform forensic investigation

### Playbook 3: Denial of Service Against Control Center

**Trigger**: Network monitoring detects flood of traffic to control center

**Automated Actions**:
1. Create MISP incident event from IDS alert
2. Populate: source IPs, target systems, traffic volume
3. Determine if BES Cyber System affected
4. If BES Cyber System degraded: Set incident as "Reportable"
5. Generate containment recommendations:
   - Block source IPs at perimeter firewall
   - Enable rate limiting
   - Engage ISP for upstream filtering

**Manual Steps**:
1. Assess impact on BES operations
2. File E-ISAC report if BES reliability impacted
3. Coordinate with ISP/network team for mitigation
```

#### 3. SOAR Integration Research

Research Security Orchestration, Automation, and Response (SOAR) platforms:

```markdown
# SOAR Platform Assessment

## Current SOAR Platform

**Do we have a SOAR platform?**: [ ] Yes  [ ] No  [ ] Don't know

**If yes, which vendor?**:
- [ ] Splunk SOAR (formerly Phantom)
- [ ] IBM Security Resilient (IBM SOAR)
- [ ] Palo Alto Cortex XSOAR
- [ ] Microsoft Sentinel (built-in SOAR)
- [ ] Swimlane
- [ ] Other: _______________________________

**SOAR Administrator**: _______________________________

## MISP Integration Capabilities

**Does our SOAR platform have a MISP integration?**: [ ] Yes  [ ] No  [ ] Unknown

**Integration capabilities needed**:
- [ ] Create MISP event from SOAR playbook
- [ ] Query MISP for IOC enrichment
- [ ] Update MISP event with incident response progress
- [ ] Export MISP IOCs to firewall/EDR
- [ ] Generate E-ISAC report from MISP event

**If no SOAR platform**:
- Recommend implementing SOAR for CIP-008 compliance
- MISP + SOAR = Faster incident response = Meeting 1-hour E-ISAC requirement

## Automation Opportunities

**High-value automations for CIP-008**:
1. Auto-create MISP incident event when SIEM alert fires
2. Auto-populate IOCs from EDR/firewall logs
3. Auto-determine if incident is reportable (decision tree logic)
4. Auto-notify Incident Manager via SMS/email
5. Auto-generate E-ISAC report draft
6. Auto-block malicious IPs/domains at firewall
7. Auto-disable compromised user accounts
8. Auto-start 1-hour countdown timer with alerts
```

---

