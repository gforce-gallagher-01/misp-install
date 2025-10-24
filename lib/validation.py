"""
MISP Validation Library

Centralized validation functions used by both installation phases and verification scripts.
Follows DRY (Don't Repeat Yourself) principle.

Author: tKQB Enterprises
Version: 1.0
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MISPValidator:
    """Centralized MISP validation functions (DRY principle)"""

    def __init__(self, misp_dir: Path = Path("/opt/misp"), logger=None):
        """Initialize validator

        Args:
            misp_dir: MISP installation directory
            logger: Optional logger instance
        """
        self.misp_dir = misp_dir
        self.logger = logger

    def run_docker_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str]:
        """Run docker compose exec command

        Args:
            command: Command to run (without docker compose exec prefix)
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, output)
        """
        full_command = ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core'] + command

        try:
            result = subprocess.run(
                full_command,
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)

    def check_containers(self) -> Tuple[bool, Dict[str, bool]]:
        """Check if all critical MISP containers are running

        Returns:
            Tuple of (all_running, container_status_dict)
        """
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return False, {}

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            critical_containers = ['misp-core', 'misp-modules', 'misp-workers', 'db', 'redis']
            status = {}
            all_running = True

            for container_name in critical_containers:
                container = next((c for c in containers if container_name in c.get('Name', '')), None)
                is_running = container and container.get('State') == 'running'
                status[container_name] = is_running

                if not is_running:
                    all_running = False

            return all_running, status

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking containers: {e}")
            return False, {}

    def check_web_interface(self, base_url: Optional[str] = None) -> Tuple[bool, str]:
        """Check if MISP web interface is accessible

        Args:
            base_url: Optional base URL (defaults to https://localhost/)

        Returns:
            Tuple of (accessible, http_status_code)
        """
        url = base_url or 'https://localhost/'

        try:
            result = subprocess.run(
                ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                timeout=10,
                capture_output=True,
                text=True
            )

            status_code = result.stdout.strip()
            is_accessible = status_code in ['200', '302', '303']

            return is_accessible, status_code

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking web interface: {e}")
            return False, "error"

    def check_misp_setting(self, setting_name: str) -> Tuple[bool, str]:
        """Check value of a MISP setting

        Args:
            setting_name: Setting name (e.g., 'MISP.background_jobs')

        Returns:
            Tuple of (is_enabled, value)
        """
        success, output = self.run_docker_command(
            ['/var/www/MISP/app/Console/cake', 'Admin', 'getSetting', setting_name],
            timeout=30
        )

        if not success:
            return False, ""

        # Parse output to determine if enabled
        is_enabled = 'true' in output.lower() or '1' in output

        return is_enabled, output.strip()

    def check_core_settings(self) -> Dict[str, bool]:
        """Check multiple core MISP settings

        Returns:
            Dictionary of {setting_name: is_enabled}
        """
        settings_to_check = {
            'MISP.background_jobs': 'Background jobs',
            'MISP.cached_attachments': 'Cached attachments',
            'MISP.enable_advanced_correlations': 'Advanced correlations',
            'Plugin.Enrichment_services_enable': 'Enrichment services'
        }

        results = {}

        for setting, description in settings_to_check.items():
            is_enabled, _ = self.check_misp_setting(setting)
            results[description] = is_enabled

        return results

    def check_feeds(self) -> Tuple[int, int]:
        """Check how many feeds are configured and enabled

        Returns:
            Tuple of (total_feeds, enabled_feeds)
        """
        try:
            # Get MySQL password from .env
            env_file = self.misp_dir / ".env"
            if not env_file.exists():
                return 0, 0

            mysql_password = None
            with open(env_file) as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        mysql_password = line.split('=', 1)[1].strip().strip('"')
                        break

            if not mysql_password:
                return 0, 0

            # Query feeds table
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{mysql_password}', 'misp', '-e',
                 'SELECT COUNT(*) as total, SUM(enabled) as enabled FROM feeds;'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    data = lines[1].split('\t')
                    total = int(data[0])
                    enabled = int(data[1]) if data[1] != 'NULL' else 0
                    return total, enabled

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking feeds: {e}")

        return 0, 0

    def check_news_count(self) -> int:
        """Check how many news articles are in MISP

        Returns:
            Number of news articles
        """
        try:
            env_file = self.misp_dir / ".env"
            if not env_file.exists():
                return 0

            mysql_password = None
            with open(env_file) as f:
                for line in f:
                    if line.startswith('MYSQL_PASSWORD='):
                        mysql_password = line.split('=', 1)[1].strip().strip('"')
                        break

            if not mysql_password:
                return 0

            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
                 'mysql', '-umisp', f'-p{mysql_password}', 'misp', '-e',
                 'SELECT COUNT(*) FROM news;'],
                cwd=str(self.misp_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    return int(lines[1])

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking news: {e}")

        return 0

    def run_comprehensive_check(self) -> Dict[str, any]:
        """Run all validation checks and return results

        Returns:
            Dictionary with all check results
        """
        results = {
            'timestamp': subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip(),
            'containers': {},
            'web_interface': {},
            'settings': {},
            'feeds': {},
            'news': {},
            'summary': {
                'passed': 0,
                'failed': 0,
                'warning': 0
            }
        }

        # Check containers
        all_running, container_status = self.check_containers()
        results['containers']['all_running'] = all_running
        results['containers']['status'] = container_status

        if all_running:
            results['summary']['passed'] += 1
        else:
            results['summary']['failed'] += 1

        # Check web interface
        is_accessible, status_code = self.check_web_interface()
        results['web_interface']['accessible'] = is_accessible
        results['web_interface']['status_code'] = status_code

        if is_accessible:
            results['summary']['passed'] += 1
        else:
            results['summary']['warning'] += 1

        # Check core settings
        settings = self.check_core_settings()
        results['settings'] = settings

        enabled_count = sum(1 for enabled in settings.values() if enabled)
        if enabled_count >= len(settings) / 2:
            results['summary']['passed'] += 1
        else:
            results['summary']['warning'] += 1

        # Check feeds
        total_feeds, enabled_feeds = self.check_feeds()
        results['feeds']['total'] = total_feeds
        results['feeds']['enabled'] = enabled_feeds

        if enabled_feeds > 0:
            results['summary']['passed'] += 1
        else:
            results['summary']['warning'] += 1

        # Check news
        news_count = self.check_news_count()
        results['news']['count'] = news_count

        if news_count > 0:
            results['summary']['passed'] += 1
        else:
            results['summary']['warning'] += 1

        return results
