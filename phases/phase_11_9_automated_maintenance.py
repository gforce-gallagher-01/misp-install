"""
Phase 11.9: Configure automated maintenance cron jobs
"""

import os
from pathlib import Path

from lib.colors import Colors
from lib.misp_api_helpers import get_api_key
from phases.base_phase import BasePhase


class Phase11_9AutomatedMaintenance(BasePhase):
    """Phase 11.9: Configure automated maintenance cron jobs"""

    def run(self):
        """Execute automated maintenance setup"""
        # Check exclusion list first
        if self.config.is_feature_excluded('automated-maintenance'):
            self.logger.info("⏭️  Skipping automated maintenance setup (excluded)")
            self.save_state(11.9, "Automated Maintenance Skipped")
            return

        self.section_header("PHASE 11.9: AUTOMATED MAINTENANCE")

        self.logger.info("[11.9.1] Setting up automated maintenance cron jobs...")
        self.logger.info("          • Daily: Database cleanup, log rotation, update feeds")
        self.logger.info("          • Weekly: Full database optimization, security updates")

        os.chdir(self.misp_dir)

        try:
            api_key = self._get_api_key()

            if not api_key:
                self.logger.warning("⚠️  No API key found - skipping automated maintenance setup")
                self.logger.info("   Can be configured manually later")
                self.save_state(11.9, "Automated Maintenance Skipped (No API Key)")
                return

            self._setup_maintenance_cron(api_key)

            self.save_state(11.9, "Automated Maintenance Configured")

        except Exception as e:
            self.logger.error(Colors.error(f"Automated maintenance setup failed: {e}"))
            self.logger.warning("Can be configured manually later:")
            self.logger.warning("  bash scripts/setup-misp-maintenance-cron.sh")
            self.logger.info("Continuing installation...")

    def _get_api_key(self) -> str:
        """Get API key from .env file using centralized helper"""
        return get_api_key(env_file=str(self.misp_dir / ".env"))

    def _setup_maintenance_cron(self, api_key: str):
        """Setup maintenance cron jobs using setup-misp-maintenance-cron.sh script"""
        import subprocess

        script_path = Path(__file__).parent.parent / 'scripts' / 'setup-misp-maintenance-cron.sh'

        # Set environment variable for API key
        os.environ['MISP_API_KEY'] = api_key

        # Pipe 'y' to script to auto-confirm (non-interactive mode)
        try:
            result = subprocess.run(
                f'echo "y" | bash {script_path}',
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
        except Exception as e:
            self.logger.error(f"Failed to run maintenance setup: {e}")
            return

        if result.returncode == 0:
            self.logger.info(Colors.success("✓ Automated maintenance cron jobs configured"))
            self._display_cron_schedule()
        else:
            self.logger.warning("⚠️  Maintenance cron jobs may not have been configured")
            self.logger.info("   Check: bash scripts/setup-misp-maintenance-cron.sh")

    def _display_cron_schedule(self):
        """Display cron job schedule"""
        self.logger.info("  Scheduled Jobs:")
        self.logger.info("    • Daily   (3:00 AM): Database cleanup, log rotation, feed updates")
        self.logger.info("    • Weekly  (4:00 AM Sunday): Full optimization, security updates")
        self.logger.info("  View jobs: crontab -l")
        self.logger.info("  Logs: /var/log/misp-maintenance/")
