# MISP Systemd Service - Boot Management

**Version:** 5.6+
**Feature:** Automatic MISP startup on boot with systemd
**Platform:** Ubuntu 24.04 LTS (Noble Numbat)
**Last Updated:** 2025-10-16

## Overview

The MISP systemd service provides automatic startup, graceful shutdown, and centralized management of the entire MISP Docker stack. This ensures MISP is always available after system reboots.

## Features

- ✅ **Automatic Boot Startup** - MISP starts automatically when system boots
- ✅ **Graceful Shutdown** - Proper container shutdown with 60s timeout
- ✅ **Health Monitoring** - Verifies 5 containers are running after startup
- ✅ **Restart on Failure** - Automatic restart if service fails
- ✅ **User Isolation** - Runs as `misp-owner` user (not root)
- ✅ **Resource Limits** - Prevents resource exhaustion
- ✅ **Security Hardening** - Ubuntu 24.04 systemd security features

## Installation

### Quick Install

Run the setup script:

```bash
sudo bash scripts/setup-misp-systemd.sh
```

### Manual Install

1. **Copy service file:**
   ```bash
   sudo cp scripts/misp.service /etc/systemd/system/
   ```

2. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   ```

3. **Enable and start:**
   ```bash
   sudo systemctl enable misp.service
   sudo systemctl start misp.service
   ```

4. **Verify:**
   ```bash
   sudo systemctl status misp
   ```

## Usage

### Basic Commands

```bash
# Start MISP
sudo systemctl start misp

# Stop MISP
sudo systemctl stop misp

# Restart MISP
sudo systemctl restart misp

# Check status
sudo systemctl status misp

# View logs
sudo journalctl -u misp -f

# View recent logs
sudo journalctl -u misp -n 100 --no-pager
```

### Advanced Commands

```bash
# Update and recreate containers (pull latest images)
sudo systemctl reload misp

# Enable auto-start on boot
sudo systemctl enable misp

# Disable auto-start on boot
sudo systemctl disable misp

# Check if enabled
systemctl is-enabled misp

# View service configuration
systemctl cat misp.service

# Security analysis
sudo systemd-analyze security misp.service
```

### Container Status

```bash
# Check Docker containers
cd /opt/misp && sudo docker compose ps

# Check container health
cd /opt/misp && sudo docker compose ps --format "{{.Service}}: {{.Status}}"

# View container logs
cd /opt/misp && sudo docker compose logs -f misp-core
```

## Service Details

### Service Configuration

- **User:** `misp-owner`
- **Group:** `docker`
- **Working Directory:** `/opt/misp`
- **Type:** `oneshot` with `RemainAfterExit=yes`
- **Restart Policy:** On failure (3 attempts within 600s)
- **Start Timeout:** 600s (10 minutes)
- **Stop Timeout:** 90s

### Managed Containers

The service manages 5 Docker containers:

1. **misp-db** - MariaDB database
2. **misp-redis** - Redis cache
3. **misp-core** - MISP web application (ports 80, 443)
4. **misp-modules** - MISP modules for enrichment
5. **misp-mail** - Postfix mail server

### Health Check

After startup, the service verifies that at least 3 containers are running. If less than 3 are detected, the service fails and triggers a restart.

## Security

### Port 443 Binding

- **Docker daemon** (running as root) binds privileged ports like 443
- **misp-owner** user runs `docker compose` commands
- **User must be in docker group** to communicate with Docker daemon
- No additional permissions needed for non-root user

### Security Hardening

The service includes Ubuntu 24.04 security features:

- **File System Protection:** Limited write access to `/opt/misp`
- **Private Temp:** Isolated temporary filesystem
- **No New Privileges:** Prevents privilege escalation
- **Resource Limits:** Prevents resource exhaustion
- **UMask:** 0027 for proper file permissions

**Note:** Many strict security hardening options are disabled because Docker Compose needs to create namespaces, configure networks, and manage containers. Security is primarily enforced at the Docker daemon level.

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u misp.service -n 50 --no-pager
```

**Common issues:**
1. Docker not running: `sudo systemctl status docker`
2. User not in docker group: `groups misp-owner | grep docker`
3. /opt/misp missing: `ls -la /opt/misp`

### Containers Not Starting

**Check Docker:**
```bash
cd /opt/misp && sudo docker compose ps
cd /opt/misp && sudo docker compose logs --tail=50
```

**Restart containers manually:**
```bash
cd /opt/misp && sudo docker compose up -d
```

### Permission Denied Errors

**Verify ownership:**
```bash
ls -la /opt/misp | head -10
```

**Fix ownership:**
```bash
sudo chown -R misp-owner:misp-owner /opt/misp
```

### Port 443 Already in Use

**Check what's using port 443:**
```bash
sudo netstat -tlnp | grep :443
```

**Stop conflicting service:**
```bash
# Example: Apache
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### Service Fails on Boot

**Check service status:**
```bash
sudo systemctl status misp
```

**Check dependencies:**
```bash
systemctl list-dependencies misp.service
```

**View startup time:**
```bash
systemd-analyze blame | grep misp
```

## Uninstallation

### Remove Systemd Service

```bash
# Stop service
sudo systemctl stop misp

# Disable service
sudo systemctl disable misp

# Remove service file
sudo rm /etc/systemd/system/misp.service

# Reload systemd
sudo systemctl daemon-reload
```

### Automated Uninstall

```bash
sudo bash scripts/setup-misp-systemd.sh --uninstall
```

## Testing

### Test Service Functionality

```bash
# 1. Stop MISP
sudo systemctl stop misp
sleep 5

# 2. Verify containers stopped
cd /opt/misp && sudo docker compose ps

# 3. Start MISP
sudo systemctl start misp
sleep 40

# 4. Verify containers running
cd /opt/misp && sudo docker compose ps

# 5. Check service status
sudo systemctl status misp
```

### Test Boot Startup

**Simulate reboot:**
```bash
sudo systemctl reboot
```

**After reboot, verify:**
```bash
# Check service started
sudo systemctl status misp

# Check containers
cd /opt/misp && sudo docker compose ps

# Check uptime
uptime
```

## Integration with MISP Install

The systemd service is compatible with all MISP install scripts:

- ✅ Works with `misp-install.py`
- ✅ Works with `misp-install-gui`
- ✅ Compatible with automated backups
- ✅ Compatible with update scripts
- ✅ Compatible with uninstall scripts

**Note:** The systemd service should be installed **after** MISP installation is complete.

## Files

### Service Files

- `scripts/misp.service` - Systemd service unit file
- `scripts/setup-misp-systemd.sh` - Installation script
- `/etc/systemd/system/misp.service` - Installed service file

### Dependencies

- Docker CE 20.10+
- Docker Compose v2.0+
- systemd 255+ (Ubuntu 24.04)
- MISP installation at `/opt/misp`
- User `misp-owner` exists and is in `docker` group

## Related Documentation

- [INSTALLATION.md](INSTALLATION.md) - MISP installation guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [SCRIPTS.md](SCRIPTS.md) - Script inventory
- [README.md](../README.md) - Main documentation

## Support

### View System Information

```bash
# OS version
cat /etc/os-release | grep -E "PRETTY_NAME|VERSION_ID"

# Systemd version
systemctl --version | head -1

# Docker version
docker --version
docker compose version

# Service status
systemctl status misp --no-pager
```

### Useful Commands for Support

```bash
# Export service definition
systemctl cat misp.service > misp-service-config.txt

# Export logs
sudo journalctl -u misp -n 200 --no-pager > misp-service-logs.txt

# Export container status
cd /opt/misp && sudo docker compose ps > misp-containers.txt
```

## Example Output

### Successful Startup

```
● misp.service - MISP (Malware Information Sharing Platform) Docker Stack
     Loaded: loaded (/etc/systemd/system/misp.service; enabled; preset: enabled)
     Active: active (exited) since Thu 2025-10-16 14:47:23 UTC; 40s ago
       Docs: https://www.misp-project.org/
             https://github.com/MISP/misp-docker
    Process: 23392 ExecStart=/usr/bin/docker compose up -d --wait --wait-timeout 300 (code=exited, status=0/SUCCESS)
    Process: 28371 ExecStartPost=... (code=exited, status=0/SUCCESS)
   Main PID: 23392 (code=exited, status=0/SUCCESS)

Oct 16 14:47:23 misp-test misp[28371]: SUCCESS: 5 containers running
Oct 16 14:47:23 misp-test systemd[1]: Finished misp.service
```

### Healthy Containers

```
SERVICE        STATUS                        PORTS
db             Up About a minute (healthy)   3306/tcp
mail           Up About a minute             25/tcp
misp-core      Up About a minute (healthy)   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
misp-modules   Up About a minute (healthy)
redis          Up About a minute (healthy)   6379/tcp
```

## Changelog

### v5.6 (2025-10-16)
- Initial systemd service implementation
- Boot startup support for Ubuntu 24.04
- Security hardening with systemd features
- Health check verification
- Automated installation script

---

**Last Updated:** 2025-10-16
**Maintainer:** tKQB Enterprises
**Version:** 5.6+
