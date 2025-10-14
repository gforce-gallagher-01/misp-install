# MISP Installation Suite - Architecture Guide

**Version**: 5.4
**Last Updated**: 2025-10-14
**Status**: STABLE - PRODUCTION READY

## Overview

This document describes the core architecture of the MISP installation suite, including design principles, directory structure, logging system, and technical implementation details.

## Core Design Principles

### 1. Centralized JSON Logging

All scripts use `/opt/misp/logs/` with CIM (Common Information Model) field names for SIEM integration (Splunk, ELK, etc.)

**Key Features**:
- JSON-formatted log files for machine parsing
- CIM-compliant field names (`event_type`, `action`, `status`, `result`)
- Automatic log rotation (5 files × 20MB each)
- Centralized location: `/opt/misp/logs/`
- Sourcetype tagging for SIEM classification

**Usage Pattern**:
```python
from misp_logger import get_logger
logger = get_logger('script-name', 'misp:sourcetype')
logger.info("message", event_type="backup", action="start", status="success")
```

**Log File Naming**: `{script-name}-{timestamp}.log`

**See Also**: `README_LOGGING.md` for complete logging documentation

### 2. State Management

Installation uses resume capability via `~/.misp-install/state.json`

**State File Format**:
```json
{
  "phase": 6,
  "phase_name": "Configuration Complete",
  "timestamp": "2025-10-13T15:30:00",
  "config": {
    "server_ip": "192.168.20.193",
    "domain": "misp-dev.lan",
    ...
  }
}
```

**Resume Logic**:
1. Check if state file exists
2. Load last completed phase
3. Skip completed phases
4. Continue from `phase + 1`

**Resume Command**: `python3 misp-install.py --resume`

### 3. Phase-Based Execution

Operations are broken into numbered phases that can be resumed if interrupted

**Benefits**:
- Fault tolerance: Resume after failure/interruption
- Progress tracking: Clear indication of current step
- Debugging: Isolate issues to specific phase
- Logging: Each phase logged separately

**Implementation**:
- Each phase is a method in `MISPInstaller` class
- Naming convention: `phase_N_description()`
- State saved after each phase completes
- Phases can have sub-phases (e.g., Phase 5.5)

### 4. Docker-First

All MISP components run in Docker containers managed via docker-compose

**Containers**:
- `misp-core` - MISP web application (Apache + PHP)
- `misp-modules` - MISP enrichment modules
- `db` - MySQL database
- `redis` - Redis cache

**Container Management**:
```bash
cd /opt/misp && sudo docker compose ps      # Status
cd /opt/misp && sudo docker compose logs    # Logs
cd /opt/misp && sudo docker compose up -d   # Start
cd /opt/misp && sudo docker compose down    # Stop
```

## Critical Directory Structure

```
/opt/misp/                  # Main MISP installation
  ├── logs/                 # Centralized JSON logs - MUST EXIST before logging starts
  │   ├── misp-install-*.log
  │   ├── backup-misp-*.log
  │   ├── configure-misp-*.log
  │   └── ...
  ├── .env                  # Docker environment config (chmod 600)
  ├── PASSWORDS.txt         # All credentials (chmod 600)
  ├── ssl/                  # SSL certificates
  │   ├── cert.pem
  │   └── key.pem
  ├── docker-compose.yml    # Docker configuration
  ├── MISP/                 # MISP application files (docker volume)
  └── misp-db/              # MySQL data (docker volume)

~/misp-backups/            # Backup storage (preserved during uninstall)
  ├── full/                 # Full backups (Sunday)
  └── incremental/          # Incremental backups (Mon-Sat)

~/.misp-install/           # Installation state and metadata
  └── state.json            # Current installation state
```

### Directory Ownership (v5.4)

**Critical**: All `/opt/misp/` files are owned by `misp-owner:misp-owner` system user

```bash
# Owner: misp-owner:misp-owner
/opt/misp/                 # 755
/opt/misp/logs/            # 777 (Docker www-data + scripts write here)
/opt/misp/.env             # 600
/opt/misp/PASSWORDS.txt    # 600
/opt/misp/ssl/             # 755
```

**Why 777 on logs/**:
- Docker containers run as `www-data` user (UID 33)
- Scripts run as regular user (e.g., `gallagher`)
- Both need write access to log directory
- Directory is owned by `misp-owner` for consistency

### Directory Creation Order (Critical!)

**Phase 1 (Line 1586-1601)**:
```python
# Create /opt/misp directory structure
misp_dir = Path('/opt/misp')
logs_dir = misp_dir / 'logs'

# Create with sudo (owned by misp-owner)
subprocess.run(['sudo', '-u', MISP_USER, 'mkdir', '-p', str(logs_dir)])
subprocess.run(['sudo', 'chmod', '777', str(logs_dir)])
```

**⚠️ CRITICAL**: `/opt/misp/logs/` MUST exist BEFORE any logger initialization. NO FALLBACK directories are used - logging will fail if this directory doesn't exist.

## Logging Architecture

### Logger Initialization

**Centralized Module**: `misp_logger.py`

```python
from misp_logger import get_logger

# Initialize logger
logger = get_logger('script-name', 'misp:sourcetype')

# Log with structured fields
logger.info("Operation started",
            event_type="operation",
            action="start",
            component="component-name",
            status="success")
```

### Log File Rotation

- **Max Size**: 20 MB per file
- **Max Files**: 5 backups
- **Total Storage**: ~100 MB per script
- **Rotation Mode**: Size-based (not time-based)

### Sourcetype Convention

| Script | Sourcetype | Purpose |
|--------|-----------|---------|
| `misp-install.py` | `misp:install` | Installation logs |
| `backup-misp.py` | `misp:backup` | Backup logs |
| `misp-restore.py` | `misp:restore` | Restore logs |
| `misp-update.py` | `misp:update` | Update logs |
| `configure-misp-nerc-cip.py` | `misp:nerc-cip` | NERC CIP config logs |
| `populate-misp-news.py` | `misp:news` | News population logs |

### CIM Field Names

**Standard Fields** (all logs):
- `timestamp` - ISO 8601 timestamp
- `level` - Log level (INFO, WARNING, ERROR)
- `sourcetype` - Log sourcetype (e.g., `misp:backup`)
- `message` - Human-readable message

**Event Fields** (operation logs):
- `event_type` - Type of event (backup, restore, update, install)
- `action` - Action performed (start, complete, enable, disable)
- `status` - Operation status (success, failed, in_progress)
- `result` - Result code (0=success, 1=failure)
- `component` - Component affected (feed, setting, container)

**Example Log Entry**:
```json
{
  "timestamp": "2025-10-14T15:30:00Z",
  "level": "INFO",
  "sourcetype": "misp:backup",
  "event_type": "backup",
  "action": "complete",
  "status": "success",
  "backup_type": "full",
  "backup_size_mb": 1024,
  "duration_seconds": 120,
  "message": "Full backup completed successfully"
}
```

## v5.4 Dedicated User Architecture

### System User: `misp-owner`

**Created During**: Phase 1 (Dependencies)

**User Properties**:
- **Type**: System user (`--system` flag)
- **Shell**: `/usr/sbin/nologin` (no interactive login)
- **Home**: `/nonexistent` (no home directory)
- **Groups**: `docker` (added in Phase 2)

**Creation Command**:
```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin misp-owner
```

### Ownership Model

**Script Execution**: Runs as regular user (e.g., `gallagher`)

**File Ownership**: `/opt/misp/` owned by `misp-owner:misp-owner`

**File Operations Pattern** (Temp File + Sudo):
```python
# Write to temp location as current user
temp_file = f"/tmp/.env.{os.getpid()}"
with open(temp_file, 'w') as f:
    f.write(content)

# Move to final location as misp-owner
subprocess.run(['sudo', '-u', 'misp-owner', 'cp', temp_file, '/opt/misp/.env'])
subprocess.run(['sudo', 'chmod', '600', '/opt/misp/.env'])
subprocess.run(['sudo', 'chown', 'misp-owner:misp-owner', '/opt/misp/.env'])

# Cleanup temp file
os.unlink(temp_file)
```

### Passwordless Sudo Requirements

**Required Commands** (see `SETUP.md` for sudoers config):
- **File Operations**: `mkdir`, `chown`, `chmod`, `rm`, `mv`, `cp`
- **Docker Operations**: `docker`, `docker-compose`
- **System Operations**: `apt`, `systemctl`, `usermod`
- **User Management**: `useradd`, `userdel`

**Sudoers Entry Example**:
```bash
gallagher ALL=(ALL) NOPASSWD: /usr/bin/mkdir, /usr/bin/chown, /usr/bin/chmod, \
    /usr/bin/docker, /usr/bin/docker-compose, /usr/bin/apt, /usr/bin/systemctl
```

### Security Standards Compliance

- ✅ **NIST SP 800-53 AC-6** (Least Privilege)
- ✅ **CIS Benchmarks 5.4.1** (Service Account Isolation)
- ✅ **OWASP Server Security Best Practices**

## Backup Strategy

### Backup Types

**Full Backup** (Sunday):
- Database dump (MySQL)
- Configuration files (.env, docker-compose.yml)
- SSL certificates
- PASSWORDS.txt
- Retention: 8 weeks

**Incremental Backup** (Monday-Saturday):
- Database changes only
- Deleted after next full backup
- Retention: 7 days

### Backup Scripts

**Manual Backup**:
```bash
python3 scripts/backup-misp.py
```

**Automated Backup** (Cron):
```bash
python3 scripts/misp-backup-cron.py
```

**Cron Schedule**:
```cron
# Full backup every Sunday at 2 AM
0 2 * * 0 /usr/bin/python3 /path/to/scripts/misp-backup-cron.py

# Incremental backup Mon-Sat at 2 AM
0 2 * * 1-6 /usr/bin/python3 /path/to/scripts/misp-backup-cron.py
```

### Backup Location

**Directory**: `~/misp-backups/`

**Structure**:
```
~/misp-backups/
├── full/
│   └── misp-backup-2025-10-13-full.tar.gz
└── incremental/
    ├── misp-backup-2025-10-14-incremental.tar.gz
    └── misp-backup-2025-10-15-incremental.tar.gz
```

## Performance Tuning

### Auto-Detection (Phase 6)

System resources are detected and used to configure PHP and workers:

**RAM-Based Configuration**:
- **< 8GB RAM**: 1024M PHP memory, 2 workers
- **8-16GB RAM**: 2048M PHP memory, 4 workers
- **16GB+ RAM**: 4096M PHP memory, 8+ workers

**Worker Calculation**: `max(2, CPU_CORES)`

**Implementation** (line 803-825 in `misp-install.py`):
```python
import psutil

total_ram_gb = psutil.virtual_memory().total / (1024**3)
cpu_cores = psutil.cpu_count()

if total_ram_gb < 8:
    php_memory = "1024M"
    workers = 2
elif total_ram_gb < 16:
    php_memory = "2048M"
    workers = 4
else:
    php_memory = "4096M"
    workers = max(2, cpu_cores)
```

### Environment Types

**Development**:
- Debug enabled
- Verbose logging
- Lower resource allocation
- Self-signed SSL acceptable

**Staging**:
- Production-like configuration
- Testing environment
- Moderate resources
- Self-signed SSL acceptable

**Production** (default):
- Optimized performance
- Security hardened
- Full resource allocation
- Trusted SSL recommended

## State Management Details

### State File Location

`~/.misp-install/state.json`

### State Persistence

**After Each Phase**:
```python
def save_state(self, phase: int, phase_name: str):
    """Save installation state for resume capability"""
    state = {
        'phase': phase,
        'phase_name': phase_name,
        'timestamp': datetime.now().isoformat(),
        'config': self.config
    }

    state_file = Path.home() / '.misp-install' / 'state.json'
    state_file.parent.mkdir(exist_ok=True)

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
```

### Resume Logic

**Check for Existing State**:
```python
def load_state(self) -> Optional[Dict]:
    """Load installation state if exists"""
    state_file = Path.home() / '.misp-install' / 'state.json'

    if not state_file.exists():
        return None

    with open(state_file, 'r') as f:
        return json.load(f)
```

**Resume Execution**:
```python
if args.resume:
    state = self.load_state()
    if state:
        start_phase = state['phase'] + 1
        self.info(f"Resuming from Phase {start_phase}: {state['phase_name']}")
    else:
        self.error("No state file found. Cannot resume.")
        sys.exit(1)
```

## Security Considerations

### File Permissions

| File/Directory | Owner | Permissions | Contains |
|---------------|-------|-------------|----------|
| `/opt/misp/` | misp-owner:misp-owner | 755 | All MISP files |
| `/opt/misp/logs/` | misp-owner:misp-owner | 777 | Log files |
| `/opt/misp/.env` | misp-owner:misp-owner | 600 | Credentials |
| `/opt/misp/PASSWORDS.txt` | misp-owner:misp-owner | 600 | Credentials |
| `/opt/misp/ssl/` | misp-owner:misp-owner | 755 | SSL certs |

### Password Validation

**Requirements** (PasswordValidator class):
- Minimum 12 characters
- Contains uppercase letter
- Contains lowercase letter
- Contains number
- Contains special character

**Validation Code** (line 346-379 in `misp-install.py`):
```python
class PasswordValidator:
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        if len(password) < 12:
            return False, "Must be at least 12 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Must contain uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Must contain lowercase letter"
        if not re.search(r'\d', password):
            return False, "Must contain number"
        if not re.search(r'[!@#$%^&*]', password):
            return False, "Must contain special character"
        return True, "Password meets requirements"
```

### Secrets Management

**Current Approach**: Files with 600 permissions
- `/opt/misp/.env` - Docker environment variables
- `/opt/misp/PASSWORDS.txt` - Human-readable credential reference

**Future**: Azure Key Vault integration (see TODO.md)

### Encryption Key

**Auto-Generated**: Never change after installation (data loss)

**Location**: `/opt/misp/.env` as `ENCRYPTION_KEY`

## Docker Integration

### Container Communication

**Network**: Docker bridge network (default)

**DNS Resolution**: Via `/etc/hosts` (Phase 8)
```
192.168.20.193  misp-dev.lan
```

### Health Checks

**Known Issue**: `misp-core` shows "unhealthy" despite working

**Root Cause**: Health check uses `BASE_URL` domain which container cannot resolve internally

**Impact**: None - MISP functions correctly

**Workaround**: Ignore health check status, verify via web interface

### Volume Mounts

**Persistent Volumes**:
```yaml
volumes:
  - ./MISP:/var/www/MISP
  - ./misp-db:/var/lib/mysql
  - ./ssl:/etc/nginx/certs:ro
  - ./logs:/var/www/MISP/app/tmp/logs
```

## Related Documentation

- **INSTALLATION.md** - Installation flow and phases
- **v5.4_DEDICATED_USER.md** - v5.4 testing history
- **README_LOGGING.md** - Logging system details
- **SETUP.md** - Sudoers configuration
- **KNOWN-ISSUES.md** - Known issues and workarounds

---

**Last Updated**: 2025-10-14
**Maintainer**: tKQB Enterprises
