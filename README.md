# MISP Complete Installation Tool v5.5
**tKQB Enterprises**

A professional-grade Python installation script for MISP (Malware Information Sharing Platform) with enterprise features.

## 🚀 Features

- ✅ **Automatic Hostname Detection** - Detects and uses system FQDN automatically
- ✅ **Pre-flight System Checks** - Validates disk, RAM, CPU, ports, Docker
- ✅ **Full Logging** - Detailed logs saved to `/opt/misp/logs/`
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
- ✅ **API Key Generation** - Automatic API key for automation

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
# ONE-COMMAND INSTALL (handles everything automatically!)
cd ~/misp-install/misp-install
./install-gui.sh

# That's it! The script will:
# - Install all dependencies (xclip, pipx, pyperclip)
# - Configure PATH automatically
# - Install the GUI installer
# - Verify everything works
# - Optionally launch the GUI installer
```

**Features:**
- ✨ Multi-step wizard with validation
- 🔒 Real-time password strength checking
- 🎲 Auto-generate secure passwords
- 💾 Save configurations for reuse
- 🌐 Run in terminal OR web browser
- ⌨️ Full keyboard navigation
- 📋 **Ctrl+V clipboard paste support**

**Manual installation** (if you prefer):
```bash
sudo apt install xclip pipx
pipx install .
pipx ensurepath
misp-install-gui
```

See `docs/GUI_INSTALLER.md` for complete documentation.

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

5. **Post-Install Configuration (Recommended):**
   ```bash
   # Run general configuration (updates taxonomies, galaxies, feeds)
   python3 scripts/configure-misp-ready.py

   # For NERC CIP compliance (energy utilities)
   python3 scripts/configure-misp-nerc-cip.py

   # Check which feeds are enabled
   python3 scripts/check-misp-feeds.py

   # Enable all NERC CIP recommended feeds automatically
   python3 scripts/enable-misp-feeds.py --nerc-cip
   ```

### Feed Management (NEW - October 2025)

**Check Feed Status:**
```bash
# View feed summary (NERC CIP focus)
python3 scripts/check-misp-feeds.py

# Show all 88 feeds
python3 scripts/check-misp-feeds.py --show-all
```

**Enable Feeds:**
```bash
# Enable all NERC CIP recommended feeds (14 feeds)
python3 scripts/enable-misp-feeds.py --nerc-cip

# Enable specific feed by ID
python3 scripts/enable-misp-feeds.py --id 60

# Enable feeds by name (partial match)
python3 scripts/enable-misp-feeds.py --name "URLhaus"

# Preview changes without making them
python3 scripts/enable-misp-feeds.py --nerc-cip --dry-run
```

**What it does:**
- ✅ Checks which of 88 feeds are enabled/disabled
- ✅ Highlights NERC CIP recommended feeds
- ✅ Enables feeds individually or in bulk
- ✅ Automatically fetches feed data after enabling
- ✅ Provides detailed feed information (ID, name, URL, format)

### Community Discovery (NEW - October 2025)

**IMPORTANT**: Communities involve **two-way data sharing** (unlike feeds which are one-way). For NERC CIP organizations, joining communities requires management approval and CIP-011 BCSI protection controls.

**Discover Available Communities:**
```bash
# List energy sector communities (NERC CIP relevant)
python3 scripts/list-misp-communities.py --sector energy

# Show only NERC CIP relevant communities
python3 scripts/list-misp-communities.py --nerc-cip

# Show all communities across all sectors
python3 scripts/list-misp-communities.py --all

# List financial sector communities
python3 scripts/list-misp-communities.py --sector financial

# List ICS/SCADA focused communities
python3 scripts/list-misp-communities.py --sector ics
```

**What it does:**
- ✅ Lists 8 MISP communities (3 NERC CIP relevant, 5 general)
- ✅ Shows cost information (FREE to $50,000/year)
- ✅ Displays requirements and contact information
- ✅ Highlights NERC CIP relevant communities for energy utilities
- ✅ Provides warnings about two-way data sharing
- ✅ **Informational only** - does not configure any connections

**Featured Communities:**

| Community | Sector | Cost | NERC CIP Relevant |
|-----------|--------|------|-------------------|
| **E-ISAC** | Energy | $5,000 - $25,000/year | ✅ **PRIMARY** |
| **CISA ICS-CERT** | Multi-Sector | FREE | ✅ Essential |
| **OT-ISAC** | ICS/SCADA | Paid | ✅ Recommended |
| CIRCL MISP | Multi-Sector | FREE | - |
| FIRST | Multi-Sector | $3,500 - $50,000/year | - |
| FS-ISAC | Financial | Paid | - |
| MS-ISAC | Government | FREE | - |
| Danish MISP | Multi-Sector | FREE | - |

**Key Differences: Feeds vs Communities:**

| Feature | Feeds (Already Enabled) | Communities (This Script) |
|---------|-------------------------|---------------------------|
| Data Flow | One-way (consume only) | Two-way (share and receive) |
| BCSI Risk | None (no data leaves MISP) | Yes (requires CIP-011 controls) |
| Approval | None required | Management + Legal required |
| Cost | FREE | FREE to $50K/year |
| Setup | Automatic (via scripts) | Manual (via community contact) |

**For NERC CIP Compliance:**
- ⚠️ **E-ISAC membership HIGHLY RECOMMENDED** - $5K-$25K/year, PRIMARY for electric utilities
- ⚠️ **CISA ICS-CERT is FREE and essential** - US government ICS threat intelligence
- ⚠️ Before joining ANY community, ensure:
  - Management approval obtained
  - CIP-011 BCSI protection controls in place
  - Sharing groups configured to "Your organization only" by default
  - Legal review of community agreements (NDAs, TLP)

**Next Steps After Running Script:**
1. Review community requirements and costs
2. Obtain management approval (required for NERC CIP organizations)
3. Contact community using provided contact information
4. Complete membership application and agreements
5. Configure MISP server connection (after approval)

See `docs/NERC_CIP_CONFIGURATION.md` for E-ISAC integration guidance.

### NERC CIP Configuration (Energy Utilities)

**NEW**: For electric utilities operating solar, wind, and battery storage systems under NERC CIP compliance:

```bash
# Configure MISP for NERC CIP compliance
python3 scripts/configure-misp-nerc-cip.py
```

**What it does:**
- ✅ Configures 11 NERC CIP-specific settings
- ✅ Recommends 15 ICS/SCADA threat intelligence feeds
- ✅ Maps MISP features to 8 NERC CIP standards (CIP-003 through CIP-015)
- ✅ Provides audit evidence guidance for compliance

**Documentation:** See `docs/NERC_CIP_CONFIGURATION.md` for complete 50+ page guide including:
- NERC CIP 2025 requirements
- ICS/SCADA threat intelligence sources (CISA ICS-CERT, E-ISAC)
- Solar/wind/battery-specific considerations
- Vendor-specific intelligence (Siemens, Schneider, ABB, GE)
- Audit checklist with evidence mapping
- Cost estimates (Free to $475K/year)

**Relevant for:**
- Electric utilities (Low & Medium Impact BES Cyber Systems)
- Energy sector security teams
- ICS/SCADA cybersecurity professionals

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