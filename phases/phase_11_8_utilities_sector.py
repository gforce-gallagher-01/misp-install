"""
Phase 11.8: Configure utilities sector threat intelligence
"""

import os
from pathlib import Path

from lib.colors import Colors
from lib.misp_api_helpers import get_api_key
from phases.base_phase import BasePhase


class Phase11_8UtilitiesSector(BasePhase):
    """Phase 11.8: Configure utilities sector threat intelligence"""

    def run(self):
        """Execute utilities sector configuration"""
        # Check exclusion list first
        if self.config.is_feature_excluded('utilities-sector'):
            self.logger.info("⏭️  Skipping utilities sector config (excluded)")
            self.save_state(11.8, "Utilities Sector Skipped")
            return

        self.section_header("PHASE 11.8: UTILITIES SECTOR THREAT INTELLIGENCE")

        self.logger.info("[11.8.1] Configuring ICS/SCADA/Utilities sector threat intelligence...")
        self.logger.info("          This includes ICS taxonomies, MITRE ATT&CK for ICS, and sector-specific feeds")

        os.chdir(self.misp_dir)

        try:
            api_key = self._get_api_key()

            if not api_key:
                self.logger.warning("⚠️  No API key found - skipping utilities sector configuration")
                self.logger.info("   Can be configured manually later")
                self.save_state(11.8, "Utilities Sector Skipped (No API Key)")
                return

            self._configure_utilities_sector(api_key)

            # Populate ICS/OT threat intelligence events (31 events)
            self._populate_utilities_events(api_key)

            self.save_state(11.8, "Utilities Sector Configured")

        except Exception as e:
            self.logger.error(Colors.error(f"Utilities sector configuration failed: {e}"))
            self.logger.warning("Can be configured manually later:")
            self.logger.warning("  python3 scripts/configure-misp-utilities-sector.py")
            self.logger.info("Continuing installation...")

    def _get_api_key(self) -> str:
        """Get API key from .env file using centralized helper"""
        return get_api_key(env_file=str(self.misp_dir / ".env"))

    def _configure_utilities_sector(self, api_key: str):
        """Configure utilities sector using configure-misp-utilities-sector.py script"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'configure-misp-utilities-sector.py'

        # Set environment variable for API key
        os.environ['MISP_API_KEY'] = api_key

        result = self.run_command([
            'python3', str(script_path)
        ], timeout=300, check=False)

        if result.returncode == 0:
            self.logger.info(Colors.success("✓ Utilities sector threat intelligence configured"))
            self._display_sector_features()
        else:
            self.logger.warning("⚠️  Some utilities sector features may not have been configured")
            self.logger.info("   Check: python3 scripts/configure-misp-utilities-sector.py")

    def _populate_utilities_events(self, api_key: str):
        """Populate 31 ICS/OT threat intelligence events for dashboard widgets"""
        self.logger.info("[11.8.2] Populating ICS/OT threat intelligence events...")
        self.logger.info("          Creating 31 demonstration events for Threat Actor Dashboard widgets")

        script_path = Path(__file__).parent.parent / 'scripts' / 'populate-utilities-events.py'

        # Set environment variable for API key
        os.environ['MISP_API_KEY'] = api_key

        result = self.run_command([
            'python3', str(script_path)
        ], timeout=180, check=False)

        if result.returncode == 0:
            self.logger.info(Colors.success("✓ 31 ICS/OT threat intelligence events created"))
        else:
            self.logger.warning("⚠️  Event population may have failed")
            self.logger.info("   Can be run manually: python3 scripts/populate-utilities-events.py")

    def _display_sector_features(self):
        """Display list of configured features"""
        self.logger.info("  Configured Features:")
        self.logger.info("    • ICS/OT Taxonomies (NIST ICS, ICS-CERT Advisories)")
        self.logger.info("    • MITRE ATT&CK for ICS Galaxy")
        self.logger.info("    • DHS Critical Infrastructure Sectors")
        self.logger.info("    • Utilities Sector Threat Feeds")
        self.logger.info("    • ICS/SCADA Event Templates")
        self.logger.info("    • 31 ICS/OT Threat Intelligence Events")
