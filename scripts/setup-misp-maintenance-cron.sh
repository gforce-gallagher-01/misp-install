#!/bin/bash
#
# MISP Maintenance Cron Job Setup Script
#
# This script sets up automated daily and weekly maintenance jobs for MISP.
# It configures cron jobs to run maintenance scripts at optimal times.
#
# Daily Maintenance (2 AM):
#   - Update warninglists
#   - Fetch OSINT feeds
#   - Cache feed data
#   - Health checks (containers, disk space)
#
# Weekly Maintenance (Sunday 3 AM):
#   - Update taxonomies
#   - Update galaxies (MITRE ATT&CK, threat actors)
#   - Update object templates
#   - Database optimization
#
# Usage:
#   ./setup-misp-maintenance-cron.sh              # Interactive setup
#   ./setup-misp-maintenance-cron.sh --auto       # Automatic setup (no prompts)
#   ./setup-misp-maintenance-cron.sh --remove     # Remove cron jobs
#   ./setup-misp-maintenance-cron.sh --status     # Check cron job status
#
# Requirements:
#   - MISP installation at /opt/misp
#   - Scripts in /home/gallagher/misp-install/misp-install/scripts
#   - User with sudo access
#
# Author: tKQB Enterprises
# Version: 1.0
# Created: October 2025
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="/home/gallagher/misp-install/misp-install/scripts"
LOG_DIR="/var/log/misp-maintenance"
DAILY_SCRIPT="$SCRIPT_DIR/misp-daily-maintenance.py"
WEEKLY_SCRIPT="$SCRIPT_DIR/misp-weekly-maintenance.py"

# Cron schedule
DAILY_CRON="0 2 * * *"     # Daily at 2 AM
WEEKLY_CRON="0 3 * * 0"    # Sunday at 3 AM

# Banner
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   MISP Maintenance Cron Job Setup                     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if scripts exist
check_scripts() {
    echo -e "${BLUE}Checking maintenance scripts...${NC}"

    if [ ! -f "$DAILY_SCRIPT" ]; then
        echo -e "${RED}✗ Daily maintenance script not found: $DAILY_SCRIPT${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Daily maintenance script found${NC}"

    if [ ! -f "$WEEKLY_SCRIPT" ]; then
        echo -e "${RED}✗ Weekly maintenance script not found: $WEEKLY_SCRIPT${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Weekly maintenance script found${NC}"
    echo ""
}

# Create log directory
setup_log_directory() {
    echo -e "${BLUE}Setting up log directory...${NC}"

    if [ ! -d "$LOG_DIR" ]; then
        sudo mkdir -p "$LOG_DIR"
        sudo chown $USER:$USER "$LOG_DIR"
        sudo chmod 755 "$LOG_DIR"
        echo -e "${GREEN}✓ Created log directory: $LOG_DIR${NC}"
    else
        echo -e "${GREEN}✓ Log directory already exists: $LOG_DIR${NC}"
    fi
    echo ""
}

# Make scripts executable
make_executable() {
    echo -e "${BLUE}Making scripts executable...${NC}"

    chmod +x "$DAILY_SCRIPT"
    chmod +x "$WEEKLY_SCRIPT"

    echo -e "${GREEN}✓ Scripts are now executable${NC}"
    echo ""
}

# Add cron jobs
add_cron_jobs() {
    echo -e "${BLUE}Adding cron jobs...${NC}"

    # Create temporary crontab file
    TEMP_CRON=$(mktemp)

    # Get current crontab (if exists)
    crontab -l > "$TEMP_CRON" 2>/dev/null || true

    # Check if jobs already exist
    if grep -q "misp-daily-maintenance" "$TEMP_CRON"; then
        echo -e "${YELLOW}⚠ Daily maintenance cron job already exists${NC}"
    else
        # Add daily maintenance job
        echo "" >> "$TEMP_CRON"
        echo "# MISP Daily Maintenance (2 AM)" >> "$TEMP_CRON"
        echo "$DAILY_CRON cd $SCRIPT_DIR && python3 misp-daily-maintenance.py >> $LOG_DIR/daily-\$(date +\\%Y\\%m\\%d).log 2>&1" >> "$TEMP_CRON"
        echo -e "${GREEN}✓ Added daily maintenance cron job${NC}"
    fi

    if grep -q "misp-weekly-maintenance" "$TEMP_CRON"; then
        echo -e "${YELLOW}⚠ Weekly maintenance cron job already exists${NC}"
    else
        # Add weekly maintenance job
        echo "" >> "$TEMP_CRON"
        echo "# MISP Weekly Maintenance (Sunday 3 AM)" >> "$TEMP_CRON"
        echo "$WEEKLY_CRON cd $SCRIPT_DIR && python3 misp-weekly-maintenance.py >> $LOG_DIR/weekly-\$(date +\\%Y\\%m\\%d).log 2>&1" >> "$TEMP_CRON"
        echo -e "${GREEN}✓ Added weekly maintenance cron job${NC}"
    fi

    # Install new crontab
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"

    echo ""
}

# Remove cron jobs
remove_cron_jobs() {
    echo -e "${BLUE}Removing cron jobs...${NC}"

    # Create temporary crontab file
    TEMP_CRON=$(mktemp)

    # Get current crontab (if exists)
    crontab -l > "$TEMP_CRON" 2>/dev/null || true

    # Remove MISP maintenance jobs
    grep -v "misp-daily-maintenance\|misp-weekly-maintenance\|MISP Daily Maintenance\|MISP Weekly Maintenance" "$TEMP_CRON" > "${TEMP_CRON}.new" || true
    mv "${TEMP_CRON}.new" "$TEMP_CRON"

    # Install new crontab
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"

    echo -e "${GREEN}✓ MISP maintenance cron jobs removed${NC}"
    echo ""
}

# Show cron job status
show_status() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   MISP Maintenance Cron Job Status                    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${BLUE}Current cron jobs:${NC}"
    echo ""

    if crontab -l 2>/dev/null | grep -q "misp-daily-maintenance\|misp-weekly-maintenance"; then
        crontab -l | grep -A1 -B1 "MISP.*Maintenance\|misp-.*-maintenance" || true
        echo ""
        echo -e "${GREEN}✓ MISP maintenance cron jobs are configured${NC}"
    else
        echo -e "${YELLOW}⚠ No MISP maintenance cron jobs found${NC}"
        echo ""
        echo "Run this script without arguments to set up cron jobs."
    fi
    echo ""

    # Show recent logs
    echo -e "${BLUE}Recent maintenance logs:${NC}"
    echo ""

    if [ -d "$LOG_DIR" ]; then
        ls -lht "$LOG_DIR" | head -10
    else
        echo -e "${YELLOW}⚠ Log directory does not exist: $LOG_DIR${NC}"
    fi
    echo ""
}

# Test run (dry-run)
test_scripts() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   Testing Maintenance Scripts (Dry-Run)               ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${BLUE}Testing daily maintenance script...${NC}"
    echo ""
    python3 "$DAILY_SCRIPT" --dry-run
    echo ""

    echo -e "${BLUE}Testing weekly maintenance script...${NC}"
    echo ""
    python3 "$WEEKLY_SCRIPT" --dry-run
    echo ""

    echo -e "${GREEN}✓ Test completed - scripts are working${NC}"
    echo ""
}

# Main setup function
main_setup() {
    check_scripts
    setup_log_directory
    make_executable
    add_cron_jobs

    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   MISP Maintenance Cron Jobs Configured!              ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${GREEN}Configured Jobs:${NC}"
    echo ""
    echo "  • Daily Maintenance:  Every day at 2:00 AM"
    echo "    - Update warninglists"
    echo "    - Fetch OSINT feeds"
    echo "    - Cache feed data"
    echo "    - Health checks"
    echo ""
    echo "  • Weekly Maintenance: Every Sunday at 3:00 AM"
    echo "    - Update taxonomies"
    echo "    - Update galaxies (MITRE ATT&CK)"
    echo "    - Update object templates"
    echo "    - Database optimization"
    echo ""

    echo -e "${BLUE}Logs Location:${NC}"
    echo "  $LOG_DIR"
    echo ""

    echo -e "${BLUE}View Cron Jobs:${NC}"
    echo "  crontab -l | grep misp"
    echo ""

    echo -e "${BLUE}View Logs:${NC}"
    echo "  tail -f $LOG_DIR/daily-*.log"
    echo "  tail -f $LOG_DIR/weekly-*.log"
    echo ""

    echo -e "${BLUE}Manual Run (Testing):${NC}"
    echo "  python3 $DAILY_SCRIPT --dry-run"
    echo "  python3 $WEEKLY_SCRIPT --dry-run"
    echo ""

    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    --auto)
        echo -e "${YELLOW}Running automatic setup (no prompts)...${NC}"
        echo ""
        main_setup
        ;;
    --remove)
        echo -e "${YELLOW}Removing MISP maintenance cron jobs...${NC}"
        echo ""
        remove_cron_jobs
        echo -e "${GREEN}✓ Cron jobs removed${NC}"
        echo ""
        ;;
    --status)
        show_status
        ;;
    --test)
        check_scripts
        test_scripts
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  (no option)  Interactive setup (default)"
        echo "  --auto       Automatic setup (no prompts)"
        echo "  --remove     Remove cron jobs"
        echo "  --status     Show cron job status"
        echo "  --test       Test scripts (dry-run)"
        echo "  --help       Show this help message"
        echo ""
        exit 0
        ;;
    "")
        # Interactive mode
        echo -e "${YELLOW}This will set up automated MISP maintenance cron jobs.${NC}"
        echo ""
        echo "Daily maintenance (2 AM):"
        echo "  - Update warninglists (false positive filters)"
        echo "  - Fetch OSINT feeds (threat intelligence)"
        echo "  - Cache feed data"
        echo "  - Health checks (containers, disk space)"
        echo ""
        echo "Weekly maintenance (Sunday 3 AM):"
        echo "  - Update taxonomies"
        echo "  - Update galaxies (MITRE ATT&CK, threat actors)"
        echo "  - Update object templates"
        echo "  - Database optimization"
        echo ""

        read -p "Continue with setup? (y/N): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            main_setup
        else
            echo -e "${YELLOW}Setup cancelled.${NC}"
            exit 0
        fi
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information."
        exit 1
        ;;
esac
