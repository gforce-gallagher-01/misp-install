# MISP Installation Checklist

Use this checklist to ensure a successful MISP installation.

## 📋 Pre-Installation

### System Preparation
- [ ] Ubuntu 20.04 LTS or newer installed
- [ ] Server has static IP address configured
- [ ] DNS/hosts file configured (if needed)
- [ ] At least 4GB RAM available
- [ ] At least 20GB free disk space
- [ ] 2+ CPU cores
- [ ] Ports 80 and 443 available
- [ ] Internet connection active
- [ ] sudo/root access available

### Software Prerequisites
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] pip installed: `pip3 --version`
- [ ] User account created (not root)
- [ ] System packages updated: `sudo apt update && sudo apt upgrade`

### Planning
- [ ] Decided on FQDN (e.g., misp.gridsec.com)
- [ ] Static IP address documented
- [ ] Admin email address decided
- [ ] Organization name decided
- [ ] Environment chosen (dev/staging/prod)
- [ ] Strong passwords prepared (or will generate during install)
- [ ] Backup strategy planned

## 📥 Download & Setup

### Files
- [ ] Downloaded `misp-install.py`
- [ ] Downloaded `README.md`
- [ ] Downloaded `QUICKSTART.md`
- [ ] Downloaded `misp-config.yaml` (if using config file)
- [ ] Downloaded `requirements.txt` (optional)
- [ ] Files placed in home directory: `cd ~`
- [ ] Script made executable: `chmod +x misp-install.py`

### Optional: PyYAML
- [ ] Installed PyYAML: `pip3 install pyyaml` (for YAML config support)
- [ ] Or decided to use JSON config instead
- [ ] Or decided to use interactive mode

## ⚙️ Configuration

### If Using Config File
- [ ] Copied config template: `cp misp-config.yaml my-config.yaml`
- [ ] Updated `server_ip` with your server IP
- [ ] Updated `domain` with your FQDN
- [ ] Updated `admin_email` with your email
- [ ] Updated `admin_org` with your organization
- [ ] Generated and set strong `admin_password`
- [ ] Generated and set strong `mysql_password`
- [ ] Generated and set strong `gpg_passphrase`
- [ ] Generated encryption key: `python3 -c "import secrets; print(secrets.token_hex(16))"`
- [ ] Updated `encryption_key` in config
- [ ] Reviewed performance settings
- [ ] Saved config file securely

### If Using Interactive Mode
- [ ] Prepared all required information
- [ ] Passwords ready (or will generate during installation)

## 🚀 Installation

### Pre-Flight Checks
- [ ] Logged in as regular user (not root)
- [ ] Verified system meets requirements
- [ ] Checked ports 80/443 are not in use: `sudo lsof -i :443`
- [ ] Verified disk space: `df -h`
- [ ] Verified RAM: `free -h`

### Running Installation
- [ ] Started installation: `python3 misp-install.py` or with config
- [ ] Answered all prompts (if interactive)
- [ ] Waited for completion (10-15 minutes)
- [ ] Verified no errors in output
- [ ] Noted log file location

### Docker Group
- [ ] Added to docker group by script
- [ ] Logged out and back in (if prompted)
- [ ] Or ran: `newgrp docker`
- [ ] Verified: `groups | grep docker`

## ✅ Post-Installation

### Immediate Verification
- [ ] Installation completed successfully
- [ ] All 12 phases completed
- [ ] Final summary displayed
- [ ] No error messages

### Credential Backup
- [ ] Viewed passwords: `cat /opt/misp/PASSWORDS.txt`
- [ ] **CRITICAL:** Copied PASSWORDS.txt to secure location
- [ ] **CRITICAL:** Backed up /opt/misp/.env file
- [ ] Stored credentials in password manager
- [ ] Documented backup location

### Container Verification
- [ ] Checked container status: `cd /opt/misp && sudo docker compose ps`
- [ ] All 5 containers running (db, redis, misp-core, misp-modules, mail)
- [ ] No containers in "Exit" or "Unhealthy" state
- [ ] Checked logs: `sudo docker compose logs | tail -50`

### Network Configuration
- [ ] Verified /etc/hosts on server: `grep misp /etc/hosts`
- [ ] Added entry to workstation hosts file
- [ ] Can ping MISP domain: `ping misp.yourdomain.com`
- [ ] Can resolve domain: `nslookup misp.yourdomain.com`

### Web Interface Access
- [ ] Opened browser to MISP URL
- [ ] Accepted self-signed certificate warning
- [ ] Login page displayed
- [ ] Logged in with admin credentials from PASSWORDS.txt
- [ ] Dashboard loads successfully
- [ ] No errors in web interface

### Documentation Review
- [ ] Read POST-INSTALL-CHECKLIST.md
- [ ] Read README.md
- [ ] Bookmarked MISP documentation
- [ ] Saved all relevant links

## 🔒 Security Hardening

### Immediate Security Tasks
- [ ] Changed admin password (even though it's already strong)
- [ ] Enabled 2FA for admin account
- [ ] Configured firewall: `sudo ufw allow 443/tcp && sudo ufw enable`
- [ ] Reviewed user permissions
- [ ] Disabled unnecessary services
- [ ] Configured fail2ban (optional)

### MISP Configuration
- [ ] Reviewed Administration → Server Settings
- [ ] Configured email settings (SMTP)
- [ ] Tested email notifications
- [ ] Reviewed security settings
- [ ] Updated base URL if needed
- [ ] Configured GPG key
- [ ] Set up API access

## 📦 Backup Configuration

### Backup Setup
- [ ] Documented backup locations:
  - [ ] PASSWORDS.txt
  - [ ] .env file
  - [ ] SSL certificates
  - [ ] Database
- [ ] Created backup script
- [ ] Tested backup process
- [ ] Tested restore process
- [ ] Scheduled automated backups (cron/systemd)
- [ ] Configured off-site backup storage
- [ ] Documented backup procedures

### Backup Script Example
```bash
#!/bin/bash
# Add to cron: 0 2 * * * /home/user/backup-misp.sh

BACKUP_DIR=/opt/misp-backups/$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Backup config files
cp /opt/misp/.env $BACKUP_DIR/
cp /opt/misp/PASSWORDS.txt $BACKUP_DIR/
cp -r /opt/misp/ssl $BACKUP_DIR/

# Backup database
cd /opt/misp
sudo docker compose exec -T db mysqldump -umisp -p"$(grep MYSQL_PASSWORD .env | cut -d= -f2)" misp > $BACKUP_DIR/misp_database.sql

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR/
rm -rf $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

## 🔍 Monitoring Setup

### Monitoring Configuration
- [ ] Configured log monitoring
- [ ] Set up disk space alerts
- [ ] Configured container health checks
- [ ] Set up uptime monitoring
- [ ] Configured performance monitoring
- [ ] Created monitoring dashboard (optional)
- [ ] Documented monitoring procedures

### Health Check Commands
```bash
# Container health
cd /opt/misp && sudo docker compose ps

# Disk usage
df -h /opt/misp
docker system df

# Memory usage
docker stats --no-stream

# Recent logs
sudo docker compose logs --tail=100

# Worker status
sudo docker compose exec misp-core ps aux | grep worker
```

## 👥 Team Setup

### User Management
- [ ] Created user accounts for team members
- [ ] Assigned appropriate roles
- [ ] Configured permissions
- [ ] Set up email notifications per user
- [ ] Documented user management procedures

### Training
- [ ] Scheduled training session
- [ ] Created user guide
- [ ] Documented common workflows
- [ ] Set up support channel
- [ ] Created FAQ document

## 📊 Integration

### MISP Configuration
- [ ] Configured MISP feeds
- [ ] Set up sync servers (if needed)
- [ ] Configured API access
- [ ] Tested MISP modules
- [ ] Configured enrichment services
- [ ] Set up correlation rules
- [ ] Configured taxonomies
- [ ] Imported initial data

### External Integrations
- [ ] SIEM integration configured (if needed)
- [ ] SOAR integration configured (if needed)
- [ ] EDR integration configured (if needed)
- [ ] Other security tools integrated
- [ ] Tested all integrations

## 🧪 Testing

### Functionality Tests
- [ ] Created test event
- [ ] Added attributes to event
- [ ] Tested correlation
- [ ] Tested searching
- [ ] Tested exports
- [ ] Tested API endpoints
- [ ] Tested email notifications
- [ ] Tested user permissions
- [ ] Tested backups and restore

### Performance Tests
- [ ] Tested with sample data
- [ ] Monitored resource usage
- [ ] Verified acceptable response times
- [ ] Tested concurrent users
- [ ] Checked worker performance

## 📝 Documentation

### Internal Documentation
- [ ] Documented installation details
- [ ] Created runbook for common tasks
- [ ] Documented backup procedures
- [ ] Documented disaster recovery plan
- [ ] Created troubleshooting guide
- [ ] Documented custom configurations
- [ ] Created architecture diagram
- [ ] Documented network requirements

### Handoff
- [ ] Presented to team
- [ ] Conducted knowledge transfer
- [ ] Provided access to documentation
- [ ] Identified support contacts
- [ ] Created escalation procedure

## ✨ Final Steps

### Sign-Off
- [ ] All items in checklist completed
- [ ] System tested and verified
- [ ] Team trained
- [ ] Documentation complete
- [ ] Backups tested
- [ ] Monitoring active
- [ ] Go-live approval obtained

### Launch
- [ ] Announced MISP availability to organization
- [ ] Provided access instructions
- [ ] Started using MISP for threat intelligence
- [ ] Monitoring dashboards reviewed
- [ ] Support channels active

## 📞 Support Resources

- **MISP Documentation:** https://www.misp-project.org/documentation/
- **MISP Book:** https://www.circl.lu/doc/misp/
- **Community Forum:** https://www.misp-project.org/community/
- **GitHub Issues:** https://github.com/MISP/MISP/issues
- **Installation Logs:** `/var/log/misp-install/`
- **Password File:** `/opt/misp/PASSWORDS.txt`

---

**Installation Date:** _______________

**Installed By:** _______________

**Sign-Off:** _______________

**Notes:**
```
[Space for installation notes]
```