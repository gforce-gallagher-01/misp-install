<?php
/**
 * Subsector Contribution Widget
 *
 * BarChart showing contribution breakdown by utilities subsector:
 * generation, transmission, distribution, water, gas.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class SubsectorContributionWidget
{
    public $title = 'Utilities Subsector Contributions';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y)',
        'limit' => 'Max subsectors to display (default: 10)'
    );
    public $description = 'Threat intelligence contributions by utilities subsector';
    public $cacheLifetime = 1800; // 30 minutes
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "90d",
    "limit": "10"
}';

    // Utilities subsectors with color coding
    private $subsectors = array(
        'generation' => array(
            'name' => 'Power Generation',
            'color' => '#e74c3c',
            'keywords' => array('generation', 'power plant', 'generator', 'nuclear', 'coal', 'gas turbine', 'renewable')
        ),
        'transmission' => array(
            'name' => 'Transmission',
            'color' => '#3498db',
            'keywords' => array('transmission', 'substation', 'grid', 'hvdc', 'transformer', 'switchyard')
        ),
        'distribution' => array(
            'name' => 'Distribution',
            'color' => '#2ecc71',
            'keywords' => array('distribution', 'utility', 'electric utility', 'power distribution', 'smart meter', 'ami')
        ),
        'water' => array(
            'name' => 'Water/Wastewater',
            'color' => '#1abc9c',
            'keywords' => array('water', 'wastewater', 'treatment plant', 'municipal water', 'water utility')
        ),
        'gas' => array(
            'name' => 'Natural Gas',
            'color' => '#f39c12',
            'keywords' => array('natural gas', 'pipeline', 'lng', 'gas utility', 'compressor station')
        ),
        'oil' => array(
            'name' => 'Oil & Petroleum',
            'color' => '#34495e',
            'keywords' => array('oil', 'petroleum', 'refinery', 'crude', 'pipeline')
        ),
        'renewable' => array(
            'name' => 'Renewable Energy',
            'color' => '#27ae60',
            'keywords' => array('solar', 'wind', 'renewable', 'photovoltaic', 'wind farm', 'wind turbine')
        ),
        'regional' => array(
            'name' => 'Regional Grid',
            'color' => '#9b59b6',
            'keywords' => array('iso', 'rto', 'regional transmission', 'balancing authority', 'ercot', 'pjm', 'caiso')
        ),
        'municipal' => array(
            'name' => 'Municipal Utilities',
            'color' => '#16a085',
            'keywords' => array('municipal', 'city', 'public power', 'cooperative', 'coop')
        ),
        'wholesale' => array(
            'name' => 'Wholesale Power',
            'color' => '#d35400',
            'keywords' => array('wholesale', 'power authority', 'bulk power')
        )
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '90d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('utilities:', 'energy:'),
            'limit' => 10000,
            'includeEventTags' => 1,
            'metadata' => true
        );

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

        $subsectorCounts = array();
        $subsectorColors = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Build searchable text from event and organization
            $searchText = '';
            if (!empty($event['info'])) {
                $searchText .= ' ' . strtolower($event['info']);
            }

            if (!empty($event['Orgc']['name'])) {
                $searchText .= ' ' . strtolower($event['Orgc']['name']);
            } elseif (!empty($event['orgc_name'])) {
                $searchText .= ' ' . strtolower($event['orgc_name']);
            }

            if (!empty($event['EventTag'])) {
                foreach ($event['EventTag'] as $tagData) {
                    if (isset($tagData['Tag']['name'])) {
                        $searchText .= ' ' . strtolower($tagData['Tag']['name']);
                    }
                }
            }

            // Match to subsectors
            foreach ($this->subsectors as $key => $info) {
                foreach ($info['keywords'] as $keyword) {
                    if (strpos($searchText, $keyword) !== false) {
                        $displayName = $info['name'];

                        if (!isset($subsectorCounts[$displayName])) {
                            $subsectorCounts[$displayName] = 0;
                            $subsectorColors[$displayName] = $info['color'];
                        }
                        $subsectorCounts[$displayName]++;
                        break; // Count once per event
                    }
                }
            }
        }

        arsort($subsectorCounts);
        $subsectorCounts = array_slice($subsectorCounts, 0, $limit, true);

        return array(
            'data' => $subsectorCounts,
            'colours' => $subsectorColors
        );
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
