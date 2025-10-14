"""
Phase 4: Nuclear cleanup
"""

from phases.base_phase import BasePhase
from lib.colors import Colors


class Phase04Cleanup(BasePhase):
    """Phase 4: Nuclear cleanup of existing MISP installation"""

    def run(self):
        """Execute cleanup"""
        self.section_header("PHASE 4: NUCLEAR CLEANUP")

        self._stop_containers()
        self._remove_containers()
        self._remove_misp_directory()
        self._remove_volumes()
        self._prune_docker()
        self._clean_hosts_file()

        self.logger.info(Colors.success("Nuclear cleanup complete"))
        self.save_state(4, "Cleanup Complete")

    def _stop_containers(self):
        """Stop all Docker containers"""
        self.logger.info("[4.1] Stopping all Docker containers...")
        try:
            result = self.run_command(['docker', 'ps', '-aq'], check=False)
            if result.stdout.strip():
                self.run_command(['docker', 'stop'] + result.stdout.strip().split('\n'), timeout=60)
        except Exception as e:
            self.logger.warning(f"Could not stop containers: {e}")

    def _remove_containers(self):
        """Remove all Docker containers"""
        self.logger.info("[4.2] Removing all Docker containers...")
        try:
            result = self.run_command(['docker', 'ps', '-aq'], check=False)
            if result.stdout.strip():
                self.run_command(['docker', 'rm', '-f'] + result.stdout.strip().split('\n'))
        except Exception as e:
            self.logger.warning(f"Could not remove containers: {e}")

    def _remove_misp_directory(self):
        """Remove MISP directory (except logs)"""
        self.logger.info("[4.3] Removing MISP directory...")
        if self.misp_dir.exists():
            # CRITICAL: Preserve /opt/misp/logs directory (logger is actively writing)
            # Remove everything EXCEPT logs directory
            for item in self.misp_dir.iterdir():
                if item.name != 'logs':
                    self.run_command(['sudo', 'rm', '-rf', str(item)])

    def _remove_volumes(self):
        """Remove all Docker volumes"""
        self.logger.info("[4.4] Removing all Docker volumes...")
        try:
            result = self.run_command(['docker', 'volume', 'ls', '-q'], check=False)
            if result.stdout.strip():
                self.run_command(['docker', 'volume', 'rm'] + result.stdout.strip().split('\n'), check=False)
        except Exception as e:
            self.logger.warning(f"Could not remove volumes: {e}")

    def _prune_docker(self):
        """Prune Docker system"""
        self.logger.info("[4.5] Docker system prune...")
        self.run_command(['docker', 'system', 'prune', '-af', '--volumes'], check=False)

    def _clean_hosts_file(self):
        """Clean /etc/hosts file"""
        self.logger.info("[4.6] Cleaning up /etc/hosts...")
        try:
            # Remove existing entries
            with open('/etc/hosts', 'r') as f:
                lines = f.readlines()

            with open('/tmp/hosts', 'w') as f:
                for line in lines:
                    if self.config.domain not in line:
                        f.write(line)

            self.run_command(['sudo', 'mv', '/tmp/hosts', '/etc/hosts'])
        except Exception as e:
            self.logger.warning(f"Could not clean /etc/hosts: {e}")
