#!/usr/bin/env python3
"""
MISP Communities Discovery Script
Version: 1.0
Date: 2025-10-14

Purpose:
    Discover and list available MISP threat intelligence sharing communities.
    Helps organizations find relevant communities to join based on sector, region, or focus.

Usage:
    python3 scripts/list-misp-communities.py
    python3 scripts/list-misp-communities.py --sector energy
    python3 scripts/list-misp-communities.py --sector financial
    python3 scripts/list-misp-communities.py --all

Features:
    - Lists public MISP communities
    - Filters by sector (Energy, Financial, Government, Healthcare, etc.)
    - Shows contact information for joining
    - Highlights NERC CIP relevant communities for energy utilities
    - Displays community focus areas and requirements
    - Provides guidance on joining process

IMPORTANT - NERC CIP Compliance Note:
    Joining communities involves TWO-WAY data sharing. For energy utilities under
    NERC CIP, ensure:
    - CIP-011 BCSI protection controls are in place
    - Sharing groups configured to "Your organization only" by default
    - Management approval before joining any community
    - Legal review of community agreements (NDAs, TLP)

Requirements:
    - Internet connection (fetches community data)
    - No MISP instance required (informational only)
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List

# Import centralized logger
sys.path.insert(0, str(Path(__file__).parent.parent))
from misp_logger import get_logger

# MISP Communities Database
# Source: https://www.misp-project.org/communities/
MISP_COMMUNITIES = [
    {
        "name": "CIRCL MISP",
        "organization": "CIRCL (Computer Incident Response Center Luxembourg)",
        "sector": "Multi-Sector",
        "focus": "Private organizations, CERTs, trusted security vendors and researchers",
        "geographic": "International",
        "url": "https://www.circl.lu/services/misp-malware-information-sharing-platform/",
        "contact": "info@circl.lu",
        "cost": "Free",
        "requirements": [
            "At least one PGP key per organization",
            "Trusted organization (private sector, CERT, security vendor/researcher)",
            "Agreement to CIRCL sharing policy"
        ],
        "nerc_cip_relevant": False,
        "description": "One of the largest public MISP communities. Suitable for general threat intelligence sharing."
    },
    {
        "name": "E-ISAC (Electricity Information Sharing and Analysis Center)",
        "organization": "E-ISAC",
        "sector": "Energy",
        "focus": "Electric utilities, solar, wind, battery storage, transmission operators",
        "geographic": "North America (US, Canada, Mexico)",
        "url": "https://www.eisac.com/",
        "contact": "Contact via website form",
        "cost": "$5,000 - $25,000/year (based on organization size)",
        "requirements": [
            "Electric utility or energy sector organization",
            "NERC-registered entity or supplier",
            "Membership application and approval",
            "NDA and information sharing agreement"
        ],
        "nerc_cip_relevant": True,
        "description": "PRIMARY community for NERC CIP compliance. Provides ICS/SCADA threat intelligence specific to electric utilities, solar, wind, and battery storage systems. Highly recommended for Medium+ Impact BES Cyber Systems."
    },
    {
        "name": "FIRST MISP Community",
        "organization": "FIRST (Forum of Incident Response and Security Teams)",
        "sector": "Multi-Sector",
        "focus": "Incident response teams, CERTs, SOCs",
        "geographic": "International",
        "url": "https://www.first.org/global/sigs/information-sharing/misp",
        "contact": "Via FIRST membership",
        "cost": "Requires FIRST membership ($3,500 - $50,000/year)",
        "requirements": [
            "FIRST membership required",
            "Active incident response team",
            "Participation in FIRST community"
        ],
        "nerc_cip_relevant": False,
        "description": "Global incident response community. Good for SOC teams and incident responders."
    },
    {
        "name": "Danish MISP Community",
        "organization": "eCrimeLabs",
        "sector": "Multi-Sector",
        "focus": "Danish organizations, Nordic region",
        "geographic": "Denmark, Nordic countries",
        "url": "https://www.ecrimelabs.com/danish-misp-user-group",
        "contact": "misp@ecrimelabs.dk",
        "cost": "Free",
        "requirements": [
            "Organization UUID from existing MISP instance",
            "Danish or Nordic organization",
            "Email contact with organization details"
        ],
        "nerc_cip_relevant": False,
        "description": "Regional community for Danish and Nordic organizations."
    },
    {
        "name": "Financial Services ISAC (FS-ISAC)",
        "organization": "FS-ISAC",
        "sector": "Financial",
        "focus": "Banks, financial institutions, payment processors",
        "geographic": "International",
        "url": "https://www.fsisac.com/",
        "contact": "Via website membership",
        "cost": "Membership fees apply (tiered)",
        "requirements": [
            "Financial sector organization",
            "Membership application",
            "Information sharing agreement"
        ],
        "nerc_cip_relevant": False,
        "description": "Financial sector specific threat intelligence. Not relevant for energy utilities."
    },
    {
        "name": "OT-ISAC (Operational Technology ISAC)",
        "organization": "OT-ISAC",
        "sector": "Industrial Control Systems",
        "focus": "ICS/SCADA, operational technology, critical infrastructure",
        "geographic": "International",
        "url": "https://www.otisac.org/",
        "contact": "info@otisac.org",
        "cost": "Membership fees apply",
        "requirements": [
            "Organization operating OT/ICS systems",
            "Critical infrastructure provider",
            "Membership application"
        ],
        "nerc_cip_relevant": True,
        "description": "OT/ICS focused community. Relevant for energy utilities with SCADA systems. Covers multiple critical infrastructure sectors."
    },
    {
        "name": "MS-ISAC (Multi-State ISAC)",
        "organization": "MS-ISAC / Center for Internet Security",
        "sector": "Government",
        "focus": "State, local, tribal, territorial governments",
        "geographic": "United States",
        "url": "https://www.cisecurity.org/ms-isac",
        "contact": "Via CIS",
        "cost": "Free for SLTT governments",
        "requirements": [
            "State, local, tribal, or territorial government",
            "US-based",
            "Registration and agreement"
        ],
        "nerc_cip_relevant": False,
        "description": "US government-focused. Relevant if your utility is municipally owned."
    },
    {
        "name": "CISA (Cybersecurity and Infrastructure Security Agency)",
        "organization": "US Department of Homeland Security",
        "sector": "Multi-Sector",
        "focus": "Critical infrastructure, government, private sector",
        "geographic": "United States",
        "url": "https://www.cisa.gov/topics/cybersecurity-best-practices/information-sharing",
        "contact": "central@cisa.dhs.gov",
        "cost": "Free",
        "requirements": [
            "US-based organization",
            "Critical infrastructure sector",
            "Registration with CISA"
        ],
        "nerc_cip_relevant": True,
        "description": "US government threat intelligence. CISA ICS-CERT advisories are critical for NERC CIP compliance. Free access to ICS/SCADA threat intelligence."
    },
]

# Sector categories
SECTORS = {
    "energy": ["Energy", "Industrial Control Systems"],
    "financial": ["Financial"],
    "government": ["Government", "Multi-Sector"],
    "healthcare": ["Healthcare"],
    "ics": ["Industrial Control Systems", "Energy"],
    "all": ["Multi-Sector", "Energy", "Financial", "Government", "Healthcare", "Industrial Control Systems"]
}


class MISPCommunityLister:
    """List and discover MISP communities"""

    def __init__(self, sector_filter: str = None, show_all: bool = False, nerc_cip_only: bool = False):
        self.sector_filter = sector_filter
        self.show_all = show_all
        self.nerc_cip_only = nerc_cip_only
        self.logger = get_logger('list-misp-communities', 'misp:communities')

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")

    def print_community(self, community: Dict):
        """Print community details"""
        # NERC CIP marker
        nerc_marker = " [NERC CIP RELEVANT]" if community.get('nerc_cip_relevant') else ""

        print(f"\n{community['name']}{nerc_marker}")
        print(f"{'─'*80}")
        print(f"Organization:  {community['organization']}")
        print(f"Sector:        {community['sector']}")
        print(f"Focus:         {community['focus']}")
        print(f"Geographic:    {community['geographic']}")
        print(f"Cost:          {community['cost']}")
        print("\nDescription:")
        print(f"  {community['description']}")
        print("\nRequirements:")
        for req in community['requirements']:
            print(f"  • {req}")
        print("\nContact:")
        print(f"  URL:     {community['url']}")
        print(f"  Email:   {community['contact']}")
        print()

    def filter_communities(self) -> List[Dict]:
        """Filter communities based on criteria"""
        filtered = MISP_COMMUNITIES

        # Filter by NERC CIP relevance
        if self.nerc_cip_only:
            filtered = [c for c in filtered if c.get('nerc_cip_relevant')]

        # Filter by sector
        if self.sector_filter and self.sector_filter != 'all':
            sector_list = SECTORS.get(self.sector_filter.lower(), [])
            filtered = [c for c in filtered if c['sector'] in sector_list]

        return filtered

    def run(self):
        """Main execution"""
        self.print_header("MISP Communities Discovery")

        print("This tool helps you discover MISP threat intelligence sharing communities.")
        print("Communities involve TWO-WAY data sharing with trusted partners.")
        print()

        if self.nerc_cip_only or self.sector_filter == 'energy':
            print("⚠️  NERC CIP COMPLIANCE NOTE:")
            print("   Before joining any community, ensure:")
            print("   • Management approval obtained")
            print("   • CIP-011 BCSI protection controls in place")
            print("   • Sharing groups configured properly")
            print("   • Legal review of community agreements")
            print()

        # Filter communities
        communities = self.filter_communities()

        if not communities:
            print("⚠️  No communities found matching your criteria")
            return 1

        # Summary
        nerc_cip_count = len([c for c in communities if c.get('nerc_cip_relevant')])
        free_count = len([c for c in communities if 'Free' in c['cost']])

        print(f"Found {len(communities)} communities:")
        print(f"  • NERC CIP Relevant: {nerc_cip_count}")
        print(f"  • Free to join: {free_count}")
        print(f"  • Paid membership: {len(communities) - free_count}")

        # Show NERC CIP communities first if filtering by energy
        if self.sector_filter == 'energy' or self.nerc_cip_only:
            nerc_cip_communities = [c for c in communities if c.get('nerc_cip_relevant')]
            other_communities = [c for c in communities if not c.get('nerc_cip_relevant')]

            if nerc_cip_communities:
                self.print_header("NERC CIP Relevant Communities (Priority)")
                for community in nerc_cip_communities:
                    self.print_community(community)

            if other_communities and not self.nerc_cip_only:
                self.print_header("Other Relevant Communities")
                for community in other_communities:
                    self.print_community(community)
        else:
            # Show all communities
            self.print_header("Available Communities")
            for community in communities:
                self.print_community(community)

        # Next steps
        self.print_header("Next Steps")
        print("To join a community:")
        print("1. Review community requirements and costs")
        print("2. Obtain management approval (required for NERC CIP organizations)")
        print("3. Contact the community using the provided contact information")
        print("4. Complete membership application and agreements")
        print("5. Configure MISP server connection (after approval)")
        print()
        print("For NERC CIP compliance:")
        print("• E-ISAC membership is HIGHLY RECOMMENDED ($5K-$25K/year)")
        print("• CISA ICS-CERT is FREE and essential for ICS threat intelligence")
        print("• OT-ISAC covers broader OT/ICS sectors")
        print()
        print("Need help configuring community connections?")
        print("  See: docs/NERC_CIP_CONFIGURATION.md (Section on E-ISAC integration)")

        # Log summary
        self.logger.info(f"Listed {len(communities)} communities",
                        event_type="community_discovery",
                        action="list",
                        result="success",
                        total_communities=len(communities),
                        nerc_cip_relevant=nerc_cip_count)

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Discover MISP threat intelligence sharing communities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all communities
  python3 scripts/list-misp-communities.py --all

  # List energy sector communities (NERC CIP relevant)
  python3 scripts/list-misp-communities.py --sector energy

  # List only NERC CIP relevant communities
  python3 scripts/list-misp-communities.py --nerc-cip

  # List financial sector communities
  python3 scripts/list-misp-communities.py --sector financial

  # List ICS/SCADA focused communities
  python3 scripts/list-misp-communities.py --sector ics

Available sectors:
  energy      - Electric utilities, solar, wind, battery (NERC CIP)
  financial   - Banks, financial institutions
  government  - Government agencies, SLTT
  ics         - Industrial Control Systems, SCADA
  all         - Show all communities
        """
    )

    parser.add_argument('--sector', type=str,
                       choices=['energy', 'financial', 'government', 'healthcare', 'ics', 'all'],
                       help='Filter by sector')
    parser.add_argument('--all', action='store_true',
                       help='Show all communities (same as --sector all)')
    parser.add_argument('--nerc-cip', action='store_true',
                       help='Show only NERC CIP relevant communities')

    args = parser.parse_args()

    # Set sector to 'all' if --all flag used
    sector = args.sector
    if args.all:
        sector = 'all'

    # Default to energy sector if no filter specified
    if not sector and not args.nerc_cip:
        print("No sector specified. Showing energy sector communities (use --all to see all)")
        print()
        sector = 'energy'

    lister = MISPCommunityLister(
        sector_filter=sector,
        show_all=args.all,
        nerc_cip_only=args.nerc_cip
    )

    return lister.run()


if __name__ == '__main__':
    sys.exit(main())
