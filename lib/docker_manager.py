"""
Docker group and container management
"""

import subprocess
import logging
import pwd
import os
from lib.colors import Colors
from lib.user_manager import MISP_USER


class DockerGroupManager:
    """Manages Docker group membership for MISP installation user

    SECURITY: Adds the dedicated misp-owner user to docker group,
    following best practice of using a dedicated service account.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def add_user_to_docker_group(self, username: str = None) -> bool:
        """Add specified user to docker group (defaults to current user)

        Args:
            username: Username to add to docker group. If None, uses current user.
                     For MISP installation, should be MISP_USER constant.

        Returns:
            True if user is in docker group (already or newly added), False on failure
        """
        if username is None:
            username = pwd.getpwuid(os.getuid()).pw_name

        try:
            # Check if already in docker group
            result = subprocess.run(
                ['groups', username],
                capture_output=True,
                text=True
            )

            if 'docker' in result.stdout:
                self.logger.info(Colors.success(f"{username} already in docker group"))
                return True

            # Add user to docker group
            self.logger.info(f"Adding {username} to docker group...")
            subprocess.run(
                ['sudo', 'usermod', '-aG', 'docker', username],
                check=True
            )

            self.logger.info(Colors.success(f"Added {username} to docker group"))
            self.logger.info(f"Note: {username} may need to log out/in for group to take full effect")
            return True

        except Exception as e:
            self.logger.error(Colors.error(f"Failed to add {username} to docker group: {e}"))
            return False


class DockerCommandRunner:
    """Helper for running Docker commands"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def compose_ps(self, cwd, timeout=30) -> subprocess.CompletedProcess:
        """Get docker compose process status

        Args:
            cwd: Working directory for docker compose
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        return subprocess.run(
            ['sudo', 'docker', 'compose', 'ps'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

    def compose_up(self, cwd, detached=True, timeout=300) -> subprocess.CompletedProcess:
        """Start docker compose services

        Args:
            cwd: Working directory for docker compose
            detached: Run in detached mode (-d)
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'up']
        if detached:
            cmd.append('-d')

        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )

    def compose_down(self, cwd, volumes=False, timeout=120) -> subprocess.CompletedProcess:
        """Stop and remove docker compose services

        Args:
            cwd: Working directory for docker compose
            volumes: Also remove volumes
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'down']
        if volumes:
            cmd.append('-v')

        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )

    def compose_logs(self, cwd, service=None, follow=False, tail=None, timeout=30) -> subprocess.CompletedProcess:
        """Get docker compose service logs

        Args:
            cwd: Working directory for docker compose
            service: Specific service name (optional)
            follow: Follow logs in real-time
            tail: Number of lines to show from end
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'logs']

        if follow:
            cmd.append('-f')

        if tail:
            cmd.extend(['--tail', str(tail)])

        if service:
            cmd.append(service)

        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

    def prune_system(self, volumes=True, timeout=300) -> subprocess.CompletedProcess:
        """Prune unused Docker resources

        Args:
            volumes: Also prune volumes
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['docker', 'system', 'prune', '-af']
        if volumes:
            cmd.append('--volumes')

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
