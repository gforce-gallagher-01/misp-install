<?php
/**
 * Campaign Tracking Widget
 *
 * SimpleList showing active campaigns against energy infrastructure with
 * campaign names, dates, and attribution.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class CampaignTrackingWidget
{
    public $title = 'Active Energy Infrastructure Campaigns';
    public $render = 'SimpleList';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y)',
        'limit' => 'Max campaigns to show (default: 10)'
    );
    public $description = 'Active threat campaigns targeting energy infrastructure';
    public $cacheLifetime = 600;
    public $autoRefreshDelay = 300;
    public $placeholder =
'{
    "timeframe": "90d",
    "limit": "10"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '90d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 10;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('misp-galaxy:campaign', 'ics:%'),
            'limit' => 1000,
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
        $campaignCount = 0;

        // Track unique campaigns
        $seenCampaigns = array();

        foreach ($events as $eventWrapper) {
            if ($campaignCount >= $limit) {
                break;
            }

            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Extract campaign info
            $campaignName = $this->extractCampaignName($event);

            if (empty($campaignName) || isset($seenCampaigns[$campaignName])) {
                continue;
            }

            $seenCampaigns[$campaignName] = true;

            // Get attribution
            $attribution = $this->extractAttribution($event);

            // Format date
            $eventDate = !empty($event['date']) ? $event['date'] : 'Unknown';

            $data[] = array(
                'title' => $campaignName,
                'value' => $attribution . ' - ' . $eventDate,
                'html' => sprintf(
                    ' (<a href="%s">%s</a>)',
                    $baseUrl . '/events/view/' . $event['id'],
                    __('Details')
                )
            );

            $campaignCount++;
        }

        if (empty($data)) {
            $data[] = array(
                'title' => __('No active campaigns'),
                'value' => __('in timeframe'),
                'html' => ''
            );
        }

        return $data;
    }

    private function extractCampaignName($event)
    {
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = $tagData['Tag']['name'];

                    // Look for campaign tags
                    if (strpos($tagName, 'misp-galaxy:campaign') !== false) {
                        if (preg_match('/"([^"]+)"/', $tagName, $matches)) {
                            return $matches[1];
                        }
                    }
                }
            }
        }

        // Fallback to event info if no campaign tag
        if (!empty($event['info']) && strlen($event['info']) > 10) {
            return substr($event['info'], 0, 50);
        }

        return null;
    }

    private function extractAttribution($event)
    {
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = $tagData['Tag']['name'];

                    // Look for threat actor tags
                    if (strpos($tagName, 'misp-galaxy:threat-actor') !== false) {
                        if (preg_match('/"([^"]+)"/', $tagName, $matches)) {
                            return $matches[1];
                        }
                    }
                }
            }
        }

        return 'Unattributed';
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
