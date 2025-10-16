"""
Phase 8: Configure DNS
"""

from phases.base_phase import BasePhase
from lib.colors import Colors
from lib.config import get_system_hostname


class Phase08DNS(BasePhase):
    """Phase 8: Configure DNS in /etc/hosts"""

    def run(self):
        """Execute DNS configuration"""
        self.section_header("PHASE 8: DNS CONFIGURATION")

        # ALWAYS use auto-detected hostname
        detected_hostname = get_system_hostname()

        self._configure_hosts_file(detected_hostname)

        self.logger.info(Colors.success("DNS configured in /etc/hosts"))
        self.logger.info(f"  Entries: 127.0.0.1 {detected_hostname}")
        self.logger.info(f"           {self.config.server_ip} {detected_hostname}")

        self.save_state(8, "DNS Configured")

    def _configure_hosts_file(self, hostname):
        """Configure /etc/hosts file"""
        self.logger.info("[8.1] Configuring /etc/hosts...")
        self.logger.info(f"Using detected hostname: {hostname}")

        # Read existing hosts file
        with open('/etc/hosts', 'r') as f:
            lines = f.readlines()

        # Remove any existing entries for this domain
        lines = [line for line in lines if hostname not in line]

        # Add new entries
        lines.append(f"\n127.0.0.1 {hostname}\n")
        lines.append(f"{self.config.server_ip} {hostname}\n")

        # Write to temp file
        with open('/tmp/hosts', 'w') as f:
            f.writelines(lines)

        # Move to /etc/hosts
        self.run_command(['sudo', 'mv', '/tmp/hosts', '/etc/hosts'])
