# MISP Automated Backup Setup Guide

**Version:** 1.0  
**Script:** `misp-backup-cron.py`  
**Last Updated:** 2025-10-11

---

## Overview

Automated nightly backup system for MISP with intelligent full/incremental rotation:

- **Sunday:** Full backup (keep 8 weeks)
- **Monday-Saturday:** Incremental backup (auto-deleted after next Sunday)
- **Automatic:** Runs via cron every night
- **Verified:** Each backup is tested for integrity
- **Notifications:** Optional email alerts

---

## Quick Setup

### 1. Install the Script

```bash
# Copy script to home directory
cp misp-backup-cron.py ~/
chmod +x ~/misp-backup-cron.py

# Test it manually first
python3 ~/misp-backup-cron.py --dry-run
```

### 2. Configure Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * /usr/bin/python3 /home/user/misp-backup-cron.py >> /home/user/misp-logs/backup-cron.log 2>&1
```

### 3. Verify Setup

```bash
# Check cron job is installed
crontab -l

# Test the backup manually
python3 ~/misp-backup-cron.py --full

# Check backup was created
ls -lh /opt/misp-backups/full/
ls -lh /opt/misp-backups/incremental/
```

**Done!** Your MISP backups will now run automatically every night.

---

## Backup Strategy

### Sunday (Full Backup)

**What Happens:**
1. Creates full backup in `/opt/misp-backups/full/`
2. Includes: database + configs + SSL certs + all files
3. Verifies backup integrity
4. Deletes incremental backups from the past week
5. Removes old full backups (keeps most recent 8)

**Retention:** 8 weeks (56 days)

### Monday - Saturday (Incremental)

**What Happens:**
1. Creates incremental backup in `/opt/misp-backups/incremental/`
2. Includes: database + configs + SSL certs
3. Verifies backup integrity
4. **Kept until next Sunday**, then deleted

**Purpose:** Quick daily snapshots for recent recovery

---

## Directory Structure

```
/opt/misp-backups/
├── full/
│   ├── full-20251005_020001/        # Week 1
│   ├── full-20251012_020001/        # Week 2
│   ├── full-20251019_020001/        # Week 3
│   ├── full-20251026_020001/        # Week 4
│   ├── full-20251102_020001/        # Week 5
│   ├── full-20251109_020001/        # Week 6
│   ├── full-20251116_020001/        # Week 7
│   └── full-20251123_020001/        # Week 8 (oldest kept)
└── incremental/
    ├── incremental-monday-20251124_020001/
    ├── incremental-tuesday-20251125_020001/
    ├── incremental-wednesday-20251126_020001/
    ├── incremental-thursday-20251127_020001/
    ├── incremental-friday-20251128_020001/
    └── incremental-saturday-20251129_020001/
    # All deleted after next Sunday backup

Each backup contains:
├── misp_database.sql           # Full database dump
├── .env                        # Configuration
├── PASSWORDS.txt               # Credentials
├── docker-compose.yml          # Docker config
├── docker-compose.override.yml # Docker overrides
├── ssl/                        # SSL certificates
│   ├── cert.pem
│   └── key.pem
└── metadata.json               # Backup info
```

---

## Configuration

### Basic Settings

Edit `misp-backup-cron.py` to customize:

```python
class BackupConfig:
    # Directories
    MISP_DIR = Path.home() / "misp-docker"
    BACKUP_BASE_DIR = Path.home() / "misp-backups"
    
    # Retention (weeks to keep full backups)
    FULL_BACKUP_WEEKS = 8
    
    # Email notifications
    EMAIL_ENABLED = False  # Set to True to enable
```

### Email Notifications

To enable email alerts on backup completion/failure:

```python
class BackupConfig:
    # Email settings
    EMAIL_ENABLED = True
    EMAIL_FROM = "misp-backup@yourdomain.com"
    EMAIL_TO = ["admin@yourdomain.com", "ops@yourdomain.com"]
    SMTP_SERVER = "smtp.yourdomain.com"
    SMTP_PORT = 587
    SMTP_USER = "misp-backup"
    SMTP_PASSWORD = "your-smtp-password"
```

Or use local mail server:

```python
    EMAIL_ENABLED = True
    SMTP_SERVER = "localhost"
    SMTP_PORT = 25
    SMTP_USER = None
    SMTP_PASSWORD = None
```

---

## Usage

### Automatic (Cron)

Once configured, backups run automatically:
- **Every night at 2 AM**
- **Sunday:** Full backup
- **Mon-Sat:** Incremental backup
- **Automatic cleanup** of old backups

### Manual Execution

```bash
# Run normal backup (full on Sunday, incremental otherwise)
python3 ~/misp-backup-cron.py

# Force full backup on any day
python3 ~/misp-backup-cron.py --full

# Test without making changes
python3 ~/misp-backup-cron.py --dry-run

# Run with email notification
python3 ~/misp-backup-cron.py --notify

# Combine options
python3 ~/misp-backup-cron.py --full --notify
```

---

## Cron Schedule Examples

### Default: Daily at 2 AM

```bash
0 2 * * * /usr/bin/python3 /home/user/misp-backup-cron.py >> /home/user/misp-logs/backup-cron.log 2>&1
```

### Daily at 3:30 AM

```bash
30 3 * * * /usr/bin/python3 /home/user/misp-backup-cron.py >> /home/user/misp-logs/backup-cron.log 2>&1
```

### Twice Daily (2 AM and 2 PM)

```bash
0 2,14 * * * /usr/bin/python3 /home/user/misp-backup-cron.py >> /home/user/misp-logs/backup-cron.log 2>&1
```

### Every 6 Hours

```bash
0 */6 * * * /usr/bin/python3 /home/user/misp-backup-cron.py >> /home/user/misp-logs/backup-cron.log 2>&1
```

---

## Monitoring

### Check Backup Logs

```bash
# View latest backup log
ls -lt /opt/misp/logs/misp-backup-*.log | head -1 | xargs cat

# View cron log
cat /opt/misp/logs/backup-cron.log

# Check last 50 lines (JSON format)
tail -50 /opt/misp/logs/misp-backup-cron.log | jq '.'

# Follow live with JSON formatting
tail -f /opt/misp/logs/misp-backup-cron.log | jq '.'

# View only error messages
cat /opt/misp/logs/misp-backup-cron.log | jq 'select(.severity=="ERROR")'
```

**Note:** Logs use centralized JSON format with automatic rotation. See `README_LOGGING.md` for details.

### Check Backup Status

```bash
# List all backups with sizes
ls -lh /opt/misp-backups/full/
ls -lh /opt/misp-backups/incremental/

# Count backups
echo "Full backups: $(ls /opt/misp-backups/full/ | wc -l)"
echo "Incremental backups: $(ls /opt/misp-backups/incremental/ | wc -l)"

# Check total backup disk usage
du -sh /opt/misp-backups/
```

### Verify Latest Backup

```bash
# Check latest full backup
LATEST_FULL=$(ls -t /opt/misp-backups/full/ | head -1)
echo "Latest full backup: $LATEST_FULL"
ls -lh /opt/misp-backups/full/$LATEST_FULL/

# Verify database file exists and has content
LATEST_DB=$(ls -t /opt/misp-backups/full/ | head -1)
ls -lh /opt/misp-backups/full/$LATEST_DB/misp_database.sql

# Check backup metadata
cat /opt/misp-backups/full/$LATEST_FULL/metadata.json
```

---

## Restoring from Backups

### List Available Backups

```bash
# Use the restore tool
python3 misp-restore.py --list
```

### Restore Latest Full Backup

```bash
python3 misp-restore.py --restore latest --misp-dir /opt/misp --backup-dir /opt/misp-backups/full
```

### Restore Specific Backup

```bash
# List full backups
ls /opt/misp-backups/full/

# Restore specific one
python3 misp-restore.py --restore full-20251117_020001 --backup-dir /opt/misp-backups/full
```

### Restore from Incremental

```bash
# List incremental backups
ls /opt/misp-backups/incremental/

# Restore specific incremental
python3 misp-restore.py --restore incremental-wednesday-20251127_020001 --backup-dir /opt/misp-backups/incremental
```

---

## Troubleshooting

### Backup Not Running

**Check cron job:**
```bash
# List cron jobs
crontab -l

# Check cron service
sudo systemctl status cron

# Check cron logs
sudo grep CRON /var/log/syslog | tail -20
```

**Check permissions:**
```bash
# Ensure script is executable
chmod +x ~/misp-backup-cron.py

# Check Python path
which python3

# Test script manually
python3 ~/misp-backup-cron.py --dry-run
```

---

### Lock File Issues

If backup won't run due to lock file:

```bash
# Check if backup is actually running
ps aux | grep misp-backup-cron

# If not running, remove stale lock file
rm -f ~/.misp-backup.lock

# Try again
python3 ~/misp-backup-cron.py
```

---

### Backup Fails

**Check logs:**
```bash
# View latest backup log
ls -lt /opt/misp/logs/misp-backup-*.log | head -1 | xargs cat

# Check cron output
cat /opt/misp/logs/backup-cron.log
```

**Common issues:**

1. **Database not accessible**
   ```bash
   # Check containers running
   cd /opt/misp && sudo docker compose ps
   
   # Check database
   cd /opt/misp && sudo docker compose exec db mysqladmin ping
   ```

2. **Disk space full**
   ```bash
   # Check disk space
   df -h ~
   
   # Clean old backups manually if needed
   rm -rf /opt/misp-backups/full/full-YYYYMMDD_HHMMSS
   ```

3. **Permission issues**
   ```bash
   # Check backup directory permissions
   ls -ld /opt/misp-backups/
   
   # Fix if needed
   chmod 755 /opt/misp-backups/
   ```

---

### Email Notifications Not Working

**Test email configuration:**
```bash
# Test SMTP connection
python3 -c "
import smtplib
server = smtplib.SMTP('localhost', 25)
server.quit()
print('SMTP OK')
"
```

**Check mail logs:**
```bash
sudo tail -50 /var/log/mail.log
```

---

## Disk Space Management

### Monitor Backup Size

```bash
# Total backup space used
du -sh /opt/misp-backups/

# Size by type
du -sh /opt/misp-backups/full/
du -sh /opt/misp-backups/incremental/

# Individual backup sizes
du -sh /opt/misp-backups/full/* | sort -h
```

### Estimate Space Needed

**Rule of thumb:**
- **Full backup:** 2-5 GB (depends on database size)
- **8 weeks full:** 16-40 GB
- **6 daily incrementals:** 12-30 GB
- **Total needed:** ~30-70 GB

### Adjust Retention

To keep fewer full backups:

```python
# In misp-backup-cron.py
class BackupConfig:
    FULL_BACKUP_WEEKS = 4  # Keep only 4 weeks instead of 8
```

---

## Advanced Configuration

### Custom Backup Schedule

Keep different schedules for different days:

```bash
# Full backup Sunday at 2 AM
0 2 * * 0 /usr/bin/python3 /home/user/misp-backup-cron.py --full >> /home/user/misp-logs/backup-cron.log 2>&1

# Incremental Mon-Sat at 2 AM
0 2 * * 1-6 /usr/bin/python3 /home/user/misp-backup-cron.py >> /home/user/misp-logs/backup-cron.log 2>&1
```

### Additional Items to Backup

Add custom files/directories:

```python
class BackupConfig:
    FILES_TO_BACKUP = [
        '.env',
        'PASSWORDS.txt',
        'docker-compose.yml',
        'docker-compose.override.yml',
        'custom-config.json',  # Add your file
    ]
    
    DIRS_TO_BACKUP = [
        'ssl',
        'custom-data',  # Add your directory
    ]
```

### Remote Backup Copy

Automatically copy backups to remote server:

```bash
# Add to crontab after backup completes
0 3 * * * rsync -avz --delete /opt/misp-backups/full/ backup-server:/backups/misp/full/ >> /home/user/misp-logs/backup-sync.log 2>&1
```

---

## Best Practices

### ✅ Do's

- **Monitor regularly** - Check logs weekly
- **Test restores** - Verify backups work (monthly)
- **Keep off-site copy** - Sync to remote location
- **Document procedures** - Keep restore steps handy
- **Set up notifications** - Know when backups fail
- **Review retention** - Adjust based on compliance needs

### ❌ Don'ts

- **Don't ignore failures** - Fix issues immediately
- **Don't skip tests** - Untested backups are useless
- **Don't fill disk** - Monitor space usage
- **Don't store only local** - Always have off-site backup
- **Don't modify running backup** - Let it complete

---

## Compliance & Security

### Data Protection

- Backups contain **sensitive data** (passwords, keys, database)
- Stored in `/opt/misp-backups/` with **restricted permissions**
- Database files are **not encrypted** by default
- Consider **encrypting backup directory** for compliance

### Encryption (Optional)

```bash
# Encrypt backup directory
sudo apt install ecryptfs-utils
ecryptfs-add-passphrase

# Or use LUKS encrypted partition for /opt/misp-backups/
```

### Compliance Requirements

Adjust retention based on your requirements:
- **GDPR:** May require deletion after certain period
- **HIPAA:** May require longer retention
- **PCI-DSS:** Specific retention requirements

---

## Quick Reference

### Daily Operations

```bash
# Check if backup ran last night
ls -lt /opt/misp-backups/full/ | head -2
ls -lt /opt/misp-backups/incremental/ | head -2

# View last backup log
tail -50 /opt/misp/logs/backup-cron.log

# Run backup manually
python3 ~/misp-backup-cron.py
```

### Weekly Tasks

```bash
# Verify Sunday full backup created
ls -lt /opt/misp-backups/full/ | head -2

# Check incremental backups were cleaned
ls /opt/misp-backups/incremental/

# Review backup sizes
du -sh /opt/misp-backups/*/
```

### Monthly Tasks

```bash
# Test restore from latest backup
python3 misp-restore.py --show latest

# Review disk space
df -h ~

# Check old backups being deleted
ls -l /opt/misp-backups/full/ | wc -l  # Should be ≤ 8
```

---

## FAQ

**Q: What happens if Sunday backup fails?**  
A: Incremental backups continue. Fix issue and run `--full` manually.

**Q: Can I change backup time?**  
A: Yes, edit crontab: `crontab -e`

**Q: How much space do I need?**  
A: ~30-70 GB depending on database size. Monitor with `du -sh /opt/misp-backups/`

**Q: Can backups run while MISP is in use?**  
A: Yes, uses `--single-transaction` for consistent database snapshot.

**Q: What if I need more than 8 weeks?**  
A: Edit `FULL_BACKUP_WEEKS` in script.

**Q: Can I restore to a different server?**  
A: Yes, use `misp-restore.py --misp-dir /path/to/misp` on target server.

**Q: Are backups tested?**  
A: Yes, script verifies each backup after creation.

**Q: What about external volumes?**  
A: Database backups include all data. External file storage needs separate backup.

---

## Support

### Logs
- Backup logs: `/opt/misp/logs/misp-backup-*.log`
- Cron output: `/opt/misp/logs/backup-cron.log`

### Files
- Script: `~/misp-backup-cron.py`
- Lock file: `~/.misp-backup.lock`
- Backups: `/opt/misp-backups/`

### Tools
- `misp-backup-cron.py` - Automated backup script
- `misp-restore.py` - Restore tool
- `crontab -l` - View scheduled jobs

---

**Script Version:** 1.0  
**Last Updated:** 2025-10-11  

For latest version, check repository or contact support.