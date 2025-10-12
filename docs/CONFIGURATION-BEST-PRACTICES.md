# MISP Configuration Best Practices

This guide covers enterprise-grade configuration recommendations for production MISP deployments.

## Table of Contents

1. [Security Configuration](#security-configuration)
2. [Performance Tuning](#performance-tuning)
3. [Email/SMTP Setup](#emailsmtp-setup)
4. [Network & Proxy Configuration](#network--proxy-configuration)
5. [Authentication Options](#authentication-options)
6. [Backup & Disaster Recovery](#backup--disaster-recovery)
7. [Monitoring & Logging](#monitoring--logging)

---

## Security Configuration

### 1. Strong Passwords & Keys

**Critical Security Settings** - Generate strong random values:

```bash
# Generate strong passwords
openssl rand -base64 32

# Generate encryption key (32 characters)
openssl rand -hex 16
```

Update these in `/opt/misp/.env`:

```bash
ADMIN_PASSWORD=$(openssl rand -base64 24)
MYSQL_PASSWORD=$(openssl rand -base64 24)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 24)
REDIS_PASSWORD=$(openssl rand -base64 24)
GPG_PASSPHRASE=$(openssl rand -base64 24)
ENCRYPTION_KEY=$(openssl rand -hex 16)
```

### 2. HTTPS and SSL Configuration

**Requirement**: Production MISP deployments MUST use HTTPS.

**Options**:

1. **Let's Encrypt (Recommended for internet-facing)**:
   ```bash
   # Install certbot
   sudo apt install certbot

   # Get certificate
   sudo certbot certonly --standalone -d misp.example.com

   # Copy to MISP SSL directory
   sudo cp /etc/letsencrypt/live/misp.example.com/fullchain.pem /opt/misp/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/misp.example.com/privkey.pem /opt/misp/ssl/key.pem
   sudo chown -R $USER:$USER /opt/misp/ssl/
   ```

2. **Corporate PKI Certificate** (for internal deployments):
   ```bash
   # Place your certificates in:
   /opt/misp/ssl/cert.pem    # Certificate + intermediates
   /opt/misp/ssl/key.pem     # Private key
   /opt/misp/ssl/ca.pem      # Root CA (optional)
   ```

3. **Self-signed (Development ONLY)**:
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout /opt/misp/ssl/key.pem \
     -out /opt/misp/ssl/cert.pem \
     -subj "/CN=misp.example.com"
   ```

**Configure in .env**:
```bash
BASE_URL=https://misp.example.com
DISABLE_SSL_REDIRECT=false
HSTS_MAX_AGE=31536000  # 1 year
X_FRAME_OPTIONS=SAMEORIGIN
```

### 3. Security Headers

Enable security headers in `/opt/misp/.env`:

```bash
# HTTP Strict Transport Security
HSTS_MAX_AGE=31536000

# Clickjacking protection
X_FRAME_OPTIONS=SAMEORIGIN

# Content Security Policy (advanced)
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'

# Cookie security
PHP_SESSION_COOKIE_SECURE=true
PHP_SESSION_COOKIE_SAMESITE=Strict
```

### 4. Hide Credentials from Logs

**Best Practice**: Prevent plaintext credentials in logs:

```bash
DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true
```

### 5. Database Security

```bash
# Use strong passwords
MYSQL_PASSWORD=$(openssl rand -base64 24)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 24)

# Restrict database access (optional - for advanced setups)
# MYSQL_HOST=db  # Keep as 'db' for Docker internal network
```

---

## Performance Tuning

### 1. Resource Allocation

**Minimum Requirements**:
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB SSD

**Recommended Production**:
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB SSD (NVMe preferred)

### 2. MySQL/MariaDB Tuning

Adjust based on available RAM in `/opt/misp/.env`:

```bash
# For 16 GB RAM server (allocate ~50% to MySQL)
INNODB_BUFFER_POOL_SIZE=8G

# For 8 GB RAM server
INNODB_BUFFER_POOL_SIZE=4G

# For 4 GB RAM server
INNODB_BUFFER_POOL_SIZE=2G

# Performance settings
INNODB_CHANGE_BUFFERING=none
INNODB_IO_CAPACITY=1000
INNODB_IO_CAPACITY_MAX=2000
INNODB_LOG_FILE_SIZE=600M
INNODB_READ_IO_THREADS=16
INNODB_WRITE_IO_THREADS=4
INNODB_STATS_PERSISTENT=ON
```

### 3. PHP Performance Tuning

```bash
# Memory and execution time
PHP_MEMORY_LIMIT=2048M           # Increase for large imports
PHP_MAX_EXECUTION_TIME=300       # 5 minutes for long operations
PHP_MAX_INPUT_TIME=300

# Upload limits (match workload)
PHP_UPLOAD_MAX_FILESIZE=100M     # For large file uploads
PHP_POST_MAX_SIZE=100M
NGINX_CLIENT_MAX_BODY_SIZE=100M  # Must match PHP limits

# FastCGI timeouts (increase for slow operations)
FASTCGI_READ_TIMEOUT=600s        # 10 minutes for large imports
FASTCGI_SEND_TIMEOUT=300s
FASTCGI_CONNECT_TIMEOUT=300s
```

### 4. PHP-FPM Worker Configuration

Calculate based on available RAM:

```bash
# Formula: (Total RAM - MySQL - OS) / PHP_MEMORY_LIMIT
# Example: 16GB server with 8GB MySQL
# Available for PHP: 16GB - 8GB - 2GB (OS) = 6GB
# Workers: 6GB / 2GB = 3 workers

PHP_FCGI_CHILDREN=3
PHP_FCGI_START_SERVERS=2
PHP_FCGI_SPARE_SERVERS=1
```

For high-traffic environments:
```bash
PHP_FCGI_CHILDREN=10
PHP_FCGI_START_SERVERS=5
PHP_FCGI_SPARE_SERVERS=2
```

### 5. Background Workers

Set based on CPU cores:

```bash
# Number of CPU cores (recommended)
WORKERS=8

# Minimum 2, even for small systems
WORKERS=2
```

### 6. Redis Configuration

```bash
# Enable password authentication
REDIS_PASSWORD=$(openssl rand -base64 24)
ENABLE_REDIS_EMPTY_PASSWORD=false
```

---

## Email/SMTP Setup

### 1. Gmail (with App Password)

```bash
SMARTHOST_ADDRESS=smtp.gmail.com
SMARTHOST_PORT=587
SMARTHOST_USER=youremail@yourdomain.com
SMARTHOST_PASSWORD=your-app-password  # Not your regular password!
SMTP_FQDN=misp.example.com
```

**Gmail Setup**:
1. Enable 2-Step Verification in Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use 16-character app password in SMARTHOST_PASSWORD

### 2. Microsoft 365 / Office 365

```bash
SMARTHOST_ADDRESS=smtp.office365.com
SMARTHOST_PORT=587
SMARTHOST_USER=youremail@yourdomain.com
SMARTHOST_PASSWORD=your-password
SMTP_FQDN=misp.example.com
```

**Authentication**: Modern Authentication supported (OAuth2 not required)

### 3. Amazon SES

```bash
SMARTHOST_ADDRESS=email-smtp.us-east-1.amazonaws.com
SMARTHOST_PORT=587
SMARTHOST_USER=your-smtp-username
SMARTHOST_PASSWORD=your-smtp-password
SMTP_FQDN=misp.example.com
```

**Amazon SES Setup**:
1. Verify domain in SES Console
2. Move out of sandbox for production use
3. Create SMTP credentials
4. Use region-specific SMTP endpoint

### 4. Generic SMTP Server

```bash
SMARTHOST_ADDRESS=mail.example.com
SMARTHOST_PORT=587  # or 25, 465
SMARTHOST_USER=smtp-user
SMARTHOST_PASSWORD=smtp-password
SMTP_FQDN=misp.example.com
```

### 5. Test Email Configuration

After configuration:

```bash
# Restart MISP
cd /opt/misp && docker compose down && docker compose up -d

# Test from MISP UI
# Log in > Administration > Server Settings > MISP Settings > Email
# Click "Test Email" button
```

---

## Network & Proxy Configuration

### 1. Reverse Proxy Setup

If MISP is behind Nginx, HAProxy, or Cloudflare:

```bash
# Trust proxy headers
NGINX_X_FORWARDED_FOR=X-Forwarded-For

# List of trusted proxy IPs (CIDR notation)
NGINX_SET_REAL_IP_FROM=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16

# If behind Cloudflare, add Cloudflare IPs
NGINX_SET_REAL_IP_FROM=103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,...
```

### 2. Corporate HTTP Proxy

For environments requiring outbound proxy:

```bash
PROXY_ENABLE=true
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
PROXY_METHOD=http

# If proxy requires authentication
PROXY_USER=proxy-username
PROXY_PASSWORD=proxy-password
```

### 3. Port Configuration

Default ports (80/443):
```bash
CORE_HTTP_PORT=80
CORE_HTTPS_PORT=443
```

Custom ports (if 80/443 are in use):
```bash
CORE_HTTP_PORT=8080
CORE_HTTPS_PORT=8443

# Update BASE_URL accordingly
BASE_URL=https://misp.example.com:8443
```

---

## Authentication Options

### 1. Local Authentication (Default)

Standard username/password authentication:

```bash
# No additional configuration needed
# Users managed in MISP UI
```

### 2. Azure Entra ID (Recommended for Microsoft 365 Environments)

See [AZURE-ENTRA-ID-SETUP.md](AZURE-ENTRA-ID-SETUP.md) for detailed guide.

Quick configuration:
```bash
AAD_ENABLE=true
AAD_CLIENT_ID=your-client-id
AAD_TENANT_ID=your-tenant-id
AAD_CLIENT_SECRET=your-client-secret
AAD_REDIRECT_URI=https://misp.example.com/users/login
AAD_PROVIDER=AzureAD
AAD_PROVIDER_USER=AzureAD
```

### 3. LDAP / Active Directory

For traditional AD environments:

```bash
APACHESECUREAUTH_LDAP_ENABLE=true
APACHESECUREAUTH_LDAP_SERVER=ldaps://dc.example.com:636
APACHESECUREAUTH_LDAP_READER_USER=cn=misp-service,dc=example,dc=com
APACHESECUREAUTH_LDAP_READER_PASSWORD=service-password
APACHESECUREAUTH_LDAP_DN=dc=example,dc=com
APACHESECUREAUTH_LDAP_SEARCH_FILTER=(objectClass=person)
APACHESECUREAUTH_LDAP_SEARCH_ATTRIBUTE=sAMAccountName
APACHESECUREAUTH_LDAP_EMAIL_FIELD=mail
APACHESECUREAUTH_LDAP_DEFAULT_ROLE_ID=3
APACHESECUREAUTH_LDAP_DEFAULT_ORG=1
```

### 4. Generic OIDC (Okta, Auth0, Keycloak)

```bash
OIDC_ENABLE=true
OIDC_PROVIDER_URL=https://login.example.com/realms/misp
OIDC_CLIENT_ID=misp-client
OIDC_CLIENT_SECRET=your-client-secret
OIDC_CODE_CHALLENGE_METHOD=S256
OIDC_DEFAULT_ORG=1
OIDC_MIXEDAUTH=true  # Allow local login as fallback
```

---

## Backup & Disaster Recovery

### 1. Automated Backups

**Daily backups** with 30-day retention (recommended):

```bash
# Create cron job
crontab -e

# Add daily backup at 2 AM
0 2 * * * ~/misp-repo/misp-install/scripts/backup-misp.py >> /var/log/misp-backup.log 2>&1
```

### 2. Backup to Remote Storage

**Option 1: rsync to remote server**:

```bash
# In backup script or cron
rsync -avz ~/misp-backups/ backup-server:/backups/misp/
```

**Option 2: S3 / Cloud Storage**:

```bash
# Install AWS CLI
pip3 install awscli

# Configure credentials
aws configure

# Upload to S3
aws s3 sync ~/misp-backups/ s3://your-bucket/misp-backups/
```

### 3. Test Restore Procedure

**Best Practice**: Test restore procedure quarterly:

```bash
# 1. Create test backup
python3 backup-misp.py

# 2. Uninstall MISP
python3 uninstall-misp.py --force

# 3. Reinstall MISP
python3 misp-install.py

# 4. Restore from backup
tar -xzf ~/misp-backups/misp-backup-YYYYMMDD_HHMMSS.tar.gz
# Follow restore procedure in backup_info.txt
```

---

## Monitoring & Logging

### 1. Application Logs

**Log Locations**:
```bash
# Installation logs
~/.misp-install/logs/

# MISP application logs
/opt/misp/logs/

# Docker container logs
docker compose logs -f misp-core
docker compose logs -f db
docker compose logs -f redis
```

### 2. Health Checks

**Check MISP Status**:

```bash
# Container status
cd /opt/misp && docker compose ps

# Health check
curl -k https://localhost/users/heartbeat

# Database connection
docker compose exec db mysql -umisp -p -e "SELECT VERSION();"
```

### 3. Resource Monitoring

**Monitor System Resources**:

```bash
# CPU and memory usage
docker stats

# Disk usage
df -h /opt/misp
df -h /var/lib/docker

# Network connections
netstat -tunlp | grep -E '(80|443|3306|6379)'
```

### 4. Centralized Logging (Optional)

For enterprise environments, forward logs to SIEM:

**Example with rsyslog**:

```bash
# Configure Docker logging driver
# Edit docker-compose.yml or /etc/docker/daemon.json
{
  "log-driver": "syslog",
  "log-opts": {
    "syslog-address": "udp://siem.example.com:514",
    "tag": "misp/{{.Name}}"
  }
}
```

### 5. Alerting

**Set up alerts** for critical events:

- Disk space < 20%
- Database connection failures
- Container crashes
- Failed logins (multiple attempts)
- Backup failures

**Example: Disk space alert**:

```bash
# Add to cron
DISK_USAGE=$(df -h /opt/misp | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
  echo "MISP disk usage: ${DISK_USAGE}%" | mail -s "MISP Disk Alert" youremail@yourdomain.com
fi
```

---

## Environment-Specific Configurations

### Development Environment

```bash
BASE_URL=https://misp-dev.example.com
DEBUG=1  # Enable debug (DEV ONLY!)
HSTS_MAX_AGE=0  # Disable HSTS
WORKERS=2  # Minimal workers
PHP_MEMORY_LIMIT=1024M
INNODB_BUFFER_POOL_SIZE=1G
```

### Production Environment

```bash
BASE_URL=https://misp.example.com
DEBUG=0  # Disable debug
DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true
HSTS_MAX_AGE=31536000
WORKERS=8
PHP_MEMORY_LIMIT=2048M
INNODB_BUFFER_POOL_SIZE=8G
```

### High-Availability / Clustered

For clustered deployments, consult MISP clustering documentation:
- External MySQL cluster
- Redis Sentinel/Cluster
- Load balancer configuration
- Shared storage for attachments

---

## Configuration Checklist

Before going to production, verify:

- [ ] Strong passwords for all services
- [ ] Valid SSL certificate installed
- [ ] HSTS enabled (HSTS_MAX_AGE=31536000)
- [ ] Debug mode disabled (DEBUG=0)
- [ ] Credentials hidden from logs (DISABLE_PRINTING_PLAINTEXT_CREDENTIALS=true)
- [ ] SMTP configured and tested
- [ ] Automated backups configured
- [ ] Restore procedure tested
- [ ] Authentication method configured (Azure AD, LDAP, or local)
- [ ] Resource limits tuned for workload
- [ ] Monitoring and alerting configured
- [ ] Firewall rules configured
- [ ] User access controls configured in MISP

---

## Additional Resources

- **MISP Documentation**: https://www.misp-project.org/documentation/
- **MISP Security Guide**: https://www.misp-project.org/documentation/administration.html
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **MISP Docker GitHub**: https://github.com/MISP/misp-docker

---

**tKQB Enterprises MISP Deployment**
