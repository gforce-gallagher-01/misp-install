<?php
/**
 * Nation-State Attribution Widget
 *
 * Bar chart showing nation-state attribution for ICS/utilities targeting.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class NationStateAttributionWidget
{
    public $title = 'Nation-State Attribution';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y, all)',
        'limit' => 'Max countries to display (default: 10)'
    );
    public $description = 'Nation-state attribution for ICS/utilities targeting';
    public $cacheLifetime = 600;
    public $autoRefreshDelay = 300;
    public $placeholder =
'{
    "timeframe": "1y",
    "limit": "10"
}';

    // Nation-state color mapping
    private $countryColors = array(
        'russia' => '#c0392b',
        'china' => '#e74c3c',
        'iran' => '#8e44ad',
        'north korea' => '#2980b9',
        'unknown' => '#95a5a6'
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'published' => 1,
            'tags' => array('misp-galaxy:threat-actor', 'ics:%'),
            'limit' => 5000,
            'includeEventTags' => 1
        );

        if ($timeframe !== 'all') {
            $filters['last'] = $timeframe;
        }

        try {
            $eventData = $Event->restSearch($user, 'json', $filters);
            if ($eventData === false) {
                return array('data' => array());
            }

            $eventJson = $eventData->intoString();
            $response = JsonTool::decode($eventJson);

            if (empty($response['response'])) {
                return array('data' => array());
            }

            $events = $response['response'];
        } catch (Exception $e) {
            return array('data' => array());
        }

        $countryCounts = array();
        $countryColorMap = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            $country = $this->extractNationState($event);

            if (!empty($country)) {
                if (!isset($countryCounts[$country])) {
                    $countryCounts[$country] = 0;
                    $countryKey = strtolower($country);
                    $countryColorMap[$country] = isset($this->countryColors[$countryKey]) ?
                        $this->countryColors[$countryKey] : '#34495e';
                }
                $countryCounts[$country]++;
            }
        }

        arsort($countryCounts);
        $countryCounts = array_slice($countryCounts, 0, $limit, true);

        return array(
            'data' => $countryCounts,
            'colours' => $countryColorMap
        );
    }

    private function extractNationState($event)
    {
        // Get tags from either Tag or EventTag structure
        $tags = array();
        if (!empty($event['Tag'])) {
            $tags = $event['Tag'];
        } elseif (!empty($event['EventTag'])) {
            $tags = $event['EventTag'];
        }

        if (empty($tags)) {
            return null;
        }

        // Look for country/nation-state indicators
        foreach ($tags as $tagData) {
            // Handle both Tag array (direct) and EventTag array (wrapped)
            $tagName = isset($tagData['name']) ? $tagData['name'] : (isset($tagData['Tag']['name']) ? $tagData['Tag']['name'] : '');
            if (!empty($tagName)) {
                $tagName = strtolower($tagName);

                // Check for country mentions
                if (strpos($tagName, 'russia') !== false) return 'Russia';
                if (strpos($tagName, 'china') !== false) return 'China';
                if (strpos($tagName, 'iran') !== false) return 'Iran';
                if (strpos($tagName, 'north korea') !== false || strpos($tagName, 'dprk') !== false) return 'North Korea';

                // Russian APTs
                if (strpos($tagName, 'apt28') !== false || strpos($tagName, 'apt29') !== false ||
                    strpos($tagName, 'sandworm') !== false || strpos($tagName, 'dragonfly') !== false ||
                    strpos($tagName, 'chernovite') !== false) return 'Russia';

                // Iranian APTs
                if (strpos($tagName, 'apt33') !== false || strpos($tagName, 'apt 33') !== false) return 'Iran';

                // Chinese APTs
                if (strpos($tagName, 'apt41') !== false || strpos($tagName, 'apt10') !== false ||
                    strpos($tagName, 'volt typhoon') !== false) return 'China';

                // North Korean APTs
                if (strpos($tagName, 'lazarus') !== false) return 'North Korea';

                // Non-nation state actors
                if (strpos($tagName, 'lockbit') !== false || strpos($tagName, 'mercury') !== false ||
                    strpos($tagName, 'xenotime') !== false) return 'Unknown';
            }
        }

        return 'Unknown';
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
