## Section 1: Core Security Architecture

### 1.1 Current Implementation

**Location**: `docs/SECURITY_ARCHITECTURE.md`

**Implemented Features:**
- ✅ Dedicated system user (`misp-owner`)
- ✅ Least privilege principle
- ✅ ACL-based log directory access
- ✅ Secure credential storage (600 permissions)
- ✅ CIS Benchmarks compliance
- ✅ NIST SP 800-53 AC-6 compliance

### 1.2 NERC CIP Medium Enhancements Needed

#### 1.2.1 Multi-Factor Authentication (MFA)

**Requirement**: CIP-004 R4 - Access management for Medium Impact systems

**Current Status**: ❌ NOT IMPLEMENTED

**Implementation Plan:**

**File**: `scripts/configure-rbac-mfa.py`

```python
"""
Configure Multi-Factor Authentication for NERC CIP Medium
Implements CIP-004 R4 requirements
"""

MFA_METHODS = {
    'totp': 'Time-based One-Time Password (Google Authenticator)',
    'yubikey': 'YubiKey Hardware Token',
    'duo': 'Duo Security Push',
    'azure_mfa': 'Azure Entra ID MFA (recommended for M365 orgs)'
}

NERC_CIP_MFA_REQUIREMENTS = {
    'enforce_for_roles': [
        'admin',           # System administrators
        'org_admin',       # Organization administrators
        'sync_user',       # Users with sharing privileges
        'publisher'        # Users who can publish events
    ],
    'grace_period_hours': 24,  # 24-hour grace period for enrollment
    'backup_codes': 10,        # Number of backup codes to generate
    'session_timeout_minutes': 60  # Re-auth after 60 minutes
}
```

**MISP Settings to Configure:**
- `Security.require_2fa` = true
- `Security.2fa_methods` = ['totp', 'yubikey']
- `Security.2fa_grace_period` = 86400
- `Security.password_policy_enforce` = true

**Audit Evidence**: MFA enrollment logs, authentication logs showing 2FA usage

---

#### 1.2.2 Role-Based Access Control (RBAC)

**Requirement**: CIP-004 R3 - Authorization based on need-to-know

**Current Status**: ⚠️ PARTIAL (MISP has roles, but no NERC CIP-specific configuration)

**Implementation Plan:**

**File**: `scripts/configure-nerc-cip-roles.py`

```python
"""
Configure NERC CIP Medium Impact Role Structure
Maps organizational roles to MISP permissions
"""

NERC_CIP_ROLES = {
    'cip_admin': {
        'name': 'CIP Administrator',
        'description': 'NERC CIP compliance officer with full access',
        'permissions': [
            'admin',           # Full system access
            'audit_log_view',  # View all audit logs
            'user_management', # Manage user accounts
            'taxonomy_editor'  # Manage NERC CIP taxonomies
        ],
        'cip_requirement': 'CIP-004 R3.1',
        'max_users': 3  # Limit administrative accounts
    },

    'cip_analyst': {
        'name': 'Cyber Security Analyst',
        'description': 'Analyzes threats, creates events, no administrative access',
        'permissions': [
            'auth',            # Authentication required
            'add_event',       # Create security events
            'tag',             # Add tags/taxonomies
            'view_own_org',    # View own organization only
            'search'           # Search threats
        ],
        'cip_requirement': 'CIP-004 R3.2',
        'max_users': 20
    },

    'cip_readonly': {
        'name': 'Security Awareness Viewer',
        'description': 'Read-only access for training/awareness (CIP-003)',
        'permissions': [
            'auth',
            'view_own_org',
            'search'
        ],
        'cip_requirement': 'CIP-003 R2',
        'max_users': 100
    },

    'cip_incident_responder': {
        'name': 'Incident Responder',
        'description': 'Creates/manages incidents, reports to E-ISAC (CIP-008)',
        'permissions': [
            'auth',
            'add_event',
            'publish',         # Publish to E-ISAC
            'tag',
            'view_own_org'
        ],
        'cip_requirement': 'CIP-008 R1',
        'max_users': 10
    },

    'cip_vulnerability_manager': {
        'name': 'Vulnerability Assessment Manager',
        'description': 'Manages vulnerability assessments (CIP-010)',
        'permissions': [
            'auth',
            'add_event',
            'tag',
            'view_own_org',
            'galaxy_editor'    # Manage vulnerability intel
        ],
        'cip_requirement': 'CIP-010 R3',
        'max_users': 5
    },

    'cip_supply_chain': {
        'name': 'Supply Chain Risk Manager',
        'description': 'Tracks vendor notifications (CIP-013)',
        'permissions': [
            'auth',
            'add_event',
            'tag',
            'view_own_org',
            'add_org'          # Track vendors as orgs
        ],
        'cip_requirement': 'CIP-013 R1',
        'max_users': 5
    }
}

def create_nerc_cip_roles(api_key: str, misp_url: str):
    """Create NERC CIP-specific roles in MISP"""
    # Implementation details
    pass

def assign_users_to_roles(api_key: str, user_email: str, role: str):
    """Assign users to NERC CIP roles"""
    # Implementation details
    pass

def audit_role_assignments():
    """Generate CIP-004 R4 audit report of role assignments"""
    # Returns: PDF report of who has access to what
    pass
```

**Audit Evidence**: Role assignment matrix, quarterly access reviews

---

### 1.3 Encryption Requirements

**Requirement**: CIP-011 R1 - Encryption for BCSI at rest and in transit

**Current Status**: ✅ IMPLEMENTED (TLS, encrypted Docker volumes)

**Enhancement Needed**: Key management documentation

**File**: `docs/ENCRYPTION_KEY_MANAGEMENT.md`

**Topics to Cover:**
- Encryption key rotation procedure
- Backup encryption requirements
- Key escrow/recovery procedures
- Integration with Azure Key Vault (future)

---

## Section 2: Access Control & Authentication (CIP-004/CIP-005)

### 2.1 Personnel Risk Assessment (CIP-004 R3)

**Requirement**: Personnel with access to BES Cyber Systems must have risk assessments

**MISP Integration**: Track personnel access in MISP

**Implementation Plan:**

**File**: `scripts/track-personnel-access.py`

```python
"""
Personnel Access Tracking for CIP-004 R3
Links MISP user accounts to HR personnel records
"""

class PersonnelAccessTracker:
    """
    Tracks personnel with MISP access for CIP-004 compliance
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def get_all_users_with_access(self) -> List[Dict]:
        """Returns list of all MISP users with access"""
        pass

    def check_risk_assessment_current(self, user_email: str) -> bool:
        """Check if risk assessment is current (7 years for background check)"""
        pass

    def check_training_current(self, user_email: str) -> bool:
        """Check if CIP-003 R2 training is current (15 months)"""
        pass

    def generate_cip_004_compliance_report(self) -> str:
        """Generate quarterly report of all personnel with access"""
        # Returns: PDF report suitable for audit
        pass
```

**Audit Evidence**: Quarterly personnel access reports

---

### 2.2 Access Revocation (CIP-004 R5)

**Requirement**: Revoke access within 24 hours of termination/role change

**Implementation Plan:**

**File**: `scripts/automated-access-revocation.py`

```python
"""
Automated Access Revocation
Integrates with HR system to revoke MISP access
"""

HR_INTEGRATION_METHODS = {
    'azure_ad': 'Azure Entra ID SSO (automated)',
    'ldap': 'LDAP/Active Directory (automated)',
    'manual': 'Manual webhook from HR system'
}

def revoke_user_access(user_email: str, reason: str):
    """
    Revoke MISP access within CIP-004 24-hour requirement

    Args:
        user_email: User to revoke
        reason: Termination, role change, etc.
    """
    # 1. Disable MISP account
    # 2. Revoke API keys
    # 3. Terminate active sessions
    # 4. Log revocation for audit
    # 5. Generate CIP-004 R5 evidence
    pass
```

**Audit Evidence**: Access revocation logs with timestamps

---

## Section 3: Electronic Security Perimeter Monitoring (CIP-005)

### 3.1 IOC Export for EAP Firewalls

**Requirement**: CIP-005 R2 - Block malicious traffic at Electronic Access Points

**Current Status**: ⚠️ PARTIAL (IOCs available in MISP, no automated export)

**Implementation Plan:**

**File**: `scripts/export-iocs-for-firewall.py`

```python
"""
Export IOCs from MISP for Electronic Access Point firewalls
Supports multiple firewall formats
"""

SUPPORTED_FIREWALLS = {
    'palo_alto': {
        'format': 'external_dynamic_list',
        'url_format': 'https://misp.example.com/attributes/text/download/ip-src/',
        'update_interval': 3600  # 1 hour
    },
    'fortinet': {
        'format': 'threat_feed',
        'update_interval': 3600
    },
    'cisco': {
        'format': 'security_intelligence_feed',
        'update_interval': 3600
    },
    'checkpoint': {
        'format': 'ioc_feed',
        'update_interval': 3600
    }
}

def export_iocs_for_eap(firewall_type: str, output_path: str):
    """
    Export MISP IOCs in firewall-compatible format

    Categories:
    - Malicious IPs (block at EAP)
    - Malicious domains (DNS filtering)
    - Known C2 infrastructure
    - ICS-specific threats (Dragos, Claroty intel)
    """
    pass

def generate_cip_005_compliance_report():
    """
    Generate CIP-005 R2 evidence:
    - Number of IOCs blocking at EAPs
    - Number of blocked connection attempts
    - Malicious traffic prevented
    """
    pass
```

**Firewall Configuration Examples:**

```bash
# Palo Alto External Dynamic List
# Admin > External Dynamic Lists > IP Address
# Source: https://misp.example.com/attributes/text/download/ip-src/json
# Update Interval: Hourly

# Fortinet Threat Feed
config system external-resource
    edit "MISP_IOC_Feed"
        set type domain
        set resource "https://misp.example.com/attributes/text/download/domain/txt"
        set refresh 3600
    next
end

# Cisco Security Intelligence Feed
# Configuration > ASA FirePOWER Configuration > Policies > Access Control
# Objects > Security Intelligence > Network Lists
# URL: https://misp.example.com/attributes/text/download/ip-src/txt
```

**Audit Evidence**:
- EAP firewall configuration screenshots
- Logs showing blocked connections from MISP IOCs
- Monthly reports of threats blocked

---

### 3.2 EAP Log Integration with MISP

**Requirement**: CIP-007 R4 - Security event logging

**Implementation Plan:**

**File**: `scripts/ingest-eap-logs.py`

```python
"""
Ingest EAP (Electronic Access Point) logs into MISP
Creates events for suspicious activity at perimeter
"""

def ingest_firewall_alerts(log_source: str, alert_data: Dict):
    """
    Convert firewall alerts to MISP events

    Triggers:
    - Multiple failed authentication attempts at EAP
    - Connection attempts to known malicious IPs
    - Unusual protocol usage (Modbus, DNP3 from outside ESP)
    - Port scanning detected
    """
    pass

def create_cip_005_incident_event(alert: Dict) -> str:
    """
    Create MISP event for CIP-005 Electronic Security Perimeter incident

    Returns: Event ID for incident response workflow
    """
    pass
```

**Audit Evidence**: MISP events showing EAP monitoring alerts

---

## Section 4: Internal Network Security Monitoring (CIP-015)

### 4.1 Architecture for CIP-015 Compliance

**Requirement**: CIP-015 R1 - Detect malicious communications inside ESP

**NEW STANDARD** (Effective June 2025)

**Integration Points:**
```
Dragos Platform ──┐
Nozomi Networks ──┼──> MISP IOC Export ──> Detection Rules
Claroty ──────────┤
Darktrace ────────┘
```

**Implementation Plan:**

**File**: `scripts/configure-cip-015-monitoring.py`

```python
"""
CIP-015 Internal Network Security Monitoring Configuration
Exports IOCs for ICS network monitoring tools
"""

ICS_MONITORING_PLATFORMS = {
    'dragos': {
        'name': 'Dragos Platform',
        'api_endpoint': '/api/v1/iocs',
        'supported_ioc_types': ['ip', 'domain', 'hash', 'protocol_anomaly']
    },
    'nozomi': {
        'name': 'Nozomi Networks Guardian',
        'api_endpoint': '/api/open/v2/threats',
        'supported_ioc_types': ['ip', 'domain', 'mac', 'asset']
    },
    'claroty': {
        'name': 'Claroty Platform',
        'api_endpoint': '/api/v1/indicators',
        'supported_ioc_types': ['ip', 'domain', 'hash']
    },
    'darktrace': {
        'name': 'Darktrace Industrial',
        'api_endpoint': '/api/v1/iocs',
        'supported_ioc_types': ['ip', 'domain', 'behavior']
    }
}

def export_iocs_for_ics_platform(platform: str, api_key: str):
    """
    Export MISP IOCs to ICS network monitoring platform

    IOC Categories for CIP-015:
    - ICS-specific malware (TRISIS, INDUSTROYER, etc.)
    - Protocol-level attacks (Modbus function code abuse)
    - Lateral movement indicators
    - Known C2 infrastructure
    - Insider threat indicators
    """
    pass

def ingest_cip_015_alerts(platform: str, alert_data: Dict):
    """
    Ingest CIP-015 alerts from ICS monitoring platforms into MISP
    Creates incident events for analysis
    """
    pass

def generate_cip_015_compliance_report():
    """
    Generate CIP-015 evidence:
    - Number of malicious communications detected inside ESP
    - Response actions taken
    - Mean time to detection (MTTD)
    - Mean time to response (MTTR)
    """
    pass
```

**CIP-015 Detection Use Cases:**

| Use Case | MISP IOC Category | Detection Method |
|----------|-------------------|------------------|
| **ICS Malware Detection** | `ics-malware` tag | File hash matching |
| **Modbus Function Code Abuse** | `modbus-attack` tag | Protocol analysis |
| **DNP3 Unauthorized Commands** | `dnp3-attack` tag | Protocol analysis |
| **Lateral Movement** | `lateral-movement` tag | Network flow analysis |
| **C2 Communication** | `c2` tag | Domain/IP matching |
| **Insider Threat** | `insider-threat` tag | Behavioral analysis |

**Audit Evidence**:
- ICS monitoring tool configuration screenshots
- CIP-015 detection logs
- Quarterly report of detections inside ESP

---

