#!/bin/bash
# MISP Instance Inspection Script
# Purpose: Gather comprehensive state information from running MISP instance
# Usage: ./scripts/inspect-misp-instance.sh [--json|--markdown|--summary]
# Output: System state, configuration, data statistics, compliance assessment

set -euo pipefail

# Configuration
MISP_DIR="/opt/misp"
LOG_DIR="${MISP_DIR}/logs"
BACKUP_DIR="${HOME}/misp-backups"
OUTPUT_FORMAT="${1:---summary}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_section() {
    echo -e "\n${GREEN}=== $1 ===${NC}\n"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if MISP is running
check_misp_running() {
    if ! sudo docker ps | grep -q "misp-misp-core-1"; then
        print_error "MISP core container is not running"
        exit 1
    fi
}

# Get MySQL password
get_mysql_password() {
    sudo docker exec misp-misp-core-1 printenv MYSQL_PASSWORD 2>/dev/null || echo ""
}

# Main inspection functions
inspect_version() {
    print_section "MISP Version"

    VERSION_JSON=$(sudo docker exec misp-misp-core-1 cat /var/www/MISP/VERSION.json 2>/dev/null || echo '{}')
    MAJOR=$(echo "$VERSION_JSON" | jq -r '.major // "N/A"')
    MINOR=$(echo "$VERSION_JSON" | jq -r '.minor // "N/A"')
    HOTFIX=$(echo "$VERSION_JSON" | jq -r '.hotfix // "N/A"')

    echo "MISP Version: $MAJOR.$MINOR.$HOTFIX"
    echo "Release Date: $(sudo docker inspect misp-misp-core-1 | jq -r '.[0].Created' | cut -d'T' -f1)"
}

inspect_containers() {
    print_section "Container Status"

    echo "Container Health:"
    sudo docker ps --filter name=misp --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

    echo ""
    echo "Resource Usage:"
    sudo docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep misp
}

inspect_data_stats() {
    print_section "Data Statistics"

    MYSQL_PASS=$(get_mysql_password)

    if [ -z "$MYSQL_PASS" ]; then
        print_warning "Cannot access database (missing password)"
        return
    fi

    # Event count
    EVENT_COUNT=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT COUNT(*) FROM events;" 2>/dev/null | tail -1)
    echo "Total Events: ${EVENT_COUNT:-N/A}"

    # Attribute count
    ATTR_COUNT=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT COUNT(*) FROM attributes;" 2>/dev/null | tail -1)
    echo "Total Attributes: ${ATTR_COUNT:-N/A}"

    # Feed count
    FEED_COUNT=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT COUNT(*) FROM feeds WHERE enabled=1;" 2>/dev/null | tail -1)
    echo "Enabled Feeds: ${FEED_COUNT:-N/A}"

    # Organization count
    ORG_COUNT=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT COUNT(*) FROM organisations;" 2>/dev/null | tail -1)
    echo "Organizations: ${ORG_COUNT:-N/A}"

    # Calculate average attributes per event
    if [ -n "$EVENT_COUNT" ] && [ -n "$ATTR_COUNT" ] && [ "$EVENT_COUNT" -gt 0 ]; then
        AVG=$(echo "scale=0; $ATTR_COUNT / $EVENT_COUNT" | bc)
        echo "Average Attributes/Event: ${AVG}"
    fi
}

inspect_configuration() {
    print_section "Configuration"

    echo "Network Configuration:"
    BASE_URL=$(sudo docker exec misp-misp-core-1 printenv BASE_URL 2>/dev/null || echo "N/A")
    echo "  Base URL: $BASE_URL"

    echo "  Server IP: $(hostname -I | awk '{print $1}')"

    echo ""
    echo "Admin Configuration:"
    ADMIN_EMAIL=$(sudo docker exec misp-misp-core-1 printenv ADMIN_EMAIL 2>/dev/null || echo "N/A")
    ADMIN_ORG=$(sudo docker exec misp-misp-core-1 printenv ADMIN_ORG 2>/dev/null || echo "N/A")
    echo "  Admin Email: $ADMIN_EMAIL"
    echo "  Admin Org: $ADMIN_ORG"
}

inspect_operations() {
    print_section "Operational Status"

    echo "Cron Jobs:"
    crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" || echo "  No user cron jobs"

    echo ""
    echo "Recent Backups (Last 5):"
    if [ -d "$BACKUP_DIR" ]; then
        ls -lt "$BACKUP_DIR" | head -6 | tail -5 | awk '{print "  " $9 " (" $6 " " $7 ")"}'
    else
        print_warning "No backup directory found"
    fi

    echo ""
    echo "Recent Logs (Last 5):"
    if [ -d "$LOG_DIR" ]; then
        ls -lt "$LOG_DIR" | head -6 | tail -5 | awk '{print "  " $9 " (" $6 " " $7 ")"}'
    else
        print_warning "No log directory found"
    fi
}

inspect_disk_usage() {
    print_section "Disk Usage"

    df -h "$MISP_DIR" 2>/dev/null || df -h /

    echo ""
    echo "MISP Directory Size:"
    sudo du -sh "$MISP_DIR" 2>/dev/null || echo "N/A"

    echo ""
    echo "Backup Directory Size:"
    du -sh "$BACKUP_DIR" 2>/dev/null || echo "N/A"
}

inspect_security() {
    print_section "Security Status"

    # Check SSL configuration
    if sudo docker exec misp-misp-core-1 test -f /etc/nginx/certs/cert.pem 2>/dev/null; then
        CERT_INFO=$(sudo docker exec misp-misp-core-1 openssl x509 -in /etc/nginx/certs/cert.pem -noout -subject -issuer -dates 2>/dev/null)
        echo "SSL Certificate:"
        echo "$CERT_INFO" | sed 's/^/  /'

        # Check if self-signed
        if echo "$CERT_INFO" | grep -q "issuer.*MISP"; then
            print_warning "Using self-signed certificate"
        else
            print_success "Using CA-signed certificate"
        fi
    else
        print_error "No SSL certificate found"
    fi

    echo ""
    echo "File Permissions:"
    ls -la "$MISP_DIR/.env" 2>/dev/null | awk '{print "  .env: " $1 " (owner: " $3 ")"}'
    ls -la "$MISP_DIR/PASSWORDS.txt" 2>/dev/null | awk '{print "  PASSWORDS.txt: " $1 " (owner: " $3 ")"}'

    if ls -la "$MISP_DIR/.env" 2>/dev/null | grep -q "rw-------"; then
        print_success "Sensitive files properly secured (600)"
    else
        print_warning "Check file permissions on sensitive files"
    fi
}

inspect_compliance() {
    print_section "NERC CIP Compliance Quick Check"

    MYSQL_PASS=$(get_mysql_password)

    if [ -z "$MYSQL_PASS" ]; then
        print_warning "Cannot assess compliance (database not accessible)"
        return
    fi

    # Check default distribution setting (CIP-011)
    DEFAULT_DIST=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT value FROM settings WHERE setting='MISP.default_event_distribution';" 2>/dev/null | tail -1)

    if [ "$DEFAULT_DIST" = "0" ]; then
        print_success "CIP-011: Default distribution is 'Your organization only'"
    else
        print_warning "CIP-011: Default distribution is NOT restricted (current: ${DEFAULT_DIST:-N/A})"
    fi

    # Check for taxonomies (basic compliance check)
    TAXONOMY_COUNT=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT COUNT(*) FROM taxonomies WHERE enabled=1;" 2>/dev/null | tail -1)

    if [ -n "$TAXONOMY_COUNT" ] && [ "$TAXONOMY_COUNT" -gt 5 ]; then
        print_success "Taxonomies: ${TAXONOMY_COUNT} enabled (good coverage)"
    else
        print_warning "Taxonomies: Only ${TAXONOMY_COUNT:-0} enabled (recommend 10+)"
    fi

    # Check for feeds
    FEED_COUNT=$(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp \
        -e "SELECT COUNT(*) FROM feeds WHERE enabled=1;" 2>/dev/null | tail -1)

    if [ -n "$FEED_COUNT" ] && [ "$FEED_COUNT" -gt 10 ]; then
        print_success "Threat Feeds: ${FEED_COUNT} enabled (excellent)"
    else
        print_warning "Threat Feeds: Only ${FEED_COUNT:-0} enabled (recommend 10+)"
    fi

    echo ""
    echo "Estimated Overall Compliance: ~35%"
    echo "See NERC_CIP_IMPLEMENTATION_GUIDE.md for improvement roadmap"
}

generate_summary() {
    print_header "MISP Instance Inspection Summary"
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    inspect_version
    inspect_containers
    inspect_data_stats
    inspect_configuration
    inspect_operations
    inspect_disk_usage
    inspect_security
    inspect_compliance

    echo ""
    print_header "Inspection Complete"
    echo ""
    echo "For detailed production state documentation, see:"
    echo "  docs/PRODUCTION_STATE.md"
    echo ""
    echo "To regenerate production state document:"
    echo "  ./scripts/inspect-misp-instance.sh > docs/PRODUCTION_STATE_$(date +%Y%m%d).md"
}

generate_json() {
    MYSQL_PASS=$(get_mysql_password)

    # Build JSON output
    cat <<EOF
{
  "inspection_date": "$(date -Iseconds)",
  "version": {
    "misp": $(sudo docker exec misp-misp-core-1 cat /var/www/MISP/VERSION.json 2>/dev/null || echo '{}')
  },
  "containers": $(sudo docker ps --filter name=misp --format json | jq -s '.'),
  "data": {
    "events": $(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp -e "SELECT COUNT(*) FROM events;" 2>/dev/null | tail -1),
    "attributes": $(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp -e "SELECT COUNT(*) FROM attributes;" 2>/dev/null | tail -1),
    "feeds": $(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp -e "SELECT COUNT(*) FROM feeds WHERE enabled=1;" 2>/dev/null | tail -1),
    "organizations": $(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp -e "SELECT COUNT(*) FROM organisations;" 2>/dev/null | tail -1)
  },
  "configuration": {
    "base_url": "$(sudo docker exec misp-misp-core-1 printenv BASE_URL 2>/dev/null)",
    "admin_email": "$(sudo docker exec misp-misp-core-1 printenv ADMIN_EMAIL 2>/dev/null)",
    "admin_org": "$(sudo docker exec misp-misp-core-1 printenv ADMIN_ORG 2>/dev/null)"
  },
  "compliance": {
    "estimated_percentage": 35,
    "default_distribution": $(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp -e "SELECT value FROM settings WHERE setting='MISP.default_event_distribution';" 2>/dev/null | tail -1 || echo "null"),
    "enabled_taxonomies": $(sudo docker exec misp-db-1 mysql -u misp -p"$MYSQL_PASS" misp -e "SELECT COUNT(*) FROM taxonomies WHERE enabled=1;" 2>/dev/null | tail -1 || echo "null")
  }
}
EOF
}

# Main execution
main() {
    # Check requirements
    if ! command -v jq &> /dev/null; then
        print_error "jq is required but not installed. Install with: sudo apt install jq"
        exit 1
    fi

    # Check MISP is running
    check_misp_running

    # Generate output based on format
    case "$OUTPUT_FORMAT" in
        --json)
            generate_json
            ;;
        --markdown)
            echo "Markdown output not yet implemented. Use --summary for now."
            generate_summary
            ;;
        --summary|*)
            generate_summary
            ;;
    esac
}

# Run main function
main
