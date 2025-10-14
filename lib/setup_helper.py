"""
MISP Setup Helper Module
Centralized setup and configuration operations

This module provides helper functions for MISP post-installation
setup tasks including:
- Script execution with timeout and error handling
- Cake command execution (taxonomies, warninglists, etc.)
- Verification checks
- Statistics tracking
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
import logging

# Add parent directory for imports
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from lib.docker_manager import DockerCommandRunner


class MISPSetupHelper:
    """Helper class for MISP setup operations"""

    def __init__(self, logger: logging.Logger, misp_dir: Path = Path("/opt/misp"),
                 dry_run: bool = False):
        """Initialize setup helper

        Args:
            logger: Logger instance
            misp_dir: MISP installation directory
            dry_run: Preview mode without making changes
        """
        self.logger = logger
        self.misp_dir = Path(misp_dir)
        self.dry_run = dry_run
        self.docker = DockerCommandRunner(logger)

    def run_script(self, script_path: Path, args: List[str],
                   description: str, timeout: int = 600) -> Tuple[bool, str]:
        """Run a setup script and capture output

        Args:
            script_path: Path to script file
            args: List of command-line arguments
            description: Human-readable description for logging
            timeout: Command timeout in seconds (default 10 minutes)

        Returns:
            (success: bool, output: str)
        """
        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            self.logger.error(error_msg, event_type="setup", action="run_script",
                            script=str(script_path), result="failed")
            return False, error_msg

        self.logger.info(f"Running: {description}", event_type="setup",
                        action="run_script", script=script_path.name)

        if self.dry_run:
            return True, f"Dry-run: Would execute {script_path} {' '.join(args)}"

        try:
            cmd = ['python3', str(script_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=script_path.parent.parent
            )

            if result.returncode == 0:
                self.logger.info(f"Completed: {description}", event_type="setup",
                               action="run_script", script=script_path.name,
                               result="success")
                return True, result.stdout
            else:
                self.logger.error(f"Failed: {description}", event_type="setup",
                                action="run_script", script=script_path.name,
                                result="failed", error=result.stderr[:500])
                return False, result.stderr

        except subprocess.TimeoutExpired:
            error_msg = f"Script timeout: {script_path.name}"
            self.logger.error(error_msg, event_type="setup", action="run_script",
                            script=script_path.name, result="timeout")
            return False, error_msg

        except Exception as e:
            error_msg = f"Script execution error: {e}"
            self.logger.error(error_msg, event_type="setup", action="run_script",
                            script=script_path.name, result="error")
            return False, str(e)

    def run_cake_command(self, command: str, subcommand: str,
                        timeout: int = 300) -> Tuple[bool, str]:
        """Execute MISP cake command in container

        Args:
            command: Cake command (e.g., 'Admin')
            subcommand: Cake subcommand (e.g., 'updateTaxonomies')
            timeout: Command timeout in seconds (default 5 minutes)

        Returns:
            (success: bool, output: str)
        """
        self.logger.info(f"Running cake {command} {subcommand}",
                        event_type="setup", action="cake_command",
                        command=command, subcommand=subcommand)

        if self.dry_run:
            return True, f"Dry-run: Would execute cake {command} {subcommand}"

        try:
            result = self.docker.compose_exec(
                self.misp_dir,
                'misp-core',
                ['/var/www/MISP/app/Console/cake', command, subcommand],
                timeout=timeout
            )

            if result.returncode == 0:
                self.logger.info(f"Cake command completed: {command} {subcommand}",
                               event_type="setup", action="cake_command",
                               result="success")
                return True, result.stdout
            else:
                self.logger.error(f"Cake command failed: {command} {subcommand}",
                                event_type="setup", action="cake_command",
                                result="failed", error=result.stderr[:500])
                return False, result.stderr

        except Exception as e:
            error_msg = f"Cake command error: {e}"
            self.logger.error(error_msg, event_type="setup", action="cake_command",
                            command=command, subcommand=subcommand)
            return False, str(e)

    def update_taxonomies(self) -> bool:
        """Update MISP taxonomies

        Returns:
            True if successful, False otherwise
        """
        success, output = self.run_cake_command('Admin', 'updateTaxonomies')
        return success

    def update_warninglists(self) -> bool:
        """Update MISP warning lists

        Returns:
            True if successful, False otherwise
        """
        success, output = self.run_cake_command('Admin', 'updateWarningLists')
        return success

    def update_galaxies(self) -> bool:
        """Update MISP galaxies (MITRE ATT&CK, threat actors, etc.)

        Returns:
            True if successful, False otherwise
        """
        success, output = self.run_cake_command('Admin', 'updateGalaxies',
                                                timeout=600)  # 10 min for galaxies
        return success

    def update_object_templates(self) -> bool:
        """Update MISP object templates

        Returns:
            True if successful, False otherwise
        """
        success, output = self.run_cake_command('Admin', 'updateObjectTemplates')
        return success

    def update_notice_lists(self) -> bool:
        """Update MISP notice lists

        Returns:
            True if successful, False otherwise
        """
        success, output = self.run_cake_command('Admin', 'updateNoticeLists')
        return success


class VerificationHelper:
    """Helper class for MISP setup verification"""

    def __init__(self, logger: logging.Logger, session, misp_url: str,
                 dry_run: bool = False):
        """Initialize verification helper

        Args:
            logger: Logger instance
            session: Requests session object
            misp_url: MISP base URL
            dry_run: Preview mode
        """
        self.logger = logger
        self.session = session
        self.misp_url = misp_url.rstrip('/')
        self.dry_run = dry_run

    def verify_connection(self) -> bool:
        """Verify MISP API connection

        Returns:
            True if connected, False otherwise
        """
        if self.dry_run:
            return True

        try:
            response = self.session.get(f"{self.misp_url}/servers/getPyMISPVersion.json")
            if response.status_code == 200:
                self.logger.info("API connection verified", event_type="verification",
                               action="verify_connection", result="success")
                return True
        except Exception as e:
            self.logger.error(f"Connection verification failed: {e}",
                            event_type="verification", action="verify_connection",
                            result="failed")
        return False

    def verify_feeds(self, min_feeds: int = 1) -> Tuple[bool, int]:
        """Verify feeds are configured

        Args:
            min_feeds: Minimum number of expected feeds

        Returns:
            (success: bool, feed_count: int)
        """
        if self.dry_run:
            return True, 0

        try:
            response = self.session.get(f"{self.misp_url}/feeds/index.json")
            if response.status_code == 200:
                feeds = response.json()
                feed_count = len(feeds)
                success = feed_count >= min_feeds

                self.logger.info(f"Feed verification: {feed_count} feeds found",
                               event_type="verification", action="verify_feeds",
                               result="success" if success else "failed",
                               feed_count=feed_count)
                return success, feed_count
        except Exception as e:
            self.logger.error(f"Feed verification failed: {e}",
                            event_type="verification", action="verify_feeds",
                            result="error")

        return False, 0

    def verify_modules(self) -> Tuple[bool, int]:
        """Verify MISP modules are accessible

        Returns:
            (accessible: bool, module_count: int)
        """
        if self.dry_run:
            return True, 0

        try:
            response = self.session.get(f"{self.misp_url}/modules/index")
            if response.status_code == 200:
                modules = response.json()
                module_count = len(modules)

                self.logger.info(f"Module verification: {module_count} modules found",
                               event_type="verification", action="verify_modules",
                               result="success", module_count=module_count)
                return True, module_count
        except Exception as e:
            self.logger.info(f"Modules not accessible (optional): {e}",
                           event_type="verification", action="verify_modules",
                           result="optional")

        return False, 0


class StatisticsTracker:
    """Helper class for tracking setup statistics"""

    def __init__(self):
        """Initialize statistics tracker"""
        self.stats = {
            'settings_applied': 0,
            'settings_failed': 0,
            'feeds_added': 0,
            'feeds_skipped': 0,
            'feeds_failed': 0,
            'news_added': 0,
            'news_failed': 0,
            'modules_enabled': 0,
            'taxonomies_enabled': 0,
            'warninglists_enabled': 0,
            'galaxies_enabled': 0,
            'object_templates_enabled': 0,
        }

    def increment(self, stat: str, count: int = 1):
        """Increment a statistic

        Args:
            stat: Statistic name
            count: Amount to increment (default 1)
        """
        if stat in self.stats:
            self.stats[stat] += count

    def get(self, stat: str) -> int:
        """Get statistic value

        Args:
            stat: Statistic name

        Returns:
            Statistic value
        """
        return self.stats.get(stat, 0)

    def get_all(self) -> Dict[str, int]:
        """Get all statistics

        Returns:
            Dictionary of all statistics
        """
        return self.stats.copy()

    def reset(self):
        """Reset all statistics to zero"""
        for key in self.stats:
            self.stats[key] = 0
