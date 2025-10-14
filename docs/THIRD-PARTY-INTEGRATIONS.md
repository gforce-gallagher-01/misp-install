# MISP Third-Party Integrations Overview

This directory contains integration guides for connecting MISP with SIEMs, EDRs, SOAR platforms, sandboxes, and threat intelligence services.

## Integration Categories

### SIEM Integrations
- **[Splunk](integrations/SPLUNK.md)** - MISP42, TA-misp_es, Enterprise Security integration
- **[Microsoft Sentinel](integrations/SENTINEL.md)** - Logic Apps, Azure AD integration
- **[ELK Stack](integrations/ELK.md)** - Elasticsearch, Logstash, Kibana
- QRadar - Reference set integration
- ArcSight - SmartConnector

### EDR & XDR Integrations
- **[CrowdStrike Falcon](integrations/CROWDSTRIKE.md)** - Bidirectional threat intelligence
- **[Microsoft Defender](integrations/DEFENDER.md)** - Graph Security API
- Carbon Black - Response API integration
- SentinelOne - S1 API integration

### SOAR Platforms
- **[TheHive + Cortex](integrations/THEHIVE.md)** - Complete open-source SOC stack
- **[Palo Alto Cortex XSOAR](integrations/XSOAR.md)** - Enterprise SOAR platform
- Shuffle - Open-source SOAR automation
- IBM Resilient / QRadar SOAR

### Malware Sandboxes
- **[Cuckoo Sandbox](integrations/CUCKOO.md)** - Open-source malware analysis
- Joe Sandbox - Commercial sandbox
- VMRay - Hypervisor-based analysis
- ANY.RUN - Interactive analysis
- Hybrid Analysis - CrowdStrike Falcon Sandbox

### Threat Intelligence Platforms
- **VirusTotal** - File/URL/IP reputation (built-in module)
- **Shodan** - Internet-exposed asset discovery (built-in module)
- Recorded Future - Commercial threat intelligence
- PassiveTotal (RiskIQ) - Passive DNS and WHOIS
- GreyNoise - Internet background noise
- Have I Been Pwned - Email breach checking

### Network Security
- Palo Alto Firewalls - MineMeld integration
- Suricata / Snort - IDS/IPS rule generation
- Zeek - Network security monitoring

### Cloud Security
- AWS Security Hub - Lambda function integration
- Google Chronicle - Chronicle API integration

## Quick Start Recommendations

### Tier 1: Essential Integrations (Start Here)

1. **SIEM Integration** - **CRITICAL**
   - [Splunk MISP42](integrations/SPLUNK.md) (if using Splunk)
   - [Microsoft Sentinel](integrations/SENTINEL.md) (if using Azure)
   - [ELK Stack](integrations/ELK.md) (open-source alternative)

2. **Threat Intelligence** - **HIGH**
   - VirusTotal (built-in) - File/URL reputation
   - Shodan (built-in) - Asset discovery

3. **Malware Analysis** - **HIGH**
   - [Cuckoo Sandbox](integrations/CUCKOO.md) - Behavioral analysis

### Tier 2: Enhanced Operations

4. **Case Management** - **MEDIUM**
   - [TheHive + Cortex](integrations/THEHIVE.md) - Incident response

5. **EDR Integration** - **MEDIUM**
   - [CrowdStrike Falcon](integrations/CROWDSTRIKE.md) - Endpoint intelligence
   - [Microsoft Defender](integrations/DEFENDER.md) - Microsoft ecosystem

6. **Network Security** - **MEDIUM**
   - Suricata with MISP rules - Network blocking

### Tier 3: Advanced Automation

7. **SOAR Platform** - **LOW-MEDIUM**
   - [Cortex XSOAR](integrations/XSOAR.md) (commercial)
   - Shuffle (open-source)

8. **Additional TI Sources** - **LOW**
   - Recorded Future, PassiveTotal

## Integration Comparison Matrix

| Integration | Setup Complexity | Maintenance | Value | Open Source |
|------------|------------------|-------------|-------|-------------|
| **Splunk MISP42** | Medium | Low | ⭐⭐⭐⭐⭐ | Yes (apps) / No (Splunk) |
| **Sentinel** | Medium | Low | ⭐⭐⭐⭐⭐ | No |
| **TheHive** | Low | Low | ⭐⭐⭐⭐ | Yes |
| **CrowdStrike** | Low | Low | ⭐⭐⭐⭐⭐ | No |
| **Cuckoo** | High | Medium | ⭐⭐⭐⭐ | Yes |
| **VirusTotal** | Low | Low | ⭐⭐⭐⭐⭐ | API only |
| **ELK Stack** | Medium | Medium | ⭐⭐⭐⭐ | Yes |

## Best Practices

### 1. Start Simple
- Begin with SIEM integration (central security hub)
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

## Detailed Integration Guides

Click on the links above to access detailed setup guides for each integration. Each guide includes:
- Why integrate (benefits)
- Integration methods/options
- Step-by-step setup instructions
- Configuration examples
- Use cases and best practices
- Troubleshooting tips

## Additional Resources

- **MISP Tools**: https://www.misp-project.org/tools/
- **GitHub MISP Project**: https://github.com/MISP
- **Integration Examples**: https://github.com/MISP/MISP/tree/2.4/app/files/scripts
- **MISP Modules**: https://github.com/MISP/misp-modules

---

**Last Updated:** 2025-10-14
**Maintainer:** tKQB Enterprises
