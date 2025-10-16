#!/usr/bin/env python3
"""
Test script for exclusion list functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.config import MISPConfig
from lib.features import print_feature_list, get_feature_list

def test_no_exclusions():
    """Test: No features excluded (default)"""
    print("\n" + "="*80)
    print("TEST 1: No Exclusions (Default)")
    print("="*80)

    config = MISPConfig(
        admin_password="TestPass123!",
        mysql_password="DBPass123!",
        gpg_passphrase="GPGPass123!",
        exclude_features=[]
    )

    features = ['api-key', 'threat-feeds', 'utilities-sector', 'automated-maintenance']

    for feature in features:
        excluded = config.is_feature_excluded(feature)
        status = "❌ EXCLUDED" if excluded else "✅ INCLUDED"
        print(f"  {feature:30s} {status}")

    print("\n✓ Expected: All features INCLUDED")
    print("✓ Result: PASS" if not any(config.is_feature_excluded(f) for f in features) else "✗ Result: FAIL")

def test_single_exclusion():
    """Test: Exclude single feature"""
    print("\n" + "="*80)
    print("TEST 2: Exclude Single Feature (api-key)")
    print("="*80)

    config = MISPConfig(
        admin_password="TestPass123!",
        mysql_password="DBPass123!",
        gpg_passphrase="GPGPass123!",
        exclude_features=["api-key"]
    )

    test_cases = [
        ('api-key', True),  # Should be excluded
        ('threat-feeds', False),  # Should NOT be excluded
        ('utilities-sector', False),  # Should NOT be excluded
    ]

    passed = True
    for feature, should_be_excluded in test_cases:
        excluded = config.is_feature_excluded(feature)
        status = "❌ EXCLUDED" if excluded else "✅ INCLUDED"
        expected = "❌ EXCLUDED" if should_be_excluded else "✅ INCLUDED"
        match = "✓" if (excluded == should_be_excluded) else "✗"
        print(f"  {feature:30s} {status:15s} Expected: {expected:15s} {match}")
        if excluded != should_be_excluded:
            passed = False

    print(f"\n✓ Result: {'PASS' if passed else 'FAIL'}")

def test_category_exclusion():
    """Test: Exclude entire category"""
    print("\n" + "="*80)
    print("TEST 3: Exclude Category (category:automation)")
    print("="*80)

    config = MISPConfig(
        admin_password="TestPass123!",
        mysql_password="DBPass123!",
        gpg_passphrase="GPGPass123!",
        exclude_features=["category:automation"]
    )

    test_cases = [
        ('api-key', False),  # threat-intelligence - should NOT be excluded
        ('automated-maintenance', True),  # automation - should be excluded
        ('automated-backups', True),  # automation - should be excluded
        ('news-feeds', True),  # automation - should be excluded
        ('utilities-sector', False),  # threat-intelligence - should NOT be excluded
    ]

    passed = True
    for feature, should_be_excluded in test_cases:
        excluded = config.is_feature_excluded(feature)
        status = "❌ EXCLUDED" if excluded else "✅ INCLUDED"
        expected = "❌ EXCLUDED" if should_be_excluded else "✅ INCLUDED"
        match = "✓" if (excluded == should_be_excluded) else "✗"
        print(f"  {feature:30s} {status:15s} Expected: {expected:15s} {match}")
        if excluded != should_be_excluded:
            passed = False

    print(f"\n✓ Result: {'PASS' if passed else 'FAIL'}")

def test_mixed_exclusions():
    """Test: Mix of feature and category exclusions"""
    print("\n" + "="*80)
    print("TEST 4: Mixed Exclusions (api-key + category:compliance)")
    print("="*80)

    config = MISPConfig(
        admin_password="TestPass123!",
        mysql_password="DBPass123!",
        gpg_passphrase="GPGPass123!",
        exclude_features=["api-key", "category:compliance"]
    )

    test_cases = [
        ('api-key', True),  # Directly excluded
        ('threat-feeds', False),  # Not excluded
        ('nerc-cip-taxonomies', True),  # Compliance category - excluded
        ('dhs-ciip-sectors', True),  # Compliance category - excluded
        ('ics-taxonomies', True),  # Compliance category - excluded
        ('automated-maintenance', False),  # Automation - not excluded
    ]

    passed = True
    for feature, should_be_excluded in test_cases:
        excluded = config.is_feature_excluded(feature)
        status = "❌ EXCLUDED" if excluded else "✅ INCLUDED"
        expected = "❌ EXCLUDED" if should_be_excluded else "✅ INCLUDED"
        match = "✓" if (excluded == should_be_excluded) else "✗"
        print(f"  {feature:30s} {status:15s} Expected: {expected:15s} {match}")
        if excluded != should_be_excluded:
            passed = False

    print(f"\n✓ Result: {'PASS' if passed else 'FAIL'}")

def test_get_excluded_features():
    """Test: Get full list of excluded features"""
    print("\n" + "="*80)
    print("TEST 5: Get Excluded Features List")
    print("="*80)

    config = MISPConfig(
        admin_password="TestPass123!",
        mysql_password="DBPass123!",
        gpg_passphrase="GPGPass123!",
        exclude_features=["api-key", "category:automation"]
    )

    excluded = config.get_excluded_features()
    print(f"\n  Exclusion config: {config.exclude_features}")
    print(f"\n  Resolved exclusions ({len(excluded)} features):")
    for feature in sorted(excluded):
        print(f"    • {feature}")

    # Should include: api-key, automated-maintenance, automated-backups, news-feeds
    expected = {'api-key', 'automated-maintenance', 'automated-backups', 'news-feeds'}
    passed = expected == set(excluded)

    print(f"\n✓ Result: {'PASS' if passed else 'FAIL'}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("EXCLUSION LIST FUNCTIONALITY TESTS")
    print("="*80)

    # Run tests
    test_no_exclusions()
    test_single_exclusion()
    test_category_exclusion()
    test_mixed_exclusions()
    test_get_excluded_features()

    # Print feature list
    print("\n" + "="*80)
    print("FEATURE REGISTRY")
    print("="*80)
    print_feature_list()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print()

if __name__ == "__main__":
    main()
