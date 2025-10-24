# MISP Installation Scripts Inventory

**Version**: 5.5
**Date**: 2025-10-15
**Total Scripts**: 9 Python scripts

---

## Overview

All MISP management functionality is implemented in Python with centralized JSON logging. This document provides a complete inventory of all scripts in the project.

---

## Active Scripts (Python)

### 1. misp-install.py

**Location**: `/home/gallagher/misp-install/misp-install/misp-install.py`
**Version**: 5.4
**Size**: ~72KB
**Purpose**: Main MISP installation script with enterprise features

**Key Features**:
- Pre-flight system checks (disk, RAM, CPU, ports, Docker)
- 12-phase installation process
- Automatic dedicated user creation (`misp-owner`)
- Resume capability from any phase
- Multi-environment support (dev/staging/production)
- Performance auto-tuning based on system resources
- Config file support (YAML/JSON)
- Non-interactive mode for CI/CD

**Usage**:
```bash
# Interactive installation
python3 misp-install.py

# With config file
python3 misp-install.py --config config/misp-config.json

# Non-interactive (CI/CD)
python3 misp-install.py --config config/prod-config.json --non-interactive

# Resume interrupted installation
python3 misp-install.py --resume
```

**Security Architecture**:
- Creates dedicated `misp-owner` system user
- Follows principle of least privilege (NIST SP 800-53 AC-6)
- Automatic privilege management
- All operations run as `misp-owner` (not root)

**Log Output**: `/opt/misp/logs/misp-install-TIMESTAMP.log`

---

### 2. backup-misp.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/backup-misp.py`
**Version**: 3.0
**Size**: ~17KB
**Purpose**: Manual backup utility for MISP installations

**Features**:
- Backs up configuration files (.env, PASSWORDS.txt)
- Backs up Docker Compose files
- Backs up SSL certificates
- Database dump (mysqldump)
- Attachments/files backup
- Compressed tar.gz archives
- Integrity verification

**Usage**:
```bash
# Manual backup
python3 scripts/backup-misp.py

# Specify backup directory
python3 scripts/backup-misp.py --backup-dir /custom/path
```

**Backup Location**: Default: `/home/$USER/misp-backups/`
**Log Output**: `/opt/misp/logs/backup-misp-TIMESTAMP.log`

---

### 3. configure-misp-ready.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/configure-misp-ready.py`
**Version**: 2.0
**Size**: ~12KB
**Purpose**: Post-installation MISP configuration helper

**Features**:
- Interactive configuration wizard
- Sets up MISP base URL
- Configures organization details
- Sets up email notifications
- Enables/disables modules
- Configures proxy settings
- API key generation

**Usage**:
```bash
# Interactive configuration
python3 scripts/configure-misp-ready.py
```

**Log Output**: `/opt/misp/logs/configure-misp-TIMESTAMP.log`

---

### 4. misp-backup-cron.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/misp-backup-cron.py`
**Version**: 2.0
**Size**: ~14KB
**Purpose**: Automated scheduled backups via cron

**Features**:
- Designed for cron execution
- Automatic backup rotation
- Retention policy enforcement
- Email notifications (optional)
- Backup health checks
- Minimal console output

**Usage**:
```bash
# Add to crontab (daily at 2 AM)
0 2 * * * /usr/bin/python3 /home/gallagher/misp-install/misp-install/scripts/misp-backup-cron.py

# Test manually
python3 scripts/misp-backup-cron.py
```

**Log Output**: `/opt/misp/logs/misp-backup-cron-TIMESTAMP.log`

---

### 5. misp_logger.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/misp_logger.py`
**Version**: 2.0
**Size**: ~11KB
**Purpose**: Centralized JSON logging module for all MISP scripts

**Features**:
- JSON format with CIM-compatible fields
- SIEM-ready (Splunk, ELK, etc.)
- Automatic log rotation (5 files × 20MB)
- Both file and console output
- Colored console output for readability
- Thread-safe logging
- Graceful fallback if log directory unavailable

**Usage** (imported by other scripts):
```python
from misp_logger import get_logger

logger = get_logger('my-script', 'misp:component')
logger.info("Message", event_type="install", action="start", status="info")
```

**Log Directory**: `/opt/misp/logs/`
**Rotation**: 20MB per file, 5 files max

**CIM Fields**:
- `time` - ISO 8601 timestamp (UTC)
- `host` - System hostname
- `user` - User running the script
- `source` - Script name
- `sourcetype` - MISP component type
- `severity` - INFO/WARNING/ERROR/DEBUG
- `event_type` - Primary event category
- `action` - Specific action
- `status` - Outcome (info/success/warning/error)

---

### 6. misp-restore.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/misp-restore.py`
**Version**: 2.0
**Size**: ~15KB
**Purpose**: Restore MISP from backup archives

**Features**:
- Restores from tar.gz backup archives
- Restores configuration files
- Restores Docker Compose files
- Restores SSL certificates
- Database restore (MySQL import)
- Attachments/files restore
- Pre-restore validation
- Backup of current state before restore

**Usage**:
```bash
# List available backups
python3 scripts/misp-restore.py --list

# Restore specific backup
python3 scripts/misp-restore.py --backup /path/to/backup.tar.gz

# Interactive restore
python3 scripts/misp-restore.py
```

**Log Output**: `/opt/misp/logs/misp-restore-TIMESTAMP.log`

---

### 7. misp-update.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/misp-update.py`
**Version**: 2.0
**Size**: ~13KB
**Purpose**: Update MISP to latest version or specific version

**Features**:
- Automatic backup before update
- Git pull from MISP Docker repo
- Docker image updates
- Database migrations
- Module updates
- Configuration validation
- Rollback capability
- Version pinning support

**Usage**:
```bash
# Update to latest version
python3 scripts/misp-update.py

# Update to specific version
python3 scripts/misp-update.py --version v2.4.180

# Dry run (check for updates)
python3 scripts/misp-update.py --dry-run
```

**Log Output**: `/opt/misp/logs/misp-update-TIMESTAMP.log`

---

### 8. uninstall-misp.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/uninstall-misp.py`
**Version**: 3.0
**Size**: ~17KB
**Purpose**: Complete MISP uninstallation with optional backup

**Features**:
- Automatic backup before uninstall (optional)
- Stops and removes Docker containers
- Removes Docker volumes
- Removes Docker networks
- Cleans up /opt/misp directory
- Removes /etc/hosts entries
- Interactive confirmation (bypass with --force)
- Preserves backups by default

**Usage**:
```bash
# Interactive uninstall (with backup)
python3 scripts/uninstall-misp.py

# Force uninstall without backup
python3 scripts/uninstall-misp.py --force --no-backup

# Uninstall but keep backups
python3 scripts/uninstall-misp.py --force
```

**Log Output**: `/opt/misp/logs/uninstall-misp-TIMESTAMP.log`

---

### 9. populate-misp-news.py

**Location**: `/home/gallagher/misp-install/misp-install/scripts/populate-misp-news.py`
**Version**: 1.0
**Size**: ~21KB
**Purpose**: Automatically populate MISP News from RSS feeds (utilities sector focus)

**Features**:
- Fetches articles from 9 RSS feeds across 3 categories
- Filters content for utilities/energy sector and security relevance
- Markdown-formatted news entries with clickable links
- HTML cleanup from RSS summaries
- Duplicate detection (prevents re-adding same articles)
- Configurable time range and article limits
- Dry-run mode for preview

**RSS Feed Sources** (9 feeds in 3 categories):

**Utilities Sector & ICS/SCADA News (3 feeds)**:
1. CISA ICS Advisories - https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml
2. Utility Dive - https://www.utilitydive.com/feeds/news/
3. Industrial Cyber - https://industrialcyber.co/feed/

**Vendor Security Advisories (5 feeds)**:
4. Cisco Security Advisories - https://tools.cisco.com/security/center/psirtrss20/CiscoSecurityAdvisory.xml
5. Microsoft Security Updates - https://api.msrc.microsoft.com/update-guide/rss
6. Fortinet PSIRT - https://www.fortiguard.com/rss/ir.xml
7. Palo Alto Networks Security - https://security.paloaltonetworks.com/rss.xml
8. Ubuntu Security Notices - https://ubuntu.com/security/notices/rss.xml

**Zero-Day Vulnerabilities (1 feed)**:
9. Zero Day Initiative - https://www.zerodayinitiative.com/rss/published/

**Usage**:
```bash
# Populate news (default: last 30 days, max 20 articles)
python3 scripts/populate-misp-news.py

# Preview without inserting
python3 scripts/populate-misp-news.py --dry-run

# Limit to 10 articles from last 7 days
python3 scripts/populate-misp-news.py --max-items 10 --days 7

# Set up automated daily updates
bash scripts/setup-news-cron.sh

# Manual cron setup (if needed)
0 8 * * * cd /home/gallagher/misp-install/misp-install && python3 scripts/populate-misp-news.py --quiet --days 2
```

**Cron Automation**:
- Run `bash scripts/setup-news-cron.sh` to install daily cron job
- Checks feeds daily at 8 AM
- Only fetches articles from last 2 days (efficient)
- Automatically skips duplicates
- Quiet mode for minimal cron email
- Remove with: `bash scripts/setup-news-cron.sh --remove`

**News Format**:
- **Title**: Plain text (article headline)
- **Message**: Markdown-formatted with:
  - Clean summary (250 chars, HTML removed)
  - Clickable link: `**[→ Read full article](URL)**`
  - Horizontal rule separator
  - Source attribution: `*Source: Feed Name*`

**Filtering Keywords**:
- Utilities: Energy, utility, electric, power, grid, solar, wind, SCADA, ICS, OT, NERC CIP, critical infrastructure
- Vendors: Cisco, Fortinet, FortiGate, Palo Alto, PAN-OS, Microsoft, Windows, Ubuntu, Linux
- Security: Zero-day, vulnerability, CVE, security advisory, patch, firewall, VPN, router, switch, authentication, RCE

**Log Output**: `/opt/misp/logs/populate-misp-news-TIMESTAMP.log`

---

## Script Dependencies

### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.10+

### Standard Library Dependencies
All scripts use only Python standard library modules:
- `os`, `sys`, `subprocess`, `pathlib`
- `json`, `logging`, `argparse`
- `datetime`, `socket`, `platform`
- `pwd`, `grp` (Unix-specific)

### Optional Dependencies
- `pyyaml` - For YAML config file support (misp-install.py)
  ```bash
  pip3 install pyyaml
  ```
- `feedparser` - For RSS feed parsing (populate-misp-news.py)
  ```bash
  pip3 install feedparser
  ```

### System Dependencies
- `sudo` - Required for privilege escalation
- `docker` - Required for container management
- `docker compose` - Required for multi-container orchestration

---

## Removed/Deprecated Scripts

The following scripts were **removed in v5.4** as part of cleanup:

### backup-misp.sh (REMOVED)
- **Location**: `scripts/backup-misp.sh` (deleted)
- **Reason**: Replaced by backup-misp.py (v3.0)
- **Migration**: Use `python3 scripts/backup-misp.py`

### uninstall-misp.sh (REMOVED)
- **Location**: `scripts/uninstall-misp.sh` (deleted)
- **Reason**: Replaced by uninstall-misp.py (v3.0)
- **Migration**: Use `python3 scripts/uninstall-misp.py`

**Note**: If you have cron jobs or scripts referencing `.sh` versions, update them to use `.py` versions.

---

## Logging Architecture

All scripts use centralized logging via `misp_logger.py`:

### Log Directory
```
/opt/misp/logs/
├── misp-install-TIMESTAMP.log
├── backup-misp-TIMESTAMP.log
├── configure-misp-TIMESTAMP.log
├── misp-backup-cron-TIMESTAMP.log
├── misp-restore-TIMESTAMP.log
├── misp-update-TIMESTAMP.log
└── uninstall-misp-TIMESTAMP.log
```

### Log Format
JSON format with CIM-compatible fields:
```json
{
  "time": "2025-10-13T18:33:10.453675Z",
  "host": "misp-dev",
  "user": "gallagher",
  "source": "backup-misp",
  "sourcetype": "misp:backup",
  "severity": "INFO",
  "message": "Backup process completed!",
  "event_type": "backup",
  "action": "complete",
  "status": "success",
  "duration": 55.24
}
```

### Log Rotation
- **Files per script**: 5 rotating files
- **Size limit**: 20MB per file
- **Total retention**: ~100MB per script
- **Automatic cleanup**: Oldest logs deleted when limit reached

### Viewing Logs
```bash
# View all logs
ls -lth /opt/misp/logs/

# View JSON formatted
tail -f /opt/misp/logs/misp-install.log | jq '.'

# Filter by severity
cat /opt/misp/logs/*.log | jq 'select(.severity=="ERROR")'

# Show only messages
cat /opt/misp/logs/backup-misp.log | jq -r '.message'
```

---

## Script Workflow

### Fresh Installation
```
1. misp-install.py            → Full installation
2. configure-misp-ready.py    → Post-install configuration (optional)
3. backup-misp.py             → Initial backup
4. misp-backup-cron.py        → Schedule automated backups (cron)
```

### Maintenance Operations
```
# Backup
backup-misp.py → Creates manual backup

# Update
misp-update.py → Updates MISP to latest/specific version

# Restore
misp-restore.py → Restores from backup

# Uninstall
uninstall-misp.py → Complete removal (with optional backup)
```

---

## Best Practices

### 1. Always Backup Before Major Operations
```bash
python3 scripts/backup-misp.py  # Before updates or config changes
```

### 2. Use Config Files for Consistent Deployments
```bash
python3 misp-install.py --config config/prod-config.json --non-interactive
```

### 3. Monitor Logs for Issues
```bash
tail -f /opt/misp/logs/misp-install.log | jq '.'
```

### 4. Schedule Automated Backups
```bash
# Add to crontab
0 2 * * * /usr/bin/python3 /home/gallagher/misp-install/misp-install/scripts/misp-backup-cron.py
```

### 5. Test Restores Regularly
```bash
# Verify backup integrity
python3 scripts/misp-restore.py --list
```

---

## Security Considerations

### User Execution Model
All scripts now run under the **dedicated `misp-owner` user**:
- ✅ Installation automatically creates `misp-owner` system user
- ✅ All MISP files owned by `misp-owner:misp-owner`
- ✅ Scripts automatically switch to `misp-owner` context
- ✅ Follows principle of least privilege (NIST SP 800-53 AC-6)

### Credential Storage
- **PASSWORDS.txt**: `/opt/misp/PASSWORDS.txt` (chmod 600, owner: misp-owner)
- **.env file**: `/opt/misp/.env` (chmod 600, owner: misp-owner)
- **Backup security**: Backup archives inherit security context

### Log Directory Permissions
- **Location**: `/opt/misp/logs/`
- **Ownership**: `misp-owner:misp-owner`
- **Permissions**: `777` (world-writable)
- **Reason**: Docker containers (www-data) and management scripts both write logs

---

## Troubleshooting

### Script Execution Issues

**Problem**: "Permission denied" when running script
**Solution**: Ensure script is executable:
```bash
chmod +x scripts/backup-misp.py
```

**Problem**: "Module not found: yaml"
**Solution**: Install PyYAML:
```bash
pip3 install pyyaml
```

**Problem**: "Cannot write to /opt/misp/logs"
**Solution**: Ensure log directory exists with proper permissions:
```bash
sudo mkdir -p /opt/misp/logs
sudo chown misp-owner:misp-owner /opt/misp/logs
sudo chmod 777 /opt/misp/logs
```

### Docker Issues

**Problem**: "Docker daemon not running"
**Solution**: Start Docker service:
```bash
sudo systemctl start docker
```

**Problem**: "Permission denied" accessing Docker
**Solution**: Ensure user is in docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.5 | 2025-10-15 | Added populate-misp-news.py with Markdown support |
| 5.4 | 2025-10-13 | Dedicated user architecture, removed .sh scripts |
| 5.3 | 2025-10-13 | Logger robustness, log directory fixes |
| 5.2 | 2025-10-12 | Centralized JSON logging (CIM fields) |
| 5.0 | 2025-10-11 | Enterprise-grade Python implementation |

---

## Additional Resources

- **Main README**: `README.md`
- **Security Architecture**: `docs/SECURITY_ARCHITECTURE.md`
- **Logging Guide**: `docs/README_LOGGING.md`
- **Setup Guide**: `SETUP.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Changelog**: `docs/testing_and_updates/CHANGELOG.md`

---

**Created by tKQB Enterprises MISP Installation Suite**
**Documentation Version**: 5.5
**Last Updated**: 2025-10-15
