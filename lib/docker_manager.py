"""
Docker group and container management
Centralized Docker Compose operations for MISP installation suite

This module provides unified Docker operations including:
- Container status checking
- Service lifecycle (up/down/stop/start/restart)
- Container execution (exec)
- File operations (cp)
- Image management (pull)
- Health checks and waiting
"""

import json
import logging
import os
import pwd
import subprocess
import time
from typing import Dict, List, Optional

from lib.colors import Colors


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

    def compose_exec(self, cwd, service: str, command: List[str],
                     interactive: bool = False, timeout: int = 60) -> subprocess.CompletedProcess:
        """Execute command in running container

        Args:
            cwd: Working directory for docker compose
            service: Service name (e.g., 'misp-core', 'db')
            command: Command to execute as list
            interactive: Use interactive mode (allocate TTY)
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'exec']

        if not interactive:
            cmd.append('-T')  # Disable pseudo-TTY allocation

        cmd.append(service)
        cmd.extend(command)

        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

    def compose_cp(self, cwd, source: str, destination: str, timeout: int = 300) -> subprocess.CompletedProcess:
        """Copy files between container and host

        Args:
            cwd: Working directory for docker compose
            source: Source path (service:path or local path)
            destination: Destination path (service:path or local path)
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result

        Example:
            # Copy from container to host
            compose_cp(misp_dir, 'misp-core:/var/www/MISP/app/files', '/tmp/files')

            # Copy from host to container
            compose_cp(misp_dir, '/tmp/config.php', 'misp-core:/var/www/MISP/app/Config/')
        """
        return subprocess.run(
            ['sudo', 'docker', 'compose', 'cp', source, destination],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

    def compose_stop(self, cwd, service: Optional[str] = None, timeout: int = 120) -> subprocess.CompletedProcess:
        """Stop running containers without removing them

        Args:
            cwd: Working directory for docker compose
            service: Specific service to stop (optional, stops all if None)
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'stop']
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

    def compose_start(self, cwd, service: Optional[str] = None, timeout: int = 120) -> subprocess.CompletedProcess:
        """Start stopped containers

        Args:
            cwd: Working directory for docker compose
            service: Specific service to start (optional, starts all if None)
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'start']
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

    def compose_restart(self, cwd, service: Optional[str] = None, timeout: int = 120) -> subprocess.CompletedProcess:
        """Restart containers

        Args:
            cwd: Working directory for docker compose
            service: Specific service to restart (optional, restarts all if None)
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'restart']
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

    def compose_pull(self, cwd, service: Optional[str] = None, timeout: int = 600) -> subprocess.CompletedProcess:
        """Pull latest images

        Args:
            cwd: Working directory for docker compose
            service: Specific service to pull (optional, pulls all if None)
            timeout: Command timeout in seconds (default 10 min for large images)

        Returns:
            CompletedProcess result
        """
        cmd = ['sudo', 'docker', 'compose', 'pull']
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

    def is_container_running(self, cwd, container: str, timeout: int = 10) -> bool:
        """Check if specific container is running using JSON format

        Args:
            cwd: Working directory for docker compose
            container: Container/service name to check
            timeout: Command timeout in seconds

        Returns:
            True if container is running, False otherwise
        """
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json', container],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                return False

            # Parse JSON output - docker compose returns one JSON object per line
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        container_info = json.loads(line)
                        # Check if container state is 'running'
                        if container_info.get('State') == 'running':
                            return True
                    except json.JSONDecodeError:
                        continue

            return False

        except Exception:
            return False

    def wait_for_container(self, cwd, container: str, max_attempts: int = 30,
                          delay: int = 2, logger: Optional[logging.Logger] = None) -> bool:
        """Wait for container to be running

        Args:
            cwd: Working directory for docker compose
            container: Container/service name to wait for
            max_attempts: Maximum number of check attempts
            delay: Delay in seconds between attempts
            logger: Optional logger for progress messages

        Returns:
            True if container is running within timeout, False otherwise
        """
        for attempt in range(max_attempts):
            if self.is_container_running(cwd, container):
                if logger:
                    logger.info(f"Container {container} is running (attempt {attempt + 1})")
                return True

            if attempt < max_attempts - 1:
                if logger and attempt % 5 == 0:
                    logger.info(f"Waiting for {container}... ({attempt + 1}/{max_attempts})")
                time.sleep(delay)

        return False

    def get_container_status(self, cwd, timeout: int = 10) -> List[Dict]:
        """Get detailed status of all containers using JSON format

        Args:
            cwd: Working directory for docker compose
            timeout: Command timeout in seconds

        Returns:
            List of container info dictionaries with keys:
            - Name: Container name
            - State: running/exited/etc
            - Status: Health status
            - Service: Service name
        """
        try:
            result = subprocess.run(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                return []

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            return containers

        except Exception:
            return []
