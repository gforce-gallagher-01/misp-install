# MISP Installation Guide

**Version**: 5.4
**Last Updated**: 2025-10-14
**Status**: STABLE - PRODUCTION READY

## Overview

This document describes the installation process for MISP using the automated installer suite. The installation follows a phase-based approach with resume capability and comprehensive logging.

## Installation Phases

The main installation script (`misp-install.py`) executes 12 phases:

### Phase 1: Dependencies

**Duration**: 5-10 minutes
**Purpose**: Install system packages and Docker

**Operations**:
1. Update apt package lists
2. Install Docker CE and Docker Compose
3. Install Python dependencies (pyaml, psutil)
4. Create `misp-owner` system user
5. Create `/opt/misp/logs/` directory (CRITICAL - must exist before logging starts)

**Commands Executed**:
```bash
sudo apt update
sudo apt install -y docker-ce docker-compose python3-pip
sudo useradd --system --no-create-home --shell /usr/sbin/nologin misp-owner
sudo mkdir -p /opt/misp/logs
sudo chmod 777 /opt/misp/logs
```

**Logging**: `/opt/misp/logs/misp-install-{timestamp}.log`

### Phase 2: Docker Group

**Duration**: < 1 minute
**Purpose**: Add `misp-owner` user to docker group

**Operations**:
1. Check if `misp-owner` is in docker group
2. Add user to group if needed
3. For interactive mode: Prompt user to logout/login
4. For resume mode: Skip if already past phase 2

**Commands Executed**:
```bash
sudo usermod -aG docker misp-owner
```

**Important**: User may need to logout/login for group membership to take effect

### Phase 3: Clone Repository

**Duration**: 1-2 minutes
**Purpose**: Clone MISP-docker repository from GitHub

**Operations**:
1. Remove existing MISP-docker directory (if present)
2. Clone https://github.com/MISP/misp-docker.git
3. Checkout stable branch

**Commands Executed**:
```bash
git clone https://github.com/MISP/misp-docker.git /opt/misp/MISP-docker
cd /opt/misp/MISP-docker && git checkout 2.4
```

### Phase 4: Cleanup

**Duration**: 1-2 minutes
**Purpose**: Remove previous MISP installation (preserves logs)

**Operations**:
1. Stop all MISP Docker containers
2. Remove all MISP Docker containers
3. Remove all MISP Docker volumes
4. Remove `/opt/misp/` contents (EXCEPT `/opt/misp/logs/`)
5. Clean `/etc/hosts` entries

**Commands Executed**:
```bash
cd /opt/misp && sudo docker compose down
sudo docker rm -f misp-core misp-modules db redis
sudo docker volume rm misp_mysql_data misp_misp_data
sudo rm -rf /opt/misp/* (preserving logs/)
```

**⚠️ CRITICAL**: `/opt/misp/logs/` is PRESERVED because logger is actively writing to it

### Phase 5: Directory Setup

**Duration**: < 1 minute
**Purpose**: Create /opt/misp with proper ownership

**Operations**:
1. Create `/opt/misp` directory
2. Set ownership to `misp-owner:misp-owner`
3. Set permissions to 755

**Commands Executed**:
```bash
sudo mkdir -p /opt/misp
sudo chown -R misp-owner:misp-owner /opt/misp
sudo chmod 755 /opt/misp
```

#### Phase 5.5: Log Directory Configuration (CRITICAL)

**Duration**: < 1 minute
**Purpose**: Configure logs directory BEFORE Docker starts

**Why This Phase Exists**:
- Docker mounts `./logs/` directory
- If Docker creates it first, it's owned by `www-data:www-data` with 770 permissions
- Scripts running as regular user can't write to 770 directory
- Solution: Create directory BEFORE Docker starts with 777 permissions

**Operations**:
1. Create `/opt/misp/logs` directory as `misp-owner`
2. Set permissions to 777 (allows Docker + scripts to write)
3. Set ownership to `misp-owner:misp-owner`

**Commands Executed**:
```bash
sudo -u misp-owner mkdir -p /opt/misp/logs
sudo chmod 777 /opt/misp/logs
sudo chown misp-owner:misp-owner /opt/misp/logs
```

### Phase 6: Configuration

**Duration**: 1-2 minutes
**Purpose**: Generate .env file with performance tuning

**Operations**:
1. Auto-detect system resources (RAM, CPU)
2. Calculate PHP memory limit and worker count
3. Generate `.env` file with all configuration
4. Set permissions to 600
5. Set ownership to `misp-owner:misp-owner`

**Performance Tuning Logic**:
```python
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

**Generated .env Contains**:
- Build-time variables (CORE_TAG, MODULES_TAG, PHP_VER)
- Runtime variables (BASE_URL, passwords, database config)
- Performance tuning (PHP_MEMORY_LIMIT, WORKERS)
- Security settings (HSTS, X-Frame-Options)

**File Operation Pattern** (v5.4):
```python
# Write to temp location as current user
temp_file = f"/tmp/.env.{os.getpid()}"
with open(temp_file, 'w') as f:
    f.write(env_content)

# Move to final location as misp-owner
subprocess.run(['sudo', '-u', 'misp-owner', 'cp', temp_file, '/opt/misp/.env'])
subprocess.run(['sudo', 'chmod', '600', '/opt/misp/.env'])
subprocess.run(['sudo', 'chown', 'misp-owner:misp-owner', '/opt/misp/.env'])

# Cleanup
os.unlink(temp_file)
```

### Phase 7: SSL Certificate

**Duration**: < 1 minute
**Purpose**: Create self-signed SSL certificate for domain

**Operations**:
1. Create `/opt/misp/ssl/` directory (via sudo)
2. Generate self-signed certificate and private key
3. Set certificate file permissions to 644
4. Set private key permissions to 600
5. Set ownership to `misp-owner:misp-owner`

**Commands Executed**:
```bash
sudo -u misp-owner mkdir -p /opt/misp/ssl
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=${domain}" \
    -keyout /tmp/key.pem -out /tmp/cert.pem
sudo mv /tmp/cert.pem /opt/misp/ssl/cert.pem
sudo mv /tmp/key.pem /opt/misp/ssl/key.pem
sudo chmod 644 /opt/misp/ssl/cert.pem
sudo chmod 600 /opt/misp/ssl/key.pem
sudo chown misp-owner:misp-owner /opt/misp/ssl/*
```

**Certificate Details**:
- Type: Self-signed
- Algorithm: RSA 4096-bit
- Validity: 365 days
- Subject: /CN=${domain}

**Future Enhancement**: Public signed certificate support (Let's Encrypt, commercial CA)

### Phase 8: DNS Configuration

**Duration**: < 1 minute
**Purpose**: Update /etc/hosts for domain resolution

**Operations**:
1. Read current `/etc/hosts`
2. Remove existing MISP entries
3. Add new entry: `{server_ip}  {domain}`
4. Write updated `/etc/hosts`

**Commands Executed**:
```bash
sudo bash -c "echo '{server_ip}  {domain}' >> /etc/hosts"
```

**Example Entry**:
```
192.168.20.193  misp-dev.lan
```

### Phase 9: Password Reference

**Duration**: < 1 minute
**Purpose**: Create PASSWORDS.txt file with all credentials

**Operations**:
1. Generate PASSWORDS.txt content
2. Write to temp file as current user
3. Move to `/opt/misp/PASSWORDS.txt` via sudo
4. Set permissions to 600
5. Set ownership to `misp-owner:misp-owner`

**File Contents**:
```
=== MISP Installation Credentials ===

Admin Credentials:
  Email:    admin@company.com
  Password: [admin_password]

Database Credentials:
  Username: misp
  Password: [mysql_password]
  Database: misp

GPG Configuration:
  Passphrase: [gpg_passphrase]

Encryption:
  Key: [encryption_key]

MISP URL:
  https://misp-dev.lan
```

### Phase 10: Docker Build

**Duration**: 15-30 minutes (first run)
**Purpose**: Pull Docker images and start containers

**Operations**:
1. Copy docker-compose template
2. Start Docker containers (`docker compose up -d`)
3. Pull images: misp-core, misp-modules, mysql, redis
4. Create volumes for persistent data
5. Start all services

**Commands Executed**:
```bash
cd /opt/misp
sudo docker compose up -d
```

**Containers Started**:
- `misp-core` - MISP web application (Apache + PHP)
- `misp-modules` - MISP enrichment modules
- `db` - MySQL database
- `redis` - Redis cache

**Note**: This phase takes longest on first run (image downloads)

### Phase 11: Initialization

**Duration**: 5-10 minutes
**Purpose**: Wait for MISP to initialize

**Operations**:
1. Wait for database to be ready
2. Wait for MISP web interface to respond
3. Poll `https://{domain}/users/login` for 200 OK
4. Timeout: 15 minutes

**Health Check**:
```python
def wait_for_misp_ready(timeout=900):
    """Poll MISP URL until ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"https://{domain}/users/login", verify=False)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(10)
    return False
```

**Indicators of Readiness**:
- MISP web interface responds
- Login page is accessible
- Database migrations complete

#### Phase 11.5: API Key Generation (v5.5)

**Duration**: < 1 minute
**Purpose**: Generate MISP API key for automation scripts

**Operations**:
1. Use MISP CLI to generate API key for admin user
2. Store API key in `/opt/misp/PASSWORDS.txt`
3. Store API key in `/opt/misp/.env` as `MISP_API_KEY`
4. Set proper permissions (600)

**Commands Executed**:
```bash
# Generate API key using MISP cake command
sudo docker compose exec -T misp-core \
    /var/www/MISP/app/Console/cake user change_authkey admin@company.com

# Append to PASSWORDS.txt
echo "MISP API Key: ${api_key}" >> /tmp/passwords.txt
sudo mv /tmp/passwords.txt /opt/misp/PASSWORDS.txt

# Add to .env
echo "MISP_API_KEY=${api_key}" >> /tmp/.env
sudo bash -c "cat /tmp/.env >> /opt/misp/.env"
```

**API Key Usage**:
- Automation scripts (populate-misp-news, add-feeds, etc.)
- External integrations (Splunk, Security Onion)
- REST API access

### Phase 12: Post-Install

**Duration**: < 1 minute
**Purpose**: Generate checklist and verify permissions

**Operations**:
1. Verify all containers running
2. Check file ownership and permissions
3. Generate post-installation checklist
4. Display access credentials
5. Show next steps

**Verification Checks**:
```bash
# Container status
cd /opt/misp && sudo docker compose ps

# File ownership
ls -la /opt/misp | grep misp-owner

# Log permissions
ls -la /opt/misp/logs | grep "drwxrwxrwx"
```

**Completion Message**:
```
========================================
  MISP Installation Complete!
========================================

Access Information:
  URL: https://misp-dev.lan
  Username: admin@company.com
  Password: [shown in PASSWORDS.txt]

Credentials: /opt/misp/PASSWORDS.txt
Logs: /opt/misp/logs/

Next Steps:
  1. Change default admin password
  2. Configure SMTP settings
  3. Enable threat intelligence feeds
  4. Set up authentication (LDAP/Azure AD)
```

## Resume Capability

### How Resume Works

**State File**: `~/.misp-install/state.json`

**State Saved After Each Phase**:
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

**Resume Command**:
```bash
python3 misp-install.py --resume
```

**Resume Logic**:
1. Load state file
2. Display last completed phase
3. Ask user to confirm resume
4. Skip completed phases (1 through N)
5. Continue from phase N+1

### When to Use Resume

**Resume After**:
- Network interruption during Docker pull (Phase 10)
- Script crash or error
- User interruption (Ctrl+C)
- System reboot during installation

**Don't Resume After**:
- Successful completion (re-run from start instead)
- Configuration changes (use fresh install)
- Major errors requiring cleanup

### Resume Example

```bash
# Installation interrupted at Phase 7
$ python3 misp-install.py --resume

Loading installation state...
Last completed phase: 6 (Configuration Complete)

Resume installation from Phase 7? [y/N]: y

Resuming from Phase 7: SSL Certificate...
✓ Phase 7: SSL Certificate completed
✓ Phase 8: DNS Configuration completed
...
```

## Installation Modes

### Interactive Mode (Default)

**Usage**:
```bash
python3 misp-install.py
```

**Features**:
- Prompts for all configuration (IP, domain, passwords)
- Password strength validation
- Real-time feedback
- User confirmations

**Best For**:
- First-time users
- Manual installations
- Custom configurations

### Non-Interactive Mode (CI/CD)

**Usage**:
```bash
python3 misp-install.py --config config/misp-config.json --non-interactive
```

**Features**:
- No user prompts
- All config from file
- Exits on error
- Suitable for automation

**Best For**:
- CI/CD pipelines
- Terraform/Ansible
- Batch deployments
- Testing

**Config File Format**:
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

### Debug Mode

**Usage**:
```bash
python3 misp-install.py --config config/test-debug.json --non-interactive
```

**Features**:
- Verbose logging
- Additional debug output
- Stack traces on errors
- Performance timing

**Best For**:
- Troubleshooting
- Development
- Bug reports

## Installation Time Estimates

| Phase | Duration | Notes |
|-------|----------|-------|
| Phase 1: Dependencies | 5-10 min | Depends on internet speed |
| Phase 2: Docker Group | < 1 min | Quick user group update |
| Phase 3: Clone Repository | 1-2 min | GitHub clone speed |
| Phase 4: Cleanup | 1-2 min | If previous install exists |
| Phase 5: Directory Setup | < 1 min | Local filesystem ops |
| Phase 5.5: Log Config | < 1 min | Critical permissions fix |
| Phase 6: Configuration | 1-2 min | Auto-detection + .env |
| Phase 7: SSL Certificate | < 1 min | OpenSSL generation |
| Phase 8: DNS Config | < 1 min | /etc/hosts update |
| Phase 9: Password File | < 1 min | PASSWORDS.txt creation |
| Phase 10: Docker Build | **15-30 min** | **Longest phase** (first run) |
| Phase 11: Initialization | 5-10 min | MISP startup + DB migrations |
| Phase 11.5: API Key | < 1 min | Generate API key |
| Phase 12: Post-Install | < 1 min | Verification + checklist |
| **Total** | **30-50 min** | First installation |

**Subsequent Installations**: 10-15 minutes (Docker images cached)

## System Requirements

### Minimum Requirements

- **OS**: Ubuntu 22.04 LTS or 24.04 LTS
- **RAM**: 8 GB
- **CPU**: 2 cores
- **Disk**: 50 GB free space
- **Network**: Internet connection for Docker pull

### Recommended Requirements

- **OS**: Ubuntu 24.04 LTS
- **RAM**: 16 GB
- **CPU**: 4 cores
- **Disk**: 100 GB free space (SSD)
- **Network**: 100 Mbps internet

### User Requirements

- **Sudo Access**: Required
- **Passwordless Sudo**: Recommended (see SETUP.md)
- **SSH Access**: If remote installation

## Pre-Installation Checklist

Before running the installer:

- [ ] Ubuntu 22.04+ installed
- [ ] User has sudo access
- [ ] Passwordless sudo configured (optional but recommended)
- [ ] Internet connection available
- [ ] Firewall allows HTTPS (443)
- [ ] Domain name or IP address decided
- [ ] Passwords prepared (12+ chars, mixed case, numbers, special)

## Common Installation Issues

### Issue 1: Installation Hangs at Phase 10

**Symptom**: Phase 10 (Docker Build) takes very long (30+ minutes)

**Cause**: Normal - Docker pulling large images

**Solution**: Wait patiently, monitor with:
```bash
# In separate terminal
cd /opt/misp && sudo docker compose ps
cd /opt/misp && sudo docker compose logs -f
```

### Issue 2: "Docker not in group" Error

**Symptom**: Permission denied when accessing Docker

**Cause**: User needs to logout/login for docker group to take effect

**Solution**:
```bash
# Option 1: Logout and login
exit

# Option 2: New group session
newgrp docker
```

### Issue 3: Container Shows "Unhealthy"

**Symptom**: `sudo docker compose ps` shows misp-core as "unhealthy"

**Cause**: Known upstream issue with MISP-docker healthcheck

**Impact**: None - MISP still works correctly

**Solution**: Ignore health check status, verify via web interface

### Issue 4: Logs Directory Missing Error

**Symptom**: `FileNotFoundError: /opt/misp/logs/`

**Cause**: Critical bug - logs directory should be created in Phase 1

**Solution**: Check Phase 1 execution, verify lines 1586-1601 in misp-install.py

### Issue 5: Permission Denied During Installation

**Symptom**: `[Errno 13] Permission denied: '/opt/misp/...'`

**Cause**: File operations not using sudo pattern (v5.4 architecture issue)

**Solution**: Verify temp file + sudo pattern is used for all `/opt/misp` writes

## Post-Installation Tasks

### Immediate (Required)

1. **Change Default Password**:
   - Login to https://your-domain
   - Go to Administration > Users
   - Edit admin user
   - Change password

2. **Enable SSL Certificate Validation**:
   - Replace self-signed cert with trusted cert (Let's Encrypt/commercial)
   - Or import self-signed cert to client trust store

### Within 24 Hours (Recommended)

3. **Configure SMTP Settings**:
   - Go to Administration > Server Settings
   - Set email server details
   - Test email functionality

4. **Enable Threat Intelligence Feeds**:
   - Run: `python3 scripts/configure-misp-nerc-cip.py` (if applicable)
   - Or manually enable feeds via web UI

5. **Set Up Authentication**:
   - Configure LDAP/AD integration
   - Or configure Azure AD SAML
   - Or keep local authentication

### Within 1 Week (Important)

6. **Configure Backup Automation**:
   - Add cron job for `misp-backup-cron.py`
   - Test backup/restore cycle

7. **Set Up Monitoring**:
   - Forward logs to SIEM (Splunk, ELK)
   - Configure uptime monitoring
   - Set up alerting

8. **Security Hardening**:
   - Review firewall rules
   - Configure fail2ban
   - Enable audit logging

## Related Documentation

- **ARCHITECTURE.md** - System architecture and design principles
- **v5.4_DEDICATED_USER.md** - v5.4 testing history and findings
- **README.md** - Main project documentation
- **SETUP.md** - Sudoers configuration guide
- **KNOWN-ISSUES.md** - Known issues and workarounds

---

**Last Updated**: 2025-10-14
**Maintainer**: tKQB Enterprises
