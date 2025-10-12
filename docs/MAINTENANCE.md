# MISP Maintenance Guide

Complete guide for ongoing MISP maintenance, updates, and optimization.

## 📅 Daily Tasks

### Quick Health Check
Run this every morning:

```bash
#!/bin/bash
# Save as: ~/daily-health-check.sh

cd /opt/misp

echo "=== MISP Daily Health Check - $(date) ==="

echo -e "\n1. Container Status:"
sudo docker compose ps

echo -e "\n2. Disk Usage:"
df -h ~ | grep -v tmpfs

echo -e "\n3. Recent Errors:"
sudo docker compose logs --since 24h | grep -i error | tail -10

echo -e "\n4. Worker Status:"
sudo docker compose exec misp-core ps aux | grep worker | head -5

echo -e "\n5. Database Size:"
sudo docker compose exec -T db mysql -umisp -p"$(grep MYSQL_PASSWORD .env | cut -d= -f2)" \
  -e "SELECT table_schema AS 'Database', 
      ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' 
      FROM information_schema.tables 
      WHERE table_schema = 'misp' 
      GROUP BY table_schema;"

echo -e "\n=== Health Check Complete ==="
```

Make it executable and run:
```bash
chmod +x ~/daily-health-check.sh
~/daily-health-check.sh
```

### Monitor Logs
```bash
# View real-time logs
cd /opt/misp
sudo docker compose logs -f

# View only errors
sudo docker compose logs | grep -i error

# View specific service
sudo docker compose logs misp-core -f
```

## 📆 Weekly Tasks

### 1. Backup
```bash
# Run backup script
~/backup-misp.sh

# Verify backup exists
ls -lh /opt/misp-backups/ | tail -5

# Test backup integrity
cd /opt/misp-backups
tar -tzf misp-backup-*.tar.gz | head
```

### 2. Check Disk Space
```bash
# System disk usage
df -h

# Docker disk usage
docker system df

# MISP directory usage
du -sh /opt/misp

# Clean up if needed
docker system prune -f
sudo journalctl --vacuum-time=7d
```

### 3. Review Security Logs
```bash
cd /opt/misp

# Check authentication failures
sudo docker compose logs misp-core | grep -i "authentication\|login" | grep -i "fail"

# Check for suspicious activity
sudo docker compose logs misp-core | grep -i "unauthorized\|forbidden\|attack"

# Review audit logs in MISP web interface
# Administration → Audit Actions → List Logs
```

### 4. Monitor Performance
```bash
# Container resource usage
docker stats --no-stream

# Database performance
cd /opt/misp
sudo docker compose exec db mysql -umisp -p -e "SHOW PROCESSLIST;"

# Slow queries
sudo docker compose exec db mysql -umisp -p -e "SHOW VARIABLES LIKE 'slow_query%';"
```

## 📅 Monthly Tasks

### 1. Update MISP
```bash
# IMPORTANT: Backup first!
~/backup-misp.sh

cd /opt/misp

# Pull latest images
sudo docker compose pull

# Review changelog
echo "Check: https://github.com/MISP/MISP/releases"

# Update containers
sudo docker compose down
sudo docker compose up -d

# Wait for initialization
sleep 120

# Verify
sudo docker compose ps
sudo docker compose logs misp-core | tail -50
```

### 2. Database Maintenance
```bash
cd /opt/misp

# Optimize tables
sudo docker compose exec db mysql -umisp -p misp << 'EOF'
OPTIMIZE TABLE attributes;
OPTIMIZE TABLE events;
OPTIMIZE TABLE objects;
OPTIMIZE TABLE correlations;
ANALYZE TABLE attributes;
ANALYZE TABLE events;
EOF

# Check database integrity
sudo docker compose exec db mysqlcheck -umisp -p --check --databases misp

# Clean up old data (if needed)
# Be careful with this - only delete what you don't need!
# sudo docker compose exec db mysql -umisp -p misp -e "DELETE FROM logs WHERE created < DATE_SUB(NOW(), INTERVAL 6 MONTH);"
```

### 3. SSL Certificate Check
```bash
# Check certificate expiry
openssl x509 -enddate -noout -in /opt/misp/ssl/cert.pem

# If using Let's Encrypt, renew
# sudo certbot renew --dry-run
```

### 4. Review User Accounts
```bash
# In MISP web interface:
# 1. Go to Administration → List Users
# 2. Review all accounts
# 3. Disable inactive accounts
# 4. Check for proper role assignments
# 5. Verify 2FA is enabled for admins
```

### 5. Update System Packages
```bash
# Update server packages
sudo apt update
sudo apt upgrade -y

# Check if reboot required
[ -f /var/run/reboot-required ] && echo "Reboot required" || echo "No reboot needed"

# If reboot needed:
# sudo reboot
```

## 📅 Quarterly Tasks

### 1. Security Audit
```bash
# Review user permissions
# Check MISP web interface: Administration → List Users

# Review API keys
# Check MISP web interface: Administration → List Auth Keys

# Check for outdated software
docker images | grep misp

# Review firewall rules
sudo ufw status verbose

# Check for security updates
apt list --upgradable | grep security
```

### 2. Performance Tuning
```bash
# Review and adjust PHP settings
nano /opt/misp/.env
# Adjust PHP_MEMORY_LIMIT based on usage
# Adjust WORKERS based on load

# Review database configuration
cd /opt/misp
sudo docker compose exec db mysql -umisp -p -e "SHOW VARIABLES LIKE '%buffer%';"

# Restart to apply changes
sudo docker compose restart
```

### 3. Test Backup Restoration
```bash
# CRITICAL: Test your backups actually work!

# 1. Create fresh backup
~/backup-misp.sh

# 2. On test server/VM, restore backup
# Follow restore instructions in TROUBLESHOOTING.md

# 3. Verify all data is present
# 4. Document any issues
# 5. Update backup procedures if needed
```

### 4. Review and Clean Old Data
```bash
# In MISP web interface:
# 1. Administration → Jobs
#    - Clean up old jobs
# 2. Event Actions → List Events
#    - Archive or delete very old events
# 3. Administration → Server Settings
#    - Review and adjust data retention policies
```

## 📅 Annual Tasks

### 1. Major Version Upgrades
```bash
# Plan major upgrades carefully
# 1. Review release notes
# 2. Test in staging environment
# 3. Schedule maintenance window
# 4. Create full backup
# 5. Perform upgrade
# 6. Test thoroughly
# 7. Monitor for issues
```

### 2. SSL Certificate Renewal
```bash
# If using self-signed (expires in 1 year):
cd /opt/misp/ssl

# Backup old certificate
cp cert.pem cert.pem.old
cp key.pem key.pem.old

# Generate new certificate
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=US/ST=New York/L=New York/O=YourOrg/OU=IT/CN=misp.lan"

# Restart MISP
sudo docker compose restart misp-core
```

### 3. Security Compliance Review
- Review access logs
- Update security policies
- Conduct penetration testing
- Review and update disaster recovery plan
- Update documentation
- Train team on security best practices

### 4. Capacity Planning
```bash
# Review growth trends
# Database size trend
# User growth
# Event/attribute growth
# Plan hardware upgrades if needed
```

## 🔧 Optimization Tips

### Database Optimization
```bash
cd /opt/misp

# Enable slow query log
sudo docker compose exec db mysql -umisp -p << 'EOF'
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';
EOF

# Review slow queries later
sudo docker compose exec db tail /var/log/mysql/slow-query.log
```

### Worker Optimization
```bash
# Check worker status
cd /opt/misp
sudo docker compose exec misp-core supervisorctl status

# Adjust workers based on load
nano /opt/misp/.env
# WORKERS=8  # Adjust based on CPU cores

sudo docker compose restart misp-core
```

### Cache Optimization
```bash
# Clear Redis cache if needed
cd /opt/misp
sudo docker compose exec redis redis-cli FLUSHALL

# Restart services
sudo docker compose restart
```

## 📊 Monitoring Setup

### Set Up Automated Monitoring
```bash
# Create monitoring script
cat > ~/monitor-misp.sh << 'EOF'
#!/bin/bash
# MISP Monitoring Script

cd /opt/misp

# Check if containers are running
if ! sudo docker compose ps | grep -q "Up"; then
    echo "WARNING: Some MISP containers are down!" | mail -s "MISP Alert" youremail@yourdomain.com
fi

# Check disk usage
DISK_USAGE=$(df -h ~ | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}%" | mail -s "MISP Disk Alert" youremail@yourdomain.com
fi

# Check for errors in last hour
ERROR_COUNT=$(sudo docker compose logs --since 1h | grep -i error | wc -l)
if [ "$ERROR_COUNT" -gt 50 ]; then
    echo "WARNING: ${ERROR_COUNT} errors in last hour" | mail -s "MISP Error Alert" youremail@yourdomain.com
fi
EOF

chmod +x ~/monitor-misp.sh

# Add to cron (run every hour)
(crontab -l 2>/dev/null; echo "0 * * * * ~/monitor-misp.sh") | crontab -
```

### Use External Monitoring
Consider setting up:
- **Uptime monitoring:** UptimeRobot, Pingdom
- **Log aggregation:** ELK stack, Graylog
- **Metrics:** Prometheus + Grafana
- **Alerting:** PagerDuty, Slack webhooks

## 🎯 Best Practices

### Backup Strategy
1. **Daily backups** - Automated via cron
2. **Weekly full backups** - Include all data
3. **Monthly off-site backups** - Store in different location
4. **Quarterly restore tests** - Verify backups work
5. **Retain backups** - Keep at least 3 months

### Security Best Practices
1. **Regular updates** - Keep MISP and system updated
2. **Strong passwords** - Enforce password policies
3. **2FA enabled** - Require for all admins
4. **Audit logs** - Review regularly
5. **Access control** - Least privilege principle
6. **Network security** - Firewall, VPN, etc.

### Performance Best Practices
1. **Regular optimization** - Database, cache
2. **Monitor resources** - CPU, RAM, disk
3. **Scale appropriately** - Add resources as needed
4. **Clean old data** - Archive/delete as appropriate
5. **Tune workers** - Match CPU cores

## 📞 Maintenance Checklist

Print this and check off completed tasks:

### Daily
- [ ] Check container status
- [ ] Review error logs
- [ ] Monitor disk space

### Weekly
- [ ] Run backup
- [ ] Check backup integrity
- [ ] Review security logs
- [ ] Monitor performance

### Monthly
- [ ] Update MISP
- [ ] Database maintenance
- [ ] Certificate check
- [ ] Review user accounts
- [ ] System updates

### Quarterly
- [ ] Security audit
- [ ] Performance tuning
- [ ] Test backup restoration
- [ ] Clean old data

### Annual
- [ ] Major version upgrade
- [ ] SSL renewal
- [ ] Security compliance review
- [ ] Capacity planning

---

**Remember:** Proper maintenance prevents problems!

Set up automation for repetitive tasks and always test your backups!