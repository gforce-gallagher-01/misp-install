#!/bin/bash
#
# Utilities Sector Widget Installation Script (Docker Version)
# Installs UtilitiesThreatHeatMapWidget.php to Docker-based MISP
#
# Usage:
#   sudo bash install-widget-docker.sh
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

# Container name
MISP_CONTAINER="misp-misp-core-1"

# Target paths
WIDGET_FILE="UtilitiesThreatHeatMapWidget.php"
SOURCE_FILE="${SCRIPT_DIR}/${WIDGET_FILE}"
CONTAINER_PATH="/var/www/MISP/app/Lib/Dashboard/Custom/${WIDGET_FILE}"

echo "============================================"
echo "MISP Widget Installation Script (Docker)"
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

# Check if Docker is running
echo -e "${YELLOW}[1/7]${NC} Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo -e "      ${RED}✗${NC} Docker is not running"
    exit 1
fi
echo -e "      ${GREEN}✓${NC} Docker is running"

# Check if MISP container exists
echo -e "${YELLOW}[2/7]${NC} Checking MISP container..."
if ! docker ps --format '{{.Names}}' | grep -q "^${MISP_CONTAINER}$"; then
    echo -e "      ${RED}✗${NC} MISP container not found: ${MISP_CONTAINER}"
    exit 1
fi
echo -e "      ${GREEN}✓${NC} MISP container found"

# Validate PHP syntax
echo -e "${YELLOW}[3/7]${NC} Validating PHP syntax..."
php -l "${SOURCE_FILE}" > /dev/null
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} PHP syntax valid"
else
    echo -e "      ${RED}✗${NC} PHP syntax error"
    exit 1
fi

# Copy widget to container
echo -e "${YELLOW}[4/7]${NC} Copying widget to MISP container..."
docker cp "${SOURCE_FILE}" "${MISP_CONTAINER}:${CONTAINER_PATH}"
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Widget copied successfully"
else
    echo -e "      ${RED}✗${NC} Failed to copy widget"
    exit 1
fi

# Set ownership
echo -e "${YELLOW}[5/7]${NC} Setting file ownership..."
docker exec "${MISP_CONTAINER}" chown www-data:www-data "${CONTAINER_PATH}"
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Ownership set to www-data:www-data"
else
    echo -e "      ${RED}✗${NC} Failed to set ownership"
    exit 1
fi

# Set permissions
echo -e "${YELLOW}[6/7]${NC} Setting file permissions..."
docker exec "${MISP_CONTAINER}" chmod 644 "${CONTAINER_PATH}"
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Permissions set to 644"
else
    echo -e "      ${RED}✗${NC} Failed to set permissions"
    exit 1
fi

# Clear MISP cache
echo -e "${YELLOW}[7/7]${NC} Clearing MISP cache..."
docker exec "${MISP_CONTAINER}" rm -rf /var/www/MISP/app/tmp/cache/models/* /var/www/MISP/app/tmp/cache/persistent/* 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Cache cleared"
else
    echo -e "      ${YELLOW}!${NC} Cache clear may have failed (check manually)"
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
