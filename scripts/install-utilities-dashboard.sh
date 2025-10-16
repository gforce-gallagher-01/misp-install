#!/bin/bash
#
# One-Step Utilities Sector Dashboard Installation
# Installs widget and configures dashboard automatically
#
# Usage:
#   sudo bash install-utilities-dashboard.sh
#
# Author: tKQB Enterprises
# Version: 1.0
# Date: 2025-10-16

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIDGET_DIR="${SCRIPT_DIR}/../widgets/utilities-sector"

echo "============================================"
echo "Utilities Sector Dashboard Installation"
echo "============================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root (use sudo)"
   exit 1
fi

# Step 1: Install widget
echo -e "${YELLOW}[1/2]${NC} Installing widget to MISP container..."
cd "${WIDGET_DIR}"
bash install-widget-docker.sh

# Step 2: Configure dashboard
echo ""
echo -e "${YELLOW}[2/2]${NC} Configuring dashboard with widget..."

# Get API key
API_KEY=$(grep MISP_API_KEY= /opt/misp/.env | cut -d'=' -f2)
if [ -z "$API_KEY" ]; then
    API_KEY=$(grep "API KEY:" /opt/misp/PASSWORDS.txt | awk '{print $3}')
fi

if [ -z "$API_KEY" ]; then
    echo "ERROR: Could not find API key"
    exit 1
fi

# Get MISP URL
MISP_URL=$(grep BASE_URL= /opt/misp/.env | cut -d'=' -f2)

# Run configuration script as regular user
sudo -u $(logname) python3 configure-dashboard.py \
    --api-key "$API_KEY" \
    --misp-url "$MISP_URL" \
    --backup

echo ""
echo "============================================"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "============================================"
echo ""
echo "Access your dashboard:"
echo "  URL: $MISP_URL"
echo "  Dashboard: Click 'Dashboard' in top menu"
echo ""
echo "The following widgets have been added:"
echo "  1. Utilities Sector Threat Heat Map (12x4)"
echo "  2. Trending Tags (6x3)"
echo "  3. Trending Attributes (6x3)"
echo "  4. Recent Events (12x3)"
echo ""
echo "Dashboard backup saved to: dashboard-backup.json"
echo ""
