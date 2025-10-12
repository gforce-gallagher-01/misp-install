# MISP Update Tool Documentation

**Version:** 1.0  
**Author:** tKQB Enterprises  
**Last Updated:** 2025-10-11

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Check for Updates](#check-for-updates)
  - [View Detailed Version Info](#view-detailed-version-info)
  - [Update All Components](#update-all-components)
  - [Update Specific Components](#update-specific-components)
  - [Advanced Options](#advanced-options)
- [Update Scenarios](#update-scenarios)
- [Backup & Rollback](#backup--rollback)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Command Reference](#command-reference)
- [FAQ](#faq)

---

## Overview

The MISP Update Tool (`misp-update.py`) is a comprehensive Python script for safely updating and maintaining your MISP Docker installation. It provides automated backup, health checking, and rollback capabilities.

### What It Updates

- **MISP Repository** - Git repository with latest code
- **Docker Images** - Pre-built container images
- **MISP Core** - Main MISP application
- **Database** - MySQL/MariaDB schema and data
- **Redis** - Cache and queue service
- **MISP Modules** - Enrichment and expansion modules

---

## Features

✅ **Automatic Backup** - Creates full backup before any changes  
✅ **Version Checking** - Shows current versions of all components  
✅ **Health Verification** - Ensures services are healthy after update  
✅ **Rolling Updates** - Minimal downtime with service-by-service restart  
✅ **Rollback Support** - Backup information for manual rollback  
✅ **Dry Run Mode** - Preview changes without making them  
✅ **Detailed Logging** - Full logs saved to `/var/log/misp-install/`  
✅ **Container Recreation** - Option to completely rebuild containers  

---

## Prerequisites

- MISP installed via `misp-install.py`
- Python 3.8 or higher
- Docker and Docker Compose running
- Sudo privileges
- Minimum 5GB free disk space (for backups)

### Verify Prerequisites

```bash
# Check Python version
python3 --version

# Check Docker
docker --version
docker compose version

# Check disk space
df -h ~

# Check MISP is running
cd /opt/misp && sudo docker compose ps
```

---

## Quick Start

### 1. Check What Needs Updating

```bash
python3 misp-update.py --check-only
```

**Output Example:**
```
[0/5] Checking container status...
  ✓ All 5 containers running

[1/5] Checking MISP repository...
  → Up to date

[2/5] Checking Docker images...
  → Updates available

[3/5] Checking MISP version...
  → Current version: v2.5.22

[4/5] Checking Redis version...
  → Redis v7.2.11

[5/5] Checking Database version...
  → MariaDB v10.11.14

⚠ Updates available:
  • Docker Images: local → latest
```

### 2. Preview What Will Happen (Dry Run)

```bash
python3 misp-update.py --all --dry-run
```

### 3. Perform the Update

```bash
python3 misp-update.py --all
```

---

## Usage

### Check for Updates

Check if updates are available without making any changes:

```bash
python3 misp-update.py --check-only
```

**When to use:**
- Daily/weekly routine checks
- Before planning maintenance window
- After hearing about MISP updates

---

### View Detailed Version Info

Get comprehensive version information for all components:

```bash
python3 misp-update.py --version-info
```

**Output includes:**
- Docker container image versions and tags
- MISP modules version
- Python version
- PHP version
- MySQL/MariaDB version
- Redis version

**Example Output:**
```
==================================================
DETAILED VERSION INFORMATION
==================================================

Docker Container Images:
SERVICE       REPOSITORY          TAG       IMAGE ID      SIZE
misp-core     ghcr.io/misp      v2.5.22   abc123def     2.5GB
misp-modules  ghcr.io/misp      v2.4.195  def456ghi     1.2GB
db            mariadb           10.11     ghi789jkl     400MB
redis         redis             7.2       jkl012mno     120MB

MISP Modules:
  misp-modules==2.4.195

Python Version (misp-core):
  Python 3.11.6

PHP Version:
  PHP 8.2.12 (cli)

MySQL Version:
  MariaDB v10.11.14

Redis Version:
  Redis v7.2.11
```

---

### Update All Components

Update both repository and Docker images:

```bash
# Interactive mode (recommended)
python3 misp-update.py --all

# Non-interactive mode
python3 misp-update.py --all --skip-backup  # NOT RECOMMENDED
```

**Process:**
1. Creates backup (database, configs, certs)
2. Pulls latest repository changes
3. Pulls latest Docker images
4. Restarts services with health checks
5. Verifies MISP functionality

**Downtime:** ~2-5 minutes with rolling restart

---

### Update Specific Components

Update only what you need:

#### Update Repository Only

```bash
python3 misp-update.py --repository
```

**Use when:**
- Docker images are up to date
- Only git repo has changes
- Testing configuration changes

#### Update Docker Images Only

```bash
python3 misp-update.py --images
```

**Use when:**
- Repository is up to date
- New container images available
- Security patches in base images

---

### Advanced Options

#### Dry Run Mode

See what would happen without making changes:

```bash
python3 misp-update.py --all --dry-run
```

**Shows:**
- Which commands would be executed
- Which files would be backed up
- What would be updated

#### Skip Backup

**⚠️ NOT RECOMMENDED** - Skip backup creation:

```bash
python3 misp-update.py --all --skip-backup
```

**Only use when:**
- You just created a manual backup
- Testing in development environment
- Extremely low on disk space

#### Recreate Containers

Stop and rebuild containers from scratch:

```bash
python3 misp-update.py --all --recreate
```

**Use when:**
- Troubleshooting persistent issues
- Major version upgrades
- Container corruption suspected

**Downtime:** ~5-10 minutes

#### Fast Restart (No Rolling)

Restart all services at once instead of one-by-one:

```bash
python3 misp-update.py --all --no-rolling
```

**Downtime:** ~30 seconds vs 2-5 minutes

**Trade-off:** Faster but more downtime

#### Custom MISP Directory

If MISP is installed in non-default location:

```bash
python3 misp-update.py --all --misp-dir /opt/misp-docker
```

---

## Update Scenarios

### Scenario 1: Routine Monthly Update

**Goal:** Keep MISP current with minimal risk

```bash
# 1. Check what needs updating
python3 misp-update.py --check-only

# 2. Review changes (if available)
cd /opt/misp && git log HEAD..origin/main --oneline

# 3. Dry run to see what will happen
python3 misp-update.py --all --dry-run

# 4. Perform update during maintenance window
python3 misp-update.py --all

# 5. Verify functionality
curl -k https://misp-dev.lan
cd /opt/misp && sudo docker compose logs --tail=50
```

**Best Time:** Weekend or after hours  
**Duration:** 10-15 minutes  
**Risk:** Low

---

### Scenario 2: Security Patch Update

**Goal:** Apply critical security updates quickly

```bash
# Fast update with minimal downtime
python3 misp-update.py --images --no-rolling
```

**Best Time:** ASAP after notification  
**Duration:** 3-5 minutes  
**Risk:** Low

---

### Scenario 3: Major Version Upgrade

**Goal:** Upgrade to new major MISP version

```bash
# 1. Read release notes
# Visit: https://www.misp-project.org/

# 2. Create extra backup
cd /opt/misp
sudo docker compose exec -T db mysqldump -umisp -p$(grep MYSQL_PASSWORD .env | cut -d= -f2) misp > ~/misp-backup-major-$(date +%Y%m%d).sql

# 3. Perform upgrade with recreation
python3 misp-update.py --all --recreate

# 4. Test thoroughly
# - Login to web interface
# - Create test event
# - Check feeds
# - Verify workers
```

**Best Time:** Planned maintenance window  
**Duration:** 15-30 minutes  
**Risk:** Medium

---

### Scenario 4: Recovery from Failed Update

**Goal:** Restore working state after update failure

```bash
# 1. List available backups
python3 misp-restore.py --list

# 2. Show what's in the latest backup
python3 misp-restore.py --show latest

# 3. Restore from backup
python3 misp-restore.py --restore latest

# 4. Verify restoration
cd /opt/misp
sudo docker compose ps
curl -k https://misp-dev.lan
```

**Best Time:** Immediately after failed update  
**Duration:** 10-15 minutes  
**Risk:** Low (uses automated restore tool)

---

## Backup & Rollback

### Automatic Backups

Every update creates a backup in `/opt/misp-backups/`:

```bash
ls -lh /opt/misp-backups/
```

**Backup contains:**
- `.env` file (configuration)
- `PASSWORDS.txt` (credentials)
- SSL certificates
- Database dump (`.sql` file)
- `docker-compose.yml` and overrides
- Version information

### Manual Backup

Create backup without updating:

```bash
# Create timestamped backup
BACKUP_DIR=/opt/misp-backups/manual-$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup configs
cp /opt/misp/.env $BACKUP_DIR/
cp /opt/misp/PASSWORDS.txt $BACKUP_DIR/
cp /opt/misp/docker-compose.yml $BACKUP_DIR/
cp -r /opt/misp/ssl $BACKUP_DIR/

# Backup database
cd /opt/misp
sudo docker compose exec -T db mysqldump -umisp -p$(grep MYSQL_PASSWORD .env | cut -d= -f2) misp > $BACKUP_DIR/misp_database.sql

echo "Backup created: $BACKUP_DIR"
```

### Restore from Backup

Use the `misp-restore.py` tool for safe, automated restoration:

#### Quick Restore (Latest Backup)

```bash
# List available backups
python3 misp-restore.py --list

# Show what's in latest backup
python3 misp-restore.py --show latest

# Restore from latest backup
python3 misp-restore.py --restore latest
```

#### Interactive Restore

```bash
# Interactive mode - choose which backup to restore
python3 misp-restore.py
```

#### Restore Specific Backup

```bash
# Restore from specific backup by name
python3 misp-restore.py --restore misp-backup-20251011_143052

# Restore configs only (skip database)
python3 misp-restore.py --restore latest --skip-database
```

#### What the Restore Tool Does

1. **Creates pre-restore backup** - Backs up current state first
2. **Restores configuration files** - .env, PASSWORDS.txt, docker-compose files
3. **Restores SSL certificates** - cert.pem and key.pem
4. **Restores database** - Full database restore (optional)
5. **Restarts services** - Brings everything back up
6. **Verifies restore** - Tests containers, database, web interface

#### Manual Restore (Emergency)

If the restore tool fails:

```bash
# 1. Find your backup
ls -lt /opt/misp-backups/

# 2. Stop containers
cd /opt/misp
sudo docker compose down

# 3. Restore configuration files
BACKUP_DIR=/opt/misp-backups/misp-backup-YYYYMMDD_HHMMSS
cp $BACKUP_DIR/.env /opt/misp/
cp $BACKUP_DIR/PASSWORDS.txt /opt/misp/
cp $BACKUP_DIR/docker-compose.yml /opt/misp/
cp -r $BACKUP_DIR/ssl /opt/misp/

# 4. Restore database
sudo docker compose up -d db
sleep 30
cat $BACKUP_DIR/misp_database.sql | sudo docker compose exec -T db mysql -umisp -p$(grep MYSQL_PASSWORD .env | cut -d= -f2) misp

# 5. Start all services
sudo docker compose up -d

# 6. Verify
sudo docker compose ps
curl -k https://misp-dev.lan
```

---

## Troubleshooting

### Update Fails During Pull

**Symptoms:**
- Timeout errors
- Network errors
- "Image not found"

**Solutions:**
```bash
# Check internet connectivity
ping -c 3 google.com

# Check Docker Hub access
docker pull hello-world

# Check disk space
df -h

# Try manual pull
cd /opt/misp
sudo docker compose pull

# If still failing, check Docker service
sudo systemctl status docker
sudo systemctl restart docker
```

---

### Containers Won't Start After Update

**Symptoms:**
- Containers in "Exit" or "Restarting" state
- Health checks failing

**Solutions:**
```bash
# Check container logs
cd /opt/misp
sudo docker compose logs --tail=100

# Check specific service
sudo docker compose logs misp-core --tail=50

# Verify .env file
cat /opt/misp/.env | grep -v PASSWORD

# Try recreation
sudo docker compose down
sudo docker compose up -d

# If still failing, restore from backup
```

---

### Database Connection Errors

**Symptoms:**
- "Can't connect to MySQL"
- "Access denied for user"
- MISP shows database errors

**Solutions:**
```bash
# Check database container
cd /opt/misp
sudo docker compose ps db

# Test database connection
sudo docker compose exec -T db mysql -umisp -p$(grep MYSQL_PASSWORD .env | cut -d= -f2) -e "SELECT VERSION();" misp

# Check logs
sudo docker compose logs db --tail=100

# Verify password in .env
grep MYSQL_PASSWORD /opt/misp/.env

# Restart database
sudo docker compose restart db
sleep 30
sudo docker compose restart misp-core
```

---

### MISP Version Shows "unknown"

**Symptoms:**
- `--check-only` shows "Current version: unknown"
- Cannot determine MISP version

**Solutions:**
```bash
# Check if container is fully started
cd /opt/misp
sudo docker compose ps

# Wait for initialization (may take 5-10 minutes on first start)
sudo docker compose logs -f misp-core | grep -i "init.*done"

# Check VERSION.json manually
sudo docker compose exec -T misp-core cat /var/www/MISP/VERSION.json

# Verify file exists
sudo docker compose exec -T misp-core ls -la /var/www/MISP/VERSION.json
```

---

### Update Tool Hangs or Freezes

**Symptoms:**
- Script stops responding
- No output for long time

**Solutions:**
```bash
# Kill the script
Ctrl+C

# Check what's running
ps aux | grep docker

# Check Docker processes
sudo docker ps

# Try with verbose logging
python3 misp-update.py --all 2>&1 | tee update-debug.log

# Check system resources
top
df -h
```

---

## Best Practices

### Before Updating

✅ **Schedule maintenance window** - Plan for 30 minutes  
✅ **Notify users** - Send advance notice  
✅ **Check release notes** - Review breaking changes  
✅ **Verify backups exist** - Ensure recent backup available  
✅ **Test in dev first** - If you have dev environment  
✅ **Check disk space** - Need 5GB+ free  

### During Update

✅ **Monitor logs** - Watch for errors  
✅ **Don't interrupt** - Let process complete  
✅ **Note any warnings** - Document for troubleshooting  
✅ **Keep terminal open** - Don't close SSH session  

### After Update

✅ **Verify web interface** - Test login  
✅ **Check core functionality** - Create test event  
✅ **Review logs** - Look for errors  
✅ **Test key features** - Feeds, workers, API  
✅ **Monitor for 24 hours** - Watch for issues  
✅ **Update documentation** - Note any changes  

### Regular Maintenance Schedule

| Frequency | Task |
|-----------|------|
| **Daily** | Check container status |
| **Weekly** | Check for updates (`--check-only`) |
| **Monthly** | Apply updates |
| **Quarterly** | Review and clean old backups |
| **Annually** | Major version upgrades |

---

## Command Reference

### Update Tool Commands

```bash
python3 misp-update.py [OPTIONS]

Options:
  --check-only              Only check for updates, don't apply
  --version-info           Show detailed version information
  --all                    Update all components (repository + images)
  --repository             Update repository only
  --images                 Update Docker images only
  --skip-backup            Skip backup before update (NOT RECOMMENDED)
  --recreate              Recreate containers instead of restart
  --no-rolling            Restart all services at once
  --dry-run               Show what would be done without making changes
  --misp-dir PATH         Specify MISP installation directory
  -h, --help              Show help message
```

### Restore Tool Commands

```bash
python3 misp-restore.py [OPTIONS]

Options:
  --list                   List all available backups
  --show BACKUP           Show contents of backup ("latest" or backup name)
  --restore BACKUP        Restore from backup ("latest" or backup name)
  --skip-database         Skip database restore (configs only)
  --skip-backup           Skip pre-restore backup (NOT RECOMMENDED)
  --misp-dir PATH         MISP installation directory
  --backup-dir PATH       Backup directory location
  -h, --help              Show help message

Examples:
  python3 misp-restore.py --list
  python3 misp-restore.py --show latest
  python3 misp-restore.py --restore latest
  python3 misp-restore.py --restore misp-backup-20251011_143052
  python3 misp-restore.py  # Interactive mode
```

### Common Command Combinations

```bash
# Safe routine update
python3 misp-update.py --all

# Fast security patch
python3 misp-update.py --images --no-rolling

# Major upgrade with clean start
python3 misp-update.py --all --recreate

# Preview major changes
python3 misp-update.py --all --recreate --dry-run

# Update and rebuild in dev environment
python3 misp-update.py --all --recreate --skip-backup --misp-dir /opt/misp-dev

# Check everything is current
python3 misp-update.py --check-only && python3 misp-update.py --version-info

# Restore from backup after failed update
python3 misp-restore.py --restore latest
```

### Backup Management Commands

```bash
# List all backups
python3 misp-restore.py --list

# Show backup details
python3 misp-restore.py --show latest

# Clean old backups (manual - be careful!)
cd /opt/misp-backups
ls -lt  # Review backups
rm -rf misp-backup-YYYYMMDD_HHMMSS  # Delete specific backup

# Backup current state manually (without update)
cd /opt/misp
BACKUP_DIR=/opt/misp-backups/manual-$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp .env PASSWORDS.txt docker-compose.yml $BACKUP_DIR/
cp -r ssl $BACKUP_DIR/
sudo docker compose exec -T db mysqldump -umisp -p$(grep MYSQL_PASSWORD .env | cut -d= -f2) misp > $BACKUP_DIR/misp_database.sql
```

---

## FAQ

### Q: How often should I update MISP?

**A:** 
- **Security updates:** Within 1-2 weeks
- **Minor updates:** Monthly
- **Major versions:** Quarterly, after thorough testing

### Q: How long does an update take?

**A:**
- **Check only:** 10-30 seconds
- **Image update:** 10-20 minutes (first time), 2-5 minutes (subsequent)
- **Repository update:** 1-3 minutes
- **Full update:** 15-30 minutes
- **With recreation:** 20-40 minutes

### Q: How much downtime should I expect?

**A:**
- **Rolling restart:** 2-5 minutes
- **Fast restart:** 30 seconds
- **Recreation:** 5-10 minutes

### Q: Can I update without downtime?

**A:** No, but rolling restarts minimize downtime to 2-5 minutes. For zero-downtime, you need a clustered/HA setup.

### Q: What if the update fails?

**A:** 
1. Review logs in `/var/log/misp-install/`
2. Check container status: `sudo docker compose ps`
3. Restore from backup (see Backup & Rollback section)
4. Open GitHub issue or seek community support

### Q: Can I skip the backup?

**A:** Not recommended. Backups are critical for recovery. Only skip in dev/test environments or if you just created a manual backup.

### Q: Do I need to stop MISP before updating?

**A:** No, the script handles starting/stopping services.

### Q: Will I lose data during update?

**A:** No, if backup is created. Database and configurations are preserved.

### Q: How do I update MISP Modules separately?

**A:** They're included in `--images` update. Use `--images` to update modules without touching repository.

### Q: Can I automate updates?

**A:** Yes, but carefully:

```bash
# Create cron job for check-only (safe)
0 9 * * 1 python3 ~/misp-update.py --check-only >> ~/update-checks.log 2>&1

# Automated updates NOT recommended - always review first
```

### Q: What if I see "WARN" messages?

**A:** Docker Compose warnings about unset variables are normal and can be ignored. The script suppresses them in output but they appear in logs.

### Q: How do I restore from a backup?

**A:** Use the `misp-restore.py` tool:

```bash
# List all backups
python3 misp-restore.py --list

# Restore from latest
python3 misp-restore.py --restore latest

# Interactive mode
python3 misp-restore.py
```

The restore tool automatically:
- Creates a pre-restore backup
- Restores configs, SSL certs, and database
- Restarts services
- Verifies the restoration

### Q: Can I test a backup without affecting production?

**A:** Yes, restore to a test/dev environment:

```bash
python3 misp-restore.py --restore latest --misp-dir /opt/misp-test
```

### Q: What if the restore tool fails?

**A:** Use manual restore (see "Manual Restore (Emergency)" section in docs) or restore individual files:

```bash
# Just restore configs (no database)
python3 misp-restore.py --restore latest --skip-database
```

### Q: How do I check if MISP is working after update?

**A:**
```bash
# Quick checks
curl -k https://misp-dev.lan  # Should return 200 or 302
cd /opt/misp && sudo docker compose ps  # All should be "Up"

# Detailed checks
python3 misp-update.py --version-info  # Shows all versions
cd /opt/misp && sudo docker compose logs --tail=50  # Recent logs
```

---

## Support & Resources

### Scripts

- **misp-update.py** - Update tool for keeping MISP current
- **misp-restore.py** - Restore tool for recovering from backups
- **misp-install.py** - Original installation tool

### Logs

All operations are logged to: `/var/log/misp-install/misp-update-TIMESTAMP.log`

```bash
# View latest log
ls -lt /var/log/misp-install/ | head -5
tail -f /var/log/misp-install/misp-update-*.log
```

### Get Help

- **MISP Documentation:** https://www.misp-project.org/documentation/
- **MISP GitHub:** https://github.com/MISP/MISP
- **MISP Docker:** https://github.com/MISP/misp-docker
- **Community:** https://www.misp-project.org/community/

### Reporting Issues

When reporting issues, include:

1. Output of `python3 misp-update.py --check-only`
2. Output of `python3 misp-update.py --version-info`
3. Error messages from logs
4. Container status: `cd /opt/misp && sudo docker compose ps`
5. System info: `uname -a`, `docker --version`

---

## Version History

### v1.0 (2025-10-11)
- Initial release
- Support for repository and image updates
- Automatic backup creation
- Health checking
- Version reporting
- Dry run mode
- Container recreation
- Rolling vs fast restart options
- Automated restore tool (`misp-restore.py`)
- Interactive and command-line restore modes
- Pre-restore backup creation
- Restore verification

---

**Document Version:** 1.0  
**Script Version:** 1.0  
**Last Updated:** 2025-10-11  

For the latest version of this documentation, check the repository or run:
```bash
python3 misp-update.py --help
```