<?php
/**
 * Vendor Security Bulletins Widget
 *
 * BarChart showing security bulletins from major ICS vendors (Siemens,
 * Schneider, ABB, Rockwell, etc.) affecting utilities sector.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class VendorSecurityBulletinsWidget
{
    public $title = 'ICS Vendor Security Bulletins';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y)',
        'limit' => 'Max vendors to display (default: 10)'
    );
    public $description = 'Security bulletins from major ICS vendors';
    public $cacheLifetime = 1800; // 30 minutes
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "90d",
    "limit": "10"
}';

    // Major ICS vendors
    private $icsVendors = array(
        'siemens' => array('name' => 'Siemens', 'color' => '#009999', 'keywords' => array('siemens', 'simatic', 'sinumerik')),
        'schneider' => array('name' => 'Schneider Electric', 'color' => '#3dcd58', 'keywords' => array('schneider', 'modicon', 'triconex')),
        'abb' => array('name' => 'ABB', 'color' => '#ff000f', 'keywords' => array('abb', 'ac800m', 'system 800xa')),
        'rockwell' => array('name' => 'Rockwell Automation', 'color' => '#e4002b', 'keywords' => array('rockwell', 'allen-bradley', 'controllogix', 'compactlogix')),
        'ge' => array('name' => 'GE Digital', 'color' => '#005eb8', 'keywords' => array('ge digital', 'ge vernova', 'mark vie', 'cimplicity')),
        'honeywell' => array('name' => 'Honeywell', 'color' => '#da291c', 'keywords' => array('honeywell', 'experion', 'c300')),
        'emerson' => array('name' => 'Emerson', 'color' => '#004b8d', 'keywords' => array('emerson', 'ovation', 'deltav')),
        'yokogawa' => array('name' => 'Yokogawa', 'color' => '#0067b1', 'keywords' => array('yokogawa', 'centum', 'prosafe-rs')),
        'omron' => array('name' => 'OMRON', 'color' => '#0071c5', 'keywords' => array('omron', 'sysmac', 'cj2m')),
        'mitsubishi' => array('name' => 'Mitsubishi Electric', 'color' => '#e60012', 'keywords' => array('mitsubishi', 'melsec', 'fx5u')),
        'phoenix' => array('name' => 'Phoenix Contact', 'color' => '#ff6600', 'keywords' => array('phoenix contact', 'plcnext')),
        'aveva' => array('name' => 'AVEVA', 'color' => '#00a3e0', 'keywords' => array('aveva', 'wonderware', 'system platform'))
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
            'tags' => array('ics:%', 'scada:'),
            'limit' => 2000,
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

        $vendorCounts = array();
        $vendorColors = array();

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

            // Check for vendor matches
            foreach ($this->icsVendors as $key => $info) {
                foreach ($info['keywords'] as $keyword) {
                    if (strpos($searchText, $keyword) !== false) {
                        $displayName = $info['name'];

                        if (!isset($vendorCounts[$displayName])) {
                            $vendorCounts[$displayName] = 0;
                            $vendorColors[$displayName] = $info['color'];
                        }
                        $vendorCounts[$displayName]++;
                        break; // Count once per event
                    }
                }
            }
        }

        arsort($vendorCounts);
        $vendorCounts = array_slice($vendorCounts, 0, $limit, true);

        return array(
            'data' => $vendorCounts,
            'colours' => $vendorColors
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
