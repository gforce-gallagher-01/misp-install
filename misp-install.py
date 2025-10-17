#!/usr/bin/env python3
"""
MISP Complete Installation & Management Tool
tKQB Enterprises
Version: 5.6 (Advanced Features Release)

Features:
- Modular architecture with phase-based execution
- Pre-flight system checks
- Centralized JSON logging with CIM fields
- Backup before cleanup
- Config file support (YAML/JSON)
- Docker group activation
- Resume capability
- Error recovery with retry
- Password validation
- Post-install checklist
- Port conflict detection
- Multi-environment (dev/staging/prod)
- Performance tuning based on resources
"""

import os
import sys
import subprocess
from pathlib import Path

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

# Import library modules
from lib.colors import Colors
from lib.config import MISPConfig, Environment
from lib.validators import PasswordValidator
from lib.system_checker import SystemChecker
from lib.state_manager import StateManager
from lib.user_manager import ensure_misp_user_exists, get_current_username, MISP_USER
from lib.logging_setup import setup_logging

# Import phase modules
from phases import (
    Phase01Dependencies,
    Phase02DockerGroup,
    Phase03Backup,
    Phase04Cleanup,
    Phase05Clone,
    Phase06Configuration,
    Phase07SSL,
    Phase08DNS,
    Phase09Passwords,
    Phase10DockerBuild,
    Phase11Initialization,
    Phase11_5APIKey,
    Phase11_7ThreatFeeds,
    Phase11_8UtilitiesSector,
    Phase11_9AutomatedMaintenance,
    Phase11_10SecurityNews,
    Phase11_11UtilitiesDashboards,
    Phase12PostInstall,
)

# Try to import yaml for config file support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class MISPInstaller:
    """Main MISP installation orchestrator"""

    def __init__(self, config: MISPConfig, logger, interactive: bool = True):
        """Initialize installer

        Args:
            config: MISP configuration
            logger: Logger instance
            interactive: Interactive mode flag
        """
        self.config = config
        self.logger = logger
        self.interactive = interactive
        self.misp_dir = Path("/opt/misp")
        self.state_manager = StateManager()

        # Define phase sequence
        self.phases = [
            (1, "Dependencies", Phase01Dependencies),
            (2, "Docker Group", Phase02DockerGroup),
            (3, "Backup", Phase03Backup),
            (4, "Cleanup", Phase04Cleanup),
            (5, "Clone Repository", Phase05Clone),
            (6, "Configuration", Phase06Configuration),
            (7, "SSL Certificate", Phase07SSL),
            (8, "DNS Configuration", Phase08DNS),
            (9, "Password Reference", Phase09Passwords),
            (10, "Docker Build", Phase10DockerBuild),
            (11, "Initialization", Phase11Initialization),
            (11.5, "API Key", Phase11_5APIKey),
            (11.7, "Threat Feeds", Phase11_7ThreatFeeds),
            (11.8, "Utilities Sector", Phase11_8UtilitiesSector),
            (11.9, "Automated Maintenance", Phase11_9AutomatedMaintenance),
            (11.10, "Security News", Phase11_10SecurityNews),
            (11.11, "Utilities Dashboards", Phase11_11UtilitiesDashboards),
            (12, "Post-Install", Phase12PostInstall),
        ]

    def run_installation(self, start_phase: int = 1) -> bool:
        """Run the complete installation

        Args:
            start_phase: Phase number to start from (for resume)

        Returns:
            True if successful, False otherwise
        """
        # Show installation plan
        if start_phase > 1:
            self.logger.info(Colors.info("\nInstallation Plan:"))
            for phase_num, phase_name, _ in self.phases:
                if phase_num < start_phase:
                    self.logger.info(Colors.success(f"  Phase {phase_num:4}: {phase_name:30s} [COMPLETED]"))
                else:
                    self.logger.info(f"  Phase {phase_num:4}: {phase_name:30s} [PENDING]")
            self.logger.info("")

        # Execute phases
        for phase_num, phase_name, PhaseClass in self.phases:
            if phase_num < start_phase:
                continue

            try:
                # Create phase instance
                phase = PhaseClass(self.config, self.logger, self.misp_dir)

                # Execute phase with retry logic
                max_retries = 3
                for attempt in range(1, max_retries + 1):
                    try:
                        phase.run()
                        break  # Success
                    except Exception as e:
                        self.logger.error(Colors.error(f"Attempt {attempt}/{max_retries} failed: {e}"))

                        if attempt < max_retries:
                            if self.interactive:
                                response = input(f"Retry {phase_name}? (yes/no): ").lower()
                                if response != 'yes':
                                    return False
                            else:
                                self.logger.info("Retrying...")
                                import time
                                time.sleep(5)
                        else:
                            self.logger.error(Colors.error(f"Phase {phase_num} failed after {max_retries} attempts"))
                            return False

            except KeyboardInterrupt:
                self.logger.warning("\n⚠️  Installation interrupted by user")
                self.logger.info(f"Resume from phase {phase_num} with: python3 misp-install.py --resume")
                return False
            except Exception as e:
                self.logger.error(Colors.error(f"Phase {phase_num} ({phase_name}) failed: {e}"))
                self.logger.exception("Full traceback:")
                return False

        return True

    def print_final_summary(self):
        """Print final installation summary"""
        self.logger.info("\n" + Colors.info("="*50))
        self.logger.info(Colors.info("✅ MISP INSTALLATION COMPLETE!"))
        self.logger.info(Colors.info("="*50) + "\n")

        print(f"""
🌐 Access Information:
   URL:      {self.config.base_url}
   Email:    {self.config.admin_email}
   Password: (see PASSWORDS.txt)

🔐 All Credentials Saved To:
   {self.misp_dir}/PASSWORDS.txt
   {self.misp_dir}/.env

   ⚠️  BACKUP THESE FILES SECURELY!

📁 Installation Directory: {self.misp_dir}

📋 View Your Passwords:
   sudo cat {self.misp_dir}/PASSWORDS.txt

📝 Post-Install Checklist:
   sudo cat {self.misp_dir}/POST-INSTALL-CHECKLIST.md

⚠️  IMPORTANT - WORKSTATION SETUP:

   Windows users add to C:\\Windows\\System32\\drivers\\etc\\hosts:
   {self.config.server_ip} {self.config.domain}

   macOS/Linux workstations:
   echo '{self.config.server_ip} {self.config.domain}' | sudo tee -a /etc/hosts

🔧 Useful Commands:
   View passwords: sudo cat {self.misp_dir}/PASSWORDS.txt
   View logs:      cd {self.misp_dir} && sudo docker compose logs -f
   Restart:        cd {self.misp_dir} && sudo docker compose restart
   Stop:           cd {self.misp_dir} && sudo docker compose down
   Start:          cd {self.misp_dir} && sudo docker compose up -d

⚠️  NOTE: You may need to logout/login for docker group to take full effect

==================================================
🎉 Ready to use! Open browser to: {self.config.base_url}
==================================================
""")


def get_user_input_interactive(logger) -> MISPConfig:
    """Get configuration from user interactively

    Args:
        logger: Logger instance

    Returns:
        MISPConfig object
    """
    print(Colors.info("\n" + "="*50))
    print(Colors.info("📋 CONFIGURATION"))
    print(Colors.info("="*50 + "\n"))

    print("Please provide installation details:\n")

    # Import hostname detection
    from lib.config import get_system_hostname

    # Auto-detect system hostname
    detected_hostname = get_system_hostname()
    print(f"🔍 Detected system hostname: {Colors.success(detected_hostname)}\n")

    server_ip = input("Enter server IP address [192.168.20.193]: ") or "192.168.20.193"
    domain = input(f"Enter FQDN for MISP [{detected_hostname}]: ") or detected_hostname
    admin_email = input("Enter admin email [admin@yourcompany.com]: ") or "admin@yourcompany.com"
    admin_org = input("Enter organization name [tKQB Enterprises]: ") or "tKQB Enterprises"

    # Environment selection
    print("\nEnvironment:")
    print("1) Development")
    print("2) Staging")
    print("3) Production (recommended)")
    env_choice = input("Select environment [3]: ") or "3"

    env_map = {
        "1": Environment.DEV.value,
        "2": Environment.STAGING.value,
        "3": Environment.PROD.value
    }
    environment = env_map.get(env_choice, Environment.PROD.value)

    print(Colors.info("\n" + "="*50))
    print(Colors.info("🔐 PASSWORD CONFIGURATION"))
    print(Colors.info("="*50 + "\n"))
    print("Passwords must be at least 12 characters with uppercase, lowercase, number, and special character.\n")

    admin_password = PasswordValidator.get_password_interactive("Enter MISP admin password (min 12 chars): ")
    print()

    mysql_password = PasswordValidator.get_password_interactive("Enter MySQL database password (min 12 chars): ")
    print()

    gpg_passphrase = PasswordValidator.get_password_interactive("Enter GPG passphrase (min 12 chars): ")
    print()

    print("Generating encryption key...")
    import secrets
    encryption_key = secrets.token_hex(16)
    print(Colors.success("Encryption key generated"))

    # Create config
    config = MISPConfig(
        server_ip=server_ip,
        domain=domain,
        admin_email=admin_email,
        admin_org=admin_org,
        admin_password=admin_password,
        mysql_password=mysql_password,
        gpg_passphrase=gpg_passphrase,
        encryption_key=encryption_key,
        environment=environment
    )

    # Show summary
    print(Colors.info("\n" + "="*50 + "\n"))
    print("Configuration Summary:")
    print(f"  Server IP:    {config.server_ip}")
    print(f"  FQDN:         {config.domain}")
    print(f"  Admin Email:  {config.admin_email}")
    print(f"  Organization: {config.admin_org}")
    print(f"  Environment:  {config.environment}")
    print(f"  Base URL:     {config.base_url}")
    print()
    print(f"  Admin Password:   {'*' * len(config.admin_password)} ({len(config.admin_password)} characters)")
    print(f"  MySQL Password:   {'*' * len(config.mysql_password)} ({len(config.mysql_password)} characters)")
    print(f"  GPG Passphrase:   {'*' * len(config.gpg_passphrase)} ({len(config.gpg_passphrase)} characters)")
    print(f"  Encryption Key:   {config.encryption_key}")
    print()
    print("⚠️  IMPORTANT: Save these passwords securely!")
    print()

    confirm = input("Is this correct? Type 'YES' to proceed: ")
    if confirm != 'YES':
        print("Aborted.")
        sys.exit(0)

    return config


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='MISP Installation Tool v5.5 (Modular)')
    parser.add_argument('--config', type=str, help='Path to config file (YAML or JSON)')
    parser.add_argument('--non-interactive', action='store_true', help='Run in non-interactive mode')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--skip-checks', action='store_true', help='Skip pre-flight checks')

    args = parser.parse_args()

    # SECURITY: Ensure NOT running as root
    if os.geteuid() == 0:
        print("❌ ERROR: Do not run this script as root!")
        print("\nFor security, this script should be run as a regular user.")
        print("The script will automatically create and use a dedicated 'misp-owner' user.")
        print("\nUsage:")
        print(f"  python3 {sys.argv[0]}")
        sys.exit(1)

    # Ensure dedicated misp-owner user exists
    current_user = get_current_username()
    print(f"\n✓ Running as: {current_user}")

    print(f"\n📋 Ensuring dedicated user '{MISP_USER}' exists...")
    print("   This follows security best practices (principle of least privilege).")

    if not ensure_misp_user_exists():
        print(f"\n❌ Cannot proceed without dedicated user. Exiting.")
        sys.exit(1)

    print(f"✓ User '{MISP_USER}' ready")
    print(f"✓ All MISP files will be owned by {MISP_USER}\n")

    # CRITICAL: Create /opt/misp/logs directory BEFORE initializing logger
    log_dir = Path("/opt/misp/logs")
    if not log_dir.exists():
        try:
            result = subprocess.run(['sudo', 'mkdir', '-p', '/opt/misp/logs'],
                                  check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️  Could not create /opt/misp/logs with sudo: {result.stderr}")
                print(f"⚠️  Will use console-only logging")
            else:
                subprocess.run(['sudo', 'chown', '-R', f'{MISP_USER}:{MISP_USER}', '/opt/misp/logs'],
                             check=False, capture_output=True)
                subprocess.run(['sudo', 'chmod', '777', '/opt/misp/logs'],
                             check=False, capture_output=True)
        except Exception as e:
            print(f"⚠️  Could not create /opt/misp/logs directory: {e}")
            print(f"⚠️  Will use console-only logging")

    # Setup logging
    logger = setup_logging()

    logger.info(Colors.info("""
╔══════════════════════════════════════════════════╗
║                                                  ║
║      MISP Complete Installation Tool v5.5       ║
║              tKQB Enterprises                    ║
║         Modular Architecture Edition             ║
║         Dedicated User: misp-owner               ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""))

    try:
        # Pre-flight checks
        if not args.skip_checks:
            checker = SystemChecker(logger)
            if not checker.run_all_checks():
                logger.error(Colors.error("\n❌ Pre-flight checks failed!"))
                logger.info("Fix the issues above and try again")
                sys.exit(1)

        # Check for resume
        start_phase = 1
        config = None
        interactive = True

        state_manager = StateManager()
        state = state_manager.load()

        if args.resume and state:
            # Resume from saved state
            start_phase = state['phase'] + 1
            logger.info(Colors.info("\n📍 RESUMING PREVIOUS INSTALLATION"))
            logger.info(Colors.info("="*50))
            logger.info(f"Last completed phase: {state['phase']} - {state.get('phase_name', 'Unknown')}")
            logger.info(f"Previous run: {state['timestamp']}")
            logger.info(f"Resuming from phase: {start_phase}")
            logger.info(Colors.info("="*50 + "\n"))

            # Load config from saved state
            config = MISPConfig.from_dict(state['config'])
            logger.info("✓ Configuration loaded from saved state")
            logger.info(f"  Organization: {config.admin_org}")
            logger.info(f"  Domain: {config.domain}")
            logger.info(f"  Environment: {config.environment}\n")

            if start_phase > 2:
                interactive = False
        elif args.resume and not state:
            logger.warning(Colors.warning("⚠️  No saved state found. Starting fresh installation."))
            args.resume = False

        # Load or get configuration
        if config is None:
            if args.config:
                logger.info(f"Loading configuration from: {args.config}")
                if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                    if not HAS_YAML:
                        logger.error(Colors.error("❌ PyYAML not installed. Install with: pip3 install pyyaml"))
                        sys.exit(1)
                    config = MISPConfig.from_yaml(args.config)
                else:
                    config = MISPConfig.from_json(args.config)
                interactive = False
            elif args.non_interactive:
                logger.error(Colors.error("❌ Non-interactive mode requires --config"))
                sys.exit(1)
            else:
                config = get_user_input_interactive(logger)
                interactive = True

        # Create installer
        installer = MISPInstaller(config, logger, interactive=interactive)

        # Run installation
        success = installer.run_installation(start_phase=start_phase)

        if success:
            state_manager.clear()
            installer.print_final_summary()
            sys.exit(0)
        else:
            logger.error(Colors.error("\n❌ Installation failed"))
            logger.info(f"Check logs: /opt/misp/logs/")
            logger.info("You can resume with: python3 misp-install.py --resume")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Installation interrupted by user")
        logger.info("Resume with: python3 misp-install.py --resume")
        sys.exit(1)
    except Exception as e:
        logger.error(Colors.error(f"\n❌ Unexpected error: {e}"))
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
