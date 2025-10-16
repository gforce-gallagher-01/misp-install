"""
Phase 11.11: Configure Utilities Sector Dashboards

Installs and configures 25 custom MISP dashboard widgets for utilities
sector threat intelligence monitoring across 5 specialized dashboards.
"""

import os
import subprocess
from phases.base_phase import BasePhase
from lib.colors import Colors


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

            # Step 3: Configure dashboards via API
            self._configure_dashboards(api_key)

            self.logger.info("✓ Utilities dashboards configured successfully (25 widgets)")

            self.save_state(11.11, "Utilities Dashboards Configured")

        except Exception as e:
            self.logger.error(f"Dashboard configuration failed: {e}")
            raise

    def _check_misp_ready(self):
        """Check if MISP container is running and accessible"""
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return 'misp-misp-core-1' in result.stdout
        except Exception as e:
            self.logger.error(f"Failed to check MISP status: {e}")
            return False

    def _get_api_key(self):
        """Get MISP API key from environment or .env file"""
        # Try environment variable first
        api_key = os.environ.get('MISP_API_KEY')
        if api_key:
            return api_key

        # Try reading from .env file
        env_file = '/opt/misp/.env'
        if os.path.exists(env_file):
            try:
                result = subprocess.run(
                    ['sudo', 'grep', 'MISP_API_KEY=', env_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout:
                    api_key = result.stdout.split('=', 1)[1].strip()
                    return api_key
            except Exception as e:
                self.logger.warning(f"Could not read API key from .env: {e}")

        return None

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

        # Get MISP URL from config or default
        misp_url = self.config.get('misp_url', 'https://misp.local')
        if not misp_url.startswith('http'):
            misp_url = f'https://{misp_url}'

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
