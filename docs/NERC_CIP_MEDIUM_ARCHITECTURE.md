# MISP for NERC CIP Medium Impact - Architecture & Implementation Guide

**Version:** 2.0
**Date:** October 24, 2025
**Industry:** Electric Utilities
**Compliance:** NERC CIP Medium Impact BES Cyber Systems
**Status:** ARCHITECTURAL DESIGN

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Section 1: Core Security Architecture](#section-1-core-security-architecture)
4. [Section 2: Access Control & Authentication (CIP-004/CIP-005)](#section-2-access-control--authentication-cip-004cip-005)
5. [Section 3: Electronic Security Perimeter Monitoring (CIP-005)](#section-3-electronic-security-perimeter-monitoring-cip-005)
6. [Section 4: Internal Network Security Monitoring (CIP-015)](#section-4-internal-network-security-monitoring-cip-015)
7. [Section 5: Vulnerability Assessment & Patch Management (CIP-010)](#section-5-vulnerability-assessment--patch-management-cip-010)
8. [Section 6: Supply Chain Risk Management (CIP-013)](#section-6-supply-chain-risk-management-cip-013)
9. [Section 7: Incident Response & Forensics (CIP-008)](#section-7-incident-response--forensics-cip-008)
10. [Section 8: Security Event Logging (CIP-007)](#section-8-security-event-logging-cip-007)
11. [Section 9: Information Protection (CIP-011)](#section-9-information-protection-cip-011)
12. [Section 10: Security Awareness Training (CIP-003)](#section-10-security-awareness-training-cip-003)
13. [Section 11: Audit & Compliance Reporting](#section-11-audit--compliance-reporting)
14. [Section 12: SIEM Integration Architecture](#section-12-siem-integration-architecture)
15. [Implementation Roadmap](#implementation-roadmap)
16. [Gap Analysis & Recommendations](#gap-analysis--recommendations)

---

## Executive Summary

This document provides a comprehensive architectural breakdown for implementing MISP (Malware Information Sharing Platform) to support **NERC CIP Medium Impact** BES Cyber System requirements.

### Key Differences: Low vs Medium Impact

| Aspect | Low Impact | Medium Impact (This Guide) |
|--------|------------|----------------------------|
| **Scope** | Aggregate 15 MW or more | Between Low and High thresholds |
| **Access Control** | Basic policies | Role-based access control (RBAC) |
| **Monitoring** | Basic logging | Enhanced monitoring + CIP-015 |
| **Vulnerability Assessment** | 15-month intervals | 15-month intervals + active monitoring |
| **Incident Response** | Basic plan | Comprehensive plan + forensics |
| **Supply Chain** | Vendor notifications | Formal SCRM program with tracking |
| **Data Retention** | 90 days (logs) | 90 days (logs) + 3 years (evidence) |
| **Audit Evidence** | Basic documentation | Comprehensive evidence generation |

### Implementation Status

✅ **IMPLEMENTED:**
- Core MISP installation framework
- Basic threat intelligence feeds
- ICS/SCADA threat intelligence
- Basic NERC CIP configuration
- Security news feeds
- Automated maintenance

⚠️ **PARTIAL:**
- RBAC configuration
- Audit evidence generation
- SIEM integration (documentation only)
- CIP-015 monitoring integration

❌ **NOT IMPLEMENTED:**
- Automated compliance reporting
- Supply chain risk tracking system
- Incident response workflow automation
- Vulnerability assessment tracking
- ESP monitoring integration
- Forensics evidence collection
- Training material generation
- Data retention policy enforcement

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NERC CIP Medium Impact                        │
│                   MISP Architecture (v2.0)                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│  Electronic Security     │  │  Internal Networks       │
│  Perimeter (ESP)         │  │  (CIP-015 Monitoring)    │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │ • Firewalls        │──┼──┼──│ • Dragos Platform  │  │
│  │ • IDS/IPS          │  │  │  │ • Nozomi Networks  │  │
│  │ • EAP Monitoring   │  │  │  │ • Claroty/Forescout│  │
│  └────────────────────┘  │  │  └────────────────────┘  │
└────────────┬─────────────┘  └────────────┬─────────────┘
             │                              │
             │  IOCs, Rules, Indicators     │
             └──────────────┬───────────────┘
                            │
                     ┌──────▼──────────┐
                     │   MISP CORE     │
                     │   (v5.6+)       │
                     │                 │
                     │ ┌─────────────┐ │
                     │ │ Threat Intel│ │
                     │ │   Engine    │ │
                     │ └─────────────┘ │
                     │ ┌─────────────┐ │
                     │ │ Compliance  │ │
                     │ │   Module    │ │
                     │ └─────────────┘ │
                     │ ┌─────────────┐ │
                     │ │ Audit &     │ │
                     │ │ Reporting   │ │
                     │ └─────────────┘ │
                     └─────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
   ┌──────▼──────┐   ┌──────▼──────┐   ┌─────▼──────┐
   │ Vulnerability│   │  Supply     │   │  Incident  │
   │  Assessment │   │  Chain      │   │  Response  │
   │  Tracking   │   │  Risk Mgmt  │   │  Workflow  │
   └─────────────┘   └─────────────┘   └────────────┘
          │                 │                 │
   ┌──────▼──────┐   ┌──────▼──────┐   ┌─────▼──────┐
   │  Splunk /   │   │  E-ISAC     │   │  Security  │
   │  SIEM       │   │  Integration│   │  Awareness │
   │  Integration│   │             │   │  Training  │
   └─────────────┘   └─────────────┘   └────────────┘
```

### Component Mapping to NERC CIP Standards

| Component | CIP Standards | Purpose |
|-----------|---------------|---------|
| **Threat Intel Engine** | CIP-013, CIP-015 | IOC collection and distribution |
| **Compliance Module** | CIP-003, CIP-010 | Policy enforcement and tracking |
| **Audit & Reporting** | ALL CIP | Evidence generation for audits |
| **Vulnerability Tracking** | CIP-010 R3 | 15-month assessment cycle |
| **Supply Chain Risk Mgmt** | CIP-013 | Vendor risk tracking |
| **Incident Response** | CIP-008 | E-ISAC reporting within 1 hour |
| **ESP Monitoring** | CIP-005 | Electronic Access Point protection |
| **Internal Monitoring** | CIP-015 | Malicious communication detection |
| **RBAC** | CIP-004 | Personnel access management |
| **Security Awareness** | CIP-003 R2 | Training material generation |

---

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

## Section 5: Vulnerability Assessment & Patch Management (CIP-010)

### 5.1 Vulnerability Tracking System

**Requirement**: CIP-010 R3 - Vulnerability assessments at least every 15 months

**Current Status**: ❌ NOT IMPLEMENTED

**Implementation Plan:**

**File**: `scripts/vulnerability-assessment-tracker.py`

```python
"""
CIP-010 R3 Vulnerability Assessment Tracking
Tracks 15-month assessment cycle per BES Cyber System
"""

class VulnerabilityAssessmentTracker:
    """
    Tracks vulnerability assessments for NERC CIP Medium compliance
    """

    BES_ASSET_TYPES = [
        'energy_management_system',  # EMS
        'scada_server',
        'historian',
        'hmi_workstation',
        'engineering_workstation',
        'firewall_eap',
        'relay_protection',
        'rtu_controller',
        'solar_inverter',
        'battery_management_system',
        'wind_turbine_controller'
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def create_vulnerability_assessment_event(self,
                                               asset_type: str,
                                               asset_id: str,
                                               findings: List[Dict]) -> str:
        """
        Create MISP event for vulnerability assessment

        Args:
            asset_type: Type of BES Cyber System
            asset_id: Unique identifier
            findings: List of vulnerabilities found

        Returns: MISP event ID
        """
        pass

    def track_patch_status(self, cve_id: str, asset_id: str, status: str):
        """
        Track patch deployment status for CIP-010 R2

        Status: identified, testing, deployed, mitigated, accepted_risk
        """
        pass

    def generate_15_month_assessment_schedule(self) -> List[Dict]:
        """
        Generate schedule ensuring all BES Cyber Systems assessed
        every 15 months
        """
        pass

    def check_overdue_assessments(self) -> List[str]:
        """
        Alert on BES Cyber Systems with overdue vulnerability assessments
        """
        pass

    def generate_cip_010_compliance_report(self) -> str:
        """
        Generate CIP-010 R3 compliance evidence:
        - Last assessment date per asset
        - Vulnerabilities identified
        - Remediation status
        - Risk acceptance documentation
        """
        pass

def import_vulnerability_scan_results(scanner: str, scan_file: str):
    """
    Import vulnerability scan results into MISP

    Supported Scanners:
    - Tenable.sc (Nessus)
    - Qualys VMDR
    - Rapid7 InsightVM
    - OpenVAS
    """
    pass
```

**Integration with Vulnerability Scanners:**

```python
# Tenable.sc Integration
TENABLE_CONFIG = {
    'api_url': 'https://tenable.example.com',
    'access_key': 'xxx',
    'secret_key': 'yyy',
    'scan_policy': 'NERC_CIP_ICS_Scan',
    'scan_schedule': 'monthly'  # More frequent than 15-month requirement
}

# Filter ICS-relevant vulnerabilities
ICS_CVE_FILTERS = [
    'Siemens',
    'Schneider Electric',
    'ABB',
    'GE Digital',
    'Rockwell Automation',
    'Modbus',
    'DNP3',
    'IEC 61850'
]
```

**Audit Evidence**:
- Vulnerability assessment schedule
- Assessment reports per asset
- Patch deployment status
- Risk acceptance documentation

---

### 5.2 Patch Management Workflow

**Requirement**: CIP-010 R2 - Patch or mitigate within 35 days

**Implementation Plan:**

**File**: `scripts/patch-management-workflow.py`

```python
"""
CIP-010 R2 Patch Management Workflow
Tracks 35-day remediation timeline
"""

PATCH_STATUSES = {
    'identified': 'Vulnerability identified from MISP feed',
    'assessed': 'Impact assessment completed',
    'testing': 'Patch testing in progress',
    'scheduled': 'Deployment scheduled',
    'deployed': 'Patch deployed to production',
    'mitigated': 'Compensating control implemented',
    'accepted_risk': 'Risk accepted by management'
}

def create_patch_tracking_event(cve_id: str, affected_assets: List[str]):
    """
    Create MISP event to track patch deployment
    Automatically calculates 35-day deadline
    """
    pass

def send_patch_deadline_alerts():
    """
    Send alerts for patches approaching 35-day deadline
    Alert at: Day 20, Day 30, Day 35 (violation)
    """
    pass

def generate_cip_010_r2_report():
    """
    Evidence for auditors:
    - All patches identified in last 15 months
    - Deployment status
    - Average time to patch
    - Violations (patches >35 days)
    - Risk acceptance documentation
    """
    pass
```

**Audit Evidence**: Patch management reports, risk acceptance forms

---

## Section 6: Supply Chain Risk Management (CIP-013)

### 6.1 Vendor Notification Tracking

**Requirement**: CIP-013 R1.2.5 - Notifications from vendors about cyber security risks

**Current Status**: ⚠️ PARTIAL (Can manually add vendor notifications, no tracking system)

**Implementation Plan:**

**File**: `scripts/supply-chain-risk-tracker.py`

```python
"""
CIP-013 Supply Chain Risk Management
Tracks vendor security notifications and remediation
"""

class SupplyChainRiskTracker:
    """
    Tracks vendor cyber security notifications for CIP-013 compliance
    """

    NERC_CIP_VENDORS = [
        # EMS/SCADA Vendors
        {'name': 'GE Digital', 'product': 'EMS', 'security_contact': 'security@ge.com'},
        {'name': 'Siemens Energy', 'product': 'SCADA', 'security_contact': 'productcert@siemens.com'},
        {'name': 'Schneider Electric', 'product': 'EcoStruxure', 'security_contact': 'cybersecurity@se.com'},
        {'name': 'ABB', 'product': 'Grid Automation', 'security_contact': 'cybersecurity@abb.com'},

        # Solar Inverter Vendors
        {'name': 'SMA', 'product': 'Solar Inverters', 'security_contact': 'security@sma.de'},
        {'name': 'SolarEdge', 'product': 'Inverters', 'security_contact': 'security@solaredge.com'},

        # Battery Storage Vendors
        {'name': 'Tesla', 'product': 'Megapack', 'security_contact': 'security@tesla.com'},
        {'name': 'Fluence', 'product': 'Energy Storage', 'security_contact': 'security@fluenceenergy.com'},

        # Wind Turbine Vendors
        {'name': 'Vestas', 'product': 'Wind Turbines', 'security_contact': 'cybersecurity@vestas.com'},
        {'name': 'GE Renewable Energy', 'product': 'Wind Turbines', 'security_contact': 'security@ge.com'}
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def create_vendor_notification_event(self,
                                          vendor_name: str,
                                          notification_date: str,
                                          vulnerability_details: Dict,
                                          affected_products: List[str]) -> str:
        """
        Create MISP event for vendor security notification

        Tags: cip-013, supply-chain, vendor-notification
        """
        pass

    def track_vendor_response_time(self, vendor_name: str) -> Dict:
        """
        Track how quickly vendors notify of vulnerabilities
        CIP-013 audit metric
        """
        pass

    def track_remediation_status(self, event_id: str, status: str):
        """
        Track remediation of vendor-reported vulnerabilities
        """
        pass

    def generate_cip_013_compliance_report(self) -> str:
        """
        Evidence for CIP-013 audits:
        - All vendor notifications received in last 3 years
        - Remediation status
        - Vendor response time metrics
        - Procurement decisions based on cyber security
        """
        pass

    def import_vendor_security_bulletin(self, vendor: str, bulletin_url: str):
        """
        Automatically import vendor security bulletins
        (e.g., Siemens ProductCERT, ICS-CERT)
        """
        pass

def assess_vendor_cyber_security_risk(vendor_name: str) -> Dict:
    """
    CIP-013 R1.2.1 - Assess vendor cyber security practices

    Criteria:
    - Vulnerability disclosure program
    - Response time to vulnerabilities
    - Secure development lifecycle
    - Incident notification procedures
    """
    pass
```

**Vendor Security Bulletin Sources:**

```python
VENDOR_SECURITY_FEEDS = {
    'siemens': 'https://cert-portal.siemens.com/productcert/xml/advisories.xml',
    'schneider': 'https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp',
    'ge': 'https://www.ge.com/digital/documentation/cyber-security-notifications',
    'abb': 'https://search.abb.com/library/Download.aspx?DocumentID=9AKK107680A9387',
    'rockwell': 'https://rockwellautomation.custhelp.com/app/answers/answer_view/a_id/1085012'
}
```

**Audit Evidence**:
- Vendor notification log
- Vendor risk assessments
- Procurement criteria documentation

---

## Section 7: Incident Response & Forensics (CIP-008)

### 7.1 Incident Response Workflow

**Requirement**: CIP-008 R1 - Incident response plan with testing every 36 months

**Current Status**: ⚠️ PARTIAL (Basic event templates exist, no workflow automation)

**Implementation Plan:**

**File**: `scripts/incident-response-workflow.py`

```python
"""
CIP-008 Incident Response Workflow Automation
Integrates MISP with E-ISAC reporting
"""

class CIPIncidentResponse:
    """
    Automates NERC CIP incident response workflow
    """

    REPORTABLE_INCIDENT_CRITERIA = [
        'compromised_bes_cyber_system',  # Reportable within 1 hour to E-ISAC
        'attempt_to_compromise',          # Reportable within 1 hour
        'data_exfiltration',
        'ransomware',
        'lateral_movement_detected',
        'ics_malware_detected'
    ]

    INCIDENT_PHASES = [
        'detection',      # CIP-015 detection or external notification
        'analysis',       # Threat analysis in MISP
        'containment',    # Isolate affected systems
        'eradication',    # Remove threat
        'recovery',       # Restore operations
        'lessons_learned' # Post-incident review
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def create_incident_event(self,
                               incident_type: str,
                               detection_time: str,
                               affected_assets: List[str],
                               iocs: List[Dict]) -> str:
        """
        Create MISP incident event
        Automatically determines if reportable to E-ISAC
        """
        pass

    def check_if_reportable(self, incident_event_id: str) -> bool:
        """
        Determine if incident meets CIP-008 reportable criteria
        """
        pass

    def generate_eisac_report(self, incident_event_id: str) -> Dict:
        """
        Generate report for E-ISAC submission
        CIP-008 requires reporting within 1 hour
        """
        pass

    def track_incident_timeline(self, incident_event_id: str):
        """
        Track incident response timeline for lessons learned

        Metrics:
        - Time to detection
        - Time to containment
        - Time to eradication
        - Time to recovery
        """
        pass

    def collect_forensic_evidence(self, incident_event_id: str, evidence_files: List[str]):
        """
        Attach forensic evidence to MISP event

        Evidence types:
        - Network packet captures
        - Memory dumps
        - Log files
        - Disk images
        """
        pass

    def generate_lessons_learned_report(self, incident_event_id: str) -> str:
        """
        Generate post-incident lessons learned report
        CIP-008 R1.4: Update incident response plan within 90 days
        """
        pass

    def schedule_incident_response_test(self):
        """
        Schedule CIP-008 R2 testing (every 36 months)
        Generates tabletop exercise scenarios from MISP threat intel
        """
        pass

def integrate_with_eisac(api_key: str, eisac_credentials: Dict):
    """
    Integration with E-ISAC portal
    Automates incident reporting
    """
    pass
```

**E-ISAC Integration:**

```python
EISAC_CONFIG = {
    'portal_url': 'https://eisac.com',
    'api_endpoint': '/api/v1/incidents',
    'organization_id': 'YOUR_EISAC_ORG_ID',
    'reporting_contact': 'security@yourcompany.com',
    'tlp_default': 'AMBER'  # Traffic Light Protocol
}

EISAC_INCIDENT_TYPES = [
    'cyber_attack',
    'unauthorized_access',
    'malware_infection',
    'data_breach',
    'denial_of_service',
    'supply_chain_compromise'
]
```

**Audit Evidence**:
- Incident response plan (with MISP integration documented)
- Testing documentation (every 36 months)
- E-ISAC incident reports
- Lessons learned reports

---

## Section 8: Security Event Logging (CIP-007)

### 8.1 MISP Integration with SIEM

**Requirement**: CIP-007 R4 - Security event logging (90-day retention minimum)

**Current Status**: ✅ IMPLEMENTED (MISP logs to `/opt/misp/logs/`)

**Enhancement Needed**: Automated log forwarding to SIEM

**Implementation Plan:**

**File**: `scripts/configure-siem-forwarding.py`

```python
"""
Configure MISP log forwarding to SIEM platforms
CIP-007 R4 compliance
"""

SIEM_PLATFORMS = {
    'splunk': {
        'method': 'hec',  # HTTP Event Collector
        'port': 8088,
        'index': 'nerc_cip',
        'sourcetype': 'misp:json'
    },
    'security_onion': {
        'method': 'syslog',
        'port': 514,
        'protocol': 'tcp'
    },
    'qradar': {
        'method': 'syslog',
        'port': 514
    },
    'sentinel': {
        'method': 'azure_monitor',
        'workspace_id': 'xxx',
        'shared_key': 'yyy'
    }
}

def configure_splunk_hec_forwarding(hec_token: str, splunk_url: str):
    """
    Configure MISP logs to forward to Splunk via HEC
    All 14 MISP log sources forwarded
    """
    pass

def configure_syslog_forwarding(siem_ip: str, port: int):
    """
    Configure syslog forwarding for Security Onion / QRadar
    """
    pass

def generate_cip_007_compliance_report():
    """
    Evidence for CIP-007 R4:
    - Log sources configured
    - 90-day retention verified
    - SIEM receiving logs
    - Log review procedures documented
    """
    pass
```

**SIEM Use Cases:**

| Use Case | MISP Log Source | SIEM Alert |
|----------|-----------------|------------|
| Failed login attempts | `misp:auth` | Alert after 5 failures |
| Privilege escalation | `misp:admin` | Alert on role changes |
| IOC export | `misp:api` | Monitor firewall integration |
| Event publication | `misp:event` | Track E-ISAC sharing |
| Configuration changes | `misp:admin` | Alert on taxonomy/setting changes |

**Audit Evidence**: SIEM configuration, log review documentation

---

## Section 9: Information Protection (CIP-011)

### 9.1 BCSI Protection in MISP

**Requirement**: CIP-011 R1 - Protect BES Cyber System Information (BCSI)

**MISP Contains BCSI:**
- Asset inventory (BES Cyber Systems)
- Vulnerability information
- Network architecture (indirectly via IOCs)
- Incident response procedures
- Vendor information

**Implementation Plan:**

**File**: `scripts/configure-bcsi-protection.py`

```python
"""
Configure BCSI Protection Controls in MISP
CIP-011 R1 compliance
"""

class BCSIProtection:
    """
    Implements CIP-011 BCSI protection requirements
    """

    BCSI_TAXONOMIES = [
        'cip-011:bcsi',                   # Mark events as BCSI
        'tlp:red',                        # Do not share externally
        'confidentiality:organization'     # Organization-only
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def configure_default_distribution(self):
        """
        Set default distribution to "Your organization only"
        CIP-011 requirement: no external sharing without controls
        """
        # MISP Setting: default_sharing_group = "Your Organization"
        pass

    def enable_encryption_at_rest(self):
        """
        Verify Docker volumes encrypted
        CIP-011 R1.1: Encryption for storage
        """
        pass

    def enable_encryption_in_transit(self):
        """
        Enforce TLS for all connections
        CIP-011 R1.2: Encryption for transit
        """
        # MISP Settings:
        # - HSTS enabled
        # - TLS 1.2+ only
        # - Certificate validation
        pass

    def configure_bcsi_watermarking(self):
        """
        Add watermark to exported reports
        Example: "BCSI - CIP-011 Protected Information"
        """
        pass

    def track_bcsi_access(self):
        """
        Log all access to BCSI-tagged events
        CIP-011 R1.3: Access logging
        """
        pass

    def generate_cip_011_compliance_report(self):
        """
        Evidence for CIP-011:
        - Encryption status (at rest, in transit)
        - Access control matrix
        - Default distribution settings
        - BCSI handling procedures
        """
        pass

def audit_bcsi_sharing(api_key: str):
    """
    Audit all events shared externally
    Ensure CIP-011 controls in place
    """
    pass
```

**CIP-011 Checklist:**
- [ ] Default distribution: "Your organization only"
- [ ] TLS 1.2+ enforced
- [ ] Docker volumes encrypted
- [ ] Access logging enabled
- [ ] Quarterly access reviews
- [ ] BCSI handling procedures documented
- [ ] User training on BCSI protection

**Audit Evidence**: BCSI protection procedures, access logs

---

## Section 10: Security Awareness Training (CIP-003)

### 10.1 Automated Training Material Generation

**Requirement**: CIP-003 R2 - Cyber security awareness training at least every 15 months

**Current Status**: ⚠️ PARTIAL (Security news feeds exist, no training material generation)

**Implementation Plan:**

**File**: `scripts/generate-training-materials.py`

```python
"""
Generate CIP-003 R2 Security Awareness Training Materials from MISP
Leverages threat intelligence and security news feeds
"""

class SecurityAwarenessTrainingGenerator:
    """
    Generates CIP-003 compliant training materials
    """

    TRAINING_TOPICS = [
        'ics_threat_landscape',      # ICS/SCADA threats
        'phishing_awareness',        # Top attack vector
        'password_security',         # CIP-004 requirement
        'incident_reporting',        # CIP-008 procedures
        'insider_threats',           # Behavioral indicators
        'supply_chain_risks',        # CIP-013 awareness
        'mobile_device_security',    # BYOD policies
        'physical_security',         # CIP-006 integration
        'email_security',            # Phishing/spearphishing
        'removable_media',           # USB attacks on ICS
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def generate_quarterly_threat_briefing(self, quarter: str) -> str:
        """
        Generate quarterly threat briefing from MISP intel

        Content:
        - Top threats this quarter (from MISP events)
        - Industry incidents (from security news feeds)
        - Lessons learned (from incident response)
        - Recommended actions for employees

        Output: PDF presentation slides
        """
        pass

    def generate_annual_training_course(self) -> Dict:
        """
        Generate annual CIP-003 R2 training course

        Format: PowerPoint with speaker notes
        Duration: 45 minutes
        Includes: Quiz questions for completion tracking
        """
        pass

    def generate_phishing_scenarios(self) -> List[Dict]:
        """
        Generate realistic phishing scenarios from MISP threat intel

        Uses real phishing campaigns from threat feeds
        Customizes for utility sector context
        """
        pass

    def track_training_completion(self, employee_email: str, training_date: str):
        """
        Track employee training completion
        CIP-003 R2: Training within 15 months
        """
        pass

    def alert_overdue_training(self) -> List[str]:
        """
        Alert on employees overdue for training (>15 months)
        """
        pass

    def generate_cip_003_compliance_report(self) -> str:
        """
        Evidence for CIP-003 R2:
        - Training materials delivered
        - Employee completion records
        - Threat intelligence used in training
        - 15-month compliance status
        """
        pass

def import_training_completion_records(hr_system: str, csv_file: str):
    """
    Import training completion records from HR/LMS system
    """
    pass
```

**Training Material Templates:**

```
docs/templates/
├── CIP-003-Annual-Training-Template.pptx
├── CIP-003-Quarterly-Threat-Briefing.pptx
├── Phishing-Awareness-Module.pptx
└── ICS-Threat-Landscape-Module.pptx
```

**Audit Evidence**:
- Training materials (dated)
- Employee completion records
- Quarterly threat briefings
- 15-month compliance tracking

---

## Section 11: Audit & Compliance Reporting

### 11.1 Automated Compliance Report Generation

**Current Status**: ❌ NOT IMPLEMENTED

**Implementation Plan:**

**File**: `scripts/generate-compliance-report.py`

```python
"""
Automated NERC CIP Compliance Report Generation
Generates audit-ready evidence from MISP
"""

class NERCCIPComplianceReporter:
    """
    Generates comprehensive compliance reports for NERC CIP audits
    """

    CIP_STANDARDS_COVERED = [
        'CIP-003-9',  # Security Management Controls
        'CIP-004-7',  # Personnel & Training
        'CIP-005-7',  # Electronic Security Perimeters
        'CIP-007-6',  # Systems Security Management
        'CIP-008-6',  # Incident Reporting
        'CIP-010-4',  # Configuration Change Management
        'CIP-011-3',  # Information Protection
        'CIP-013-2',  # Supply Chain Risk Management
        'CIP-015-1',  # Internal Network Security Monitoring
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.misp_url = get_misp_url()

    def generate_master_compliance_report(self, date_range: str) -> str:
        """
        Generate master compliance report covering all CIP standards

        Output: PDF report suitable for audit submission
        """
        pass

    def generate_cip_003_report(self) -> Dict:
        """CIP-003: Security awareness training evidence"""
        return {
            'training_materials': self.get_training_materials(),
            'completion_records': self.get_training_completion(),
            'overdue_personnel': self.check_overdue_training()
        }

    def generate_cip_004_report(self) -> Dict:
        """CIP-004: Personnel risk assessment evidence"""
        return {
            'personnel_with_access': self.get_all_misp_users(),
            'role_assignments': self.get_role_matrix(),
            'access_reviews': self.get_quarterly_access_reviews(),
            'revocation_logs': self.get_access_revocations()
        }

    def generate_cip_005_report(self) -> Dict:
        """CIP-005: Electronic Security Perimeter evidence"""
        return {
            'eap_configurations': self.get_firewall_configs(),
            'iocs_blocked': self.get_ioc_blocking_stats(),
            'perimeter_alerts': self.get_eap_security_events(),
            'eap_monitoring_logs': self.get_eap_monitoring_evidence()
        }

    def generate_cip_007_report(self) -> Dict:
        """CIP-007: Systems Security Management evidence"""
        return {
            'logging_configuration': self.get_siem_config(),
            'log_retention_status': self.verify_90_day_retention(),
            'patch_status': self.get_patch_compliance()
        }

    def generate_cip_008_report(self) -> Dict:
        """CIP-008: Incident Response evidence"""
        return {
            'incident_response_plan': self.get_ir_plan_with_misp(),
            'testing_documentation': self.get_ir_test_records(),
            'eisac_reports': self.get_eisac_submissions(),
            'lessons_learned': self.get_lessons_learned_reports()
        }

    def generate_cip_010_report(self) -> Dict:
        """CIP-010: Vulnerability Assessment evidence"""
        return {
            'assessment_schedule': self.get_15_month_schedule(),
            'completed_assessments': self.get_vulnerability_assessments(),
            'patch_tracking': self.get_35_day_patch_compliance(),
            'risk_acceptances': self.get_risk_acceptance_documentation()
        }

    def generate_cip_011_report(self) -> Dict:
        """CIP-011: Information Protection evidence"""
        return {
            'bcsi_identification': self.get_bcsi_taxonomy_usage(),
            'encryption_status': self.verify_encryption(),
            'access_controls': self.get_rbac_configuration(),
            'bcsi_handling_procedures': self.get_bcsi_procedures()
        }

    def generate_cip_013_report(self) -> Dict:
        """CIP-013: Supply Chain Risk Management evidence"""
        return {
            'vendor_notifications': self.get_vendor_security_bulletins(),
            'vendor_risk_assessments': self.get_vendor_assessments(),
            'procurement_criteria': self.get_cyber_security_procurement_docs(),
            'remediation_tracking': self.get_vendor_vuln_remediation()
        }

    def generate_cip_015_report(self) -> Dict:
        """CIP-015: Internal Network Security Monitoring evidence"""
        return {
            'monitoring_tools_configured': self.get_ics_monitoring_config(),
            'detections_inside_esp': self.get_cip_015_alerts(),
            'response_actions': self.get_detection_response_logs(),
            'false_positive_tuning': self.get_tuning_documentation()
        }

    def export_audit_evidence_package(self, output_dir: str):
        """
        Export complete audit evidence package

        Contents:
        - Master compliance report (PDF)
        - Supporting evidence per CIP standard
        - Configuration screenshots
        - Log excerpts
        - Procedure documentation
        """
        pass

def schedule_quarterly_compliance_reports():
    """
    Schedule automated quarterly compliance reports
    Runs on first day of quarter
    """
    pass
```

**Report Templates:**

```
docs/compliance_reports/
├── NERC_CIP_Master_Report_Template.docx
├── CIP-003_Security_Awareness_Evidence.xlsx
├── CIP-004_Personnel_Access_Matrix.xlsx
├── CIP-005_EAP_Configuration_Evidence.docx
├── CIP-010_Vulnerability_Assessment_Report.xlsx
└── CIP-013_Supply_Chain_Risk_Report.xlsx
```

**Audit Evidence**: Comprehensive compliance reports, quarterly evidence packages

---

## Section 12: SIEM Integration Architecture

### 12.1 Splunk Integration

**Current Status**: ✅ DOCUMENTATION ONLY (`docs/THIRD-PARTY-INTEGRATIONS.md`)

**Implementation Needed**: Automated configuration

**File**: `scripts/configure-splunk-integration.py`

```python
"""
Configure Splunk SIEM Integration for NERC CIP Medium
Includes correlation rules and dashboards
"""

SPLUNK_NERC_CIP_INDEX = 'nerc_cip'

SPLUNK_CORRELATION_RULES = {
    'cip_005_eap_breach_attempt': {
        'search': '''
            index=nerc_cip sourcetype=misp:ioc action=blocked
            | stats count by src_ip, dest_ip, dest_port
            | where count > 10
        ''',
        'description': 'CIP-005: Multiple blocked connection attempts at EAP',
        'severity': 'high',
        'cip_standard': 'CIP-005 R2'
    },

    'cip_015_ics_malware_detected': {
        'search': '''
            index=nerc_cip sourcetype=dragos:alert OR sourcetype=nozomi:alert
            signature="ICS Malware"
            | table _time, src_ip, dest_ip, malware_family, affected_asset
        ''',
        'description': 'CIP-015: ICS malware detected inside ESP',
        'severity': 'critical',
        'cip_standard': 'CIP-015 R1'
    },

    'cip_007_failed_authentication': {
        'search': '''
            index=nerc_cip sourcetype=misp:auth action=failed
            | stats count by user, src_ip
            | where count > 5
        ''',
        'description': 'CIP-007: Multiple failed authentication attempts',
        'severity': 'medium',
        'cip_standard': 'CIP-007 R5'
    },

    'cip_011_unauthorized_data_access': {
        'search': '''
            index=nerc_cip sourcetype=misp:event tag="cip-011:bcsi"
            user NOT IN (authorized_users)
            | table _time, user, event_id, action
        ''',
        'description': 'CIP-011: Unauthorized access to BCSI',
        'severity': 'high',
        'cip_standard': 'CIP-011 R1'
    }
}

def deploy_splunk_correlation_rules(splunk_api_key: str, splunk_url: str):
    """
    Deploy NERC CIP correlation rules to Splunk
    """
    pass

def create_splunk_nerc_cip_dashboard():
    """
    Create Splunk dashboard for NERC CIP compliance monitoring

    Panels:
    - CIP-005 EAP monitoring stats
    - CIP-015 internal detections
    - CIP-007 authentication failures
    - CIP-010 patch compliance status
    - CIP-008 incident timeline
    """
    pass
```

**Splunk Dashboard Panels:**

1. **CIP-005 Electronic Security Perimeter**
   - IOCs blocked at EAPs (last 24 hours)
   - Top blocked IPs/domains
   - EAP alert trend

2. **CIP-015 Internal Network Monitoring**
   - Detections inside ESP (last 7 days)
   - Detection type breakdown
   - Mean time to detection

3. **CIP-007 Systems Security**
   - Failed authentication attempts
   - Patch compliance percentage
   - Systems needing patches

4. **CIP-008 Incident Response**
   - Active incidents
   - Incident response timeline
   - E-ISAC reports submitted

5. **CIP-010 Vulnerability Assessment**
   - Vulnerability assessment schedule
   - Overdue assessments
   - 35-day patch compliance

**Audit Evidence**: Splunk dashboard screenshots, correlation rule documentation

---

### 12.2 Security Onion Integration

**Implementation Plan:**

**File**: `scripts/configure-security-onion-integration.py`

```python
"""
Configure Security Onion Integration for NERC CIP Medium
Bidirectional IOC sharing
"""

SECURITY_ONION_CONFIG = {
    'api_url': 'https://securityonion.example.com',
    'api_key': 'xxx',
    'integration_mode': 'bidirectional',  # MISP <-> Security Onion
    'ioc_sync_interval': 3600  # 1 hour
}

def export_iocs_to_security_onion():
    """
    Export MISP IOCs to Security Onion for detection
    """
    pass

def import_alerts_from_security_onion():
    """
    Import Security Onion alerts into MISP as events
    Creates CIP-015 incidents for analysis
    """
    pass
```

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-2)

**Priority: HIGH**

- [ ] Implement MFA (Section 2.1.1)
- [ ] Configure NERC CIP roles (Section 2.1.2)
- [ ] Configure BCSI protection (Section 9)
- [ ] Enable SIEM log forwarding (Section 8.1)

**Scripts to Create:**
- `scripts/configure-rbac-mfa.py`
- `scripts/configure-nerc-cip-roles.py`
- `scripts/configure-bcsi-protection.py`
- `scripts/configure-siem-forwarding.py`

**Deliverables:**
- MFA enabled for all admin/analyst accounts
- Role-based access control configured
- BCSI taxonomies implemented
- Logs forwarding to SIEM

---

### Phase 2: Threat Intelligence & Monitoring (Months 2-3)

**Priority: HIGH**

- [ ] IOC export for EAP firewalls (Section 3.1)
- [ ] CIP-015 ICS monitoring integration (Section 4)
- [ ] EAP log ingestion (Section 3.2)

**Scripts to Create:**
- `scripts/export-iocs-for-firewall.py`
- `scripts/configure-cip-015-monitoring.py`
- `scripts/ingest-eap-logs.py`

**Deliverables:**
- Automated IOC distribution to EAP firewalls
- Integration with Dragos/Nozomi/Claroty
- EAP alerts flowing into MISP

---

### Phase 3: Vulnerability & Patch Management (Months 3-4)

**Priority: MEDIUM**

- [ ] Vulnerability assessment tracker (Section 5.1)
- [ ] Patch management workflow (Section 5.2)
- [ ] 15-month assessment scheduler

**Scripts to Create:**
- `scripts/vulnerability-assessment-tracker.py`
- `scripts/patch-management-workflow.py`
- `scripts/import-vulnerability-scans.py`

**Deliverables:**
- 15-month vulnerability assessment schedule
- 35-day patch tracking system
- Integration with Tenable/Qualys

---

### Phase 4: Supply Chain & Incident Response (Months 4-5)

**Priority: MEDIUM**

- [ ] Supply chain risk tracker (Section 6)
- [ ] Incident response workflow (Section 7)
- [ ] E-ISAC integration

**Scripts to Create:**
- `scripts/supply-chain-risk-tracker.py`
- `scripts/incident-response-workflow.py`
- `scripts/integrate-with-eisac.py`

**Deliverables:**
- Vendor notification tracking
- Automated E-ISAC reporting
- Forensic evidence collection

---

### Phase 5: Compliance & Training (Months 5-6)

**Priority: LOW**

- [ ] Training material generator (Section 10)
- [ ] Personnel access tracker (Section 2.1)
- [ ] Compliance report generator (Section 11)

**Scripts to Create:**
- `scripts/generate-training-materials.py`
- `scripts/track-personnel-access.py`
- `scripts/generate-compliance-report.py`

**Deliverables:**
- Automated CIP-003 training materials
- Quarterly compliance reports
- Audit evidence packages

---

### Phase 6: SIEM Integration (Month 6)

**Priority: LOW (if SIEM already exists)**

- [ ] Splunk correlation rules (Section 12.1)
- [ ] Security Onion integration (Section 12.2)
- [ ] Compliance dashboards

**Scripts to Create:**
- `scripts/configure-splunk-integration.py`
- `scripts/configure-security-onion-integration.py`
- `scripts/create-compliance-dashboards.py`

**Deliverables:**
- Splunk NERC CIP dashboard
- Automated correlation rules
- Security Onion bidirectional sync

---

## Gap Analysis & Recommendations

### Current Implementation Gaps

#### Critical Gaps (Immediate Action Required)

| Gap | CIP Standard | Impact | Recommended Action |
|-----|--------------|--------|-------------------|
| **No MFA** | CIP-004 R4 | HIGH | Implement TOTP/YubiKey MFA (Phase 1) |
| **No CIP-015 integration** | CIP-015 R1 | HIGH | Integrate with ICS monitoring tools (Phase 2) |
| **No vulnerability tracking** | CIP-010 R3 | MEDIUM | Build 15-month assessment tracker (Phase 3) |
| **No incident workflow** | CIP-008 R1 | MEDIUM | Automate E-ISAC reporting (Phase 4) |

#### High Priority Gaps

| Gap | CIP Standard | Impact | Recommended Action |
|-----|--------------|--------|-------------------|
| **No IOC automation** | CIP-005 R2 | MEDIUM | Automate firewall IOC export (Phase 2) |
| **No supply chain tracking** | CIP-013 | MEDIUM | Build vendor notification tracker (Phase 4) |
| **Manual compliance reporting** | ALL | LOW | Automate quarterly reports (Phase 5) |
| **No SIEM correlation rules** | CIP-007 R4 | LOW | Deploy Splunk rules (Phase 6) |

#### Low Priority Gaps (Nice to Have)

| Gap | CIP Standard | Impact | Recommended Action |
|-----|--------------|--------|-------------------|
| **Manual training materials** | CIP-003 R2 | LOW | Automate training generation (Phase 5) |
| **No Security Onion integration** | CIP-015 R1 | LOW | Bidirectional IOC sync (Phase 6) |
| **No forensics workflow** | CIP-008 R1 | LOW | Evidence collection automation (Phase 4) |

---

### Recommendations for NERC CIP Medium Organizations

#### Immediate (0-3 Months)

1. **Enable Multi-Factor Authentication** (CIP-004)
   - Implement TOTP for all admin accounts
   - Grace period: 30 days for enrollment

2. **Configure Role-Based Access Control** (CIP-004)
   - Map organizational roles to MISP permissions
   - Document access matrix for audits

3. **Integrate with Electronic Security Perimeter** (CIP-005)
   - Export IOCs to EAP firewalls
   - Automate hourly updates

4. **Enable SIEM Log Forwarding** (CIP-007)
   - Forward all MISP logs to SIEM
   - Verify 90-day retention

#### Short-Term (3-6 Months)

5. **Implement CIP-015 Monitoring Integration**
   - Connect with Dragos/Nozomi/Claroty
   - Automate IOC distribution

6. **Build Vulnerability Assessment Tracking** (CIP-010)
   - Schedule 15-month assessments
   - Track 35-day patch compliance

7. **Create Supply Chain Risk Tracker** (CIP-013)
   - Track vendor security bulletins
   - Document remediation actions

8. **Automate Incident Response Workflow** (CIP-008)
   - Integrate with E-ISAC
   - Implement 1-hour reporting

#### Long-Term (6-12 Months)

9. **Deploy SIEM Correlation Rules**
   - Create Splunk/Security Onion dashboards
   - Automate threat detection

10. **Generate Automated Compliance Reports**
    - Quarterly evidence packages
    - Audit-ready documentation

11. **Implement Training Material Generation** (CIP-003)
    - Quarterly threat briefings
    - Annual training courses

12. **Optimize & Mature**
    - Fine-tune false positives
    - Continuous improvement

---

## Appendix A: Configuration File Examples

### A.1 NERC CIP Medium Configuration Template

**File**: `config/nerc-cip-medium-config.json`

```json
{
  "server_ip": "192.168.20.54",
  "domain": "misp.utility.com",
  "admin_email": "cybersecurity@utility.com",
  "admin_org": "Example Electric Utility",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "encryption_key": "auto-generated",
  "environment": "production",

  "nerc_cip_config": {
    "impact_level": "medium",
    "bes_asset_count": 15,
    "enable_mfa": true,
    "enable_rbac": true,
    "enable_eisac_integration": true,
    "enable_cip_015_monitoring": true,
    "siem_platform": "splunk",
    "vulnerability_scanner": "tenable",
    "ics_monitoring_platform": "dragos"
  },

  "exclude_features": []
}
```

### A.2 Phase Installation Template

**File**: `config/nerc-cip-phased-config.json`

```json
{
  "server_ip": "192.168.20.54",
  "domain": "misp.utility.com",
  "admin_email": "cybersecurity@utility.com",
  "admin_org": "Example Electric Utility",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "environment": "production",

  "implementation_phase": 1,

  "exclude_features": [
    "utilities-dashboards",
    "automated-backups"
  ]
}
```

---

## Appendix B: Script Inventory

### Scripts to Create for NERC CIP Medium

**Security & Access Control:**
- `scripts/configure-rbac-mfa.py` - Multi-factor authentication setup
- `scripts/configure-nerc-cip-roles.py` - Role-based access control
- `scripts/track-personnel-access.py` - Personnel access tracking (CIP-004)
- `scripts/automated-access-revocation.py` - 24-hour access revocation (CIP-004)

**Monitoring & Detection:**
- `scripts/export-iocs-for-firewall.py` - EAP firewall IOC export (CIP-005)
- `scripts/ingest-eap-logs.py` - EAP log ingestion (CIP-005)
- `scripts/configure-cip-015-monitoring.py` - ICS monitoring integration (CIP-015)
- `scripts/configure-siem-forwarding.py` - SIEM log forwarding (CIP-007)

**Vulnerability Management:**
- `scripts/vulnerability-assessment-tracker.py` - 15-month assessment tracking (CIP-010)
- `scripts/patch-management-workflow.py` - 35-day patch tracking (CIP-010)
- `scripts/import-vulnerability-scans.py` - Tenable/Qualys integration

**Supply Chain & Incidents:**
- `scripts/supply-chain-risk-tracker.py` - Vendor notification tracking (CIP-013)
- `scripts/incident-response-workflow.py` - Incident response automation (CIP-008)
- `scripts/integrate-with-eisac.py` - E-ISAC reporting automation

**Compliance & Reporting:**
- `scripts/configure-bcsi-protection.py` - BCSI protection controls (CIP-011)
- `scripts/generate-training-materials.py` - Training material generation (CIP-003)
- `scripts/generate-compliance-report.py` - Automated compliance reports
- `scripts/configure-splunk-integration.py` - Splunk correlation rules
- `scripts/configure-security-onion-integration.py` - Security Onion integration

**Total New Scripts**: 19

---

## Appendix C: Audit Evidence Checklist

### Comprehensive Audit Evidence by CIP Standard

**CIP-003 (Security Management Controls):**
- [ ] Security awareness training materials
- [ ] Training completion records (15-month compliance)
- [ ] Quarterly threat briefings
- [ ] MISP usage in training documentation

**CIP-004 (Personnel & Training):**
- [ ] Role assignment matrix
- [ ] Personnel access list (quarterly)
- [ ] Risk assessment records
- [ ] Access revocation logs (24-hour compliance)
- [ ] MFA enrollment records

**CIP-005 (Electronic Security Perimeters):**
- [ ] EAP firewall configuration screenshots
- [ ] IOC blocking statistics
- [ ] EAP monitoring logs
- [ ] Blocked connection attempts log

**CIP-007 (Systems Security Management):**
- [ ] SIEM configuration documentation
- [ ] 90-day log retention verification
- [ ] Patch deployment status
- [ ] Security event monitoring logs

**CIP-008 (Incident Reporting):**
- [ ] Incident response plan (with MISP integration)
- [ ] 36-month testing documentation
- [ ] E-ISAC incident reports
- [ ] Lessons learned reports

**CIP-010 (Configuration Change Management):**
- [ ] 15-month vulnerability assessment schedule
- [ ] Completed vulnerability assessments
- [ ] 35-day patch compliance tracking
- [ ] Risk acceptance documentation

**CIP-011 (Information Protection):**
- [ ] BCSI identification (taxonomies)
- [ ] Encryption verification (at rest, in transit)
- [ ] Access control configuration
- [ ] BCSI handling procedures

**CIP-013 (Supply Chain Risk Management):**
- [ ] Vendor security notification log
- [ ] Vendor risk assessments
- [ ] Cyber security procurement criteria
- [ ] Vendor vulnerability remediation tracking

**CIP-015 (Internal Network Security Monitoring):**
- [ ] ICS monitoring tool configuration
- [ ] Detection logs inside ESP
- [ ] Response action documentation
- [ ] False positive tuning records

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-14 | Initial | Based on existing NERC_CIP_CONFIGURATION.md |
| 2.0 | 2025-10-24 | Revision | Complete architectural breakdown with 12 sections |

**Review Schedule:** Quarterly (January, April, July, October)

**Next Review Date:** January 2026

**Document Owner:** Cyber Security Team

**Approvers:**
- NERC CIP Compliance Officer
- Chief Information Security Officer (CISO)
- Director of Operations

---

**END OF DOCUMENT**
