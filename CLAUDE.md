# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a professional-grade Python automation suite for deploying and managing MISP (Malware Information Sharing Platform) via Docker. The suite includes installation, backup, restore, update, and uninstallation tools with enterprise-grade features.

**Organization**: tKQB Enterprises
**Current Version**: 5.4 (STABLE - PRODUCTION READY)
**Status**: v5.4 dedicated user architecture fully implemented and tested
**Last Updated**: 2025-10-13

## Architecture

### Core Design Principles

1. **Centralized JSON Logging**: All scripts use `/opt/misp/logs/` with CIM (Common Information Model) field names for SIEM integration (Splunk, ELK, etc.)
2. **State Management**: Installation uses resume capability via `~/.misp-install/state.json`
3. **Phase-Based Execution**: Operations are broken into numbered phases that can be resumed if interrupted
4. **Docker-First**: All MISP components run in Docker containers managed via docker-compose

### Critical Directory Structure

```
/opt/misp/                  # Main MISP installation (DO NOT delete during cleanup)
  ├── logs/                 # Centralized JSON logs - MUST EXIST before logging starts
  ├── .env                  # Docker environment config (chmod 600)
  ├── PASSWORDS.txt         # All credentials (chmod 600)
  ├── ssl/                  # SSL certificates
  └── docker-compose.yml    # Docker configuration

~/misp-backups/            # Backup storage (preserved during uninstall)
~/.misp-install/           # Installation state and metadata
```

### Logging Architecture

**Critical**: `/opt/misp/logs/` must exist BEFORE any logger initialization. The directory is created in Phase 1 of `misp-install.py` at line 1586-1601. NO FALLBACK directories are used - logging will fail if this directory doesn't exist.

All scripts import and use `misp_logger.py`:
```python
from misp_logger import get_logger
logger = get_logger('script-name', 'misp:sourcetype')
logger.info("message", event_type="backup", action="start", status="success")
```

Log files are named: `{script-name}-{timestamp}.log` with automatic rotation (5 files × 20MB each).

### Installation Flow

The main installation script (`misp-install.py`) executes 10 phases with dedicated user architecture:

1. **Dependencies** - Install Docker and system packages
2. **Docker Group** - Add misp-owner user to docker group
3. **Clone Repository** - Clone MISP-docker from GitHub
4. **Cleanup** - Remove previous MISP installation (preserves logs)
5. **Directory Setup** - Create /opt/misp with proper ownership
   - **Phase 5.5**: Configure logs directory BEFORE Docker starts (critical for permissions)
6. **Configuration** - Generate .env with performance tuning
7. **SSL Certificate** - Create self-signed cert for domain
8. **DNS Configuration** - Update /etc/hosts
9. **Password Reference** - Create PASSWORDS.txt
10. **Docker Build** - Pull images and start containers (15-30 min)
11. **Initialization** - Wait for MISP init (5-10 min)
12. **Post-Install** - Generate checklist and verify permissions

**Resume Capability**: If interrupted, run with `--resume` flag to continue from last completed phase.

### Backup Strategy

- **Manual backups**: `backup-misp.py` - On-demand full backups
- **Automated backups**: `misp-backup-cron.py` - Runs via cron
  - Sunday: Full backup (retained 8 weeks)
  - Mon-Sat: Incremental backup (deleted after next Sunday)
- **Backup contents**: Database dump, .env, PASSWORDS.txt, SSL certs, docker-compose files

## Prerequisites

### v5.4 Dedicated User Architecture

**NO MANUAL SETUP REQUIRED** - The installer handles everything automatically:

1. **misp-owner System User**: Created automatically during installation
   - System user with no login shell (security best practice)
   - Follows NIST SP 800-53 AC-6 (Least Privilege)
   - Follows CIS Benchmarks 5.4.1 (Service Account Isolation)

2. **Ownership Model**:
   - `/opt/misp/` owned by `misp-owner:misp-owner`
   - `/opt/misp/logs/` has 777 permissions (allows Docker www-data + scripts to write)
   - All MISP files owned by dedicated user, not regular user account

3. **Passwordless Sudo**: Required for specific commands (see SETUP.md):
   - File operations: mkdir, chown, chmod, rm, mv, cp
   - Docker operations: docker, docker-compose
   - System operations: apt, systemctl, usermod

For CI/CD environments, see SETUP.md for sudoers configuration.

## Common Commands

### Development Workflow

```bash
# Install MISP (interactive - recommended for first-time users)
python3 misp-install.py

# Install with config file (non-interactive - CI/CD)
python3 misp-install.py --config config/misp-config.json --non-interactive

# Resume interrupted installation
python3 misp-install.py --resume

# Create manual backup
python3 scripts/backup-misp.py

# List available backups
python3 scripts/misp-restore.py --list

# Restore from backup
python3 scripts/misp-restore.py --restore latest

# Update MISP (with auto-backup)
python3 scripts/misp-update.py --all

# Uninstall MISP completely (removes misp-owner user, preserves backups)
python3 scripts/uninstall-misp.py --force

# View logs with JSON formatting
tail -f /opt/misp/logs/misp-install-*.log | jq '.'

# Check container status
cd /opt/misp && sudo docker compose ps

# View container logs
cd /opt/misp && sudo docker compose logs -f misp-core

# Verify ownership and permissions
ls -la /opt/misp
ls -la /opt/misp/logs
id misp-owner
```

### Testing

No automated test suite exists. Testing is done by:
1. Running full installation on clean Ubuntu system
2. Verifying each phase completes successfully
3. Checking MISP web interface accessibility
4. Testing backup/restore cycle
5. Reviewing JSON logs for errors

## Key Implementation Details

### Password Validation

All passwords must meet requirements (line 346-379 in misp-install.py):
- Min 12 characters
- Contains uppercase, lowercase, number, special character
- Validated via `PasswordValidator` class

### Performance Tuning

Auto-configured based on system resources (line 803-825):
- RAM < 8GB: 1024M PHP memory, 2 workers
- RAM 8-16GB: 2048M PHP memory, 4 workers
- RAM 16GB+: 4096M PHP memory, 8+ workers

Workers calculated as: `max(2, CPU_CORES)`

### Docker Group Handling

Critical flow (line 1684-1692):
1. Check if user in docker group
2. If not, add user with `sudo usermod -aG docker $USER`
3. For interactive mode: Exit and prompt user to logout/login
4. For resume mode: Skip if already past phase 2

### Cleanup Operations

During Phase 4 cleanup (line 690-745):
- **CRITICAL**: Preserve `/opt/misp/logs/` directory (logger is actively writing)
- Remove all other `/opt/misp/` contents
- Stop and remove all Docker containers
- Remove all Docker volumes
- Clean /etc/hosts entries

### Known Issues

**Docker Health Check Failure** (non-critical):
- MISP core container reports "unhealthy" despite working correctly
- Root cause: Upstream MISP-docker healthcheck uses `BASE_URL` domain which container cannot resolve internally
- Impact: None on functionality, only affects status reporting
- See KNOWN-ISSUES.md for details

## Configuration Files

### Environment Variables (.env)

Generated in Phase 6, contains:
- Build-time variables (CORE_TAG, MODULES_TAG, PHP_VER)
- Runtime variables (BASE_URL, passwords, database config)
- Performance tuning (PHP_MEMORY_LIMIT, WORKERS)
- Security settings (HSTS, X-Frame-Options)

### Config File Format

Supports JSON and YAML (requires PyYAML):
```json
{
  "server_ip": "192.168.20.193",
  "domain": "misp-dev.lan",
  "admin_email": "admin@company.com",
  "admin_org": "tKQB Enterprises",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass123!",
  "encryption_key": "auto-generated-if-blank",
  "environment": "production"
}
```

## Working with the Code

### Adding New Scripts

1. Import centralized logger: `from misp_logger import get_logger`
2. Initialize logger with sourcetype: `logger = get_logger('script-name', 'misp:category')`
3. Use structured logging with CIM fields:
   ```python
   logger.info("Operation started",
               event_type="operation",
               action="start",
               component="component-name")
   ```
4. Add script to scripts/README.md documentation
5. Ensure logs go to `/opt/misp/logs/` with rotation

### Modifying Installation Phases

Each phase is a method in `MISPInstaller` class:
- Follow naming: `phase_N_description()`
- Call `save_state(phase_num, "Phase Name")` at end
- Use `self.section_header("PHASE N: DESCRIPTION")` for consistency
- Log all operations with appropriate severity
- Handle errors gracefully with retry logic

### Environment Support

Three environment types (line 67-70):
- **development**: Debug enabled, verbose logging, lower resources
- **staging**: Production-like config for testing
- **production**: Optimized performance, security hardened (default)

### State Management

State saved after each phase in `~/.misp-install/state.json`:
```json
{
  "phase": 6,
  "phase_name": "Configuration Complete",
  "timestamp": "2025-10-13T15:30:00",
  "config": { ... }
}
```

Resume logic: Load state, skip completed phases, continue from `phase + 1`

## Security Considerations

- All credential files have 600 permissions
- Passwords stored in PASSWORDS.txt and .env (both chmod 600)
- SSL certificates auto-generated (self-signed)
- Backups contain sensitive data - stored in user home directory with 755 permissions
- No passwords in logs (only masked output to console)
- Encryption key auto-generated and must not be changed (data loss)

## Troubleshooting Common Issues

**Installation hangs at Phase 8 (Docker Build)**:
- Normal - Docker pull takes 10-20 minutes on first run
- Monitor with: `sudo docker compose ps` in separate terminal

**"Docker not in group" after installation**:
- User needs to logout/login for group membership to take effect
- Or run: `newgrp docker` in current shell

**Container shows unhealthy**:
- Known issue with upstream MISP-docker (see KNOWN-ISSUES.md)
- Does not affect functionality - MISP still works

**Logs directory missing error**:
- Critical bug - /opt/misp/logs should be created in Phase 1
- Check lines 1586-1601 in misp-install.py

## Documentation Files

- **README.md**: Main project documentation
- **README_LOGGING.md**: Centralized logging system details
- **scripts/README.md**: All scripts documentation and workflows
- **config/README.md**: Configuration file examples
- **KNOWN-ISSUES.md**: Documented issues and workarounds
- **CHANGELOG-LOGGING-UPDATE.md**: Logging migration details

## Python Dependencies

Required: Python 3.8+
```
# Core (no external dependencies for basic operation)
# Optional:
pyyaml  # For YAML config file support
```

All other functionality uses Python standard library.

---

## v5.4 Testing History & Findings (2025-10-13)

### Context: Dedicated User Architecture Implementation

This section documents the journey from v5.3 (working) to v5.4 (attempted dedicated user architecture) to help future developers understand the challenges and decisions.

### User Requirements

The user requested elimination of the "one-time setup" requirement and implementation of a dedicated system user architecture following industry security best practices:

**Key Requirements**:
1. "why can't we create user that the install runs as? like have the user misp-owner be the user created with all permissions set to that user"
2. "I want to ensure nothing runs as root as part of the project"
3. "continue. again ensure yu are using industry best practice for all changes. I want this to be a model build for using every coding best practice"
4. **CRITICAL CORRECTION**: "wait. the new misp user should be applied to the /opt/misp only. the install comes from my home directory. those permissions should not have been changed"
5. "now (using just the scripts) teardown one last time and rebuild enabling debug mode for everything... Do nothing manually. Use the scripts only."

**Security Standards Referenced**:
- NIST SP 800-53 AC-6 (Least Privilege)
- CIS Benchmarks 5.4.1 (Service Account Isolation)
- OWASP Server Security Best Practices

### Initial Implementation (FAILED)

**Approach**: Script re-executes itself as `misp-owner` user
```python
def reexecute_as_misp_user(script_path: str, args: list):
    """Re-execute this script as misp-owner user"""
    temp_script = f"/tmp/misp-install-{os.getpid()}.py"
    shutil.copy2(script_path, temp_script)
    cmd = ['sudo', '-u', MISP_USER, sys.executable, temp_script] + args
    os.execvp('sudo', cmd)
```

**Why It Failed**:
1. **Home Directory Permissions**: User's home directory (`/home/gallagher`) has 750 permissions (correct for security)
2. **Access Denied**: When script re-executed as `misp-owner`, it couldn't access files in `/home/gallagher`
3. **Error**: `/usr/bin/python3: can't open file '/home/gallagher/misp-install/misp-install/misp-install.py': [Errno 13] Permission denied`
4. **Module Import Issue**: When copied to `/tmp`, script couldn't find `misp_logger` module (ModuleNotFoundError)

**User Feedback**: User correctly identified this as a bad approach:
> "wait. the new misp user should be applied to the /opt/misp only. the install comes from my home directory. those permissions should not have been changed"

### Revised Implementation (PARTIALLY WORKING)

**Correct Approach**: Script runs as regular user, uses sudo for `/opt/misp` operations

**Architecture**:
```python
# Script runs as regular user (e.g., gallagher)
current_user = get_current_username()  # Returns: gallagher

# Create dedicated misp-owner system user
ensure_misp_user_exists()  # Creates misp-owner with --system flag

# All /opt/misp files owned by misp-owner
subprocess.run(['sudo', 'chown', '-R', 'misp-owner:misp-owner', '/opt/misp'])

# File operations use temp file + sudo pattern
temp_file = f"/tmp/.env.{os.getpid()}"
with open(temp_file, 'w') as f:
    f.write(content)
subprocess.run(['sudo', '-u', 'misp-owner', 'cp', temp_file, '/opt/misp/.env'])
subprocess.run(['sudo', 'chmod', '600', '/opt/misp/.env'])
subprocess.run(['sudo', 'chown', 'misp-owner:misp-owner', '/opt/misp/.env'])
```

**What Works**:
- ✅ User creation: `misp-owner` system user created successfully
- ✅ Phase 1 (Dependencies): Package installation works
- ✅ Phase 2 (Docker Group): Adding misp-owner to docker group works
- ✅ Phase 5 (Clone Repository): Git clone and ownership setting works
- ✅ Phase 6 (Configuration): .env file creation works with temp file pattern

**What's Broken**:
- ❌ Phase 7 (SSL Certificate): `[Errno 13] Permission denied: '/opt/misp/ssl'`
- ❌ Phase 8 (Password File): Likely will fail with same issue
- ❌ All other phases that create files/directories in `/opt/misp`

### Root Cause Analysis

**Fundamental Issue**: The script runs as regular user (`gallagher`) but `/opt/misp` is owned by `misp-owner`. Python's standard file operations (`open()`, `os.mkdir()`, `Path.mkdir()`) fail with `[Errno 13] Permission denied`.

**Pattern That Works** (Phase 6):
```python
# Write to temp location as current user
temp_file = f"/tmp/.env.{os.getpid()}"
with open(temp_file, 'w') as f:
    f.write(env_content)

# Move to final location as misp-owner
self.run_command(['sudo', '-u', MISP_USER, 'cp', temp_file, str(env_file)])
self.run_command(['sudo', 'chmod', '600', str(env_file)])
self.run_command(['sudo', 'chown', f'{MISP_USER}:{MISP_USER}', str(env_file)])

# Cleanup
os.unlink(temp_file)
```

**Pattern That Fails** (Phase 7):
```python
ssl_dir = self.misp_dir / "ssl"
ssl_dir.mkdir(parents=True, exist_ok=True)  # FAILS - Permission denied
```

### What Needs Fixing

To complete v5.4, ALL file operations in `/opt/misp` need to use the sudo pattern:

**Directory Creation** (Phase 7, etc.):
```python
# Instead of: ssl_dir.mkdir()
# Use:
self.run_command(['sudo', '-u', MISP_USER, 'mkdir', '-p', str(ssl_dir)])
self.run_command(['sudo', 'chmod', '755', str(ssl_dir)])
```

**File Writing** (Phase 8 - PASSWORDS.txt, etc.):
```python
# Use the temp file pattern from Phase 6
temp_file = f"/tmp/passwords.{os.getpid()}"
with open(temp_file, 'w') as f:
    f.write(content)
self.run_command(['sudo', '-u', MISP_USER, 'cp', temp_file, str(target_file)])
self.run_command(['sudo', 'chmod', '600', str(target_file)])
self.run_command(['sudo', 'chown', f'{MISP_USER}:{MISP_USER}', str(target_file)])
os.unlink(temp_file)
```

**Affected Phases**:
- Phase 7: SSL Certificate (directory + file creation)
- Phase 8: Password File (file creation)
- Any other phases that write to `/opt/misp` (need full audit)

### Testing Commands & Results

**Test Environment**: Ubuntu system with clean installation

**Cleanup Command**:
```bash
python3 scripts/uninstall-misp.py --force
```
Result: ✅ Successfully removes containers, /opt/misp, and misp-owner user

**Installation Command**:
```bash
python3 misp-install.py --config config/test-debug.json --non-interactive 2>&1 | tee /tmp/final-test.log
```

**Test Results**:
```
✓ Phase 1: Dependencies - PASSED
✓ Phase 2: Docker Group - PASSED
✓ Phase 5: Clone Repository - PASSED
✓ Phase 6: Configuration - PASSED (after fix)
❌ Phase 7: SSL Certificate - FAILED
   Error: [Errno 13] Permission denied: '/opt/misp/ssl'
   Retries: 3/3 attempts failed
```

**Log Location**: `/tmp/final-test.log`

### Key Learnings

1. **Unix Permissions Are Strict**: Cannot mix user identities without proper privilege escalation
2. **Home Directory Security**: User home directories should remain 750 (correct for security)
3. **Sudo Pattern Required**: When dedicated user owns files, all operations need sudo
4. **Python Limitations**: Standard Python file operations don't understand sudo - must use subprocess
5. **Temp File Approach**: Writing to /tmp first, then moving with sudo is the correct pattern

### Files Modified in v5.4

**Core Files**:
- `misp-install.py` - Added user creation, Phase 6 fixed, Phase 7+ broken
- `scripts/uninstall-misp.py` - Enhanced to remove misp-owner user
- `scripts/backup-misp.py` - Updated SSL backup to use sudo

**Documentation Created**:
- `docs/SECURITY_ARCHITECTURE.md` - 480 lines documenting dedicated user approach
- `SETUP.md` - Complete rewrite (296 lines) for v5.4 architecture
- `README.md` - Removed one-time setup section, added security architecture
- `docs/testing_and_updates/CHANGELOG.md` - v5.4 release notes (156 lines)

### Decision Point

**Option A: Complete v5.4 Implementation**
- Fix Phase 7+ by applying temp file + sudo pattern to ALL file operations
- Systematic audit of every `open()`, `mkdir()`, file write in `/opt/misp`
- Estimated effort: 3-5 hours of careful testing
- Risk: Medium (may discover more edge cases)

**Option B: Revert to v5.3**
- v5.3 was working correctly with one-time setup
- Faster path to stable release
- User performs one-time: `sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp`
- Risk: Low (known working state)

**Recommendation**: Given the partial implementation and testing complexity, Option B (revert) is safer for immediate release. The v5.4 dedicated user architecture is sound in principle but requires systematic completion and extensive testing.

### Commands for Future Testing

**Clean System**:
```bash
python3 scripts/uninstall-misp.py --force
```

**Full Install Test**:
```bash
python3 misp-install.py --config config/test-debug.json --non-interactive 2>&1 | tee /tmp/install-test.log
```

**Check Ownership**:
```bash
ls -la /opt/misp
namei -l /opt/misp/ssl
```

**Check User**:
```bash
id misp-owner
groups misp-owner
```

**Monitor Logs**:
```bash
tail -f /tmp/install-test.log
```

### Related Documentation

- `docs/SECURITY_ARCHITECTURE.md` - Comprehensive security documentation for v5.4
- `SETUP.md` - Setup guide for dedicated user architecture
- `docs/testing_and_updates/CHANGELOG.md` - v5.4 release notes

### v5.4 Completion (October 2025)

**Status**: ✅ COMPLETE AND PRODUCTION READY

After systematic debugging and permission architecture fixes, v5.4 was successfully completed:

#### Final Fixes Applied

1. **Phase 5.5 - Log Directory Timing** (lines 819-837):
   - **Problem**: Docker mounts `./logs/` and creates it as `www-data:www-data` with 770 permissions
   - **Solution**: Create log directory BEFORE Docker starts in Phase 5.5
   - **Implementation**:
     ```python
     logs_dir = self.misp_dir / "logs"
     self.run_command(['sudo', '-u', MISP_USER, 'mkdir', '-p', str(logs_dir)])
     self.run_command(['sudo', 'chmod', '777', str(logs_dir)])
     self.run_command(['sudo', 'chown', f'{MISP_USER}:{MISP_USER}', str(logs_dir)])
     ```
   - **Result**: Both Docker (www-data) and scripts (current user) can write logs

2. **All Phases Sudo Pattern Applied**:
   - Phase 7 (SSL Certificate): Fixed directory + file creation
   - Phase 8 (Password File): Fixed file creation with temp file pattern
   - Phase 10.6: Kept as safety net (redundant but harmless)
   - All file operations use temp file + sudo pattern

3. **Documentation Cleanup** (October 13, 2025):
   - ✅ Removed duplicate scripts: `backup-misp.sh`, `uninstall-misp.sh`
   - ✅ Created `SCRIPTS.md`: Comprehensive 14KB inventory of all 8 Python scripts
   - ✅ Created `docs/archive/`: Moved 3 outdated files (INDEX.md, COMPLETE-FILE-LAYOUT.md, READY-TO-RUN-SETUP.md)
   - ✅ Created `docs/README.md`: Directory guide with archive explanation
   - ✅ Updated 15+ documentation files: v5.0→v5.4, 775→777, .sh→.py
   - ✅ Updated `KNOWN-ISSUES.md`: All v5.4 issues resolved

4. **Git Commits**:
   - `a431f0e` - v5.4 dedicated user architecture implementation
   - `a6d94ef` - Documentation updates to v5.4 standards
   - `00eb459` - Archive outdated documentation

#### Production Validation

**Test Environment**: Clean Ubuntu system
**Test Method**: Full uninstall + fresh install with debug config

**Results**:
- ✅ All 10 phases complete successfully
- ✅ Log directory permissions correct (777, misp-owner:misp-owner)
- ✅ Docker containers start with proper file ownership
- ✅ Both www-data and scripts can write to logs
- ✅ No manual setup required
- ✅ Resume functionality works
- ✅ Uninstall cleanly removes misp-owner user

#### Architecture Summary

**Final v5.4 Architecture**:
- Script runs as regular user (e.g., `gallagher`)
- Creates dedicated `misp-owner` system user (no login shell)
- All `/opt/misp/` files owned by `misp-owner:misp-owner`
- Log directory has 777 permissions (allows Docker + scripts to write)
- All file operations use sudo with temp file pattern
- Follows NIST SP 800-53 AC-6, CIS Benchmarks 5.4.1, OWASP best practices

**Production Ready**: v5.4 is stable, fully tested, and ready for production deployment.

---

## Future Development Roadmap

### Next Feature: Public Signed Certificate Support

**Priority**: High
**Target Version**: 5.5
**Status**: Planned

#### Feature Overview

Add support for using public signed certificates (Let's Encrypt, commercial CA) instead of self-signed certificates, with automatic integration into the existing nginx setup in Docker containers.

#### Requirements

1. **Certificate Sources**:
   - Let's Encrypt (automated via certbot or ACME client)
   - Commercial CA certificates (manual upload)
   - Custom CA certificates (enterprise environments)

2. **Nginx Integration**:
   - Automatic configuration of nginx in MISP Docker containers
   - Certificate path mapping from host to container
   - Certificate renewal automation (for Let's Encrypt)
   - Graceful container reload after certificate update

3. **Configuration Options**:
   ```json
   {
     "ssl_mode": "letsencrypt|commercial|self-signed",
     "ssl_email": "admin@company.com",
     "ssl_cert_path": "/path/to/cert.pem",
     "ssl_key_path": "/path/to/key.pem",
     "ssl_chain_path": "/path/to/chain.pem",
     "ssl_auto_renew": true
   }
   ```

#### Implementation Plan

**Phase 1: Certificate Mode Detection**
- Add `ssl_mode` configuration option to config files
- Detect certificate type (self-signed vs public)
- Validate certificate paths and permissions

**Phase 2: Let's Encrypt Integration**
- Install certbot package during Phase 1 (Dependencies)
- Add Phase 7.5: Let's Encrypt Certificate Acquisition
  - Use certbot with standalone or webroot mode
  - Store certificates in `/opt/misp/ssl/letsencrypt/`
  - Set proper permissions (600 for key, 644 for cert)
- Configure certbot renewal cron job

**Phase 3: Commercial Certificate Support**
- Add validation for user-provided certificate files
- Copy certificates to `/opt/misp/ssl/commercial/`
- Verify certificate chain completeness
- Check certificate expiration and warn if < 30 days

**Phase 4: Nginx Configuration**
- Update docker-compose.yml to mount certificate directory:
  ```yaml
  volumes:
    - ./ssl:/etc/nginx/certs:ro
  ```
- Generate nginx config snippets for each certificate type
- Update MISP nginx configuration in container
- Test nginx config before reload

**Phase 5: Certificate Renewal Automation**
- Create `scripts/renew-certificates.py`
- Add cron job for automatic renewal (weekly check)
- Implement container reload logic after renewal
- Add logging and alerting for renewal failures

#### Technical Considerations

1. **Docker Volume Mounts**:
   - Certificates must be readable by nginx (www-data) in container
   - Use `:ro` (read-only) mount for security
   - Path consistency between host and container

2. **Let's Encrypt Challenges**:
   - HTTP-01: Requires port 80 accessible (webroot or standalone)
   - DNS-01: Requires DNS API access (more complex but works with firewall)
   - TLS-ALPN-01: Requires port 443 accessible

3. **Security Best Practices**:
   - Private keys: 600 permissions, owned by misp-owner
   - Certificates: 644 permissions, owned by misp-owner
   - No keys in logs or console output
   - Secure deletion of old certificates

4. **Backward Compatibility**:
   - Default behavior: Self-signed certificate (v5.4 behavior)
   - No breaking changes to existing installations
   - Optional feature activated via config

#### Files to Modify

**Core Installation** (`misp-install.py`):
- Line ~820: Add Phase 7.5 for certificate acquisition
- Line ~1150: Update docker-compose.yml generation
- Line ~400: Add certificate validation methods
- Add `CertificateManager` class for certificate operations

**New Scripts**:
- `scripts/renew-certificates.py` - Certificate renewal automation
- `scripts/update-certificates.py` - Manual certificate update

**Configuration Templates**:
- `config/misp-config.yaml.example` - Add SSL mode options
- `config/misp-config-production.yaml` - Add Let's Encrypt example

**Documentation**:
- `docs/SSL-CERTIFICATES.md` - New guide for certificate management
- `docs/LETSENCRYPT-SETUP.md` - Let's Encrypt specific guide
- `README.md` - Update SSL section
- `docs/TROUBLESHOOTING.md` - Add certificate troubleshooting

#### Testing Requirements

1. **Let's Encrypt Test**:
   - Use Let's Encrypt staging environment for testing
   - Verify certificate acquisition
   - Test renewal process
   - Validate nginx configuration

2. **Commercial Certificate Test**:
   - Test with various CA formats (PEM, DER)
   - Validate certificate chain handling
   - Test with wildcard certificates
   - Verify expiration warnings

3. **Upgrade Test**:
   - Existing v5.4 installation upgrades cleanly
   - Self-signed certificates remain functional
   - Migration path to public certificates documented

#### Success Metrics

- ✅ Let's Encrypt certificates automatically acquired and installed
- ✅ Automatic renewal working (90-day cycle)
- ✅ Commercial certificates supported with manual upload
- ✅ Nginx reloads gracefully after certificate changes
- ✅ No breaking changes to existing installations
- ✅ Complete documentation for all certificate types

#### Related Issues

- KNOWN-ISSUES.md: Self-signed certificate browser warnings
- User feedback: "Need trusted certificates for production"
- Security compliance: Many organizations require CA-signed certificates

#### Additional Features (Optional)

- Certificate monitoring dashboard
- Slack/email alerts for certificate expiration
- Multi-domain certificate support
- Certificate backup in misp-backup.py
- Certificate restore in misp-restore.py

---

## Script Inventory (v5.4)

All Python scripts in this project:

1. **misp-install.py** - Main installation script (1850+ lines)
2. **misp_install_gui.py** - GUI installer (v1.0 - Textual framework)
3. **scripts/backup-misp.py** - Manual backup script (v2.0)
4. **scripts/uninstall-misp.py** - Uninstallation script (v2.0)
5. **scripts/misp-backup-cron.py** - Automated backup for cron (v2.0)
6. **scripts/misp-restore.py** - Backup restoration script (v2.0)
7. **scripts/misp-update.py** - MISP update automation (v2.0)
8. **scripts/verify-installation.py** - Post-install verification (v1.0)
9. **misp_logger.py** - Centralized logging module (v1.0)

**Removed Scripts** (v5.4 cleanup):
- `scripts/backup-misp.sh` - Duplicate of .py version
- `scripts/uninstall-misp.sh` - Duplicate of .py version

See `SCRIPTS.md` for complete documentation of all scripts.

## GUI Installer (v1.0 - October 2025)

**Status**: ✅ PRODUCTION READY

The GUI installer provides a modern graphical alternative to the CLI installer using the Textual framework. It generates configuration files compatible with `misp-install.py`.

### Quick Start

```bash
# Automated installation (recommended - handles everything)
cd ~/misp-install/misp-install
./install-gui.sh

# Manual installation (Ubuntu 24.04+)
pipx install .
misp-install-gui

# Run directly without installing
python3 misp_install_gui.py

# Web browser mode
textual serve misp_install_gui.py
```

### Key Features

- ✨ Multi-step wizard with 5 screens (Welcome, Network, Security, Environment, Review)
- 🔒 Real-time password strength validation (12+ chars, mixed case, numbers, special)
- 🎲 Auto-generate secure passwords (cryptographically secure)
- 📋 Clipboard paste support (Ctrl+V) - works with pyperclip + xclip
- 🌐 Runs in terminal OR web browser (same code, dual mode)
- 💾 Configuration file generation (JSON format)
- ⌨️ Full keyboard navigation (Tab, Arrow keys, Enter, Esc)
- 🎨 Dark/Light theme toggle (press 'd' key)

### Architecture

**Design Pattern**: Frontend/Backend Separation
- **Frontend**: Textual TUI framework (Python)
  - Handles user interaction, form validation, UI rendering
  - Generates JSON config file
  - No direct MISP installation logic
- **Backend**: `misp-install.py --config [file]`
  - Reads GUI-generated config
  - Performs actual installation (all 10 phases)
  - No changes needed to support GUI

**Benefits of This Approach**:
1. Clean separation of concerns
2. GUI and CLI share same installation backend
3. Config files are portable (use in CI/CD)
4. Easier to maintain (UI bugs don't affect installation)

### Implementation Details

**Wizard Flow**:
```python
# misp_install_gui.py structure
class MISPInstallApp(App):
    SCREENS = {
        "welcome": WelcomeScreen,      # Step 1: Introduction
        "network": NetworkScreen,      # Step 2: IP, domain, email, org
        "security": SecurityScreen,    # Step 3: Passwords
        "environment": EnvironmentScreen,  # Step 4: Dev/Staging/Prod
        "review": ReviewScreen,        # Step 5: Confirm & save
    }

    def on_mount(self):
        self.push_screen("welcome")

    def save_config(self):
        config = {
            "server_ip": self.server_ip,
            "domain": self.domain,
            # ... all fields
        }
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
```

**Password Validation**:
```python
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password meets requirements"""
    if len(password) < 12:
        return False, "Must be at least 12 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Must contain lowercase letter"
    if not re.search(r'\d', password):
        return False, "Must contain number"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        return False, "Must contain special character"
    return True, "Strong password"
```

**Clipboard Integration**:
```python
import pyperclip  # Requires xclip on Linux

def action_paste_clipboard(self):
    """Handle Ctrl+V paste"""
    clipboard_text = pyperclip.paste()
    focused = self.focused
    if isinstance(focused, Input):
        # Insert at cursor position
        current = focused.value
        cursor = focused.cursor_position
        focused.value = current[:cursor] + clipboard_text + current[cursor:]
        focused.cursor_position = cursor + len(clipboard_text)
```

### Files & Dependencies

**Core Files**:
- `misp_install_gui.py` - Main GUI application (800+ lines)
- `install-gui.sh` - Bootstrap script (handles deps, PATH, installation)
- `setup.py` - pip/pipx packaging configuration
- `requirements-gui.txt` - Python dependencies list
- `check_deps.py` - Dependency verification script
- `test_clipboard.py` - Clipboard functionality tester
- `docs/GUI_INSTALLER.md` - Complete user documentation

**Dependencies**:
```python
# setup.py - install_requires
textual>=0.45.0        # TUI framework
textual-dev>=1.2.0     # Development tools (textual serve)
pyperclip>=1.8.0       # Clipboard support
```

**System Dependencies** (Ubuntu):
```bash
xclip          # Linux clipboard utility (required for pyperclip)
pipx           # Python app installer (Ubuntu 24.04+)
python3.8+     # Minimum Python version
```

### Installation Methods

**Method 1: Automated (Recommended)**
```bash
./install-gui.sh
# Installs: xclip, pipx, misp-installer-gui package
# Configures: PATH automatically
# Verifies: Command works (--version test)
```

**Method 2: pipx (Manual)**
```bash
sudo apt install xclip pipx
pipx install .
pipx ensurepath
misp-install-gui
```

**Method 3: Direct Run (Development)**
```bash
pip install -r requirements-gui.txt
python3 misp_install_gui.py
```

**Method 4: Web Browser Mode**
```bash
textual serve misp_install_gui.py --port 8080
# Open: http://localhost:8080
```

### Configuration Output

**Generated Config File Format**:
```json
{
  "server_ip": "192.168.20.193",
  "domain": "misp-dev.lan",
  "admin_email": "admin@company.com",
  "admin_org": "tKQB Enterprises",
  "admin_password": "Generated_Or_Manual_123!",
  "mysql_password": "DbPass456!@#",
  "gpg_passphrase": "GpgPass789!@#",
  "environment": "production"
}
```

**File Location**: `config/misp-gui-config-YYYYMMDD_HHMMSS.json`
**Permissions**: 600 (owner read/write only)

### Usage with CLI Installer

```bash
# 1. Generate config via GUI
misp-install-gui
# (Save config, exit without installing)

# 2. Use config with CLI installer
python3 misp-install.py --config config/misp-gui-config-20251014_120000.json --non-interactive

# Perfect for:
# - CI/CD pipelines
# - Automated deployments
# - Testing multiple configurations
# - Ansible/Terraform integration
```

### Troubleshooting Common Issues

**Issue 1: "textual not installed" after pipx install**
- **Cause**: pipx reused old venv without new dependencies
- **Fix**: `install-gui.sh` now force-removes venv before reinstall
- **Verify**: `misp-install-gui --version` should work

**Issue 2: Clipboard paste (Ctrl+V) not working**
- **Cause**: xclip not installed or pyperclip missing
- **Fix**: `sudo apt install xclip` then `pipx reinstall .`
- **Test**: `python3 test_clipboard.py`

**Issue 3: pipx PATH warning**
- **Cause**: `~/.local/bin` not in PATH
- **Fix**: `install-gui.sh` runs `pipx ensurepath --force`
- **Manual**: `export PATH="$HOME/.local/bin:$PATH"` or restart shell

**Issue 4: Web mode not working**
- **Cause**: textual-dev not installed
- **Fix**: `pip install textual-dev` or `pipx install textual-dev`
- **Alternative**: `python3 -m textual serve misp_install_gui.py`

**Issue 5: Permission denied saving config**
- **Cause**: config/ directory doesn't exist or not writable
- **Fix**: `mkdir -p config && chmod 755 config`

### Development Notes

**Adding New Screens**:
1. Create new screen class in `misp_install_gui.py`
2. Add to `SCREENS` dictionary
3. Implement `compose()` method for UI
4. Add navigation buttons (Back/Next)
5. Update data model with new fields
6. Test navigation flow

**Modifying Validation**:
- All validation in `validate_*()` functions
- Real-time feedback via `watch_*()` methods
- Error messages shown inline below fields
- Validation runs on every keystroke

**Testing Workflow**:
```bash
# Quick test
python3 misp_install_gui.py

# Test clipboard
python3 test_clipboard.py

# Test dependencies
python3 check_deps.py

# Test web mode
textual serve misp_install_gui.py --port 8000

# Full install test
./install-gui.sh
```

**Keyboard Shortcuts** (for users):
- `q` - Quit application
- `d` - Toggle dark/light theme
- `Ctrl+V` - Paste from clipboard
- `Tab` - Next field
- `Shift+Tab` - Previous field
- `Enter` - Activate button
- `Esc` - Go back

### Integration with v5.4 Architecture

The GUI installer is **completely independent** of the v5.4 dedicated user architecture:

- ✅ GUI runs as regular user (no sudo needed for GUI itself)
- ✅ Generates config file in user home directory
- ✅ CLI installer handles all sudo operations when using config
- ✅ No conflicts with misp-owner user creation
- ✅ Works with any installation method (interactive or non-interactive)

**Workflow**:
1. User runs GUI installer (as regular user)
2. GUI generates config file (stored in `~/misp-install/config/`)
3. User runs CLI installer with config (handles misp-owner creation)
4. CLI installer uses sudo for `/opt/misp` operations (v5.4 architecture)

### Future Enhancements (Planned)

**v1.1**:
- Real-time installation progress integration
- Log streaming from misp-install.py backend
- Resume capability after interruption

**v1.2**:
- Performance tuning screen (PHP memory, workers)
- Optional integrations (Splunk, Security Onion, Azure Key Vault)
- System resource auto-detection

**v2.0**:
- Multi-language support (i18n)
- Configuration templates
- Custom branding
- Authentication for web mode

For complete user documentation, see `docs/GUI_INSTALLER.md`.
