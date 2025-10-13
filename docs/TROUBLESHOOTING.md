# MISP Installation Troubleshooting Guide

Complete troubleshooting guide for common MISP installation and runtime issues.

## 🔍 Quick Diagnostics

### Run Full Diagnostic
```bash
cd /opt/misp

echo "=== Container Status ==="
sudo docker compose ps

echo -e "\n=== Recent Logs ==="
sudo docker compose logs --tail=50

echo -e "\n=== Disk Usage ==="
df -h
docker system df

echo -e "\n=== Memory Usage ==="
free -h
docker stats --no-stream

echo -e "\n=== Network ==="
ss -tuln | grep -E ':(80|443|3306|6379)'

echo -e "\n=== Docker Group ==="
groups | grep docker
```

## 🚨 Installation Issues

### Issue: "Python version too old"
**Error:** `❌ Python 3.8 or higher required`

**Solution:**
```bash
# Check current version
python3 --version

# Install Python 3.8+ on Ubuntu 20.04+
sudo apt update
sudo apt install python3.8 python3-pip

# Verify
python3 --version
```

---

### Issue: "Script should not be run as root"
**Error:** `❌ Don't run this script as root!`

**Solution:**
```bash
# Exit root shell
exit

# Run as regular user
cd /home/yourusername
python3 misp-install.py
```

---

### Issue: "Pre-flight checks failed - Insufficient disk space"
**Error:** `Insufficient disk space: 15GB available, 20GB required`

**Solution:**
```bash
# Check disk usage
df -h

# Clean up space
sudo apt clean
sudo apt autoremove

# Clean Docker (if Docker installed)
docker system prune -af --volumes

# Check again
df -h
```

---

### Issue: "Pre-flight checks failed - Insufficient RAM"
**Error:** `Insufficient RAM: 2GB available, 4GB required`

**Solution:**
- Upgrade server RAM to minimum 4GB
- Or use a larger VM/instance
- For testing only: Use `--skip-checks` flag (NOT recommended for production)

---

### Issue: "Port 443 already in use"
**Error:** `Ports already in use: 443`

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :443
# or
sudo ss -tulpn | grep :443

# If it's Apache
sudo systemctl stop apache2
sudo systemctl disable apache2

# If it's Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# Verify port is free
sudo lsof -i :443
```

---

### Issue: "Docker not installed"
**Error:** `Docker not installed`

**Solution:**
```bash
# The script should install Docker automatically
# If it fails, install manually:

# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Verify
docker --version
docker compose version
```

---

### Issue: "Docker group not active"
**Error:** User not in docker group or group not active

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Activate immediately (option 1)
newgrp docker

# Or logout and login again (option 2)
exit
# Then SSH back in

# Verify
groups | grep docker
docker ps
```

---

### Issue: "Git clone failed"
**Error:** `fatal: unable to access 'https://github.com/MISP/misp-docker.git/'`

**Solution:**
```bash
# Check internet connectivity
ping -c 3 github.com

# Check DNS
nslookup github.com

# Try manual clone
cd ~
git clone https://github.com/MISP/misp-docker.git

# If behind proxy, configure git
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy http://proxy.example.com:8080
```

---

### Issue: "Installation interrupted"
**Error:** User pressed Ctrl+C or connection lost

**Solution:**
```bash
# Resume from last checkpoint
python3 misp-install.py --resume

# Check what phase it was on
cat ~/.misp-install-state.json

# If state file corrupted, start fresh
rm ~/.misp-install-state.json
python3 misp-install.py
```

## 🐋 Docker Issues

### Issue: "Container won't start"
**Symptoms:** Container immediately exits

**Diagnosis:**
```bash
cd /opt/misp

# Check all container status
sudo docker compose ps

# View logs for specific container
sudo docker compose logs misp-core
sudo docker compose logs db
sudo docker compose logs redis

# Check for specific errors
sudo docker compose logs | grep -i error
```

**Solutions:**

**Database won't start:**
```bash
# Check database logs
sudo docker compose logs db | tail -100

# Common issue: Corrupted database
sudo docker compose down
sudo docker volume rm misp-docker_mysql_data
sudo docker compose up -d

# Wait and check
sudo docker compose logs db -f
```

**MISP core won't start:**
```bash
# Check for configuration errors
sudo cat /opt/misp/.env | grep -v "^#"

# Restart
sudo docker compose restart misp-core

# If still failing, rebuild
sudo docker compose down
sudo docker compose up -d --build
```

---

### Issue: "misp-modules unhealthy"
**Error:** Container shows "unhealthy" status

**Solution:**
```bash
cd /opt/misp

# Check module status
sudo docker compose ps misp-modules

# View detailed logs
sudo docker compose logs misp-modules --tail=100

# Test module endpoint
curl -s http://localhost:6666/modules | jq

# Restart modules
sudo docker compose restart misp-modules

# Give it time to initialize (3-5 minutes)
sleep 180

# Check again
sudo docker compose ps misp-modules
```

---

### Issue: "Database connection failed"
**Error:** Can't connect to database from MISP core

**Diagnosis:**
```bash
cd /opt/misp

# Check if database is running
sudo docker compose ps db

# Check database logs
sudo docker compose logs db | tail -50

# Test database connection
sudo docker compose exec db mysql -umisp -p
# Enter password from PASSWORDS.txt
```

**Solution:**
```bash
# Verify password in .env
grep MYSQL_PASSWORD /opt/misp/.env

# Restart database
sudo docker compose restart db

# Wait for healthy status
sudo docker compose ps

# If password mismatch, update .env and recreate
sudo docker compose down
# Edit .env with correct password
sudo docker compose up -d
```

---

### Issue: "Redis connection failed"
**Error:** MISP can't connect to Redis

**Solution:**
```bash
cd /opt/misp

# Check Redis status
sudo docker compose ps redis

# Test Redis connection
sudo docker compose exec redis redis-cli ping
# Should return: PONG

# View Redis logs
sudo docker compose logs redis

# Restart Redis
sudo docker compose restart redis
```

---

### Issue: "Out of disk space"
**Error:** Docker operations fail due to disk space

**Solution:**
```bash
# Check disk usage
df -h
docker system df

# Clean up Docker
docker system prune -af --volumes

# Clean up old images
docker image prune -af

# Clean up old logs
sudo journalctl --vacuum-time=3d

# Clean apt cache
sudo apt clean

# Check again
df -h
```

## 🌐 Web Interface Issues

### Issue: "Can't access https://misp.lan"
**Error:** Browser can't connect or times out

**Diagnosis:**
```bash
# 1. Check if containers running
cd /opt/misp
sudo docker compose ps

# 2. Check if MISP core is healthy
sudo docker compose ps misp-core

# 3. Check logs
sudo docker compose logs misp-core --tail=50

# 4. Test from server
curl -k https://localhost
curl -k https://misp.lan

# 5. Check ports
sudo ss -tulpn | grep -E ':(80|443)'

# 6. Check DNS/hosts
grep misp /etc/hosts
ping misp.lan
```

**Solutions:**

**Hosts file not configured:**
```bash
# On server
sudo bash -c 'echo "127.0.0.1 misp.lan" >> /etc/hosts'
sudo bash -c 'echo "192.168.20.95 misp.lan" >> /etc/hosts'

# On workstation (Linux/Mac)
echo "192.168.20.95 misp.lan" | sudo tee -a /etc/hosts

# On workstation (Windows - Run as Admin)
Add-Content C:\Windows\System32\drivers\etc\hosts "`n192.168.20.95 misp.lan"
```

**Firewall blocking:**
```bash
# Check firewall status
sudo ufw status

# Allow HTTPS
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

# Or disable firewall (testing only)
sudo ufw disable
```

**Container not ready:**
```bash
# Wait for initialization (5-10 minutes on first start)
cd /opt/misp
sudo docker compose logs misp-core -f
# Wait for "INIT | Done"
```

---

### Issue: "SSL certificate error"
**Error:** Browser shows certificate warning

**Solution:**
```bash
# This is EXPECTED for self-signed certificates

# Option 1: Accept the warning (temporary)
# Click "Advanced" → "Proceed anyway"

# Option 2: Add exception (permanent)
# Firefox: Add Exception → Confirm
# Chrome: Type "thisisunsafe" on warning page

# Option 3: Get proper SSL certificate
# Use Let's Encrypt:
sudo apt install certbot
sudo certbot certonly --standalone -d misp.yourdomain.com

# Then update docker-compose.override.yml to use new certs
```

---

### Issue: "Login page not loading"
**Error:** Blank page or 500 error

**Diagnosis:**
```bash
cd /opt/misp

# Check MISP core logs
sudo docker compose logs misp-core | tail -100

# Check for PHP errors
sudo docker compose exec misp-core cat /var/www/MISP/app/tmp/logs/error.log

# Check database connection
sudo docker compose exec misp-core cat /var/www/MISP/app/tmp/logs/debug.log
```

**Solution:**
```bash
# Restart MISP core
sudo docker compose restart misp-core

# Wait 30 seconds
sleep 30

# Clear browser cache and try again

# If still failing, check database
sudo docker compose exec db mysql -umisp -p -e "USE misp; SHOW TABLES;"
```

---

### Issue: "Can't login - Invalid credentials"
**Error:** Username/password not working

**Solution:**
```bash
# 1. Check your credentials
cat /opt/misp/PASSWORDS.txt

# 2. Default credentials:
# Email: admin@admin.test  (if you didn't change it)
# Check ADMIN_EMAIL in .env

# 3. Reset admin password
cd /opt/misp
sudo docker compose exec misp-core /var/www/MISP/app/Console/cake user change_pw admin@admin.test

# Follow prompts to set new password

# 4. Or reset to password from .env
sudo docker compose down
sudo docker compose up -d
# Wait for full initialization
```

---

### Issue: "Page loads but looks broken"
**Error:** CSS/styling not loading

**Solution:**
```bash
# Clear browser cache (Ctrl+Shift+Delete)

# Check MISP core logs for asset errors
cd /opt/misp
sudo docker compose logs misp-core | grep -i "css\|js\|asset"

# Restart with clean cache
sudo docker compose down
sudo docker compose up -d

# Try different browser
```

## 📊 Performance Issues

### Issue: "MISP is very slow"
**Symptoms:** Pages take long to load, timeouts

**Diagnosis:**
```bash
# Check resource usage
docker stats --no-stream

# Check disk I/O
iostat -x 1 5

# Check database performance
cd /opt/misp
sudo docker compose exec db mysql -umisp -p -e "SHOW PROCESSLIST;"

# Check worker status
sudo docker compose exec misp-core ps aux | grep worker
```

**Solutions:**

**Increase PHP memory:**
```bash
# Edit .env
nano /opt/misp/.env

# Increase PHP_MEMORY_LIMIT
PHP_MEMORY_LIMIT=4096M

# Restart
sudo docker compose restart misp-core
```

**Increase workers:**
```bash
# Edit .env
nano /opt/misp/.env

# Add or modify
WORKERS=8

# Restart
sudo docker compose down
sudo docker compose up -d
```

**Optimize database:**
```bash
cd /opt/misp
sudo docker compose exec db mysql -umisp -p misp -e "OPTIMIZE TABLE events;"
sudo docker compose exec db mysql -umisp -p misp -e "OPTIMIZE TABLE attributes;"
```

---

### Issue: "Running out of memory"
**Error:** OOM killer, containers crash

**Solution:**
```bash
# Check memory usage
free -h
docker stats

# Restart services
sudo docker compose restart

# Reduce PHP memory if server RAM limited
nano /opt/misp/.env
# PHP_MEMORY_LIMIT=1024M

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🔧 Maintenance Issues

### Issue: "How to update MISP"
**Solution:**
```bash
cd /opt/misp

# Backup first!
./backup-misp.py  # If you created the backup script

# Or manual backup
sudo docker compose exec -T db mysqldump -umisp -p misp > backup.sql

# Pull latest images
sudo docker compose pull

# Restart with new images
sudo docker compose down
sudo docker compose up -d

# Check logs
sudo docker compose logs -f
```

---

### Issue: "How to backup MISP"
**Solution:**
```bash
# Create backup script
cat > ~/backup-misp.py << 'EOF'
#!/bin/bash
BACKUP_DIR=/opt/misp-backups/$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

cd /opt/misp

# Backup configuration
cp .env $BACKUP_DIR/
cp PASSWORDS.txt $BACKUP_DIR/
cp -r ssl $BACKUP_DIR/

# Backup database
sudo docker compose exec -T db mysqldump -umisp -p"$(grep MYSQL_PASSWORD .env | cut -d= -f2)" misp > $BACKUP_DIR/misp.sql

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR/
rm -rf $BACKUP_DIR/

echo "Backup: $BACKUP_DIR.tar.gz"
EOF

chmod +x ~/backup-misp.py

# Run backup
~/backup-misp.py

# Schedule with cron
crontab -e
# Add: 0 2 * * * /home/yourusername/backup-misp.py
```

---

### Issue: "How to restore from backup"
**Solution:**
```bash
# Extract backup
tar -xzf misp-backups/backup-YYYYMMDD.tar.gz

# Stop MISP
cd /opt/misp
sudo docker compose down

# Restore configuration
cp backup-YYYYMMDD/.env /opt/misp/
cp backup-YYYYMMDD/PASSWORDS.txt /opt/misp/
cp -r backup-YYYYMMDD/ssl /opt/misp/

# Start database only
sudo docker compose up -d db

# Wait for database
sleep 30

# Restore database
sudo docker compose exec -T db mysql -umisp -p"$(grep MYSQL_PASSWORD .env | cut -d= -f2)" misp < backup-YYYYMMDD/misp.sql

# Start all services
sudo docker compose up -d

# Verify
sudo docker compose ps
```

## 📞 Getting Help

### Collect Diagnostic Information
Before asking for help, collect this information:

```bash
# Run diagnostic collection script
cat > ~/collect-diagnostics.sh << 'EOF'
#!/bin/bash
OUT=~/misp-diagnostics-$(date +%Y%m%d_%H%M%S).txt

{
  echo "=== System Info ==="
  uname -a
  cat /etc/os-release
  
  echo -e "\n=== Python Version ==="
  python3 --version
  
  echo -e "\n=== Docker Version ==="
  docker --version
  docker compose version
  
  echo -e "\n=== Container Status ==="
  cd /opt/misp
  sudo docker compose ps
  
  echo -e "\n=== Recent Logs ==="
  sudo docker compose logs --tail=200
  
  echo -e "\n=== Disk Usage ==="
  df -h
  docker system df
  
  echo -e "\n=== Memory ==="
  free -h
  
  echo -e "\n=== Network ==="
  ss -tuln | grep -E ':(80|443|3306|6379)'
  
  echo -e "\n=== Configuration (sanitized) ==="
  grep -v "PASSWORD\|KEY\|PASSPHRASE" /opt/misp/.env
  
} > $OUT

echo "Diagnostics saved to: $OUT"
echo "Share this file when asking for help (passwords removed)"
EOF

chmod +x ~/collect-diagnostics.sh
~/collect-diagnostics.sh
```

### Where to Get Help
1. **Check logs:** `/opt/misp/logs/`
2. **MISP Documentation:** https://www.misp-project.org/documentation/
3. **MISP Community:** https://www.misp-project.org/community/
4. **GitHub Issues:** https://github.com/MISP/MISP/issues
5. **Gitter Chat:** https://gitter.im/MISP/MISP

### When Asking for Help, Provide:
- Output from `collect-diagnostics.sh`
- Installation method used (interactive/config file)
- Phase where it failed (if during installation)
- Exact error message
- Steps to reproduce
- What you've already tried

---

**💡 Pro Tip:** Always check the logs first! 90% of issues can be diagnosed from logs:
```bash
cd /opt/misp
sudo docker compose logs | grep -i error
```