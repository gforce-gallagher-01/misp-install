#!/bin/bash
#
# MISP GUI Installer - Bootstrap Script
# Automatically installs all dependencies and sets up PATH
#
# Usage: ./install-gui.sh
#
# This script handles everything automatically:
# - Installs system dependencies (xclip, pipx)
# - Configures PATH automatically
# - Installs MISP GUI Installer
# - Verifies installation
# - Provides clear next steps
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==================================================${NC}"
    echo ""
}

print_step() {
    echo ""
    echo -e "${GREEN}$1${NC}"
    echo "--------------------------------------------------"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header "MISP GUI Installer - Automatic Setup"

# Check if running on Ubuntu
if [ -f /etc/os-release ]; then
    . /etc/os-release
    print_success "Detected: $PRETTY_NAME"

    # Check Ubuntu version
    if [[ "$VERSION_ID" < "22.04" ]]; then
        print_warning "Ubuntu 22.04+ recommended (you have $VERSION_ID)"
    fi
else
    print_warning "Could not detect OS version"
fi

print_step "Step 1: Installing system dependencies"

# Check if xclip is installed
if ! command -v xclip &> /dev/null; then
    echo "Installing xclip (for clipboard support)..."
    sudo apt update -qq
    sudo apt install -y xclip
    print_success "xclip installed"
else
    print_success "xclip already installed"
fi

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "Installing pipx..."
    sudo apt install -y pipx
    print_success "pipx installed"
else
    print_success "pipx already installed"
fi

print_step "Step 2: Setting up PATH"

# Check if PATH is already configured
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to PATH..."
    pipx ensurepath --force

    # Also add to current shell's PATH immediately
    export PATH="$HOME/.local/bin:$PATH"

    print_success "PATH configured"
    print_warning "Shell config updated (bashrc/profile)"
    NEED_SHELL_RESTART=true
else
    print_success "PATH already configured"
    NEED_SHELL_RESTART=false
fi

print_step "Step 3: Installing MISP GUI Installer"

# Force complete removal of old version (including venv)
if pipx list 2>/dev/null | grep -q "misp-installer-gui"; then
    echo "Removing old version completely..."
    pipx uninstall misp-installer-gui 2>/dev/null || true

    # Remove venv directory if it exists (try both possible locations)
    if [ -d "$HOME/.local/pipx/venvs/misp-installer-gui" ]; then
        rm -rf "$HOME/.local/pipx/venvs/misp-installer-gui"
    fi
    if [ -d "$HOME/.local/share/pipx/venvs/misp-installer-gui" ]; then
        rm -rf "$HOME/.local/share/pipx/venvs/misp-installer-gui"
    fi

    print_success "Old version removed"
fi

# Install from current directory with GUI dependencies (fresh install)
echo "Installing misp-installer-gui from current directory..."
if pipx install ".[gui]"; then
    print_success "MISP GUI Installer installed"
else
    print_error "Installation failed"
    exit 1
fi

print_step "Step 4: Verifying installation"

# Test that the command works (pipx handles dependencies automatically)
if "$HOME/.local/bin/misp-install-gui" --version &>/dev/null || command -v misp-install-gui &>/dev/null && misp-install-gui --version &>/dev/null; then
    print_success "Installation verified - GUI installer is ready"
else
    print_error "Installation verification failed"
    exit 1
fi

print_header "✓ Installation Complete!"

if [ "$NEED_SHELL_RESTART" = true ]; then
    echo -e "${YELLOW}IMPORTANT:${NC} PATH was updated for future shells"
    echo ""
    echo -e "${GREEN}The GUI installer is ready to use RIGHT NOW!${NC}"
    echo ""
    echo "Run it with:"
    echo -e "  ${BLUE}misp-install-gui${NC}"
    echo ""
    echo -e "For ${YELLOW}future terminal sessions${NC}, the command will be globally available."
    echo "If it's not found, restart your shell:"
    echo "  exec bash"
    echo ""
else
    echo -e "${GREEN}The GUI installer is ready to use!${NC}"
    echo ""
    echo "Run it with:"
    echo -e "  ${BLUE}misp-install-gui${NC}"
    echo ""
fi

echo "Other options:"
echo "  python3 misp_install_gui.py     # Run directly without installing"
echo "  cat docs/GUI_INSTALLER.md       # Read the documentation"
echo ""

# Try to run it automatically if PATH is set
if [ "$NEED_SHELL_RESTART" = false ] && command -v misp-install-gui &>/dev/null; then
    echo -e "${GREEN}Would you like to launch the GUI installer now? (y/n)${NC}"
    read -r -n 1 response
    echo ""
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Launching GUI installer..."
        misp-install-gui
    fi
else
    # PATH was just updated, use full path
    echo -e "${GREEN}Would you like to launch the GUI installer now? (y/n)${NC}"
    read -r -n 1 response
    echo ""
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Launching GUI installer..."
        "$HOME/.local/bin/misp-install-gui" || python3 misp_install_gui.py
    fi
fi
