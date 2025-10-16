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
        'limit' => 'Maximum events to analyze (default: 1000)',
        'sector_tag' => 'Sector tag filter (default: ics:sector)'
    );
    public $description = 'Geographic heat map showing threat activity targeting utilities sector infrastructure';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "timeframe": "7d",
    "limit": "1000",
    "sector_tag": "ics:sector"
}';

    public function handler($user, $options = array())
    {
        // Parse parameters with defaults
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 1000;
        $sectorTag = !empty($options['sector_tag']) ? $options['sector_tag'] : 'ics:sector';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build filters for MISP REST API (following RecentSightingsWidget pattern)
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array($sectorTag),
            'limit' => $limit,
            'includeEventTags' => 1
        );

        // Use MISP REST API
        try {
            $eventData = $Event->restSearch($user, 'json', $filters);
            if ($eventData === false) {
                return array();
            }

            $eventJson = $eventData->intoString();
            $response = JsonTool::decode($eventJson);

            if (empty($response['response'])) {
                return array();
            }

            $events = $response['response'];
        } catch (Exception $e) {
            return array();
        }

        // Aggregate threats by country
        $countries = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Extract country from event
            $country = $this->extractCountryCode($event);
            if (empty($country)) {
                continue;
            }

            // Initialize country data
            if (!isset($countries[$country])) {
                $countries[$country] = array(
                    'count' => 0,
                    'ics_count' => 0
                );
            }

            $countries[$country]['count']++;

            // Count ICS-specific events
            if ($this->isICSRelated($event)) {
                $countries[$country]['ics_count']++;
            }
        }

        // Format for WorldMap widget
        $mapData = array();
        foreach ($countries as $countryCode => $data) {
            $mapData[] = array(
                'country' => $countryCode,
                'value' => $data['count'],
                'title' => sprintf(
                    '%s: %d events (%d ICS-related)',
                    $countryCode,
                    $data['count'],
                    $data['ics_count']
                )
            );
        }

        return $mapData;
    }

    /**
     * Extract country code from event
     */
    private function extractCountryCode($event)
    {
        // Check for country in event tags
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = $tagData['Tag']['name'];
                    // Look for country tags (e.g., "country:US", "tlp:amber:country=US")
                    if (preg_match('/country[=:]([A-Z]{2})/i', $tagName, $matches)) {
                        return strtoupper($matches[1]);
                    }
                }
            }
        }

        // Check Attribute data for country indicators
        if (!empty($event['Attribute'])) {
            foreach ($event['Attribute'] as $attr) {
                if ($attr['type'] === 'country-code') {
                    return strtoupper($attr['value']);
                }
            }
        }

        // Default fallback - could be extended with GeoIP lookup
        return null;
    }

    /**
     * Check if event is ICS-related
     */
    private function isICSRelated($event)
    {
        if (empty($event['EventTag'])) {
            return false;
        }

        $icsKeywords = array('ics', 'scada', 'plc', 'hmi', 'rtu', 'modbus', 'dnp3');

        foreach ($event['EventTag'] as $tagData) {
            if (isset($tagData['Tag']['name'])) {
                $tagName = strtolower($tagData['Tag']['name']);
                foreach ($icsKeywords as $keyword) {
                    if (strpos($tagName, $keyword) !== false) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    /**
     * Check user permissions
     */
    public function checkPermissions($user)
    {
        // Allow all authenticated users
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
