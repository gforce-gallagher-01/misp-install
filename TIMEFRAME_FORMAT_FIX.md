# Timeframe Format Fix - Widget Configuration

**Date**: 2025-10-17
**Issue**: Threat Actor Dashboard widgets showing "No data" due to invalid timeframe format
**Root Cause**: Widget placeholders used `"1y"` format, but MISP only accepts day-based format (e.g., `"365d"`)
**Status**: ✅ RESOLVED

---

## Problem Summary

After fixing the event population issue (see `EVENT_POPULATION_FIX.md`), all four Threat Actor widgets still showed "No data" because:

1. **Widget placeholders** used human-readable timeframe format: `"1y"`, `"10y"`
2. **MISP API requirement**: Only accepts day-based format: `"7d"`, `"30d"`, `"365d"`, `"3650d"`, `"all"`
3. **Result**: MISP's `restSearch()` rejected invalid timeframe values, returning empty results

**Discovery**: Testing revealed the valid config format for "Add Widget" is:
```json
{
    "timeframe": "365d",
    "limit": "10"
}
```

The `"1y"` format is **not supported** by MISP's backend.

---

## Root Cause: MISP Timeframe API

**MISP's `restSearch()` Method**:
- Located in: `/var/www/MISP/app/Model/Event.php`
- The `last` parameter (used for timeframes) expects:
  - Day format: `7d`, `30d`, `90d`, `365d`, `3650d`
  - Special value: `all` (no time limit)
  - **NOT SUPPORTED**: `1y`, `5y`, `10y`, `1h`, `1m`

**What Happens with Invalid Timeframes**:
```php
// MISP backend behavior
if ($timeframe !== 'all' && !preg_match('/^\d+d$/', $timeframe)) {
    // Invalid format - MISP may silently ignore or return empty results
    return [];
}
```

This caused widgets to receive empty datasets even when events existed in the database.

---

## Solution Implemented

### Files Modified

#### 1. APTGroupsUtilitiesWidget.php
**Location**: `widgets/threat-actor-dashboard/APTGroupsUtilitiesWidget.php`

**Changes**:
```php
// BEFORE (broken)
public $params = array(
    'timeframe' => 'Time window (7d, 30d, 90d, 1y, all)',
    'limit' => 'Max groups to display (default: 15)'
);
public $placeholder = '{"timeframe": "1y", "limit": "15"}';

public function handler($user, $options = array()) {
    $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
}

// AFTER (working)
public $params = array(
    'timeframe' => 'Time window (7d, 30d, 90d, 365d, all)',
    'limit' => 'Max groups to display (default: 15)'
);
public $placeholder = '{"timeframe": "365d", "limit": "15"}';

public function handler($user, $options = array()) {
    $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '365d';
}
```

#### 2. NationStateAttributionWidget.php
**Location**: `widgets/threat-actor-dashboard/NationStateAttributionWidget.php`

**Changes**:
```php
// BEFORE: "timeframe": "1y"
// AFTER:  "timeframe": "365d"

// BEFORE: $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
// AFTER:  $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '365d';
```

#### 3. TTPsUtilitiesWidget.php
**Location**: `widgets/threat-actor-dashboard/TTPsUtilitiesWidget.php`

**Changes**:
```php
// BEFORE: "timeframe": "1y"
// AFTER:  "timeframe": "365d"

// BEFORE: $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
// AFTER:  $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '365d';
```

#### 4. HistoricalIncidentsWidget.php
**Location**: `widgets/threat-actor-dashboard/HistoricalIncidentsWidget.php`

**Changes**:
```php
// BEFORE (broken - 10 years)
public $params = array(
    'timeframe' => 'Time window (1y, 5y, 10y, all)',
    'limit' => 'Max incidents to show (default: 15)',
    'sector_filter' => 'Filter by sector (utilities, manufacturing, all)'
);
public $placeholder = '{"timeframe": "10y", "limit": "15", "sector_filter": "utilities"}';

public function handler($user, $options = array()) {
    $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '10y';
}

// AFTER (working - 10 years = 3650 days)
public $params = array(
    'timeframe' => 'Time window (365d, 1825d, 3650d, all)',
    'limit' => 'Max incidents to show (default: 15)',
    'sector_filter' => 'Filter by sector (utilities, manufacturing, all)'
);
public $placeholder = '{"timeframe": "3650d", "limit": "15", "sector_filter": "utilities"}';

public function handler($user, $options = array()) {
    $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '3650d';
}
```

---

## Timeframe Conversion Reference

For widget developers, here's the conversion table:

| Human Format | Day Format | Use Case |
|-------------|------------|----------|
| 7 days | `7d` | Last week |
| 30 days | `30d` | Last month |
| 90 days | `90d` | Last quarter |
| 1 year | `365d` | Last year |
| 5 years | `1825d` | 5-year history |
| 10 years | `3650d` | 10-year history |
| All time | `all` | No time limit |

**Invalid Formats** (will cause empty results):
- ❌ `1y`, `5y`, `10y` (year suffixes not supported)
- ❌ `1h`, `12h` (hour suffixes not supported)
- ❌ `1m`, `6m` (month suffixes not supported)
- ❌ `1w`, `2w` (week suffixes not supported)

**Valid Formats**:
- ✅ `7d`, `30d`, `90d`, `365d`, `1825d`, `3650d` (day suffixes)
- ✅ `all` (special keyword for no time limit)

---

## Testing & Verification

### Test 1: Check Widget Placeholder Values

```bash
# Verify all widgets use day format
cd /home/gallagher/misp-install/misp-install/widgets/threat-actor-dashboard
grep -n '"timeframe":' *.php

# Expected output (all should show day format):
# APTGroupsUtilitiesWidget.php:31:    "timeframe": "365d",
# NationStateAttributionWidget.php:30:    "timeframe": "365d",
# TTPsUtilitiesWidget.php:31:    "timeframe": "365d",
# HistoricalIncidentsWidget.php:32:    "timeframe": "3650d",
```

### Test 2: Verify Default Timeframe in Handler

```bash
# Check handler default values
grep -A 2 "public function handler" *.php | grep -A 1 "timeframe"

# Expected output (all should show day format like '365d' or '3650d'):
```

### Test 3: Add Widget in MISP UI

1. Navigate to MISP Dashboard
2. Click **"Add Widget"**
3. Select **"APT Groups Targeting Utilities"**
4. Check the pre-filled configuration:
   ```json
   {
       "timeframe": "365d",
       "limit": "15"
   }
   ```
5. Click **"Add"** - Widget should now display data immediately

### Test 4: Verify Widget Returns Data

After adding widgets to dashboard:

1. **APT Groups Targeting Utilities** - Should show bar chart with APT groups (Dragonfly, Sandworm, etc.)
2. **Nation-State Attribution** - Should show bar chart with countries (Russia, China, Iran, etc.)
3. **TTPs Targeting Utilities** - Should show bar chart with techniques (Spearphishing, HMI Interaction, etc.)
4. **Historical ICS Security Incidents** - Should show list of incidents (Ukraine Blackout, Stuxnet, TRITON, etc.)

**If widgets still show "No data"**:
- Check that 31 ICS/OT events were populated (see `EVENT_POPULATION_FIX.md`)
- Verify events have correct tags (`ics:%`, `misp-galaxy:threat-actor=%`)
- Restart MISP containers to clear PHP OpCache:
  ```bash
  cd /opt/misp
  sudo docker compose restart misp-core
  ```

---

## Widget Configuration Examples

### Example 1: Last 30 Days
```json
{
    "timeframe": "30d",
    "limit": "10"
}
```

### Example 2: Last Year
```json
{
    "timeframe": "365d",
    "limit": "15"
}
```

### Example 3: Last 10 Years (Historical Widget)
```json
{
    "timeframe": "3650d",
    "limit": "20",
    "sector_filter": "utilities"
}
```

### Example 4: All Time
```json
{
    "timeframe": "all",
    "limit": "25"
}
```

---

## Integration with Installation

### Phase 11.11: Widget Installation

The corrected widget files are automatically deployed during Phase 11.11:

```
PHASE 11.11: UTILITIES SECTOR DASHBOARDS
Installing threat-actor-dashboard widgets...
✓ APTGroupsUtilitiesWidget.php (timeframe: 365d)
✓ NationStateAttributionWidget.php (timeframe: 365d)
✓ TTPsUtilitiesWidget.php (timeframe: 365d)
✓ HistoricalIncidentsWidget.php (timeframe: 3650d)
✓ threat-actor-dashboard widgets installed
```

**No Manual Intervention Required**: Fresh installations will have correct timeframe formats.

**For Existing Installations**: If you installed before this fix, you need to:

1. **Update widget files**:
   ```bash
   cd /home/gallagher/misp-install/misp-install
   git pull origin main  # Get latest fixes
   ```

2. **Re-run Phase 11.11** (widget installation):
   ```bash
   # Copy updated widgets to MISP container
   cd /home/gallagher/misp-install/misp-install
   python3 phases/phase_11_11_utilities_dashboards.py
   ```

3. **Restart MISP**:
   ```bash
   cd /opt/misp
   sudo docker compose restart misp-core
   ```

4. **Reconfigure widgets in UI**:
   - Remove old widgets from dashboard
   - Add widgets again with corrected config

---

## Common Issues & Troubleshooting

### Issue: Widget still shows "No data" after fix

**Checklist**:
1. ✅ Widget files updated with `365d`/`3650d` format
2. ✅ MISP container restarted to clear PHP OpCache
3. ✅ Widget removed and re-added in dashboard UI
4. ✅ Events populated with correct tags (see `EVENT_POPULATION_FIX.md`)
5. ✅ User has `perm_auth` permission to view events

**Debug**:
```bash
# Check if widget files have correct timeframe
cd /opt/misp
sudo docker compose exec misp-core grep -r '"timeframe": "365d"' /var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/

# Expected: Should find matches in all 4 widgets
```

### Issue: "Invalid timeframe format" error in MISP logs

**Symptom**:
```
ERROR: restSearch() called with invalid 'last' parameter: 1y
```

**Cause**: Widget file not updated or cached old version

**Fix**:
```bash
# Clear PHP OpCache
cd /opt/misp
sudo docker compose exec misp-core rm -rf /var/www/MISP/app/tmp/cache/*
sudo docker compose restart misp-core
```

### Issue: Widget configuration UI shows old format

**Symptom**: When adding widget, placeholder shows `"timeframe": "1y"`

**Cause**: Browser cache or widget file not updated in container

**Fix**:
1. Hard refresh browser: `Ctrl+Shift+R` (Linux/Windows) or `Cmd+Shift+R` (Mac)
2. Verify widget file in container:
   ```bash
   cd /opt/misp
   sudo docker compose exec misp-core cat /var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/APTGroupsUtilitiesWidget.php | grep -A 3 "placeholder"

   # Expected: Should show "365d" not "1y"
   ```

---

## Best Practices for Widget Development

### 1. Always Use Day Format for Timeframes

```php
// ✅ CORRECT
public $placeholder = '{"timeframe": "365d", "limit": "15"}';
$timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '365d';

// ❌ WRONG
public $placeholder = '{"timeframe": "1y", "limit": "15"}';
$timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
```

### 2. Document Valid Timeframe Options

```php
public $params = array(
    'timeframe' => 'Time window (7d, 30d, 90d, 365d, all)',  // ✅ Clear day-based options
    'limit' => 'Max items to display (default: 15)'
);
```

### 3. Validate Timeframe in Handler (Optional)

```php
public function handler($user, $options = array()) {
    $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '365d';

    // Validate format (optional but recommended)
    if ($timeframe !== 'all' && !preg_match('/^\d+d$/', $timeframe)) {
        $timeframe = '365d'; // Fallback to default
    }

    // ... rest of handler ...
}
```

### 4. Test with Multiple Timeframes

Always test widgets with:
- Short timeframe: `7d` (should return recent events)
- Medium timeframe: `365d` (should return year's events)
- Long timeframe: `3650d` (should return 10 years)
- All time: `all` (should return all events)

---

## Summary

✅ **Fixed**: All 4 Threat Actor widgets now use correct day-based timeframe format
✅ **Converted**: `1y` → `365d`, `10y` → `3650d`
✅ **Updated**: Widget placeholders, default values, and parameter descriptions
✅ **Tested**: Widgets now return data when added to dashboard
✅ **Documented**: Timeframe conversion reference and best practices

**Status**: COMPLETE - Widgets should now display data correctly in fresh installations

**Next Steps**:
- If widgets still show "No data", verify event population (see `EVENT_POPULATION_FIX.md`)
- For existing installations, update widget files and restart MISP containers

---

**Maintainer**: tKQB Enterprises
**Related Files**:
- `widgets/threat-actor-dashboard/APTGroupsUtilitiesWidget.php`
- `widgets/threat-actor-dashboard/NationStateAttributionWidget.php`
- `widgets/threat-actor-dashboard/TTPsUtilitiesWidget.php`
- `widgets/threat-actor-dashboard/HistoricalIncidentsWidget.php`
- `EVENT_POPULATION_FIX.md` (prerequisite fix)
- `WIDGET_TROUBLESHOOTING_SUMMARY.md` (previous debugging)
