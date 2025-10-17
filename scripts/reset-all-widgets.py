#!/usr/bin/env python3
"""
Reset All Widgets - Complete Widget Removal and Reinstallation

This script completely removes all custom widgets from MISP and reinstalls them
with the corrected timeframe formats (365d instead of 1y).

Usage:
    python3 scripts/reset-all-widgets.py
    python3 scripts/reset-all-widgets.py --api-key YOUR_API_KEY
    python3 scripts/reset-all-widgets.py --dry-run

Author: tKQB Enterprises
Version: 1.0
"""

import os
import sys
import subprocess
import argparse
import json
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.colors import Colors
from lib.misp_api_helpers import get_api_key, get_misp_url
from lib.docker_helpers import is_container_running


def print_header(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(Colors.info(title))
    print("=" * 80)


def check_prerequisites():
    """Check that MISP container is running"""
    print_header("CHECKING PREREQUISITES")

    if not is_container_running('misp-misp-core-1'):
        print(Colors.error("✗ MISP container is not running"))
        print("  Start MISP: cd /opt/misp && sudo docker compose up -d")
        return False

    print(Colors.success("✓ MISP container is running"))
    return True


def remove_all_widgets(dry_run=False):
    """Remove all custom widgets from MISP container"""
    print_header("REMOVING ALL CUSTOM WIDGETS")

    widget_dir = "/var/www/MISP/app/Lib/Dashboard/Custom"

    # List all PHP files in Custom directory
    result = subprocess.run(
        ['sudo', 'docker', 'exec', 'misp-misp-core-1',
         'find', widget_dir, '-name', '*.php'],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        print(Colors.error(f"✗ Failed to list widgets: {result.stderr}"))
        return False

    widget_files = result.stdout.strip().split('\n')
    widget_files = [f for f in widget_files if f]  # Remove empty strings

    if not widget_files:
        print(Colors.warning("⚠ No widgets found (directory may be empty)"))
        return True

    print(f"Found {len(widget_files)} widget files to remove:")
    for widget_file in widget_files:
        widget_name = os.path.basename(widget_file)
        print(f"  - {widget_name}")

    if dry_run:
        print(Colors.warning("\n[DRY RUN] Would remove all widgets (not actually removing)"))
        return True

    # Remove all widget files
    print("\nRemoving widgets...")
    removed_count = 0
    failed_count = 0

    for widget_file in widget_files:
        widget_name = os.path.basename(widget_file)

        result = subprocess.run(
            ['sudo', 'docker', 'exec', 'misp-misp-core-1',
             'rm', widget_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            removed_count += 1
            print(Colors.success(f"✓ Removed {widget_name}"))
        else:
            failed_count += 1
            print(Colors.error(f"✗ Failed to remove {widget_name}: {result.stderr}"))

    print(f"\nSummary:")
    print(f"  ✓ Removed: {removed_count}")
    print(f"  ✗ Failed: {failed_count}")

    return failed_count == 0


def clear_php_cache():
    """Clear PHP OpCache to ensure fresh widget loading"""
    print_header("CLEARING PHP CACHE")

    # Clear PHP OpCache
    result = subprocess.run(
        ['sudo', 'docker', 'exec', 'misp-misp-core-1',
         'rm', '-rf', '/var/www/MISP/app/tmp/cache/*'],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        print(Colors.warning(f"⚠ Failed to clear cache: {result.stderr}"))
        print("  (This may not be critical)")
    else:
        print(Colors.success("✓ PHP cache cleared"))

    return True


def reinstall_widgets(dry_run=False):
    """Reinstall all widgets with corrected configuration"""
    print_header("REINSTALLING WIDGETS")

    if dry_run:
        print(Colors.warning("[DRY RUN] Would reinstall all 25 widgets"))
        return True

    # Install base files first
    print("\n[Step 1/6] Installing base widget files...")
    result = _run_install_script('widgets/install-base-files.sh')
    if result:
        print(Colors.success("✓ Base widget files installed"))
    else:
        print(Colors.error("✗ Base files installation failed"))
        return False

    # Install widget sets
    widget_sets = [
        ('utilities-sector', 'install-all-widgets.sh', 2),
        ('ics-ot-dashboard', 'install-ics-ot-widgets.sh', 3),
        ('threat-actor-dashboard', 'install-threat-actor-widgets.sh', 4),
        ('utilities-feed-dashboard', 'install-feed-widgets.sh', 5),
        ('organizational-dashboard', 'install-organizational-widgets.sh', 6)
    ]

    for widget_dir, install_script, step_num in widget_sets:
        print(f"\n[Step {step_num}/6] Installing {widget_dir} widgets...")

        script_path = os.path.join('widgets', widget_dir, install_script)
        result = _run_install_script(script_path)

        if result:
            print(Colors.success(f"✓ {widget_dir} widgets installed"))
        else:
            print(Colors.error(f"✗ {widget_dir} installation failed"))
            return False

    print(Colors.success("\n✓ All 25 widgets reinstalled successfully"))
    return True


def _run_install_script(script_path):
    """Helper function to run widget installation scripts"""
    full_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        script_path
    )

    if not os.path.exists(full_path):
        print(Colors.error(f"✗ Script not found: {full_path}"))
        return False

    # Make executable
    subprocess.run(['chmod', '+x', full_path], check=True)

    # Run installation
    result = subprocess.run(
        ['sudo', 'bash', full_path],
        cwd=os.path.dirname(full_path),
        capture_output=True,
        text=True,
        timeout=120
    )

    return result.returncode == 0


def remove_abstract_classes():
    """Remove abstract base classes that cause instantiation errors"""
    print_header("REMOVING ABSTRACT BASE CLASSES")

    widget_dir = "/var/www/MISP/app/Lib/Dashboard/Custom"

    abstract_classes = [
        "BaseUtilitiesWidget.php",
        "BaseWidget.php",
        "AbstractWidget.php"
    ]

    removed_count = 0

    for abstract_class in abstract_classes:
        class_path = f"{widget_dir}/{abstract_class}"

        # Check if exists
        check_result = subprocess.run(
            ['sudo', 'docker', 'exec', 'misp-misp-core-1',
             'test', '-f', class_path],
            capture_output=True,
            timeout=5
        )

        if check_result.returncode == 0:  # File exists
            # Remove it
            result = subprocess.run(
                ['sudo', 'docker', 'exec', 'misp-misp-core-1',
                 'rm', class_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                removed_count += 1
                print(Colors.success(f"✓ Removed: {abstract_class}"))

    if removed_count > 0:
        print(Colors.success(f"\n✓ Removed {removed_count} abstract base class(es)"))
    else:
        print(Colors.info("✓ No abstract classes found (already clean)"))

    return True


def apply_widget_fixes():
    """Apply wildcard and timeframe fixes to widgets"""
    print_header("APPLYING WIDGET FIXES")

    widget_dir = "/var/www/MISP/app/Lib/Dashboard/Custom"

    # Fix 'ics:' to 'ics:%' wildcard
    print("\nApplying wildcard fixes (ics: → ics:%)...")

    widgets_to_fix = [
        "UtilitiesSectorStatsWidget.php",
        "ISACContributionRankingsWidget.php",
        "NationStateAttributionWidget.php",
        "ICSVulnerabilityFeedWidget.php",
        "RegionalCooperationHeatMapWidget.php",
        "CriticalInfrastructureBreakdownWidget.php",
        "IndustrialMalwareWidget.php",
        "NERCCIPComplianceWidget.php",
        "SCADAIOCMonitorWidget.php",
        "TTPsUtilitiesWidget.php",
        "AssetTargetingAnalysisWidget.php",
        "SectorSharingMetricsWidget.php",
        "VendorSecurityBulletinsWidget.php",
        "HistoricalIncidentsWidget.php",
        "CampaignTrackingWidget.php",
        "ICSZeroDayTrackerWidget.php",
        "MonthlyContributionTrendWidget.php",
        "APTGroupsUtilitiesWidget.php"
    ]

    fixed_count = 0

    for widget in widgets_to_fix:
        widget_path = f"{widget_dir}/{widget}"

        result = subprocess.run(
            ['sudo', 'docker', 'exec', 'misp-misp-core-1',
             'sed', '-i', "s/'ics:'/'ics:%'/g", widget_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            fixed_count += 1

    print(Colors.success(f"✓ Applied wildcard fixes to {fixed_count}/{len(widgets_to_fix)} widgets"))

    # Verify timeframe formats are correct
    print("\nVerifying timeframe formats...")

    threat_actor_widgets = [
        "APTGroupsUtilitiesWidget.php",
        "NationStateAttributionWidget.php",
        "TTPsUtilitiesWidget.php",
        "HistoricalIncidentsWidget.php"
    ]

    format_ok = 0
    format_bad = 0

    for widget in threat_actor_widgets:
        widget_path = f"{widget_dir}/{widget}"

        # Check for correct day format (365d, 3650d)
        result = subprocess.run(
            ['sudo', 'docker', 'exec', 'misp-misp-core-1',
             'grep', '-q', '"timeframe": ".*d"', widget_path],
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            format_ok += 1
            print(Colors.success(f"✓ {widget}: Correct format (day-based)"))
        else:
            format_bad += 1
            print(Colors.warning(f"⚠ {widget}: May have incorrect format"))

    if format_bad > 0:
        print(Colors.warning(f"\n⚠ {format_bad} widgets may have incorrect timeframe format"))
        print("  Run again or check widget files manually")
    else:
        print(Colors.success("\n✓ All threat actor widgets have correct timeframe format"))

    return True


def restart_misp():
    """Restart MISP container to apply changes"""
    print_header("RESTARTING MISP")

    print("Restarting MISP core container...")

    result = subprocess.run(
        ['sudo', 'docker', 'restart', 'misp-misp-core-1'],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        print(Colors.error(f"✗ Failed to restart: {result.stderr}"))
        return False

    print(Colors.success("✓ MISP container restarted"))

    # Wait for MISP to be ready
    print("\nWaiting for MISP to be ready...")

    for i in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        if is_container_running('misp-misp-core-1'):
            print(Colors.success(f"✓ MISP is ready (after {i+1} seconds)"))
            return True
        print(".", end="", flush=True)

    print(Colors.warning("\n⚠ MISP may still be starting (check manually)"))
    return True


def verify_widgets():
    """Verify that widgets were installed correctly"""
    print_header("VERIFYING WIDGET INSTALLATION")

    widget_dir = "/var/www/MISP/app/Lib/Dashboard/Custom"

    # Count widgets
    result = subprocess.run(
        ['sudo', 'docker', 'exec', 'misp-misp-core-1',
         'find', widget_dir, '-name', '*.php', '-type', 'f'],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        print(Colors.error(f"✗ Failed to verify widgets: {result.stderr}"))
        return False

    widget_files = result.stdout.strip().split('\n')
    widget_files = [f for f in widget_files if f]
    widget_count = len(widget_files)

    print(f"Total widgets installed: {widget_count}")

    if widget_count < 25:
        print(Colors.warning(f"⚠ Expected 25 widgets, found {widget_count}"))
    else:
        print(Colors.success(f"✓ All 25 widgets installed"))

    # Check for threat actor widgets specifically
    threat_actor_widgets = [
        "APTGroupsUtilitiesWidget.php",
        "NationStateAttributionWidget.php",
        "TTPsUtilitiesWidget.php",
        "HistoricalIncidentsWidget.php"
    ]

    print("\nVerifying Threat Actor Dashboard widgets:")
    for widget in threat_actor_widgets:
        widget_path = f"{widget_dir}/{widget}"

        result = subprocess.run(
            ['sudo', 'docker', 'exec', 'misp-misp-core-1',
             'test', '-f', widget_path],
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            print(Colors.success(f"  ✓ {widget}"))
        else:
            print(Colors.error(f"  ✗ {widget} NOT FOUND"))

    return True


def print_summary():
    """Print final summary and next steps"""
    print_header("WIDGET RESET COMPLETE")

    print(Colors.success("✓ All widgets removed and reinstalled with corrected configuration"))
    print()
    print("Next Steps:")
    print("  1. Access MISP dashboard: https://<your-misp-domain>")
    print("  2. Click 'Add Widget' button")
    print("  3. Add the 4 Threat Actor widgets:")
    print("     - APT Groups Targeting Utilities")
    print("     - Nation-State Attribution")
    print("     - TTPs Targeting Utilities")
    print("     - Historical ICS Security Incidents")
    print("  4. Verify widgets display data (not 'No data')")
    print()
    print("Configuration format:")
    print(Colors.info('  {"timeframe": "365d", "limit": "15"}'))
    print()
    print("Timeframe options:")
    print("  - 7d   (last 7 days)")
    print("  - 30d  (last 30 days)")
    print("  - 90d  (last 90 days)")
    print("  - 365d (last year)")
    print("  - 3650d (last 10 years)")
    print("  - all  (all time)")
    print()
    print("Troubleshooting:")
    print("  - If widgets still show 'No data', verify events were populated:")
    print("    python3 scripts/populate-utilities-events.py")
    print("  - Check MISP logs:")
    print("    cd /opt/misp && sudo docker compose logs -f misp-core")
    print()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Remove and reinstall all MISP custom widgets with corrected configuration'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--api-key', type=str,
                        help='MISP API key (optional, will auto-detect if not provided)')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip confirmation prompt (non-interactive mode)')

    args = parser.parse_args()

    print_header("MISP WIDGET RESET TOOL")
    print("This script will:")
    print("  1. Remove all existing custom widgets")
    print("  2. Clear PHP cache")
    print("  3. Reinstall all 25 widgets with corrected timeframe formats")
    print("  4. Remove abstract base classes")
    print("  5. Apply wildcard fixes")
    print("  6. Restart MISP")

    if args.dry_run:
        print(Colors.warning("\n[DRY RUN MODE] No changes will be made"))

    if not args.yes:
        print()
        input("Press ENTER to continue or Ctrl+C to cancel... ")
    else:
        print(Colors.info("\n[NON-INTERACTIVE MODE] Proceeding automatically..."))

    # Execute steps
    try:
        # Check prerequisites
        if not check_prerequisites():
            sys.exit(1)

        # Remove all widgets
        if not remove_all_widgets(dry_run=args.dry_run):
            print(Colors.error("\n✗ Widget removal failed"))
            sys.exit(1)

        if args.dry_run:
            print_summary()
            return

        # Clear PHP cache
        clear_php_cache()

        # Reinstall widgets
        if not reinstall_widgets(dry_run=args.dry_run):
            print(Colors.error("\n✗ Widget reinstallation failed"))
            sys.exit(1)

        # Remove abstract classes
        remove_abstract_classes()

        # Apply fixes
        apply_widget_fixes()

        # Restart MISP
        if not restart_misp():
            print(Colors.warning("\n⚠ MISP restart had issues, but widgets may be OK"))

        # Verify installation
        verify_widgets()

        # Print summary
        print_summary()

        sys.exit(0)

    except KeyboardInterrupt:
        print(Colors.warning("\n\n⚠ Cancelled by user"))
        sys.exit(1)
    except Exception as e:
        print(Colors.error(f"\n✗ Error: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
