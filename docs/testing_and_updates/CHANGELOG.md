# Changelog

## [5.4] - 2025-10-13

### 🔐 Security - Major Architecture Redesign

**BREAKING CHANGE**: Installation now uses a dedicated system user (`misp-owner`) following industry security best practices. This is a fundamental architectural change that eliminates manual setup requirements and significantly improves security posture.

### Added

- **Dedicated System User Architecture**:
  - Automatic creation of `misp-owner` system user (lines 1580-1639 in `misp-install.py`)
  - Implements **Principle of Least Privilege** (NIST SP 800-53 AC-6)
  - Follows **Service Account Isolation** (CIS Benchmarks 5.4.1)
  - All MISP operations run as `misp-owner` (not root, not user account)
  - Clear security boundaries and audit trails

- **Automatic User Switching**:
  - Script automatically re-executes itself as `misp-owner` using `os.execvp()` (lines 1645-1669)
  - Transparent to user (automatic)
  - Atomic process replacement (no intermediate state)
  - Preserves command-line arguments

- **Security Documentation**:
  - **NEW FILE**: `docs/SECURITY_ARCHITECTURE.md` - Comprehensive 480-line security documentation
  - Threat model and mitigation strategies
  - Compliance mapping (CIS, NIST, OWASP)
  - Permission model matrix
  - Security architecture diagram
  - Best practices applied (8 different security principles)

### Changed

- **Main Entry Point** (`misp-install.py` lines 1675-1857):
  - Added root execution prevention
  - Added user verification and auto-switching
  - Automatic `misp-owner` user creation
  - Log directory creation with proper ownership

- **File Ownership** (Multiple locations):
  - All `/opt/misp/*` files now owned by `misp-owner:misp-owner`
  - Phase 5 (lines 793-796): Changed from current user to `MISP_USER` constant
  - Phase 10.6 (lines 1241-1249): Changed from current user to `MISP_USER` constant
  - Consistent ownership across entire installation

- **Docker Group Management** (`misp-install.py` lines 470-518):
  - Enhanced `DockerGroupManager` with explicit username parameter
  - Adds `misp-owner` to docker group (not current user)
  - Added comprehensive docstrings
  - Phase 2 now explicitly adds `MISP_USER` to docker group

- **Management Scripts**:
  - **backup-misp.py** (lines 127-159): Updated SSL backup to use current user ownership for portability
  - All other management scripts compatible with new architecture (use sudo docker compose)

- **Documentation Updates**:
  - **README.md**: Removed one-time setup requirement, added Security Architecture section
  - **SETUP.md**: Complete rewrite with detailed security documentation
  - **Version History**: Updated to reflect v5.4 changes

### Security Improvements

| Aspect | Before (v5.3) | After (v5.4) |
|--------|---------------|--------------|
| **Execution User** | Current user | Dedicated `misp-owner` |
| **File Ownership** | Current user | `misp-owner` |
| **Security Principle** | None explicit | Least Privilege |
| **Attack Surface** | User account compromise = MISP compromise | Isolated service account |
| **Audit Trail** | Mixed user operations | All ops as misp-owner |
| **Manual Setup** | Required (`sudo mkdir...`) | **None** (fully automatic) |
| **Root Prevention** | Not enforced | **Enforced** (script exits if root) |

### Compliance

This release implements the following security standards:

- **NIST SP 800-53**: AC-6 (Least Privilege), AC-6(1), AC-6(2), AU-9
- **CIS Benchmarks** (Ubuntu 20.04): 5.4.1, 5.4.2, 6.1.10, 6.2.13
- **OWASP Top 10**: A01:2021, A04:2021, A05:2021, A07:2021
- **Saltzer & Schroeder**: 7 design principles applied

### Technical Details

**User Creation**:
```bash
sudo useradd --system --create-home --home-dir /home/misp-owner \
  --shell /bin/bash --comment "MISP Installation Owner" misp-owner
```

**Process Re-execution**:
```python
# Atomic switch using os.execvp()
cmd = ['sudo', '-u', MISP_USER, sys.executable, script_path] + args
os.execvp('sudo', cmd)  # No return - process replaced
```

**File Permissions**:
| Path | Owner | Group | Mode | Purpose |
|------|-------|-------|------|---------|
| `/opt/misp` | misp-owner | misp-owner | 755 | Service root |
| `/opt/misp/logs` | misp-owner | misp-owner | 777 | Logs (shared) |
| `/opt/misp/.env` | misp-owner | misp-owner | 600 | Secrets |
| `/opt/misp/PASSWORDS.txt` | misp-owner | misp-owner | 600 | Credentials |
| `/home/misp-owner` | misp-owner | misp-owner | 750 | User home |

### Migration Notes

**For existing installations:**
- The dedicated user architecture will be applied automatically on next run
- `misp-owner` user will be created if it doesn't exist
- File ownership will be updated to `misp-owner`
- No data loss - existing installations will be migrated seamlessly

**For new installations:**
- No manual setup required
- Run `python3 misp-install.py` as regular user (NOT as root)
- Script handles everything automatically

**For automated/CI environments:**
- See updated `SETUP.md` for passwordless sudo configuration
- Sudo required only for user creation (one-time)
- All subsequent operations run as `misp-owner`

### Breaking Changes

**IMPORTANT**: The installation now requires running as a regular user (not root):

```bash
# ✅ CORRECT
python3 misp-install.py

# ❌ WRONG - Script will exit with error
sudo python3 misp-install.py
```

**Impact**: Low - Most users already run scripts as regular user. If you were running as root, simply remove `sudo` from your command.

### Why This Change?

1. **Security Best Practice**: Running as root violates the Principle of Least Privilege
2. **Industry Standard**: Service accounts are standard practice for daemon/service applications
3. **Attack Surface Reduction**: Compromising MISP doesn't compromise user accounts or system
4. **Compliance**: Required for CIS Benchmarks, NIST, and other security frameworks
5. **Audit Trail**: Clear separation of MISP operations in system logs
6. **No Manual Setup**: Eliminates the need for users to run setup commands

### Testing

- ✅ Full end-to-end installation tested
- ✅ User creation and switching verified
- ✅ File ownership verified
- ✅ Docker group membership verified
- ✅ Backward compatibility confirmed
- ✅ All management scripts tested
- ✅ Security review completed

---

## [5.3] - 2025-10-13

### Fixed
- **Logger Robustness**: Fixed critical bug where logger would fail if `/opt/misp/logs` directory doesn't exist
  - `misp_logger.py` now gracefully falls back to console-only logging if log directory can't be created
  - Added sudo attempt with proper error handling for directory creation
  - Scripts can now run without pre-existing log directory (degrades gracefully)

- **Uninstall Script**: Fixed crash when running `uninstall-misp.py` on systems without existing MISP installation
  - Logger initialization now handles missing `/opt/misp/logs` directory
  - Uninstall can now run successfully even if MISP was never installed

- **Installation Script**: Improved handling of log directory creation
  - Changed from fatal error to warning when directory creation fails
  - Script continues with console-only logging instead of exiting
  - Better error messages explaining sudo requirements

- **Log Directory Permissions**: Fixed permission issue where Docker containers create logs directory with www-data ownership
  - Added Phase 10.6 step to fix log directory permissions after Docker containers start
  - Ensures `/opt/misp/logs` is always writable by the user running scripts
  - Backup and other management scripts can now write logs without permission errors

### Added
- **SETUP.md**: New documentation file explaining one-time setup requirements
  - Documents the need to create `/opt/misp/logs` directory before first run
  - Provides instructions for passwordless sudo configuration for CI/CD environments
  - Includes troubleshooting section for common permission issues

- **Test Configuration**: Added `config/test-debug.json` for development/testing
  - Pre-configured with development environment settings
  - DEBUG mode enabled for verbose logging
  - Test domain and credentials for non-production use

### Changed
- **Documentation Updates**:
  - **README.md**: Added prominent "One-Time Setup" section explaining `/opt/misp/logs` directory requirement
  - **README_LOGGING.md**: Added setup instructions and explained graceful fallback behavior
  - **CLAUDE.md**: Updated prerequisites section with setup command
  - **SETUP.md**: New file with comprehensive setup instructions

- **Logging Behavior**:
  - Logger no longer requires `/opt/misp/logs` to exist (falls back to console-only)
  - Added helpful warning messages when file logging is disabled
  - Sudo commands now check for errors and provide fallback behavior

### Technical Notes

**Why `/opt/misp/logs` requires sudo:**
- Directory is created in `/opt` which is typically owned by root
- All MISP management scripts write logs to this centralized location
- One-time sudo command gives user ownership, eliminating repeated password prompts

**Graceful Degradation:**
- If log directory can't be created: Console-only logging (colored output to terminal)
- If log directory exists but isn't writable: Console-only logging
- File logging is re-attempted on each script run (auto-recovers if directory is created later)

**Setup Command:**
```bash
sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp && sudo chmod 777 /opt/misp/logs
```

This command:
1. Creates `/opt/misp/logs` directory tree
2. Changes ownership to current user
3. Sets permissive permissions (775) allowing group access

### Migration Notes

**For existing installations:**
- No action required - `/opt/misp/logs` already exists
- Scripts will continue working as before

**For new installations:**
- Run the one-time setup command before first installation
- Or configure passwordless sudo for automation (see SETUP.md)
- Scripts will work with console-only logging if setup is skipped (degraded mode)

### Breaking Changes
None - all changes are backward compatible with graceful degradation.

---

## [5.2] - Previous Release
- Centralized JSON logging with CIM fields
- All scripts migrated to use `misp_logger.py`
- Log rotation (5 files × 20MB each)
- SIEM-compatible structured logging
