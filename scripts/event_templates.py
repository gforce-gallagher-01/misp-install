"""
Event Templates for Utilities Sector Threat Intelligence

DRY approach: Centralized event data templates to eliminate code duplication.
All 20 events use the same structure, just different data.
"""

# Event templates distributed across last 30 days
EVENT_TEMPLATES = [
    # Events 3-5: ICS Malware (continuing from Industroyer2 and TRITON)
    {
        "number": 3,
        "name": "PIPEDREAM ICS Malware",
        "days_ago": 10,
        "info": "PIPEDREAM Malware Framework Targeting Multiple ICS/SCADA Platforms",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%malware"},
            {"name": "malware-category:SCADA"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "md5", "category": "Payload delivery", "value": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", "to_ids": True},
            {"type": "filename", "category": "Payload delivery", "value": "codesys.exe", "to_ids": True},
            {"type": "text", "category": "External analysis", "value": "Schneider Electric, Omron, Rockwell targets", "to_ids": False}
        ]
    },
    {
        "number": 4,
        "name": "Havex Energy Campaign",
        "days_ago": 12,
        "info": "Havex Malware Campaign Targeting Energy Sector SCADA Systems",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%malware"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "md5", "category": "Payload delivery", "value": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7", "to_ids": True},
            {"type": "ip-dst", "category": "Network activity", "value": "185.10.58.197", "to_ids": True}
        ]
    },
    {
        "number": 5,
        "name": "BlackEnergy Ukraine Grid",
        "days_ago": 15,
        "info": "BlackEnergy Malware Used in Ukrainian Power Grid Cyber Attack",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%malware"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "md5", "category": "Payload delivery", "value": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8", "to_ids": True}
        ]
    },

    # Events 6-10: APT Groups
    {
        "number": 6,
        "name": "APT33 Energy Targeting",
        "days_ago": 3,
        "info": "APT33 Persistent Targeting of Energy Sector Organizations",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "ics:%attack-target=\"control-system\""},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "domain", "category": "Network activity", "value": "windowsupdate-security.com", "to_ids": True},
            {"type": "ip-dst", "category": "Network activity", "value": "5.61.34.176", "to_ids": True}
        ]
    },
    {
        "number": 7,
        "name": "Dragonfly 2.0 Campaign",
        "days_ago": 6,
        "info": "Dragonfly 2.0 Advanced Persistent Threat Targeting Energy Infrastructure",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "domain", "category": "Network activity", "value": "energyinfrastructure.com", "to_ids": True}
        ]
    },
    {
        "number": 8,
        "name": "XENOTIME Safety Targeting",
        "days_ago": 9,
        "info": "XENOTIME Threat Group Expanding Targeting Beyond Safety Systems",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "ip-dst", "category": "Network activity", "value": "91.219.29.81", "to_ids": True}
        ]
    },
    {
        "number": 9,
        "name": "Sandworm ICS Attacks",
        "days_ago": 11,
        "info": "Sandworm Team Ongoing ICS/SCADA Targeting and Attack Infrastructure",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "ics:%malware"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "domain", "category": "Network activity", "value": "scada-systems.net", "to_ids": True}
        ]
    },
    {
        "number": 10,
        "name": "MERCURY Water Targeting",
        "days_ago": 14,
        "info": "MERCURY Threat Group Targeting Water and Wastewater Systems",
        "tags": [
            {"name": "dhs-ciip-sectors:water"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "ip-dst", "category": "Network activity", "value": "45.141.84.223", "to_ids": True}
        ]
    },

    # Events 11-15: Vulnerabilities
    {
        "number": 11,
        "name": "Critical Modbus Vulnerability",
        "days_ago": 2,
        "info": "Critical Modbus TCP/IP Stack Vulnerability Affecting Multiple ICS Vendors",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%vulnerability"},
            {"name": "tlp:amber"}
        ],
        "threat_level": "1",
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2023-1234", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "CVSS 9.8 Critical", "to_ids": False}
        ]
    },
    {
        "number": 12,
        "name": "Schneider SCADA Bypass",
        "days_ago": 4,
        "info": "Schneider Electric SCADA Authentication Bypass Vulnerability",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%vulnerability"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2023-5678", "to_ids": False}
        ]
    },
    {
        "number": 13,
        "name": "Siemens S7 PLC Vulnerability",
        "days_ago": 8,
        "info": "Siemens S7-1200/1500 PLC Memory Corruption Vulnerability",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%vulnerability"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2023-9012", "to_ids": False}
        ]
    },
    {
        "number": 14,
        "name": "Rockwell PLC Code Injection",
        "days_ago": 13,
        "info": "Allen-Bradley (Rockwell) PLC Remote Code Injection Vulnerability",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%vulnerability"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2023-3456", "to_ids": False}
        ]
    },
    {
        "number": 15,
        "name": "GE CIMPLICITY RCE",
        "days_ago": 16,
        "info": "GE Digital CIMPLICITY HMI/SCADA Remote Code Execution",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%vulnerability"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2023-7890", "to_ids": False}
        ]
    },

    # Events 16-18: Water Sector
    {
        "number": 16,
        "name": "Water Plant SCADA Breach",
        "days_ago": 18,
        "info": "Water Treatment Facility SCADA System Security Breach Investigation",
        "tags": [
            {"name": "dhs-ciip-sectors:water"},
            {"name": "ics:%attack-target=\"scada\""},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "Targeting data", "value": "Municipal water treatment plant", "to_ids": False}
        ]
    },
    {
        "number": 17,
        "name": "Municipal Water Ransomware",
        "days_ago": 20,
        "info": "Ransomware Attack on Municipal Water System Control Network",
        "tags": [
            {"name": "dhs-ciip-sectors:water"},
            {"name": "ics:%malware"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "md5", "category": "Payload delivery", "value": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9", "to_ids": True}
        ]
    },
    {
        "number": 18,
        "name": "Wastewater HMI Compromise",
        "days_ago": 22,
        "info": "Wastewater Treatment Facility HMI System Compromise and Data Exfiltration",
        "tags": [
            {"name": "dhs-ciip-sectors:water"},
            {"name": "ics:%attack-target=\"hmi\""},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "ip-dst", "category": "Network activity", "value": "198.51.100.45", "to_ids": True}
        ]
    },

    # Events 19-20: Dams Sector
    {
        "number": 19,
        "name": "Hydroelectric Dam Probe",
        "days_ago": 25,
        "info": "Reconnaissance Activity Targeting Hydroelectric Dam Control Systems",
        "tags": [
            {"name": "dhs-ciip-sectors:dams"},
            {"name": "ics:%attack-target=\"control-system\""},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "ip-src", "category": "Network activity", "value": "203.0.113.78", "to_ids": True}
        ]
    },
    {
        "number": 20,
        "name": "Bureau Reclamation Targeting",
        "days_ago": 20,
        "info": "Advanced Persistent Threat Targeting Bureau of Reclamation Dam Infrastructure",
        "tags": [
            {"name": "dhs-ciip-sectors:dams"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "domain", "category": "Network activity", "value": "dam-infrastructure.org", "to_ids": True}
        ]
    },

    # Events 21-23: CISA ICS Advisories (Real-world, recent)
    {
        "number": 21,
        "name": "CISA: Volt Typhoon Infrastructure Targeting",
        "days_ago": 3,
        "info": "CISA Alert: Volt Typhoon APT Targeting US Critical Infrastructure Networks",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "dhs-ciip-sectors:water"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "ics:%campaign"},
            {"name": "cisa:alert"},
            {"name": "tlp:white"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "CISA AA24-038A", "to_ids": False},
            {"type": "link", "category": "External analysis", "value": "https://www.cisa.gov/news-events/cybersecurity-advisories", "to_ids": False},
            {"type": "text", "category": "Targeting data", "value": "Living-off-the-land techniques", "to_ids": False}
        ]
    },
    {
        "number": 22,
        "name": "CISA: Unitronics PLC Vulnerabilities",
        "days_ago": 5,
        "info": "CISA ICS Advisory: Unitronics Vision Series PLC Critical Vulnerabilities Exploited",
        "tags": [
            {"name": "dhs-ciip-sectors:water"},
            {"name": "ics:%vulnerability"},
            {"name": "cisa:advisory"},
            {"name": "tlp:white"}
        ],
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2024-1234", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "CISA ICSA-24-030-01", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "Authentication bypass, RCE", "to_ids": False}
        ]
    },
    {
        "number": 23,
        "name": "CISA: Industrial Ransomware Surge",
        "days_ago": 7,
        "info": "CISA Warning: Surge in Ransomware Attacks Targeting Industrial Control Systems",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "dhs-ciip-sectors:manufacturing"},
            {"name": "ics:%malware"},
            {"name": "cisa:warning"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "LockBit 3.0 variant targeting OT", "to_ids": False},
            {"type": "md5", "category": "Payload delivery", "value": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0", "to_ids": True}
        ]
    },

    # Events 24-25: NERC CIP Compliance Incidents
    {
        "number": 24,
        "name": "NERC CIP-010: Supply Chain Incident",
        "days_ago": 9,
        "info": "NERC CIP-010 Supply Chain Risk Management Incident - Compromised Vendor Equipment",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "nerc-cip:CIP-010"},
            {"name": "ics:%supply-chain"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "NERC CIP-010-4 Configuration Management", "to_ids": False},
            {"type": "text", "category": "Targeting data", "value": "Bulk Electric System operator", "to_ids": False}
        ]
    },
    {
        "number": 25,
        "name": "NERC CIP-007: Patch Management Violation",
        "days_ago": 11,
        "info": "NERC CIP-007 Systems Security Management - Critical Patch Delay Incident",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "nerc-cip:CIP-007"},
            {"name": "ics:%vulnerability"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2024-5678", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "35-day patch window exceeded", "to_ids": False}
        ]
    },

    # Events 26-27: Campaign Tracking
    {
        "number": 26,
        "name": "Coordinated ICS Reconnaissance Campaign",
        "days_ago": 4,
        "info": "Multi-Sector ICS Network Reconnaissance Campaign Targeting Energy and Water",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "dhs-ciip-sectors:water"},
            {"name": "ics:%campaign"},
            {"name": "misp-galaxy:mitre-ics-tactics=\"Collection\""},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "Campaign: VOLT-RECON-2024", "to_ids": False},
            {"type": "ip-dst", "category": "Network activity", "value": "45.142.214.123", "to_ids": True},
            {"type": "domain", "category": "Network activity", "value": "scada-scan.net", "to_ids": True}
        ]
    },
    {
        "number": 27,
        "name": "OT Malware Deployment Campaign",
        "days_ago": 8,
        "info": "Coordinated OT-Specific Malware Deployment Campaign Across Multiple Utilities",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "ics:%malware"},
            {"name": "ics:%campaign"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "Campaign: FROSTBITE-OT", "to_ids": False},
            {"type": "md5", "category": "Payload delivery", "value": "f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1", "to_ids": True}
        ]
    },

    # Events 28-29: Zero-Day Exploits
    {
        "number": 28,
        "name": "Siemens S7 Zero-Day Active Exploit",
        "days_ago": 2,
        "info": "Siemens S7-1500 PLC Zero-Day Vulnerability Under Active Exploitation",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "dhs-ciip-sectors:manufacturing"},
            {"name": "ics:%vulnerability"},
            {"name": "ics:%0-day"},
            {"name": "tlp:red"}
        ],
        "threat_level": "1",
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2024-0001", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "CVSS 9.8 Critical - RCE without authentication", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "No patch available - Workaround only", "to_ids": False}
        ]
    },
    {
        "number": 29,
        "name": "Rockwell FactoryTalk Zero-Day",
        "days_ago": 6,
        "info": "Rockwell Automation FactoryTalk View 0-Day Exploited in Targeted Attacks",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "dhs-ciip-sectors:manufacturing"},
            {"name": "ics:%vulnerability"},
            {"name": "ics:%0-day"},
            {"name": "tlp:red"}
        ],
        "threat_level": "1",
        "attributes": [
            {"type": "vulnerability", "category": "External analysis", "value": "CVE-2024-0002", "to_ids": False},
            {"type": "text", "category": "External analysis", "value": "CVSS 9.1 Critical - Path traversal + RCE", "to_ids": False},
            {"type": "ip-dst", "category": "Network activity", "value": "103.75.201.45", "to_ids": True}
        ]
    },

    # Events 30-33: ISAC Intelligence Sharing
    {
        "number": 30,
        "name": "E-ISAC: Grid Targeting Intelligence",
        "days_ago": 1,
        "info": "E-ISAC Bulletin: Coordinated Targeting of Bulk Electric System Control Centers",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "isac:E-ISAC"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "E-ISAC TLP:AMBER 2024-10-17", "to_ids": False},
            {"type": "text", "category": "Targeting data", "value": "Energy Management Systems (EMS)", "to_ids": False},
            {"type": "domain", "category": "Network activity", "value": "grid-maintenance.org", "to_ids": True}
        ]
    },
    {
        "number": 31,
        "name": "WaterISAC: Treatment Plant Threat",
        "days_ago": 4,
        "info": "WaterISAC Alert: Persistent Threat Activity Targeting Water Treatment SCADA",
        "tags": [
            {"name": "dhs-ciip-sectors:water"},
            {"name": "isac:WaterISAC"},
            {"name": "ics:%attack-target=\"scada\""},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "WaterISAC Advisory 2024-10-13", "to_ids": False},
            {"type": "ip-dst", "category": "Network activity", "value": "198.51.100.89", "to_ids": True}
        ]
    },
    {
        "number": 32,
        "name": "Multi-State ISAC Coordinated Alert",
        "days_ago": 10,
        "info": "Multi-ISAC Coordinated Alert: Cross-Sector Critical Infrastructure Reconnaissance",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "dhs-ciip-sectors:water"},
            {"name": "dhs-ciip-sectors:dams"},
            {"name": "isac:MS-ISAC"},
            {"name": "isac:E-ISAC"},
            {"name": "isac:WaterISAC"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "Multi-ISAC Joint Alert 2024-10-07", "to_ids": False},
            {"type": "text", "category": "Targeting data", "value": "State and local government utilities", "to_ids": False}
        ]
    },
    {
        "number": 33,
        "name": "Regional Utility Threat Intelligence",
        "days_ago": 15,
        "info": "Regional Utility Consortium Shared Threat Intelligence on OT Network Intrusions",
        "tags": [
            {"name": "dhs-ciip-sectors:energy"},
            {"name": "isac:regional"},
            {"name": "ics:%intrusion"},
            {"name": "tlp:green"}
        ],
        "attributes": [
            {"type": "text", "category": "External analysis", "value": "Pacific Northwest utilities sharing group", "to_ids": False},
            {"type": "ip-dst", "category": "Network activity", "value": "103.73.65.201", "to_ids": True}
        ]
    }
]
