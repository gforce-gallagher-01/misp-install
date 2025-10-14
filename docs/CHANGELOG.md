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

## [5.5.0] - 2025-10-14

### Added
- 🎯 **MISP Complete Setup Script** - Post-installation orchestration with NERC CIP mode
  - Orchestrates all post-installation configuration (settings, feeds, news, taxonomies)
  - `--nerc-cip-ready` flag for utilities/energy sector compliance
  - `--dry-run` mode for preview
  - Skip flags for individual steps (--skip-feeds, --skip-news, --skip-settings)
  - Auto-detect API key from multiple sources
  - Comprehensive error handling and statistics tracking
  - Created `scripts/misp-setup-complete.py` (800+ lines)
- 🔑 **API Key Generation** - Automatic API key during installation (Phase 11.5)
  - Uses MISP CLI (`cake user change_authkey`) to generate API key
  - Stores API key in `/opt/misp/PASSWORDS.txt` and `/opt/misp/.env`
  - Proper permissions (600) and graceful error handling
  - Added to main installation flow between Phase 11 and Phase 12
- 🔧 **API Helper Module** - Centralized API access for all scripts
  - Created `misp_api.py` with functions: `get_api_key()`, `get_misp_url()`, `get_misp_client()`, `test_connection()`
  - Auto-detects API key from .env, PASSWORDS.txt, or environment variable
  - SSL verification disabled for self-signed certs
  - Test mode available (`python3 misp_api.py`)
- 📡 **API-Based Scripts** - New scripts using MISP REST API instead of database
  - `scripts/add-nerc-cip-news-feeds-api.py` (v2.0) - Add feeds via `/feeds/add` API ✅ Working
  - `scripts/check-misp-feeds-api.py` (v2.0) - Check feeds via `/feeds/index` API ✅ Working
  - `scripts/populate-misp-news-complete.py` (v2.0) - Populate news via `/news/add` API ⚠️ Limited (API returns HTTP 500)
  - Better error handling, version independence, and RBAC enforcement
  - Database versions remain available as fallback
- 🖥️ **GUI Installer** - Textual framework TUI/web interface (v1.0)
  - Multi-step wizard with 5 screens (Welcome, Network, Security, Environment, Review)
  - Real-time password strength validation (12+ chars, mixed case, numbers, special)
  - Auto-generate secure passwords (cryptographically secure)
  - Clipboard paste support (Ctrl+V) with pyperclip + xclip
  - Runs in terminal OR web browser (same code, dual mode)
  - Configuration file generation (JSON format)
  - Full keyboard navigation and Dark/Light theme toggle
  - Created `misp_install_gui.py`, `install-gui.sh`, `setup.py`
- 📖 **Comprehensive Documentation** - 52KB API usage guide
  - Created `docs/API_USAGE.md` (1000+ lines)
  - Documented API key retrieval methods (auto, web, CLI)
  - Added helper module usage examples
  - Troubleshooting for common API issues
  - All common API endpoints with examples
  - Error handling patterns and best practices

### Changed
- **Installation Flow** - Added Phase 11.5 for automatic API key generation
- **Script Architecture** - Migrated from direct database access to MISP REST API where possible (85% complete)
  - 2 scripts fully converted to API (add-nerc-cip-news-feeds, check-misp-feeds)
  - 1 script partially working (populate-misp-news - upstream API issue)
  - 1 script keeps database approach (configure-misp-nerc-cip - uses proper cake commands)
- **GUI Installer** - Configuration files now compatible with `misp-install.py --config`

### Fixed
- **API Integration** - Worked around broken `/news/add` endpoint by keeping database version as fallback
- **Feed Management** - Duplicate detection via API prevents adding same feed twice
- **GUI Clipboard** - Fixed clipboard paste support with xclip dependency

### Security
- **API Keys** - Secure storage in PASSWORDS.txt and .env with 600 permissions
- **No Database Passwords in Scripts** - API-based scripts don't need MySQL credentials
- **RBAC Enforcement** - API calls respect MISP role-based access control

### Known Issues
- **MISP /news/add API** - Returns HTTP 500 (upstream issue) - using database version as workaround
- **GUI Installer** - Requires pipx on Ubuntu 24.04+ or manual pip installation

## [5.4.0] - 2025-10-13

### Added
- 🔒 **ACL-based Permission System** - Implemented Linux Access Control Lists for multi-user log directory access
  - Replaces world-writable (777) permissions with granular user-specific ACLs
  - Supports Docker containers (www-data), misp-owner, and installation user writing to logs simultaneously
  - Critical ACL mask fix ensures rwx permissions are effective
  - Config files (.env, PASSWORDS.txt, docker-compose files) now have read ACLs for backup scripts
  - Backup/restore scripts can now run as regular user without sudo for file reads
- 📦 **ACL Package** - Added `acl` package to system dependencies (Phase 1)
- 📝 **Enhanced Documentation** - Complete ACL implementation documented in:
  - SECURITY_ARCHITECTURE.md - ACL security model and architecture
  - TROUBLESHOOTING.md - ACL permission troubleshooting guide
  - MAINTENANCE.md - ACL management and verification procedures
  - ACL-FIX-SUMMARY.md - Complete technical implementation details

### Changed
- **Phase 10.6**: Completely rewritten to use ACL-based permissions instead of chmod 777
  - Multi-step ACL configuration for existing files
  - Default ACL configuration for newly created files
  - ACL mask correction to enable write permissions
  - Config file ACLs for backup script access
- **Backup Scripts**: Now work as regular user without root privileges (thanks to config file ACLs)
- **Permission Model**: Updated file ownership matrix to reflect ACL permissions

### Fixed
- **Log Permission Conflicts**: Solved Docker's forceful ownership reset of `/opt/misp/logs` to www-data:www-data
  - Previous chmod 777 approach was reset by Docker on container restart
  - ACL solution persists across Docker restarts while respecting upstream behavior
- **Backup Permission Errors**: Fixed `PermissionError` when backup scripts tried to read config files owned by misp-owner
- **Effective Permissions**: Fixed ACL mask issue where effective permissions were r-x instead of rwx

### Security
- **More Secure Than 777**: ACLs grant access only to specific users, not all system users
- **Principle of Least Privilege**: Each user/process has only the permissions it needs
- **Respects Docker Ownership**: No modifications to upstream MISP Docker images required
- **Audit Trail**: ACLs provide clear visibility into which users have access to which files

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

### Patch Version 5.4.X)
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

# 3. Download v5.4
wget https://github.com/gforce-gallagher-01/misp-install/releases/download/v5.4.0/misp-install.py

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

### v5.4.0
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