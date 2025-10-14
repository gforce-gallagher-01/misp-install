# MISP Installation Suite - Development Roadmap

**Version:** 6.0 and Beyond
**Last Updated:** 2025-10-14

This document outlines the long-term vision and detailed implementation plans for future versions of the MISP installation suite. For current active priorities, see [TODO.md](../TODO.md). For completed features, see [CHANGELOG.md](CHANGELOG.md).

---

## Table of Contents

- [Version Planning](#version-planning)
- [v5.6 Features (Q1 2026)](#v56-features-q1-2026)
  - [Splunk Cloud Integration](#splunk-cloud-integration)
  - [Security Onion Integration](#security-onion-integration)
  - [Azure Key Vault Integration](#azure-key-vault-integration)
- [v5.7 Features (Q2 2026)](#v57-features-q2-2026)
  - [Email Notifications](#email-notifications)
  - [Slack/Teams Webhooks](#slackteams-webhooks)
- [v6.0 Features (Q3 2026)](#v60-features-q3-2026)
  - [GUI Post-Installation Setup](#gui-post-installation-setup)
  - [Let's Encrypt Certificates](#lets-encrypt-certificates)
- [v7.0+ Vision (2027+)](#v70-vision-2027)
  - [Multi-Cloud Support](#multi-cloud-support)
  - [Advanced Monitoring](#advanced-monitoring)

---

## Version Planning

### v5.6 (Next - Q1 2026)
**Theme:** Enterprise Integrations
- Splunk Cloud integration
- Security Onion integration
- Azure Key Vault secrets management

### v5.7 (Q2 2026)
**Theme:** Operational Notifications
- Email notifications
- Slack/Teams webhooks

### v6.0 (Q3 2026)
**Theme:** User Experience & Security
- GUI post-install integration
- Enhanced monitoring
- Let's Encrypt support

### v7.0 (2027+)
**Theme:** Multi-Cloud & Scale
- AWS/GCP deployment support
- Kubernetes/container orchestration
- Enterprise-scale features

---

## v5.6 Features (Q1 2026)

### Splunk Cloud Integration

**Status:** Planned
**Priority:** High
**Estimated Effort:** 20-30 hours
**Target Completion:** Q1 2026

#### Overview

Integrate MISP with Splunk Cloud for real-time threat intelligence sharing and automated response. Provides bidirectional integration using Splunk Cloud-compatible methods including HEC (HTTP Event Collector), certified apps, and Universal Forwarder.

#### Benefits

- Real-time IOC ingestion into Splunk Cloud
- Automated event enrichment with MISP threat data
- SOAR workflow automation for incident response
- CIM-compliant data format for ES correlation
- Leverage existing MISP JSON logs from v5.4 installation
- Bidirectional threat intelligence sharing

#### Integration Methods

**Method 1: MISP App for SOAR Cloud (Certified)**
- App ID: 5820 (Splunk LLC official app)
- Cloud Compatible: ✅ Yes
- SOAR Cloud Supported: ✅ Yes
- Latest Version: 2.2.7 (August 2025)
- Actions: Test connectivity, create event, update event, run query, get attributes
- Requires: Splunk SOAR Cloud subscription

**Method 2: HTTP Event Collector (HEC) + Custom Scripts**
- Direct MISP API → Splunk HEC integration
- Works with Splunk Cloud Platform (no SOAR required)
- Python script pulls MISP data and pushes via HEC
- Scheduled collection (cron/systemd)
- Full control over data transformation

**Method 3: Universal Forwarder for MISP Logs**
- Forward existing `/opt/misp/logs/*.log` to Splunk Cloud
- JSON logs with CIM field names (already implemented in v5.4)
- Real-time log forwarding
- Sourcetypes: misp:json, misp:install, misp:backup, misp:update

**Method 4: MISP42 or Benni0 App (Requires Vetting)**
- Request private app installation via Splunk support
- Full-featured MISP integration
- Custom commands: mispgetioc, mispcollect, mispsearch, mispsight
- Alert actions for creating/updating MISP events

#### Implementation Phases

**Phase 1: Universal Forwarder Setup (4-6 hours)**
1. Install Splunk Universal Forwarder on MISP server
2. Configure inputs.conf to monitor /opt/misp/logs/
3. Configure props.conf for JSON parsing
4. Set up forwarding to Splunk Cloud
5. Create `misp` index in Splunk Cloud
6. Verify log ingestion and field extraction

**Phase 2: HEC Integration (8-10 hours)**
1. Create HEC token in Splunk Cloud
2. Develop Python script for MISP → HEC:
   - Query MISP API for events/attributes
   - Transform to CIM format
   - Push to Splunk HEC endpoint
3. Implement error handling and retry logic
4. Schedule script execution (every 15 min for high severity, hourly for all)
5. Create monitoring dashboard for integration health

**Phase 3: Splunk App Configuration (4-6 hours)**
1. Evaluate SOAR Cloud vs custom integration
2. If SOAR: Install MISP App (5820) from Splunkbase
3. If Platform: Request MISP42/Benni0 vetting or use HEC
4. Configure MISP instance connection (URL + API key)
5. Test connectivity and data flow

**Phase 4: Threat Intelligence Framework (4-6 hours)**
1. Create lookup tables for IOC enrichment
2. Configure saved searches for scheduled IOC pulls
3. Set up ES threat intelligence collections (if using ES)
4. Create correlation searches for MISP-enriched events
5. Configure alert actions for automated MISP event creation

**Phase 5: Dashboards and Reports (4-6 hours)**
1. Create MISP Threat Intelligence dashboard
2. Build IOC tracking and trending reports
3. Set up automated threat briefing reports
4. Create executive summary dashboard

#### Deliverables

**Scripts:**
- `scripts/splunk-hec-forwarder.py` - HEC integration script
- `scripts/splunk-misp-sync.py` - Bidirectional sync service

**Configuration Files:**
- `config/splunk-forwarder-inputs.conf` - UF inputs configuration
- `config/splunk-forwarder-props.conf` - UF props configuration
- `config/splunk-hec.yaml` - HEC configuration template

**Documentation:**
- `docs/integrations/SPLUNK_CLOUD.md` - Complete integration guide
- `docs/integrations/SPLUNK_DASHBOARDS.md` - Dashboard XML examples

#### Configuration Examples

**Universal Forwarder inputs.conf:**
```ini
[monitor:///opt/misp/logs/*.log]
disabled = false
index = misp
sourcetype = misp:json
recursive = true

[monitor:///opt/misp/logs/misp-install-*.log]
disabled = false
index = misp
sourcetype = misp:install
```

**HEC Python Script (splunk-hec-forwarder.py):**
```python
import requests
import json
from datetime import datetime, timedelta

MISP_URL = "https://misp-test.lan"
MISP_KEY = "${MISP_API_KEY}"
HEC_URL = "https://inputs.splunkcloud.com:8088/services/collector"
HEC_TOKEN = "${SPLUNK_HEC_TOKEN}"

def get_misp_events(hours=1):
    headers = {"Authorization": MISP_KEY}
    params = {"last": f"{hours}h", "published": 1}
    r = requests.get(f"{MISP_URL}/events/restSearch",
                     headers=headers, params=params, verify=False)
    return r.json()

def send_to_splunk(event):
    headers = {"Authorization": f"Splunk {HEC_TOKEN}"}
    payload = {
        "sourcetype": "misp:event",
        "source": "misp_api",
        "event": event
    }
    requests.post(HEC_URL, json=payload, headers=headers)
```

**Splunk Search Examples:**
```spl
# Search for IOCs in your data
index=network sourcetype=firewall
| lookup misp_ioc_lookup value AS dest_ip OUTPUT misp_event_id threat_level
| where isnotnull(misp_event_id)

# Pull recent high-severity events
| mispgetioc misp_instance=prod last=24h threat_level=high

# Enrich with MISP data
index=proxy
| mispsearch field=url
| where misp_found=1
```

#### Testing Requirements

- Test HEC token creation and data ingestion
- Verify JSON log forwarding from UF
- Test MISP API connectivity from script
- Validate CIM field mappings
- Performance test with large IOC sets
- Test alert actions (if using MISP42)
- Verify ES threat intel framework integration (if applicable)

#### Performance Considerations

- HEC batch size: 1000 events per request
- Collection interval: 15 min (high severity), 1 hour (all events)
- Universal Forwarder: Monitor /opt/misp/logs/ in real-time
- Lookup table size: Monitor and prune old IOCs (90-day retention)
- Index sizing: Estimate 10-50 MB/day for typical MISP usage

#### Security Considerations

- Store HEC token in Splunk secrets management
- Use MISP API key with read-only permissions for pulls
- Implement TLS verification for production
- Audit log all MISP → Splunk data transfers
- RBAC for MISP dashboards in Splunk

#### Related Projects

- [Splunk MISP App](https://splunkbase.splunk.com/app/5820)
- [MISP42Splunk](https://splunkbase.splunk.com/app/4335)
- [Benni0 App for MISP](https://splunkbase.splunk.com/app/7536)
- [TA-misp_es](https://github.com/splunk/TA-misp_es)
- [Splunk HEC Documentation](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)

---

### Security Onion Integration

**Status:** Planned
**Priority:** High
**Estimated Effort:** 15-20 hours
**Target Completion:** Q1 2026

#### Overview

Integrate MISP with Security Onion for bidirectional threat intelligence sharing. Security Onion is a free and open platform for threat hunting, enterprise security monitoring, and log management.

#### Benefits

- Automatic IOC (Indicators of Compromise) synchronization
- Enhanced threat detection capabilities
- Unified threat intelligence across security stack
- Real-time alert enrichment with MISP data
- Automated threat hunting workflows
- Integration with Suricata, Zeek, and Elasticsearch

#### Integration Points

1. **MISP → Security Onion**: Push IOCs to SO for detection rules
2. **Security Onion → MISP**: Import detected threats back to MISP
3. **Suricata Rule Generation**: Auto-generate Suricata rules from MISP events
4. **Elasticsearch Integration**: Index MISP data in SO's Elasticsearch
5. **TheHive Integration**: Optional case management workflow

#### Implementation Tasks

1. Add Security Onion configuration options to installer
2. Configure MISP API endpoints for SO access
3. Set up MISP feeds for SO consumption
4. Configure Suricata rule import/export
5. Implement event synchronization service
6. Add SO API authentication (API keys or certificates)
7. Create automated IOC push script
8. Configure Elasticsearch indexing for MISP data
9. Add health monitoring for SO connection
10. Create documentation for SO operators

#### Deliverables

**Scripts:**
- `scripts/so-sync.py` - Bidirectional sync service
- `scripts/so-push-iocs.py` - Push IOCs to Security Onion
- `scripts/so-import-detections.py` - Import detections from SO

**Configuration Files:**
- `config/security-onion.yaml` - SO configuration template

**Documentation:**
- `docs/integrations/SECURITY_ONION.md` - Integration guide

**Installer Updates:**
- `misp-install.py` - Add SO integration option during install

#### Configuration Example

```yaml
# config/security-onion.yaml
security_onion:
  enabled: true
  api_url: "https://securityonion.local/api"
  api_key: "${SO_API_KEY}"
  sync_interval: 300  # seconds
  push_to_suricata: true
  push_to_elasticsearch: true
  import_detections: true
  detection_threshold: "medium"  # low, medium, high, critical
  ioc_types:
    - ip-src
    - ip-dst
    - domain
    - hostname
    - url
    - md5
    - sha1
    - sha256
```

#### Testing Requirements

- Test with Security Onion 2.4+ (latest stable)
- Verify Suricata rule generation
- Test bidirectional sync
- Validate Elasticsearch indexing
- Test alert enrichment workflow
- Performance testing with large IOC sets

#### Documentation Needed

- Security Onion setup prerequisites
- MISP API configuration for SO
- Suricata rule customization guide
- Troubleshooting common integration issues
- Performance tuning recommendations

#### Related Projects

- [Security Onion](https://securityonionsolutions.com/)
- [MISP-Security-Onion-Sync](https://github.com/cudeso/misp-security-onion-sync)
- [TheHive](https://thehive-project.org/)

---

### Azure Key Vault Integration

**Status:** Planned
**Priority:** High
**Estimated Effort:** 10-15 hours
**Target Completion:** Q1 2026

#### Overview

Implement Azure Key Vault integration for secure secrets management in Azure environments, eliminating the need for PASSWORDS.txt file on disk.

#### Benefits

- No secrets stored on VM disk
- Centralized secret management
- Audit logging for secret access
- Automatic rotation support
- RBAC integration with Azure AD
- Industry standard for Azure production workloads

#### Implementation Tasks

1. Add Azure SDK dependencies (azure-identity, azure-keyvault-secrets)
2. Create secrets management abstraction layer
3. Add Key Vault configuration options:
   - `--use-keyvault` flag
   - `AZURE_KEYVAULT_URL` environment variable
   - Key Vault URL in config files
4. Implement Managed Identity authentication (DefaultAzureCredential)
5. Create secret retrieval functions:
   - `get_admin_password()` from Key Vault
   - `get_db_password()` from Key Vault
   - `get_gpg_passphrase()` from Key Vault
6. Modify Phase 6 (Configuration) to use Key Vault secrets
7. Add fallback to local PASSWORDS.txt for non-Azure deployments
8. Update backup script to handle Key Vault mode
9. Create Key Vault setup documentation
10. Add Key Vault testing mode

#### Deliverables

**Core Files Modified:**
- `misp-install.py` (Phases 6, 9)
- `scripts/backup-misp.py` - Handle Key Vault mode
- `scripts/misp-restore.py` - Handle Key Vault mode

**Configuration Files:**
- `config/azure-keyvault.yaml` - YAML configuration example
- `config/azure-keyvault.json` - JSON configuration example

**Documentation:**
- `docs/integrations/AZURE_KEYVAULT.md` - Complete setup guide

#### Configuration Examples

**YAML Configuration:**
```yaml
# config/azure-keyvault.yaml
secrets_backend: keyvault
azure:
  keyvault_url: "https://misp-secrets-kv.vault.azure.net/"
  use_managed_identity: true
```

**JSON Configuration:**
```json
{
  "secrets_backend": "keyvault",
  "azure": {
    "keyvault_url": "https://misp-secrets-kv.vault.azure.net/",
    "use_managed_identity": true
  }
}
```

#### Testing Requirements

- Test with Managed Identity
- Test with Service Principal
- Test fallback to local file
- Test secret rotation
- Test backup/restore with Key Vault

#### Cost Estimate

**Azure Key Vault Pricing:**
- Standard tier: $0.03 per 10,000 operations
- Typical MISP usage: ~100 secret retrievals/day
- Monthly cost: **~$0.03/month** (negligible)

#### Documentation Needed

- Azure Key Vault setup guide
- Managed Identity configuration
- Secret naming conventions
- Migration guide from PASSWORDS.txt to Key Vault
- Troubleshooting guide

---

## v5.7 Features (Q2 2026)

### Email Notifications

**Status:** Planned
**Priority:** Medium
**Estimated Effort:** 8-10 hours
**Target Completion:** Q2 2026

#### Overview

Add email notification support for installation, backup, update, and error events.

#### Features

- Installation completion emails
- Backup completion/failure notifications
- Update completion/failure notifications
- Critical error alerts

#### Implementation

**Method 1: Python smtplib (Simple)**
- Use built-in Python smtplib
- Configuration via `--email-notify` flag or config file
- SMTP settings in PASSWORDS.txt or Key Vault

**Method 2: Third-Party Service (Recommended)**
- SendGrid API integration
- AWS SES integration
- More reliable delivery
- Better tracking and analytics

#### Configuration Example

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_user: "misp-alerts@company.com"
    smtp_password: "${EMAIL_PASSWORD}"
    from_address: "misp-alerts@company.com"
    to_addresses:
      - "soc-team@company.com"
      - "admin@company.com"
    events:
      - installation_complete
      - backup_success
      - backup_failure
      - update_complete
      - update_failure
      - critical_error
```

---

### Slack/Teams Webhooks

**Status:** Planned
**Priority:** Medium
**Estimated Effort:** 6-8 hours
**Target Completion:** Q2 2026

#### Overview

Add webhook support for real-time notifications to Slack and Microsoft Teams.

#### Features

- Installation status webhooks
- Backup notifications
- Update notifications
- Critical error alerts

#### Implementation

**Slack Integration:**
- Incoming webhook URLs
- Rich formatted messages (Slack Blocks)
- Color-coded alerts (green=success, red=failure)

**Teams Integration:**
- Incoming webhook URLs
- Adaptive Cards formatting
- Actionable notifications

#### Configuration Example

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    channel: "#misp-alerts"
    events:
      - installation_complete
      - backup_failure
      - critical_error

  teams:
    enabled: true
    webhook_url: "https://company.webhook.office.com/YOUR/WEBHOOK/URL"
    events:
      - installation_complete
      - backup_success
      - update_complete
```

#### Retry Logic

- Exponential backoff for failed webhook calls
- Maximum 3 retry attempts
- Log all webhook delivery attempts

---

## v6.0 Features (Q3 2026)

### GUI Post-Installation Setup

**Status:** Planned
**Priority:** Medium
**Estimated Effort:** 32-44 hours
**Target Completion:** Q3 2026

#### Overview

Integrate the `misp-setup-complete.py` script into the GUI installer, adding post-installation configuration screens that allow users to configure MISP settings, feeds, and features through the graphical interface.

#### New GUI Screens

**Screen 7: Post-Installation Setup**
- Checkbox: "Run post-installation setup automatically"
- Checkbox: "Enable NERC CIP compliance mode"
- Multi-select: Configuration steps to run
  - [ ] Apply MISP best practice settings
  - [ ] Add threat intelligence feeds
  - [ ] Populate security news
  - [ ] Enable taxonomies & warning lists
  - [ ] Verify setup
- Button: "Configure Now" or "Skip"

**Screen 8: Feed Selection**
- If NERC CIP mode enabled:
  - Pre-selected: ICS/OT security feeds
  - Display: CISA ICS Advisories, SecurityWeek ICS/OT, IndustrialCyber
  - Info banner: "Feeds selected for utilities/energy sector"
- If standard mode:
  - Multi-select: Common threat intelligence feeds
  - Search box: Filter available feeds
  - Categories: Malware, Phishing, IPs, Domains, etc.
- Preview: Feed details (provider, update frequency, format)
- Validation: At least 1 feed selected

**Screen 9: News & Taxonomies**
- Checkbox: "Populate security news from RSS feeds"
  - Input: Days to look back (default: 30)
  - Input: Maximum items (default: 20)
  - Display: News sources (auto-filtered for NERC CIP mode)
- Checkbox: "Update taxonomies and warning lists"
  - Display: Estimated time (5-10 minutes)
- Progress bar: Real-time progress during update

**Screen 10: Setup Summary & Execution**
- Summary of selected configuration
- Estimated time: X minutes
- Button: "Apply Configuration"
- Progress display: Real-time feedback
- Error handling: Show errors inline, allow continue/retry

#### Implementation Tasks

**GUI Components (16-20 hours):**
1. Modify Installation Progress Screen
2. Create Post-Install Setup Screens (4 new screens)
3. Create Setup Widgets (feed selector, progress, NERC CIP banner)
4. Integrate `misp-setup-complete.py` into GUI
5. Update Completion Screen

**Backend Integration (8-12 hours):**
1. API key auto-detection in GUI
2. Real-time progress tracking
3. Error handling and retry logic
4. State persistence for GUI setup

**Testing (8-12 hours):**
1. Test all GUI workflows
2. Test NERC CIP mode vs standard mode
3. Test error scenarios
4. Test with different feed selections
5. Performance testing with large setups

#### Deliverables

**New Files:**
- `gui/screens/post_setup.py`
- `gui/screens/feed_selection.py`
- `gui/screens/news_taxonomies.py`
- `gui/screens/setup_execution.py`
- `gui/widgets/feed_selector.py`
- `gui/widgets/setup_progress.py`
- `gui/widgets/nerc_cip_banner.py`

**Modified Files:**
- `misp_install_gui.py` - Add new screen routing
- `gui/screens/progress.py` - Add post-install phase
- `gui/screens/completion.py` - Show setup summary

**Documentation:**
- `docs/GUI_POST_INSTALL.md` - Post-install setup guide

---

### Let's Encrypt Certificates

**Status:** Planned
**Priority:** Low
**Estimated Effort:** 12-16 hours
**Target Completion:** v6.1

#### Overview

Replace self-signed certificates with Let's Encrypt (automated) or commercial CA certificates for production deployments.

#### Features

**Let's Encrypt Integration:**
- Automatic certificate acquisition
- Automatic renewal (90-day cycle)
- DNS-01 or HTTP-01 challenge support
- Certbot integration

**Commercial Certificate Support:**
- Manual certificate upload
- Certificate validation
- Expiration warnings
- Renewal reminders

#### Implementation Tasks

1. Add `ssl_mode` configuration option (self-signed, letsencrypt, commercial)
2. Install certbot during Phase 1 (Dependencies)
3. Add Phase 7.5: Let's Encrypt Certificate Acquisition
4. Configure certbot renewal cron job
5. Update docker-compose.yml for certificate mounts
6. Add certificate monitoring and alerting
7. Create migration guide from self-signed to Let's Encrypt

#### Configuration Example

```yaml
ssl:
  mode: letsencrypt  # self-signed, letsencrypt, commercial
  email: admin@company.com  # For Let's Encrypt
  auto_renew: true
  # For commercial certificates:
  cert_path: /path/to/cert.pem
  key_path: /path/to/key.pem
  chain_path: /path/to/chain.pem
```

#### Deliverables

- `docs/integrations/SSL_CERTIFICATES.md` - SSL certificate guide
- `docs/integrations/LETSENCRYPT.md` - Let's Encrypt setup guide
- `scripts/renew-certificates.py` - Certificate renewal script

---

## v7.0+ Vision (2027+)

### Multi-Cloud Support

**Status:** Concept
**Priority:** Low
**Target Version:** v7.0+

#### Overview

Extend beyond Azure to support AWS and GCP deployments with cloud-native features.

#### AWS Features

- EC2 instance deployment
- AWS Secrets Manager integration
- S3 backup storage
- CloudWatch integration
- AWS Systems Manager integration

#### GCP Features

- Compute Engine deployment
- Secret Manager integration
- Cloud Storage backup
- Cloud Monitoring integration
- Cloud Logging integration

#### Implementation Estimate

**Effort:** 80-120 hours
**Timeline:** 6-9 months

---

### Advanced Monitoring

**Status:** Concept
**Priority:** Medium
**Target Version:** v7.0+

#### Features

- Prometheus metrics export
- Grafana dashboard templates
- Performance monitoring
- Feed health tracking
- API usage analytics
- Container resource monitoring

#### Deliverables

- `scripts/prometheus-exporter.py` - Metrics exporter
- `config/grafana-dashboards/` - Dashboard templates
- `docs/MONITORING.md` - Monitoring guide

---

## Contributing to the Roadmap

Have ideas for future features? We welcome community input!

1. Check this roadmap for planned features
2. Check [GitHub Issues](https://github.com/your-org/misp-install/issues)
3. Open a new issue with tag `enhancement`
4. Describe:
   - Problem/use case
   - Proposed solution
   - Estimated effort (if known)
   - Willingness to contribute code

---

**Last Updated:** 2025-10-14
**Maintainer:** tKQB Enterprises
