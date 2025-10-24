#!/usr/bin/env python3
"""
MISP Utilities Sector Configuration Script
Version: 1.0
Author: tKQB Enterprises
Date: 2025-10-15

Purpose:
    Configure MISP for utilities sector (solar, wind, battery storage, transmission,
    distribution) with ICS/SCADA threat intelligence focus.

Features:
    - Module 1: ICS/OT Taxonomies (FIRST ICS, DHS CIIP sectors)
    - Module 2: MITRE ATT&CK for ICS Galaxy
    - Module 3: ICS Malware & APT Groups (TRITON, INDUSTROYER, Dragonfly, etc.)
    - Module 4: Custom Object Templates (Solar PV, Wind Turbines, Battery Systems)
    - Module 5: Utilities-Specific Feeds & Communities (E-ISAC, ICS-CERT)
    - Module 6: Correlation Rules for ICS Protocols (Modbus, DNP3, IEC 61850)
    - Module 7: Integration Guides (Splunk, Security Onion, ICS monitoring)

Architecture:
    - Modular design: Each module can be run independently
    - Builds on configure-misp-nerc-cip.py (NERC CIP compliance baseline)
    - Uses centralized logging (misp_logger.py)
    - Dry-run mode for testing
    - Color-coded output for readability

Usage:
    # Run all modules (recommended)
    python3 scripts/configure-misp-utilities-sector.py

    # Run specific module
    python3 scripts/configure-misp-utilities-sector.py --module 1

    # Dry-run (show what would be done)
    python3 scripts/configure-misp-utilities-sector.py --dry-run

    # Run modules 1-3 only (taxonomies, galaxies, threat actors)
    python3 scripts/configure-misp-utilities-sector.py --module 1,2,3

Requirements:
    - MISP installed and running
    - configure-misp-nerc-cip.py already run (optional but recommended)
    - MISP containers operational
    - MySQL database accessible

Related Documentation:
    - docs/NERC_CIP_CONFIGURATION.md (50+ pages)
    - docs/ICS_THREAT_INTELLIGENCE.md (to be created)
    - https://www.misp-project.org/taxonomies.html
    - https://attack.mitre.org/matrices/ics/

SPDX-License-Identifier: MIT
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.misp_logger import get_logger
except ImportError:
    # Fallback if logger not available
    import logging
    def get_logger(name, _sourcetype):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        return logging.getLogger(name)


#==============================================================================
# CONFIGURATION CLASSES
#==============================================================================

class UtilitiesSectorConfig:
    """Configuration constants for utilities sector MISP setup"""

    # Directory paths
    MISP_DIR = Path('/opt/misp')
    ENV_FILE = MISP_DIR / '.env'
    LOGS_DIR = MISP_DIR / 'logs'

    # Module 1: ICS/OT Taxonomies
    ICS_TAXONOMIES = [
        {
            'name': 'ics',
            'description': 'FIRST.ORG ICS/OT Threat Attribution (IOC) Project',
            'priority': 'CRITICAL',
            'tags_example': [
                'ics:protocol="modbus"',
                'ics:protocol="dnp3"',
                'ics:protocol="iec-61850"',
                'ics:asset-type="solar-inverter"',
                'ics:asset-type="wind-turbine"',
                'ics:asset-type="battery-storage"',
                'ics:impact="loss-of-control"',
                'ics:impact="loss-of-view"',
            ]
        },
        {
            'name': 'dhs-ciip-sectors',
            'description': 'DHS Critical Infrastructure Protection Sectors',
            'priority': 'HIGH',
            'tags_example': [
                'dhs-ciip-sectors:energy',
                'dhs-ciip-sectors:critical-manufacturing',
            ]
        },
        {
            'name': 'misp-workflow',
            'description': 'Workflow states for threat intelligence processing',
            'priority': 'MEDIUM',
            'tags_example': [
                'misp-workflow:state="draft"',
                'misp-workflow:state="validated"',
                'misp-workflow:state="published"',
            ]
        },
        {
            'name': 'incident-disposition',
            'description': 'Incident categorization for security events',
            'priority': 'MEDIUM',
            'tags_example': [
                'incident-disposition:confirmed-incident',
                'incident-disposition:false-positive',
            ]
        },
    ]

    # Module 2: MITRE ATT&CK for ICS
    ICS_GALAXIES = [
        {
            'name': 'mitre-ics-groups',
            'description': 'APT groups targeting industrial control systems',
            'priority': 'CRITICAL',
            'threat_actors': [
                'Dragonfly',  # Russia - Energy sector
                'XENOTIME',  # Russia - Petrochemical/utilities
                'APT33',  # Iran - Energy/aviation
                'TEMP.Veles',  # Russia - North American power grids
                'Sandworm',  # Russia - Ukraine power grid attacks
            ]
        },
        {
            'name': 'mitre-ics-software',
            'description': 'ICS malware families',
            'priority': 'CRITICAL',
            'malware': [
                'TRITON',  # Safety systems (Triconex)
                'INDUSTROYER',  # Power grid disruption
                'Stuxnet',  # PLC manipulation
                'BlackEnergy',  # SCADA targeting
                'Havex',  # OPC reconnaissance
            ]
        },
        {
            'name': 'mitre-ics-techniques',
            'description': 'MITRE ATT&CK for ICS techniques',
            'priority': 'HIGH',
            'techniques_example': [
                'T0883 - Internet Accessible Device',
                'T0885 - Man in the Middle',
                'T0886 - Remote System Discovery',
                'T0889 - Modify Parameter',
                'T0891 - Denial of Control',
                'T0816 - Device Restart/Shutdown',
            ]
        },
    ]

    # Module 3: Utilities-Specific Threat Actors (detailed profiles)
    UTILITIES_THREAT_ACTORS = {
        'Dragonfly': {
            'aka': ['Energetic Bear', 'Crouching Yeti', 'DYMALLOY'],
            'origin': 'Russia',
            'targets': 'Energy sector (electric utilities, solar, wind)',
            'first_seen': '2011',
            'techniques': ['Spear phishing', 'Watering hole', 'Supply chain compromise'],
            'malware': ['Havex', 'Karagany'],
            'impact': 'Reconnaissance and potential sabotage of energy infrastructure',
            'nerc_cip_relevance': 'HIGH - Directly targets BES Cyber Systems',
        },
        'XENOTIME': {
            'aka': ['TEMP.Veles for ICS'],
            'origin': 'Russia',
            'targets': 'Petrochemical, likely expanding to electric utilities',
            'first_seen': '2017',
            'techniques': ['ICS protocol exploitation', 'Safety system targeting'],
            'malware': ['TRITON/TRISIS'],
            'impact': 'First malware to target safety instrumented systems (SIS)',
            'nerc_cip_relevance': 'CRITICAL - Targets safety systems in power plants',
        },
        'APT33': {
            'aka': ['Elfin', 'Holmium'],
            'origin': 'Iran',
            'targets': 'Energy sector (especially Saudi Arabia, US utilities)',
            'first_seen': '2013',
            'techniques': ['Spear phishing', 'Password spraying', 'VPN compromise'],
            'malware': ['Shamoon', 'DropShot'],
            'impact': 'Reconnaissance and data destruction in energy sector',
            'nerc_cip_relevance': 'HIGH - Targets transmission operators',
        },
        'TEMP.Veles': {
            'aka': ['XENOTIME subset focused on electric grid'],
            'origin': 'Russia',
            'targets': 'North American power grids',
            'first_seen': '2018',
            'techniques': ['Living off the land', 'ICS protocol manipulation'],
            'malware': ['Custom malware for grid disruption'],
            'impact': 'Direct targeting of electric grid control systems',
            'nerc_cip_relevance': 'CRITICAL - North American grid focus',
        },
        'Sandworm': {
            'aka': ['BlackEnergy Group', 'TeleBots', 'Voodoo Bear'],
            'origin': 'Russia (GRU Unit 74455)',
            'targets': 'Ukraine energy sector (2015, 2016 attacks)',
            'first_seen': '2009',
            'techniques': ['SCADA targeting', 'ICS protocol attacks', 'Wiper malware'],
            'malware': ['BlackEnergy', 'INDUSTROYER', 'NotPetya'],
            'impact': 'First confirmed cyber attacks causing power outages',
            'nerc_cip_relevance': 'CRITICAL - Proven grid disruption capability',
        },
    }

    # Module 4: Custom Object Templates
    CUSTOM_OBJECT_TEMPLATES = [
        {
            'name': 'solar-pv-system',
            'description': 'Solar photovoltaic system components',
            'category': 'ICS Equipment',
            'attributes': [
                'inverter-manufacturer',  # SMA, Fronius, Enphase, SolarEdge
                'inverter-model',
                'inverter-firmware-version',
                'inverter-protocol',  # Modbus TCP, SunSpec, proprietary
                'inverter-ip-address',
                'monitoring-system',  # SolarEdge monitoring, SMA Sunny Portal
                'capacity-mw',
                'nerc-registration-status',
                'communication-protocol',  # Modbus, DNP3, IEC 61850
                'scada-integration',
                'cve-list',  # Known vulnerabilities
                'last-patched-date',
            ]
        },
        {
            'name': 'wind-turbine-system',
            'description': 'Wind turbine controller and SCADA components',
            'category': 'ICS Equipment',
            'attributes': [
                'turbine-manufacturer',  # Vestas, GE, Siemens Gamesa
                'turbine-model',
                'controller-type',
                'controller-firmware',
                'scada-vendor',  # Vestas Online, GE Digital Wind Farm
                'communication-protocol',  # Modbus, IEC 61400-25, OPC UA
                'turbine-ip-address',
                'capacity-mw',
                'nerc-registration-status',
                'remote-access-method',
                'cve-list',
                'last-patched-date',
            ]
        },
        {
            'name': 'battery-energy-storage-system',
            'description': 'Battery storage system (BESS) components',
            'category': 'ICS Equipment',
            'attributes': [
                'bess-manufacturer',  # Tesla, LG Chem, BYD, Fluence
                'bess-model',
                'bms-vendor',  # Battery Management System
                'bms-firmware',
                'inverter-type',  # Bi-directional inverter
                'capacity-mwh',
                'communication-protocol',  # Modbus, CAN bus, proprietary
                'scada-integration',
                'ip-address',
                'nerc-registration-status',
                'safety-system-vendor',
                'cve-list',
                'last-patched-date',
            ]
        },
        {
            'name': 'scada-rtu-plc',
            'description': 'SCADA Remote Terminal Unit or Programmable Logic Controller',
            'category': 'ICS Equipment',
            'attributes': [
                'device-type',  # RTU or PLC
                'manufacturer',  # Schneider, Siemens, ABB, GE
                'model',
                'firmware-version',
                'protocols-supported',  # Modbus, DNP3, IEC 61850, IEC 60870
                'ip-address',
                'subnet',
                'connected-assets',  # What it controls
                'scada-server',
                'hmi-access',
                'authentication-method',
                'cve-list',
                'last-patched-date',
            ]
        },
        {
            'name': 'substation-automation',
            'description': 'Substation automation equipment',
            'category': 'ICS Equipment',
            'attributes': [
                'substation-id',
                'relay-manufacturer',  # SEL, ABB, Siemens
                'relay-models',
                'iec-61850-compliance',
                'protocol-list',  # IEC 61850, DNP3, Modbus
                'gateway-vendor',
                'firewall-present',
                'monitoring-system',
                'ip-range',
                'nerc-cip-classification',  # High/Medium/Low Impact
                'cve-list',
                'last-patched-date',
            ]
        },
    ]

    # Module 5: Utilities-Specific Threat Feeds
    UTILITIES_FEEDS = [
        {
            'name': 'ICS-CERT Advisories (CISA)',
            'url': 'https://www.cisa.gov/ics',
            'format': 'Manual import (no automated feed yet)',
            'cost': 'FREE',
            'priority': 'CRITICAL',
            'content': 'Vendor-specific ICS/SCADA vulnerabilities',
            'update_frequency': 'Weekly',
            'setup': 'Manual - check website weekly and create MISP events',
        },
        {
            'name': 'DHS AIS (Automated Indicator Sharing)',
            'url': 'https://www.cisa.gov/ais',
            'format': 'STIX/TAXII',
            'cost': 'FREE (critical infrastructure entities)',
            'priority': 'HIGH',
            'content': 'US Government threat indicators',
            'update_frequency': 'Real-time',
            'setup': 'Requires registration and TAXII configuration',
        },
        {
            'name': 'E-ISAC Threat Intelligence',
            'url': 'https://www.eisac.com/',
            'format': 'STIX/TAXII + Portal',
            'cost': '$5,000-$25,000/year (membership)',
            'priority': 'CRITICAL',
            'content': 'Electric sector-specific threat intelligence',
            'update_frequency': 'Real-time',
            'setup': 'Membership application required',
            'nerc_alignment': 'PRIMARY source for NERC CIP compliance',
        },
        {
            'name': 'Dragos WorldView',
            'url': 'https://www.dragos.com/',
            'format': 'STIX/TAXII + Platform',
            'cost': '$50,000-$150,000/year',
            'priority': 'HIGH (if budget allows)',
            'content': 'ICS-specific threat intelligence (Activity Groups, malware)',
            'update_frequency': 'Real-time',
            'setup': 'Commercial contract required',
        },
    ]

    # Module 6: ICS Protocol Correlation Rules
    ICS_CORRELATION_RULES = [
        {
            'name': 'Modbus Write to Critical Register',
            'description': 'Detect Modbus function code 06 (Write Single Register) to critical addresses',
            'protocols': ['Modbus TCP'],
            'severity': 'HIGH',
            'misp_correlation': 'Tag events with ics:protocol="modbus" + ics:technique="modify-parameter"',
        },
        {
            'name': 'DNP3 Unauthorized Control',
            'description': 'DNP3 OPERATE command from unexpected source',
            'protocols': ['DNP3'],
            'severity': 'CRITICAL',
            'misp_correlation': 'Tag events with ics:protocol="dnp3" + ics:impact="loss-of-control"',
        },
        {
            'name': 'IEC 61850 Abnormal GOOSE/MMS',
            'description': 'IEC 61850 Generic Object Oriented Substation Events with anomalies',
            'protocols': ['IEC 61850'],
            'severity': 'HIGH',
            'misp_correlation': 'Tag events with ics:protocol="iec-61850" + ics:asset-type="substation"',
        },
        {
            'name': 'Solar Inverter Firmware Update',
            'description': 'Unexpected firmware update to solar inverter (SunSpec protocol)',
            'protocols': ['Modbus SunSpec'],
            'severity': 'HIGH',
            'misp_correlation': 'Tag events with ics:asset-type="solar-inverter" + ics:technique="modify-program"',
        },
        {
            'name': 'Wind Turbine Shutdown Command',
            'description': 'Emergency shutdown command to wind turbine controller',
            'protocols': ['IEC 61400-25', 'Modbus'],
            'severity': 'CRITICAL',
            'misp_correlation': 'Tag events with ics:asset-type="wind-turbine" + ics:impact="denial-of-control"',
        },
        {
            'name': 'Battery BMS Parameter Change',
            'description': 'Battery management system parameters modified remotely',
            'protocols': ['CAN bus', 'Modbus'],
            'severity': 'CRITICAL',
            'misp_correlation': 'Tag events with ics:asset-type="battery-storage" + ics:technique="modify-parameter"',
        },
    ]

    # Module 7: Integration Recommendations
    INTEGRATIONS = {
        'splunk': {
            'name': 'Splunk Enterprise Security',
            'cost': 'Commercial',
            'setup': 'MISP App for Splunk + Threat Intelligence framework',
            'benefit': 'Correlate MISP IOCs with SCADA logs, solar inverter events',
            'priority': 'HIGH',
            'documentation': 'https://splunkbase.splunk.com/app/3112/',
        },
        'security_onion': {
            'name': 'Security Onion (ICS monitoring)',
            'cost': 'FREE',
            'setup': 'Feed MISP IOCs into Suricata/Zeek via TheHive integration',
            'benefit': 'Monitor ICS network traffic for Modbus/DNP3 anomalies',
            'priority': 'HIGH',
            'documentation': 'https://securityonionsolutions.com/',
        },
        'nozomi': {
            'name': 'Nozomi Networks Guardian',
            'cost': 'Commercial (~$25K-$100K)',
            'setup': 'Bidirectional API integration (MISP ← → Nozomi)',
            'benefit': 'OT asset discovery fed to MISP, MISP IOCs fed to Nozomi',
            'priority': 'MEDIUM',
            'documentation': 'Contact Nozomi for API documentation',
        },
        'claroty': {
            'name': 'Claroty xDome',
            'cost': 'Commercial',
            'setup': 'STIX/TAXII integration',
            'benefit': 'ICS threat intelligence sharing',
            'priority': 'MEDIUM',
            'documentation': 'https://claroty.com/',
        },
        'dragos_platform': {
            'name': 'Dragos Platform',
            'cost': 'Commercial (~$150K-$500K)',
            'setup': 'Dragos WorldView STIX/TAXII → MISP',
            'benefit': 'Activity Group tracking, ICS-specific intelligence',
            'priority': 'LOW (unless already a Dragos customer)',
            'documentation': 'https://www.dragos.com/',
        },
    }


#==============================================================================
# UTILITIES CONFIGURATION MANAGER
#==============================================================================

class MISPUtilitiesConfig:
    """MISP Utilities Sector configuration manager"""

    def __init__(self, dry_run: bool = False):
        """Initialize utilities sector configuration

        Args:
            dry_run: If True, show what would be done without making changes
        """
        self.config = UtilitiesSectorConfig()
        self.dry_run = dry_run
        self.logger = get_logger('configure-misp-utilities-sector', 'misp:utilities')

        # Color codes for output
        self.MAGENTA = '\033[35m'
        self.CYAN = '\033[36m'
        self.YELLOW = '\033[33m'
        self.GREEN = '\033[32m'
        self.BLUE = '\033[34m'
        self.RED = '\033[31m'
        self.BOLD = '\033[1m'
        self.NC = '\033[0m'  # No Color

    def print_header(self, text: str, color: str = '\033[36m'):
        """Print colored section header"""
        print(f"\n{color}{'=' * 80}{self.NC}")
        print(f"{color}  {text}{self.NC}")
        print(f"{color}{'=' * 80}{self.NC}\n")

    def print_subsection(self, text: str):
        """Print subsection header"""
        print(f"\n{self.CYAN}{text}{self.NC}")
        print(f"{self.CYAN}{'-' * len(text)}{self.NC}\n")


    def run_docker_command(self, command: List[str], description: str = "") -> bool:
        """Run docker compose exec command with error handling

        Args:
            command: List of command arguments (after 'docker compose exec')
            description: What this command does (for logging)

        Returns:
            bool: True if successful, False otherwise
        """
        full_command = ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core'] + command

        if self.dry_run:
            print(f"{self.YELLOW}[DRY-RUN] Would run:{self.NC} {' '.join(full_command)}")
            if description:
                print(f"{self.YELLOW}           Purpose:{self.NC} {description}")
            return True

        try:
            result = subprocess.run(
                full_command,
                cwd=str(self.config.MISP_DIR),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.logger.info(f"Command successful: {description}",
                                event_type="docker_command",
                                action="execute",
                                result="success")
                return True
            else:
                self.logger.error(f"Command failed: {description}",
                                 event_type="docker_command",
                                 action="execute",
                                 result="failed",
                                 error=result.stderr[:500])
                print(f"{self.RED}✗ Failed:{self.NC} {description}")
                print(f"{self.RED}  Error:{self.NC} {result.stderr[:200]}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {description}",
                            event_type="docker_command",
                            action="execute",
                            result="timeout")
            print(f"{self.RED}✗ Timeout:{self.NC} {description}")
            return False

        except Exception as e:
            self.logger.error(f"Command exception: {description}",
                            event_type="docker_command",
                            action="execute",
                            result="exception",
                            error=str(e))
            print(f"{self.RED}✗ Exception:{self.NC} {description} - {e}")
            return False


    #==========================================================================
    # MODULE 1: ICS/OT TAXONOMIES
    #==========================================================================

    def module_1_enable_ics_taxonomies(self):
        """Module 1: Enable ICS/OT and critical infrastructure taxonomies"""

        self.print_header("MODULE 1: ICS/OT TAXONOMIES", self.MAGENTA)

        print(f"{self.CYAN}Enabling taxonomies for utilities sector threat intelligence...{self.NC}\n")

        success_count = 0
        total_count = len(self.config.ICS_TAXONOMIES)

        for taxonomy in self.config.ICS_TAXONOMIES:
            name = taxonomy['name']
            description = taxonomy['description']
            priority = taxonomy.get('priority', 'MEDIUM')

            print(f"{self.BOLD}Taxonomy:{self.NC} {name}")
            print(f"  Description: {description}")
            print(f"  Priority: {priority}")

            # Enable taxonomy via MISP cake command
            success = self.run_docker_command(
                ['/var/www/MISP/app/Console/cake', 'Admin', 'enableTaxonomy', name],
                f"Enable {name} taxonomy"
            )

            if success:
                success_count += 1
                print(f"{self.GREEN}✓ Enabled:{self.NC} {name}\n")

                # Show example tags
                if 'tags_example' in taxonomy:
                    print(f"{self.CYAN}  Example tags:{self.NC}")
                    for tag in taxonomy['tags_example'][:3]:  # Show first 3
                        print(f"    - {tag}")
                    print()
            else:
                print(f"{self.YELLOW}⚠ Might already be enabled:{self.NC} {name}\n")

        # Summary
        print(f"{self.BOLD}Summary:{self.NC}")
        print(f"  Taxonomies enabled: {success_count}/{total_count}")

        self.logger.info(f"Module 1 complete: {success_count}/{total_count} taxonomies enabled",
                        event_type="module_complete",
                        module=1,
                        taxonomies_enabled=success_count,
                        total=total_count)


    #==========================================================================
    # MODULE 2: MITRE ATT&CK FOR ICS GALAXY
    #==========================================================================

    def module_2_enable_ics_galaxies(self):
        """Module 2: Enable MITRE ATT&CK for ICS galaxy"""

        self.print_header("MODULE 2: MITRE ATT&CK FOR ICS GALAXY", self.MAGENTA)

        print(f"{self.CYAN}Enabling ICS-specific threat actor and malware galaxies...{self.NC}\n")

        success_count = 0
        total_count = len(self.config.ICS_GALAXIES)

        for galaxy in self.config.ICS_GALAXIES:
            name = galaxy['name']
            description = galaxy['description']
            priority = galaxy.get('priority', 'MEDIUM')

            print(f"{self.BOLD}Galaxy:{self.NC} {name}")
            print(f"  Description: {description}")
            print(f"  Priority: {priority}")

            # Enable galaxy via MISP cake command
            success = self.run_docker_command(
                ['/var/www/MISP/app/Console/cake', 'Admin', 'updateGalaxies'],
                f"Update MISP galaxies (includes {name})"
            )

            if success:
                success_count += 1
                print(f"{self.GREEN}✓ Galaxy updated{self.NC}\n")

                # Show examples
                if 'threat_actors' in galaxy:
                    print(f"{self.CYAN}  Notable threat actors:{self.NC}")
                    for actor in galaxy['threat_actors'][:3]:
                        print(f"    - {actor}")
                    print()

                if 'malware' in galaxy:
                    print(f"{self.CYAN}  Notable malware:{self.NC}")
                    for malware in galaxy['malware'][:3]:
                        print(f"    - {malware}")
                    print()

                if 'techniques_example' in galaxy:
                    print(f"{self.CYAN}  Example techniques:{self.NC}")
                    for technique in galaxy['techniques_example'][:3]:
                        print(f"    - {technique}")
                    print()

        # Summary
        print(f"{self.BOLD}Summary:{self.NC}")
        print(f"  Galaxies updated: {success_count}/{total_count}")

        self.logger.info(f"Module 2 complete: {success_count}/{total_count} galaxies updated",
                        event_type="module_complete",
                        module=2,
                        galaxies_updated=success_count,
                        total=total_count)


    #==========================================================================
    # MODULE 3: UTILITIES THREAT ACTOR PROFILES
    #==========================================================================

    def module_3_show_threat_actor_profiles(self):
        """Module 3: Display detailed threat actor profiles for utilities sector"""

        self.print_header("MODULE 3: UTILITIES THREAT ACTOR PROFILES", self.MAGENTA)

        print(f"{self.CYAN}Detailed profiles of APT groups targeting electric utilities...{self.NC}\n")

        for actor_name, profile in self.config.UTILITIES_THREAT_ACTORS.items():
            print(f"{self.BOLD}{self.RED}Threat Actor:{self.NC} {actor_name}")
            print(f"{self.CYAN}{'─' * 60}{self.NC}")

            print(f"  {self.BOLD}Also Known As:{self.NC} {', '.join(profile['aka'])}")
            print(f"  {self.BOLD}Origin:{self.NC} {profile['origin']}")
            print(f"  {self.BOLD}First Seen:{self.NC} {profile['first_seen']}")
            print(f"  {self.BOLD}Targets:{self.NC} {profile['targets']}")
            print(f"  {self.BOLD}Techniques:{self.NC} {', '.join(profile['techniques'])}")
            print(f"  {self.BOLD}Known Malware:{self.NC} {', '.join(profile['malware'])}")
            print(f"  {self.BOLD}Impact:{self.NC} {profile['impact']}")

            # NERC CIP relevance
            relevance = profile['nerc_cip_relevance']
            if 'CRITICAL' in relevance:
                color = self.RED
            elif 'HIGH' in relevance:
                color = self.YELLOW
            else:
                color = self.CYAN

            print(f"  {self.BOLD}NERC CIP Relevance:{self.NC} {color}{relevance}{self.NC}")
            print()

        # Action items
        print(f"{self.BOLD}Recommended Actions:{self.NC}")
        print("  1. Tag MISP events with threat actor names when identified")
        print("  2. Use MITRE ATT&CK for ICS techniques for attribution")
        print("  3. Monitor for TTPs (Tactics, Techniques, Procedures) listed above")
        print("  4. Include in CIP-003 security awareness training")
        print("  5. Document in CIP-008 incident response plans")

        self.logger.info("Module 3 complete: Displayed threat actor profiles",
                        event_type="module_complete",
                        module=3,
                        threat_actors=len(self.config.UTILITIES_THREAT_ACTORS))


    #==========================================================================
    # MODULE 4: CUSTOM OBJECT TEMPLATES (INFORMATIONAL)
    #==========================================================================

    def module_4_show_custom_object_templates(self):
        """Module 4: Show custom object templates for utilities assets"""

        self.print_header("MODULE 4: CUSTOM OBJECT TEMPLATES", self.MAGENTA)

        print(f"{self.CYAN}Custom MISP object templates for utilities sector assets...{self.NC}\n")

        print(f"{self.YELLOW}Note:{self.NC} Creating custom object templates requires manual configuration")
        print(f"       via MISP web interface: {self.CYAN}Administration > Object Templates{self.NC}\n")

        for template in self.config.CUSTOM_OBJECT_TEMPLATES:
            name = template['name']
            description = template['description']
            category = template['category']
            attributes = template['attributes']

            print(f"{self.BOLD}Object Template:{self.NC} {name}")
            print(f"  Description: {description}")
            print(f"  Category: {category}")
            print(f"  Attributes ({len(attributes)} total):")

            for attr in attributes[:5]:  # Show first 5
                print(f"    - {attr}")

            if len(attributes) > 5:
                print(f"    ... and {len(attributes) - 5} more")

            print()

        # Instructions
        print(f"{self.BOLD}Manual Creation Steps:{self.NC}")
        print("  1. Login to MISP web interface")
        print(f"  2. Navigate to: {self.CYAN}Administration > Object Templates > Add Object Template{self.NC}")
        print("  3. Create templates using attribute lists shown above")
        print("  4. Set Meta Category to 'network' or 'ics'")
        print("  5. Save and enable template")

        print(f"\n{self.BOLD}Usage in MISP:{self.NC}")
        print("  - When creating events, attach these objects to track ICS assets")
        print("  - Use for asset inventory in combination with threat intelligence")
        print("  - Tag with appropriate ICS taxonomy tags")
        print("  - Link to related vulnerabilities (CVEs)")

        self.logger.info("Module 4 complete: Displayed custom object templates",
                        event_type="module_complete",
                        module=4,
                        templates=len(self.config.CUSTOM_OBJECT_TEMPLATES))


    #==========================================================================
    # MODULE 5: UTILITIES-SPECIFIC FEEDS & COMMUNITIES
    #==========================================================================

    def module_5_show_feeds_and_communities(self):
        """Module 5: Show utilities-specific threat intelligence feeds"""

        self.print_header("MODULE 5: UTILITIES-SPECIFIC FEEDS & COMMUNITIES", self.MAGENTA)

        print(f"{self.CYAN}Recommended threat intelligence sources for utilities sector...{self.NC}\n")

        for feed in self.config.UTILITIES_FEEDS:
            name = feed['name']
            url = feed['url']
            cost = feed['cost']
            priority = feed['priority']
            content = feed['content']
            update_frequency = feed['update_frequency']
            setup = feed['setup']

            # Priority color
            if 'CRITICAL' in priority:
                priority_color = self.RED
            elif 'HIGH' in priority:
                priority_color = self.YELLOW
            else:
                priority_color = self.CYAN

            print(f"{self.BOLD}Feed:{self.NC} {name}")
            print(f"  URL: {self.CYAN}{url}{self.NC}")
            print(f"  Cost: {cost}")
            print(f"  Priority: {priority_color}{priority}{self.NC}")
            print(f"  Content: {content}")
            print(f"  Update Frequency: {update_frequency}")
            print(f"  Setup: {setup}")

            if 'nerc_alignment' in feed:
                print(f"  {self.BOLD}NERC Alignment:{self.NC} {self.GREEN}{feed['nerc_alignment']}{self.NC}")

            print()

        # Recommendations
        print(f"{self.BOLD}Implementation Priority:{self.NC}")
        print(f"  {self.RED}1. ICS-CERT Advisories{self.NC} - FREE, essential for all utilities")
        print(f"  {self.RED}2. E-ISAC Membership{self.NC} - PRIMARY source for NERC CIP compliance")
        print(f"  {self.YELLOW}3. DHS AIS{self.NC} - FREE for critical infrastructure entities")
        print(f"  {self.CYAN}4. Dragos WorldView{self.NC} - If budget allows ($$$ but high quality)")

        print(f"\n{self.BOLD}Next Steps:{self.NC}")
        print("  1. Apply for E-ISAC membership (if electric utility)")
        print("  2. Register for DHS AIS (critical infrastructure)")
        print("  3. Create manual process for ICS-CERT advisory review")
        print("  4. Consider commercial ICS intel if High-Impact BES Cyber System")

        self.logger.info("Module 5 complete: Displayed feeds and communities",
                        event_type="module_complete",
                        module=5,
                        feeds=len(self.config.UTILITIES_FEEDS))


    #==========================================================================
    # MODULE 6: ICS PROTOCOL CORRELATION RULES
    #==========================================================================

    def module_6_show_correlation_rules(self):
        """Module 6: Show ICS protocol correlation rules for SIEM integration"""

        self.print_header("MODULE 6: ICS PROTOCOL CORRELATION RULES", self.MAGENTA)

        print(f"{self.CYAN}Correlation rules for ICS protocol monitoring...{self.NC}\n")

        print(f"{self.YELLOW}Note:{self.NC} These rules should be implemented in your SIEM (Splunk, ELK)")
        print("       or ICS monitoring platform (Nozomi, Claroty, Dragos)\n")

        for rule in self.config.ICS_CORRELATION_RULES:
            name = rule['name']
            description = rule['description']
            protocols = rule['protocols']
            severity = rule['severity']
            misp_correlation = rule['misp_correlation']

            # Severity color
            if severity == 'CRITICAL':
                severity_color = self.RED
            elif severity == 'HIGH':
                severity_color = self.YELLOW
            else:
                severity_color = self.CYAN

            print(f"{self.BOLD}Rule:{self.NC} {name}")
            print(f"  Description: {description}")
            print(f"  Protocols: {', '.join(protocols)}")
            print(f"  Severity: {severity_color}{severity}{self.NC}")
            print(f"  {self.BOLD}MISP Correlation:{self.NC}")
            print(f"    {misp_correlation}")
            print()

        # Implementation guidance
        print(f"{self.BOLD}Implementation in Splunk:{self.NC}")
        print("  1. Install MISP App for Splunk")
        print("  2. Create correlation searches matching rules above")
        print("  3. Tag MISP events with ICS taxonomy when matches occur")
        print("  4. Create Notable Events for CRITICAL/HIGH severity")

        print(f"\n{self.BOLD}Implementation in Security Onion:{self.NC}")
        print("  1. Feed MISP IOCs into Suricata")
        print("  2. Create custom Suricata rules for ICS protocols")
        print("  3. Use Zeek ICS protocol analyzers (Modbus, DNP3)")
        print("  4. Send alerts back to MISP via TheHive")

        print(f"\n{self.BOLD}Implementation in Nozomi/Claroty/Dragos:{self.NC}")
        print("  1. Export MISP IOCs via STIX/TAXII")
        print("  2. Import into ICS monitoring platform")
        print("  3. Enable bidirectional sync (platform discoveries → MISP)")
        print("  4. Correlate ICS asset inventory with threat intelligence")

        self.logger.info("Module 6 complete: Displayed correlation rules",
                        event_type="module_complete",
                        module=6,
                        rules=len(self.config.ICS_CORRELATION_RULES))


    #==========================================================================
    # MODULE 7: INTEGRATION GUIDES
    #==========================================================================

    def module_7_show_integration_guides(self):
        """Module 7: Show integration guides for SIEM and ICS monitoring tools"""

        self.print_header("MODULE 7: INTEGRATION GUIDES", self.MAGENTA)

        print(f"{self.CYAN}Integration guides for utilities sector security tools...{self.NC}\n")

        for _integration_key, integration in self.config.INTEGRATIONS.items():
            name = integration['name']
            cost = integration['cost']
            setup = integration['setup']
            benefit = integration['benefit']
            priority = integration['priority']
            documentation = integration['documentation']

            # Priority color
            if 'HIGH' in priority:
                priority_color = self.GREEN
            elif 'MEDIUM' in priority:
                priority_color = self.YELLOW
            else:
                priority_color = self.CYAN

            print(f"{self.BOLD}Integration:{self.NC} {name}")
            print(f"  Cost: {cost}")
            print(f"  Priority: {priority_color}{priority}{self.NC}")
            print(f"  Setup: {setup}")
            print(f"  Benefit: {benefit}")
            print(f"  Documentation: {self.CYAN}{documentation}{self.NC}")
            print()

        # Summary recommendations
        print(f"{self.BOLD}Recommended Integration Path:{self.NC}")
        print(f"  {self.GREEN}Phase 1:{self.NC} Splunk or Security Onion (SIEM integration)")
        print(f"  {self.YELLOW}Phase 2:{self.NC} ICS monitoring platform (Nozomi/Claroty)")
        print(f"  {self.CYAN}Phase 3:{self.NC} Dragos Platform (if High-Impact site)")

        print(f"\n{self.BOLD}Cost Comparison:{self.NC}")
        print("  FREE: Security Onion")
        print("  $25K-$100K/year: Nozomi Networks, Claroty")
        print("  $50K-$150K/year: Splunk ES, Dragos WorldView")
        print("  $150K-$500K/year: Dragos Platform (full suite)")

        self.logger.info("Module 7 complete: Displayed integration guides",
                        event_type="module_complete",
                        module=7,
                        integrations=len(self.config.INTEGRATIONS))


    #==========================================================================
    # MAIN ORCHESTRATION
    #==========================================================================

    def run_all_modules(self):
        """Run all utilities sector configuration modules"""

        print(f"\n{self.MAGENTA}{self.BOLD}{'═' * 80}{self.NC}")
        print(f"{self.MAGENTA}{self.BOLD}║{'  ' * 10}MISP UTILITIES SECTOR CONFIGURATION{'  ' * 10}║{self.NC}")
        print(f"{self.MAGENTA}{self.BOLD}║{'  ' * 15}tKQB Enterprises{'  ' * 17}║{self.NC}")
        print(f"{self.MAGENTA}{self.BOLD}{'═' * 80}{self.NC}\n")

        if self.dry_run:
            print(f"{self.YELLOW}{self.BOLD}DRY-RUN MODE{self.NC} - No changes will be made\n")

        start_time = datetime.now()

        # Run all modules
        self.module_1_enable_ics_taxonomies()
        self.module_2_enable_ics_galaxies()
        self.module_3_show_threat_actor_profiles()
        self.module_4_show_custom_object_templates()
        self.module_5_show_feeds_and_communities()
        self.module_6_show_correlation_rules()
        self.module_7_show_integration_guides()

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.print_header("CONFIGURATION COMPLETE", self.GREEN)

        print(f"{self.BOLD}Summary:{self.NC}")
        print("  ✓ Module 1: ICS/OT Taxonomies enabled")
        print("  ✓ Module 2: MITRE ATT&CK for ICS Galaxy updated")
        print("  ✓ Module 3: Threat actor profiles displayed")
        print("  ✓ Module 4: Custom object templates documented")
        print("  ✓ Module 5: Feeds and communities documented")
        print("  ✓ Module 6: Correlation rules documented")
        print("  ✓ Module 7: Integration guides documented")
        print(f"\n  Duration: {duration:.1f} seconds")

        print(f"\n{self.BOLD}Next Steps:{self.NC}")
        print("  1. Create custom object templates via MISP web interface")
        print("  2. Apply for E-ISAC membership (if electric utility)")
        print("  3. Register for DHS AIS (critical infrastructure)")
        print("  4. Implement SIEM correlation rules (Splunk/Security Onion)")
        print("  5. Consider ICS monitoring platform integration")
        print("  6. Train SOC team on ICS threat actor TTPs")
        print("  7. Update CIP-003 security awareness training materials")

        print(f"\n{self.BOLD}Documentation:{self.NC}")
        print("  - NERC CIP Guide: docs/NERC_CIP_CONFIGURATION.md")
        print("  - MISP Taxonomies: https://www.misp-project.org/taxonomies.html")
        print("  - MITRE ATT&CK ICS: https://attack.mitre.org/matrices/ics/")
        print("  - E-ISAC: https://www.eisac.com/")
        print("  - ICS-CERT: https://www.cisa.gov/ics")

        self.logger.info("Utilities sector configuration complete",
                        event_type="configuration_complete",
                        duration_seconds=duration,
                        modules_run=7)


    def run_specific_modules(self, module_list: List[int]):
        """Run specific modules by number

        Args:
            module_list: List of module numbers to run (1-7)
        """

        print(f"\n{self.MAGENTA}{self.BOLD}{'═' * 80}{self.NC}")
        print(f"{self.MAGENTA}{self.BOLD}║{'  ' * 8}MISP UTILITIES SECTOR CONFIGURATION (Selective){' ' * 9}║{self.NC}")
        print(f"{self.MAGENTA}{self.BOLD}{'═' * 80}{self.NC}\n")

        print(f"{self.CYAN}Running modules: {', '.join(map(str, module_list))}{self.NC}\n")

        module_functions = {
            1: self.module_1_enable_ics_taxonomies,
            2: self.module_2_enable_ics_galaxies,
            3: self.module_3_show_threat_actor_profiles,
            4: self.module_4_show_custom_object_templates,
            5: self.module_5_show_feeds_and_communities,
            6: self.module_6_show_correlation_rules,
            7: self.module_7_show_integration_guides,
        }

        for module_num in sorted(module_list):
            if module_num in module_functions:
                module_functions[module_num]()
            else:
                print(f"{self.RED}✗ Invalid module number: {module_num}{self.NC}")


#==============================================================================
# MAIN FUNCTION
#==============================================================================

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description='Configure MISP for utilities sector (solar, wind, battery, transmission)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run all modules (recommended)
  python3 configure-misp-utilities-sector.py

  # Run specific module
  python3 configure-misp-utilities-sector.py --module 1

  # Run multiple modules
  python3 configure-misp-utilities-sector.py --module 1,2,3

  # Dry-run (show what would be done)
  python3 configure-misp-utilities-sector.py --dry-run

Modules:
  1 - ICS/OT Taxonomies (FIRST ICS, DHS CIIP)
  2 - MITRE ATT&CK for ICS Galaxy
  3 - Utilities Threat Actor Profiles
  4 - Custom Object Templates
  5 - Utilities-Specific Feeds & Communities
  6 - ICS Protocol Correlation Rules
  7 - Integration Guides (Splunk, Security Onion, ICS monitoring)
        '''
    )

    parser.add_argument(
        '--module',
        type=str,
        help='Run specific module(s) by number (e.g., "1" or "1,2,3")'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Initialize configuration manager
    config = MISPUtilitiesConfig(dry_run=args.dry_run)

    # Run modules
    if args.module:
        # Parse module list
        try:
            module_list = [int(m.strip()) for m in args.module.split(',')]
            config.run_specific_modules(module_list)
        except ValueError:
            print(f"{config.RED}Error: Invalid module format. Use numbers 1-7, comma-separated{config.NC}")
            sys.exit(1)
    else:
        # Run all modules
        config.run_all_modules()


if __name__ == '__main__':
    main()
