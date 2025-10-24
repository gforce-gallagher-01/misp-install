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

