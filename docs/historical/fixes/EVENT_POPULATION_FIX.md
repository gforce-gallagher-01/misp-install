# Event Population Fix - Widget "No Data" Issue

**Date**: 2025-10-17
**Issue**: Threat Actor Dashboard widgets showing "No data" after fresh installation
**Root Cause**: Phase 11.8 configured taxonomies/galaxies but never created the 31 ICS/OT events
**Status**: ✅ RESOLVED

---

## Problem Summary

After fixing the abstract class issue (see `WIDGET_TROUBLESHOOTING_SUMMARY.md`), widgets still showed "No data" because:

1. **Phase 11.8** (`configure-misp-utilities-sector.py`) only configured:
   - ICS/OT taxonomies
   - MITRE ATT&CK for ICS galaxy
   - Threat feeds

2. **Missing**: Creation of the 31 demonstration ICS/OT events
   - Event templates existed in `scripts/event_templates.py`
   - No script was using these templates during installation
   - Widgets had no events to query

## Root Cause: MISP API Event Creation Error

Initial attempts to create events via `/events/add` API failed with:

```
HTTP 403: "Received a published event that was empty. Event add process blocked."
```

**Why This Happened**:
- MISP security policy: **published events MUST have attributes or tags**
- Original script tried to create events with `"published": true`
- Events had tags but MISP still rejected them as "empty"
- This is a MISP anti-spam protection mechanism

## Solution Implemented

### 1. Fixed Event Creation Logic

**File**: `scripts/populate-utilities-events.py`

**Changes**:
```python
# BEFORE (broken)
event_payload = {
    "Event": {
        "published": True,  # ❌ Rejected by MISP
        "Tag": enhanced_tags
    }
}

# AFTER (working)
event_payload = {
    "Event": {
        "published": False,  # ✅ Create unpublished first
        "Tag": enhanced_tags
    }
}

# After event creation, publish it
response = requests.post(f"{misp_url}/events/publish/{event_id}")
```

**Workflow**:
1. Create event as **unpublished** (MISP accepts this)
2. Add attributes if specified in template
3. **Publish** the event via `/events/publish/{id}` endpoint
4. Result: Published event with tags available for widget queries

### 2. Fixed Colors.section() Error

**Error**:
```
AttributeError: type object 'Colors' has no attribute 'section'
```

**Fix**: Replaced `Colors.section()` with valid methods:
```python
# BEFORE
print(Colors.section("POPULATING EVENTS"))

# AFTER
print("\n" + "="*60)
print(Colors.info("POPULATING EVENTS"))
print("="*60)
```

### 3. Integrated into Phase 11.8

**File**: `phases/phase_11_8_utilities_sector.py`

**Added Method**:
```python
def _populate_utilities_events(self, api_key: str):
    """Populate 31 ICS/OT threat intelligence events for dashboard widgets"""
    self.logger.info("[11.8.2] Populating ICS/OT threat intelligence events...")
    self.logger.info("          Creating 31 demonstration events for Threat Actor Dashboard widgets")

    script_path = Path(__file__).parent.parent / 'scripts' / 'populate-utilities-events.py'
    os.environ['MISP_API_KEY'] = api_key

    result = self.run_command(['python3', str(script_path)], timeout=180, check=False)

    if result.returncode == 0:
        self.logger.info(Colors.success("✓ 31 ICS/OT threat intelligence events created"))
    else:
        self.logger.warning("⚠️  Event population may have failed")
```

**Execution Order in Phase 11.8**:
1. Configure taxonomies/galaxies (`configure-misp-utilities-sector.py`)
2. **Populate 31 events** (`populate-utilities-events.py`) ← NEW
3. Display configured features

---

## Event Templates

**Location**: `scripts/event_templates.py`

**Structure**:
- 31 events numbered 3-33 (continuous sequence)
- Each event has:
  - Descriptive `info` field (incident description)
  - Base tags: `ics:`, `utilities:`, `incident:`
  - Enhanced tags: `misp-galaxy:threat-actor=` (added via `ENHANCED_TAGS_BY_EVENT`)
  - Date spread over last 20 days
  - Optional attributes (IP addresses, domains, file hashes)

**Event Categories**:
1. **ICS/OT Malware** (Events 3-10): PIPEDREAM, Havex, BlackEnergy, APT33, Dragonfly, XENOTIME, Sandworm, MERCURY
2. **ICS Vulnerabilities** (Events 11-15): Modbus, Schneider, Siemens, Rockwell, GE CIMPLICITY
3. **Water Sector Incidents** (Events 16-20): Treatment facilities, municipal systems, dams
4. **CISA Alerts** (Events 21-23): Volt Typhoon, Unitronics, ransomware
5. **NERC CIP Compliance** (Events 24-25): Supply chain, patch management
6. **Multi-Sector Campaigns** (Events 26-28): Reconnaissance, malware, zero-days
7. **ISAC Bulletins** (Events 29-33): E-ISAC, WaterISAC, multi-ISAC alerts

**Enhanced Threat Actor Tags** (added to specific events):
```python
ENHANCED_TAGS_BY_EVENT = {
    3: [..., {"name": "misp-galaxy:threat-actor=\"CHERNOVITE\""}],
    4: [..., {"name": "misp-galaxy:threat-actor=\"Dragonfly\""}],
    5: [..., {"name": "misp-galaxy:threat-actor=\"Sandworm\""}],
    6: [..., {"name": "misp-galaxy:threat-actor=\"APT33\""}],
    7: [..., {"name": "misp-galaxy:threat-actor=\"Dragonfly 2.0\""}],
    8: [..., {"name": "misp-galaxy:threat-actor=\"XENOTIME\""}],
    9: [..., {"name": "misp-galaxy:threat-actor=\"Sandworm Team\""}],
    10: [..., {"name": "misp-galaxy:threat-actor=\"MERCURY\""}],
    21: [..., {"name": "misp-galaxy:threat-actor=\"Volt Typhoon\""}],
    27: [..., {"name": "misp-galaxy:threat-actor=\"LockBit\""}],
}
```

---

## Testing & Verification

### Test 1: Manual Event Population

```bash
# Run the populate script manually
python3 scripts/populate-utilities-events.py

# Expected output:
============================================================
POPULATING ICS/OT THREAT INTELLIGENCE EVENTS
============================================================
MISP URL: https://misp-test.lan
Events to create: 31

✓ Event 3: PIPEDREAM Malware Framework... (ID: 2)
✓ Event 4: Havex Malware Campaign... (ID: 3)
...
✓ Event 33: Regional Utility Consortium... (ID: 32)

============================================================
SUMMARY
============================================================
  ✓ Created: 31
  → Skipped: 0
  ✗ Failed: 0

✓ Successfully populated 31 ICS/OT threat intelligence events
```

### Test 2: Verify Events in MISP

```bash
# Query events with threat-actor and ICS tags
curl -k -X POST \
  -H "Authorization: $MISP_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"returnFormat": "json", "published": 1, "tags": ["misp-galaxy:threat-actor", "ics:%"], "limit": 5}' \
  https://misp-test.lan/events/restSearch | python3 -m json.tool

# Expected: 5 events returned with published=true
```

### Test 3: Widget Debug Script

```bash
# Simulate widget PHP logic
MISP_API_KEY=<key> python3 /tmp/debug_widget_execution.py

# Expected output:
================================================================================
WIDGET EXECUTION DEBUG - Simulating PHP Widget Logic
================================================================================

1. APT GROUPS WIDGET SIMULATION
--------------------------------------------------------------------------------
   Query returned: 31 events

   TOTAL APT MATCHES ACROSS ALL EVENTS:
      dragonfly: 2 events
      chernovite: 1 events
      sandworm: 1 events
      apt33: 1 events
      xenotime: 1 events
      mercury: 1 events
      volt typhoon: 1 events
      lockbit: 1 events
```

### Test 4: Check Dashboard Widgets

1. Navigate to MISP web interface: `https://misp-test.lan`
2. Go to **Dashboard** (Home icon)
3. Click **"Add Widget"** button
4. Add the 4 Threat Actor widgets:
   - APT Groups Targeting Utilities
   - Nation-State Attribution
   - TTPs Targeting Utilities
   - Historical ICS Security Incidents
5. **Expected**: All 4 widgets show data immediately

---

## Files Modified

### Created:
- `scripts/populate-utilities-events.py` - Event population script (new)
- `EVENT_POPULATION_FIX.md` - This documentation

### Modified:
- `phases/phase_11_8_utilities_sector.py` - Added `_populate_utilities_events()` method

### Referenced (no changes):
- `scripts/event_templates.py` - Event template definitions
- `lib/colors.py` - Color output utilities

---

## Common Issues & Troubleshooting

### Issue: "Permission denied (403)" when creating events

**Symptom**:
```
⚠ Event 3: Permission denied (403)
```

**Cause**: API key doesn't have "Add Event" permission

**Fix**: Verify API key role:
```bash
curl -k -H "Authorization: $MISP_API_KEY" https://misp-test.lan/users/view/me | grep -A 3 "Role"
# Look for: "perm_add": true
```

### Issue: "Received a published event that was empty"

**Symptom**:
```
Error: Received a published event that was empty. Event add process blocked.
```

**Cause**: Trying to create published events without attributes

**Fix**: Already fixed in current version - events are created unpublished, then published after creation

### Issue: Widgets still show "No data" after event population

**Checklist**:
1. ✅ Events are published: Check `"published": true` in API response
2. ✅ Events have threat-actor tags: Check for `misp-galaxy:threat-actor=` tags
3. ✅ Events have ICS tags: Check for `ics:%` tags
4. ✅ Widget code uses wildcards: `'ics:%'` not `'ics:'`
5. ✅ Abstract classes removed: No `BaseUtilitiesWidget.php` in Custom directory
6. ✅ Container restarted: Clear PHP OpCache

---

## Manual Event Population (If Needed)

If events weren't created during installation, run manually:

```bash
# Set API key environment variable
export MISP_API_KEY=$(sudo grep MISP_API_KEY= /opt/misp/.env | cut -d= -f2)

# Or use specific key
export MISP_API_KEY="your-api-key-here"

# Run populate script
python3 scripts/populate-utilities-events.py

# Verify events created
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://misp-test.lan/events/restSearch" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"returnFormat": "json", "published": 1, "tags": ["misp-galaxy:threat-actor"], "limit": 50}' \
  | python3 -m json.tool | grep -c '"Event"'

# Expected: 31 (or more if other events exist)
```

---

## Integration with Installation

**Phase 11.8 Execution**:

```
PHASE 11.8: UTILITIES SECTOR THREAT INTELLIGENCE
[11.8.1] Configuring ICS/SCADA/Utilities sector threat intelligence...
          This includes ICS taxonomies, MITRE ATT&CK for ICS, and sector-specific feeds
✓ Utilities sector threat intelligence configured

[11.8.2] Populating ICS/OT threat intelligence events...
          Creating 31 demonstration events for Threat Actor Dashboard widgets
✓ 31 ICS/OT threat intelligence events created

  Configured Features:
    • ICS/OT Taxonomies (NIST ICS, ICS-CERT Advisories)
    • MITRE ATT&CK for ICS Galaxy
    • DHS Critical Infrastructure Sectors
    • Utilities Sector Threat Feeds
    • ICS/SCADA Event Templates
    • 31 ICS/OT Threat Intelligence Events
```

**Phase 11.11 Execution** (happens after 11.8):

```
PHASE 11.11: UTILITIES SECTOR DASHBOARDS
Installing base widget files...
✓ Base widget files installed

Installing utilities-sector widgets...
✓ utilities-sector widgets installed

Installing ics-ot-dashboard widgets...
✓ ics-ot-dashboard widgets installed

Installing threat-actor-dashboard widgets...
✓ threat-actor-dashboard widgets installed

Installing utilities-feed-dashboard widgets...
✓ utilities-feed-dashboard widgets installed

Installing organizational-dashboard widgets...
✓ organizational-dashboard widgets installed

✓ All 25 widgets installed successfully

Removing abstract base classes from Custom directory...
✓ Removed abstract class: BaseUtilitiesWidget.php
✓ Removed 1 abstract base class(es)
✓ Dashboard 'Add Widget' functionality preserved

Applying widget query fixes...
✓ Applied wildcard fixes to 18/18 widgets

Configuring dashboards via MISP API...
✓ All 25 dashboards configured via API

✓ Utilities dashboards configured successfully (25 widgets)
```

**Result**: Widgets have data to display immediately after installation completes.

---

## Summary

✅ **Fixed**: Event population script (`populate-utilities-events.py`)
✅ **Fixed**: Colors.section() method calls
✅ **Fixed**: MISP API "empty published event" rejection
✅ **Integrated**: Event population into Phase 11.8 automated installation
✅ **Verified**: 31 events created with correct tags and published status
✅ **Verified**: Widgets now return data when queried

**Status**: COMPLETE - Widgets should now show data in fresh installations

---

**Maintainer**: tKQB Enterprises
**Related Files**:
- `scripts/populate-utilities-events.py`
- `scripts/event_templates.py`
- `phases/phase_11_8_utilities_sector.py`
- `WIDGET_TROUBLESHOOTING_SUMMARY.md`
- `widgets/DASHBOARD_WIDGET_FIXES.md`
