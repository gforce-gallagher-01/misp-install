"""
Phase 5: Clone MISP repository
"""

import os
from pathlib import Path

from lib.colors import Colors
from lib.user_manager import MISP_USER
from phases.base_phase import BasePhase


class Phase05Clone(BasePhase):
    """Phase 5: Clone MISP Docker repository"""

    def run(self):
        """Execute repository cloning"""
        self.section_header("PHASE 5: CLONING MISP REPOSITORY")

        self._check_existing_installation()
        self._ensure_misp_directory()
        self._clone_repository()
        self._set_ownership()
        self._configure_logs_directory()

        os.chdir(self.misp_dir)

        self.logger.info(Colors.success("Repository cloned"))
        self.save_state(5, "Repository Cloned")

    def _check_existing_installation(self):
        """Check for existing MISP installation"""
        self.logger.info("[5.1] Checking if /opt/misp exists...")

        # Check if /opt/misp exists and has MISP content (not just logs)
        if self.misp_dir.exists():
            # Count items in /opt/misp (excluding logs directory)
            existing_items = [item for item in self.misp_dir.iterdir() if item.name != 'logs']

            if existing_items:
                # MISP already installed - user must run uninstall first
                self.logger.error(Colors.error("\n❌ Existing MISP installation detected!"))
                self.logger.error(f"   Found {len(existing_items)} items in /opt/misp")
                self.logger.error("\n   You must uninstall first:")
                self.logger.error("   python3 scripts/uninstall-misp.py --force\n")
                raise RuntimeError("Existing MISP installation found. Run uninstall-misp.py first.")

    def _ensure_misp_directory(self):
        """Ensure /opt/misp directory exists"""
        # Ensure /opt/misp directory exists (might only have logs directory at this point)
        self.misp_dir.mkdir(exist_ok=True)

    def _clone_repository(self):
        """Clone MISP Docker repository"""
        self.logger.info("[5.2] Cloning MISP Docker repository...")
        self.logger.info("This may take 1-2 minutes...")

        # Clone to temporary directory
        temp_clone = Path("/tmp/misp-docker-clone")
        if temp_clone.exists():
            self.run_command(['sudo', 'rm', '-rf', str(temp_clone)])

        self.run_command([
            'sudo', 'git', 'clone', '--progress',
            'https://github.com/MISP/misp-docker.git',
            str(temp_clone)
        ], timeout=300)

        # Move contents from temp to /opt/misp (preserving logs directory if it exists)
        self.logger.info("[5.3] Moving repository contents...")
        for item in temp_clone.iterdir():
            # Skip .git directory and don't overwrite logs
            if item.name not in ['.git', 'logs']:
                self.run_command(['sudo', 'mv', str(item), str(self.misp_dir)])

        # Clean up temp directory
        self.run_command(['sudo', 'rm', '-rf', str(temp_clone)])

    def _set_ownership(self):
        """Set ownership to misp-owner"""
        # Set ownership to misp-owner (dedicated system user)
        # SECURITY: All MISP files owned by misp-owner, following least privilege principle
        self.logger.info(f"[5.4] Setting ownership to {MISP_USER}...")
        self.run_command(['sudo', 'chown', '-R', f'{MISP_USER}:{MISP_USER}', str(self.misp_dir)])

    def _configure_logs_directory(self):
        """Configure logs directory with proper permissions"""
        # CRITICAL: Ensure logs directory exists with proper permissions BEFORE Docker starts
        # Docker will mount ./logs and if we don't set this up correctly, Docker will create it as www-data
        self.logger.info("[5.5] Configuring logs directory permissions...")
        logs_dir = self.misp_dir / "logs"

        # Create logs directory if it doesn't exist
        self.run_command(['sudo', '-u', MISP_USER, 'mkdir', '-p', str(logs_dir)])

        # SECURITY: Set 777 permissions so both Docker (www-data) and management scripts can write
        # This is necessary because:
        # 1. Docker containers run as www-data and write MISP application logs
        # 2. Our installation/management scripts run as current user and write JSON logs
        # 3. ACLs would be cleaner but require additional setup
        self.run_command(['sudo', 'chmod', '777', str(logs_dir)])

        # Ensure ownership is misp-owner (for consistency)
        self.run_command(['sudo', 'chown', f'{MISP_USER}:{MISP_USER}', str(logs_dir)])

        self.logger.info(Colors.success(f"✓ Logs directory ready (owner: {MISP_USER}, mode: 777)"))
