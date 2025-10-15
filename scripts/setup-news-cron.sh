#!/bin/bash
#
# Setup MISP News Auto-Population Cron Job
# Version: 1.0
# Date: 2025-10-15
#
# Purpose:
#   Install cron job to automatically populate MISP news from RSS feeds daily
#
# Usage:
#   ./scripts/setup-news-cron.sh
#   ./scripts/setup-news-cron.sh --remove

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cron job configuration
CRON_TIME="0 8 * * *"  # Daily at 8 AM
CRON_CMD="cd $PROJECT_DIR && /usr/bin/python3 scripts/populate-misp-news.py --quiet --days 2"
CRON_COMMENT="# MISP News Auto-Population (Daily)"

print_header() {
    echo ""
    echo "========================================================================"
    echo "  $1"
    echo "========================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

remove_cron() {
    print_header "Remove MISP News Cron Job"

    # Check if cron job exists
    if crontab -l 2>/dev/null | grep -q "populate-misp-news.py"; then
        # Remove the cron job
        crontab -l 2>/dev/null | grep -v "populate-misp-news.py" | grep -v "MISP News Auto-Population" | crontab -
        print_success "MISP news cron job removed"
    else
        print_info "No MISP news cron job found"
    fi

    echo ""
    print_success "Done!"
    exit 0
}

install_cron() {
    print_header "Setup MISP News Auto-Population Cron Job"

    # Check if script exists
    if [ ! -f "$PROJECT_DIR/scripts/populate-misp-news.py" ]; then
        print_error "populate-misp-news.py not found at $PROJECT_DIR/scripts/"
        exit 1
    fi

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "populate-misp-news.py"; then
        print_info "MISP news cron job already exists"
        echo ""
        echo "Current cron job:"
        crontab -l 2>/dev/null | grep -A 1 "MISP News"
        echo ""
        read -p "Replace existing cron job? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cancelled - no changes made"
            exit 0
        fi
        # Remove old entry
        crontab -l 2>/dev/null | grep -v "populate-misp-news.py" | grep -v "MISP News Auto-Population" | crontab -
    fi

    # Add new cron job
    (crontab -l 2>/dev/null; echo ""; echo "$CRON_COMMENT"; echo "$CRON_TIME $CRON_CMD") | crontab -

    print_success "MISP news cron job installed"
    echo ""
    echo "Schedule: Daily at 8:00 AM"
    echo "Command:  $CRON_CMD"
    echo ""

    # Verify installation
    print_info "Current crontab:"
    echo ""
    crontab -l | grep -A 1 "MISP News" || true
    echo ""

    print_success "Setup complete!"
    echo ""
    echo "The script will:"
    echo "  • Run daily at 8:00 AM"
    echo "  • Check RSS feeds for new articles (last 2 days)"
    echo "  • Add utilities/energy sector news to MISP"
    echo "  • Skip duplicates automatically"
    echo "  • Log to: /opt/misp/logs/populate-misp-news-*.log"
    echo ""
    echo "Manual run:"
    echo "  python3 $PROJECT_DIR/scripts/populate-misp-news.py"
    echo ""
    echo "Remove cron job:"
    echo "  $0 --remove"
    echo ""
}

# Main execution
if [ "$1" == "--remove" ]; then
    remove_cron
else
    install_cron
fi
