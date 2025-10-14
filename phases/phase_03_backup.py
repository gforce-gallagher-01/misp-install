"""
Phase 3: Backup existing installation
"""

from phases.base_phase import BasePhase
from lib.backup_manager import BackupManager
from lib.colors import Colors


class Phase03Backup(BasePhase):
    """Phase 3: Backup existing MISP installation"""

    def run(self):
        """Execute backup"""
        self.section_header("PHASE 3: BACKUP EXISTING INSTALLATION")

        backup_mgr = BackupManager(self.logger)
        backup_path = backup_mgr.create_backup(self.misp_dir)

        if backup_path:
            self.logger.info(Colors.success(f"Backup saved to: {backup_path}"))

        self.save_state(3, "Backup Complete")
