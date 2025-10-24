# Widget Reset Guide - Complete Removal and Reinstallation

**Date**: 2025-10-17
**Purpose**: Remove all existing widgets and reinstall with corrected timeframe formats
**Status**: Ready for execution

---

## Quick Start

```bash
# Run the complete widget reset
cd /home/gallagher/misp-install/misp-install
python3 scripts/reset-all-widgets.py

# Or do a dry run first (recommended)
python3 scripts/reset-all-widgets.py --dry-run
```

---

## What This Script Does

The `reset-all-widgets.py` script performs a complete widget reset in 6 steps:

### Step 1: Check Prerequisites
- Verifies MISP container is running
- Ensures all required tools are available

### Step 2: Remove All Widgets
- Lists all widget files in `/var/www/MISP/app/Lib/Dashboard/Custom/`
- Removes all `.php` widget files
- Shows progress for each removal

### Step 3: Clear PHP Cache
- Removes PHP OpCache to prevent stale widget loading
- Clears `/var/www/MISP/app/tmp/cache/*`

### Step 4: Reinstall All Widgets
- Installs base widget files (DRY patterns)
- Installs 5 widget sets (25 total widgets):
  1. **utilities-sector** (6 widgets)
  2. **ics-ot-dashboard** (6 widgets)
  3. **threat-actor-dashboard** (4 widgets) ← Fixed timeframe formats
  4. **utilities-feed-dashboard** (5 widgets)
  5. **organizational-dashboard** (4 widgets)

### Step 5: Apply Critical Fixes
- Removes abstract base classes (prevents instantiation errors)
- Applies wildcard fixes (`ics:` → `ics:%`)
- Verifies timeframe formats are correct (`365d` not `1y`)

### Step 6: Restart MISP
- Restarts `misp-misp-core-1` container
- Waits for container to be ready
- Verifies widgets are installed

---

## Usage Examples

### Example 1: Dry Run (Recommended First)
```bash
cd /home/gallagher/misp-install/misp-install
python3 scripts/reset-all-widgets.py --dry-run

# Output shows what would be done without making changes
```

### Example 2: Full Reset
```bash
cd /home/gallagher/misp-install/misp-install
python3 scripts/reset-all-widgets.py

# Interactive - press ENTER to confirm
```

### Example 3: With Custom API Key
```bash
python3 scripts/reset-all-widgets.py --api-key YOUR_API_KEY_HERE
```

---

## Expected Output

```
================================================================================
MISP WIDGET RESET TOOL
================================================================================
This script will:
  1. Remove all existing custom widgets
  2. Clear PHP cache
  3. Reinstall all 25 widgets with corrected timeframe formats
  4. Remove abstract base classes
  5. Apply wildcard fixes
  6. Restart MISP

Press ENTER to continue or Ctrl+C to cancel...

================================================================================
CHECKING PREREQUISITES
================================================================================
✓ MISP container is running

================================================================================
REMOVING ALL CUSTOM WIDGETS
================================================================================
Found 25 widget files to remove:
  - APTGroupsUtilitiesWidget.php
  - NationStateAttributionWidget.php
  - TTPsUtilitiesWidget.php
  - HistoricalIncidentsWidget.php
  ... (21 more)

Removing widgets...
✓ Removed APTGroupsUtilitiesWidget.php
✓ Removed NationStateAttributionWidget.php
✓ Removed TTPsUtilitiesWidget.php
✓ Removed HistoricalIncidentsWidget.php
... (21 more)

Summary:
  ✓ Removed: 25
  ✗ Failed: 0

================================================================================
CLEARING PHP CACHE
================================================================================
✓ PHP cache cleared

================================================================================
REINSTALLING WIDGETS
================================================================================

[Step 1/6] Installing base widget files...
✓ Base widget files installed

[Step 2/6] Installing utilities-sector widgets...
✓ utilities-sector widgets installed

[Step 3/6] Installing ics-ot-dashboard widgets...
✓ ics-ot-dashboard widgets installed

[Step 4/6] Installing threat-actor-dashboard widgets...
✓ threat-actor-dashboard widgets installed

[Step 5/6] Installing utilities-feed-dashboard widgets...
✓ utilities-feed-dashboard widgets installed

[Step 6/6] Installing organizational-dashboard widgets...
✓ organizational-dashboard widgets installed

✓ All 25 widgets reinstalled successfully

================================================================================
REMOVING ABSTRACT BASE CLASSES
================================================================================
✓ Removed: BaseUtilitiesWidget.php
✓ Removed 1 abstract base class(es)

================================================================================
APPLYING WIDGET FIXES
================================================================================

Applying wildcard fixes (ics: → ics:%)...
✓ Applied wildcard fixes to 18/18 widgets

Verifying timeframe formats...
✓ APTGroupsUtilitiesWidget.php: Correct format (day-based)
✓ NationStateAttributionWidget.php: Correct format (day-based)
✓ TTPsUtilitiesWidget.php: Correct format (day-based)
✓ HistoricalIncidentsWidget.php: Correct format (day-based)

✓ All threat actor widgets have correct timeframe format

================================================================================
RESTARTING MISP
================================================================================
Restarting MISP core container...
✓ MISP container restarted

Waiting for MISP to be ready...
✓ MISP is ready (after 8 seconds)

================================================================================
VERIFYING WIDGET INSTALLATION
================================================================================
Total widgets installed: 25
✓ All 25 widgets installed

Verifying Threat Actor Dashboard widgets:
  ✓ APTGroupsUtilitiesWidget.php
  ✓ NationStateAttributionWidget.php
  ✓ TTPsUtilitiesWidget.php
  ✓ HistoricalIncidentsWidget.php

================================================================================
WIDGET RESET COMPLETE
================================================================================
✓ All widgets removed and reinstalled with corrected configuration

Next Steps:
  1. Access MISP dashboard: https://<your-misp-domain>
  2. Click 'Add Widget' button
  3. Add the 4 Threat Actor widgets:
     - APT Groups Targeting Utilities
     - Nation-State Attribution
     - TTPs Targeting Utilities
     - Historical ICS Security Incidents
  4. Verify widgets display data (not 'No data')

Configuration format:
  {"timeframe": "365d", "limit": "15"}

Timeframe options:
  - 7d   (last 7 days)
  - 30d  (last 30 days)
  - 90d  (last 90 days)
  - 365d (last year)
  - 3650d (last 10 years)
  - all  (all time)

Troubleshooting:
  - If widgets still show 'No data', verify events were populated:
    python3 scripts/populate-utilities-events.py
  - Check MISP logs:
    cd /opt/misp && sudo docker compose logs -f misp-core
```

---

## Post-Reset Steps (Manual in MISP UI)

After running the reset script, you need to add widgets to your dashboard manually:

### 1. Access MISP Dashboard
Navigate to: `https://<your-misp-domain>/dashboards`

### 2. Add Threat Actor Widgets

For each of the 4 widgets, click **"Add Widget"** and configure:

#### Widget 1: APT Groups Targeting Utilities
```json
{
    "timeframe": "365d",
    "limit": "15"
}
```

#### Widget 2: Nation-State Attribution
```json
{
    "timeframe": "365d",
    "limit": "10"
}
```

#### Widget 3: TTPs Targeting Utilities
```json
{
    "timeframe": "365d",
    "limit": "15"
}
```

#### Widget 4: Historical ICS Security Incidents
```json
{
    "timeframe": "3650d",
    "limit": "15",
    "sector_filter": "utilities"
}
```

### 3. Verify Data Display

Each widget should now display data:

- **APT Groups**: Bar chart with Dragonfly, Sandworm, APT33, etc.
- **Nation-State Attribution**: Bar chart with Russia, China, Iran, etc.
- **TTPs**: Bar chart with Spearphishing, HMI Interaction, etc.
- **Historical Incidents**: List with Ukraine Blackout, Stuxnet, TRITON, etc.

**If "No data" appears:**
1. Check events were populated: `python3 scripts/populate-utilities-events.py`
2. Verify timeframe format is correct (day-based: `365d` not `1y`)
3. Check MISP logs for errors

---

## Troubleshooting

### Issue: "MISP container is not running"

**Solution**:
```bash
cd /opt/misp
sudo docker compose up -d
```

Wait 1-2 minutes for MISP to start, then run reset script again.

### Issue: "Failed to remove widgets"

**Possible Causes**:
- Insufficient permissions (need sudo)
- MISP container not running
- Widgets directory doesn't exist

**Solution**:
```bash
# Check container status
sudo docker ps | grep misp

# Verify widgets directory exists
sudo docker exec misp-misp-core-1 ls -la /var/www/MISP/app/Lib/Dashboard/Custom/

# Try running with sudo
sudo python3 scripts/reset-all-widgets.py
```

### Issue: "Widget installation failed"

**Possible Causes**:
- Installation scripts not executable
- Missing widget files

**Solution**:
```bash
# Make all install scripts executable
cd /home/gallagher/misp-install/misp-install
find widgets -name "*.sh" -exec chmod +x {} \;

# Verify widget files exist
ls -la widgets/threat-actor-dashboard/*.php

# Run reset script again
python3 scripts/reset-all-widgets.py
```

### Issue: Widgets still show "No data" after reset

**Checklist**:
1. ✅ Events populated (run `python3 scripts/populate-utilities-events.py`)
2. ✅ Timeframe format correct (`365d` not `1y`)
3. ✅ Wildcard tags used (`ics:%` not `ics:`)
4. ✅ MISP restarted after reset
5. ✅ Widget removed and re-added in UI

**Debug Steps**:
```bash
# Check widget file has correct timeframe
sudo docker exec misp-misp-core-1 grep -A 5 "placeholder" \
  /var/www/MISP/app/Lib/Dashboard/Custom/APTGroupsUtilitiesWidget.php

# Should show: "timeframe": "365d"

# Check events exist with correct tags
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://your-misp-domain/events/restSearch" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"returnFormat": "json", "published": 1, "tags": ["misp-galaxy:threat-actor=%"], "limit": 5}'

# Should return events
```

### Issue: "Cannot instantiate abstract class" error

This should be fixed by the script, but if it persists:

```bash
# Manually remove abstract classes
sudo docker exec misp-misp-core-1 \
  rm -f /var/www/MISP/app/Lib/Dashboard/Custom/BaseUtilitiesWidget.php

sudo docker exec misp-misp-core-1 \
  rm -f /var/www/MISP/app/Lib/Dashboard/Custom/AbstractWidget.php

# Restart MISP
sudo docker restart misp-misp-core-1
```

---

## Script Features

### Safety Features
- **Dry run mode**: Test without making changes
- **Interactive confirmation**: Requires ENTER key press before executing
- **Error handling**: Stops on critical errors
- **Rollback-friendly**: All widgets can be reinstalled anytime

### Progress Tracking
- Detailed step-by-step output
- Success/failure counters
- Color-coded messages (green=success, red=error, yellow=warning)
- Verification of installation at end

### Comprehensive Fixes
- Removes old widgets completely
- Clears PHP cache
- Installs corrected widget files
- Removes abstract classes
- Applies wildcard fixes
- Verifies timeframe formats
- Restarts MISP automatically

---

## Integration with Installation

This script can be integrated into Phase 11.11 for fresh installations:

```python
# In phases/phase_11_11_utilities_dashboards.py

def run(self):
    """Execute utilities dashboards installation and configuration"""

    # Run widget reset for clean installation
    reset_script = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'scripts',
        'reset-all-widgets.py'
    )

    subprocess.run(['python3', reset_script], check=True)

    self.save_state(11.11, "Utilities Dashboards Configured")
```

---

## Files Modified/Created

### Created:
- `scripts/reset-all-widgets.py` - Main reset script
- `WIDGET_RESET_GUIDE.md` - This documentation

### Referenced (no changes):
- `phases/phase_11_11_utilities_dashboards.py` - Widget installation phase
- `widgets/threat-actor-dashboard/*.php` - Widget files (corrected timeframe formats)
- `lib/colors.py` - Color output utilities
- `lib/misp_api_helpers.py` - API helper functions
- `lib/docker_helpers.py` - Docker helper functions

---

## Summary

✅ **Created**: Comprehensive widget reset script (`reset-all-widgets.py`)
✅ **Features**: Dry run, error handling, progress tracking, verification
✅ **Fixes Applied**: Timeframe formats, wildcards, abstract classes
✅ **Status**: Ready for testing

**Next Steps**:
1. Run dry run: `python3 scripts/reset-all-widgets.py --dry-run`
2. Run full reset: `python3 scripts/reset-all-widgets.py`
3. Add widgets in MISP UI with corrected configuration
4. Verify widgets display data

---

**Maintainer**: tKQB Enterprises
**Related Files**:
- `scripts/reset-all-widgets.py`
- `TIMEFRAME_FORMAT_FIX.md`
- `EVENT_POPULATION_FIX.md`
- `WIDGET_TROUBLESHOOTING_SUMMARY.md`
