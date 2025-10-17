# Widget Troubleshooting Summary

## Issue: Threat Actor Dashboard Widgets Showing "No Data"

**Date**: 2025-10-17
**Affected Widgets**: APTGroupsUtilitiesWidget, NationStateAttributionWidget, TTPsUtilitiesWidget, HistoricalIncidentsWidget

---

## Root Cause Analysis

After extensive debugging, we identified **ONE CRITICAL** issue that broke the widgets:

### Critical Issue: Abstract Base Class in Custom Directory

**Problem**: `BaseUtilitiesWidget.php` was an abstract PHP class located in `/var/www/MISP/app/Lib/Dashboard/Custom/`

**Why This Breaks Everything**:
1. MISP's dashboard loader (`Dashboard::loadAllWidgets()`) scans ALL `.php` files in Custom directory
2. It tries to instantiate EVERY class it finds
3. Abstract classes CANNOT be instantiated in PHP
4. Result: PHP fatal error that breaks the entire "Add Widget" UI

**Error Message**:
```
Error: [Error] Cannot instantiate abstract class BaseUtilitiesWidget
Request URL: /dashboards/getForm/add
```

**Impact**:
- ❌ "Add Widget" button completely broken
- ❌ Cannot add ANY widgets to dashboard
- ❌ Existing widgets may not load properly

---

## Solution Implemented

### 1. Prevention (Source Code)
- Renamed `widgets/BaseUtilitiesWidget.php` → `widgets/BaseUtilitiesWidget.php.DONOTINSTALL`
- This prevents the file from being installed in future deployments

### 2. Automated Fix (Installation Phase)
Added cleanup step to `phases/phase_11_11_utilities_dashboards.py`:

```python
def _remove_abstract_classes(self):
    """Remove abstract base classes from Custom widget directory."""
    abstract_classes = [
        "BaseUtilitiesWidget.php",
        "BaseWidget.php",
        "AbstractWidget.php"
    ]
    # Remove each file from /var/www/MISP/app/Lib/Dashboard/Custom/
```

**Execution Order**:
1. Install all 25 widgets
2. **Remove abstract classes** ← NEW STEP
3. Apply wildcard fixes
4. Configure dashboards via API

### 3. Documentation
Created comprehensive fix documentation:
- `widgets/DASHBOARD_WIDGET_FIXES.md` - Technical details
- This file - Executive summary

---

## Additional Fixes Applied

While debugging, we also fixed several other issues (though these were NOT the root cause):

### Fix A: Widget Code Updates
- ✅ Fixed Tag/EventTag structure handling in all 4 threat actor widgets
- ✅ Added missing APT aliases (CHERNOVITE, MERCURY, Volt Typhoon, LockBit)
- ✅ Fixed nation-state attribution mappings
- ✅ Removed incorrect tag requirements (utilities:, incident:)

### Fix B: Event Data
- ✅ Added threat-actor galaxy tags to all 31 ICS/OT events
- ✅ Recreated events with proper attribution (events 90-120)
- ✅ Verified all events are published

### Fix C: Wildcard Tag Matching
- ✅ Changed 'ics:' to 'ics:%' in 18 widgets
- ✅ Automated fix applied during Phase 11.11

---

## Testing & Verification

### Before Fix
```
❌ Click "Add Widget" → PHP error
❌ Widgets show "No data"
❌ Dashboard broken
```

### After Fix (Fresh Install)
```
✅ Click "Add Widget" → Widget list loads
✅ Add 4 threat actor widgets → Success
✅ Widgets populate with data immediately
✅ Dashboard fully functional
```

### Test Commands
```bash
# 1. Verify no abstract classes installed
sudo docker exec misp-misp-core-1 find /var/www/MISP/app/Lib/Dashboard/Custom/ -name "Base*.php"
# Expected: Empty (no results)

# 2. Verify widgets exist
sudo docker exec misp-misp-core-1 ls /var/www/MISP/app/Lib/Dashboard/Custom/ | grep -E "(APT|Nation|TTPs|Historical)"
# Expected: 4 widget files

# 3. Test Add Widget functionality
# Manual: Navigate to Dashboard → Click "Add Widget" → Should work
```

---

## Lessons Learned

### PHP Widget Development Best Practices

1. **Never put abstract classes in Custom directory**
   - MISP's loader instantiates ALL classes
   - Put base classes in separate `lib/` or `includes/` directory
   - Or use traits/interfaces instead of abstract classes

2. **MISP tag matching requires wildcards**
   - Use `'ics:%'` not `'ics:'`
   - MISP treats tags as literal strings without wildcard syntax

3. **Handle both Tag structures**
   - Check both `$event['Tag']` and `$event['EventTag']`
   - Different API endpoints return different structures

4. **Clear PHP cache after widget changes**
   - Delete `/var/www/MISP/app/tmp/cache/*`
   - Restart container to clear OpCache

---

## Files Modified

### Source Code
- `phases/phase_11_11_utilities_dashboards.py` - Added `_remove_abstract_classes()` method
- `widgets/BaseUtilitiesWidget.php` - Renamed to `.DONOTINSTALL`
- `widgets/threat-actor-dashboard/*.php` - Fixed Tag/EventTag handling

### Documentation
- `widgets/DASHBOARD_WIDGET_FIXES.md` - Technical fix documentation
- `WIDGET_TROUBLESHOOTING_SUMMARY.md` - This file

---

## Future Recommendations

### For Developers
1. Run widget installation with `--exclude utilities-dashboards` during testing
2. Test "Add Widget" functionality immediately after widget installation
3. Check PHP error logs for abstract class errors
4. Never commit abstract base classes to widget source directories

### For Deployment
1. Fresh installation now includes all fixes automatically
2. Existing installations: Run Phase 11.11 manually to apply fixes
3. Monitor PHP error logs for dashboard-related errors

---

## Quick Reference

### Problem: Widgets show "No data"
**Fix**: Check if abstract classes exist → Remove them → Restart container

### Problem: "Add Widget" broken
**Fix**: Same as above (abstract class issue)

### Problem: Widget query returns 0 events
**Fix**: Verify tag syntax uses wildcards (`ics:%`)

---

**Status**: ✅ RESOLVED
**Verified**: 2025-10-17 fresh installation - all 4 widgets working
**Maintainer**: tKQB Enterprises
