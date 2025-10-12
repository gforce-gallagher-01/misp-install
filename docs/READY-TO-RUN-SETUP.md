# MISP Ready-to-Run Setup Guide

This guide explains how to achieve a "ready-to-run" MISP deployment with all essential features pre-configured and automated.

## Overview

A "ready-to-run" MISP installation includes:
- ✅ All taxonomies, galaxies, and warninglists updated
- ✅ Recommended OSINT feeds enabled
- ✅ Background jobs and caching configured
- ✅ Enrichment modules enabled
- ✅ Best practice settings applied
- ✅ Initial backup created

## Quick Start

### 1. Install MISP

```bash
cd ~/misp-repo/misp-install
python3 misp-install.py --config config/misp-config.json
```

### 2. Run Ready-to-Run Configuration

```bash
cd ~/misp-repo/misp-install/scripts
python3 configure-misp-ready.py
```

This script will:
- Update taxonomies (TLP, PAP, etc.)
- Update galaxies (MITRE ATT&CK, threat actors)
- Update warninglists (false positive filters)
- Update object templates
- Configure background jobs
- Enable enrichment modules
- Create initial backup

### 3. Complete Manual Steps

```bash
# Change default admin password
# Login: admin@admin.test / admin
# Go to: Global Actions > My Profile > Change Password

# Enable recommended feeds (via web UI)
# Go to: Sync Actions > List Feeds
# Enable and cache recommended feeds
```

## Automated Features

### What Gets Configured Automatically

#### 1. **Taxonomies**
Taxonomies provide classification tags for events:
- **TLP (Traffic Light Protocol)**: tlp:clear, tlp:green, tlp:amber, tlp:red
- **PAP (Permissible Actions Protocol)**: Data handling guidance
- **Admiralty Scale**: Information reliability and credibility
- **IEP**: Information Exchange Policy
- **OSINT**: Open Source Intelligence classification
- **And 70+ more taxonomies**

#### 2. **Galaxies**
Large knowledge objects that can be attached to events:
- **MITRE ATT&CK**: Adversary tactics and techniques (1000+ entries)
- **Threat Actors**: Known threat groups and APTs (500+ entries)
- **Malware**: Malware families and variants (1000+ entries)
- **Tools**: Attack tools and utilities
- **Exploit Kits**: Known exploit frameworks
- **Ransomware**: Ransomware families
- **And 50+ more galaxies**

#### 3. **Warninglists**
Lists of indicators that might be false positives:
- RFC1918 addresses (private IPs)
- Top 1M domains (Alexa, Cisco Umbrella)
- Common software and OS IPs
- Known good CAs and certificates
- Google, Microsoft, Amazon, Cloudflare IPs
- Bank ASNs and CIDRs
- And 50+ more warninglists

#### 4. **Object Templates**
Structured data objects for complex indicators:
- Email objects
- File objects
- Network traffic objects
- Domain/IP objects
- Person objects
- Organization objects
- And 200+ more templates

#### 5. **Core Settings**
Best practice MISP settings:
```python
MISP.background_jobs = true                      # Enable background processing
MISP.cached_attachments = true                   # Cache feed data
MISP.enable_advanced_correlations = true         # Better correlation engine
Plugin.Enrichment_services_enable = true         # Enable enrichment
Plugin.Import_services_enable = true             # Enable import modules
Plugin.Export_services_enable = true             # Enable export modules
```

### What Requires Manual Configuration

Some integrations cannot be fully automated and require:

#### 1. **OSINT Feeds** (Manual Enablement)
Recommended feeds to enable manually:
- **CIRCL OSINT Feed** - General threat intelligence
- **Abuse.ch Feodo Tracker** - Banking trojans
- **Abuse.ch URLhaus** - Malware URLs
- **Abuse.ch ThreatFox** - IOC database
- **Botvrij.eu** - Dutch botnet tracker
- **OpenPhish** - Phishing URLs

**Steps**:
1. Go to **Sync Actions** > **List Feeds**
2. Find recommended feeds
3. Click **Edit** for each feed
4. Check **Enabled**
5. Check **Caching enabled**
6. Click **Submit**
7. Click **Fetch and store all feed data**

**Automation Option** (Advanced):
```bash
# Create a cron job to fetch feeds automatically
0 */6 * * * docker compose exec -T misp-core /var/www/MISP/app/Console/cake Server fetchFeed all
```

#### 2. **SMTP Configuration** (Email Notifications)
Configure in `/opt/misp/.env`:
```bash
SMARTHOST_ADDRESS=smtp.office365.com
SMARTHOST_PORT=587
SMARTHOST_USER=youremail@yourdomain.com
SMARTHOST_PASSWORD=your-password
SMTP_FQDN=misp.example.com
```

Test via: **Administration** > **Server Settings** > **Email** > **Test Email**

#### 3. **Enrichment Module API Keys**
Many enrichment modules require API keys:

**VirusTotal**:
```bash
# Get API key from: https://www.virustotal.com/gui/my-apikey
# Set in MISP: Administration > Server Settings > Plugin Settings
Plugin.Enrichment_virustotal_apikey = your-api-key
```

**Shodan**:
```bash
# Get API key from: https://account.shodan.io/
Plugin.Enrichment_shodan_apikey = your-api-key
```

**PassiveTotal/RiskIQ**:
```bash
Plugin.Enrichment_passivetotal_username = your-username
Plugin.Enrichment_passivetotal_apikey = your-api-key
```

**Others**: See [Advanced Features § MISP Modules](ADVANCED-FEATURES.md#misp-modules)

#### 4. **Authentication** (Azure AD, LDAP)
Configure enterprise SSO:
- **Azure Entra ID**: See [Azure Entra ID Setup](AZURE-ENTRA-ID-SETUP.md)
- **LDAP/AD**: Configure in `/opt/misp/.env`

#### 5. **Sync Servers** (Multi-Instance Sharing)
Connect to partner MISP instances:
- **Manual**: Via **Sync Actions** > **List Servers** > **New Server**
- **Automated**: Via environment variables in `.env`

See [Advanced Features § Sync Servers](ADVANCED-FEATURES.md#sync-servers--sharing)

## Integration Checklist

Use this checklist after running `configure-misp-ready.py`:

### Automated (Done by Script)
- [x] Taxonomies updated
- [x] Galaxies updated (MITRE ATT&CK, threat actors)
- [x] Warninglists updated
- [x] Object templates updated
- [x] Background jobs enabled
- [x] Enrichment modules enabled
- [x] Initial backup created

### Manual Configuration Required
- [ ] Change default admin password
- [ ] Enable recommended OSINT feeds
- [ ] Configure feed caching schedule
- [ ] Configure SMTP for email notifications
- [ ] Add enrichment module API keys (VirusTotal, Shodan, etc.)
- [ ] Configure authentication (Azure AD, LDAP, or use local)
- [ ] Set up automated backups (cron job)
- [ ] Configure sync servers (if applicable)
- [ ] Test email notifications
- [ ] Review security settings (HSTS, SSL, etc.)

## Advanced Integrations

### 1. Automated Feed Updates

Create cron job for automatic feed updates:

```bash
# Edit crontab
crontab -e

# Add feed fetch every 6 hours
0 */6 * * * cd /opt/misp && docker compose exec -T misp-core /var/www/MISP/app/Console/cake Server fetchFeed all

# Add weekly full feed refresh
0 3 * * 0 cd /opt/misp && docker compose exec -T misp-core /var/www/MISP/app/Console/cake Server cacheFeed all force
```

### 2. Automated Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * ~/misp-repo/misp-install/scripts/backup-misp.py >> /var/log/misp-backup.log 2>&1
```

### 3. SIEM Integration

**Splunk**:
```bash
# Use Splunk App for MISP
# Download: https://splunkbase.splunk.com/app/4913/
```

**Elasticsearch**:
```bash
# Export MISP events to Elasticsearch
# Use misp-modules elasticsearch_query module
```

**QRadar**:
```bash
# Use QRadar MISP App
# Configure MISP API connection in QRadar
```

### 4. SOAR Integration

**TheHive**:
```bash
# Install TheHive connector
# Configure in MISP: Administration > Server Settings > TheHive
```

**Cortex**:
```bash
# Configure Cortex analyzers
# Set Cortex API key in MISP settings
```

**MISP Modules**:
```bash
# Use action modules for SOAR workflows
# See: /opt/misp/custom/action_mod/
```

### 5. Threat Intelligence Platforms

**MISP can integrate with**:
- **ThreatConnect**: Via API
- **Anomali**: Via STIX export
- **ThreatQuotient**: Via API sync
- **Recorded Future**: Via enrichment module
- **PassiveTotal/RiskIQ**: Via enrichment module

## Custom Initialization Script

For advanced custom integrations, create `/opt/misp/files/customize_misp.sh`:

```bash
#!/bin/bash
# Custom MISP initialization script
# This runs when misp-core container starts

echo "Running custom MISP initialization..."

# Example: Set custom settings
/var/www/MISP/app/Console/cake Admin setSetting "MISP.custom_setting" "value"

# Example: Enable specific taxonomies
/var/www/MISP/app/Console/cake Admin updateTaxonomies

# Example: Install custom Python packages
# pip3 install custom-package

# Example: Configure custom certificates
# cp /custom/rootca.crt /usr/local/share/ca-certificates/
# update-ca-certificates

echo "Custom initialization complete"
```

Enable in `.env`:
```bash
CUSTOM_PATH=/opt/misp/files
```

Mount in `docker-compose.yml` (already configured):
```yaml
volumes:
  - "${CUSTOM_PATH}/:/custom/:Z"
```

## Testing Your Ready-to-Run Setup

### 1. Web Interface Test
```bash
# Access MISP
https://your-misp-domain

# Login with default credentials
# Email: admin@admin.test
# Password: admin

# Expected: Successful login, no errors
```

### 2. Taxonomies Test
```bash
# In MISP: Event Actions > Add Event
# Click on "Tags" field
# Search for "tlp:"

# Expected: See tlp:clear, tlp:green, tlp:amber, tlp:red
```

### 3. Galaxies Test
```bash
# In MISP: Event Actions > View Galaxies
# Browse MITRE ATT&CK

# Expected: See tactics, techniques, and groups
```

### 4. Feeds Test
```bash
# In MISP: Sync Actions > List Feeds
# Click on enabled feed
# Click "Fetch and store all feed data"

# Expected: Feed data downloaded and cached
```

### 5. Modules Test
```bash
# In MISP: Create/edit event
# Add IP address attribute
# Hover over attribute > Click "Enrichment"
# Select "dns" module

# Expected: DNS resolution results shown
```

### 6. Correlation Test
```bash
# In MISP: Add attribute to event
# Check "Correlations" tab

# Expected: Shows correlated attributes from other events/feeds
```

## Performance Optimization

For production "ready-to-run" deployments:

### 1. Resource Allocation
```bash
# In /opt/misp/.env:
WORKERS=8                      # Set to CPU core count
PHP_MEMORY_LIMIT=2048M        # Increase for large datasets
INNODB_BUFFER_POOL_SIZE=8G    # 50-70% of available RAM
```

### 2. Feed Caching Strategy
```bash
# Cache only essential feeds initially
# Add more feeds gradually
# Monitor disk space and Redis memory
```

### 3. Background Jobs
```bash
# Ensure background jobs are enabled
MISP.background_jobs = true

# Monitor job queue
# In MISP: Administration > Jobs > View Background Jobs
```

## Troubleshooting

### Script Fails to Update Galaxies

**Symptom**: `update_galaxies()` times out or fails

**Solution**:
```bash
# Run manually with more time
docker compose exec misp-core /var/www/MISP/app/Console/cake Admin updateGalaxies --force

# Monitor progress
docker compose logs -f misp-core
```

### Feeds Not Appearing

**Symptom**: Feeds list is empty

**Solution**:
```bash
# Feeds are configured in MISP database
# They should appear automatically
# If not, check MISP version and run:
docker compose exec misp-core /var/www/MISP/app/Console/cake Server fetchFeed all
```

### Enrichment Modules Not Working

**Symptom**: Module enrichment returns errors

**Solution**:
```bash
# Check misp-modules container
docker compose ps misp-modules

# Verify module URL
# In MISP: Administration > Server Settings > Plugin Settings
# Should be: http://misp-modules

# Test connectivity
docker compose exec misp-core curl http://misp-modules/modules
```

## Additional Resources

- **Configuration Guide**: [CONFIGURATION-GUIDE.md](CONFIGURATION-GUIDE.md)
- **Advanced Features**: [ADVANCED-FEATURES.md](ADVANCED-FEATURES.md)
- **Azure Entra ID**: [AZURE-ENTRA-ID-SETUP.md](AZURE-ENTRA-ID-SETUP.md)
- **Best Practices**: [CONFIGURATION-BEST-PRACTICES.md](CONFIGURATION-BEST-PRACTICES.md)

---

**tKQB Enterprises MISP Deployment**
