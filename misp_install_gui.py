#!/usr/bin/env python3
"""
MISP GUI Installer
tKQB Enterprises Edition
Version: 1.0

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
except ImportError:
    print("❌ Textual framework not installed")
    print("📦 Install with: pip install textual textual-dev")
    sys.exit(1)

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
            yield Label("tKQB Enterprises Edition v1.0", id="subtitle")

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
                yield Button("Continue", id="btn-continue", variant="primary")
                yield Button("Exit", id="btn-exit", variant="default")

        yield Footer()

    @on(Button.Pressed, "#btn-continue")
    def on_continue(self):
        """Move to network configuration screen"""
        self.app.push_screen("network")

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
            yield Static("💡 Tip: Use Ctrl+Shift+V or Right-Click to paste", classes="field-help")

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
            yield Static("Step 2 of 5", classes="step-indicator")

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
            yield Static("Step 3 of 5", classes="step-indicator")

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
        """Move to review screen"""
        radio_set = self.query_one("#environment-radio", RadioSet)

        if radio_set.pressed_button:
            self.app.config["environment"] = radio_set.pressed_button.value
            self.app.push_screen("review")
        else:
            self.notify("Please select an environment", severity="error")

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
            yield Static("Step 4 of 5", classes="step-indicator")

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

            with Container(id="warning-box"):
                yield Static(
                    "⚠️  The installation will now begin. This process takes 15-30 minutes.\n"
                    "Your system will download and configure MISP components.",
                    classes="warning-text"
                )

            with Horizontal(id="button-container"):
                yield Button("← Back", id="btn-back", variant="default")
                yield Button("Save Config Only", id="btn-save", variant="default")
                yield Button("Install MISP", id="btn-install", variant="success")

        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def on_back(self):
        """Go back to environment screen"""
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-save")
    def on_save(self):
        """Save configuration to file without installing"""
        self.save_config()
        self.notify("✓ Configuration saved successfully", severity="information")

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
            "environment": self.app.config.get("environment", "production")
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Set file permissions to 600 (owner read/write only)
        config_file.chmod(0o600)

        return str(config_file)

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
            yield Static("Step 5 of 5 - Please wait...", classes="step-indicator")

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
        "review": ReviewScreen,
        "install": InstallScreen
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("ctrl+v", "paste", "Paste (Ctrl+Shift+V)"),
    ]

    def __init__(self, load_config=None, save_only=False):
        super().__init__()
        self.config = {}
        self.load_config_file = load_config
        self.save_only = save_only

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
    parser.add_argument('--version', action='version', version='MISP GUI Installer v1.0')

    args = parser.parse_args()

    # Run the application
    app = MISPInstallerApp(load_config=args.load, save_only=args.save_only)
    app.run()

if __name__ == "__main__":
    main()
