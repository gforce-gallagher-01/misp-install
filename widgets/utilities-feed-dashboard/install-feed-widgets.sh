#!/bin/bash
# Install Utilities Sector Feed Dashboard Widgets to MISP
# Created: 2025-10-16

set -e

CONTAINER="misp-misp-core-1"
WIDGET_DIR="/var/www/MISP/app/Lib/Dashboard/Custom"

echo "======================================"
echo "Installing Feed Dashboard Widgets"
echo "======================================"
echo ""

# Check if container is running
if ! sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "✗ Error: Container ${CONTAINER} is not running"
    exit 1
fi

echo "✓ Container ${CONTAINER} is running"
echo ""

# Widget files to install
WIDGETS=(
    "ICSCERTAdvisoryWidget.php"
    "CISAUtilitiesAlertsWidget.php"
    "VendorSecurityBulletinsWidget.php"
    "ICSZeroDayTrackerWidget.php"
    "FeedHealthMonitorWidget.php"
)

echo "Installing ${#WIDGETS[@]} widgets..."
echo ""

for widget in "${WIDGETS[@]}"; do
    echo "Installing: $widget"

    # Copy widget to container
    sudo docker cp "$widget" "${CONTAINER}:${WIDGET_DIR}/${widget}"

    # Set ownership to www-data
    sudo docker exec "${CONTAINER}" chown www-data:www-data "${WIDGET_DIR}/${widget}"

    # Set permissions
    sudo docker exec "${CONTAINER}" chmod 644 "${WIDGET_DIR}/${widget}"

    echo "  ✓ Installed and configured"
done

echo ""
echo "Clearing MISP cache..."
sudo docker exec "${CONTAINER}" bash -c "rm -rf /var/www/MISP/app/tmp/cache/models/* /var/www/MISP/app/tmp/cache/persistent/*" 2>/dev/null || true
echo "  ✓ Cache cleared"

echo ""
echo "======================================"
echo "✓ All 5 Feed Dashboard widgets installed!"
echo "======================================"
echo ""
echo "Installed widgets:"
echo "  1. ICSCERTAdvisoryWidget (SimpleList)"
echo "  2. CISAUtilitiesAlertsWidget (SimpleList)"
echo "  3. VendorSecurityBulletinsWidget (BarChart)"
echo "  4. ICSZeroDayTrackerWidget (SimpleList)"
echo "  5. FeedHealthMonitorWidget (BarChart)"
echo ""
echo "Next steps:"
echo "  1. Update master dashboard script (configure-all-dashboards.py)"
echo "  2. Run master script to add widgets to dashboard"
echo "  3. Refresh MISP dashboard in browser"
