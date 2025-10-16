# Utilities Sector Dashboard - Quick Start Guide

**Version:** 1.0
**Date:** 2025-10-16
**Target:** Docker-based MISP installations

---

## 🚀 One-Command Installation

```bash
cd /home/gallagher/misp-install/misp-install
sudo bash scripts/install-utilities-dashboard.sh
```

**That's it!** Your dashboard is now configured.

---

## 📊 What You Get

After installation, your MISP dashboard will have an optimized 2-column layout:

### Dashboard Layout

```
┌────────────────────────────────────────────────┐
│ Event      │  Utilities Threat Heat Map       │
│ Stream     │  (World Map - 6×9)               │
│ (2×5)      │                                  │
│            │  Geographic visualization        │
│────────────│  of ICS/utilities threats        │
│ Trending   │                                  │
│ Attributes │                                  │
│ (2×2)      │                                  │
│────────────│                                  │
│ Trending   │                                  │
│ Tags       │                                  │
│ (2×6)      │                                  │
└────────────────────────────────────────────────┘
```

### Widget Details

**Left Column (narrow):**
1. **Event Stream** (2×5) - 5 most recent events, real-time updates
2. **Trending Attributes** (2×2) - Top 10 IOCs from last 7 days
3. **Trending Tags** (2×6) - Most used tags from last 7 days

**Right Column (wide):**
4. **Utilities Threat Heat Map** (6×9) - Large world map showing geographic distribution of threats targeting utilities sector
   - **Updates**: Auto-refreshes every 60 seconds
   - **Filter**: ICS sector events from last 7 days
   - **Limit**: 1000 events analyzed

---

## 🌐 Access Your Dashboard

1. **Open MISP in browser**:
   ```
   https://misp-test.lan
   ```

2. **Login**:
   - Email: `admin@tkqb.local`
   - Password: `MISPadmin2025!@#`

3. **View Dashboard**:
   - Click **"Dashboard"** in the top menu
   - Your widgets should be visible immediately

4. **If widgets don't appear**:
   - Refresh page (Ctrl+R or F5)
   - Clear browser cache (Ctrl+Shift+Delete)
   - Wait 30 seconds for MISP to load widget data

---

## 🧪 Test With Sample Data

The heat map widget needs events with country tags to display data.

### Create a test event:

```bash
# Get your API key
API_KEY=$(sudo grep "API KEY:" /opt/misp/PASSWORDS.txt | awk '{print $3}')
MISP_URL="https://misp-test.lan"

# Create test event
curl -k -X POST "${MISP_URL}/events/add" \
  -H "Authorization: ${API_KEY}" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "Event": {
      "info": "Test ICS Event - Widget Validation",
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
          "value": "192.0.2.100",
          "to_ids": true
        }
      ]
    }
  }'
```

### Verify widget shows data:

1. Wait 60 seconds (for cache to expire)
2. Refresh dashboard
3. Heat map should show United States highlighted
4. Hover over US to see event count tooltip

---

## 🎨 Customize Your Dashboard

### Change widget configuration:

1. Click **"Dashboard"** → (look for edit option if available)
2. If edit isn't available, reconfigure via API:

```bash
cd /home/gallagher/misp-install/misp-install/widgets/utilities-sector

# Export current dashboard
python3 configure-dashboard.py --export-only

# Edit dashboard-backup.json to customize

# Import modified dashboard
python3 configure-dashboard.py --api-key YOUR_API_KEY --misp-url https://misp-test.lan
```

### Widget configuration options:

**Utilities Threat Heat Map:**
```json
{
  "timeframe": "7d",    // Options: 1d, 7d, 30d, 90d, 1y
  "limit": "1000",      // Max events to analyze
  "sector_tag": "ics:sector"  // Tag filter
}
```

**Examples:**

- **Last 24 hours, energy sector only:**
  ```json
  {
    "timeframe": "1d",
    "limit": "500",
    "sector_tag": "ics:sector=\"energy\""
  }
  ```

- **Last 30 days, all ICS events:**
  ```json
  {
    "timeframe": "30d",
    "limit": "2000",
    "sector_tag": "ics:"
  }
  ```

---

## 🔧 Troubleshooting

### Dashboard is blank

**Cause**: No events match filter criteria

**Solution**: Create test events (see above) or adjust filters to broader criteria

---

### Heat map shows no countries

**Cause**: Events don't have country tags

**Solution**: Add country tags to events:
- Via web UI: Event → Edit → Add Tag → Search "country:"
- Via API: Include `{"name": "country:US"}` in event tags

---

### "UtilitiesThreatHeatMapWidget" not found error

**Cause**: Widget not installed correctly

**Solution**: Reinstall widget:
```bash
cd /home/gallagher/misp-install/misp-install/widgets/utilities-sector
sudo bash install-widget-docker.sh
```

---

### Widget shows old data

**Cause**: Cache hasn't expired yet

**Solution**:
- Wait 5 minutes (widget cache lifetime)
- Or manually clear cache:
  ```bash
  sudo docker exec misp-misp-core-1 rm -rf \
    /var/www/MISP/app/tmp/cache/models/* \
    /var/www/MISP/app/tmp/cache/persistent/*
  ```

---

### Dashboard configuration resets

**Cause**: MISP dashboard is user-specific

**Solution**: Ensure you're logged in as the correct user (admin@tkqb.local)

---

## 📁 Files Installed

```
/var/www/MISP/app/Lib/Dashboard/Custom/
└── UtilitiesThreatHeatMapWidget.php

/home/gallagher/misp-install/misp-install/
├── scripts/
│   └── install-utilities-dashboard.sh
└── widgets/utilities-sector/
    ├── UtilitiesThreatHeatMapWidget.php
    ├── configure-dashboard.py
    ├── install-widget-docker.sh
    ├── INSTALLATION.md
    ├── VALIDATION_CHECKLIST.md
    ├── KNOWN_LIMITATIONS.md
    └── README.md
```

---

## 🔄 Backup & Restore

### Backup current dashboard:

```bash
cd /home/gallagher/misp-install/misp-install/widgets/utilities-sector
python3 configure-dashboard.py --export-only
# Saves to: dashboard-backup.json
```

### Restore from backup:

```bash
# Import saved configuration
python3 configure-dashboard.py --api-key YOUR_API_KEY --misp-url https://misp-test.lan
```

---

## 📚 Additional Documentation

- **[README.md](README.md)** - Complete widget documentation
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation guide
- **[VALIDATION_CHECKLIST.md](VALIDATION_CHECKLIST.md)** - Testing checklist
- **[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)** - Known issues and limitations

---

## 🆘 Getting Help

**Check logs:**
```bash
# MISP error log
sudo docker exec misp-misp-core-1 tail -50 /var/www/MISP/app/tmp/logs/error.log

# MISP debug log
sudo docker exec misp-misp-core-1 tail -50 /var/www/MISP/app/tmp/logs/debug.log
```

**Test API connectivity:**
```bash
API_KEY=$(sudo grep "API KEY:" /opt/misp/PASSWORDS.txt | awk '{print $3}')
curl -k -H "Authorization: ${API_KEY}" https://misp-test.lan/users/view/me
```

**Verify widget file:**
```bash
sudo docker exec misp-misp-core-1 ls -la \
  /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php
```

**GitHub Issues:**
- https://github.com/gforce-gallagher-01/misp-install/issues

---

**Last Updated:** 2025-10-16
**Maintainer:** tKQB Enterprises
