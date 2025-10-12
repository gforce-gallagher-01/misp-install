# MISP Third-Party Integrations Guide

Complete guide to integrating MISP with SIEMs, EDRs, SOAR platforms, sandboxes, and threat intelligence services.

## Table of Contents

1. [SIEM Integrations](#siem-integrations)
2. [EDR & XDR Integrations](#edr--xdr-integrations)
3. [SOAR Platforms](#soar-platforms)
4. [Malware Sandboxes](#malware-sandboxes)
5. [Threat Intelligence Platforms](#threat-intelligence-platforms)
6. [Case Management](#case-management)
7. [Network Security](#network-security)
8. [Cloud Security](#cloud-security)
9. [Recommended Integration Stack](#recommended-integration-stack)

---

## SIEM Integrations

### 1. Splunk & Splunk Enterprise Security ⭐ **HIGHLY RECOMMENDED**

**Why This Integration**: Splunk is one of the most popular SIEM platforms, and MISP integration creates a bidirectional pipeline for automated threat intelligence enrichment.

#### Available Apps

**Option A: MISP42** (Most Popular)
- **Splunkbase**: https://splunkbase.splunk.com/app/4335
- **GitHub**: https://github.com/remg427/misp42splunk
- **Best for**: Bidirectional integration, custom workflows

**Features**:
- Pull MISP events into Splunk as custom commands
- Push Splunk alerts to MISP as events
- Create local CSV files for Enterprise Security
- Support for multiple MISP instances
- Custom search commands (`mispgetioc`, `mispgetevent`, `mispsearch`)

**Alert Actions**:
- Create MISP events from Splunk alerts
- Add sightings to MISP from Splunk detections
- Tag MISP events based on Splunk analysis

**Option B: TA-misp_es** (Official Splunk)
- **GitHub**: https://github.com/splunk/TA-misp_es
- **Best for**: Enterprise Security Threat Intelligence Framework integration

**Features**:
- Dedicated MISP-labeled CSV lookups
- Pre-built saved searches for each TI framework component
- Designed specifically for ES integration
- Complements MISP42 for complete integration

#### Setup Guide

1. **Install Both Apps**:
   ```bash
   # On Splunk Search Head
   # Install MISP42 from Splunkbase
   # Install TA-misp_es from GitHub
   ```

2. **Configure MISP42**:
   ```
   Settings > MISP42 Configuration

   MISP Instance:
   - URL: https://your-misp-instance.com
   - API Key: (from MISP user profile)
   - SSL Verify: Yes (for production)

   Test Connection: Verify successful
   ```

3. **Create Threat Intelligence Lookups**:
   ```spl
   | mispgetioc misp_instance=main last=7d
   | stats values(*) as * by value
   | outputlookup misp_indicators.csv
   ```

4. **Schedule Regular Updates**:
   ```
   Create saved search:
   - Name: "MISP Threat Intel Update"
   - Cron: 0 */6 * * * (every 6 hours)
   - Actions: Update threat intelligence lookups
   ```

5. **Configure ES Notable Event Actions**:
   ```
   Incident Review > Configure Actions
   - Add "Create MISP Event" action
   - Add "Add MISP Sighting" action
   ```

#### Use Cases

**Automatic IOC Matching**:
```spl
index=firewall
| lookup misp_indicators.csv value as dest_ip OUTPUT misp_event_id, misp_tags
| where isnotnull(misp_event_id)
| table _time, src_ip, dest_ip, misp_event_id, misp_tags
```

**Enrich Alerts with MISP Context**:
```spl
index=security_alerts
| mispgetevent misp_instance=main eventid=$event_id$
| eval threat_level=case(threat_level_id=1, "High", threat_level_id=2, "Medium", ...)
| table _time, event_name, threat_level, analysis_status, tags
```

**Push Detections to MISP**:
```spl
# As alert action on detection rule
# Automatically creates MISP event with:
# - Title from alert name
# - Attributes from detected indicators
# - Tags based on alert category
```

#### Best Practices

1. **Scheduled Updates**: Pull MISP indicators every 4-6 hours
2. **Sighting Feedback**: Push sightings back to MISP when indicators match
3. **Selective Import**: Use filters to import only relevant events (TLP, tags)
4. **Performance**: Use summary indexing for large MISP instances
5. **Data Retention**: Align lookup retention with MISP data lifecycle

---

### 2. Microsoft Sentinel ⭐ **HIGHLY RECOMMENDED**

**Why This Integration**: Native Azure integration with automated threat indicator synchronization.

#### Integration Methods

**Option A: Logic Apps (Recommended)**
- **GitHub**: https://github.com/cudeso/misp2sentinel
- **Best for**: Automated, serverless integration

**Features**:
- Real-time threat indicator sync
- Automated incident creation with MISP context
- No infrastructure to maintain
- Native Azure integration

**Option B: Python Script + Azure Functions**
- **Best for**: Custom workflows, complex transformations

**Features**:
- Full control over data transformation
- Custom enrichment logic
- Integration with other Azure services

#### Setup Guide

1. **Create Azure App Registration**:
   ```
   Azure Portal > App Registrations > New Registration
   - Name: MISP-Sentinel-Integration
   - Permissions: ThreatIndicators.ReadWrite.OwnedBy
   ```

2. **Deploy Logic App**:
   ```
   Template: misp2sentinel from GitHub
   Configuration:
   - MISP URL: https://your-misp.com
   - MISP API Key: (from MISP)
   - Tenant ID: (Azure AD)
   - Client ID: (App Registration)
   - Client Secret: (App Registration)
   ```

3. **Configure Sync Schedule**:
   ```
   Logic App Trigger:
   - Recurrence: Every 1 hour
   - Filter: TLP:CLEAR, TLP:GREEN, TLP:AMBER
   - Target Product: Azure Sentinel
   ```

4. **Verify Indicators**:
   ```
   Sentinel > Threat Intelligence > Indicators
   - Check for imported MISP indicators
   - Verify expirationDateTime
   - Confirm tags and confidence scores
   ```

#### Use Cases

- **Automated Blocking**: Push high-confidence indicators to firewall rules
- **Incident Enrichment**: Automatically attach MISP context to incidents
- **Threat Hunting**: Use MISP indicators in KQL queries
- **Sighting Feedback**: Report sightings back to MISP

---

### 3. QRadar

**Integration**: QRadar Reference Set integration
- **Method**: Custom Python script via QRadar API
- **Best for**: IBM QRadar deployments

**Features**:
- Populate reference sets with MISP indicators
- Automatic rule creation for MISP events
- Offense enrichment with MISP data

---

### 4. ArcSight

**Integration**: SmartConnector for MISP
- **Method**: CEF format export from MISP
- **Best for**: Micro Focus ArcSight ESM

---

### 5. ELK Stack (Elasticsearch, Logstash, Kibana)

**Integration**: Logstash input plugin
- **GitHub**: Various community plugins
- **Best for**: Open-source SIEM deployments

**Setup**:
```ruby
input {
  http_poller {
    urls => {
      misp => "https://misp.example.com/events/restSearch"
    }
    request_timeout => 60
    schedule => { cron => "0 */6 * * *" }
    headers => {
      Authorization => "your-api-key"
    }
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "misp-indicators-%{+YYYY.MM.dd}"
  }
}
```

---

## EDR & XDR Integrations

### 1. CrowdStrike Falcon ⭐ **HIGHLY RECOMMENDED**

**Why This Integration**: Bidirectional threat intelligence sharing between MISP and CrowdStrike's industry-leading EDR.

#### Integration Options

**Option A: CrowdStrike to MISP** (Import Intel)
- **GitHub**: https://github.com/CrowdStrike/MISP-tools
- **Best for**: Importing CrowdStrike Threat Intelligence

**Features**:
- Import adversaries (threat actors)
- Import indicators of compromise
- Import threat reports
- Automatic updates via API

**Option B: MISP to CrowdStrike** (Export to Falcon)
- **Script**: `misp2cs.py`
- **Best for**: Pushing MISP indicators to Falcon for blocking

**Features**:
- Push custom indicators to Falcon platform
- Automatic IOC watchlist updates
- Severity and confidence mapping

**Option C: CrowdStrike Expansion Module**
- **Built-in MISP module**: `crowdstrike_falcon`
- **Best for**: On-demand enrichment

**Features**:
- Query CrowdStrike Falcon Intel Indicator API
- Enrich attributes with CrowdStrike context
- View actor profiles and campaigns

#### Setup Guide

**Import CrowdStrike Intel to MISP**:

```bash
# Install MISP-tools
git clone https://github.com/CrowdStrike/MISP-tools
cd MISP-tools

# Configure API keys
cp config.json.sample config.json
nano config.json

# Add:
{
  "misp": {
    "url": "https://your-misp.com",
    "key": "your-misp-api-key"
  },
  "crowdstrike": {
    "client_id": "your-cs-client-id",
    "client_secret": "your-cs-secret"
  }
}

# Run import
python3 cs_misp_import.py --type adversaries
python3 cs_misp_import.py --type indicators
python3 cs_misp_import.py --type reports

# Schedule via cron
0 2 * * * cd /path/to/MISP-tools && python3 cs_misp_import.py --type indicators
```

**Configure Expansion Module**:

```bash
# In MISP Web UI:
Administration > Server Settings > Plugin Settings

Plugin.Enrichment_crowdstrike_falcon_enabled = true
Plugin.Enrichment_crowdstrike_falcon_api_id = your-client-id
Plugin.Enrichment_crowdstrike_falcon_api_secret = your-client-secret
```

---

### 2. Microsoft Defender for Endpoint

**Integration**: Microsoft Graph Security API
- **Method**: Same as Sentinel (targetProduct: "Microsoft Defender ATP")
- **Best for**: Microsoft-centric environments

**Features**:
- Push MISP indicators to Defender for blocking
- Automatic alert generation on matches
- Integration with Microsoft 365 Defender

---

### 3. Carbon Black

**Integration**: Carbon Black Response API
- **Method**: Custom Python script
- **Best for**: VMware Carbon Black deployments

---

### 4. SentinelOne

**Integration**: SentinelOne API integration
- **Method**: Custom integration via S1 API
- **Best for**: SentinelOne Singularity Platform

---

## SOAR Platforms

### 1. TheHive + Cortex ⭐ **HIGHLY RECOMMENDED FOR OPEN-SOURCE SOC**

**Why This Integration**: Complete open-source SOC stack with MISP as threat intel hub.

#### Architecture

```
MISP (Threat Intel) ←→ TheHive (Case Management) ←→ Cortex (Analyzers)
```

#### TheHive Integration

**Features**:
- Automatic alert creation from MISP events
- Manual import of MISP events as cases
- Export TheHive cases to MISP as events
- Observable enrichment with MISP data

**Setup**:

```yaml
# TheHive application.conf

## MISP Configuration
misp {
  servers = [
    {
      name = "Production MISP"
      url = "https://misp.example.com"
      auth {
        type = "key"
        key = "your-misp-api-key"
      }
      ## Import configuration
      purpose = "ImportAndExport"
      # Automatically import events with these tags
      tags = ["tlp:clear", "tlp:green", "to-siem"]
      # Create alerts for events
      alert {
        enabled = true
        tags = ["thehive:import"]
      }
    }
  ]
}
```

**Use Cases**:
1. **Automatic Alerting**: MISP events become TheHive alerts
2. **Case Enrichment**: Enrich observables with MISP threat intelligence
3. **Intelligence Sharing**: Export investigations back to MISP
4. **Collaborative Analysis**: Team case management with MISP context

#### Cortex Integration

**Features**:
- Analyze observables using MISP expansion modules
- Enrich data with 100+ Cortex analyzers
- Bidirectional: Cortex can query MISP, MISP can trigger Cortex

**Cortex Analyzers Using MISP**:
- `MISP_Query`: Query MISP for existing indicators
- `MISP_Warning_List`: Check against MISP warning lists

**MISP Using Cortex**:
- Configure MISP to invoke Cortex analyzers for attribute enrichment
- Automatic analysis of uploaded files
- Observable reputation checking

**Setup**:

```yaml
# Cortex application.conf

## MISP Analyzer Configuration
analyzer {
  config {
    MISP_Query {
      url = "https://misp.example.com"
      key = "your-misp-api-key"
    }
  }
}
```

#### Complete Stack Deployment

```bash
# Docker Compose for TheHive + Cortex + MISP
version: '3'
services:
  misp:
    # MISP configuration (existing)

  thehive:
    image: strangebee/thehive:latest
    depends_on:
      - elasticsearch
      - cassandra
    ports:
      - "9000:9000"

  cortex:
    image: thehiveproject/cortex:latest
    depends_on:
      - elasticsearch
    ports:
      - "9001:9001"

  elasticsearch:
    image: elasticsearch:7.17.0

  cassandra:
    image: cassandra:4
```

---

### 2. Palo Alto Cortex XSOAR

**Integration**: MISP integration pack
- **Splunkbase**: Available in XSOAR Marketplace
- **Best for**: Palo Alto security ecosystem

**Features**:
- Fetch MISP events as incidents
- Query MISP from playbooks
- Create/update MISP events
- Enrich indicators with MISP data

**Playbooks**:
- MISP Threat Intel Enrichment
- MISP Event Creation from Alert
- MISP Sighting Report

---

### 3. Shuffle (Open Source)

**Integration**: MISP app for Shuffle
- **GitHub**: https://github.com/Shuffle/Shuffle
- **Best for**: Open-source SOAR automation

**Features**:
- Trigger workflows from MISP events
- Create MISP events from any source
- Enrich data using MISP modules
- Automate sighting reports

---

### 4. IBM Resilient / QRadar SOAR

**Integration**: MISP integration app
- **Best for**: IBM security ecosystem

---

## Malware Sandboxes

### 1. Cuckoo Sandbox ⭐ **HIGHLY RECOMMENDED FOR OPEN-SOURCE**

**Integration**: Built-in MISP export module
- **Best for**: Open-source malware analysis

**Features**:
- Automatic submission of MISP attachments
- Export analysis results to MISP
- Behavior indicators as MISP attributes
- Network IOCs from PCAP analysis

**Setup**:

```bash
# Enable MISP module in Cuckoo
nano cuckoo/conf/reporting.conf

[misp]
enabled = yes
url = https://misp.example.com
apikey = your-api-key

# Automatic upload of analysis results
upload = yes
# Minimum score to upload (0-10)
min_score = 5
```

**MISP Configuration**:

```bash
# Enable Cuckoo submission module
Administration > Server Settings > Plugin Settings

Plugin.Action_cuckoo_submit_enabled = true
Plugin.Action_cuckoo_submit_url = http://cuckoo.example.com:8090
Plugin.Action_cuckoo_submit_api_key = cuckoo-api-key
```

---

### 2. Joe Sandbox

**Integration**: MISP expansion module `joe_sandbox_submit`
- **Best for**: Commercial sandbox with comprehensive analysis

**Features**:
- Submit files/URLs to Joe Sandbox
- Retrieve behavioral indicators
- Extract network communications
- Automatic MISP attribute creation

---

### 3. VMRay

**Integration**: MISP expansion module `vmray_submit`
- **Best for**: Advanced sandbox with hypervisor-level monitoring

**Features**:
- Hypervisor-based malware analysis
- Evasion technique detection
- Comprehensive behavioral analysis

---

### 4. ANY.RUN

**Integration**: MISP expansion module `anyrun_submit`
- **Best for**: Interactive malware analysis

---

### 5. Hybrid Analysis (CrowdStrike Falcon Sandbox)

**Integration**: MISP expansion module `hybrid_analysis`
- **Best for**: Cloud-based sandbox integration

---

## Threat Intelligence Platforms

### 1. VirusTotal ⭐ **HIGHLY RECOMMENDED**

**Integration**: Built-in expansion module
- **Module**: `virustotal` and `virustotal_public`
- **Best for**: File/URL/IP reputation checking

**Setup**:

```bash
Administration > Server Settings > Plugin Settings

Plugin.Enrichment_virustotal_enabled = true
Plugin.Enrichment_virustotal_apikey = your-vt-api-key
Plugin.Enrichment_virustotal_event_limit = 1000
```

**Features**:
- File hash lookups
- URL reputation
- IP/domain analysis
- Automatic attribute creation

---

### 2. Shodan ⭐ **HIGHLY RECOMMENDED**

**Integration**: Built-in expansion module
- **Module**: `shodan`
- **Best for**: Internet-exposed asset discovery

**Setup**:

```bash
Plugin.Enrichment_shodan_enabled = true
Plugin.Enrichment_shodan_apikey = your-shodan-api-key
```

---

### 3. Recorded Future

**Integration**: Expansion module `recordedfuture`
- **Best for**: Commercial threat intelligence enrichment

---

### 4. Passive Total (RiskIQ)

**Integration**: Expansion module `passivetotal`
- **Best for**: Passive DNS and WHOIS enrichment

---

### 5. GreyNoise

**Integration**: Expansion module `greynoise`
- **Best for**: Internet background noise identification

---

### 6. Have I Been Pwned

**Integration**: Expansion module `hibp`
- **Best for**: Email breach checking

---

## Case Management

### TheHive ⭐ **HIGHLY RECOMMENDED**
(See SOAR Platforms section above)

---

## Network Security

### 1. Palo Alto Firewalls

**Integration**: MineMeld + MISP
- **Best for**: Palo Alto NGFW deployments

**Features**:
- Dynamic address/URL filtering
- Automatic EDL updates from MISP
- Integration with Panorama

---

### 2. Suricata / Snort

**Integration**: MISP IDS export
- **Best for**: Network IDS/IPS deployments

**Setup**:

```bash
# Generate Suricata rules from MISP
curl -H "Authorization: your-api-key" \
  https://misp.example.com/events/nids/suricata/download \
  > misp.rules

# Include in Suricata config
rule-files:
  - misp.rules
```

---

### 3. Zeek (formerly Bro)

**Integration**: MISP Intelligence Framework
- **Best for**: Network security monitoring

---

## Cloud Security

### 1. AWS Security Hub

**Integration**: Custom Lambda function
- **Best for**: AWS-centric environments

---

### 2. Google Chronicle

**Integration**: Custom integration via Chronicle API
- **Best for**: Google Cloud security

---

## Recommended Integration Stack

### Tier 1: Essential Integrations (Start Here)

1. **SIEM**: Splunk/MISP42 **OR** Microsoft Sentinel
   - Why: Central security operations hub
   - Priority: **CRITICAL**

2. **Threat Intelligence**: VirusTotal + Shodan
   - Why: Essential enrichment sources
   - Priority: **HIGH**

3. **Malware Analysis**: Cuckoo Sandbox
   - Why: Understand malware behavior
   - Priority: **HIGH**

### Tier 2: Enhanced Security Operations

4. **Case Management**: TheHive + Cortex
   - Why: Structured incident response
   - Priority: **MEDIUM**

5. **EDR**: CrowdStrike Falcon
   - Why: Endpoint threat intelligence
   - Priority: **MEDIUM**

6. **Network Security**: Suricata with MISP rules
   - Why: Network-level blocking
   - Priority: **MEDIUM**

### Tier 3: Advanced Automation

7. **SOAR**: Cortex XSOAR **OR** Shuffle
   - Why: Automated response workflows
   - Priority: **LOW-MEDIUM**

8. **Additional TI Sources**: Recorded Future, PassiveTotal
   - Why: Enhanced enrichment
   - Priority: **LOW**

---

## Integration Best Practices

### 1. Start Simple
- Begin with SIEM integration
- Add enrichment sources (VirusTotal, Shodan)
- Gradually expand to additional integrations

### 2. Data Quality
- Filter MISP exports by TLP level
- Use tags to categorize exported data
- Set appropriate confidence levels

### 3. Bidirectional Feedback
- Push sightings back to MISP
- Report false positives
- Share detection context

### 4. Performance
- Cache frequently accessed data
- Use batch processing for large datasets
- Schedule updates during off-peak hours

### 5. Security
- Use HTTPS for all integrations
- Rotate API keys regularly
- Limit integration permissions (least privilege)

### 6. Monitoring
- Track integration health
- Alert on failed syncs
- Monitor API rate limits

---

## Integration Comparison Matrix

| Integration | Setup Complexity | Maintenance | Value | Open Source |
|------------|------------------|-------------|-------|-------------|
| **Splunk MISP42** | Medium | Low | ⭐⭐⭐⭐⭐ | Yes (apps) / No (Splunk) |
| **Sentinel** | Medium | Low | ⭐⭐⭐⭐⭐ | No |
| **TheHive** | Low | Low | ⭐⭐⭐⭐ | Yes |
| **CrowdStrike** | Low | Low | ⭐⭐⭐⭐⭐ | No |
| **Cuckoo** | High | Medium | ⭐⭐⭐⭐ | Yes |
| **VirusTotal** | Low | Low | ⭐⭐⭐⭐⭐ | API only |

---

## Next Steps

1. **Prioritize**: Choose integrations based on your security stack
2. **Test**: Start with development/test environment
3. **Automate**: Schedule regular synchronization
4. **Monitor**: Track integration health and value
5. **Expand**: Add additional integrations as needed

---

## Additional Resources

- **MISP Tools**: https://www.misp-project.org/tools/
- **GitHub MISP Project**: https://github.com/MISP
- **Integration Examples**: https://github.com/MISP/MISP/tree/2.4/app/files/scripts

---

**tKQB Enterprises MISP Deployment**
