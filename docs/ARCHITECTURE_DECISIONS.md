# Architecture Decision Records (ADR)

**Purpose**: Document significant architectural decisions with context, alternatives, and consequences
**Format**: Based on Michael Nygard's ADR template
**Last Updated**: 2025-10-25

This document records all major architectural decisions for the MISP Installation Suite using the Architecture Decision Record format.

---

## Table of Contents

- [ADR-001: Modular Phase System](#adr-001-modular-phase-system)
- [ADR-002: Docker-Based Deployment](#adr-002-docker-based-deployment)
- [ADR-003: Centralized Helper Modules (DRY)](#adr-003-centralized-helper-modules-dry)
- [ADR-004: Feature Exclusion System](#adr-004-feature-exclusion-system)
- [ADR-005: State Management for Resumability](#adr-005-state-management-for-resumability)
- [ADR-006: Structured JSON Logging](#adr-006-structured-json-logging)
- [ADR-007: Dedicated Service User Architecture](#adr-007-dedicated-service-user-architecture)
- [ADR-008: Widget Trait Pattern Over Inheritance](#adr-008-widget-trait-pattern-over-inheritance)
- [ADR-009: Documentation Split Strategy](#adr-009-documentation-split-strategy)
- [ADR-010: Branch Preservation Policy](#adr-010-branch-preservation-policy)
- [ADR Template](#adr-template)

---

## ADR-001: Modular Phase System

**Status**: Accepted

**Date**: 2025-10-01

**Context**

The initial MISP installation was a monolithic script (~3000 lines) that was difficult to maintain, debug, and extend. Any failure required starting from scratch. Adding new features meant modifying a large, complex file.

**Decision**

Split installation into 11 sequential, modular phases. Each phase:
- Is a self-contained Python module
- Inherits from `BasePhase` class
- Has its own state file for persistence
- Can be run independently for testing
- Implements `check_requirements()` and `run()` methods

**Alternatives Considered**

1. **Keep monolithic script**: Simple, but unmaintainable
2. **Ansible playbooks**: More declarative, but adds dependency and learning curve
3. **Bash scripts**: Simpler but harder to test and maintain
4. **Python with functions**: Better than monolithic, but no state management

**Consequences**

**Positive:**
- ✅ Each phase has clear responsibility (Single Responsibility Principle)
- ✅ Easier to debug (isolate failures to specific phase)
- ✅ State management enables resume-after-failure
- ✅ New features can be added as new phases
- ✅ Testable in isolation
- ✅ Self-documenting code structure

**Negative:**
- ❌ More files to manage (11+ phase files)
- ❌ Sequential execution (can't parallelize easily)
- ❌ State file management adds complexity
- ❌ Need to coordinate phase dependencies

**Implementation**

- Created `phases/base_phase.py` abstract base class
- Migrated monolithic script to 11 phase modules
- Implemented state persistence using `lib/state_manager.py`
- Added `misp-install.py` orchestrator to run phases sequentially

**Related Files**:
- `phases/base_phase.py`
- `phases/phase_*.py` (11 modules)
- `lib/state_manager.py`
- `docs/PATTERNS.md` (Phase Pattern)

---

## ADR-002: Docker-Based Deployment

**Status**: Accepted

**Date**: 2025-10-01

**Context**

MISP can be installed directly on the host OS or via Docker. Direct installation has complex dependencies (PHP, MySQL, Redis, multiple services) that vary by OS distribution. Version conflicts and dependency management are challenging.

**Decision**

Use official MISP Docker containers (ghcr.io/misp/misp-docker) for deployment. All MISP components run in containers, managed by Docker Compose.

**Alternatives Considered**

1. **Native installation**: Full control, but complex dependencies
2. **Custom Docker images**: More control, but maintenance burden
3. **Kubernetes**: Overkill for single-instance deployment
4. **VM-based**: Heavy overhead, slower

**Consequences**

**Positive:**
- ✅ Consistent deployment across distributions
- ✅ Upstream MISP team maintains images
- ✅ Isolation from host system
- ✅ Easy backup/restore (container volumes)
- ✅ Simplified dependency management
- ✅ Easy to upgrade (pull new image)

**Negative:**
- ❌ Requires Docker (additional dependency)
- ❌ File operations require `docker exec`
- ❌ Network complexity (container networking)
- ❌ Volume permissions issues (solved in v5.4)

**Implementation**

- Use official `docker-compose.yml` from MISP project
- Create `lib/docker_helpers.py` for container operations
- Implement volume mounting for configuration
- Add Docker health checks

**Related Files**:
- `lib/docker_helpers.py`
- `lib/docker_manager.py`
- `config/docker-compose.yml` (user-provided)

---

## ADR-003: Centralized Helper Modules (DRY)

**Status**: Accepted

**Date**: 2025-10-16 (v5.6 refactoring)

**Context**

Analysis of codebase revealed ~40% code duplication:
- MISP API calls repeated in 20+ scripts
- Docker commands duplicated everywhere
- Identical error handling patterns
- Same logging setup code

Code review identified 25+ occurrences of identical API interaction patterns, making bug fixes require changes in multiple files.

**Decision**

Extract all repeated code into centralized `lib/` helper modules:
- `lib/misp_api_helpers.py` - MISP REST API operations
- `lib/docker_helpers.py` - Docker container management
- `lib/misp_config.py` - MISP configuration file operations
- `lib/state_manager.py` - State persistence
- `lib/features.py` - Feature definitions and exclusion logic
- Additional helpers for specific domains

**Alternatives Considered**

1. **Leave as-is**: Simple, but unmaintainable
2. **Copy-paste with comments**: Doesn't solve duplication
3. **Partial refactoring**: Inconsistent, confusing
4. **External library**: Overhead, not MISP-specific

**Consequences**

**Positive:**
- ✅ DRY (Don't Repeat Yourself) principle applied
- ✅ Bug fixes in one place propagate everywhere
- ✅ Consistent error handling
- ✅ Easier to test (isolated functions)
- ✅ Reduced codebase by ~40%
- ✅ Self-documenting through docstrings
- ✅ Easier onboarding (patterns clear)

**Negative:**
- ❌ Abstraction layer to understand
- ❌ Import overhead (minimal)
- ❌ Need to maintain backwards compatibility
- ❌ Can become "junk drawer" if not organized

**Implementation**

- Created `lib/` directory structure
- Extracted common patterns from 20+ scripts
- Updated all scripts to import from `lib/`
- Added comprehensive docstrings
- Wrote unit tests for critical functions

**Metrics**:
- Lines of code reduced from ~15,000 to ~9,000 (~40%)
- Helper modules: 15 files
- Functions centralized: 50+

**Related Files**:
- `lib/misp_api_helpers.py`
- `lib/docker_helpers.py`
- `lib/misp_config.py`
- `lib/state_manager.py`
- `docs/PATTERNS.md` (Centralized Helper Pattern)

---

## ADR-004: Feature Exclusion System

**Status**: Accepted

**Date**: 2025-10-16 (v5.6)

**Context**

Different users have different needs:
- Small utilities don't need all threat intel feeds
- Some orgs prohibit cloud integrations
- Non-compliance users don't need NERC CIP features
- Minimal installations should be fast

Installation time with all features: ~45 minutes. Many features optional but always installed.

**Decision**

Implement feature exclusion system allowing users to exclude:
- Individual features by ID
- Entire categories of features
- Via simple configuration file

**Alternatives Considered**

1. **Separate installation tracks**: Rigid, hard to maintain
2. **Command-line flags**: Too many flags, complex
3. **Interactive prompts**: Not automation-friendly
4. **Multiple installer versions**: Maintenance nightmare

**Consequences**

**Positive:**
- ✅ User control over installation
- ✅ Reduced installation time (can be <10 min)
- ✅ Minimized attack surface
- ✅ Industry-specific customization
- ✅ Easy to extend with new features
- ✅ Configuration-based (no code changes)

**Negative:**
- ❌ Testing complexity (many combinations)
- ❌ Need to handle missing dependencies
- ❌ Documentation overhead
- ❌ Users might exclude too much

**Implementation**

- Created `lib/features.py` with feature registry
- Extended `lib/config.py` to parse exclusions
- Added `config/exclusions.conf` format
- Implemented exclusion checks in all phases
- Created 4 example configurations

**Feature Categories**:
- `category:threat_intel` - Threat intelligence features
- `category:automation` - Automated maintenance
- `category:integrations` - Third-party integrations
- `category:compliance` - NERC CIP compliance features

**Related Files**:
- `lib/features.py`
- `lib/config.py`
- `config/exclusions.conf` (template)
- `config/examples/*.conf` (4 examples)
- `docs/development/EXCLUSION_LIST_DESIGN.md`

---

## ADR-005: State Management for Resumability

**Status**: Accepted

**Date**: 2025-10-01

**Context**

Installation can fail for many reasons:
- Network interruptions
- Docker issues
- MISP API timeouts
- System resource exhaustion

Without state management, users must start from scratch after any failure, repeating completed steps.

**Decision**

Implement JSON-based state persistence:
- Each phase maintains state file in `state/` directory
- State includes completed steps and results
- Atomic writes (temp file + rename)
- Phases check state before running steps

**Alternatives Considered**

1. **No state management**: Simple, but poor UX
2. **Database**: Overkill, adds dependency
3. **SQLite**: Better than full DB, still overhead
4. **YAML state files**: JSON simpler and built-in to Python

**Consequences**

**Positive:**
- ✅ Resume after failure without repeating work
- ✅ Progress tracking
- ✅ Audit trail of what happened
- ✅ Debugging aid (see what completed)
- ✅ No additional dependencies (JSON built-in)

**Negative:**
- ❌ State file management complexity
- ❌ JSON serialization limitations
- ❌ Need to clean up old state files
- ❌ State can become stale

**Implementation**

- Created `lib/state_manager.py` with atomic writes
- Each phase saves state after major steps
- State format standardized across phases
- Added state inspection tools

**State File Format**:
```json
{
    "status": "completed|in_progress|failed|skipped",
    "completed_steps": ["step1", "step2"],
    "last_step": "step2",
    "timestamp": "2025-10-25T12:34:56",
    "results": {},
    "error": null
}
```

**Related Files**:
- `lib/state_manager.py`
- `state/*.json` (generated at runtime)
- `docs/PATTERNS.md` (State Manager Pattern)

---

## ADR-006: Structured JSON Logging

**Status**: Accepted

**Date**: 2025-10-13 (v5.4)

**Context**

Logs were inconsistent:
- Each script had different format
- Hard to parse for SIEM systems
- No structured data
- Difficult to search/filter
- No log rotation (files growing unbounded)

Electric utilities need SIEM integration for compliance (CIP-007 R4 requires 90-day log retention).

**Decision**

Implement centralized JSON logging:
- All components use `lib/misp_logger.py`
- JSON format for structured data
- Automatic log rotation (5 files × 20MB)
- Sourcetype categorization
- Extra fields for rich context

**Alternatives Considered**

1. **Plain text logs**: Simple, but unparseable
2. **Syslog**: Standard, but adds dependency
3. **CEF format**: Industry standard, but complex
4. **Custom binary format**: Efficient, but non-standard

**Consequences**

**Positive:**
- ✅ Structured logs (parseable by SIEM)
- ✅ Consistent format everywhere
- ✅ Rich context (extra fields)
- ✅ Automatic rotation
- ✅ Categorization via sourcetype
- ✅ NERC CIP compliance ready

**Negative:**
- ❌ JSON overhead (slightly larger)
- ❌ Less human-readable
- ❌ Requires JSON parser for viewing

**Implementation**

- Created `lib/misp_logger.py` with rotating file handler
- All scripts updated to use centralized logger
- Documented in `docs/README_LOGGING.md`
- SIEM forwarding configuration provided

**Log Format Example**:
```json
{
    "timestamp": "2025-10-25T12:34:56.789Z",
    "level": "INFO",
    "logger": "phase_11_8",
    "sourcetype": "misp:phase",
    "message": "Phase 11.8 completed",
    "phase_number": "11.8"
}
```

**Related Files**:
- `lib/misp_logger.py`
- `docs/README_LOGGING.md`
- `logs/` (generated at runtime)

---

## ADR-007: Dedicated Service User Architecture

**Status**: Accepted

**Date**: 2025-10-13 (v5.4)

**Context**

Initial implementation ran everything as root user:
- Security risk (unnecessary privileges)
- File ownership issues
- Docker volume permission problems
- Failed NERC CIP audit requirements (CIP-005 R2.1)

NERC CIP compliance requires principle of least privilege.

**Decision**

Create dedicated `misp-admin` user for all operations:
- Non-root user with sudo only for specific commands
- Sudoers configuration for required operations
- Proper file ownership and permissions
- Docker group membership for container access

**Alternatives Considered**

1. **Continue as root**: Simple, but insecure
2. **Multiple users**: Complex permission management
3. **Service accounts per component**: Overkill
4. **Container-only isolation**: Doesn't solve host-level issues

**Consequences**

**Positive:**
- ✅ Principle of least privilege
- ✅ Better security posture
- ✅ NERC CIP compliance (CIP-005 R2.1)
- ✅ Clear ownership model
- ✅ Easier permission debugging

**Negative:**
- ❌ Sudoers configuration complexity
- ❌ Permission issues during migration
- ❌ Need to handle both root and user scenarios
- ❌ Testing complexity (test as both users)

**Implementation**

- Created `misp-admin` user during installation
- Configured sudoers for specific operations
- Fixed file ownership issues (ACL masks)
- Updated all scripts to use proper user
- Documented in `SETUP.md`

**Sudoers Configuration**:
```bash
misp-admin ALL=(ALL) NOPASSWD: /usr/bin/docker
misp-admin ALL=(ALL) NOPASSWD: /usr/local/bin/docker-compose
misp-admin ALL=(ALL) NOPASSWD: /bin/systemctl
```

**Related Files**:
- `SETUP.md`
- `docs/historical/fixes/ACL-FIX-SUMMARY.md`

---

## ADR-008: Widget Trait Pattern Over Inheritance

**Status**: Accepted

**Date**: 2025-10-17 (v5.6 dashboard development)

**Context**

Developing 25 custom widgets with shared functionality (permission checks, data formatting). Natural inclination: create abstract base class.

**Problem Discovered**: MISP's dashboard loader (`Dashboard::loadAllWidgets()`) scans `Custom/` directory and attempts to instantiate every `.php` file, including abstract classes, causing fatal error.

**Decision**

Use PHP traits instead of abstract base classes for code reuse:
- Traits provide shared functionality
- No instantiation issue (traits can't be instantiated)
- Consistent patterns across widgets
- MISP dashboard loader happy

**Alternatives Considered**

1. **Abstract base class**: Clean OOP, but breaks MISP
2. **Copy-paste code**: Works, but not DRY
3. **Include files**: Messy, global namespace pollution
4. **Separate helper class**: Extra file operations, less clean

**Consequences**

**Positive:**
- ✅ Code reuse across 25 widgets
- ✅ No MISP instantiation bug
- ✅ Clean, maintainable code
- ✅ Traits can be tested independently

**Negative:**
- ❌ Traits don't enforce interface
- ❌ Less explicit than inheritance
- ❌ PHP trait limitations

**Implementation**

- Created `WidgetHelpers` trait with common methods
- All 25 widgets use trait
- Documented pattern in `docs/PATTERNS.md`
- Added to widget development guide

**Example**:
```php
trait WidgetHelpers {
    protected function checkPermissions($user) { ... }
    protected function formatTags($event) { ... }
}

class MyWidget {
    use WidgetHelpers;
    // Widget implementation
}
```

**Related Files**:
- `widgets/utilities-sector/*.php` (25 widgets)
- `docs/PATTERNS.md` (Widget Base Class Pattern)
- `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md`

---

## ADR-009: Documentation Split Strategy

**Status**: Accepted

**Date**: 2025-10-24 (PR #13)

**Context**

Two documentation files exceeded AI reading limits:
- `RESEARCH_TASKS_PERSON_3.md`: 2,768 lines (138% of 2000 line limit)
- `NERC_CIP_MEDIUM_ARCHITECTURE.md`: 2,135 lines (107% of limit)

This prevented AI assistants from reading complete files, reducing effectiveness. Human readers also struggled with large files. Root directory cluttered with 37 markdown files.

**Decision**

Comprehensive documentation reorganization:
1. Split oversized files at logical boundaries (<750 lines each)
2. Create topic-based directory structure
3. Move historical work to `docs/historical/`
4. Create navigation index files
5. Validate all internal links

**Alternatives Considered**

1. **Leave as-is**: Simple, but limits AI assistance
2. **Summary files only**: Loses detail
3. **External wiki**: Adds complexity, loses git history
4. **Multiple repositories**: Splits context

**Consequences**

**Positive:**
- ✅ All files under 750 lines (well under 2000 limit)
- ✅ AI assistants can read everything
- ✅ Easier human navigation
- ✅ Clean root directory (6 essential files)
- ✅ Logical organization
- ✅ Comprehensive navigation hubs
- ✅ All links validated (199 links, 0 broken)

**Negative:**
- ❌ More files to manage (60+ docs)
- ❌ Risk of broken cross-references (mitigated with validation)
- ❌ Need to update navigation when adding docs

**Implementation**

- Phase 1: Split 2 files into 14 files
- Phase 2: Reorganized 60+ files into directories
- Phase 3: Created navigation indexes
- Phase 4: Updated cross-references
- Phase 5: Validated all links

**Metrics**:
- Files before: 37 in root
- Files after: 6 in root, 60+ organized
- Largest file before: 2,768 lines
- Largest file after: 707 lines
- Broken links: 0

**Related Files**:
- `docs/README.md` - Main navigation hub
- `docs/nerc-cip/README.md` - NERC CIP hub
- `docs/PROJECT_KNOWLEDGE.md` - Project knowledge base

---

## ADR-010: Branch Preservation Policy

**Status**: Accepted

**Date**: 2025-10-25

**Context**

Development branches contain valuable implementation patterns, problem-solving approaches, and historical context. Traditional practice: delete branches after merge.

**Problem**: Losing:
- Learning resources (how problems were solved)
- Reference implementations (what was tried)
- Historical context (why decisions made)
- Troubleshooting aids (similar issues in future)

**Decision**

Preserve selected development branches indefinitely:
- Document purpose and learnings in `BRANCHES.md`
- Keep branches with unique implementation value
- Quarterly review of branch value
- Clear criteria for keeping vs. deleting

**Alternatives Considered**

1. **Delete all merged branches**: Clean, but loses context
2. **Keep all branches**: Cluttered, hard to navigate
3. **Archive to separate repo**: Splits context
4. **Tag-only preservation**: Loses branch context

**Consequences**

**Positive:**
- ✅ Preserved implementation patterns
- ✅ Learning resource for team
- ✅ Troubleshooting reference
- ✅ Historical context available
- ✅ Onboarding aid

**Negative:**
- ❌ More branches in repo
- ❌ Need to document each branch
- ❌ Quarterly review overhead
- ❌ Potential confusion (which branch is active?)

**Implementation**

- Created `BRANCHES.md` inventory
- Documented 5 preserved branches
- Established keep/delete criteria
- Scheduled quarterly reviews (next: 2026-01-25)

**Keep Criteria**:
- Unique implementation patterns
- Learning value for team
- Troubleshooting reference value
- Historical decision context

**Delete Criteria**:
- Fully merged, no unique commits
- No reference value
- >6 months inactive with no value
- Superseded by better implementation

**Related Files**:
- `BRANCHES.md` - Branch inventory and documentation

---

## ADR Template

Use this template for future architectural decisions:

```markdown
## ADR-XXX: Decision Title

**Status**: Proposed | Accepted | Deprecated | Superseded

**Date**: YYYY-MM-DD

**Context**

What is the issue we're seeing that is motivating this decision or change?
What are the forces at play?
What are the goals and constraints?

**Decision**

What is the change we're proposing and/or doing?
Be specific and concrete.

**Alternatives Considered**

1. **Alternative 1**: Description
   - Pros: ...
   - Cons: ...

2. **Alternative 2**: Description
   - Pros: ...
   - Cons: ...

**Consequences**

What becomes easier or more difficult to do because of this change?

**Positive:**
- ✅ Benefit 1
- ✅ Benefit 2

**Negative:**
- ❌ Drawback 1
- ❌ Drawback 2

**Implementation**

- How was this implemented?
- What files changed?
- Any metrics to support the decision?

**Related Files**:
- `path/to/file.py`
- `docs/TOPIC.md`
```

---

## Adding New ADRs

**When to Create an ADR**:
- Significant architectural or design decision
- Affects multiple components or teams
- Hard to reverse (one-way door)
- Alternatives need to be documented
- Future "why did we do this?" question

**When NOT to Create an ADR**:
- Minor bug fixes
- Code style choices
- Obvious decisions with no alternatives
- Temporary/experimental changes

**Process**:
1. Copy ADR template above
2. Number sequentially (ADR-011, ADR-012, etc.)
3. Fill in all sections thoroughly
4. Add to Table of Contents
5. Get team review
6. Merge to main branch

---

**Maintained by**: tKQB Enterprises
**Format**: Architecture Decision Records (Michael Nygard format)
**Version**: 1.0
**Last Updated**: 2025-10-25
