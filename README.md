# MISP Complete Installation Tool v5.4
**tKQB Enterprises**

A professional-grade Python installation script for MISP (Malware Information Sharing Platform) with enterprise features.

## 🚀 Features

- ✅ **Pre-flight System Checks** - Validates disk, RAM, CPU, ports, Docker
- ✅ **Full Logging** - Detailed logs saved to `/var/log/misp-install/`
- ✅ **Automatic Backups** - Backs up existing installation before cleanup
- ✅ **Config File Support** - YAML/JSON configuration files
- ✅ **Docker Group Activation** - Automatic docker group configuration
- ✅ **Resume Capability** - Resume from any phase if interrupted
- ✅ **Error Recovery** - Retry failed phases with smart recovery
- ✅ **Password Validation** - Strong password enforcement
- ✅ **Post-Install Checklist** - Complete setup guide
- ✅ **Port Conflict Detection** - Prevents installation conflicts
- ✅ **Multi-Environment** - Dev/Staging/Production profiles
- ✅ **Performance Tuning** - Auto-configures based on system resources

## 📋 Requirements

### System Requirements
- **OS:** Ubuntu 20.04 LTS or newer
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk:** 20GB free space minimum
- **CPU:** 2 cores minimum
- **Ports:** 80, 443 available
- **Python:** 3.8 or higher

### Software Requirements
- Python 3.8+
- sudo access (required for creating `/opt/misp` directory tree and Docker operations)
- Internet connection

### Optional Python Packages
```bash
# For YAML config support
pip3 install pyyaml
```

## 🔐 Security Architecture

**IMPORTANT:** This installation follows security best practices by using a **dedicated system user** (`misp-owner`) rather than your personal user account.

**What this means:**
- ✅ The script automatically creates a dedicated `misp-owner` user
- ✅ All MISP files and operations run under `misp-owner` (not root, not your user)
- ✅ Follows the **Principle of Least Privilege** (NIST SP 800-53 AC-6)
- ✅ Provides clear security boundaries and audit trails
- ✅ Compliant with CIS Benchmarks and OWASP best practices

**How it works:**
1. Run the script as your regular user (NOT as root)
2. Script automatically creates `misp-owner` system user (requires sudo once)
3. Script automatically re-executes itself as `misp-owner`
4. All installation operations run as `misp-owner`

**No manual setup required!** The script handles everything automatically.

For more details, see: `docs/SECURITY_ARCHITECTURE.md`

## 🎯 Quick Start

### Interactive Installation (Recommended)

```bash
# Run as your regular user (NOT as root!)
python3 misp-install.py
```

The script will automatically:
- Create the `misp-owner` system user (if needed)
- Switch execution to `misp-owner` user
- Create all required directories with proper ownership
- Install and configure MISP

### Using Configuration File

```bash
# Create config file (see misp-config.yaml example)
python3 misp-install.py --config misp-config.yaml
```

### Non-Interactive (CI/CD)

```bash
# For automated deployments
python3 misp-install.py --config prod-config.yaml --non-interactive
```

### GUI Installer (NEW in v1.0)

For users who prefer a graphical interface:

```bash
# Terminal mode (TUI)
python3 misp-install-gui.py

# Web browser mode
textual serve misp-install-gui.py
# Then open: http://localhost:8000
```

**Features:**
- ✨ Multi-step wizard with validation
- 🔒 Real-time password strength checking
- 🎲 Auto-generate secure passwords
- 💾 Save configurations for reuse
- 🌐 Run in terminal OR web browser
- ⌨️ Full keyboard navigation

See `docs/GUI_INSTALLER.md` for complete documentation.

**Installation (Ubuntu 24.04+):**
```bash
# Create virtual environment
python3 -m venv ~/misp-gui-env
source ~/misp-gui-env/bin/activate
pip install -r requirements-gui.txt

# Then run GUI installer
python3 misp-install-gui.py
```

## 📝 Usage Examples

### Basic Interactive Installation
```bash
python3 misp-install.py
```
Follow the prompts to configure your installation.

### Resume After Interruption
```bash
python3 misp-install.py --resume
```
Automatically resumes from the last completed phase.

### Using YAML Config
```bash
python3 misp-install.py --config misp-config.yaml
```

### Using JSON Config
```bash
python3 misp-install.py --config misp-config.json
```

### Skip Pre-flight Checks (Not Recommended)
```bash
python3 misp-install.py --skip-checks
```

## 📁 File Structure

```
/opt/
├── misp/                     # MISP installation directory
│   ├── .env                  # Environment configuration
│   ├── PASSWORDS.txt         # Credential reference
│   ├── POST-INSTALL-CHECKLIST.md
│   ├── ssl/                  # SSL certificates
│   └── docker-compose.yml    # Docker configuration
└── misp-backups/             # Automatic backups

/var/log/misp-install/        # Installation logs
```

## 🔐 Security

### Password Requirements
All passwords must meet these criteria:
- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*...)

### Credential Storage
All credentials are stored in:
- `/opt/misp/PASSWORDS.txt` (chmod 600)
- `/opt/misp/.env` (chmod 600)

**⚠️ IMPORTANT:** Backup these files securely!

## 🔧 Installation Phases

The installation consists of 12 phases:

1. **Install Dependencies** - System packages and Docker
2. **Docker Group** - Add user to docker group
3. **Backup** - Backup existing installation
4. **Cleanup** - Remove old containers/volumes
5. **Clone Repository** - Fresh MISP Docker repo
6. **Configuration** - Generate .env and configs
7. **SSL Certificate** - Self-signed certificate
8. **DNS Configuration** - Configure /etc/hosts
9. **Password Reference** - Create PASSWORDS.txt
10. **Docker Build** - Build and start containers
11. **Initialization** - Wait for MISP init
12. **Post-Install** - Checklist and documentation

## 🌍 Multi-Environment Support

### Development
```yaml
environment: development
```
- Lower resource allocation
- Debug mode enabled
- Verbose logging

### Staging
```yaml
environment: staging
```
- Production-like configuration
- Testing features enabled

### Production (Default)
```yaml
environment: production
```
- Optimized performance
- Security hardened
- Production-ready settings

## ⚡ Performance Tuning

The script automatically tunes performance based on system resources:

| RAM Available | PHP Memory Limit | Workers |
|--------------|------------------|---------|
| < 8GB        | 1024M           | 2       |
| 8-16GB       | 2048M           | 4       |
| 16GB+        | 4096M           | 8+      |

Workers are calculated as: `max(2, CPU_CORES)`

## 🔄 Resume Capability

If installation is interrupted, resume with:
```bash
python3 misp-install.py --resume
```

State is saved after each phase in `~/.misp-install-state.json`

## 📊 Logs

All logs are saved to `/var/log/misp-install/misp-install-TIMESTAMP.log`

View logs:
```bash
# Latest log
sudo ls -lt /var/log/misp-install/ | head -n 2

# View specific log
sudo cat /var/log/misp-install/misp-install-20251011_120000.log
```

## 🔙 Backups

Automatic backups are created before cleanup:

```bash
/opt/misp-backups/
└── misp-backup-20251011_120000/
    ├── .env
    ├── PASSWORDS.txt
    ├── ssl/
    └── misp_database.sql
```

## 🐛 Troubleshooting

### Docker Group Issues
```bash
# Verify docker group
groups

# If docker not listed, logout and login
# Or activate manually:
newgrp docker
```

### Port Conflicts
```bash
# Check what's using port 443
sudo lsof -i :443

# Or with ss
ss -tuln | grep 443
```

### Container Issues
```bash
# Check container status
cd /opt/misp
sudo docker compose ps

# View logs
sudo docker compose logs misp-core

# Restart containers
sudo docker compose restart
```

### Database Issues
```bash
# Check database logs
cd /opt/misp
sudo docker compose logs db | grep -i error

# Connect to database
sudo docker compose exec db mysql -umisp -p
```

## 📚 Post-Installation

After installation completes:

1. **View Credentials:**
   ```bash
   sudo cat /opt/misp/PASSWORDS.txt
   ```

2. **Access MISP:**
   - URL: https://misp.lan
   - Login with admin credentials

3. **Configure Workstations:**
   ```bash
   # Linux/Mac
   echo "192.168.20.95 misp.lan" | sudo tee -a /etc/hosts

   # Windows (PowerShell as Admin)
   Add-Content C:\Windows\System32\drivers\etc\hosts "`n192.168.20.95 misp.lan"
   ```

4. **Review Checklist:**
   ```bash
   sudo cat /opt/misp/POST-INSTALL-CHECKLIST.md
   ```

## 🛠️ Useful Commands

```bash
# View passwords
sudo cat /opt/misp/PASSWORDS.txt

# View logs
cd /opt/misp && sudo docker compose logs -f

# Check status
cd /opt/misp && sudo docker compose ps

# Restart MISP
cd /opt/misp && sudo docker compose restart

# Stop MISP
cd /opt/misp && sudo docker compose down

# Start MISP
cd /opt/misp && sudo docker compose up -d

# Backup database
cd /opt/misp
sudo docker compose exec -T db mysqldump -umisp -p"PASSWORD" misp > backup.sql
```

## 🤝 Support

### Resources
- **MISP Documentation:** https://www.misp-project.org/documentation/
- **MISP Book:** https://www.circl.lu/doc/misp/
- **Community:** https://www.misp-project.org/community/
- **GitHub:** https://github.com/MISP/MISP

### Common Issues

**Issue:** "Docker not installed"
```bash
# Run phase 1 manually
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

**Issue:** "Insufficient disk space"
```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -af --volumes
```

**Issue:** "Port already in use"
```bash
# Find and stop conflicting service
sudo lsof -i :443
sudo systemctl stop <service>
```

## 📄 License

This script is provided as-is for MISP deployment purposes.

## ✅ Version History

### v5.4 (Current) - 2025-10-13
- **SECURITY:** Dedicated system user architecture (`misp-owner`)
- Automatic user creation and privilege management
- Follows industry best practices (NIST, CIS, OWASP)
- Principle of least privilege implementation
- Enhanced security boundaries and audit trails
- See [CHANGELOG](docs/testing_and_updates/CHANGELOG.md) for details

### v5.3 - 2025-10-13
- Logger robustness with graceful fallback
- Fixed log directory permission issues
- Enhanced error handling and messaging
- Comprehensive documentation updates

### v5.2
- Centralized JSON logging with CIM fields
- Log rotation and SIEM compatibility

### v5.0
- Enterprise-grade Python implementation
- Pre-flight system checks
- Resume capability
- Multi-environment support
- Performance auto-tuning

### v4.0
- Bash script with basic features
- Interactive installation
- SSL certificate generation

## 🎯 Roadmap

- [x] GUI installer (Terminal + Web browser)
- [ ] Email notifications
- [ ] Slack/Teams integration
- [ ] Splunk Cloud integration
- [ ] Security Onion integration
- [ ] Azure Key Vault integration
- [ ] Automated testing suite
- [ ] HA/cluster deployment
- [ ] Kubernetes support
- [ ] Ansible playbook version

---

**Made with ❤️ for the MISP Community**

For questions or issues, please check the logs in `/var/log/misp-install/`