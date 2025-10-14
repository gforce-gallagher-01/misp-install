#!/usr/bin/env python3
"""
MISP NERC CIP Configuration Script
tKQB Enterprises - Energy Utilities Edition
Version: 1.0

Configures MISP for NERC CIP compliance in electric utilities
operating solar, wind, and battery energy storage systems.

Focus: ICS/SCADA threat intelligence for Low & Medium Impact BES Cyber Systems
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import centralized modules
from misp_logger import get_logger
from lib.colors import Colors
from lib.setup_helper import MISPSetupHelper

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# ==========================================
# NERC CIP Configuration
# ==========================================

class NERCCIPConfig:
    """NERC CIP-specific configuration"""
    MISP_DIR = Path("/opt/misp")

    # ICS/SCADA-Specific OSINT Feeds for NERC CIP
    NERC_CIP_FEEDS = [
        # Core Malware Feeds (ICS malware IOCs)
        "CIRCL OSINT Feed",
        "Abuse.ch URLhaus",              # Malware distribution URLs
        "Abuse.ch ThreatFox",            # IOCs from ICS malware families
        "Abuse.ch Feodo Tracker",        # Botnet C2 infrastructure
        "Abuse.ch SSL Blacklist",        # Malicious SSL certificates

        # APT Groups Targeting Critical Infrastructure
        "Bambenek Consulting - C2 All Indicator Feed",

        # IP Reputation (Electronic Access Point protection)
        "Blocklist.de",                  # SSH/RDP brute force
        "Botvrij.eu",                    # General malicious IPs

        # Phishing (NERC CIP-003 security awareness)
        "OpenPhish url",                 # Phishing targeting utility employees
        "Phishtank online valid phishing",

        # Comprehensive Threat Intelligence
        "DigitalSide Threat-Intel",
        "Cybercrime-Tracker - All",
        "MalwareBazaar Recent Additions",

        # Additional ICS-Relevant Feeds
        "Dataplane.org - sipquery",      # SIP attack attempts
        "Dataplane.org - vncrfb",        # VNC brute force
    ]

    # NERC CIP-Specific Settings
    NERC_CIP_SETTINGS = {
        # Incident Response (CIP-008)
        "MISP.incident_response": True,

        # Extended retention for NERC audits (3-7 year cycles)
        "MISP.log_new_audit": True,
        "MISP.log_auth": True,

        # Sharing Controls (CIP-011 information protection)
        "MISP.default_event_distribution": "0",  # Your organization only
        "MISP.default_attribute_distribution": "0",

        # API Security
        "Security.rest_client_enable_arbitrary_body_for_URL_object": False,

        # Correlation (detect patterns across ICS threats)
        "MISP.correlation_engine": "Default",
        "MISP.enable_advanced_correlations": True,

        # Background Jobs (automated feed updates)
        "MISP.background_jobs": True,

        # Taxonomies (TLP, ICS classification)
        "MISP.enable_taxonomy": True,

        # Enrichment for ICS data
        "Plugin.Enrichment_services_enable": True,
    }

    # Custom Taxonomies for NERC CIP
    NERC_CIP_TAXONOMIES = {
        "tlp": True,                     # Traffic Light Protocol (required)
        "workflow": True,                # Incident response workflow
        "priority-level": True,          # Threat prioritization
        "incident-category": True,       # CIP-008 incident classification
        "cssa": True,                    # ICS/SCADA specific
        "mitre-attack-pattern": True,   # MITRE ATT&CK for ICS
    }

# ==========================================
# NERC CIP Configuration Manager
# ==========================================

class MISPNERCCIPConfig:
    """MISP NERC CIP configuration manager"""

    def __init__(self, dry_run: bool = False):
        self.config = NERCCIPConfig()
        self.dry_run = dry_run
        self.start_time = time.time()

        # Initialize centralized logger
        self.logger = get_logger('configure-misp-nerc-cip', 'misp:nerc-cip')

        # Initialize centralized setup helper
        self.setup_helper = MISPSetupHelper(self.logger.logger, self.config.MISP_DIR, dry_run=dry_run)

        self.logger.info(
            "MISP NERC CIP configuration initiated",
            event_type="nerc_cip_config",
            action="start"
        )

    def log(self, message: str, level: str = "info"):
        """Print colored log message"""
        if level == "error":
            print(Colors.error(message))
        elif level == "success":
            print(Colors.success(message))
        elif level == "warning":
            print(Colors.warning(message))
        elif level == "step":
            print(Colors.step(message))
        elif level == "nerc":
            print(Colors.nerc(message))
        else:
            print(Colors.info(message))

    def print_banner(self):
        """Print startup banner"""
        print()
        print(Colors.colored("=" * 70, Colors.CYAN))
        print(Colors.colored("     MISP NERC CIP Configuration for Energy Utilities", Colors.CYAN))
        print(Colors.colored("        ICS/SCADA Threat Intelligence Setup", Colors.CYAN))
        print(Colors.colored("        tKQB Enterprises - Version 1.0", Colors.CYAN))
        print(Colors.colored("=" * 70, Colors.CYAN))
        print()
        print(Colors.nerc("Configuring MISP for NERC CIP Compliance"))
        print(Colors.nerc("Sectors: Solar, Wind, Battery Energy Storage"))
        print(Colors.nerc("Impact Levels: Low & Medium BES Cyber Systems"))
        print()

    def check_misp_running(self) -> bool:
        """Check if MISP containers are running"""
        self.logger.info("Checking MISP containers", event_type="nerc_cip_config", action="check_containers")

        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--services', '--filter', 'status=running'],
                cwd=self.config.MISP_DIR,
                capture_output=True,
                text=True,
                timeout=10
            )

            running_services = result.stdout.strip().split('\n')
            required_services = ['misp-core', 'db', 'redis', 'misp-modules']

            all_running = all(svc in running_services for svc in required_services)

            if all_running:
                self.logger.success("All MISP services running", event_type="nerc_cip_config", action="check_containers")
                return True
            else:
                missing = [svc for svc in required_services if svc not in running_services]
                self.logger.warning(f"Missing services: {', '.join(missing)}", event_type="nerc_cip_config", action="check_containers")
                return False

        except Exception as e:
            self.logger.error(f"Could not check container status: {e}", event_type="nerc_cip_config", action="check_containers", error_message=str(e))
            return False

    def run_cake_command(self, command: List[str]) -> bool:
        """Run MISP console cake command (uses centralized MISPSetupHelper)"""
        if len(command) >= 2:
            # Use centralized setup helper
            success, output = self.setup_helper.run_cake_command(command[0], command[1])
            if not success and output:
                self.logger.warning(f"Command failed: {output[:200]}",
                                  event_type="nerc_cip_config", action="run_command")
            return success
        return False

    def set_setting(self, setting: str, value) -> bool:
        """Set a MISP setting"""
        value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        return self.run_cake_command(['Admin', 'setSetting', setting, value_str])

    def configure_nerc_cip_settings(self):
        """Configure NERC CIP-specific MISP settings"""
        self.log("Configuring NERC CIP-specific settings", "step")
        self.logger.info("Configuring NERC CIP settings", event_type="nerc_cip_config", phase="nerc_settings")

        success_count = 0
        for setting, value in self.config.NERC_CIP_SETTINGS.items():
            if self.set_setting(setting, value):
                success_count += 1
                self.log(f"✓ Set {setting}", "info")
            else:
                self.log(f"✗ Could not set {setting}", "warning")

        self.logger.success(
            f"Configured {success_count}/{len(self.config.NERC_CIP_SETTINGS)} NERC CIP settings",
            event_type="nerc_cip_config",
            action="configure_settings",
            count=success_count
        )

        print()
        self.log(f"Configured {success_count}/{len(self.config.NERC_CIP_SETTINGS)} settings", "success")
        print()

    def show_feed_recommendations(self):
        """Show recommended feeds for NERC CIP"""
        self.log("ICS/SCADA Recommended Feeds for NERC CIP", "step")
        self.logger.info("Displaying NERC CIP feed recommendations", event_type="nerc_cip_config", phase="feed_recommendations")

        print()
        print(Colors.nerc("These feeds contain IOCs relevant to ICS/SCADA systems:"))
        print()

        print(Colors.colored("Core Malware & C2 Feeds:", Colors.YELLOW))
        for feed in self.config.NERC_CIP_FEEDS[:6]:
            print(f"  ✓ {feed}")
        print()

        print(Colors.colored("IP Reputation & Phishing:", Colors.YELLOW))
        for feed in self.config.NERC_CIP_FEEDS[6:10]:
            print(f"  ✓ {feed}")
        print()

        print(Colors.colored("Additional ICS-Relevant Feeds:", Colors.YELLOW))
        for feed in self.config.NERC_CIP_FEEDS[10:]:
            print(f"  ✓ {feed}")
        print()

        print(Colors.nerc("To enable feeds:"))
        print("  1. Access MISP web interface")
        print("  2. Go to: Sync Actions > List Feeds")
        print("  3. Search for each feed by name")
        print("  4. Enable and 'Fetch and store all feed data'")
        print()

    def show_nerc_cip_use_cases(self):
        """Show NERC CIP compliance use cases"""
        self.log("NERC CIP Compliance Use Cases", "step")
        print()

        use_cases = {
            "CIP-003-R2": "Security Awareness Training - Use MISP threat reports in training",
            "CIP-005-R2": "Electronic Access Point Monitoring - Export IOCs to firewalls",
            "CIP-007-R4": "Security Event Logging - MISP access logs as audit evidence",
            "CIP-008-R1": "Incident Response - Document incidents in MISP",
            "CIP-010-R3": "Vulnerability Assessment - Query MISP for ICS vulnerabilities",
            "CIP-011-R1": "BCSI Protection - MISP contains BES Cyber System Information",
            "CIP-013-R1": "Supply Chain Security - Track vendor security bulletins",
            "CIP-015-R1": "Internal Network Monitoring - Use MISP IOCs for detection",
        }

        for standard, description in use_cases.items():
            print(Colors.colored(f"{standard}:", Colors.CYAN))
            print(f"  {description}")
            print()

    def show_next_steps(self):
        """Show next steps for NERC CIP compliance"""
        print()
        print(Colors.colored("=" * 70, Colors.CYAN))
        print(Colors.colored("         NERC CIP CONFIGURATION COMPLETE", Colors.CYAN))
        print(Colors.colored("=" * 70, Colors.CYAN))
        print()

        print(Colors.nerc("Next Steps for NERC CIP Compliance:"))
        print()

        print(Colors.colored("1. Enable Recommended Feeds (Critical):", Colors.YELLOW))
        print("   Access MISP web interface: https://your-misp-domain")
        print("   Navigate to: Sync Actions > List Feeds")
        print("   Enable the ICS/SCADA-specific feeds listed above")
        print()

        print(Colors.colored("2. Configure Taxonomies:", Colors.YELLOW))
        print("   Go to: Event Actions > List Taxonomies")
        print("   Enable: TLP, workflow, priority-level, incident-category")
        print("   Enable: cssa (ICS/SCADA specific)")
        print()

        print(Colors.colored("3. Create Custom NERC CIP Taxonomies:", Colors.YELLOW))
        print("   Go to: Event Actions > Add Taxonomy")
        print("   Create tags: nerc-cip:low-impact, nerc-cip:medium-impact")
        print("   Create tags: nerc-cip:eacms, nerc-cip:supply-chain")
        print()

        print(Colors.colored("4. Integrate with Electronic Access Points (CIP-005):", Colors.YELLOW))
        print("   Export malicious IP list from MISP")
        print("   Import into firewall at EAPs (Palo Alto, Fortinet, Cisco)")
        print("   Configure blocking/alerting rules")
        print()

        print(Colors.colored("5. Document for NERC CIP Audits:", Colors.YELLOW))
        print("   Review: docs/NERC_CIP_CONFIGURATION.md")
        print("   Add MISP to CIP-008 Incident Response Plan")
        print("   Document MISP as BCSI (CIP-011)")
        print()

        print(Colors.colored("6. Consider E-ISAC Membership:", Colors.YELLOW))
        print("   Apply at: https://www.eisac.com/")
        print("   Cost: $5,000 - $25,000/year (varies by utility size)")
        print("   Benefit: Electric sector-specific threat intelligence")
        print()

        print(Colors.colored("7. Training & Awareness:", Colors.YELLOW))
        print("   Train SOC team on MISP for ICS incident response")
        print("   Include MISP threat reports in CIP-003 security awareness")
        print("   Conduct tabletop exercise using MISP threat scenarios")
        print()

        print(Colors.success("MISP is now configured for NERC CIP compliance!"))
        print()
        print(Colors.nerc("Documentation: docs/NERC_CIP_CONFIGURATION.md"))
        print()

    def run(self) -> bool:
        """Run complete NERC CIP configuration"""
        self.print_banner()

        # Check if MISP is installed
        if not self.config.MISP_DIR.exists():
            self.logger.error(
                f"MISP directory not found: {self.config.MISP_DIR}",
                event_type="nerc_cip_config",
                action="check_dir"
            )
            self.log("Please install MISP first: python3 misp-install.py", "error")
            return False

        # Check if containers are running
        if not self.check_misp_running():
            self.logger.error("MISP containers not running", event_type="nerc_cip_config", action="check_containers")
            self.log("Please start MISP: cd /opt/misp && sudo docker compose up -d", "error")
            return False

        try:
            # Configure NERC CIP-specific settings
            self.configure_nerc_cip_settings()
            time.sleep(2)

            # Show feed recommendations
            self.show_feed_recommendations()
            time.sleep(1)

            # Show NERC CIP use cases
            self.show_nerc_cip_use_cases()
            time.sleep(1)

            # Show next steps
            self.show_next_steps()

            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            self.logger.success(
                f"NERC CIP configuration completed in {elapsed:.1f} seconds",
                event_type="nerc_cip_config",
                action="complete"
            )

            return True

        except KeyboardInterrupt:
            print()
            self.logger.warning("Configuration interrupted by user", event_type="nerc_cip_config", action="interrupt")
            return False
        except Exception as e:
            self.logger.error(
                f"Configuration failed: {e}",
                event_type="nerc_cip_config",
                action="complete",
                error_message=str(e)
            )
            import traceback
            traceback.print_exc()
            return False

# ==========================================
# Main
# ==========================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='MISP NERC CIP Configuration for Energy Utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configure MISP for NERC CIP compliance
  python3 configure-misp-nerc-cip.py

  # Dry run (show what would be done)
  python3 configure-misp-nerc-cip.py --dry-run

NERC CIP Standards Addressed:
  - CIP-003: Security awareness training
  - CIP-005: Electronic Access Point monitoring
  - CIP-007: Security event logging
  - CIP-008: Incident response planning
  - CIP-010: Vulnerability assessments
  - CIP-011: BCSI protection
  - CIP-013: Supply chain security
  - CIP-015: Internal network monitoring

For complete documentation, see: docs/NERC_CIP_CONFIGURATION.md
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')

    args = parser.parse_args()

    config = MISPNERCCIPConfig(dry_run=args.dry_run)
    success = config.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
