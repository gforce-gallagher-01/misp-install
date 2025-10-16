#!/bin/bash
set -e
WIDGETS=("MITREAttackICSWidget.php" "ICSVulnerabilityFeedWidget.php" "IndustrialMalwareWidget.php" "SCADAIOCMonitorWidget.php" "AssetTargetingAnalysisWidget.php")
CONTAINER="misp-misp-core-1"
DEST="/var/www/MISP/app/Lib/Dashboard/Custom"
echo "Installing 5 ICS/OT Dashboard widgets..."
for widget in "${WIDGETS[@]}"; do
  docker cp "$widget" "$CONTAINER:$DEST/"
  docker exec "$CONTAINER" chown www-data:www-data "$DEST/$widget"
  docker exec "$CONTAINER" chmod 644 "$DEST/$widget"
  echo "✓ ${widget%.php}"
done
docker exec "$CONTAINER" rm -rf /var/www/MISP/app/tmp/cache/models/* /var/www/MISP/app/tmp/cache/persistent/*
echo "✓ All 5 ICS/OT widgets installed!"
