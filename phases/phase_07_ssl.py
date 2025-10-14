"""
Phase 7: Generate SSL certificate
"""

import os
from phases.base_phase import BasePhase
from lib.colors import Colors
from lib.user_manager import MISP_USER


class Phase07SSL(BasePhase):
    """Phase 7: Generate SSL certificates"""

    def run(self):
        """Execute SSL certificate generation"""
        self.section_header("PHASE 7: SSL CERTIFICATE")

        self._create_ssl_directory()
        self._generate_certificate()
        self._create_docker_override()

        self.logger.info(Colors.success("SSL certificate generated"))
        self.save_state(7, "SSL Certificate Created")

    def _create_ssl_directory(self):
        """Create SSL directory"""
        self.logger.info("[7.1] Creating SSL directory...")
        ssl_dir = self.misp_dir / "ssl"

        # SECURITY: Create directory as misp-owner using sudo
        self.create_dir_as_misp_user(ssl_dir, mode='755', misp_user=MISP_USER)

    def _generate_certificate(self):
        """Generate self-signed SSL certificate"""
        self.logger.info(f"[7.2] Generating self-signed certificate for {self.config.domain}...")

        ssl_dir = self.misp_dir / "ssl"

        # Generate certificate in /tmp first (accessible by current user)
        temp_key = f"/tmp/misp-key-{os.getpid()}.pem"
        temp_cert = f"/tmp/misp-cert-{os.getpid()}.pem"

        self.run_command([
            'openssl', 'req', '-x509', '-nodes', '-days', '365',
            '-newkey', 'rsa:4096',
            '-keyout', temp_key,
            '-out', temp_cert,
            '-subj', f"/C=US/ST=New York/L=New York/O={self.config.admin_org}/OU=IT/CN={self.config.domain}",
            '-addext', f"subjectAltName=DNS:{self.config.domain},DNS:*.{self.config.domain},IP:{self.config.server_ip}"
        ])

        # Move certificates to ssl directory (as root, then chown to misp-owner)
        # SECURITY NOTE: Can't use -u misp-owner because temp files are owned by current user with 600 perms
        self.run_command(['sudo', 'cp', temp_key, str(ssl_dir / 'key.pem')])
        self.run_command(['sudo', 'cp', temp_cert, str(ssl_dir / 'cert.pem')])

        # Set proper permissions
        self.run_command(['sudo', 'chmod', '644', str(ssl_dir / 'cert.pem')])
        self.run_command(['sudo', 'chmod', '600', str(ssl_dir / 'key.pem')])
        self.run_command(['sudo', 'chown', f'{MISP_USER}:{MISP_USER}', str(ssl_dir / 'key.pem')])
        self.run_command(['sudo', 'chown', f'{MISP_USER}:{MISP_USER}', str(ssl_dir / 'cert.pem')])

        # Clean up temp files
        try:
            os.unlink(temp_key)
            os.unlink(temp_cert)
        except:
            pass

    def _create_docker_override(self):
        """Create docker-compose.override.yml"""
        self.logger.info("[7.3] Creating docker-compose.override.yml...")

        override_content = """services:
  misp-core:
    volumes:
      - ./ssl:/etc/nginx/certs:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      misp-modules:
        condition: service_started

  misp-modules:
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6666/modules || exit 1"]
      interval: 30s
      timeout: 15s
      retries: 15
      start_period: 180s
"""

        # Write docker-compose.override.yml using temp file pattern
        override_file = self.misp_dir / "docker-compose.override.yml"
        self.write_file_as_misp_user(override_content, override_file, mode='644', misp_user=MISP_USER)
