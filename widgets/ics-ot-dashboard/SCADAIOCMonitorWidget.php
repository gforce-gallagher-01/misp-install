<?php
/**
 * SCADA-Specific IOC Monitoring Widget
 *
 * SimpleList showing recent SCADA/ICS-specific indicators of compromise
 * including IPs, domains, hashes targeting industrial systems.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class SCADAIOCMonitorWidget
{
    public $title = 'SCADA IOC Monitor';
    public $render = 'SimpleList';
    public $width = 4;
    public $height = 5;
    public $params = array(
        'timeframe' => 'Time window (1d, 7d, 30d)',
        'limit' => 'Maximum IOCs to display (default: 15)',
        'ioc_type' => 'Filter by type: ip, domain, hash, all (default: all)'
    );
    public $description = 'Recent SCADA/ICS-specific indicators of compromise';
    public $cacheLifetime = 180; // 3 minutes (fresher data)
    public $autoRefreshDelay = 60;
    public $placeholder =
'{
    "timeframe": "7d",
    "limit": "15",
    "ioc_type": "all"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '7d';
        $limit = !empty($options['limit']) ? intval($options['limit']) : 15;
        $iocType = !empty($options['ioc_type']) ? strtolower($options['ioc_type']) : 'all';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('ics:', 'scada'),
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
        $iocCount = 0;

        foreach ($events as $eventWrapper) {
            if ($iocCount >= $limit) {
                break;
            }

            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            if (empty($event['Attribute'])) {
                continue;
            }

            foreach ($event['Attribute'] as $attr) {
                if ($iocCount >= $limit) {
                    break 2;
                }

                // Filter by IOC type
                $attrType = strtolower($attr['type']);
                if ($iocType !== 'all') {
                    if ($iocType === 'ip' && !in_array($attrType, array('ip-src', 'ip-dst', 'ip'))) {
                        continue;
                    }
                    if ($iocType === 'domain' && !in_array($attrType, array('domain', 'hostname'))) {
                        continue;
                    }
                    if ($iocType === 'hash' && !in_array($attrType, array('md5', 'sha1', 'sha256', 'ssdeep'))) {
                        continue;
                    }
                }

                // Check if attribute is IDS-relevant
                if (empty($attr['to_ids']) || $attr['to_ids'] != 1) {
                    continue;
                }

                $iocValue = !empty($attr['value']) ? $attr['value'] : '';
                if (empty($iocValue)) {
                    continue;
                }

                // Truncate long values
                if (strlen($iocValue) > 40) {
                    $iocValue = substr($iocValue, 0, 37) . '...';
                }

                $data[] = array(
                    'title' => $this->formatIOCType($attrType),
                    'value' => $iocValue,
                    'html' => sprintf(
                        ' (<a href="%s">%s</a>)',
                        $baseUrl . '/events/view/' . $event['id'],
                        __('Event')
                    )
                );

                $iocCount++;
            }
        }

        if (empty($data)) {
            $data[] = array(
                'title' => __('No SCADA IOCs'),
                'value' => __('in timeframe'),
                'html' => ''
            );
        }

        return $data;
    }

    private function formatIOCType($type)
    {
        $typeMap = array(
            'ip-src' => 'Source IP',
            'ip-dst' => 'Dest IP',
            'domain' => 'Domain',
            'hostname' => 'Hostname',
            'md5' => 'MD5',
            'sha1' => 'SHA1',
            'sha256' => 'SHA256',
            'url' => 'URL',
            'email' => 'Email'
        );

        return isset($typeMap[$type]) ? $typeMap[$type] : strtoupper($type);
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
