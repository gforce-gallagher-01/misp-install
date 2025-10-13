# Changelog

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
sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp && sudo chmod 775 /opt/misp/logs
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
