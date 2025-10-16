"""
Pre-flight system checks for MISP installation
"""

import os
import shutil
import socket
import subprocess
import logging
from pathlib import Path
from typing import Tuple
from lib.colors import Colors
from lib.config import SystemRequirements


class SystemChecker:
    """Pre-flight system checks"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.requirements = SystemRequirements()

    def check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space

        Returns:
            Tuple of (passed, message)
        """
        try:
            stat = shutil.disk_usage(str(Path.home()))
            available_gb = stat.free // (1024**3)

            if available_gb < self.requirements.min_disk_gb:
                return False, f"Insufficient disk space: {available_gb}GB available, {self.requirements.min_disk_gb}GB required"

            return True, f"Disk space OK: {available_gb}GB available"
        except Exception as e:
            return False, f"Could not check disk space: {e}"

    def check_ram(self) -> Tuple[bool, str]:
        """Check available RAM

        Returns:
            Tuple of (passed, message)
        """
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        total_kb = int(line.split()[1])
                        total_gb = total_kb // (1024**2)

                        if total_gb < self.requirements.min_ram_gb:
                            return False, f"Insufficient RAM: {total_gb}GB available, {self.requirements.min_ram_gb}GB required"

                        return True, f"RAM OK: {total_gb}GB available"

            return False, "Could not read memory info"
        except Exception as e:
            return False, f"Could not check RAM: {e}"

    def check_cpu(self) -> Tuple[bool, str]:
        """Check CPU cores

        Returns:
            Tuple of (passed, message)
        """
        try:
            cpu_count = os.cpu_count()

            if cpu_count < self.requirements.min_cpu_cores:
                return False, f"Insufficient CPU cores: {cpu_count} available, {self.requirements.min_cpu_cores} required"

            return True, f"CPU OK: {cpu_count} cores available"
        except Exception as e:
            return False, f"Could not check CPU: {e}"

    def check_ports(self) -> Tuple[bool, str]:
        """Check if required ports are available

        Returns:
            Tuple of (passed, message)
        """
        blocked_ports = []

        for port in self.requirements.required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
            except OSError as e:
                if e.errno == 98:  # EADDRINUSE
                    blocked_ports.append(port)
                elif e.errno == 13:  # EACCES - expected for privileged ports
                    continue
                else:
                    blocked_ports.append(port)

        if blocked_ports:
            return False, f"Ports already in use: {', '.join(map(str, blocked_ports))}"

        return True, "All required ports available (Docker will use privileged ports)"

    def check_docker(self) -> Tuple[bool, str]:
        """Check if Docker is installed and running

        Returns:
            Tuple of (passed, message)
        """
        try:
            result = subprocess.run(
                ['docker', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return True, "Docker not running (will be started during installation)"

            return True, "Docker is installed and running"
        except FileNotFoundError:
            return True, "Docker not installed (will be installed during Phase 1)"
        except subprocess.TimeoutExpired:
            return True, "Docker not responding (will be configured during installation)"

    def check_root(self) -> Tuple[bool, str]:
        """Check if running as root

        Returns:
            Tuple of (passed, message)
        """
        if os.geteuid() == 0:
            return False, "Script should not be run as root"
        return True, "Running as regular user"

    def run_all_checks(self) -> bool:
        """Run all system checks

        Returns:
            True if all checks passed, False otherwise
        """
        self.logger.info(Colors.info("\n" + "="*50))
        self.logger.info(Colors.info("PRE-FLIGHT SYSTEM CHECKS"))
        self.logger.info(Colors.info("="*50 + "\n"))

        checks = [
            ("User Check", self.check_root),
            ("Disk Space", self.check_disk_space),
            ("RAM", self.check_ram),
            ("CPU Cores", self.check_cpu),
            ("Port Availability", self.check_ports),
            ("Docker", self.check_docker),
        ]

        all_passed = True

        for name, check_func in checks:
            passed, message = check_func()

            if passed:
                self.logger.info(Colors.success(f"{name}: {message}"))
            else:
                self.logger.error(Colors.error(f"{name}: {message}"))
                all_passed = False

        return all_passed
