<?php
/**
 * Regional Cooperation Heat Map Widget
 *
 * WorldMap showing geographic distribution of utilities sector threat
 * intelligence sharing by region/country.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class RegionalCooperationHeatMapWidget
{
    public $title = 'Regional Utilities Cooperation';
    public $render = 'WorldMap';
    public $width = 12;
    public $height = 9;
    public $params = array(
        'timeframe' => 'Time window (30d, 90d, 1y)',
        'metric' => 'Map metric (events, organizations, both)'
    );
    public $description = 'Geographic distribution of utilities sector threat intelligence sharing';
    public $cacheLifetime = 3600; // 1 hour
    public $autoRefreshDelay = 600; // 10 minutes
    public $placeholder =
'{
    "timeframe": "90d",
    "metric": "events"
}';

    public function handler($user, $options = array())
    {
        $timeframe = !empty($options['timeframe']) ? $options['timeframe'] : '90d';
        $metric = !empty($options['metric']) ? $options['metric'] : 'events';

        /** @var Event $Event */
        $Event = ClassRegistry::init('Event');

        $filters = array(
            'last' => $timeframe,
            'published' => 1,
            'tags' => array('utilities:', 'energy:', 'ics:'),
            'limit' => 10000,
            'metadata' => true
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

        $countryData = array();
        $countryOrgs = array();

        foreach ($events as $eventWrapper) {
            $event = isset($eventWrapper['Event']) ? $eventWrapper['Event'] : $eventWrapper;

            // Extract country from organization or tags
            $country = $this->extractCountry($event);

            if (!empty($country)) {
                // Count events per country
                if (!isset($countryData[$country])) {
                    $countryData[$country] = 0;
                    $countryOrgs[$country] = array();
                }
                $countryData[$country]++;

                // Track unique organizations per country
                $orgId = !empty($event['orgc_id']) ? $event['orgc_id'] :
                         (!empty($event['Orgc']['id']) ? $event['Orgc']['id'] : null);
                if ($orgId) {
                    $countryOrgs[$country][$orgId] = true;
                }
            }
        }

        // Apply metric selection
        if ($metric === 'organizations') {
            // Replace event counts with organization counts
            foreach ($countryOrgs as $country => $orgs) {
                $countryData[$country] = count($orgs);
            }
        } elseif ($metric === 'both') {
            // Combine metrics (weighted average)
            foreach ($countryOrgs as $country => $orgs) {
                $eventCount = $countryData[$country];
                $orgCount = count($orgs);
                $countryData[$country] = round(($eventCount + ($orgCount * 5)) / 2);
            }
        }

        return $countryData;
    }

    private function extractCountry($event)
    {
        // Try to get from org nationality tags
        if (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $tagData) {
                if (isset($tagData['Tag']['name'])) {
                    $tagName = strtolower($tagData['Tag']['name']);

                    // Look for country/nationality tags
                    if (preg_match('/country[:\-]([a-z]{2,3})/i', $tagName, $matches)) {
                        return strtoupper($matches[1]);
                    }
                }
            }
        }

        // Try to infer from organization name
        $orgName = '';
        if (!empty($event['Orgc']['name'])) {
            $orgName = $event['Orgc']['name'];
        } elseif (!empty($event['orgc_name'])) {
            $orgName = $event['orgc_name'];
        }

        if (!empty($orgName)) {
            return $this->inferCountryFromOrg($orgName);
        }

        // Default to US for utilities (most ISAC members are US-based)
        return 'US';
    }

    private function inferCountryFromOrg($orgName)
    {
        $orgName = strtolower($orgName);

        // Country indicators in organization names
        $countryPatterns = array(
            'US' => array('united states', 'u.s.', 'american', 'usa'),
            'CA' => array('canada', 'canadian'),
            'UK' => array('united kingdom', 'british', 'uk'),
            'DE' => array('germany', 'german', 'deutschland'),
            'FR' => array('france', 'french', 'française'),
            'JP' => array('japan', 'japanese', 'nippon'),
            'CN' => array('china', 'chinese'),
            'AU' => array('australia', 'australian'),
            'NL' => array('netherlands', 'dutch'),
            'SE' => array('sweden', 'swedish', 'sverige'),
            'NO' => array('norway', 'norwegian', 'norge'),
            'FI' => array('finland', 'finnish', 'suomi'),
            'DK' => array('denmark', 'danish', 'danmark'),
            'CH' => array('switzerland', 'swiss', 'schweiz'),
            'AT' => array('austria', 'austrian', 'österreich'),
            'BE' => array('belgium', 'belgian', 'belgique'),
            'ES' => array('spain', 'spanish', 'españa'),
            'IT' => array('italy', 'italian', 'italia'),
            'BR' => array('brazil', 'brazilian', 'brasil'),
            'IN' => array('india', 'indian'),
            'SG' => array('singapore'),
            'KR' => array('korea', 'korean'),
            'MX' => array('mexico', 'mexican')
        );

        foreach ($countryPatterns as $code => $patterns) {
            foreach ($patterns as $pattern) {
                if (strpos($orgName, $pattern) !== false) {
                    return $code;
                }
            }
        }

        // Default to US (utilities ISAC is predominantly US)
        return 'US';
    }

    public function checkPermissions($user)
    {
        if (!empty($user['Role']['perm_auth'])) {
            return true;
        }
        return false;
    }
}
