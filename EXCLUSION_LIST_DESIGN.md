# Exclusion List Feature Design

**Version**: 5.6
**Status**: Design Phase
**Date**: 2025-10-15

## 🎯 Overview

The exclusion list feature allows users to opt-out of specific advanced features during MISP installation. By default, **ALL features are installed**. Users can selectively exclude features they don't need.

## 📋 Design Philosophy

### **Install Everything by Default**
- New installations get all advanced features automatically
- Zero configuration for full-featured deployment
- Best security posture out of the box

### **Opt-Out Model**
- Users explicitly exclude unwanted features
- Granular control (exclude individual features)
- Category-based exclusions (exclude entire groups)

### **Benefits**
- ✅ Easier for new users (everything just works)
- ✅ Better security baseline (all protections enabled)
- ✅ Reduced support burden (standard configuration)
- ✅ Flexibility for advanced users (can disable what they don't need)

## 🗂️ Feature Categories

### **Category 1: Threat Intelligence**
**Default**: ALL ENABLED

| Feature ID | Description | Scripts |
|------------|-------------|---------|
| `api-key` | API key generation for automation | Phase 11.5 |
| `threat-feeds` | Built-in threat intelligence feeds | Phase 11.7 |
| `utilities-sector` | ICS/SCADA/Utilities threat intel | `configure-misp-utilities-sector.py` |
| `nerc-cip` | NERC CIP compliance features | `configure-misp-nerc-cip.py` |
| `mitre-attack-ics` | MITRE ATT&CK for ICS | Included in utilities-sector |

### **Category 2: Automation**
**Default**: ALL ENABLED

| Feature ID | Description | Scripts |
|------------|-------------|---------|
| `automated-maintenance` | Daily/weekly maintenance cron jobs | `setup-misp-maintenance-cron.sh` |
| `automated-backups` | Scheduled backup cron job | `misp-backup-cron.py` |
| `news-feeds` | Security news population | `populate-misp-news.py` |

### **Category 3: Integrations**
**Default**: ALL ENABLED

| Feature ID | Description | Scripts |
|------------|-------------|---------|
| `splunk-integration` | Splunk correlation rules | Documentation only |
| `security-onion` | Security Onion integration | Documentation only |
| `siem-correlation` | Generic SIEM correlation rules | Documentation only |

### **Category 4: Compliance**
**Default**: ALL ENABLED

| Feature ID | Description | Scripts |
|------------|-------------|---------|
| `nerc-cip-taxonomies` | NERC CIP taxonomies | Part of nerc-cip |
| `dhs-ciip-sectors` | DHS CI sectors taxonomy | Part of utilities-sector |
| `ics-taxonomies` | ICS/OT taxonomies | Part of utilities-sector |

## 📝 Configuration Format

### **Example 1: Install Everything (Default)**
```json
{
  "server_ip": "192.168.20.54",
  "domain": "",
  "admin_email": "admin@company.com",
  "admin_org": "My Company",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "encryption_key": "",
  "environment": "production",

  "exclude_features": []
}
```

### **Example 2: Exclude Specific Features**
```json
{
  "server_ip": "192.168.20.54",
  "domain": "",
  "admin_email": "admin@company.com",
  "admin_org": "My Company",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "encryption_key": "",
  "environment": "production",

  "exclude_features": [
    "nerc-cip",
    "automated-backups",
    "splunk-integration"
  ]
}
```

### **Example 3: Exclude Entire Categories**
```json
{
  "server_ip": "192.168.20.54",
  "domain": "",
  "admin_email": "admin@company.com",
  "admin_org": "My Company",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "encryption_key": "",
  "environment": "production",

  "exclude_features": [
    "category:compliance",
    "automated-backups"
  ]
}
```

### **Example 4: Minimal Installation**
```json
{
  "server_ip": "192.168.20.54",
  "domain": "",
  "admin_email": "admin@company.com",
  "admin_org": "My Company",
  "admin_password": "SecurePass123!",
  "mysql_password": "DBPass123!",
  "gpg_passphrase": "GPGPass789!",
  "encryption_key": "",
  "environment": "production",

  "exclude_features": [
    "category:threat-intelligence",
    "category:automation",
    "category:integrations",
    "category:compliance"
  ]
}
```

## 🔧 Implementation Details

### **1. Config Class Updates** (`lib/config.py`)

```python
@dataclass
class MISPConfig:
    """MISP installation configuration"""
    server_ip: str = "192.168.20.193"
    domain: str = ""  # Auto-detected if empty
    admin_email: str = "admin@yourcompany.com"
    admin_org: str = "tKQB Enterprises"
    admin_password: str = ""
    mysql_password: str = ""
    gpg_passphrase: str = ""
    encryption_key: str = ""
    environment: str = Environment.PROD.value
    base_url: str = ""
    performance: Optional[Dict] = None
    exclude_features: List[str] = None  # NEW

    def __post_init__(self):
        # Auto-detect hostname if not specified
        if not self.domain:
            self.domain = get_system_hostname()

        if not self.base_url:
            self.base_url = f"https://{self.domain}"

        if self.performance is None:
            self.performance = asdict(PerformanceTuning())

        # NEW: Initialize exclusion list
        if self.exclude_features is None:
            self.exclude_features = []

    def is_feature_excluded(self, feature_id: str) -> bool:
        """Check if a feature should be excluded"""
        # Check direct feature exclusion
        if feature_id in self.exclude_features:
            return True

        # Check category exclusion
        feature_category = FEATURE_CATEGORIES.get(feature_id)
        if feature_category and f"category:{feature_category}" in self.exclude_features:
            return True

        return False
```

### **2. Feature Registry** (new file: `lib/features.py`)

```python
"""
Feature registry for exclusion list
"""

# Feature to category mapping
FEATURE_CATEGORIES = {
    # Threat Intelligence
    'api-key': 'threat-intelligence',
    'threat-feeds': 'threat-intelligence',
    'utilities-sector': 'threat-intelligence',
    'nerc-cip': 'threat-intelligence',
    'mitre-attack-ics': 'threat-intelligence',

    # Automation
    'automated-maintenance': 'automation',
    'automated-backups': 'automation',
    'news-feeds': 'automation',

    # Integrations
    'splunk-integration': 'integrations',
    'security-onion': 'integrations',
    'siem-correlation': 'integrations',

    # Compliance
    'nerc-cip-taxonomies': 'compliance',
    'dhs-ciip-sectors': 'compliance',
    'ics-taxonomies': 'compliance',
}

# Feature descriptions
FEATURE_DESCRIPTIONS = {
    'api-key': 'API key generation for automation scripts',
    'threat-feeds': 'Built-in threat intelligence feeds',
    'utilities-sector': 'ICS/SCADA/Utilities sector threat intelligence',
    'nerc-cip': 'NERC CIP compliance features',
    'mitre-attack-ics': 'MITRE ATT&CK for ICS framework',
    'automated-maintenance': 'Daily and weekly maintenance cron jobs',
    'automated-backups': 'Scheduled backup cron job',
    'news-feeds': 'Security news population',
    'splunk-integration': 'Splunk SIEM correlation rules',
    'security-onion': 'Security Onion integration',
    'siem-correlation': 'Generic SIEM correlation rules',
    'nerc-cip-taxonomies': 'NERC CIP taxonomies',
    'dhs-ciip-sectors': 'DHS Critical Infrastructure sectors',
    'ics-taxonomies': 'ICS/OT taxonomies',
}

def get_feature_list() -> list:
    """Get list of all available features"""
    return list(FEATURE_DESCRIPTIONS.keys())

def get_category_features(category: str) -> list:
    """Get all features in a category"""
    return [f for f, c in FEATURE_CATEGORIES.items() if c == category]
```

### **3. Phase Updates**

Each advanced feature phase needs to check exclusions:

**Phase 11.5 (API Key):**
```python
def run(self):
    """Execute API key generation"""
    if self.config.is_feature_excluded('api-key'):
        self.logger.info("⏭️  Skipping API key generation (excluded)")
        self.save_state(11.5, "API Key Skipped")
        return

    self.section_header("PHASE 11.5: API KEY GENERATION")
    # ... rest of implementation
```

**Phase 11.7 (Threat Feeds):**
```python
def run(self):
    """Execute threat feeds setup"""
    if self.config.is_feature_excluded('threat-feeds'):
        self.logger.info("⏭️  Skipping threat feeds (excluded)")
        self.save_state(11.7, "Threat Feeds Skipped")
        return

    self.section_header("PHASE 11.7: THREAT FEEDS")
    # ... rest of implementation
```

### **4. New Phases to Add**

**Phase 11.8: Utilities Sector Configuration**
```python
class Phase11_8UtilitiesSector(BasePhase):
    """Phase 11.8: Configure utilities sector threat intelligence"""

    def run(self):
        """Execute utilities sector configuration"""
        if self.config.is_feature_excluded('utilities-sector'):
            self.logger.info("⏭️  Skipping utilities sector config (excluded)")
            self.save_state(11.8, "Utilities Sector Skipped")
            return

        self.section_header("PHASE 11.8: UTILITIES SECTOR CONFIGURATION")
        # Run configure-misp-utilities-sector.py
        self.run_command(['python3', 'scripts/configure-misp-utilities-sector.py'])
        self.save_state(11.8, "Utilities Sector Configured")
```

**Phase 11.9: Automated Maintenance**
```python
class Phase11_9Maintenance(BasePhase):
    """Phase 11.9: Set up automated maintenance"""

    def run(self):
        """Execute maintenance setup"""
        if self.config.is_feature_excluded('automated-maintenance'):
            self.logger.info("⏭️  Skipping automated maintenance (excluded)")
            self.save_state(11.9, "Maintenance Skipped")
            return

        self.section_header("PHASE 11.9: AUTOMATED MAINTENANCE")
        # Run setup-misp-maintenance-cron.sh
        self.run_command(['./scripts/setup-misp-maintenance-cron.sh', '--auto'])
        self.save_state(11.9, "Maintenance Configured")
```

**Phase 11.10: News Feeds**
```python
class Phase11_10News(BasePhase):
    """Phase 11.10: Populate security news"""

    def run(self):
        """Execute news population"""
        if self.config.is_feature_excluded('news-feeds'):
            self.logger.info("⏭️  Skipping news feeds (excluded)")
            self.save_state(11.10, "News Feeds Skipped")
            return

        self.section_header("PHASE 11.10: SECURITY NEWS")
        # Run populate-misp-news.py
        self.run_command(['python3', 'scripts/populate-misp-news.py'])
        self.save_state(11.10, "News Populated")
```

## 📊 Installation Flow

### **Current Flow (v5.5):**
```
Phase 1-10: Core installation
Phase 11: MISP initialization
Phase 11.5: API key (NEW)
Phase 11.7: Threat feeds (NEW)
Phase 12: Post-install checklist
```

### **Proposed Flow (v5.6 with exclusions):**
```
Phase 1-10: Core installation (always run)
Phase 11: MISP initialization (always run)

--- ADVANCED FEATURES (check exclusions) ---
Phase 11.5: API key generation
Phase 11.7: Built-in threat feeds
Phase 11.8: Utilities sector config
Phase 11.9: Automated maintenance
Phase 11.10: Security news population

--- FINALIZATION ---
Phase 12: Post-install checklist & summary
```

## 🎯 User Experience

### **Interactive Mode:**
```
📋 ADVANCED FEATURES
==================================================

The following advanced features will be installed:
  ✓ API key generation
  ✓ Threat intelligence feeds
  ✓ Utilities sector configuration (ICS/SCADA)
  ✓ Automated maintenance (cron jobs)
  ✓ Security news population

To exclude features, press Ctrl+C and use --config with exclude_features.
Press Enter to continue...
```

### **Non-Interactive Mode:**
```bash
# Install everything (default)
python3 misp-install.py --config config.json --non-interactive

# Minimal install
python3 misp-install.py --config config-minimal.json --non-interactive
```

### **List Available Features:**
```bash
python3 misp-install.py --list-features

Available Features:
==================

THREAT INTELLIGENCE:
  - api-key: API key generation for automation scripts
  - threat-feeds: Built-in threat intelligence feeds
  - utilities-sector: ICS/SCADA/Utilities sector threat intelligence
  - nerc-cip: NERC CIP compliance features
  - mitre-attack-ics: MITRE ATT&CK for ICS framework

AUTOMATION:
  - automated-maintenance: Daily and weekly maintenance cron jobs
  - automated-backups: Scheduled backup cron job
  - news-feeds: Security news population

INTEGRATIONS:
  - splunk-integration: Splunk SIEM correlation rules
  - security-onion: Security Onion integration
  - siem-correlation: Generic SIEM correlation rules

COMPLIANCE:
  - nerc-cip-taxonomies: NERC CIP taxonomies
  - dhs-ciip-sectors: DHS Critical Infrastructure sectors
  - ics-taxonomies: ICS/OT taxonomies

To exclude features, add to config file:
  "exclude_features": ["feature-id", "category:category-name"]
```

## 📝 Documentation Updates

### **Files to Update:**
1. **README.md** - Add exclusion list section
2. **docs/INSTALLATION.md** - Document exclusion process
3. **docs/CONFIGURATION-GUIDE.md** - Add exclude_features examples
4. **CLAUDE.md** - Update for developers

### **New Documentation:**
1. **EXCLUSION_LIST_DESIGN.md** (this file)
2. **config/examples/** - Various exclusion examples

## ✅ Testing Plan

### **Test Cases:**
1. Default install (no exclusions) - all features
2. Exclude single feature
3. Exclude multiple features
4. Exclude entire category
5. Exclude multiple categories
6. Invalid feature ID (should warn, not fail)
7. Resume after interrupted install with exclusions

### **Expected Behavior:**
- Excluded features: Skipped with log message "⏭️  Skipping [feature] (excluded)"
- Installation: Continues without errors
- State: Saves as "Feature Skipped" in state file
- Summary: Shows excluded features in final report

## 🚀 Implementation Priority

### **Phase 1: Core Architecture** (Current)
- [ ] Create `lib/features.py` with feature registry
- [ ] Update `lib/config.py` with exclusion list support
- [ ] Add `is_feature_excluded()` method

### **Phase 2: Phase Updates**
- [ ] Update Phase 11.5 (API key) with exclusion check
- [ ] Update Phase 11.7 (Threat feeds) with exclusion check
- [ ] Create Phase 11.8 (Utilities sector)
- [ ] Create Phase 11.9 (Automated maintenance)
- [ ] Create Phase 11.10 (News feeds)

### **Phase 3: CLI & Documentation**
- [ ] Add `--list-features` command
- [ ] Update interactive mode with feature preview
- [ ] Create example config files
- [ ] Update all documentation

### **Phase 4: Testing**
- [ ] Test all exclusion scenarios
- [ ] Test resume capability with exclusions
- [ ] Verify state management

## 📌 Notes

- **Backwards Compatible**: Old config files without `exclude_features` will install everything
- **Fail-Safe**: Invalid feature IDs log warning but don't fail installation
- **Resumable**: Exclusions preserved across resume operations
- **Auditable**: Exclusions logged and shown in final summary

---

**Status**: Design Complete, Ready for Implementation
**Next Step**: Create `lib/features.py` and update `lib/config.py`
