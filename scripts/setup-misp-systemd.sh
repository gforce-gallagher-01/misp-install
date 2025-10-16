#!/bin/bash
# MISP Systemd Service Setup Script for Ubuntu 24.04
# This script installs and configures the MISP systemd service for automatic startup
# with comprehensive security hardening
#
# Usage:
#   sudo bash scripts/setup-misp-systemd.sh
#   sudo bash scripts/setup-misp-systemd.sh --dry-run
#   sudo bash scripts/setup-misp-systemd.sh --uninstall

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="${SCRIPT_DIR}/misp.service"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="misp.service"
MISP_DIR="/opt/misp"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[→]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    local errors=0

    log_step "Checking prerequisites..."

    # Check Ubuntu version
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$VERSION_ID" == "24.04" ]]; then
            log_success "Ubuntu 24.04 detected"
        else
            log_warning "Ubuntu version: $VERSION_ID (recommended: 24.04)"
        fi
    fi

    # Check systemd version
    local systemd_version=$(systemctl --version | head -1 | awk '{print $2}')
    if [[ "$systemd_version" -ge 255 ]]; then
        log_success "systemd version: $systemd_version"
    else
        log_warning "systemd version: $systemd_version (some security features require 255+)"
    fi

    # Check AppArmor
    if command -v aa-status &>/dev/null && aa-status --enabled 2>/dev/null; then
        log_success "AppArmor is enabled"
    else
        log_warning "AppArmor is not enabled (optional but recommended)"
    fi

    # Check MISP installation
    if [[ ! -d "$MISP_DIR" ]]; then
        log_error "MISP installation not found at $MISP_DIR"
        ((errors++))
    else
        log_success "MISP directory found"
    fi

    # Check Docker Compose file
    if [[ ! -f "$MISP_DIR/docker-compose.yml" ]]; then
        log_error "Docker Compose file not found at $MISP_DIR/docker-compose.yml"
        ((errors++))
    else
        log_success "Docker Compose file found"
    fi

    # Check misp-owner user
    if ! id misp-owner &>/dev/null; then
        log_error "User 'misp-owner' does not exist"
        ((errors++))
    else
        log_success "User 'misp-owner' exists"
    fi

    # Check misp-owner is in docker group
    if groups misp-owner | grep -q docker; then
        log_success "User 'misp-owner' is in docker group"
    else
        log_error "User 'misp-owner' is NOT in docker group"
        log_info "Run: sudo usermod -aG docker misp-owner"
        ((errors++))
    fi

    # Check Docker is running
    if systemctl is-active --quiet docker; then
        log_success "Docker service is running"
    else
        log_error "Docker service is not running"
        ((errors++))
    fi

    # Check service file exists
    if [[ ! -f "$SERVICE_FILE" ]]; then
        log_error "Service file not found at $SERVICE_FILE"
        ((errors++))
    else
        log_success "Service file found"
    fi

    if [[ $errors -gt 0 ]]; then
        log_error "Prerequisites check failed with $errors error(s)"
        exit 1
    fi

    log_success "All prerequisites verified"
}

# Display current status
show_current_status() {
    section_header "CURRENT STATUS"

    # Service status
    if systemctl is-active --quiet misp 2>/dev/null; then
        log_info "MISP service status: $(systemctl is-active misp)"
    else
        log_info "MISP service status: not installed or inactive"
    fi

    # Boot startup status
    if systemctl is-enabled --quiet misp 2>/dev/null; then
        log_info "Boot startup: $(systemctl is-enabled misp)"
    else
        log_info "Boot startup: disabled or not configured"
    fi

    # Docker containers
    if command -v docker &>/dev/null && [[ -d "$MISP_DIR" ]]; then
        echo ""
        log_info "Current Docker containers:"
        cd "$MISP_DIR" && docker compose ps 2>/dev/null || log_warning "Unable to query Docker containers"
    fi

    echo ""
}

# Install service
install_service() {
    section_header "INSTALLING SYSTEMD SERVICE"

    log_step "Stopping MISP if running..."
    if systemctl is-active --quiet misp 2>/dev/null; then
        systemctl stop misp || true
        sleep 3
    fi

    log_step "Copying service file to $SYSTEMD_DIR/"
    cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME"
    chmod 644 "$SYSTEMD_DIR/$SERVICE_NAME"
    log_success "Service file installed"

    log_step "Reloading systemd daemon..."
    systemctl daemon-reload
    log_success "Systemd daemon reloaded"

    log_step "Enabling MISP service for auto-start on boot..."
    systemctl enable misp.service
    log_success "MISP service enabled"

    log_step "Starting MISP service..."
    systemctl start misp.service

    log_step "Waiting for services to start (30 seconds)..."
    sleep 30

    if systemctl is-active --quiet misp; then
        log_success "MISP service started successfully"
    else
        log_error "MISP service failed to start"
        log_info "Check logs with: sudo journalctl -u misp -n 50 --no-pager"
        return 1
    fi
}

# Verify installation
verify_installation() {
    section_header "VERIFICATION"

    log_step "Checking service status..."
    echo ""
    systemctl status misp --no-pager --lines=10 || true

    echo ""
    log_step "Checking Docker containers..."
    if [[ -d "$MISP_DIR" ]]; then
        cd "$MISP_DIR" && docker compose ps || true
    fi

    echo ""
    log_info "Service enabled for boot: $(systemctl is-enabled misp 2>/dev/null || echo 'unknown')"
    log_info "Service currently active: $(systemctl is-active misp 2>/dev/null || echo 'unknown')"

    echo ""
    log_step "Running security analysis..."
    systemd-analyze security misp.service 2>/dev/null | head -20 || log_warning "Security analysis unavailable"
}

# Uninstall service
uninstall_service() {
    section_header "UNINSTALLING SYSTEMD SERVICE"

    if [[ ! -f "$SYSTEMD_DIR/$SERVICE_NAME" ]]; then
        log_warning "Service file not found - nothing to uninstall"
        return 0
    fi

    log_step "Stopping MISP service..."
    systemctl stop misp || true

    log_step "Disabling MISP service..."
    systemctl disable misp || true

    log_step "Removing service file..."
    rm -f "$SYSTEMD_DIR/$SERVICE_NAME"
    log_success "Service file removed"

    log_step "Reloading systemd daemon..."
    systemctl daemon-reload
    log_success "Systemd daemon reloaded"

    log_success "MISP systemd service uninstalled successfully"
}

# Display usage info
show_usage_info() {
    section_header "INSTALLATION COMPLETE"

    log_success "MISP systemd service installed and running!"
    echo ""
    log_info "MISP will now start automatically on boot"
    echo ""

    echo -e "${CYAN}Available commands:${NC}"
    echo "  sudo systemctl start misp       - Start MISP stack"
    echo "  sudo systemctl stop misp        - Stop MISP stack"
    echo "  sudo systemctl restart misp     - Restart MISP stack"
    echo "  sudo systemctl status misp      - Check service status"
    echo "  sudo systemctl reload misp      - Update & recreate containers"
    echo "  sudo journalctl -u misp -f      - View live logs"
    echo "  sudo journalctl -u misp -n 100  - View last 100 log lines"
    echo ""

    echo -e "${CYAN}Management:${NC}"
    echo "  sudo systemctl disable misp     - Disable auto-start on boot"
    echo "  sudo systemctl enable misp      - Enable auto-start on boot"
    echo ""

    echo -e "${CYAN}Security:${NC}"
    echo "  sudo systemd-analyze security misp.service  - View security score"
    echo ""

    echo -e "${CYAN}Access MISP:${NC}"
    if [[ -f "$MISP_DIR/PASSWORDS.txt" ]]; then
        local base_url=$(grep "Base URL:" "$MISP_DIR/PASSWORDS.txt" | awk '{print $3}' || echo "https://misp.local")
        echo "  URL: $base_url"
        echo "  Credentials: See $MISP_DIR/PASSWORDS.txt"
    fi
    echo ""
}

# Parse arguments
DRY_RUN=false
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run     Check prerequisites without making changes"
            echo "  --uninstall   Remove MISP systemd service"
            echo "  --help        Show this help message"
            echo ""
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    section_header "MISP SYSTEMD SERVICE SETUP"

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi

    # Handle uninstall
    if [[ "$UNINSTALL" == true ]]; then
        uninstall_service
        exit 0
    fi

    # Check prerequisites
    check_prerequisites

    # Show current status
    show_current_status

    # Dry run mode
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN mode - no changes will be made"
        log_success "Prerequisites check passed - ready for installation"
        exit 0
    fi

    # Confirm installation
    echo ""
    log_warning "This will install the MISP systemd service with the following:"
    echo "  • Automatic start on boot"
    echo "  • Security hardening (Ubuntu 24.04)"
    echo "  • Graceful start/stop management"
    echo "  • Docker Compose integration"
    echo ""
    read -p "Continue with installation? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled by user"
        exit 0
    fi

    # Install service
    install_service

    # Verify installation
    verify_installation

    # Show usage info
    show_usage_info
}

# Run main function
main "$@"
