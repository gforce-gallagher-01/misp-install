"""
Base class for all installation phases
"""

import subprocess
import logging
import time
from pathlib import Path
from typing import List, Optional, Callable
from lib.colors import Colors
from lib.state_manager import StateManager


class BasePhase:
    """Base class for all installation phases"""

    def __init__(self, config, logger: logging.Logger, misp_dir: Path):
        """Initialize phase

        Args:
            config: MISP configuration object
            logger: Logger instance
            misp_dir: MISP installation directory
        """
        self.config = config
        self.logger = logger
        self.misp_dir = misp_dir
        self.state_manager = StateManager()

    def run(self):
        """Execute phase - must be implemented by subclass

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement run() method")

    def run_command(self, cmd: List[str], check: bool = True,
                   cwd: Optional[Path] = None, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Run a command and log output

        Args:
            cmd: Command to run as list
            check: Raise exception on non-zero exit code
            cwd: Working directory for command
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result

        Raises:
            subprocess.CalledProcessError: If check=True and command fails
            subprocess.TimeoutExpired: If command times out
        """
        self.logger.debug(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=cwd,
                timeout=timeout
            )

            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"STDERR: {result.stderr}")

            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")
            if e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            raise
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out: {e}")
            raise

    def section_header(self, title: str):
        """Print a section header

        Args:
            title: Header title
        """
        self.logger.info("\n" + Colors.info("="*50))
        self.logger.info(Colors.info(title))
        self.logger.info(Colors.info("="*50) + "\n")

    def retry_on_failure(self, func: Callable, max_retries: int = 3,
                        retry_delay: int = 5) -> bool:
        """Retry a function on failure

        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds

        Returns:
            True if function succeeded, False if all retries failed
        """
        for attempt in range(1, max_retries + 1):
            try:
                func()
                return True
            except Exception as e:
                self.logger.error(Colors.error(f"Attempt {attempt}/{max_retries} failed: {e}"))

                if attempt < max_retries:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    return False

        return False

    def save_state(self, phase: int, phase_name: str):
        """Save installation state

        Args:
            phase: Current phase number
            phase_name: Descriptive phase name
        """
        self.state_manager.save(phase, phase_name, self.config.to_dict())
        self.logger.debug(f"Saved state: Phase {phase} - {phase_name}")

    def write_file_as_misp_user(self, content: str, dest_path: Path,
                                mode: str = '644', misp_user: str = 'misp-owner'):
        """Write file content to destination as misp-owner user

        Uses temp file pattern for secure file creation:
        1. Write to /tmp as current user
        2. Copy to destination with sudo
        3. Set ownership and permissions
        4. Clean up temp file

        Args:
            content: File content to write
            dest_path: Destination file path
            mode: File permissions (default: '644')
            misp_user: Owner user (default: 'misp-owner')
        """
        import os

        # Write to temp file first (accessible by current user)
        temp_file = f"/tmp/{dest_path.name}-{os.getpid()}"

        try:
            with open(temp_file, 'w') as f:
                f.write(content)

            # Copy to final location as misp-owner
            self.run_command(['sudo', 'cp', temp_file, str(dest_path)])
            self.run_command(['sudo', 'chmod', mode, str(dest_path)])
            self.run_command(['sudo', 'chown', f'{misp_user}:{misp_user}', str(dest_path)])

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass

    def create_dir_as_misp_user(self, dir_path: Path, mode: str = '755',
                               misp_user: str = 'misp-owner'):
        """Create directory as misp-owner user

        Args:
            dir_path: Directory path to create
            mode: Directory permissions (default: '755')
            misp_user: Owner user (default: 'misp-owner')
        """
        self.run_command(['sudo', '-u', misp_user, 'mkdir', '-p', str(dir_path)])
        self.run_command(['sudo', 'chmod', mode, str(dir_path)])
        self.run_command(['sudo', 'chown', f'{misp_user}:{misp_user}', str(dir_path)])
