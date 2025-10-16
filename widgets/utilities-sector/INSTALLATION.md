# Utilities Sector Dashboard Widget - Installation & Testing Guide

**Version:** 1.0
**Date:** 2025-10-16

## Prerequisites Checklist

Before installing, verify:

- [ ] MISP 2.4.x is installed and running
- [ ] You have SSH/shell access to the MISP server
- [ ] You have sudo privileges
- [ ] MISP web interface is accessible
- [ ] Phase 11.8 (Utilities Sector) is completed (optional but recommended)
- [ ] ICS taxonomy is enabled in MISP

## Installation Steps

### Step 1: Verify MISP Installation

```bash
# Check MISP is running
cd /var/www/MISP && sudo -u www-data ./app/Console/cake version

# Expected output: MISP version 2.4.xxx
```

### Step 2: Copy Widget File

```bash
# Navigate to your misp-install directory
cd /home/gallagher/misp-install/misp-install

# Copy widget to MISP custom dashboard directory
sudo cp widgets/utilities-sector/UtilitiesThreatHeatMapWidget.php \
    /var/www/MISP/app/Lib/Dashboard/Custom/

# Set correct permissions
sudo chown www-data:www-data \
    /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php

# Set correct file permissions
sudo chmod 644 \
    /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
```

### Step 3: Verify File Placement

```bash
# List custom widgets
ls -la /var/www/MISP/app/Lib/Dashboard/Custom/

# You should see: UtilitiesThreatHeatMapWidget.php
```

### Step 4: Clear MISP Cache

```bash
# Clear MISP cache to recognize new widget
sudo -u www-data /var/www/MISP/app/Console/cake Admin clearCache

# Alternative: Clear tmp cache manually
sudo rm -rf /var/www/MISP/app/tmp/cache/models/*
sudo rm -rf /var/www/MISP/app/tmp/cache/persistent/*
```

### Step 5: Restart Web Server

```bash
# For Apache
sudo systemctl restart apache2

# For Nginx + PHP-FPM
sudo systemctl restart php7.4-fpm  # Adjust PHP version
sudo systemctl restart nginx
```

## Verification Steps

### 1. Check Widget Appears in MISP

1. Log into MISP web interface
2. Navigate to: **Dashboard** (top menu)
3. Click **"Edit Dashboard"** button (top right)
4. Click **"Add Widget"** button
5. Look for **"Custom"** section
6. Verify **"Utilities Sector Threat Heat Map"** appears in the list

### 2. Add Widget to Dashboard

1. Click on **"Utilities Sector Threat Heat Map"**
2. Widget configuration modal should appear
3. Enter configuration (or leave defaults):
   ```json
   {
       "timeframe": "7d",
       "limit": "1000",
       "sector_tag": "ics:sector"
   }
   ```
4. Click **"Add Widget"**
5. Widget should appear on your dashboard

### 3. Test Widget Functionality

**If Data Appears:**
- ✅ Widget is working correctly
- You should see a world map with country heat map data

**If "No Data" Message:**
- This is normal if you don't have events with country tags yet
- See "Adding Test Data" section below

**If Error Messages:**
- Check MISP error logs (see Troubleshooting section)

## Adding Test Data (Optional)

To test the widget with sample data:

```bash
# Create a test event via MISP API
curl -k -X POST https://localhost/events/add \
  -H "Authorization: YOUR_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "Event": {
      "info": "Test ICS Event for Widget",
      "distribution": "1",
      "threat_level_id": "2",
      "analysis": "1",
      "Tag": [
        {"name": "ics:sector=\"energy\""},
        {"name": "country:US"}
      ],
      "Attribute": [
        {
          "category": "Network activity",
          "type": "ip-dst",
          "value": "192.0.2.1",
          "to_ids": true
        }
      ]
    }
  }'
```

## Troubleshooting

### Widget Not Appearing

**Check PHP syntax:**
```bash
php -l /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
```

**Check MISP logs:**
```bash
sudo tail -f /var/www/MISP/app/tmp/logs/error.log
sudo tail -f /var/www/MISP/app/tmp/logs/debug.log
```

**Check web server logs:**
```bash
# Apache
sudo tail -f /var/log/apache2/error.log

# Nginx
sudo tail -f /var/log/nginx/error.log
```

**Check file permissions:**
```bash
ls -la /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php

# Should be: -rw-r--r-- 1 www-data www-data
```

### Widget Shows But No Data

**Check if you have events with appropriate tags:**
```bash
sudo -u www-data /var/www/MISP/app/Console/cake Event searchAttributes \
  --tags="ics:sector"
```

**Check widget parameters:**
- Try increasing `limit` parameter
- Try different `timeframe` (e.g., "30d" instead of "7d")
- Try different `sector_tag` (e.g., "tlp:white")

**Enable debug mode:**
1. Go to MISP → Administration → Server Settings
2. Find `debug` setting
3. Temporarily set to `1` or `2`
4. Check `/var/www/MISP/app/tmp/logs/debug.log`

### Permission Errors

**Reset permissions on entire Custom directory:**
```bash
sudo chown -R www-data:www-data /var/www/MISP/app/Lib/Dashboard/Custom/
sudo chmod -R 755 /var/www/MISP/app/Lib/Dashboard/Custom/
sudo chmod 644 /var/www/MISP/app/Lib/Dashboard/Custom/*.php
```

### Widget Causes PHP Errors

**Check PHP error log:**
```bash
# Find PHP error log location
php -i | grep error_log

# Tail the log
sudo tail -f /path/to/php_error.log
```

**Common issues:**
1. **JsonTool class not found** - Check MISP version (needs 2.4.x)
2. **ClassRegistry error** - Verify CakePHP is working
3. **Permission denied** - Check file ownership

## Uninstallation

To remove the widget:

```bash
# Remove widget file
sudo rm /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php

# Clear cache
sudo -u www-data /var/www/MISP/app/Console/cake Admin clearCache

# Restart web server
sudo systemctl restart apache2  # or nginx
```

## Widget Configuration Reference

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeframe` | string | `"7d"` | Time window: 1d, 7d, 30d, 90d, 1y |
| `limit` | integer | `1000` | Max events to analyze |
| `sector_tag` | string | `"ics:sector"` | Tag filter for sector |

### Example Configurations

**Last 24 hours, energy sector only:**
```json
{
    "timeframe": "1d",
    "limit": "500",
    "sector_tag": "ics:sector=\"energy\""
}
```

**Last 30 days, all ICS events:**
```json
{
    "timeframe": "30d",
    "limit": "2000",
    "sector_tag": "ics:"
}
```

**Last 90 days, water sector:**
```json
{
    "timeframe": "90d",
    "limit": "5000",
    "sector_tag": "ics:sector=\"water\""
}
```

## Performance Notes

- **Cache**: Widget caches results for 5 minutes (`cacheLifetime = 300`)
- **Auto-refresh**: Widget auto-refreshes every 60 seconds (`autoRefreshDelay = 60`)
- **Limits**: Keep `limit` under 5000 for good performance
- **Timeframe**: Shorter timeframes (1d, 7d) perform better than longer ones

## Next Steps

After successfully installing this widget:

1. Review the widget output and adjust parameters
2. Create additional test events with country tags
3. Consider installing the remaining 4 widgets:
   - ICS Protocols Targeted Widget
   - Critical Infrastructure Breakdown Widget
   - Utilities Sector Stats Widget
   - NERC CIP Compliance Widget

## Support

For issues:
- Check MISP community forums
- Review MISP documentation: https://www.circl.lu/doc/misp/
- Create GitHub issue: https://github.com/gforce-gallagher-01/misp-install/issues

---

**Last Updated:** 2025-10-16
**Maintainer:** tKQB Enterprises
