# NERC CIP Research Validation Criteria

**Purpose**: Define specific, measurable validation criteria for all research deliverables
**Applies To**: All 19 tasks across 3 research assignments
**Use**: Self-assessment by researchers, formal review by reviewers

---

## Overview

This document provides **specific, actionable validation criteria** for each research task. Each criterion is designed to be:

- ✅ **Specific**: Clear and unambiguous
- ✅ **Measurable**: Can be objectively verified
- ✅ **Achievable**: Realistic within time constraints
- ✅ **Relevant**: Directly supports NERC CIP compliance
- ✅ **Testable**: Can be validated through testing or inspection

---

## Universal Criteria

**All deliverables must meet these minimum requirements**:

### Documentation Quality
- [ ] Written in clear, professional English
- [ ] Follows Markdown format standards
- [ ] Includes table of contents (if >500 lines)
- [ ] Contains working examples
- [ ] Has no broken links or references
- [ ] Includes author, date, version information

### Technical Accuracy
- [ ] Information is factually correct
- [ ] Configurations are tested and validated
- [ ] Code/scripts execute without errors
- [ ] Examples produce expected results
- [ ] Edge cases are documented

### NERC CIP Compliance
- [ ] Maps to specific CIP standard(s)
- [ ] Addresses all control objectives
- [ ] Supports audit evidence collection
- [ ] Includes compliance justification
- [ ] Follows security best practices

### Completeness
- [ ] All required sections present
- [ ] No "TODO" or "TBD" placeholders
- [ ] Prerequisites clearly stated
- [ ] Assumptions documented
- [ ] Limitations acknowledged

---

## Person 1: Authentication & Access Control

### Task 1.1: Research Azure AD Integration Options

**Deliverables**:
1. Azure AD setup guide (docs/nerc-cip/research/person-1/azure-ad-setup.md)
2. Configuration examples (code snippets or config files)
3. Testing results (screenshots or test report)

**Validation Criteria**:

#### Azure AD Setup Guide
- [ ] **Section 1: Overview** - Explains what Azure AD is and why use it for MISP
- [ ] **Section 2: Prerequisites** - Lists Azure AD requirements (tenant, licenses, permissions)
- [ ] **Section 3: Azure AD Configuration** - Step-by-step Azure portal setup (10+ steps with screenshots)
- [ ] **Section 4: MISP Configuration** - MISP LDAP/SAML settings for Azure AD
- [ ] **Section 5: User Provisioning** - How to add users and map to MISP roles
- [ ] **Section 6: Testing** - Validation steps with expected results
- [ ] **Section 7: Troubleshooting** - Common issues and solutions (5+ issues)

#### Configuration Examples
- [ ] Complete `ldap.conf` or SAML config file for Azure AD
- [ ] Example user provisioning script or template
- [ ] Role mapping configuration
- [ ] All configs tested and working

#### Testing Results
- [ ] Successful login screenshot
- [ ] User list showing Azure AD users
- [ ] Role assignment verification
- [ ] At least 1 test user documented

#### CIP-004 Mapping
- [ ] Documents how Azure AD satisfies CIP-004-6 R4 (Access management)
- [ ] Explains MFA enablement (if available)
- [ ] Shows audit log capabilities

**Pass/Fail**:
- **Pass**: All sections complete, configs work, testing documented
- **Fail**: Missing sections, configs untested, or no CIP mapping

---

### Task 1.2: Research LDAP Integration Options

**Deliverables**:
1. LDAP setup guide (docs/nerc-cip/research/person-1/ldap-setup.md)
2. LDAP schema examples
3. Testing results

**Validation Criteria**:

#### LDAP Setup Guide
- [ ] **Section 1: Overview** - LDAP vs Azure AD comparison
- [ ] **Section 2: LDAP Server Options** - At least 3 options evaluated (OpenLDAP, Active Directory, FreeIPA)
- [ ] **Section 3: LDAP Server Setup** - Installation steps for recommended option
- [ ] **Section 4: Schema Design** - MISP-specific LDAP attributes and object classes
- [ ] **Section 5: MISP Configuration** - MISP LDAP settings
- [ ] **Section 6: User Management** - Add/remove/modify users
- [ ] **Section 7: Group Mapping** - LDAP groups → MISP roles
- [ ] **Section 8: Testing** - Validation steps

#### LDAP Schema Examples
- [ ] LDIF file with MISP user schema
- [ ] Example user entries (at least 3 users with different roles)
- [ ] Group definitions for MISP roles
- [ ] All LDIFs validated with ldapwhoami or similar

#### Testing Results
- [ ] LDAP bind test successful
- [ ] User search results
- [ ] Group membership verification
- [ ] Login test screenshot

#### CIP-004 Mapping
- [ ] Maps to CIP-004-6 R4
- [ ] Shows personnel tracking capability
- [ ] Audit logging demonstrated

**Pass/Fail**:
- **Pass**: 3+ LDAP options compared, working schema, testing complete
- **Fail**: Incomplete comparison, schema not tested, or no CIP mapping

---

### Task 1.3: Research MFA Solutions

**Deliverables**:
1. MFA comparison matrix (docs/nerc-cip/research/person-1/mfa-comparison.md)
2. Implementation guide for top recommendation
3. Testing results

**Validation Criteria**:

#### MFA Comparison Matrix
- [ ] **At least 3 MFA solutions evaluated**:
  - Azure AD MFA
  - Google Authenticator / TOTP
  - Hardware tokens (Yubikey)
  - SMS (for completeness, but note security concerns)
- [ ] **Comparison criteria** (table format):
  - Cost (free / paid / enterprise)
  - Ease of setup (1-5 rating)
  - User experience (1-5 rating)
  - Security level (1-5 rating)
  - NERC CIP compliance (Yes/No/Partial)
  - MISP compatibility (Native/Plugin/Custom)
- [ ] **Recommendation** with justification

#### Implementation Guide
- [ ] Step-by-step setup for recommended MFA solution
- [ ] MISP configuration changes required
- [ ] User enrollment process
- [ ] Recovery/bypass procedures (for emergencies)
- [ ] Testing procedure

#### Testing Results
- [ ] MFA enrollment screenshot
- [ ] Login with MFA screenshot
- [ ] Failed MFA attempt (shows blocking)
- [ ] Recovery process tested

#### CIP-004 Mapping
- [ ] Maps to CIP-004-6 R4 (Multi-factor authentication)
- [ ] Explains how MFA strengthens access control
- [ ] Shows audit trail of MFA events

**Pass/Fail**:
- **Pass**: 3+ solutions compared, implementation guide complete, tested
- **Fail**: < 3 solutions, no recommendation, or untested

---

### Task 1.4: Define 6 NERC CIP User Roles

**Deliverables**:
1. User role definitions (docs/nerc-cip/research/person-1/user-roles.md)
2. Permission matrix (table)
3. MISP role configuration examples

**Validation Criteria**:

#### User Role Definitions

Must define **exactly 6 roles** aligned with NERC CIP responsibilities:

**Role 1: CIP Compliance Manager**
- [ ] Description: Responsible for overall CIP compliance
- [ ] CIP Responsibilities: Oversee all CIP standards, audit coordination
- [ ] MISP Permissions: Site Admin, full access to all events/attributes
- [ ] Example Users: Compliance officer, security manager

**Role 2: Incident Responder**
- [ ] Description: Handles security incidents and E-ISAC reporting
- [ ] CIP Responsibilities: CIP-008 incident response
- [ ] MISP Permissions: Create/modify events, publish to E-ISAC
- [ ] Example Users: SOC analysts, IR team

**Role 3: Threat Analyst**
- [ ] Description: Analyzes threat intelligence and creates events
- [ ] CIP Responsibilities: CIP-003 information sharing
- [ ] MISP Permissions: Create events, add attributes, view all orgs
- [ ] Example Users: Threat intel analysts

**Role 4: Read-Only Analyst**
- [ ] Description: Consumes threat intelligence for defensive actions
- [ ] CIP Responsibilities: CIP-007 malicious code prevention
- [ ] MISP Permissions: Read-only access to events/attributes
- [ ] Example Users: Firewall admins, SIEM operators

**Role 5: Auditor**
- [ ] Description: Reviews MISP for compliance auditing
- [ ] CIP Responsibilities: CIP-003 evidence collection
- [ ] MISP Permissions: Read-only, access to audit logs
- [ ] Example Users: Internal auditors, NERC auditors

**Role 6: System Administrator**
- [ ] Description: Manages MISP platform and infrastructure
- [ ] CIP Responsibilities: CIP-007 system security management
- [ ] MISP Permissions: Site Admin, but not compliance decisions
- [ ] Example Users: IT administrators, DevOps

#### Permission Matrix

Table format (✓ = allowed, ✗ = denied):

| Permission | Compliance Mgr | Incident Resp | Threat Analyst | Read-Only | Auditor | Sys Admin |
|------------|---------------|---------------|----------------|-----------|---------|-----------|
| View Events | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Create Events | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| Modify Events | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| Delete Events | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Publish Events | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| E-ISAC Sharing | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| View Audit Logs | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| Manage Users | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Manage Taxonomies | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| System Config | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |

- [ ] All 6 roles defined with at least 10 permissions each
- [ ] No role has all permissions (except maybe Compliance Manager)
- [ ] Principle of least privilege applied

#### MISP Role Configuration
- [ ] Instructions to create each role in MISP UI
- [ ] Screenshot showing role list in MISP
- [ ] Example user assignment to each role
- [ ] Testing: Each role can perform allowed actions, blocked from denied

#### CIP-004 Mapping
- [ ] Maps to CIP-004-6 R4 (Access controls based on need)
- [ ] Demonstrates separation of duties
- [ ] Supports audit and accountability

**Pass/Fail**:
- **Pass**: All 6 roles defined, permission matrix complete, MISP config documented
- **Fail**: < 6 roles, incomplete matrix, or no MISP examples

---

### Task 1.5: Personnel Access Tracking (CIP-004)

**Deliverables**:
1. Access tracking template (docs/nerc-cip/research/person-1/access-tracking-template.md)
2. MISP events for access tracking (JSON examples)
3. Reporting script or procedure

**Validation Criteria**:

#### Access Tracking Template
- [ ] **Tracked Information**:
  - User ID / Name
  - Role assigned
  - Access granted date
  - Access revoked date (if applicable)
  - Justification for access
  - Approver
  - Background check status
  - Training completion status
- [ ] **Template Format**: Spreadsheet (CSV/Excel) or MISP event structure
- [ ] **Example**: At least 5 example personnel records

#### MISP Events for Access Tracking
- [ ] Event template: "Personnel Access Request"
  - Attributes: user-id, role, grant-date, justification, approver
  - Tags: `cip-004:access`, `cip-004:personnel`
- [ ] Event template: "Personnel Access Revocation"
  - Attributes: user-id, revoke-date, reason
  - Tags: `cip-004:access`, `cip-004:revocation`
- [ ] Event template: "Background Check Completion"
  - Attributes: user-id, check-date, result
  - Tags: `cip-004:background-check`
- [ ] All templates provided as JSON files

#### Reporting Script/Procedure
- [ ] Script or manual procedure to generate:
  - Current access list (who has access right now)
  - Access history (who had access in past 90 days)
  - Pending access requests
  - Access reviews (quarterly review report)
- [ ] Output format: CSV or PDF report
- [ ] Example report generated

#### CIP-004 Mapping
- [ ] Maps to CIP-004-6 R4 (Access management and authorization)
- [ ] Shows quarterly review capability (CIP-004-6 R4.4)
- [ ] Demonstrates audit trail

**Pass/Fail**:
- **Pass**: Template complete, 3+ event types, reporting functional
- **Fail**: Incomplete template, < 3 event types, no reporting

---

### Task 1.6: BCSI Information Protection (CIP-011)

**Deliverables**:
1. BCSI tagging strategy (docs/nerc-cip/research/person-1/bcsi-tagging.md)
2. Distribution policy rules
3. MISP configuration examples

**Validation Criteria**:

#### BCSI Tagging Strategy
- [ ] **BCSI Definition**: Clear definition of BES Cyber System Information per CIP-011
- [ ] **BCSI Categories**:
  - Category 1: Network diagrams / IP addresses
  - Category 2: Security configurations
  - Category 3: Vulnerability information
  - Category 4: Access credentials (should never be in MISP!)
  - Category 5: Other sensitive operational info
- [ ] **Tagging Scheme**:
  - Tag: `cip-011:bcsi`
  - Sub-tags: `cip-011:bcsi:network`, `cip-011:bcsi:config`, etc.
- [ ] **Application Rules**: When to apply BCSI tags (decision tree or flowchart)
- [ ] **Examples**: 10+ examples of events/attributes with correct BCSI tags

#### Distribution Policy Rules
- [ ] **Default Distribution**: "Your organization only" (level 0) for all BCSI
- [ ] **Sharing Exceptions**: Process to request sharing BCSI (requires approval)
- [ ] **MISP Settings**:
  ```
  MISP.default_event_distribution = 0  # Your org only
  MISP.default_attribute_distribution = 5  # Inherit from event
  ```
- [ ] **Enforcement**:
  - API checks before publishing
  - User training on distribution levels
  - Regular audits

#### MISP Configuration Examples
- [ ] Screenshot: MISP server settings showing default distribution
- [ ] Example event with BCSI tag and distribution=0
- [ ] Sharing group configuration (if using for controlled BCSI sharing)
- [ ] Audit query: `events.tags:cip-011:bcsi AND distribution:>0` (should return 0 results)

#### CIP-011 Mapping
- [ ] Maps to CIP-011-2 R1 (Information protection)
- [ ] Shows BCSI identification process
- [ ] Demonstrates access controls (distribution restrictions)
- [ ] Audit trail for BCSI access

**Pass/Fail**:
- **Pass**: BCSI categories defined, tagging scheme clear, distribution enforced
- **Fail**: Incomplete categories, no tagging examples, or distribution not configured

---

### Task 1.7: Integration Testing & Documentation

**Deliverables**:
1. Integration test plan (docs/nerc-cip/research/person-1/integration-test-plan.md)
2. Test results (test report or spreadsheet)
3. Known issues and workarounds

**Validation Criteria**:

#### Integration Test Plan
- [ ] **Test Scope**: All Person 1 deliverables integrated
- [ ] **Test Cases** (minimum 10):
  - TC1: Azure AD user login → MISP
  - TC2: LDAP user login → MISP
  - TC3: MFA enrollment and login
  - TC4: Role assignment and permission verification (6 roles)
  - TC5: Personnel access tracking event creation
  - TC6: BCSI tag application and distribution check
  - TC7: Cross-integration: Azure AD user with MFA + correct role
  - TC8: Negative test: User without MFA blocked
  - TC9: Negative test: Wrong role cannot perform action
  - TC10: Audit log verification for all actions
- [ ] **Expected Results**: Documented for each test case
- [ ] **Test Data**: Sample users, events, attributes

#### Test Results
- [ ] All 10+ test cases executed
- [ ] Pass/Fail status for each
- [ ] Screenshots or logs as evidence
- [ ] Pass rate ≥ 80% (8/10 tests pass)

#### Known Issues and Workarounds
- [ ] Any failing tests documented
- [ ] Root cause analysis (if known)
- [ ] Workarounds provided (if available)
- [ ] Future resolution plan

#### CIP-004 & CIP-011 Integration
- [ ] End-to-end flow: User provisioned (Azure AD/LDAP) → Assigned role → Creates event with BCSI tag → Distribution restricted
- [ ] Audit report showing all steps

**Pass/Fail**:
- **Pass**: 10+ tests, ≥80% pass rate, issues documented
- **Fail**: <10 tests, <80% pass, or no documentation

---

## Person 2: Events & Threat Intelligence

### Task 2.1: Create 5 ICS Attack Event Templates

**Deliverables**:
1. 5 ICS attack event templates (JSON files)
2. Documentation for each template (markdown)
3. Import/usage guide

**Validation Criteria**:

#### Event Templates

Must create templates for these **5 specific attacks**:

**Template 1: TRITON/TRISIS (Safety System Attack)**
- [ ] Event info: "ICS Attack: TRITON/TRISIS Safety Instrumented System Compromise"
- [ ] Date: 2017-12-14 (discovery date)
- [ ] Threat level: High
- [ ] Tags:
  - `mitre-attack:ics:t0803` (Program/Download)
  - `mitre-attack:ics:t0806` (Brute Force I/O)
  - `ics:malware:triton`
  - `cip-003:cyber-attack`
- [ ] Attributes (minimum 10):
  - Malware hash (SHA256)
  - C2 domain
  - Target: Triconex SIS controllers
  - MITRE ATT&CK technique IDs
  - IOCs (IP addresses, domains)
  - Timeline of attack
- [ ] References: Public reports (FireEye, ICS-CERT)

**Template 2: INDUSTROYER/CRASHOVERRIDE (Power Grid Attack)**
- [ ] Event info: "ICS Attack: INDUSTROYER/CRASHOVERRIDE Power Grid Compromise"
- [ ] Date: 2016-12-17 (Ukraine attack)
- [ ] Threat level: High
- [ ] Tags:
  - `mitre-attack:ics:t0816` (Device Restart/Shutdown)
  - `mitre-attack:ics:t0855` (Unauthorized Command Message)
  - `ics:malware:industroyer`
  - `cip-008:incident`
- [ ] Attributes (minimum 10):
  - Malware components (4 payloads)
  - IEC 60870-5-104 protocol abuse
  - Targeted substations
  - IOCs
- [ ] References: ESET, NERC alerts

**Template 3: Stuxnet (PLC Manipulation)**
- [ ] Event info: "ICS Attack: Stuxnet PLC Manipulation"
- [ ] Date: 2010-06-17
- [ ] Threat level: High
- [ ] Tags:
  - `mitre-attack:ics:t0849` (Masquerading)
  - `mitre-attack:ics:t0871` (Execution through API)
  - `ics:malware:stuxnet`
- [ ] Attributes (minimum 10)
- [ ] References: Symantec reports

**Template 4: Havex/Dragonfly (ICS Reconnaissance)**
- [ ] Event info: "ICS Attack: Havex/Dragonfly ICS Network Reconnaissance"
- [ ] Date: 2014-06-30
- [ ] Threat level: Medium
- [ ] Tags:
  - `mitre-attack:ics:t0840` (Network Connection Enumeration)
  - `mitre-attack:ics:t0888` (Remote System Discovery)
  - `ics:malware:havex`
- [ ] Attributes (minimum 10)
- [ ] References: ICS-CERT alerts

**Template 5: BlackEnergy (Ukraine Grid 2015)**
- [ ] Event info: "ICS Attack: BlackEnergy Ukraine Power Grid 2015"
- [ ] Date: 2015-12-23
- [ ] Threat level: High
- [ ] Tags:
  - `mitre-attack:ics:t0880` (Loss of Safety)
  - `mitre-attack:ics:t0836` (Modify Parameter)
  - `ics:malware:blackenergy`
  - `cip-008:incident:grid-outage`
- [ ] Attributes (minimum 10)
- [ ] References: E-ISAC, SANS ICS

#### Documentation for Each Template
- [ ] Attack overview (what happened)
- [ ] Impact and lessons learned
- [ ] Indicators of Compromise (IOC) list
- [ ] Detection opportunities
- [ ] Prevention/mitigation strategies
- [ ] Relevance to electric utilities

#### Import/Usage Guide
- [ ] Instructions to import JSON into MISP
- [ ] How to customize for your organization
- [ ] How to use as training material
- [ ] How to reference in incident response

#### CIP Mapping
- [ ] Maps to CIP-003-8 R2 (Cyber security awareness)
- [ ] Maps to CIP-008-6 R1 (Incident response plan)
- [ ] Demonstrates threat intelligence sharing

**Pass/Fail**:
- **Pass**: All 5 templates, ≥10 attributes each, documentation complete
- **Fail**: <5 templates, incomplete attributes, or no documentation

---

### Task 2.2: Design NERC CIP Taxonomy Structure

**Deliverables**:
1. Custom NERC CIP taxonomy (JSON file)
2. Taxonomy documentation (markdown)
3. Usage examples

**Validation Criteria**:

#### NERC CIP Taxonomy (JSON)

Taxonomy structure must include:

**Namespace**: `nerc-cip`
**Description**: "NERC Critical Infrastructure Protection standards compliance tagging"
**Version**: 1.0

**Predicates** (top-level categories):
- [ ] `cip-003` - Security management controls
- [ ] `cip-004` - Personnel and training
- [ ] `cip-005` - Electronic security perimeters
- [ ] `cip-006` - Physical security (N/A for MISP, but include for completeness)
- [ ] `cip-007` - System security management
- [ ] `cip-008` - Incident reporting and response
- [ ] `cip-009` - Recovery plans
- [ ] `cip-010` - Configuration change management and vulnerability assessments
- [ ] `cip-011` - Information protection (BCSI)
- [ ] `cip-013` - Supply chain risk management
- [ ] `cip-014` - Physical security (transmission stations)
- [ ] `cip-015` - ICS/SCADA security

**Entries** (sub-categories):

Example for `cip-003`:
```json
{
  "predicate": "cip-003",
  "entry": [
    {"value": "cyber-attack", "expanded": "Cyber security attack or incident"},
    {"value": "information-sharing", "expanded": "Information sharing with E-ISAC or peers"},
    {"value": "training", "expanded": "Cyber security awareness and training"}
  ]
}
```

- [ ] Each predicate has ≥3 entries
- [ ] Total entries ≥30
- [ ] All entries have "value" and "expanded" fields

#### Taxonomy Documentation
- [ ] Overview of NERC CIP taxonomy purpose
- [ ] How to install in MISP
- [ ] When to use each tag
- [ ] Examples for each predicate (30+ examples)
- [ ] Integration with existing taxonomies (TLP, PAP, etc.)

#### Usage Examples
- [ ] Event tagged with `cip-008:incident` for E-ISAC reporting
- [ ] Event tagged with `cip-011:bcsi` for information protection
- [ ] Event tagged with `cip-003:training` for awareness material
- [ ] Multi-tag example: `cip-008:incident` + `cip-015:ics-attack` + `mitre-attack:ics:t0816`

#### JSON Validation
- [ ] JSON is valid (passes jq or JSON validator)
- [ ] Follows MISP taxonomy schema
- [ ] Can be imported into MISP without errors

#### CIP Mapping
- [ ] Covers all applicable CIP standards (CIP-003 through CIP-015)
- [ ] Aligns with NERC CIP definitions
- [ ] Supports audit evidence tagging

**Pass/Fail**:
- **Pass**: Valid JSON, ≥12 predicates, ≥30 entries, importable to MISP
- **Fail**: Invalid JSON, <12 predicates, or import errors

---

### Task 2.3: E-ISAC Feed Integration Research

**Deliverables**:
1. E-ISAC feed integration guide (markdown)
2. Feed configuration examples
3. Authentication setup instructions

**Validation Criteria**:

#### E-ISAC Feed Integration Guide

**Section 1: E-ISAC Overview**
- [ ] What is E-ISAC (Electricity Information Sharing and Analysis Center)
- [ ] Why integrate with MISP
- [ ] Membership requirements
- [ ] Feed availability (member-only vs. public)

**Section 2: Membership and Access**
- [ ] How to join E-ISAC (utility membership process)
- [ ] Cost and requirements
- [ ] Obtaining API credentials / feed access
- [ ] Contact information

**Section 3: Feed Configuration**
- [ ] E-ISAC feed URL format
- [ ] Authentication method (API key, OAuth, etc.)
- [ ] Feed format (JSON, STIX, CSV)
- [ ] Update frequency
- [ ] MISP feed configuration example:
  ```json
  {
    "Feed": {
      "name": "E-ISAC Security Advisories",
      "provider": "E-ISAC",
      "url": "https://advisories.eisac.com/feed/...",
      "source_format": "misp",
      "enabled": true,
      "distribution": 0,
      "caching_enabled": true,
      "authkey": "[REDACTED]"
    }
  }
  ```

**Section 4: Testing**
- [ ] How to test feed connectivity
- [ ] Example events from E-ISAC feed
- [ ] Verification steps

**Section 5: Automation**
- [ ] Automated feed updates (cron job or MISP worker)
- [ ] Alert on new E-ISAC advisories
- [ ] Integration with incident response workflow

**Section 6: Compliance**
- [ ] Maps to CIP-003-8 R2 (Cyber security awareness from E-ISAC)
- [ ] Maps to CIP-008-6 R1 (Incident response coordination with E-ISAC)

#### Feed Configuration Examples
- [ ] Complete MISP feed config (JSON or UI screenshots)
- [ ] Tested with dummy data (if no E-ISAC access yet)
- [ ] Documentation on how to update config when credentials available

#### Authentication Setup
- [ ] Step-by-step API key configuration
- [ ] Secure storage of credentials (not in git!)
- [ ] Credential rotation procedure

#### Blockers and Alternatives
- [ ] If E-ISAC membership not available:
  - [ ] Document blocker clearly
  - [ ] Provide ICS-CERT as alternative source
  - [ ] Plan to integrate E-ISAC when membership obtained

#### CIP Mapping
- [ ] CIP-003-8 R2 (Cyber security awareness)
- [ ] CIP-008-6 R1.2 (Information sharing with E-ISAC)

**Pass/Fail**:
- **Pass**: Guide complete, config examples provided, authentication documented
- **Conditional Pass**: E-ISAC access blocked but alternatives provided
- **Fail**: Incomplete guide, no config examples, or no CIP mapping

---

### Task 2.4: ICS-CERT Feed Integration

**Deliverables**:
1. ICS-CERT feed setup guide (markdown)
2. Feed parsing rules (if custom format)
3. Testing results

**Validation Criteria**:

#### ICS-CERT Feed Setup Guide

**Section 1: ICS-CERT Overview**
- [ ] What is ICS-CERT (now CISA ICS)
- [ ] Feed availability (public feeds)
- [ ] Types of advisories (alerts, advisories, reports)

**Section 2: Feed Sources**
- [ ] ICS-CERT RSS feeds
- [ ] ICS-CERT API (if available)
- [ ] Email alerts
- [ ] Web scraping (last resort)

**Section 3: MISP Configuration**
- [ ] Feed config for ICS-CERT advisories
- [ ] URL: `https://www.cisa.gov/uscert/ics/advisories.xml` (or current URL)
- [ ] Parsing rules (RSS to MISP event conversion)
- [ ] Tagging strategy: `ics-cert:advisory`, `cip-003:information-sharing`

**Section 4: Automation**
- [ ] Script to fetch and import ICS-CERT advisories
- [ ] Scheduled execution (daily)
- [ ] Deduplication logic

#### Feed Parsing Rules
- [ ] If RSS/XML feed:
  - [ ] Parse title → Event info
  - [ ] Parse description → Event description
  - [ ] Parse link → Reference URL
  - [ ] Parse pubDate → Event date
- [ ] If custom format:
  - [ ] Parsing script provided
  - [ ] Tested with ≥5 sample advisories

#### Testing Results
- [ ] Successfully imported ≥5 ICS-CERT advisories
- [ ] Screenshots showing events in MISP
- [ ] Verification that tags applied correctly

#### CIP Mapping
- [ ] CIP-003-8 R2 (Cyber security awareness)
- [ ] CIP-008-6 R1 (Incident intelligence)

**Pass/Fail**:
- **Pass**: Guide complete, ≥5 advisories imported, automation working
- **Fail**: Incomplete guide, <5 advisories, or no automation

---

### Task 2.5: CIP-003 Training Event Requirements

**Deliverables**:
1. Training event library template (markdown + JSON events)
2. Tracking procedure
3. Reporting capability

**Validation Criteria**:

#### Training Event Library Template

**Categories of training events** (minimum 5):

**Category 1: Cyber Security Awareness (CIP-003-8 R2)**
- [ ] Event: "Cyber Security Awareness Training - Q1 2025"
- [ ] Attributes: training-date, attendees, topics-covered, duration, trainer
- [ ] Tags: `cip-003:training`, `cip-003:awareness`
- [ ] Attachments: Training materials (PDFs), sign-in sheets

**Category 2: Phishing Awareness**
- [ ] Event: "Phishing Simulation and Training - January 2025"
- [ ] Attributes: simulation-results, click-rate, remediation-actions
- [ ] Tags: `cip-003:training`, `cip-003:phishing`

**Category 3: ICS-Specific Threats**
- [ ] Event: "ICS Attack Case Studies Training - February 2025"
- [ ] Attributes: case-studies (TRITON, INDUSTROYER), lessons-learned
- [ ] Tags: `cip-003:training`, `cip-015:ics`
- [ ] References: ICS attack event templates (from Task 2.1)

**Category 4: Incident Response Training**
- [ ] Event: "CIP-008 Incident Response Tabletop Exercise"
- [ ] Attributes: scenario, participants, actions-taken, timeline
- [ ] Tags: `cip-008:training`, `cip-008:tabletop`

**Category 5: Annual Refresher**
- [ ] Event: "Annual CIP Cyber Security Training - 2025"
- [ ] Attributes: All personnel list, completion-status, expiration-date
- [ ] Tags: `cip-003:training`, `cip-003:annual`

- [ ] All 5+ event templates provided as JSON
- [ ] Each template has ≥5 attributes
- [ ] Example events with realistic data

#### Tracking Procedure
- [ ] How to create training event in MISP
- [ ] How to add attendee list (as attributes or objects)
- [ ] How to track completion (tags: `cip-004:training-complete`)
- [ ] How to track expiration (annual refresher due dates)

#### Reporting Capability
- [ ] Query to list all training events in past year
- [ ] Query to list personnel who completed training
- [ ] Query to list personnel overdue for training (annual refresher)
- [ ] Example report (CSV or PDF) showing:
  - Training name
  - Date
  - Attendees
  - Topics
  - Next due date

#### CIP Mapping
- [ ] CIP-003-8 R2 (Cyber security awareness program)
- [ ] CIP-004-6 R2 (Training program)
- [ ] Demonstrates quarterly awareness (CIP-003-8 R2.1)

**Pass/Fail**:
- **Pass**: 5+ event categories, tracking procedure documented, reporting functional
- **Fail**: <5 categories, no tracking, or no reporting

---

## Person 3: Integrations & Automation

### Task 3.1: SIEM Log Forwarding (CIP-007 R4)

**Deliverables**:
1. SIEM integration guide (markdown)
2. Syslog configuration examples
3. Log retention script
4. Testing results

**Validation Criteria**:

#### SIEM Integration Guide

**Section 1: Overview**
- [ ] Why SIEM integration for NERC CIP
- [ ] CIP-007-6 R4 requirements (security event monitoring)
- [ ] Supported SIEMs (Splunk, ELK, QRadar, etc.)

**Section 2: Log Sources from MISP**
- [ ] Application logs: `/opt/misp/logs/`
- [ ] Apache/Nginx access logs
- [ ] Docker container logs
- [ ] Database audit logs
- [ ] API access logs

**Section 3: Syslog Configuration**
- [ ] Configure MISP to forward logs via syslog
- [ ] Syslog format (CEF, JSON, etc.)
- [ ] Example syslog config:
  ```conf
  *.* @@siem.example.com:514
  ```
- [ ] MISP application log forwarding script

**Section 4: SIEM-Specific Setup**

At least **2 SIEMs** documented:

**Splunk**:
- [ ] Splunk Universal Forwarder installation on MISP server
- [ ] inputs.conf configuration
- [ ] props.conf for MISP sourcetype
- [ ] Example searches/alerts

**ELK Stack**:
- [ ] Filebeat configuration
- [ ] Logstash pipeline for MISP logs
- [ ] Elasticsearch index mapping
- [ ] Kibana dashboard

**Section 5: Log Retention (90 days)**
- [ ] CIP-007-6 R4.2 requires 90-day retention
- [ ] SIEM retention configuration
- [ ] Backup/archive strategy for logs >90 days

#### Syslog Configuration Examples
- [ ] Complete rsyslog.conf or syslog-ng.conf
- [ ] Tested and forwarding logs
- [ ] Sample logs shown in SIEM

#### Log Retention Script
- [ ] Script to check log age
- [ ] Alert if logs <90 days missing
- [ ] Archive/delete logs >90 days (optional, based on policy)
- [ ] Example output:
  ```
  Retention Check: 2025-10-25
  Oldest log: 2025-07-27 (90 days ago) ✓
  Total log size: 15GB
  ```

#### Testing Results
- [ ] Logs successfully forwarded to SIEM
- [ ] Screenshot of MISP logs in SIEM
- [ ] Example security event (login failure) detected in SIEM
- [ ] Retention verified (90+ days of logs present)

#### CIP-007 Mapping
- [ ] CIP-007-6 R4.1 (Log events per standard)
- [ ] CIP-007-6 R4.2 (Retain logs for 90 days)
- [ ] CIP-007-6 R4.3 (Review logs)

**Pass/Fail**:
- **Pass**: Guide complete, ≥2 SIEMs documented, retention script works, logs forwarded
- **Fail**: <2 SIEMs, no retention script, or logs not forwarding

---

### Task 3.2: Vulnerability Tracking (CIP-010 R3)

**Deliverables**:
1. Vulnerability import script (Python or Bash)
2. Vulnerability tracking dashboard (MISP or external)
3. 15-month vulnerability cycle tracking
4. Testing results

**Validation Criteria**:

#### Vulnerability Import Script

**Functionality**:
- [ ] Imports vulnerabilities from scanner (Nessus, Qualys, OpenVAS, etc.)
- [ ] Converts vulnerability data to MISP events
- [ ] Attributes include:
  - CVE ID
  - CVSS score
  - Affected system
  - Severity
  - Patch availability
  - Detection date
- [ ] Tags: `cip-010:vulnerability`, `cip-010:15-month-cycle`

**Example Event**:
```json
{
  "Event": {
    "info": "Vulnerability Assessment - 2025-10-25",
    "threat_level_id": "2",
    "analysis": "1",
    "distribution": "0",
    "Tag": [
      {"name": "cip-010:vulnerability"},
      {"name": "cip-010:assessment"}
    ],
    "Attribute": [
      {"type": "vulnerability", "value": "CVE-2024-1234", "category": "External analysis"},
      {"type": "text", "value": "CVSS: 7.5", "category": "Other"},
      {"type": "text", "value": "Affected: MISP Server", "category": "Targeting data"}
    ]
  }
}
```

- [ ] Script tested with ≥10 sample vulnerabilities
- [ ] Can run via cron (automated)

#### Vulnerability Tracking Dashboard
- [ ] MISP dashboard widget showing:
  - Open vulnerabilities count
  - Critical/High/Medium/Low breakdown
  - Oldest vulnerability (days open)
  - Patched vulnerabilities this month
- [ ] Or external dashboard (Splunk, Grafana):
  - Same metrics
  - Screenshot provided

#### 15-Month Vulnerability Cycle Tracking

**CIP-010-3 R3** requires vulnerability assessments every 15 months:

- [ ] Script/procedure to track when last assessment was performed
- [ ] Alert when next assessment due (15 months from last)
- [ ] Example tracking:
  ```
  Last Assessment: 2024-07-15
  Next Due: 2025-10-15 (15 months)
  Status: OVERDUE (by 10 days)
  ```

- [ ] Automated reminder (email or MISP event) 30 days before due date

#### Testing Results
- [ ] Imported ≥10 sample vulnerabilities
- [ ] Dashboard shows correct metrics
- [ ] 15-month cycle tracking functional
- [ ] Alert tested (manual trigger)

#### CIP-010 Mapping
- [ ] CIP-010-3 R3 (Vulnerability assessments every 15 months)
- [ ] CIP-007-6 R2 (Patch management - related)
- [ ] Demonstrates tracking and reporting

**Pass/Fail**:
- **Pass**: Script imports vulnerabilities, dashboard functional, 15-month tracking works
- **Fail**: Script errors, no dashboard, or no cycle tracking

---

### Task 3.3: Patch Management (CIP-010 R2)

**Deliverables**:
1. Patch tracking events (MISP event templates)
2. 35-day alert automation
3. Patch management dashboard
4. Testing results

**Validation Criteria**:

#### Patch Tracking Events

**Event Template 1: Patch Release Notification**
- [ ] Info: "Security Patch Released - [Vendor] - [CVE-ID]"
- [ ] Attributes:
  - CVE ID
  - Patch ID
  - Release date
  - Severity
  - Affected systems
  - Vendor bulletin URL
- [ ] Tags: `cip-010:patch`, `cip-010:release`

**Event Template 2: Patch Installation**
- [ ] Info: "Patch Installed - [System] - [Patch ID]"
- [ ] Attributes:
  - System name
  - Patch ID
  - Installation date
  - Installer (person)
  - Pre/post validation results
- [ ] Tags: `cip-010:patch`, `cip-010:installed`

**Event Template 3: Patch Deferral (if not installed within 35 days)**
- [ ] Info: "Patch Deferred - [Patch ID] - Justification Required"
- [ ] Attributes:
  - Patch ID
  - Deferral reason
  - Risk assessment
  - Approver
  - Target install date
- [ ] Tags: `cip-010:patch`, `cip-010:deferred`, `cip-010:35-day-exception`

- [ ] All 3 templates provided as JSON
- [ ] Example events with realistic data

#### 35-Day Alert Automation

**CIP-010-3 R2** requires patches installed within 35 days (or documented deferral):

- [ ] Script that:
  1. Queries MISP for "Patch Release" events
  2. Checks if corresponding "Patch Installed" event exists
  3. If not installed within 35 days, creates alert event
  4. Alert includes: Patch ID, days overdue, affected systems

- [ ] Example alert:
  ```
  ALERT: Patch Overdue
  Patch: MS-2024-001
  Released: 2025-09-01
  Days Overdue: 40 (35-day deadline: 2025-10-06)
  Status: NOT INSTALLED - ACTION REQUIRED
  ```

- [ ] Script runs daily via cron
- [ ] Tested with sample patches (simulate overdue)

#### Patch Management Dashboard
- [ ] Metrics:
  - Patches released this month
  - Patches installed this month
  - Patches overdue (>35 days)
  - Average install time
  - Compliance rate (% installed within 35 days)
- [ ] MISP widget or external dashboard
- [ ] Screenshot provided

#### Testing Results
- [ ] Created ≥3 patch release events
- [ ] Created ≥2 patch installed events
- [ ] Simulated overdue patch (>35 days)
- [ ] Alert triggered correctly
- [ ] Dashboard shows correct metrics

#### CIP-010 Mapping
- [ ] CIP-010-3 R2 (Security patches within 35 days)
- [ ] CIP-007-6 R2 (Patch management process)
- [ ] Demonstrates tracking, alerting, and compliance

**Pass/Fail**:
- **Pass**: All 3 templates, 35-day alert works, dashboard functional
- **Fail**: Missing templates, alert doesn't work, or no dashboard

---

### Task 3.4: E-ISAC Incident Reporting (CIP-008)

**Deliverables**:
1. 1-hour incident reporting automation (script)
2. E-ISAC report template
3. Workflow documentation
4. Testing results

**Validation Criteria**:

#### 1-Hour Incident Reporting Automation

**CIP-008-6 R1** requires reporting Cyber Security Incidents to E-ISAC within 1 hour:

**Script Functionality**:
- [ ] Triggered when MISP event tagged with `cip-008:incident`
- [ ] Automatically generates E-ISAC report format
- [ ] Submits to E-ISAC via:
  - Email (if no API)
  - API (if available)
  - Web form (automated browser)
- [ ] Logs submission time (for audit)
- [ ] Alert if submission fails

**Required Information** (per E-ISAC):
- [ ] Incident ID (MISP event ID)
- [ ] Incident date/time
- [ ] Description (from MISP event)
- [ ] Impact (estimated customers affected, if applicable)
- [ ] IOCs (IP addresses, malware hashes, etc.)
- [ ] Organization contact info
- [ ] Status (ongoing/resolved)

- [ ] Script tested with dummy incident
- [ ] Timing: Event tagged → Report sent within 5 minutes (target <1 hour)

#### E-ISAC Report Template
- [ ] MISP event template for incidents:
  ```json
  {
    "Event": {
      "info": "CIP-008 Cyber Security Incident - [Brief Description]",
      "threat_level_id": "1",
      "analysis": "1",
      "distribution": "0",
      "Tag": [
        {"name": "cip-008:incident"},
        {"name": "cip-008:reportable"},
        {"name": "e-isac:submitted"}
      ],
      "Attribute": [
        {"type": "datetime", "value": "2025-10-25T14:30:00", "comment": "Incident start"},
        {"type": "text", "value": "Ransomware detected on SCADA workstation", "category": "Internal reference"},
        {"type": "ip-dst", "value": "192.0.2.1", "comment": "C2 server"}
      ]
    }
  }
  ```

- [ ] Template includes all E-ISAC required fields
- [ ] Easy to populate for incident responders

#### Workflow Documentation
- [ ] Step-by-step process:
  1. Incident detected (manual or automated)
  2. Create MISP event with `cip-008:incident` tag
  3. Script auto-triggers
  4. E-ISAC report generated and sent
  5. Confirmation received (email or API response)
  6. MISP event updated with `e-isac:submitted` tag
- [ ] Flowchart or diagram
- [ ] Roles and responsibilities
- [ ] Escalation if automated reporting fails

#### Testing Results
- [ ] Created test incident event
- [ ] Script triggered and generated report
- [ ] Report format validated (matches E-ISAC requirements)
- [ ] If E-ISAC access available: Report successfully submitted
- [ ] If no access: Report saved to file for manual submission

#### CIP-008 Mapping
- [ ] CIP-008-6 R1.2 (Report to E-ISAC within 1 hour)
- [ ] CIP-008-6 R1.3 (Update E-ISAC on incident status)
- [ ] Demonstrates automated compliance

**Pass/Fail**:
- **Pass**: Script works, report generated, <1 hour timing, workflow documented
- **Conditional Pass**: No E-ISAC access but report format validated
- **Fail**: Script doesn't work, >1 hour, or no workflow

---

### Task 3.5: Firewall IOC Export (CIP-005 R2)

**Deliverables**:
1. IOC export script (IP/domain blocklist)
2. Firewall-specific formats (3+ vendors)
3. Automation setup
4. Testing results

**Validation Criteria**:

#### IOC Export Script

**Functionality**:
- [ ] Queries MISP for IOCs (IP addresses, domains, URLs)
- [ ] Filters for high-confidence, recent IOCs (e.g., last 90 days)
- [ ] Exports to firewall-compatible formats
- [ ] Supports deduplication
- [ ] Supports allowlist (exclude false positives)

**Query Example**:
```python
# Pseudo-code
iocs = misp.search(
    type=['ip-dst', 'domain'],
    tags=['tlp:amber', 'confidence:high'],
    publish_timestamp='90d'
)
blocklist = [ioc.value for ioc in iocs]
```

- [ ] Script runs without errors
- [ ] Exports ≥100 IOCs (from test data or real MISP)

#### Firewall-Specific Formats

At least **3 firewall vendors** supported:

**1. Palo Alto Networks**:
- [ ] Format: External Dynamic List (EDL)
- [ ] Output: Plain text, one IP/domain per line
- [ ] Example:
  ```
  192.0.2.1
  198.51.100.1
  example-malware.com
  ```
- [ ] Upload to web server for PAN-OS EDL fetch

**2. Cisco ASA/Firepower**:
- [ ] Format: Object-group
- [ ] Output: CLI commands
- [ ] Example:
  ```
  object-group network MISP-BLOCKLIST
   network-object host 192.0.2.1
   network-object host 198.51.100.1
  ```

**3. Fortinet FortiGate**:
- [ ] Format: Threat feed
- [ ] Output: CSV or JSON
- [ ] Example CSV:
  ```csv
  ip,type,severity
  192.0.2.1,malware,critical
  198.51.100.1,c2,high
  ```

- [ ] All 3 formats tested and validated (format check, not necessarily deployed)

#### Automation Setup
- [ ] Cron job to run export script daily
- [ ] Example crontab:
  ```
  0 2 * * * /opt/misp-scripts/export-firewall-iocs.sh --vendor palo-alto > /var/www/html/misp-blocklist.txt
  ```
- [ ] Firewall configured to fetch IOC list (or manual import instructions)
- [ ] Alert on export failures

#### Testing Results
- [ ] Exported ≥100 IOCs in all 3 formats
- [ ] Format validation (no syntax errors)
- [ ] If test firewall available: Imported and blocked test IOC
- [ ] If no firewall: Manual validation of format

#### CIP-005 Mapping
- [ ] CIP-005-6 R2 (Electronic access controls at perimeter)
- [ ] CIP-007-6 R2 (Malicious code prevention)
- [ ] Demonstrates automated threat blocking

**Pass/Fail**:
- **Pass**: Script works, 3+ formats, automation setup, ≥100 IOCs
- **Fail**: Script errors, <3 formats, or no IOCs exported

---

### Task 3.6: ICS Monitoring Integration (CIP-015 R1)

**Deliverables**:
1. ICS event import guide (markdown)
2. SCADA/ICS protocol mapping
3. Integration examples (2+ tools)
4. Testing results

**Validation Criteria**:

#### ICS Event Import Guide

**Section 1: Overview**
- [ ] Why ICS monitoring in MISP
- [ ] CIP-015 R1 requirements (Transient Cyber Assets and Removable Media)
- [ ] Types of ICS events to import

**Section 2: ICS Monitoring Tools**

At least **2 tools** documented:

**Tool 1: Nozomi Networks / Claroty / Dragos**:
- [ ] How to export events/alerts
- [ ] Format (SIEM, syslog, API)
- [ ] Mapping to MISP attributes
- [ ] Example events

**Tool 2: Wireshark / Zeek (open source)**:
- [ ] Capture ICS protocols (Modbus, DNP3, IEC 60870-5-104)
- [ ] Parse with Zeek scripts
- [ ] Convert to MISP events
- [ ] Example PCAP analysis

**Section 3: SCADA/ICS Protocol Mapping**

Map common ICS protocols to MISP attributes:

| ICS Protocol | MISP Attribute Type | Example Value | Notes |
|--------------|---------------------|---------------|-------|
| Modbus | modbus-function-code | 0x03 (Read Holding Registers) | Attribute type may need custom |
| DNP3 | dnp3-function-code | 0x02 (Write) | Monitor write commands |
| IEC 60870-5-104 | iec104-asdu-type | C_SC_NA_1 (Single Command) | INDUSTROYER used this |
| BACnet | bacnet-object-type | analog-value | Building automation |

- [ ] Table includes ≥4 ICS protocols
- [ ] Example MISP events for each protocol

**Section 4: Integration Examples**

**Example 1: Unauthorized Modbus Write**
- [ ] Event info: "ICS Alert: Unauthorized Modbus Write to PLC"
- [ ] Attributes: Source IP, Destination IP, Function code, Register address
- [ ] Tags: `cip-015:ics-alert`, `mitre-attack:ics:t0836`

**Example 2: Removable Media Detection**
- [ ] Event info: "CIP-015: USB Device Connected to ICS Workstation"
- [ ] Attributes: Device ID, Workstation, User, Timestamp
- [ ] Tags: `cip-015:removable-media`, `cip-015:transient-asset`

- [ ] Both examples provided as JSON templates
- [ ] Tested (manually created in MISP)

#### Testing Results
- [ ] Imported ≥5 ICS event examples (real or simulated)
- [ ] Screenshot of ICS events in MISP
- [ ] Verified tags and attributes correct

#### CIP-015 Mapping
- [ ] CIP-015-1 R1 (ICS asset monitoring)
- [ ] CIP-015-1 R2 (Transient Cyber Assets and Removable Media controls)
- [ ] Demonstrates ICS visibility in MISP

**Pass/Fail**:
- **Pass**: Guide complete, ≥2 tools documented, ≥4 protocols mapped, ≥5 events imported
- **Fail**: <2 tools, <4 protocols, or <5 events

---

### Task 3.7: Automated Backup Procedures (CIP-009 R2)

**Deliverables**:
1. Backup automation script (Python or Bash)
2. Recovery testing procedure
3. DR documentation
4. Testing results

**Validation Criteria**:

#### Backup Automation Script

**Functionality**:
- [ ] Backs up critical MISP components:
  - Database (MySQL dump)
  - Configuration files (`/opt/misp/.env`, `PASSWORDS.txt`, etc.)
  - SSL certificates
  - Custom scripts and widgets
- [ ] Compression (gzip or tar.gz)
- [ ] Encryption (GPG or AES)
- [ ] Remote storage (S3, NFS, or offsite)
- [ ] Retention policy (30 days default)
- [ ] Email notification on success/failure

**Example Script Structure**:
```bash
#!/bin/bash
# misp-automated-backup.sh

BACKUP_DIR="/backup/misp"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec misp-db mysqldump -u misp -p$MYSQL_PASSWORD misp > $BACKUP_DIR/misp-db-$DATE.sql

# Config files
tar -czf $BACKUP_DIR/misp-config-$DATE.tar.gz /opt/misp/.env /opt/misp/PASSWORDS.txt

# Encrypt
gpg --encrypt --recipient backup@example.com $BACKUP_DIR/*-$DATE.*

# Upload to S3 (example)
aws s3 cp $BACKUP_DIR/ s3://misp-backups/ --recursive

# Retention (delete >30 days)
find $BACKUP_DIR -type f -mtime +30 -delete
```

- [ ] Script tested and runs without errors
- [ ] Creates valid backup archive
- [ ] Encryption works (can decrypt)

#### Cron Schedule
- [ ] Daily backup: `0 2 * * *` (2:00 AM)
- [ ] Example crontab entry provided
- [ ] Tested (manual trigger)

#### Recovery Testing Procedure

**Test Plan**:
- [ ] Step 1: Destroy test MISP instance (docker down + delete volumes)
- [ ] Step 2: Restore from latest backup
- [ ] Step 3: Verify:
  - Database restored (event count matches)
  - Configuration intact (settings preserved)
  - SSL certs working
  - Users can log in
- [ ] Step 4: Document recovery time (RTO - Recovery Time Objective)

**Target RTO**: < 4 hours (CIP-009 requirement)

- [ ] Recovery tested at least once
- [ ] Documented with screenshots/logs
- [ ] RTO ≤ 4 hours

#### DR Documentation

**Section 1: Disaster Scenarios**
- [ ] Scenario 1: Database corruption
- [ ] Scenario 2: Server hardware failure
- [ ] Scenario 3: Ransomware attack
- [ ] Scenario 4: Data center outage

**Section 2: Recovery Procedures**
- [ ] Step-by-step for each scenario
- [ ] Contact information (on-call, vendors)
- [ ] Decision tree (when to failover, when to restore)

**Section 3: Backup Locations**
- [ ] Primary: Local disk
- [ ] Secondary: Remote storage (S3, NFS)
- [ ] Offsite: (optional, recommended)

**Section 4: Testing Schedule**
- [ ] Annual DR test (CIP-009-6 R2 requirement)
- [ ] Next test date: [YYYY-MM-DD]

#### Testing Results
- [ ] Backup script runs successfully
- [ ] Backup file created and encrypted
- [ ] Restore tested (at least once)
- [ ] RTO measured and documented

#### CIP-009 Mapping
- [ ] CIP-009-6 R2 (Backup and restore of BES Cyber Assets)
- [ ] CIP-009-6 R3 (Test recovery plans annually)
- [ ] Demonstrates automated compliance

**Pass/Fail**:
- **Pass**: Script works, backup created, restore tested, RTO ≤4h
- **Fail**: Script errors, backup corrupt, restore fails, or RTO >4h

---

## Scoring Summary

### Overall Pass Criteria

**To pass research review, must meet ALL of**:
1. **Task Completion**: 19/19 tasks completed (100%)
2. **Quality Score**: Average ≥ 7.0 / 10 across all deliverables
3. **Compliance**: All CIP mappings documented
4. **Testing**: All deliverables tested and functional
5. **Documentation**: All docs complete, clear, and actionable

### Conditional Pass Criteria

**May pass with conditions if**:
- **Task Completion**: 17-18/19 tasks (89-94%)
- **Quality Score**: Average 5.0-6.9 / 10
- **Blockers**: External dependencies (E-ISAC access, SIEM endpoint) documented
- **Plan**: Clear path to complete remaining tasks within 1 week

### Fail Criteria

**Automatic fail if**:
- **Task Completion**: <17/19 tasks (<89%)
- **Quality Score**: Average <5.0 / 10
- **Critical Gaps**: No CIP mapping, no testing, or major technical errors
- **No Plan**: No path forward to complete work

---

## Appendix: Quick Validation Checklist

Use this for rapid self-assessment:

```markdown
## Research Self-Assessment Checklist

**Researcher**: [Name]
**Date**: [YYYY-MM-DD]

### Universal Criteria (All Tasks)
- [ ] Documentation is clear and well-formatted
- [ ] All code/scripts are tested and working
- [ ] Examples are provided and realistic
- [ ] CIP standards are mapped
- [ ] No TODO/TBD placeholders remain

### Person 1 Specific
- [ ] Azure AD + LDAP + MFA guides complete
- [ ] 6 user roles defined with permission matrix
- [ ] Personnel access tracking functional
- [ ] BCSI tagging strategy implemented
- [ ] Integration testing passed (≥80%)

### Person 2 Specific
- [ ] 5 ICS attack templates created
- [ ] NERC CIP taxonomy valid JSON
- [ ] E-ISAC feed integration researched
- [ ] ICS-CERT feed working
- [ ] Training event library complete

### Person 3 Specific
- [ ] SIEM log forwarding configured
- [ ] Vulnerability tracking with 15-month cycle
- [ ] Patch management with 35-day alerts
- [ ] E-ISAC 1-hour incident reporting
- [ ] Firewall IOC export (3+ formats)
- [ ] ICS monitoring integrated
- [ ] Backup automation tested (RTO ≤4h)

### Overall
- [ ] All assigned tasks completed
- [ ] Total hours within estimate
- [ ] Ready for formal review
- [ ] Confident in quality

**Estimated Self-Score**: [X] / 10

**Concerns**: [List any issues or questions]
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-25
**Next Review**: After first research cycle completion (Nov 2025)
