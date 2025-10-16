# MISP Systemd Service

**Version:** 5.6+ | **Platform:** Ubuntu 24.04 LTS

Automatic MISP startup on boot with graceful shutdown and health monitoring.

## Features

- Automatic boot startup
- Graceful shutdown (60s timeout)
- Health monitoring (5 containers)
- Restart on failure
- User isolation (misp-owner)
- Security hardening

## Quick Start

```bash
# Install
sudo bash scripts/setup-misp-systemd.sh

# Or manually
sudo cp scripts/misp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now misp.service
```

## Usage

```bash
# Service management
sudo systemctl start misp          # Start
sudo systemctl stop misp           # Stop
sudo systemctl restart misp        # Restart
sudo systemctl status misp         # Status
sudo systemctl reload misp         # Update containers

# Logs
sudo journalctl -u misp -f         # Follow logs
sudo journalctl -u misp -n 100     # Last 100 lines

# Container status
cd /opt/misp && sudo docker compose ps
```

## Architecture

- **User:** misp-owner (docker group)
- **Containers:** 5 (db, redis, core, modules, mail)
- **Ports:** 80, 443 (bound by Docker daemon as root)
- **Health Check:** Verifies ≥3 containers after startup
- **Timeouts:** Start 600s, Stop 90s
- **Security:** PrivateTmp, NoNewPrivileges, Resource limits

## Troubleshooting

```bash
# Service won't start
sudo journalctl -u misp -n 50
sudo systemctl status docker
groups misp-owner | grep docker

# Containers not starting
cd /opt/misp && sudo docker compose logs --tail=50

# Permission errors
sudo chown -R misp-owner:misp-owner /opt/misp

# Port 443 in use
sudo netstat -tlnp | grep :443
```

## Uninstall

```bash
sudo bash scripts/setup-misp-systemd.sh --uninstall
```

## Requirements

- Ubuntu 24.04 LTS (systemd 255+)
- Docker CE 20.10+ / Compose v2.0+
- MISP installed at `/opt/misp`
- User `misp-owner` in `docker` group

---

**Version:** 5.6+ | **Maintainer:** tKQB Enterprises
