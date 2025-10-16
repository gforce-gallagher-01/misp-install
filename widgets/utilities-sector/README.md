# Utilities Sector Dashboard Widgets for MISP

**Version:** 1.0
**Target MISP Version:** 2.4.x
**Created:** 2025-10-16

Custom dashboard widgets designed specifically for utilities sector threat intelligence monitoring, focusing on ICS/SCADA/OT environments.

## Overview

This collection provides 5 specialized widgets for the **Utilities Sector Overview Dashboard**, designed to give SOC teams real-time visibility into threats targeting critical energy infrastructure.

## Widgets Included

### 1. UtilitiesThreatHeatMapWidget.php
**Render Type:** WorldMap
**Description:** Real-time geographic heat map showing threat activity targeting utilities sector by region.

**Features:**
- Geographic distribution of threats
- Energy sector specific filtering
- ICS/SCADA incident highlighting
- NERC region overlay

**Parameters:**
- `timeframe`: Time window (1d, 7d, 30d)
- `sector`: Sector filter (utilities, energy, all)
- `threat_types`: Threat type filter (malware, apt, vulnerability)

### 2. ICSProtocolsTargetedWidget.php
**Render Type:** BarChart
**Description:** Bar chart showing top targeted ICS protocols (Modbus, DNP3, IEC 61850, etc.)

**Features:**
- Protocol-specific threat counts
- Trend analysis over time
- Vulnerability correlation
- Critical protocol highlighting

**Parameters:**
- `timeframe`: Time window for analysis
- `limit`: Number of protocols to display (default: 10)
- `sort`: Sort by (incidents, vulnerabilities, impact)

### 3. CriticalInfrastructureBreakdownWidget.php
**Render Type:** BarChart
**Description:** Breakdown of threats by critical infrastructure subsector (generation, transmission, distribution)

**Features:**
- Subsector threat distribution
- Asset type targeting (SCADA, HMI, PLC, RTU)
- NERC CIP asset category mapping
- Month-over-month trends

**Parameters:**
- `timeframe`: Analysis period
- `subsectors`: Subsector filter array
- `asset_types`: Asset type filter array

### 4. UtilitiesSectorStatsWidget.php
**Render Type:** Array
**Description:** Key statistics for utilities sector threat intelligence

**Features:**
- Total threats detected (24h, 7d, 30d)
- Active APT campaigns
- Critical vulnerabilities (ICS-specific)
- NERC CIP relevant events
- Feed update status

**Parameters:**
- `refresh_interval`: Auto-refresh delay (seconds)
- `stats_to_show`: Array of statistics to display

### 5. NERCCIPComplianceWidget.php
**Render Type:** SimpleList
**Description:** NERC CIP compliance monitoring showing recent events requiring attention

**Features:**
- CIP-related threat events
- Compliance gap identification
- Required action items
- Risk scoring

**Parameters:**
- `cip_standards`: Array of CIP standards to monitor (CIP-003 through CIP-011)
- `risk_threshold`: Minimum risk level to display
- `limit`: Maximum events to show

## Installation

### Quick Start (Recommended)

**One-command installation for Docker-based MISP:**

```bash
cd /home/gallagher/misp-install/misp-install
sudo bash scripts/install-utilities-dashboard.sh
```

This will:
1. ✅ Install the widget to MISP container
2. ✅ Configure your dashboard automatically
3. ✅ Backup existing dashboard
4. ✅ Add 4 widgets (including Utilities Sector Heat Map)

**Then refresh your browser** and go to Dashboard!

### Manual Installation

#### For Docker-based MISP:

```bash
cd widgets/utilities-sector
sudo bash install-widget-docker.sh
```

Then configure dashboard:
```bash
python3 configure-dashboard.py --api-key YOUR_API_KEY --misp-url https://your-misp-url
```

#### For Traditional MISP Installation:

1. **Copy widget files to MISP:**
   ```bash
   sudo cp widgets/utilities-sector/*.php /var/www/MISP/app/Lib/Dashboard/Custom/
   sudo chown -R www-data:www-data /var/www/MISP/app/Lib/Dashboard/Custom/
   ```

2. **Clear MISP cache:**
   ```bash
   sudo rm -rf /var/www/MISP/app/tmp/cache/models/*
   sudo rm -rf /var/www/MISP/app/tmp/cache/persistent/*
   ```

3. **Restart web server:**
   ```bash
   sudo systemctl restart apache2
   # OR
   sudo systemctl restart nginx
   ```

### Prerequisites
- MISP 2.4.x installed (Docker or traditional)
- Phase 11.8 (Utilities Sector configuration) completed (optional)
- ICS taxonomy enabled (optional but recommended)
- MITRE ATT&CK for ICS Galaxy enabled (optional but recommended)
- Python 3.6+ with `requests` module

## Widget Configuration Examples

### Example 1: 24-Hour Threat Heat Map
```json
{
    "timeframe": "1d",
    "sector": "utilities",
    "threat_types": ["malware", "apt"]
}
```

### Example 2: ICS Protocols (Weekly Analysis)
```json
{
    "timeframe": "7d",
    "limit": "10",
    "sort": "incidents"
}
```

### Example 3: NERC CIP Compliance Monitoring
```json
{
    "cip_standards": ["CIP-005", "CIP-007", "CIP-010"],
    "risk_threshold": "medium",
    "limit": "20"
}
```

## Dashboard Layout

### Current Layout (User-Optimized)

The automated installer configures this optimized 2-column layout:

```
┌────────────────────────────────────────────────────────┐
│ Event      │  Utilities Threat Heat Map               │
│ Stream     │  (World Map)                             │
│ (2×5)      │                                          │
│            │  (6×9)                                   │
│────────────│                                          │
│ Trending   │                                          │
│ Attributes │                                          │
│ (2×2)      │                                          │
│────────────│                                          │
│ Trending   │                                          │
│ Tags       │                                          │
│ (2×6)      │                                          │
│            │                                          │
│            │                                          │
└────────────────────────────────────────────────────────┘

Left column (narrow):  Recent activity and trending indicators
Right column (wide):   Large heat map visualization
```

**Position coordinates:**
- Event Stream: x=1, y=0, width=2, height=5
- Trending Attributes: x=1, y=5, width=2, height=2
- Trending Tags: x=1, y=7, width=2, height=6
- Utilities Heat Map: x=3, y=0, width=6, height=9

### Full Utilities Dashboard (5 Widgets) - User-Optimized

Production layout with all 5 utilities sector widgets:

```
┌────────────────────────────────────────────────┐
│ Stats │ ICS Protocols Targeted                │
│ (2×3) │ (6×3)                                 │
├────────────────────────────────────────────────┤
│ Infrastructure  │ NERC CIP Compliance         │
│ Breakdown (6×5) │ (6×5)                       │
├────────────────────────────────────────────────┤
│ Utilities Threat Heat Map                     │
│ (Full Width - 12×9)                           │
│                                               │
└────────────────────────────────────────────────┘
```

**Position coordinates:**
- Stats: x=0, y=0, width=2, height=3
- ICS Protocols: x=2, y=0, width=6, height=3
- Infrastructure Breakdown: x=0, y=3, width=6, height=5
- NERC CIP Compliance: x=6, y=3, width=6, height=5
- Threat Heat Map: x=0, y=8, width=12, height=9

**Installation:**
```bash
cd /home/gallagher/misp-install/misp-install/widgets/utilities-sector
sudo bash install-all-widgets.sh
python3 configure-dashboard-full.py --api-key YOUR_KEY --misp-url https://your-misp
```

## Data Sources

These widgets aggregate data from:
- MISP events with ICS taxonomy tags
- MITRE ATT&CK for ICS techniques
- ICS-CERT advisories (Phase 11.10 feeds)
- E-ISAC threat intelligence
- CISA ICS alerts
- Utilities sector vendor bulletins

## Performance Considerations

- **Caching:** All widgets support caching (default: 5 minutes)
- **Auto-refresh:** Configurable refresh intervals (30s - 5m recommended)
- **Query optimization:** Widgets use indexed fields for performance
- **Large datasets:** Consider increasing PHP memory limit for complex queries

## Troubleshooting

### Widgets Not Appearing
```bash
# Check file permissions
ls -la /var/www/MISP/app/Lib/Dashboard/Custom/

# Check PHP syntax
sudo -u www-data php -l /var/www/MISP/app/Lib/Dashboard/Custom/UtilitiesThreatHeatMapWidget.php

# Check MISP logs
tail -f /var/www/MISP/app/tmp/logs/error.log
```

### Performance Issues
- Reduce `timeframe` parameter
- Increase `cacheLifetime` value
- Increase `autoRefreshDelay` value
- Add database indexes if needed

### No Data Displayed
- Verify Phase 11.8 is completed
- Check ICS taxonomy is enabled
- Verify feeds are updating
- Check event tagging is correct

## Customization

### Modifying Widget Parameters

Edit the widget PHP file and update the `$params` array:

```php
public $params = array(
    'timeframe' => 'Time window for analysis (1d, 7d, 30d)',
    'limit' => 'Maximum items to display',
    'custom_param' => 'Your custom parameter description'
);
```

### Changing Widget Appearance

Modify the `$render` type:
- `SimpleList`: List format
- `BarChart`: Bar chart visualization
- `WorldMap`: Geographic heat map
- `Array`: Key-value statistics
- `MultiLineChart`: Line graph

## Security Considerations

- **Permission checks:** All widgets implement `checkPermissions()` method
- **Input validation:** Widget parameters are sanitized
- **SQL injection protection:** Uses MISP's query builder
- **XSS protection:** Output is escaped

## Known Limitations

See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) for detailed documentation of:
- Geographic data requirements
- GeoIP lookup implementation needs
- REST API event limits
- Tag-based filtering requirements
- NERC region overlay limitations
- Performance considerations

## Support

For issues or feature requests:
- GitHub Issues: https://github.com/gforce-gallagher-01/misp-install/issues
- MISP Community: https://www.misp-project.org/community/

## License

Same license as MISP (AGPL-3.0)

## Authors

- tKQB Enterprises
- Utilities Sector MISP Community

## Changelog

### v1.0 (2025-10-16)
- Initial release
- 5 custom widgets for utilities sector
- Full NERC CIP compliance monitoring
- ICS/SCADA/OT specific visualizations

---

**Last Updated:** 2025-10-16
**Maintainer:** tKQB Enterprises
