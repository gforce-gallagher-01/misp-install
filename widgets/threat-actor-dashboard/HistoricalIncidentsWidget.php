<?php
/**
 * Historical ICS Incidents Widget
 *
 * Timeline widget showing major historical ICS/utilities sector security
 * incidents with dates, targets, and attribution.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class HistoricalIncidentsWidget
{
    public $title = 'Historical ICS Security Incidents';
    public $render = 'SimpleList';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (1y, 5y, 10y, all)',
        'limit' => 'Max incidents to show (default: 15)',
        'sector_filter' => 'Filter by sector (utilities, manufacturing, all)'
    );
    public $description = 'Timeline of significant ICS security incidents affecting utilities and critical infrastructure';
    public $cacheLifetime = 3600; // 1 hour (historical data changes slowly)
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "10y",
    "limit": "15",
    "sector_filter": "utilities"
}';

    // Known historical ICS incidents (keyword-based detection)
    private $knownIncidents = array(
        'ukraine blackout' => array('name' => 'Ukraine Power Grid (2015)', 'year' => '2015', 'actor' => 'Sandworm'),
        'ukraine blackout 2016' => array('name' => 'Ukraine Power Grid (2016)', 'year' => '2016', 'actor' => 'Sandworm'),
        'industroyer' => array('name' => 'Industroyer/Crashoverride', 'year' => '2016', 'actor' => 'Sandworm'),
        'triton' => array('name' => 'TRITON/Saudi Aramco', 'year' => '2017', 'actor' => 'XENOTIME'),
        'trisis' => array('name' => 'TRISIS/Safety System Attack', 'year' => '2017', 'actor' => 'XENOTIME'),
        'stuxnet' => array('name' => 'Stuxnet/Natanz', 'year' => '2010', 'actor' => 'Unknown'),
        'dragonfly 2.0' => array('name' => 'Dragonfly 2.0 Campaign', 'year' => '2017', 'actor' => 'Dragonfly'),
        'energetic bear' => array('name' => 'Energetic Bear Campaign', 'year' => '2014', 'actor' => 'Dragonfly'),
        'blackenergy' => array('name' => 'BlackEnergy Campaign', 'year' => '2014', 'actor' => 'Sandworm'),
        'pipedream' => array('name' => 'PIPEDREAM/Incontroller', 'year' => '2022', 'actor' => 'Unknown'),
        'colonial pipeline' => array('name' => 'Colonial Pipeline Ransomware', 'year' => '2021', 'actor' => 'DarkSide'),
        'oldsmar water' => array('name' => 'Oldsmar Water Treatment', 'year' => '2021', 'actor' => 'Unknown'),
        'kemuri water' => array('name' => 'Kemuri Water Company', 'year' => '2016', 'actor' => 'Unknown')
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '10y';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;
        $sectorFilter = !empty($options['sector_filter']) ? $options['sector_filter'] : 'utilities';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'published' => 1,
            'tags' => array('ics:%', 'incident:'),
            'limit' => 2000,
            'includeEventTags' => 1,
            'metadata' => false
        );

        if ($timeframe !== 'all') {
            $filters['last'] = $timeframe;
        }

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

        $baseUrl = Configure::read('MISP.baseurl');
        $data = array();
        $foundIncidents = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Build searchable text
            $searchText = '';
            if (!empty($event['info'])) {
                $searchText .= ' ' . strtolower($event['info']);
            }

            if (!empty($event['EventTag'])) {
                foreach ($event['EventTag'] as $tagData) {
                    if (isset($tagData['Tag']['name'])) {
                        $searchText .= ' ' . strtolower($tagData['Tag']['name']);
                    }
                }
            }

            // Apply sector filter
            if ($sectorFilter !== 'all') {
                if (strpos($searchText, $sectorFilter) === false &&
                    strpos($searchText, 'utilities') === false &&
                    strpos($searchText, 'energy') === false &&
                    strpos($searchText, 'power') === false) {
                    continue;
                }
            }

            // Check for known incident matches
            foreach ($this->knownIncidents as $keyword => $incidentInfo) {
                if (strpos($searchText, $keyword) !== false) {
                    if (!isset($foundIncidents[$incidentInfo['name']])) {
                        $foundIncidents[$incidentInfo['name']] = array(
                            'name' => $incidentInfo['name'],
                            'year' => $incidentInfo['year'],
                            'actor' => $incidentInfo['actor'],
                            'event_id' => $event['id'],
                            'date' => !empty($event['date']) ? $event['date'] : 'Unknown'
                        );
                    }
                    break;
                }
            }
        }

        // Sort by year (newest first)
        uasort($foundIncidents, function($a, $b) {
            return strcmp($b['year'], $a['year']);
        });

        // Format for SimpleList
        $count = 0;
        foreach ($foundIncidents as $incident) {
            if ($count >= $limit) {
                break;
            }

            $data[] = array(
                'title' => $incident['name'],
                'value' => 'Year: ' . $incident['year'] . ' | Actor: ' . $incident['actor'],
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/view/' . $incident['event_id'],
                    __('View Event')
                )
            );

            $count++;
        }

        if (empty($data)) {
            $data[] = array(
                'title' => __('No historical incidents'),
                'value' => __('matching filters'),
                'html' => ''
            );
        }

        return $data;
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
