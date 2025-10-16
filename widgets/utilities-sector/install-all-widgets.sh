#!/bin/bash
#
# Install All Utilities Sector Widgets
# Installs all 5 utilities sector widgets to Docker-based MISP
#
# Usage:
#   sudo bash install-all-widgets.sh
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

# Widget files
WIDGETS=(
    "UtilitiesThreatHeatMapWidget.php"
    "ICSProtocolsTargetedWidget.php"
    "CriticalInfrastructureBreakdownWidget.php"
    "UtilitiesSectorStatsWidget.php"
    "NERCCIPComplianceWidget.php"
)

CONTAINER_DIR="/var/www/MISP/app/Lib/Dashboard/Custom"

echo "============================================"
echo "Install All Utilities Sector Widgets"
echo "============================================"
echo ""
echo "This will install ${#WIDGETS[@]} widgets:"
for widget in "${WIDGETS[@]}"; do
    echo "  - ${widget%.php}"
done
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}ERROR: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Check if Docker is running
echo -e "${YELLOW}[1/5]${NC} Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo -e "      ${RED}✗${NC} Docker is not running"
    exit 1
fi
echo -e "      ${GREEN}✓${NC} Docker is running"

# Check if MISP container exists
echo -e "${YELLOW}[2/5]${NC} Checking MISP container..."
if ! docker ps --format '{{.Names}}' | grep -q "^${MISP_CONTAINER}$"; then
    echo -e "      ${RED}✗${NC} MISP container not found: ${MISP_CONTAINER}"
    exit 1
fi
echo -e "      ${GREEN}✓${NC} MISP container found"

# Validate PHP syntax for all widgets
echo -e "${YELLOW}[3/5]${NC} Validating PHP syntax..."
VALID_COUNT=0
for widget in "${WIDGETS[@]}"; do
    SOURCE_FILE="${SCRIPT_DIR}/${widget}"

    if [[ ! -f "${SOURCE_FILE}" ]]; then
        echo -e "      ${RED}✗${NC} Widget file not found: ${widget}"
        exit 1
    fi

    if php -l "${SOURCE_FILE}" > /dev/null 2>&1; then
        VALID_COUNT=$((VALID_COUNT + 1))
    else
        echo -e "      ${RED}✗${NC} PHP syntax error in: ${widget}"
        php -l "${SOURCE_FILE}"
        exit 1
    fi
done
echo -e "      ${GREEN}✓${NC} All ${VALID_COUNT} widgets have valid syntax"

# Copy all widgets to container
echo -e "${YELLOW}[4/5]${NC} Installing widgets..."
INSTALLED_COUNT=0
for widget in "${WIDGETS[@]}"; do
    SOURCE_FILE="${SCRIPT_DIR}/${widget}"
    CONTAINER_PATH="${CONTAINER_DIR}/${widget}"

    # Copy to container
    if docker cp "${SOURCE_FILE}" "${MISP_CONTAINER}:${CONTAINER_PATH}" 2>/dev/null; then
        # Set ownership and permissions
        docker exec "${MISP_CONTAINER}" chown www-data:www-data "${CONTAINER_PATH}" 2>/dev/null
        docker exec "${MISP_CONTAINER}" chmod 644 "${CONTAINER_PATH}" 2>/dev/null
        INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
        echo -e "      ${GREEN}✓${NC} ${widget%.php}"
    else
        echo -e "      ${RED}✗${NC} Failed to install: ${widget}"
        exit 1
    fi
done

# Clear MISP cache
echo -e "${YELLOW}[5/5]${NC} Clearing MISP cache..."
docker exec "${MISP_CONTAINER}" rm -rf /var/www/MISP/app/tmp/cache/models/* /var/www/MISP/app/tmp/cache/persistent/* 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo -e "      ${GREEN}✓${NC} Cache cleared"
else
    echo -e "      ${YELLOW}!${NC} Cache clear may have failed (check manually)"
fi

echo ""
echo "============================================"
echo -e "${GREEN}✓ All ${INSTALLED_COUNT} Widgets Installed!${NC}"
echo "============================================"
echo ""
echo "Widgets installed:"
for widget in "${WIDGETS[@]}"; do
    echo "  ✓ ${widget%.php}"
done
echo ""
echo "Next steps:"
echo "1. Configure dashboard with all widgets:"
echo "   cd ${SCRIPT_DIR}"
echo "   python3 configure-dashboard-full.py"
echo ""
echo "2. Or manually add widgets in MISP:"
echo "   - Navigate to Dashboard"
echo "   - Click 'Edit Dashboard' (if available)"
echo "   - Click 'Add Widget'"
echo "   - Look in 'Custom' section"
echo ""
