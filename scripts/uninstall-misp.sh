#!/bin/bash
##############################################
# MISP Complete Uninstallation Script
# GridSec - Safe MISP Removal
# Version: 1.0
##############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
MISP_DIR="/opt/misp"
BACKUP_DIR="/opt/misp-backups"

echo -e "${RED}"
cat << "EOF"
╔══════════════════════════════════════════════════╗
║                                                  ║
║          ⚠️  MISP UNINSTALLATION  ⚠️             ║
║                                                  ║
║  This will COMPLETELY REMOVE your MISP instance  ║
║                                                  ║
╚══════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "This script will remove:"
echo "  • All MISP Docker containers"
echo "  • All MISP Docker volumes (DATABASE WILL BE DELETED!)"
echo "  • All MISP Docker images"
echo "  • MISP configuration files"
echo "  • MISP directory: $MISP_DIR"
echo ""
echo -e "${YELLOW}NOTE: Backups in $BACKUP_DIR will NOT be deleted${NC}"
echo ""

# Function to ask for confirmation
confirm() {
    local prompt="$1"
    local response
    
    read -p "$prompt (type 'DELETE' to confirm): " response
    
    if [ "$response" != "DELETE" ]; then
        echo -e "${GREEN}Aborted. No changes made.${NC}"
        exit 0
    fi
}

# Function to create final backup
create_final_backup() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Would you like to create a final backup before uninstalling?"
    read -p "Create backup? (yes/no): " response

    if [ "$response" = "yes" ]; then
        if [ -f "/opt/misp/scripts/backup-misp.sh" ]; then
            echo -e "${BLUE}[INFO]${NC} Creating final backup..."
            bash "/opt/misp/scripts/backup-misp.sh"
            echo -e "${GREEN}[SUCCESS]${NC} Backup completed"
        else
            echo -e "${YELLOW}[WARNING]${NC} Backup script not found, skipping..."
        fi
    fi
}

# Function to stop and remove containers
remove_containers() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Stopping MISP containers..."

    if [ -d "$MISP_DIR" ]; then
        cd "$MISP_DIR"

        # Stop all containers
        if sudo docker compose ps | grep -q "Up"; then
            sudo docker compose down
            echo -e "${GREEN}[SUCCESS]${NC} Containers stopped"
        else
            echo -e "${YELLOW}[INFO]${NC} No running containers found"
        fi
    else
        echo -e "${YELLOW}[INFO]${NC} MISP directory not found"
    fi
}

# Function to remove volumes
remove_volumes() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Removing MISP Docker volumes..."

    # Get all MISP-related volumes
    VOLUMES=$(sudo docker volume ls -q | grep misp || true)

    if [ -n "$VOLUMES" ]; then
        echo "$VOLUMES" | while read -r volume; do
            echo "  Removing volume: $volume"
            sudo docker volume rm "$volume" 2>/dev/null || true
        done
        echo -e "${GREEN}[SUCCESS]${NC} Volumes removed"
    else
        echo -e "${YELLOW}[INFO]${NC} No MISP volumes found"
    fi
}

# Function to remove images
remove_images() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Removing MISP Docker images..."

    # Get all MISP-related images
    IMAGES=$(sudo docker images | grep -E "misp|ghcr.io/misp" | awk '{print $3}' || true)

    if [ -n "$IMAGES" ]; then
        echo "$IMAGES" | while read -r image; do
            echo "  Removing image: $image"
            sudo docker rmi -f "$image" 2>/dev/null || true
        done
        echo -e "${GREEN}[SUCCESS]${NC} Images removed"
    else
        echo -e "${YELLOW}[INFO]${NC} No MISP images found"
    fi
}

# Function to remove MISP directory
remove_misp_directory() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Removing MISP directory..."

    if [ -d "$MISP_DIR" ]; then
        # List what will be deleted
        echo "  Contents to be deleted:"
        sudo ls -la "$MISP_DIR" | head -10
        echo "  ..."

        # Remove directory
        sudo rm -rf "$MISP_DIR"
        echo -e "${GREEN}[SUCCESS]${NC} MISP directory removed"
    else
        echo -e "${YELLOW}[INFO]${NC} MISP directory not found"
    fi
}

# Function to clean up hosts file
cleanup_hosts_file() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Cleaning up /etc/hosts..."
    
    # Remove MISP entries from hosts file
    if grep -q "misp" /etc/hosts 2>/dev/null; then
        sudo sed -i '/misp/d' /etc/hosts
        echo -e "${GREEN}[SUCCESS]${NC} Hosts file cleaned"
    else
        echo -e "${YELLOW}[INFO]${NC} No MISP entries in hosts file"
    fi
}

# Function to remove installation state
remove_state_files() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Removing installation state files..."

    if [ -f "/var/lib/misp-install-state.json" ]; then
        sudo rm "/var/lib/misp-install-state.json"
        echo -e "${GREEN}[SUCCESS]${NC} State file removed"
    else
        echo -e "${YELLOW}[INFO]${NC} No state file found"
    fi
}

# Function to remove logs (optional)
remove_logs() {
    echo ""
    read -p "Remove installation logs from /var/log/misp-install? (yes/no): " response

    if [ "$response" = "yes" ]; then
        if [ -d "/var/log/misp-install" ]; then
            sudo rm -rf "/var/log/misp-install"
            echo -e "${GREEN}[SUCCESS]${NC} Logs removed"
        else
            echo -e "${YELLOW}[INFO]${NC} No log directory found"
        fi
    else
        echo -e "${BLUE}[INFO]${NC} Logs preserved in /var/log/misp-install"
    fi
}

# Function to remove scripts (optional)
remove_scripts() {
    echo ""
    read -p "Remove MISP installation scripts from /opt/misp/scripts? (yes/no): " response

    if [ "$response" = "yes" ]; then
        echo -e "${BLUE}[INFO]${NC} Removing scripts..."

        if [ -d "/opt/misp/scripts" ]; then
            sudo rm -rf "/opt/misp/scripts"
            echo -e "${GREEN}[SUCCESS]${NC} Scripts removed"
        else
            echo -e "${YELLOW}[INFO]${NC} Scripts directory not found"
        fi
    else
        echo -e "${BLUE}[INFO]${NC} Scripts preserved"
    fi
}

# Function to show backup info
show_backup_info() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              BACKUP INFORMATION                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        echo "Backups are preserved in: $BACKUP_DIR"
        echo ""
        echo "Available backups:"
        ls -lh "$BACKUP_DIR" | grep "misp-backup" | tail -5
        echo ""
        echo "To restore MISP from backup:"
        echo "  1. Reinstall MISP using: python3 misp-install.py"
        echo "  2. Follow restore instructions in TROUBLESHOOTING.md"
    else
        echo -e "${YELLOW}No backups found${NC}"
        echo ""
        echo "If you need to reinstall MISP, download the installation script:"
        echo "  python3 misp-install.py"
    fi
}

# Function to remove Docker completely (optional)
remove_docker() {
    echo ""
    echo -e "${YELLOW}[WARNING]${NC} Do you want to remove Docker completely?"
    echo "This will affect ALL Docker containers and images on this system,"
    echo "not just MISP!"
    echo ""
    read -p "Remove Docker? (yes/no): " response
    
    if [ "$response" = "yes" ]; then
        echo -e "${BLUE}[INFO]${NC} Removing Docker..."
        
        # Stop Docker service
        sudo systemctl stop docker
        
        # Remove Docker packages
        sudo apt purge -y docker-ce docker-ce-cli containerd.io \
            docker-buildx-plugin docker-compose-plugin 2>/dev/null || true
        
        # Remove Docker directories
        sudo rm -rf /var/lib/docker
        sudo rm -rf /var/lib/containerd
        sudo rm -rf /etc/docker
        
        # Remove Docker group
        sudo groupdel docker 2>/dev/null || true
        
        echo -e "${GREEN}[SUCCESS]${NC} Docker removed"
    else
        echo -e "${BLUE}[INFO]${NC} Docker preserved"
    fi
}

# Function to show final summary
show_summary() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         UNINSTALLATION COMPLETE                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "The following items have been removed:"
    echo "  ✓ MISP containers"
    echo "  ✓ MISP volumes (including database)"
    echo "  ✓ MISP images"
    echo "  ✓ MISP directory"
    echo "  ✓ MISP entries in /etc/hosts"
    echo "  ✓ Installation state files"
    echo ""
    echo "Preserved items:"
    echo "  • Backups: $BACKUP_DIR"

    if [ -d "/var/log/misp-install" ]; then
        echo "  • Logs: /var/log/misp-install"
    fi
    
    echo ""
    echo "To reinstall MISP in the future:"
    echo "  python3 misp-install.py"
    echo ""
    echo -e "${GREEN}Thank you for using MISP!${NC}"
}

# Main execution
main() {
    # First confirmation
    confirm "Are you absolutely sure you want to uninstall MISP?"
    
    # Offer backup
    create_final_backup
    
    # Second confirmation
    echo ""
    echo -e "${RED}FINAL WARNING:${NC} This will DELETE your MISP database and all configuration!"
    confirm "Proceed with uninstallation?"
    
    # Execute removal steps
    remove_containers
    remove_volumes
    remove_images
    remove_misp_directory
    cleanup_hosts_file
    remove_state_files
    remove_logs
    remove_scripts
    
    # Optional: Remove Docker
    remove_docker
    
    # Show backup information
    show_backup_info
    
    # Show summary
    show_summary
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} Don't run this script as root!"
    echo "Run as regular user: bash uninstall-misp.sh"
    exit 1
fi

# Run main function
main

# Exit
exit 0