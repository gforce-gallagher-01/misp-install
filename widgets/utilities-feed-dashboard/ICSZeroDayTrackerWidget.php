<?php
/**
 * ICS Zero-Day Tracker Widget
 *
 * SimpleList showing zero-day vulnerabilities affecting ICS/OT systems with
 * CVE numbers, CVSS scores, and affected vendors.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class ICSZeroDayTrackerWidget
{
    public $title = 'ICS Zero-Day Vulnerabilities';
    public $render = 'SimpleList';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y, all)',
        'limit' => 'Max vulnerabilities to show (default: 10)',
        'min_cvss' => 'Minimum CVSS score (default: 7.0)'
    );
    public $description = 'Zero-day and critical vulnerabilities in ICS systems';
    public $cacheLifetime = 1800; // 30 minutes
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "90d",
    "limit": "10",
    "min_cvss": "7.0"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '90d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;
        $minCvss = !empty($options['min_cvss']) ? floatval($options['min_cvss']) : 7.0;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('cve:', 'ics:', 'zero-day', 'vulnerability:'),
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
        $vulnerabilities = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Extract CVE
            $cve = $this->extractCVE($event);
            if (empty($cve)) {
                continue;
            }

            // Get CVSS score
            $cvss = $this->extractCVSS($event);
            if ($cvss < $minCvss) {
                continue;
            }

            // Check if zero-day or critical
            $isZeroDay = $this->isZeroDay($event);
            $isCritical = ($cvss >= 9.0);

            // Extract vendor
            $vendor = $this->extractVendor($event);

            // Format date
            $eventDate = !empty($event['date']) ? $event['date'] : 'Unknown';

            // Build indicator
            $indicator = '';
            if ($isZeroDay) {
                $indicator = '[0-DAY] ';
            } elseif ($isCritical) {
                $indicator = '[CRIT] ';
            }

            $vulnerabilities[] = array(
                'cve' => $cve,
                'cvss' => $cvss,
                'vendor' => $vendor,
                'date' => $eventDate,
                'indicator' => $indicator,
                'event_id' => $event['id'],
                'is_zero_day' => $isZeroDay
            );
        }

        // Sort by CVSS (highest first), then zero-day first
        usort($vulnerabilities, function($a, $b) {
            if ($a['is_zero_day'] !== $b['is_zero_day']) {
                return $b['is_zero_day'] - $a['is_zero_day'];
            }
            return $b['cvss'] <=> $a['cvss'];
        });

        // Limit results
        $vulnerabilities = array_slice($vulnerabilities, 0, $limit);

        // Format for SimpleList
        $data = array();
        foreach ($vulnerabilities as $vuln) {
            $data[] = array(
                'title' => $vuln['indicator'] . $vuln['cve'],
                'value' => sprintf(
                    'CVSS: %.1f | %s | %s',
                    $vuln['cvss'],
                    $vuln['vendor'],
                    $vuln['date']
                ),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/view/' . $vuln['event_id'],
                    __('Details')
                )
            );
        }

        if (empty($data)) {
            $data[] = array(
                'title' => __('No zero-day vulnerabilities'),
                'value' => __('in timeframe'),
                'html' => ''
            );
        }

        return $data;
    }

    private function extractCVE($event)
    {
        // Check tags first
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    if (preg_match('/CVE-\d{4}-\d+/', $tagData['Tag']['name'], $matches)) {
                        return $matches[0];
                    }
                }
            }
        }

        // Check info field
        if (!empty($event['info'])) {
            if (preg_match('/CVE-\d{4}-\d+/', $event['info'], $matches)) {
                return $matches[0];
            }
        }

        return null;
    }

    private function extractCVSS($event)
    {
        // Check tags for CVSS score
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = $tagData['Tag']['name'];

                    // Look for cvss:score=X.X pattern
                    if (preg_match('/cvss[:\s]*(?:score[=:\s]*)?(\d+\.?\d*)/', strtolower($tagName), $matches)) {
                        return floatval($matches[1]);
                    }
                }
            }
        }

        // Check info field for CVSS mentions
        if (!empty($event['info'])) {
            if (preg_match('/cvss[:\s]+(\d+\.?\d*)/', strtolower($event['info']), $matches)) {
                return floatval($matches[1]);
            }
        }

        // Default based on threat level
        if (!empty($event['threat_level_id'])) {
            switch ($event['threat_level_id']) {
                case 1: return 9.5; // High
                case 2: return 7.5; // Medium
                case 3: return 4.0; // Low
                default: return 5.0;
            }
        }

        return 7.0; // Default critical
    }

    private function isZeroDay($event)
    {
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = strtolower($tagData['Tag']['name']);

                    if (strpos($tagName, 'zero-day') !== false ||
                        strpos($tagName, '0-day') !== false ||
                        strpos($tagName, 'zeroday') !== false) {
                        return true;
                    }
                }
            }
        }

        // Check info field
        if (!empty($event['info'])) {
            $info = strtolower($event['info']);
            if (strpos($info, 'zero-day') !== false ||
                strpos($info, '0-day') !== false) {
                return true;
            }
        }

        return false;
    }

    private function extractVendor($event)
    {
        $vendors = array(
            'siemens', 'schneider', 'abb', 'rockwell', 'ge', 'honeywell',
            'emerson', 'yokogawa', 'omron', 'mitsubishi', 'phoenix contact', 'aveva'
        );

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

        foreach ($vendors as $vendor) {
            if (strpos($searchText, $vendor) !== false) {
                return ucwords($vendor);
            }
        }

        return 'Multiple';
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
