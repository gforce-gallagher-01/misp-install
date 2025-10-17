<?php
/**
 * ICS-CERT Advisory Feed Widget
 *
 * SimpleList showing recent ICS-CERT advisories with severity, CVE count, and
 * affected vendors. Focuses on advisories relevant to utilities sector.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class ICSCERTAdvisoryWidget
{
    public $title = 'ICS-CERT Advisories (Utilities)';
    public $render = 'SimpleList';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (7d, 30d, 90d)',
        'limit' => 'Max advisories to show (default: 15)',
        'severity_filter' => 'Filter by severity (critical, high, medium, all)'
    );
    public $description = 'Recent ICS-CERT advisories affecting utilities sector';
    public $cacheLifetime = 1800; // 30 minutes
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "30d",
    "limit": "15",
    "severity_filter": "all"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '30d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;
        $severityFilter = !empty($options['severity_filter']) ? strtolower($options['severity_filter']) : 'all';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('ics-cert:%', 'icsa-%'),
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

            // Extract advisory info
            $advisoryId = $this->extractAdvisoryId($event);
            if (empty($advisoryId)) {
                continue;
            }

            // Get severity
            $severity = $this->extractSeverity($event);

            // Apply severity filter
            if ($severityFilter !== 'all' && strtolower($severity) !== $severityFilter) {
                continue;
            }

            // Count CVEs
            $cveCount = $this->countCVEs($event);

            // Extract vendor
            $vendor = $this->extractVendor($event);

            // Format date
            $eventDate = !empty($event['date']) ? $event['date'] : 'Unknown';

            // Build severity indicator
            $severityIndicator = $this->getSeverityIndicator($severity);

            $data[] = array(
                'title' => $advisoryId,
                'value' => sprintf(
                    '%s | %s | %d CVEs | %s',
                    $severityIndicator,
                    $vendor,
                    $cveCount,
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
                'title' => __('No ICS-CERT advisories'),
                'value' => __('in timeframe'),
                'html' => ''
            );
        }

        return $data;
    }

    private function extractAdvisoryId($event)
    {
        if (!empty($event['info'])) {
            // Look for ICSA-XX-XXX-XX format
            if (preg_match('/ICSA-\d{2}-\d{3}-\d{2}/', $event['info'], $matches)) {
                return $matches[0];
            }

            // Look for ICS-CERT advisory mentions
            if (preg_match('/ICS-CERT[:\s]+([A-Z0-9-]+)/', $event['info'], $matches)) {
                return 'ICS-CERT ' . $matches[1];
            }
        }

        return null;
    }

    private function extractSeverity($event)
    {
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = strtolower($tagData['Tag']['name']);

                    if (strpos($tagName, 'critical') !== false) return 'Critical';
                    if (strpos($tagName, 'high') !== false) return 'High';
                    if (strpos($tagName, 'medium') !== false) return 'Medium';
                    if (strpos($tagName, 'low') !== false) return 'Low';
                }
            }
        }

        // Check threat level
        if (!empty($event['threat_level_id'])) {
            switch ($event['threat_level_id']) {
                case 1: return 'High';
                case 2: return 'Medium';
                case 3: return 'Low';
                default: return 'Medium';
            }
        }

        return 'Medium';
    }

    private function countCVEs($event)
    {
        $cveCount = 0;

        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    if (preg_match('/CVE-\d{4}-\d+/', $tagData['Tag']['name'])) {
                        $cveCount++;
                    }
                }
            }
        }

        // Also check attributes if available
        if (!empty($event['Attribute'])) {
            foreach ($event['Attribute'] as $attr) {
                if (!empty($attr['value']) && preg_match('/CVE-\d{4}-\d+/', $attr['value'])) {
                    $cveCount++;
                }
            }
        }

        return $cveCount;
    }

    private function extractVendor($event)
    {
        $vendors = array(
            'siemens', 'schneider', 'abb', 'rockwell', 'ge', 'honeywell',
            'emerson', 'yokogawa', 'omron', 'mitsubishi', 'phoenix contact'
        );

        $searchText = '';
        if (!empty($event['info'])) {
            $searchText .= ' ' . strtolower($event['info']);
        }

        foreach ($vendors as $vendor) {
            if (strpos($searchText, $vendor) !== false) {
                return ucfirst($vendor);
            }
        }

        return 'Various';
    }

    private function getSeverityIndicator($severity)
    {
        switch (strtolower($severity)) {
            case 'critical':
                return '[CRIT]';
            case 'high':
                return '[HIGH]';
            case 'medium':
                return '[MED]';
            case 'low':
                return '[LOW]';
            default:
                return '[INFO]';
        }
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
