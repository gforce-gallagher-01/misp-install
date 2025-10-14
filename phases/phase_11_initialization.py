"""
Phase 11: Wait for MISP initialization
"""

import os
import time
from phases.base_phase import BasePhase
from lib.colors import Colors


class Phase11Initialization(BasePhase):
    """Phase 11: Wait for MISP to complete initialization"""

    def run(self):
        """Execute initialization wait"""
        self.section_header("PHASE 11: MISP INITIALIZATION")

        self._wait_for_init()

        self.save_state(11, "MISP Initialized")

    def _wait_for_init(self):
        """Wait for MISP initialization to complete"""
        self.logger.info("[11.1] Waiting for MISP to initialize (5-10 minutes)...")
        self.logger.info("       Monitoring logs for 'INIT | Done'...")

        timeout = 600
        elapsed = 0
        interval = 10

        os.chdir(self.misp_dir)

        while elapsed < timeout:
            result = self.run_command(
                ['docker', 'compose', 'logs', 'misp-core'],
                check=False
            )

            if "INIT | Done" in result.stdout:
                self.logger.info(Colors.success("\n✅ MISP initialization complete!"))
                break

            self.logger.info(f"⏳ Waiting... ({elapsed} seconds elapsed)")
            time.sleep(interval)
            elapsed += interval

        if elapsed >= timeout:
            self.logger.warning("⚠️  Timeout waiting for initialization")
            self.logger.warning("MISP may still be starting")

        self.logger.info("\nWaiting additional 30 seconds...")
        time.sleep(30)
