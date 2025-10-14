"""
Phase 6: Create configuration files
"""

import os
from phases.base_phase import BasePhase
from lib.colors import Colors
from lib.config import PerformanceTuning
from lib.user_manager import MISP_USER


class Phase06Configuration(BasePhase):
    """Phase 6: Create MISP configuration files"""

    def run(self):
        """Execute configuration"""
        self.section_header("PHASE 6: CONFIGURATION")

        self._create_env_file()

        self.logger.info(Colors.success("Configuration created"))
        self.save_state(6, "Configuration Complete")

    def _create_env_file(self):
        """Create .env configuration file"""
        self.logger.info("[6.1] Creating .env file...")

        # Calculate performance tuning
        perf = PerformanceTuning()

        # Adjust based on RAM
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        total_gb = int(line.split()[1]) // (1024**2)
                        if total_gb >= 16:
                            perf.php_memory_limit = "4096M"
                        elif total_gb >= 8:
                            perf.php_memory_limit = "2048M"
                        else:
                            perf.php_memory_limit = "1024M"
        except Exception:
            pass

        env_content = f"""##
# Build-time variables
##

CORE_TAG=v2.5.22
MODULES_TAG=v3.0.2
GUARD_TAG=v1.2
PHP_VER=20220829

PYPI_SETUPTOOLS_VERSION="==80.3.1"
PYPI_SUPERVISOR_VERSION="==4.2.5"

##
# Run-time variables - {self.config.admin_org} Configuration
# Environment: {self.config.environment}
##

# CRITICAL: {self.config.admin_org} Settings
BASE_URL={self.config.base_url}
ADMIN_EMAIL={self.config.admin_email}
ADMIN_ORG={self.config.admin_org}
ADMIN_PASSWORD={self.config.admin_password}
GPG_PASSPHRASE={self.config.gpg_passphrase}
MYSQL_PASSWORD={self.config.mysql_password}
ENCRYPTION_KEY={self.config.encryption_key}

# Database Configuration
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=misp
MYSQL_DATABASE=misp

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Optional Settings
ENABLE_DB_SETTINGS=true
ENABLE_BACKGROUND_UPDATES=true
CRON_USER_ID=1

# Security Settings
DISABLE_IPV6=false
DISABLE_SSL_REDIRECT=false
HSTS_MAX_AGE=31536000
X_FRAME_OPTIONS=SAMEORIGIN

# PHP Configuration (Performance Tuned)
PHP_MEMORY_LIMIT={perf.php_memory_limit}
PHP_MAX_EXECUTION_TIME={perf.php_max_execution_time}
PHP_UPLOAD_MAX_FILESIZE=50M
PHP_POST_MAX_SIZE=50M

# Nginx Configuration
NGINX_CLIENT_MAX_BODY_SIZE=50M

# Workers (Auto-calculated: {perf.workers} workers for {os.cpu_count()} CPU cores)
WORKERS={perf.workers}

# Debug (enabled for development environment)
DEBUG={1 if self.config.environment == 'development' else 0}
"""

        # Write as misp-owner using temp file pattern
        env_file = self.misp_dir / ".env"
        self.write_file_as_misp_user(env_content, env_file, mode='600', misp_user=MISP_USER)

        self.logger.info(Colors.success("Configuration created"))
        self.logger.info(f"  Performance tuning: {perf.php_memory_limit} RAM, {perf.workers} workers")
