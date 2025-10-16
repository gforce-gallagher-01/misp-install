# Example Configuration Files

This directory contains example configuration files demonstrating the exclusion list feature introduced in v5.6.

## 🎯 Philosophy

**By default, MISP v5.6 installs ALL advanced features.** These examples show you how to **opt-out** of features you don't need.

## 📁 Available Examples

### 1. `full-install.json` (Default Behavior)
**Use Case:** Full-featured MISP deployment with everything enabled.

**What's Included:**
- ✅ All threat intelligence features
- ✅ All automation features
- ✅ All integration documentation
- ✅ All compliance features

**Command:**
```bash
python3 misp-install.py --config config/examples/full-install.json --non-interactive
```

---

### 2. `minimal-install.json`
**Use Case:** Bare-bones MISP installation, just the core platform.

**What's Excluded:**
- ❌ All advanced features (threat intel, automation, integrations, compliance)

**What's Included:**
- ✅ Core MISP platform
- ✅ Docker containers
- ✅ Basic configuration

**Command:**
```bash
python3 misp-install.py --config config/examples/minimal-install.json --non-interactive
```

---

### 3. `no-automation.json`
**Use Case:** Organizations that prefer manual operations and don't want automated cron jobs.

**What's Excluded:**
- ❌ Automated maintenance (daily/weekly cron)
- ❌ Automated backups
- ❌ News feeds population

**What's Included:**
- ✅ All threat intelligence features
- ✅ All integration documentation
- ✅ All compliance features

**Command:**
```bash
python3 misp-install.py --config config/examples/no-automation.json --non-interactive
```

---

### 4. `custom-exclusions.json`
**Use Case:** Cherry-pick exactly which features you want. Mix of feature and category exclusions.

**What's Excluded:**
- ❌ API key generation (`api-key`)
- ❌ Automated backups (`automated-backups`)
- ❌ All compliance features (`category:compliance`)
- ❌ News feeds (`news-feeds`)

**What's Included:**
- ✅ Threat intelligence feeds
- ✅ Utilities sector configuration
- ✅ Automated maintenance (daily/weekly)
- ✅ Integration documentation

**Command:**
```bash
python3 misp-install.py --config config/examples/custom-exclusions.json --non-interactive
```

---

## 🔧 How to Customize

### Step 1: Copy an Example
```bash
cp config/examples/full-install.json config/my-config.json
```

### Step 2: List Available Features
```bash
python3 misp-install.py --list-features
```

### Step 3: Add Exclusions
Edit `config/my-config.json`:

```json
{
  "exclude_features": [
    "api-key",
    "category:automation"
  ]
}
```

### Step 4: Install
```bash
python3 misp-install.py --config config/my-config.json --non-interactive
```

## 📋 Available Features

### Threat Intelligence
- `api-key` - API key generation for automation scripts
- `threat-feeds` - Built-in threat intelligence feeds
- `utilities-sector` - ICS/SCADA/Utilities sector threat intelligence
- `nerc-cip` - NERC CIP compliance features
- `mitre-attack-ics` - MITRE ATT&CK for ICS framework

### Automation
- `automated-maintenance` - Daily and weekly maintenance cron jobs
- `automated-backups` - Scheduled backup cron job
- `news-feeds` - Security news population

### Integrations
- `splunk-integration` - Splunk SIEM correlation rules (documentation)
- `security-onion` - Security Onion integration (documentation)
- `siem-correlation` - Generic SIEM correlation rules (documentation)

### Compliance
- `nerc-cip-taxonomies` - NERC CIP taxonomies
- `dhs-ciip-sectors` - DHS Critical Infrastructure sectors
- `ics-taxonomies` - ICS/OT taxonomies

## 📚 More Information

- **Complete Design:** See `EXCLUSION_LIST_DESIGN.md`
- **Installation Guide:** See `docs/INSTALLATION.md`
- **Configuration Guide:** See `docs/CONFIGURATION-GUIDE.md`

## ⚠️ Important Notes

- **Backwards Compatible:** Old config files without `exclude_features` work fine (installs everything)
- **Invalid Feature IDs:** Will log a warning but won't fail installation
- **Category Format:** Use `"category:category-name"` (e.g., `"category:automation"`)
- **Default Behavior:** Empty list `[]` installs everything

## 🎯 Common Use Cases

### Use Case 1: Energy Utility
**Wants:** Full threat intelligence, automation, NERC CIP compliance
**Doesn't Want:** Generic SIEM docs (they use Splunk specifically)

```json
{
  "exclude_features": ["security-onion", "siem-correlation"]
}
```

### Use Case 2: Development Environment
**Wants:** Core MISP only for testing
**Doesn't Want:** Any production features

```json
{
  "exclude_features": [
    "category:threat-intelligence",
    "category:automation",
    "category:compliance"
  ]
}
```

### Use Case 3: Locked-Down Environment
**Wants:** Threat intelligence only
**Doesn't Want:** Automated jobs that run without approval

```json
{
  "exclude_features": ["category:automation"]
}
```

### Use Case 4: Custom Setup
**Wants:** Manual control over everything
**Doesn't Want:** API key (will generate manually)

```json
{
  "exclude_features": ["api-key", "category:automation"]
}
```

---

**Need Help?** See the main README.md or EXCLUSION_LIST_DESIGN.md for complete documentation.
