# MISP Installation Tool - TODO List

**Version:** 5.6
**Last Updated:** 2025-10-16

This file tracks active development priorities. For completed features, see [CHANGELOG.md](docs/CHANGELOG.md). For long-term vision, see [ROADMAP.md](docs/ROADMAP.md).

---

## Quick Links

- **[CHANGELOG.md](docs/CHANGELOG.md)** - Completed features and version history
- **[ROADMAP.md](docs/ROADMAP.md)** - Future vision (v6.0+)
- **[GitHub Issues](https://github.com/your-org/misp-install/issues)** - Bug tracking

---

## High Priority (v5.7 - Next Release)

### Custom MISP Dashboards for Utilities Sector
**Status:** Planned
**Priority:** High
**Target Version:** v5.7
**Estimated Effort:** 40-50 hours

**Description:**
Develop comprehensive custom dashboards and widgets specifically designed for utilities sector threat intelligence monitoring, focusing on ICS/SCADA/OT environments.

**Key Components:**

#### 1. Utilities Sector Overview Dashboard
**Effort:** 12-15 hours
- Real-time threat activity heat map (energy sector focus)
- ICS/SCADA specific threat indicators
- Critical infrastructure sector breakdown
- Top targeted ICS protocols (Modbus, DNP3, IEC 61850)
- Geographic threat distribution for utilities
- NERC CIP compliance monitoring widget

#### 2. ICS/OT Threat Intelligence Dashboard
**Effort:** 10-12 hours
- MITRE ATT&CK for ICS techniques trending
- ICS vulnerability feed aggregation widget
- SCADA-specific IOC monitoring
- OT protocol anomaly detection
- Industrial malware family tracking (TRITON, INDUSTROYER, etc.)
- Asset type targeting analysis

#### 3. Utilities Sector Feed Dashboard
**Effort:** 8-10 hours
- ICS-CERT advisory feed visualization
- E-ISAC alert monitoring
- DHS CISA utilities sector alerts
- Vendor security bulletins (Siemens, Schneider, ABB, Rockwell)
- Zero-day tracking for ICS vendors
- CVE scoring specific to utilities

#### 4. Organizational Contribution Dashboard (Utilities)
**Effort:** 5-6 hours
- Utilities ISAC member contribution rankings
- Sector-specific sharing metrics
- Regional utilities cooperation heat map
- Energy sector organization participation
- Monthly contribution trends by subsector (generation, transmission, distribution)

#### 5. Threat Actor Dashboard (Utilities Focus)
**Effort:** 5-6 hours
- APT groups targeting utilities (Dragonfly, XENOTIME, APT33, Sandworm)
- Nation-state attribution timeline
- Campaign tracking against energy infrastructure
- TTPs specific to utilities sector
- Historical incident timeline

**Technical Implementation:**
1. Create custom widget collection in `/var/www/MISP/app/View/Elements/dashboard/Widgets/`
2. Develop utilities-specific data aggregation modules
3. Integrate with ICS taxonomy and MITRE ATT&CK for ICS
4. Create sector filtering logic (organization metadata)
5. Implement real-time ZMQ feed processing for ICS events
6. Design responsive layouts for SOC environments

**Deliverables:**
- `/scripts/create-utilities-dashboards.py` - Dashboard setup automation
- `/config/dashboards/utilities-sector-default.json` - Default dashboard config
- `/docs/UTILITIES_DASHBOARDS.md` - User guide with screenshots
- Custom widget collection for ICS/OT monitoring
- Example queries and filters for utilities sector

**Dependencies:**
- MISP Dashboard (separate installation - misp-dashboard)
- Phase 11.8 (Utilities Sector configuration) completed
- ICS taxonomy enabled
- MITRE ATT&CK for ICS Galaxy enabled
- Utilities sector feeds configured
- PHP 8.3+ CLI (for widget development/testing)

**Note:** PHP Apache module may be installed as dependency but should be disabled to prevent port conflicts with MISP:
```bash
sudo systemctl stop apache2 && sudo systemctl disable apache2
```

**Success Metrics:**
- 5+ custom dashboards deployed
- 15+ utilities-specific widgets created
- Real-time ICS threat visibility
- Reduced mean time to detect (MTTD) for utilities threats
- Enhanced situational awareness for SOC teams

---

### Splunk Cloud Integration
**Status:** Planned
**Priority:** High
**Target Version:** v5.7
**Estimated Effort:** 20-30 hours

**Description:**
Integrate MISP with Splunk Cloud for real-time threat intelligence sharing and automated response using HEC (HTTP Event Collector), certified apps, and Universal Forwarder.

**Key Tasks:**
1. Universal Forwarder setup for `/opt/misp/logs/`
2. HEC integration script (MISP API → Splunk)
3. Splunk App configuration (SOAR or Platform)
4. Threat Intelligence framework setup
5. Dashboards and correlation searches

**Deliverables:**
- `scripts/splunk-hec-forwarder.py` - HEC integration
- `docs/integrations/SPLUNK_CLOUD.md` - Complete guide
- Configuration templates

**See:** [ROADMAP.md - Splunk Integration](docs/ROADMAP.md#splunk-cloud-integration) for full details

---

### Security Onion Integration
**Status:** Planned
**Priority:** High
**Target Version:** v5.7
**Estimated Effort:** 15-20 hours

**Description:**
Integrate MISP with Security Onion for bidirectional threat intelligence sharing, Suricata rule generation, and automated threat hunting workflows.

**Key Tasks:**
1. Security Onion configuration options
2. MISP API endpoints for SO access
3. Suricata rule import/export
4. Event synchronization service
5. Elasticsearch indexing

**Deliverables:**
- `scripts/so-sync.py` - Bidirectional sync
- `docs/integrations/SECURITY_ONION.md` - Complete guide

**See:** [ROADMAP.md - Security Onion](docs/ROADMAP.md#security-onion-integration) for full details

---

### Azure Key Vault Integration
**Status:** Planned
**Priority:** High
**Target Version:** v5.7
**Estimated Effort:** 10-15 hours

**Description:**
Implement Azure Key Vault for secure secrets management in Azure environments, eliminating PASSWORDS.txt file on disk.

**Key Tasks:**
1. Add Azure SDK dependencies
2. Secrets management abstraction layer
3. Key Vault configuration options (`--use-keyvault`)
4. Managed Identity authentication
5. Fallback to local PASSWORDS.txt

**Deliverables:**
- Modified `misp-install.py` (Phases 6, 9)
- `docs/integrations/AZURE_KEYVAULT.md` - Setup guide
- Configuration templates

**See:** [ROADMAP.md - Azure Key Vault](docs/ROADMAP.md#azure-key-vault-integration) for full details

---

## Medium Priority (v5.8+)

### MISP-Dashboard Automated Installation
**Status:** Planned
**Priority:** Medium
**Target Version:** v5.8
**Estimated Effort:** 12-15 hours

**Description:**
Automate installation and configuration of MISP-Dashboard (separate component) for real-time threat intelligence visualization.

**Key Tasks:**
1. Clone MISP-dashboard repository
2. Install Python dependencies (redis, zmq)
3. Configure ZMQ feeds from MISP instance
4. Setup Redis for data storage
5. Configure web server (Flask development or production)
6. Create systemd service for dashboard
7. Configure default dashboards
8. Import utilities sector custom widgets

**Deliverables:**
- `scripts/install-misp-dashboard.sh` - Automated installer
- `scripts/misp-dashboard.service` - Systemd service file
- `docs/MISP_DASHBOARD.md` - Installation guide
- Default configuration with utilities widgets

**Integration:**
- Add as Phase 12 (optional) in main installer
- Configuration option: `install_dashboard: true/false`
- Integrate with utilities sector dashboards (v5.7)

---

### Email Notification Support
**Status:** Planned
**Priority:** Medium
**Target Version:** v5.8
**Estimated Effort:** 8-10 hours

**Features:**
- Installation completion emails
- Backup completion/failure notifications
- Update completion/failure notifications
- Critical error alerts

**Implementation:**
- Use Python `smtplib` or third-party service (SendGrid, AWS SES)
- Configuration via `--email-notify` flag or config file
- SMTP settings in PASSWORDS.txt or Key Vault

---

### Slack/Teams Webhook Integration
**Status:** Planned
**Priority:** Medium
**Target Version:** v5.8
**Estimated Effort:** 6-8 hours

**Features:**
- Installation status webhooks
- Backup notifications
- Update notifications
- Critical error alerts

**Implementation:**
- Webhook URL configuration
- Rich formatted messages (Slack Blocks, Teams Adaptive Cards)
- Retry logic for webhook failures

---

### GUI Post-Installation Setup Integration
**Status:** Planned
**Priority:** Medium
**Target Version:** v6.0
**Estimated Effort:** 32-44 hours

**Description:**
Integrate `misp-setup-complete.py` into GUI installer, adding post-installation configuration screens.

**New GUI Screens:**
- Post-Installation Setup (enable/disable)
- Feed Selection (with NERC CIP mode)
- News & Taxonomies configuration
- Setup Execution with progress tracking

**See:** [ROADMAP.md - GUI Post-Install](docs/ROADMAP.md#gui-post-installation-setup) for full details

---

## Low Priority / Future Enhancements

### Let's Encrypt Certificate Support
**Status:** Planned
**Priority:** Low
**Target Version:** v6.1

Replace self-signed certificates with Let's Encrypt (automated) or commercial CA certificates.

**See:** [ROADMAP.md - SSL Certificates](docs/ROADMAP.md#ssl-certificate-support)

---

### Multi-Cloud Support
**Status:** Concept
**Priority:** Low
**Target Version:** v7.0+

Extend beyond Azure to support AWS and GCP deployments with cloud-native features.

**See:** [ROADMAP.md - Multi-Cloud](docs/ROADMAP.md#multi-cloud-support)

---

## Recently Completed (v5.6 - October 2025)

✅ **v5.6 Advanced Features Release** - Install everything by default with opt-out exclusions
  - Phase 11.8: Utilities Sector Threat Intelligence (ICS/SCADA/MITRE ATT&CK for ICS)
  - Phase 11.9: Automated Maintenance (daily/weekly cron jobs)
  - Phase 11.10: Security News Feeds (ICS-CERT, CISA, Industrial Cyber)
  - Exclusion list system (14 features across 4 categories)
  - Feature registry in `lib/features.py`
  - 4 example configurations in `config/examples/`
  - 100% backward compatible

✅ **Systemd Service for Boot Management** - Automatic MISP startup on Ubuntu 24.04
  - Automatic boot startup with graceful shutdown
  - Health monitoring (5 containers)
  - Restart on failure with security hardening
  - Installation script: `scripts/setup-misp-systemd.sh`
  - Complete documentation: `docs/SYSTEMD_SERVICE.md`

✅ **Critical Bug Fixes**
  - MySQL password escaping in news population script
  - Phase module environment variable handling

---

## Completed (v5.5 - October 2025)

✅ **Code Refactoring - Phases 1-9** - Eliminated duplicate code across codebase
  - Phase 1: Centralized Colors class in `lib/colors.py` (242 lines eliminated)
  - Phase 2: Created `lib/database_manager.py` for MySQL operations (150 lines eliminated)
  - Phase 3: Enhanced `lib/docker_manager.py` for Docker operations (60 lines eliminated)
  - Phase 4: Integrated `lib/backup_manager.py` with centralized managers
  - Phase 5: Created `lib/setup_helper.py` for setup operations (69 lines eliminated, 342 lines reusable)
  - Phase 6: Centralized get_mysql_password() and run_cake_command() (54 net lines eliminated)
    - Phase 6a: DatabaseManager integration (4 scripts)
    - Phase 6b: MISPSetupHelper integration (2 scripts)
  - Phase 7: Centralized API key retrieval from database in `misp_api.py` (19 lines eliminated)
  - Phase 8: Centralized feed constants in `lib/feed_constants.py` (49 lines eliminated)
  - Phase 9: Created `lib/misp_config.py` for MISP paths (2+ lines per script, 10 scripts affected)
  - **Total Impact:** ~650+ lines eliminated, 6 lib/ modules created, improved maintainability

✅ **MISP Complete Setup Script** - Post-installation orchestration with NERC CIP mode
✅ **API Key Generation** - Automatic API key during installation (Phase 11.5)
✅ **API Helper Module** - `misp_api.py` for centralized API access
✅ **API-Based Scripts** - Feed management and news population via REST API
✅ **GUI Installer** - Textual framework TUI/web interface (v1.0)

**See:** [CHANGELOG.md](docs/CHANGELOG.md#v55---2025-10-14) for complete v5.5 release notes

---

## Version Planning

### v5.7 (Next - Q4 2025 / Q1 2026)
- Custom utilities sector dashboards (5+ dashboards, 15+ widgets)
- Splunk Cloud integration
- Security Onion integration
- Azure Key Vault secrets management

### v5.8 (Q1-Q2 2026)
- MISP-Dashboard automated installation
- Email notifications
- Slack/Teams webhooks

### v6.0 (Q3 2026)
- GUI post-install integration
- Enhanced monitoring
- Let's Encrypt support

**See:** [ROADMAP.md](docs/ROADMAP.md) for long-term vision

---

## Contributing

Found a bug or have a feature request?

1. Check existing [TODO items](#high-priority-v56---next-release) above
2. Check [GitHub Issues](https://github.com/your-org/misp-install/issues)
3. Check [ROADMAP.md](docs/ROADMAP.md) for planned features
4. If not listed, [create a new issue](https://github.com/your-org/misp-install/issues/new)

**Development Guidelines:** See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

**Last Updated:** 2025-10-16
**Maintainer:** tKQB Enterprises
