"""
Phase 11.10: Configure security news feeds
"""

import os
from pathlib import Path
from phases.base_phase import BasePhase
from lib.colors import Colors
from lib.misp_api_helpers import get_api_key


class Phase11_10SecurityNews(BasePhase):
    """Phase 11.10: Configure security news feeds"""

    def run(self):
        """Execute security news feed setup"""
        # Check exclusion list first
        if self.config.is_feature_excluded('news-feeds'):
            self.logger.info("⏭️  Skipping security news feeds (excluded)")
            self.save_state(11.10, "Security News Skipped")
            return

        self.section_header("PHASE 11.10: SECURITY NEWS FEEDS")

        self.logger.info("[11.10.1] Setting up security news feeds...")
        self.logger.info("           • ICS/OT security news")
        self.logger.info("           • Critical infrastructure news")
        self.logger.info("           • Automated daily updates")

        os.chdir(self.misp_dir)

        try:
            api_key = self._get_api_key()

            if not api_key:
                self.logger.warning("⚠️  No API key found - skipping security news setup")
                self.logger.info("   Can be configured manually later")
                self.save_state(11.10, "Security News Skipped (No API Key)")
                return

            self._populate_news(api_key)
            self._setup_news_cron(api_key)

            self.save_state(11.10, "Security News Configured")

        except Exception as e:
            self.logger.error(Colors.error(f"Security news setup failed: {e}"))
            self.logger.warning("Can be configured manually later:")
            self.logger.warning("  python3 scripts/populate-misp-news.py")
            self.logger.warning("  bash scripts/setup-news-cron.sh")
            self.logger.info("Continuing installation...")

    def _get_api_key(self) -> str:
        """Get API key from .env file using centralized helper"""
        return get_api_key(env_file=str(self.misp_dir / ".env"))

    def _populate_news(self, api_key: str):
        """Populate initial news using populate-misp-news.py script"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'populate-misp-news.py'

        # Set environment variable for API key
        os.environ['MISP_API_KEY'] = api_key

        self.logger.info("[11.10.2] Populating initial security news...")

        result = self.run_command([
            'python3', str(script_path)
        ], timeout=300, check=False)

        if result.returncode == 0:
            self.logger.info(Colors.success("✓ Security news populated"))
        else:
            self.logger.warning("⚠️  Initial news population may have failed")
            self.logger.info("   News can be populated manually later")

    def _setup_news_cron(self, api_key: str):
        """Setup news cron job using setup-news-cron.sh script"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'setup-news-cron.sh'

        # Set environment variable for API key
        os.environ['MISP_API_KEY'] = api_key

        self.logger.info("[11.10.3] Setting up automated daily news updates...")

        result = self.run_command([
            'bash', str(script_path)
        ], timeout=120, check=False)

        if result.returncode == 0:
            self.logger.info(Colors.success("✓ Automated news updates configured"))
            self._display_news_schedule()
        else:
            self.logger.warning("⚠️  News cron job may not have been configured")
            self.logger.info("   Check: bash scripts/setup-news-cron.sh")

    def _display_news_schedule(self):
        """Display news feed information"""
        self.logger.info("  News Sources:")
        self.logger.info("    • ICS-CERT Advisories")
        self.logger.info("    • SecurityWeek ICS/OT Security")
        self.logger.info("    • Industrial Cyber")
        self.logger.info("    • CISA Alerts")
        self.logger.info("  Update Schedule: Daily at 2:00 AM")
        self.logger.info("  View jobs: crontab -l")
