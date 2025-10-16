# Organizational Contribution Dashboard Widgets

**Version**: 1.0
**Created**: 2025-10-16
**Author**: tKQB Enterprises
**Status**: Production Ready ✅

## Overview

This dashboard provides comprehensive metrics and visualizations for utilities sector ISAC contribution tracking, sharing metrics, regional cooperation analysis, subsector breakdowns, and monthly trend analysis.

## Widgets (5 Total)

### 1. ISACContributionRankingsWidget (BarChart, 6×5)
Top contributing organizations to utilities ISAC threat intelligence sharing, ranked by event count. Features dynamic color generation based on organization name hashing for consistent visual identification.

### 2. SectorSharingMetricsWidget (SimpleList, 6×5)
Key metrics dashboard showing: Events Published, Total Attributes, Contributing Organizations, Average Events per Org, and Critical Threats. Includes period-over-period comparison showing percentage changes.

### 3. RegionalCooperationHeatMapWidget (WorldMap, 12×9)
Geographic heat map showing utilities sector threat intelligence sharing by country. Supports three metrics: event counts, organization counts, or combined weighted metric. Includes country inference from organization names.

### 4. SubsectorContributionWidget (BarChart, 6×5)
Contribution breakdown by 10 utilities subsectors: Power Generation, Transmission, Distribution, Water/Wastewater, Natural Gas, Oil & Petroleum, Renewable Energy, Regional Grid (ISOs/RTOs), Municipal Utilities, and Wholesale Power.

### 5. MonthlyContributionTrendWidget (MultiLineChart, 6×5)
12-month trend line chart tracking monthly contributions. Supports three metrics: events, organizations (unique per month), or attributes. Provides historical trend analysis for planning and reporting.

## Dashboard Layout

```
Row 13 (y=62): ISAC Rankings (left) + Sharing Metrics (right)
Row 14 (y=67): Regional Cooperation Heat Map (full width, 12×9)
Row 15 (y=76): Subsector Contribution (left) + Monthly Trends (right)
```

## Installation

```bash
cd /home/gallagher/misp-install/misp-install/widgets/organizational-dashboard
sudo bash install-organizational-widgets.sh

cd /home/gallagher/misp-install/misp-install/scripts
python3 configure-all-dashboards.py --api-key YOUR_API_KEY --misp-url https://misp.local
```

## Data Requirements

- Published events tagged with `utilities:`, `energy:`, or `ics:`
- Organization metadata (Orgc/Org fields)
- Event dates for trend analysis
- EventTag relationships for subsector classification

## Key Features

- **Dynamic Color Generation**: Consistent colors per organization using MD5 hashing
- **Period Comparison**: Automatic comparison to previous timeframe
- **Geographic Intelligence**: Country inference from organization names
- **Subsector Tracking**: 10 utilities subsectors with keyword matching
- **Trend Analysis**: 12-month historical tracking with configurable metrics

---

**Last Updated**: 2025-10-16
**Status**: Production Ready ✅
**Total Widgets**: 5
**Dashboard Position**: Rows 13-15 (y=62-80)
