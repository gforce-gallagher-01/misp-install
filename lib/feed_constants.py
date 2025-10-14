#!/usr/bin/env python3
"""
MISP Feed Constants
Version: 1.0
Date: 2025-10-14

Purpose:
    Centralized feed lists and name mappings shared across scripts.
    Eliminates duplicate NERC CIP feed definitions.

Usage:
    from lib.feed_constants import NERC_CIP_FEEDS, FEED_NAME_MAPPINGS

    # Check if a feed is NERC CIP recommended
    if feed_name in NERC_CIP_FEEDS:
        print("NERC CIP feed")

    # Map user-friendly names to actual MISP feed names
    for keyword, mapped_names in FEED_NAME_MAPPINGS.items():
        # Search logic here
"""

# NERC CIP recommended feeds (for energy utilities)
# From configure-misp-nerc-cip.py - ICS/SCADA threat intelligence
NERC_CIP_FEEDS = [
    "CIRCL OSINT Feed",
    "Abuse.ch URLhaus",
    "Abuse.ch ThreatFox",
    "Abuse.ch Feodo Tracker",
    "Abuse.ch SSL Blacklist",
    "OpenPhish url",
    "Phishtank online valid phishing",
    "Bambenek Consulting - C2 All Indicator Feed",
    "Botvrij.eu",
    "Blocklist.de",
    "DigitalSide Threat-Intel",
    "Cybercrime-Tracker - All",
    "MalwareBazaar Recent Additions",
    "Dataplane.org - sipquery",
    "Dataplane.org - vncrfb",
]

# Feed name mappings (MISP actual name → user-friendly name)
# Maps NERC CIP recommendation names to actual feed names in MISP database
FEED_NAME_MAPPINGS = {
    "urlhaus": ["URLHaus Malware URLs", "URLhaus"],
    "threatfox": ["Threatfox", "threatfox indicators of compromise"],
    "ssl blacklist": ["abuse.ch SSL IPBL"],
    "cybercrime": [
        "http://cybercrime-tracker.net gatelist",
        "http://cybercrime-tracker.net hashlist"
    ],
    "sipquery": ["sipquery"],
    "digitalside": ["DigitalSide Threat-Intel OSINT Feed"],
    "blocklist": ["blocklist.de/lists/all.txt"],
    "botvrij": ["The Botvrij.eu Data"],
    "openphish": ["OpenPhish url list"],
    "phishtank": ["Phishtank online valid phishing"],
}
