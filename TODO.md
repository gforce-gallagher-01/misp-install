# MISP Installation Tool - TODO List

## High Priority

### Security Onion (SO) Integration
**Status:** Planned
**Priority:** High (threat intelligence sharing with SIEM/IDS platform)

**Description:**
Integrate MISP with Security Onion for bidirectional threat intelligence sharing. Security Onion is a free and open platform for threat hunting, enterprise security monitoring, and log management.

**Benefits:**
- Automatic IOC (Indicators of Compromise) synchronization
- Enhanced threat detection capabilities
- Unified threat intelligence across security stack
- Real-time alert enrichment with MISP data
- Automated threat hunting workflows
- Integration with Suricata, Zeek, and Elasticsearch

**Integration Points:**
1. **MISP → Security Onion**: Push IOCs to SO for detection rules
2. **Security Onion → MISP**: Import detected threats back to MISP
3. **Suricata Rule Generation**: Auto-generate Suricata rules from MISP events
4. **Elasticsearch Integration**: Index MISP data in SO's Elasticsearch
5. **TheHive Integration**: Optional case management workflow

**Implementation Tasks:**
1. Add Security Onion configuration options to installer
2. Configure MISP API endpoints for SO access
3. Set up MISP feeds for SO consumption
4. Configure Suricata rule import/export
5. Implement event synchronization service
6. Add SO API authentication (API keys or certificates)
7. Create automated IOC push script
8. Configure Elasticsearch indexing for MISP data
9. Add health monitoring for SO connection
10. Create documentation for SO operators

**Files to Create/Modify:**
- `scripts/so-sync.py` - Bidirectional sync service
- `scripts/so-push-iocs.py` - Push IOCs to Security Onion
- `scripts/so-import-detections.py` - Import detections from SO
- `config/security-onion.yaml` - SO configuration template
- `docs/SECURITY_ONION_INTEGRATION.md` - Integration guide
- `misp-install.py` - Add SO integration option during install

**Configuration Examples:**
```yaml
# config/security-onion.yaml
security_onion:
  enabled: true
  api_url: "https://securityonion.local/api"
  api_key: "${SO_API_KEY}"
  sync_interval: 300  # seconds
  push_to_suricata: true
  push_to_elasticsearch: true
  import_detections: true
  detection_threshold: "medium"  # low, medium, high, critical
  ioc_types:
    - ip-src
    - ip-dst
    - domain
    - hostname
    - url
    - md5
    - sha1
    - sha256
```

**Testing Requirements:**
- Test with Security Onion 2.4+ (latest stable)
- Verify Suricata rule generation
- Test bidirectional sync
- Validate Elasticsearch indexing
- Test alert enrichment workflow
- Performance testing with large IOC sets

**Documentation Needed:**
- Security Onion setup prerequisites
- MISP API configuration for SO
- Suricata rule customization guide
- Troubleshooting common integration issues
- Performance tuning recommendations

**Related Projects:**
- [Security Onion](https://securityonionsolutions.com/)
- [MISP-Security-Onion-Sync](https://github.com/cudeso/misp-security-onion-sync)
- [TheHive](https://thehive-project.org/)

---

### Azure Key Vault Integration
**Status:** Planned
**Priority:** High (for production Azure deployments)

**Description:**
Implement Azure Key Vault integration for secure secrets management in Azure environments, eliminating the need for PASSWORDS.txt file on disk.

**Benefits:**
- No secrets stored on VM disk
- Centralized secret management
- Audit logging for secret access
- Automatic rotation support
- RBAC integration with Azure AD
- Industry standard for Azure production workloads

**Implementation Tasks:**
1. Add Azure SDK dependencies (azure-identity, azure-keyvault-secrets)
2. Create secrets management abstraction layer
3. Add Key Vault configuration options:
   - `--use-keyvault` flag
   - `AZURE_KEYVAULT_URL` environment variable
   - Key Vault URL in config files
4. Implement Managed Identity authentication (DefaultAzureCredential)
5. Create secret retrieval functions:
   - `get_admin_password()` from Key Vault
   - `get_db_password()` from Key Vault
   - `get_gpg_passphrase()` from Key Vault
6. Modify Phase 6 (Configuration) to use Key Vault secrets
7. Add fallback to local PASSWORDS.txt for non-Azure deployments
8. Update backup script to handle Key Vault mode
9. Create Key Vault setup documentation
10. Add Key Vault testing mode

**Files to Modify:**
- `misp-install.py` (Phases 6, 9)
- `config/` - Add Key Vault configuration examples
- `scripts/backup-misp.py` - Handle Key Vault mode
- `scripts/misp-restore.py` - Handle Key Vault mode
- `docs/AZURE_KEYVAULT.md` - New documentation

**Configuration Examples:**
```yaml
# config/azure-keyvault.yaml
secrets_backend: keyvault
azure:
  keyvault_url: "https://misp-secrets-kv.vault.azure.net/"
  use_managed_identity: true
```

```json
// config/azure-keyvault.json
{
  "secrets_backend": "keyvault",
  "azure": {
    "keyvault_url": "https://misp-secrets-kv.vault.azure.net/",
    "use_managed_identity": true
  }
}
```

**Testing Requirements:**
- Test with Managed Identity
- Test with Service Principal
- Test fallback to local file
- Test secret rotation
- Test backup/restore with Key Vault

**Cost Estimate:** ~$0.03/month for typical usage

**Documentation Needed:**
- Azure Key Vault setup guide
- Managed Identity configuration
- Secret naming conventions
- Migration guide from PASSWORDS.txt to Key Vault
- Troubleshooting guide

---

## Medium Priority

### Email Notification Support
**Status:** Planned
**Priority:** Medium

Add email notifications for:
- Installation completion
- Backup completion/failures
- Update completion/failures
- Critical errors

---

### Slack/Teams Webhook Integration
**Status:** Planned
**Priority:** Medium

Add webhook support for:
- Installation status
- Backup notifications
- Update notifications

---

### GUI Installer Option
**Status:** Planned
**Priority:** Low

Web-based or TUI installer for users who prefer GUI over CLI.

---

## Completed

✅ v5.4.0 - ACL-based permission system
✅ v5.4.0 - misp-update.py implementation
✅ v5.4.0 - Complete documentation updates
✅ v5.0.0 - Python rewrite
✅ v5.0.0 - Centralized logging
✅ v5.0.0 - Backup/restore scripts
✅ v5.0.0 - Health checks

---

## Version Planning

### v5.5.0 (Next Release)
- Azure Key Vault integration
- Email notifications

### v6.0.0 (Future)
- Multi-cloud support (Azure, AWS, GCP)
- GUI installer
- Enhanced monitoring

---

**Last Updated:** 2025-10-14
**Maintainer:** Claude Code / tKQB Enterprises
