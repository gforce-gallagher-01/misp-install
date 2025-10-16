<?php
/**
 * Sector Sharing Metrics Widget
 *
 * SimpleList showing key metrics for utilities sector threat intelligence
 * sharing: events published, attributes shared, organizations participating.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class SectorSharingMetricsWidget
{
    public $title = 'Utilities Sector Sharing Metrics';
    public $render = 'SimpleList';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (7d, 30d, 90d)',
        'compare_previous' => 'Show comparison to previous period (true/false)'
    );
    public $description = 'Key metrics for utilities sector threat intelligence sharing';
    public $cacheLifetime = 1800; // 30 minutes
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "30d",
    "compare_previous": "true"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '30d';
        $comparePrevious = !empty($options['compare_previous']) ?
            filter_var($options['compare_previous'], FILTER_VALIDATE_BOOLEAN) : true;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Get current period metrics
        $currentMetrics = $this->getMetrics($Event, $user, $timeframe);

        // Get previous period metrics if comparison enabled
        $previousMetrics = null;
        if ($comparePrevious) {
            $previousTimeframe = $this->getPreviousPeriod($timeframe);
            $previousMetrics = $this->getMetrics($Event, $user, $previousTimeframe);
        }

        // Format data for SimpleList
        $data = array();

        // Events Published
        $eventValue = number_format($currentMetrics['events']);
        if ($previousMetrics) {
            $eventChange = $this->calculateChange($currentMetrics['events'], $previousMetrics['events']);
            $eventValue .= ' ' . $eventChange;
        }
        $data[] = array(
            'title' => 'Events Published',
            'value' => $eventValue,
            'html' => ''
        );

        // Total Attributes
        $attrValue = number_format($currentMetrics['attributes']);
        if ($previousMetrics) {
            $attrChange = $this->calculateChange($currentMetrics['attributes'], $previousMetrics['attributes']);
            $attrValue .= ' ' . $attrChange;
        }
        $data[] = array(
            'title' => 'Total Attributes',
            'value' => $attrValue,
            'html' => ''
        );

        // Contributing Organizations
        $orgValue = number_format($currentMetrics['organizations']);
        if ($previousMetrics) {
            $orgChange = $this->calculateChange($currentMetrics['organizations'], $previousMetrics['organizations']);
            $orgValue .= ' ' . $orgChange;
        }
        $data[] = array(
            'title' => 'Contributing Orgs',
            'value' => $orgValue,
            'html' => ''
        );

        // Average Events per Org
        $avgEvents = $currentMetrics['organizations'] > 0 ?
            round($currentMetrics['events'] / $currentMetrics['organizations'], 1) : 0;
        $data[] = array(
            'title' => 'Avg Events per Org',
            'value' => number_format($avgEvents, 1),
            'html' => ''
        );

        // Critical Events (Threat Level 1)
        $criticalValue = number_format($currentMetrics['critical']);
        if ($previousMetrics) {
            $criticalChange = $this->calculateChange($currentMetrics['critical'], $previousMetrics['critical']);
            $criticalValue .= ' ' . $criticalChange;
        }
        $data[] = array(
            'title' => 'Critical Threats',
            'value' => $criticalValue,
            'html' => ''
        );

        return $data;
    }

    private function getMetrics($Event, $user, $timeframe)
    {
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('utilities:', 'energy:', 'ics:'),
            'limit' => 10000,
            'metadata' => false
        );

        try {
            $eventData = $Event->restSearch($user, 'json', $filters);
            if ($eventData === false) {
                return $this->getEmptyMetrics();
            }

            $eventJson = $eventData->intoString();
            $response = JsonTool::decode($eventJson);

            if (empty($response['response'])) {
                return $this->getEmptyMetrics();
            }

            $events = $response['response'];
        } catch (Exception $e) {
            return $this->getEmptyMetrics();
        }

        $metrics = array(
            'events' => count($events),
            'attributes' => 0,
            'organizations' => 0,
            'critical' => 0
        );

        $uniqueOrgs = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Count attributes
            if (!empty($event['Attribute'])) {
                $metrics['attributes'] += count($event['Attribute']);
            }

            // Track unique organizations
            $orgId = !empty($event['orgc_id']) ? $event['orgc_id'] :
                     (!empty($event['Orgc']['id']) ? $event['Orgc']['id'] : null);
            if ($orgId) {
                $uniqueOrgs[$orgId] = true;
            }

            // Count critical events
            if (!empty($event['threat_level_id']) && $event['threat_level_id'] == 1) {
                $metrics['critical']++;
            }
        }

        $metrics['organizations'] = count($uniqueOrgs);

        return $metrics;
    }

    private function getEmptyMetrics()
    {
        return array(
            'events' => 0,
            'attributes' => 0,
            'organizations' => 0,
            'critical' => 0
        );
    }

    private function getPreviousPeriod($timeframe)
    {
        // Convert timeframe to previous period
        // e.g., "30d" becomes "60d" to get previous 30 days
        $value = intval($timeframe);
        $unit = preg_replace('/[0-9]/', '', $timeframe);

        return ($value * 2) . $unit;
    }

    private function calculateChange($current, $previous)
    {
        if ($previous == 0) {
            return $current > 0 ? '(+100%)' : '(-)';
        }

        $change = (($current - $previous) / $previous) * 100;

        if ($change > 0) {
            return sprintf('(+%.0f%%)', $change);
        } elseif ($change < 0) {
            return sprintf('(%.0f%%)', $change);
        } else {
            return '(-)';
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
