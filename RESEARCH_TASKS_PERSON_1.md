# MISP NERC CIP Research Tasks - Person 1
## Authentication, Users, Organizations, Access Control

**Assigned To**: Person 1
**Focus Areas**: CIP-004 (Personnel & Training), CIP-011 (Information Protection)
**Estimated Total Time**: 20-25 hours
**Priority**: HIGH (Foundational for all other work)
**Dependencies**: None (can start immediately)

---

## Overview

You are responsible for researching and documenting how **authentication, user management, organizations, and access control** should be configured in MISP to meet NERC CIP Medium Impact requirements. Your work will establish the foundation for secure access to BES Cyber System Information (BCSI).

**Why This Matters**:
- CIP-004 requires proper authentication, role-based access control, and personnel tracking
- CIP-011 requires protecting BCSI with proper access controls
- Without your research, we cannot properly secure the MISP instance

---

## Your Task List

### SECTION 1: AUTHENTICATION METHODS (CIP-004 R4)

**CIP Requirement**: CIP-004 R4 - Multi-Factor Authentication for interactive remote access

**Current State**:
- Only local authentication enabled
- No MFA configured
- Single admin user

**Your Goal**: Research and document the best authentication method(s) for our organization.

---

#### TASK 1.1: Evaluate Authentication Options

**Time Estimate**: 2-3 hours

**What to Research**:

1. **Does our organization use Azure Entra ID (formerly Azure AD)?**
   - If yes, gather Azure tenant information
   - Check if we have Microsoft 365 E3/E5 licenses (includes MFA)
   - Identify who manages Azure AD

2. **Do we have Active Directory / LDAP?**
   - If yes, get LDAP server details
   - Check if we have LDAPS (secure LDAP) configured
   - Identify LDAP administrators

3. **What MFA methods are already deployed?**
   - Google Authenticator / Microsoft Authenticator (TOTP)
   - Hardware tokens (YubiKey, RSA SecurID)
   - Duo Security
   - SMS (not recommended but document if in use)

4. **SSO (Single Sign-On) Requirements**
   - Do users expect to use their corporate credentials?
   - Is SSO a requirement or nice-to-have?

**Deliverable**: Complete the template below

---

**TEMPLATE: Authentication Assessment**

```markdown
# Authentication Method Assessment

## Current Corporate Authentication

**Primary Identity Provider**: [ ] Azure AD  [ ] Active Directory  [ ] Other: _______

**Azure Entra ID Details** (if applicable):
- Tenant ID: _______________________________
- Tenant Name: _______________________________
- Administrator Contact: _______________________________
- Microsoft 365 License Level: [ ] E3  [ ] E5  [ ] Business  [ ] Other: _______

**Active Directory / LDAP Details** (if applicable):
- LDAP Server: ldaps://dc.example.com:636
- Base DN: dc=example,dc=com
- Service Account for LDAP Reads: cn=misp-reader,ou=service-accounts,dc=example,dc=com
- LDAP Administrator Contact: _______________________________
- LDAPS Enabled: [ ] Yes  [ ] No

**Multi-Factor Authentication (MFA)**:

Currently Deployed MFA Methods:
- [ ] Microsoft Authenticator (TOTP)
- [ ] Google Authenticator (TOTP)
- [ ] Duo Security
- [ ] YubiKey / Hardware Tokens
- [ ] Other: _______________________________

**SSO Requirements**:
- [ ] SSO is required (users must use corporate credentials)
- [ ] SSO is preferred but not required
- [ ] SSO is not needed (MISP-local accounts acceptable)

**Recommended Authentication Method for MISP**:

(Choose one based on research above)
- [ ] Azure Entra ID with MFA (if we have M365)
- [ ] LDAP + TOTP MFA (if we have Active Directory)
- [ ] Local MISP accounts + TOTP MFA (if no corporate identity provider)

**Rationale**:
(Explain why this method is best for our organization)

_________________________________________________________________________
_________________________________________________________________________

**CIP-004 Compliance Notes**:
- MFA required for: [ ] All users  [ ] Admin only  [ ] Admin + Analysts
- Grace period for MFA enrollment: _____ hours (recommend 24-48 hours)
- Backup authentication method if MFA device lost: _______________________________
```

**Where to Save**: `research/person1/authentication-assessment.md`

---

#### TASK 1.2: Document Azure AD Integration Requirements

**Time Estimate**: 2 hours

**Skip this task if**: We are NOT using Azure Entra ID

**What to Research**:

1. **Azure App Registration**
   - Who can create app registrations in our Azure tenant?
   - What approval process is required?

2. **Required Information**:
   - Tenant ID (get from Azure portal)
   - Client ID (will be generated during app registration)
   - Client Secret (will be generated during app registration)
   - Redirect URI: `https://misp.example.com/users/login`

3. **Group-Based Access Control**
   - Can we use Azure AD groups to control MISP roles?
   - What groups should map to what MISP roles?

**Deliverable**: Complete the template below

---

**TEMPLATE: Azure AD Integration Plan**

```markdown
# Azure Entra ID Integration Plan for MISP

## Prerequisites

**Azure AD Administrator**: _______________________________
**Approval Required**: [ ] Yes  [ ] No
**Approval Process**: _______________________________

## Azure App Registration Details

**Application Name**: MISP-Production (or MISP-Test for testing)
**Redirect URI**: https://misp.example.com/users/login
**Supported Account Types**: [ ] Single tenant  [ ] Multi-tenant

**Tenant Information**:
- Tenant ID: _______________________________
- Tenant Name: _______________________________

**App Registration Location**:
Azure Portal → Entra ID → App registrations → New registration

## Group-Based Role Mapping

(If using Azure AD groups for MISP role assignment)

| Azure AD Group Name | MISP Role | Purpose |
|---------------------|-----------|---------|
| MISP-Admins | Admin | NERC CIP Compliance Officers |
| MISP-Analysts | User | Security Analysts |
| MISP-Viewers | Read Only | Security Awareness Training |
| _______________ | ________ | _____________ |

**Group Creation Required**: [ ] Yes (list groups to create)  [ ] No (groups exist)

**Groups to Create**:
1. _______________________________
2. _______________________________
3. _______________________________

## MFA Configuration

**Azure AD MFA Policy**:
- [ ] MFA already required for all users (via Conditional Access)
- [ ] MFA required for specific groups only
- [ ] MFA not yet configured (need to enable)

**Conditional Access Policy Name** (if applicable): _______________________________

## API Permissions Required

(These will be requested during app registration)

- [ ] User.Read (read user profile)
- [ ] User.ReadBasic.All (read basic info of all users)
- [ ] Group.Read.All (if using group-based roles)

## Testing Plan

**Test Environment**:
- Test Tenant: [ ] We have a test Azure tenant  [ ] Use production tenant
- Test Users: _______________________________

**Timeline**:
- App Registration: Week _____
- Test Authentication: Week _____
- Production Rollout: Week _____

## Contact for Implementation

**Name**: _______________________________
**Email**: _______________________________
**Phone**: _______________________________
```

**Where to Save**: `research/person1/azure-ad-integration-plan.md`

---

### SECTION 2: USER ROLES & ACCESS CONTROL (CIP-004 R3)

**CIP Requirement**: CIP-004 R3 - Authorization based on need-to-know

**Current State**: Only 1 admin role, no role-based access control

**Your Goal**: Define the user roles needed for NERC CIP compliance

---

#### TASK 1.3: Define NERC CIP User Roles

**Time Estimate**: 3-4 hours

**What to Research**:

1. **Identify Personnel Categories**:
   - Who needs full admin access? (NERC CIP Compliance Officers)
   - Who needs to create/edit events? (Security Analysts)
   - Who needs read-only access? (Training, awareness)
   - Who needs incident response capabilities? (SOC team)
   - Who manages vulnerability assessments? (CIP-010)
   - Who tracks supply chain risks? (CIP-013)

2. **Current Organizational Structure**:
   - How many people in each role?
   - What are their current job titles?
   - Who is the NERC CIP Compliance Officer?

3. **Need-to-Know Assessment**:
   - Does everyone need access to all events?
   - Should some users only see "Your organization only" events?
   - Should contractors have different access than employees?

**Deliverable**: Complete the template below

---

**TEMPLATE: NERC CIP User Roles Definition**

```markdown
# NERC CIP User Roles for MISP

## Role 1: CIP Compliance Administrator

**MISP Role**: Admin
**CIP Requirement**: CIP-004 R3.1 (System administrators)

**Personnel in This Role**:
1. Name: _____________________ Email: _____________________ Job Title: _____________________
2. Name: _____________________ Email: _____________________ Job Title: _____________________
3. Name: _____________________ Email: _____________________ Job Title: _____________________

**Total Count**: _____ (Recommend: 2-3 for redundancy)

**Responsibilities**:
- [ ] Full MISP administrative access
- [ ] User management
- [ ] System configuration
- [ ] Taxonomy management
- [ ] Compliance reporting
- [ ] Audit log access

**Need-to-Know Justification**:
(Why do these personnel need full admin access?)

_________________________________________________________________________

**MFA Required**: [ ] Yes  [ ] No

---

## Role 2: Security Analyst

**MISP Role**: User (or custom "Analyst" role)
**CIP Requirement**: CIP-004 R3.2 (Authorized users)

**Personnel in This Role**:
1. Name: _____________________ Email: _____________________ Job Title: _____________________
2. Name: _____________________ Email: _____________________ Job Title: _____________________
3. Name: _____________________ Email: _____________________ Job Title: _____________________
4. (Continue as needed)

**Total Count**: _____ (Typical: 5-20)

**Responsibilities**:
- [ ] Create security events
- [ ] Add IOCs and attributes
- [ ] Tag events with taxonomies
- [ ] Search threat intelligence
- [ ] Correlate events
- [ ] View organization events only

**Cannot Do**:
- [ ] User management
- [ ] System configuration
- [ ] Publish events externally (without approval)

**Need-to-Know Justification**:
_________________________________________________________________________

**MFA Required**: [ ] Yes  [ ] No

---

## Role 3: Incident Responder

**MISP Role**: Publisher (or custom "Incident Response" role)
**CIP Requirement**: CIP-008 R1 (Incident response team)

**Personnel in This Role**:
1. Name: _____________________ Email: _____________________ Job Title: _____________________
2. Name: _____________________ Email: _____________________ Job Title: _____________________
3. Name: _____________________ Email: _____________________ Job Title: _____________________

**Total Count**: _____ (Typical: 5-10)

**Responsibilities**:
- [ ] Create incident events
- [ ] Publish events (to E-ISAC if needed)
- [ ] Attach forensic evidence
- [ ] Track incident timeline
- [ ] Report to E-ISAC within 1 hour (CIP-008)

**Need-to-Know Justification**:
_________________________________________________________________________

**MFA Required**: [ ] Yes  [ ] No

---

## Role 4: Vulnerability Manager

**MISP Role**: Custom "Vulnerability Manager" role
**CIP Requirement**: CIP-010 R3 (Vulnerability assessments)

**Personnel in This Role**:
1. Name: _____________________ Email: _____________________ Job Title: _____________________
2. Name: _____________________ Email: _____________________ Job Title: _____________________

**Total Count**: _____ (Typical: 2-5)

**Responsibilities**:
- [ ] Create vulnerability assessment events
- [ ] Track 15-month assessment cycle
- [ ] Track 35-day patch compliance
- [ ] Import vulnerability scan results
- [ ] Document risk acceptances

**Need-to-Know Justification**:
_________________________________________________________________________

**MFA Required**: [ ] Yes  [ ] No

---

## Role 5: Supply Chain Risk Manager

**MISP Role**: Custom "Supply Chain Manager" role
**CIP Requirement**: CIP-013 R1 (Supply chain risk management)

**Personnel in This Role**:
1. Name: _____________________ Email: _____________________ Job Title: _____________________
2. Name: _____________________ Email: _____________________ Job Title: _____________________

**Total Count**: _____ (Typical: 2-5)

**Responsibilities**:
- [ ] Track vendor security notifications
- [ ] Create vendor notification events
- [ ] Track vendor remediation status
- [ ] Conduct vendor risk assessments

**Need-to-Know Justification**:
_________________________________________________________________________

**MFA Required**: [ ] Yes  [ ] No

---

## Role 6: Read-Only Viewer

**MISP Role**: Read Only
**CIP Requirement**: CIP-003 R2 (Security awareness)

**Personnel in This Role**:
(Anyone needing security awareness access)

**Total Count**: _____ (Could be: All employees with BES access)

**Responsibilities**:
- [ ] View threat intelligence for awareness
- [ ] Search events
- [ ] Generate reports for training

**Cannot Do**:
- [ ] Create or edit events
- [ ] Export data
- [ ] Tag events

**Need-to-Know Justification**:
_________________________________________________________________________

**MFA Required**: [ ] Optional (low privilege)

---

## Role Summary Table

| Role Name | MISP Role | Count | MFA Required | CIP Standard |
|-----------|-----------|-------|--------------|--------------|
| CIP Compliance Admin | Admin | _____ | Yes | CIP-004 R3.1 |
| Security Analyst | User | _____ | Yes | CIP-004 R3.2 |
| Incident Responder | Publisher | _____ | Yes | CIP-008 R1 |
| Vulnerability Manager | Custom | _____ | Yes | CIP-010 R3 |
| Supply Chain Manager | Custom | _____ | Yes | CIP-013 R1 |
| Read-Only Viewer | Read Only | _____ | Optional | CIP-003 R2 |
| **TOTAL USERS** | | **_____** | | |

## Custom Roles Needed

(If MISP's default roles don't match our needs)

**Custom Role 1**: _______________________________
- Based on: [ ] Admin  [ ] User  [ ] Read Only
- Additional Permissions: _______________________________
- Restricted Permissions: _______________________________

**Custom Role 2**: _______________________________
- Based on: [ ] Admin  [ ] User  [ ] Read Only
- Additional Permissions: _______________________________
- Restricted Permissions: _______________________________
```

**Where to Save**: `research/person1/user-roles-definition.md`

---

#### TASK 1.4: Document Personnel Access Tracking Requirements

**Time Estimate**: 2 hours

**What to Research**:

1. **HR Integration**:
   - How does HR notify IT of terminations/role changes?
   - Is there an automated system?
   - What is the typical notice period?

2. **Background Checks**:
   - Who tracks personnel risk assessments?
   - How often are background checks renewed? (CIP-004: 7 years)
   - Where is this information stored?

3. **Training Records**:
   - Who tracks CIP-003 security awareness training?
   - How often is training required? (CIP-003: 15 months)
   - Where are training records stored?

4. **Access Reviews**:
   - How often should we review MISP access? (Recommend: Quarterly)
   - Who conducts the reviews?

**Deliverable**: Complete the template below

---

**TEMPLATE: Personnel Access Tracking**

```markdown
# Personnel Access Tracking for CIP-004 Compliance

## HR Integration

**HR System**: _______________________________

**Termination Notification Process**:
- [ ] Automated (via API/webhook)
- [ ] Email to IT Security
- [ ] Manual check of HR system
- [ ] Other: _______________________________

**Typical Notice Period**: _____ hours/days

**HR Contact for MISP Access**:
- Name: _______________________________
- Email: _______________________________
- Phone: _______________________________

## Personnel Risk Assessments (CIP-004 R3)

**Background Check Requirements**:
- Initial background check before access: [ ] Yes  [ ] No
- Renewal period: [ ] 7 years  [ ] Other: _______
- Who performs background checks: _______________________________
- Where are records stored: _______________________________

**Personnel with MISP Access Requiring Background Checks**:
(All personnel with access to BCSI)

- [ ] All MISP users
- [ ] Admin and Analyst roles only
- [ ] Other: _______________________________

## Security Awareness Training (CIP-003 R2)

**Training System**: _______________________________

**Training Frequency**: [ ] Annual  [ ] Every 15 months  [ ] Other: _______

**Training Content Includes**:
- [ ] ICS/SCADA threats
- [ ] Phishing awareness
- [ ] Password security
- [ ] Incident reporting procedures
- [ ] BCSI protection (CIP-011)

**Training Records Stored In**: _______________________________

**Training Coordinator**:
- Name: _______________________________
- Email: _______________________________

**Can MISP threat intelligence be used for training?**: [ ] Yes  [ ] No

## Access Reviews

**Review Frequency**: [ ] Quarterly  [ ] Semi-annually  [ ] Annually

**Review Process**:
1. Generate list of all MISP users
2. Verify each user still needs access (need-to-know)
3. Verify MFA is enabled
4. Verify training is current (15 months)
5. Document review for audit

**Reviewer(s)**:
- Primary: _______________________________
- Secondary: _______________________________

**Review Documentation Storage**: _______________________________

## Access Revocation (CIP-004 R5)

**Revocation Timeline**: Within 24 hours of:
- [ ] Termination
- [ ] Role change (no longer needs MISP access)
- [ ] Extended leave (>30 days)

**Revocation Process**:
1. Receive notification from HR
2. Disable MISP account
3. Revoke API keys
4. Terminate active sessions
5. Document revocation

**Who performs revocation**: _______________________________

**Emergency After-Hours Contact**: _______________________________

## Audit Evidence

**Documentation to Maintain for NERC CIP Audits**:
- [ ] Current user access list (quarterly)
- [ ] Access review records (quarterly)
- [ ] Termination/revocation logs (24-hour compliance)
- [ ] Background check records (7-year validity)
- [ ] Training completion records (15-month compliance)

**Where to Store Audit Evidence**: _______________________________
```

**Where to Save**: `research/person1/personnel-tracking-requirements.md`

---

### SECTION 3: ORGANIZATION STRUCTURE (CIP-011)

**CIP Requirement**: CIP-011 R1 - BCSI stays within organization

**Current State**: Single organization ("Hell")

**Your Goal**: Define organization structure for sharing controls

---

#### TASK 1.5: Define Organization & Sharing Requirements

**Time Estimate**: 2 hours

**What to Research**:

1. **Organization Name**:
   - What should the MISP organization be called?
   - Legal entity name or operating name?

2. **Sharing Communities**:
   - Will we share with E-ISAC? (if member)
   - Will we share with other utilities?
   - Will we share with parent company / subsidiaries?

3. **Default Sharing Policy**:
   - Should events default to "Your organization only"? (CIP-011 requirement)
   - Who can override this to share externally?

**Deliverable**: Complete the template below

---

**TEMPLATE: Organization & Sharing Configuration**

```markdown
# MISP Organization & Sharing Configuration

## Primary Organization

**Organization Name**: _______________________________
(Example: "GridSec Utilities" or "Example Electric Company")

**Organization UUID**: (Will be auto-generated by MISP)

**Organization Contact**:
- Name: _______________________________
- Email: _______________________________
- Phone: _______________________________

**Organization Type**: [ ] Electric Utility  [ ] Energy Provider  [ ] Other: _______

## Sharing Policy (CIP-011 Compliance)

**Default Event Distribution**:
- [ ] Your organization only (CIP-011 BCSI protection - RECOMMENDED)
- [ ] This community only (share with connected MISP instances)
- [ ] Connected communities (wider sharing)
- [ ] All communities (public - NOT RECOMMENDED for utilities)

**CIP-011 Justification**:
MISP events may contain BCSI (BES Cyber System Information) including:
- Asset inventory information
- Vulnerability details
- Network architecture
- Incident response procedures

Default distribution MUST be "Your organization only" per CIP-011 R1.

**Who Can Override Default Distribution**:
(Personnel authorized to share BCSI externally)

1. Name: _____________________ Role: _____________________ Approval Required: [ ] Yes  [ ] No
2. Name: _____________________ Role: _____________________ Approval Required: [ ] Yes  [ ] No

## Sharing Groups

**Sharing Group 1: Internal Only** (Default)
- Members: Our organization only
- Purpose: All BCSI-containing events
- Distribution Level: Organization only

**Sharing Group 2: E-ISAC Members** (If applicable)
- Members: Our organization + E-ISAC member orgs
- Purpose: Incident reporting, sector-wide threats
- Distribution Level: This community
- E-ISAC Membership Status: [ ] Active Member  [ ] Not a Member  [ ] Pending

**Sharing Group 3: Trusted Partners** (If applicable)
- Members: List partner organizations
  1. _______________________________
  2. _______________________________
- Purpose: Mutual threat intelligence sharing
- Distribution Level: Connected communities

## E-ISAC Integration (CIP-008)

**E-ISAC Membership**:
- [ ] We are E-ISAC members
- [ ] We are NOT E-ISAC members (consider joining)
- [ ] Membership pending

**If E-ISAC Member**:
- Membership ID: _______________________________
- Organization Contact: _______________________________
- Portal Access: [ ] Yes  [ ] No
- Sync Server Available: [ ] Yes  [ ] No

**E-ISAC Incident Reporting**:
- Who is authorized to report to E-ISAC: _______________________________
- Reporting timeline: Within 1 hour (CIP-008 requirement)
- Contact method: [ ] Portal  [ ] Email  [ ] Phone  [ ] MISP Sync

## External MISP Synchronization

**Do we plan to sync with other MISP instances?**:
- [ ] Yes - E-ISAC MISP server
- [ ] Yes - Other utility's MISP server(s)
- [ ] No - Internal use only

**If Yes, List External MISP Servers**:

**Server 1**:
- Name: _______________________________
- URL: _______________________________
- Purpose: _______________________________
- Sync Direction: [ ] Pull Only  [ ] Push Only  [ ] Bidirectional

**Server 2**:
- Name: _______________________________
- URL: _______________________________
- Purpose: _______________________________
- Sync Direction: [ ] Pull Only  [ ] Push Only  [ ] Bidirectional

## BCSI Handling Procedures

**Events Containing BCSI Must**:
- [ ] Be tagged with "cip-011:bcsi" taxonomy
- [ ] Have distribution set to "Your organization only"
- [ ] Include BCSI warning in event description
- [ ] Be reviewed before any external sharing

**BCSI Review Process** (if sharing externally):
1. Event creator requests external sharing
2. CIP Compliance Officer reviews event
3. BCSI information is redacted or removed
4. Approval is documented
5. Distribution level is changed
6. Event is published

**BCSI Approval Authority**: _______________________________

**Review Documentation Storage**: _______________________________
```

**Where to Save**: `research/person1/organization-sharing-config.md`

---

### SECTION 4: PASSWORD & CREDENTIAL POLICIES (CIP-004, CIP-011)

**CIP Requirement**: CIP-007 R5 - Password complexity, change requirements

**Your Goal**: Define password policies for NERC CIP compliance

---

#### TASK 1.6: Document Password Policy Requirements

**Time Estimate**: 1-2 hours

**What to Research**:

1. **Current Corporate Password Policy**:
   - Minimum length
   - Complexity requirements
   - Change frequency
   - Account lockout settings

2. **Exceptions for Service Accounts**:
   - Are there service accounts that need MISP API access?
   - Do they use different password rules?

3. **Password Manager Usage**:
   - Does the organization use a password manager?
   - Can we store MISP credentials in it?

**Deliverable**: Complete the template below

---

**TEMPLATE: Password & Credential Policy**

```markdown
# MISP Password & Credential Policy

## Corporate Password Policy

**Current Policy**:
- Minimum Length: _____ characters (CIP-007 R5: Minimum 8, recommend 12+)
- Complexity Requirements:
  - [ ] Uppercase letter required
  - [ ] Lowercase letter required
  - [ ] Number required
  - [ ] Special character required
- Password Change Frequency: Every _____ days (CIP-007 R5: 15 months for utilities)
- Password History: Cannot reuse last _____ passwords (CIP-007 R5: Minimum 3)

**Account Lockout**:
- Failed Attempts: _____ attempts (Recommend: 5)
- Lockout Duration: _____ minutes (Recommend: 15-30)
- Lockout Reset: [ ] Automatic  [ ] Manual (by admin)

## MISP-Specific Password Requirements

**For MISP Local Accounts** (if not using SSO):

**Minimum Password Length**: [ ] 12 characters  [ ] 15 characters  [ ] Other: _____

**Complexity Requirements**:
- [ ] Uppercase (A-Z)
- [ ] Lowercase (a-z)
- [ ] Numbers (0-9)
- [ ] Special characters (!@#$%^&*)

**Password Expiration**:
- [ ] 90 days (standard IT policy)
- [ ] 15 months (CIP-007 R5 utilities exemption)
- [ ] Never expire (if using MFA and SSO)

**Force Password Change**:
- [ ] On first login
- [ ] After password reset
- [ ] After X days

## API Key Management

**API Keys for Automation**:
- Who can generate API keys: _______________________________
- API key rotation frequency: [ ] Annually  [ ] Bi-annually  [ ] Never (unless compromised)
- Where are API keys stored: _______________________________

**Service Accounts**:
(For automated scripts, backup scripts, etc.)

| Service Account | Purpose | API Key Location | Owner |
|-----------------|---------|------------------|-------|
| misp-backup | Daily backups | /opt/misp/.backup-key | sysadmin@example.com |
| misp-feeds | Feed automation | /opt/misp/.feed-key | security@example.com |
| _____________ | _____________ | _____________ | _____________ |

## Password Manager Integration

**Corporate Password Manager**: _______________________________

**Can store MISP credentials**: [ ] Yes  [ ] No

**Access to password manager**:
- [ ] All MISP users have access
- [ ] Only admins have access
- [ ] Not applicable (no password manager)

## Emergency Access

**Break-Glass Account**:
(For emergency access if SSO fails)

- Account Name: emergency-admin or break-glass
- Password Storage: [ ] Physical safe  [ ] Password manager  [ ] Other: _______
- Who has access: _______________________________
- Usage logged: [ ] Yes  [ ] No

**Last Resort Access**:
- [ ] Root access to MISP server
- [ ] Database direct access
- [ ] Container shell access

## Credential Handling (CIP-011)

**Storing Credentials**:
- /opt/misp/PASSWORDS.txt: [ ] 600 permissions  [ ] Encrypted
- /opt/misp/.env: [ ] 600 permissions  [ ] Encrypted
- Backup of credentials: _______________________________

**Who has access to credential files**:
1. _______________________________
2. _______________________________

**Credential Rotation Schedule**:
- Admin passwords: Every _______
- Database passwords: Every _______
- API keys: Every _______
- GPG passphrase: [ ] Never (data loss)  [ ] Document exception

## Compliance Mapping

| Requirement | Implementation | Compliant |
|-------------|----------------|-----------|
| CIP-007 R5.1 - Password length (8+ chars) | _____ characters | [ ] Yes [ ] No |
| CIP-007 R5.2 - Password complexity | _______________ | [ ] Yes [ ] No |
| CIP-007 R5.3 - Password change (15 months) | Every _____ | [ ] Yes [ ] No |
| CIP-007 R5.4 - Password history (3+) | _____ passwords | [ ] Yes [ ] No |
| CIP-004 R4 - MFA for remote access | _______________ | [ ] Yes [ ] No |
```

**Where to Save**: `research/person1/password-policy.md`

---

### SECTION 5: AUDIT LOGGING & ACCESS TRACKING (CIP-004, CIP-007)

**CIP Requirement**: CIP-007 R4 - Logging of security events

**Your Goal**: Define what user actions should be logged for audit

---

#### TASK 1.7: Define Audit Logging Requirements

**Time Estimate**: 1-2 hours

**What to Research**:

1. **What user actions must be audited?**:
   - Login attempts (success and failure)
   - User creation/modification/deletion
   - Role changes
   - Permission changes
   - Password resets
   - API key generation
   - Event publication (especially to external orgs)

2. **How long should audit logs be retained?**:
   - CIP-007 R4: Minimum 90 days
   - CIP-004: Access reviews quarterly (need 3+ months)
   - Audit cycles: 3 years

3. **Who reviews audit logs?**:
   - How often?
   - What are they looking for?

**Deliverable**: Complete the template below

---

**TEMPLATE: Audit Logging Requirements**

```markdown
# MISP Audit Logging Requirements

## User Actions to Log (CIP-007 R4)

**Authentication Events**:
- [ ] Successful logins (timestamp, username, source IP)
- [ ] Failed login attempts (timestamp, username, source IP)
- [ ] Logout events
- [ ] Session timeouts
- [ ] Password changes
- [ ] Password reset requests
- [ ] MFA enrollment
- [ ] MFA authentication (success/failure)

**User Management Events** (Admin actions):
- [ ] User account creation (who, when, what role)
- [ ] User account modification (role changes, email changes)
- [ ] User account deletion
- [ ] User account enable/disable
- [ ] Role assignment changes
- [ ] Permission changes

**Privilege Escalation Events**:
- [ ] Admin actions (any action by admin role)
- [ ] User becoming admin
- [ ] API key generation
- [ ] API key revocation

**Event Publication Events** (CIP-011 BCSI tracking):
- [ ] Event published externally (who, what, where, distribution level)
- [ ] Event distribution level changed
- [ ] Event shared with external organization
- [ ] Sharing group membership changes

**System Configuration Events**:
- [ ] Taxonomy enable/disable
- [ ] Feed enable/disable
- [ ] Server settings changes
- [ ] Organization settings changes

## Log Retention

**Retention Period**:
- [ ] 90 days (CIP-007 R4 minimum)
- [ ] 1 year (recommended)
- [ ] 3 years (align with CIP audit cycles)

**Current Retention**: _____ days (verify with sysadmin)

**Log Storage Location**: /opt/misp/logs/

**Log Rotation**:
- Max file size: _____ MB
- Max files: _____
- Total storage: _____ GB

**Log Archival**:
- [ ] Logs archived after rotation
- [ ] Logs sent to SIEM (long-term storage)
- [ ] Logs backed up daily
- Archive location: _______________________________

## Log Review Process

**Review Frequency**:
- [ ] Daily (for critical events)
- [ ] Weekly (for routine review)
- [ ] Quarterly (for access review / CIP-004)

**Reviewer(s)**:
- Daily: _______________________________
- Weekly: _______________________________
- Quarterly: _______________________________

**What to Look For**:
- [ ] Unusual login times (after hours)
- [ ] Failed login attempts (>5 attempts)
- [ ] Changes to admin accounts
- [ ] External event publication (BCSI leakage)
- [ ] Disabled accounts attempting login
- [ ] API key generation
- [ ] Privilege escalation

**Review Documentation**:
- [ ] Log review documented in security log
- [ ] Findings escalated to management
- [ ] CIP compliance evidence saved

## Audit Evidence for NERC CIP

**CIP-004 Evidence** (Personnel Access):
- [ ] Quarterly user access list
- [ ] Access review documentation
- [ ] Termination logs (24-hour compliance)

**CIP-007 Evidence** (Security Event Logging):
- [ ] 90-day log retention verification
- [ ] Log review procedures documented
- [ ] SIEM integration confirmed

**CIP-011 Evidence** (BCSI Protection):
- [ ] Logs showing BCSI event access
- [ ] Logs showing external publication (with approval)
- [ ] Access control effectiveness

**Where to Store Audit Evidence**: _______________________________

## SIEM Integration

**Do logs forward to SIEM?**: [ ] Yes  [ ] No  [ ] Planned

**If Yes**:
- SIEM Platform: _______________________________
- Log forwarding method: [ ] Syslog  [ ] HEC  [ ] File copy  [ ] Other
- SIEM index/sourcetype: _______________________________

**If No**:
- Plan to integrate: [ ] Yes  [ ] No
- Timeline: _______________________________
- See Person 3's research for SIEM integration details

## Alerting on Critical Events

**Real-Time Alerts Needed For**:
- [ ] 5+ failed login attempts (potential brute force)
- [ ] Admin account creation
- [ ] API key generated
- [ ] Event published externally (BCSI tracking)
- [ ] User disabled account attempting login

**Alert Delivery**:
- [ ] Email to: _______________________________
- [ ] SIEM alert
- [ ] SMS/Page to on-call
- [ ] Other: _______________________________

## Log Security

**Log File Permissions**:
- Owner: [ ] misp-owner  [ ] root  [ ] Other: _______
- Permissions: [ ] 644 (read-only for non-owner)  [ ] 600 (owner only)

**Log Integrity**:
- [ ] Logs digitally signed (tamper detection)
- [ ] Logs forwarded to write-once storage
- [ ] Logs on separate partition (prevent filling root)

**Log Access Control**:
Who can read MISP audit logs:
1. _______________________________
2. _______________________________
3. _______________________________
```

**Where to Save**: `research/person1/audit-logging-requirements.md`

---

## DELIVERABLES CHECKLIST

By the end of your research, you should have completed:

- [ ] **Task 1.1**: Authentication Assessment (authentication-assessment.md)
- [ ] **Task 1.2**: Azure AD Integration Plan (azure-ad-integration-plan.md) - If applicable
- [ ] **Task 1.3**: User Roles Definition (user-roles-definition.md)
- [ ] **Task 1.4**: Personnel Tracking Requirements (personnel-tracking-requirements.md)
- [ ] **Task 1.5**: Organization & Sharing Config (organization-sharing-config.md)
- [ ] **Task 1.6**: Password Policy (password-policy.md)
- [ ] **Task 1.7**: Audit Logging Requirements (audit-logging-requirements.md)

**Total Files**: 7 markdown documents
**Total Estimated Time**: 20-25 hours

---

## WHERE TO SAVE YOUR WORK

Create this directory structure:

```
/home/gallagher/misp-install/misp-install/research/person1/
├── authentication-assessment.md
├── azure-ad-integration-plan.md (if applicable)
├── user-roles-definition.md
├── personnel-tracking-requirements.md
├── organization-sharing-config.md
├── password-policy.md
└── audit-logging-requirements.md
```

---

## WHO TO CONTACT FOR INFORMATION

**Azure AD / Identity**:
- Contact: _____________________________ (IT/Identity team)

**HR / Personnel**:
- Contact: _____________________________ (HR for terminations, background checks)

**NERC CIP Compliance**:
- Contact: _____________________________ (Compliance officer)

**Security Policies**:
- Contact: _____________________________ (CISO or security team)

**Training Coordinator**:
- Contact: _____________________________ (CIP-003 training)

---

## TIPS FOR SUCCESS

1. **Schedule Meetings Early**: You'll need to talk to HR, IT, and Compliance
2. **Use Templates**: Fill out every field - "Unknown" or "TBD" is better than blank
3. **Ask "Why"**: Understanding the reason helps with better solutions
4. **Document Everything**: Even "we don't have this" is useful information
5. **Prioritize MFA**: This is the biggest gap - focus on Task 1.1 and 1.2 first

---

## QUESTIONS?

If you're stuck or need clarification:
1. Review the NERC CIP Audit Report: `docs/NERC_CIP_AUDIT_REPORT.md`
2. Check current configuration: `sudo cat /opt/misp/.env`
3. Ask the team lead or escalate to me for guidance

---

**Good luck with your research! Your work is foundational for securing our MISP instance.**

**Remember**: Better to have incomplete but accurate information than complete but wrong information.

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Assigned To**: Person 1
**Status**: Ready to Start
