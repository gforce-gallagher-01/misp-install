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

### Prerequisites
- MISP 2.4.x installed
- Phase 11.8 (Utilities Sector configuration) completed
- ICS taxonomy enabled
- MITRE ATT&CK for ICS Galaxy enabled

### Installation Steps

1. **Copy widget files to MISP:**
   ```bash
   sudo cp widgets/utilities-sector/*.php /var/www/MISP/app/Lib/Dashboard/Custom/
   sudo chown -R www-data:www-data /var/www/MISP/app/Lib/Dashboard/Custom/
   ```

2. **Clear MISP cache:**
   ```bash
   sudo -u www-data /var/www/MISP/app/Console/cake Admin setSetting "MISP.background_jobs" true
   sudo -u www-data /var/www/MISP/app/Console/cake Admin clearCache
   ```

3. **Restart web server:**
   ```bash
   sudo systemctl restart apache2
   # OR
   sudo systemctl restart nginx
   ```

4. **Add widgets to dashboard:**
   - Navigate to MISP → Dashboard
   - Click "Add Widget"
   - Select from "Custom" category
   - Configure parameters
   - Save layout

### Automated Installation

Use the provided setup script:

```bash
sudo python3 scripts/install-utilities-dashboard.py
```

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

## Dashboard Layout Recommendations

### Recommended Grid Layout (12 columns)

```
┌──────────────────────────────────────────────────────┐
│  UtilitiesSectorStatsWidget (12 cols × 2 rows)      │
├──────────────────────────────────────────────────────┤
│  UtilitiesThreatHeatMapWidget                        │
│  (6 cols × 4 rows)                                   │
│                                    ICSProtocolsTarget│
│                                    Widget            │
│                                    (6 cols × 4 rows) │
├──────────────────────────────────────────────────────┤
│  CriticalInfrastructureBreakdown │ NERCCIPCompliance│
│  Widget (6 cols × 4 rows)        │ Widget           │
│                                   │ (6 cols × 4 rows)│
└──────────────────────────────────────────────────────┘
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
