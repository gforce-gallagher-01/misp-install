# MISP Advanced Features Guide

This guide covers advanced MISP features including workflows, feeds, modules, sync servers, and automation capabilities.

## Table of Contents

1. [MISP Workflows](#misp-workflows)
2. [Threat Intelligence Feeds](#threat-intelligence-feeds)
3. [MISP Modules](#misp-modules)
4. [Sync Servers & Sharing](#sync-servers--sharing)
5. [MISP-Guard (Optional)](#misp-guard-optional)
6. [Custom Integrations](#custom-integrations)
7. [Advanced Build Configuration](#advanced-build-configuration)

---

## MISP Workflows

### Overview

MISP workflows provide automatic, customizable data pipelines for data qualification, automated analysis, modification, and publication control.

### Key Features

- **Automated Data Processing**: Automatically enrich, tag, or modify events based on rules
- **Workflow Blueprints**: Pre-built workflows for common use cases
- **Event-driven Actions**: Trigger actions based on event creation, modification, or attributes
- **Conditional Logic**: Complex if/then logic with tag-based conditions
- **Integration with Modules**: Call enrichment modules automatically

### Common Workflow Use Cases

1. **Auto-tagging**: Automatically apply tags based on attribute types or values
2. **Data Enrichment**: Automatically query threat intelligence feeds
3. **Quality Control**: Block publication of events that don't meet criteria
4. **Distribution Control**: Automatically set TLP levels based on content
5. **Notification**: Send alerts for specific IoC types

### Workflow Blueprints

MISP includes pre-built workflow blueprints available at:
https://github.com/MISP/misp-workflow-blueprints

Example blueprints:
- **TLP Management**: Auto-convert `tlp:white` to `tlp:clear`
- **PAP/TLP Blocking**: Block actions for RED classified data
- **Hash Deduplication**: Disable `to_ids` flag for known-good hashes
- **BGP Ranking**: Set tags based on IP maliciousness scores

### Configuring Workflows

1. **Access Workflows**:
   - Log in as admin
   - Navigate to **Administration** > **Workflows**

2. **Import Blueprint**:
   - Click **Import**
   - Select blueprint JSON file
   - Configure trigger conditions

3. **Create Custom Workflow**:
   - Click **Add Workflow**
   - Choose trigger (before/after save, publish, etc.)
   - Add workflow modules
   - Configure conditions and actions

### Workflow Configuration Tags

Use these tags on events to control workflow behavior:

```
misp-workflow:mutability="allowed"       # Allow workflows to modify data
misp-workflow:mutability="forbidden"     # Prevent workflows from modifying
misp-workflow:state="enabled"            # Enable workflows for this event
misp-workflow:state="disabled"           # Disable workflows for this event
```

### Best Practices

- Start with simple workflows and test thoroughly
- Use blueprints as templates for custom workflows
- Document workflow purpose and triggers
- Monitor workflow execution in logs
- Use workflow debugging feature before production deployment

---

## Threat Intelligence Feeds

### Overview

MISP feeds allow automatic import of threat intelligence from remote or local sources without prior agreements. MISP includes 50+ pre-configured OSINT feeds.

### Feed Types

1. **MISP Format Feeds**: Native MISP JSON format (fastest, most efficient)
2. **CSV Feeds**: Comma-separated values with configurable fields
3. **Free-text Feeds**: Unstructured text with IOC extraction
4. **Custom Formats**: Extensible with custom parsers

### Configuring Feeds

#### 1. Enable Default Feeds

```bash
# Log in to MISP as admin
# Navigate to: Sync Actions > List Feeds
# Enable desired feeds (recommended starters):
#   - CIRCL OSINT Feed
#   - Abuse.ch Feodo Tracker
#   - Abuse.ch URLhaus
#   - Abuse.ch ThreatFox
```

#### 2. Configure Feed Caching

```bash
# In MISP web UI:
# Administration > Server Settings > Plugin Settings

# Cache Configuration:
MISP.background_jobs = true
MISP.cached_attachments = true

# Feed Pull Schedule (cron format):
# Add to system crontab or use MISP scheduler
0 */6 * * * /var/www/MISP/app/Console/cake Server fetchFeed all
```

#### 3. Feed Correlation

When feeds are cached, MISP automatically correlates feed indicators with event data:
- Matching indicators show as "Feed hits" in event view
- Appears on attribute rows (not in correlation graph)
- Helps identify threat actor overlap
- Provides context without importing all data

### Feed Management Best Practices

1. **Selective Enablement**: Don't enable all feeds - choose relevant sources
2. **Regular Caching**: Schedule feed updates every 6-12 hours
3. **Filter Rules**: Apply filters to reduce noise (e.g., TLP, tags, types)
4. **Distribution Levels**: Set appropriate sharing levels for feed data
5. **Performance**: Monitor disk space and Redis memory usage
6. **Feed Overlap**: Analyze feed overlap to understand source diversity

### Adding Custom Feeds

```bash
# In MISP Web UI:
# Sync Actions > List Feeds > Add Feed

# Required Fields:
Name: Custom Feed Name
Provider: Organization providing feed
URL: https://example.com/feed/manifest.json  # for MISP format
Input Source: Network  # or Local
Source Format: MISP Feed  # or CSV, Freetext
Enabled: Yes
Caching: Yes  # Recommended

# Optional Fields:
Distribution: Your Organization Only
Default Tag: custom-feed
Filter Rules: {"type": ["ip-src", "ip-dst", "domain"]}
```

### Popular Public Feeds

Pre-configured in MISP:
- **Abuse.ch**: Malware, botnet, phishing feeds
- **CIRCL**: OSINT threat intelligence
- **Botvrij.eu**: Dutch DDoS, malware feeds
- **EmergingThreats**: IDS/IPS rules and IOCs
- **OpenPhish**: Phishing URLs
- **Ransomware Tracker**: Ransomware IOCs

---

## MISP Modules

### Overview

MISP modules extend MISP with external services for enrichment, import, export, and actions. Over 200 modules are available.

### Module Types

1. **Expansion Modules**: Enrich existing attributes with external data
   - **Hover Type**: Show enriched data on hover
   - **Expansion Type**: Add enriched data as proposals

2. **Import Modules**: Import data from various formats
   - Email imports (EML files)
   - Threat intelligence platform imports
   - Custom data formats

3. **Export Modules**: Export MISP data to external formats
   - STIX 1/2
   - PDF reports
   - Custom formats

4. **Action Modules**: Workflow actions
   - Send to SIEM
   - Submit to sandboxes
   - Custom integrations

### Popular Expansion Modules

#### DNS & Network
- `dns`: DNS resolution for IPs/domains
- `shodan`: Shodan API lookups
- `greynoise`: GreyNoise IP reputation
- `ipasn`: AS number lookup
- `geoip`: Geolocation data

#### Threat Intelligence
- `virustotal`: VirusTotal file/URL/IP lookups
- `passivetotal`: RiskIQ PassiveTotal enrichment
- `recorded_future`: Recorded Future threat intel
- `threatminer`: ThreatMiner OSINT
- `crowdstrike`: CrowdStrike Falcon Intel

#### Malware Analysis
- `vmray_submit`: Submit files to VMRay sandbox
- `joe_sandbox`: Joe Sandbox analysis
- `cuckoo_submit`: Cuckoo sandbox submission
- `assemblyline_submit`: CCCS AssemblyLine submission

#### Utilities
- `yara_query`: YARA rule matching
- `hashlookup`: CIRCL hash lookup
- `cve`: CVE information enrichment
- `sigma_queries`: Sigma rule generation

### Configuring Modules

#### 1. Verify Modules Container is Running

```bash
cd /opt/misp
docker compose ps misp-modules

# Should show: Up and healthy
```

#### 2. Configure Module Settings

```bash
# In MISP Web UI:
# Administration > Server Settings > Plugin Settings

# Enable modules:
Plugin.Enrichment_services_enable = true
Plugin.Import_services_enable = true
Plugin.Export_services_enable = true

# Module FQDN (default for Docker):
Plugin.Enrichment_services_url = http://misp-modules
Plugin.Import_services_url = http://misp-modules
Plugin.Export_services_url = http://misp-modules
```

#### 3. Configure API Keys

Many modules require API keys:

```bash
# In MISP Web UI:
# Administration > Server Settings > Plugin Settings

# Example: VirusTotal
Plugin.Enrichment_virustotal_apikey = your-vt-api-key
Plugin.Enrichment_virustotal_enabled = true

# Example: Shodan
Plugin.Enrichment_shodan_apikey = your-shodan-api-key
Plugin.Enrichment_shodan_enabled = true
```

#### 4. Test Module

```bash
# In an event, hover over an attribute
# Click "Enrichment" button
# Select a module (e.g., "dns", "virustotal")
# View results and optionally add to event
```

### Environment Variables for Modules

Configure in `/opt/misp/.env`:

```bash
# MISP Modules FQDN (for custom deployments)
# MISP_MODULES_FQDN=misp-modules:6666

# Module Commit (for specific version)
# MODULES_COMMIT=abc123def456

# Slim modules (minimal footprint)
# MODULES_FLAVOR=slim
```

### Creating Custom Modules

See:
- Documentation: https://misp.github.io/misp-modules/
- Tutorial: https://medium.com/ouspg/quick-guide-to-writing-misp-modules-c53c7bb00914
- Repository: https://github.com/MISP/misp-modules

Basic structure:
```python
def handler(q=False):
    # Process input
    request = json.loads(q)
    attribute = request['attribute']

    # Enrich data
    results = enrich_attribute(attribute)

    # Return results
    return {'results': results}

def introspection():
    return {
        'input': ['ip-dst', 'domain'],
        'output': ['text']
    }

def version():
    return {'version': '1.0'}
```

---

## Sync Servers & Sharing

### Overview

MISP supports automated synchronization with other MISP instances for threat intelligence sharing.

### Sync Server Configuration

Configure in `/opt/misp/.env`:

```bash
# Number of sync servers
SYNCSERVERS=2

# Server 1 Configuration
SYNCSERVERS_1_NAME=Partner MISP
SYNCSERVERS_1_URL=https://partner-misp.example.com
SYNCSERVERS_1_UUID=organization-uuid-from-partner
SYNCSERVERS_1_KEY=authentication-key-from-partner
SYNCSERVERS_1_PULL_RULES={"tags":["tlp:white","tlp:green","tlp:clear"]}

# Server 2 Configuration (optional)
SYNCSERVERS_2_NAME=Community MISP
SYNCSERVERS_2_URL=https://community-misp.example.com
SYNCSERVERS_2_UUID=community-org-uuid
SYNCSERVERS_2_KEY=community-auth-key
SYNCSERVERS_2_PULL_RULES={"tags":["tlp:clear"]}
```

### Sync Server Setup (Manual via UI)

1. **Generate API Key**:
   - Log in to your MISP
   - Go to **Administration** > **List Users** > Your User
   - Click **Auth Keys** > **Add authentication key**
   - Copy the generated key

2. **Exchange Organization UUIDs**:
   - **Administration** > **List Organisations** > Your Org
   - Share your Organization UUID with partner

3. **Add Sync Server**:
   - **Sync Actions** > **List Servers** > **New Server**
   - Fill in partner details:
     - Name, URL, Remote Organization UUID
     - Authentication Key (from partner)
   - Configure pull/push settings
   - Set pull rules (tag filters, types, etc.)

4. **Test Connection**:
   - Click **Test Connection** on server entry
   - Verify successful connection

### Distribution Levels

Control data sharing with distribution settings:

- **Your Organisation Only**: Never shared externally
- **This Community Only**: Shared with connected servers you manage
- **Connected Communities**: Shared with all directly connected servers
- **All Communities**: Shared with all servers (including indirect connections)
- **Sharing Groups**: Shared only with defined sharing group members

### Automated Sync Schedule

Configure automatic pull/push:

```bash
# In .env file:
CRON_USER_ID=1

# Pull from all sync servers at 2 AM daily
CRON_PULLALL=0 2 * * *

# Push to all sync servers at 3 AM daily
CRON_PUSHALL=0 3 * * *
```

### Sharing Groups

Create sharing groups for selective sharing:

1. **Create Sharing Group**:
   - **Sync Actions** > **List Sharing Groups** > **Add Sharing Group**
   - Name: Sector-Specific Intel Group
   - Add organizations (local and remote)

2. **Use Sharing Group**:
   - When creating/editing events
   - Set Distribution to "Sharing Group"
   - Select the sharing group

3. **Best Practices**:
   - Create sector-specific groups (finance, healthcare, etc.)
   - Create trust-level groups (TLP-based)
   - Document group purpose and membership criteria

---

## MISP-Guard (Optional)

### Overview

MISP-Guard is an optional traffic filtering and monitoring component that acts as a proxy between MISP and external systems.

### When to Use MISP-Guard

- **Traffic Inspection**: Monitor API calls and data transfers
- **Rate Limiting**: Protect MISP from excessive API requests
- **Access Control**: Additional layer of authentication
- **Audit Logging**: Detailed logs of all API interactions
- **Development/Testing**: Intercept and modify traffic for debugging

### Enabling MISP-Guard

#### 1. Configure Environment Variables

Add to `/opt/misp/.env`:

```bash
# Enable MISP-Guard profile
# Note: Must be set before docker compose up
COMPOSE_PROFILES=misp-guard

# Guard Configuration
GUARD_PORT=8888
GUARD_ARGS=--set block_global=false --ssl-insecure

# Advanced: Specific version
# GUARD_COMMIT=abc123def456
# GUARD_RUNNING_TAG=v1.2
```

#### 2. Create Guard Configuration

Create `/opt/misp/guard/config.json`:

```json
{
  "mode": "transparent",
  "listen_port": 8888,
  "upstream": "https://misp-core:443",
  "log_level": "info",
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 60
  },
  "filtering": {
    "block_patterns": [],
    "allow_patterns": ["*"]
  }
}
```

#### 3. Start with Guard Profile

```bash
cd /opt/misp
docker compose --profile misp-guard up -d
```

#### 4. Access via Guard

```bash
# Access MISP through Guard proxy
https://your-misp-domain:8888

# Direct access (bypasses guard)
https://your-misp-domain
```

### Guard Use Cases

1. **API Monitoring**: Log all API requests for auditing
2. **Development**: Modify requests/responses for testing
3. **Rate Limiting**: Protect from API abuse
4. **SSL Inspection**: Analyze encrypted traffic

---

## Custom Integrations

### Custom Python Scripts Location

Place custom scripts in these directories:

```bash
# Custom MISP modules
/opt/misp/custom/action_mod/      # Workflow action modules
/opt/misp/custom/expansion/       # Expansion modules
/opt/misp/custom/export_mod/      # Export modules
/opt/misp/custom/import_mod/      # Import modules
```

These directories are mounted as volumes and loaded automatically.

### Custom Initialization Script

Create `/opt/misp/files/customize_misp.sh` for custom startup tasks:

```bash
#!/bin/bash
# Custom MISP initialization
# This script runs when misp-core container starts

# Example: Install custom CA certificate
# cp /custom/rootca.crt /usr/local/share/ca-certificates/
# update-ca-certificates

# Example: Configure custom settings
# /var/www/MISP/app/Console/cake Admin setSetting "MISP.custom_setting" "value"

# Example: Import custom taxonomies
# /var/www/MISP/app/Console/cake Admin updateTaxonomies
```

Enable custom script in `/opt/misp/.env`:

```bash
# Uncomment and set path
# CUSTOM_PATH=/opt/misp/files
```

Then mount in `docker-compose.yml` (already configured):

```yaml
volumes:
  - "${CUSTOM_PATH}/:/custom/:Z"
```

### Custom Root CA Certificates

For corporate environments with internal CAs:

```bash
# Place certificate in MISP directory
cp your-root-ca.crt /opt/misp/ssl/rootca.pem

# Mount in docker-compose.yml (uncomment existing line)
volumes:
  - "./ssl/rootca.pem:/usr/local/share/ca-certificates/rootca.crt:Z"

# Restart containers
cd /opt/misp
docker compose down
docker compose up -d
```

---

## Advanced Build Configuration

### Build Variables

For custom MISP builds, configure these in `.env`:

```bash
##
# Advanced Build Configuration
# Only modify if building custom MISP images
##

# Use specific git commits instead of tags
# CORE_COMMIT=abc123def456  # Takes precedence over CORE_TAG
# MODULES_COMMIT=xyz789ghi012  # Takes precedence over MODULES_TAG
# GUARD_COMMIT=qrs345tuv678  # Takes precedence over GUARD_TAG

# Build flavors
# CORE_FLAVOR=full  # Options: full, slim (default: full)
# MODULES_FLAVOR=full  # Options: full, slim (default: full)

# Use specific running tags (for pre-built images)
# CORE_RUNNING_TAG=v2.5.22
# MODULES_RUNNING_TAG=v3.0.2
# GUARD_RUNNING_TAG=v1.2

# Python package versions (advanced)
# PYPI_REDIS_VERSION=5.0.0
# PYPI_LIEF_VERSION=0.13.0
# PYPI_PYDEEP2_VERSION=0.5.1
# PYPI_PYTHON_MAGIC_VERSION=0.4.27
# PYPI_MISP_LIB_STIX2_VERSION=3.0.1
# PYPI_MAEC_VERSION=4.1.0.17
# PYPI_MIXBOX_VERSION=1.0.5
# PYPI_CYBOX_VERSION=2.1.0.21
# PYPI_PYMISP_VERSION=2.4.170
# PYPI_MISP_STIX_VERSION=2.4.170
```

### Building Custom Images

```bash
# Build all images
cd /opt/misp
docker compose build

# Build specific service
docker compose build misp-core

# Build with no cache
docker compose build --no-cache

# Build and start
docker compose up -d --build
```

### Slim vs Full Images

**Full images** (default):
- All modules and dependencies included
- Larger image size (~2GB)
- Suitable for production

**Slim images**:
- Minimal dependencies
- Smaller image size (~500MB)
- Faster startup
- May require additional module installation

```bash
# Use slim images
CORE_FLAVOR=slim
MODULES_FLAVOR=slim
```

---

## Additional Resources

### Official Documentation
- MISP Book: https://www.circl.lu/doc/misp/
- MISP Training Materials: https://github.com/MISP/misp-training
- MISP Modules: https://misp.github.io/misp-modules/
- Workflow Blueprints: https://github.com/MISP/misp-workflow-blueprints

### Community Resources
- MISP Project: https://www.misp-project.org/
- GitHub: https://github.com/MISP/MISP
- Gitter Chat: https://gitter.im/MISP/MISP
- Twitter: @MISPProject

### Training Videos
- YouTube: https://www.youtube.com/c/MISPProject
- CIRCL: https://www.circl.lu/services/misp-training-materials/

---

**tKQB Enterprises MISP Deployment**
