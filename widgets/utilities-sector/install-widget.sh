#!/bin/bash
#
# Utilities Sector Widget Installation Script
# Installs UtilitiesThreatHeatMapWidget.php to MISP
#
# Usage:
#   sudo bash install-widget.sh
#
# Author: tKQB Enterprises
# Version: 1.0
# Date: 2025-10-16

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Target paths
MISP_CUSTOM_DIR="/var/www/MISP/app/Lib/Dashboard/Custom"
WIDGET_FILE="UtilitiesThreatHeatMapWidget.php"
SOURCE_FILE="${SCRIPT_DIR}/${WIDGET_FILE}"
TARGET_FILE="${MISP_CUSTOM_DIR}/${WIDGET_FILE}"

echo "============================================"
echo "MISP Widget Installation Script"
echo "Widget: Utilities Sector Threat Heat Map"
echo "============================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Check if source file exists
if [[ ! -f "${SOURCE_FILE}" ]]; then
    echo -e "${RED}ERROR: Widget file not found: ${SOURCE_FILE}${NC}"
    exit 1
fi

# Check if MISP directory exists
if [[ ! -d "${MISP_CUSTOM_DIR}" ]]; then
    echo -e "${RED}ERROR: MISP custom widget directory not found: ${MISP_CUSTOM_DIR}${NC}"
    echo "Is MISP installed?"
    exit 1
fi

# Validate PHP syntax
echo -e "${YELLOW}[1/6]${NC} Validating PHP syntax..."
php -l "${SOURCE_FILE}" > /dev/null
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} PHP syntax valid"
else
    echo -e "      ${RED}✗${NC} PHP syntax error"
    exit 1
fi

# Copy widget file
echo -e "${YELLOW}[2/6]${NC} Copying widget to MISP..."
cp "${SOURCE_FILE}" "${TARGET_FILE}"
if [[ -f "${TARGET_FILE}" ]]; then
    echo -e "      ${GREEN}✓${NC} Widget copied successfully"
else
    echo -e "      ${RED}✗${NC} Failed to copy widget"
    exit 1
fi

# Set ownership
echo -e "${YELLOW}[3/6]${NC} Setting file ownership..."
chown www-data:www-data "${TARGET_FILE}"
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Ownership set to www-data:www-data"
else
    echo -e "      ${RED}✗${NC} Failed to set ownership"
    exit 1
fi

# Set permissions
echo -e "${YELLOW}[4/6]${NC} Setting file permissions..."
chmod 644 "${TARGET_FILE}"
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Permissions set to 644"
else
    echo -e "      ${RED}✗${NC} Failed to set permissions"
    exit 1
fi

# Clear MISP cache
echo -e "${YELLOW}[5/6]${NC} Clearing MISP cache..."
sudo -u www-data /var/www/MISP/app/Console/cake Admin clearCache > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Cache cleared"
else
    echo -e "      ${YELLOW}!${NC} Cache clear may have failed (check manually)"
fi

# Restart web server
echo -e "${YELLOW}[6/6]${NC} Restarting web server..."
if systemctl is-active --quiet apache2; then
    systemctl restart apache2
    echo -e "      ${GREEN}✓${NC} Apache2 restarted"
elif systemctl is-active --quiet nginx; then
    systemctl restart nginx
    systemctl restart php8.3-fpm 2>/dev/null || systemctl restart php8.1-fpm 2>/dev/null || systemctl restart php7.4-fpm
    echo -e "      ${GREEN}✓${NC} Nginx and PHP-FPM restarted"
else
    echo -e "      ${YELLOW}!${NC} Could not detect web server (restart manually)"
fi

echo ""
echo "============================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Log into MISP web interface"
echo "2. Navigate to Dashboard"
echo "3. Click 'Edit Dashboard' → 'Add Widget'"
echo "4. Look for 'Utilities Sector Threat Heat Map' in Custom section"
echo ""
echo "Widget configuration example:"
echo '{"timeframe": "7d", "limit": "1000", "sector_tag": "ics:sector"}'
echo ""
echo "For troubleshooting, see: INSTALLATION.md"
echo ""
