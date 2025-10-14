"""
Phase 2: Configure Docker group access
"""

from phases.base_phase import BasePhase
from lib.docker_manager import DockerGroupManager
from lib.user_manager import MISP_USER


class Phase02DockerGroup(BasePhase):
    """Phase 2: Configure Docker group access for misp-owner

    SECURITY: Adds misp-owner to docker group, allowing container management
    without requiring root privileges for the installation user.
    """

    def run(self):
        """Execute Docker group configuration"""
        self.section_header("PHASE 2: DOCKER GROUP CONFIGURATION")

        docker_mgr = DockerGroupManager(self.logger)

        # SECURITY: Add dedicated misp-owner user to docker group
        docker_mgr.add_user_to_docker_group(MISP_USER)

        self.save_state(2, "Docker Group Configured")
