# MISP Installation Tool - TODO List

## High Priority

### MISP Complete Setup Script with NERC CIP Mode
**Status:** ✅ **COMPLETED** (v5.5 - 2025-10-14)
**Priority:** High (production deployment automation)
**Target Version:** v5.5

**Description:**
Post-installation orchestration script that applies all recommended MISP settings, adds threat intelligence feeds, populates security news, and configures MISP for production use. Special `--nerc-cip-ready` mode for utilities/energy sector compliance with NERC CIP standards.

**Features Implemented:**
- ✅ Orchestrates all post-installation configuration scripts
- ✅ Step 1: Apply MISP best practice settings (via configure-misp-nerc-cip.py)
- ✅ Step 2: Add threat intelligence feeds (standard or NERC CIP focused)
- ✅ Step 3: Populate security news from RSS feeds
- ✅ Step 4: Enable taxonomies and warning lists
- ✅ Step 5: Check MISP modules status
- ✅ Step 6: Verify complete setup
- ✅ `--nerc-cip-ready` flag for utilities sector compliance
- ✅ `--dry-run` mode for preview
- ✅ Skip flags for individual steps (--skip-feeds, --skip-news, --skip-settings)
- ✅ Auto-detect API key from multiple sources
- ✅ Comprehensive error handling and logging
- ✅ Statistics tracking and summary report

**NERC CIP Mode Features:**
When `--nerc-cip-ready` is specified:
- ICS/OT specific threat intelligence feeds (E-ISAC, ICS-CERT)
- Utilities sector taxonomies and tags
- Critical infrastructure security news filtering
- Enhanced audit logging (CIP-007-R2 compliance)
- Security awareness content (CIP-003-R2 compliance)
- Event correlation for OT/ICS threats

**Files Created:**
- ✅ `scripts/misp-setup-complete.py` - Complete setup orchestrator (800+ lines)

**Usage Examples:**
```bash
# Standard production setup
python3 scripts/misp-setup-complete.py --api-key YOUR_KEY

# NERC CIP compliance setup
python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --nerc-cip-ready

# Dry-run mode (preview)
python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --dry-run

# Skip specific steps
python3 scripts/misp-setup-complete.py --api-key YOUR_KEY --skip-news

# Auto-detect API key
python3 scripts/misp-setup-complete.py
```

**Best Practices Applied:**
- ✅ Type hints for all function parameters and returns
- ✅ Comprehensive docstrings (Google style)
- ✅ Centralized logging with structured fields
- ✅ Error handling with graceful degradation
- ✅ Subprocess management with timeouts
- ✅ Exit code conventions (0=success, 1=failure)
- ✅ Colored terminal output for readability
- ✅ Statistics tracking for reporting
- ✅ Dry-run mode for safe testing
- ✅ API key auto-detection (environment, .env, PASSWORDS.txt)

**Integration with Existing Scripts:**
- Calls `configure-misp-nerc-cip.py` for settings
- Calls `add-nerc-cip-news-feeds-api.py` for feeds
- Calls `populate-misp-news.py` for news content
- Uses `misp_api.py` helper module
- Uses `misp_logger.py` for logging

---

### API Key Generation During Installation
**Status:** ✅ **COMPLETED** (v5.5 - 2025-10-14)
**Priority:** Critical (required for all API-based scripts)
**Target Version:** v5.5

**Description:**
Automatically generate and store MISP API key during initial installation for use by automation scripts. All scripts should use MISP REST API instead of direct database manipulation for better reliability, error handling, and compatibility.

**Benefits:**
- No direct database access required (cleaner, more maintainable)
- Better error handling via API responses
- Version-independent (API is more stable than DB schema)
- Supports RBAC and audit logging
- Industry best practice for automation

**Implementation Tasks:**
1. **Phase 1: Add PyMISP to System Dependencies**
   - Install PyMISP during Phase 1 (Dependencies)
   - Add to system packages: `pip3 install pymisp --break-system-packages`
   - Also install feedparser for RSS/Atom parsing
   - Log package installation

2. **Phase 11.5: API Key Generation** ✅ **COMPLETED** (2025-10-14)
   - ✅ Wait for MISP initialization to complete
   - ✅ Use MISP CLI (`cake user change_authkey`) to generate API key
   - ✅ Store API key in `/opt/misp/PASSWORDS.txt`
   - ✅ Store API key in `/opt/misp/.env` as `MISP_API_KEY`
   - ✅ Set proper permissions (600)
   - ✅ Log API key generation
   - ✅ Graceful error handling (continues if API key generation fails)

3. **Convert Existing Scripts to API:**
   - ✅ `populate-misp-news-api.py` - Already API-based (v2.0) - LIMITED (API endpoint broken)
   - ✅ `add-nerc-cip-news-feeds-api.py` - **COMPLETED** (v2.0 - 2025-10-14)
   - ✅ `check-misp-feeds-api.py` - **COMPLETED** (v2.0 - 2025-10-14)
   - ✅ `list-misp-communities.py` - No changes needed (informational only)
   - ✅ `configure-misp-nerc-cip.py` - No conversion needed (already uses cake commands)
   - ⏳ `backup-misp.py` - Keep DB dumps (required for full backup)
   - ⏳ `misp-restore.py` - Keep DB restore (required for full restore)

3. **Script Pattern (Standard API Usage):**
   ```python
   import requests

   # Read API key from environment
   MISP_URL = os.getenv('MISP_URL', 'https://misp-test.lan')
   MISP_API_KEY = os.getenv('MISP_API_KEY') or get_api_key_from_passwords()

   headers = {
       'Authorization': MISP_API_KEY,
       'Accept': 'application/json',
       'Content-Type': 'application/json'
   }

   # Use requests for all MISP operations
   response = requests.post(
       f"{MISP_URL}/feeds/add",
       headers=headers,
       json=feed_data,
       verify=False  # Self-signed cert
   )
   ```

4. **API Key Helper Module:** ✅ **COMPLETED** (2025-10-14)
   - ✅ Created `misp_api.py` - Centralized API helper
   - ✅ Functions: `get_api_key()`, `get_misp_url()`, `get_misp_client()`, `test_connection()`
   - ✅ Auto-detects API key from .env, PASSWORDS.txt, or environment variable
   - ✅ SSL verification disabled for self-signed certs
   - ✅ Test mode (`python3 misp_api.py`) for verification

5. **Documentation Updates:** ✅ **COMPLETED** (2025-10-14)
   - ✅ Created comprehensive API usage guide (docs/API_USAGE.md)
   - ✅ Documented API key retrieval methods (auto, web, CLI)
   - ✅ Added helper module usage examples
   - ✅ Added troubleshooting for common API issues
   - ✅ Documented all common API endpoints
   - ✅ Included error handling patterns and best practices

**Files Created/Modified:**
- ✅ `misp-install.py` - Added Phase 11.5 for API key generation
- ✅ `misp_api.py` - **COMPLETED**: Centralized API helper module
- ✅ `scripts/populate-misp-news-api.py` - Already created (v2.0) - LIMITED (API endpoint broken)
- ✅ `scripts/add-nerc-cip-news-feeds-api.py` - **COMPLETED** (v2.0 - 2025-10-14)
- ✅ `scripts/check-misp-feeds-api.py` - **COMPLETED** (v2.0 - 2025-10-14)
- ✅ `scripts/configure-misp-nerc-cip.py` - No API version needed (uses cake commands)
- ✅ `/opt/misp/PASSWORDS.txt` - Automatically updated with MISP_API_KEY section
- ✅ `/opt/misp/.env` - Automatically updated with MISP_API_KEY variable
- ✅ `docs/API_USAGE.md` - **COMPLETED**: Comprehensive API usage guide (52KB, 1000+ lines)

**Testing Requirements:**
- Test API key generation during fresh install
- Test all scripts with API key from environment
- Test all scripts with API key from PASSWORDS.txt
- Test error handling when API key is invalid
- Test error handling when MISP is not reachable

**Priority Order for Conversion:**
1. ✅ `populate-misp-news-api.py` - DONE (LIMITED - API endpoint returns HTTP 500)
2. ✅ `add-nerc-cip-news-feeds-api.py` - **COMPLETED** (v2.0 - 2025-10-14)
3. ✅ `check-misp-feeds-api.py` - **COMPLETED** (v2.0 - 2025-10-14)
4. ✅ `configure-misp-nerc-cip.py` - No conversion needed (uses proper cake commands)
5. ⏳ `backup-misp.py` - Keep DB dumps (required for full backup)

**Status:** ✅ **100% COMPLETE** - All tasks finished!

**Summary:**
- ✅ API key auto-generation during installation (Phase 11.5)
- ✅ Centralized API helper module (misp_api.py) with comprehensive functions
- ✅ 2 new API scripts created and tested (add-nerc-cip-news-feeds-api.py, check-misp-feeds-api.py)
- ✅ Both scripts use `/feeds/add`, `/feeds/index`, `/feeds/enable`, `/feeds/disable` endpoints
- ✅ Database versions remain available as fallback
- ✅ Comprehensive API usage documentation (docs/API_USAGE.md - 1000+ lines)
- ℹ️  News API still broken upstream (HTTP 500 on /news/add) - using DB version as workaround

---

### Splunk Cloud Integration
**Status:** Planned
**Priority:** High (real-time threat intelligence for Splunk SIEM)

**Description:**
Integrate MISP with Splunk Cloud for real-time threat intelligence sharing and automated response. Provides bidirectional integration using Splunk Cloud-compatible methods including HEC (HTTP Event Collector), certified apps, and Universal Forwarder.

**Benefits:**
- Real-time IOC ingestion into Splunk Cloud
- Automated event enrichment with MISP threat data
- SOAR workflow automation for incident response
- CIM-compliant data format for ES correlation
- Leverage existing MISP JSON logs from v5.4 installation
- Bidirectional threat intelligence sharing

**Integration Methods:**

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

**Implementation Tasks:**

**Phase 1: Universal Forwarder Setup**
1. Install Splunk Universal Forwarder on MISP server
2. Configure inputs.conf to monitor /opt/misp/logs/
3. Configure props.conf for JSON parsing
4. Set up forwarding to Splunk Cloud
5. Create `misp` index in Splunk Cloud
6. Verify log ingestion and field extraction

**Phase 2: HEC Integration**
7. Create HEC token in Splunk Cloud
8. Develop Python script for MISP → HEC:
   - Query MISP API for events/attributes
   - Transform to CIM format
   - Push to Splunk HEC endpoint
9. Implement error handling and retry logic
10. Schedule script execution (every 15 min for high severity, hourly for all)
11. Create monitoring dashboard for integration health

**Phase 3: Splunk App Configuration**
12. Evaluate SOAR Cloud vs custom integration
13. If SOAR: Install MISP App (5820) from Splunkbase
14. If Platform: Request MISP42/Benni0 vetting or use HEC
15. Configure MISP instance connection (URL + API key)
16. Test connectivity and data flow

**Phase 4: Threat Intelligence Framework**
17. Create lookup tables for IOC enrichment
18. Configure saved searches for scheduled IOC pulls
19. Set up ES threat intelligence collections (if using ES)
20. Create correlation searches for MISP-enriched events
21. Configure alert actions for automated MISP event creation

**Phase 5: Dashboards and Reports**
22. Create MISP Threat Intelligence dashboard
23. Build IOC tracking and trending reports
24. Set up automated threat briefing reports
25. Create executive summary dashboard

**Files to Create:**
- `scripts/splunk-hec-forwarder.py` - HEC integration script
- `scripts/splunk-misp-sync.py` - Bidirectional sync service
- `config/splunk-forwarder-inputs.conf` - UF inputs configuration
- `config/splunk-forwarder-props.conf` - UF props configuration
- `config/splunk-hec.yaml` - HEC configuration template
- `docs/SPLUNK_CLOUD_INTEGRATION.md` - Complete integration guide
- `docs/SPLUNK_DASHBOARDS.md` - Dashboard XML examples

**Configuration Examples:**

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

**Testing Requirements:**
- Test HEC token creation and data ingestion
- Verify JSON log forwarding from UF
- Test MISP API connectivity from script
- Validate CIM field mappings
- Performance test with large IOC sets
- Test alert actions (if using MISP42)
- Verify ES threat intel framework integration (if applicable)

**Performance Considerations:**
- HEC batch size: 1000 events per request
- Collection interval: 15 min (high severity), 1 hour (all events)
- Universal Forwarder: Monitor /opt/misp/logs/ in real-time
- Lookup table size: Monitor and prune old IOCs (90-day retention)
- Index sizing: Estimate 10-50 MB/day for typical MISP usage

**Documentation Needed:**
- HEC token creation guide
- Universal Forwarder installation steps
- Python script deployment and scheduling
- Splunk Cloud app vetting process
- Saved search configuration
- Dashboard deployment
- Troubleshooting guide
- Performance tuning recommendations

**Security Considerations:**
- Store HEC token in Splunk secrets management
- Use MISP API key with read-only permissions for pulls
- Implement TLS verification for production
- Audit log all MISP → Splunk data transfers
- RBAC for MISP dashboards in Splunk

**Related Projects:**
- [Splunk MISP App](https://splunkbase.splunk.com/app/5820)
- [MISP42Splunk](https://splunkbase.splunk.com/app/4335)
- [Benni0 App for MISP](https://splunkbase.splunk.com/app/7536)
- [TA-misp_es](https://github.com/splunk/TA-misp_es)
- [Splunk HEC Documentation](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)

---

### Security Onion (SO) Integration
**Status:** Planned
**Priority:** High (threat intelligence sharing with SIEM/IDS platform)

**Description:**
Integrate MISP with Security Onion for bidirectional threat intelligence sharing. Security Onion is a free and open platform for threat hunting, enterprise security monitoring, and log management.

**Benefits:**
- Automatic IOC (Indicators of Compromise) synchronization
- Enhanced threat detection capabilities
- Unified threat intelligence across security stack
- Real-time alert enrichment with MISP data
- Automated threat hunting workflows
- Integration with Suricata, Zeek, and Elasticsearch

**Integration Points:**
1. **MISP → Security Onion**: Push IOCs to SO for detection rules
2. **Security Onion → MISP**: Import detected threats back to MISP
3. **Suricata Rule Generation**: Auto-generate Suricata rules from MISP events
4. **Elasticsearch Integration**: Index MISP data in SO's Elasticsearch
5. **TheHive Integration**: Optional case management workflow

**Implementation Tasks:**
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

**Files to Create/Modify:**
- `scripts/so-sync.py` - Bidirectional sync service
- `scripts/so-push-iocs.py` - Push IOCs to Security Onion
- `scripts/so-import-detections.py` - Import detections from SO
- `config/security-onion.yaml` - SO configuration template
- `docs/SECURITY_ONION_INTEGRATION.md` - Integration guide
- `misp-install.py` - Add SO integration option during install

**Configuration Examples:**
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

**Testing Requirements:**
- Test with Security Onion 2.4+ (latest stable)
- Verify Suricata rule generation
- Test bidirectional sync
- Validate Elasticsearch indexing
- Test alert enrichment workflow
- Performance testing with large IOC sets

**Documentation Needed:**
- Security Onion setup prerequisites
- MISP API configuration for SO
- Suricata rule customization guide
- Troubleshooting common integration issues
- Performance tuning recommendations

**Related Projects:**
- [Security Onion](https://securityonionsolutions.com/)
- [MISP-Security-Onion-Sync](https://github.com/cudeso/misp-security-onion-sync)
- [TheHive](https://thehive-project.org/)

---

### Azure Key Vault Integration
**Status:** Planned
**Priority:** High (for production Azure deployments)

**Description:**
Implement Azure Key Vault integration for secure secrets management in Azure environments, eliminating the need for PASSWORDS.txt file on disk.

**Benefits:**
- No secrets stored on VM disk
- Centralized secret management
- Audit logging for secret access
- Automatic rotation support
- RBAC integration with Azure AD
- Industry standard for Azure production workloads

**Implementation Tasks:**
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

**Files to Modify:**
- `misp-install.py` (Phases 6, 9)
- `config/` - Add Key Vault configuration examples
- `scripts/backup-misp.py` - Handle Key Vault mode
- `scripts/misp-restore.py` - Handle Key Vault mode
- `docs/AZURE_KEYVAULT.md` - New documentation

**Configuration Examples:**
```yaml
# config/azure-keyvault.yaml
secrets_backend: keyvault
azure:
  keyvault_url: "https://misp-secrets-kv.vault.azure.net/"
  use_managed_identity: true
```

```json
// config/azure-keyvault.json
{
  "secrets_backend": "keyvault",
  "azure": {
    "keyvault_url": "https://misp-secrets-kv.vault.azure.net/",
    "use_managed_identity": true
  }
}
```

**Testing Requirements:**
- Test with Managed Identity
- Test with Service Principal
- Test fallback to local file
- Test secret rotation
- Test backup/restore with Key Vault

**Cost Estimate:** ~$0.03/month for typical usage

**Documentation Needed:**
- Azure Key Vault setup guide
- Managed Identity configuration
- Secret naming conventions
- Migration guide from PASSWORDS.txt to Key Vault
- Troubleshooting guide

---

## Medium Priority

### Email Notification Support
**Status:** Planned
**Priority:** Medium

Add email notifications for:
- Installation completion
- Backup completion/failures
- Update completion/failures
- Critical errors

---

### Slack/Teams Webhook Integration
**Status:** Planned
**Priority:** Medium

Add webhook support for:
- Installation status
- Backup notifications
- Update notifications

---

### GUI Post-Installation Setup Integration
**Status:** 🔄 Planned
**Priority:** High (user experience enhancement)
**Target Version:** v6.0

**Description:**
Integrate the new `misp-setup-complete.py` script into the GUI installer, adding post-installation configuration screens that allow users to configure MISP settings, feeds, and features through the graphical interface.

**New GUI Screens to Add:**

**Screen 7: Post-Installation Setup** (NEW - after Installation Progress)
- Checkbox: "Run post-installation setup automatically"
- Checkbox: "Enable NERC CIP compliance mode" (shows sector-specific info)
- Multi-select: Configuration steps to run
  - [ ] Apply MISP best practice settings
  - [ ] Add threat intelligence feeds
  - [ ] Populate security news
  - [ ] Enable taxonomies & warning lists
  - [ ] Verify setup
- Button: "Configure Now" or "Skip" (configure manually later)

**Screen 8: Feed Selection** (NEW)
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

**Screen 9: News & Taxonomies** (NEW)
- Checkbox: "Populate security news from RSS feeds"
  - Input: Days to look back (default: 30)
  - Input: Maximum items (default: 20)
  - Display: News sources (auto-filtered for NERC CIP mode)
- Checkbox: "Update taxonomies and warning lists"
  - Display: Estimated time (5-10 minutes)
- Progress bar: Real-time progress during update

**Screen 10: Setup Summary & Execution** (NEW)
- Summary of selected configuration:
  - NERC CIP mode: Enabled/Disabled
  - Settings: X settings to apply
  - Feeds: X feeds to add
  - News: X days of news to fetch
  - Taxonomies: Update enabled/disabled
- Estimated time: X minutes
- Button: "Apply Configuration"
- Progress display: Real-time feedback
  - Step 1: Applying settings... ✓
  - Step 2: Adding feeds... [===>  ] 60%
  - Step 3: Fetching news... ⏳
- Error handling: Show errors inline, allow continue/retry

**Integration Tasks:**

1. **Modify Installation Progress Screen** (progress.py)
   - Add "Post-installation setup" phase after "Initialization"
   - Option to launch setup wizard after installation complete
   - Pass API key to setup screens automatically

2. **Create Post-Install Setup Screens**
   - `gui/screens/post_setup.py` - Main post-installation configuration screen
   - `gui/screens/feed_selection.py` - Feed selection with NERC CIP mode
   - `gui/screens/news_taxonomies.py` - News and taxonomy configuration
   - `gui/screens/setup_execution.py` - Execute setup with progress tracking

3. **Create Setup Widgets**
   - `gui/widgets/feed_selector.py` - Multi-select feed widget with preview
   - `gui/widgets/setup_progress.py` - Real-time setup progress widget
   - `gui/widgets/nerc_cip_banner.py` - NERC CIP mode indicator/banner

4. **Integrate misp-setup-complete.py**
   - Import `MISPSetupComplete` class into GUI
   - Call setup methods from GUI screens
   - Capture output for progress display
   - Handle errors gracefully in GUI

5. **Update Completion Screen** (completion.py)
   - Add "Setup Configuration" section showing what was configured
   - Display feed count, news count, settings applied
   - Show "NERC CIP Mode: ENABLED" if applicable
   - Add button: "Run Additional Setup" (re-launch post-install wizard)

**Files to Create/Modify:**
- 🆕 `gui/screens/post_setup.py` - Post-installation setup wizard entry
- 🆕 `gui/screens/feed_selection.py` - Feed selection screen
- 🆕 `gui/screens/news_taxonomies.py` - News & taxonomy configuration
- 🆕 `gui/screens/setup_execution.py` - Setup execution with progress
- 🆕 `gui/widgets/feed_selector.py` - Feed selection widget
- 🆕 `gui/widgets/setup_progress.py` - Setup progress widget
- 🆕 `gui/widgets/nerc_cip_banner.py` - NERC CIP indicator widget
- ✏️ `gui/screens/progress.py` - Add post-install phase
- ✏️ `gui/screens/completion.py` - Add setup summary section
- ✏️ `misp_install_gui.py` - Integrate new screens into wizard flow

**User Flow Updates:**

**Current Flow:**
1. Welcome → 2. Network → 3. Security → 4. Performance → 5. Environment → 6. Review → 7. Progress → 8. Completion

**New Flow with Post-Install:**
1. Welcome
2. Network
3. Security
4. Performance
5. Environment
6. **Post-Install Setup** (NEW)
7. **Feed Selection** (NEW - conditional)
8. **News & Taxonomies** (NEW - conditional)
9. Review (updated to include post-install config)
10. Progress (updated to include setup phase)
11. **Setup Execution** (NEW - conditional)
12. Completion (updated with setup summary)

**Configuration File Updates:**

Generated config now includes post-install settings:
```json
{
  "server_ip": "192.168.20.193",
  "domain": "misp.company.com",
  "admin_email": "admin@company.com",
  "admin_org": "Security Operations",
  "environment": "production",
  "post_install": {
    "enabled": true,
    "nerc_cip_ready": true,
    "run_setup": true,
    "skip_feeds": false,
    "skip_news": false,
    "skip_settings": false,
    "selected_feeds": [
      "cisa-ics-advisories",
      "securityweek-ics-ot",
      "bleepingcomputer-critical-infra",
      "industrialcyber"
    ],
    "news_settings": {
      "days": 30,
      "max_items": 20
    }
  }
}
```

**Benefits:**
- ✨ Complete MISP setup in single GUI workflow
- ✨ No need to run separate command-line scripts
- ✨ Visual feed selection with previews
- ✨ Real-time progress feedback
- ✨ NERC CIP mode prominently displayed
- ✨ Saved configuration can be reused (CI/CD)
- ✨ Reduces post-install manual steps

**Testing Requirements:**
- Test complete flow: install + post-install via GUI
- Test NERC CIP mode UI elements
- Test feed selection with many feeds
- Test progress display during setup
- Test error handling (failed feed adds, etc.)
- Test skip options (skip post-install entirely)
- Test resume after interruption
- Test web mode with post-install screens

**Estimated Development Time:**
- Screen development: 12-16 hours
- Widget development: 8-10 hours
- Integration & testing: 8-12 hours
- Documentation: 4-6 hours
- **Total: 32-44 hours**

---

### GUI Installer Option
**Status:** ✅ COMPLETED (v1.0 - October 2025)
**Priority:** ~~Medium~~ **DONE**
**Target Version:** ~~v5.5 or v6.0~~ **Released: v1.0**

**Description:**
Modern graphical installer using Python Textual framework. Provides an intuitive multi-step wizard interface that runs in terminal (TUI) or web browser, making MISP installation accessible to users who prefer visual interfaces over command-line.

**✅ IMPLEMENTATION COMPLETE:**
- Multi-step wizard with 5 screens (Welcome, Network, Security, Environment, Review)
- Password strength validation and auto-generation
- Clipboard paste support (Ctrl+V) using pyperclip
- pipx installation for Ubuntu 24.04+
- Automated setup script (install-gui.sh)
- Configuration file generation (JSON format)
- Full keyboard navigation
- Dark/Light theme toggle
- Complete user documentation (docs/GUI_INSTALLER.md)

**Framework: Textual** (https://github.com/Textualize/textual)
- Modern Python TUI framework with web capability
- Run as terminal application OR serve via web browser (`textual serve`)
- API inspired by React/web development
- Built-in validation, forms, widgets
- Production-ready (MIT license)
- No external dependencies beyond Python 3.8+

**Benefits:**
- **User-Friendly**: Visual forms with real-time validation
- **Multi-Step Wizard**: Guided installation process
- **Dual Mode**: Terminal or web browser (same code)
- **Input Validation**: Immediate feedback on configuration errors
- **Progress Tracking**: Visual progress bars for installation phases
- **Accessibility**: Easier for non-technical users
- **Resume Support**: Save progress and resume later
- **Help Text**: Contextual help for each configuration option

**Architecture:**

```
misp_install_gui.py (Frontend - Textual UI)
    ↓ Multi-step wizard interface
    ↓ Form validation and user input
    ↓ Generates config JSON
    ↓ Calls backend with --config flag
misp-install.py (Backend - Installation Engine)
    ↓ Shared installation logic (no changes needed)
    ↓ Uses config file from GUI
    ↓ Performs actual installation
```

**User Flow - 8 Step Wizard:**

1. **Welcome Screen**
   - Introduction to MISP
   - Prerequisites checklist (Ubuntu 22.04+, 8GB+ RAM, sudo access)
   - System resource detection
   - Continue or Exit

2. **Network Configuration**
   - Server IP address (auto-detect with override)
   - Domain/FQDN (e.g., misp.company.com)
   - Admin email address
   - Admin organization name
   - Real-time DNS validation

3. **Security Settings**
   - Admin password (with strength meter)
   - MySQL password (with strength meter)
   - GPG passphrase (with strength meter)
   - Auto-generate option for all passwords
   - Password visibility toggle
   - Validation: 12+ chars, uppercase, lowercase, number, special

4. **Performance Tuning**
   - Auto-detect system resources (recommended)
   - Manual override options:
     - PHP memory limit (1024M, 2048M, 4096M)
     - Worker processes (2, 4, 8, 16)
   - Resource calculator based on RAM/CPU
   - Performance impact explanation

5. **Environment Selection**
   - Development (debug enabled, verbose logging)
   - Staging (production-like, testing)
   - Production (optimized, security hardened)
   - Environment comparison table

6. **Optional Integrations** (Future Expansion)
   - Splunk Cloud (HEC URL, token)
   - Security Onion (API URL, key)
   - Azure Key Vault (vault URL, managed identity)
   - Email notifications (SMTP settings)
   - Slack/Teams webhooks

7. **Review & Confirm**
   - Summary of all configuration
   - Estimated installation time
   - Disk space requirements
   - Final confirmation prompt
   - Save config option (for CI/CD reuse)

8. **Installation Progress**
   - Phase-by-phase progress display
   - Current operation indicator
   - Estimated time remaining
   - Real-time log streaming (optional)
   - Pause/Resume capability

9. **Completion Screen**
   - Success message
   - Access credentials display
   - MISP URL with clickable link
   - Post-installation checklist
   - Copy credentials to clipboard

**Implementation Tasks:**

**Phase 1: Core Framework Setup**
1. Install Textual dependencies (`pip install textual textual-dev`)
2. Create `misp-install-gui.py` skeleton
3. Implement welcome screen with system checks
4. Add basic navigation (Next/Back/Cancel buttons)
5. Test TUI rendering in terminal

**Phase 2: Form Screens (Steps 2-5)**
6. Implement Network Configuration screen with validation
7. Implement Security Settings screen with password strength meter
8. Implement Performance Tuning screen with auto-detection
9. Implement Environment Selection screen
10. Add form state management (save progress between screens)

**Phase 3: Integration & Progress**
11. Implement Review & Confirm screen with editable summary
12. Create config JSON generator from form data
13. Implement Installation Progress screen
14. Add real-time log streaming from misp-install.py
15. Implement phase progress tracking

**Phase 4: Completion & Error Handling**
16. Implement Completion screen with credentials display
17. Add error handling for installation failures
18. Implement resume capability (load saved state)
19. Add rollback option on failure
20. Create help system (contextual tooltips)

**Phase 5: Testing & Polish**
21. Test full installation flow end-to-end
22. Test web browser mode (`textual serve`)
23. Add keyboard shortcuts (Tab, Enter, Esc)
24. Implement dark/light theme toggle
25. Create user documentation

**Files to Create:**
- `misp_install_gui.py` - Main GUI application (Textual app)
- `gui/screens/` - Directory for wizard screen modules:
  - `welcome.py` - Welcome screen with prerequisites
  - `network.py` - Network configuration form
  - `security.py` - Password configuration with strength meter
  - `performance.py` - Performance tuning options
  - `environment.py` - Environment selection
  - `integrations.py` - Optional integrations (future)
  - `review.py` - Configuration review summary
  - `progress.py` - Installation progress display
  - `completion.py` - Success/failure results
- `gui/widgets/` - Custom Textual widgets:
  - `password_input.py` - Password field with strength meter
  - `validator.py` - Real-time form validation
  - `progress_tracker.py` - Phase progress widget
- `gui/utils.py` - Helper functions (system detection, validation)
- `docs/GUI_INSTALLER.md` - GUI installer user guide
- `docs/GUI_DEVELOPMENT.md` - Developer guide for GUI

**Dependencies:**
```bash
pip install textual textual-dev textual-wizard
```

**Configuration Example (Generated by GUI):**
```json
{
  "server_ip": "192.168.20.193",
  "domain": "misp.company.com",
  "admin_email": "admin@company.com",
  "admin_org": "Security Operations",
  "admin_password": "SecurePass123!@#",
  "mysql_password": "DBPass456!@#",
  "gpg_passphrase": "GPGPass789!@#",
  "encryption_key": "auto-generated",
  "environment": "production",
  "php_memory_limit": "2048M",
  "workers": 4,
  "integrations": {
    "splunk_cloud": false,
    "security_onion": false,
    "azure_keyvault": false
  }
}
```

**Usage Examples:**

**Terminal Mode (TUI):**
```bash
# Launch GUI installer in terminal
python3 misp_install_gui.py

# Load existing config and edit
python3 misp_install_gui.py --load config/misp-config.json

# Save config without installing
python3 misp_install_gui.py --save-only
```

**Web Browser Mode:**
```bash
# Serve GUI on localhost:8000
textual serve misp_install_gui.py

# Serve on specific port
textual serve misp_install_gui.py --port 8080

# Share URL with team (accessible from any browser)
textual serve misp_install_gui.py --host 0.0.0.0
```

**CI/CD Integration:**
```bash
# Generate config via GUI, then use in automation
python3 misp_install_gui.py --save-only --output ci-config.json
python3 misp-install.py --config ci-config.json --non-interactive
```

**Key Features:**

**Input Validation:**
- IP address format validation
- Domain name DNS resolution check
- Email format validation
- Password strength scoring (zxcvbn-style)
- Real-time feedback as user types

**System Detection:**
- Auto-detect server IP from network interfaces
- Auto-detect RAM and suggest PHP memory limit
- Auto-detect CPU cores and suggest worker count
- Disk space check before installation

**Accessibility:**
- Keyboard navigation (Tab, Shift+Tab, Arrow keys)
- Screen reader friendly (semantic HTML in web mode)
- High contrast theme option
- Tooltips and help text on every field

**Error Handling:**
- Validation errors shown inline
- Installation failures show detailed logs
- Resume from last successful phase
- Rollback option if installation fails
- Export error logs for support

**Testing Requirements:**
- Test on Ubuntu 22.04 and 24.04
- Test in various terminal emulators (Gnome Terminal, iTerm2, etc.)
- Test web mode in Chrome, Firefox, Safari
- Test with screen readers (accessibility)
- Test keyboard-only navigation
- Test resume after interruption
- Test with various screen sizes (responsive)
- Performance test with slow network/disk

**Documentation Needed:**
- GUI installer user guide with screenshots
- Web mode setup instructions
- Keyboard shortcuts reference
- Troubleshooting guide for GUI issues
- Developer guide for adding new screens
- Theme customization guide

**Security Considerations:**
- No passwords logged or displayed in web mode without auth
- Config file saved with 600 permissions
- Web mode should bind to localhost by default
- Add authentication option for web mode (future)
- Clear credentials from memory on exit

**Performance Considerations:**
- Async UI updates during installation
- Non-blocking progress display
- Efficient log streaming (last N lines)
- Lazy loading of screens
- Minimal memory footprint

**Future Enhancements (v6.1+):**
- Multi-language support (i18n)
- Configuration templates (dev, prod, enterprise)
- Wizard replay (show what was configured)
- Integration testing wizard (test Splunk/SO connections)
- Custom branding (logo, colors, company name)
- Save favorite configurations
- Installation time estimation based on hardware
- Notification when installation complete (desktop notification)

**Related Projects:**
- [Textual Framework](https://github.com/Textualize/textual)
- [textual-wizard](https://github.com/SkwalExe/textual-wizard)
- [textual-forms](https://pypi.org/project/textual-forms/)
- [Rich (Terminal Styling)](https://github.com/Textualize/rich)

**Estimated Development Time:**
- Phase 1-2: 8-12 hours (core screens)
- Phase 3: 6-8 hours (integration & progress)
- Phase 4: 4-6 hours (completion & errors)
- Phase 5: 6-8 hours (testing & polish)
- **Total: 24-34 hours** for complete implementation

**Why This Approach:**
1. **Non-invasive**: No changes to existing misp-install.py backend
2. **Reusable**: Generated config files work with CLI installer
3. **Maintainable**: Separation of UI and installation logic
4. **Flexible**: Easy to add new screens for integrations
5. **Modern**: Uses industry-standard framework (Textual)
6. **Accessible**: Works in terminal AND web browser

---

## Completed

✅ v5.4.0 - ACL-based permission system
✅ v5.4.0 - misp-update.py implementation
✅ v5.4.0 - Complete documentation updates
✅ v5.0.0 - Python rewrite
✅ v5.0.0 - Centralized logging
✅ v5.0.0 - Backup/restore scripts
✅ v5.0.0 - Health checks

---

## Version Planning

### v5.5.0 (Next Release)
- Azure Key Vault integration
- Email notifications

### v6.0.0 (Future)
- Multi-cloud support (Azure, AWS, GCP)
- GUI installer
- Enhanced monitoring

---

**Last Updated:** 2025-10-14
**Maintainer:** Claude Code / tKQB Enterprises
