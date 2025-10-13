# Known Issues

**Version**: 5.4
**Last Updated**: 2025-10-13
**Status**: All critical issues resolved ✅

---

## Current Known Issues

### 1. Docker Health Check Failing (Non-Critical)

**Severity**: Low (cosmetic only)
**Status**: Upstream issue - not fixable in our scripts

**Issue**: The MISP core container reports "unhealthy" status despite MISP working correctly.

**Root Cause**: The upstream MISP-docker healthcheck uses the `BASE_URL` domain (`https://misp.lan/users/heartbeat`) to check container health, but the container cannot resolve this hostname internally.

**Evidence**:
- ✅ MISP web interface is accessible at https://[SERVER_IP]/
- ✅ The `/users/heartbeat` endpoint returns correct response when accessed via `localhost`:
  ```json
  {"message": "Additional supply depots required."}
  ```
- ✅ All MISP services are running and functional

**Impact**:
- Does NOT affect MISP functionality
- Does NOT affect backup/restore operations
- Does NOT affect installation or updates
- Only affects Docker Compose health status reporting

**Workaround**: This is an upstream MISP-docker issue. The healthcheck in the official MISP docker-compose.yml should use `https://localhost/users/heartbeat` instead of `https://${BASE_URL}/users/heartbeat`.

**Resolution Status**: Documented for awareness. This does not require fixes in our deployment scripts. Users can safely ignore the "unhealthy" status.

**Reference**:
- Healthcheck command: `curl -ks https://misp.lan/users/heartbeat > /dev/null || exit 1`
- Container: `ghcr.io/misp/misp-docker/misp-core:latest`
- First verified: 2025-10-13
- Still present in: v5.4

---

## Resolved Issues (v5.4)

### ✅ Log Directory Permission Conflicts
**Fixed in**: v5.4 (Phase 5.5)

**Issue**: Docker containers created `/opt/misp/logs` with restrictive permissions, preventing management scripts from writing logs.

**Resolution**: Added Phase 5.5 to create and configure log directory with 777 permissions BEFORE Docker starts. See `misp-install.py:819-837`.

### ✅ Duplicate Scripts (.sh versions)
**Fixed in**: v5.4

**Issue**: Both `.sh` and `.py` versions of backup and uninstall scripts existed, causing confusion.

**Resolution**: Removed legacy `backup-misp.sh` and `uninstall-misp.sh`. All functionality consolidated into Python scripts.

### ✅ Inconsistent Documentation
**Fixed in**: v5.4

**Issue**: Documentation referenced outdated permission values (775) and .sh scripts.

**Resolution**: Updated 15+ documentation files for consistency. All references now point to .py scripts and correct permissions (777 for logs).

---

## Previously Resolved Issues (v5.3 and earlier)

### ✅ Logger Permission Errors (v5.3)
**Resolution**: Implemented graceful fallback when log directory unavailable. Scripts continue with console-only logging.

### ✅ Docker Group Activation (v5.2)
**Resolution**: Automatic docker group configuration with session refresh. Users no longer need to logout/login.

### ✅ Resume Capability (v5.0)
**Resolution**: Installation can now resume from any interrupted phase using `--resume` flag.

---

## Issue Categories

### Upstream Issues (Not Our Code)
- Docker healthcheck failure (MISP-docker project)

### Known Limitations (By Design)
- None currently

### Fixed Issues (Resolved)
- Log directory permissions (v5.4)
- Duplicate scripts (v5.4)
- Documentation inconsistencies (v5.4)
- Logger errors (v5.3)
- Docker group activation (v5.2)

---

## Reporting New Issues

If you encounter issues not listed here:

1. **Check Logs**: `/opt/misp/logs/misp-install-*.log`
2. **Verify System**: Run pre-flight checks (automatic in script)
3. **Search Documentation**: Check `docs/TROUBLESHOOTING.md`
4. **Report**: Create GitHub issue with:
   - Version number (v5.4)
   - Error logs (JSON formatted)
   - System details (OS, RAM, disk space)
   - Steps to reproduce

---

## Summary

**Critical Issues**: 0
**Non-Critical Issues**: 1 (upstream cosmetic issue)
**Fixed in v5.4**: 3 major improvements

This project maintains high code quality with comprehensive testing and documentation. All critical deployment issues have been resolved. The only remaining issue is a cosmetic healthcheck status from upstream MISP-docker that does not affect functionality.

**Status**: Production-ready ✅

---

**Last Review**: 2025-10-13
**Next Review**: After v5.5 release or when new issues reported
