"""
Phase 11.5: Generate automation API key
"""

import os
from datetime import datetime

from lib.colors import Colors
from lib.user_manager import MISP_USER
from phases.base_phase import BasePhase


class Phase11_5APIKey(BasePhase):
    """Phase 11.5: Generate automation API key"""

    def run(self):
        """Execute API key generation"""
        self.section_header("PHASE 11.5: API KEY GENERATION")

        self.logger.info("[11.5.1] Generating automation API key for admin user...")
        self.logger.info(f"        User: {self.config.admin_email}")

        os.chdir(self.misp_dir)

        try:
            api_key = self._generate_api_key()
            self._add_to_env_file(api_key)
            self._add_to_passwords_file(api_key)
            self._display_summary(api_key)

            self.save_state(11.5, "API Key Generated")

        except Exception as e:
            self.logger.error(Colors.error(f"API key generation failed: {e}"))
            self.logger.warning("You can generate an API key manually:")
            self.logger.warning("  1. Login to MISP web interface")
            self.logger.warning("  2. Navigate to: Global Actions > My Profile > Auth Keys")
            self.logger.warning("  3. Click 'Add authentication key'")
            self.logger.warning("  4. Add to /opt/misp/.env as MISP_API_KEY=<key>")
            # Don't fail installation - API key is optional
            self.logger.info("Continuing installation...")

    def _generate_api_key(self) -> str:
        """Generate new API key using MISP cake command"""
        result = self.run_command(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
             '/var/www/MISP/app/Console/cake', 'user', 'change_authkey',
             self.config.admin_email],
            timeout=30
        )

        # Extract API key from output
        # Expected output format: "Old authentication keys disabled and new key created: <KEY>"
        api_key = None
        for line in result.stdout.split('\n'):
            if 'new key created:' in line or 'Authkey updated:' in line or 'Authentication key:' in line:
                # Extract the key (last part of the line after ':')
                api_key = line.split(':')[-1].strip()
                break

        if not api_key:
            # Try alternative format - sometimes cake just outputs the key
            lines = [l.strip() for l in result.stdout.split('\n') if l.strip()]
            if lines:
                # Last non-empty line might be the key
                potential_key = lines[-1]
                # API keys are typically 40 characters alphanumeric
                if len(potential_key) == 40 and potential_key.isalnum():
                    api_key = potential_key

        if not api_key:
            self.logger.error("Could not extract API key from output")
            self.logger.error(f"Output was: {result.stdout}")
            raise RuntimeError("API key generation failed - could not parse output")

        self.logger.info(Colors.success(f"✓ API key generated: {api_key[:8]}...{api_key[-4:]}"))
        return api_key

    def _add_to_env_file(self, api_key: str):
        """Add API key to .env file"""
        self.logger.info("[11.5.2] Adding API key to .env file...")

        env_file = self.misp_dir / ".env"

        # Read existing .env content
        result = self.run_command(['sudo', 'cat', str(env_file)])
        env_content = result.stdout

        # Check if MISP_API_KEY already exists
        if 'MISP_API_KEY' in env_content:
            # Replace existing
            lines = env_content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('MISP_API_KEY='):
                    new_lines.append(f'MISP_API_KEY={api_key}')
                else:
                    new_lines.append(line)
            env_content = '\n'.join(new_lines)
        else:
            # Append new entry
            if not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'\n# API Key for automation scripts (generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n'
            env_content += f'MISP_API_KEY={api_key}\n'

        # Write updated .env using temp file pattern
        self.write_file_as_misp_user(env_content, env_file, mode='600', misp_user=MISP_USER)

        self.logger.info(Colors.success("✓ API key added to .env"))

    def _add_to_passwords_file(self, api_key: str):
        """Add API key to PASSWORDS.txt"""
        self.logger.info("[11.5.3] Adding API key to PASSWORDS.txt...")

        passwords_file = self.misp_dir / "PASSWORDS.txt"

        # Read existing PASSWORDS.txt content
        result = self.run_command(['sudo', 'cat', str(passwords_file)])
        passwords_content = result.stdout

        # Check if API KEY section already exists
        if 'API KEY:' in passwords_content:
            # Replace existing
            lines = passwords_content.split('\n')
            new_lines = []
            skip_next = False
            for i, line in enumerate(lines):
                if 'API KEY:' in line:
                    new_lines.append('API KEY:')
                    new_lines.append(f'  Key: {api_key}')
                    new_lines.append(f'  User: {self.config.admin_email}')
                    new_lines.append('  Use: Automation scripts (backup, feeds, news, etc.)')
                    new_lines.append('')
                    # Skip old API key lines
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('='):
                        j += 1
                    skip_next = j - i - 1
                elif skip_next > 0:
                    skip_next -= 1
                else:
                    new_lines.append(line)
            passwords_content = '\n'.join(new_lines)
        else:
            # Insert before final separator
            lines = passwords_content.split('\n')
            insert_pos = len(lines)
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].startswith('==='):
                    insert_pos = i
                    break

            api_section = [
                '',
                'API KEY:',
                f'  Key: {api_key}',
                f'  User: {self.config.admin_email}',
                '  Use: Automation scripts (backup, feeds, news, etc.)',
                ''
            ]

            lines = lines[:insert_pos] + api_section + lines[insert_pos:]
            passwords_content = '\n'.join(lines)

        # Write updated PASSWORDS.txt using temp file pattern
        self.write_file_as_misp_user(passwords_content, passwords_file, mode='600', misp_user=MISP_USER)

        self.logger.info(Colors.success("✓ API key added to PASSWORDS.txt"))

    def _display_summary(self, api_key: str):
        """Display API key summary"""
        self.logger.info(Colors.success("\n✓ API Key Setup Complete"))
        self.logger.info(f"  Key: {api_key}")
        self.logger.info(f"  User: {self.config.admin_email}")
        self.logger.info("  Stored in: /opt/misp/.env (MISP_API_KEY)")
        self.logger.info("             /opt/misp/PASSWORDS.txt")
        self.logger.info("\n  Use this key for automation scripts:")
        self.logger.info("  - python3 scripts/add-threat-feeds.py")
        self.logger.info("  - python3 scripts/populate-misp-news.py")
        self.logger.info("  - python3 scripts/fetch-all-feeds.py")
