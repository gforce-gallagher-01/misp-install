# Branch Inventory

**Last Updated**: 2025-10-25
**Purpose**: Track development branches for research, learning, and troubleshooting

This document catalogs all active branches in the repository, their purpose, and why they're being preserved.

---

## Active Development Branches

### `main`
**Status**: Primary production branch
**Latest**: c5f28e6 - Merge pull request #14 (final cleanup)
**Purpose**: Stable, production-ready code
**Merge Strategy**: Only accept PRs after review and testing

### `develop`
**Status**: Active development branch
**Latest**: 204173e - Add comprehensive NERC CIP Medium Impact compliance documentation
**Purpose**: Integration branch for ongoing development
**Merge Strategy**: Feature branches merge here first, then PR to main

---

## Research & Learning Branches

These branches are preserved for reference, learning, and troubleshooting. They contain valuable implementation patterns and historical context.

### `feature/utilities-dashboards-25-widgets`
**Status**: Preserved for reference
**Latest**: 7fd7030 - refactor: implement DRY principles with centralized helper modules
**Created**: ~2025-10-16
**Merged**: Yes (via PR #8 and #9)

**Purpose**: Complete utilities sector dashboard implementation

**Key Learnings**:
- 25 custom MISP widgets for ICS/SCADA threat intelligence
- DRY refactoring with base classes
- MISP dashboard widget architecture
- Fix for abstract class instantiation issues
- Tag wildcard matching patterns (`ics:` → `ics:%`)

**Why Preserved**:
- Reference for widget development patterns
- Troubleshooting template for future dashboard work
- Example of DRY principles in PHP widget code
- Documents MISP dashboard API quirks and solutions

**Reference Documentation**:
- `widgets/utilities-sector/README.md`
- `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md`
- `docs/historical/implementations/DRY_REFACTORING_SUMMARY.md`

---

### `merge-nerc-cip-and-feeds`
**Status**: Preserved for reference
**Latest**: 917e9c5 - docs: Add comprehensive merge verification report
**Created**: 2025-10-24
**Merged**: Yes (via PR #12)

**Purpose**: Clean merge of NERC CIP docs and feed management work

**Key Learnings**:
- Git merge conflict resolution patterns
- Verification procedures for complex merges
- Documentation consolidation strategies
- Branch synchronization techniques

**Why Preserved**:
- Template for future complex merges
- Documents merge verification procedures
- Reference for clean git history maintenance
- Example of documentation-heavy merge

**Reference Documentation**:
- `docs/historical/merges/MERGE_VERIFICATION_REPORT.md`

---

### `nerc-cip-docs`
**Status**: Preserved for reference (49 commits behind main)
**Latest**: 70ba1c9 - Week 1 Complete: Feed Management, Communities Integration, and Code Quality Fixes (#11)
**Created**: Early October 2025

**Purpose**: Initial NERC CIP compliance documentation development

**Key Learnings**:
- NERC CIP Medium Impact requirements research
- Compliance documentation structure
- Multi-person research task breakdown
- Architecture documentation patterns

**Why Preserved**:
- Historical context for NERC CIP work
- Original research and planning documents
- Evolution of compliance approach
- Reference for future compliance projects

**Reference Documentation**:
- `docs/nerc-cip/` (entire directory structure)
- Research documents for 3-person team

**Note**: This branch predates the documentation reorganization (PR #13), so file locations differ from main

---

### `refactor/fix-systemrequirements-duplication`
**Status**: Preserved for reference
**Latest**: 80b42a9 - refactor: eliminate SystemRequirements duplication (DRY principle)
**Created**: ~October 2025
**Merged**: Partially (needs verification)

**Purpose**: Eliminate code duplication in system requirements checking

**Key Learnings**:
- DRY principle implementation
- Python code refactoring patterns
- System requirements validation architecture
- Centralized validation approach

**Why Preserved**:
- Template for future refactoring work
- Documents DRY transformation process
- Reference for system requirements patterns
- Example of code quality improvement

**Potential Action**: May need to verify if fully merged or create PR for remaining changes

---

## Remote-Only Branches

### `origin/docs-reorganization`
**Status**: Merged to main via PR #13
**Latest**: bb62e19 - Cleanup: Remove redundant files and update version tracking
**Purpose**: Documentation reorganization (Phases 1-5)
**Can Delete**: Yes, but preserving for now

### `origin/final-cleanup`
**Status**: Merged to main via PR #14
**Latest**: e0d5335 - Cleanup: Remove redundant files and update version tracking
**Purpose**: Post-merge cleanup
**Can Delete**: Yes, but preserving for now

### `origin/docs/utilities-dashboards-todo`
**Status**: Unknown (likely merged)
**Latest**: 42a8727 - docs: add comprehensive utilities sector dashboard roadmap to TODO.md
**Purpose**: Dashboard documentation updates
**Can Delete**: Needs verification

### `origin/feature/v5.6-systemd-service`
**Status**: Unknown (likely merged)
**Latest**: efccdc8 - docs: condense SYSTEMD_SERVICE.md for readability
**Purpose**: Systemd service implementation
**Can Delete**: Needs verification

---

## Branch Maintenance Strategy

### Keep Branches If:
- ✅ Contains unique implementation patterns worth referencing
- ✅ Documents problem-solving approaches for complex issues
- ✅ Serves as template for future similar work
- ✅ Historical context valuable for troubleshooting
- ✅ Learning resource for team members

### Consider Deleting Branches If:
- ❌ Fully merged with no unique commits
- ❌ Superseded by better implementation
- ❌ No documentation or reference value
- ❌ >6 months old with no activity
- ❌ Experimental work that didn't pan out

### Cleanup Schedule
**Quarterly Review**: Every 3 months, review branches and update this document
**Next Review**: 2026-01-25

---

## Branch Usage Guide

### For Research
```bash
# Compare branch with main
git log main..feature/utilities-dashboards-25-widgets --oneline

# See what's unique to the branch
git diff main...feature/utilities-dashboards-25-widgets

# Check out branch for inspection (read-only)
git checkout feature/utilities-dashboards-25-widgets
# ... review code ...
git checkout main  # Return to main
```

### For Learning
```bash
# See commit history and evolution
git log --oneline --graph feature/utilities-dashboards-25-widgets

# Find specific changes
git log --all --grep="DRY"
git log --all --grep="widget"

# Compare implementations
git diff main:widgets/utilities-sector/UtilitiesSectorStatsWidget.php \
         feature/utilities-dashboards-25-widgets:widgets/utilities-sector/UtilitiesSectorStatsWidget.php
```

### For Troubleshooting
```bash
# Find when a bug was introduced
git bisect start
git bisect bad main
git bisect good feature/utilities-dashboards-25-widgets

# See who changed a line
git blame -L 100,120 widgets/utilities-sector/SomeWidget.php

# Find commits that touched a file
git log --follow -- widgets/utilities-sector/SomeWidget.php
```

---

## Notes

- **Do not force-delete branches** without consulting this document
- **Update this document** when creating/deleting branches
- **Document purpose** when creating new long-lived branches
- **Add "Why Preserved"** section for research branches
- **Link to related documentation** for context

---

**Maintained by**: tKQB Enterprises
**Questions**: See this document before deleting any branch
