# Utilities Sector Dashboard Widgets - Known Limitations

**Version:** 1.0
**Last Updated:** 2025-10-16

This document outlines known limitations and considerations for the utilities sector MISP dashboard widgets.

## UtilitiesThreatHeatMapWidget.php

### Geographic Data Requirements

**Limitation:** Events will only appear on the heat map if they contain geographic information (country codes or IP addresses).

**Impact:** Events without country data are silently excluded from visualization.

**Workaround:** Ensure events are tagged with:
- `country-code` or `country` attribute types
- IP addresses (for GeoIP lookup, if implemented)
- Proper geographic metadata during event creation

**Example:**
```json
{
  "Attribute": [
    {
      "type": "country-code",
      "value": "US"
    }
  ]
}
```

### GeoIP Lookup Not Implemented

**Limitation:** The `geolocateIP()` method is a placeholder that always returns `null`.

**Impact:** Events with only IP addresses (no country attributes) won't appear on the map.

**Future Enhancement:** Integrate MaxMind GeoIP2 or similar library:
```php
private function geolocateIP($ip)
{
    // Implement with MaxMind GeoIP2
    require_once 'vendor/maxmind/geoip2/src/autoload.php';
    $reader = new GeoIp2\Database\Reader('/path/to/GeoLite2-Country.mmdb');
    try {
        $record = $reader->country($ip);
        return $record->country->isoCode;
    } catch (Exception $e) {
        return null;
    }
}
```

### REST API Limitations

**Limitation:** Uses MISP REST API (`restSearch`) with 5000 event limit for performance.

**Impact:** Large MISP instances with >5000 matching events will only show subset of data.

**Workaround:** Adjust timeframe parameter to reduce event count or increase limit (may impact performance).

**Configuration:**
```php
$filters = array(
    'limit' => 5000,  // Increase if needed (affects performance)
    // ...
);
```

### Tag-Based Filtering Limitations

**Limitation:** Widget relies on proper event tagging with sector taxonomies.

**Impact:** Events without proper ICS/utilities sector tags won't be included.

**Required Tags:**
- `misp-galaxy:sector="Utilities"`
- `ics:asset-category="control"`
- `ics:sector="energy"`
- `ics:sector="water"`

**Best Practice:** Configure automatic tagging rules in MISP for utilities sector feeds.

### NERC Region Overlay Not Functional

**Limitation:** The `show_nerc_regions` parameter and `getNERCRegions()` method are implemented but not integrated with WorldMap widget.

**Impact:** NERC regions are stored in data but not visually displayed on map.

**Future Enhancement:** Requires custom WorldMap widget extension or alternative map library that supports region overlays (e.g., Leaflet.js with GeoJSON regions).

### Performance Considerations

**Limitation:** Widget caching set to 5 minutes, may not reflect real-time changes.

**Impact:** Recent events (< 5 minutes old) may not immediately appear.

**Configuration:**
```php
public $cacheLifetime = 300; // 5 minutes
public $autoRefreshDelay = 60; // 1 minute
```

**Recommendation:** For real-time monitoring, reduce `cacheLifetime` to 60-120 seconds (may increase MISP load).

### WorldMap Data Format Requirements

**Requirement:** WorldMap widget expects simple key-value pairs:
```php
return array(
    "US" => 150,  // Country code => Event count
    "CA" => 45,
    "UK" => 78
);
```

**Limitation:** Cannot include additional metadata (threat scores, event types) in tooltip without custom WorldMap widget modification.

**Impact:** Heat map only shows event count intensity, not threat severity.

**Future Enhancement:** Create custom tooltip handler in WorldMap widget template to display:
- Average threat score
- ICS event count
- APT event count
- Malware event count

### Threat Score Calculation

**Limitation:** Threat scoring is heuristic-based (tag matching) and subjective.

**Scoring Logic:**
- Base score: 5
- APT tag: +3
- Critical tag: +2
- ICS/SCADA tag: +2
- Ransomware tag: +2
- MITRE ATT&CK for ICS: +2
- Maximum score: 10

**Impact:** Scores may not accurately reflect actual threat severity without CVSS integration.

**Recommendation:** Tune scoring weights based on organizational risk assessment.

## General Widget Limitations

### Permission Model

**Limitation:** Widgets use basic permission check (site admin or authenticated user).

**Impact:** All authenticated users can view widgets (no role-based restrictions).

**Code:**
```php
public function checkPermissions($user)
{
    if (!empty($user['Role']['perm_site_admin']) || !empty($user['Role']['perm_auth'])) {
        return true;
    }
    return false;
}
```

**Future Enhancement:** Implement granular role-based access control for sensitive sectors.

### Error Handling

**Limitation:** REST API errors return error message arrays instead of empty widgets.

**Impact:** Widget shows error message instead of gracefully degrading.

**Example:**
```php
return array('error' => 'Failed to fetch event data: Connection timeout');
```

**Recommendation:** Implement fallback to cached data or "No data available" placeholder.

### Browser Compatibility

**Limitation:** Requires modern browser with JavaScript enabled (jVectorMap dependency).

**Impact:** May not work on older browsers (IE11, legacy Edge).

**Supported Browsers:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Testing Recommendations

1. **Test with sample data:** Create test events with known country codes
2. **Verify tag filtering:** Ensure ICS taxonomy tags are correctly applied
3. **Monitor performance:** Check MISP logs for slow queries (>5 seconds)
4. **Test timeframes:** Verify 1d, 7d, 30d, 90d options work correctly
5. **Validate caching:** Confirm cache expires after 5 minutes

## Support

For issues or enhancement requests:
- GitHub: https://github.com/gforce-gallagher-01/misp-install/issues
- MISP Community: https://www.misp-project.org/community/

---

**Maintainer:** tKQB Enterprises
**Last Updated:** 2025-10-16
