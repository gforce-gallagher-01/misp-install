# MISP Scripts Collection

**Version:** 1.0  
**Organization:** tKQB Enterprises  
**Last Updated:** 2025-10-11

Complete toolkit for installing, managing, backing up, and maintaining MISP (Malware Information Sharing Platform) via Docker.

---

## 📋 Quick Reference

| Script | Purpose | Typical Usage |
|--------|---------|--------------|
| `misp-install.py` | Initial MISP installation | One-time setup |
| `misp-update.py` | Update MISP components | Monthly maintenance |
| `misp-restore.py` | Restore from backup | After failures/disasters |
| `misp-backup-cron.py` | Automated nightly backups | Cron job |
| `backup-misp.sh` | Manual backup script | On-demand backups |
| `uninstall-misp.sh` | Complete MISP removal | Cleanup/reinstall |

---

## 🚀 Installation Script

### `misp-install.py`

**Purpose:** Complete automated MISP installation with Docker

**Features:**
- ✅ Pre-flight system checks (disk, RAM, CPU)
- ✅ Docker installation if needed
- ✅ Automatic password generation
- ✅ SSL certificate creation
- ✅ Configuration file setup
- ✅ Resume capability if interrupted
- ✅ Full logging

**Usage:**

```bash
# Basic installation (interactive)
python3 misp-install.py

# Resume interrupted installation
python3 misp-install.py --resume

# Skip pre-flight checks
python3 misp-install.py --skip-checks

# Use config file
python3 misp-install.py --config misp-config.json

# Non-interactive mode
python3 misp-install.py --config misp-config.json --non-interactive
```

**What It Creates:**
- `/opt/misp/` - MISP installation directory
- `/opt/misp/.env` - Configuration file
- `/opt/misp/PASSWORDS.txt` - All credentials
- `/opt/misp/ssl/` - SSL certificates
- `/var/log/misp-install/` - Installation logs

**Time Required:** 20-40 minutes (first time)

---

## 🔄 Update Script

### `misp-update.py`

**Purpose:** Safely update MISP components with automatic backup

**Features:**
- ✅ Check for updates before applying
- ✅ Automatic pre-update backup
- ✅ Repository and Docker image updates
- ✅ Health verification after update
- ✅ Rolling or fast restart options
- ✅ Dry run mode

**Common Commands:**

```bash
# Check what needs updating
python3 misp-update.py --check-only

# View detailed version info
python3 misp-update.py --version-info

# Update everything (recommended)
python3 misp-update.py --all

# Update only Docker images
python3 misp-update.py --images

# Update only repository
python3 misp-update.py --repository

# Dry run (preview changes)
python3 misp-update.py --all --dry-run

# Update with container recreation
python3 misp-update.py --all --recreate

# Fast restart (more downtime, but faster)
python3 misp-update.py --all --no-rolling
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
```

**Downtime:** 2-5 minutes (rolling), 30 seconds (fast)

---

## 💾 Restore Script

### `misp-restore.py`

**Purpose:** Restore MISP from backup with verification

**Features:**
- ✅ List available backups
- ✅ Preview backup contents
- ✅ Automated restoration process
- ✅ Pre-restore safety backup
- ✅ Verification testing
- ✅ Interactive or command-line modes

**Common Commands:**

```bash
# List all available backups
python3 misp-restore.py --list

# Show what's in latest backup
python3 misp-restore.py --show latest

# Show specific backup
python3 misp-restore.py --show misp-backup-20251011_143052

# Restore from latest backup
python3 misp-restore.py --restore latest

# Restore from specific backup
python3 misp-restore.py --restore misp-backup-20251011_143052

# Restore configs only (skip database)
python3 misp-restore.py --restore latest --skip-database

# Interactive mode (guided)
python3 misp-restore.py
```

**What It Restores:**
- ✅ Configuration files (.env, PASSWORDS.txt)
- ✅ Docker compose files
- ✅ SSL certificates
- ✅ Complete database
- ✅ All MISP settings

**Time Required:** 10-20 minutes

---

## 🤖 Automated Backup Script

### `misp-backup-cron.py`

**Purpose:** Nightly automated backups with intelligent rotation

**Backup Strategy:**
- **Sunday:** Full backup (keep 8 weeks)
- **Monday-Saturday:** Incremental backup (deleted after next Sunday)
- Automatic cleanup of old backups
- Verification of each backup
- Optional email notifications

**Manual Usage:**

```bash
# Run automatic backup (full on Sunday, incremental otherwise)
python3 misp-backup-cron.py

# Force full backup any day
python3 misp-backup-cron.py --full

# Test without making changes
python3 misp-backup-cron.py --dry-run

# Send email notification
python3 misp-backup-cron.py --notify
```

**Cron Setup:**

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * /usr/bin/python3 /home/gallagher/misp-backup-cron.py >> /home/gallagher/misp-logs/backup-cron.log 2>&1
```

**Backup Locations:**
- `/opt/misp-backups/full/` - Sunday full backups (8 weeks)
- `/opt/misp-backups/incremental/` - Daily backups (deleted each Sunday)

**Disk Space Needed:** 30-70 GB

**Monitoring:**

```bash
# Check last backup
ls -lt /opt/misp-backups/full/ | head -2
ls -lt /opt/misp-backups/incremental/ | head -2

# View backup log
tail -50 /var/log/misp-install/backup-cron.log

# Check disk usage
du -sh /opt/misp-backups/
```

---

## 📦 Manual Backup Script

### `backup-misp.sh`

**Purpose:** Quick manual backup for ad-hoc needs

**Features:**
- ✅ Simple shell script
- ✅ Fast execution
- ✅ Manual control
- ✅ Good for pre-maintenance backups

**Usage:**

```bash
# Make executable (first time)
chmod +x backup-misp.sh

# Run backup
./backup-misp.sh

# Run with sudo if needed
sudo ./backup-misp.sh
```

**When to Use:**
- Before manual changes
- Before major updates
- Quick backup before testing
- When Python not available

**Output:** Creates timestamped backup in `/opt/misp-backups/`

---

## 🗑️ Uninstall Script

### `uninstall-misp.sh`

**Purpose:** Completely remove MISP and all components

**⚠️ WARNING:** This script completely removes MISP! Use with caution.

**What It Removes:**
- ❌ All Docker containers
- ❌ All Docker volumes
- ❌ All Docker images
- ❌ Installation directory (`/opt/misp/`)
- ❌ Configuration files

**What It Preserves:**
- ✅ Backups (`/opt/misp-backups/`)
- ✅ Logs (`/var/log/misp-install/`)

**Usage:**

```bash
# Make executable
chmod +x uninstall-misp.sh

# Run uninstall (will prompt for confirmation)
./uninstall-misp.sh

# Force uninstall (skip confirmation)
./uninstall-misp.sh --force
```

**Before Running:**
1. ✅ Create backup: `python3 misp-backup-cron.py --full`
2. ✅ Verify backup: `python3 misp-restore.py --show latest`
3. ✅ Document reason for uninstall
4. ✅ Notify team if production system

**After Uninstall:**
- Clean install: `python3 misp-install.py`
- Restore data: `python3 misp-restore.py --restore latest`

---

## 📁 File Structure

```
~/
├── misp-docker/                    # MISP installation
│   ├── .env                       # Configuration
│   ├── PASSWORDS.txt              # Credentials
│   ├── docker-compose.yml         # Docker config
│   ├── ssl/                       # SSL certificates
│   └── POST-INSTALL-CHECKLIST.md  # Next steps
│
├── misp-backups/                  # All backups
│   ├── full/                      # Sunday full backups (8 weeks)
│   │   ├── full-20251005_020001/
│   │   ├── full-20251012_020001/
│   │   └── ...
│   └── incremental/               # Daily backups (Mon-Sat)
│       ├── incremental-monday-20251124_020001/
│       ├── incremental-tuesday-20251125_020001/
│       └── ...
│
└── misp-logs/                     # All logs
    ├── misp-install-*.log
    ├── misp-update-*.log
    ├── misp-backup-*.log
    ├── misp-restore-*.log
    └── backup-cron.log
```

---

## 🔧 Common Workflows

### Initial Setup

```bash
# 1. Install MISP
python3 misp-install.py

# 2. Wait for completion (20-40 minutes)
# 3. Access MISP at https://misp-dev.lan
# 4. Login with credentials from /opt/misp/PASSWORDS.txt

# 5. Set up automated backups
crontab -e
# Add: 0 2 * * * /usr/bin/python3 /home/gallagher/misp-backup-cron.py >> /home/gallagher/misp-logs/backup-cron.log 2>&1

# 6. Run first manual backup
python3 misp-backup-cron.py --full
```

### Monthly Maintenance

```bash
# 1. Check for updates
python3 misp-update.py --check-only

# 2. Review changes if available
cd /opt/misp && git log HEAD..origin/main --oneline

# 3. Preview update
python3 misp-update.py --all --dry-run

# 4. Perform update (auto-creates backup)
python3 misp-update.py --all

# 5. Verify MISP is working
python3 misp-update.py --version-info
curl -k https://misp-dev.lan
```

### Disaster Recovery

```bash
# 1. Check available backups
python3 misp-restore.py --list

# 2. Preview backup contents
python3 misp-restore.py --show latest

# 3. Restore from backup
python3 misp-restore.py --restore latest

# 4. Verify restoration
cd /opt/misp && sudo docker compose ps
curl -k https://misp-dev.lan
```

### Clean Reinstall

```bash
# 1. Create final backup
python3 misp-backup-cron.py --full

# 2. Verify backup
python3 misp-restore.py --show latest

# 3. Uninstall MISP
./uninstall-misp.sh

# 4. Reinstall fresh
python3 misp-install.py

# 5. Restore data if needed
python3 misp-restore.py --restore latest
```

---

## 📊 Monitoring Commands

### Check MISP Status

```bash
# Container status
cd /opt/misp && sudo docker compose ps

# View logs
cd /opt/misp && sudo docker compose logs -f

# Check versions
python3 misp-update.py --version-info

# Test web interface
curl -k https://misp-dev.lan
```

### Check Backups

```bash
# List all backups
python3 misp-restore.py --list

# Count backups
echo "Full: $(ls /opt/misp-backups/full/ 2>/dev/null | wc -l)"
echo "Incremental: $(ls /opt/misp-backups/incremental/ 2>/dev/null | wc -l)"

# Check disk usage
du -sh /opt/misp-backups/

# View backup log
tail -50 /var/log/misp-install/backup-cron.log
```

### Review Logs

```bash
# Latest install log
ls -lt /var/log/misp-install/misp-install-*.log | head -1 | xargs tail -100

# Latest update log
ls -lt /var/log/misp-install/misp-update-*.log | head -1 | xargs tail -100

# Latest backup log
ls -lt /var/log/misp-install/misp-backup-*.log | head -1 | xargs tail -100

# Cron backup log
tail -100 /var/log/misp-install/backup-cron.log
```

---

## 🆘 Troubleshooting

### MISP Won't Start

```bash
# Check container status
cd /opt/misp && sudo docker compose ps

# View logs
cd /opt/misp && sudo docker compose logs --tail=100

# Restart services
cd /opt/misp && sudo docker compose restart

# Full restart
cd /opt/misp
sudo docker compose down
sudo docker compose up -d
```

### Backup Failed

```bash
# Check logs
tail -100 /var/log/misp-install/backup-cron.log

# Check disk space
df -h ~

# Test backup manually
python3 misp-backup-cron.py --dry-run

# Check database access
cd /opt/misp && sudo docker compose exec db mysqladmin ping
```

### Update Failed

```bash
# View update log
ls -lt /var/log/misp-install/misp-update-*.log | head -1 | xargs cat

# Check for backups
python3 misp-restore.py --list

# Restore from backup if needed
python3 misp-restore.py --restore latest
```

### Can't Access MISP

```bash
# Check containers
cd /opt/misp && sudo docker compose ps

# Check web interface
curl -k -I https://misp-dev.lan

# Check /etc/hosts
grep misp-dev.lan /etc/hosts

# Add if missing
echo "192.168.20.193 misp-dev.lan" | sudo tee -a /etc/hosts
```

---

## 📞 Support & Resources

### Documentation

- **Installation:** See `POST-INSTALL-CHECKLIST.md` in `/opt/misp/`
- **Updates:** See `MISP-UPDATE.md` for detailed update guide
- **Backups:** See `MISP-BACKUP-SETUP.md` for backup configuration

### Log Files

All operations log to `/var/log/misp-install/`:
- `misp-install-YYYYMMDD_HHMMSS.log`
- `misp-update-YYYYMMDD_HHMMSS.log`
- `misp-backup-YYYYMMDD_HHMMSS.log`
- `misp-restore-YYYYMMDD_HHMMSS.log`
- `backup-cron.log`

### Important Files

- **Credentials:** `/opt/misp/PASSWORDS.txt`
- **Configuration:** `/opt/misp/.env`
- **SSL Certs:** `/opt/misp/ssl/`
- **Backups:** `/opt/misp-backups/`

### MISP Resources

- **Official Docs:** https://www.misp-project.org/documentation/
- **MISP Book:** https://www.circl.lu/doc/misp/
- **GitHub:** https://github.com/MISP/MISP
- **Community:** https://www.misp-project.org/community/

---

## 🔐 Security Notes

### Credential Management

- ✅ **Passwords stored in:** `/opt/misp/PASSWORDS.txt` (mode 600)
- ✅ **Change default passwords** after first login
- ✅ **Enable 2FA** for admin account
- ✅ **Back up credentials** securely off-site

### Backup Security

- ⚠️ **Backups contain sensitive data** (passwords, keys, database)
- ⚠️ **Backups are not encrypted** by default
- ✅ **Restrict access:** `chmod 700 /opt/misp-backups/`
- ✅ **Consider encryption** for compliance requirements
- ✅ **Store off-site copy** on secure backup server

### Network Security

- ✅ **Configure firewall:** `sudo ufw allow 443/tcp`
- ✅ **Use SSL/TLS** (auto-configured)
- ✅ **Update /etc/hosts** on client workstations
- ✅ **Consider VPN** for remote access

---

## 📝 Version History

### v1.0 (2025-10-11)
- Initial release
- Complete MISP installation automation
- Update management with backup
- Automated backup with rotation
- Restore functionality
- Uninstall script
- Full documentation

---

## 📄 License

These scripts are provided by YourCompanyName for internal use. Modify as needed for your environment.

---

## ✅ Quick Checklist

### After Installation
- [ ] Login to MISP web interface
- [ ] Change admin password
- [ ] Set up automated backups (cron)
- [ ] Configure firewall
- [ ] Update workstation /etc/hosts
- [ ] Test backup and restore
- [ ] Document credentials securely

### Monthly Maintenance
- [ ] Check for updates
- [ ] Apply updates during maintenance window
- [ ] Verify backups are running
- [ ] Review logs for errors
- [ ] Test backup restoration
- [ ] Check disk space

### Before Major Changes
- [ ] Create manual backup: `python3 misp-backup-cron.py --full`
- [ ] Verify backup: `python3 misp-restore.py --show latest`
- [ ] Document changes
- [ ] Notify team

---

**Script Collection Version:** 1.0  
**Last Updated:** 2025-10-11  
**Maintained By:** tKQB Enterprises  

For questions or issues, check logs in `/var/log/misp-install/` or consult the detailed documentation files.