# Widget Configuration Fix - Final Resolution

**Date**: 2025-10-17
**Issue**: Three widgets showing "No data" due to incorrect tag filters
**Root Cause**: Widgets used literal tags (`ics:sector`, `ics-cert:`) instead of wildcards (`ics:%`, `ics-cert:%`)
**Status**: ✅ RESOLVED

---

## Problem Summary

After populating 18 events with geographic, MITRE ATT&CK, and ICS-CERT data, three widgets still showed "No data":

1. **Utilities Sector Threat Heat Map** - Used `ics:sector` tag (doesn't exist)
2. **MITRE ATT&CK for ICS Techniques** - Used `7d` timeframe (too short)
3. **ICS-CERT Advisories** - Used literal `ics-cert:` tag instead of wildcard

### Root Cause Analysis

**Heat Map Widget**:
```php
// BEFORE (broken)
'tags' => array('ics:sector')  // This tag doesn't exist in any events

// Events actually have these tags:
// 'ics:scada', 'ics:hmi', 'ics:plc', 'ics:modbus', 'ics:dnp3', etc.
```

**ICS-CERT Widget**:
```php
// BEFORE (broken)
'tags' => array('ics-cert:', 'icsa-')  // Literal match only

// MISP requires wildcards for prefix matching:
'tags' => array('ics-cert:%', 'icsa-%')  // Wildcard match
```

**MITRE ATT&CK Widget**:
```php
// BEFORE (suboptimal)
$timeframe = '7d';  // Only last 7 days

// Events are spread over 20 days, so 7d misses most of them
```

---

## Solution Implemented

### 1. Heat Map Widget - Fixed Tag Filter

**File**: `widgets/utilities-sector/UtilitiesThreatHeatMapWidget.php`

**Changes**:
```php
// BEFORE
public $placeholder = '{
    "timeframe": "7d",
    "limit": "1000",
    "sector_tag": "ics:sector"  // ❌ Wrong - this tag doesn't exist
}';

$sectorTag = !empty($options['sector_tag']) ? $options['sector_tag'] : 'ics:sector';

// AFTER
public $placeholder = '{
    "timeframe": "30d",
    "limit": "1000",
    "sector_tag": "ics:%"  // ✅ Correct - matches all ICS tags
}';

$sectorTag = !empty($options['sector_tag']) ? $options['sector_tag'] : 'ics:%';
```

**Result**: Widget now finds 11+ events with ICS tags (scada, hmi, plc, modbus, dnp3, etc.)

### 2. MITRE ATT&CK Widget - Extended Timeframe

**File**: `widgets/ics-ot-dashboard/MITREAttackICSWidget.php`

**Changes**:
```php
// BEFORE
public $placeholder = '{
    "timeframe": "7d",  // ❌ Too short - events spread over 20 days
    "limit": "15",
    "tactic_filter": ""
}';

// AFTER
public $placeholder = '{
    "timeframe": "30d",  // ✅ Extended to cover all events
    "limit": "15",
    "tactic_filter": ""
}';
```

**Result**: Widget now finds 11+ events with MITRE ATT&CK tags across 30-day period

### 3. ICS-CERT Widget - Fixed Wildcard Tags

**File**: `widgets/utilities-feed-dashboard/ICSCERTAdvisoryWidget.php`

**Changes**:
```php
// BEFORE
$filters = array(
    'last' => $timeframe,
    'published' => 1,
    'tags' => array('ics-cert:', 'icsa-'),  // ❌ Literal match only
    'limit' => 500,
    'includeEventTags' => 1,
    'metadata' => false
);

// AFTER
$filters = array(
    'last' => $timeframe,
    'published' => 1,
    'tags' => array('ics-cert:%', 'icsa-%'),  // ✅ Wildcard match
    'limit' => 500,
    'includeEventTags' => 1,
    'metadata' => false
);
```

**Result**: Widget now finds 7 events with ICS-CERT advisory tags

---

## Verification

### Heat Map Data Verification

```bash
# Query that heat map widget uses
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://misp-test.lan/events/restSearch" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"returnFormat": "json", "published": 1, "tags": ["ics:%"], "last": "30d", "limit": 1000}' \
  | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'Events found: {len(data.get(\"response\", []))}')"

# Expected: 10+ events
# Actual Result: ✅ 11 events with country codes and ICS tags
```

### MITRE ATT&CK Data Verification

```bash
# Query that MITRE ATT&CK widget uses
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://misp-test.lan/events/restSearch" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"returnFormat": "json", "published": 1, "tags": ["misp-galaxy:mitre-attack-pattern=%"], "last": "30d"}' \
  | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'Events found: {len(data.get(\"response\", []))}')"

# Expected: 10+ events
# Actual Result: ✅ 11 events with MITRE ATT&CK tags
```

### ICS-CERT Data Verification

```bash
# Query that ICS-CERT widget uses
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://misp-test.lan/events/restSearch" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"returnFormat": "json", "published": 1, "tags": ["ics-cert:%"], "last": "30d"}' \
  | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'Events found: {len(data.get(\"response\", []))}')"

# Expected: 7 events
# Actual Result: ✅ 7 events with ICS-CERT advisory tags
```

---

## Corrected Widget Configurations

### 1. Utilities Sector Threat Heat Map

**Add Widget Configuration**:
```json
{
    "timeframe": "30d",
    "limit": "1000",
    "sector_tag": "ics:%"
}
```

**What You'll See**:
- World map with color-coded threat intensity
- 12 countries with activity: US, Ukraine, Germany, France, UK, South Korea, Japan, Saudi Arabia, Australia, Canada, Brazil, India
- Hover tooltips: "US: 4 events (4 ICS-related)"
- Color intensity based on event count per country

### 2. MITRE ATT&CK for ICS Techniques

**Add Widget Configuration**:
```json
{
    "timeframe": "30d",
    "limit": "15",
    "tactic_filter": ""
}
```

**What You'll See**:
- Bar chart showing top 15 trending techniques
- Techniques like:
  - Spearphishing Attachment - T1566.001
  - Exploitation for Privilege Escalation - T1068
  - Screen Capture - T1113
  - Valid Accounts - T1078
  - External Remote Services - T1133
  - Data Encrypted for Impact - T1486
  - Modify Controller Tasking - T0821
  - And more...
- Color-coded by tactic (red=initial-access, blue=execution, orange=impact)

### 3. ICS-CERT Advisories (Utilities)

**Add Widget Configuration**:
```json
{
    "timeframe": "30d",
    "limit": "15",
    "severity_filter": "all"
}
```

**What You'll See**:
- List of 7 recent advisories
- Format: `ICSA-25-01-042 | [HIGH] | Siemens | 3 CVEs | 2025-10-15 (View)`
- Vendors: Siemens, Schneider Electric, Rockwell, ABB, GE Vernova, Honeywell, Emerson
- Severity indicators: [CRIT], [HIGH], [MED]
- Clickable links to view full event details

---

## Files Modified

### Widget Files:
1. **UtilitiesThreatHeatMapWidget.php**
   - Changed `sector_tag` default from `ics:sector` to `ics:%`
   - Changed `timeframe` default from `7d` to `30d`
   - Updated parameter description

2. **MITREAttackICSWidget.php**
   - Changed `timeframe` default from `7d` to `30d`
   - No tag changes needed (already using correct format)

3. **ICSCERTAdvisoryWidget.php**
   - Changed tag filters from `'ics-cert:', 'icsa-'` to `'ics-cert:%', 'icsa-%'`
   - Added wildcard for proper tag matching

### Documentation:
- **WIDGET_CONFIG_FIX_FINAL.md** - This document
- **WIDGET_DATA_POPULATION.md** - Updated with corrected configurations

---

## Integration with Installation

The corrected widgets are now part of Phase 11.11 and will be automatically installed with the correct configurations:

```bash
# Fresh installation - widgets automatically correct
python3 misp-install.py --config config.json

# Or reinstall widgets manually
python3 scripts/reset-all-widgets.py --yes
```

---

## Troubleshooting

### Widget Still Shows "No data"

**Checklist**:
1. ✅ Events populated (49 total: 31 utilities + 18 widget events)
2. ✅ Widgets reinstalled with corrected configurations
3. ✅ MISP container restarted
4. ✅ Browser cache cleared (Ctrl+Shift+R)
5. ⚠️ Widget removed and re-added in UI (may still have old config)

**Solution**: Remove widget from dashboard and re-add with new configuration

### Heat Map Shows No Countries

**Possible Causes**:
- Using old configuration with `"sector_tag": "ics:sector"`
- Timeframe too short (`7d` instead of `30d`)

**Solution**: Update widget configuration:
```json
{
    "timeframe": "30d",
    "limit": "1000",
    "sector_tag": "ics:%"
}
```

### MITRE ATT&CK Shows No Techniques

**Possible Causes**:
- Timeframe too short (using `7d` instead of `30d`)
- Events not published

**Solution**: Extend timeframe to `30d`:
```json
{
    "timeframe": "30d",
    "limit": "15",
    "tactic_filter": ""
}
```

### ICS-CERT Shows No Advisories

**Possible Causes**:
- Using old widget file without wildcard fix
- Severity filter too restrictive

**Solution**:
1. Verify widget has wildcard tags: `sudo docker exec misp-misp-core-1 grep "ics-cert" /var/www/MISP/app/Lib/Dashboard/Custom/ICSCERTAdvisoryWidget.php | grep tags`
2. Should show: `'tags' => array('ics-cert:%', 'icsa-%'),`
3. If not, reinstall widgets: `python3 scripts/reset-all-widgets.py --yes`

---

## Summary

✅ **Heat Map Widget**: Fixed `ics:sector` → `ics:%` wildcard, extended timeframe `7d` → `30d`
✅ **MITRE ATT&CK Widget**: Extended timeframe `7d` → `30d` for better coverage
✅ **ICS-CERT Widget**: Fixed tags `ics-cert:` → `ics-cert:%` wildcard
✅ **All Widgets Reinstalled**: Correct configurations deployed to MISP
✅ **Verification Complete**: All queries return expected event counts

**Status**: COMPLETE - All three widgets now have correct configurations and data

**Expected Results**:
- **Heat Map**: 12 countries with ICS threat activity (11 events)
- **MITRE ATT&CK**: 20+ unique techniques across all tactics (11 events)
- **ICS-CERT**: 7 advisories with CVE details (7 events)

**Total Events in MISP**: 49 events (31 utilities + 18 widget events)

---

## Next Steps for User

1. **Access MISP Dashboard**: https://your-misp-domain/dashboards

2. **Remove Old Widgets** (if already added):
   - Click the X on each widget to remove it
   - This clears any cached old configurations

3. **Add Widgets with New Configurations**:
   - Click "Add Widget" button
   - Select widget from list
   - Use configurations shown above (30d timeframe, ics:% wildcard)
   - Click "Add"

4. **Verify Data Display**:
   - Heat map should show world map with colored countries
   - MITRE ATT&CK should show bar chart with techniques
   - ICS-CERT should show list of 7 advisories

5. **If Still No Data**:
   - Hard refresh browser: Ctrl+Shift+R
   - Check widget configuration shows `30d` and `ics:%`
   - Verify events exist: `curl -k -H "Authorization: $MISP_API_KEY" "https://misp-test.lan/events/restSearch" -X POST -d '{"published": 1, "limit": 50}'`

---

**Maintainer**: tKQB Enterprises
**Version**: 1.0
**Date**: 2025-10-17
**Related Documentation**:
- WIDGET_DATA_POPULATION.md - Event creation details
- TIMEFRAME_FORMAT_FIX.md - Timeframe format issues
- WIDGET_RESET_COMPLETE.md - Widget reinstallation
- EVENT_POPULATION_FIX.md - Threat actor widget fixes
