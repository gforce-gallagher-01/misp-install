"""
Phase 1: Install system dependencies
"""

import subprocess
from phases.base_phase import BasePhase
from lib.colors import Colors


class Phase01Dependencies(BasePhase):
    """Phase 1: Install required system dependencies"""

    def run(self):
        """Execute dependency installation"""
        self.section_header("PHASE 1: INSTALLING DEPENDENCIES")

        self._install_packages()
        self._install_docker()
        self._verify_docker_compose()

        self.logger.info(Colors.success("All dependencies installed"))
        self.save_state(1, "Dependencies Installed")

    def _install_packages(self):
        """Install required system packages"""
        packages = [
            'curl', 'wget', 'git', 'ca-certificates', 'gnupg',
            'lsb-release', 'openssl', 'net-tools', 'iputils-ping',
            'dnsutils', 'jq', 'acl'
        ]

        self.logger.info("[1.1] Updating package lists...")
        self.run_command(['sudo', 'apt', 'update', '-qq'])

        self.logger.info("[1.2] Installing required packages...")
        self.run_command(['sudo', 'apt', 'install', '-y'] + packages, timeout=300)

    def _install_docker(self):
        """Install Docker if not already installed"""
        self.logger.info("[1.3] Checking Docker installation...")

        try:
            self.run_command(['docker', '--version'])
            self.logger.info(Colors.success("Docker already installed"))
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.logger.info("Installing Docker...")

            # Install Docker
            self.run_command(['sudo', 'mkdir', '-p', '/etc/apt/keyrings'])

            # Add Docker GPG key
            gpg_result = subprocess.run(
                ['curl', '-fsSL', 'https://download.docker.com/linux/ubuntu/gpg'],
                capture_output=True
            )
            subprocess.run(
                ['sudo', 'gpg', '--dearmor', '-o', '/etc/apt/keyrings/docker.gpg'],
                input=gpg_result.stdout,
                check=True
            )

            # Add Docker repository
            lsb_release = subprocess.run(['lsb_release', '-cs'], capture_output=True, text=True).stdout.strip()
            arch = subprocess.run(['dpkg', '--print-architecture'], capture_output=True, text=True).stdout.strip()

            repo_line = f"deb [arch={arch} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu {lsb_release} stable"

            with open('/tmp/docker.list', 'w') as f:
                f.write(repo_line)

            self.run_command(['sudo', 'mv', '/tmp/docker.list', '/etc/apt/sources.list.d/docker.list'])

            # Install Docker packages
            self.run_command(['sudo', 'apt', 'update', '-qq'])
            self.run_command([
                'sudo', 'apt', 'install', '-y',
                'docker-ce', 'docker-ce-cli', 'containerd.io',
                'docker-buildx-plugin', 'docker-compose-plugin'
            ], timeout=600)

            self.logger.info(Colors.success("Docker installed"))

    def _verify_docker_compose(self):
        """Verify Docker Compose is installed"""
        self.logger.info("[1.4] Verifying Docker Compose...")
        self.run_command(['docker', 'compose', 'version'])
