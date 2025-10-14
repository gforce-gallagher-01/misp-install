# Script Refactoring Recommendations

**Date:** 2025-10-14
**Status:** ANALYSIS COMPLETE - Ready for Implementation
**Priority:** HIGH (reduces maintenance burden and code duplication)

---

## Executive Summary

Analysis of 20+ scripts reveals significant code duplication that should be refactored into shared library modules. This will improve maintainability, consistency, and reduce the codebase by an estimated **2,000-3,000 lines** of duplicate code.

**Current State:**
- 9 scripts duplicate the `Colors` class (~270 lines total)
- 7 scripts duplicate database operations (~350 lines total)
- 16 scripts duplicate Docker operations (~800 lines total)
- 7 scripts duplicate backup operations (~700 lines total)

**Recommendation:** Create additional `lib/` modules to eliminate duplication across all scripts.

---

## Refactoring Priorities

### Priority 1: Critical Duplications (HIGH - Do First)

#### 1.1 Colors Module ✅ ALREADY EXISTS
**Status:** Already implemented in `lib/colors.py`
**Problem:** 9 scripts still have duplicate Colors classes instead of importing from lib

**Scripts to Fix:**
- scripts/backup-misp.py
- scripts/configure-misp-nerc-cip.py
- scripts/configure-misp-ready.py
- scripts/misp-backup-cron.py
- scripts/misp_logger.py (special case - this IS a lib module)
- scripts/misp-restore.py
- scripts/misp-setup-complete.py
- scripts/misp-update.py
- scripts/uninstall-misp.py

**Refactoring:**
```python
# OLD (duplicate in each script):
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    # ... 25+ lines

# NEW (one line import):
from lib.colors import Colors
```

**Savings:** ~270 lines eliminated across 9 scripts

---

#### 1.2 Docker Manager Module (PARTIALLY EXISTS)
**Current:** `lib/docker_manager.py` exists but not used by scripts
**Problem:** 16 scripts have duplicate Docker Compose operations

**Common Operations to Centralize:**
```python
# Duplicate pattern in 16 scripts:
subprocess.run(['sudo', 'docker', 'compose', 'ps'], cwd='/opt/misp')
subprocess.run(['sudo', 'docker', 'compose', 'up', '-d'], cwd='/opt/misp')
subprocess.run(['sudo', 'docker', 'compose', 'down'], cwd='/opt/misp')
subprocess.run(['sudo', 'docker', 'compose', 'exec', '-T', container, ...])
```

**Proposed lib/docker_manager.py Enhancements:**
```python
class DockerManager:
    def __init__(self, misp_dir: Path = Path('/opt/misp')):
        self.misp_dir = misp_dir

    def compose_ps(self) -> List[str]:
        """Get list of running containers"""

    def compose_up(self, services: List[str] = None) -> bool:
        """Start containers"""

    def compose_down(self) -> bool:
        """Stop containers"""

    def compose_exec(self, container: str, command: List[str]) -> subprocess.CompletedProcess:
        """Execute command in container"""

    def check_container_health(self, container: str) -> bool:
        """Check if container is healthy"""

    def get_container_logs(self, container: str, tail: int = 50) -> str:
        """Get container logs"""
```

**Savings:** ~800 lines eliminated across 16 scripts

---

#### 1.3 Database Operations Module (NEW)
**File:** `lib/database_manager.py` (to be created)
**Problem:** 7 scripts duplicate MySQL operations

**Common Operations:**
```python
# Duplicate pattern in 7 scripts:
# 1. Read MySQL password from .env (20-30 lines each script)
# 2. Execute MySQL commands via docker compose exec
# 3. Backup database (mysqldump)
# 4. Restore database (mysql import)
# 5. Check database health
```

**Proposed lib/database_manager.py:**
```python
class DatabaseManager:
    def __init__(self, misp_dir: Path = Path('/opt/misp')):
        self.misp_dir = misp_dir
        self.docker_mgr = DockerManager(misp_dir)

    def get_mysql_password(self) -> str:
        """Read MySQL password from .env file"""

    def execute_sql(self, sql: str) -> subprocess.CompletedProcess:
        """Execute SQL command"""

    def backup_database(self, output_file: Path) -> bool:
        """Create database backup using mysqldump"""

    def restore_database(self, backup_file: Path) -> bool:
        """Restore database from backup"""

    def check_database_health(self) -> bool:
        """Check if database is accessible"""

    def wait_for_database(self, max_attempts: int = 30, delay: int = 2) -> bool:
        """Wait for database to be ready"""
```

**Scripts to Update:**
- scripts/backup-misp.py
- scripts/misp-backup-cron.py
- scripts/misp-restore.py
- scripts/configure-misp-nerc-cip.py
- scripts/configure-misp-ready.py
- scripts/populate-misp-news.py
- scripts/add-nerc-cip-news-feeds.py

**Savings:** ~350 lines eliminated across 7 scripts

---

### Priority 2: Medium Duplications (MEDIUM)

#### 2.1 Backup Manager Module ✅ EXISTS but Needs Enhancement
**Current:** `lib/backup_manager.py` exists (6.6KB)
**Problem:** Not used by backup scripts, which have duplicate logic

**Current Duplication:**
- scripts/backup-misp.py (477 lines) - duplicates BackupManager logic
- scripts/misp-backup-cron.py - duplicates backup logic
- scripts/misp-restore.py - has its own BackupInfo class

**Proposed Enhancement:**
```python
# lib/backup_manager.py (enhance existing)
class BackupManager:
    def create_full_backup(self) -> Path:
        """Create full backup (DB + config + SSL)"""

    def create_incremental_backup(self) -> Path:
        """Create incremental backup (DB only)"""

    def list_backups(self) -> List[BackupInfo]:
        """List all available backups"""

    def cleanup_old_backups(self, retention_days: int):
        """Remove backups older than retention period"""

    def get_backup_info(self, backup_path: Path) -> BackupInfo:
        """Get metadata about a backup"""
```

**Scripts to Update:**
- scripts/backup-misp.py - use BackupManager instead of duplicating
- scripts/misp-backup-cron.py - use BackupManager
- scripts/misp-restore.py - use BackupInfo from lib

**Savings:** ~700 lines eliminated across 3 scripts

---

#### 2.2 MISP API Helper Module ✅ ALREADY EXISTS
**Current:** `misp_api.py` in root (good, but could be in lib/)
**Usage:** Some scripts use it, others don't

**Scripts Using misp_api.py:**
- ✅ scripts/add-nerc-cip-news-feeds-api.py
- ✅ scripts/check-misp-feeds-api.py
- ✅ scripts/populate-misp-news-api.py

**Scripts NOT Using misp_api.py (but should):**
- ❌ scripts/configure-misp-nerc-cip.py (uses cake commands - OK)
- ❌ scripts/configure-misp-ready.py (uses cake commands - OK)
- ❌ scripts/misp-setup-complete.py (uses cake commands - OK)

**Recommendation:** Keep as-is. Some scripts correctly use cake commands instead of API.

---

### Priority 3: Large Script Refactoring (LOWER PRIORITY)

#### 3.1 misp_install_gui.py (1087 lines)
**Analysis:** 11 classes, well-organized
**Recommendation:** Keep as monolithic for now
**Reason:** GUI code is cohesive, splitting would reduce readability

**Possible Future Enhancement:** Extract validation logic to `lib/validators.py` (already exists)

---

#### 3.2 misp-setup-complete.py (715 lines)
**Analysis:** Orchestrator script with 20 methods
**Recommendation:** Medium priority refactoring

**Potential Extraction:**
- Feed management operations → use existing API scripts
- Settings configuration → use lib/config.py
- Database operations → use lib/database_manager.py (when created)

**Estimated Reduction:** 715 → 400 lines (44% reduction)

---

#### 3.3 misp-restore.py (794 lines)
**Analysis:** Comprehensive backup/restore tool
**Recommendation:** Refactor to use lib modules

**Current Issues:**
- Duplicate Colors class (use lib/colors.py)
- Duplicate BackupInfo class (use lib/backup_manager.py)
- Duplicate database operations (use lib/database_manager.py)
- Duplicate Docker operations (use lib/docker_manager.py)

**Estimated Reduction:** 794 → 400 lines (50% reduction)

---

## Implementation Plan

### Phase 1: Quick Wins (1-2 hours)
**Goal:** Eliminate Colors duplication across all scripts

1. Update all 9 scripts to import from `lib.colors`
2. Remove duplicate Colors classes
3. Test each script after modification
4. Commit: "Refactor: Use centralized Colors class from lib"

**Files to Modify:**
```
scripts/backup-misp.py
scripts/configure-misp-nerc-cip.py
scripts/configure-misp-ready.py
scripts/misp-backup-cron.py
scripts/misp-restore.py
scripts/misp-setup-complete.py
scripts/misp-update.py
scripts/uninstall-misp.py
```

**Pattern:**
```python
# Remove lines 40-70 (Colors class definition)
# Add at top:
from lib.colors import Colors
```

---

### Phase 2: Database Operations (4-6 hours)
**Goal:** Create and use lib/database_manager.py

1. Create `lib/database_manager.py` with DatabaseManager class
2. Implement all common database operations
3. Update 7 scripts to use DatabaseManager
4. Test database backup, restore, health checks
5. Commit: "Refactor: Centralize database operations in lib"

**New File:** `lib/database_manager.py` (~200 lines)

**Scripts to Update:**
```
scripts/backup-misp.py
scripts/misp-backup-cron.py
scripts/misp-restore.py
scripts/configure-misp-nerc-cip.py
scripts/configure-misp-ready.py
scripts/populate-misp-news.py
scripts/add-nerc-cip-news-feeds.py
```

---

### Phase 3: Docker Operations (4-6 hours)
**Goal:** Enhance and use lib/docker_manager.py

1. Enhance existing `lib/docker_manager.py`
2. Add methods for all common docker compose operations
3. Update 16 scripts to use DockerManager
4. Test container management operations
5. Commit: "Refactor: Use centralized DockerManager from lib"

**Enhanced File:** `lib/docker_manager.py` (expand from 5.6KB to ~10KB)

**Scripts to Update:** All 16 scripts that use docker compose

---

### Phase 4: Backup Operations (6-8 hours)
**Goal:** Use lib/backup_manager.py across all backup scripts

1. Enhance existing `lib/backup_manager.py`
2. Extract BackupInfo class from misp-restore.py
3. Update backup-misp.py to use BackupManager
4. Update misp-backup-cron.py to use BackupManager
5. Update misp-restore.py to use BackupManager
6. Test full backup/restore cycle
7. Commit: "Refactor: Use centralized BackupManager from lib"

**Scripts to Update:**
```
scripts/backup-misp.py (477 lines → ~200 lines)
scripts/misp-backup-cron.py
scripts/misp-restore.py (794 lines → ~400 lines)
```

---

### Phase 5: Large Script Refactoring (8-12 hours)
**Goal:** Refactor misp-setup-complete.py and misp-restore.py

1. Apply all lib modules to misp-setup-complete.py
2. Apply all lib modules to misp-restore.py
3. Extract any remaining common code
4. Test complete setup and restore workflows
5. Commit: "Refactor: Simplify orchestrator scripts using lib modules"

---

## Testing Plan

### Unit Tests (NEW)
Create `tests/` directory with unit tests for each lib module:

```
tests/
├── test_colors.py
├── test_config.py
├── test_validators.py
├── test_database_manager.py
├── test_docker_manager.py
├── test_backup_manager.py
└── test_system_checker.py
```

### Integration Tests
Test refactored scripts:
```bash
# Test backup/restore cycle
python3 scripts/backup-misp.py
python3 scripts/misp-restore.py --restore latest

# Test NERC CIP configuration
python3 scripts/configure-misp-nerc-cip.py --dry-run

# Test complete setup
python3 scripts/misp-setup-complete.py --dry-run
```

### Regression Tests
Ensure all existing functionality still works:
1. Fresh MISP installation
2. Backup creation
3. Restore from backup
4. NERC CIP configuration
5. Feed management
6. News population

---

## Benefits Summary

### Code Reduction
- **Phase 1:** ~270 lines eliminated (Colors duplication)
- **Phase 2:** ~350 lines eliminated (Database operations)
- **Phase 3:** ~800 lines eliminated (Docker operations)
- **Phase 4:** ~700 lines eliminated (Backup operations)
- **Phase 5:** ~500 lines eliminated (Large script optimization)

**Total:** ~2,620 lines eliminated (estimated)

### Maintainability
✅ **Single Source of Truth:** Bug fixes in one place benefit all scripts
✅ **Consistency:** All scripts use same patterns and error handling
✅ **Testability:** Lib modules are easier to unit test than monolithic scripts
✅ **Documentation:** Central modules are easier to document
✅ **Onboarding:** New developers have clear, organized code structure

### Development Speed
✅ **Faster Features:** Reuse existing modules instead of duplicating code
✅ **Easier Debugging:** Centralized code is easier to trace
✅ **Better IDE Support:** Autocomplete and navigation work better with modules

---

## Estimated Effort

| Phase | Hours | Priority | Impact |
|-------|-------|----------|--------|
| Phase 1: Colors | 2 | HIGH | ~270 lines saved, 9 scripts cleaned |
| Phase 2: Database | 6 | HIGH | ~350 lines saved, 7 scripts cleaned |
| Phase 3: Docker | 6 | HIGH | ~800 lines saved, 16 scripts cleaned |
| Phase 4: Backup | 8 | MEDIUM | ~700 lines saved, 3 scripts cleaned |
| Phase 5: Large Scripts | 12 | MEDIUM | ~500 lines saved, 2 scripts optimized |
| **Total** | **34 hours** | | **~2,620 lines eliminated** |

**Timeline:**
- **Aggressive:** 1 week (full-time)
- **Moderate:** 2 weeks (half-time)
- **Relaxed:** 4 weeks (quarter-time)

---

## Success Criteria

✅ **All scripts import from lib/** - No duplicate Colors, no duplicate database ops
✅ **Code reduction achieved** - At least 2,000 lines eliminated
✅ **No functionality lost** - All existing features still work
✅ **Tests pass** - All integration tests succeed
✅ **Documentation updated** - SCRIPTS.md reflects new architecture

---

## Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation:**
- Test each refactored script thoroughly
- Keep backup of original scripts during refactoring
- Use git branches for each phase

### Risk 2: Unexpected Dependencies
**Mitigation:**
- Analyze import chains before refactoring
- Test each phase independently
- Have rollback plan for each phase

### Risk 3: Performance Regression
**Mitigation:**
- Benchmark before/after for critical operations
- Monitor import overhead
- Profile if performance degrades

---

## Next Steps

### Immediate (This Week)
1. ✅ Review and approve this refactoring plan
2. ⏳ Create `lib/database_manager.py` module
3. ⏳ Start Phase 1 (Colors refactoring) - 2 hours
4. ⏳ Test Phase 1 changes
5. ⏳ Commit Phase 1

### This Month
- Complete Phases 2-3 (Database + Docker refactoring)
- Update documentation
- Create unit tests

### Next Month
- Complete Phases 4-5 (Backup + Large scripts)
- Final integration testing
- Release refactored v5.6

---

## Questions for Review

1. **Approve refactoring plan?** - Is this the right approach?
2. **Priority order correct?** - Colors → Database → Docker → Backup → Large Scripts?
3. **Timeline acceptable?** - 34 hours over 2-4 weeks?
4. **Testing approach?** - Unit tests + integration tests sufficient?
5. **Breaking changes acceptable?** - All changes are internal, no user-facing changes

---

**Status:** ✅ READY FOR IMPLEMENTATION
**Next Action:** Get approval, then start Phase 1 (Colors refactoring)
**Estimated Completion:** 2-4 weeks (34 hours total)

---

**Last Updated:** 2025-10-14
**Author:** Claude Code Analysis
**Maintainer:** tKQB Enterprises
