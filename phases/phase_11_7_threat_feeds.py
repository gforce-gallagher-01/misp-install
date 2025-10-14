"""
Phase 11.7: Add comprehensive threat intelligence feeds
"""

import os
from pathlib import Path
from phases.base_phase import BasePhase
from lib.colors import Colors


class Phase11_7ThreatFeeds(BasePhase):
    """Phase 11.7: Add comprehensive threat intelligence feeds"""

    def run(self):
        """Execute threat feed addition"""
        self.section_header("PHASE 11.7: COMPREHENSIVE THREAT INTELLIGENCE FEEDS")

        self.logger.info("[11.7.1] Adding comprehensive threat intelligence feeds...")
        self.logger.info("          This adds 9 threat intelligence feeds (4 ICS/OT + 5 General)")

        os.chdir(self.misp_dir)

        try:
            api_key = self._get_api_key()

            if not api_key:
                self.logger.warning("⚠️  No API key found - skipping feed addition")
                self.logger.info("   Feeds can be added manually later")
                self.save_state(11.7, "Threat Feeds Skipped (No API Key)")
                return

            self._add_feeds(api_key)

            self.save_state(11.7, "Threat Feeds Added")

        except Exception as e:
            self.logger.error(Colors.error(f"Feed addition failed: {e}"))
            self.logger.warning("Feeds can be added manually later:")
            self.logger.warning("  python3 scripts/add-threat-feeds.py --api-key YOUR_KEY --profile all")
            self.logger.info("Continuing installation...")

    def _get_api_key(self) -> str:
        """Get API key from .env file"""
        try:
            result = self.run_command(['sudo', 'grep', 'MISP_API_KEY=', str(self.misp_dir / ".env")])
            api_key = result.stdout.strip().split('=')[1] if '=' in result.stdout else None
            return api_key
        except:
            return None

    def _add_feeds(self, api_key: str):
        """Add feeds using add-threat-feeds.py script"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'add-threat-feeds.py'

        result = self.run_command([
            'python3', str(script_path),
            '--api-key', api_key,
            '--profile', 'all'
        ], timeout=180, check=False)

        if result.returncode == 0:
            self.logger.info(Colors.success("✓ Comprehensive threat intelligence feeds added"))
            self._display_feed_list()
        else:
            self.logger.warning("⚠️  Some feeds may not have been added")
            self.logger.info("   Check: python3 scripts/add-threat-feeds.py --api-key YOUR_KEY --profile all")

    def _display_feed_list(self):
        """Display list of added feeds"""
        self.logger.info("  ICS/OT Feeds (4):")
        self.logger.info("    • abuse.ch URLhaus (malware distribution URLs)")
        self.logger.info("    • abuse.ch Feodo Tracker (botnet C2 servers)")
        self.logger.info("    • Blocklist.de All (attack sources)")
        self.logger.info("    • OpenPhish URL Feed (phishing URLs)")
        self.logger.info("  General Threat Intel Feeds (5):")
        self.logger.info("    • abuse.ch ThreatFox (recent malware IOCs)")
        self.logger.info("    • abuse.ch SSL Blacklist (malicious certificates)")
        self.logger.info("    • abuse.ch MalwareBazaar (recent malware samples)")
        self.logger.info("    • PhishTank (community-verified phishing)")
        self.logger.info("    • abuse.ch Feodo Tracker Full (complete botnet tracker)")
