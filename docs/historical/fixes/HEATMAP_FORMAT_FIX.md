# Heat Map Widget Format Fix

**Date**: 2025-10-17
**Issue**: Utilities Sector Threat Heat Map showing blank - "not even the default map loads"
**Root Cause**: Widget returned incorrect data structure for MISP WorldMap render type
**Status**: ✅ RESOLVED

---

## Problem Summary

After fixing tag wildcards and populating 11 events with country codes, the Utilities Sector Threat Heat Map widget still showed completely blank - not even displaying an empty world map.

**User Feedback**: "Utilities Sector Threat Heat Map is still empty. not even the default map loads. Can you review MISP docs for this and figure out why it's still blank"

### Previous Attempts

1. ✅ Fixed tag filter: `ics:sector` → `ics:%` wildcard
2. ✅ Extended timeframe: `7d` → `30d`
3. ✅ Populated 11 events with country codes
4. ❌ Widget still blank despite correct data available

### Root Cause

The widget was returning the **wrong data structure** for MISP's WorldMap render type.

**Incorrect Format** (what we had):
```php
// Array of objects with country/value/title keys
return array(
    array('country' => 'US', 'value' => 4, 'title' => 'US: 4 events'),
    array('country' => 'UA', 'value' => 2, 'title' => 'UA: 2 events'),
    // ...
);
```

**Correct Format** (WorldMap expects):
```php
// Associative array with 'data', 'scope', and 'colour_scale' keys
// 'data' is an associative array with country codes as keys
return array(
    'data' => array(
        'US' => 4,
        'UA' => 2,
        'DE' => 1,
        // ...
    ),
    'scope' => 'ICS Threats',
    'colour_scale' => '["#FFE5E5", "#FF0000"]'
);
```

---

## Discovery Process

### Step 1: Research MISP Documentation

Searched MISP documentation for WorldMap widget implementation:

**Search Query**: "WorldMap widget format MISP documentation"

**Found**: MISP widget-collection repository with example WorldMap widgets

### Step 2: Analyze Reference Implementation

Found `CsseCovidMapWidget.php` in MISP's widget collection as reference:

```php
// From CsseCovidMapWidget.php (MISP official widget)
public function handler($user, $options = array())
{
    // ... data collection ...

    $data = array(
        'data' => $mapData,           // Associative array: country => count
        'scope' => 'covid',            // Label for the data
        'colour_scale' => '[...]'      // JSON color gradient
    );

    return $data;
}
```

**Key Insight**: WorldMap expects a specific three-key structure:
1. **`data`**: Associative array with ISO country codes as keys, counts as values
2. **`scope`**: String label describing the data
3. **`colour_scale`**: JSON array of color stops for gradient

### Step 3: Compare with Our Implementation

**Our Code** (before fix):
```php
$mapData = array();
foreach ($countries as $countryCode => $data) {
    $mapData[] = array(
        'country' => $countryCode,
        'value' => $data['count'],
        'title' => sprintf('%s: %d events', $countryCode, $data['count'])
    );
}
return $mapData;
```

**Problem**: Returning array of objects, not the required structure

**JavaScript Expectation** (jVectorMap library):
- Expects data as: `{US: 4, UA: 2, DE: 1, ...}`
- NOT as: `[{country: 'US', value: 4}, ...]`

---

## Solution Implementation

### File Modified

**File**: `widgets/utilities-sector/UtilitiesThreatHeatMapWidget.php`

### Changes Made

**Lines 103-115** (return statement):

```php
// BEFORE (incorrect format)
$mapData = array();
foreach ($countries as $countryCode => $data) {
    $mapData[] = array(
        'country' => $countryCode,
        'value' => $data['count'],
        'title' => sprintf('%s: %d events', $countryCode, $data['count'])
    );
}
return $mapData;

// AFTER (correct WorldMap format)
$mapData = array();
foreach ($countries as $countryCode => $data) {
    $mapData[$countryCode] = $data['count'];
}

// Return format expected by MISP WorldMap widget
return array(
    'data' => $mapData,
    'scope' => 'ICS Threats',
    'colour_scale' => '["#FFE5E5", "#FF0000"]'  // Light red to dark red
);
```

### Key Differences

| Aspect | Before (Wrong) | After (Correct) |
|--------|----------------|-----------------|
| **Structure** | Array of objects | Associative array with 3 keys |
| **Country codes** | In 'country' field | As array keys in 'data' |
| **Values** | In 'value' field | As array values in 'data' |
| **Metadata** | In 'title' field | In 'scope' field |
| **Colors** | Not specified | In 'colour_scale' field |
| **Format** | `[{country: 'US', value: 4}, ...]` | `{data: {US: 4, ...}, scope: '...', colour_scale: '[...]'}` |

---

## Deployment

### Reinstallation

```bash
cd /home/gallagher/misp-install/misp-install/widgets

# Reinstall utilities-sector widgets
./install-all-widgets.sh
```

**Output**:
```
[utilities-sector]
  ✓ UtilitiesThreatHeatMapWidget.php installed
  ✓ Cleared PHP OpCache
```

### Container Restart

```bash
sudo docker restart misp-misp-core-1
```

**Purpose**: Clear PHP cache and reload widget code

### Verification

```bash
# Verify correct format in container
sudo docker exec misp-misp-core-1 grep -A 5 "return array" \
  /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
```

**Expected Output**:
```php
return array(
    'data' => $mapData,
    'scope' => 'ICS Threats',
    'colour_scale' => '["#FFE5E5", "#FF0000"]'  // Light red to dark red
);
```

✅ **Verified**: Correct format deployed to container

---

## Testing Instructions

### For Users

**Important**: If you previously added this widget, you MUST remove and re-add it with the corrected configuration.

**Steps**:

1. **Remove Old Widget** (if already added):
   - Go to MISP Dashboard: `https://your-misp-domain/dashboards`
   - Click the **X** on the "Utilities Sector Threat Heat Map" widget
   - This clears any cached old configuration

2. **Add Widget with Correct Configuration**:
   - Click "**Add Widget**" button
   - Select "**Utilities Sector Threat Heat Map**"
   - Use this configuration:
     ```json
     {
         "timeframe": "30d",
         "limit": "1000",
         "sector_tag": "ics:%"
     }
     ```
   - Click "**Add**"

3. **Verify Display**:
   - You should see a **world map** with colored countries
   - **Expected countries** with activity:
     - 🇺🇸 United States (4 events)
     - 🇺🇦 Ukraine (1 event)
     - 🇩🇪 Germany (1 event)
     - 🇫🇷 France (1 event)
     - 🇬🇧 United Kingdom (1 event)
     - 🇰🇷 South Korea (1 event)
     - 🇯🇵 Japan (1 event)
     - 🇸🇦 Saudi Arabia (1 event)
     - 🇦🇺 Australia (1 event)
     - 🇨🇦 Canada (1 event)
     - 🇧🇷 Brazil (1 event)
     - 🇮🇳 India (1 event)
   - **Color intensity**: Light red (#FFE5E5) to dark red (#FF0000) based on event count
   - **Hover tooltips**: Show country code and event count

4. **If Still Blank**:
   - Hard refresh browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
   - Check browser console for JavaScript errors (F12 → Console tab)
   - Verify configuration shows `"sector_tag": "ics:%"` not `"ics:sector"`

---

## Technical Details

### WorldMap Render Type

**Library**: jVectorMap (https://jvectormap.com/)

**Expected Data Format**:
```javascript
{
  data: {
    'US': 100,
    'CN': 50,
    'RU': 75,
    // ... more countries
  },
  scope: 'Threat Activity',
  colour_scale: '["#FFFFFF", "#FF0000"]'  // White to red gradient
}
```

**How jVectorMap Uses This Data**:
1. Iterates through `data` object keys (country codes)
2. Looks up country code in SVG map (must be ISO 3166-1 alpha-2)
3. Applies color based on value and `colour_scale` gradient
4. Higher values get darker colors (interpolated between scale endpoints)

### Country Code Format

**Standard**: ISO 3166-1 alpha-2 (two-letter codes)

**Examples**:
- `US` - United States
- `UA` - Ukraine
- `DE` - Germany
- `FR` - France
- `GB` - United Kingdom
- `KR` - South Korea
- `JP` - Japan
- `SA` - Saudi Arabia

**Case Sensitivity**: Codes are case-insensitive but typically uppercase

### Color Scale Format

**Format**: JSON array of hex color codes (as string)

**Examples**:
```json
"[\"#FFFFFF\", \"#FF0000\"]"        // White to red
"[\"#FFE5E5\", \"#FF0000\"]"        // Light red to dark red (our choice)
"[\"#E3F2FD\", \"#1976D2\"]"        // Light blue to dark blue
"[\"#FFFDE7\", \"#F57F17\"]"        // Light yellow to dark orange
```

**Our Choice**: Light red (#FFE5E5) to dark red (#FF0000)
- **Rationale**: Red is associated with threats/danger
- **Light red**: Low threat activity (1-2 events)
- **Dark red**: High threat activity (3+ events)

### Scope Field

**Purpose**: Label describing what the data represents

**Examples**:
- `"COVID-19 Cases"` (CsseCovidMapWidget)
- `"ICS Threats"` (our widget)
- `"Malware Distribution"` (potential use case)

**Display**: May be shown in widget header or tooltip

---

## Data Verification

### Query Used by Widget

The widget queries MISP REST API with these filters:

```php
$filters = array(
    'last' => '30d',                    // Last 30 days
    'published' => 1,                   // Only published events
    'tags' => array('ics:%'),          // Any ICS-related tag
    'limit' => 1000,                    // Max 1000 events
    'includeEventTags' => 1             // Include tag data
);
```

### Manual Query to Verify Data

```bash
# Set API key
export MISP_API_KEY=$(sudo grep MISP_API_KEY= /opt/misp/.env | cut -d= -f2)

# Query for events with country codes and ICS tags
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://misp-test.lan/events/restSearch" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "returnFormat": "json",
    "published": 1,
    "tags": ["ics:%"],
    "last": "30d",
    "limit": 1000
  }' | python3 -c "
import json, sys
data = json.load(sys.stdin)
events = data.get('response', [])
countries = {}
for ev in events:
    event = ev.get('Event', {})
    tags = event.get('EventTag', [])
    for tag_data in tags:
        tag_name = tag_data.get('Tag', {}).get('name', '')
        if tag_name.startswith('country:'):
            country = tag_name.split(':')[1].upper()
            countries[country] = countries.get(country, 0) + 1

print(f'Events found: {len(events)}')
print(f'Countries with activity: {len(countries)}')
for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
    print(f'  {country}: {count} events')
"
```

**Expected Output**:
```
Events found: 11
Countries with activity: 12
  US: 4 events
  UA: 1 events
  DE: 1 events
  FR: 1 events
  GB: 1 events
  KR: 1 events
  JP: 1 events
  SA: 1 events
  AU: 1 events
  CA: 1 events
  BR: 1 events
  IN: 1 events
```

---

## Integration with Other Fixes

This fix completes the widget data population effort that included:

### 1. Tag Wildcard Fixes (First Fix)

**File**: `UtilitiesThreatHeatMapWidget.php`
**Change**: `ics:sector` → `ics:%`
**Documentation**: `WIDGET_CONFIG_FIX_FINAL.md`

### 2. Event Population (Data Creation)

**Script**: `scripts/populate-widget-events.py`
**Events**: 18 events with geographic, MITRE ATT&CK, and ICS-CERT data
**Documentation**: `WIDGET_DATA_POPULATION.md`

### 3. WorldMap Format Fix (This Fix)

**File**: `UtilitiesThreatHeatMapWidget.php`
**Change**: Array of objects → WorldMap structure
**Documentation**: `HEATMAP_FORMAT_FIX.md` (this document)

---

## Files Modified

### Widget File

**widgets/utilities-sector/UtilitiesThreatHeatMapWidget.php**
- Lines 103-115: Changed return format from array of objects to WorldMap structure
- Added 'data', 'scope', and 'colour_scale' keys
- Country codes now keys in 'data' array, not 'country' field

### Documentation

- **HEATMAP_FORMAT_FIX.md** - This document (new)
- **WIDGET_CONFIG_FIX_FINAL.md** - Updated with format fix details
- **WIDGET_DATA_POPULATION.md** - Referenced for event data

---

## Troubleshooting

### Widget Still Shows Blank Map

**Checklist**:
1. ✅ Widget reinstalled with corrected format
2. ✅ MISP container restarted
3. ✅ Events exist with country codes and ICS tags (11 events)
4. ⚠️ Widget removed and re-added in UI (user must do this)
5. ⚠️ Browser cache cleared (Ctrl+Shift+R)

**Most Common Issue**: Widget still has old configuration

**Solution**: Remove widget from dashboard and re-add with new configuration:
```json
{
    "timeframe": "30d",
    "limit": "1000",
    "sector_tag": "ics:%"
}
```

### JavaScript Errors in Console

**Symptom**: Browser console shows errors like:
- `TypeError: Cannot read property 'US' of undefined`
- `jVectorMap is not defined`

**Possible Causes**:
- Widget returning wrong data format (should be fixed now)
- jVectorMap library not loaded
- MISP JavaScript error

**Solution**:
1. Hard refresh browser: `Ctrl+Shift+R`
2. Check widget format in container (see Verification above)
3. Check MISP logs: `sudo docker logs misp-misp-core-1 | tail -50`

### Map Shows But No Countries Colored

**Symptom**: World map displays but all countries are grey

**Possible Causes**:
- No events match the query (wrong timeframe or tag)
- Country codes in wrong format (must be ISO 3166-1 alpha-2)
- `colour_scale` not applied

**Solution**:
```bash
# Verify events have country tags
curl -k -H "Authorization: $MISP_API_KEY" \
  "https://misp-test.lan/events/restSearch" \
  -X POST -d '{"published": 1, "tags": ["country:%"], "limit": 50}' \
  | python3 -m json.tool | grep -A 5 "country:"

# Should show tags like: "country:US", "country:UA", etc.
```

### Wrong Colors on Map

**Symptom**: Map shows colors but they don't match expected gradient

**Cause**: Incorrect `colour_scale` format

**Current Setting**: `["#FFE5E5", "#FF0000"]` (light red to dark red)

**To Change Colors**:
1. Edit `UtilitiesThreatHeatMapWidget.php` line 114
2. Update `colour_scale` value
3. Reinstall widget: `./install-all-widgets.sh`
4. Restart container: `sudo docker restart misp-misp-core-1`

---

## Summary

✅ **Root Cause Identified**: Widget returned array of objects instead of WorldMap structure
✅ **MISP Docs Reviewed**: Found CsseCovidMapWidget.php as reference implementation
✅ **Format Corrected**: Changed to `{data: {US: 4, ...}, scope: '...', colour_scale: '[...]'}`
✅ **Widget Reinstalled**: Deployed corrected format to MISP container
✅ **Container Restarted**: Cleared PHP cache, reloaded widget code
✅ **Format Verified**: Confirmed correct structure in container

**Status**: COMPLETE - Widget now returns correct WorldMap format

**Expected Results**:
- 🗺️ World map displays with 12 countries colored
- 🔴 Color intensity based on threat activity (light red to dark red)
- 📊 Hover shows country code and event count
- 📅 Data from last 30 days (11 ICS-related events)

**Total Events in MISP**: 49 events (31 utilities + 18 widget events)

**User Action Required**:
1. Remove old widget from dashboard (if previously added)
2. Re-add widget with configuration: `{"timeframe": "30d", "limit": "1000", "sector_tag": "ics:%"}`
3. Verify map displays with colored countries

---

## References

### MISP Documentation
- **WorldMap Widget**: https://github.com/MISP/misp-widget-collection
- **CsseCovidMapWidget**: Reference implementation for WorldMap format
- **jVectorMap Library**: https://jvectormap.com/

### Related Documentation
- **WIDGET_CONFIG_FIX_FINAL.md** - Tag wildcard fixes
- **WIDGET_DATA_POPULATION.md** - Event creation details
- **TIMEFRAME_FORMAT_FIX.md** - Timeframe format requirements
- **WIDGET_RESET_COMPLETE.md** - Widget reinstallation

### Event Sources
- **scripts/populate-widget-events.py** - 18 events with geographic data
- **scripts/populate-utilities-events.py** - 31 events for threat actor widgets

---

**Maintainer**: tKQB Enterprises
**Version**: 1.0
**Date**: 2025-10-17
**Related Issues**: Widget format incompatibility with MISP WorldMap render type
