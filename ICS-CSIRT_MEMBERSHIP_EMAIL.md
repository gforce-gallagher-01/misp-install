# ICS-CSIRT.io Membership Request Email

**To**: info@ics-csirt.io
**Subject**: Membership Request - ICS/SCADA Threat Intelligence Sharing

---

## Email Template

```
Subject: Membership Request - Utilities Sector Organization

Dear ICS-CSIRT.io Team,

I am writing to request membership in the ICS-CSIRT.io community on behalf of [YOUR ORGANIZATION NAME].

ORGANIZATION DETAILS:
- Organization: [YOUR ORGANIZATION NAME]
- Sector: Utilities / Energy / [SPECIFY]
- Industry Focus: Electric Power / Water / Gas / [SPECIFY]
- Location: [YOUR COUNTRY/REGION]
- Contact Person: [YOUR NAME]
- Role/Title: [YOUR TITLE]
- Email: [YOUR EMAIL]
- Phone: [OPTIONAL]

CURRENT ICS/SCADA ENVIRONMENT:
We operate critical infrastructure with the following ICS/SCADA systems:
- [Example: Siemens SIMATIC PCS 7]
- [Example: Schneider Electric EcoStruxure]
- [Example: Rockwell Automation ControlLogix]
- [Add your systems]

MISP INSTANCE:
We currently operate a MISP instance for threat intelligence management:
- MISP Version: 2.4.x
- Instance URL: https://misp-test.lan (internal)
- Deployment: Docker-based
- Purpose: Utilities sector threat intelligence correlation and analysis

COMMITMENT TO COMMUNITY:
We understand that ICS-CSIRT.io membership requires active participation through:
- Sharing ICS/SCADA threat intelligence and indicators of compromise (IOCs)
- Contributing incident reports and lessons learned
- Collaborating on ICS security advisories
- Participating in community discussions

We are committed to contributing threat data related to:
- ICS-CERT advisories affecting our sector
- SCADA/HMI/PLC vulnerabilities and exploits
- Industrial malware and APT campaigns targeting utilities
- Network-based attacks on OT environments
- Phishing campaigns targeting energy sector personnel

EXPECTED BENEFITS:
We seek membership to:
- Access real-time ICS/SCADA threat intelligence
- Collaborate with other utilities sector organizations
- Leverage OpenCVE for vulnerability tracking
- Improve our security posture through community intelligence
- Share our threat intelligence to help protect other critical infrastructure

INTEGRATION PLAN:
Upon approval, we plan to:
- Configure bi-directional MISP synchronization
- Establish automated threat feed integration
- Contribute weekly threat intelligence reports
- Participate in community threat analysis

We appreciate your consideration of our membership request and look forward to contributing to the ICS-CSIRT.io community.

Best regards,

[YOUR NAME]
[YOUR TITLE]
[YOUR ORGANIZATION]
[YOUR EMAIL]
[YOUR PHONE]
```

---

## Customization Instructions

### Required Information
Replace the following placeholders:

1. **[YOUR ORGANIZATION NAME]** - Legal name of your organization
2. **[YOUR NAME]** - Your full name
3. **[YOUR TITLE]** - Your job title (e.g., "CISO", "Security Engineer", "Infrastructure Manager")
4. **[YOUR EMAIL]** - Your business email address
5. **[YOUR COUNTRY/REGION]** - Your geographic location
6. **[SPECIFY]** - Specific sector details (Electric Power, Water, Gas, etc.)

### Optional Enhancements

**Add specific details about**:
- Recent security incidents you can share (anonymized)
- Specific threat actors targeting your sector
- Unique ICS security research or tools you've developed
- Any published security advisories or blog posts
- Participation in other ISACs or threat sharing communities

### Tips for Approval

1. **Be specific** about your ICS/SCADA environment
2. **Demonstrate commitment** to sharing threat intelligence
3. **Highlight unique value** you can contribute
4. **Show technical capability** (mention your MISP instance)
5. **Explain how you'll contribute** to the community

---

## Follow-Up

If you don't receive a response within **5-7 business days**:

1. Send a polite follow-up email
2. Reference your original request date
3. Ask if any additional information is needed

Example follow-up:
```
Subject: Re: Membership Request - [YOUR ORGANIZATION]

Dear ICS-CSIRT.io Team,

I wanted to follow up on my membership request sent on [DATE].

Please let me know if you need any additional information to process our application.

Thank you for your time and consideration.

Best regards,
[YOUR NAME]
```

---

## After Approval

Once approved, you'll receive:

1. **MISP Instance Access**
   - URL for ICS-CSIRT.io MISP
   - Authentication credentials
   - API key for automation

2. **OpenCVE Access**
   - CVE tracking platform credentials
   - ICS-specific vulnerability monitoring

3. **Community Guidelines**
   - Information sharing protocols
   - Data classification standards
   - Contribution expectations

---

## Integration Steps

After receiving credentials:

### 1. Add ICS-CSIRT.io as MISP Sync Server

```bash
# Via MISP UI
# Navigate to: Sync Actions → List Servers → Add Server

# Or via API
curl -k -H "Authorization: $MISP_API_KEY" \
  -X POST "https://misp-test.lan/servers/add" \
  -d '{
    "url": "https://misp.ics-csirt.io",
    "authkey": "YOUR_ICS_CSIRT_API_KEY",
    "name": "ICS-CSIRT.io",
    "push": true,
    "pull": true,
    "remote_org_id": 1,
    "push_rules": "",
    "pull_rules": ""
  }'
```

### 2. Configure Sync Settings

- **Push**: Share your utilities sector threat intelligence
- **Pull**: Receive ICS/SCADA threat data from community
- **Filters**: Configure to focus on utilities-relevant threats

### 3. Set Up Automated Sync

```bash
# Add to cron for automatic synchronization
0 */6 * * * /var/www/MISP/app/Console/cake Server pull 1
0 */6 * * * /var/www/MISP/app/Console/cake Server push 1
```

---

## What to Share

### High-Value Intelligence for ICS-CSIRT.io

1. **ICS-CERT Advisories** affecting utilities
2. **SCADA/HMI vulnerabilities** discovered in your environment
3. **Industrial malware** samples (TRITON, INDUSTROYER, etc.)
4. **APT campaigns** targeting energy sector
5. **Phishing campaigns** with utilities sector themes
6. **Network reconnaissance** attempts on OT networks
7. **PLC/RTU exploitation** attempts
8. **Protocol-specific attacks** (Modbus, DNP3, IEC 104, etc.)

### Data to Contribute

- **IOCs**: IPs, domains, file hashes, email addresses
- **TTPs**: MITRE ATT&CK for ICS techniques observed
- **Vulnerabilities**: 0-days or exploited CVEs
- **Incident Reports**: Lessons learned from security events
- **YARA Rules**: Custom rules for ICS malware detection

---

## Privacy and Confidentiality

### What NOT to Share

- ❌ Specific asset locations or facility names
- ❌ Network diagrams or topology details
- ❌ Credentials or authentication details
- ❌ Personally identifiable information (PII)
- ❌ Information restricted by regulations (NDA, CUI, etc.)

### Best Practices

- ✅ Anonymize incident reports
- ✅ Use TLP (Traffic Light Protocol) markings
- ✅ Share indicators, not attribution details
- ✅ Sanitize logs and screenshots
- ✅ Follow your organization's information sharing policy

---

## Expected Timeline

- **Application Review**: 3-7 business days
- **Approval Process**: 1-2 weeks
- **Onboarding**: 1-2 days after approval
- **First Sync**: Immediate after configuration

---

## Contact Information

**ICS-CSIRT.io**
- Email: info@ics-csirt.io
- Website: https://misp.ics-csirt.io/
- Community: Industrial Control Systems focus
- Cost: Free (in exchange for threat data contribution)

---

## Additional Resources

**After joining, explore**:
- ICS-CERT Advisories: https://www.cisa.gov/ics
- MITRE ATT&CK for ICS: https://attack.mitre.org/matrices/ics/
- OpenCVE: https://www.opencve.io/
- ICS Security Community: https://ics-cert.us-cert.gov/

---

**Document Version**: 1.0
**Date**: 2025-10-17
**Maintainer**: tKQB Enterprises
