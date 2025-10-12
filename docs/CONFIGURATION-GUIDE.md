# MISP Configuration Guide

## Overview

This guide provides comprehensive configuration options for MISP deployments, from basic setups to enterprise-grade configurations with Azure Entra ID integration.

## Quick Links

- **[Enterprise .env Template](../config/.env.enterprise-template)** - Complete configuration template with all options
- **[Azure Entra ID Setup](AZURE-ENTRA-ID-SETUP.md)** - Step-by-step guide for Azure AD authentication
- **[Configuration Best Practices](CONFIGURATION-BEST-PRACTICES.md)** - Security, performance, and operational recommendations
- **[Advanced Features](ADVANCED-FEATURES.md)** - Workflows, feeds, modules, sync servers, and automation
- **[Third-Party Integrations](THIRD-PARTY-INTEGRATIONS.md)** - SIEM, EDR, SOAR, sandbox integrations (Splunk, Sentinel, CrowdStrike, etc.)

## Getting Started

### Basic Configuration

For a quick start with minimal configuration:

```bash
# Use the default configuration
cd ~/misp-repo/misp-install
python3 misp-install.py --config config/misp-config.json
```

This creates a basic `.env` file with:
- Local authentication (username/password)
- Default performance settings
- Development-friendly configuration

### Enterprise Configuration

For production deployments with advanced features:

1. **Copy the enterprise template**:
   ```bash
   cp config/.env.enterprise-template /opt/misp/.env
   ```

2. **Edit the configuration**:
   ```bash
   nano /opt/misp/.env
   ```

3. **Update required settings**:
   - `BASE_URL` - Your MISP domain
   - `ADMIN_EMAIL` - Administrator email
   - `ADMIN_ORG` - Organization name
   - All passwords and secrets (search for "CHANGE_THIS")

4. **Configure optional features** (see sections below)

5. **Restart MISP**:
   ```bash
   cd /opt/misp
   docker compose down
   docker compose up -d
   ```

## Configuration Sections

### 1. Core Settings (Required)

Minimum required configuration:

```bash
BASE_URL=https://misp.example.com
ADMIN_EMAIL=youremail@yourdomain.com
ADMIN_ORG=YourOrganization
ADMIN_PASSWORD=strong-password-here
MYSQL_PASSWORD=strong-password-here
GPG_PASSPHRASE=strong-passphrase-here
ENCRYPTION_KEY=32-character-key-here
```

### 2. Authentication Methods

Choose one or more authentication methods:

#### Local Authentication (Default)
No additional configuration needed. Users managed in MISP UI.

#### Azure Entra ID (Recommended for Microsoft 365)
```bash
AAD_ENABLE=true
AAD_CLIENT_ID=your-client-id
AAD_TENANT_ID=your-tenant-id
AAD_CLIENT_SECRET=your-client-secret
AAD_REDIRECT_URI=https://misp.example.com/users/login
```

**Setup Guide**: [AZURE-ENTRA-ID-SETUP.md](AZURE-ENTRA-ID-SETUP.md)

#### LDAP / Active Directory
```bash
APACHESECUREAUTH_LDAP_ENABLE=true
APACHESECUREAUTH_LDAP_SERVER=ldaps://dc.example.com:636
APACHESECUREAUTH_LDAP_READER_USER=cn=service-account,dc=example,dc=com
APACHESECUREAUTH_LDAP_READER_PASSWORD=password
APACHESECUREAUTH_LDAP_DN=dc=example,dc=com
```

#### Generic OIDC (Okta, Auth0, Keycloak)
```bash
OIDC_ENABLE=true
OIDC_PROVIDER_URL=https://login.example.com
OIDC_CLIENT_ID=misp-client
OIDC_CLIENT_SECRET=your-secret
```

### 3. Email / SMTP Configuration

Configure email for notifications and user invitations:

#### Gmail
```bash
SMARTHOST_ADDRESS=smtp.gmail.com
SMARTHOST_PORT=587
SMARTHOST_USER=youremail@yourdomain.com
SMARTHOST_PASSWORD=app-password  # Generate from Google Account
SMTP_FQDN=misp.example.com
```

#### Office 365
```bash
SMARTHOST_ADDRESS=smtp.office365.com
SMARTHOST_PORT=587
SMARTHOST_USER=youremail@yourdomain.com
SMARTHOST_PASSWORD=password
SMTP_FQDN=misp.example.com
```

#### Amazon SES
```bash
SMARTHOST_ADDRESS=email-smtp.us-east-1.amazonaws.com
SMARTHOST_PORT=587
SMARTHOST_USER=smtp-username
SMARTHOST_PASSWORD=smtp-password
SMTP_FQDN=misp.example.com
```

### 4. Security Configuration

#### SSL/TLS Settings
```bash
BASE_URL=https://misp.example.com
DISABLE_SSL_REDIRECT=false
HSTS_MAX_AGE=31536000  # 1 year
X_FRAME_OPTIONS=SAMEORIGIN
```

#### Session Security
```bash
PHP_SESSION_COOKIE_SECURE=true
PHP_SESSION_COOKIE_SAMESITE=Strict
PHP_SESSION_TIMEOUT=60
```

#### Credential Protection
```bash
DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true
```

### 5. Performance Tuning

#### MySQL/MariaDB
```bash
# Adjust based on available RAM (50-70% for dedicated DB)
INNODB_BUFFER_POOL_SIZE=8G        # For 16GB server
INNODB_IO_CAPACITY=1000
INNODB_READ_IO_THREADS=16
INNODB_WRITE_IO_THREADS=4
```

#### PHP
```bash
PHP_MEMORY_LIMIT=2048M
PHP_MAX_EXECUTION_TIME=300
PHP_UPLOAD_MAX_FILESIZE=100M
PHP_POST_MAX_SIZE=100M
NGINX_CLIENT_MAX_BODY_SIZE=100M
```

#### Workers
```bash
# Set to number of CPU cores
WORKERS=8
```

### 6. Network Configuration

#### Reverse Proxy
```bash
NGINX_X_FORWARDED_FOR=X-Forwarded-For
NGINX_SET_REAL_IP_FROM=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

#### HTTP Proxy (for outbound connections)
```bash
PROXY_ENABLE=true
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
PROXY_USER=username
PROXY_PASSWORD=password
```

#### Custom Ports
```bash
CORE_HTTP_PORT=8080
CORE_HTTPS_PORT=8443
```

## Configuration Validation

After updating `.env`, validate your configuration:

1. **Check syntax**:
   ```bash
   grep -v '^#' /opt/misp/.env | grep -v '^$' | grep '='
   ```

2. **Restart MISP**:
   ```bash
   cd /opt/misp
   docker compose down
   docker compose up -d
   ```

3. **Check container health**:
   ```bash
   docker compose ps
   ```

4. **View logs for errors**:
   ```bash
   docker compose logs -f misp-core
   ```

5. **Test web access**:
   ```bash
   curl -k https://localhost/users/heartbeat
   ```

## Common Configuration Scenarios

### Scenario 1: Small Organization (< 10 users)

```bash
# Basic settings
BASE_URL=https://misp.example.com
ADMIN_EMAIL=youremail@yourdomain.com
WORKERS=2

# Performance (4GB RAM, 2 CPU)
PHP_MEMORY_LIMIT=1024M
INNODB_BUFFER_POOL_SIZE=1G
PHP_FCGI_CHILDREN=2

# Authentication
# Use local authentication (default)

# Email
SMARTHOST_ADDRESS=smtp.gmail.com
SMARTHOST_PORT=587
```

### Scenario 2: Medium Organization (10-50 users)

```bash
# Basic settings
BASE_URL=https://misp.example.com
ADMIN_EMAIL=youremail@yourdomain.com
WORKERS=4

# Performance (8GB RAM, 4 CPU)
PHP_MEMORY_LIMIT=2048M
INNODB_BUFFER_POOL_SIZE=4G
PHP_FCGI_CHILDREN=4

# Authentication (choose one)
# Option A: Azure Entra ID
AAD_ENABLE=true
AAD_CLIENT_ID=...
# Option B: LDAP
APACHESECUREAUTH_LDAP_ENABLE=true
APACHESECUREAUTH_LDAP_SERVER=...

# Email
SMARTHOST_ADDRESS=smtp.office365.com
SMARTHOST_PORT=587
```

### Scenario 3: Large Enterprise (50+ users)

```bash
# Basic settings
BASE_URL=https://misp.example.com
ADMIN_EMAIL=youremail@yourdomain.com
WORKERS=8

# Performance (16GB RAM, 8 CPU)
PHP_MEMORY_LIMIT=2048M
INNODB_BUFFER_POOL_SIZE=8G
PHP_FCGI_CHILDREN=10
PHP_UPLOAD_MAX_FILESIZE=200M

# Authentication
AAD_ENABLE=true
AAD_CLIENT_ID=...
AAD_CHECK_GROUPS=true  # Group-based roles

# Email
SMARTHOST_ADDRESS=smtp.office365.com
SMARTHOST_PORT=587

# Proxy (if required)
PROXY_ENABLE=true
PROXY_HOST=proxy.corp.com

# Security
DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true
HSTS_MAX_AGE=31536000
```

## Troubleshooting

### Configuration not taking effect

1. Verify `.env` file exists: `ls -la /opt/misp/.env`
2. Check for syntax errors: `cat /opt/misp/.env | grep -E '^[A-Z].*='`
3. Restart containers: `cd /opt/misp && docker compose down && docker compose up -d`
4. Check logs: `docker compose logs misp-core | tail -50`

### Containers failing to start

1. Check Docker resources: `docker stats`
2. Verify disk space: `df -h`
3. Check logs: `docker compose logs`
4. Validate compose file: `docker compose config`

### Authentication not working

1. Verify authentication variables in `.env`
2. Check container logs: `docker compose logs misp-core | grep -i auth`
3. Test connectivity (for LDAP/Azure AD)
4. Verify redirect URIs match exactly

### Email not sending

1. Test SMTP from container:
   ```bash
   docker compose exec misp-core telnet smtp.example.com 587
   ```
2. Check mail container logs: `docker compose logs mail`
3. Verify SMTP credentials
4. Check firewall/proxy blocking outbound SMTP

## Security Checklist

Before deploying to production:

- [ ] All passwords changed from defaults
- [ ] SSL certificate installed and valid
- [ ] HSTS enabled (HSTS_MAX_AGE > 0)
- [ ] Debug mode disabled (DEBUG=0)
- [ ] Credentials hidden from logs (DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true)
- [ ] Strong password policy enforced
- [ ] Authentication method configured (Azure AD/LDAP recommended)
- [ ] SMTP configured and tested
- [ ] Automated backups configured
- [ ] Firewall rules configured
- [ ] Regular updates scheduled

## Additional Resources

- **Enterprise Template**: [config/.env.enterprise-template](../config/.env.enterprise-template)
- **Azure AD Setup**: [AZURE-ENTRA-ID-SETUP.md](AZURE-ENTRA-ID-SETUP.md)
- **Best Practices**: [CONFIGURATION-BEST-PRACTICES.md](CONFIGURATION-BEST-PRACTICES.md)
- **MISP Documentation**: https://www.misp-project.org/documentation/
- **MISP Docker Repository**: https://github.com/MISP/misp-docker

## Support

For configuration assistance:

1. Review documentation files in this directory
2. Check MISP logs: `docker compose logs`
3. Consult MISP community: https://www.misp-project.org/community/
4. Review GitHub issues: https://github.com/MISP/MISP/issues

---

**tKQB Enterprises MISP Deployment**
