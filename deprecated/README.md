# Deprecated Files

**Date**: 2025-10-14
**Reason**: Historical files no longer actively used but preserved for reference

This directory contains files that are no longer part of the active codebase but are preserved for historical reference and potential future needs.

## Directory Structure

```
deprecated/
├── README.md (this file)
├── docs/              # Deprecated documentation
├── scripts/           # Deprecated scripts
└── build/             # Build artifacts (can be regenerated)
```

## Deprecated Documentation (Root Level)

### ACL-FIX-SUMMARY.md
- **Date Deprecated**: 2025-10-14
- **Reason**: Historical document from v5.4 ACL permission fixes
- **Status**: Fixes implemented and documented in main docs
- **Safe to Delete**: Yes (after 6 months)

### DOCUMENTATION_REVIEW.md
- **Date Deprecated**: 2025-10-14
- **Reason**: One-time documentation review completed
- **Status**: All updates applied to active documentation
- **Safe to Delete**: Yes (after 3 months)

### REFACTORING_PLAN.md
- **Date Deprecated**: 2025-10-14
- **Reason**: Refactoring completed via Phases 1-9
- **Status**: Superseded by docs/REFACTORING_SUMMARY.md
- **Safe to Delete**: Yes (after 6 months)

### REFACTORING_RECOMMENDATIONS.md
- **Date Deprecated**: 2025-10-14
- **Reason**: All recommendations implemented
- **Status**: Phases 1-9 completed, documented in TODO.md
- **Safe to Delete**: Yes (after 6 months)

## Deprecated Scripts

### scripts/populate-misp-news-api.py
- **Date Deprecated**: 2025-10-14
- **Reason**: MISP `/news/add` API returns HTTP 500 error
- **Replacement**: `scripts/populate-misp-news.py` (database version)
- **Status**: API endpoint broken in upstream MISP
- **Safe to Delete**: No - keep until MISP upstream fixes API

### scripts/populate-misp-news-complete.py
- **Date Deprecated**: 2025-10-14
- **Reason**: HTTP POST to `/news/add` returns HTTP 500 error
- **Replacement**: `scripts/populate-misp-news.py` (database version)
- **Status**: Same API issue as populate-misp-news-api.py
- **Safe to Delete**: No - keep until MISP upstream fixes API

### scripts/add-nerc-cip-news-feeds-api.py
- **Date Deprecated**: 2025-10-14
- **Reason**: Database version preferred for reliability
- **Replacement**: `scripts/add-nerc-cip-news-feeds.py` (database version)
- **Status**: API works but DB version is more reliable
- **Safe to Delete**: Yes (after testing period - 3 months)

### scripts/check-misp-feeds-api.py
- **Date Deprecated**: 2025-10-14
- **Reason**: Database version preferred for consistency
- **Replacement**: `scripts/check-misp-feeds.py` (database version)
- **Status**: API works but DB version is more reliable
- **Safe to Delete**: Yes (after testing period - 3 months)

## Build Directory

### build/
- **Date Deprecated**: 2025-10-14
- **Reason**: pipx build artifacts (auto-generated)
- **Replacement**: Can be regenerated with `pipx install .`
- **Status**: Not needed in version control
- **Safe to Delete**: Yes (immediately)

## Deletion Schedule

| Item | Deprecation Date | Safe Deletion Date | Auto-Delete |
|------|------------------|-------------------|-------------|
| ACL-FIX-SUMMARY.md | 2025-10-14 | 2026-04-14 | ✅ |
| DOCUMENTATION_REVIEW.md | 2025-10-14 | 2026-01-14 | ✅ |
| REFACTORING_PLAN.md | 2025-10-14 | 2026-04-14 | ✅ |
| REFACTORING_RECOMMENDATIONS.md | 2025-10-14 | 2026-04-14 | ✅ |
| populate-misp-news-api.py | 2025-10-14 | TBD | ❌ Keep |
| populate-misp-news-complete.py | 2025-10-14 | TBD | ❌ Keep |
| add-nerc-cip-news-feeds-api.py | 2025-10-14 | 2026-01-14 | ✅ |
| check-misp-feeds-api.py | 2025-10-14 | 2026-01-14 | ✅ |
| build/ | 2025-10-14 | Immediate | ✅ |

## Recovery Instructions

If you need to restore any deprecated file:

```bash
# From project root
cp deprecated/docs/FILENAME.md .
# or
cp deprecated/scripts/FILENAME.py scripts/
```

## Notes

- Files in this directory are not actively maintained
- They may contain outdated information or code
- Refer to active codebase for current implementations
- Historical value preserved for audit trails and reference

---

**Maintained by**: tKQB Enterprises
**Last Updated**: 2025-10-14
