# MISP Installation Setup Guide

## 🔐 Security Architecture

This installation uses a **dedicated system user** (`misp-owner`) following security best practices:

- ✅ **Principle of Least Privilege** (NIST SP 800-53 AC-6)
- ✅ **Service Account Isolation** (CIS Benchmarks 5.4.1)
- ✅ **Defense in Depth** (OWASP)
- ✅ **Clear Security Boundaries**

**No manual setup required!** The script automatically handles user creation and permission management.

For complete security documentation, see: `docs/SECURITY_ARCHITECTURE.md`

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04 LTS or newer
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk:** 20GB free space minimum
- **CPU:** 2 cores minimum
- **Python:** 3.8 or higher
- **Sudo Access:** Required (for initial user creation and Docker operations)
- **Internet Connection:** Required

### Software Requirements
```bash
# Python 3.8+
python3 --version

# Sudo access
sudo -v

# Git (usually pre-installed)
git --version
```

---

## 🚀 Running the Installation

### Interactive Mode (Recommended)

Run as your **regular user** (NOT as root):

```bash
python3 misp-install.py
```

**What happens:**
1. Script checks you're not running as root (for security)
2. Script creates `misp-owner` system user (if doesn't exist)
3. Script automatically re-executes itself as `misp-owner`
4. All installation operations run as `misp-owner`

You'll be prompted for sudo password **once** to create the dedicated user.

### Using Configuration File

```bash
python3 misp-install.py --config config/misp-config.json
```

### Non-Interactive Mode (CI/CD)

```bash
python3 misp-install.py --config config/prod-config.json --non-interactive
```

---

## 🤖 Automated Environments (CI/CD, Ansible, etc.)

For fully automated deployments, configure passwordless sudo for specific commands only:

### Option 1: Minimal Sudo Configuration (Recommended)

Add these specific commands to sudoers:

```bash
sudo visudo
```

Add this line (creates file in `/etc/sudoers.d/`):

```bash
# Or use sudoers.d for better management
sudo visudo -f /etc/sudoers.d/misp-install
```

Add (replace `your-username` with actual username):

```
# MISP Installation - Minimal Sudo Permissions
your-username ALL=(ALL) NOPASSWD: /bin/mkdir, /bin/chown, /bin/chmod, /bin/rm, /bin/mv, /bin/cp, /usr/bin/docker, /usr/bin/apt, /usr/bin/apt-get, /usr/bin/systemctl, /usr/bin/useradd, /usr/bin/usermod, /usr/sbin/groupadd, /usr/bin/tee
```

### Option 2: User-Specific Docker Access

If you only want to grant Docker access:

```bash
# Add user to docker group
sudo usermod -aG docker your-username

# Configure passwordless sudo for user creation only
echo "your-username ALL=(ALL) NOPASSWD: /usr/bin/useradd, /usr/bin/usermod, /bin/chown, /bin/chmod, /bin/mkdir" | sudo tee /etc/sudoers.d/misp-user-mgmt
```

### Testing Automation

Test your automated setup:

```bash
# Test non-interactive installation
python3 misp-install.py --config config/test-debug.json --non-interactive

# Verify no password prompts occur
```

---

## 📋 How It Works

### User Creation Process

1. **Check Current User**: Script verifies you're not running as root
2. **Check for misp-owner**: Script looks for existing `misp-owner` user
3. **Create User (if needed)**:
   ```bash
   sudo useradd --system --create-home --home-dir /home/misp-owner \
     --shell /bin/bash --comment "MISP Installation Owner" misp-owner
   ```
4. **Re-execute**: Script re-runs itself as `misp-owner` using:
   ```bash
   sudo -u misp-owner python3 misp-install.py [args...]
   ```

### File Ownership

All MISP files are owned by `misp-owner`:

| Path | Owner | Group | Permissions |
|------|-------|-------|-------------|
| `/opt/misp` | misp-owner | misp-owner | 755 |
| `/opt/misp/.env` | misp-owner | misp-owner | 600 |
| `/opt/misp/PASSWORDS.txt` | misp-owner | misp-owner | 600 |
| `/opt/misp/logs` | misp-owner | misp-owner | 777 |
| `/opt/misp/ssl/*` | misp-owner | misp-owner | 644/600 |
| `/home/misp-owner` | misp-owner | misp-owner | 750 |

### Docker Group Membership

The `misp-owner` user is added to the `docker` group:

```bash
sudo usermod -aG docker misp-owner
```

This allows `misp-owner` to manage Docker containers without requiring root privileges.

**Security Note**: Docker group membership is equivalent to root access, but this is acceptable because `misp-owner` is a dedicated service account with no interactive login shell.

---

## 🔍 Verification

After installation, verify the security setup:

### Check User Creation

```bash
# Verify misp-owner user exists
id misp-owner

# Expected output:
# uid=XXX(misp-owner) gid=XXX(misp-owner) groups=XXX(misp-owner),YYY(docker)
```

### Check File Ownership

```bash
# Check MISP directory ownership
ls -la /opt/misp

# Expected: all files owned by misp-owner:misp-owner
```

### Check Docker Access

```bash
# Test Docker access as misp-owner
sudo -u misp-owner docker ps

# Should show running containers
```

---

## 🛠️ Troubleshooting

### "ERROR: Do not run this script as root!"

**Cause**: Running script with `sudo` or as root user

**Solution**: Run as your regular user:
```bash
python3 misp-install.py  # NOT: sudo python3 ...
```

### "Failed to create user misp-owner"

**Cause**: Insufficient sudo privileges

**Solution**: Ensure you can run sudo:
```bash
sudo -v  # Test sudo access
```

### "Permission denied" when accessing Docker

**Cause**: misp-owner not in docker group, or group not activated

**Solution**: The script handles this automatically. If issues persist:
```bash
# Manually add to docker group
sudo usermod -aG docker misp-owner

# Verify
sudo -u misp-owner groups
```

### Passwordless Sudo Not Working

**Cause**: Incorrect sudoers configuration

**Solution**: Verify syntax:
```bash
# Test specific command
sudo -l -U your-username

# Should show NOPASSWD entries
```

### Container Permission Issues

**Cause**: Docker volumes created with wrong ownership

**Solution**: The script fixes this in Phase 5.5. If issues persist:
```bash
cd /opt/misp
sudo chown -R misp-owner:misp-owner logs/
sudo chmod 777 logs/
```

---

## 📚 Additional Documentation

- **Security Architecture**: `docs/SECURITY_ARCHITECTURE.md`
- **Main README**: `README.md`
- **Changelog**: `docs/testing_and_updates/CHANGELOG.md`
- **Logging Guide**: `README_LOGGING.md`
- **Development Guide**: `CLAUDE.md`

---

## ✅ Best Practices

### DO ✅
- Run installation as regular user
- Let script create misp-owner automatically
- Use config files for automated deployments
- Review logs in `/opt/misp/logs/`
- Keep backups of credentials (PASSWORDS.txt, .env)

### DON'T ❌
- Don't run installation as root
- Don't manually create misp-owner user (script does this)
- Don't modify misp-owner's home directory manually
- Don't remove misp-owner from docker group
- Don't change ownership of /opt/misp files manually

---

## 🤝 Support

For issues, check:
1. Installation logs: `/opt/misp/logs/`
2. Docker container logs: `cd /opt/misp && sudo docker compose logs`
3. System logs: `journalctl -xe`

**Made with ❤️ following industry security best practices**
