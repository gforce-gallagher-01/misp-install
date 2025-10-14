# MISP Installation Tool - TODO List

**Version:** 5.5
**Last Updated:** 2025-10-14

This file tracks active development priorities. For completed features, see [CHANGELOG.md](docs/CHANGELOG.md). For long-term vision, see [ROADMAP.md](docs/ROADMAP.md).

---

## Quick Links

- **[CHANGELOG.md](docs/CHANGELOG.md)** - Completed features and version history
- **[ROADMAP.md](docs/ROADMAP.md)** - Future vision (v6.0+)
- **[GitHub Issues](https://github.com/your-org/misp-install/issues)** - Bug tracking

---

## High Priority (v5.6 - Next Release)

### Splunk Cloud Integration
**Status:** Planned
**Priority:** High
**Target Version:** v5.6
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
**Target Version:** v5.6
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
**Target Version:** v5.6
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

## Medium Priority (v5.7+)

### Email Notification Support
**Status:** Planned
**Priority:** Medium
**Target Version:** v5.7
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
**Target Version:** v5.7
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

## Recently Completed (v5.5 - October 2025)

✅ **MISP Complete Setup Script** - Post-installation orchestration with NERC CIP mode
✅ **API Key Generation** - Automatic API key during installation (Phase 11.5)
✅ **API Helper Module** - `misp_api.py` for centralized API access
✅ **API-Based Scripts** - Feed management and news population via REST API
✅ **GUI Installer** - Textual framework TUI/web interface (v1.0)

**See:** [CHANGELOG.md](docs/CHANGELOG.md#v55---2025-10-14) for complete v5.5 release notes

---

## Version Planning

### v5.6 (Next - Q1 2026)
- Splunk Cloud integration
- Security Onion integration
- Azure Key Vault secrets management

### v5.7 (Q2 2026)
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

**Last Updated:** 2025-10-14
**Maintainer:** tKQB Enterprises
