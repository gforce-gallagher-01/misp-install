# NERC CIP Implementation Guide

**Purpose**: Step-by-step guide for implementing NERC CIP compliance features in MISP
**Compliance Target**: 95-100% Medium Impact compliance
**Last Updated**: 2025-10-25
**Version**: 1.0

This guide provides detailed implementation instructions for achieving NERC CIP Medium Impact compliance with the MISP Installation Suite.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Quick Wins (Week 1)](#phase-1-quick-wins-week-1)
4. [Phase 2: Core Infrastructure (Weeks 2-4)](#phase-2-core-infrastructure-weeks-2-4)
5. [Phase 3: Advanced Features (Weeks 5-8)](#phase-3-advanced-features-weeks-5-8)
6. [Phase 4: Audit Preparation (Weeks 9-12)](#phase-4-audit-preparation-weeks-9-12)
7. [Feature-to-CIP Mapping](#feature-to-cip-mapping)
8. [Evidence Collection](#evidence-collection)
9. [Validation Procedures](#validation-procedures)
10. [Audit Checklist](#audit-checklist)

---

## Overview

### Current State

**Compliance Score**: 35/100 (baseline audit: 2025-10-24)

**Critical Findings**:
- ❌ No MFA (CIP-004 R4)
- ❌ No taxonomies enabled (CIP-011)
- ❌ Development environment in production
- ❌ Default sharing settings (CIP-011 violation)
- ✅ 11 threat feeds enabled
- ✅ Docker containers healthy

**Full Audit**: See `docs/nerc-cip/AUDIT_REPORT.md`

---

### Target State

**Compliance Score**: 95-100/100

**Timeline**: 12 weeks (4 phases)

**Team Effort**:
- Research completed: 78-99 hours (3 team members)
- Implementation: ~200 hours total
- Testing & validation: ~40 hours
- Audit preparation: ~20 hours

---

### CIP Standards Coverage

| Standard | Title | Current | Target |
|----------|-------|---------|--------|
| CIP-003 | Security Management | 40% | 95% |
| CIP-004 | Personnel & Training | 30% | 95% |
| CIP-005 | Electronic Security Perimeter | 35% | 95% |
| CIP-007 | Systems Security Management | 40% | 95% |
| CIP-008 | Incident Reporting | 25% | 95% |
| CIP-009 | Recovery Plans | 45% | 95% |
| CIP-010 | Configuration Management | 30% | 95% |
| CIP-011 | Information Protection | 25% | 95% |
| CIP-013 | Supply Chain Risk | 20% | 90% |
| CIP-015 | Internal Network Security | 10% | 90% |

---

## Prerequisites

### Completed Research

Ensure all 3 team members have completed their research:

- [ ] **Person 1**: Auth & Access Control (20-25 hours)
  - Document: `docs/nerc-cip/research/person-1/AUTH-ACCESS-CONTROL.md`
  - Deliverables: Azure AD plan, 6 user roles, password policy

- [ ] **Person 2**: Events & Threat Intelligence (25-30 hours)
  - Document: `docs/nerc-cip/research/person-2/EVENTS-THREAT-INTEL.md`
  - Deliverables: 15-25 training events, 5 attack templates, E-ISAC plan

- [ ] **Person 3**: Integrations & Automation (33-44 hours)
  - Documents: `docs/nerc-cip/research/person-3/` (8 files)
  - Deliverables: SIEM config, vulnerability tracking, patch mgmt, incident response

### System Requirements

- [ ] MISP installation complete (v5.6+)
- [ ] Docker containers healthy
- [ ] API access working
- [ ] Backup system configured
- [ ] Test environment available

### Documentation Review

- [ ] Read `docs/nerc-cip/README.md` (compliance overview)
- [ ] Read `docs/nerc-cip/AUDIT_REPORT.md` (current state)
- [ ] Read `docs/nerc-cip/PRODUCTION_READINESS_TASKS.md` (20-task checklist)
- [ ] Review architecture docs in `docs/nerc-cip/architecture/`

---

## Phase 1: Quick Wins (Week 1)

**Goal**: 35% → 55% compliance (+20%)
**Time**: 4-6 hours
**Priority**: HIGH (fast compliance improvement)

### Task 1.1: Enable NERC CIP Taxonomies (30 min)

**CIP Requirement**: CIP-011 R1 (BCSI protection)

**Implementation**:
```bash
# 1. Check current taxonomies
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
     https://localhost/taxonomies/index.json | jq '.[] | select(.enabled==true)'

# 2. Enable NERC CIP-specific taxonomies
python3 scripts/enable-nerc-cip-taxonomies.py

# 3. Verify
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
     https://localhost/taxonomies/index.json | \
     jq '.[] | select(.namespace | contains("cip"))'
```

**Required Taxonomies**:
- `cip-011` - BCSI classification
- `tlp` - Traffic Light Protocol
- `ics` - ICS/SCADA specific
- `mitre-attack-pattern` - ATT&CK for ICS

**Validation**:
- [ ] Taxonomies appear in MISP web UI
- [ ] Can tag events with CIP taxonomies
- [ ] Default event template includes BCSI tags

**Evidence**: Screenshot of enabled taxonomies

---

### Task 1.2: Change Environment to Production (15 min)

**CIP Requirement**: CIP-007 R1 (secure configuration)

**Implementation**:
```bash
# 1. Update MISP config
sudo docker exec misp-misp-core-1 \
     sed -i "s/'debug' => 2/'debug' => 0/" \
     /var/www/MISP/app/Config/config.php

# 2. Set production environment
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
     -X POST https://localhost/servers/serverSettings/edit/debug \
     -d '{"value": "0"}'

# 3. Restart container
sudo docker restart misp-misp-core-1
```

**Validation**:
- [ ] MISP shows no debug output
- [ ] Error messages sanitized (no stack traces to users)
- [ ] Logs show "Production mode" active

**Evidence**: Configuration screenshot, log entry

---

### Task 1.3: Fix Default Distribution Settings (10 min)

**CIP Requirement**: CIP-011 R1.2 (control BCSI sharing)

**Implementation**:
```python
from lib.misp_config import set_misp_setting
from lib.misp_api_helpers import get_api_key

api_key = get_api_key()

# Set default distribution to "Your organization only"
set_misp_setting(api_key, 'MISP.default_event_distribution', '0')
set_misp_setting(api_key, 'MISP.default_attribute_distribution', '0')

# Disable automatic publishing
set_misp_setting(api_key, 'MISP.unpublishedprivate', '1')
```

**Validation**:
- [ ] New events default to org-only distribution
- [ ] New attributes default to org-only
- [ ] Events not auto-published

**Evidence**: Settings screenshot, test event creation

---

### Task 1.4: Enable Credential Protection (5 min)

**CIP Requirement**: CIP-004 R4 (access management)

**Implementation**:
```bash
# Enable password complexity requirements
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
     -X POST https://localhost/servers/serverSettings/edit/Security.password_policy_complexity \
     -d '{"value": "/^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{12,}$/"}'

# Set password minimum length
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
     -X POST https://localhost/servers/serverSettings/edit/Security.password_policy_length \
     -d '{"value": "12"}'

# Enable password expiration (90 days)
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
     -X POST https://localhost/servers/serverSettings/edit/Security.password_expiration_in_days \
     -d '{"value": "90"}'
```

**Validation**:
- [ ] Password complexity enforced (test with weak password)
- [ ] Minimum 12 characters required
- [ ] Password expiration set to 90 days

**Evidence**: Password policy settings, failed weak password attempt

---

### Task 1.5: Create Additional User Accounts (30 min)

**CIP Requirement**: CIP-004 R3 (access control)

**Implementation**: Use findings from Person 1's research

**User Roles** (from research):
1. `cip-admin` - Full administrative access
2. `cip-analyst` - Read/write threat intelligence
3. `cip-viewer` - Read-only access
4. `cip-publisher` - Publish/share events
5. `cip-auditor` - Audit log access only
6. `cip-automation` - API/automation account

**Script**:
```python
# scripts/create-cip-users.py
from lib.misp_api_helpers import get_api_key, misp_add_user

api_key = get_api_key()

users = [
    {'email': 'cip-admin@org.com', 'role_id': 1, 'org_id': 1},
    {'email': 'cip-analyst@org.com', 'role_id': 3, 'org_id': 1},
    {'email': 'cip-viewer@org.com', 'role_id': 5, 'org_id': 1},
    # ... remaining users
]

for user in users:
    result = misp_add_user(api_key, user)
    print(f"Created: {user['email']}")
```

**Validation**:
- [ ] All 6 user roles created
- [ ] Appropriate permissions assigned
- [ ] Users can login
- [ ] Access restrictions working

**Evidence**: User list screenshot, access control matrix

---

### Task 1.6: Install Utilities Dashboards (20 min)

**CIP Requirement**: CIP-015 R1 (internal network monitoring)

**Implementation**:
```bash
# Already installed in base system (v5.6)
# Verify installation
ls -la widgets/utilities-sector/

# If not installed:
sudo python3 phases/phase_11_11_utilities_dashboards.py
```

**Validation**:
- [ ] 25 widgets installed
- [ ] Dashboards accessible in MISP
- [ ] Widgets display ICS/OT threat data

**Evidence**: Dashboard screenshot

---

### Task 1.7: Add Training Events (2 hours)

**CIP Requirement**: CIP-003 R2 (security awareness training)

**Implementation**: Use findings from Person 2's research

**Script**:
```python
# scripts/create-training-events.py
from lib.misp_api_helpers import get_api_key, misp_add_event
from datetime import datetime, timedelta

api_key = get_api_key()

# Training event templates (from Person 2's research)
training_events = [
    {
        'info': 'Phishing Awareness - ICS Environment',
        'date': (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        'threat_level_id': 2,
        'tags': ['cip-003:training', 'phishing', 'ics:awareness']
    },
    {
        'info': 'TRISIS Malware Analysis - ICS Attack Case Study',
        'date': (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        'threat_level_id': 1,
        'tags': ['cip-003:training', 'ics:malware', 'ics:attack-target="safety-system"']
    },
    # ... remaining 3 events
]

for event in training_events:
    event_data = {'Event': event}
    result = misp_add_event(api_key, event_data)
    print(f"Created training event: {event['info']}")
```

**Required Events** (minimum 5):
1. Phishing awareness (ICS context)
2. ICS malware case study (TRISIS)
3. Password security best practices
4. Incident reporting procedures
5. Insider threat awareness

**Validation**:
- [ ] 5+ training events created
- [ ] Tagged with `cip-003:training`
- [ ] Searchable by users
- [ ] Content relevant to ICS/OT

**Evidence**: Event list, event details screenshots

---

### Phase 1 Summary

**Compliance Impact**: 35% → 55% (+20%)

**Time Investment**: 4-6 hours

**Deliverables**:
- [x] NERC CIP taxonomies enabled
- [x] Production mode active
- [x] BCSI protection configured
- [x] Password policy enforced
- [x] 6 user roles created
- [x] Utilities dashboards installed
- [x] 5 training events created

**Next Phase**: Core Infrastructure (authentication, logging, monitoring)

---

## Phase 2: Core Infrastructure (Weeks 2-4)

**Goal**: 55% → 75% compliance (+20%)
**Time**: 3 weeks
**Priority**: HIGH (foundational systems)

### Task 2.1: Implement MFA (Week 2)

**CIP Requirement**: CIP-004 R4 (multi-factor authentication)

**Options** (from Person 1's research):
1. **Azure AD SSO** (recommended for enterprise)
2. **TOTP** (Google Authenticator, Authy)
3. **LDAP + MFA**

**Implementation** (Azure AD example):
```bash
# See Person 1's research for complete Azure AD integration plan
# docs/nerc-cip/research/person-1/AUTH-ACCESS-CONTROL.md

# 1. Configure Azure AD app registration
# 2. Install SAML plugin for MISP
# 3. Configure MISP SAML settings
# 4. Test login flow

python3 scripts/configure-azure-ad-sso.py
```

**Validation**:
- [ ] MFA required for all users
- [ ] Login requires 2 factors
- [ ] Failed login attempts logged
- [ ] Session timeout configured

**Evidence**: MFA configuration, login flow screenshots, audit logs

**Time**: 20-30 hours

---

### Task 2.2: Configure SIEM Log Forwarding (Week 2)

**CIP Requirement**: CIP-007 R4 (90-day log retention)

**Implementation**: Use Person 3's SIEM research

**Script**:
```bash
# From research: docs/nerc-cip/research/person-3/01-SIEM-INTEGRATION.md

python3 scripts/configure-siem-forwarding.py \
    --siem-type splunk \
    --siem-host siem.company.local \
    --siem-port 514 \
    --protocol syslog

# Configure retention
python3 scripts/set-log-retention.py --days 90
```

**Validation**:
- [ ] Logs forwarded to SIEM
- [ ] 90-day retention configured
- [ ] All required log types included
- [ ] Log integrity verified

**Evidence**: SIEM configuration, retention policy, log samples

**Time**: 12-16 hours

---

### Task 2.3: Set Up Vulnerability Tracking (Week 3)

**CIP Requirement**: CIP-010 R3 (vulnerability assessment - 15 months)

**Implementation**: Use Person 3's vulnerability tracking research

**Script**:
```python
# From research: docs/nerc-cip/research/person-3/02-VULNERABILITY-TRACKING.md

python3 scripts/configure-vulnerability-tracking.py
```

**Workflow**:
1. Import CVE feeds for ICS vendors
2. Tag events with affected systems
3. Track remediation status
4. Generate 15-month compliance report

**Validation**:
- [ ] CVE feeds configured
- [ ] Vulnerability events tracked
- [ ] 15-month assessment cycle active
- [ ] Reports generated

**Evidence**: Vulnerability tracking dashboard, assessment schedule

**Time**: 10-14 hours

---

### Task 2.4: Create User Roles (Week 3)

**CIP Requirement**: CIP-004 R3 (role-based access control)

**Implementation**: Expand Task 1.5 with detailed permissions

**6 Defined Roles** (from Person 1's research):
1. **CIP Administrator** - Full access
2. **Security Analyst** - Read/write threat intel
3. **Read-Only Viewer** - View events only
4. **Publisher** - Publish/share events
5. **Auditor** - Audit logs only
6. **Automation** - API access only

**Script**:
```python
# scripts/configure-cip-roles.py
# Implements detailed permission matrix from Person 1's research

python3 scripts/configure-cip-roles.py
```

**Validation**:
- [ ] All roles defined
- [ ] Permissions tested
- [ ] Access control matrix documented
- [ ] Quarterly review scheduled

**Evidence**: Role definitions, permission matrix, test results

**Time**: 8-12 hours

---

### Task 2.5: Enable E-ISAC Feed (Week 4)

**CIP Requirement**: CIP-003 R1 (security awareness), CIP-008 R1 (incident reporting)

**Implementation**: Use Person 2's E-ISAC feed research

**Script**:
```python
# From research: docs/nerc-cip/research/person-2/EVENTS-THREAT-INTEL.md

python3 scripts/enable-eisac-feed.py \
    --api-key YOUR_EISAC_API_KEY \
    --feed-url https://eisac.feed.url/api
```

**Validation**:
- [ ] E-ISAC feed enabled
- [ ] Events importing correctly
- [ ] Tags applied automatically
- [ ] Feed health monitoring active

**Evidence**: Feed configuration, imported events

**Time**: 6-8 hours

---

### Task 2.6: Configure 90-Day Log Retention (Week 4)

**CIP Requirement**: CIP-007 R4 (log retention)

**Implementation**:
```bash
# Configure logrotate for 90-day retention
python3 scripts/configure-log-retention.py --days 90

# Set up automated cleanup
python3 scripts/schedule-log-cleanup.py
```

**Validation**:
- [ ] Logs retained for 90 days
- [ ] Automated cleanup configured
- [ ] Disk space monitoring active
- [ ] Log integrity checks passing

**Evidence**: Retention configuration, cleanup schedule, disk usage report

**Time**: 4-6 hours

---

### Phase 2 Summary

**Compliance Impact**: 55% → 75% (+20%)

**Time Investment**: 60-86 hours (3 weeks)

**Deliverables**:
- [x] MFA implemented
- [x] SIEM log forwarding active
- [x] Vulnerability tracking configured
- [x] 6 user roles with detailed permissions
- [x] E-ISAC feed enabled
- [x] 90-day log retention active

**Next Phase**: Advanced automation and integrations

---

## Phase 3: Advanced Features (Weeks 5-8)

**Goal**: 75% → 90% compliance (+15%)
**Time**: 4 weeks
**Priority**: MEDIUM (advanced capabilities)

### Tasks

1. **E-ISAC Incident Reporting Automation** (Week 5) - 12 hours
   - CIP-008 R1: 1-hour reporting requirement
   - Implementation: Person 3's research (04-INCIDENT-RESPONSE.md)

2. **Patch Management Workflow** (Week 5-6) - 16 hours
   - CIP-010 R2: 35-day patch deadline
   - Implementation: Person 3's research (03-PATCH-MANAGEMENT.md)

3. **ICS Monitoring Tool Integration** (Week 6-7) - 12 hours
   - CIP-015 R1: Internal network security monitoring
   - Implementation: Person 3's research (06-ICS-MONITORING.md)

4. **Firewall IOC Export Automation** (Week 7) - 10 hours
   - CIP-005 R2: Electronic access control
   - Implementation: Person 3's research (05-FIREWALL-IOC-EXPORT.md)

5. **Supply Chain Risk Tracking** (Week 7-8) - 10 hours
   - CIP-013 R1: Vendor management
   - Implementation: Based on architecture docs

6. **Training Event Library** (Week 8) - 20 hours
   - CIP-003 R2: 15-month training requirement
   - Implementation: Person 2's research (complete 15-25 event library)

**Phase 3 Total**: 80 hours over 4 weeks

---

## Phase 4: Audit Preparation (Weeks 9-12)

**Goal**: 90% → 95-100% compliance (+5-10%)
**Time**: 4 weeks
**Priority**: HIGH (audit readiness)

### Tasks

1. **Compliance Reporting Automation** (Week 9) - 16 hours
2. **Audit Evidence Collection System** (Week 10) - 16 hours
3. **Training Content Creation** (Week 10-11) - 24 hours
4. **Final Vulnerability Assessment** (Week 11) - 12 hours
5. **Disaster Recovery Testing** (Week 11-12) - 16 hours
6. **External Audit Preparation** (Week 12) - 16 hours

**Phase 4 Total**: 100 hours over 4 weeks

**Deliverables**:
- Automated compliance reports
- Complete audit evidence package
- Training materials for all CIP requirements
- Validated disaster recovery procedures
- Audit-ready documentation

---

## Feature-to-CIP Mapping

### Feature Implementation → CIP Requirements

| Feature | CIP Standard | Requirement | Implementation File |
|---------|--------------|-------------|---------------------|
| Azure AD MFA | CIP-004 | R4 | Person 1 research |
| SIEM Forwarding | CIP-007 | R4 | Person 3: 01-SIEM |
| Vulnerability Tracking | CIP-010 | R3 | Person 3: 02-VULN |
| Patch Management | CIP-010 | R2 | Person 3: 03-PATCH |
| E-ISAC Reporting | CIP-008 | R1 | Person 3: 04-INCIDENT |
| Firewall IOC Export | CIP-005 | R2 | Person 3: 05-FIREWALL |
| ICS Monitoring | CIP-015 | R1 | Person 3: 06-ICS |
| Automated Backups | CIP-009 | R2 | Person 3: 07-BACKUP |
| Training Events | CIP-003 | R2 | Person 2 research |
| User Roles | CIP-004 | R3 | Person 1 research |
| BCSI Protection | CIP-011 | R1 | Architecture docs |

---

## Evidence Collection

### Evidence Types

**Configuration Evidence**:
- Settings screenshots
- Configuration files
- Policy documents

**Operational Evidence**:
- Log samples
- Incident reports
- Training records
- Access logs

**Testing Evidence**:
- Test results
- Validation reports
- Security assessments

### Evidence Collection Script

```bash
# scripts/collect-audit-evidence.py
python3 scripts/collect-audit-evidence.py \
    --output-dir /audit/evidence/ \
    --date-range "2025-01-01 to 2025-12-31"
```

**Output Structure**:
```
audit/evidence/
├── CIP-003/ (Security Management)
│   ├── training-records/
│   ├── security-policies/
│   └── evidence.pdf
├── CIP-004/ (Personnel & Training)
│   ├── access-logs/
│   ├── user-list/
│   └── evidence.pdf
... (one directory per CIP standard)
```

---

## Validation Procedures

### Compliance Verification

**Weekly Status Check**:
```bash
python3 scripts/check-compliance-status.py
```

**Output**:
```
NERC CIP Compliance Status
==========================
Overall: 75%

CIP-003 Security Management: 85%
CIP-004 Personnel & Training: 70%
CIP-005 Electronic Security Perimeter: 75%
... (full breakdown)

Next Actions:
- Complete MFA implementation (CIP-004 R4)
- Enable E-ISAC reporting (CIP-008 R1)
```

---

### Testing Checklist

- [ ] MFA enforced for all users
- [ ] Logs forwarded to SIEM successfully
- [ ] 90-day retention verified
- [ ] Vulnerability assessments on 15-month cycle
- [ ] Patch management tracking 35-day deadline
- [ ] E-ISAC reporting functional (test report)
- [ ] Training events complete and tagged
- [ ] User roles enforced correctly
- [ ] BCSI protection working
- [ ] Audit evidence collection automated

---

## Audit Checklist

### Pre-Audit Preparation

**30 Days Before Audit**:
- [ ] Run compliance verification
- [ ] Collect all evidence
- [ ] Review documentation
- [ ] Test all systems
- [ ] Prepare audit narrative

**7 Days Before Audit**:
- [ ] Final compliance check
- [ ] Update evidence package
- [ ] Brief audit team
- [ ] Prepare demo environment

**Day of Audit**:
- [ ] System demonstrations ready
- [ ] Evidence organized and accessible
- [ ] Team members briefed
- [ ] Q&A preparation complete

---

### Audit Evidence Package

**Required Documentation**:
1. Compliance matrix (feature → CIP requirement)
2. Configuration snapshots
3. Access control matrix
4. Training records
5. Incident response logs
6. Vulnerability assessment reports
7. Patch management records
8. SIEM log samples
9. Backup/recovery test results
10. Security awareness training materials

---

## Success Metrics

### Target Compliance Levels

| Phase | Timeline | Compliance | Critical Findings |
|-------|----------|------------|-------------------|
| Baseline | Week 0 | 35% | 20 |
| Phase 1 | Week 1 | 55% | 15 |
| Phase 2 | Week 4 | 75% | 8 |
| Phase 3 | Week 8 | 90% | 3 |
| Phase 4 | Week 12 | 95-100% | 0 |

---

**Maintained by**: tKQB Enterprises
**Version**: 1.0
**Last Updated**: 2025-10-25
**Related Documents**:
- `docs/nerc-cip/README.md` - Overview
- `docs/nerc-cip/AUDIT_REPORT.md` - Current state
- `docs/nerc-cip/PRODUCTION_READINESS_TASKS.md` - Task checklist
- `docs/nerc-cip/architecture/` - Technical architecture
- `docs/nerc-cip/research/` - Research deliverables
