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

