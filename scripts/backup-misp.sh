#!/bin/bash
##############################################
# MISP Backup Script
# GridSec - Complete Backup Solution
# Version: 1.0
##############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
MISP_DIR="/opt/misp"
BACKUP_BASE_DIR="$HOME/misp-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/misp-backup-$TIMESTAMP"
RETENTION_DAYS=30  # Keep backups for 30 days

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_misp_dir() {
    if [ ! -d "$MISP_DIR" ]; then
        log_error "MISP directory not found: $MISP_DIR"
        exit 1
    fi
}

create_backup_dir() {
    log_info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    chmod 755 "$BACKUP_DIR"
}

backup_configuration() {
    log_info "Backing up configuration files..."

    if [ -f "$MISP_DIR/.env" ]; then
        cp "$MISP_DIR/.env" "$BACKUP_DIR/"
        log_success "Backed up .env"
    else
        log_warning ".env file not found"
    fi

    if [ -f "$MISP_DIR/PASSWORDS.txt" ]; then
        cp "$MISP_DIR/PASSWORDS.txt" "$BACKUP_DIR/"
        log_success "Backed up PASSWORDS.txt"
    else
        log_warning "PASSWORDS.txt not found"
    fi

    if [ -f "$MISP_DIR/docker-compose.yml" ]; then
        cp "$MISP_DIR/docker-compose.yml" "$BACKUP_DIR/"
        log_success "Backed up docker-compose.yml"
    fi

    if [ -f "$MISP_DIR/docker-compose.override.yml" ]; then
        cp "$MISP_DIR/docker-compose.override.yml" "$BACKUP_DIR/"
        log_success "Backed up docker-compose.override.yml"
    fi
}

backup_ssl_certificates() {
    log_info "Backing up SSL certificates..."

    if [ -d "$MISP_DIR/ssl" ]; then
        cp -r "$MISP_DIR/ssl" "$BACKUP_DIR/"
        log_success "Backed up SSL certificates"
    else
        log_warning "SSL directory not found"
    fi
}

backup_database() {
    log_info "Backing up MySQL database..."
    
    cd "$MISP_DIR"

    # Check if database container is running
    if ! docker compose ps db | grep -q "Up"; then
        log_warning "Database container is not running, skipping database backup"
        return
    fi

    # Get MySQL password from .env
    if [ -f ".env" ]; then
        MYSQL_PASSWORD=$(grep "^MYSQL_PASSWORD=" .env | cut -d= -f2)

        if [ -n "$MYSQL_PASSWORD" ]; then
            log_info "Dumping database (this may take a few minutes)..."

            if docker compose exec -T db mysqldump \
                -umisp \
                -p"$MYSQL_PASSWORD" \
                --single-transaction \
                --quick \
                --lock-tables=false \
                misp > "$BACKUP_DIR/misp_database.sql" 2>/dev/null; then

                log_success "Database backed up successfully"

                # Get database size
                DB_SIZE=$(du -h "$BACKUP_DIR/misp_database.sql" | cut -f1)
                log_info "Database backup size: $DB_SIZE"
            else
                log_error "Database backup failed"
                return 1
            fi
        else
            log_warning "MySQL password not found in .env"
        fi
    else
        log_warning ".env file not found, cannot backup database"
    fi
}

backup_attachments() {
    log_info "Backing up MISP attachments..."

    # Check if attachments directory exists in volume
    if docker compose exec -T misp-core test -d /var/www/MISP/app/files 2>/dev/null; then
        log_info "Copying attachments from container..."

        # Create attachments directory in backup
        mkdir -p "$BACKUP_DIR/attachments"

        # Copy attachments from container
        docker compose cp misp-core:/var/www/MISP/app/files "$BACKUP_DIR/attachments/" 2>/dev/null || {
            log_warning "Could not backup attachments (container might not be running)"
            return
        }

        # Get attachments size
        if [ -d "$BACKUP_DIR/attachments" ]; then
            ATTACH_SIZE=$(du -sh "$BACKUP_DIR/attachments" | cut -f1)
            log_success "Attachments backed up successfully ($ATTACH_SIZE)"
        fi
    else
        log_warning "Attachments directory not accessible"
    fi
}

create_backup_metadata() {
    log_info "Creating backup metadata..."

    tee "$BACKUP_DIR/backup_info.txt" > /dev/null << EOF
MISP Backup Information
=======================
Backup Date: $(date)
Backup Directory: $BACKUP_DIR
MISP Directory: $MISP_DIR
Hostname: $(hostname)

Backup Contents:
- Configuration files (.env, docker-compose.yml)
- SSL certificates
- MySQL database dump
- Attachments (if accessible)

Container Status at Backup Time:
$(cd "$MISP_DIR" && docker compose ps 2>/dev/null || echo "Could not get container status")

Disk Usage:
$(df -h "$MISP_DIR" | tail -1)

Backup Size:
$(du -sh "$BACKUP_DIR" | cut -f1)
EOF
    
    log_success "Backup metadata created"
}

compress_backup() {
    log_info "Compressing backup..."

    cd "$BACKUP_BASE_DIR"

    ARCHIVE_NAME="misp-backup-$TIMESTAMP.tar.gz"

    if tar -czf "$ARCHIVE_NAME" "misp-backup-$TIMESTAMP" 2>/dev/null; then
        # Remove uncompressed directory
        rm -rf "misp-backup-$TIMESTAMP"

        ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
        log_success "Backup compressed: $ARCHIVE_NAME ($ARCHIVE_SIZE)"
        
        echo ""
        echo "=========================================="
        echo -e "${GREEN}BACKUP COMPLETED SUCCESSFULLY${NC}"
        echo "=========================================="
        echo "Location: $BACKUP_BASE_DIR/$ARCHIVE_NAME"
        echo "Size: $ARCHIVE_SIZE"
        echo ""
    else
        log_error "Failed to compress backup"
        return 1
    fi
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."

    cd "$BACKUP_BASE_DIR"

    # Find and delete old backups
    DELETED=$(find . -name "misp-backup-*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)
    
    if [ "$DELETED" -gt 0 ]; then
        log_success "Deleted $DELETED old backup(s)"
    else
        log_info "No old backups to delete"
    fi
}

verify_backup() {
    log_info "Verifying backup integrity..."

    cd "$BACKUP_BASE_DIR"
    ARCHIVE_NAME="misp-backup-$TIMESTAMP.tar.gz"

    if tar -tzf "$ARCHIVE_NAME" >/dev/null 2>&1; then
        log_success "Backup archive is valid"
        return 0
    else
        log_error "Backup archive is corrupted!"
        return 1
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "MISP Backup Script"
    echo "=========================================="
    echo ""
    
    check_misp_dir
    create_backup_dir
    backup_configuration
    backup_ssl_certificates
    backup_database
    backup_attachments
    create_backup_metadata
    compress_backup
    verify_backup
    cleanup_old_backups
    
    echo ""
    echo "To restore this backup, run:"
    echo "  cd $BACKUP_BASE_DIR"
    echo "  tar -xzf misp-backup-$TIMESTAMP.tar.gz"
    echo "  # Then follow restore instructions in TROUBLESHOOTING.md"
    echo ""
    
    log_success "Backup process completed!"
}

# Run main function
main

# Exit with success
exit 0