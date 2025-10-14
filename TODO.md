# MISP Installation Tool - TODO List

## High Priority

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
