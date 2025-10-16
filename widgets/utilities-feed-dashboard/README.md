# Utilities Feed Dashboard Widgets

**Version**: 1.0
**Created**: 2025-10-16
**Author**: tKQB Enterprises
**Status**: Production Ready ✅

## Overview

This dashboard provides comprehensive monitoring of threat intelligence feeds specific to utilities and critical infrastructure, including ICS-CERT advisories, CISA alerts, vendor security bulletins, zero-day vulnerabilities, and feed health status.

## Widgets (5 Total)

### 1. ICSCERTAdvisoryWidget (SimpleList)
**File**: `ICSCERTAdvisoryWidget.php`
**Render Type**: SimpleList
**Size**: 6×5

**Purpose**: Recent ICS-CERT advisories affecting utilities sector with severity, CVE count, and affected vendors.

**Features**:
- Advisory ID extraction (ICSA-XX-XXX-XX format)
- Severity indicators ([CRIT], [HIGH], [MED], [LOW])
- CVE counting from tags and attributes
- Vendor detection (Siemens, Schneider, ABB, Rockwell, GE, etc.)
- Event date tracking

**Configuration**:
```json
{
    "timeframe": "30d",
    "limit": "15",
    "severity_filter": "all"
}
```

**Severity Filters**:
- `all` - All severities
- `critical` - Critical only
- `high` - High severity
- `medium` - Medium severity

**Output Format**:
```
ICSA-23-166-01
[HIGH] | Siemens | 3 CVEs | 2023-06-15 (View)
```

---

### 2. CISAUtilitiesAlertsWidget (SimpleList)
**File**: `CISAUtilitiesAlertsWidget.php`
**Render Type**: SimpleList
**Size**: 6×5

**Purpose**: CISA alerts and advisories specific to utilities and energy sector critical infrastructure.

**Features**:
- Alert type classification (Alert, Advisory, Analysis)
- Alert ID extraction (AA/AB/MAR format)
- Threat level indicators
- Utilities sector filtering

**Configuration**:
```json
{
    "timeframe": "30d",
    "limit": "10",
    "alert_type": "all"
}
```

**Alert Type Filters**:
- `all` - All types
- `alert` - Cybersecurity alerts only
- `advisory` - Advisories only
- `analysis` - Malware analysis reports

**Output Format**:
```
AA23-257A
Alert | High | 2023-09-14 (View)
```

---

### 3. VendorSecurityBulletinsWidget (BarChart)
**File**: `VendorSecurityBulletinsWidget.php`
**Render Type**: BarChart
**Size**: 6×5

**Purpose**: Security bulletins from major ICS vendors showing bulletin counts by vendor.

**Tracked Vendors** (12 total):
- **Siemens** (#009999) - SIMATIC, SINUMERIK products
- **Schneider Electric** (#3dcd58) - Modicon, Triconex
- **ABB** (#ff000f) - AC800M, System 800xA
- **Rockwell Automation** (#e4002b) - Allen-Bradley, ControlLogix
- **GE Digital** (#005eb8) - Mark VIe, CIMPLICITY
- **Honeywell** (#da291c) - Experion, C300
- **Emerson** (#004b8d) - Ovation, DeltaV
- **Yokogawa** (#0067b1) - CENTUM, ProSafe-RS
- **OMRON** (#0071c5) - SYSMAC
- **Mitsubishi Electric** (#e60012) - MELSEC
- **Phoenix Contact** (#ff6600) - PLCnext
- **AVEVA** (#00a3e0) - Wonderware, System Platform

**Configuration**:
```json
{
    "timeframe": "90d",
    "limit": "10"
}
```

**Data Sources**:
- Events tagged with `ics:` or `scada:`
- Keyword matching on vendor names and product lines
- Event info and tag searching

---

### 4. ICSZeroDayTrackerWidget (SimpleList)
**File**: `ICSZeroDayTrackerWidget.php`
**Render Type**: SimpleList
**Size**: 6×5

**Purpose**: Zero-day and critical vulnerabilities in ICS/OT systems with CVSS scoring.

**Features**:
- CVE extraction from tags and event info
- CVSS score extraction and estimation
- Zero-day identification ([0-DAY] indicator)
- Critical vulnerability flagging ([CRIT] for CVSS >= 9.0)
- Vendor attribution
- Sorting by severity (zero-days first, then by CVSS)

**Configuration**:
```json
{
    "timeframe": "90d",
    "limit": "10",
    "min_cvss": "7.0"
}
```

**CVSS Thresholds**:
- 9.0-10.0: Critical
- 7.0-8.9: High
- 4.0-6.9: Medium
- 0.1-3.9: Low

**Output Format**:
```
[0-DAY] CVE-2023-1234
CVSS: 9.8 | Siemens | 2023-08-01 (Details)
```

---

### 5. FeedHealthMonitorWidget (BarChart)
**File**: `FeedHealthMonitorWidget.php`
**Render Type**: BarChart
**Size**: 12×5 (full width)

**Purpose**: Health monitoring for utilities sector threat intelligence feeds showing event counts per feed.

**Monitored Feeds** (10 critical feeds):
- **ICS-CERT** (#e74c3c) - Industrial control systems advisories
- **CISA Alerts** (#3498db) - Cybersecurity and Infrastructure Security Agency
- **NERC CIP** (#2ecc71) - Electric Reliability Organization standards
- **Utilities ISAC** (#f39c12) - Information Sharing and Analysis Center
- **E-ISAC** (#9b59b6) - Electricity sector ISAC
- **MITRE ATT&CK ICS** (#1abc9c) - ICS attack techniques
- **OT-CERT** (#34495e) - Operational technology alerts
- **Dragos WorldView** (#e67e22) - ICS/OT threat intelligence
- **Claroty Team82** (#16a085) - ICS vulnerability research
- **Industrial Cyber** (#c0392b) - ICS security news

**Configuration**:
```json
{
    "timeframe": "7d",
    "show_inactive": "false"
}
```

**Features**:
- Event counting per feed within timeframe
- Color-coded bar chart
- Optional display of inactive feeds (0 events)
- Tag pattern matching for feed identification

---

## Dashboard Layout

```
┌────────────────────────────────────────┐
│ Row 10 (y=47):                         │
│ ┌────────────────┬──────────────────┐  │
│ │ ICS-CERT       │ CISA Alerts      │  │
│ │ Advisory(6×5)  │ (6×5)            │  │
│ └────────────────┴──────────────────┘  │
├────────────────────────────────────────┤
│ Row 11 (y=52):                         │
│ ┌────────────────┬──────────────────┐  │
│ │ Vendor         │ Zero-Day         │  │
│ │ Bulletins(6×5) │ Tracker (6×5)    │  │
│ └────────────────┴──────────────────┘  │
├────────────────────────────────────────┤
│ Row 12 (y=57):                         │
│ ┌────────────────────────────────────┐ │
│ │ Feed Health Monitor                │ │
│ │ (12×5)                             │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Installation

### Step 1: Install Widgets
```bash
cd /home/gallagher/misp-install/misp-install/widgets/utilities-feed-dashboard
sudo bash install-feed-widgets.sh
```

### Step 2: Configure Dashboard
**IMPORTANT**: Always use the master script to prevent widgets from disappearing:
```bash
cd /home/gallagher/misp-install/misp-install/scripts
python3 configure-all-dashboards.py --api-key YOUR_API_KEY --misp-url https://misp.local
```

### Step 3: Verify
1. Refresh MISP dashboard in browser (F5 or Ctrl+R)
2. Scroll down to see Feed Dashboard section
3. Verify all 5 widgets are displayed

## Data Requirements

For widgets to display meaningful data, MISP needs:

1. **Feed Configuration**:
   - ICS-CERT advisory feeds enabled
   - CISA alert feeds configured
   - Vendor security bulletin feeds active
   - CVE feeds with ICS tagging

2. **Event Tags**:
   - `ics-cert:` or `icsa-` for ICS-CERT events
   - `cisa:` or `us-cert:` for CISA events
   - `cve:` for vulnerability tracking
   - `ics:` and `scada:` for vendor bulletins
   - `zero-day` for 0-day vulnerabilities

3. **Event Attributes**:
   - Published events only
   - CVE numbers in tags or attributes
   - CVSS scores in tags (optional, estimated if missing)
   - Vendor names in event info or tags

## Configuration Examples

### Focus on Critical Vulnerabilities Only
```json
{
    "widget": "ICSCERTAdvisoryWidget",
    "config": {
        "timeframe": "30d",
        "limit": "10",
        "severity_filter": "critical"
    }
}
```

### Track Recent Zero-Days
```json
{
    "widget": "ICSZeroDayTrackerWidget",
    "config": {
        "timeframe": "30d",
        "limit": "15",
        "min_cvss": "8.0"
    }
}
```

### Monitor All Feeds Including Inactive
```json
{
    "widget": "FeedHealthMonitorWidget",
    "config": {
        "timeframe": "7d",
        "show_inactive": "true"
    }
}
```

## Troubleshooting

### Widget Shows "No Data"
1. Check if threat intelligence feeds are enabled in MISP
2. Verify feed synchronization is working
3. Check if events have required tags (ics-cert:, cisa:, etc.)
4. Expand timeframe to test data availability
5. Review MISP feed configuration: Administration → Feeds

### Feed Health Shows Zero Events
1. Verify feed is actually configured in MISP
2. Check feed last sync time
3. Review feed fetch/pull results
4. Ensure feed events are being published
5. Check tag patterns match feed configuration

### CVSS Scores Not Displaying
1. Add `cvss:score=X.X` tags to vulnerability events
2. Ensure threat_level_id is set on events
3. Widget will estimate CVSS if not found (based on threat level)

### Vendor Not Detected
1. Update vendor keyword list in VendorSecurityBulletinsWidget.php
2. Add vendor product names to keywords array
3. Ensure vendor names appear in event info or tags

## Performance Notes

- **Cache Lifetime**: 1800 seconds (30 minutes) for most widgets
- **Auto Refresh**: 600 seconds (10 minutes)
- **Query Limits**: 500-2000 events per widget
- **Feed Health**: 5 minute cache (real-time monitoring)

## Security Considerations

- All widgets require `perm_auth` role permission
- Only published events are displayed
- Feed health data is aggregated (no sensitive details)
- Advisory IDs and CVEs are public information

## Integration with Other Dashboards

This dashboard complements:

1. **ICS/OT Dashboard** - Provides source intelligence for vulnerabilities and malware
2. **Threat Actor Dashboard** - Links advisories to attribution data
3. **Utilities Sector Overview** - Provides feed-level context for sector threats

**Recommended Workflow**:
1. Check Feed Health Monitor for data availability
2. Review ICS-CERT and CISA alerts for recent threats
3. Track Zero-Day vulnerabilities affecting your vendors
4. Monitor Vendor Bulletins for patch availability
5. Correlate with Threat Actor Dashboard for attribution

## Maintenance

### Adding New Vendors
Edit `VendorSecurityBulletinsWidget.php`:
```php
'new_vendor' => array(
    'name' => 'Vendor Name',
    'color' => '#hexcolor',
    'keywords' => array('vendor', 'product1', 'product2')
)
```

### Adding New Feeds to Health Monitor
Edit `FeedHealthMonitorWidget.php`:
```php
'feed-key' => array('name' => 'Feed Name', 'color' => '#hexcolor')

// Add tag patterns
'feed-key' => array('tag1:', 'tag2:')
```

### Adjusting Alert Priorities
Modify severity/threat level mappings in widget handlers to match organizational priorities.

## Version History

- **1.0** (2025-10-16): Initial release with 5 widgets
  - ICS-CERT advisory monitoring
  - CISA alert tracking
  - Vendor bulletin aggregation
  - Zero-day vulnerability tracking
  - Feed health monitoring

## References

- [ICS-CERT Advisories](https://www.cisa.gov/uscert/ics/advisories)
- [CISA Alerts](https://www.cisa.gov/news-events/cybersecurity-advisories)
- [NERC CIP Standards](https://www.nerc.com/pa/Stand/Pages/CIPStandards.aspx)
- [MISP Feeds](https://www.misp-project.org/feeds/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/)

## Support

For issues or questions:
1. Review feed configuration in MISP Administration
2. Check widget PHP syntax and permissions
3. Verify API connectivity
4. Review event tagging consistency
5. Check MISP logs for feed errors

---

**Last Updated**: 2025-10-16
**Status**: Production Ready ✅
**Total Widgets**: 5
**Dashboard Position**: Rows 10-12 (y=47-61)
