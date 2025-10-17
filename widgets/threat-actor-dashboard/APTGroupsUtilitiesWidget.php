<?php
/**
 * APT Groups Targeting Utilities Widget
 *
 * Bar chart showing APT groups targeting utilities sector with focus on
 * known ICS-targeting actors: Dragonfly, XENOTIME, APT33, Sandworm, etc.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class APTGroupsUtilitiesWidget
{
    public $title = 'APT Groups Targeting Utilities';
    public $render = 'BarChart';
    public $width = 6;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (7d, 30d, 90d, 1y, all)',
        'limit' => 'Max groups to display (default: 15)'
    );
    public $description = 'APT groups observed targeting utilities and energy infrastructure';
    public $cacheLifetime = 600; // 10 minutes (slower changing data)
    public $autoRefreshDelay = 300; // 5 minutes
    public $placeholder =
'{
    "timeframe": "1y",
    "limit": "15"
}';

    // Known APT groups targeting utilities/ICS
    private $utilityAPTGroups = array(
        'dragonfly' => array('name' => 'Dragonfly/DYMALLOY', 'color' => '#c0392b', 'aliases' => array('dragonfly', 'energetic bear', 'dymalloy', 'crouching yeti')),
        'xenotime' => array('name' => 'XENOTIME', 'color' => '#e74c3c', 'aliases' => array('xenotime', 'temp.veles')),
        'apt33' => array('name' => 'APT33/Elfin', 'color' => '#8e44ad', 'aliases' => array('apt33', 'elfin', 'holmium')),
        'sandworm' => array('name' => 'Sandworm/Voodoo Bear', 'color' => '#2980b9', 'aliases' => array('sandworm', 'voodoo bear', 'telebots', 'iridium')),
        'apt41' => array('name' => 'APT41/Winnti', 'color' => '#27ae60', 'aliases' => array('apt41', 'winnti', 'wicked panda', 'double dragon')),
        'lazarus' => array('name' => 'Lazarus Group', 'color' => '#d35400', 'aliases' => array('lazarus', 'hidden cobra', 'zinc')),
        'apt10' => array('name' => 'APT10/MenuPass', 'color' => '#16a085', 'aliases' => array('apt10', 'menupass', 'stone panda')),
        'apt29' => array('name' => 'APT29/Cozy Bear', 'color' => '#34495e', 'aliases' => array('apt29', 'cozy bear', 'dukes')),
        'apt28' => array('name' => 'APT28/Fancy Bear', 'color' => '#e67e22', 'aliases' => array('apt28', 'fancy bear', 'sofacy', 'pawn storm')),
        'magnallium' => array('name' => 'MAGNALLIUM', 'color' => '#9b59b6', 'aliases' => array('magnallium')),
        'palmerworm' => array('name' => 'PALMERWORM', 'color' => '#1abc9c', 'aliases' => array('palmerworm', 'blacktech')),
        'voltzite' => array('name' => 'VOLTZITE', 'color' => '#95a5a6', 'aliases' => array('voltzite'))
    );

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '1y';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'published' => 1,
            'tags' => array('misp-galaxy:threat-actor', 'ics:%'),
            'limit' => 5000,
            'includeEventTags' => 1
        );

        // Add timeframe if not "all"
        if ($timeframe !== 'all') {
            $filters['last'] = $timeframe;
        }

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

        $aptCounts = array();
        $aptColors = array();

        foreach ($events as $eventWrapper) {
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

            // Check for APT group matches
            foreach ($this->utilityAPTGroups as $key => $info) {
                foreach ($info['aliases'] as $alias) {
                    if (strpos($searchText, $alias) !== false) {
                        $displayName = $info['name'];

                        if (!isset($aptCounts[$displayName])) {
                            $aptCounts[$displayName] = 0;
                            $aptColors[$displayName] = $info['color'];
                        }
                        $aptCounts[$displayName]++;
                        break; // Count once per event
                    }
                }
            }
        }

        arsort($aptCounts);
        $aptCounts = array_slice($aptCounts, 0, $limit, true);

        return array(
            'data' => $aptCounts,
            'colours' => $aptColors
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
