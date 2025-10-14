"""
Phase 9: Create password reference file
"""

from datetime import datetime
from phases.base_phase import BasePhase
from lib.colors import Colors
from lib.user_manager import MISP_USER


class Phase09Passwords(BasePhase):
    """Phase 9: Create password reference file"""

    def run(self):
        """Execute password reference creation"""
        self.section_header("PHASE 9: PASSWORD REFERENCE")

        self._create_password_file()

        self.logger.info(Colors.success(f"Password reference saved to: {self.misp_dir}/PASSWORDS.txt"))
        self.save_state(9, "Password Reference Created")

    def _create_password_file(self):
        """Create PASSWORDS.txt with all credentials"""
        self.logger.info("[9.1] Creating secure password reference file...")

        # Get certificate expiry
        try:
            result = self.run_command([
                'openssl', 'x509', '-enddate', '-noout',
                '-in', str(self.misp_dir / 'ssl' / 'cert.pem')
            ])
            cert_expiry = result.stdout.strip().split('=')[1]
        except Exception:
            cert_expiry = "Unknown"

        password_content = f"""================================================
MISP PASSWORD REFERENCE - {self.config.admin_org}
================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: {self.config.environment}

ADMIN WEB LOGIN:
  URL:      {self.config.base_url}
  Email:    {self.config.admin_email}
  Password: {self.config.admin_password}

DATABASE:
  Host:     db (container)
  User:     misp
  Password: {self.config.mysql_password}
  Database: misp

GPG:
  Passphrase: {self.config.gpg_passphrase}
  Email:      {self.config.admin_email}

ENCRYPTION:
  Key: {self.config.encryption_key}
  ⚠️  DO NOT CHANGE - data will be lost!

SERVER:
  IP:   {self.config.server_ip}
  FQDN: {self.config.domain}

CERTIFICATE:
  Location: /opt/misp/ssl/cert.pem
  Expires:  {cert_expiry}

PERFORMANCE:
  PHP Memory: {self.config.performance['php_memory_limit']}
  Workers:    {self.config.performance['workers']}

================================================
⚠️  KEEP THIS FILE SECURE AND BACKED UP!
================================================
"""

        # SECURITY: Write using temp file pattern (owned by misp-owner)
        passwords_file = self.misp_dir / "PASSWORDS.txt"
        self.write_file_as_misp_user(password_content, passwords_file, mode='600', misp_user=MISP_USER)
