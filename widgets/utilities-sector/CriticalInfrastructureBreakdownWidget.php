<?php
/**
 * Critical Infrastructure Breakdown Widget
 *
 * Bar chart showing threat distribution across critical infrastructure subsectors
 * (generation, transmission, distribution) and asset types (SCADA, HMI, PLC, RTU).
 * Aligned with NERC CIP asset categories.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class CriticalInfrastructureBreakdownWidget
{
    public $title = 'Critical Infrastructure Breakdown';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 4;
    public $params = array(
        'timeframe' => 'Time window for analysis (1d, 7d, 30d, 90d)',
        'breakdown_by' => 'Breakdown type: subsector or asset_type (default: subsector)',
        'limit' => 'Maximum categories to display (default: 10)'
    );
    public $description = 'Breakdown of threats by critical infrastructure subsector or asset type';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "timeframe": "7d",
    "breakdown_by": "subsector",
    "limit": "10"
}';

    // Infrastructure subsectors
    private $subsectors = array(
        'generation' => array('name' => 'Generation', 'color' => '#e74c3c', 'keywords' => array('generation', 'power plant', 'generator', 'turbine')),
        'transmission' => array('name' => 'Transmission', 'color' => '#3498db', 'keywords' => array('transmission', 'substation', 'grid', 'bulk electric')),
        'distribution' => array('name' => 'Distribution', 'color' => '#2ecc71', 'keywords' => array('distribution', 'feeder', 'circuit breaker', 'switchgear')),
        'control-center' => array('name' => 'Control Center', 'color' => '#f39c12', 'keywords' => array('control center', 'ecc', 'energy control', 'operations center')),
        'renewable' => array('name' => 'Renewable Energy', 'color' => '#1abc9c', 'keywords' => array('solar', 'wind', 'renewable', 'photovoltaic', 'wind farm')),
        'nuclear' => array('name' => 'Nuclear', 'color' => '#9b59b6', 'keywords' => array('nuclear', 'reactor', 'nrc')),
        'water' => array('name' => 'Water/Wastewater', 'color' => '#16a085', 'keywords' => array('water', 'wastewater', 'treatment plant', 'reservoir')),
        'gas' => array('name' => 'Natural Gas', 'color' => '#e67e22', 'keywords' => array('natural gas', 'pipeline', 'lng', 'gas facility'))
    );

    // Asset types
    private $assetTypes = array(
        'scada' => array('name' => 'SCADA', 'color' => '#e74c3c', 'keywords' => array('scada', 'supervisory control')),
        'hmi' => array('name' => 'HMI', 'color' => '#3498db', 'keywords' => array('hmi', 'human machine interface', 'operator interface')),
        'plc' => array('name' => 'PLC', 'color' => '#2ecc71', 'keywords' => array('plc', 'programmable logic controller', 'ladder logic')),
        'rtu' => array('name' => 'RTU', 'color' => '#f39c12', 'keywords' => array('rtu', 'remote terminal unit')),
        'ied' => array('name' => 'IED', 'color' => '#9b59b6', 'keywords' => array('ied', 'intelligent electronic device', 'protective relay')),
        'dcs' => array('name' => 'DCS', 'color' => '#1abc9c', 'keywords' => array('dcs', 'distributed control system')),
        'historian' => array('name' => 'Historian', 'color' => '#34495e', 'keywords' => array('historian', 'data historian', 'pi system')),
        'engineering-station' => array('name' => 'Engineering Station', 'color' => '#95a5a6', 'keywords' => array('engineering station', 'engineering workstation', 'programming station'))
    );

    public function handler($user, $options = array())
    {
        // Parse parameters with defaults
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $breakdownBy = !empty($options['breakdown_by']) ? $options['breakdown_by'] : 'subsector';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;

        // Select breakdown categories
        $categories = ($breakdownBy === 'asset_type') ? $this->assetTypes : $this->subsectors;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build filters for MISP REST API
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('ics:'), // Any ICS-related tag
            'limit' => 5000,
            'includeEventTags' => 1
        );

        // Fetch events
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

        // Count category mentions
        $categoryCounts = array();
        $categoryColors = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Build searchable text from event
            $searchText = '';

            // Include event info
            if (!empty($event['info'])) {
                $searchText .= ' ' . strtolower($event['info']);
            }

            // Include tags
            if (!empty($event['EventTag'])) {
                foreach ($event['EventTag'] as $tagData) {
                    if (isset($tagData['Tag']['name'])) {
                        $searchText .= ' ' . strtolower($tagData['Tag']['name']);
                    }
                }
            }

            // Include attributes
            if (!empty($event['Attribute'])) {
                foreach ($event['Attribute'] as $attr) {
                    if (!empty($attr['comment'])) {
                        $searchText .= ' ' . strtolower($attr['comment']);
                    }
                    if (!empty($attr['value']) && strlen($attr['value']) > 3) {
                        $searchText .= ' ' . strtolower($attr['value']);
                    }
                }
            }

            // Check for category matches
            foreach ($categories as $categoryKey => $categoryInfo) {
                $matched = false;

                foreach ($categoryInfo['keywords'] as $keyword) {
                    if (strpos($searchText, $keyword) !== false) {
                        $matched = true;
                        break;
                    }
                }

                if ($matched) {
                    $displayName = $categoryInfo['name'];

                    if (!isset($categoryCounts[$displayName])) {
                        $categoryCounts[$displayName] = 0;
                        $categoryColors[$displayName] = $categoryInfo['color'];
                    }
                    $categoryCounts[$displayName]++;
                }
            }
        }

        // Sort by count descending
        arsort($categoryCounts);

        // Limit results
        $categoryCounts = array_slice($categoryCounts, 0, $limit, true);

        // Format for BarChart widget
        $data = array(
            'data' => $categoryCounts,
            'colours' => $categoryColors
        );

        return $data;
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
