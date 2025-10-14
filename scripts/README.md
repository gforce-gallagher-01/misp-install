# MISP Scripts Directory

This directory contains all operational scripts for managing your MISP installation.

## 📚 Complete Script Documentation

For comprehensive documentation of all MISP scripts, see **[../SCRIPTS.md](../SCRIPTS.md)** in the project root.

The main SCRIPTS.md file provides:
- Complete script inventory (all 16+ scripts)
- Detailed usage instructions
- Configuration examples
- Best practices and workflows
- Troubleshooting guides

## Quick Reference

### Installation & Setup
- **[../misp-install.py](../misp-install.py)** - Main installation script
- **[../misp_install_gui.py](../misp_install_gui.py)** - GUI installer

### Backup & Restore
- **[backup-misp.py](backup-misp.py)** - Manual backups
- **[misp-backup-cron.py](misp-backup-cron.py)** - Automated cron backups
- **[misp-restore.py](misp-restore.py)** - Restore from backup

### Maintenance
- **[misp-update.py](misp-update.py)** - Update MISP components
- **[uninstall-misp.py](uninstall-misp.py)** - Complete MISP removal
- **[verify-installation.py](verify-installation.py)** - Post-install verification

### Configuration
- **[configure-misp-nerc-cip.py](configure-misp-nerc-cip.py)** - NERC CIP compliance mode
- **[misp-setup-complete.py](misp-setup-complete.py)** - Complete setup orchestrator

### Feed Management
- **[add-nerc-cip-news-feeds-api.py](add-nerc-cip-news-feeds-api.py)** - Add news feeds (API)
- **[check-misp-feeds-api.py](check-misp-feeds-api.py)** - Check feed status (API)
- **[enable-misp-feeds.py](enable-misp-feeds.py)** - Enable feeds
- **[populate-misp-news.py](populate-misp-news.py)** - Populate security news

### Discovery
- **[list-misp-communities.py](list-misp-communities.py)** - Discover MISP communities

## Common Commands

```bash
# Fresh installation
python3 ../misp-install.py

# Installation with config file
python3 ../misp-install.py --config ../config/production.json --non-interactive

# Manual backup
python3 backup-misp.py

# Restore from latest backup
python3 misp-restore.py --restore latest

# Update MISP
python3 misp-update.py --all

# NERC CIP configuration
python3 configure-misp-nerc-cip.py

# Complete post-install setup
python3 misp-setup-complete.py --api-key YOUR_KEY

# Check feed status
python3 check-misp-feeds-api.py --api-key YOUR_KEY

# Enable NERC CIP feeds
python3 enable-misp-feeds.py --nerc-cip
```

## Getting Help

For detailed usage of any script:
```bash
python3 <script-name> --help
```

For comprehensive documentation, workflows, and best practices, see **[../SCRIPTS.md](../SCRIPTS.md)**.

---

**Last Updated:** 2025-10-14
**Maintainer:** tKQB Enterprises
