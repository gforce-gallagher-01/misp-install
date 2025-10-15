#!/usr/bin/env python3
"""
MISP GUI Installer
tKQB Enterprises Edition
Version: 2.0

Modern graphical installer using Python Textual framework.
Provides an intuitive multi-step wizard interface that runs in terminal (TUI) or web browser.

Usage:
    # Terminal mode
    python3 misp-install-gui.py

    # Web browser mode
    textual serve misp-install-gui.py

    # Load existing config
    python3 misp-install-gui.py --load config/misp-config.json

    # Save config without installing
    python3 misp-install-gui.py --save-only
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import os

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8 or higher required")
    sys.exit(1)

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
    from textual.widgets import (
        Header, Footer, Button, Static, Label, Input,
        Select, RadioSet, RadioButton, Checkbox, ProgressBar
    )
    from textual.screen import Screen
    from textual import on
    from textual.validation import ValidationResult, Validator
    from textual.events import Paste
except ImportError:
    print("❌ Textual framework not installed")
    print("📦 Install with: pip install textual textual-dev")
    sys.exit(1)

# Try to import pyperclip for clipboard support
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("")
    print("=" * 60)
    print("⚠️  CLIPBOARD SUPPORT NOT AVAILABLE")
    print("=" * 60)
    print("")
    print("The GUI installer requires pyperclip for Ctrl+V paste support.")
    print("")
    print("To install all dependencies automatically, run:")
    print("  ./install-gui.sh")
    print("")
    print("Or install manually:")
    print("  sudo apt install xclip")
    print("  pipx uninstall misp-installer-gui")
    print("  pipx install .")
    print("")
    print("Continuing without clipboard support...")
    print("")
    import time
    time.sleep(3)

# ==========================================
# Helper Functions
# ==========================================

def check_misp_installed() -> bool:
    """Check if MISP is already installed"""
    misp_dir = Path("/opt/misp")
    docker_compose = misp_dir / "docker-compose.yml"
    env_file = misp_dir / ".env"

    # Check if key files exist
    if not misp_dir.exists():
        return False

    if not docker_compose.exists() or not env_file.exists():
        return False

    # Check if containers are running
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'compose', 'ps', '-q'],
            cwd=str(misp_dir),
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except:
        return False


def verify_uninstall_complete() -> dict:
    """Verify that MISP has been completely uninstalled

    Returns:
        dict: Health check results with status and details
    """
    health_checks = {
        'misp_directory': False,
        'docker_containers': False,
        'docker_images': False,
        'misp_user': False,
        'all_clean': True
    }

    details = []

    # Check 1: MISP directory should not exist
    misp_dir = Path("/opt/misp")
    if not misp_dir.exists():
        health_checks['misp_directory'] = True
        details.append("✓ MISP directory removed (/opt/misp)")
    else:
        health_checks['misp_directory'] = False
        health_checks['all_clean'] = False
        details.append("✗ MISP directory still exists (/opt/misp)")

    # Check 2: No MISP Docker containers running
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '--filter', 'name=misp', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        containers = [c for c in result.stdout.strip().split('\n') if c]
        if not containers:
            health_checks['docker_containers'] = True
            details.append("✓ No MISP Docker containers found")
        else:
            health_checks['docker_containers'] = False
            health_checks['all_clean'] = False
            details.append(f"✗ Found {len(containers)} MISP container(s) still present")
            for container in containers[:3]:  # Show first 3
                details.append(f"  - {container}")
    except Exception as e:
        details.append(f"⚠️  Could not check Docker containers: {e}")
        health_checks['all_clean'] = False

    # Check 3: No MISP Docker images
    try:
        result = subprocess.run(
            ['sudo', 'docker', 'images', '--filter', 'reference=*misp*', '--format', '{{.Repository}}:{{.Tag}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        images = [img for img in result.stdout.strip().split('\n') if img and img != '<none>:<none>']
        if not images:
            health_checks['docker_images'] = True
            details.append("✓ No MISP Docker images found")
        else:
            health_checks['docker_images'] = False
            health_checks['all_clean'] = False
            details.append(f"⚠️  Found {len(images)} MISP image(s) still present")
            for image in images[:3]:  # Show first 3
                details.append(f"  - {image}")
    except Exception as e:
        details.append(f"⚠️  Could not check Docker images: {e}")

    # Check 4: misp-owner user should not exist
    try:
        result = subprocess.run(
            ['id', 'misp-owner'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            health_checks['misp_user'] = True
            details.append("✓ misp-owner user removed")
        else:
            health_checks['misp_user'] = False
            health_checks['all_clean'] = False
            details.append("✗ misp-owner user still exists")
    except Exception as e:
        details.append(f"⚠️  Could not check misp-owner user: {e}")
        health_checks['all_clean'] = False

    return {
        'checks': health_checks,
        'details': details
    }

# ==========================================
# Custom Validators
# ==========================================

class IPAddressValidator(Validator):
    """Validate IP address format"""
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("IP address is required")

        parts = value.split('.')
        if len(parts) != 4:
            return self.failure("Must be in format: xxx.xxx.xxx.xxx")

        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return self.failure("Each octet must be 0-255")
            return self.success()
        except ValueError:
            return self.failure("Each octet must be a number")

class DomainValidator(Validator):
    """Validate domain/FQDN format"""
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("Domain is required")

        if len(value) < 4:
            return self.failure("Domain too short")

        if ' ' in value:
            return self.failure("Domain cannot contain spaces")

        if not '.' in value:
            return self.failure("Must be a valid domain (e.g., misp.local)")

        return self.success()

class EmailValidator(Validator):
    """Validate email format"""
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("Email is required")

        if '@' not in value or '.' not in value:
            return self.failure("Must be valid email (e.g., admin@company.com)")

        parts = value.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return self.failure("Invalid email format")

        return self.success()

class PasswordValidator(Validator):
    """Validate password strength"""
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("Password is required")

        if len(value) < 12:
            return self.failure("Password must be at least 12 characters")

        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in value)

        if not (has_upper and has_lower and has_digit and has_special):
            return self.failure("Password must contain uppercase, lowercase, number, and special character")

        return self.success()

# ==========================================
# Welcome Screen
# ==========================================

class WelcomeScreen(Screen):
    """Welcome screen with introduction and prerequisites"""

    CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #welcome-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .status-box {
        border: solid $success;
        padding: 1;
        margin: 1 0;
        background: $success 20%;
    }

    .prereq-item {
        margin-left: 2;
        margin-bottom: 1;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="welcome-container"):
            yield Label("MISP Installation Wizard", id="title")
            yield Label("tKQB Enterprises Edition v2.0", id="subtitle")
            yield Static("💡 Tip: Press Ctrl+Q to quit at any time", classes="tip-text")

            # Check if MISP is installed
            misp_installed = check_misp_installed()

            if misp_installed:
                with Container(classes="status-box"):
                    yield Static("✓ MISP is currently installed and running", id="install-status")

                yield Static("\nWhat would you like to do?\n", classes="intro")

                with Horizontal(id="button-container"):
                    yield Button("🔄 Update MISP", id="btn-update", variant="primary")
                    yield Button("🗑️  Uninstall MISP", id="btn-uninstall", variant="error")
                    yield Button("Exit", id="btn-exit", variant="default")
            else:
                yield Static("Welcome to the MISP GUI Installer!\n", classes="intro")
                yield Static(
                    "This wizard will guide you through installing MISP "
                    "(Malware Information Sharing Platform) on your server.\n",
                    classes="intro"
                )

                yield Label("Prerequisites:", classes="prereq-header")
                yield Static("✓ Ubuntu 22.04 LTS or 24.04 LTS", classes="prereq-item")
                yield Static("✓ 8GB+ RAM recommended", classes="prereq-item")
                yield Static("✓ 50GB+ free disk space", classes="prereq-item")
                yield Static("✓ sudo privileges", classes="prereq-item")
                yield Static("✓ Internet connection", classes="prereq-item")

                with Horizontal(id="button-container"):
                    yield Button("Install MISP", id="btn-continue", variant="primary")
                    yield Button("Exit", id="btn-exit", variant="default")

        yield Footer()

    @on(Button.Pressed, "#btn-continue")
    def on_continue(self):
        """Move to network configuration screen"""
        self.app.push_screen("network")

    @on(Button.Pressed, "#btn-update")
    def on_update(self):
        """Move to update screen"""
        self.app.push_screen("update")

    @on(Button.Pressed, "#btn-uninstall")
    def on_uninstall(self):
        """Move to uninstall screen"""
        self.app.push_screen("uninstall")

    @on(Button.Pressed, "#btn-exit")
    def on_exit(self):
        """Exit the application"""
        self.app.exit()

# ==========================================
# Network Configuration Screen
# ==========================================

class NetworkScreen(Screen):
    """Network configuration screen"""

    CSS = """
    NetworkScreen {
        align: center middle;
    }

    #network-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
        color: $text;
    }

    .field-help {
        color: $text-muted;
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="network-container"):
            yield Label("Network Configuration", id="screen-title")
            yield Static("Step 1 of 5", classes="step-indicator")
            yield Static("💡 Tip: Press Ctrl+V to paste from clipboard | Ctrl+Q to quit", classes="field-help")

            yield Label("Server IP Address:", classes="field-label")
            yield Static("The IP address of this server", classes="field-help")
            yield Input(
                placeholder="e.g., 192.168.1.100",
                id="input-ip",
                validators=[IPAddressValidator()]
            )

            yield Label("Domain/FQDN:", classes="field-label")
            yield Static("Fully qualified domain name for MISP", classes="field-help")
            yield Input(
                placeholder="e.g., misp.company.com",
                id="input-domain",
                validators=[DomainValidator()]
            )

            yield Label("Admin Email:", classes="field-label")
            yield Static("Email for MISP admin account", classes="field-help")
            yield Input(
                placeholder="e.g., admin@company.com",
                id="input-email",
                validators=[EmailValidator()]
            )

            yield Label("Organization Name:", classes="field-label")
            yield Static("Your organization name", classes="field-help")
            yield Input(
                placeholder="e.g., Security Operations",
                id="input-org"
            )

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Next →", id="btn-next", variant="primary")

        yield Footer()

    def on_mount(self):
        """Auto-detect IP address on mount"""
        try:
            result = subprocess.run(
                ['hostname', '-I'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                ip = result.stdout.strip().split()[0]
                self.query_one("#input-ip", Input).value = ip
        except Exception:
            pass

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to welcome screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-next")
    def on_next(self):
        """Validate and move to security screen"""
        ip_input = self.query_one("#input-ip", Input)
        domain_input = self.query_one("#input-domain", Input)
        email_input = self.query_one("#input-email", Input)
        org_input = self.query_one("#input-org", Input)

        # Validate all fields
        if not ip_input.is_valid:
            self.notify("Please enter a valid IP address", severity="error")
            ip_input.focus()
            return

        if not domain_input.is_valid:
            self.notify("Please enter a valid domain", severity="error")
            domain_input.focus()
            return

        if not email_input.is_valid:
            self.notify("Please enter a valid email", severity="error")
            email_input.focus()
            return

        if not org_input.value:
            self.notify("Please enter an organization name", severity="error")
            org_input.focus()
            return

        # Save to app config
        self.app.config["server_ip"] = ip_input.value
        self.app.config["domain"] = domain_input.value
        self.app.config["admin_email"] = email_input.value
        self.app.config["admin_org"] = org_input.value

        self.app.push_screen("security")

# ==========================================
# Security Settings Screen
# ==========================================

class SecurityScreen(Screen):
    """Security settings screen for passwords"""

    CSS = """
    SecurityScreen {
        align: center middle;
    }

    #security-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
        color: $text;
    }

    .field-help {
        color: $text-muted;
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    #auto-generate-btn {
        margin-bottom: 2;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="security-container"):
            yield Label("Security Settings", id="screen-title")
            yield Static("Step 2 of 5 | Press Ctrl+Q to quit", classes="step-indicator")

            yield Static(
                "⚠️  Strong passwords are required for security.\n"
                "Passwords must be 12+ characters with uppercase, lowercase, number, and special character.",
                classes="security-warning"
            )

            yield Button("🎲 Auto-Generate All Passwords", id="auto-generate-btn", variant="success")

            yield Label("Admin Password:", classes="field-label")
            yield Static("Password for MISP web interface", classes="field-help")
            yield Input(
                placeholder="Enter strong password",
                id="input-admin-password",
                password=True,
                validators=[PasswordValidator()]
            )

            yield Label("MySQL Database Password:", classes="field-label")
            yield Static("Password for MySQL database", classes="field-help")
            yield Input(
                placeholder="Enter strong password",
                id="input-mysql-password",
                password=True,
                validators=[PasswordValidator()]
            )

            yield Label("GPG Passphrase:", classes="field-label")
            yield Static("Passphrase for GPG encryption", classes="field-help")
            yield Input(
                placeholder="Enter strong passphrase",
                id="input-gpg-passphrase",
                password=True,
                validators=[PasswordValidator()]
            )

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Next →", id="btn-next", variant="primary")

        yield Footer()

    @on(Button.Pressed, "#auto-generate-btn")
    def on_auto_generate(self):
        """Auto-generate strong passwords"""
        import secrets
        import string

        def generate_password(length=16):
            """Generate a strong random password"""
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(chars) for _ in range(length))
            # Ensure it has all required character types
            while not (any(c.isupper() for c in password) and
                      any(c.islower() for c in password) and
                      any(c.isdigit() for c in password) and
                      any(c in "!@#$%^&*" for c in password)):
                password = ''.join(secrets.choice(chars) for _ in range(length))
            return password

        self.query_one("#input-admin-password", Input).value = generate_password()
        self.query_one("#input-mysql-password", Input).value = generate_password()
        self.query_one("#input-gpg-passphrase", Input).value = generate_password(20)

        self.notify("✓ Passwords auto-generated successfully", severity="information")

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to network screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-next")
    def on_next(self):
        """Validate and move to environment screen"""
        admin_pw = self.query_one("#input-admin-password", Input)
        mysql_pw = self.query_one("#input-mysql-password", Input)
        gpg_pw = self.query_one("#input-gpg-passphrase", Input)

        # Validate all passwords
        if not admin_pw.is_valid:
            self.notify("Admin password does not meet requirements", severity="error")
            admin_pw.focus()
            return

        if not mysql_pw.is_valid:
            self.notify("MySQL password does not meet requirements", severity="error")
            mysql_pw.focus()
            return

        if not gpg_pw.is_valid:
            self.notify("GPG passphrase does not meet requirements", severity="error")
            gpg_pw.focus()
            return

        # Save to app config
        self.app.config["admin_password"] = admin_pw.value
        self.app.config["mysql_password"] = mysql_pw.value
        self.app.config["gpg_passphrase"] = gpg_pw.value

        self.app.push_screen("environment")

# ==========================================
# Environment Selection Screen
# ==========================================

class EnvironmentScreen(Screen):
    """Environment selection screen"""

    CSS = """
    EnvironmentScreen {
        align: center middle;
    }

    #environment-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    RadioSet {
        margin: 2;
    }

    .env-description {
        margin-left: 4;
        color: $text-muted;
        margin-bottom: 1;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="environment-container"):
            yield Label("Environment Selection", id="screen-title")
            yield Static("Step 3 of 5 | Press Ctrl+Q to quit", classes="step-indicator")

            yield Static("Select the deployment environment:")

            with RadioSet(id="environment-radio"):
                yield RadioButton("Production (Recommended)", value="production", id="env-production")
                yield Static("Optimized performance, security hardened, minimal logging", classes="env-description")

                yield RadioButton("Staging", value="staging", id="env-staging")
                yield Static("Production-like configuration for testing", classes="env-description")

                yield RadioButton("Development", value="development", id="env-development")
                yield Static("Debug enabled, verbose logging, relaxed security", classes="env-description")

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Next →", id="btn-next", variant="primary")

        yield Footer()

    def on_mount(self):
        """Set default to production"""
        self.query_one("#env-production", RadioButton).value = True

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to security screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-next")
    def on_next(self):
        """Move to features screen"""
        radio_set = self.query_one("#environment-radio", RadioSet)

        if radio_set.pressed_button:
            # Get the button ID and extract environment name
            button_id = radio_set.pressed_button.id
            if button_id == "env-production":
                self.app.config["environment"] = "production"
            elif button_id == "env-staging":
                self.app.config["environment"] = "staging"
            elif button_id == "env-development":
                self.app.config["environment"] = "development"
            else:
                self.app.config["environment"] = "production"  # default

            self.app.push_screen("features")
        else:
            self.notify("Please select an environment", severity="error")

# ==========================================
# Enhanced Features Screen
# ==========================================

class FeaturesScreen(Screen):
    """Enhanced features configuration screen"""

    CSS = """
    FeaturesScreen {
        align: center middle;
    }

    #features-container {
        width: 90;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .feature-section {
        border: solid $primary-lighten-2;
        padding: 1;
        margin: 1 0;
        background: $primary 10%;
    }

    .section-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .feature-description {
        color: $text-muted;
        margin-left: 2;
        margin-bottom: 0;
    }

    Checkbox {
        margin: 0 2;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="features-container"):
            yield Label("Enhanced Features Configuration", id="screen-title")
            yield Static("Step 4 of 6 | Press Ctrl+Q to quit", classes="step-indicator")

            yield Static(
                "📦 Select the enhanced features to install and configure.\n"
                "💡 All features can be enabled/disabled later.\n",
                classes="feature-intro"
            )

            # Industry-Specific Configuration
            with Container(classes="feature-section"):
                yield Label("🏭 Industry-Specific Configuration", classes="section-title")
                yield Checkbox("Configure for NERC CIP Compliance (Energy Sector)", id="feat-nerc-cip")
                yield Static("ICS/SCADA threat feeds, compliance settings, regulatory requirements", classes="feature-description")
                yield Checkbox("Configure for Critical Infrastructure / Utilities Sector", id="feat-utilities")
                yield Static("Water, power, gas sector threats and CISA alerts", classes="feature-description")

            # Threat Intelligence Feeds
            with Container(classes="feature-section"):
                yield Label("🌐 Threat Intelligence Feeds", classes="section-title")
                yield Checkbox("Enable Core Threat Intel Feeds", id="feat-threat-feeds", value=True)
                yield Static("CIRCL, Abuse.ch, OpenPhish, Blocklist.de", classes="feature-description")
                yield Checkbox("Enable ICS/OT-Specific Threat Feeds", id="feat-ics-feeds")
                yield Static("Industrial control systems and operational technology threats", classes="feature-description")

            # Security News & Alerts
            with Container(classes="feature-section"):
                yield Label("📰 Security News & Alerts", classes="section-title")
                yield Checkbox("Populate Security News Dashboard", id="feat-news", value=True)
                yield Static("Latest cybersecurity news from trusted sources", classes="feature-description")
                yield Checkbox("Add NERC CIP News Feeds", id="feat-nerc-news")
                yield Static("Energy sector security news and compliance updates", classes="feature-description")

            # Automated Maintenance
            with Container(classes="feature-section"):
                yield Label("⚙️ Automated Maintenance & Updates", classes="section-title")
                yield Checkbox("Setup Daily Maintenance Tasks", id="feat-daily-maintenance", value=True)
                yield Static("Database optimization, cache clearing, log rotation", classes="feature-description")
                yield Checkbox("Setup Weekly Maintenance Tasks", id="feat-weekly-maintenance", value=True)
                yield Static("Feed updates, taxonomy updates, system cleanup", classes="feature-description")
                yield Checkbox("Setup Automated Feed Fetching (Cron)", id="feat-feed-cron", value=True)
                yield Static("Automatically fetch threat intel feeds daily", classes="feature-description")
                yield Checkbox("Setup Automated News Updates (Cron)", id="feat-news-cron")
                yield Static("Daily security news dashboard updates", classes="feature-description")
                yield Checkbox("Setup Automated Backups", id="feat-backup-cron", value=True)
                yield Static("Daily automated backups with 30-day retention", classes="feature-description")

            # Advanced Configuration
            with Container(classes="feature-section"):
                yield Label("🔧 Advanced Configuration", classes="section-title")
                yield Checkbox("Enable All Default Feeds (70+ feeds)", id="feat-enable-feeds")
                yield Static("Activate all built-in MISP feed sources", classes="feature-description")
                yield Checkbox("Configure MISP for Production Best Practices", id="feat-production-config", value=True)
                yield Static("Security hardening, performance tuning, recommended settings", classes="feature-description")

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Select All", id="btn-select-all", variant="default")
                yield Button("Deselect All", id="btn-deselect-all", variant="default")
                yield Button("Next →", id="btn-next", variant="primary")

        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to environment screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-select-all")
    def on_select_all(self):
        """Select all feature checkboxes"""
        for checkbox in self.query(Checkbox):
            checkbox.value = True
        self.notify("✓ All features selected", severity="information")

    @on(Button.Pressed, "#btn-deselect-all")
    def on_deselect_all(self):
        """Deselect all feature checkboxes"""
        for checkbox in self.query(Checkbox):
            checkbox.value = False
        self.notify("✓ All features deselected", severity="information")

    @on(Button.Pressed, "#btn-next")
    def on_next(self):
        """Save feature selections and move to review screen"""
        # Save all checkbox states to config
        self.app.config["features"] = {
            "nerc_cip": self.query_one("#feat-nerc-cip", Checkbox).value,
            "utilities_sector": self.query_one("#feat-utilities", Checkbox).value,
            "threat_feeds": self.query_one("#feat-threat-feeds", Checkbox).value,
            "ics_feeds": self.query_one("#feat-ics-feeds", Checkbox).value,
            "security_news": self.query_one("#feat-news", Checkbox).value,
            "nerc_news": self.query_one("#feat-nerc-news", Checkbox).value,
            "daily_maintenance": self.query_one("#feat-daily-maintenance", Checkbox).value,
            "weekly_maintenance": self.query_one("#feat-weekly-maintenance", Checkbox).value,
            "feed_cron": self.query_one("#feat-feed-cron", Checkbox).value,
            "news_cron": self.query_one("#feat-news-cron", Checkbox).value,
            "backup_cron": self.query_one("#feat-backup-cron", Checkbox).value,
            "enable_all_feeds": self.query_one("#feat-enable-feeds", Checkbox).value,
            "production_best_practices": self.query_one("#feat-production-config", Checkbox).value,
        }

        # Count selected features
        selected_count = sum(1 for v in self.app.config["features"].values() if v)

        self.notify(f"✓ {selected_count} features selected", severity="information")
        self.app.push_screen("review")

# ==========================================
# Review & Confirm Screen
# ==========================================

class ReviewScreen(Screen):
    """Review and confirm configuration"""

    CSS = """
    ReviewScreen {
        align: center middle;
    }

    #review-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .config-section {
        margin-top: 1;
        margin-bottom: 1;
    }

    .config-label {
        color: $accent;
        text-style: bold;
    }

    .config-value {
        color: $text;
        margin-left: 2;
    }

    #warning-box {
        border: solid $warning;
        padding: 1;
        margin: 2 0;
        background: $warning 20%;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="review-container"):
            yield Label("Review Configuration", id="screen-title")
            yield Static("Step 5 of 6 | Press Ctrl+Q to quit", classes="step-indicator")

            yield Static("Please review your configuration before installation:\n")

            with Container(classes="config-section"):
                yield Label("Network Configuration", classes="config-label")
                yield Static(f"Server IP: {self.app.config.get('server_ip', 'N/A')}", classes="config-value")
                yield Static(f"Domain: {self.app.config.get('domain', 'N/A')}", classes="config-value")
                yield Static(f"Admin Email: {self.app.config.get('admin_email', 'N/A')}", classes="config-value")
                yield Static(f"Organization: {self.app.config.get('admin_org', 'N/A')}", classes="config-value")

            with Container(classes="config-section"):
                yield Label("Security", classes="config-label")
                yield Static("Admin Password: ••••••••", classes="config-value")
                yield Static("MySQL Password: ••••••••", classes="config-value")
                yield Static("GPG Passphrase: ••••••••", classes="config-value")

            with Container(classes="config-section"):
                yield Label("Environment", classes="config-label")
                yield Static(f"Type: {self.app.config.get('environment', 'N/A').title()}", classes="config-value")

            # Show selected features
            features = self.app.config.get('features', {})
            selected_features = [k for k, v in features.items() if v]

            with Container(classes="config-section"):
                yield Label("Enhanced Features", classes="config-label")
                if selected_features:
                    feature_names = {
                        'nerc_cip': 'NERC CIP Compliance',
                        'utilities_sector': 'Utilities Sector Configuration',
                        'threat_feeds': 'Core Threat Intel Feeds',
                        'ics_feeds': 'ICS/OT Threat Feeds',
                        'security_news': 'Security News Dashboard',
                        'nerc_news': 'NERC CIP News Feeds',
                        'daily_maintenance': 'Daily Maintenance',
                        'weekly_maintenance': 'Weekly Maintenance',
                        'feed_cron': 'Automated Feed Fetching',
                        'news_cron': 'Automated News Updates',
                        'backup_cron': 'Automated Backups',
                        'enable_all_feeds': 'Enable All Default Feeds',
                        'production_best_practices': 'Production Best Practices'
                    }
                    for feature_key in selected_features:
                        feature_name = feature_names.get(feature_key, feature_key.replace('_', ' ').title())
                        yield Static(f"✓ {feature_name}", classes="config-value")
                else:
                    yield Static("(No enhanced features selected)", classes="config-value")

            with Container(id="warning-box"):
                yield Static(
                    "⚠️  The installation will now begin. This process takes 15-30 minutes.\n"
                    "Your system will download and configure MISP components.",
                    classes="warning-text"
                )

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Save Config", id="btn-save", variant="default")
                yield Button("Save & Exit", id="btn-save-exit", variant="default")
                yield Button("Install MISP", id="btn-install", variant="success")

        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to environment screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-save")
    def on_save(self):
        """Save configuration to file (stays in app)"""
        config_file = self.save_config()
        config_file_abs = Path(config_file).resolve()

        message = (
            f"✓ Configuration saved successfully!\n\n"
            f"📁 Location: {config_file_abs}\n\n"
            f"📋 To use this configuration:\n"
            f"   python3 misp-install.py --config {config_file} --non-interactive\n\n"
            f"💡 The config file contains all your settings and can be reused for automated deployments."
        )
        self.notify(message, severity="information", timeout=10)

    @on(Button.Pressed, "#btn-save-exit")
    def on_save_exit(self):
        """Save configuration and exit application"""
        config_file = self.save_config()
        config_file_abs = Path(config_file).resolve()

        # Store message for printing after app exits
        self.app.exit_message = {
            "type": "save_exit",
            "config_file": str(config_file),
            "config_file_abs": str(config_file_abs)
        }

        # Show brief in-app notification
        message = (
            f"✓ Configuration saved to:\n{config_file_abs}\n\n"
            f"Exiting... (check terminal for usage instructions)"
        )
        self.notify(message, severity="information", timeout=2)

        # Schedule exit after brief delay to show notification
        self.set_timer(0.5, self.app.exit)

    @on(Button.Pressed, "#btn-install")
    def on_install(self):
        """Save config and start installation"""
        config_file = self.save_config()
        self.app.config["config_file"] = config_file
        self.app.push_screen("install")

    def save_config(self) -> str:
        """Save configuration to JSON file"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file = config_dir / f"misp-gui-config-{timestamp}.json"

        config_data = {
            "server_ip": self.app.config.get("server_ip"),
            "domain": self.app.config.get("domain"),
            "admin_email": self.app.config.get("admin_email"),
            "admin_org": self.app.config.get("admin_org"),
            "admin_password": self.app.config.get("admin_password"),
            "mysql_password": self.app.config.get("mysql_password"),
            "gpg_passphrase": self.app.config.get("gpg_passphrase"),
            "environment": self.app.config.get("environment", "production"),
            "features": self.app.config.get("features", {})
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Set file permissions to 600 (owner read/write only)
        config_file.chmod(0o600)

        return str(config_file)

# ==========================================
# Update MISP Screen
# ==========================================

class UpdateScreen(Screen):
    """Update MISP screen"""

    CSS = """
    UpdateScreen {
        align: center middle;
    }

    #update-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .update-option {
        margin: 1 0;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="update-container"):
            yield Label("Update MISP", id="screen-title")
            yield Static("Press Ctrl+Q to quit", classes="step-indicator")

            yield Static(
                "Select which components to update:\n",
                classes="intro"
            )

            yield Checkbox("Update MISP Core", id="update-core", value=True)
            yield Static("Updates MISP application to latest version", classes="update-option")

            yield Checkbox("Update Docker Containers", id="update-containers", value=True)
            yield Static("Pulls latest Docker images", classes="update-option")

            yield Checkbox("Update Feeds", id="update-feeds", value=True)
            yield Static("Fetches latest threat intelligence feeds", classes="update-option")

            yield Checkbox("Update Taxonomies & Galaxies", id="update-taxonomies", value=True)
            yield Static("Updates MISP taxonomies and galaxy clusters", classes="update-option")

            yield Checkbox("Update System Packages", id="update-system")
            yield Static("Updates underlying system packages (apt update/upgrade)", classes="update-option")

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Start Update", id="btn-update", variant="primary")

        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to welcome screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-update")
    def on_update(self):
        """Start update process"""
        # Collect selected options
        update_options = {
            "core": self.query_one("#update-core", Checkbox).value,
            "containers": self.query_one("#update-containers", Checkbox).value,
            "feeds": self.query_one("#update-feeds", Checkbox).value,
            "taxonomies": self.query_one("#update-taxonomies", Checkbox).value,
            "system": self.query_one("#update-system", Checkbox).value,
        }

        self.app.config["update_options"] = update_options

        # Confirm before starting
        if not any(update_options.values()):
            self.notify("Please select at least one update option", severity="error")
            return

        # Push to update progress screen
        self.app.push_screen("update_progress")

# ==========================================
# Uninstall MISP Screen
# ==========================================

class UninstallScreen(Screen):
    """Uninstall MISP screen"""

    CSS = """
    UninstallScreen {
        align: center middle;
    }

    #uninstall-container {
        width: 80;
        height: auto;
        border: solid $error;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 2;
    }

    .warning-box {
        border: solid $warning;
        padding: 1;
        margin: 2 0;
        background: $warning 20%;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="uninstall-container"):
            yield Label("Uninstall MISP", id="screen-title")
            yield Static("Press Ctrl+Q to quit", classes="step-indicator")

            with Container(classes="warning-box"):
                yield Static(
                    "⚠️  WARNING: This will remove MISP from your system!\n\n"
                    "The following will be removed:\n"
                    "• Docker containers\n"
                    "• MISP configuration files\n"
                    "• Databases and data\n\n"
                    "Your backups in ~/misp-backups will be preserved.",
                    classes="warning-text"
                )

            yield Static("\nUninstall options:\n")

            yield Checkbox("Keep backups", id="keep-backups", value=True)
            yield Static("Preserve ~/misp-backups directory", classes="option-desc")

            yield Checkbox("Keep logs", id="keep-logs", value=True)
            yield Static("Preserve /opt/misp/logs directory", classes="option-desc")

            yield Checkbox("Remove Docker volumes", id="remove-volumes")
            yield Static("Remove Docker volumes (WARNING: deletes all data)", classes="option-desc")

            yield Static("\n")
            yield Checkbox("I understand and want to uninstall MISP", id="confirm-uninstall")

            with Horizontal(id="button-container"):
                yield Button("← Cancel", id="btn-cancel", variant="default")
                yield Button("Uninstall MISP", id="btn-uninstall", variant="error")

        yield Footer()

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self):
        """Cancel and go back"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-uninstall")
    def on_uninstall(self):
        """Confirm and uninstall"""
        confirm = self.query_one("#confirm-uninstall", Checkbox).value

        if not confirm:
            self.notify("Please check the confirmation box to proceed", severity="error")
            return

        # Collect options
        uninstall_options = {
            "keep_backups": self.query_one("#keep-backups", Checkbox).value,
            "keep_logs": self.query_one("#keep-logs", Checkbox).value,
            "remove_volumes": self.query_one("#remove-volumes", Checkbox).value,
        }

        self.app.config["uninstall_options"] = uninstall_options

        # Push to uninstall progress screen
        self.app.push_screen("uninstall_progress")

# ==========================================
# Update Progress Screen
# ==========================================

class UpdateProgressScreen(Screen):
    """Update progress screen with live output"""

    CSS = """
    UpdateProgressScreen {
        align: center middle;
    }

    #update-progress-container {
        width: 90;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    #status-text {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }

    #log-container {
        height: 25;
        border: solid $primary;
        padding: 1;
        margin: 2 0;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="update-progress-container"):
            yield Label("Updating MISP", id="screen-title")
            yield Static("Starting update process...", id="status-text")

            yield Label("Update Log:", classes="log-header")
            with ScrollableContainer(id="log-container"):
                yield Static("", id="log-output")

            with Horizontal(id="button-container"):
                yield Button("Close", id="btn-close", variant="default", disabled=True)

        yield Footer()

    def on_mount(self):
        """Start update when screen mounts"""
        self.run_update()

    def run_update(self):
        """Execute misp-update.py script"""
        import threading

        def update_thread():
            try:
                self.update_status("Running MISP update script...")

                # Get the directory where the GUI script is located
                script_dir = Path(__file__).parent

                # Build command based on options
                cmd = ['sudo', 'python3', 'scripts/misp-update.py']

                # Run the update script from project root
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=str(script_dir)
                )

                # Stream output
                for line in process.stdout:
                    self.append_log(line.rstrip())

                process.wait()

                if process.returncode == 0:
                    self.update_status("✓ Update completed successfully!")
                    self.append_log("\n✓ MISP has been updated successfully")
                else:
                    self.update_status("✗ Update failed")
                    self.append_log(f"\n✗ Update failed with exit code {process.returncode}")

            except Exception as e:
                self.update_status("✗ Update error")
                self.append_log(f"\n✗ Error: {str(e)}")

            finally:
                # Enable close button using Textual's thread-safe method
                def enable_button():
                    try:
                        btn = self.query_one("#btn-close", Button)
                        btn.disabled = False
                    except:
                        pass
                self.call_from_thread(enable_button)

        # Start update in background thread
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()

    def update_status(self, message: str):
        """Update status text"""
        try:
            self.query_one("#status-text", Static).update(message)
        except:
            pass

    def append_log(self, message: str):
        """Append message to log output"""
        try:
            log_widget = self.query_one("#log-output", Static)
            current = str(log_widget.renderable)
            log_widget.update(current + "\n" + message if current else message)
        except:
            pass

    @on(Button.Pressed, "#btn-close")
    def on_close(self):
        """Close and return to welcome"""
        self.app.pop_screen()

# ==========================================
# Uninstall Progress Screen
# ==========================================

class UninstallProgressScreen(Screen):
    """Uninstall progress screen with live output"""

    CSS = """
    UninstallProgressScreen {
        align: center middle;
    }

    #uninstall-progress-container {
        width: 90;
        height: auto;
        border: solid $error;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 2;
    }

    #status-text {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }

    #log-container {
        height: 25;
        border: solid $primary;
        padding: 1;
        margin: 2 0;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="uninstall-progress-container"):
            yield Label("Uninstalling MISP", id="screen-title")
            yield Static("Starting uninstall process...", id="status-text")

            yield Label("Uninstall Log:", classes="log-header")
            with ScrollableContainer(id="log-container"):
                yield Static("", id="log-output")

            with Horizontal(id="button-container"):
                yield Button("Close", id="btn-close", variant="default", disabled=True)

        yield Footer()

    def on_mount(self):
        """Start uninstall when screen mounts"""
        self.run_uninstall()

    def run_uninstall(self):
        """Execute uninstall-misp.py script"""
        import threading

        def uninstall_thread():
            try:
                self.update_status("Running MISP uninstall script...")

                # Get the directory where the GUI script is located
                script_dir = Path(__file__).parent

                # Build command based on options
                cmd = ['sudo', 'python3', 'scripts/uninstall-misp.py', '--force']

                options = self.app.config.get("uninstall_options", {})
                if not options.get("keep_logs", True):
                    cmd.append('--remove-logs')

                # Run the uninstall script from project root
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=str(script_dir)
                )

                # Stream output
                for line in process.stdout:
                    self.append_log(line.rstrip())

                process.wait()

                if process.returncode == 0:
                    self.update_status("✓ Uninstall completed - Running health checks...")
                    self.append_log("\n✓ MISP uninstall script completed")
                    self.append_log("\n" + "=" * 50)
                    self.append_log("Running post-uninstall health checks...")
                    self.append_log("=" * 50)

                    # Run health checks
                    health_results = verify_uninstall_complete()

                    self.append_log("")
                    for detail in health_results['details']:
                        self.append_log(detail)

                    self.append_log("")
                    self.append_log("=" * 50)
                    if health_results['checks']['all_clean']:
                        self.update_status("✓ Uninstall completed successfully - System is clean!")
                        self.append_log("✓ All health checks passed - MISP fully removed")
                    else:
                        self.update_status("⚠️  Uninstall completed with warnings")
                        self.append_log("⚠️  Some components may require manual cleanup")
                    self.append_log("=" * 50)
                else:
                    self.update_status("✗ Uninstall failed")
                    self.append_log(f"\n✗ Uninstall failed with exit code {process.returncode}")

            except Exception as e:
                self.update_status("✗ Uninstall error")
                self.append_log(f"\n✗ Error: {str(e)}")

            finally:
                # Enable close button using Textual's thread-safe method
                def enable_button():
                    try:
                        btn = self.query_one("#btn-close", Button)
                        btn.disabled = False
                    except:
                        pass
                self.call_from_thread(enable_button)

        # Start uninstall in background thread
        thread = threading.Thread(target=uninstall_thread, daemon=True)
        thread.start()

    def update_status(self, message: str):
        """Update status text"""
        try:
            self.query_one("#status-text", Static).update(message)
        except:
            pass

    def append_log(self, message: str):
        """Append message to log output"""
        try:
            log_widget = self.query_one("#log-output", Static)
            current = str(log_widget.renderable)
            log_widget.update(current + "\n" + message if current else message)
        except:
            pass

    @on(Button.Pressed, "#btn-close")
    def on_close(self):
        """Close and return to welcome"""
        self.app.pop_screen()

# ==========================================
# Installation Progress Screen
# ==========================================

class InstallScreen(Screen):
    """Installation progress screen"""

    CSS = """
    InstallScreen {
        align: center middle;
    }

    #install-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 2;
    }

    #screen-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    #progress-bar {
        margin: 2 0;
    }

    #status-text {
        text-align: center;
        color: $text-muted;
        margin: 1 0;
    }

    #log-container {
        height: 20;
        border: solid $primary;
        padding: 1;
        margin: 2 0;
    }

    #button-container {
        dock: bottom;
        height: 3;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="install-container"):
            yield Label("Installing MISP", id="screen-title")
            yield Static("Step 6 of 6 - Please wait... | Press Ctrl+Q to quit", classes="step-indicator")

            yield ProgressBar(total=100, show_eta=False, id="progress-bar")
            yield Static("Initializing installation...", id="status-text")

            yield Label("Installation Log:", classes="log-header")
            with ScrollableContainer(id="log-container"):
                yield Static("", id="log-output")

            with Horizontal(id="button-container"):
                yield Button("View Full Logs", id="btn-logs", variant="default", disabled=True)
                yield Button("Exit", id="btn-exit", variant="default", disabled=True)

        yield Footer()

    def on_mount(self):
        """Start installation when screen mounts"""
        self.run_installation()

    def run_installation(self):
        """Run the actual installation (placeholder for now)"""
        # TODO: Implement actual installation by calling misp-install.py
        # For now, just show a demo
        self.query_one("#status-text", Static).update(
            "⚠️  Demo Mode: Installation not implemented yet\n"
            "In production, this would run: python3 misp-install.py --config [config-file]"
        )
        self.query_one("#log-output", Static).update(
            "Installation would proceed with the following phases:\n"
            "1. Installing dependencies\n"
            "2. Setting up Docker\n"
            "3. Cloning MISP repository\n"
            "4. Configuring MISP\n"
            "5. Generating SSL certificate\n"
            "6. Starting Docker containers\n"
            "7. Initializing MISP\n\n"
            f"Config file: {self.app.config.get('config_file', 'N/A')}\n\n"
            "To complete the implementation, integrate with misp-install.py backend."
        )

        # Enable exit button
        self.query_one("#btn-exit", Button).disabled = False

    @on(Button.Pressed, "#btn-exit")
    def on_exit(self):
        """Exit the application"""
        self.app.exit()

# ==========================================
# Main Application
# ==========================================

class MISPInstallerApp(App):
    """Main MISP Installer application"""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    SCREENS = {
        "welcome": WelcomeScreen,
        "network": NetworkScreen,
        "security": SecurityScreen,
        "environment": EnvironmentScreen,
        "features": FeaturesScreen,
        "review": ReviewScreen,
        "install": InstallScreen,
        "update": UpdateScreen,
        "uninstall": UninstallScreen,
        "update_progress": UpdateProgressScreen,
        "uninstall_progress": UninstallProgressScreen
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("ctrl+v", "paste_clipboard", "Paste"),
    ]

    def __init__(self, load_config=None, save_only=False):
        super().__init__()
        self.config = {}
        self.load_config_file = load_config
        self.save_only = save_only
        self.exit_message = None  # Store message to print after exit

    def on_mount(self):
        """Initialize the application"""
        self.title = "MISP Installer"
        self.sub_title = "tKQB Enterprises Edition"

        # Load config if provided
        if self.load_config_file:
            self.load_config(self.load_config_file)

        # Push welcome screen
        self.push_screen("welcome")

    def load_config(self, config_file: str):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            self.notify(f"✓ Loaded configuration from {config_file}", severity="information")
        except Exception as e:
            self.notify(f"⚠️  Could not load config: {e}", severity="warning")

    def action_toggle_dark(self):
        """Toggle dark mode"""
        self.dark = not self.dark

    def action_paste_clipboard(self):
        """Paste from clipboard into focused Input widget"""
        if not CLIPBOARD_AVAILABLE:
            self.notify("⚠️  Clipboard not available - install pyperclip", severity="warning")
            return

        try:
            # Get clipboard content
            clipboard_text = pyperclip.paste()

            # Get the currently focused widget
            focused = self.focused

            # If it's an Input widget, insert the clipboard text
            if isinstance(focused, Input):
                # Get current value and cursor position
                current_value = focused.value
                cursor_pos = focused.cursor_position

                # Insert clipboard text at cursor position
                new_value = current_value[:cursor_pos] + clipboard_text + current_value[cursor_pos:]
                focused.value = new_value

                # Move cursor to end of pasted text
                focused.cursor_position = cursor_pos + len(clipboard_text)

                self.notify("✓ Pasted from clipboard", severity="information")
            else:
                self.notify("⚠️  Focus an input field first", severity="warning")

        except Exception as e:
            self.notify(f"⚠️  Paste failed: {e}", severity="error")

# ==========================================
# Main Entry Point
# ==========================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MISP GUI Installer - Modern graphical installer for MISP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI installer
  python3 misp-install-gui.py

  # Load existing configuration
  python3 misp-install-gui.py --load config/misp-config.json

  # Save config without installing
  python3 misp-install-gui.py --save-only

  # Run in web browser
  textual serve misp-install-gui.py
        """
    )

    parser.add_argument('--load', metavar='FILE', help='Load configuration from file')
    parser.add_argument('--save-only', action='store_true', help='Save configuration without installing')
    parser.add_argument('--version', action='version', version='MISP GUI Installer v2.0')

    args = parser.parse_args()

    # Run the application
    app = MISPInstallerApp(load_config=args.load, save_only=args.save_only)
    app.run()

    # Print exit message if one was set (after TUI has fully exited)
    if app.exit_message and app.exit_message.get("type") == "save_exit":
        config_file = app.exit_message.get("config_file")
        config_file_abs = app.exit_message.get("config_file_abs")

        print("")
        print("=" * 80)
        print("✓ Configuration saved successfully!")
        print("")
        print(f"📁 Location: {config_file_abs}")
        print("")
        print("📋 To use this configuration:")
        print(f"   python3 misp-install.py --config {config_file} --non-interactive")
        print("")
        print("💡 The config file contains all your settings and can be reused for")
        print("   automated deployments.")
        print("=" * 80)
        print("")

if __name__ == "__main__":
    main()
