# Project Knowledge Base - Meta Documentation

**Purpose**: Help Claude Code (and new team members) quickly understand the codebase structure, patterns, and context
**Last Updated**: 2025-10-25
**Version**: 1.0

This document provides high-level context that helps AI assistants and developers quickly orient to the project.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Key Concepts & Patterns](#key-concepts--patterns)
4. [Historical Context](#historical-context)
5. [Common Workflows](#common-workflows)
6. [Important Relationships](#important-relationships)
7. [Decision Log](#decision-log)
8. [Quick Reference](#quick-reference)

---

## Project Overview

### What This Is
**MISP Installation Suite for Electric Utilities**
- Automated MISP (Malware Information Sharing Platform) deployment
- Specialized for electric utility sector (NERC CIP compliance)
- ICS/SCADA/OT threat intelligence focus
- Complete installation, configuration, and customization automation

### Current State
- **Version**: 5.6
- **Status**: Production-ready
- **Compliance**: 35% → targeting 95-100% NERC CIP Medium Impact
- **Key Features**: 14 advanced features, 25 custom dashboards, automated maintenance

### Primary Use Cases
1. **Electric utilities** needing NERC CIP compliance
2. **ICS/OT security teams** tracking industrial threats
3. **Security analysts** in critical infrastructure sectors
4. **NERC auditors** requiring compliance evidence

---

## Codebase Architecture

### High-Level Structure

```
misp-install/
├── misp-install.py          # Main installer (orchestrates phases)
├── phases/                   # 11 installation phases (modular)
├── scripts/                  # Standalone utility scripts (100+)
├── lib/                      # Centralized helper modules (DRY)
├── widgets/                  # Custom MISP dashboard widgets (25)
├── config/                   # Configuration files & examples
├── docs/                     # Documentation (100+ files, organized)
│   ├── nerc-cip/            # NERC CIP compliance documentation
│   ├── integrations/        # Third-party integrations
│   ├── development/         # Development guides
│   ├── historical/          # Archived work (fixes, implementations)
│   └── releases/            # Release notes
├── deprecated/              # Old files (retention schedule)
├── tests/                   # Test suites
└── README.md                # Main project documentation
```

### Key Architecture Principles

**1. Modular Phases**: Installation broken into 11 sequential phases
- Each phase is self-contained and state-managed
- Phases can be excluded via feature flags
- State persistence allows resume after failure

**2. DRY (Don't Repeat Yourself)**: Centralized helper modules
- `lib/misp_api_helpers.py` - MISP REST API operations
- `lib/docker_helpers.py` - Docker container management
- `lib/state_manager.py` - Installation state tracking
- `lib/config.py` - Configuration management
- `lib/features.py` - Feature flag system

**3. Feature Exclusion System**: Granular control over installation
- Category-based exclusions: `category:threat_intel`
- Feature-based exclusions: `feature:azure-ad`
- Configuration via `config/exclusions.conf`
- See: `docs/development/EXCLUSION_LIST_DESIGN.md`

**4. Centralized Logging**: Structured JSON logging
- All scripts use `lib/misp_logger.py`
- Automatic log rotation (5 files × 20MB)
- Consistent format across all components
- See: `docs/README_LOGGING.md`

---

## Key Concepts & Patterns

### 1. Phase System

**Concept**: Installation split into logical phases that can run independently

**Pattern**:
```python
from phases.base_phase import BasePhase

class Phase_X_Y_Description(BasePhase):
    def __init__(self):
        super().__init__(
            phase_number="X.Y",
            phase_name="Description",
            state_file="phase_X_Y_description.json"
        )

    def check_requirements(self):
        # Pre-flight checks
        pass

    def run(self):
        # Feature exclusion check
        if self.config.is_feature_excluded('feature-id'):
            self.logger.info("Feature excluded, skipping")
            return

        # Main implementation
        pass
```

**Location**: `phases/phase_*.py`

### 2. Feature Exclusion

**Concept**: Users can selectively exclude features/categories they don't need

**Pattern**:
```python
from lib.config import Config

config = Config()

# Check single feature
if config.is_feature_excluded('azure-ad'):
    print("Azure AD integration excluded")

# Check category
if config.is_feature_excluded('category:threat_intel'):
    print("All threat intel features excluded")

# Get list of excluded features
excluded = config.get_excluded_features()
```

**Configuration**:
```ini
# config/exclusions.conf
[exclusions]
# Exclude entire categories
category:threat_intel
category:compliance

# Exclude specific features
azure-ad
nerc-cip-dashboards
```

**Location**: `lib/features.py`, `lib/config.py`

### 3. MISP API Interaction

**Concept**: Centralized MISP REST API operations with error handling

**Pattern**:
```python
from lib.misp_api_helpers import (
    get_api_key,
    get_misp_url,
    misp_rest_search,
    misp_add_event,
    misp_enable_feed
)

api_key = get_api_key()
misp_url = get_misp_url()

# Search for events
events = misp_rest_search(
    api_key=api_key,
    filters={"tags": ["ics:%"], "published": 1, "last": "7d"}
)

# Add event
event_data = {"Event": {"info": "...", "threat_level_id": 2}}
result = misp_add_event(api_key, event_data)
```

**Location**: `lib/misp_api_helpers.py`

### 4. State Management

**Concept**: Track installation progress, allow resume after failure

**Pattern**:
```python
from lib.state_manager import StateManager

state = StateManager('my_phase.json')

# Save state
state.save({
    'completed_steps': ['step1', 'step2'],
    'current_step': 'step3',
    'timestamp': datetime.now().isoformat()
})

# Load state
previous_state = state.load()
if previous_state:
    print(f"Resuming from {previous_state['current_step']}")
```

**Location**: `lib/state_manager.py`

### 5. Widget Development

**Concept**: Custom MISP dashboard widgets for utilities sector

**Pattern**:
```php
// widgets/utilities-sector/MyWidget.php
class MyWidget
{
    public $title = 'Widget Title';
    public $render = 'SimpleList';
    public $width = 3;
    public $height = 4;

    public function handler($user, $options = array())
    {
        // Permission check
        if (!$this->checkPermissions($user)) {
            return array();
        }

        // Fetch data from MISP
        $Event = ClassRegistry::init('Event');
        $eventIds = $Event->fetchEventIds($user, array(
            'tags' => array('ics:%'),  // Wildcard matching
            'published' => 1,
            'last' => '7d'
        ));

        // Process and return
        return $this->formatDataForWidget($eventIds);
    }
}
```

**Critical Widget Patterns**:
- Use `'ics:%'` not `'ics:'` for tag wildcards (MISP quirk)
- Always check permissions with `checkPermissions($user)`
- No abstract classes in Custom directory (MISP loads all .php files)
- Handle both `$event['Tag']` and `$event['EventTag']` structures

**Location**: `widgets/*/`, `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md`

---

## Historical Context

### Major Milestones

**v5.0 (2025-10-01)**: Initial release
- Basic MISP installation automation
- 11-phase installation system
- Docker-based deployment

**v5.4 (2025-10-13)**: Dedicated user architecture
- Changed from root to misp-admin user
- ACL permission fixes
- Improved security posture

**v5.5 (2025-10-14)**: Feed management
- Automated feed configuration
- ICS-CERT and E-ISAC integration
- Vendor security bulletins

**v5.6 (2025-10-16)**: Advanced features
- 25 custom utilities sector widgets
- NERC CIP compliance documentation
- DRY refactoring (centralized helpers)
- Feature exclusion system

**Current (2025-10-25)**: Documentation reorganization
- Split oversized files (2,768 and 2,135 lines → 14 files)
- Comprehensive navigation indexes
- Historical work archival
- Production-ready structure

### Evolution of Patterns

**Early Approach** (v5.0-5.3):
- Monolithic installation script
- Direct Docker commands everywhere
- Repeated code patterns
- No state management

**Refactoring** (v5.4-5.5):
- Modular phase system
- Centralized Docker helpers
- State management added
- Logging standardized

**Current Approach** (v5.6+):
- Full DRY implementation
- Feature exclusion system
- Comprehensive error handling
- Production-grade architecture

---

## Common Workflows

### 1. Adding a New Feature

```bash
# 1. Choose feature category and ID
#    See lib/features.py for existing features

# 2. Create phase or script
#    phases/phase_X_Y_feature_name.py
#    scripts/configure-feature-name.py

# 3. Add feature to lib/features.py
FEATURE_DESCRIPTIONS = {
    'my-feature': 'Description of my feature'
}

FEATURE_CATEGORIES = {
    'my-feature': 'category:automation'  # or create new category
}

# 4. Implement exclusion check
if self.config.is_feature_excluded('my-feature'):
    self.logger.info("Feature excluded")
    return

# 5. Add example exclusion to config/examples/
#    config/examples/no-automation.conf

# 6. Update documentation
#    docs/development/EXCLUSION_LIST_DESIGN.md
#    SCRIPTS.md (if standalone script)
#    TODO.md (remove from todo list)
```

### 2. Creating a Custom Widget

```bash
# 1. Create widget PHP file
#    widgets/category-name/MyWidget.php

# 2. Follow widget pattern (see Key Concepts #5)

# 3. Add installation script
#    scripts/install-my-widget.py

# 4. Add to phase or make standalone
#    Either: add to phase_11_11_utilities_dashboards.py
#    Or: create new phase for widget category

# 5. Test widget installation
sudo python3 scripts/install-my-widget.py

# 6. Verify in MISP
#    Dashboard → Add Widget → Find your widget

# 7. Document
#    widgets/category-name/README.md
```

### 3. Adding NERC CIP Compliance Feature

```bash
# 1. Determine CIP standard(s) addressed
#    See docs/nerc-cip/README.md for coverage

# 2. Check if research completed
#    docs/nerc-cip/research/person-*/

# 3. Implement according to architecture
#    docs/nerc-cip/architecture/

# 4. Add to production readiness checklist
#    docs/nerc-cip/PRODUCTION_READINESS_TASKS.md

# 5. Update compliance percentage
#    docs/nerc-cip/README.md (Quick Status table)
#    docs/nerc-cip/AUDIT_REPORT.md (findings)

# 6. Add to audit evidence collection
#    Logging, screenshots, configuration exports
```

### 4. Debugging Installation Issues

```bash
# 1. Check logs
tail -f logs/misp_installer.log

# 2. Check phase state
cat state/phase_X_Y_name.json

# 3. Check Docker containers
sudo docker ps -a
sudo docker logs misp-misp-core-1

# 4. Check MISP logs
sudo docker exec misp-misp-core-1 \
  tail -f /var/www/MISP/app/tmp/logs/error.log

# 5. Verify MISP API
curl -k -H "Authorization: $(cat /home/misp-admin/.misp/apikey)" \
  https://localhost/users/view/me.json

# 6. Check feature exclusions
python3 -c "from lib.config import Config; print(Config().get_excluded_features())"

# 7. Review phase requirements
#    Read phase_X_Y_name.py check_requirements() method
```

---

## Important Relationships

### Component Dependencies

```
misp-install.py (orchestrator)
    ├── phases/ (11 phases, sequential)
    │   ├── lib/ (helpers, imported by phases)
    │   └── state/ (phase state files)
    ├── config/ (configuration, read by phases)
    └── scripts/ (can be called by phases or standalone)

widgets/ (independent, installed by phases or scripts)
    └── installed to: /var/www/MISP/app/Lib/Dashboard/Custom/

docs/ (documentation, no code dependencies)
    ├── nerc-cip/ (compliance documentation)
    └── historical/ (archived work)
```

### Data Flow

```
1. User runs installer
   └→ misp-install.py

2. Reads configuration
   └→ config/exclusions.conf
   └→ config/misp-config.yaml

3. Executes phases sequentially
   └→ phases/phase_*.py
   └→ Uses: lib/ helpers
   └→ Saves: state/*.json

4. Phases may call scripts
   └→ scripts/*.py
   └→ Also uses: lib/ helpers

5. Installation complete
   └→ MISP configured and running
   └→ Widgets installed
   └→ Feeds enabled
   └→ Dashboards configured
```

### File Location Patterns

| Type | Location | Example |
|------|----------|---------|
| Phase modules | `phases/phase_X_Y_name.py` | `phases/phase_11_11_utilities_dashboards.py` |
| Standalone scripts | `scripts/action-target.py` | `scripts/configure-nerc-cip-feeds.py` |
| Helper modules | `lib/module_name.py` | `lib/misp_api_helpers.py` |
| State files | `state/phase_X_Y_name.json` | `state/phase_11_8_utilities_intel.json` |
| Widget PHP | `widgets/category/WidgetName.php` | `widgets/utilities-sector/ICSVulnerabilityFeedWidget.php` |
| Config examples | `config/examples/use-case.conf` | `config/examples/minimal-install.conf` |
| Documentation | `docs/TOPIC.md` | `docs/INSTALLATION.md` |
| NERC CIP docs | `docs/nerc-cip/` | `docs/nerc-cip/AUDIT_REPORT.md` |
| Historical docs | `docs/historical/category/` | `docs/historical/fixes/WIDGET_FIXES_COMPLETE.md` |

---

## Decision Log

Important architectural and design decisions documented for context.

### Decision 1: Modular Phase System (v5.0)
**Date**: 2025-10-01
**Decision**: Split installation into 11 sequential phases instead of monolithic script
**Rationale**:
- Easier to maintain and debug
- State management allows resume after failure
- Selective execution possible
- Better code organization
**Impact**: Foundation for all future development

### Decision 2: Centralized Helper Modules (v5.6)
**Date**: 2025-10-16
**Decision**: Extract repeated code into `lib/` modules
**Rationale**:
- DRY principle (Don't Repeat Yourself)
- Easier to update and maintain
- Consistent error handling
- Testable in isolation
**Impact**: Reduced codebase by ~40%, improved reliability

### Decision 3: Feature Exclusion System (v5.6)
**Date**: 2025-10-16
**Decision**: Allow users to exclude features/categories they don't need
**Rationale**:
- Not all users need all features
- Reduces installation time
- Minimizes attack surface
- Industry-specific customization
**Impact**: Flexible installation, better user control

### Decision 4: Documentation Reorganization (v5.6)
**Date**: 2025-10-24
**Decision**: Split oversized files, reorganize into topic-based directories
**Rationale**:
- Files >2000 lines exceeded AI reading limits
- Hard to navigate for humans
- No clear organization
- Cluttered root directory
**Impact**: All files <750 lines, clear navigation, production-ready docs

### Decision 5: Keep Research Branches
**Date**: 2025-10-25
**Decision**: Preserve development branches for learning and troubleshooting
**Rationale**:
- Historical context valuable
- Reference implementations
- Troubleshooting aid
- Learning resource
**Impact**: Better knowledge preservation, easier onboarding

---

## Quick Reference

### Critical Files (Read These First)

1. **CLAUDE.md** - Instructions for Claude Code (you're reading related content now!)
2. **README.md** - Project overview and features
3. **docs/README.md** - Documentation hub with navigation
4. **docs/nerc-cip/README.md** - NERC CIP compliance documentation hub
5. **BRANCHES.md** - Branch inventory and purpose
6. **TODO.md** - Current development priorities

### Key Directories

| Directory | Purpose | File Count |
|-----------|---------|------------|
| `phases/` | Installation phases | 20+ files |
| `scripts/` | Standalone utilities | 100+ scripts |
| `lib/` | Helper modules | 15+ modules |
| `widgets/` | Dashboard widgets | 25+ widgets |
| `docs/` | Documentation | 100+ files |
| `docs/nerc-cip/` | Compliance docs | 30+ files |
| `config/examples/` | Config templates | 4 examples |

### Common Commands

```bash
# Run full installation
sudo python3 misp-install.py

# Run with exclusions
sudo python3 misp-install.py --config config/examples/minimal-install.conf

# List available features
python3 misp-install.py --list-features

# Run single phase
sudo python3 phases/phase_X_Y_name.py

# Check logs
tail -f logs/misp_installer.log

# Verify MISP running
sudo docker ps | grep misp

# Check MISP API
curl -k -H "Authorization: $(cat ~/.misp/apikey)" \
  https://localhost/users/view/me.json
```

### Environment Variables

```bash
# MISP API access (set by installer)
~/.misp/apikey          # API key
~/.misp/url             # MISP URL (https://localhost)

# Installation directories
/home/misp-admin/       # Installation user home
/var/www/MISP/          # MISP Docker mount
```

### Troubleshooting Checklist

- [ ] Check logs: `logs/misp_installer.log`
- [ ] Check phase state: `state/*.json`
- [ ] Verify Docker: `sudo docker ps -a`
- [ ] Check MISP logs: `sudo docker exec misp-misp-core-1 tail -f /var/www/MISP/app/tmp/logs/error.log`
- [ ] Verify API key: `cat ~/.misp/apikey`
- [ ] Test API: `curl -k -H "Authorization: $(cat ~/.misp/apikey)" https://localhost/users/view/me.json`
- [ ] Check exclusions: `cat config/exclusions.conf`
- [ ] Review requirements: Check phase's `check_requirements()` method

---

## For Claude Code: Context Resumption Guide

When resuming work on this project in a new session, read these files in order:

### Session Startup Checklist

1. **CLAUDE.md** - Current project instructions and state
2. **This file** (PROJECT_KNOWLEDGE.md) - Architecture and patterns
3. **BRANCHES.md** - Branch inventory and purposes
4. **TODO.md** - Current priorities and active work
5. **docs/nerc-cip/README.md** - Compliance project status (if NERC work)
6. **Recent git commits** - `git log --oneline -20`

### Quick Context Questions

Answer these to orient quickly:

- What version are we on? → Check `TODO.md` or `CLAUDE.md`
- What's the current focus? → Check `TODO.md` "High Priority" section
- What branch are we on? → Run `git branch`
- Any pending research? → Check `docs/nerc-cip/README.md` for team status
- What was last worked on? → Check `git log -5 --oneline`
- Any open PRs? → Run `gh pr list`

### Common Session Patterns

**Pattern 1: Feature Development**
→ Check `TODO.md` → Read `lib/features.py` → Review phase examples → Implement

**Pattern 2: Documentation Work**
→ Check `docs/README.md` → Review file sizes → Check link validity → Update

**Pattern 3: NERC CIP Compliance**
→ Check `docs/nerc-cip/README.md` → Review research progress → Check architecture → Implement

**Pattern 4: Troubleshooting**
→ Read logs → Check state files → Review phase code → Check Docker → Fix issue

---

## Meta: Improving This Document

### What to Add When:

**New Pattern Discovered**:
→ Add to "Key Concepts & Patterns" with example code

**Major Decision Made**:
→ Add to "Decision Log" with date, rationale, impact

**New Workflow Established**:
→ Add to "Common Workflows" with step-by-step guide

**Architecture Changed**:
→ Update "Codebase Architecture" and component diagrams

**Historical Milestone**:
→ Add to "Historical Context" with version and changes

### Template for Adding Patterns

```markdown
### N. Pattern Name

**Concept**: Brief description of what this pattern does

**Pattern**:
\```language
# Example code showing the pattern
\```

**Location**: Where to find examples in codebase

**Common Use Cases**:
- Use case 1
- Use case 2

**Gotchas**:
- Common mistake 1
- Edge case to watch for
```

---

**Maintained by**: tKQB Enterprises
**For**: Claude Code, AI assistants, new developers
**Update Frequency**: After major architectural changes or new patterns emerge
**Last Major Update**: 2025-10-25 (v1.0 - Initial creation)
