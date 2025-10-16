<?php
/**
 * CISA Utilities Sector Alerts Widget
 *
 * SimpleList showing recent CISA alerts and advisories specific to utilities
 * and energy sector critical infrastructure.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class CISAUtilitiesAlertsWidget
{
    public $title = 'CISA Utilities Sector Alerts';
    public $render = 'SimpleList';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (7d, 30d, 90d)',
        'limit' => 'Max alerts to show (default: 10)',
        'alert_type' => 'Type filter (all, alert, advisory, analysis)'
    );
    public $description = 'CISA alerts and advisories for utilities sector';
    public $cacheLifetime = 1800; // 30 minutes
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "30d",
    "limit": "10",
    "alert_type": "all"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '30d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;
        $alertType = !empty($options['alert_type']) ? strtolower($options['alert_type']) : 'all';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('cisa:', 'us-cert:', 'utilities:', 'energy:'),
            'limit' => 500,
            'includeEventTags' => 1,
            'metadata' => false
        );

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
        $count = 0;

        foreach ($events as $eventWrapper) {
            if ($count >= $limit) {
                break;
            }

            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Extract alert type
            $currentAlertType = $this->extractAlertType($event);

            // Apply type filter
            if ($alertType !== 'all' && strtolower($currentAlertType) !== $alertType) {
                continue;
            }

            // Extract alert ID
            $alertId = $this->extractAlertId($event);

            // Get threat level
            $threatLevel = $this->getThreatLevel($event);

            // Format date
            $eventDate = !empty($event['date']) ? $event['date'] : 'Unknown';

            // Build title
            $title = !empty($alertId) ? $alertId : substr($event['info'], 0, 50);

            $data[] = array(
                'title' => $title,
                'value' => sprintf(
                    '%s | %s | %s',
                    $currentAlertType,
                    $threatLevel,
                    $eventDate
                ),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/view/' . $event['id'],
                    __('View')
                )
            );

            $count++;
        }

        if (empty($data)) {
            $data[] = array(
                'title' => __('No CISA alerts'),
                'value' => __('in timeframe'),
                'html' => ''
            );
        }

        return $data;
    }

    private function extractAlertType($event)
    {
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = strtolower($tagData['Tag']['name']);

                    if (strpos($tagName, 'alert') !== false) return 'Alert';
                    if (strpos($tagName, 'advisory') !== false) return 'Advisory';
                    if (strpos($tagName, 'analysis') !== false) return 'Analysis';
                }
            }
        }

        // Check info field
        if (!empty($event['info'])) {
            $info = strtolower($event['info']);
            if (strpos($info, 'alert') !== false) return 'Alert';
            if (strpos($info, 'advisory') !== false) return 'Advisory';
            if (strpos($info, 'analysis') !== false) return 'Analysis';
        }

        return 'Alert';
    }

    private function extractAlertId($event)
    {
        if (!empty($event['info'])) {
            // Look for AA/AB/MAR patterns (CISA format)
            if (preg_match('/\b(AA|AB|MAR)\d{2}-\d{3}[A-Z]?\b/', $event['info'], $matches)) {
                return $matches[0];
            }

            // Look for US-CERT patterns
            if (preg_match('/TA\d{2}-\d{3}/', $event['info'], $matches)) {
                return $matches[0];
            }
        }

        return null;
    }

    private function getThreatLevel($event)
    {
        if (!empty($event['threat_level_id'])) {
            switch ($event['threat_level_id']) {
                case 1: return 'High';
                case 2: return 'Medium';
                case 3: return 'Low';
                case 4: return 'Undefined';
                default: return 'Medium';
            }
        }

        return 'Medium';
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
