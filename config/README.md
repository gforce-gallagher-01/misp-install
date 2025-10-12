# MISP Configuration Files

Quick reference for MISP installation configuration files.

---

## 📁 Configuration Files

### `misp-config.json`
Default configuration for automated MISP installation.

```json
{
  "server_ip": "192.168.20.95",
  "domain": "misp.lan",
  "admin_email": "admin@example.com",
  "admin_org": "YourOrganization",
  "admin_password": "YourSecurePassword123!",
  "mysql_password": "YourMySQLPassword123!",
  "gpg_passphrase": "YourGPGPassphrase123!",
  "encryption_key": "generate_or_paste_32_char_hex",
  "environment": "production"
}
```

### `misp-config-dev.json`
Development environment configuration.

```json
{
  "server_ip": "192.168.20.100",
  "domain": "misp-dev.lan",
  "admin_email": "dev@example.com",
  "admin_org": "DevTeam",
  "environment": "development"
}
```

### `misp-config.yaml`
YAML format for those who prefer it (requires PyYAML).

```yaml
server_ip: "192.168.20.95"
domain: "misp.lan"
admin_email: "admin@example.com"
admin_org: "YourOrganization"
environment: "production"
```

---

## 🚀 Quick Start

### 1. Copy Template

```bash
# Copy and edit default config
cp misp-config.json my-config.json
nano my-config.json
```

### 2. Edit Values

**Required Fields:**
- `server_ip` - Server IP address
- `domain` - FQDN for MISP
- `admin_email` - Admin email address
- `admin_org` - Organization name
- `admin_password` - Admin password (min 12 chars)
- `mysql_password` - Database password (min 12 chars)
- `gpg_passphrase` - GPG passphrase (min 12 chars)

**Optional Fields:**
- `encryption_key` - Auto-generated if not provided
- `environment` - `production`, `staging`, or `development`
- `base_url` - Auto-generated from domain if not provided

### 3. Run Installation

```bash
# Use your config file
python3 misp-install.py --config my-config.json --non-interactive
```

---

## 🔐 Password Requirements

All passwords must have:
- ✅ Minimum 12 characters
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter
- ✅ At least one number
- ✅ At least one special character (!@#$%^&*)

**Example Valid Passwords:**
- `MySecure123!Pass`
- `P@ssw0rd2024Secure`
- `Admin#Pass123Word`

---

## 🌍 Environment Types

| Environment | Use Case | Features |
|-------------|----------|----------|
| `production` | Live system | Full security, performance tuning |
| `staging` | Pre-production testing | Same as prod, separate data |
| `development` | Development/testing | Debug enabled, relaxed security |

---

## 📝 Configuration Examples

### Minimal Config (Passwords Only)

Only specify passwords, all else uses defaults:

```json
{
  "admin_password": "YourSecure123!Pass",
  "mysql_password": "Database123!Pass",
  "gpg_passphrase": "GPGPhrase123!Secure"
}
```

### Production Config

```json
{
  "server_ip": "10.0.1.50",
  "domain": "misp.company.com",
  "admin_email": "security@company.com",
  "admin_org": "Company Security Team",
  "admin_password": "Prod#Secure123!Pass",
  "mysql_password": "ProdDB#123!Secure",
  "gpg_passphrase": "ProdGPG#123!Phrase",
  "encryption_key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "environment": "production"
}
```

### Multi-Environment Setup

```bash
configs/
├── production.json    # Live system
├── staging.json       # Pre-prod testing
└── development.json   # Dev environment
```

---

## 🔧 Advanced Configuration

### Performance Tuning

Add to config (optional):

```json
{
  "performance": {
    "php_memory_limit": "4096M",
    "php_max_execution_time": 300,
    "workers": 4
  }
}
```

### Auto-calculated if not specified:
- `workers` - Based on CPU cores
- `php_memory_limit` - Based on available RAM

---

## 🛡️ Security Best Practices

### ✅ Do's
- **Store configs outside git** - Add `*.json` to `.gitignore`
- **Use strong passwords** - Follow password requirements
- **Restrict file permissions** - `chmod 600 my-config.json`
- **Use environment-specific configs** - Separate prod/dev/staging
- **Generate unique encryption keys** - Never reuse across environments

### ❌ Don'ts
- **Don't commit passwords to git**
- **Don't share config files** via email/chat
- **Don't reuse passwords** across environments
- **Don't use default/example passwords**

---

## 📋 Configuration Checklist

Before running installation:

- [ ] Config file created from template
- [ ] All passwords meet requirements
- [ ] Server IP is correct
- [ ] Domain name is correct
- [ ] Admin email is valid
- [ ] Organization name is set
- [ ] Environment type is correct
- [ ] File permissions set to 600
- [ ] Passwords documented securely (not in config)

---

## 🆘 Common Issues

### Invalid Password Error

```
❌ Password must be at least 12 characters
```

**Fix:** Ensure password meets all requirements (length, uppercase, lowercase, number, special char)

### Config File Not Found

```
❌ Configuration file not found: my-config.json
```

**Fix:** Check file path and current directory
```bash
ls -la my-config.json
python3 misp-install.py --config $(pwd)/my-config.json
```

### PyYAML Not Found

```
⚠️ PyYAML not installed. YAML config support disabled.
```

**Fix:** Install PyYAML or use JSON format
```bash
pip3 install pyyaml
```

---

## 💡 Tips

**Generate Secure Passwords:**
```bash
# Generate random secure password
openssl rand -base64 16 | tr -d '/+=' | head -c 16 && echo '!@#'
```

**Generate Encryption Key:**
```bash
# Generate 32-character hex key
openssl rand -hex 16
```

**Validate JSON:**
```bash
# Check if JSON is valid
python3 -m json.tool my-config.json
```

**Create from Environment Variables:**
```bash
# Use environment variables instead of config file
export MISP_ADMIN_PASSWORD="YourPass123!"
export MISP_MYSQL_PASSWORD="DBPass123!"
export MISP_GPG_PASSPHRASE="GPGPass123!"

python3 misp-install.py  # Will prompt for these
```

---

## 📚 Related Documentation

- **Scripts README:** `../README.md` - All script documentation
- **Installation Guide:** Run `python3 misp-install.py --help`
- **Update Guide:** `MISP-UPDATE.md` - Update procedures
- **Backup Guide:** `MISP-BACKUP-SETUP.md` - Backup configuration

---

**Version:** 1.0  
**Last Updated:** 2025-10-11  

For more information, see the main scripts README or run scripts with `--help`.