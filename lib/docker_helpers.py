"""
Docker Helper Functions
Centralized functions for Docker container operations (DRY refactoring)
"""

import subprocess
from typing import List, Optional, Tuple


def is_container_running(container_name: str = 'misp-misp-core-1',
                         timeout: int = 10) -> bool:
    """
    Check if Docker container is running

    This function consolidates the duplicate container readiness checks
    found across 22+ scripts (identified in DRY analysis).

    Args:
        container_name: Name of container to check (default: misp-misp-core-1)
        timeout: Command timeout in seconds

    Returns:
        True if container is running, False otherwise

    Example:
        >>> if is_container_running():
        >>>     print("MISP is running")
    """
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return container_name in result.stdout
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        return False


def is_container_healthy(container_name: str = 'misp-misp-core-1',
                        timeout: int = 10) -> bool:
    """
    Check if Docker container is healthy

    Args:
        container_name: Name of container to check
        timeout: Command timeout in seconds

    Returns:
        True if container is healthy, False otherwise

    Example:
        >>> if is_container_healthy():
        >>>     print("MISP is healthy")
    """
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        for line in result.stdout.strip().split('\n'):
            if container_name in line:
                return 'healthy' in line.lower()

        return False
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        return False


def get_container_status(container_name: str = 'misp-misp-core-1',
                        timeout: int = 10) -> Tuple[bool, str]:
    """
    Get detailed container status

    Args:
        container_name: Name of container to check
        timeout: Command timeout in seconds

    Returns:
        Tuple of (is_running: bool, status_message: str)

    Example:
        >>> running, status = get_container_status()
        >>> print(f"Running: {running}, Status: {status}")
    """
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '--format', '{{.Names}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        for line in result.stdout.strip().split('\n'):
            if container_name in line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    status = parts[1].strip()
                    is_running = status.startswith('Up')
                    return is_running, status

        return False, "Container not found"

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception) as e:
        return False, f"Error: {str(e)}"


def list_misp_containers(timeout: int = 10) -> List[Tuple[str, str]]:
    """
    List all MISP-related containers and their status

    Args:
        timeout: Command timeout in seconds

    Returns:
        List of (container_name, status) tuples

    Example:
        >>> containers = list_misp_containers()
        >>> for name, status in containers:
        >>>     print(f"{name}: {status}")
    """
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '--format', '{{.Names}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        containers = []
        for line in result.stdout.strip().split('\n'):
            if 'misp' in line.lower():
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    containers.append((parts[0].strip(), parts[1].strip()))

        return containers

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        return []


def exec_in_container(container_name: str,
                     command: List[str],
                     timeout: int = 30) -> Tuple[int, str, str]:
    """
    Execute command in Docker container

    Args:
        container_name: Name of container
        command: Command to execute as list
        timeout: Command timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr)

    Example:
        >>> code, out, err = exec_in_container(
        >>>     'misp-misp-core-1',
        >>>     ['ls', '/var/www/MISP']
        >>> )
    """
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'exec', container_name] + command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def wait_for_container_ready(container_name: str = 'misp-misp-core-1',
                             max_wait: int = 300,
                             check_interval: int = 5) -> Tuple[bool, str]:
    """
    Wait for container to become ready (running and healthy)

    Args:
        container_name: Name of container to wait for
        max_wait: Maximum wait time in seconds
        check_interval: Check interval in seconds

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = wait_for_container_ready()
        >>> if success:
        >>>     print("MISP is ready!")
    """
    import time

    elapsed = 0
    while elapsed < max_wait:
        if is_container_running(container_name):
            # Container is running, check if healthy
            time.sleep(check_interval)

            if is_container_healthy(container_name):
                return True, f"Container ready after {elapsed}s"

        time.sleep(check_interval)
        elapsed += check_interval

    return False, f"Timeout after {max_wait}s"


def copy_to_container(container_name: str,
                     source_path: str,
                     dest_path: str,
                     timeout: int = 30) -> Tuple[bool, str]:
    """
    Copy file to Docker container

    Args:
        container_name: Name of container
        source_path: Source file path on host
        dest_path: Destination path in container
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = copy_to_container(
        >>>     'misp-misp-core-1',
        >>>     'widget.php',
        >>>     '/var/www/MISP/app/Lib/Dashboard/Custom/widget.php'
        >>> )
    """
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'cp', source_path, f'{container_name}:{dest_path}'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return True, "File copied successfully"
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Copy operation timed out"
    except Exception as e:
        return False, str(e)


# Usage examples for documentation
if __name__ == "__main__":
    print("Docker Helpers - Usage Examples")
    print("="*50)

    # Example 1: Check if running
    print("\n1. Check Container Running:")
    if is_container_running():
        print("   ✓ MISP container is running")
    else:
        print("   ✗ MISP container is not running")

    # Example 2: Check if healthy
    print("\n2. Check Container Health:")
    if is_container_healthy():
        print("   ✓ MISP container is healthy")
    else:
        print("   ⚠ MISP container is not healthy")

    # Example 3: Get detailed status
    print("\n3. Get Detailed Status:")
    running, status = get_container_status()
    print(f"   Running: {running}")
    print(f"   Status: {status}")

    # Example 4: List all MISP containers
    print("\n4. List MISP Containers:")
    containers = list_misp_containers()
    for name, status in containers:
        print(f"   • {name}: {status}")
