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
# Skip BaseUtilitiesWidget.php - it's an abstract class that should NOT be installed
# Only validate UtilitiesWidgetConstants.php
if [ -f "UtilitiesWidgetConstants.php" ]; then
    php -l UtilitiesWidgetConstants.php || exit 1
    echo "  ✓ UtilitiesWidgetConstants.php has valid syntax"
else
    echo "  ⚠ UtilitiesWidgetConstants.php not found, skipping"
fi
echo ""

# Install base files
echo "Installing base files..."

# Skip BaseUtilitiesWidget.php - abstract classes should NOT be in Custom directory
# This causes "Cannot instantiate abstract class" errors in MISP

# Copy UtilitiesWidgetConstants.php (if exists)
if [ -f "UtilitiesWidgetConstants.php" ]; then
    sudo docker cp UtilitiesWidgetConstants.php "${CONTAINER}:${WIDGET_DIR}/UtilitiesWidgetConstants.php"
    sudo docker exec "${CONTAINER}" chown www-data:www-data "${WIDGET_DIR}/UtilitiesWidgetConstants.php"
    sudo docker exec "${CONTAINER}" chmod 644 "${WIDGET_DIR}/UtilitiesWidgetConstants.php"
    echo "  ✓ UtilitiesWidgetConstants.php"
else
    echo "  ⚠ UtilitiesWidgetConstants.php not found, skipping"
fi

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
echo "  ✓ UtilitiesWidgetConstants.php (Shared constants)"
echo ""
echo "Note: BaseUtilitiesWidget.php (abstract class) intentionally NOT installed"
echo "      Abstract classes cannot be instantiated and break MISP's widget loader"
