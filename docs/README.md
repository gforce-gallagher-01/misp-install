# MISP Installation & Configuration Documentation

Complete documentation for enterprise MISP deployment using YourCompanyName installation scripts.

## 📚 Documentation Index

### Getting Started
- **[Main Installation Script](../misp-install.py)** - Primary MISP installation script
- **[Quick Start Guide](../README.md)** - Basic installation instructions

### Configuration Guides
1. **[Configuration Guide](CONFIGURATION-GUIDE.md)** ⭐ START HERE
   - Overview of all configuration options
   - Quick reference for common scenarios
   - Links to detailed guides

2. **[Enterprise .env Template](../config/.env.enterprise-template)**
   - Complete `.env` configuration file template
   - All 180+ environment variables documented
   - Inline examples and explanations

3. **[Configuration Best Practices](CONFIGURATION-BEST-PRACTICES.md)**
   - Security hardening (SSL/TLS, HSTS, strong passwords)
   - Performance tuning (MySQL, PHP, workers)
   - SMTP configuration for multiple providers
   - Network and proxy setup
   - Monitoring and logging best practices
   - Backup and disaster recovery

### Authentication & Identity
4. **[Azure Entra ID Setup](AZURE-ENTRA-ID-SETUP.md)**
   - Step-by-step Azure AD (Entra ID) configuration
   - Azure Portal setup walkthrough
   - Group-based role mapping
   - SSO troubleshooting
   - MFA and Conditional Access integration

### Advanced Features
5. **[Advanced Features Guide](ADVANCED-FEATURES.md)**
   - **MISP Workflows**: Automation and data pipelines
   - **Threat Intelligence Feeds**: OSINT feed configuration
   - **MISP Modules**: Enrichment, import, export modules
   - **Sync Servers**: Multi-instance threat sharing
   - **MISP-Guard**: Traffic filtering and monitoring
   - **Custom Integrations**: Custom modules and scripts

6. **[Third-Party Integrations](THIRD-PARTY-INTEGRATIONS.md)** ⭐ NEW
   - **SIEM**: Splunk, Microsoft Sentinel, QRadar, ELK
   - **EDR**: CrowdStrike, Microsoft Defender, Carbon Black
   - **SOAR**: TheHive + Cortex, Cortex XSOAR, Shuffle
   - **Sandboxes**: Cuckoo, Joe Sandbox, VMRay, ANY.RUN
   - **Threat Intel**: VirusTotal, Shodan, Recorded Future
   - **Recommended Stack**: Tier 1, 2, 3 integrations

### Management Scripts
6. **[Ready-to-Run Configuration](../scripts/configure-misp-ready.py)** ⭐ NEW
   - Post-installation automation
   - Updates taxonomies, galaxies, warninglists
   - Enables recommended feeds
   - Configures best practices
   - Creates initial backup
   - **Guide**: [Ready-to-Run Setup](READY-TO-RUN-SETUP.md)

7. **[Backup Script](../scripts/backup-misp.py)**
   - Complete MISP backup (config, database, attachments)
   - Automated scheduling with retention
   - Backup verification

8. **[Restore Script](../scripts/restore-misp.py)**
   - Disaster recovery from backups
   - Selective restore options

9. **[Uninstall Script](../scripts/uninstall-misp.py)**
   - Complete MISP removal
   - Preserves backups
   - Safety confirmations

## 🚀 Quick Start

### 1. Install MISP

```bash
cd ~/misp-repo/misp-install
python3 misp-install.py --config config/misp-config.json
```

### 2. Configure for Production

```bash
# Copy enterprise template
cp config/.env.enterprise-template /opt/misp/.env

# Edit configuration
nano /opt/misp/.env

# Update these critical settings:
# - BASE_URL (your domain)
# - All passwords (search for "CHANGE_THIS")
# - SMTP settings (for email notifications)
# - Authentication method (Azure AD, LDAP, or local)

# Restart MISP
cd /opt/misp
docker compose down
docker compose up -d
```

### 3. Run Ready-to-Run Configuration

```bash
# Automate post-installation setup
cd ~/misp-repo/misp-install/scripts
python3 configure-misp-ready.py
```

This automatically:
- Updates taxonomies (TLP, PAP, etc.)
- Updates galaxies (MITRE ATT&CK)
- Updates warninglists
- Enables background jobs
- Configures enrichment modules
- Creates initial backup

### 4. Access MISP

```bash
# Web Interface
https://your-misp-domain

# Default credentials (change immediately):
# Email: admin@admin.test
# Password: admin
```

### 5. Enable Advanced Features

See [Advanced Features Guide](ADVANCED-FEATURES.md) for:
- Enabling threat intelligence feeds
- Configuring MISP modules for enrichment
- Setting up workflows for automation
- Connecting to sync servers for threat sharing

## 📖 Documentation by Use Case

### Security Team
- [Configuration Best Practices](CONFIGURATION-BEST-PRACTICES.md) - Security hardening
- [Azure Entra ID Setup](AZURE-ENTRA-ID-SETUP.md) - SSO and MFA
- [Advanced Features](ADVANCED-FEATURES.md) - Feeds and automation

### DevOps / System Administrator
- [Configuration Guide](CONFIGURATION-GUIDE.md) - Performance tuning
- [Enterprise Template](../config/.env.enterprise-template) - Full configuration options
- [Backup/Restore Scripts](../scripts/) - Disaster recovery

### SOC Analyst
- [Advanced Features](ADVANCED-FEATURES.md) - Workflows, feeds, modules
- [Configuration Guide](CONFIGURATION-GUIDE.md) - Basic setup

### Management / Compliance
- [Configuration Best Practices](CONFIGURATION-BEST-PRACTICES.md) - Security checklist
- [Azure Entra ID Setup](AZURE-ENTRA-ID-SETUP.md) - Enterprise authentication

## 🔧 Common Configuration Scenarios

### Scenario 1: Small Organization (< 10 users)
- **Resources**: 4GB RAM, 2 CPU cores
- **Authentication**: Local (username/password)
- **Email**: Gmail with app password
- **Features**: Basic threat intelligence
- **Guide**: [Configuration Guide § Small Organization](CONFIGURATION-GUIDE.md#scenario-1-small-organization--10-users)

### Scenario 2: Medium Organization (10-50 users)
- **Resources**: 8GB RAM, 4 CPU cores
- **Authentication**: Azure Entra ID or LDAP
- **Email**: Office 365
- **Features**: Feeds, modules, basic workflows
- **Guide**: [Configuration Guide § Medium Organization](CONFIGURATION-GUIDE.md#scenario-2-medium-organization-10-50-users)

### Scenario 3: Large Enterprise (50+ users)
- **Resources**: 16GB+ RAM, 8+ CPU cores
- **Authentication**: Azure Entra ID with group-based roles
- **Email**: Office 365 or Amazon SES
- **Features**: Full workflows, all feeds, sync servers, custom modules
- **Guide**: [Configuration Guide § Large Enterprise](CONFIGURATION-GUIDE.md#scenario-3-large-enterprise-50-users)

## 📋 Configuration Checklist

Before production deployment:

### Security
- [ ] Strong passwords for all services
- [ ] Valid SSL certificate installed
- [ ] HSTS enabled (`HSTS_MAX_AGE=31536000`)
- [ ] Debug mode disabled (`DEBUG=0`)
- [ ] Credentials hidden from logs (`DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true`)
- [ ] Authentication method configured (Azure AD/LDAP recommended)

### Functionality
- [ ] SMTP configured and tested
- [ ] User access controls configured in MISP
- [ ] Threat intelligence feeds enabled
- [ ] MISP modules configured (if needed)

### Operations
- [ ] Automated backups configured
- [ ] Restore procedure tested
- [ ] Monitoring and alerting configured
- [ ] Firewall rules configured
- [ ] Documentation updated with organization-specific details

## 🔗 External Resources

### Official MISP Documentation
- MISP Project: https://www.misp-project.org/
- MISP Book: https://www.circl.lu/doc/misp/
- MISP Training: https://github.com/MISP/misp-training
- MISP GitHub: https://github.com/MISP/MISP

### MISP Docker
- GitHub Repository: https://github.com/MISP/misp-docker
- Docker Hub: https://hub.docker.com/r/misp/misp-docker

### MISP Modules & Extensions
- MISP Modules: https://github.com/MISP/misp-modules
- Workflow Blueprints: https://github.com/MISP/misp-workflow-blueprints
- Module Documentation: https://misp.github.io/misp-modules/

### Community
- Gitter Chat: https://gitter.im/MISP/MISP
- Twitter: @MISPProject
- YouTube: https://www.youtube.com/c/MISPProject

## 🛠️ Management Commands

### Backup MISP
```bash
cd ~/misp-repo/misp-install/scripts
python3 backup-misp.py
```

### Restore MISP
```bash
cd ~/misp-repo/misp-install/scripts
python3 misp-restore.py --restore latest
```

### View MISP Logs
```bash
cd /opt/misp
docker compose logs -f misp-core
```

### Restart MISP
```bash
cd /opt/misp
docker compose down
docker compose up -d
```

### Update MISP
```bash
cd /opt/misp
docker compose pull
docker compose down
docker compose up -d
```

## 🐛 Troubleshooting

### Common Issues

1. **Containers not starting**
   - Check Docker resources: `docker stats`
   - Verify disk space: `df -h`
   - Review logs: `docker compose logs`

2. **Cannot access web interface**
   - Verify containers are running: `docker compose ps`
   - Check firewall rules: `sudo ufw status`
   - Test locally: `curl -k https://localhost/users/heartbeat`

3. **Email not sending**
   - Verify SMTP settings in `/opt/misp/.env`
   - Check mail container logs: `docker compose logs mail`
   - Test SMTP from container: `docker compose exec misp-core telnet smtp.example.com 587`

4. **Authentication not working**
   - Verify auth variables in `/opt/misp/.env`
   - Check container logs: `docker compose logs misp-core | grep -i auth`
   - Restart containers: `docker compose down && docker compose up -d`

For more troubleshooting:
- [Configuration Guide § Troubleshooting](CONFIGURATION-GUIDE.md#troubleshooting)
- [Best Practices § Monitoring](CONFIGURATION-BEST-PRACTICES.md#monitoring--logging)

## 📞 Support

For issues or questions:

1. **Documentation**: Review guides in this directory
2. **Logs**: Check MISP logs for error messages
3. **Community**: MISP Gitter chat and GitHub issues
4. **Professional**: Contact YourCompanyName for enterprise support

---

## Document Version

- **Last Updated**: 2025-10-12
- **MISP Version**: 2.5.22
- **Docker Compose Version**: 3.x
- **Author**: YourCompanyName

---

**tKQB Enterprises MISP Deployment**
