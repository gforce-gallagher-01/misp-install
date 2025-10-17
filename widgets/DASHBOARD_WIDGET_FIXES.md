# Dashboard Widget Fixes

This document tracks critical fixes applied during widget installation to ensure proper functionality.

## Fix 1: Abstract Class Removal

**Problem**: MISP's dashboard loader (`/var/www/MISP/app/Model/Dashboard.php`) scans all `.php` files in the Custom widget directory and attempts to instantiate them. When abstract base classes are present, PHP throws a fatal error:

```
Error: Cannot instantiate abstract class BaseUtilitiesWidget
```

This breaks the entire "Add Widget" functionality in the dashboard UI.

**Root Cause**:
- MISP's `Dashboard::loadAllWidgets()` method does directory scan + class instantiation
- It doesn't check if a class is abstract before instantiation
- Abstract classes in Custom directory cause PHP fatal errors

**Solution**: Remove all abstract base classes from `/var/www/MISP/app/Lib/Dashboard/Custom/` after widget installation.

**Abstract Classes Removed**:
- `BaseUtilitiesWidget.php` - Base class for utilities sector widgets
- `BaseWidget.php` - Generic widget base class (if present)
- `AbstractWidget.php` - Abstract widget template (if present)

**Implementation**:
- Applied in Phase 11.11 (`phase_11_11_utilities_dashboards.py`)
- Method: `_remove_abstract_classes()`
- Executed after widget installation, before wildcard fixes

**Testing**: Verify "Add Widget" button works in dashboard UI without PHP errors.

---

## Fix 2: Wildcard Tag Matching

**Problem**: Widget queries using `'ics:'` as a tag filter don't match any events, even though events have tags like `ics:attack-target="plc"`.

**Root Cause**: MISP's `restSearch` API requires explicit wildcard syntax. The tag `'ics:'` is treated as a literal tag name, NOT as a prefix match.

**Solution**: Change all instances of `'ics:'` to `'ics:%'` in widget PHP code to enable wildcard matching.

**Example**:
```php
// BEFORE (broken - no matches)
$filters = array(
    'tags' => array('ics:'),
);

// AFTER (fixed - matches all ics:* tags)
$filters = array(
    'tags' => array('ics:%'),
);
```

**Affected Widgets**: 18 widgets across all 5 dashboard sets

**Implementation**:
- Applied in Phase 11.11 (`phase_11_11_utilities_dashboards.py`)
- Method: `_apply_widget_fixes()`
- Uses `sed` to replace `'ics:'` with `'ics:%'` in all affected widgets

**Testing**: Verify widgets return data from events with `ics:` prefixed tags.

---

## Fix 3: Tag vs EventTag Structure Handling

**Problem**: Some widgets check `$event['EventTag']` but MISP API returns `$event['Tag']` in restSearch responses.

**Root Cause**: Inconsistent tag structure between different MISP API endpoints:
- `/events/restSearch` returns `$event['Tag']` (direct array)
- `/events/view/:id` returns `$event['EventTag']` (wrapped array)

**Solution**: Update widget code to check both structures:

```php
// Check both Tag and EventTag structures
$tags = array();
if (!empty($event['Tag'])) {
    $tags = $event['Tag'];
} elseif (!empty($event['EventTag'])) {
    $tags = $event['EventTag'];
}

foreach ($tags as $tagData) {
    // Handle both Tag array (direct) and EventTag array (wrapped)
    $tagName = isset($tagData['name']) ? $tagData['name'] :
               (isset($tagData['Tag']['name']) ? $tagData['Tag']['name'] : '');
    // ... process tag
}
```

**Affected Widgets**:
- APTGroupsUtilitiesWidget.php
- NationStateAttributionWidget.php
- TTPsUtilitiesWidget.php
- HistoricalIncidentsWidget.php

**Implementation**: Fixed in widget source files in `widgets/threat-actor-dashboard/`

**Testing**: Verify widgets correctly extract tags from API responses.

---

## Troubleshooting Guide

### Widgets Show "No Data"

**Checklist**:
1. ✅ Events exist with proper tags (check via API: `/events/restSearch`)
2. ✅ Events are published (`published: 1`)
3. ✅ Widget queries use wildcard syntax (`ics:%` not `ics:`)
4. ✅ Widget handles both `Tag` and `EventTag` structures
5. ✅ No abstract classes in Custom directory (breaks Add Widget)
6. ✅ PHP cache cleared after widget installation
7. ✅ Container restarted after widget changes

### "Add Widget" Button Broken

**Symptom**: Clicking "Add Widget" button shows error or doesn't load widget list

**Diagnosis**: Check PHP error log:
```bash
sudo docker exec misp-misp-core-1 tail -50 /var/www/MISP/app/tmp/logs/error.log | grep -i "abstract\|widget"
```

**Fix**: Remove abstract classes from Custom directory (see Fix 1)

### Widget Execution Fails

**Symptom**: Widget displays error message or shows "Loading..." indefinitely

**Diagnosis**: Check PHP error log during widget refresh:
```bash
sudo docker exec misp-misp-core-1 tail -f /var/www/MISP/app/tmp/logs/error.log
```

**Common Issues**:
- Missing `includeEventTags` in restSearch query
- Incorrect tag syntax in query
- PHP syntax errors in widget code
- Missing required methods (`handler`, `checkPermissions`)

---

## Testing Commands

```bash
# 1. Verify widgets installed
sudo docker exec misp-misp-core-1 ls -la /var/www/MISP/app/Lib/Dashboard/Custom/ | grep -i "apt\|nation\|ttps\|historical"

# 2. Check for abstract classes (should be empty)
sudo docker exec misp-misp-core-1 find /var/www/MISP/app/Lib/Dashboard/Custom/ -name "Base*.php" -o -name "Abstract*.php"

# 3. Verify wildcard fixes applied
sudo docker exec misp-misp-core-1 grep -n "'ics:%'" /var/www/MISP/app/Lib/Dashboard/Custom/APTGroupsUtilitiesWidget.php

# 4. Test widget execution (simulates PHP logic)
python3 /tmp/debug_widget_execution.py

# 5. Check PHP errors
sudo docker exec misp-misp-core-1 tail -50 /var/www/MISP/app/tmp/logs/error.log | grep -i "widget\|dashboard"
```

---

## Version History

- **v1.0** (2025-10-17): Initial documentation
  - Fix 1: Abstract class removal
  - Fix 2: Wildcard tag matching
  - Fix 3: Tag/EventTag structure handling

---

**Maintainer**: tKQB Enterprises
**Related Files**:
- `phases/phase_11_11_utilities_dashboards.py`
- `widgets/threat-actor-dashboard/*.php`
- `scripts/populate-utilities-events.py`
