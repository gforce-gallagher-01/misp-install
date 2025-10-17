<?php
/**
 * TTPs Targeting Utilities Widget
 *
 * Bar chart showing Tactics, Techniques, and Procedures (TTPs) specific to
 * utilities sector attacks, mapped to MITRE ATT&CK for ICS.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class TTPsUtilitiesWidget
{
    public $title = 'TTPs Targeting Utilities';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y, all)',
        'limit' => 'Max TTPs to display (default: 15)'
    );
    public $description = 'Tactics, Techniques, and Procedures observed in utilities sector attacks';
    public $cacheLifetime = 600;
    public $autoRefreshDelay = 300;
    public $placeholder =
'{
    "timeframe": "1y",
    "limit": "15"
}';

    // ICS-specific TTPs commonly used against utilities
    private $utilityTTPs = array(
        'spearphishing' => array('name' => 'Spearphishing', 'color' => '#e74c3c', 'keywords' => array('spearphish', 'phishing', 'social engineering')),
        'watering-hole' => array('name' => 'Watering Hole', 'color' => '#c0392b', 'keywords' => array('watering hole', 'strategic web compromise')),
        'remote-access' => array('name' => 'Remote Access Tools', 'color' => '#3498db', 'keywords' => array('remote access', 'rat', 'teamviewer', 'vnc')),
        'lateral-movement' => array('name' => 'Lateral Movement', 'color' => '#2980b9', 'keywords' => array('lateral movement', 'psexec', 'wmi', 'pass the hash')),
        'credential-dumping' => array('name' => 'Credential Dumping', 'color' => '#9b59b6', 'keywords' => array('credential dump', 'mimikatz', 'lsass', 'password hash')),
        'screen-capture' => array('name' => 'Screen Capture', 'color' => '#8e44ad', 'keywords' => array('screen capture', 'screenshot', 'screen grab')),
        'hmi-interaction' => array('name' => 'HMI/SCADA Interaction', 'color' => '#27ae60', 'keywords' => array('hmi', 'scada interaction', 'operator workstation')),
        'plc-programming' => array('name' => 'PLC Programming', 'color' => '#16a085', 'keywords' => array('plc program', 'ladder logic', 'function block')),
        'modbus-manipulation' => array('name' => 'Modbus Manipulation', 'color' => '#d35400', 'keywords' => array('modbus', 'function code', 'register manipulation')),
        'dnp3-manipulation' => array('name' => 'DNP3 Manipulation', 'color' => '#e67e22', 'keywords' => array('dnp3', 'outstation', 'master station')),
        'denial-of-service' => array('name' => 'Denial of Service', 'color' => '#c0392b', 'keywords' => array('dos', 'denial of service', 'resource exhaustion')),
        'loss-of-view' => array('name' => 'Loss of View', 'color' => '#7f8c8d', 'keywords' => array('loss of view', 'blind operator', 'hmi manipulation')),
        'loss-of-control' => array('name' => 'Loss of Control', 'color' => '#95a5a6', 'keywords' => array('loss of control', 'unauthorized command', 'rogue device')),
        'manipulation-of-control' => array('name' => 'Manipulation of Control', 'color' => '#34495e', 'keywords' => array('manipulation of control', 'false data injection', 'setpoint change')),
        'firmware-modification' => array('name' => 'Firmware Modification', 'color' => '#e74c3c', 'keywords' => array('firmware', 'bootkit', 'uefi', 'bios'))
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'published' => 1,
            'tags' => array('ics:%', 'utilities:'),
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

        $ttpCounts = array();
        $ttpColors = array();

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

            // Check for TTP matches
            foreach ($this->utilityTTPs as $key => $info) {
                foreach ($info['keywords'] as $keyword) {
                    if (strpos($searchText, $keyword) !== false) {
                        $displayName = $info['name'];

                        if (!isset($ttpCounts[$displayName])) {
                            $ttpCounts[$displayName] = 0;
                            $ttpColors[$displayName] = $info['color'];
                        }
                        $ttpCounts[$displayName]++;
                        break; // Count once per event
                    }
                }
            }
        }

        arsort($ttpCounts);
        $ttpCounts = array_slice($ttpCounts, 0, $limit, true);

        return array(
            'data' => $ttpCounts,
            'colours' => $ttpColors
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
