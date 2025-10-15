# MISP Maintenance Automation Guide

**Author**: tKQB Enterprises
**Version**: 1.0
**Created**: October 2025
**Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Automated Maintenance Scripts](#automated-maintenance-scripts)
3. [Daily Maintenance](#daily-maintenance)
4. [Weekly Maintenance](#weekly-maintenance)
5. [Cron Setup](#cron-setup)
6. [Manual Execution](#manual-execution)
7. [Monitoring & Logs](#monitoring--logs)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Overview

The MISP installation includes automated maintenance scripts to keep your threat intelligence platform up-to-date and healthy. These scripts ensure that:

- **OSINT feeds** are fetched daily (latest threat indicators)
- **Taxonomies & galaxies** are updated weekly (classification systems)
- **Database** is optimized for performance
- **Health checks** catch issues early
- **Disk space** is monitored

### Components Requiring Updates

| Component | Frequency | Script | Why Important |
|-----------|-----------|--------|---------------|
| Warninglists | Daily | `misp-daily-maintenance.py` | False positive filters (reduce noise) |
| OSINT Feeds | Daily | `misp-daily-maintenance.py` | Latest threat intelligence IOCs |
| Feed Cache | Daily | `misp-daily-maintenance.py` | Faster correlation performance |
| Taxonomies | Weekly | `misp-weekly-maintenance.py` | Classification tags (TLP, ICS, Priority) |
| Galaxies | Weekly | `misp-weekly-maintenance.py` | MITRE ATT&CK, threat actors, malware |
| Object Templates | Weekly | `misp-weekly-maintenance.py` | Structured threat intel objects |
| Notice Lists | Weekly | `misp-weekly-maintenance.py` | Community notices |
| Database Optimization | Weekly | `misp-weekly-maintenance.py` | Query performance |

---

## Automated Maintenance Scripts

Three scripts work together to keep MISP healthy:

### 1. `misp-daily-maintenance.py`
**Purpose**: Daily updates for time-sensitive components
**Schedule**: Every day at 2:00 AM
**Duration**: 5-10 minutes

**Tasks**:
- ✅ Container health check (verify all services running)
- ✅ Disk space check (warn if >80%, critical if >90%)
- ✅ Update warninglists (false positive filters)
- ✅ Fetch all enabled OSINT feeds (threat intelligence)
- ✅ Cache feed data (faster correlation)

### 2. `misp-weekly-maintenance.py`
**Purpose**: Weekly updates for slower-changing components
**Schedule**: Every Sunday at 3:00 AM
**Duration**: 15-30 minutes

**Tasks**:
- ✅ Update taxonomies (classification systems)
- ✅ Update galaxies (MITRE ATT&CK, threat actors, malware families)
- ✅ Update object templates
- ✅ Update notice lists
- ✅ Verify utilities sector configurations enabled
- ✅ Optimize database tables (improve query performance)
- ✅ Generate statistics

### 3. `setup-misp-maintenance-cron.sh`
**Purpose**: Install/manage cron jobs
**Usage**: Interactive or automated setup

**Features**:
- ✅ Creates cron jobs for daily and weekly maintenance
- ✅ Sets up log directory (`/var/log/misp-maintenance/`)
- ✅ Makes scripts executable
- ✅ Validates scripts exist before installation
- ✅ Can remove cron jobs (for testing or decommissioning)
- ✅ Shows cron job status

---

## Daily Maintenance

### Schedule
```
Daily at 2:00 AM
```

### What It Does

**1. Container Health Check**
```
Checks all critical containers are running:
  ✓ misp-core (web interface)
  ✓ misp-modules (enrichment)
  ✓ misp-workers (background jobs)
  ✓ db (MariaDB database)
  ✓ redis (caching)
```

**2. Disk Space Check**
```
Monitors /opt/misp disk usage:
  - Warning at 80% full
  - Critical at 90% full
  - Logs alert and sends to stdout
```

**3. Update Warninglists**
```
Updates false positive filters:
  - Reduces noise in threat intelligence
  - Filters benign IPs/domains
  - Examples: Google IPs, Cloudflare DNS, legitimate software
```

**4. Fetch OSINT Feeds**
```
Downloads latest IOCs from enabled feeds:
  - Malware URLs (URLhaus, ThreatFox)
  - C2 infrastructure (Bambenek, Abuse.ch)
  - Phishing (OpenPhish, Phishtank)
  - IP reputation (Blocklist.de, Botvrij.eu)

Timeout: 10 minutes for all feeds
```

**5. Cache Feed Data**
```
Pre-processes feed data for faster correlation:
  - Builds correlation tables
  - Indexes IOCs
  - Improves query performance
```

### Manual Execution

```bash
# Test without making changes (dry-run)
cd /home/gallagher/misp-install/misp-install/scripts
python3 misp-daily-maintenance.py --dry-run

# Run actual daily maintenance
python3 misp-daily-maintenance.py
```

### Expected Output

```
================================================================================
  MISP Daily Maintenance
  2025-10-15 02:00:00
================================================================================

================================================================================
  Task 1: Check Container Health
================================================================================

✓ Container misp-core running
✓ Container misp-modules running
✓ Container misp-workers running
✓ Container db running
✓ Container redis running

================================================================================
  Task 2: Check Disk Space
================================================================================

  Total: 100.00 GB
  Used:  45.30 GB
  Free:  54.70 GB
  Usage: 45.3%

✓ Disk space healthy (45.3% used)

================================================================================
  Task 3: Update Warninglists
================================================================================

Updating warninglists (false positive filters)...
This helps reduce false positives in threat intelligence.

✓ Warninglists updated successfully

================================================================================
  Task 4: Fetch OSINT Feeds
================================================================================

Fetching all enabled threat intelligence feeds...
This downloads latest IOCs from configured OSINT sources.

✓ Feeds fetched successfully

================================================================================
  Task 5: Cache Feed Data
================================================================================

Caching feed data for faster correlation...

✓ Feed data cached successfully

================================================================================
  Daily Maintenance Report
================================================================================

  Date: 2025-10-15 02:05:30
  Tasks Completed: 5
  Tasks Failed: 0
  Success Rate: 100.0%

✓ All daily maintenance tasks completed successfully!
```

---

## Weekly Maintenance

### Schedule
```
Every Sunday at 3:00 AM
```

### What It Does

**1. Update Taxonomies**
```
Updates classification systems:
  - TLP (Traffic Light Protocol) - sharing restrictions
  - ICS taxonomy - industrial control systems
  - DHS-CIIP-sectors - critical infrastructure
  - Priority levels - event prioritization
  - Workflow status - incident lifecycle
  - Incident categories - event classification
```

**2. Update Galaxies** (Longest Task: 5-10 minutes)
```
Updates threat intelligence knowledge bases:
  - MITRE ATT&CK - tactics, techniques, procedures
  - MITRE ATT&CK for ICS - OT/SCADA specific TTPs
  - Threat actors - APT groups (Dragonfly, XENOTIME, etc.)
  - ICS malware - TRITON, INDUSTROYER, Stuxnet, etc.
  - Ransomware families - REvil, Conti, LockBit, etc.
  - Tools & software - threat actor toolkits
```

**3. Update Object Templates**
```
Updates structured object definitions:
  - Network objects (IP, domain, URL)
  - File objects (hash, filename, path)
  - Email objects (headers, attachments)
  - ICS objects (solar inverters, wind turbines, PLCs)
```

**4. Update Notice Lists**
```
Updates community notices and warnings
```

**5. Verify Utilities Sector Configuration**
```
Checks that utilities-specific features are enabled:
  - ICS taxonomy
  - DHS-CIIP sectors taxonomy
  - MITRE ATT&CK for ICS galaxy
  - Utilities threat actors
```

**6. Optimize Database**
```
Optimizes MariaDB tables for performance:
  - attributes (IOC storage)
  - events (threat intel events)
  - feeds (feed configuration)
  - servers (sync servers)
  - correlations (IOC relationships)
  - shadow_attributes (proposals)

Reduces fragmentation and improves query speed
```

**7. Generate Statistics**
```
Captures MISP usage metrics:
  - Total events
  - Total attributes (IOCs)
```

### Manual Execution

```bash
# Test without making changes (dry-run)
cd /home/gallagher/misp-install/misp-install/scripts
python3 misp-weekly-maintenance.py --dry-run

# Run actual weekly maintenance
python3 misp-weekly-maintenance.py
```

### Expected Output

```
================================================================================
  MISP Weekly Maintenance
  2025-10-20 03:00:00
================================================================================

================================================================================
  Task 1: Update Taxonomies
================================================================================

Updating taxonomies (classification systems)...
Taxonomies include: TLP, ICS, Critical Infrastructure, Priority Levels

✓ Taxonomies updated successfully

================================================================================
  Task 2: Update Galaxies
================================================================================

Updating galaxies (MITRE ATT&CK, threat actors, malware families)...
This is the largest update and may take 5-10 minutes.

✓ Galaxies updated successfully

================================================================================
  Task 3: Update Object Templates
================================================================================

Updating object templates...
Templates for structured threat intelligence objects.

✓ Object templates updated successfully

================================================================================
  Task 4: Update Notice Lists
================================================================================

Updating notice lists...

✓ Notice lists updated successfully

================================================================================
  Task 5: Verify Utilities Sector Configuration
================================================================================

Verifying utilities sector taxonomies and galaxies are enabled...

Note: Manual verification recommended:
  1. Check ICS taxonomy is enabled
  2. Check DHS-CIIP sectors taxonomy is enabled
  3. Verify MITRE ATT&CK for ICS is updated
  4. Verify ICS threat actors are in galaxy

✓ Configuration verification noted

================================================================================
  Task 6: Optimize Database
================================================================================

Optimizing MISP database tables...
This improves query performance and reduces fragmentation.

✓ Optimized table: attributes
✓ Optimized table: events
✓ Optimized table: feeds
✓ Optimized table: servers
✓ Optimized table: correlations
✓ Optimized table: shadow_attributes

Database optimization: 6 tables optimized, 0 failed

================================================================================
  Task 7: Generate Statistics
================================================================================

Generating MISP usage statistics...

✓ Statistics generated
  Events: 1234
  Attributes: 56789

================================================================================
  Weekly Maintenance Report
================================================================================

  Date: 2025-10-20 03:20:00
  Tasks Completed: 7
  Tasks Failed: 0
  Success Rate: 100.0%

Next Steps:
  1. Review MISP web interface for new taxonomies/galaxies
  2. Enable any new relevant ICS/utilities threat actors
  3. Check OSINT feeds are fetching data (via daily maintenance)
  4. Review MISP logs for any errors

✓ All weekly maintenance tasks completed successfully!
```

---

## Cron Setup

### Automated Setup (Recommended)

```bash
cd /home/gallagher/misp-install/misp-install/scripts
./setup-misp-maintenance-cron.sh --auto
```

**What This Does**:
1. ✅ Creates `/var/log/misp-maintenance/` directory
2. ✅ Makes scripts executable
3. ✅ Adds 2 cron jobs:
   - Daily maintenance: `0 2 * * *` (2 AM daily)
   - Weekly maintenance: `0 3 * * 0` (3 AM Sundays)
4. ✅ Logs to dated files (e.g., `daily-20251015.log`)

### Interactive Setup

```bash
cd /home/gallagher/misp-install/misp-install/scripts
./setup-misp-maintenance-cron.sh
```

**Prompts you to confirm before installation**

### Manual Setup

```bash
# Open crontab editor
crontab -e

# Add these lines:

# MISP Daily Maintenance (2 AM)
0 2 * * * cd /home/gallagher/misp-install/misp-install/scripts && python3 misp-daily-maintenance.py >> /var/log/misp-maintenance/daily-$(date +\%Y\%m\%d).log 2>&1

# MISP Weekly Maintenance (Sunday 3 AM)
0 3 * * 0 cd /home/gallagher/misp-install/misp-install/scripts && python3 misp-weekly-maintenance.py >> /var/log/misp-maintenance/weekly-$(date +\%Y\%m\%d).log 2>&1
```

### Check Cron Job Status

```bash
cd /home/gallagher/misp-install/misp-install/scripts
./setup-misp-maintenance-cron.sh --status
```

**Output**:
```
╔════════════════════════════════════════════════════════╗
║   MISP Maintenance Cron Job Status                    ║
╚════════════════════════════════════════════════════════╝

Current cron jobs:

# MISP Daily Maintenance (2 AM)
0 2 * * * cd /home/gallagher/misp-install/misp-install/scripts && python3 misp-daily-maintenance.py >> /var/log/misp-maintenance/daily-$(date +\%Y\%m\%d).log 2>&1

# MISP Weekly Maintenance (Sunday 3 AM)
0 3 * * 0 cd /home/gallagher/misp-install/misp-install/scripts && python3 misp-weekly-maintenance.py >> /var/log/misp-maintenance/weekly-$(date +\%Y\%m\%d).log 2>&1

✓ MISP maintenance cron jobs are configured

Recent maintenance logs:

-rw-r--r-- 1 gallagher gallagher  12345 Oct 15 02:05 daily-20251015.log
-rw-r--r-- 1 gallagher gallagher  23456 Oct 13 03:20 weekly-20251013.log
```

### Remove Cron Jobs

```bash
cd /home/gallagher/misp-install/misp-install/scripts
./setup-misp-maintenance-cron.sh --remove
```

---

## Manual Execution

### Test Before Deploying

Always test scripts before setting up cron jobs:

```bash
cd /home/gallagher/misp-install/misp-install/scripts

# Test daily maintenance (dry-run)
python3 misp-daily-maintenance.py --dry-run

# Test weekly maintenance (dry-run)
python3 misp-weekly-maintenance.py --dry-run

# Test cron setup script
./setup-misp-maintenance-cron.sh --test
```

### Run Individual Tasks

```bash
# Daily maintenance only
python3 scripts/misp-daily-maintenance.py

# Weekly maintenance only
python3 scripts/misp-weekly-maintenance.py
```

### Force Update Outside Schedule

```bash
# Need to update galaxies immediately (e.g., new MITRE ATT&CK release)
python3 scripts/misp-weekly-maintenance.py

# Need to fetch feeds now (e.g., urgent threat intel)
python3 scripts/misp-daily-maintenance.py
```

---

## Monitoring & Logs

### Log Locations

| Log Type | Location | Rotation |
|----------|----------|----------|
| Daily Maintenance | `/var/log/misp-maintenance/daily-YYYYMMDD.log` | Daily (one log per day) |
| Weekly Maintenance | `/var/log/misp-maintenance/weekly-YYYYMMDD.log` | Weekly (one log per Sunday) |
| MISP Internal | `/opt/misp/logs/misp-install-*.log` | Centralized JSON logs |
| Cron Execution | `/var/log/syslog` | System cron log |

### View Logs

```bash
# Today's daily maintenance log
tail -f /var/log/misp-maintenance/daily-$(date +%Y%m%d).log

# Last Sunday's weekly maintenance log
tail -f /var/log/misp-maintenance/weekly-$(date -d "last Sunday" +%Y%m%d).log

# All recent maintenance logs
ls -lht /var/log/misp-maintenance/ | head -10

# Cron execution history
grep misp-maintenance /var/log/syslog | tail -20
```

### Parse JSON Logs

Daily and weekly maintenance scripts also log to `/opt/misp/logs/` in JSON format:

```bash
# View daily maintenance JSON logs
tail -f /opt/misp/logs/misp-daily-maintenance-*.log | jq '.'

# View weekly maintenance JSON logs
tail -f /opt/misp/logs/misp-weekly-maintenance-*.log | jq '.'

# Filter for errors only
cat /opt/misp/logs/misp-daily-maintenance-*.log | jq 'select(.level=="ERROR")'

# Count successful operations today
cat /opt/misp/logs/misp-daily-maintenance-$(date +%Y%m%d)*.log | jq 'select(.result=="success")' | wc -l
```

### Monitor Cron Execution

```bash
# Check if cron jobs ran today
grep "misp-daily-maintenance" /var/log/syslog | grep "$(date +%Y-%m-%d)"

# Check last run time
crontab -l | grep misp
```

### Email Notifications (Optional)

Configure cron to email on failures:

```bash
# Add to top of crontab (crontab -e)
MAILTO=admin@company.com

# Cron will email if any job fails (non-zero exit code)
```

---

## Troubleshooting

### Issue 1: Cron Job Not Running

**Symptoms**:
- No new logs in `/var/log/misp-maintenance/`
- Last log is old (more than 1 day for daily, more than 1 week for weekly)

**Diagnosis**:
```bash
# Check cron jobs are installed
crontab -l | grep misp

# Check cron service is running
systemctl status cron

# Check syslog for errors
grep CRON /var/log/syslog | grep misp | tail -20
```

**Solutions**:
```bash
# Reinstall cron jobs
cd /home/gallagher/misp-install/misp-install/scripts
./setup-misp-maintenance-cron.sh --auto

# Restart cron service
sudo systemctl restart cron

# Verify scripts are executable
ls -l misp-daily-maintenance.py
chmod +x misp-daily-maintenance.py misp-weekly-maintenance.py
```

---

### Issue 2: Script Fails with Docker Permission Denied

**Symptoms**:
```
ERROR: permission denied while trying to connect to the Docker daemon socket
```

**Cause**: User running cron job not in docker group (v5.4 architecture)

**Solution**:
```bash
# Scripts use 'sudo docker compose' which requires passwordless sudo
# Check sudoers configuration (see SETUP.md)
sudo visudo

# Or add user to docker group (may still need sudo for some operations)
sudo usermod -aG docker $USER
newgrp docker
```

---

### Issue 3: Feed Fetch Timeout

**Symptoms**:
```
WARNING: Some feeds may have failed to fetch
Command timeout: Fetch all enabled feeds
```

**Cause**: Large feeds or slow network

**Solution**:
```bash
# Edit misp-daily-maintenance.py
# Increase timeout for feed fetch (line ~217)
timeout=600  # Change to 900 (15 minutes)

# Or fetch feeds individually for problematic feeds
cd /opt/misp
sudo docker compose exec -T misp-core /var/www/MISP/app/Console/cake Server fetchFeed 1
```

---

### Issue 4: Disk Space Critical

**Symptoms**:
```
CRITICAL: Disk usage at 92.5% (threshold: 90%)
```

**Immediate Actions**:
```bash
# Check what's using space
du -sh /opt/misp/* | sort -h

# Clear old Docker images
sudo docker system prune -a

# Clear old backups
ls -lht ~/misp-backups/ | tail -20
rm -rf ~/misp-backups/misp-backup-OLD_DATE

# Clear old feed data (if safe)
cd /opt/misp
sudo docker compose exec -T misp-core rm -rf /var/www/MISP/app/tmp/cache/*
```

**Long-Term Solution**:
```bash
# Expand disk partition
# Move /opt/misp to larger volume
# Implement backup rotation policy
```

---

### Issue 5: Container Unhealthy

**Symptoms**:
```
✗ Container misp-core not running (state: unhealthy)
```

**Diagnosis**:
```bash
# Check container logs
cd /opt/misp
sudo docker compose logs misp-core | tail -50

# Check container health
sudo docker inspect misp-misp-core-1 | jq '.[].State.Health'
```

**Known Issue**: MISP core container reports "unhealthy" despite working correctly
- Root cause: Healthcheck uses BASE_URL domain which container can't resolve internally
- Impact: None on functionality (see KNOWN-ISSUES.md)
- Workaround: Ignore unhealthy status if MISP web interface works

**Real Issues to Check**:
```bash
# Database connection
sudo docker compose exec -T misp-core /var/www/MISP/app/Console/cake Database dbConnect

# MISP workers running
sudo docker compose exec -T misp-core supervisorctl status
```

---

### Issue 6: Galaxy Update Fails

**Symptoms**:
```
✗ Failed to update galaxies
Command timeout: Update galaxies
```

**Cause**: Galaxy update is large (100+ MB of data), may timeout on slow systems

**Solution**:
```bash
# Edit misp-weekly-maintenance.py
# Increase galaxy update timeout (line ~183)
timeout=600  # Change to 1200 (20 minutes)

# Or run galaxy update manually (outside cron)
cd /opt/misp
sudo docker compose exec -T misp-core /var/www/MISP/app/Console/cake Admin updateGalaxies --force
```

---

## Best Practices

### 1. Test Before Production

Always run dry-run mode first:
```bash
python3 misp-daily-maintenance.py --dry-run
python3 misp-weekly-maintenance.py --dry-run
```

### 2. Monitor Logs Regularly

Set up weekly log review:
```bash
# Create weekly log review checklist
# - Check for failed tasks
# - Verify feeds are updating
# - Confirm disk space is healthy
# - Review any warnings
```

### 3. Schedule Wisely

Default schedule is optimized for minimal impact:
- **Daily: 2 AM** - Low user activity, before business hours
- **Weekly: Sunday 3 AM** - Weekend, low impact, galaxy update has time to complete

Adjust if needed:
```bash
# Example: Run daily maintenance at 1 AM instead
0 1 * * * cd /home/gallagher/misp-install/misp-install/scripts && python3 misp-daily-maintenance.py ...
```

### 4. Keep Scripts Updated

When updating MISP installation:
```bash
cd /home/gallagher/misp-install/misp-install
git pull

# Verify maintenance scripts still work
python3 scripts/misp-daily-maintenance.py --dry-run
python3 scripts/misp-weekly-maintenance.py --dry-run
```

### 5. Backup Before Major Changes

Before modifying maintenance scripts:
```bash
# Backup current working scripts
cp scripts/misp-daily-maintenance.py scripts/misp-daily-maintenance.py.backup
cp scripts/misp-weekly-maintenance.py scripts/misp-weekly-maintenance.py.backup

# If changes fail, restore backups
mv scripts/misp-daily-maintenance.py.backup scripts/misp-daily-maintenance.py
```

### 6. Document Custom Changes

If you customize scripts, document in CLAUDE.md:
```markdown
## Custom Maintenance Modifications

- 2025-10-15: Increased feed fetch timeout to 15 minutes (slow network)
- 2025-10-20: Added custom disk space notification (email to admin@company.com)
```

### 7. Align with NERC CIP Compliance

For utilities sector organizations:
- Maintenance logs = CIP-007 audit evidence (system maintenance)
- Feed updates = CIP-008 incident intelligence (threat awareness)
- Health checks = CIP-007 security event monitoring

Save logs for required retention period (3-7 years depending on CIP requirements)

### 8. Integrate with Monitoring

Consider integrating with:
- **Splunk**: Ingest JSON logs from `/opt/misp/logs/`
- **Nagios/Zabbix**: Monitor cron job success/failure
- **Email alerts**: Configure cron MAILTO for failures
- **Slack/Teams**: Webhook notifications on critical issues

---

## Related Documentation

- **Installation Guide**: `README.md`
- **Utilities Sector Configuration**: `scripts/configure-misp-utilities-sector.py`
- **NERC CIP Configuration**: `docs/NERC_CIP_CONFIGURATION.md`
- **Centralized Logging**: `README_LOGGING.md`
- **Known Issues**: `KNOWN-ISSUES.md`

---

## Quick Reference Commands

```bash
# Setup cron jobs
./scripts/setup-misp-maintenance-cron.sh --auto

# Check cron job status
./scripts/setup-misp-maintenance-cron.sh --status

# Test scripts (dry-run)
python3 scripts/misp-daily-maintenance.py --dry-run
python3 scripts/misp-weekly-maintenance.py --dry-run

# Run maintenance manually
python3 scripts/misp-daily-maintenance.py
python3 scripts/misp-weekly-maintenance.py

# View logs
tail -f /var/log/misp-maintenance/daily-$(date +%Y%m%d).log
tail -f /var/log/misp-maintenance/weekly-*.log

# Remove cron jobs
./scripts/setup-misp-maintenance-cron.sh --remove
```

---

**Last Updated**: October 2025
**Maintained By**: tKQB Enterprises
