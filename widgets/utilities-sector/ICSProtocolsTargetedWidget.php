<?php
/**
 * ICS Protocols Targeted Widget
 *
 * Bar chart showing top targeted ICS/SCADA protocols based on event attributes
 * and tags. Tracks attacks against Modbus, DNP3, IEC 61850, BACnet, and other
 * industrial control system protocols.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class ICSProtocolsTargetedWidget
{
    public $title = 'ICS Protocols Targeted';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 4;
    public $params = array(
        'timeframe' => 'Time window for analysis (1d, 7d, 30d, 90d)',
        'limit' => 'Maximum number of protocols to display (default: 10)',
        'sector_filter' => 'Filter by sector tag (optional, e.g., ics:sector="energy")'
    );
    public $description = 'Bar chart showing most targeted ICS/SCADA protocols (Modbus, DNP3, IEC 61850, etc.)';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "timeframe": "7d",
    "limit": "10",
    "sector_filter": ""
}';

    // Known ICS protocols to track
    private $icsProtocols = array(
        'modbus' => array('name' => 'Modbus', 'color' => '#e74c3c'),
        'dnp3' => array('name' => 'DNP3', 'color' => '#3498db'),
        'iec-61850' => array('name' => 'IEC 61850', 'color' => '#2ecc71'),
        'bacnet' => array('name' => 'BACnet', 'color' => '#f39c12'),
        'profinet' => array('name' => 'PROFINET', 'color' => '#9b59b6'),
        'ethercat' => array('name' => 'EtherCAT', 'color' => '#1abc9c'),
        'opcua' => array('name' => 'OPC UA', 'color' => '#34495e'),
        'codesys' => array('name' => 'CODESYS', 'color' => '#e67e22'),
        'ethernet/ip' => array('name' => 'EtherNet/IP', 'color' => '#95a5a6'),
        'powerlink' => array('name' => 'POWERLINK', 'color' => '#c0392b'),
        'hart-ip' => array('name' => 'HART-IP', 'color' => '#16a085'),
        's7' => array('name' => 'Siemens S7', 'color' => '#2980b9'),
        'fins' => array('name' => 'FINS', 'color' => '#8e44ad'),
        'melsec' => array('name' => 'MELSEC', 'color' => '#d35400')
    );

    public function handler($user, $options = array())
    {
        // Parse parameters with defaults
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;
        $sectorFilter = !empty($options['sector_filter']) ? $options['sector_filter'] : '';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build filters for MISP REST API
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'limit' => 5000, // Analyze more events to find protocol mentions
            'includeEventTags' => 1
        );

        // Add sector filter if specified
        if (!empty($sectorFilter)) {
            $filters['tags'] = array($sectorFilter);
        }

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

        // Count protocol mentions
        $protocolCounts = array();
        $protocolColors = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Check event tags for protocol mentions
            if (!empty($event['EventTag'])) {
                foreach ($event['EventTag'] as $tagData) {
                    if (isset($tagData['Tag']['name'])) {
                        $tagName = strtolower($tagData['Tag']['name']);

                        // Check each known protocol
                        foreach ($this->icsProtocols as $protocolKey => $protocolInfo) {
                            if (strpos($tagName, $protocolKey) !== false) {
                                $displayName = $protocolInfo['name'];

                                if (!isset($protocolCounts[$displayName])) {
                                    $protocolCounts[$displayName] = 0;
                                    $protocolColors[$displayName] = $protocolInfo['color'];
                                }
                                $protocolCounts[$displayName]++;
                            }
                        }
                    }
                }
            }

            // Check attributes for protocol mentions (comments, values)
            if (!empty($event['Attribute'])) {
                foreach ($event['Attribute'] as $attr) {
                    $searchText = '';

                    // Combine value and comment for searching
                    if (!empty($attr['value'])) {
                        $searchText .= ' ' . strtolower($attr['value']);
                    }
                    if (!empty($attr['comment'])) {
                        $searchText .= ' ' . strtolower($attr['comment']);
                    }

                    // Check for protocol mentions
                    foreach ($this->icsProtocols as $protocolKey => $protocolInfo) {
                        if (strpos($searchText, $protocolKey) !== false) {
                            $displayName = $protocolInfo['name'];

                            if (!isset($protocolCounts[$displayName])) {
                                $protocolCounts[$displayName] = 0;
                                $protocolColors[$displayName] = $protocolInfo['color'];
                            }
                            $protocolCounts[$displayName]++;
                            break; // Count once per attribute
                        }
                    }
                }
            }
        }

        // Sort by count descending
        arsort($protocolCounts);

        // Limit results
        $protocolCounts = array_slice($protocolCounts, 0, $limit, true);

        // Format for BarChart widget
        $data = array(
            'data' => $protocolCounts,
            'colours' => $protocolColors
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
