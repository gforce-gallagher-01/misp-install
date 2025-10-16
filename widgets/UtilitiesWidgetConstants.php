<?php
/**
 * Shared Constants for Utilities Sector Widgets
 *
 * Centralized definitions for ICS vendors, APT groups, malware families,
 * protocols, and other common data structures to follow DRY principles.
 *
 * @package    MISP
 * @subpackage Dashboard.Custom
 * @author     tKQB Enterprises
 * @license    AGPL-3.0
 * @version    1.0
 * @since      MISP 2.4.x
 */

class UtilitiesWidgetConstants
{
    /**
     * Major ICS vendors with colors and product keywords
     */
    public static function getICSVendors()
    {
        return array(
            'siemens' => array(
                'name' => 'Siemens',
                'color' => '#009999',
                'keywords' => array('siemens', 'simatic', 'sinumerik')
            ),
            'schneider' => array(
                'name' => 'Schneider Electric',
                'color' => '#3dcd58',
                'keywords' => array('schneider', 'modicon', 'triconex')
            ),
            'abb' => array(
                'name' => 'ABB',
                'color' => '#ff000f',
                'keywords' => array('abb', 'ac800m', 'system 800xa')
            ),
            'rockwell' => array(
                'name' => 'Rockwell Automation',
                'color' => '#e4002b',
                'keywords' => array('rockwell', 'allen-bradley', 'controllogix', 'compactlogix')
            ),
            'ge' => array(
                'name' => 'GE Digital',
                'color' => '#005eb8',
                'keywords' => array('ge digital', 'ge vernova', 'mark vie', 'cimplicity')
            ),
            'honeywell' => array(
                'name' => 'Honeywell',
                'color' => '#da291c',
                'keywords' => array('honeywell', 'experion', 'c300')
            ),
            'emerson' => array(
                'name' => 'Emerson',
                'color' => '#004b8d',
                'keywords' => array('emerson', 'ovation', 'deltav')
            ),
            'yokogawa' => array(
                'name' => 'Yokogawa',
                'color' => '#0067b1',
                'keywords' => array('yokogawa', 'centum', 'prosafe-rs')
            ),
            'omron' => array(
                'name' => 'OMRON',
                'color' => '#0071c5',
                'keywords' => array('omron', 'sysmac', 'cj2m')
            ),
            'mitsubishi' => array(
                'name' => 'Mitsubishi Electric',
                'color' => '#e60012',
                'keywords' => array('mitsubishi', 'melsec', 'fx5u')
            ),
            'phoenix' => array(
                'name' => 'Phoenix Contact',
                'color' => '#ff6600',
                'keywords' => array('phoenix contact', 'plcnext')
            ),
            'aveva' => array(
                'name' => 'AVEVA',
                'color' => '#00a3e0',
                'keywords' => array('aveva', 'wonderware', 'system platform')
            )
        );
    }

    /**
     * Known APT groups targeting utilities sector
     */
    public static function getUtilityAPTGroups()
    {
        return array(
            'dragonfly' => array(
                'name' => 'Dragonfly/DYMALLOY',
                'color' => '#c0392b',
                'aliases' => array('dragonfly', 'energetic bear', 'dymalloy', 'crouching yeti')
            ),
            'xenotime' => array(
                'name' => 'XENOTIME',
                'color' => '#e74c3c',
                'aliases' => array('xenotime', 'temp.veles')
            ),
            'apt33' => array(
                'name' => 'APT33/Elfin',
                'color' => '#8e44ad',
                'aliases' => array('apt33', 'elfin', 'holmium')
            ),
            'sandworm' => array(
                'name' => 'Sandworm/Voodoo Bear',
                'color' => '#2980b9',
                'aliases' => array('sandworm', 'voodoo bear', 'telebots', 'iridium')
            ),
            'apt41' => array(
                'name' => 'APT41/Winnti',
                'color' => '#27ae60',
                'aliases' => array('apt41', 'winnti', 'wicked panda', 'double dragon')
            ),
            'lazarus' => array(
                'name' => 'Lazarus Group',
                'color' => '#d35400',
                'aliases' => array('lazarus', 'hidden cobra', 'zinc')
            ),
            'apt10' => array(
                'name' => 'APT10/MenuPass',
                'color' => '#16a085',
                'aliases' => array('apt10', 'menupass', 'stone panda')
            ),
            'apt29' => array(
                'name' => 'APT29/Cozy Bear',
                'color' => '#34495e',
                'aliases' => array('apt29', 'cozy bear', 'dukes')
            ),
            'apt28' => array(
                'name' => 'APT28/Fancy Bear',
                'color' => '#e67e22',
                'aliases' => array('apt28', 'fancy bear', 'sofacy', 'pawn storm')
            ),
            'magnallium' => array(
                'name' => 'MAGNALLIUM',
                'color' => '#9b59b6',
                'aliases' => array('magnallium')
            ),
            'palmerworm' => array(
                'name' => 'PALMERWORM',
                'color' => '#1abc9c',
                'aliases' => array('palmerworm', 'blacktech')
            ),
            'voltzite' => array(
                'name' => 'VOLTZITE',
                'color' => '#95a5a6',
                'aliases' => array('voltzite')
            )
        );
    }

    /**
     * Industrial malware families
     */
    public static function getICSMalware()
    {
        return array(
            'triton' => array(
                'name' => 'TRITON/TRISIS',
                'color' => '#c0392b',
                'aliases' => array('triton', 'trisis', 'hatman')
            ),
            'industroyer' => array(
                'name' => 'INDUSTROYER',
                'color' => '#e74c3c',
                'aliases' => array('industroyer', 'crashoverride')
            ),
            'stuxnet' => array(
                'name' => 'Stuxnet',
                'color' => '#8e44ad',
                'aliases' => array('stuxnet')
            ),
            'havex' => array(
                'name' => 'Havex',
                'color' => '#3498db',
                'aliases' => array('havex')
            ),
            'blackenergy' => array(
                'name' => 'BlackEnergy',
                'color' => '#2c3e50',
                'aliases' => array('blackenergy', 'black energy')
            ),
            'pipedream' => array(
                'name' => 'PIPEDREAM/Incontroller',
                'color' => '#27ae60',
                'aliases' => array('pipedream', 'incontroller')
            ),
            'irongate' => array(
                'name' => 'IRONGATE',
                'color' => '#95a5a6',
                'aliases' => array('irongate')
            ),
            'killdisk' => array(
                'name' => 'KillDisk',
                'color' => '#e67e22',
                'aliases' => array('killdisk', 'kill disk')
            ),
            'wannacry' => array(
                'name' => 'WannaCry',
                'color' => '#d35400',
                'aliases' => array('wannacry', 'wanna cry', 'wcry')
            ),
            'ekans' => array(
                'name' => 'EKANS/Snake',
                'color' => '#16a085',
                'aliases' => array('ekans', 'snake ransomware')
            ),
            'fuxnet' => array(
                'name' => 'Fuxnet',
                'color' => '#9b59b6',
                'aliases' => array('fuxnet')
            )
        );
    }

    /**
     * ICS protocols
     */
    public static function getICSProtocols()
    {
        return array(
            'modbus' => array('name' => 'Modbus', 'color' => '#3498db'),
            'dnp3' => array('name' => 'DNP3', 'color' => '#e74c3c'),
            'iec61850' => array('name' => 'IEC 61850', 'color' => '#2ecc71'),
            'iec104' => array('name' => 'IEC 60870-5-104', 'color' => '#f39c12'),
            'profinet' => array('name' => 'PROFINET', 'color' => '#9b59b6'),
            'ethernetip' => array('name' => 'EtherNet/IP', 'color' => '#1abc9c'),
            'bacnet' => array('name' => 'BACnet', 'color' => '#34495e'),
            'opcua' => array('name' => 'OPC UA', 'color' => '#16a085'),
            's7comm' => array('name' => 'S7comm', 'color' => '#27ae60'),
            'codesys' => array('name' => 'CODESYS', 'color' => '#d35400'),
            'hart' => array('name' => 'HART-IP', 'color' => '#c0392b'),
            'foundation' => array('name' => 'Foundation Fieldbus', 'color' => '#8e44ad'),
            'zigbee' => array('name' => 'ZigBee', 'color' => '#2980b9'),
            'lora' => array('name' => 'LoRaWAN', 'color' => '#e67e22')
        );
    }

    /**
     * Utilities subsectors
     */
    public static function getUtilitiesSubsectors()
    {
        return array(
            'generation' => array(
                'name' => 'Power Generation',
                'color' => '#e74c3c',
                'keywords' => array('generation', 'power plant', 'generator', 'nuclear', 'coal', 'gas turbine', 'renewable')
            ),
            'transmission' => array(
                'name' => 'Transmission',
                'color' => '#3498db',
                'keywords' => array('transmission', 'substation', 'grid', 'hvdc', 'transformer', 'switchyard')
            ),
            'distribution' => array(
                'name' => 'Distribution',
                'color' => '#2ecc71',
                'keywords' => array('distribution', 'utility', 'electric utility', 'power distribution', 'smart meter', 'ami')
            ),
            'water' => array(
                'name' => 'Water/Wastewater',
                'color' => '#1abc9c',
                'keywords' => array('water', 'wastewater', 'treatment plant', 'municipal water', 'water utility')
            ),
            'gas' => array(
                'name' => 'Natural Gas',
                'color' => '#f39c12',
                'keywords' => array('natural gas', 'pipeline', 'lng', 'gas utility', 'compressor station')
            ),
            'oil' => array(
                'name' => 'Oil & Petroleum',
                'color' => '#34495e',
                'keywords' => array('oil', 'petroleum', 'refinery', 'crude', 'pipeline')
            ),
            'renewable' => array(
                'name' => 'Renewable Energy',
                'color' => '#27ae60',
                'keywords' => array('solar', 'wind', 'renewable', 'photovoltaic', 'wind farm', 'wind turbine')
            ),
            'regional' => array(
                'name' => 'Regional Grid',
                'color' => '#9b59b6',
                'keywords' => array('iso', 'rto', 'regional transmission', 'balancing authority', 'ercot', 'pjm', 'caiso')
            ),
            'municipal' => array(
                'name' => 'Municipal Utilities',
                'color' => '#16a085',
                'keywords' => array('municipal', 'city', 'public power', 'cooperative', 'coop')
            ),
            'wholesale' => array(
                'name' => 'Wholesale Power',
                'color' => '#d35400',
                'keywords' => array('wholesale', 'power authority', 'bulk power')
            )
        );
    }

    /**
     * Nation-state colors for attribution
     */
    public static function getNationStateColors()
    {
        return array(
            'russia' => '#c0392b',
            'china' => '#e74c3c',
            'iran' => '#8e44ad',
            'north korea' => '#2980b9',
            'unknown' => '#95a5a6'
        );
    }

    /**
     * Critical threat intelligence feeds
     */
    public static function getCriticalFeeds()
    {
        return array(
            'ics-cert' => array('name' => 'ICS-CERT', 'color' => '#e74c3c'),
            'cisa' => array('name' => 'CISA Alerts', 'color' => '#3498db'),
            'nerc-cip' => array('name' => 'NERC CIP', 'color' => '#2ecc71'),
            'utilities-isac' => array('name' => 'Utilities ISAC', 'color' => '#f39c12'),
            'e-isac' => array('name' => 'E-ISAC', 'color' => '#9b59b6'),
            'mitre-ics' => array('name' => 'MITRE ATT&CK ICS', 'color' => '#1abc9c'),
            'ot-cert' => array('name' => 'OT-CERT', 'color' => '#34495e'),
            'dragos' => array('name' => 'Dragos WorldView', 'color' => '#e67e22'),
            'claroty' => array('name' => 'Claroty Team82', 'color' => '#16a085'),
            'industrial-cyber' => array('name' => 'Industrial Cyber', 'color' => '#c0392b')
        );
    }
}
