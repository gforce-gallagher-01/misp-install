<?php
/**
 * Asset Type Targeting Analysis Widget
 *
 * Bar chart showing which asset types (SCADA, HMI, PLC, RTU, etc.) are
 * being targeted in recent threat activity.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class AssetTargetingAnalysisWidget
{
    public $title = 'Asset Targeting Analysis';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (1d, 7d, 30d, 90d)',
        'limit' => 'Max asset types to display (default: 10)'
    );
    public $description = 'Analysis of which ICS asset types are being targeted';
    public $cacheLifetime = 300;
    public $autoRefreshDelay = 60;
    public $placeholder =
'{
    "timeframe": "7d",
    "limit": "10"
}';

    private $assetTypes = array(
        'scada' => array('name' => 'SCADA Systems', 'color' => '#e74c3c', 'keywords' => array('scada', 'supervisory control')),
        'hmi' => array('name' => 'HMI', 'color' => '#3498db', 'keywords' => array('hmi', 'human machine interface', 'operator interface', 'operator station')),
        'plc' => array('name' => 'PLC', 'color' => '#2ecc71', 'keywords' => array('plc', 'programmable logic controller', 'ladder logic', 'allen bradley', 'siemens s7')),
        'rtu' => array('name' => 'RTU', 'color' => '#f39c12', 'keywords' => array('rtu', 'remote terminal unit')),
        'ied' => array('name' => 'IED/Relay', 'color' => '#9b59b6', 'keywords' => array('ied', 'intelligent electronic device', 'protective relay', 'relay')),
        'dcs' => array('name' => 'DCS', 'color' => '#1abc9c', 'keywords' => array('dcs', 'distributed control system')),
        'historian' => array('name' => 'Historian', 'color' => '#34495e', 'keywords' => array('historian', 'data historian', 'pi system', 'osisoft')),
        'safety-system' => array('name' => 'Safety System', 'color' => '#c0392b', 'keywords' => array('safety system', 'sis', 'triconex', 'emergency shutdown')),
        'controller' => array('name' => 'Field Controller', 'color' => '#27ae60', 'keywords' => array('field controller', 'pac', 'controller')),
        'sensor' => array('name' => 'Sensors/Actuators', 'color' => '#95a5a6', 'keywords' => array('sensor', 'actuator', 'transducer')),
        'network-device' => array('name' => 'Network Devices', 'color' => '#16a085', 'keywords' => array('switch', 'router', 'firewall', 'gateway', 'network equipment'))
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('ics:'),
            'limit' => 5000,
            'includeEventTags' => 1
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

        $assetCounts = array();
        $assetColors = array();

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

            if (!empty($event['Attribute'])) {
                foreach ($event['Attribute'] as $attr) {
                    if (!empty($attr['comment'])) {
                        $searchText .= ' ' . strtolower($attr['comment']);
                    }
                }
            }

            // Check for asset type matches
            foreach ($this->assetTypes as $key => $info) {
                $matched = false;

                foreach ($info['keywords'] as $keyword) {
                    if (strpos($searchText, $keyword) !== false) {
                        $matched = true;
                        break;
                    }
                }

                if ($matched) {
                    $displayName = $info['name'];

                    if (!isset($assetCounts[$displayName])) {
                        $assetCounts[$displayName] = 0;
                        $assetColors[$displayName] = $info['color'];
                    }
                    $assetCounts[$displayName]++;
                }
            }
        }

        arsort($assetCounts);
        $assetCounts = array_slice($assetCounts, 0, $limit, true);

        return array(
            'data' => $assetCounts,
            'colours' => $assetColors
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
