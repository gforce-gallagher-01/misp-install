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
