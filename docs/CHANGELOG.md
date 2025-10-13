# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Coming soon...

### Changed
- TBD

### Fixed
- TBD

## [5.0.0] - 2025-10-11

### Added
- 🎉 **Complete Python rewrite** - Enterprise-grade installation system
- ✅ **Pre-flight system checks** - Validates disk, RAM, CPU, ports, and Docker before installation
- 📝 **Comprehensive logging** - All operations logged to `/opt/misp/logs/` with timestamps
- 💾 **Automatic backups** - Creates backup before cleanup with retention policy
- 🔐 **Password validation** - Enforces strong passwords (12+ chars, complexity requirements)
- 📋 **Config file support** - YAML and JSON configuration files for automation
- 🔄 **Resume capability** - Can resume from any phase if installation interrupted
- 🔁 **Error recovery** - Automatic retry with smart recovery for failed phases
- 🌍 **Multi-environment support** - Dev, Staging, and Production configurations
- ⚡ **Performance auto-tuning** - Automatically configures based on system resources
- 🔍 **Port conflict detection** - Checks for port conflicts before installation
- 📊 **Docker group activation** - Automatic docker group configuration
- 📚 **Comprehensive documentation** - 10,000+ words of professional documentation
- 🛠️ **Operational scripts** - backup-misp.py, uninstall-misp.py, health-check scripts
- 📝 **Post-install checklist** - Auto-generated checklist for post-installation tasks
- 🧪 **Test suite generation** - Creates standalone test script for health checks

### Changed
- **BREAKING:** Script now requires Python 3.8+ (was Bash-only before)
- Installation process now uses 12 phases instead of 8
- Configuration moved to dataclasses for better type safety
- Docker group activation now happens without logout (using sg)
- Improved error messages with color coding
- Better container health monitoring with retries

### Fixed
- Docker group activation no longer requires logout/login
- Better handling of interrupted installations
- Fixed SSL certificate generation on various Ubuntu versions
- Improved git clone error handling
- Better detection of missing dependencies

### Security
- Password complexity requirements enforced
- Secure file permissions (600) for sensitive files
- No passwords in logs or error messages
- Validation of all user inputs
- State files protected with proper permissions

## [4.0.0] - 2024-XX-XX

### Added
- Initial Bash script version
- Basic installation workflow
- SSL certificate generation
- Docker container management
- Simple backup functionality

### Known Issues
- Required manual logout for docker group
- Limited error recovery
- No resume capability
- Basic logging only

## [3.0.0] - 2023-XX-XX

### Added
- Docker Compose support
- Environment variable configuration
- Basic health checks

## [2.0.0] - 2022-XX-XX

### Added
- Multi-container deployment
- Redis support
- MISP modules integration

## [1.0.0] - 2021-XX-XX

### Added
- Initial release
- Basic MISP installation via Docker
- MySQL database setup
- Nginx configuration

---

## Version Strategy

### Major Version (X.0.0)
- Breaking changes
- Major architectural changes
- Incompatible API changes
- Migration guide required

### Minor Version (5.X.0)
- New features
- Non-breaking enhancements
- New optional parameters
- Backward compatible

### Patch Version (5.0.X)
- Bug fixes
- Documentation updates
- Security patches
- Performance improvements

---

## Migration Guides

### Migrating from 4.x to 5.0

**Breaking Changes:**
1. **Python Required:** Now requires Python 3.8+ instead of pure Bash
2. **Config Format:** New config file format (see `config/` directory)
3. **Directory Structure:** Some files reorganized

**Migration Steps:**

```bash
# 1. Backup your current installation
bash backup-misp.py  # If you have v4.x script

# 2. Install Python 3.8+ if needed
sudo apt install python3.8 python3-pip

# 3. Download v5.0
wget https://github.com/gforce-gallagher-01/misp-install/releases/download/v5.0.0/misp-install.py

# 4. Optional: Install PyYAML for YAML config support
pip3 install pyyaml

# 5. Run new installer
python3 misp-install.py

# Or migrate your old config to new format
# See docs/UPGRADE.md for details
```

**What Stays the Same:**
- MISP container structure
- Database location
- SSL certificates
- Backup files
- `/etc/hosts` configuration

**What Changes:**
- Installation script (Python instead of Bash)
- Config file format (YAML/JSON with more options)
- State management (JSON state files)
- Logging (more comprehensive)

---

## Deprecation Notices

### Deprecated in 5.0.0
- None yet

### Removed in 5.0.0
- Pure Bash installation method (replaced with Python)
- Manual docker group activation (now automatic)
- Simple logging (replaced with comprehensive logging)

---

## Known Issues

### Current (5.0.0)
- PyYAML is optional but recommended for YAML config files
- First-time Docker downloads can be slow (expected behavior)
- Self-signed certificate warnings in browsers (expected behavior)

### Planned Fixes
- Add email notification support (planned for 5.1.0)
- Add Slack/Teams webhook support (planned for 5.1.0)
- Add GUI installer option (planned for 6.0.0)

---

## Contributors

### v5.0.0
- Your Name (@yourusername) - Complete Python rewrite
- Contributors welcome!

### Previous Versions
- Original contributors from v1.0-4.0

---

## Links

- **Repository:** https://github.com/gforce-gallagher-01/misp-install
- **Issues:** https://github.com/gforce-gallagher-01/misp-install/issues
- **Discussions:** https://github.com/gforce-gallagher-01/misp-install/discussions
- **MISP Project:** https://www.misp-project.org/

---

## Changelog Format

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Deprecated
- Features that will be removed in future

### Removed
- Features removed in this version

### Fixed
- Bug fixes

### Security
- Security patches and improvements
```