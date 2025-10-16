#!/bin/bash
# Install Base Widget Files (DRY Refactoring)
# Created: 2025-10-16

set -e

CONTAINER="misp-misp-core-1"
WIDGET_DIR="/var/www/MISP/app/Lib/Dashboard/Custom"

echo "======================================"
echo "Installing Base Widget Files"
echo "======================================"
echo ""

# Check if container is running
if ! sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "✗ Error: Container ${CONTAINER} is not running"
    exit 1
fi

echo "✓ Container ${CONTAINER} is running"
echo ""

# Validate PHP syntax
echo "Validating PHP syntax..."
php -l BaseUtilitiesWidget.php || exit 1
php -l UtilitiesWidgetConstants.php || exit 1
echo "  ✓ Base files have valid syntax"
echo ""

# Install base files
echo "Installing base files..."

# Copy BaseUtilitiesWidget.php
sudo docker cp BaseUtilitiesWidget.php "${CONTAINER}:${WIDGET_DIR}/BaseUtilitiesWidget.php"
sudo docker exec "${CONTAINER}" chown www-data:www-data "${WIDGET_DIR}/BaseUtilitiesWidget.php"
sudo docker exec "${CONTAINER}" chmod 644 "${WIDGET_DIR}/BaseUtilitiesWidget.php"
echo "  ✓ BaseUtilitiesWidget.php"

# Copy UtilitiesWidgetConstants.php
sudo docker cp UtilitiesWidgetConstants.php "${CONTAINER}:${WIDGET_DIR}/UtilitiesWidgetConstants.php"
sudo docker exec "${CONTAINER}" chown www-data:www-data "${WIDGET_DIR}/UtilitiesWidgetConstants.php"
sudo docker exec "${CONTAINER}" chmod 644 "${WIDGET_DIR}/UtilitiesWidgetConstants.php"
echo "  ✓ UtilitiesWidgetConstants.php"

echo ""
echo "Clearing MISP cache..."
sudo docker exec "${CONTAINER}" bash -c "rm -rf /var/www/MISP/app/tmp/cache/models/* /var/www/MISP/app/tmp/cache/persistent/*" 2>/dev/null || true
echo "  ✓ Cache cleared"

echo ""
echo "======================================"
echo "✓ Base Files Installed!"
echo "======================================"
echo ""
echo "Installed:"
echo "  ✓ BaseUtilitiesWidget.php (Abstract base class)"
echo "  ✓ UtilitiesWidgetConstants.php (Shared constants)"
echo ""
echo "Next steps:"
echo "  1. Refactor individual widgets to extend BaseUtilitiesWidget"
echo "  2. Replace hardcoded constants with UtilitiesWidgetConstants methods"
echo "  3. Reinstall refactored widgets"
