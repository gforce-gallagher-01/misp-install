# Widget Validation Checklist

**Widget:** UtilitiesThreatHeatMapWidget.php
**Version:** 1.0
**Date:** 2025-10-16

Use this checklist to systematically validate the widget installation and functionality.

---

## Pre-Installation Checks

- [ ] MISP 2.4.x is installed and accessible
- [ ] Have sudo/root access to MISP server
- [ ] MISP web interface is working (can login)
- [ ] ICS taxonomy is enabled in MISP
- [ ] Have at least one test event with country tags

---

## Installation Steps

- [ ] **Step 1**: Validate widget PHP syntax
  ```bash
  cd /home/gallagher/misp-install/misp-install/widgets/utilities-sector
  php -l UtilitiesThreatHeatMapWidget.php
  ```
  **Expected**: "No syntax errors detected"

- [ ] **Step 2**: Run installation script
  ```bash
  sudo bash install-widget.sh
  ```
  **Expected**: All 6 steps complete with green checkmarks

- [ ] **Step 3**: Verify file placement
  ```bash
  ls -la /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
  ```
  **Expected**: `-rw-r--r-- 1 www-data www-data ... UtilitiesThreatHeatMapWidget.php`

- [ ] **Step 4**: Check web server is running
  ```bash
  sudo systemctl status apache2
  # OR
  sudo systemctl status nginx
  ```
  **Expected**: "active (running)"

---

## MISP Web Interface Checks

- [ ] **Check 1**: Login to MISP
  - URL: `https://your-misp-domain/`
  - Login with admin credentials

- [ ] **Check 2**: Navigate to Dashboard
  - Click "Dashboard" in top menu
  - Verify dashboard page loads

- [ ] **Check 3**: Enter edit mode
  - Click "Edit Dashboard" button (top right)
  - Verify edit mode activates

- [ ] **Check 4**: Open Add Widget modal
  - Click "Add Widget" button
  - Verify modal opens with widget categories

- [ ] **Check 5**: Locate widget
  - Scroll to "Custom" section
  - Look for "Utilities Sector Threat Heat Map"

  **If NOT found:**
  - Widget did not register correctly
  - See "Troubleshooting: Widget Not Appearing" below

- [ ] **Check 6**: Widget appears in list
  - Widget title: "Utilities Sector Threat Heat Map"
  - Widget description visible
  - Can click to configure

---

## Widget Configuration Test

- [ ] **Test 1**: Add widget with default config
  - Click on "Utilities Sector Threat Heat Map"
  - Configuration modal should appear
  - Enter default config:
    ```json
    {
        "timeframe": "7d",
        "limit": "1000",
        "sector_tag": "ics:sector"
    }
    ```
  - Click "Add Widget"
  - Widget should appear on dashboard

- [ ] **Test 2**: Check widget renders
  - Widget displays without PHP errors
  - Shows world map (even if empty)
  - No JavaScript console errors

- [ ] **Test 3**: Test with "No Data" scenario
  - If no matching events exist, widget should show:
    - Empty map, OR
    - "No data available" message
  - This is NORMAL for new installations

---

## Data Validation Tests

### Test 4: Create test event

- [ ] **Step 1**: Navigate to Event Actions → Add Event
- [ ] **Step 2**: Create test event:
  - **Info**: "Test ICS Event - Widget Validation"
  - **Distribution**: Your Organisation Only
  - **Threat Level**: Medium
  - **Analysis**: Initial

- [ ] **Step 3**: Add attributes:
  - **Type**: ip-dst
  - **Category**: Network activity
  - **Value**: 192.0.2.1
  - **To IDS**: Yes

- [ ] **Step 4**: Add tags to event:
  - `ics:sector="energy"`
  - `country:US` (or your country code)

- [ ] **Step 5**: Publish event
  - Click "Publish Event"
  - Confirm publication

### Test 5: Verify widget shows data

- [ ] **Step 1**: Return to dashboard
- [ ] **Step 2**: Wait 60 seconds (for cache expiry)
- [ ] **Step 3**: Refresh dashboard or wait for auto-refresh
- [ ] **Step 4**: Check widget displays:
  - Country on map should be highlighted
  - Hover tooltip should show event count
  - Data should reflect test event

---

## Functional Tests

- [ ] **Test 6**: Test different timeframes
  - Edit widget configuration
  - Try: `"timeframe": "1d"`
  - Try: `"timeframe": "30d"`
  - Verify data changes appropriately

- [ ] **Test 7**: Test different limits
  - Edit widget configuration
  - Try: `"limit": "500"`
  - Verify widget still works

- [ ] **Test 8**: Test different sector tags
  - Edit widget configuration
  - Try: `"sector_tag": "ics:sector=\"energy\""`
  - Verify filtering works

- [ ] **Test 9**: Test auto-refresh
  - Leave dashboard open for 60+ seconds
  - Widget should auto-refresh (per `autoRefreshDelay = 60`)

---

## Performance Tests

- [ ] **Test 10**: Check MISP logs for errors
  ```bash
  sudo tail -50 /var/www/MISP/app/tmp/logs/error.log
  ```
  **Expected**: No PHP errors related to widget

- [ ] **Test 11**: Check page load time
  - Dashboard should load in <5 seconds
  - Widget should render in <2 seconds
  - No significant performance impact

- [ ] **Test 12**: Check with multiple events
  - Create 5-10 test events with different countries
  - Verify widget handles multiple data points
  - Map should show multiple countries highlighted

---

## Troubleshooting: Widget Not Appearing

If widget does NOT appear in "Add Widget" list:

### Check 1: PHP Syntax Error
```bash
php -l /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
```
**Fix**: Review syntax errors and correct them

### Check 2: File Permissions
```bash
ls -la /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
```
**Expected**: `-rw-r--r-- 1 www-data www-data`
**Fix**:
```bash
sudo chown www-data:www-data /var/www/MISP/app/Lib/Dashboard/Custom/*.php
sudo chmod 644 /var/www/MISP/app/Lib/Dashboard/Custom/*.php
```

### Check 3: Cache Not Cleared
```bash
sudo -u www-data /var/www/MISP/app/Console/cake Admin clearCache
```
**Fix**: Clear cache and restart web server

### Check 4: MISP Logs
```bash
sudo tail -100 /var/www/MISP/app/tmp/logs/error.log | grep -i widget
sudo tail -100 /var/www/MISP/app/tmp/logs/debug.log | grep -i widget
```
**Fix**: Review error messages for clues

### Check 5: Web Server Logs
```bash
# Apache
sudo tail -100 /var/log/apache2/error.log

# Nginx
sudo tail -100 /var/log/nginx/error.log
```
**Fix**: Look for PHP fatal errors or class loading issues

### Check 6: Class Name Mismatch
- Open `/var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php`
- Verify class name: `class UtilitiesThreatHeatMapWidget`
- Verify filename matches class name exactly

### Check 7: Required Methods
Verify widget class has:
- `public $title`
- `public $render`
- `public function handler($user, $options = array())`
- `public function checkPermissions($user)`

---

## Troubleshooting: Widget Shows But No Data

### Scenario 1: "No matching events"

**Cause**: No events match the filter criteria

**Fix**:
1. Verify you have events with appropriate tags
2. Try broader filter: `"sector_tag": "tlp:white"` (should match more events)
3. Check event publication status (only published events shown)

### Scenario 2: "No country data"

**Cause**: Events don't have country tags or attributes

**Fix**:
1. Add country tags to events: `country:US`, `country:CA`, etc.
2. Or add country-code attributes to events
3. Verify tag format matches pattern: `country[=:]([A-Z]{2})`

### Scenario 3: "Map shows but countries not highlighted"

**Cause**: Data format issue or JavaScript error

**Fix**:
1. Open browser console (F12) → Console tab
2. Look for JavaScript errors
3. Verify WorldMap widget is enabled in MISP
4. Check browser compatibility (Chrome/Firefox/Safari latest)

---

## Success Criteria

Widget installation is successful when:

✅ Widget appears in MISP "Add Widget" → "Custom" section
✅ Widget can be added to dashboard without errors
✅ Widget renders world map visualization
✅ Widget displays data when matching events exist
✅ Widget shows appropriate "no data" state when no events match
✅ No PHP errors in MISP logs
✅ No JavaScript errors in browser console
✅ Widget auto-refreshes every 60 seconds
✅ Performance is acceptable (<5s dashboard load)

---

## Reporting Issues

If validation fails, collect this information:

1. **MISP Version**:
   ```bash
   cd /var/www/MISP && sudo -u www-data ./app/Console/cake version
   ```

2. **PHP Version**:
   ```bash
   php -v
   ```

3. **Widget File Listing**:
   ```bash
   ls -la /var/www/MISP/app/Lib/Dashboard/Custom/
   ```

4. **Error Logs** (last 50 lines):
   ```bash
   sudo tail -50 /var/www/MISP/app/tmp/logs/error.log
   ```

5. **Browser Console Errors** (screenshot or copy/paste)

6. **Widget Configuration** (JSON used)

**Submit to**: https://github.com/gforce-gallagher-01/misp-install/issues

---

## Next Steps After Validation

Once this widget is validated and working:

1. ✅ Document any issues encountered
2. ✅ Update INSTALLATION.md with any additional troubleshooting
3. ✅ Proceed to develop remaining 4 widgets:
   - ICSProtocolsTargetedWidget.php
   - CriticalInfrastructureBreakdownWidget.php
   - UtilitiesSectorStatsWidget.php
   - NERCCIPComplianceWidget.php

---

**Last Updated**: 2025-10-16
**Maintainer**: tKQB Enterprises
