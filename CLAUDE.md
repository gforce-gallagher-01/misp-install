# CLAUDE.md

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a professional-grade Python automation suite for deploying and managing MISP (Malware Information Sharing Platform) via Docker. The suite includes installation, backup, restore, update, and uninstallation tools with enterprise-grade features.

**Organization**: tKQB Enterprises
**Current Version**: 5.5 (STABLE - PRODUCTION READY)
**Status**: v5.4 dedicated user architecture + v5.5 API integration
**Last Updated**: 2025-10-14

## Quick Start

```bash
# Install MISP (interactive)
python3 misp-install.py

# Install with config file (CI/CD)
python3 misp-install.py --config config/misp-config.json --non-interactive

# Resume interrupted installation
python3 misp-install.py --resume

# GUI installer
./install-gui.sh
misp-install-gui
```

## Core Architecture Principles

1. **Centralized JSON Logging** - All scripts use `/opt/misp/logs/` with CIM field names for SIEM integration
2. **State Management** - Resume capability via `~/.misp-install/state.json`
3. **Phase-Based Execution** - 12 numbered phases that can be resumed if interrupted
4. **Docker-First** - All MISP components run in Docker containers
5. **Dedicated User** - v5.4 uses `misp-owner` system user for security isolation

## Documentation Index

### Core Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture, logging, directory structure, design principles
- **[INSTALLATION.md](docs/INSTALLATION.md)** - Installation phases, resume capability, system requirements
- **[README.md](README.md)** - Main project documentation and getting started guide
- **[SETUP.md](SETUP.md)** - Sudoers configuration for v5.4 architecture

### Feature Guides

- **[GUI_INSTALLER.md](docs/GUI_INSTALLER.md)** - GUI installer guide (Textual framework)
- **[API_USAGE.md](docs/API_USAGE.md)** - MISP REST API usage and helper module
- **[NERC_CIP_CONFIGURATION.md](docs/NERC_CIP_CONFIGURATION.md)** - Energy sector compliance guide

### Technical References

- **[README_LOGGING.md](README_LOGGING.md)** - Centralized logging system details
- **[SCRIPTS.md](SCRIPTS.md)** - Complete script inventory and usage
- **[KNOWN-ISSUES.md](KNOWN-ISSUES.md)** - Known issues and workarounds
- **[TODO.md](TODO.md)** - Planned features and roadmap

## Critical Directory Structure

```
/opt/misp/                  # Main MISP installation
  ├── logs/                 # Centralized JSON logs (MUST EXIST before logging starts)
  ├── .env                  # Docker environment config (chmod 600)
  ├── PASSWORDS.txt         # All credentials (chmod 600)
  ├── ssl/                  # SSL certificates
  └── docker-compose.yml    # Docker configuration

~/misp-backups/            # Backup storage (preserved during uninstall)
~/.misp-install/           # Installation state and metadata
```

**⚠️ CRITICAL**: `/opt/misp/logs/` must exist BEFORE any logger initialization. Created in Phase 1, line 1586-1601.

## v5.4 Dedicated User Architecture

**System User**: `misp-owner` (created automatically)

**Ownership Model**:
- `/opt/misp/` owned by `misp-owner:misp-owner`
- `/opt/misp/logs/` has 777 permissions (Docker www-data + scripts write here)
- Scripts run as regular user, use sudo for `/opt/misp` operations

**File Operation Pattern** (temp file + sudo):
```python
# Write to temp location as current user
temp_file = f"/tmp/.env.{os.getpid()}"
with open(temp_file, 'w') as f:
    f.write(content)

# Move to final location as misp-owner
subprocess.run(['sudo', '-u', 'misp-owner', 'cp', temp_file, '/opt/misp/.env'])
subprocess.run(['sudo', 'chmod', '600', '/opt/misp/.env'])
subprocess.run(['sudo', 'chown', 'misp-owner:misp-owner', '/opt/misp/.env'])

# Cleanup
os.unlink(temp_file)
```

## Installation Phases (12 Total)

1. **Dependencies** - Install Docker, create misp-owner user, create logs directory
2. **Docker Group** - Add misp-owner to docker group
3. **Clone Repository** - Clone MISP-docker from GitHub
4. **Cleanup** - Remove previous installation (preserves logs)
5. **Directory Setup** - Create /opt/misp with proper ownership
   - **Phase 5.5**: Configure logs directory BEFORE Docker starts (critical!)
6. **Configuration** - Generate .env with performance tuning
7. **SSL Certificate** - Create self-signed cert
8. **DNS Configuration** - Update /etc/hosts
9. **Password Reference** - Create PASSWORDS.txt
10. **Docker Build** - Pull images and start containers (15-30 min)
11. **Initialization** - Wait for MISP to be ready (5-10 min)
    - **Phase 11.5**: Generate API key for automation (v5.5)
12. **Post-Install** - Verify and display credentials

**Total Time**: 30-50 minutes (first install), 10-15 minutes (subsequent)

**See**: [INSTALLATION.md](docs/INSTALLATION.md) for detailed phase documentation

## Logging System

**Centralized Module**: `misp_logger.py`

**Usage Pattern**:
```python
from misp_logger import get_logger

logger = get_logger('script-name', 'misp:sourcetype')
logger.info("Operation started",
            event_type="operation",
            action="start",
            component="component-name",
            status="success")
```

**Log Location**: `/opt/misp/logs/{script-name}-{timestamp}.log`

**Format**: JSON with CIM field names for SIEM integration

**See**: [ARCHITECTURE.md](docs/ARCHITECTURE.md#logging-architecture) for complete logging details

## Working with the Code

### Coding Best Practices

**⚠️ ALWAYS Follow DRY Principle** (Don't Repeat Yourself):

- **NO code duplication** - Extract common functionality into reusable functions/classes
- **Centralize constants** - Use configuration classes (e.g., `UtilitiesSectorConfig`)
- **Reuse existing modules** - Import from `misp_logger.py`, `misp_api.py`, etc.
- **Extract repeated patterns** - Create helper functions for common operations
- **Single source of truth** - One definition, referenced everywhere

**Examples of DRY in this project**:
- ✅ `misp_logger.py` - Centralized logging (NOT repeated in each script)
- ✅ `misp_api.py` - API helpers (NOT duplicated across scripts)
- ✅ Configuration classes - Constants defined once (NOT hardcoded everywhere)
- ✅ Temp file pattern - Documented once, referenced everywhere

**Anti-patterns to avoid**:
- ❌ Copy-pasting code between scripts
- ❌ Hardcoding values in multiple places
- ❌ Reimplementing existing functionality
- ❌ Duplicating validation logic

### Adding New Scripts

1. Import centralized logger: `from misp_logger import get_logger`
2. Initialize with sourcetype: `logger = get_logger('script-name', 'misp:category')`
3. Use structured logging with CIM fields
4. **Follow DRY**: Extract common patterns into reusable functions
5. Add to [SCRIPTS.md](SCRIPTS.md) documentation
6. Ensure logs go to `/opt/misp/logs/` with rotation

### Modifying Installation Phases

Each phase is a method in `MISPInstaller` class:

- Follow naming: `phase_N_description()`
- Call `save_state(phase_num, "Phase Name")` at end
- Use `self.section_header("PHASE N: DESCRIPTION")` for consistency
- Log all operations with appropriate severity
- Handle errors gracefully with retry logic

### Using MISP REST API

**API Helper Module**: `misp_api.py`

```python
from misp_api import get_api_key, get_misp_url, test_connection

# Auto-detect API key from .env, PASSWORDS.txt, or environment
api_key = get_api_key()
misp_url = get_misp_url()

# Test connection
if test_connection(misp_url, api_key):
    print("Connected to MISP successfully")
```

**See**: [API_USAGE.md](docs/API_USAGE.md) for complete API documentation

## Common Commands

```bash
# Installation
python3 misp-install.py                                    # Interactive
python3 misp-install.py --config config.json --non-interactive  # CI/CD
python3 misp-install.py --resume                           # Resume after interruption

# Management
python3 scripts/backup-misp.py                             # Manual backup
python3 scripts/misp-restore.py --list                     # List backups
python3 scripts/misp-restore.py --restore latest           # Restore backup
python3 scripts/misp-update.py --all                       # Update MISP
python3 scripts/uninstall-misp.py --force                  # Uninstall

# Post-Install Configuration
python3 scripts/configure-misp-nerc-cip.py                 # NERC CIP compliance
python3 scripts/misp-setup-complete.py --api-key KEY       # Complete setup
python3 scripts/check-misp-feeds-api.py --api-key KEY      # Check feeds

# Monitoring
tail -f /opt/misp/logs/misp-install-*.log | jq '.'        # View logs
cd /opt/misp && sudo docker compose ps                     # Container status
cd /opt/misp && sudo docker compose logs -f misp-core      # Container logs
```

## Configuration Files

### Environment Variables (.env)

Generated in Phase 6, contains:
- Build-time variables (CORE_TAG, MODULES_TAG, PHP_VER)
- Runtime variables (BASE_URL, passwords, database config)
- Performance tuning (PHP_MEMORY_LIMIT, WORKERS)
- Security settings (HSTS, X-Frame-Options)
- **MISP_API_KEY** (v5.5 - generated in Phase 11.5)

### Config File Format

Supports JSON and YAML:

```json
{
  "server_ip": "192.168.20.193",
  "domain": "misp-dev.lan",
  "admin_email": "admin@company.com",
  "admin_org": "tKQB Enterprises",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "encryption_key": "auto-generated-if-blank",
  "environment": "production"
}
```

### Environment Types

- **development**: Debug enabled, verbose logging, lower resources
- **staging**: Production-like config for testing
- **production**: Optimized performance, security hardened (default)

## Security Considerations

- All credential files have 600 permissions
- Passwords stored in PASSWORDS.txt and .env (both chmod 600)
- SSL certificates auto-generated (self-signed by default)
- Backups contain sensitive data - stored in user home directory
- No passwords in logs (only masked output to console)
- Encryption key auto-generated and must not be changed (data loss)
- Follows NIST SP 800-53 AC-6, CIS Benchmarks 5.4.1, OWASP best practices

**See**: [ARCHITECTURE.md](docs/ARCHITECTURE.md#security-considerations) for detailed security documentation

## Script Inventory

**Core Scripts** (4):

1. `misp-install.py` - Main installation (1850+ lines)
2. `misp_install_gui.py` - GUI installer (Textual framework)
3. `misp_logger.py` - Centralized logging module
4. `misp_api.py` - API helper module (v5.5)

**Management Scripts** (6):

5. `scripts/backup-misp.py` - Manual backup
6. `scripts/misp-backup-cron.py` - Automated backup for cron
7. `scripts/misp-restore.py` - Backup restoration
8. `scripts/misp-update.py` - MISP updates
9. `scripts/uninstall-misp.py` - Complete uninstall
10. `scripts/verify-installation.py` - Post-install verification

**Configuration Scripts** (6):

11. `scripts/configure-misp-nerc-cip.py` - NERC CIP compliance
12. `scripts/misp-setup-complete.py` - Complete setup orchestrator (v5.5)
13. `scripts/populate-misp-news.py` - Populate security news
14. `scripts/check-misp-feeds-api.py` - Check feed status (v5.5 API)
15. `scripts/add-nerc-cip-news-feeds-api.py` - Add news feeds (v5.5 API)
16. `scripts/list-misp-communities.py` - Discover threat intel communities

**See**: [SCRIPTS.md](SCRIPTS.md) for complete inventory and usage

## Troubleshooting Common Issues

**Installation hangs at Phase 10 (Docker Build)**:
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

**Permission denied during installation**:
- Verify file operations use temp file + sudo pattern (v5.4)
- Check /opt/misp ownership: `ls -la /opt/misp | grep misp-owner`

**See**: [INSTALLATION.md](docs/INSTALLATION.md#common-installation-issues) for complete troubleshooting guide

## Python Dependencies

**Required**: Python 3.8+

**Core Dependencies** (no external deps for basic operation):
- Standard library only

**Optional Dependencies**:
- `pyyaml` - For YAML config file support
- `psutil` - For system resource detection
- `requests` - For API operations (v5.5)

**GUI Dependencies**:
- `textual>=0.45.0` - TUI framework
- `textual-dev>=1.2.0` - Development tools
- `pyperclip>=1.8.0` - Clipboard support
- `xclip` - Linux clipboard utility (system package)

## Key Features by Version

### v5.4 (Stable)
- ✅ Dedicated user architecture (misp-owner)
- ✅ Phase-based installation with resume capability
- ✅ Centralized JSON logging with CIM fields
- ✅ GUI installer (Textual framework)
- ✅ NERC CIP compliance scripts
- ✅ Automated backup/restore
- ✅ Feed management scripts

### v5.5 (Current)
- ✅ Automatic API key generation (Phase 11.5)
- ✅ API helper module (misp_api.py)
- ✅ API-based scripts (feeds, news, setup)
- ✅ Complete setup orchestrator (misp-setup-complete.py)
- ✅ Comprehensive API documentation (docs/API_USAGE.md)

### Planned (v6.0)
- ⏳ Splunk Cloud integration
- ⏳ Security Onion integration
- ⏳ Azure Key Vault secrets management
- ⏳ Let's Encrypt certificate support
- ⏳ GUI post-installation setup integration

**See**: [TODO.md](TODO.md) for complete roadmap

## Testing

No automated test suite exists. Testing is done by:

1. Running full installation on clean Ubuntu system
2. Verifying each phase completes successfully
3. Checking MISP web interface accessibility
4. Testing backup/restore cycle
5. Reviewing JSON logs for errors

**Test Commands**:
```bash
# Clean system
python3 scripts/uninstall-misp.py --force

# Full install test
python3 misp-install.py --config config/test-debug.json --non-interactive 2>&1 | tee /tmp/install-test.log

# Verify ownership
ls -la /opt/misp
id misp-owner
groups misp-owner
```

## Quick Reference

### File Locations

- **Logs**: `/opt/misp/logs/`
- **Credentials**: `/opt/misp/PASSWORDS.txt`, `/opt/misp/.env`
- **Backups**: `~/misp-backups/`
- **State**: `~/.misp-install/state.json`
- **SSL**: `/opt/misp/ssl/`

### Important Line Numbers (misp-install.py)

- Line 346-379: Password validation
- Line 803-825: Performance tuning
- Line 1586-1601: Log directory creation (CRITICAL)
- Line 1684-1692: Docker group handling

### Key Classes

- `MISPInstaller` - Main installation orchestrator
- `PasswordValidator` - Password strength validation
- `Logger` (misp_logger.py) - Centralized logging

### State Machine

- Phase 0: Not started
- Phase 1-11: In progress
- Phase 12: Complete
- Resume: Load state, skip to phase N+1

## Getting Help

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Check [KNOWN-ISSUES.md](KNOWN-ISSUES.md)
- **Logs**: `/opt/misp/logs/` with JSON format
- **Community**: MISP Project (https://www.misp-project.org/)

## Related Projects

- **MISP**: https://github.com/MISP/MISP
- **MISP-docker**: https://github.com/MISP/misp-docker
- **Textual**: https://github.com/Textualize/textual

---

**Last Updated**: 2025-10-14
**Maintainer**: tKQB Enterprises
**Version**: 5.5 (API Integration Release)

**📚 For detailed information, see the comprehensive documentation in [docs/](docs/)**
