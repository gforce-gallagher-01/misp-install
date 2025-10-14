#!/usr/bin/env python3
"""
MISP Feed Cron Setup Helper
Version: 1.0
Date: 2025-10-14

Purpose:
    Helper script to set up automated daily feed fetching via cron.
    Handles crontab creation, API key storage, and verification.

Usage:
    # Setup daily feed fetch at 2 AM
    python3 scripts/setup-feed-cron.py --api-key YOUR_KEY

    # Setup with custom schedule
    python3 scripts/setup-feed-cron.py --api-key YOUR_KEY --schedule "0 */6 * * *"

    # Dry-run mode (preview cron entry)
    python3 scripts/setup-feed-cron.py --api-key YOUR_KEY --dry-run

    # Remove existing cron job
    python3 scripts/setup-feed-cron.py --remove

Features:
    - Auto-detects API key from .env
    - Creates crontab entry for feed fetching
    - Logs to /opt/misp/logs/feed-fetch-cron.log
    - Verifies cron setup
    - Can remove existing cron entries

Cron Schedules:
    Daily at 2 AM:       0 2 * * *
    Every 6 hours:       0 */6 * * *
    Every 12 hours:      0 */12 * * *
    Twice daily (6a,6p): 0 6,18 * * *
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from misp_api import get_api_key
from misp_logger import get_logger


class CronSetup:
    """Setup automated feed fetching via cron"""

    def __init__(self, api_key: Optional[str] = None, schedule: str = "0 2 * * *",
                 dry_run: bool = False):
        """Initialize cron setup

        Args:
            api_key: MISP API key (auto-detected if None)
            schedule: Cron schedule expression
            dry_run: Preview mode without making changes
        """
        self.api_key = api_key or get_api_key()
        self.schedule = schedule
        self.dry_run = dry_run

        # Paths
        self.script_dir = Path(__file__).parent
        self.fetch_script = self.script_dir / "fetch-all-feeds.py"
        self.log_file = Path("/opt/misp/logs/feed-fetch-cron.log")

        # Initialize logger
        self.logger = get_logger('setup-feed-cron', 'misp:cron:setup')

        # Verify script exists
        if not self.fetch_script.exists():
            raise FileNotFoundError(f"Feed fetch script not found: {self.fetch_script}")

    def get_current_crontab(self) -> str:
        """Get current user's crontab"""
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True,
                check=False
            )

            # crontab -l returns non-zero if no crontab exists
            if result.returncode == 0:
                return result.stdout
            else:
                return ""

        except Exception as e:
            self.logger.error(f"Failed to get crontab: {e}",
                            event_type="cron_setup",
                            action="get_crontab",
                            result="error")
            return ""

    def has_feed_fetch_cron(self) -> bool:
        """Check if feed fetch cron job already exists"""
        crontab = self.get_current_crontab()
        return "fetch-all-feeds.py" in crontab

    def remove_feed_fetch_cron(self) -> bool:
        """Remove existing feed fetch cron job"""
        crontab = self.get_current_crontab()

        if not crontab:
            print("No crontab entries found")
            return True

        # Filter out feed-fetch lines
        lines = crontab.split('\n')
        new_lines = [line for line in lines if 'fetch-all-feeds.py' not in line]

        if len(new_lines) == len(lines):
            print("No feed fetch cron job found to remove")
            return True

        # Write updated crontab
        if self.dry_run:
            print("[DRY-RUN] Would remove feed fetch cron job")
            print("\nRemoved lines:")
            for line in lines:
                if 'fetch-all-feeds.py' in line:
                    print(f"  - {line}")
            return True

        try:
            # Write new crontab
            new_crontab = '\n'.join(new_lines)
            result = subprocess.run(
                ['crontab', '-'],
                input=new_crontab,
                text=True,
                capture_output=True,
                check=True
            )

            print("✓ Feed fetch cron job removed")
            self.logger.info("Feed fetch cron removed",
                           event_type="cron_setup",
                           action="remove",
                           result="success")
            return True

        except Exception as e:
            print(f"✗ Failed to remove cron job: {e}")
            self.logger.error(f"Failed to remove cron: {e}",
                            event_type="cron_setup",
                            action="remove",
                            result="error")
            return False

    def create_cron_entry(self) -> str:
        """Create cron entry for feed fetching"""
        # Use absolute paths
        python_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
        script_path = str(self.fetch_script.absolute())
        log_path = str(self.log_file.absolute())

        # Build cron command
        cmd = f"{python_path} {script_path} --api-key {self.api_key} --quiet >> {log_path} 2>&1"

        # Full cron entry
        cron_entry = f"{self.schedule} {cmd}"

        return cron_entry

    def install_cron_job(self) -> Tuple[bool, str]:
        """Install cron job for feed fetching

        Returns:
            (success: bool, message: str)
        """
        # Check if already exists
        if self.has_feed_fetch_cron():
            return False, "Feed fetch cron job already exists"

        # Create cron entry
        cron_entry = self.create_cron_entry()

        if self.dry_run:
            return True, f"[DRY-RUN] Would add:\n{cron_entry}"

        try:
            # Get current crontab
            current_crontab = self.get_current_crontab()

            # Add new entry
            if current_crontab and not current_crontab.endswith('\n'):
                current_crontab += '\n'

            new_crontab = current_crontab + cron_entry + '\n'

            # Install new crontab
            result = subprocess.run(
                ['crontab', '-'],
                input=new_crontab,
                text=True,
                capture_output=True,
                check=True
            )

            self.logger.info("Feed fetch cron installed",
                           event_type="cron_setup",
                           action="install",
                           result="success",
                           schedule=self.schedule)

            return True, "Cron job installed successfully"

        except Exception as e:
            self.logger.error(f"Failed to install cron: {e}",
                            event_type="cron_setup",
                            action="install",
                            result="error")
            return False, str(e)

    def verify_setup(self) -> bool:
        """Verify cron setup"""
        print("\n" + "="*80)
        print("  Verification")
        print("="*80 + "\n")

        # Check crontab
        if self.has_feed_fetch_cron():
            print("✓ Cron job installed")
        else:
            print("✗ Cron job NOT installed")
            return False

        # Check log directory
        log_dir = self.log_file.parent
        if log_dir.exists():
            print(f"✓ Log directory exists: {log_dir}")
        else:
            print(f"✗ Log directory missing: {log_dir}")
            return False

        # Check script is executable
        if self.fetch_script.exists() and os.access(self.fetch_script, os.X_OK):
            print(f"✓ Fetch script executable: {self.fetch_script}")
        else:
            print(f"✗ Fetch script not executable: {self.fetch_script}")
            return False

        # Check API key
        if self.api_key:
            print(f"✓ API key configured: {self.api_key[:8]}...{self.api_key[-4:]}")
        else:
            print("✗ API key not found")
            return False

        print("\n✓ All verification checks passed")
        return True

    def run_setup(self) -> int:
        """Execute cron setup workflow

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        print("="*80)
        print("  MISP Feed Cron Setup")
        print("="*80 + "\n")

        if not self.api_key:
            print("ERROR: No API key found")
            print("\nAPI key can be:")
            print("  1. Provided via --api-key argument")
            print("  2. Auto-detected from /opt/misp/.env")
            print("  3. Set as MISP_API_KEY environment variable")
            return 1

        if self.dry_run:
            print("[DRY-RUN MODE - No changes will be made]\n")

        # Show configuration
        print("Configuration:")
        print(f"  Schedule:     {self.schedule}")
        print(f"  Fetch script: {self.fetch_script}")
        print(f"  Log file:     {self.log_file}")
        print(f"  API key:      {self.api_key[:8]}...{self.api_key[-4:]}")

        # Explain schedule
        print(f"\nSchedule explanation:")
        if self.schedule == "0 2 * * *":
            print("  Daily at 2:00 AM")
        elif self.schedule == "0 */6 * * *":
            print("  Every 6 hours (00:00, 06:00, 12:00, 18:00)")
        elif self.schedule == "0 */12 * * *":
            print("  Every 12 hours (00:00, 12:00)")
        else:
            print(f"  Custom: {self.schedule}")

        # Install cron job
        print("\n" + "-"*80)
        print("Installing cron job...")
        success, message = self.install_cron_job()

        if success:
            print(f"✓ {message}")
            if not self.dry_run:
                print(f"\nCron entry:\n  {self.create_cron_entry()}")
        else:
            print(f"✗ {message}")
            if "already exists" in message:
                print("\nTo replace existing cron job:")
                print("  1. Remove: python3 scripts/setup-feed-cron.py --remove")
                print("  2. Re-run setup with new schedule")
            return 1

        # Verify setup
        if not self.dry_run:
            if not self.verify_setup():
                print("\n⚠️  Warning: Some verification checks failed")
                return 1

        # Show next steps
        print("\n" + "="*80)
        print("  Next Steps")
        print("="*80 + "\n")

        if not self.dry_run:
            print("Cron job is now active and will run automatically.")
            print("\nUseful commands:")
            print(f"  # View cron jobs")
            print(f"  crontab -l")
            print(f"\n  # View feed fetch logs")
            print(f"  tail -f {self.log_file}")
            print(f"\n  # Test feed fetch manually")
            print(f"  python3 {self.fetch_script} --api-key YOUR_KEY")
            print(f"\n  # Remove cron job")
            print(f"  python3 scripts/setup-feed-cron.py --remove")
        else:
            print("[DRY-RUN] Run without --dry-run to install the cron job")

        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Setup automated MISP feed fetching via cron',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup daily feed fetch at 2 AM (default)
  python3 scripts/setup-feed-cron.py --api-key YOUR_KEY

  # Setup every 6 hours
  python3 scripts/setup-feed-cron.py --api-key YOUR_KEY --schedule "0 */6 * * *"

  # Preview without installing
  python3 scripts/setup-feed-cron.py --api-key YOUR_KEY --dry-run

  # Remove existing cron job
  python3 scripts/setup-feed-cron.py --remove

Common Cron Schedules:
  0 2 * * *         Daily at 2 AM
  0 */6 * * *       Every 6 hours
  0 */12 * * *      Every 12 hours
  0 6,18 * * *      Twice daily (6 AM and 6 PM)
  0 0 * * 0         Weekly on Sunday at midnight
        """
    )

    parser.add_argument('--api-key', type=str,
                       help='MISP API key (auto-detected if not provided)')
    parser.add_argument('--schedule', type=str, default='0 2 * * *',
                       help='Cron schedule expression (default: 0 2 * * *)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview mode without making changes')
    parser.add_argument('--remove', action='store_true',
                       help='Remove existing feed fetch cron job')

    args = parser.parse_args()

    try:
        # Handle removal
        if args.remove:
            setup = CronSetup(dry_run=args.dry_run)
            return 0 if setup.remove_feed_fetch_cron() else 1

        # Normal setup
        setup = CronSetup(
            api_key=args.api_key,
            schedule=args.schedule,
            dry_run=args.dry_run
        )

        return setup.run_setup()

    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
