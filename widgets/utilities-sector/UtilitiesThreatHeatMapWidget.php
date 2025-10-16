<?php
/**
 * Utilities Sector Threat Heat Map Widget
 *
 * Geographic visualization of threat activity targeting utilities sector
 * with focus on ICS/SCADA/OT environments and energy infrastructure.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class UtilitiesThreatHeatMapWidget
{
    public $title = 'Utilities Sector Threat Heat Map';
    public $render = 'WorldMap';
    public $width = 6;
    public $height = 4;
    public $params = array(
        'timeframe' => 'Time window for analysis (1d, 7d, 30d, 90d)',
        'sector' => 'Sector filter: utilities, energy, water, all (default: utilities)',
        'threat_types' => 'Comma-separated threat types: malware,apt,vulnerability,incident',
        'min_threat_score' => 'Minimum threat score to display (0-10, default: 3)',
        'show_nerc_regions' => 'Overlay NERC regions on map (true/false)'
    );
    public $description = 'Geographic heat map showing real-time threat activity targeting utilities sector infrastructure, with ICS/SCADA incident highlighting and NERC region overlay';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "timeframe": "7d",
    "sector": "utilities",
    "threat_types": "malware,apt",
    "min_threat_score": "3",
    "show_nerc_regions": "true"
}';

    public function handler($user, $options = array())
    {
        // Parse parameters with defaults
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $sector = !empty($options['sector']) ? $options['sector'] : 'utilities';
        $threatTypes = !empty($options['threat_types']) ? explode(',', $options['threat_types']) : array('malware', 'apt', 'vulnerability');
        $minThreatScore = !empty($options['min_threat_score']) ? intval($options['min_threat_score']) : 3;
        $showNercRegions = !empty($options['show_nerc_regions']) && $options['show_nerc_regions'] === 'true';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build filters for MISP REST API
        $filters = array(
            'timestamp' => $this->parseTimeframe($timeframe),
            'published' => 1,
            'to_ids' => 1,
            'tags' => $this->buildSectorTags($sector),
            'limit' => 5000,  // Reasonable limit for dashboard performance
            'includeEventTags' => 1,
            'includeGalaxy' => 1
        );

        // Use MISP REST API (not direct database queries)
        try {
            $eventData = $Event->restSearch($user, 'json', $filters);
            if ($eventData === false || empty($eventData)) {
                return array('error' => 'No data available for the selected timeframe');
            }

            $eventJson = $eventData->intoString();
            $response = JsonTool::decode($eventJson);

            if (empty($response['response'])) {
                return array('error' => 'No events found matching criteria');
            }

            $events = $response['response'];
        } catch (Exception $e) {
            return array('error' => 'Failed to fetch event data: ' . $e->getMessage());
        }

        $countries = array();

        // Process events from REST API response
        foreach ($events as $eventWrapper) {
            // REST API returns events wrapped in 'Event' key
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Extract geographic information
            $country = $this->extractCountry($eventWrapper);
            if (empty($country)) {
                continue;
            }

            // Calculate threat score
            $threatScore = $this->calculateThreatScore($eventWrapper, $threatTypes);

            if ($threatScore < $minThreatScore) {
                continue;
            }

            // Aggregate by country (use ISO 3166-1 alpha-2 codes)
            if (!isset($countries[$country])) {
                $countries[$country] = array(
                    'count' => 0,
                    'threat_score' => 0,
                    'ics_events' => 0,
                    'apt_events' => 0,
                    'malware_events' => 0
                );
            }

            $countries[$country]['count']++;
            $countries[$country]['threat_score'] += $threatScore;

            // Categorize event types
            if ($this->isICSEvent($eventWrapper)) {
                $countries[$country]['ics_events']++;
            }
            if ($this->isAPTEvent($eventWrapper)) {
                $countries[$country]['apt_events']++;
            }
            if ($this->isMalwareEvent($eventWrapper)) {
                $countries[$country]['malware_events']++;
            }
        }

        // WorldMap widget expects: { "US": 150, "CA": 45, "UK": 78, ... }
        // Each country code maps to a numeric value (event count)
        $heatMapData = array();
        foreach ($countries as $countryCode => $data) {
            $avgThreatScore = $data['threat_score'] / $data['count'];

            // Store the count as the primary value for heat map intensity
            $heatMapData[$countryCode] = $data['count'];
        }

        // If no data found, return empty array
        if (empty($heatMapData)) {
            return array('info' => 'No threat data available for selected criteria');
        }

        return $heatMapData;
    }

    /**
     * Parse timeframe string to timestamp
     */
    private function parseTimeframe($timeframe)
    {
        $multiplier = array(
            'd' => 86400,  // days
            'h' => 3600,   // hours
            'm' => 2592000 // months (30 days)
        );

        preg_match('/^(\d+)([dhm])$/', $timeframe, $matches);
        if (count($matches) === 3) {
            $value = intval($matches[1]);
            $unit = $matches[2];
            return time() - ($value * $multiplier[$unit]);
        }

        // Default to 7 days
        return time() - (7 * 86400);
    }

    /**
     * Build taxonomy tags for sector filtering
     */
    private function buildSectorTags($sector)
    {
        $tags = array();

        switch ($sector) {
            case 'utilities':
                $tags = array(
                    'misp-galaxy:sector="Utilities"',
                    'ics:asset-category="control"',
                    'ics:sector="energy"',
                    'ics:sector="water"'
                );
                break;
            case 'energy':
                $tags = array(
                    'misp-galaxy:sector="Energy"',
                    'ics:sector="energy"'
                );
                break;
            case 'water':
                $tags = array(
                    'misp-galaxy:sector="Water"',
                    'ics:sector="water"'
                );
                break;
            default:
                $tags = array(
                    'ics:',
                    'misp-galaxy:sector'
                );
        }

        return $tags;
    }

    /**
     * Extract country from event (REST API format)
     */
    private function extractCountry($eventWrapper)
    {
        $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

        // Try multiple sources for country data
        if (!empty($event['country'])) {
            return strtoupper($event['country']);
        }

        // Check attributes for country indicators
        if (!empty($event['Attribute'])) {
            foreach ($event['Attribute'] as $attr) {
                if (isset($attr['type']) && ($attr['type'] === 'country-code' || $attr['type'] === 'country')) {
                    return strtoupper($attr['value']);
                }
            }
        }

        // Check for GeoIP data in IPs
        if (!empty($event['Attribute'])) {
            foreach ($event['Attribute'] as $attr) {
                if (isset($attr['type']) && in_array($attr['type'], array('ip-src', 'ip-dst'))) {
                    $country = $this->geolocateIP($attr['value']);
                    if ($country) {
                        return strtoupper($country);
                    }
                }
            }
        }

        // Fallback: use a default country or return null
        // Note: Without geographic data, events won't appear on map
        return null;
    }

    /**
     * Simple GeoIP lookup (extend with actual GeoIP library)
     */
    private function geolocateIP($ip)
    {
        // Placeholder - implement with MaxMind GeoIP or similar
        // For now, return null
        return null;
    }

    /**
     * Calculate threat score for event (REST API format)
     */
    private function calculateThreatScore($eventWrapper, $threatTypes)
    {
        $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;
        $score = 5; // Base score

        // Increase score for critical tags
        if (!empty($event['Tag'])) {
            foreach ($event['Tag'] as $tag) {
                $tagName = isset($tag['name']) ? strtolower($tag['name']) : '';

                if (strpos($tagName, 'apt') !== false) {
                    $score += 3;
                }
                if (strpos($tagName, 'critical') !== false) {
                    $score += 2;
                }
                if (strpos($tagName, 'ics') !== false || strpos($tagName, 'scada') !== false) {
                    $score += 2;
                }
                if (strpos($tagName, 'ransomware') !== false) {
                    $score += 2;
                }
            }
        }

        // Increase score for MITRE ATT&CK for ICS
        if (!empty($event['Galaxy'])) {
            foreach ($event['Galaxy'] as $galaxy) {
                $galaxyName = isset($galaxy['name']) ? $galaxy['name'] : '';
                if (strpos($galaxyName, 'ATT&CK for ICS') !== false) {
                    $score += 2;
                }
            }
        }

        return min($score, 10); // Cap at 10
    }

    /**
     * Check if event is ICS-related (REST API format)
     */
    private function isICSEvent($eventWrapper)
    {
        $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

        if (!empty($event['Tag'])) {
            foreach ($event['Tag'] as $tag) {
                $tagName = isset($tag['name']) ? strtolower($tag['name']) : '';
                if (strpos($tagName, 'ics') !== false ||
                    strpos($tagName, 'scada') !== false ||
                    strpos($tagName, 'plc') !== false ||
                    strpos($tagName, 'hmi') !== false) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Check if event is APT-related (REST API format)
     */
    private function isAPTEvent($eventWrapper)
    {
        $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

        if (!empty($event['Tag'])) {
            foreach ($event['Tag'] as $tag) {
                $tagName = isset($tag['name']) ? strtolower($tag['name']) : '';
                if (strpos($tagName, 'apt') !== false) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Check if event is malware-related (REST API format)
     */
    private function isMalwareEvent($eventWrapper)
    {
        $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

        if (!empty($event['Tag'])) {
            foreach ($event['Tag'] as $tag) {
                $tagName = isset($tag['name']) ? strtolower($tag['name']) : '';
                if (strpos($tagName, 'malware') !== false ||
                    strpos($tagName, 'ransomware') !== false ||
                    strpos($tagName, 'trojan') !== false) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Get NERC regions for overlay
     */
    private function getNERCRegions()
    {
        return array(
            array('name' => 'WECC', 'countries' => array('US-West', 'CA-West', 'MX-North')),
            array('name' => 'TRE', 'countries' => array('US-TX')),
            array('name' => 'RFC', 'countries' => array('US-Mid', 'CA-ON')),
            array('name' => 'SERC', 'countries' => array('US-SE')),
            array('name' => 'NPCC', 'countries' => array('US-NE', 'CA-QC', 'CA-NB', 'CA-NS')),
            array('name' => 'MRO', 'countries' => array('US-MID', 'CA-MB', 'CA-SK')),
            array('name' => 'FRCC', 'countries' => array('US-FL')),
            array('name' => 'SPP', 'countries' => array('US-Central'))
        );
    }

    /**
     * Check user permissions
     */
    public function checkPermissions($user)
    {
        // Allow all authenticated users with site access
        if (!empty($user['Role']['perm_site_admin']) || !empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
