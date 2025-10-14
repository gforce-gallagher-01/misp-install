# MISP Installation Suite - Documentation Index

**Version:** 5.5
**Last Updated:** 2025-10-14

Welcome to the MISP installation suite documentation. This index helps you find the right documentation for your role and task.

---

## 🚀 Quick Start Guides

### New Users
1. **[QUICKSTART.md](../QUICKSTART.md)** - Get MISP running in 30 minutes
2. **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation guide (12 phases)
3. **[GUI_INSTALLER.md](../GUI_INSTALLER.md)** - Graphical installation wizard

### Returning Users
1. **[README.md](../README.md)** - Project overview and features
2. **[SCRIPTS.md](../SCRIPTS.md)** - All scripts and common commands
3. **[MAINTENANCE.md](../MAINTENANCE.md)** - Ongoing operations

---

## 📖 Documentation by Role

### System Administrators

**Installation & Setup:**
- [SETUP.md](../SETUP.md) - Prerequisites and sudoers configuration
- [INSTALLATION.md](INSTALLATION.md) - Complete installation guide
- [INSTALLATION-CHECKLIST.md](../INSTALLATION-CHECKLIST.md) - Post-install verification
- [GUI_INSTALLER.md](../GUI_INSTALLER.md) - GUI installer guide

**Operations:**
- [MAINTENANCE.md](../MAINTENANCE.md) - Backup, update, monitoring
- [MISP-UPDATE.md](../MISP-UPDATE.md) - Update procedures
- [MISP-BACKUP-CRON.md](../MISP-BACKUP-CRON.md) - Automated backups

**Troubleshooting:**
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues and solutions
- [KNOWN-ISSUES.md](../KNOWN-ISSUES.md)  - Known limitations and workarounds

### Security Engineers

**Configuration:**
- [CONFIGURATION-GUIDE.md](../CONFIGURATION-GUIDE.md) - MISP configuration
- [CONFIGURATION-BEST-PRACTICES.md](../CONFIGURATION-BEST-PRACTICES.md) - Security hardening
- [NERC_CIP_CONFIGURATION.md](../NERC_CIP_CONFIGURATION.md) - Energy sector compliance

**Integrations:**
- [THIRD-PARTY-INTEGRATIONS.md](THIRD-PARTY-INTEGRATIONS.md) - SIEM, EDR, SOAR integration overview
- [integrations/SPLUNK.md](integrations/SPLUNK.md) - Splunk integration (planned)
- [integrations/SENTINEL.md](integrations/SENTINEL.md) - Microsoft Sentinel (planned)
- [integrations/THEHIVE.md](integrations/THEHIVE.md) - TheHive + Cortex (planned)

**Security:**
- [SECURITY_ARCHITECTURE.md](../SECURITY_ARCHITECTURE.md) - Security model and ACLs
- [AZURE-ENTRA-ID-SETUP.md](../AZURE-ENTRA-ID-SETUP.md) - Azure AD authentication

### Developers

**Architecture:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Core design principles
- [REFACTORING_PLAN.md](../REFACTORING_PLAN.md) - Modular architecture plan
- [REPOSITORY-STRUCTURE.md](../REPOSITORY-STRUCTURE.md) - Project layout

**API & Scripts:**
- [API_USAGE.md](API_USAGE.md) - MISP REST API usage guide
- [SCRIPTS.md](../SCRIPTS.md) - Complete script inventory
- [README_LOGGING.md](../README_LOGGING.md) - Centralized logging system

**Development:**
- [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute
- [CLAUDE.md](../CLAUDE.md) - AI assistant guidance

### Energy Sector / Utilities

**NERC CIP Compliance:**
- [NERC_CIP_CONFIGURATION.md](../NERC_CIP_CONFIGURATION.md) - Complete NERC CIP guide (50+ pages)
  - ICS/SCADA threat intelligence
  - E-ISAC integration
  - CIP-003 through CIP-015 use cases
  - Solar/wind/battery-specific guidance

**Quick Setup:**
1. Install MISP: `python3 misp-install.py`
2. Run NERC CIP configuration: `python3 scripts/configure-misp-nerc-cip.py`
3. Enable ICS/SCADA feeds: `python3 scripts/enable-misp-feeds.py --nerc-cip`
4. Review compliance documentation: [NERC_CIP_CONFIGURATION.md](../NERC_CIP_CONFIGURATION.md)

---

## 📚 Documentation by Task

### Installation

**Planning & Prerequisites:**
1. [README.md](../README.md) - System requirements
2. [SETUP.md](../SETUP.md) - Sudoers configuration
3. [QUICKSTART.md](../QUICKSTART.md) - Quick overview

**Installation Methods:**
- **CLI Interactive:** `python3 misp-install.py`
- **CLI Non-Interactive:** `python3 misp-install.py --config production.json --non-interactive`
- **GUI Mode:** `misp-install-gui` or `python3 misp_install_gui.py`

**Detailed Guides:**
- [INSTALLATION.md](INSTALLATION.md) - 12-phase installation process
- [GUI_INSTALLER.md](../GUI_INSTALLER.md) - GUI wizard walkthrough

**Post-Installation:**
- [INSTALLATION-CHECKLIST.md](../INSTALLATION-CHECKLIST.md) - Verification steps
- [API_USAGE.md](API_USAGE.md) - API key and automation setup

### Configuration

**Basic Configuration:**
- [CONFIGURATION-GUIDE.md](../CONFIGURATION-GUIDE.md) - Environment variables, settings
- [config/README.md](../config/README.md) - Configuration file examples

**Advanced Configuration:**
- [CONFIGURATION-BEST-PRACTICES.md](../CONFIGURATION-BEST-PRACTICES.md) - Security best practices
- [ADVANCED-FEATURES.md](../ADVANCED-FEATURES.md) - Advanced features
- [NERC_CIP_CONFIGURATION.md](../NERC_CIP_CONFIGURATION.md) - Sector-specific configuration

### Backup & Restore

**Backup:**
- [MAINTENANCE.md](../MAINTENANCE.md) - Backup strategies
- [MISP-BACKUP-CRON.md](../MISP-BACKUP-CRON.md) - Automated backups
- [SCRIPTS.md](../SCRIPTS.md) - Manual backup commands

**Restore:**
- [SCRIPTS.md](../SCRIPTS.md) - Restore procedures
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Recovery scenarios

### Updates & Upgrades

**Updating MISP:**
- [MISP-UPDATE.md](../MISP-UPDATE.md) - Update procedures
- [MAINTENANCE.md](../MAINTENANCE.md) - Maintenance schedules

**Migrating Versions:**
- [CHANGELOG.md](CHANGELOG.md) - Version history and migration notes

### Troubleshooting

**Common Issues:**
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Comprehensive troubleshooting guide
  - Installation issues
  - Runtime issues
  - API issues
  - Integration issues
- [KNOWN-ISSUES.md](../KNOWN-ISSUES.md) - Known limitations

**Specific Problems:**
- Docker health check failures: [KNOWN-ISSUES.md](../KNOWN-ISSUES.md)
- Permission errors: [SECURITY_ARCHITECTURE.md](../SECURITY_ARCHITECTURE.md)
- ACL issues: [ACL-FIX-SUMMARY.md](../ACL-FIX-SUMMARY.md)

### Integration

**SIEM Integration:**
- [THIRD-PARTY-INTEGRATIONS.md](THIRD-PARTY-INTEGRATIONS.md) - Integration overview
- Splunk: [integrations/SPLUNK.md](integrations/SPLUNK.md) (planned in v5.6)
- Microsoft Sentinel: [integrations/SENTINEL.md](integrations/SENTINEL.md) (planned in v5.6)
- ELK Stack: [integrations/ELK.md](integrations/ELK.md) (planned)

**EDR/XDR Integration:**
- CrowdStrike: [integrations/CROWDSTRIKE.md](integrations/CROWDSTRIKE.md) (planned)
- Microsoft Defender: [integrations/DEFENDER.md](integrations/DEFENDER.md) (planned)

**SOAR Integration:**
- TheHive + Cortex: [integrations/THEHIVE.md](integrations/THEHIVE.md) (planned)

---

## 🔍 Documentation by Topic

### Architecture & Design

- [ARCHITECTURE.md](ARCHITECTURE.md) - Core design principles
  - Centralized JSON logging
  - State management
  - Phase-based execution
  - Docker-first architecture
- [SECURITY_ARCHITECTURE.md](../SECURITY_ARCHITECTURE.md) - Security model
  - ACL-based permissions
  - Dedicated user (misp-owner)
  - File ownership matrix
- [REFACTORING_PLAN.md](../REFACTORING_PLAN.md) - Future modular architecture

### Logging & Monitoring

- [README_LOGGING.md](../README_LOGGING.md) - Centralized logging system
  - CIM field names
  - SIEM integration
  - Log rotation
  - Sourcetype conventions
- [MAINTENANCE.md](../MAINTENANCE.md) - Monitoring and health checks

### Scripts & Automation

- [SCRIPTS.md](../SCRIPTS.md) - Complete script inventory (16+ scripts)
  - Installation scripts
  - Backup/restore scripts
  - Configuration scripts
  - Feed management scripts
- [API_USAGE.md](API_USAGE.md) - MISP REST API automation
  - API key setup (3 methods)
  - Helper module usage
  - Common operations
  - Best practices

### Testing & Quality

- [testing_and_updates/TESTING_REPORT.md](testing_and_updates/TESTING_REPORT.md) - Test results
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 📋 Reference Documentation

### Version Information

- [CHANGELOG.md](CHANGELOG.md) - Complete version history
  - v5.5 (2025-10-14) - API integration, GUI installer, setup scripts
  - v5.4 (2025-10-13) - ACL permissions, dedicated user
  - v5.0 (2025-10-11) - Python rewrite

- [ROADMAP.md](ROADMAP.md) - Future development plans
  - v5.6 (Q1 2026) - Splunk, Security Onion, Azure Key Vault
  - v5.7 (Q2 2026) - Email notifications, Slack/Teams webhooks
  - v6.0 (Q3 2026) - GUI post-install, Let's Encrypt

### Current Tasks

- [TODO.md](../TODO.md) - Active development priorities
  - High priority: Splunk Cloud, Security Onion, Azure Key Vault
  - Medium priority: Email notifications, Slack/Teams webhooks
  - Recently completed: v5.5 features

### Archive

- [archive/](archive/) - Historical documentation
  - [INDEX.md](archive/INDEX.md) - Old documentation index
  - [COMPLETE-FILE-LAYOUT.md](archive/COMPLETE-FILE-LAYOUT.md) - Legacy file structure
  - [READY-TO-RUN-SETUP.md](archive/READY-TO-RUN-SETUP.md) - Old setup guide

---

## 🎯 Recommended Reading Paths

### Path 1: First-Time Installation (30 minutes)
1. [README.md](../README.md) - Overview (5 min)
2. [QUICKSTART.md](../QUICKSTART.md) - Quick setup (10 min)
3. [INSTALLATION.md](INSTALLATION.md) or [GUI_INSTALLER.md](../GUI_INSTALLER.md) (15 min)

### Path 2: Production Deployment (2-3 hours)
1. [SETUP.md](../SETUP.md) - Prerequisites (30 min)
2. [INSTALLATION.md](INSTALLATION.md) - Full installation (1 hour)
3. [CONFIGURATION-BEST-PRACTICES.md](../CONFIGURATION-BEST-PRACTICES.md) - Hardening (30 min)
4. [MISP-BACKUP-CRON.md](../MISP-BACKUP-CRON.md) - Automated backups (30 min)

### Path 3: NERC CIP Compliance (4-6 hours)
1. [NERC_CIP_CONFIGURATION.md](../NERC_CIP_CONFIGURATION.md) - Complete guide (2 hours)
2. Install MISP (1 hour)
3. Configure NERC CIP mode (1 hour)
4. Enable feeds and verify (1-2 hours)

### Path 4: SIEM Integration (2-4 hours)
1. [THIRD-PARTY-INTEGRATIONS.md](THIRD-PARTY-INTEGRATIONS.md) - Overview (30 min)
2. Choose integration (Splunk/Sentinel/ELK)
3. Follow specific integration guide (1-3 hours)
4. Test and validate (30 min)

### Path 5: Developer Onboarding (3-4 hours)
1. [CLAUDE.md](../CLAUDE.md) - Project guidance (30 min)
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Design principles (1 hour)
3. [API_USAGE.md](API_USAGE.md) - API automation (1 hour)
4. [CONTRIBUTING.md](../CONTRIBUTING.md) - Development process (30 min)
5. [REFACTORING_PLAN.md](../REFACTORING_PLAN.md) - Future architecture (30 min)

---

## 📁 Complete File List

### Root Directory
- README.md - Project overview
- QUICKSTART.md - Quick installation guide
- TODO.md - Active development priorities
- SCRIPTS.md - Complete script inventory
- CLAUDE.md - AI assistant guidance
- Various configuration and setup guides (14 files)

### docs/
- ARCHITECTURE.md - Core design principles
- INSTALLATION.md - Detailed installation guide
- ROADMAP.md - Future development plans
- CHANGELOG.md - Version history
- THIRD-PARTY-INTEGRATIONS.md - Integration overview
- API_USAGE.md - API usage guide
- NERC_CIP_CONFIGURATION.md - Energy sector compliance
- testing_and_updates/ - Test reports
- archive/ - Historical documentation
- integrations/ - Planned integration guides

### scripts/
- README.md - Script directory guide (points to ../SCRIPTS.md)
- 15+ Python scripts for installation, backup, configuration, feeds

### config/
- README.md - Configuration file examples
- *.json.example - JSON configuration templates
- *.yaml.example - YAML configuration templates

---

## 🔗 External Resources

- **MISP Project**: https://www.misp-project.org/
- **MISP GitHub**: https://github.com/MISP/MISP
- **MISP Documentation**: https://www.misp-project.org/documentation/
- **NERC Standards**: https://www.nerc.com/pa/Stand/Pages/default.aspx
- **E-ISAC**: https://www.eisac.com/

---

## 📮 Getting Help

1. **Check Documentation**: Use this index to find relevant guides
2. **Search Issues**: [GitHub Issues](https://github.com/your-org/misp-install/issues)
3. **Read Troubleshooting**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
4. **Check Known Issues**: [KNOWN-ISSUES.md](../KNOWN-ISSUES.md)
5. **Report Bugs**: [Create New Issue](https://github.com/your-org/misp-install/issues/new)

---

**Last Updated:** 2025-10-14
**Maintainer:** tKQB Enterprises
**Total Documentation**: 38 markdown files, 16,000+ lines
