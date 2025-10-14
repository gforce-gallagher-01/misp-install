# MISP GUI Installer - User Guide

**Version:** 1.0
**Framework:** Python Textual
**tKQB Enterprises Edition**

## Overview

The MISP GUI Installer provides a modern, user-friendly graphical interface for installing MISP (Malware Information Sharing Platform). It features a multi-step wizard that guides you through configuration with real-time validation and helpful prompts.

### Key Features

- ✨ **Multi-step wizard** - Guided installation process
- 🔒 **Password validation** - Real-time strength checking
- 🎲 **Auto-generate passwords** - Create strong passwords automatically
- 💾 **Save configurations** - Export config for CI/CD reuse
- 🌐 **Dual mode** - Run in terminal OR web browser
- ⌨️ **Keyboard navigation** - Full keyboard support
- 🎨 **Dark/Light themes** - Toggle with `d` key
- 📝 **Form validation** - Immediate feedback on errors

## Installation

### Prerequisites

- Python 3.8 or higher
- Ubuntu 22.04 LTS or 24.04 LTS
- sudo privileges
- Internet connection

### Install Dependencies

**Ubuntu 24.04+ (Recommended - uses pipx):**

```bash
# Install with pipx (handles everything automatically)
cd ~/misp-install/misp-install
pipx install .

# Or install from GitHub directly
pipx install git+https://github.com/gforce-gallagher-01/misp-install.git
```

**Alternative Methods:**

```bash
# Option 2: Virtual environment
python3 -m venv ~/misp-gui-env
source ~/misp-gui-env/bin/activate
pip install -r requirements-gui.txt

# Option 3: System packages (if available)
sudo apt update
sudo apt install python3-textual python3-textual-dev
```

## Usage

### Terminal Mode (TUI)

Launch the GUI installer directly in your terminal:

```bash
# If installed with pipx
misp-install-gui

# Load existing configuration
misp-install-gui --load config/misp-config.json

# Save configuration without installing
misp-install-gui --save-only

# Or run directly without installing
python3 misp_install_gui.py
```

### Web Browser Mode

Serve the GUI installer in a web browser:

```bash
# If installed with pipx
textual run --command misp-install-gui

# Or serve the Python module directly
textual serve misp_install_gui.py

# Serve on specific port
textual serve misp_install_gui.py --port 8080

# Make accessible from other machines
textual serve misp_install_gui.py --host 0.0.0.0 --port 8080
```

Then open your browser to: `http://localhost:8000`

**⚠️ Port Considerations:**
- **DO NOT use port 443** - Reserved for MISP HTTPS interface
- **DO NOT use port 80** - May be used by MISP HTTP redirect
- **Recommended ports**: 8000, 8080, 8888, 3000 (non-privileged)
- Default Textual port (8000) is safe and doesn't conflict with MISP

## Wizard Steps

### Step 1: Welcome Screen

- Introduction to MISP
- Prerequisites checklist
- System requirements

**Actions:**
- **Continue** - Proceed to network configuration
- **Exit** - Quit the installer

### Step 2: Network Configuration

Configure network settings for your MISP installation.

**Fields:**
- **Server IP Address** - Auto-detected from system (editable)
  - Format: `xxx.xxx.xxx.xxx`
  - Example: `192.168.1.100`
- **Domain/FQDN** - Fully qualified domain name
  - Example: `misp.company.com`, `misp-dev.local`
- **Admin Email** - Email for administrator account
  - Example: `admin@company.com`
- **Organization Name** - Your organization
  - Example: `Security Operations`, `tKQB Enterprises`

**Validation:**
- IP address must be valid IPv4 format
- Domain must contain at least one dot
- Email must be valid format

**Navigation:**
- **← Back** - Return to welcome screen
- **Next →** - Continue to security settings

### Step 3: Security Settings

Configure strong passwords for MISP components.

**Password Requirements:**
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

**Fields:**
- **Admin Password** - Password for MISP web interface
- **MySQL Database Password** - Password for MySQL database
- **GPG Passphrase** - Passphrase for GPG encryption

**Features:**
- **🎲 Auto-Generate All Passwords** - Generate strong random passwords
- Real-time password strength validation
- Password visibility toggle

**Navigation:**
- **← Back** - Return to network configuration
- **Next →** - Continue to environment selection

### Step 4: Environment Selection

Choose the deployment environment.

**Options:**

1. **Production (Recommended)**
   - Optimized performance
   - Security hardened
   - Minimal logging
   - Best for live deployments

2. **Staging**
   - Production-like configuration
   - Used for testing before production
   - Medium logging level

3. **Development**
   - Debug mode enabled
   - Verbose logging
   - Relaxed security for development
   - Best for testing and development

**Navigation:**
- **← Back** - Return to security settings
- **Next →** - Continue to review

### Step 5: Review & Confirm

Review all your configuration before installation.

**Configuration Summary:**
- Network settings (IP, domain, email, organization)
- Security (passwords shown as ••••••••)
- Environment type

**Actions:**
- **← Back** - Return to environment selection
- **Save Config Only** - Save configuration to JSON file without installing
- **Install MISP** - Save config and begin installation

**Configuration File:**
- Saved to: `config/misp-gui-config-YYYYMMDD_HHMMSS.json`
- File permissions: `600` (owner read/write only)
- Can be reused with CLI installer: `python3 misp-install.py --config [file]`

### Step 6: Installation Progress

Monitor the installation progress (Future Implementation).

**Features:**
- Phase-by-phase progress tracking
- Current operation display
- Real-time log streaming
- Estimated time remaining

**Note:** Currently in demo mode. Full integration with `misp-install.py` backend is planned for v1.1.

## Keyboard Shortcuts

### Global Shortcuts
- `Tab` / `Shift+Tab` - Navigate between fields
- `Enter` - Activate buttons
- `Esc` - Go back / Cancel
- `q` - Quit application (with confirmation)
- `d` - Toggle dark/light mode

### Text Input
- `Ctrl+V` - **Paste from system clipboard** (works everywhere!)
- `Ctrl+C` - Copy selected text (select with mouse first)
- `Ctrl+X` - Cut selected text (select with mouse first)

**How it works:**
- The GUI installer uses `pyperclip` for full clipboard support
- Copy text anywhere (browser, terminal, editor)
- Press `Ctrl+V` in any input field to paste
- Works on Linux (with xclip/xsel), macOS, and Windows

### Navigation
- `←` / `→` - Navigate buttons
- `↑` / `↓` - Navigate radio buttons
- `Space` - Select radio button / checkbox

## Configuration File Format

The GUI installer generates a JSON configuration file:

```json
{
  "server_ip": "192.168.20.193",
  "domain": "misp.company.com",
  "admin_email": "admin@company.com",
  "admin_org": "Security Operations",
  "admin_password": "SecurePass123!@#",
  "mysql_password": "DBPass456!@#",
  "gpg_passphrase": "GPGPass789!@#",
  "environment": "production"
}
```

### Using with CLI Installer

The generated config file is compatible with the command-line installer:

```bash
# Use GUI-generated config with CLI installer
python3 misp-install.py --config config/misp-gui-config-20251014_123456.json --non-interactive
```

This is perfect for:
- CI/CD pipelines
- Automated deployments
- Repeatable installations
- Testing different configurations

## CI/CD Integration

Use the GUI installer to create configurations, then automate with the CLI:

```bash
# 1. Create configuration via GUI (one-time)
python3 misp_install_gui.py --save-only

# 2. Use configuration in automation
python3 misp-install.py --config config/misp-gui-config.json --non-interactive

# 3. Or use in Ansible/Terraform
ansible-playbook -e "misp_config_file=config/misp-gui-config.json" misp-deploy.yml
```

## Troubleshooting

### Textual Not Installed

**Error:**
```
❌ Textual framework not installed
📦 Install with: pip install textual textual-dev
```

**Solution:**
```bash
pip install textual textual-dev
```

### Python Version Too Old

**Error:**
```
❌ Python 3.8 or higher required
```

**Solution:**
```bash
# Update Python
sudo apt update
sudo apt install python3.10

# Or use pyenv to manage Python versions
pyenv install 3.10.0
pyenv global 3.10.0
```

### Terminal Display Issues

If the UI looks garbled or incorrect:

**Solution 1: Update Terminal**
```bash
# Use a modern terminal emulator
# - Gnome Terminal
# - iTerm2 (macOS)
# - Windows Terminal (Windows 11)
```

**Solution 2: Set TERM variable**
```bash
export TERM=xterm-256color
python3 misp_install_gui.py
```

### Web Mode Not Working

**Error:**
```
textual: command not found
```

**Solution:**
```bash
# Install textual-dev
pip install textual-dev

# Or use python module directly
python3 -m textual serve misp_install_gui.py
```

### Configuration File Permissions

If you get permission errors when saving config:

**Solution:**
```bash
# Ensure config directory exists and is writable
mkdir -p config
chmod 755 config
```

## Advanced Usage

### Custom Port for Web Mode

```bash
# Serve on port 3000 (safe, doesn't conflict with MISP)
textual serve misp_install_gui.py --port 3000

# Serve on port 8888 (safe alternative)
textual serve misp_install_gui.py --port 8888
```

**⚠️ Avoid These Ports:**
- Port 443: MISP HTTPS (ssl)
- Port 80: MISP HTTP (redirect)
- Port 3306: MySQL database
- Port 6379: Redis
- Ports 1024 and below require root privileges

### Headless Server (Web Mode Only)

For servers without GUI terminal support:

```bash
# Install via SSH, serve web GUI
ssh user@server
cd misp-install
textual serve misp_install_gui.py --host 0.0.0.0 --port 8080

# Access from your local browser
http://server-ip:8080
```

### Load and Edit Existing Config

```bash
# Load existing config
python3 misp_install_gui.py --load config/production.json

# Make changes in GUI
# Save as new config
```

### Batch Configuration Generation

Create multiple configurations:

```bash
# Development config
python3 misp_install_gui.py --save-only
# Save as: config/dev-config.json

# Staging config
python3 misp_install_gui.py --save-only
# Save as: config/staging-config.json

# Production config
python3 misp_install_gui.py --save-only
# Save as: config/prod-config.json
```

## Security Considerations

### Password Handling

- Passwords are validated in real-time
- Strong passwords are enforced (12+ chars, mixed case, numbers, special chars)
- Auto-generated passwords use cryptographically secure random generation
- Passwords are never displayed in plain text (except during generation)

### Configuration Files

- Config files are saved with `600` permissions (owner read/write only)
- Keep configuration files secure - they contain sensitive passwords
- Do not commit config files to version control (add to `.gitignore`)
- Use environment variables or secrets management for CI/CD

### Web Mode Security

- Web mode binds to localhost by default (only accessible from local machine)
- Use `--host 0.0.0.0` carefully - anyone on network can access
- Consider using SSH tunneling for remote access:
  ```bash
  # On server
  textual serve misp_install_gui.py

  # On local machine
  ssh -L 8000:localhost:8000 user@server

  # Access via localhost:8000
  ```

## Tips & Best Practices

### 1. Use Auto-Generate for Passwords

Click the **🎲 Auto-Generate All Passwords** button to create strong, random passwords. This is faster and more secure than manual entry.

### 2. Save Configuration First

Before starting installation, click **Save Config Only** to save your configuration. This allows you to:
- Review the config file
- Use it later for automation
- Reuse it for multiple installations

### 3. Test in Development Environment

Always test your configuration in a development environment before production:
1. Use GUI to create dev config
2. Install with `environment: development`
3. Test MISP functionality
4. Create production config with same settings but `environment: production`

### 4. Use Descriptive Domain Names

Use meaningful domain names that reflect the environment:
- `misp-dev.company.local` - Development
- `misp-staging.company.local` - Staging
- `misp.company.com` - Production

### 5. Document Your Configuration

Add comments to your saved config files:
```json
{
  "_comment": "MISP Production Configuration - 2025-10-14",
  "_owner": "security-team@company.com",
  "server_ip": "10.0.1.100",
  ...
}
```

## Future Features (Planned)

v1.1 (Planned):
- ✅ Full installation integration with misp-install.py backend
- ✅ Real-time installation progress tracking
- ✅ Log streaming from installation process
- ✅ Resume capability after interruption

v1.2 (Planned):
- ✅ Performance tuning screen (PHP memory, workers)
- ✅ Optional integrations screen (Splunk, Security Onion, Azure Key Vault)
- ✅ System resource auto-detection
- ✅ Installation time estimation

v2.0 (Future):
- ✅ Multi-language support (i18n)
- ✅ Configuration templates
- ✅ Custom branding
- ✅ Authentication for web mode

## Support

### Documentation
- Main README: `README.md`
- CLI Installer: `misp-install.py --help`
- Developer Guide: `docs/GUI_DEVELOPMENT.md`

### Issues
Report issues at: https://github.com/gforce-gallagher-01/misp-install/issues

### Community
- MISP Project: https://www.misp-project.org/
- Textual Framework: https://github.com/Textualize/textual

## License

This project is part of the MISP Installation Tool suite by tKQB Enterprises.

---

**Version:** 1.0
**Last Updated:** 2025-10-14
**Maintainer:** tKQB Enterprises
