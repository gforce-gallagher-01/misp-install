# RESEARCH TASKS - PERSON 3
## Integrations, SIEM, Automation, Workflows

**Focus Areas**: CIP-007 (System Security Management), CIP-008 (Incident Response), CIP-010 (Vulnerability & Patch Management)

**Estimated Research Time**: 30-35 hours

**Objective**: Research and document all requirements for MISP integration with corporate security infrastructure, SIEM platforms, vulnerability management systems, and automated incident response workflows.

---

## Overview

Person 3 is responsible for researching how MISP will integrate with existing security infrastructure and automating compliance workflows. This includes:

- **CIP-007 R4**: Security event log retention (90 days minimum) and SIEM forwarding
- **CIP-008 R1**: Incident response automation and E-ISAC reporting (1-hour requirement)
- **CIP-010 R2**: Patch management workflow (35-day tracking)
- **CIP-010 R3**: Vulnerability assessment tracking (15-month cycle)
- **CIP-005 R2**: Automated IOC export to perimeter security devices
- **CIP-015 R1**: Integration with ICS network monitoring tools

---

## Task 3.1: Document SIEM Platform and Log Forwarding Requirements

**CIP Standard**: CIP-007 R4 (Security Event Monitoring)
**Estimated Time**: 6-8 hours
**Priority**: HIGH

### Research Objectives

1. Identify corporate SIEM platform and current log forwarding infrastructure
2. Document MISP log forwarding requirements (audit logs, user activity, API calls)
3. Define 90-day retention policy implementation
4. Research MISP syslog/CEF/LEEF export capabilities
5. Document parsing rules needed for MISP events in SIEM

### Deliverables

#### 1. SIEM Platform Assessment

**Template**: Copy and complete this assessment

```markdown
# SIEM Platform Assessment

## Current SIEM Platform

**SIEM Vendor**: [ ] Splunk  [ ] QRadar  [ ] ArcSight  [ ] Sentinel  [ ] LogRhythm  [ ] Other: _______

**SIEM Version**: _______________________________

**SIEM Administrator Contact**: _______________________________

**Log Collection Method**:
- [ ] Syslog (UDP 514)
- [ ] Syslog (TCP 514 or custom port: _____)
- [ ] Syslog over TLS (TCP 6514)
- [ ] Agent-based (Splunk Universal Forwarder, QRadar WinCollect, etc.)
- [ ] API integration
- [ ] Other: _______________________________

**Supported Log Formats**:
- [ ] Syslog RFC 3164
- [ ] Syslog RFC 5424
- [ ] CEF (Common Event Format)
- [ ] LEEF (Log Event Extended Format)
- [ ] JSON
- [ ] Custom format

## Current BES Cyber System Logging

**Are domain controllers currently sending logs to SIEM?**: [ ] Yes  [ ] No

**Are ICS workstations currently sending logs to SIEM?**: [ ] Yes  [ ] No

**Are network devices (firewalls, switches) sending logs to SIEM?**: [ ] Yes  [ ] No

**Current log retention period in SIEM**: _______ days

**Does current retention meet 90-day CIP-007 R4 requirement?**: [ ] Yes  [ ] No

## Log Volume Considerations

**Expected MISP log volume**:
- Estimated daily events from MISP: _______ (typical: 1,000-10,000 depending on activity)
- Estimated storage per day: _______ MB

**SIEM capacity available**: [ ] Yes, plenty  [ ] Need to request increase  [ ] Unknown

## Network Path to SIEM

**MISP Server IP**: 192.168.20.54 (misp-test.lan)

**SIEM Log Collector IP/Hostname**: _______________________________

**Network path requires firewall rule?**: [ ] Yes  [ ] No

**Firewall change request needed?**: [ ] Yes  [ ] No

**Network team contact**: _______________________________
```

#### 2. MISP Log Categories to Forward

Document which MISP logs need to be sent to SIEM for CIP-007 compliance:

```markdown
# MISP Logs for SIEM Forwarding

## Required Log Categories (CIP-007 R4)

### 1. Authentication Logs (REQUIRED)
- **File**: `/opt/misp/logs/auth.log` or audit logs
- **Events**: Login attempts, logout, failed authentication, MFA events
- **Retention**: 90 days minimum
- **Volume**: Low (10-100 events/day)

**Sample Event**:
```
2025-10-24 14:23:45 INFO [Auth] User admin@test.local logged in successfully from 192.168.20.100 using MFA
```

### 2. Audit Logs (REQUIRED)
- **File**: `/opt/misp/logs/audit.log`
- **Events**: User actions, event creation/modification, attribute changes, admin actions
- **Retention**: 90 days minimum
- **Volume**: Medium (100-1,000 events/day)

**Sample Event**:
```
2025-10-24 14:25:10 INFO [Audit] User security_analyst@test.local (ID:5) created Event #1234 "Phishing Campaign - GridSec Energy"
```

### 3. BCSI Access Logs (REQUIRED - CIP-011)
- **File**: `/opt/misp/logs/bcsi_access.log` (may need to create)
- **Events**: Access to events tagged with TLP:RED or BCSI-related tags
- **Retention**: 90 days minimum
- **Volume**: Low (10-50 events/day)

**Sample Event**:
```
2025-10-24 14:30:22 INFO [BCSI] User incident_responder@test.local (ID:8) accessed Event #1234 tagged tlp:red, cip-011:bcsi
```

### 4. API Access Logs (REQUIRED)
- **File**: `/opt/misp/logs/api_access.log`
- **Events**: API key usage, automated script access, SIEM queries
- **Retention**: 90 days minimum
- **Volume**: High (1,000-10,000 events/day depending on automation)

**Sample Event**:
```
2025-10-24 14:35:45 INFO [API] API key tseZi6l...CdlT (User ID:3) queried /events/restSearch from 192.168.20.50
```

### 5. Failed Actions / Errors (REQUIRED)
- **File**: `/opt/misp/logs/error.log`
- **Events**: Permission denied, failed operations, system errors
- **Retention**: 90 days minimum
- **Volume**: Low (5-50 events/day)

**Sample Event**:
```
2025-10-24 14:40:12 ERROR [Auth] User readonly@test.local (ID:10) attempted to modify Event #1234 - PERMISSION DENIED
```

### 6. Administrative Actions (REQUIRED)
- **File**: `/opt/misp/logs/admin.log`
- **Events**: User creation/deletion, role changes, system settings changes
- **Retention**: 90 days minimum (recommend 3+ years for compliance)
- **Volume**: Very Low (1-10 events/day)

**Sample Event**:
```
2025-10-24 15:00:00 INFO [Admin] User admin@test.local (ID:1) created new user security_analyst2@test.local with role 'User'
```
```

#### 3. MISP Log Forwarding Configuration

Research and document how to configure MISP to forward logs to SIEM:

**Questions to Answer**:

1. **Does MISP support native syslog forwarding?**
   - Research MISP documentation for built-in syslog capabilities
   - Check if MISP has rsyslog integration
   - Document configuration file locations

2. **What log forwarding method will we use?**
   - Option A: Configure rsyslog on MISP Docker host to forward `/opt/misp/logs/*`
   - Option B: Use Splunk Universal Forwarder (if Splunk is SIEM)
   - Option C: Use SIEM agent (QRadar WinCollect, ArcSight connector, etc.)
   - Option D: Custom script to parse and forward via API

3. **Example rsyslog configuration** (if using syslog):

```bash
# /etc/rsyslog.d/90-misp-forward.conf
# Forward MISP logs to corporate SIEM

# Authentication logs
$InputFileName /opt/misp/logs/auth.log
$InputFileTag misp-auth:
$InputFileStateFile stat-misp-auth
$InputFileSeverity info
$InputFileFacility local5
$InputRunFileMonitor

# Audit logs
$InputFileName /opt/misp/logs/audit.log
$InputFileTag misp-audit:
$InputFileStateFile stat-misp-audit
$InputFileSeverity info
$InputFileFacility local5
$InputRunFileMonitor

# Forward all local5 to SIEM
local5.* @@siem.company.local:514

# Restart rsyslog after configuration
# sudo systemctl restart rsyslog
```

4. **Example Splunk Universal Forwarder configuration** (if using Splunk):

```ini
# /opt/splunkforwarder/etc/system/local/inputs.conf

[monitor:///opt/misp/logs/auth.log]
disabled = false
index = misp_security
sourcetype = misp:auth

[monitor:///opt/misp/logs/audit.log]
disabled = false
index = misp_security
sourcetype = misp:audit

[monitor:///opt/misp/logs/api_access.log]
disabled = false
index = misp_security
sourcetype = misp:api

[monitor:///opt/misp/logs/error.log]
disabled = false
index = misp_security
sourcetype = misp:error

[monitor:///opt/misp/logs/admin.log]
disabled = false
index = misp_security
sourcetype = misp:admin
```

#### 4. SIEM Parsing Rules

Document parsing rules needed for your SIEM platform:

**For Splunk** - Create props.conf and transforms.conf:

```ini
# props.conf
[misp:auth]
SHOULD_LINEMERGE = false
TIME_PREFIX = ^
TIME_FORMAT = %Y-%m-%d %H:%M:%S
TRANSFORMS-misp_auth = misp_auth_extraction

[misp:audit]
SHOULD_LINEMERGE = false
TIME_PREFIX = ^
TIME_FORMAT = %Y-%m-%d %H:%M:%S
TRANSFORMS-misp_audit = misp_audit_extraction

# transforms.conf
[misp_auth_extraction]
REGEX = ^(?<timestamp>[^\s]+\s+[^\s]+)\s+(?<log_level>\w+)\s+\[(?<component>[^\]]+)\]\s+(?<message>.*)
FORMAT = timestamp::$1 log_level::$2 component::$3 message::$4

[misp_audit_extraction]
REGEX = User\s+(?<user_email>[^\s]+)\s+\(ID:(?<user_id>\d+)\)\s+(?<action>.*)
FORMAT = user_email::$1 user_id::$2 action::$3
```

**For QRadar** - Document custom log source type and parsing:

```markdown
# QRadar Custom Log Source Type for MISP

**Log Source Type Name**: MISP Security Platform

**Log Source Type**: Syslog

**Custom Properties to Extract**:
- user_email
- user_id
- action
- event_id
- component
- log_level

**Sample QRadar Custom Property Regex**:
- Property: user_email
  - Regex: `User\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})`
  - Capture Group: 1

- Property: event_id
  - Regex: `Event\s+#(\d+)`
  - Capture Group: 1
```

#### 5. SIEM Use Cases / Correlation Rules

Document SIEM correlation rules needed for CIP compliance monitoring:

```markdown
# MISP SIEM Correlation Rules

## Rule 1: Failed Login Attempts (CIP-007 R5 - Password Management)
**Trigger**: 5+ failed login attempts from same IP in 15 minutes
**Action**: Alert SOC, lock account after 5 failures
**SIEM Search** (Splunk example):
```spl
index=misp_security sourcetype=misp:auth "failed" OR "PERMISSION DENIED"
| stats count by src_ip, user_email
| where count >= 5
```

## Rule 2: Unauthorized BCSI Access Attempt (CIP-011)
**Trigger**: User without BCSI role attempts to access TLP:RED event
**Action**: Alert Compliance team, log for audit
**SIEM Search** (Splunk example):
```spl
index=misp_security sourcetype=misp:error "PERMISSION DENIED"
| search message="*tlp:red*" OR message="*cip-011:bcsi*"
```

## Rule 3: After-Hours Administrative Actions (CIP-004 R4)
**Trigger**: Admin role changes outside business hours (6pm-6am)
**Action**: Alert Security team
**SIEM Search** (Splunk example):
```spl
index=misp_security sourcetype=misp:admin
| eval hour=strftime(_time, "%H")
| where hour < 6 OR hour >= 18
| search action="*role change*" OR action="*created new user*"
```

## Rule 4: Bulk Event Deletion (CIP-008 - Incident Evidence Preservation)
**Trigger**: 10+ events deleted in 1 hour by single user
**Action**: Alert Compliance team - possible evidence tampering
**SIEM Search** (Splunk example):
```spl
index=misp_security sourcetype=misp:audit action="*deleted Event*"
| stats count by user_email
| where count >= 10
```

## Rule 5: API Key Misuse (CIP-007 R4)
**Trigger**: API key used from unauthorized IP or excessive queries
**Action**: Alert Security team, consider rotating key
**SIEM Search** (Splunk example):
```spl
index=misp_security sourcetype=misp:api
| stats count by api_key, src_ip
| where count > 1000
```
```

---

## Task 3.2: Define Vulnerability Assessment Tracking System

**CIP Standard**: CIP-010 R3 (Vulnerability Assessments)
**Estimated Time**: 5-7 hours
**Priority**: HIGH

### Research Objectives

1. Document CIP-010 R3 requirements (15-month vulnerability assessment cycle)
2. Research corporate vulnerability scanning tools (Tenable, Qualys, Rapid7, etc.)
3. Define how MISP will track vulnerabilities affecting ICS/SCADA systems
4. Design workflow for vulnerability disclosure and remediation tracking
5. Research CVE feed integration with MISP

### CIP-010 R3 Requirements Summary

```markdown
# CIP-010 R3 - Vulnerability Assessments

**Requirement**: Perform vulnerability assessments every 15 calendar months

**Scope**: All BES Cyber Systems (Medium Impact)

**Assessment Types**:
1. **Active scanning** - Automated vulnerability scanners (Tenable, Qualys, etc.)
2. **Passive scanning** - Network traffic analysis (Tenable.sc, Dragos, Claroty)
3. **Manual review** - Paper review of ICS vendor advisories

**Compliance Evidence Required**:
- Vulnerability assessment reports dated within last 15 months
- Remediation plan for identified vulnerabilities (or documented risk acceptance)
- Tracking of vulnerability remediation status

**MISP's Role**:
- Track ICS/SCADA vulnerabilities from vendor advisories
- Store assessment results and remediation status
- Provide compliance reporting (when was last assessment? which systems assessed?)
```

### Deliverables

#### 1. Corporate Vulnerability Management Platform Assessment

**Template**: Copy and complete this assessment

```markdown
# Vulnerability Management Platform Assessment

## Current Vulnerability Scanner

**Vendor**: [ ] Tenable Nessus/Security Center  [ ] Qualys VMDR  [ ] Rapid7 InsightVM  [ ] Greenbone  [ ] Other: _______

**Version**: _______________________________

**Administrator Contact**: _______________________________

**Does scanner have network access to ICS environment?**: [ ] Yes  [ ] No  [ ] Partial

**ICS scanning considerations**:
- [ ] We perform active scanning on ICS systems
- [ ] We only do passive scanning on ICS (using network tap)
- [ ] We do manual paper reviews instead of scanning
- [ ] We have separate scanner for IT vs OT environments

## Current Vulnerability Assessment Cycle

**How often do we scan/assess BES Cyber Systems?**:
- [ ] Monthly
- [ ] Quarterly
- [ ] Every 15 months (exactly meeting CIP-010 requirement)
- [ ] Other: _______

**Last vulnerability assessment date**: _______________________________

**Next scheduled assessment date**: _______________________________

**Does this meet 15-month CIP-010 R3 requirement?**: [ ] Yes  [ ] No

## Vulnerability Remediation Tracking

**How do we currently track vulnerability remediation?**:
- [ ] Spreadsheet
- [ ] Ticketing system (ServiceNow, Jira, etc.)
- [ ] Vulnerability scanner's built-in tracking
- [ ] MISP (goal state)
- [ ] Other: _______

**Current remediation SLA**: _______ days (CIP-010 R2 requires 35 days for critical patches)

## ICS Vendor Advisory Tracking

**Do we currently track ICS vendor security advisories?**: [ ] Yes  [ ] No

**Which ICS vendors do we need to monitor?**:
- [ ] Siemens (SIMATIC, SINEC, etc.)
- [ ] Schneider Electric (EcoStruxure, Modicon, etc.)
- [ ] Rockwell Automation (Allen-Bradley, FactoryTalk, etc.)
- [ ] GE Digital (iFix, CIMPLICITY, Proficy)
- [ ] ABB (800xA, Symphony+, etc.)
- [ ] Emerson (DeltaV, Ovation, ROC)
- [ ] SEL (relays, RTUs)
- [ ] Schweitzer Engineering Labs
- [ ] Other: _______________________________

**How do we receive vendor advisories?**:
- [ ] Email subscription
- [ ] ICS-CERT RSS feed
- [ ] Vendor portal (manual check)
- [ ] Not currently tracking (need to implement)
```

#### 2. MISP Vulnerability Tracking Design

Document how MISP will track vulnerabilities:

```markdown
# MISP Vulnerability Tracking Design

## Vulnerability Event Structure

### Event Type: "ICS Vulnerability Disclosure"

**Event Template Fields**:
- **Event Info**: "[CVE-YYYY-####] [Vendor] [Product] - [Vulnerability Title]"
- **Event Date**: Date vulnerability was published
- **Threat Level**: Based on CVSS score (High: 9.0-10.0, Medium: 7.0-8.9, Low: 0.0-6.9)
- **Analysis**:
  - 0 = Initial (just published, no assessment)
  - 1 = Ongoing (assessment in progress)
  - 2 = Complete (remediation plan finalized)
- **Distribution**: Your organization only (CIP-011 BCSI)

### Required Attributes

**Vulnerability Identifiers**:
- CVE ID (e.g., CVE-2024-12345)
- ICS-CERT Advisory ID (e.g., ICSA-24-001-01)
- Vendor Advisory ID (e.g., Siemens SSA-123456)

**Affected Products**:
- Vendor name
- Product name and version (e.g., "Siemens SIMATIC PCS 7 v9.0")
- CPE (Common Platform Enumeration) if available

**Severity**:
- CVSS v3.1 Base Score
- CVSS Vector String
- CVSS Temporal Score (if available)

**Remediation**:
- Patch available? (Yes/No)
- Patch version
- Patch URL
- Workaround available? (text field)

**Internal Tracking** (Custom Attributes):
- Asset inventory check: Do we have affected systems? (Yes/No)
- Number of affected systems
- Remediation status (Not Started / In Progress / Patched / Risk Accepted)
- Remediation due date (35 days from disclosure per CIP-010 R2)
- Ticket ID (link to ServiceNow/Jira ticket)

### Required Tags

- `tlp:amber` (sensitive but shareable within org)
- `cip-010:vulnerability-assessment`
- `cvss-score:high` / `cvss-score:medium` / `cvss-score:low`
- `sector:energy`
- `ics-vendor:[vendor-name]` (e.g., `ics-vendor:siemens`)
- `remediation-status:pending` / `remediation-status:patched` / `remediation-status:risk-accepted`

### Example Event JSON

```json
{
  "Event": {
    "date": "2024-10-15",
    "info": "[CVE-2024-12345] Siemens SIMATIC PCS 7 - Buffer Overflow in Web Server",
    "threat_level_id": "2",
    "analysis": "1",
    "distribution": "0",
    "Attribute": [
      {
        "type": "vulnerability",
        "category": "External analysis",
        "value": "CVE-2024-12345",
        "comment": "Primary CVE identifier"
      },
      {
        "type": "link",
        "category": "External analysis",
        "value": "https://www.cisa.gov/news-events/ics-advisories/icsa-24-001-01",
        "comment": "ICS-CERT Advisory"
      },
      {
        "type": "text",
        "category": "Other",
        "value": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "comment": "CVSS Vector - Score: 9.8 CRITICAL"
      },
      {
        "type": "text",
        "category": "Other",
        "value": "Siemens SIMATIC PCS 7 v9.0 SP2",
        "comment": "Affected product and version"
      },
      {
        "type": "link",
        "category": "External analysis",
        "value": "https://support.industry.siemens.com/cs/document/123456",
        "comment": "Vendor patch download"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Affected systems: 3 HMI workstations at Substation Alpha",
        "comment": "Internal asset inventory check"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Ticket: INC0012345",
        "comment": "ServiceNow incident ticket"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Remediation due: 2024-11-19 (35 days)",
        "comment": "CIP-010 R2 compliance deadline"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Status: In Progress - patch testing in lab environment",
        "comment": "Current remediation status"
      }
    ],
    "Tag": [
      {"name": "tlp:amber"},
      {"name": "cip-010:vulnerability-assessment"},
      {"name": "cvss-score:critical"},
      {"name": "sector:energy"},
      {"name": "ics-vendor:siemens"},
      {"name": "remediation-status:in-progress"}
    ]
  }
}
```

## Vulnerability Assessment Cycle Tracking

MISP can track the 15-month assessment cycle with a scheduled report:

### Dashboard/Report: "CIP-010 R3 Compliance Status"

**Metrics to Display**:

1. **Last Vulnerability Assessment Date**
   - Search for most recent event with tag `cip-010:vulnerability-assessment`
   - Display: "Last assessment: October 15, 2024 (4 months ago)"

2. **Next Assessment Due Date**
   - Calculate: Last assessment + 15 months
   - Display: "Next assessment due: January 15, 2026 (14 months from now)"
   - Status indicator:
     - GREEN: >6 months remaining
     - YELLOW: 3-6 months remaining
     - RED: <3 months remaining (urgent)

3. **Open Vulnerabilities by Severity**
   - CRITICAL (CVSS 9.0-10.0): X vulnerabilities
   - HIGH (CVSS 7.0-8.9): X vulnerabilities
   - MEDIUM (CVSS 4.0-6.9): X vulnerabilities
   - LOW (CVSS 0.1-3.9): X vulnerabilities

4. **Vulnerabilities Past Remediation Deadline**
   - Search for events where "Remediation due date" < today AND status != "Patched"
   - Display: "5 vulnerabilities overdue for remediation (CIP-010 R2 violation)"

5. **Remediation Status Breakdown**
   - Not Started: X
   - In Progress: X
   - Patched: X
   - Risk Accepted: X

## CVE Feed Integration

Research automatic CVE feed ingestion:

**Option 1: CISA ICS-CERT Advisories**
- Feed URL: https://www.cisa.gov/cybersecurity-advisories/ics-advisories
- Format: RSS/XML
- Frequency: As published (several per week)
- MISP sync method: Custom Python script using MISP API

**Option 2: NVD CVE Feed (filtered for ICS)**
- Feed URL: https://services.nvd.nist.gov/rest/json/cves/2.0
- Filter: CPE matches for ICS products
- MISP sync method: PyMISP script with CPE filtering

**Option 3: Commercial ICS Threat Intelligence**
- Dragos WorldView (if licensed)
- Claroty CTD (if licensed)
- Tenable OT Security feed
```

#### 3. Vulnerability Management Workflow

Document the end-to-end workflow:

```markdown
# Vulnerability Management Workflow

## Step 1: Vulnerability Discovered/Published

**Trigger**: ICS-CERT advisory published OR vulnerability scanner finds new CVE

**Actions**:
1. Create MISP event using "ICS Vulnerability Disclosure" template
2. Assign tags: `tlp:amber`, `cip-010:vulnerability-assessment`, CVSS severity
3. Set Analysis = "Initial"

## Step 2: Asset Inventory Check

**Responsible**: IT/OT team

**Actions**:
1. Check asset inventory: Do we have affected systems?
2. Update MISP event with internal reference attributes:
   - "Affected systems: [count] [system types] at [locations]"
   - If not affected: "Affected systems: None - not applicable"
3. If affected, create ticket in ServiceNow/Jira
4. Update MISP event with ticket ID

## Step 3: Risk Assessment

**Responsible**: Security/OT team

**Actions**:
1. Calculate risk: CVSS score + asset criticality + exploitability
2. Determine remediation priority:
   - CRITICAL (CVSS 9-10) + BES Cyber Asset = Immediate (7 days)
   - HIGH (CVSS 7-8.9) + BES Cyber Asset = Urgent (35 days per CIP-010 R2)
   - MEDIUM (CVSS 4-6.9) = Normal (next maintenance window)
   - LOW (CVSS 0-3.9) = Risk accept or next assessment cycle
3. Update MISP event:
   - Set "Remediation due date"
   - Set Analysis = "Ongoing"
   - Add comment with risk assessment justification

## Step 4: Remediation Planning

**Responsible**: OT team + Vendors

**Actions**:
1. Test patch in lab environment (non-production ICS mirror)
2. Coordinate outage window with operations
3. Create detailed change control plan (CAB approval required)
4. Update MISP event:
   - Tag: `remediation-status:in-progress`
   - Add comment: "Patch scheduled for [date] during [outage window]"

## Step 5: Patch Deployment

**Responsible**: OT team

**Actions**:
1. Deploy patch during approved maintenance window
2. Verify system functionality post-patch
3. Update MISP event:
   - Tag: `remediation-status:patched`
   - Add comment: "Patched on [date] - verification successful"
   - Set Analysis = "Complete"

## Step 6: Risk Acceptance (if applicable)

**Responsible**: CIP Compliance Manager + VP Operations

**Actions**:
1. If patch unavailable or too risky to deploy:
   - Document compensating controls (e.g., network segmentation, firewall rules)
   - Obtain formal risk acceptance from management
2. Update MISP event:
   - Tag: `remediation-status:risk-accepted`
   - Add attribute: "Risk acceptance approved by [name] on [date]"
   - Add attribute: "Compensating controls: [description]"
   - Set Analysis = "Complete"

## Step 7: Compliance Reporting

**Responsible**: CIP Compliance Administrator

**Frequency**: Quarterly (before NERC audits)

**Actions**:
1. Generate MISP report: All events tagged `cip-010:vulnerability-assessment` in last 15 months
2. Export to PDF/Excel showing:
   - Vulnerability count by severity
   - Remediation status breakdown
   - Overdue remediation items (CIP-010 R2 violations)
   - Risk acceptances with justification
3. Store report in compliance evidence repository
```

---

## Task 3.3: Design Patch Management Workflow

**CIP Standard**: CIP-010 R2 (Configuration Change Management & Vulnerability Mitigation)
**Estimated Time**: 4-6 hours
**Priority**: HIGH

### Research Objectives

1. Document CIP-010 R2 requirements (35-day patch deployment timeline)
2. Research corporate patch management tools (WSUS, SCCM, Ivanti, etc.)
3. Define how MISP will track security patches affecting BES Cyber Systems
4. Design workflow for emergency patches vs. planned maintenance
5. Document change control integration

### CIP-010 R2 Requirements Summary

```markdown
# CIP-010 R2 - Configuration Change Management

**Key Requirement**: Apply security patches for vulnerabilities within 35 calendar days of availability (OR document compensating controls if patch not available)

**Scope**: BES Cyber Systems (Medium Impact)

**Exceptions**:
- Patch deployment can be delayed if it requires taking BES Cyber Asset out of service
- Must be deployed during next scheduled outage (document justification)

**Compliance Evidence Required**:
- Tracking of security patch releases (when did vendor release patch?)
- Tracking of patch deployment (when did we deploy?)
- Evidence that patches deployed within 35 days OR documented technical/operational reason for delay

**MISP's Role**:
- Track security patch releases from ICS vendors
- Calculate 35-day deadline
- Track patch deployment status
- Generate compliance reports showing on-time vs. delayed patches
```

### Deliverables

#### 1. Corporate Patch Management Platform Assessment

**Template**: Copy and complete this assessment

```markdown
# Patch Management Platform Assessment

## Current Patch Management Tools

**For Windows IT systems**:
- [ ] WSUS (Windows Server Update Services)
- [ ] SCCM (System Center Configuration Manager / Endpoint Configuration Manager)
- [ ] Ivanti Patch Management
- [ ] ManageEngine Patch Manager Plus
- [ ] Other: _______________________________

**For Windows ICS/OT systems**:
- [ ] Same tool as IT environment
- [ ] Separate WSUS/SCCM for OT
- [ ] Manual patching (no automated tool)
- [ ] Vendor-managed (Siemens, Rockwell, etc.)
- [ ] Other: _______________________________

**For ICS controllers/HMIs/embedded devices**:
- [ ] Vendor-specific tools (Siemens TIA Portal, Rockwell FactoryTalk, etc.)
- [ ] Manual firmware updates
- [ ] Never patched (risk accepted)
- [ ] Other: _______________________________

## Patch Management Process

**How often do we patch BES Cyber Systems?**:
- [ ] Monthly (following Microsoft Patch Tuesday)
- [ ] Quarterly
- [ ] Semi-annually
- [ ] As-needed during planned outages
- [ ] Emergency patches only

**Do we have a formal change control process?**: [ ] Yes  [ ] No

**Change control platform**:
- [ ] ServiceNow
- [ ] Jira Service Management
- [ ] Paper-based Change Control Board (CAB)
- [ ] Other: _______________________________

**Typical change control lead time**: _______ days (from request to approval)

**Average outage window for ICS patching**: _______ hours

## 35-Day Compliance Tracking

**Do we currently track the 35-day CIP-010 R2 deadline?**: [ ] Yes  [ ] No

**If yes, how?**:
- [ ] Spreadsheet
- [ ] Ticketing system
- [ ] Patch management tool's built-in tracking
- [ ] Manual tracking by compliance team
- [ ] Not tracked (need to implement)

**Patch deployment timeliness** (estimate):
- Percent of patches deployed within 35 days: _______ %
- Common reasons for delays:
  - [ ] No planned outage within 35 days
  - [ ] Change control approval takes >14 days
  - [ ] Patch testing takes >21 days
  - [ ] Vendor patch not available for our specific version
  - [ ] Risk of patch breaking production system
```

#### 2. MISP Patch Tracking Design

Document how MISP will track security patches:

```markdown
# MISP Security Patch Tracking Design

## Patch Event Structure

### Event Type: "ICS Security Patch Release"

**Event Template Fields**:
- **Event Info**: "[Vendor] [Product] Security Patch - [Month YYYY]"
- **Event Date**: Date patch was released by vendor
- **Threat Level**: Based on vulnerabilities addressed (Critical/High/Medium/Low)
- **Analysis**:
  - 0 = Initial (patch just released)
  - 1 = Ongoing (patch testing or deployment in progress)
  - 2 = Complete (patch deployed OR risk accepted)
- **Distribution**: Your organization only (CIP-011 BCSI)

### Required Attributes

**Patch Identifiers**:
- Vendor patch ID (e.g., "Microsoft KB5012345", "Siemens SSA-123456")
- CVE(s) addressed by patch (reference to vulnerability events)
- Link to vendor patch release notes
- Link to patch download URL

**Affected Systems** (Internal tracking):
- List of affected BES Cyber Systems (from asset inventory)
- Total count of systems requiring patch
- Business unit / substation locations

**CIP-010 R2 Compliance Tracking**:
- **Patch Release Date**: [YYYY-MM-DD]
- **35-Day Deadline**: [Auto-calculated: Release Date + 35 days]
- **Patch Deployment Date**: [YYYY-MM-DD] (updated after deployment)
- **Deployment Status**: Not Started / Testing / Scheduled / Deployed / Risk Accepted
- **Days Remaining**: [Auto-calculated: 35-Day Deadline - Today]
- **Compliance Status**: On-Time / At Risk / Overdue

**Change Control Integration**:
- Change request ticket ID (ServiceNow CHG#, Jira issue)
- CAB approval date
- Scheduled maintenance window date

**Deployment Evidence**:
- Deployment method (SCCM, manual, vendor-managed)
- Deployment verification (screenshot, report, log file)
- Post-deployment testing results

### Required Tags

- `tlp:amber`
- `cip-010:patch-management`
- `patch-status:pending` / `patch-status:deployed` / `patch-status:risk-accepted`
- `patch-priority:critical` / `patch-priority:high` / `patch-priority:medium`
- `sector:energy`
- `ics-vendor:[vendor-name]`

### Example Patch Event JSON

```json
{
  "Event": {
    "date": "2024-10-08",
    "info": "Microsoft Windows Server 2019 - October 2024 Security Updates (KB5012345)",
    "threat_level_id": "2",
    "analysis": "1",
    "distribution": "0",
    "Attribute": [
      {
        "type": "link",
        "category": "External analysis",
        "value": "https://support.microsoft.com/en-us/help/5012345",
        "comment": "Microsoft KB article and download"
      },
      {
        "type": "text",
        "category": "External analysis",
        "value": "CVE-2024-12345, CVE-2024-12346, CVE-2024-12347",
        "comment": "CVEs addressed by this patch"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Patch Release Date: 2024-10-08",
        "comment": "Vendor release date - starts 35-day clock"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "35-Day Deadline: 2024-11-12",
        "comment": "CIP-010 R2 compliance deadline"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Days Remaining: 18 days",
        "comment": "Auto-calculated from deadline"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Affected Systems: 12 Windows Servers (6 HMI, 4 Engineering Workstations, 2 Historians)",
        "comment": "From asset inventory check"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Locations: Substation Alpha (4), Substation Bravo (6), Control Center (2)",
        "comment": "Physical locations requiring deployment"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Change Request: CHG0012345",
        "comment": "ServiceNow change ticket"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "CAB Approval: 2024-10-15",
        "comment": "Change Advisory Board approved deployment"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Scheduled Maintenance: 2024-10-27 02:00-06:00 AM",
        "comment": "Approved outage window"
      },
      {
        "type": "text",
        "category": "Internal reference",
        "value": "Status: Testing - patch deployed to lab environment 2024-10-16, no issues found",
        "comment": "Current deployment status"
      }
    ],
    "Tag": [
      {"name": "tlp:amber"},
      {"name": "cip-010:patch-management"},
      {"name": "patch-status:testing"},
      {"name": "patch-priority:high"},
      {"name": "sector:energy"},
      {"name": "ics-vendor:microsoft"}
    ]
  }
}
```

## Automated Patch Feed Integration

Research automatic ingestion of security patch releases:

**Option 1: Microsoft Security Update Guide API**
- API endpoint for monthly Patch Tuesday releases
- Filter for Windows Server versions in use
- Auto-create MISP events for relevant patches
- Calculate 35-day deadline automatically

**Option 2: ICS Vendor Security Bulletin RSS Feeds**
- Siemens ProductCERT: https://new.siemens.com/global/en/products/services/cert.html
- Schneider Electric Security Notifications
- Rockwell Automation Security Advisories
- Parse RSS/XML and create MISP events

**Option 3: CISA ICS-CERT Advisories** (may include patch info)
- Already covered in Task 3.2 (vulnerability tracking)
- Link patch events to vulnerability events

## Patch Management Dashboard

Create MISP dashboard for patch compliance:

**Metrics to Display**:

1. **Patches Approaching Deadline** (Yellow: <7 days, Red: Overdue)
   - "5 patches due within 7 days"
   - "2 patches overdue (CIP-010 R2 violation)"

2. **Patch Deployment Status Breakdown**
   - Not Started: X
   - Testing: X
   - Scheduled: X
   - Deployed: X
   - Risk Accepted: X

3. **Compliance Rate**
   - "87% of patches deployed within 35 days (Q3 2024)"
   - Trend chart: monthly compliance percentage

4. **Patches by Priority**
   - Critical: X patches
   - High: X patches
   - Medium: X patches
   - Low: X patches

5. **Recent Patch Deployments** (last 30 days)
   - List of recently completed patches with deployment dates
```

#### 3. Patch Management Workflow

Document the end-to-end workflow:

```markdown
# Patch Management Workflow (CIP-010 R2)

## Step 1: Patch Released by Vendor

**Trigger**: Vendor publishes security patch (Microsoft Patch Tuesday, ICS vendor advisory, etc.)

**Actions**:
1. Create MISP event using "ICS Security Patch Release" template
2. Set "Patch Release Date" = today (starts 35-day clock)
3. Calculate "35-Day Deadline" = Release Date + 35 days
4. Link to related vulnerability event(s) if applicable
5. Tag: `patch-status:pending`, `patch-priority:[critical/high/medium/low]`

**Automation**: Consider Python script that monitors vendor RSS feeds and auto-creates MISP events

## Step 2: Asset Inventory Check (Within 24 hours)

**Responsible**: IT/OT team

**Actions**:
1. Check asset inventory: Which BES Cyber Systems are affected?
2. Update MISP event with:
   - List of affected systems (hostnames, IP addresses)
   - Total count
   - Business units / physical locations
3. If no systems affected: Tag as `patch-status:not-applicable`, set Analysis = Complete

## Step 3: Criticality Assessment (Within 48 hours)

**Responsible**: Security team + OT team

**Actions**:
1. Review CVEs addressed by patch (critical? exploited in the wild?)
2. Assess impact of NOT patching (risk calculation)
3. Assess impact of patching (downtime, potential system instability)
4. Determine patch priority:
   - **CRITICAL**: Addresses active exploits, patch immediately (emergency change)
   - **HIGH**: Addresses serious vulnerabilities, deploy within 35 days (standard)
   - **MEDIUM**: Non-critical security improvements, deploy at next maintenance
   - **LOW**: Optional updates, defer to quarterly patching cycle
5. Update MISP event with risk assessment notes

## Step 4: Patch Testing (Days 1-14)

**Responsible**: OT team

**Actions**:
1. Deploy patch to lab/test environment (non-production mirror of ICS)
2. Test system functionality:
   - HMI screens load correctly?
   - Process control functions work?
   - Historian data logging continues?
   - Network connectivity stable?
3. Document testing results in MISP event:
   - "Patch tested on 2024-10-16 in Lab Environment - No issues found"
   - OR: "Patch testing revealed issue: [description] - Investigating workaround"
4. Update tag: `patch-status:testing`

## Step 5: Change Control Request (Days 7-21)

**Responsible**: OT team

**Actions**:
1. Create change request in ServiceNow/Jira:
   - Change type: Standard (if within 35 days) or Emergency (if immediate)
   - Description: "Deploy [patch name] to address [CVE numbers]"
   - Systems affected: [list from MISP]
   - Risk assessment: Attach testing results
   - Outage duration: [estimate]
2. Submit to Change Advisory Board (CAB) for approval
3. Update MISP event:
   - Attribute: "Change Request: CHG0012345"
   - Wait for CAB approval (typically next weekly CAB meeting)

## Step 6: Schedule Maintenance Window (Days 14-30)

**Responsible**: Operations team + OT team

**Actions**:
1. After CAB approval, schedule maintenance window:
   - Coordinate with operations (avoid high-demand periods)
   - Typical windows: Weekend nights, planned outages, low-load periods
2. Update MISP event:
   - Attribute: "CAB Approval: [date]"
   - Attribute: "Scheduled Maintenance: [date] [start time]-[end time]"
   - Tag: `patch-status:scheduled`
3. Ensure maintenance is scheduled BEFORE 35-day deadline

## Step 7: Deploy Patch (Day of Maintenance)

**Responsible**: OT team

**Actions**:
1. During approved maintenance window:
   - Take system backup (pre-patch state)
   - Deploy security patch
   - Reboot if required
   - Verify system functionality
   - Monitor for 1-2 hours post-patch
2. Document deployment:
   - Screenshots of patch installation
   - SCCM/WSUS deployment report
   - Post-deployment verification checklist
3. Update MISP event:
   - Attribute: "Patch Deployment Date: [YYYY-MM-DD]"
   - Attribute: "Deployment Method: [SCCM / Manual / Vendor-managed]"
   - Attribute: "Deployment Verification: Successful - all systems operational"
   - Tag: `patch-status:deployed`
   - Set Analysis = "Complete"
4. Update ServiceNow change ticket: "Implemented - Successful"

## Step 8: Risk Acceptance (If Patch Cannot Be Deployed)

**Trigger**: Patch deployment delayed beyond 35 days OR patch causes system instability

**Responsible**: CIP Compliance Manager + VP Operations

**Actions**:
1. Document reason patch cannot be deployed:
   - Technical reason: "Patch breaks HMI connectivity to PLCs (tested in lab)"
   - Operational reason: "No planned outage available within 35 days due to peak demand season"
2. Document compensating controls:
   - Network segmentation (block malicious traffic)
   - Firewall rules (restrict vulnerable services)
   - Enhanced monitoring (IDS signatures for exploit attempts)
3. Obtain formal risk acceptance from management
4. Update MISP event:
   - Attribute: "Risk Acceptance: Approved by [VP name] on [date]"
   - Attribute: "Reason: [technical/operational justification]"
   - Attribute: "Compensating Controls: [description]"
   - Attribute: "Patch deferred to: [next outage date]"
   - Tag: `patch-status:risk-accepted`
   - Set Analysis = "Complete"
5. Store risk acceptance documentation in compliance repository

## Step 9: Compliance Reporting (Quarterly)

**Responsible**: CIP Compliance Administrator

**Actions**:
1. Generate MISP report: All patch events from last quarter
2. Calculate metrics:
   - Total patches released: X
   - Patches deployed within 35 days: X (Y%)
   - Patches deployed with delay (>35 days): X
   - Patches with risk acceptance: X
3. For delayed/risk-accepted patches:
   - Export detailed justifications and compensating controls
4. Generate executive summary for NERC audit evidence
5. Store report in compliance evidence repository
```

---

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

## Task 3.7: Define Automated Backup Requirements

**CIP Standard**: CIP-009 R2 (Recovery Plans for BES Cyber Systems)
**Estimated Time**: 3-4 hours
**Priority**: LOW

### Research Objectives

1. Document CIP-009 backup requirements (recovery plan, backup testing)
2. Define MISP backup schedule and retention
3. Research MISP backup methods (database, files, configurations)
4. Define disaster recovery procedures

### Deliverables

#### 1. CIP-009 Compliance Assessment

**Template**: Copy and complete this assessment

```markdown
# CIP-009 R2 - BES Cyber System Recovery Plans

**Requirement**: Backup and recovery plan for BES Cyber Systems

**MISP as a BES Cyber Asset**:
- [ ] MISP is classified as a BES Cyber Asset (if used for incident response on BES systems)
- [ ] MISP is NOT a BES Cyber Asset (IT system only)

**If MISP is a BES Cyber Asset, CIP-009 requires**:
- Documented backup procedure
- Backup frequency (at least annually, but daily/weekly recommended)
- Backup retention policy
- Recovery procedure testing (at least once every 15 months)
- Backup storage location (off-site or alternate location)

**Current MISP Backup Status**:
- **Are MISP backups currently performed?**: [ ] Yes  [ ] No
- **If yes, backup frequency**: [ ] Daily  [ ] Weekly  [ ] Monthly  [ ] Other: _______
- **Backup retention**: _______ days/months
- **Backup storage location**: _______________________________
- **Last backup test date**: _______________________________
```

#### 2. MISP Backup Design

Document comprehensive MISP backup strategy:

```markdown
# MISP Backup and Recovery Design

## What to Backup

### 1. MISP Database (PostgreSQL or MySQL)
**Contains**:
- All events, attributes, tags
- User accounts and roles
- Organization data
- Correlation data

**Criticality**: HIGHEST - Contains all threat intelligence

**Backup method**:
```bash
# PostgreSQL backup (if using PostgreSQL)
docker exec misp-db-1 pg_dump -U misp misp > /backup/misp-db-$(date +%Y%m%d).sql

# MySQL backup (if using MySQL)
docker exec misp-db-1 mysqldump -u misp -p misp > /backup/misp-db-$(date +%Y%m%d).sql
```

### 2. MISP Configuration Files
**Contains**:
- `/opt/misp/.env` - Environment variables (BASE_URL, ADMIN_EMAIL, etc.)
- `/opt/misp/docker-compose.yml` - Container orchestration config
- `/opt/misp/PASSWORDS.txt` - Admin credentials (store securely!)

**Criticality**: HIGH - Required to restore MISP with same settings

**Backup method**:
```bash
tar -czf /backup/misp-config-$(date +%Y%m%d).tar.gz /opt/misp/.env /opt/misp/docker-compose.yml /opt/misp/PASSWORDS.txt
```

### 3. MISP Uploaded Files
**Contains**:
- `/opt/misp/files/` - Malware samples, PDFs, screenshots uploaded to events
- Potentially contains BCSI (CIP-011 sensitive data)

**Criticality**: MEDIUM - Can be re-uploaded if lost, but time-consuming

**Backup method**:
```bash
tar -czf /backup/misp-files-$(date +%Y%m%d).tar.gz /opt/misp/files/
```

### 4. MISP Custom Scripts and Integrations
**Contains**:
- Custom automation scripts (Task 3.1-3.6)
- PyMISP scripts for SIEM, firewall, ICS tool integration
- Cron jobs

**Criticality**: MEDIUM - Can be recreated, but development effort required

**Backup method**:
```bash
tar -czf /backup/misp-scripts-$(date +%Y%m%d).tar.gz /opt/misp/scripts/ /etc/cron.d/misp*
```

## Automated Backup Script

```bash
#!/bin/bash
# /opt/misp/scripts/misp-backup.sh
# Automated daily MISP backup for CIP-009 compliance

BACKUP_DIR="/mnt/backup/misp"
RETENTION_DAYS=90
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

echo "Starting MISP backup - $(date)"

# 1. Backup MySQL database
echo "Backing up database..."
docker exec misp-db-1 mysqldump -u misp -p'PASSWORD_FROM_ENV' misp | gzip > $BACKUP_DIR/misp-db-$DATE.sql.gz

# 2. Backup configuration files
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/misp-config-$DATE.tar.gz /opt/misp/.env /opt/misp/docker-compose.yml /opt/misp/PASSWORDS.txt

# 3. Backup uploaded files
echo "Backing up uploaded files..."
tar -czf $BACKUP_DIR/misp-files-$DATE.tar.gz /opt/misp/files/

# 4. Backup custom scripts
echo "Backing up scripts..."
tar -czf $BACKUP_DIR/misp-scripts-$DATE.tar.gz /opt/misp/scripts/

# 5. Generate backup manifest (for verification)
echo "Generating manifest..."
cat > $BACKUP_DIR/misp-manifest-$DATE.txt <<EOF
MISP Backup - $DATE
-------------------
Database: $(ls -lh $BACKUP_DIR/misp-db-$DATE.sql.gz)
Config: $(ls -lh $BACKUP_DIR/misp-config-$DATE.tar.gz)
Files: $(ls -lh $BACKUP_DIR/misp-files-$DATE.tar.gz)
Scripts: $(ls -lh $BACKUP_DIR/misp-scripts-$DATE.tar.gz)
EOF

# 6. Copy to off-site backup location (CIP-009 requirement)
echo "Copying to off-site location..."
rsync -avz $BACKUP_DIR/ backup-server.company.local:/backup/misp/

# 7. Cleanup old backups (retain 90 days)
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "misp-*" -mtime +$RETENTION_DAYS -delete

echo "MISP backup completed - $(date)"
```

**Deployment**:
```bash
chmod +x /opt/misp/scripts/misp-backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/misp/scripts/misp-backup.sh >> /var/log/misp-backup.log 2>&1" | crontab -
```

## Recovery Procedures

### Scenario 1: Full MISP Server Failure

**Recovery Steps**:

1. **Provision new server** (same OS, same IP if possible)

2. **Install Docker and Docker Compose**:
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# Install Docker Compose
apt-get install -y docker-compose
```

3. **Restore MISP configuration files**:
```bash
# Copy backup to new server
rsync -avz backup-server.company.local:/backup/misp/misp-config-YYYYMMDD.tar.gz /tmp/

# Extract configuration
cd /opt
tar -xzf /tmp/misp-config-YYYYMMDD.tar.gz
```

4. **Deploy MISP containers**:
```bash
cd /opt/misp
docker-compose up -d
```

5. **Wait for containers to start** (check with `docker ps`)

6. **Restore database**:
```bash
# Copy database backup
rsync -avz backup-server.company.local:/backup/misp/misp-db-YYYYMMDD.sql.gz /tmp/

# Restore database
gunzip /tmp/misp-db-YYYYMMDD.sql.gz
cat /tmp/misp-db-YYYYMMDD.sql | docker exec -i misp-db-1 mysql -u misp -p'PASSWORD' misp
```

7. **Restore uploaded files**:
```bash
rsync -avz backup-server.company.local:/backup/misp/misp-files-YYYYMMDD.tar.gz /tmp/
tar -xzf /tmp/misp-files-YYYYMMDD.tar.gz -C /opt/misp/
```

8. **Restore custom scripts**:
```bash
rsync -avz backup-server.company.local:/backup/misp/misp-scripts-YYYYMMDD.tar.gz /tmp/
tar -xzf /tmp/misp-scripts-YYYYMMDD.tar.gz -C /
```

9. **Restart MISP**:
```bash
cd /opt/misp
docker-compose restart
```

10. **Verify recovery**:
- Access MISP web interface: https://misp-test.lan
- Login with admin credentials
- Check event count matches pre-disaster count
- Verify API access works
- Test integrations (SIEM, firewall, ICS tool)

**Recovery Time Objective (RTO)**: 4-8 hours
**Recovery Point Objective (RPO)**: 24 hours (based on daily backups)

### Scenario 2: Database Corruption

If MISP database corrupted but server is functional:

```bash
# Stop MISP
cd /opt/misp && docker-compose stop misp-core misp-modules

# Restore database from last good backup
gunzip /backup/misp/misp-db-YYYYMMDD.sql.gz
cat /backup/misp/misp-db-YYYYMMDD.sql | docker exec -i misp-db-1 mysql -u misp -p'PASSWORD' misp

# Restart MISP
docker-compose start misp-core misp-modules
```

### Scenario 3: Accidental Event Deletion

MISP soft-deletes events (recoverable):

```
Admin > List Events > Include deleted events > Restore event
```

If permanently deleted, restore from database backup (Scenario 2).

## Backup Testing (CIP-009 R2.2)

**Requirement**: Test recovery plan at least once every 15 calendar months

**Test Procedure**:

1. **Schedule test** (coordinate with operations, minimize disruption)

2. **Provision test environment**:
   - Separate VM/server (NOT production)
   - Use production backups

3. **Perform full recovery** (follow Scenario 1 steps)

4. **Validate recovered MISP**:
   - Login with admin account
   - Verify event count matches production
   - Query API for test event
   - Check taxonomies and galaxies enabled
   - Test SIEM log forwarding
   - Test firewall IOC export

5. **Document test results**:
   - Test date
   - Backup date used
   - Recovery time (actual)
   - Issues encountered
   - Lessons learned

6. **Store documentation** (CIP-009 compliance evidence)

**Last recovery test**: _______________________________ (update after testing)
**Next recovery test due**: _______________________________ (15 months from last test)
```

---

## Summary of Person 3 Tasks

| Task | CIP Standard | Priority | Estimated Time | Key Deliverables |
|------|-------------|----------|----------------|------------------|
| 3.1 | CIP-007 R4 | HIGH | 6-8 hours | SIEM platform assessment, MISP log forwarding config, parsing rules, correlation rules |
| 3.2 | CIP-010 R3 | HIGH | 5-7 hours | Vulnerability assessment tracking, MISP event templates, 15-month cycle dashboard |
| 3.3 | CIP-010 R2 | HIGH | 4-6 hours | Patch management workflow, 35-day deadline tracking, change control integration |
| 3.4 | CIP-008 R1 | HIGH | 6-8 hours | E-ISAC reporting automation, incident response playbooks, SOAR integration plan |
| 3.5 | CIP-005 R2 | MEDIUM | 4-5 hours | Firewall IOC export, EDL configuration, quality control procedures |
| 3.6 | CIP-015 R1 | MEDIUM | 5-6 hours | ICS monitoring tool integration, bi-directional threat intelligence sharing |
| 3.7 | CIP-009 R2 | LOW | 3-4 hours | Automated backup script, disaster recovery procedures, backup testing plan |
| **TOTAL** | | | **33-44 hours** | Complete integration architecture for MISP |

## Next Steps After Research Completion

After Person 3 completes all research tasks:

1. **Schedule team meeting** with Person 1, Person 2, and Person 3 to present findings

2. **Consolidate requirements** into single implementation plan

3. **Begin implementation phase**:
   - Week 1-2: Quick wins (enable taxonomies, configure SIEM forwarding, enable backups)
   - Week 3-6: Core integrations (vulnerability tracking, patch management, firewall IOC export)
   - Week 7-10: Advanced automation (incident response playbooks, SOAR integration, ICS tool integration)
   - Week 11-12: Testing and documentation (CIP-009 recovery testing, E-ISAC reporting test, final compliance audit)

4. **Track implementation progress** in MISP (dogfooding!)

5. **Conduct final NERC CIP compliance audit** to verify 95-100% readiness

---

## Questions for Person 3 to Answer

As you complete each task, document answers to these questions:

### SIEM Integration (Task 3.1)
- [ ] What is our corporate SIEM platform?
- [ ] Does it support syslog/CEF input for MISP logs?
- [ ] What is the SIEM administrator contact info?
- [ ] Do we need a firewall rule change for MISP → SIEM connectivity?

### Vulnerability Management (Task 3.2)
- [ ] What vulnerability scanner do we use?
- [ ] How often do we scan BES Cyber Systems?
- [ ] When was the last vulnerability assessment?
- [ ] Which ICS vendors do we need to monitor for advisories?

### Patch Management (Task 3.3)
- [ ] What patch management tool do we use (WSUS, SCCM, etc.)?
- [ ] What is our typical change control lead time?
- [ ] What percentage of patches are deployed within 35 days currently?
- [ ] What is our change control platform (ServiceNow, Jira, etc.)?

### Incident Response (Task 3.4)
- [ ] Are we a member of E-ISAC?
- [ ] Who is our E-ISAC primary contact?
- [ ] Do we currently meet the 1-hour reporting requirement?
- [ ] Do we have a SOAR platform?

### Firewall Integration (Task 3.5)
- [ ] What firewall vendor do we use?
- [ ] Does firewall support External Dynamic Lists (EDL)?
- [ ] Does firewall currently consume threat intelligence feeds?
- [ ] Who is the firewall administrator?

### ICS Monitoring (Task 3.6)
- [ ] Do we have dedicated ICS/OT network monitoring?
- [ ] Which vendor (Dragos, Claroty, Nozomi, etc.)?
- [ ] Does it support STIX/TAXII integration?
- [ ] What is the typical alert volume?

### Backup and Recovery (Task 3.7)
- [ ] Is MISP classified as a BES Cyber Asset?
- [ ] Are MISP backups currently performed?
- [ ] Where are backups stored (off-site requirement)?
- [ ] When was the last recovery test?

---

## Useful References for Person 3

- **MISP Log Files**: `/opt/misp/logs/` (auth.log, audit.log, error.log)
- **MISP API Documentation**: https://www.misp-project.org/openapi/
- **PyMISP Documentation**: https://pymisp.readthedocs.io/
- **NERC CIP Standards**: https://www.nerc.com/pa/Stand/Pages/CIPStandards.aspx
- **E-ISAC Website**: https://www.eisac.com/
- **MISP Integrations**: https://www.misp-project.org/tools/

---

**Document Version**: 1.0
**Created**: 2024-10-24
**For**: MISP NERC CIP Medium Impact Compliance Project
**Estimated Completion Time**: 33-44 hours of research
