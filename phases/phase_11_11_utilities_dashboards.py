"""
Phase 11.11: Configure Utilities Sector Dashboards

Installs and configures 25 custom MISP dashboard widgets for utilities
sector threat intelligence monitoring across 5 specialized dashboards.
"""

import os
import subprocess

from lib.docker_helpers import is_container_running
from lib.misp_api_helpers import get_api_key, get_misp_url
from phases.base_phase import BasePhase


class Phase11_11UtilitiesDashboards(BasePhase):
    """Phase 11.11: Configure utilities sector custom dashboards"""

    def run(self):
        """Execute utilities dashboards installation and configuration"""
        # Check exclusion list first
        if self.config.is_feature_excluded('utilities-dashboards'):
            self.logger.info("⏭️  Skipping utilities dashboards (excluded)")
            self.save_state(11.11, "Utilities Dashboards Skipped")
            return

        self.section_header("PHASE 11.11: UTILITIES SECTOR DASHBOARDS")

        # Check if MISP is accessible
        if not self._check_misp_ready():
            self.logger.warning("MISP not ready, skipping dashboard configuration")
            self.save_state(11.11, "Utilities Dashboards Skipped (MISP not ready)")
            return

        # Get API key for dashboard configuration
        api_key = self._get_api_key()
        if not api_key:
            self.logger.warning("No API key found, skipping dashboard configuration")
            self.save_state(11.11, "Utilities Dashboards Skipped (no API key)")
            return

        try:
            # Step 1: Install base DRY files
            self._install_base_files()

            # Step 2: Install all 25 widgets
            self._install_all_widgets()

            # Step 2.5: Remove abstract base classes (prevent instantiation errors)
            self._remove_abstract_classes()

            # Step 2.6: Apply wildcard fixes to widget queries
            self._apply_widget_fixes()

            # Step 3: Configure dashboards via API
            self._configure_dashboards(api_key)

            self.logger.info("✓ Utilities dashboards configured successfully (25 widgets)")

            self.save_state(11.11, "Utilities Dashboards Configured")

        except Exception as e:
            self.logger.error(f"Dashboard configuration failed: {e}")
            raise

    def _check_misp_ready(self):
        """Check if MISP container is running and accessible using centralized helper"""
        try:
            return is_container_running('misp-misp-core-1')
        except Exception as e:
            self.logger.error(f"Failed to check MISP status: {e}")
            return False

    def _get_api_key(self):
        """Get MISP API key using centralized helper"""
        return get_api_key(env_file='/opt/misp/.env')

    def _install_base_files(self):
        """Install DRY base widget files"""
        self.logger.info("Installing base widget files...")

        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'widgets',
            'install-base-files.sh'
        )

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Base files installation script not found: {script_path}")

        # Make executable
        subprocess.run(['chmod', '+x', script_path], check=True)

        # Run installation
        result = subprocess.run(
            ['sudo', 'bash', script_path],
            cwd=os.path.dirname(script_path),
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(f"Base files installation failed: {result.stderr}")

        self.logger.info("✓ Base widget files installed")

    def _install_all_widgets(self):
        """Install all 25 dashboard widgets"""
        widget_sets = [
            ('utilities-sector', 'install-all-widgets.sh'),
            ('ics-ot-dashboard', 'install-ics-ot-widgets.sh'),
            ('threat-actor-dashboard', 'install-threat-actor-widgets.sh'),
            ('utilities-feed-dashboard', 'install-feed-widgets.sh'),
            ('organizational-dashboard', 'install-organizational-widgets.sh')
        ]

        for widget_dir, install_script in widget_sets:
            self.logger.info(f"Installing {widget_dir} widgets...")

            script_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'widgets',
                widget_dir,
                install_script
            )

            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Installation script not found: {script_path}")

            # Make executable
            subprocess.run(['chmod', '+x', script_path], check=True)

            # Run installation
            result = subprocess.run(
                ['sudo', 'bash', script_path],
                cwd=os.path.dirname(script_path),
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise RuntimeError(f"{widget_dir} installation failed: {result.stderr}")

            self.logger.info(f"✓ {widget_dir} widgets installed")

        self.logger.info("✓ All 25 widgets installed successfully")

    def _remove_abstract_classes(self):
        """
        Remove abstract base classes from Custom widget directory.

        CRITICAL FIX: MISP's dashboard loader scans all .php files in the Custom
        directory and attempts to instantiate them. Abstract classes cannot be
        instantiated in PHP, causing errors like:

        "Error: Cannot instantiate abstract class BaseUtilitiesWidget"

        This breaks the entire "Add Widget" functionality. Abstract base classes
        should not be in the Custom directory - only concrete widget classes.

        See: widgets/DASHBOARD_WIDGET_FIXES.md for full explanation.
        """
        self.logger.info("Removing abstract base classes from Custom directory...")

        widget_dir = "/var/www/MISP/app/Lib/Dashboard/Custom"

        # List of abstract base classes that should not be instantiated
        abstract_classes = [
            "BaseUtilitiesWidget.php",
            "BaseWidget.php",
            "AbstractWidget.php"
        ]

        removed_count = 0

        for abstract_class in abstract_classes:
            class_path = f"{widget_dir}/{abstract_class}"

            try:
                # Check if file exists
                check_result = subprocess.run(
                    ['sudo', 'docker', 'exec', 'misp-misp-core-1',
                     'test', '-f', class_path],
                    capture_output=True,
                    timeout=5
                )

                if check_result.returncode == 0:  # File exists
                    # Remove the abstract class
                    result = subprocess.run(
                        ['sudo', 'docker', 'exec', 'misp-misp-core-1',
                         'rm', class_path],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.returncode == 0:
                        removed_count += 1
                        self.logger.info(f"✓ Removed abstract class: {abstract_class}")
                    else:
                        self.logger.warning(f"⚠ Could not remove {abstract_class}: {result.stderr}")

            except Exception as e:
                self.logger.warning(f"⚠ Error checking/removing {abstract_class}: {e}")

        if removed_count > 0:
            self.logger.info(f"✓ Removed {removed_count} abstract base class(es)")
            self.logger.info("✓ Dashboard 'Add Widget' functionality preserved")
        else:
            self.logger.debug("No abstract classes found (already clean)")

    def _apply_widget_fixes(self):
        """
        Apply critical fixes to widget query syntax.

        Fix: Change 'ics:' to 'ics:%' wildcard for proper tag matching.
        MISP requires explicit wildcard syntax - 'ics:' is treated as literal
        tag name, not prefix match. See DASHBOARD_WIDGET_FIXES.md for details.
        """
        self.logger.info("Applying widget query fixes...")

        widget_dir = "/var/www/MISP/app/Lib/Dashboard/Custom"

        # List of all utilities sector widgets requiring wildcard fix
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
        failed_count = 0

        for widget in widgets_to_fix:
            widget_path = f"{widget_dir}/{widget}"

            try:
                # Fix 'ics:' to 'ics:%' wildcard
                result = subprocess.run(
                    ['sudo', 'docker', 'exec', 'misp-misp-core-1',
                     'sed', '-i', "s/'ics:'/'ics:%'/g", widget_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    fixed_count += 1
                    self.logger.debug(f"✓ Fixed wildcard in {widget}")
                else:
                    failed_count += 1
                    self.logger.warning(f"⚠ Could not fix {widget}: {result.stderr}")

            except Exception as e:
                failed_count += 1
                self.logger.warning(f"⚠ Error fixing {widget}: {e}")

        if fixed_count > 0:
            self.logger.info(f"✓ Applied wildcard fixes to {fixed_count}/{len(widgets_to_fix)} widgets")

        if failed_count > 0:
            self.logger.warning(f"⚠ {failed_count} widgets could not be fixed (may already be correct)")

    def _configure_dashboards(self, api_key):
        """Configure all dashboards via MISP API"""
        self.logger.info("Configuring dashboards via MISP API...")

        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'scripts',
            'configure-all-dashboards.py'
        )

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Dashboard configuration script not found: {script_path}")

        # Get MISP URL using centralized helper
        misp_url = get_misp_url(config_domain=self.config.domain, env_file='/opt/misp/.env')

        # Run configuration script
        result = subprocess.run(
            ['python3', script_path, '--api-key', api_key, '--misp-url', misp_url],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Dashboard configuration failed: {result.stderr}")

        self.logger.info("✓ All 25 dashboards configured via API")
        self.logger.info("Dashboard configuration output:", extra={'output': result.stdout})
