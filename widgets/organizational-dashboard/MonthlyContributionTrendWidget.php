<?php
/**
 * Monthly Contribution Trend Widget
 *
 * MultiLineChart showing monthly trends for utilities sector threat
 * intelligence contributions over time.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class MonthlyContributionTrendWidget
{
    public $title = 'Monthly Contribution Trends';
    public $render = 'MultiLineChart';
    public $width = 12;
    public $height = 5;
    public $params = array(
        'months' => 'Number of months to display (default: 12)',
        'metric' => 'Metric to track (events, organizations, attributes)'
    );
    public $description = 'Monthly trend analysis of utilities sector contributions';
    public $cacheLifetime = 3600; // 1 hour
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "months": "12",
    "metric": "events"
}';

    public function handler($user, $options = array())
    {
        $months = !empty($options['months']) ? intval($options['months']) : 12;
        $metric = !empty($options['metric']) ? $options['metric'] : 'events';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build date range for queries
        $monthlyData = array();
        $dates = array();

        for ($i = $months - 1; $i >= 0; $i--) {
            $date = date('Y-m', strtotime("-$i months"));
            $dates[] = $date;
            $monthlyData[$date] = 0;
        }

        // Query all events for the time period
        $timeframe = $months . 'm';
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('utilities:', 'energy:', 'ics:%'),
            'limit' => 50000,
            'metadata' => ($metric === 'attributes') ? false : true
        );

        try {
            $eventData = $Event->restSearch($user, 'json', $filters);
            if ($eventData === false) {
                return $this->formatForMultiLineChart($dates, $monthlyData, $metric);
            }

            $eventJson = $eventData->intoString();
            $response = JsonTool::decode($eventJson);

            if (empty($response['response'])) {
                return $this->formatForMultiLineChart($dates, $monthlyData, $metric);
            }

            $events = $response['response'];
        } catch (Exception $e) {
            return $this->formatForMultiLineChart($dates, $monthlyData, $metric);
        }

        // Aggregate by month based on metric
        $monthlyOrgs = array();
        foreach ($dates as $date) {
            $monthlyOrgs[$date] = array();
        }

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Get event date (YYYY-MM format)
            $eventDate = !empty($event['date']) ? substr($event['date'], 0, 7) : null;

            if ($eventDate && isset($monthlyData[$eventDate])) {
                if ($metric === 'events') {
                    $monthlyData[$eventDate]++;
                } elseif ($metric === 'attributes') {
                    if (!empty($event['Attribute'])) {
                        $monthlyData[$eventDate] += count($event['Attribute']);
                    }
                } elseif ($metric === 'organizations') {
                    // Track unique organizations per month
                    $orgId = !empty($event['orgc_id']) ? $event['orgc_id'] :
                             (!empty($event['Orgc']['id']) ? $event['Orgc']['id'] : null);
                    if ($orgId) {
                        $monthlyOrgs[$eventDate][$orgId] = true;
                    }
                }
            }
        }

        // For organizations metric, count unique orgs per month
        if ($metric === 'organizations') {
            foreach ($monthlyOrgs as $date => $orgs) {
                $monthlyData[$date] = count($orgs);
            }
        }

        return $this->formatForMultiLineChart($dates, $monthlyData, $metric);
    }

    private function formatForMultiLineChart($dates, $data, $metric)
    {
        // Format labels (month names)
        $labels = array();
        foreach ($dates as $date) {
            $labels[] = date('M Y', strtotime($date . '-01'));
        }

        // Format values
        $values = array();
        foreach ($dates as $date) {
            $values[] = isset($data[$date]) ? $data[$date] : 0;
        }

        // Determine line label based on metric
        $lineLabel = 'Events';
        if ($metric === 'organizations') {
            $lineLabel = 'Organizations';
        } elseif ($metric === 'attributes') {
            $lineLabel = 'Attributes';
        }

        return array(
            'labels' => $labels,
            'datasets' => array(
                array(
                    'label' => $lineLabel,
                    'data' => $values,
                    'borderColor' => '#3498db',
                    'backgroundColor' => 'rgba(52, 152, 219, 0.1)',
                    'tension' => 0.4
                )
            )
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
