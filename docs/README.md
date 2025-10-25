# MISP Installation Suite - Documentation

Welcome to the comprehensive documentation for the MISP Installation Suite. This guide will help you find the information you need quickly.

**Version**: 5.6 (Advanced Features Release)
**Last Updated**: 2025-10-25
**Total Documents**: 110+ organized files

---

## 🚀 Quick Start (New Users)

**Never used MISP Installation Suite before?** Start here:

1. **[Installation Guide](INSTALLATION.md)** - Step-by-step installation process
2. **[Quick Start](QUICKSTART.md)** - Get up and running in 15 minutes
3. **[Configuration Guide](CONFIGURATION-GUIDE.md)** - Configure your deployment

## 📚 Main Documentation Categories

### For End Users

#### Getting Started
- [Installation Guide](INSTALLATION.md) - Complete installation walkthrough
- [Installation Checklist](INSTALLATION-CHECKLIST.md) - Pre-installation verification
- [Quick Start Guide](QUICKSTART.md) - Fast deployment guide
- [Configuration Guide](CONFIGURATION-GUIDE.md) - Configuration options
- [Configuration Best Practices](CONFIGURATION-BEST-PRACTICES.md) - Recommended settings

#### User Guides
- [API Usage Guide](API_USAGE.md) - MISP REST API integration
- [GUI Installer](GUI_INSTALLER.md) - Graphical installation interface
- [Maintenance Guide](MAINTENANCE.md) - Maintaining your MISP instance
- [Maintenance Automation](MAINTENANCE_AUTOMATION.md) - Automated maintenance
- [MISP Backup (Cron)](MISP-BACKUP-CRON.md) - Automated backup configuration
- [MISP Update Guide](MISP-UPDATE.md) - Updating MISP
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Logging System](README_LOGGING.md) - Centralized logging architecture

#### Enterprise Features
- [Azure Entra ID Setup](AZURE-ENTRA-ID-SETUP.md) - Enterprise authentication
- [Advanced Features](ADVANCED-FEATURES.md) - v5.6+ advanced capabilities
- [Systemd Service](SYSTEMD_SERVICE.md) - Running as system service

### For Compliance & Security Teams

#### NERC CIP Compliance
**📁 [NERC CIP Documentation Hub](nerc-cip/README.md)**

Quick links:
- [NERC CIP Audit Report](nerc-cip/AUDIT_REPORT.md) - Current compliance status (35%)
- [Production Readiness Tasks](nerc-cip/PRODUCTION_READINESS_TASKS.md) - 20-task checklist
- [NERC CIP Configuration](nerc-cip/CONFIGURATION.md) - Low & Medium Impact setup

**For Implementation Teams:**
- [Person 1 Research](nerc-cip/research/person-1/AUTH-ACCESS-CONTROL.md) - Auth & Access Control (20-25 hours)
- [Person 2 Research](nerc-cip/research/person-2/EVENTS-THREAT-INTEL.md) - Events & Threat Intel (25-30 hours)
- [Person 3 Research Overview](nerc-cip/research/person-3/00-OVERVIEW.md) - Integrations & Automation (33-44 hours)

**Architecture Documentation:**
- [Architecture Overview](nerc-cip/architecture/00-OVERVIEW.md) - Start here
- Full architecture split into 6 manageable documents

### For Integrators

#### Third-Party Integrations
**📁 [Integrations Directory](integrations/)**
- [MISP Communities Guide](integrations/MISP_COMMUNITIES_GUIDE.md) - Community integration
- [ICS-CSIRT Membership](integrations/ICS-CSIRT_MEMBERSHIP_EMAIL.md) - ICS-CERT integration
- [Feed Management](integrations/FEED_MANAGEMENT_COMPLETE.md) - Threat feed automation
- [Third-Party Integrations](THIRD-PARTY-INTEGRATIONS.md) - General integration guide

### For Developers

#### System Architecture
- [Architecture Overview](ARCHITECTURE.md) - System design and principles
- [Security Architecture](SECURITY_ARCHITECTURE.md) - Security model
- [Repository Structure](REPOSITORY-STRUCTURE.md) - Project organization

#### Development Workflow
**📁 [Development Directory](development/)**
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Branching Strategy](BRANCHING_STRATEGY.md) - Git workflow
- [Branching Migration Guide](BRANCHING_MIGRATION_GUIDE.md) - Migration from old workflow
- [Branch Protection Setup](BRANCH_PROTECTION_SETUP.md) - GitHub branch protection
- [Branching Quick Reference](development/BRANCHING_QUICK_REFERENCE.md) - Command reference
- [CI/CD Guide](CI_CD_GUIDE.md) - Continuous integration
- [Exclusion List Design](development/EXCLUSION_LIST_DESIGN.md) - Feature exclusion system

#### Meta-Documentation & AI Context

**🤖 For AI Assistants & New Developers** - Comprehensive meta-documentation for quick orientation:

**Essential Meta-Docs** (Read these first):
- [PROJECT_KNOWLEDGE.md](PROJECT_KNOWLEDGE.md) - **START HERE** - Complete project overview, patterns, and context
- [ONBOARDING.md](ONBOARDING.md) - 30/60/90 day learning path for new developers
- [PATTERNS.md](PATTERNS.md) - 9 design patterns with code examples and anti-patterns
- [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) - 10 ADRs documenting major architectural decisions

**Implementation Guides**:
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing strategies and debugging techniques
- [TROUBLESHOOTING_PLAYBOOK.md](TROUBLESHOOTING_PLAYBOOK.md) - 22 documented issues with solutions
- [MISP_QUIRKS.md](MISP_QUIRKS.md) - 22 MISP platform quirks and workarounds
- [PRODUCTION_STATE.md](PRODUCTION_STATE.md) - Current running instance state and metrics
- [NERC_CIP_IMPLEMENTATION_GUIDE.md](NERC_CIP_IMPLEMENTATION_GUIDE.md) - 4-phase compliance roadmap (35% → 95%)

**Research Management** (For NERC CIP Research Team):
- [Research Tracker](nerc-cip/research/RESEARCH_TRACKER.md) - 19-task progress tracking (2-week sprint)
- [Review Process](nerc-cip/research/REVIEW_PROCESS.md) - Formal deliverable review (7-step process)
- [Validation Criteria](nerc-cip/research/VALIDATION_CRITERIA.md) - Specific criteria for each task

**Branch Management**:
- [../BRANCHES.md](../BRANCHES.md) - Branch inventory for research, learning, and troubleshooting

**Total Meta-Documentation**: ~10,000 lines across 13 comprehensive documents

---

## 📦 Release Information

**📁 [Releases Directory](releases/)**
- [Changelog](CHANGELOG.md) - Complete change history
- [Roadmap](ROADMAP.md) - Future plans
- [v5.6 Release Notes](releases/V5.6_RELEASE_NOTES.md) - Latest release

**Current Version**: 5.6 (Advanced Features Release)

---

## 📖 Reference Documentation

### Essential References (Root Directory)
Located in the project root for quick access:
- [../README.md](../README.md) - Project overview
- [../SETUP.md](../SETUP.md) - Quick setup guide
- [../SCRIPTS.md](../SCRIPTS.md) - Script inventory and usage
- [../TODO.md](../TODO.md) - Project roadmap and tasks
- [../KNOWN-ISSUES.md](../KNOWN-ISSUES.md) - Known issues and workarounds
- [../CLAUDE.md](../CLAUDE.md) - Project instructions for Claude Code

### Testing & Updates
**📁 [Testing Directory](testing_and_updates/)**
- [Testing Report](testing_and_updates/TESTING_REPORT.md)
- [Changelog](testing_and_updates/CHANGELOG.md)

### Widgets
**📁 [Widgets Directory](../widgets/)**
- [Utilities Sector Dashboard](../widgets/utilities-sector/README.md)
- [Threat Actor Dashboard](../widgets/threat-actor-dashboard/README.md)
- [Organizational Dashboard](../widgets/organizational-dashboard/README.md)

---

## 🗃️ Historical Documentation

**📁 [Historical Directory](historical/)**

Archived documentation from completed work (organized by category):

### Merges
- [Merge Verification Report](historical/merges/MERGE_VERIFICATION_REPORT.md)

### Bug Fixes (13 documents)
- [Dashboard Complete](historical/fixes/DASHBOARD_COMPLETE.md)
- [Widget Fixes Complete](historical/fixes/WIDGET_FIXES_COMPLETE.md)
- [Event Population Fix](historical/fixes/EVENT_POPULATION_FIX.md)
- ... and 10 more widget-related fixes

### Implementations (8 documents)
- [Branching Setup](historical/implementations/BRANCHING_SETUP_COMPLETE.md)
- [CI/CD Implementation](historical/implementations/CI_CD_IMPLEMENTATION_SUMMARY.md)
- [DRY Refactoring](historical/implementations/DRY_REFACTORING_SUMMARY.md)
- [Documentation Improvement Plan](historical/implementations/DOCUMENTATION_IMPROVEMENT_PLAN.md)
- ... and 4 more implementation summaries

### Configuration
- [MISP Configuration Status](historical/configuration/MISP_CONFIGURATION_STATUS.md)

---

## 🔍 Finding What You Need

### By Role

**System Administrator?**
→ Start with [Installation Guide](INSTALLATION.md) and [Maintenance Guide](MAINTENANCE.md)

**Security Analyst?**
→ Check [NERC CIP Hub](nerc-cip/README.md) and [Integrations](integrations/)

**Developer?**
→ See [Contributing Guide](CONTRIBUTING.md) and [Development Docs](development/)

**Manager/Executive?**
→ View [NERC CIP Audit](nerc-cip/AUDIT_REPORT.md) and [Roadmap](ROADMAP.md)

### By Task

**Installing MISP?**
→ [Installation Guide](INSTALLATION.md) → [Configuration Guide](CONFIGURATION-GUIDE.md)

**Troubleshooting Issue?**
→ [Troubleshooting](TROUBLESHOOTING.md) → [Known Issues](../KNOWN-ISSUES.md)

**Achieving Compliance?**
→ [NERC CIP Hub](nerc-cip/README.md) → [Production Readiness](nerc-cip/PRODUCTION_READINESS_TASKS.md)

**Integrating with Tools?**
→ [Integrations Directory](integrations/) → [Third-Party Integrations](THIRD-PARTY-INTEGRATIONS.md)

**Contributing Code?**
→ [Contributing](CONTRIBUTING.md) → [Branching Strategy](BRANCHING_STRATEGY.md)

---

## 📞 Getting Help

1. **Check documentation** - Use navigation above
2. **Review known issues** - See [../KNOWN-ISSUES.md](../KNOWN-ISSUES.md)
3. **Check logs** - See [README_LOGGING.md](README_LOGGING.md)
4. **Search issues** - GitHub issue tracker
5. **Community** - MISP Project (https://www.misp-project.org/)

---

## 📝 Documentation Standards

This documentation follows these principles:
- **Modular** - Each document covers one topic
- **Navigable** - Clear table of contents and links
- **Practical** - Real examples and commands
- **Current** - Kept up to date with releases
- **Accessible** - Easy to find and understand

### Documentation Structure v2.1

**Recent Improvements (2025-10-25):**
- **Meta-Documentation Suite** - Added 13 comprehensive meta-docs (~10,000 lines)
  - PROJECT_KNOWLEDGE.md - AI context and quick orientation
  - PATTERNS.md - 9 design patterns with examples
  - ARCHITECTURE_DECISIONS.md - 10 ADRs
  - ONBOARDING.md - 30/60/90 day learning path
  - TESTING_GUIDE.md - Testing strategies
  - TROUBLESHOOTING_PLAYBOOK.md - 22 issues documented
  - MISP_QUIRKS.md - 22 platform quirks
  - PRODUCTION_STATE.md - Live instance state
  - NERC_CIP_IMPLEMENTATION_GUIDE.md - 4-phase roadmap
  - Research tracking framework (tracker, review, validation)
- **Production Instance Documentation** - Automated inspection and state tracking
- **Research Management Framework** - 2-week sprint tracking for 3-person team

**Previous Improvements (2024-10-24):**
- Split oversized files for readability (all under 750 lines)
- Reorganized root directory (39 files → 6 essential files)
- Created dedicated NERC CIP compliance area
- Archived historical work for better organization
- Added comprehensive navigation indexes

---

**Last Updated**: 2025-10-25
**Documentation Structure**: v2.1 (Meta-documentation and AI context added)
**Total Documents**: 110+ markdown files organized into logical categories

For the complete project overview, see [../README.md](../README.md)
