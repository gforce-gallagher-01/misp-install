<?php
/**
 * Utilities Sector Statistics Widget
 *
 * Key statistics widget showing utilities sector threat intelligence metrics
 * including total threats, active campaigns, critical vulnerabilities, and
 * NERC CIP relevant events.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class UtilitiesSectorStatsWidget
{
    public $title = 'Utilities Sector Statistics';
    public $render = 'SimpleList';
    public $width = 3;
    public $height = 2;
    public $params = array(
        'show_24h' => 'Show 24-hour stats (default: true)',
        'show_7d' => 'Show 7-day stats (default: true)',
        'show_30d' => 'Show 30-day stats (default: true)'
    );
    public $description = 'Key statistics for utilities sector threat intelligence';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "show_24h": true,
    "show_7d": true,
    "show_30d": true
}';

    public function handler($user, $options = array())
    {
        // Parse options
        $show24h = !isset($options['show_24h']) || $options['show_24h'];
        $show7d = !isset($options['show_7d']) || $options['show_7d'];
        $show30d = !isset($options['show_30d']) || $options['show_30d'];

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $data = array();
        $baseUrl = Configure::read('MISP.baseurl');

        // 24-hour statistics
        if ($show24h) {
            $eventIds24h = $Event->fetchEventIds($user, array(
                'last' => '1d',
                'tags' => array('ics:%'),
                'published' => 1
            ));

            $data[] = array(
                'title' => __('ICS Events (24h)'),
                'value' => count($eventIds24h),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/index/searchtag:ics%3A/searchpublished:1/searchDatefrom:' . date('Y-m-d', time() - 86400),
                    __('View')
                )
            );

            // Critical vulnerabilities (24h)
            $criticalIds24h = $Event->fetchEventIds($user, array(
                'last' => '1d',
                'tags' => array('ics:%', 'vulnerability'),
                'published' => 1
            ));

            $data[] = array(
                'title' => __('ICS Vulnerabilities (24h)'),
                'value' => count($criticalIds24h),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/index/searchtag:vulnerability',
                    __('View')
                )
            );
        }

        // 7-day statistics
        if ($show7d) {
            $eventIds7d = $Event->fetchEventIds($user, array(
                'last' => '7d',
                'tags' => array('ics:%'),
                'published' => 1
            ));

            $data[] = array(
                'title' => __('ICS Events (7d)'),
                'value' => count($eventIds7d),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/index/searchtag:ics%3A/searchpublished:1/searchDatefrom:' . date('Y-m-d', time() - (7 * 86400)),
                    __('View')
                )
            );

            // APT campaigns (7d)
            $aptIds7d = $Event->fetchEventIds($user, array(
                'last' => '7d',
                'tags' => array('ics:%', 'misp-galaxy:threat-actor'),
                'published' => 1
            ));

            $data[] = array(
                'title' => __('APT Campaigns (7d)'),
                'value' => count($aptIds7d),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/index/searchtag:misp-galaxy%3Athreat-actor',
                    __('View')
                )
            );
        }

        // 30-day statistics
        if ($show30d) {
            $eventIds30d = $Event->fetchEventIds($user, array(
                'last' => '30d',
                'tags' => array('ics:%'),
                'published' => 1
            ));

            $data[] = array(
                'title' => __('ICS Events (30d)'),
                'value' => count($eventIds30d),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/index/searchtag:ics%3A/searchpublished:1/searchDatefrom:' . date('Y-m-d', time() - (30 * 86400)),
                    __('View')
                )
            );

            // Utilities sector specific (30d)
            $utilityIds30d = $Event->fetchEventIds($user, array(
                'last' => '30d',
                'tags' => array('ics:sector="energy"', 'ics:sector="water"'),
                'published' => 1
            ));

            $data[] = array(
                'title' => __('Utilities Events (30d)'),
                'value' => count($utilityIds30d),
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/index/searchtag:ics%3Asector',
                    __('View')
                )
            );
        }

        // Total ICS events
        $totalIcsIds = $Event->fetchEventIds($user, array(
            'tags' => array('ics:%'),
            'published' => 1
        ));

        $data[] = array(
            'title' => __('Total ICS Events'),
            'value' => count($totalIcsIds),
            'html' => sprintf(
                ' (<a href="%s">%s</a>)',
                $baseUrl . '/events/index/searchtag:ics%3A',
                __('View')
            )
        );

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
