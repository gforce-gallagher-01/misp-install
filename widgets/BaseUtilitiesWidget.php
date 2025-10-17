<?php
/**
 * Base Widget Class for Utilities Sector Widgets
 *
 * Provides common functionality to eliminate code duplication across all
 * utilities sector custom widgets following DRY principles.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

abstract class BaseUtilitiesWidget
{
    /**
     * Standard permission check - all utilities widgets require perm_auth
     */
    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }

    /**
     * Common event search pattern used by all widgets
     *
     * @param object $user User object
     * @param array $filters MISP search filters
     * @return array|false Array of events or false on failure
     */
    protected function searchEvents($user, $filters)
    {
        $Event = ClassRegistry::init('Event');

        try {
            $eventData = $Event->restSearch($user, 'json', $filters);
            if ($eventData === false) {
                return false;
            }

            $eventJson = $eventData->intoString();
            $response = JsonTool::decode($eventJson);

            if (empty($response['response'])) {
                return false;
            }

            return $response['response'];
        } catch (Exception $e) {
            return false;
        }
    }

    /**
     * Extract organization name from event with fallbacks
     *
     * @param array $event Event data
     * @return string Organization name or 'Unknown'
     */
    protected function extractOrgName($event)
    {
        if (!empty($event['Orgc']['name'])) {
            return $event['Orgc']['name'];
        }

        if (!empty($event['Org']['name'])) {
            return $event['Org']['name'];
        }

        if (!empty($event['orgc_name'])) {
            return $event['orgc_name'];
        }

        if (!empty($event['org_name'])) {
            return $event['org_name'];
        }

        return 'Unknown';
    }

    /**
     * Extract threat level from event
     *
     * @param array $event Event data
     * @return string Threat level (High, Medium, Low, Undefined)
     */
    protected function extractThreatLevel($event)
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

    /**
     * Build searchable text from event (info + tags)
     *
     * @param array $event Event data
     * @return string Lowercase searchable text
     */
    protected function buildSearchableText($event)
    {
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

        return $searchText;
    }

    /**
     * Count CVEs in event tags and attributes
     *
     * @param array $event Event data
     * @return int CVE count
     */
    protected function countCVEs($event)
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

        if (!empty($event['Attribute'])) {
            foreach ($event['Attribute'] as $attr) {
                if (!empty($attr['value']) && preg_match('/CVE-\d{4}-\d+/', $attr['value'])) {
                    $cveCount++;
                }
            }
        }

        return $cveCount;
    }

    /**
     * Extract CVE from event
     *
     * @param array $event Event data
     * @return string|null CVE identifier or null
     */
    protected function extractCVE($event)
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

    /**
     * Generate consistent color from string hash (for dynamic coloring)
     *
     * @param string $str Input string
     * @return string Hex color code
     */
    protected function generateColorFromHash($str)
    {
        $hash = md5($str);
        $hue = hexdec(substr($hash, 0, 2)) / 255 * 360;
        return $this->hslToHex($hue, 70, 50);
    }

    /**
     * Convert HSL to Hex color
     *
     * @param float $h Hue (0-360)
     * @param float $s Saturation (0-100)
     * @param float $l Lightness (0-100)
     * @return string Hex color code
     */
    protected function hslToHex($h, $s, $l)
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

    /**
     * Get MISP base URL from configuration
     *
     * @return string Base URL
     */
    protected function getBaseUrl()
    {
        return Configure::read('MISP.baseurl');
    }

    /**
     * Keyword matching helper for threat actor/malware/vendor detection
     *
     * @param string $searchText Haystack text (lowercase)
     * @param array $keywords Array of keywords to search for
     * @return bool True if any keyword matches
     */
    protected function matchesKeywords($searchText, $keywords)
    {
        foreach ($keywords as $keyword) {
            if (strpos($searchText, strtolower($keyword)) !== false) {
                return true;
            }
        }
        return false;
    }

    /**
     * Extract unique organization IDs from events
     *
     * @param array $events Array of events
     * @return array Array of unique org IDs
     */
    protected function extractUniqueOrgIds($events)
    {
        $uniqueOrgs = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            $orgId = !empty($event['orgc_id']) ? $event['orgc_id'] :
                     (!empty($event['Orgc']['id']) ? $event['Orgc']['id'] : null);

            if ($orgId) {
                $uniqueOrgs[$orgId] = true;
            }
        }

        return $uniqueOrgs;
    }

    /**
     * Calculate percentage change between two values
     *
     * @param int|float $current Current value
     * @param int|float $previous Previous value
     * @return string Formatted percentage change string
     */
    protected function calculatePercentageChange($current, $previous)
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
}
