# MISP Installation Refactoring Plan

**Version**: 5.5
**Date**: 2025-10-14
**Status**: PROPOSED - Ready for Implementation

## Overview

Refactor the monolithic 2183-line `misp-install.py` into a modular, maintainable architecture following Python best practices.

## Current State

- **File**: `misp-install.py` (2183 lines)
- **Phases**: 13 phases (methods in single class)
- **Issues**:
  - Hard to maintain
  - Hard to test individual phases
  - Code duplication
  - Violates Single Responsibility Principle

## Proposed Architecture

```
misp-install/
├── misp-install.py              # Main orchestrator (300-400 lines)
├── lib/                         # Shared library modules
│   ├── __init__.py              ✅ CREATED
│   ├── colors.py                ✅ CREATED
│   ├── config.py                ✅ CREATED
│   ├── validators.py            ⏳ TO CREATE
│   ├── system_checker.py        ⏳ TO CREATE
│   ├── backup_manager.py        ⏳ TO CREATE
│   ├── docker_manager.py        ⏳ TO CREATE
│   ├── user_manager.py          ⏳ TO CREATE
│   ├── state_manager.py         ⏳ TO CREATE
│   └── logging_setup.py         ⏳ TO CREATE
├── phases/                      # Phase execution modules
│   ├── __init__.py              ✅ CREATED
│   ├── base_phase.py            ⏳ TO CREATE (base class)
│   ├── phase_01_dependencies.py
│   ├── phase_02_docker_group.py
│   ├── phase_03_backup.py
│   ├── phase_04_cleanup.py
│   ├── phase_05_clone.py
│   ├── phase_06_configuration.py
│   ├── phase_07_ssl.py
│   ├── phase_08_dns.py
│   ├── phase_09_passwords.py
│   ├── phase_10_docker_build.py
│   ├── phase_11_initialization.py
│   ├── phase_11_5_api_key.py
│   ├── phase_11_7_threat_feeds.py  # NEW - feed integration
│   └── phase_12_post_install.py
└── scripts/                     # Management scripts (existing)
```

## Implementation Order

### Phase 1: Core Library Modules (Priority: HIGH)

1. **lib/validators.py** - Password validation, input validation
2. **lib/system_checker.py** - Pre-flight system checks
3. **lib/state_manager.py** - Installation state tracking
4. **lib/user_manager.py** - MISP user management (misp-owner)
5. **lib/docker_manager.py** - Docker group management
6. **lib/backup_manager.py** - Backup operations
7. **lib/logging_setup.py** - Centralized logging setup

### Phase 2: Base Phase Class (Priority: HIGH)

**File**: `phases/base_phase.py`

```python
class BasePhase:
    """Base class for all installation phases"""

    def __init__(self, config, logger, misp_dir):
        self.config = config
        self.logger = logger
        self.misp_dir = misp_dir

    def run(self):
        """Execute phase - must be implemented by subclass"""
        raise NotImplementedError

    def run_command(self, cmd, **kwargs):
        """Run shell command with logging"""
        pass

    def section_header(self, title):
        """Print phase header"""
        pass
```

### Phase 3: Individual Phase Modules (Priority: MEDIUM)

Each phase becomes a standalone module with a class inheriting from `BasePhase`:

**Example**: `phases/phase_01_dependencies.py`

```python
from phases.base_phase import BasePhase

class Phase01Dependencies(BasePhase):
    """Phase 1: Install system dependencies"""

    def run(self):
        """Execute dependency installation"""
        self.section_header("PHASE 1: INSTALLING DEPENDENCIES")
        self._install_packages()
        self._install_docker()
        self._verify_docker_compose()

    def _install_packages(self):
        """Install required system packages"""
        pass

    def _install_docker(self):
        """Install Docker if not present"""
        pass

    def _verify_docker_compose(self):
        """Verify Docker Compose is installed"""
        pass
```

### Phase 4: Main Orchestrator (Priority: HIGH)

**File**: `misp-install.py` (new version)

```python
#!/usr/bin/env python3
"""
MISP Installation Tool - Modular Architecture
Version: 5.5
"""

from lib.config import MISPConfig
from lib.state_manager import StateManager
from lib.user_manager import ensure_misp_user_exists
from lib.logging_setup import setup_logging
from phases.phase_01_dependencies import Phase01Dependencies
from phases.phase_02_docker_group import Phase02DockerGroup
# ... import all phases

class MISPInstaller:
    """Main installation orchestrator"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.state = StateManager()

        # Define phase sequence
        self.phases = [
            (1, "Dependencies", Phase01Dependencies),
            (2, "Docker Group", Phase02DockerGroup),
            # ... all phases
        ]

    def run(self, start_phase=1):
        """Execute installation from specified phase"""
        for phase_num, phase_name, PhaseClass in self.phases:
            if phase_num < start_phase:
                continue

            phase = PhaseClass(self.config, self.logger, self.misp_dir)
            phase.run()
            self.state.save(phase_num, phase_name)

def main():
    """Main entry point"""
    # Parse arguments
    # Ensure misp-owner user exists
    # Setup logging
    # Load/create config
    # Create installer
    # Run installation
    pass

if __name__ == "__main__":
    main()
```

## Benefits of Refactored Architecture

### 1. **Maintainability**
- Each phase is 100-200 lines instead of 2000+
- Easy to find and fix bugs in specific phases
- Clear separation of concerns

### 2. **Testability**
- Each phase can be tested independently
- Mock dependencies easily
- Unit tests for each phase

### 3. **Reusability**
- Shared utilities in `lib/` modules
- Base class provides common functionality
- Phases can be reused in other contexts

### 4. **Extensibility**
- Easy to add new phases (just create new file)
- Easy to modify phase order
- Easy to skip phases

### 5. **Clarity**
- File names clearly indicate purpose
- Smaller files are easier to understand
- Better IDE support (navigation, autocomplete)

### 6. **Best Practices**
- Follows Python package structure
- Follows SOLID principles
- Pythonic code organization

## Migration Strategy

### Option A: Big Bang (Not Recommended)
- Replace entire `misp-install.py` at once
- High risk of breaking changes
- Difficult to debug

### Option B: Gradual Migration (Recommended)
1. Create new modular structure alongside old code
2. Test each module thoroughly
3. Rename old `misp-install.py` to `misp-install-v5.4.py` (backup)
4. Deploy new `misp-install.py`
5. Test full installation on clean system
6. Remove old version after validation

### Option C: Parallel Development
- Keep both versions in separate branches
- Develop and test modular version in `refactor` branch
- Merge to `main` after complete validation

## Testing Plan

### Unit Tests (New)
- Test each phase module independently
- Test lib modules (validators, checkers, etc.)
- Mock external dependencies

### Integration Tests
- Test phase sequence
- Test state management
- Test error recovery

### System Tests
- Full installation on clean Ubuntu VM
- Resume capability testing
- Error scenario testing

## Backward Compatibility

### Config Files
- ✅ Same format (JSON/YAML)
- ✅ Same fields
- ✅ Same validation

### State Files
- ✅ Compatible with v5.4 state format
- ✅ Can resume v5.4 installations

### Command Line
- ✅ Same arguments
- ✅ Same behavior
- ✅ Same output format

## File Size Comparison

| Component | Current | Proposed | Reduction |
|-----------|---------|----------|-----------|
| Main file | 2183 lines | ~400 lines | -82% |
| Per phase | N/A | ~150 lines | N/A |
| Total code | 2183 lines | ~2500 lines | +15%* |

*Slight increase due to better structure and documentation

## Implementation Timeline

### Week 1: Core Infrastructure
- ✅ Day 1: Create directory structure
- ✅ Day 1: Create lib/colors.py, lib/config.py
- ⏳ Day 2: Create remaining lib/ modules
- ⏳ Day 3: Create base_phase.py
- ⏳ Day 4: Test core infrastructure

### Week 2: Phase Modules (Part 1)
- Day 1-2: Phases 1-5 (dependencies through clone)
- Day 3-4: Phases 6-9 (config through passwords)
- Day 5: Test phases 1-9

### Week 3: Phase Modules (Part 2)
- Day 1-2: Phases 10-11 (docker build, initialization)
- Day 3: Phase 11.5, 11.7, 12 (API key, feeds, post-install)
- Day 4-5: Test all phases

### Week 4: Integration & Testing
- Day 1-2: Create new main orchestrator
- Day 3: Full installation testing
- Day 4: Resume testing, error scenarios
- Day 5: Documentation updates

## Rollback Plan

If refactored version has issues:

1. **Immediate**: Restore `misp-install-v5.4.py` as `misp-install.py`
2. **Diagnose**: Review logs, identify failure point
3. **Fix**: Correct specific module
4. **Retest**: Validate fix before redeployment

## Documentation Updates Required

- ✅ **REFACTORING_PLAN.md** (this file)
- ⏳ **README.md** - Update architecture section
- ⏳ **CLAUDE.md** - Update for new structure
- ⏳ **docs/ARCHITECTURE.md** (new) - Detailed architecture doc
- ⏳ **lib/README.md** (new) - Library module documentation
- ⏳ **phases/README.md** (new) - Phase module documentation

## Success Criteria

✅ **Criteria 1**: All phases work independently
✅ **Criteria 2**: Full installation succeeds on clean system
✅ **Criteria 3**: Resume capability works
✅ **Criteria 4**: Code is more maintainable (subjective but verifiable)
✅ **Criteria 5**: No loss of functionality
✅ **Criteria 6**: Performance is equivalent or better

## Next Steps

### Immediate (Today)
1. Review and approve this plan
2. Create remaining lib/ modules
3. Create base_phase.py

### This Week
1. Create first 5 phase modules
2. Test each module
3. Create main orchestrator skeleton

### Next Week
1. Complete all phase modules
2. Integration testing
3. Full system testing

## Questions for Review

1. ✅ **Approved architecture?** - Modular structure with lib/ and phases/
2. **Migration strategy?** - Gradual (Option B) or Parallel (Option C)?
3. **Testing approach?** - Unit tests needed? System tests only?
4. **Timeline acceptable?** - 4 weeks too long? Can accelerate?
5. **Backward compatibility required?** - Yes (can resume v5.4 installations)

## References

- Python Best Practices: PEP 8, PEP 257
- SOLID Principles
- Clean Code (Robert C. Martin)
- Test-Driven Development

---

**Status**: ✅ READY FOR IMPLEMENTATION
**Next Action**: Get approval, then create lib/ modules
**Est. Completion**: 4 weeks (aggressive: 2 weeks)
