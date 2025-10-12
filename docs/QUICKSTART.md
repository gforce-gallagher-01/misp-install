# MISP Installation - Quick Start Guide

## 📦 Step 1: Download Files

Download these files to your server:
- `misp-install.py` - Main installation script
- `README.md` - Full documentation
- `misp-config.yaml` - YAML configuration template (optional)
- `misp-config.json` - JSON configuration template (optional)
- `requirements.txt` - Python dependencies (optional)

```bash
# Download all files to your server
# Place them in your home directory
cd ~
```

## 🔧 Step 2: Install Optional Dependencies

```bash
# Optional: For YAML config support
pip3 install -r requirements.txt

# Or just:
pip3 install pyyaml
```

**Note:** The script works without dependencies! You can skip this step and use interactive mode or JSON configs.

## ⚙️ Step 3: Choose Your Installation Method

### Option A: Interactive (Easiest - Recommended)

```bash
chmod +x misp-install.py
python3 misp-install.py
```

Follow the prompts to configure your installation. This is the easiest method for first-time installations.

### Option B: Using Config File

```bash
# 1. Copy and edit the config template
cp misp-config.yaml my-misp-config.yaml
nano my-misp-config.yaml

# 2. IMPORTANT: Change all passwords!
# Generate strong passwords and update:
# - admin_password
# - mysql_password
# - gpg_passphrase

# 3. Generate encryption key
python3 -c "import secrets; print(secrets.token_hex(16))"
# Copy the output and paste it into encryption_key

# 4. Update other settings
# - server_ip: Your server's IP
# - domain: Your FQDN
# - admin_email: Your email
# - admin_org: Your organization

# 5. Run installation
python3 misp-install.py --config my-misp-config.yaml
```

### Option C: Non-Interactive (CI/CD)

```bash
# For automated deployments
python3 misp-install.py --config prod-config.yaml --non-interactive
```

## 🎯 Step 4: During Installation

The script will:
1. ✅ Check system requirements
2. ✅ Install dependencies (Docker, etc.)
3. ✅ Add you to docker group
4. ✅ Backup any existing installation
5. ✅ Clean up old containers
6. ✅ Clone MISP repository
7. ✅ Generate SSL certificates
8. ✅ Configure everything automatically
9. ✅ Start MISP containers
10. ✅ Wait for initialization
11. ✅ Create documentation

**Expected Time:** 10-15 minutes

## 📝 Step 5: After Installation

### 1. Save Your Credentials
```bash
# View and backup your passwords
cat /opt/misp/PASSWORDS.txt

# IMPORTANT: Save this file somewhere secure!
# Consider using a password manager
```

### 2. Configure Workstations

**On your Windows workstation:**
```powershell
# Run PowerShell as Administrator
Add-Content C:\Windows\System32\drivers\etc\hosts "`n192.168.20.95 misp.lan"
```

**On your Linux/Mac workstation:**
```bash
echo "192.168.20.95 misp.lan" | sudo tee -a /etc/hosts
```

### 3. Access MISP
1. Open browser: `https://misp.lan`
2. Accept the self-signed certificate warning
3. Login with credentials from `PASSWORDS.txt`

### 4. Complete Post-Install Tasks
```bash
# Review the checklist
cat /opt/misp/POST-INSTALL-CHECKLIST.md
```

## 🔄 Common Scenarios

### Resume After Interruption
```bash
python3 misp-install.py --resume
```

### View Logs
```bash
# Check latest log
ls -lt /var/log/misp-install/ | head -2

# View specific log
cat /var/log/misp-install/misp-install-TIMESTAMP.log
```

### Restart MISP
```bash
cd /opt/misp
sudo docker compose restart
```

### Stop MISP
```bash
cd /opt/misp
sudo docker compose down
```

### Start MISP
```bash
cd /opt/misp
sudo docker compose up -d
```

### Check Status
```bash
cd /opt/misp
sudo docker compose ps
```

## 🐛 Troubleshooting

### "Docker group not active"
```bash
# Logout and login again
exit

# Or activate immediately
newgrp docker
```

### "Port 443 already in use"
```bash
# Find what's using the port
sudo lsof -i :443

# Stop the conflicting service
sudo systemctl stop <service-name>
```

### "Insufficient disk space"
```bash
# Check available space
df -h

# Clean Docker
docker system prune -af --volumes
```

### "MISP not responding"
```bash
# Check container logs
cd /opt/misp
sudo docker compose logs misp-core | tail -100

# Restart containers
sudo docker compose restart
```

## 📚 Need Help?

1. **Check logs:** `/var/log/misp-install/`
2. **Read README:** `README.md` has full documentation
3. **Review checklist:** `/opt/misp/POST-INSTALL-CHECKLIST.md`
4. **MISP Docs:** https://www.misp-project.org/documentation/

## 🎉 Success Checklist

- [ ] Downloaded all installation files
- [ ] Ran installation (interactive or config-based)
- [ ] Saved credentials from `PASSWORDS.txt`
- [ ] Configured workstation `/etc/hosts`
- [ ] Logged into MISP web interface
- [ ] Reviewed post-install checklist
- [ ] Configured email settings in MISP
- [ ] Set up backups

---

**That's it! You now have a fully functional MISP instance!** 🚀

For ongoing maintenance and advanced configuration, see `README.md` and the official MISP documentation.