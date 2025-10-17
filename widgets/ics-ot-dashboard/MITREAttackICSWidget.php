<?php
/**
 * MITRE ATT&CK for ICS Techniques Widget
 *
 * Bar chart showing trending MITRE ATT&CK for ICS techniques observed
 * in recent events. Tracks tactics and techniques specific to industrial
 * control systems.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class MITREAttackICSWidget
{
    public $title = 'MITRE ATT&CK for ICS Techniques';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window for analysis (7d, 30d, 90d, 365d)',
        'limit' => 'Maximum techniques to display (default: 15)',
        'tactic_filter' => 'Filter by tactic (optional, e.g., "initial-access", "execution")'
    );
    public $description = 'Trending MITRE ATT&CK for ICS techniques from recent events';
    public $cacheLifetime = 300; // 5 minutes
    public $autoRefreshDelay = 60; // 1 minute
    public $placeholder =
'{
    "timeframe": "30d",
    "limit": "15",
    "tactic_filter": ""
}';

    // ICS-specific tactics (subset of full ATT&CK matrix)
    private $icsTactics = array(
        'initial-access', 'execution', 'persistence', 'privilege-escalation',
        'evasion', 'credential-access', 'discovery', 'lateral-movement',
        'collection', 'command-and-control', 'inhibit-response-function',
        'impair-process-control', 'impact'
    );

    public function handler($user, $options = array())
    {
        // Parse parameters with defaults
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '30d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;
        $tacticFilter = !empty($options['tactic_filter']) ? $options['tactic_filter'] : '';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        // Build filters for MISP REST API
        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('misp-galaxy:mitre-attack-pattern'),
            'limit' => 5000,
            'includeEventTags' => 1
        );

        // Fetch events
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

        // Count technique mentions
        $techniqueCounts = array();
        $techniqueColors = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Check event tags for MITRE techniques
            if (!empty($event['EventTag'])) {
                foreach ($event['EventTag'] as $tagData) {
                    if (isset($tagData['Tag']['name'])) {
                        $tagName = $tagData['Tag']['name'];

                        // Look for mitre-attack-pattern or mitre-ics-technique tags
                        if (strpos($tagName, 'mitre-attack-pattern') !== false ||
                            strpos($tagName, 'mitre-ics-technique') !== false ||
                            strpos($tagName, 'misp-galaxy:mitre') !== false) {

                            // Extract technique name/ID
                            $techniqueName = $this->extractTechniqueName($tagName);

                            if (!empty($techniqueName)) {
                                // Apply tactic filter if specified
                                if (!empty($tacticFilter)) {
                                    if (strpos(strtolower($tagName), strtolower($tacticFilter)) === false) {
                                        continue;
                                    }
                                }

                                if (!isset($techniqueCounts[$techniqueName])) {
                                    $techniqueCounts[$techniqueName] = 0;
                                    $techniqueColors[$techniqueName] = $this->getTechniqueColor($tagName);
                                }
                                $techniqueCounts[$techniqueName]++;
                            }
                        }
                    }
                }
            }
        }

        // Sort by count descending
        arsort($techniqueCounts);

        // Limit results
        $techniqueCounts = array_slice($techniqueCounts, 0, $limit, true);

        // Format for BarChart widget
        $data = array(
            'data' => $techniqueCounts,
            'colours' => $techniqueColors
        );

        return $data;
    }

    /**
     * Extract technique name from tag
     */
    private function extractTechniqueName($tagName)
    {
        // Try to extract technique name/ID from tag
        // Examples:
        // - misp-galaxy:mitre-attack-pattern="Spearphishing Attachment - T1566.001"
        // - mitre-ics-technique="Drive-by Compromise - T0817"

        if (preg_match('/"([^"]+)"/', $tagName, $matches)) {
            return $matches[1];
        }

        if (preg_match('/=([^=]+)$/', $tagName, $matches)) {
            return trim($matches[1], '"');
        }

        // Fallback: return cleaned tag name
        $parts = explode(':', $tagName);
        return end($parts);
    }

    /**
     * Get color for technique based on tactic
     */
    private function getTechniqueColor($tagName)
    {
        $tagLower = strtolower($tagName);

        // Color by tactic
        if (strpos($tagLower, 'initial-access') !== false) return '#e74c3c';
        if (strpos($tagLower, 'execution') !== false) return '#3498db';
        if (strpos($tagLower, 'persistence') !== false) return '#2ecc71';
        if (strpos($tagLower, 'privilege-escalation') !== false) return '#f39c12';
        if (strpos($tagLower, 'evasion') !== false) return '#9b59b6';
        if (strpos($tagLower, 'credential-access') !== false) return '#1abc9c';
        if (strpos($tagLower, 'discovery') !== false) return '#34495e';
        if (strpos($tagLower, 'lateral-movement') !== false) return '#e67e22';
        if (strpos($tagLower, 'collection') !== false) return '#95a5a6';
        if (strpos($tagLower, 'command-and-control') !== false) return '#c0392b';
        if (strpos($tagLower, 'inhibit') !== false) return '#d35400';
        if (strpos($tagLower, 'impair') !== false) return '#8e44ad';
        if (strpos($tagLower, 'impact') !== false) return '#c0392b';

        return '#7f8c8d'; // Default gray
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
