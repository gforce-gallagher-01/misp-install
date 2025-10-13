# Known Issues

## Docker Health Check Failing (Non-Critical)

**Issue**: The MISP core container reports "unhealthy" status despite MISP working correctly.

**Root Cause**: The upstream MISP-docker healthcheck uses the `BASE_URL` domain (`https://misp-test.lan/users/heartbeat`) to check container health, but the container cannot resolve this hostname internally.

**Evidence**:
- MISP web interface is accessible at https://[SERVER_IP]/
- The `/users/heartbeat` endpoint returns correct response when accessed via `localhost`:
  ```json
  {"message": "Additional supply depots required."}
  ```
- All MISP services are running and functional

**Impact**:
- Does NOT affect MISP functionality
- Does NOT affect backup/restore operations
- Only affects Docker Compose health status reporting

**Workaround**: This is an upstream MISP-docker issue. The healthcheck in the official MISP docker-compose.yml should use `https://localhost/users/heartbeat` instead of `https://${BASE_URL}/users/heartbeat`.

**Status**: Documented for awareness. This does not require fixes in our deployment scripts.

**Reference**:
- Healthcheck command: `curl -ks https://misp-test.lan/users/heartbeat > /dev/null || exit 1`
- Container: `ghcr.io/misp/misp-docker/misp-core:latest`
- Verified: 2025-10-13

---

## Summary

This issue tracker documents problems found during deployment testing that are either:
1. Upstream issues in MISP-docker (not our scripts)
2. Known Docker Compose warnings that are expected behavior
3. Issues that have been fixed in our deployment scripts

All critical deployment issues in our scripts have been resolved.
