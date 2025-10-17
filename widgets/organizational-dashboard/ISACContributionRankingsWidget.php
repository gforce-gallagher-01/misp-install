<?php
/**
 * ISAC Contribution Rankings Widget
 *
 * BarChart showing top contributing organizations to utilities ISAC threat
 * intelligence sharing, ranked by event count and quality metrics.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class ISACContributionRankingsWidget
{
    public $title = 'Utilities ISAC Contribution Rankings';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y)',
        'limit' => 'Max organizations to display (default: 15)'
    );
    public $description = 'Top contributing organizations to utilities sector threat intelligence';
    public $cacheLifetime = 3600; // 1 hour
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "90d",
    "limit": "15"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '90d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('utilities:', 'energy:', 'ics:%'),
            'limit' => 10000,
            'metadata' => true
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

        $orgCounts = array();
        $orgColors = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Get organization from event
            $orgName = $this->extractOrgName($event);

            if (!empty($orgName)) {
                if (!isset($orgCounts[$orgName])) {
                    $orgCounts[$orgName] = 0;
                    $orgColors[$orgName] = $this->getOrgColor($orgName);
                }
                $orgCounts[$orgName]++;
            }
        }

        // Sort by contribution count (descending)
        arsort($orgCounts);
        $orgCounts = array_slice($orgCounts, 0, $limit, true);

        return array(
            'data' => $orgCounts,
            'colours' => $orgColors
        );
    }

    private function extractOrgName($event)
    {
        // First try to get from Org or Orgc
        if (!empty($event['Orgc']['name'])) {
            return $this->cleanOrgName($event['Orgc']['name']);
        }

        if (!empty($event['Org']['name'])) {
            return $this->cleanOrgName($event['Org']['name']);
        }

        // Fallback to event creator org
        if (!empty($event['orgc_name'])) {
            return $this->cleanOrgName($event['orgc_name']);
        }

        if (!empty($event['org_name'])) {
            return $this->cleanOrgName($event['org_name']);
        }

        return 'Unknown';
    }

    private function cleanOrgName($name)
    {
        // Remove common suffixes for cleaner display
        $name = preg_replace('/(,?\s*(Inc\.?|LLC|Ltd\.?|Corporation|Corp\.?))$/i', '', $name);

        // Limit length
        if (strlen($name) > 30) {
            $name = substr($name, 0, 27) . '...';
        }

        return trim($name);
    }

    private function getOrgColor($orgName)
    {
        // Generate consistent color based on org name hash
        $hash = md5($orgName);
        $hue = hexdec(substr($hash, 0, 2)) / 255 * 360;

        // Use HSL to RGB conversion for vibrant colors
        $saturation = 70;
        $lightness = 50;

        return $this->hslToHex($hue, $saturation, $lightness);
    }

    private function hslToHex($h, $s, $l)
    {
        $s /= 100;
        $l /= 100;

        $c = (1 - abs(2 * $l - 1)) * $s;
        $x = $c * (1 - abs(fmod($h / 60, 2) - 1));
        $m = $l - $c / 2;

        if ($h < 60) {
            $r = $c; $g = $x; $b = 0;
        } elseif ($h < 120) {
            $r = $x; $g = $c; $b = 0;
        } elseif ($h < 180) {
            $r = 0; $g = $c; $b = $x;
        } elseif ($h < 240) {
            $r = 0; $g = $x; $b = $c;
        } elseif ($h < 300) {
            $r = $x; $g = 0; $b = $c;
        } else {
            $r = $c; $g = 0; $b = $x;
        }

        $r = round(($r + $m) * 255);
        $g = round(($g + $m) * 255);
        $b = round(($b + $m) * 255);

        return sprintf('#%02x%02x%02x', $r, $g, $b);
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
