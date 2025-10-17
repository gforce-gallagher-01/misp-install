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
        "days_ago": 28,
        "info": "Advanced Persistent Threat Targeting Bureau of Reclamation Dam Infrastructure",
        "tags": [
            {"name": "dhs-ciip-sectors:dams"},
            {"name": "misp-galaxy:threat-actor"},
            {"name": "tlp:amber"}
        ],
        "attributes": [
            {"type": "domain", "category": "Network activity", "value": "dam-infrastructure.org", "to_ids": True}
        ]
    }
]
