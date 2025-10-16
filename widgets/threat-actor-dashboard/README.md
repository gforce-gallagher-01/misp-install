# Threat Actor Dashboard Widgets

**Version**: 1.0
**Created**: 2025-10-16
**Author**: tKQB Enterprises
**Status**: Production Ready ✅

## Overview

This dashboard provides comprehensive threat actor intelligence focused on APT groups, campaigns, and nation-state attribution targeting utilities and critical infrastructure sectors.

## Widgets (5 Total)

### 1. APTGroupsUtilitiesWidget (BarChart)
**File**: `APTGroupsUtilitiesWidget.php`
**Render Type**: BarChart
**Size**: 6×5

**Purpose**: Tracks known APT groups targeting utilities sector with focus on ICS-specific actors.

**Tracked APT Groups** (12 total):
- **Dragonfly/DYMALLOY** - Russian APT targeting energy sector
- **XENOTIME** - Highly sophisticated ICS attacker (TRITON)
- **APT33/Elfin** - Iranian APT targeting energy and aviation
- **Sandworm/Voodoo Bear** - Ukrainian power grid attacks
- **APT41/Winnti** - Chinese APT with ICS targeting
- **Lazarus Group** - North Korean APT
- **APT10/MenuPass** - Chinese MSP supply chain attacks
- **APT29/Cozy Bear** - Russian sophisticated espionage
- **APT28/Fancy Bear** - Russian military intelligence
- **MAGNALLIUM** - ICS-focused threat actor
- **PALMERWORM** - Asia-based ICS attacker
- **VOLTZITE** - Emerging ICS threat actor

**Configuration**:
```json
{
    "timeframe": "1y",
    "limit": "15"
}
```

**Data Sources**:
- Events tagged with `misp-galaxy:threat-actor` + `ics:`
- Alias matching across APT group names

---

### 2. CampaignTrackingWidget (SimpleList)
**File**: `CampaignTrackingWidget.php`
**Render Type**: SimpleList
**Size**: 6×5

**Purpose**: Shows active threat campaigns targeting energy infrastructure with attribution and dates.

**Features**:
- Campaign name extraction from `misp-galaxy:campaign` tags
- Attribution to threat actors
- Event dates and details links
- Deduplication of campaigns

**Configuration**:
```json
{
    "timeframe": "90d",
    "limit": "10"
}
```

**Output Format**:
```
Campaign Name
Attribution - YYYY-MM-DD (Details)
```

---

### 3. NationStateAttributionWidget (BarChart)
**File**: `NationStateAttributionWidget.php`
**Render Type**: BarChart
**Size**: 6×5

**Purpose**: Nation-state attribution for ICS/utilities targeting with color-coded countries.

**Tracked Nations**:
- **Russia** (#c0392b) - APT28, APT29, Sandworm
- **China** (#e74c3c) - APT10, APT41
- **Iran** (#8e44ad) - APT33
- **North Korea** (#2980b9) - Lazarus Group
- **Unknown** (#95a5a6) - Unattributed attacks

**Configuration**:
```json
{
    "timeframe": "1y",
    "limit": "10"
}
```

**Attribution Logic**:
- Tag keyword matching (country names, APT groups)
- APT group to nation-state mapping
- Fallback to "Unknown" for unattributed events

---

### 4. TTPsUtilitiesWidget (BarChart)
**File**: `TTPsUtilitiesWidget.php`
**Render Type**: BarChart
**Size**: 6×5

**Purpose**: Tactics, Techniques, and Procedures observed in utilities sector attacks, mapped to MITRE ATT&CK for ICS.

**Tracked TTPs** (15 techniques):

**Initial Access**:
- Spearphishing
- Watering Hole

**Execution & Persistence**:
- Remote Access Tools (RAT, TeamViewer, VNC)

**Lateral Movement**:
- Lateral Movement (PSExec, WMI, Pass-the-Hash)
- Credential Dumping (Mimikatz, LSASS)

**Collection**:
- Screen Capture

**ICS-Specific**:
- HMI/SCADA Interaction
- PLC Programming
- Modbus Manipulation
- DNP3 Manipulation

**Impact**:
- Denial of Service
- Loss of View
- Loss of Control
- Manipulation of Control
- Firmware Modification

**Configuration**:
```json
{
    "timeframe": "1y",
    "limit": "15"
}
```

---

### 5. HistoricalIncidentsWidget (SimpleList)
**File**: `HistoricalIncidentsWidget.php`
**Render Type**: SimpleList
**Size**: 12×5 (full width)

**Purpose**: Timeline of significant ICS security incidents affecting utilities and critical infrastructure.

**Known Incidents Tracked**:
- **Ukraine Power Grid (2015)** - Sandworm
- **Ukraine Power Grid (2016)** - Sandworm
- **Industroyer/Crashoverride (2016)** - Sandworm
- **TRITON/Saudi Aramco (2017)** - XENOTIME
- **Stuxnet/Natanz (2010)** - Unknown
- **Dragonfly 2.0 Campaign (2017)** - Dragonfly
- **Energetic Bear Campaign (2014)** - Dragonfly
- **BlackEnergy Campaign (2014)** - Sandworm
- **PIPEDREAM/Incontroller (2022)** - Unknown
- **Colonial Pipeline (2021)** - DarkSide
- **Oldsmar Water Treatment (2021)** - Unknown
- **Kemuri Water Company (2016)** - Unknown

**Configuration**:
```json
{
    "timeframe": "10y",
    "limit": "15",
    "sector_filter": "utilities"
}
```

**Sector Filters**:
- `utilities` - Energy, water, power
- `manufacturing` - Industrial facilities
- `all` - All sectors

---

## Dashboard Layout

```
┌────────────────────────────────────────┐
│ Row 7 (y=32):                          │
│ ┌────────────────┬──────────────────┐  │
│ │ APT Groups     │ Campaign Track   │  │
│ │ (6×5)          │ (6×5)            │  │
│ └────────────────┴──────────────────┘  │
├────────────────────────────────────────┤
│ Row 8 (y=37):                          │
│ ┌────────────────┬──────────────────┐  │
│ │ Nation-State   │ TTPs             │  │
│ │ (6×5)          │ (6×5)            │  │
│ └────────────────┴──────────────────┘  │
├────────────────────────────────────────┤
│ Row 9 (y=42):                          │
│ ┌────────────────────────────────────┐ │
│ │ Historical Incidents               │ │
│ │ (12×5)                             │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Installation

### Step 1: Install Widgets
```bash
cd /home/gallagher/misp-install/misp-install/widgets/threat-actor-dashboard
sudo bash install-threat-actor-widgets.sh
```

### Step 2: Configure Dashboard
**IMPORTANT**: Always use the master script to prevent widgets from disappearing:
```bash
cd /home/gallagher/misp-install/misp-install/scripts
python3 configure-all-dashboards.py --api-key YOUR_API_KEY --misp-url https://misp.local
```

### Step 3: Verify
1. Refresh MISP dashboard in browser (F5 or Ctrl+R)
2. Scroll down to see Threat Actor Dashboard section
3. Verify all 5 widgets are displayed

## Configuration Examples

### Focus on Recent Activity
```json
{
    "widget": "APTGroupsUtilitiesWidget",
    "config": {
        "timeframe": "30d",
        "limit": "10"
    }
}
```

### Long-Term Attribution Analysis
```json
{
    "widget": "NationStateAttributionWidget",
    "config": {
        "timeframe": "all",
        "limit": "20"
    }
}
```

### Comprehensive TTP Coverage
```json
{
    "widget": "TTPsUtilitiesWidget",
    "config": {
        "timeframe": "1y",
        "limit": "20"
    }
}
```

## Data Requirements

For widgets to display meaningful data, MISP needs:

1. **Events with Tags**:
   - `misp-galaxy:threat-actor` tags
   - `misp-galaxy:campaign` tags
   - `ics:` tags for ICS/SCADA relevance
   - `utilities:` tags for sector filtering

2. **Event Attributes**:
   - Published events only
   - Event info field with descriptions
   - EventTag relationships

3. **Threat Intelligence Feeds**:
   - MITRE ATT&CK for ICS
   - Nation-state attribution feeds
   - ICS-CERT advisories
   - Historical incident reports

## Troubleshooting

### Widget Shows "No Data"
1. Check if MISP has events with required tags
2. Verify API key has read permissions
3. Check timeframe - expand to "all" for testing
4. Review MISP cache: `rm -rf /var/www/MISP/app/tmp/cache/*`

### Widget Not Appearing
1. Verify widget was installed: `docker exec misp-misp-core-1 ls /var/www/MISP/app/Lib/Dashboard/Custom/`
2. Check PHP syntax: `php -l WidgetName.php`
3. Clear MISP cache
4. Re-run master dashboard configuration script

### Attribution Not Accurate
1. Update APT group alias mappings in widget code
2. Add custom nation-state mappings
3. Check event tags for consistency

## Performance Notes

- **Cache Lifetime**: 600 seconds (10 minutes)
- **Auto Refresh**: 300 seconds (5 minutes)
- **Query Limits**: 5000 events max per widget
- **Historical Data**: 1 hour cache (changes infrequently)

## Security Considerations

- All widgets require `perm_auth` role permission
- Only published events are displayed
- No sensitive data exposed in widget output
- Attribution data is based on MISP tags only

## Integration with Other Dashboards

This dashboard complements:

1. **Utilities Sector Overview** - Provides attacker context for infrastructure threats
2. **ICS/OT Dashboard** - Links TTPs to specific malware and vulnerabilities

**Recommended Workflow**:
1. Check Threat Actor Dashboard for attribution
2. Review ICS/OT Dashboard for technical IOCs
3. Correlate with Utilities Sector Overview for impact

## Version History

- **1.0** (2025-10-16): Initial release with 5 widgets
  - APT Groups tracking
  - Campaign monitoring
  - Nation-state attribution
  - TTP analysis
  - Historical incidents timeline

## References

- [MITRE ATT&CK for ICS](https://attack.mitre.org/matrices/ics/)
- [ICS-CERT Advisories](https://www.cisa.gov/uscert/ics)
- [MISP Galaxy Threat Actors](https://www.misp-project.org/galaxy.html)
- [Dragos Threat Actor Profiles](https://www.dragos.com/threat-intelligence/)

## Support

For issues or questions:
1. Review [MISP Documentation](https://www.misp-project.org/documentation/)
2. Check widget PHP syntax and logs
3. Verify API connectivity and permissions
4. Review MISP event data quality

---

**Last Updated**: 2025-10-16
**Status**: Production Ready ✅
**Total Widgets**: 5
**Dashboard Position**: Rows 7-9 (y=32-46)
