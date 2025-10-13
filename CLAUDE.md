# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a professional-grade Python automation suite for deploying and managing MISP (Malware Information Sharing Platform) via Docker. The suite includes installation, backup, restore, update, and uninstallation tools with enterprise-grade features.

**Organization**: tKQB Enterprises
**Current Version**: 5.2 (misp-install.py)

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

The main installation script (`misp-install.py`) executes 10 phases:

1. **Dependencies** - Install Docker and system packages
2. **Docker Group** - Add user to docker group
3. **Clone Repository** - Clone MISP-docker from GitHub
4. **Configuration** - Generate .env with performance tuning
5. **SSL Certificate** - Create self-signed cert for domain
6. **DNS Configuration** - Update /etc/hosts
7. **Password Reference** - Create PASSWORDS.txt
8. **Docker Build** - Pull images and start containers (15-30 min)
9. **Initialization** - Wait for MISP init (5-10 min)
10. **Post-Install** - Generate checklist

**Resume Capability**: If interrupted, run with `--resume` flag to continue from last completed phase.

### Backup Strategy

- **Manual backups**: `backup-misp.py` - On-demand full backups
- **Automated backups**: `misp-backup-cron.py` - Runs via cron
  - Sunday: Full backup (retained 8 weeks)
  - Mon-Sat: Incremental backup (deleted after next Sunday)
- **Backup contents**: Database dump, .env, PASSWORDS.txt, SSL certs, docker-compose files

## Prerequisites

### One-Time Setup

Before running any scripts for the first time, create the log directory:

```bash
sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp && sudo chmod 775 /opt/misp/logs
```

This is required because:
- All scripts write logs to `/opt/misp/logs`
- The directory requires sudo to create (owned by root initially)
- This command gives your user ownership, allowing scripts to run without sudo prompts
- For CI/CD environments, configure passwordless sudo (see SETUP.md)

## Common Commands

### Development Workflow

```bash
# One-time setup (required on first run)
sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp && sudo chmod 775 /opt/misp/logs

# Install MISP (interactive)
python3 misp-install.py

# Install with config file (non-interactive)
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

# Uninstall (preserves backups)
python3 scripts/uninstall-misp.py --force

# View logs with JSON formatting
tail -f /opt/misp/logs/misp-install-*.log | jq '.'

# Check container status
cd /opt/misp && sudo docker compose ps

# View container logs
cd /opt/misp && sudo docker compose logs -f misp-core
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
