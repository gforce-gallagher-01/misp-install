<?php
/**
 * NERC CIP Compliance Widget
 *
 * SimpleList widget showing recent events relevant to NERC CIP compliance
 * standards (CIP-003 through CIP-011). Helps utilities sector organizations
 * track threat intelligence that may require compliance actions.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class NERCCIPComplianceWidget
{
    public $title = 'NERC CIP Compliance Events';
    public $render = 'SimpleList';
    public $width = 4;
    public $height = 4;
    public $params = array(
        'timeframe' => 'Time window for analysis (1d, 7d, 30d, 90d)',
        'cip_standards' => 'Array of CIP standards to monitor (default: all)',
        'limit' => 'Maximum events to show (default: 10)'
    );
    public $description = 'Recent events requiring NERC CIP compliance attention';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "timeframe": "7d",
    "cip_standards": ["CIP-005", "CIP-007", "CIP-010"],
    "limit": "10"
}';

    // NERC CIP standards mapping
    private $cipStandards = array(
        'CIP-003' => array(
            'name' => 'Security Management Controls',
            'keywords' => array('security policy', 'security plan', 'access control', 'training')
        ),
        'CIP-004' => array(
            'name' => 'Personnel & Training',
            'keywords' => array('background check', 'personnel', 'training', 'awareness')
        ),
        'CIP-005' => array(
            'name' => 'Electronic Security Perimeter',
            'keywords' => array('firewall', 'esp', 'electronic security', 'perimeter', 'network security')
        ),
        'CIP-006' => array(
            'name' => 'Physical Security',
            'keywords' => array('physical security', 'access control', 'surveillance', 'physical access')
        ),
        'CIP-007' => array(
            'name' => 'System Security Management',
            'keywords' => array('patch', 'vulnerability', 'malware', 'security patch', 'antivirus', 'ports')
        ),
        'CIP-008' => array(
            'name' => 'Incident Reporting',
            'keywords' => array('incident', 'reporting', 'cyber incident', 'disturbance')
        ),
        'CIP-009' => array(
            'name' => 'Recovery Plans',
            'keywords' => array('recovery', 'backup', 'restoration', 'disaster recovery')
        ),
        'CIP-010' => array(
            'name' => 'Configuration Management',
            'keywords' => array('configuration', 'baseline', 'change control', 'change management')
        ),
        'CIP-011' => array(
            'name' => 'Information Protection',
            'keywords' => array('information protection', 'data protection', 'bcsi', 'classified information')
        )
    );

    public function handler($user, $options = array())
    {
        // Parse parameters with defaults
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;
        $cipFilter = !empty($options['cip_standards']) ? $options['cip_standards'] : array();

        // If no CIP standards specified, use all
        if (empty($cipFilter)) {
            $cipFilter = array_keys($this->cipStandards);
        }

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build filters for MISP REST API
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('ics:'),
            'limit' => 1000,
            'includeEventTags' => 1,
            'metadata' => false // Get full event data
        );

        // Fetch events
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
        $matchedEvents = 0;

        foreach ($events as $eventWrapper) {
            if ($matchedEvents >= $limit) {
                break;
            }

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

            // Check for CIP standard relevance
            $matchedStandards = array();

            foreach ($cipFilter as $cipCode) {
                if (!isset($this->cipStandards[$cipCode])) {
                    continue;
                }

                $cipInfo = $this->cipStandards[$cipCode];

                foreach ($cipInfo['keywords'] as $keyword) {
                    if (strpos($searchText, $keyword) !== false) {
                        $matchedStandards[] = $cipCode;
                        break;
                    }
                }
            }

            // If event matches at least one CIP standard, add to results
            if (!empty($matchedStandards)) {
                $eventInfo = !empty($event['info']) ? $event['info'] : 'Event ' . $event['id'];

                // Truncate long event titles
                if (strlen($eventInfo) > 60) {
                    $eventInfo = substr($eventInfo, 0, 57) . '...';
                }

                $data[] = array(
                    'title' => $eventInfo,
                    'value' => implode(', ', $matchedStandards),
                    'html' => sprintf(
                        ' (<a href="%s">%s</a>)',
                        $baseUrl . '/events/view/' . $event['id'],
                        __('View')
                    )
                );

                $matchedEvents++;
            }
        }

        // If no matches, show message
        if (empty($data)) {
            $data[] = array(
                'title' => __('No CIP-relevant events'),
                'value' => __('in timeframe'),
                'html' => ''
            );
        }

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
