"""
Feature registry for exclusion list

This module defines all optional features that can be installed
during MISP setup. By default, ALL features are installed unless
explicitly excluded via the exclude_features config option.
"""

# Feature to category mapping
FEATURE_CATEGORIES = {
    # Threat Intelligence
    'api-key': 'threat-intelligence',
    'threat-feeds': 'threat-intelligence',
    'utilities-sector': 'threat-intelligence',
    'nerc-cip': 'threat-intelligence',
    'mitre-attack-ics': 'threat-intelligence',

    # Automation
    'automated-maintenance': 'automation',
    'automated-backups': 'automation',
    'news-feeds': 'automation',

    # Integrations
    'splunk-integration': 'integrations',
    'security-onion': 'integrations',
    'siem-correlation': 'integrations',

    # Compliance
    'nerc-cip-taxonomies': 'compliance',
    'dhs-ciip-sectors': 'compliance',
    'ics-taxonomies': 'compliance',
}

# Feature descriptions
FEATURE_DESCRIPTIONS = {
    'api-key': 'API key generation for automation scripts',
    'threat-feeds': 'Built-in threat intelligence feeds',
    'utilities-sector': 'ICS/SCADA/Utilities sector threat intelligence',
    'nerc-cip': 'NERC CIP compliance features',
    'mitre-attack-ics': 'MITRE ATT&CK for ICS framework',
    'automated-maintenance': 'Daily and weekly maintenance cron jobs',
    'automated-backups': 'Scheduled backup cron job',
    'news-feeds': 'Security news population',
    'splunk-integration': 'Splunk SIEM correlation rules (documentation)',
    'security-onion': 'Security Onion integration (documentation)',
    'siem-correlation': 'Generic SIEM correlation rules (documentation)',
    'nerc-cip-taxonomies': 'NERC CIP taxonomies',
    'dhs-ciip-sectors': 'DHS Critical Infrastructure sectors',
    'ics-taxonomies': 'ICS/OT taxonomies',
}

# Category descriptions
CATEGORY_DESCRIPTIONS = {
    'threat-intelligence': 'Threat Intelligence - ICS/SCADA/Utilities sector threat intelligence',
    'automation': 'Automation - Daily maintenance, backups, and news feeds',
    'integrations': 'Integrations - SIEM correlation rules and integration guides',
    'compliance': 'Compliance - NERC CIP and regulatory compliance features',
}


def get_feature_list() -> list:
    """Get list of all available features

    Returns:
        List of feature IDs
    """
    return list(FEATURE_DESCRIPTIONS.keys())


def get_category_features(category: str) -> list:
    """Get all features in a category

    Args:
        category: Category name (e.g., 'threat-intelligence')

    Returns:
        List of feature IDs in the category
    """
    return [f for f, c in FEATURE_CATEGORIES.items() if c == category]


def get_categories() -> list:
    """Get list of all categories

    Returns:
        List of unique category names
    """
    return list(set(FEATURE_CATEGORIES.values()))


def validate_feature_id(feature_id: str) -> bool:
    """Check if a feature ID is valid

    Args:
        feature_id: Feature ID to validate

    Returns:
        True if valid, False otherwise
    """
    return feature_id in FEATURE_DESCRIPTIONS


def validate_category(category: str) -> bool:
    """Check if a category is valid

    Args:
        category: Category name to validate

    Returns:
        True if valid, False otherwise
    """
    return category in get_categories()


def print_feature_list():
    """Print formatted list of all available features"""
    print("\nAvailable Features:")
    print("=" * 80)
    print()

    for category in sorted(get_categories()):
        print(f"\n{CATEGORY_DESCRIPTIONS.get(category, category).upper()}")
        print("-" * 80)

        features = get_category_features(category)
        for feature in sorted(features):
            print(f"  • {feature:25s} - {FEATURE_DESCRIPTIONS[feature]}")

    print("\n" + "=" * 80)
    print("\nTo exclude features, add to your config file:")
    print('  "exclude_features": ["feature-id", "category:category-name"]')
    print("\nExamples:")
    print('  "exclude_features": ["api-key", "news-feeds"]')
    print('  "exclude_features": ["category:automation"]')
    print('  "exclude_features": ["category:compliance", "api-key"]')
    print()
