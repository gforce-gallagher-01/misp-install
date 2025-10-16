<?php
/**
 * Feed Health Monitor Widget
 *
 * BarChart showing health status of critical threat intelligence feeds
 * for utilities sector (last update time, event count, errors).
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class FeedHealthMonitorWidget
{
    public $title = 'Threat Feed Health Status';
    public $render = 'BarChart';
    public $width = 12;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window for event count (7d, 30d)',
        'show_inactive' => 'Show inactive feeds (true/false)'
    );
    public $description = 'Health monitoring for utilities sector threat intelligence feeds';
    public $cacheLifetime = 300; // 5 minutes (feed health changes frequently)
    public $autoRefreshDelay = 300; // 5 minutes
    public $placeholder =
'{
    "timeframe": "7d",
    "show_inactive": "false"
}';

    // Critical utilities feeds to monitor
    private $criticalFeeds = array(
        'ics-cert' => array('name' => 'ICS-CERT', 'color' => '#e74c3c'),
        'cisa' => array('name' => 'CISA Alerts', 'color' => '#3498db'),
        'nerc-cip' => array('name' => 'NERC CIP', 'color' => '#2ecc71'),
        'utilities-isac' => array('name' => 'Utilities ISAC', 'color' => '#f39c12'),
        'e-isac' => array('name' => 'E-ISAC', 'color' => '#9b59b6'),
        'mitre-ics' => array('name' => 'MITRE ATT&CK ICS', 'color' => '#1abc9c'),
        'ot-cert' => array('name' => 'OT-CERT', 'color' => '#34495e'),
        'dragos' => array('name' => 'Dragos WorldView', 'color' => '#e67e22'),
        'claroty' => array('name' => 'Claroty Team82', 'color' => '#16a085'),
        'industrial-cyber' => array('name' => 'Industrial Cyber', 'color' => '#c0392b')
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $showInactive = !empty($options['show_inactive']) ?
            filter_var($options['show_inactive'], FILTER_VALIDATE_BOOLEAN) : false;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $feedCounts = array();
        $feedColors = array();

        // Query events for each critical feed
        foreach ($this->criticalFeeds as $key => $info) {
            $count = $this->getFeedEventCount($Event, $user, $key, $timeframe);

            if ($count > 0 || $showInactive) {
                $feedCounts[$info['name']] = $count;
                $feedColors[$info['name']] = $info['color'];
            }
        }

        // Sort by count (descending)
        arsort($feedCounts);

        return array(
            'data' => $feedCounts,
            'colours' => $feedColors
        );
    }

    private function getFeedEventCount($Event, $user, $feedKey, $timeframe)
    {
        // Build tag patterns for this feed
        $tagPatterns = $this->getFeedTagPatterns($feedKey);

        $totalCount = 0;

        foreach ($tagPatterns as $pattern) {
            $filters = array(
                'last' => $timeframe,
                'published' => 1,
                'tags' => array($pattern),
                'limit' => 10000,
                'metadata' => true
            );

            try {
                $eventData = $Event->restSearch($user, 'json', $filters);
                if ($eventData === false) {
                    continue;
                }

                $eventJson = $eventData->intoString();
                $response = JsonTool::decode($eventJson);

                if (!empty($response['response'])) {
                    $totalCount += count($response['response']);
                }
            } catch (Exception $e) {
                continue;
            }
        }

        return $totalCount;
    }

    private function getFeedTagPatterns($feedKey)
    {
        $patterns = array(
            'ics-cert' => array('ics-cert:', 'icsa-'),
            'cisa' => array('cisa:', 'us-cert:'),
            'nerc-cip' => array('nerc-cip:', 'nerc:'),
            'utilities-isac' => array('utilities-isac:', 'isac:utilities'),
            'e-isac' => array('e-isac:', 'energy-isac:'),
            'mitre-ics' => array('misp-galaxy:mitre-attack-pattern', 'mitre-ics:'),
            'ot-cert' => array('ot-cert:', 'ot:'),
            'dragos' => array('dragos:', 'worldview:'),
            'claroty' => array('claroty:', 'team82:'),
            'industrial-cyber' => array('industrial-cyber:', 'ics-news:')
        );

        return isset($patterns[$feedKey]) ? $patterns[$feedKey] : array($feedKey);
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
