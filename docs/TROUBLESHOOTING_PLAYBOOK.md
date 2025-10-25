# MISP Installation Suite - Troubleshooting Playbook

**Version**: 1.0
**Last Updated**: 2025-10-25
**Maintainer**: Development Team

## Overview

This playbook provides step-by-step troubleshooting procedures for common issues encountered during MISP installation, configuration, and operation. Each issue includes symptoms, root cause analysis, diagnostic steps, and resolution procedures.

**Target Audience**: System administrators, developers, and support personnel working with the MISP Installation Suite.

**Related Documentation**:
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing strategies and debugging techniques
- [MISP_QUIRKS.md](MISP_QUIRKS.md) - MISP platform-specific issues
- [NERC_CIP_IMPLEMENTATION_GUIDE.md](NERC_CIP_IMPLEMENTATION_GUIDE.md) - Compliance implementation
- [ONBOARDING.md](ONBOARDING.md) - Developer onboarding and learning

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Docker Container Issues](#docker-container-issues)
3. [MISP Configuration Issues](#misp-configuration-issues)
4. [Widget and Dashboard Issues](#widget-and-dashboard-issues)
5. [API and Integration Issues](#api-and-integration-issues)
6. [NERC CIP Compliance Issues](#nerc-cip-compliance-issues)
7. [Performance Issues](#performance-issues)
8. [Security and Access Issues](#security-and-access-issues)
9. [State Management and Resume Issues](#state-management-and-resume-issues)
10. [Emergency Procedures](#emergency-procedures)

---

## Installation Issues

### Issue 1.1: Installation Fails with "Docker not running"

**Severity**: High
**Symptom**:
```
ERROR: Docker daemon is not running
Phase check_requirements failed
```

**Root Cause**: Docker service not started or user lacks permissions.

**Diagnostic Steps**:
```bash
# 1. Check Docker service status
sudo systemctl status docker

# 2. Check user group membership
groups $USER | grep docker

# 3. Test Docker access
sudo docker ps
```

**Resolution**:

**Option A: Start Docker service**
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Auto-start on boot
```

**Option B: Add user to docker group**
```bash
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect
newgrp docker  # Or use this to activate immediately
```

**Validation**:
```bash
docker ps  # Should work without sudo
```

**Prevention**: Add Docker service check to system startup scripts.

---

### Issue 1.2: Phase Fails Mid-Execution

**Severity**: Medium
**Symptom**:
```
ERROR: Failed to execute step 3 of 7
Phase status: failed
State saved: phase_X_Y_description.json
```

**Root Cause**: Network timeout, insufficient permissions, or dependency failure.

**Diagnostic Steps**:
```bash
# 1. Check phase state
cat state/phase_X_Y_description.json | jq '.'

# 2. Review logs for specific error
tail -50 logs/misp_installer.log | jq 'select(.level=="ERROR")'

# 3. Check completed steps
cat state/phase_X_Y_description.json | jq '.completed_steps'
```

**Resolution**:

**Step 1: Identify failed step**
```bash
# Find the last completed step
LAST_STEP=$(cat state/phase_X_Y_description.json | jq -r '.completed_steps[-1]')
echo "Last completed: $LAST_STEP"
```

**Step 2: Resume from saved state**
```bash
# The phase will automatically resume from last checkpoint
sudo python3 phases/phase_X_Y_description.py

# Or use the main installer
sudo python3 misp-install.py --phase X.Y
```

**Step 3: If resume fails, manual recovery**
```bash
# Clear failed state and retry
sudo rm state/phase_X_Y_description.json
sudo python3 phases/phase_X_Y_description.py
```

**Validation**:
```bash
cat state/phase_X_Y_description.json | jq '.status'
# Should show: "completed"
```

**Prevention**: Ensure stable network connection and adequate system resources before installation.

---

### Issue 1.3: Python Dependencies Missing

**Severity**: Medium
**Symptom**:
```
ModuleNotFoundError: No module named 'requests'
ImportError: cannot import name 'get_logger' from 'lib.misp_logger'
```

**Root Cause**: Missing Python packages or incorrect Python version.

**Diagnostic Steps**:
```bash
# 1. Check Python version
python3 --version  # Should be 3.8+

# 2. Check installed packages
pip3 list | grep -E 'requests|docker|pymisp'

# 3. Verify PYTHONPATH
echo $PYTHONPATH
```

**Resolution**:

**Step 1: Install required packages**
```bash
# Install from requirements file (if exists)
sudo pip3 install -r requirements.txt

# Or install individually
sudo pip3 install requests docker pymisp python-dotenv
```

**Step 2: Fix PYTHONPATH if needed**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="/home/gallagher/misp-install/misp-install:$PYTHONPATH"

# Make permanent (add to ~/.bashrc)
echo 'export PYTHONPATH="/home/gallagher/misp-install/misp-install:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
```

**Validation**:
```bash
python3 -c "import requests, docker; from lib.misp_logger import get_logger; print('OK')"
```

**Prevention**: Create and maintain requirements.txt with pinned versions.

---

## Docker Container Issues

### Issue 2.1: MISP Container Shows "Unhealthy" Status

**Severity**: Low (usually cosmetic)
**Symptom**:
```
CONTAINER ID   IMAGE          STATUS
abc123...      misp/misp:latest   Up 10 minutes (unhealthy)
```

**Root Cause**: MISP health check uses BASE_URL domain, which container cannot resolve internally.

**Diagnostic Steps**:
```bash
# 1. Check container health
sudo docker inspect misp-misp-core-1 | jq '.[0].State.Health'

# 2. Test external access
curl -k -I https://localhost/users/login

# 3. Test internal heartbeat
sudo docker exec misp-misp-core-1 curl -s http://localhost/users/heartbeat
```

**Resolution**:

**Verification (usually no action needed)**:
```bash
# MISP is accessible if this works:
curl -k https://localhost/users/login | grep -i "MISP"

# Health check failure is cosmetic if:
# 1. MISP web UI loads externally ✓
# 2. /users/heartbeat works via localhost ✓
# 3. Only health check via BASE_URL fails (expected)
```

**If truly unhealthy**:
```bash
# Check container logs
sudo docker logs misp-misp-core-1 --tail 100

# Restart container
sudo docker restart misp-misp-core-1

# Or full stack restart
cd /home/gallagher/misp-docker/
sudo docker compose down
sudo docker compose up -d
```

**Validation**:
```bash
# Wait 30 seconds, then test
curl -k https://localhost/users/login
```

**Prevention**: Document that "unhealthy" status is expected and safe to ignore if external access works.

**Reference**: See [MISP_QUIRKS.md](MISP_QUIRKS.md#quirk-15-health-check-domain-resolution) for details.

---

### Issue 2.2: MISP Database Container Won't Start

**Severity**: Critical
**Symptom**:
```
ERROR: Container misp-misp-db-1 exited with code 1
Database connection refused
```

**Root Cause**: Database corruption, port conflict, or volume permission issues.

**Diagnostic Steps**:
```bash
# 1. Check database container logs
sudo docker logs misp-misp-db-1 --tail 50

# 2. Check port conflicts
sudo netstat -tuln | grep 3306

# 3. Check volume permissions
sudo ls -la /home/gallagher/misp-docker/db-volume/
```

**Resolution**:

**Step 1: Identify specific error**
```bash
# Look for common errors in logs:
# - "port already in use" → Port conflict
# - "permission denied" → Volume permissions
# - "corrupted" or "recovery" → Database corruption
```

**Step 2a: Fix port conflict**
```bash
# Find process using port 3306
sudo lsof -i :3306
# Kill conflicting process or change MISP DB port
```

**Step 2b: Fix volume permissions**
```bash
# Set correct ownership (999:999 for MySQL container)
sudo chown -R 999:999 /home/gallagher/misp-docker/db-volume/
```

**Step 2c: Recover from corruption**
```bash
# Backup existing volume
sudo cp -r /home/gallagher/misp-docker/db-volume/ \
           /home/gallagher/misp-docker/db-volume.backup/

# Stop all containers
cd /home/gallagher/misp-docker/
sudo docker compose down

# Remove corrupted volume
sudo rm -rf /home/gallagher/misp-docker/db-volume/

# Restart (will create fresh DB)
sudo docker compose up -d

# Restore from backup if available
# (See Emergency Procedures section)
```

**Validation**:
```bash
sudo docker ps | grep misp-db
# Should show "Up" status without "(unhealthy)"
```

**Prevention**: Implement regular database backups (see Emergency Procedures).

---

### Issue 2.3: Container Disk Space Full

**Severity**: High
**Symptom**:
```
ERROR: No space left on device
docker: Error response from daemon: write /var/lib/docker/...: no space left
```

**Root Cause**: Docker images, volumes, or logs consuming all disk space.

**Diagnostic Steps**:
```bash
# 1. Check overall disk usage
df -h

# 2. Check Docker disk usage
sudo docker system df

# 3. Identify large volumes
sudo du -sh /var/lib/docker/volumes/* | sort -h | tail -10
```

**Resolution**:

**Step 1: Clean unused Docker resources**
```bash
# Remove stopped containers
sudo docker container prune -f

# Remove unused images
sudo docker image prune -a -f

# Remove unused volumes (CAREFUL - may delete data)
sudo docker volume prune -f

# All-in-one cleanup (nuclear option)
sudo docker system prune -a --volumes -f
```

**Step 2: Clean application logs**
```bash
# MISP installer logs
find /home/gallagher/misp-install/misp-install/logs/ -type f -mtime +30 -delete

# Docker container logs
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

**Step 3: Archive old data**
```bash
# Archive state files
cd /home/gallagher/misp-install/misp-install/
tar -czf state-archive-$(date +%Y%m%d).tar.gz state/
mv state-archive-*.tar.gz /backup/location/
```

**Validation**:
```bash
df -h
# Verify sufficient free space (20%+ recommended)
```

**Prevention**:
- Configure log rotation
- Schedule weekly Docker cleanup
- Monitor disk usage with alerts

---

## MISP Configuration Issues

### Issue 3.1: MISP Settings Not Persisting

**Severity**: Medium
**Symptom**:
```
Setting applied successfully via API
After restart: Setting reverted to default
```

**Root Cause**: Setting stored in database but overridden by config file, or container restart loses non-persisted data.

**Diagnostic Steps**:
```bash
# 1. Check setting via API
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/servers/serverSettings.json | \
     jq '.finalSettings[] | select(.setting=="MISP.default_event_distribution")'

# 2. Check if config file exists
sudo docker exec misp-misp-core-1 ls -la /var/www/MISP/app/Config/config.php

# 3. Check setting precedence
# Database < config.php < environment variables
```

**Resolution**:

**Option A: Use persistent API configuration**
```python
from lib.misp_config import set_misp_setting
api_key = open('/root/.misp/apikey').read().strip()

# This writes to database AND ensures persistence
set_misp_setting(api_key, 'MISP.default_event_distribution', '0',
                 base_url='https://localhost')
```

**Option B: Modify docker-compose environment variables**
```yaml
# /home/gallagher/misp-docker/docker-compose.yml
services:
  misp-core:
    environment:
      - MISP_DEFAULT_EVENT_DISTRIBUTION=0
      - MISP_DEFAULT_ATTRIBUTE_DISTRIBUTION=0
```

**Option C: Direct config file modification** (not recommended)
```bash
# Edit config inside container
sudo docker exec -it misp-misp-core-1 bash
vim /var/www/MISP/app/Config/config.php
```

**Validation**:
```bash
# Apply setting, restart container, verify persistence
sudo docker restart misp-misp-core-1
sleep 30
curl -k -H "Authorization: $API_KEY" \
     https://localhost/servers/serverSettings.json | \
     jq '.finalSettings[] | select(.setting=="MISP.default_event_distribution")'
```

**Prevention**: Use docker-compose environment variables for critical settings.

**Reference**: See [MISP_QUIRKS.md](MISP_QUIRKS.md#quirk-13-setting-precedence) for precedence details.

---

### Issue 3.2: Taxonomies Not Appearing in UI

**Severity**: Medium
**Symptom**:
```
Taxonomies enabled via API successfully
MISP UI: Event Taxonomies dropdown is empty
```

**Root Cause**: Taxonomies enabled but not updated, or cache not cleared.

**Diagnostic Steps**:
```bash
# 1. List enabled taxonomies via API
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/taxonomies/index.json | \
     jq '.[] | select(.Taxonomy.enabled==true) | .Taxonomy.namespace'

# 2. Check taxonomy update status
curl -k -H "Authorization: $API_KEY" \
     https://localhost/taxonomies/index.json | \
     jq '.[] | {namespace: .Taxonomy.namespace, entries: .Taxonomy.total_count}'
```

**Resolution**:

**Step 1: Update all taxonomies**
```bash
# Update via API (triggers entry import)
for TAX_ID in $(curl -k -H "Authorization: $API_KEY" \
                     https://localhost/taxonomies/index.json | \
                     jq -r '.[] | select(.Taxonomy.enabled==true) | .Taxonomy.id'); do
    curl -k -X POST -H "Authorization: $API_KEY" \
         "https://localhost/taxonomies/update/$TAX_ID"
done
```

**Step 2: Clear MISP cache**
```bash
sudo docker exec misp-misp-core-1 rm -rf /var/www/MISP/app/tmp/cache/models/*
sudo docker exec misp-misp-core-1 rm -rf /var/www/MISP/app/tmp/cache/persistent/*
sudo docker restart misp-misp-core-1
```

**Step 3: Verify in UI**
```
1. Log in to MISP
2. Event Actions → Add Event
3. Check "Taxonomies" section on right panel
4. Should show enabled taxonomies (TLP, ICS, NERC CIP, etc.)
```

**Validation**:
```bash
# Check entry counts
curl -k -H "Authorization: $API_KEY" \
     https://localhost/taxonomies/index.json | \
     jq '.[] | select(.Taxonomy.namespace=="tlp") | .Taxonomy.total_count'
# Should show: 5 (tlp:white, tlp:green, tlp:amber, tlp:red, tlp:amber+strict)
```

**Prevention**: Always run taxonomy update after enabling.

---

### Issue 3.3: Feed Synchronization Fails

**Severity**: Medium
**Symptom**:
```
Feed "E-ISAC Advisories" fetch failed
Error: 403 Forbidden or Connection timeout
```

**Root Cause**: Authentication failure, network restrictions, or feed source unavailable.

**Diagnostic Steps**:
```bash
# 1. Check feed configuration
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/feeds/index.json | \
     jq '.[] | select(.Feed.name | contains("E-ISAC"))'

# 2. Test feed URL manually
FEED_URL=$(curl -k -H "Authorization: $API_KEY" \
           https://localhost/feeds/index.json | \
           jq -r '.[] | select(.Feed.name | contains("E-ISAC")) | .Feed.url')
curl -I -k -H "Authorization: YOUR_FEED_API_KEY" "$FEED_URL"

# 3. Check MISP worker status
sudo docker exec misp-misp-core-1 /var/www/MISP/app/Console/cake Admin getSetting SimpleBackgroundJobs.enabled
```

**Resolution**:

**Step 1: Verify feed authentication**
```bash
# Update feed with correct API key or credentials
curl -k -X POST -H "Authorization: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"authkey": "YOUR_FEED_API_KEY"}' \
     "https://localhost/feeds/edit/[FEED_ID]"
```

**Step 2: Test network connectivity**
```bash
# From MISP container
sudo docker exec misp-misp-core-1 curl -I https://feed.example.com

# If fails: Check firewall, proxy, DNS
```

**Step 3: Manual feed fetch**
```bash
# Trigger manual fetch
curl -k -X GET -H "Authorization: $API_KEY" \
     "https://localhost/feeds/fetchFromFeed/[FEED_ID]"
```

**Validation**:
```bash
# Check feed events
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/index.json | \
     jq '[.[] | select(.Event.info | contains("E-ISAC"))] | length'
# Should show event count > 0
```

**Prevention**:
- Store feed credentials securely
- Monitor feed availability
- Configure retry logic

---

## Widget and Dashboard Issues

### Issue 4.1: "Add Widget" Button Shows No Custom Widgets

**Severity**: Medium
**Symptom**:
```
MISP Dashboard: Add Widget → Only shows default MISP widgets
Custom widgets in /var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/ not appearing
```

**Root Cause**: PHP abstract class instantiation bug in MISP's widget loader.

**Diagnostic Steps**:
```bash
# 1. Check if custom widgets exist
sudo docker exec misp-misp-core-1 ls -la \
    /var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/

# 2. Check for abstract base class files
sudo docker exec misp-misp-core-1 grep -r "abstract class" \
    /var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/

# 3. Check MISP error logs
sudo docker logs misp-misp-core-1 | grep -i "fatal error"
```

**Resolution**:

**Root Cause**: MISP's loader scans all .php files and tries to instantiate them:
```php
// MISP's buggy loader code
foreach ($files as $file) {
    if (substr($file, -4) === '.php') {
        $className = substr($file, 0, -4);
        $widget = new $className();  // ❌ Fails on abstract classes
    }
}
```

**Solution**: Use PHP **traits** instead of abstract base classes.

**❌ DO NOT DO THIS**:
```php
// widgets/Custom/BaseWidget.php
abstract class BaseWidget {
    abstract public function handler($user, $options);
    protected function checkPermissions($user) { /* ... */ }
}

// widgets/Custom/MyWidget.php
class MyWidget extends BaseWidget {
    public function handler($user, $options) { /* ... */ }
}
```

**✅ DO THIS INSTEAD**:
```php
// widgets/Custom/MyWidget.php (single file)
trait WidgetHelpers {
    protected function checkPermissions($user) {
        return $user['Role']['perm_auth'];
    }

    protected function formatTags($event) {
        // Extract tags from either Tag or EventTag array
        if (isset($event['Tag'])) {
            return array_column($event['Tag'], 'name');
        }
        return array();
    }
}

class MyWidget {
    use WidgetHelpers;  // Include trait

    public $title = 'My Custom Widget';
    public $render = 'Custom';
    public $width = 4;
    public $height = 4;
    public $params = array(/* ... */);

    public function handler($user, $options = array()) {
        if (!$this->checkPermissions($user)) {
            return array();
        }

        // Widget logic...
        return $data;
    }
}
```

**Validation**:
```bash
# 1. Upload fixed widget
sudo docker cp MyWidget.php misp-misp-core-1:/var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/

# 2. Set permissions
sudo docker exec misp-misp-core-1 chown www-data:www-data \
    /var/www/MISP/app/View/Elements/Dashboard/Widgets/Custom/MyWidget.php

# 3. Test in UI: Dashboard → Add Widget → Should appear
```

**Prevention**: Document widget development pattern in team guidelines.

**Reference**: See [MISP_QUIRKS.md](MISP_QUIRKS.md#quirk-1-abstract-class-instantiation-bug) and [PATTERNS.md](PATTERNS.md#pattern-8-widget-base-class-pattern) for details.

---

### Issue 4.2: Widget Shows Empty Results Despite Data Existing

**Severity**: Medium
**Symptom**:
```
Widget displays "No data available"
Direct API query returns events
```

**Root Cause**: Tag wildcard mismatch, time filter issue, or permission problem.

**Diagnostic Steps**:
```bash
# 1. Test widget query via API
API_KEY=$(cat ~/.misp/apikey)
curl -k -X POST -H "Authorization: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "tags": ["ics:"],
       "published": 1,
       "last": "7d"
     }' \
     https://localhost/events/restSearch.json | jq '. | length'

# 2. Test with wildcard
curl -k -X POST -H "Authorization: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "tags": ["ics:%"],
       "published": 1
     }' \
     https://localhost/events/restSearch.json | jq '. | length'
```

**Resolution**:

**Issue A: Tag wildcard missing**

**❌ BROKEN**:
```php
$eventIds = $Event->fetchEventIds($user, array(
    'tags' => array('ics:'),  // Returns 0 events
    'published' => 1
));
```

**✅ FIXED**:
```php
$eventIds = $Event->fetchEventIds($user, array(
    'tags' => array('ics:%'),  // Use % wildcard
    'published' => 1
));
```

**Issue B: Time filter using wrong date field**

**Problem**: `'last' => '7d'` checks `event.date` field (event occurrence date), NOT `event.publish_timestamp` (when published to MISP).

**Workaround**: Use recent dates for demo events, or remove time filter:
```php
// Option 1: Remove time filter for demos
$options = array(
    'tags' => array('ics:%'),
    'published' => 1
    // No 'last' parameter
);

// Option 2: Use date range instead
$options = array(
    'tags' => array('ics:%'),
    'published' => 1,
    'from' => date('Y-m-d', strtotime('-30 days')),
    'to' => date('Y-m-d')
);
```

**Issue C: Tag structure inconsistency**

**Problem**: MISP returns tags in different formats:
```php
// Format 1: Tag array
$event['Tag'] = array(
    array('name' => 'ics:malware'),
    array('name' => 'tlp:white')
);

// Format 2: EventTag array
$event['EventTag'] = array(
    array('Tag' => array('name' => 'ics:malware'))
);
```

**Solution**: Handle both formats:
```php
function extractTags($event) {
    $tags = array();

    // Check Tag array
    if (isset($event['Tag']) && is_array($event['Tag'])) {
        foreach ($event['Tag'] as $tag) {
            $tags[] = $tag['name'];
        }
    }

    // Check EventTag array
    if (isset($event['EventTag']) && is_array($event['EventTag'])) {
        foreach ($event['EventTag'] as $eventTag) {
            if (isset($eventTag['Tag']['name'])) {
                $tags[] = $eventTag['Tag']['name'];
            }
        }
    }

    return array_unique($tags);
}
```

**Validation**:
```bash
# Refresh dashboard and verify widget shows data
# Or test via curl with fixed query parameters
```

**Prevention**: Use standard tag extraction helper in all widgets.

**Reference**: See [MISP_QUIRKS.md](MISP_QUIRKS.md#quirk-2-tag-wildcard-matching) for tag quirks.

---

## API and Integration Issues

### Issue 5.1: API Returns 403 Forbidden

**Severity**: High
**Symptom**:
```
curl -H "Authorization: YOUR_API_KEY" https://localhost/events.json
HTTP/1.1 403 Forbidden
{"name":"Not authorised","message":"Not authorised","url":"\/events.json"}
```

**Root Cause**: Invalid API key, insufficient user permissions, or IP restrictions.

**Diagnostic Steps**:
```bash
# 1. Verify API key format
cat ~/.misp/apikey
# Should be 40-character alphanumeric string

# 2. Test API key validity
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/users/view/me.json | jq '.User.email'

# 3. Check user role permissions
curl -k -H "Authorization: $API_KEY" \
     https://localhost/users/view/me.json | jq '.User.Role'
```

**Resolution**:

**Step 1: Regenerate API key**
```bash
# Via MISP UI:
# 1. Log in as admin
# 2. Administration → List Users → [Your User] → Edit
# 3. Click "Reset Auth Key"
# 4. Save new key to ~/.misp/apikey

# Save to file
echo "YOUR_NEW_API_KEY" > ~/.misp/apikey
chmod 600 ~/.misp/apikey
```

**Step 2: Verify user role**
```bash
# User must have Site Admin or Org Admin role for full API access
# Check role permissions:
curl -k -H "Authorization: $API_KEY" \
     https://localhost/roles/view/[ROLE_ID].json | \
     jq '.Role | {name, perm_auth, perm_add, perm_modify, perm_publish}'
```

**Step 3: Check IP restrictions** (if configured)
```bash
# In MISP: Administration → Server Settings → Security
# Look for: Security.allowed_ips
# Ensure your IP is whitelisted or setting is empty
```

**Validation**:
```bash
# Test API access
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/index.json | jq '. | length'
# Should return event count
```

**Prevention**: Store API key securely and document required role permissions.

---

### Issue 5.2: PyMISP Script Connection Refused

**Severity**: Medium
**Symptom**:
```python
from pymisp import PyMISP
misp = PyMISP('https://localhost', api_key, False)
# Error: requests.exceptions.ConnectionError: Connection refused
```

**Root Cause**: MISP container not running, wrong URL, or SSL verification issue.

**Diagnostic Steps**:
```bash
# 1. Verify MISP is running
sudo docker ps | grep misp-core

# 2. Test HTTPS access
curl -k https://localhost/users/login
# Should return HTML login page

# 3. Check port mapping
sudo docker port misp-misp-core-1
# Should show: 443/tcp -> 0.0.0.0:443
```

**Resolution**:

**Issue A: Wrong URL format**
```python
# ❌ WRONG
misp = PyMISP('localhost', api_key, False)  # Missing https://
misp = PyMISP('https://localhost/', api_key, False)  # Trailing slash

# ✅ CORRECT
misp = PyMISP('https://localhost', api_key, False, debug=False)
```

**Issue B: SSL verification issue**
```python
# For self-signed certificates, disable SSL verification
from pymisp import PyMISP
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

misp = PyMISP(
    url='https://localhost',
    key=api_key,
    ssl=False,  # Disable SSL verification
    debug=False
)
```

**Issue C: Container networking**
```bash
# If running script from another container/host
# Use container IP instead of localhost
MISP_IP=$(sudo docker inspect misp-misp-core-1 | \
          jq -r '.[0].NetworkSettings.Networks[].IPAddress')
echo "MISP IP: $MISP_IP"

# Or use host networking
sudo docker run --network host your-script-container
```

**Validation**:
```python
from pymisp import PyMISP
misp = PyMISP('https://localhost', api_key, False)
user = misp.get_user('me')
print(f"Connected as: {user['User']['email']}")
```

**Prevention**: Use standardized connection helper in all scripts.

---

## NERC CIP Compliance Issues

### Issue 6.1: Compliance Score Not Improving After Implementation

**Severity**: Medium
**Symptom**:
```
Implemented CIP-004 user roles and training
Audit script still shows 35% compliance
Expected: 40%+ compliance
```

**Root Cause**: Audit script not detecting new features, or features not properly tagged.

**Diagnostic Steps**:
```bash
# 1. Run detailed audit
sudo python3 scripts/audit/nerc-cip-audit.py --verbose

# 2. Check specific CIP standard
sudo python3 scripts/audit/nerc-cip-audit.py --standard CIP-004

# 3. Verify feature implementation
# Example: Check if training events exist
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/restSearch.json | \
     jq '[.response.Event[] | select(.info | contains("Training"))] | length'
```

**Resolution**:

**Step 1: Update audit script detection logic**

Most common issue: Audit script has outdated detection criteria.

```python
# scripts/audit/nerc-cip-audit.py
# Example: Update CIP-004 R4 detection

# ❌ OLD (too strict)
def check_cip_004_r4():
    """Check personnel risk assessment"""
    # Only checks for specific event named "Personnel Risk Assessment"
    events = misp.search(eventinfo="Personnel Risk Assessment")
    return len(events) > 0

# ✅ NEW (comprehensive)
def check_cip_004_r4():
    """Check personnel risk assessment and training"""
    checks = {
        'training_events': False,
        'user_roles': False,
        'access_tracking': False
    }

    # Check for training events (any events tagged with training)
    training = misp.search(tags=["cip-004:training%"])
    checks['training_events'] = len(training) > 0

    # Check for user role configuration
    roles = misp.roles()
    checks['user_roles'] = len(roles) >= 6  # Minimum NERC CIP roles

    # Check for access tracking events
    access = misp.search(tags=["cip-004:access%"])
    checks['access_tracking'] = len(access) > 0

    # Partial credit scoring
    score = sum(checks.values()) / len(checks) * 100
    return score
```

**Step 2: Verify evidence collection**
```bash
# Check if evidence directory has required artifacts
ls -la audit/evidence/CIP-004/

# Should contain:
# - training-records/ (PDFs, events)
# - access-logs/ (user access events)
# - user-list/ (JSON export of users with roles)
```

**Step 3: Re-run audit with debug**
```bash
sudo python3 scripts/audit/nerc-cip-audit.py --verbose --debug | tee audit-debug.log

# Review output for detection failures
grep -i "CIP-004" audit-debug.log
```

**Validation**:
```bash
# Compliance score should increase
sudo python3 scripts/audit/nerc-cip-audit.py | grep "Overall Compliance"
```

**Prevention**:
- Document audit detection logic in NERC_CIP_IMPLEMENTATION_GUIDE.md
- Test audit script after each feature implementation
- Use compliance tagging consistently

**Reference**: See [NERC_CIP_IMPLEMENTATION_GUIDE.md](NERC_CIP_IMPLEMENTATION_GUIDE.md#validation-procedures) for audit procedures.

---

### Issue 6.2: E-ISAC Feed Not Receiving Advisories

**Severity**: Medium
**Symptom**:
```
E-ISAC feed configured but no advisories appearing
Feed status: Enabled, last fetch: Success
Event count: 0
```

**Root Cause**: Authentication failure, wrong feed URL, or filtering too aggressive.

**Diagnostic Steps**:
```bash
# 1. Check feed configuration
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/feeds/index.json | \
     jq '.[] | select(.Feed.name | contains("ISAC"))'

# 2. Check feed fetch logs
sudo docker logs misp-misp-core-1 | grep -i "feed"

# 3. Test feed URL manually
FEED_URL="https://advisories.eisac.com/..."  # Your feed URL
curl -I -H "Authorization: YOUR_FEED_API_KEY" "$FEED_URL"
```

**Resolution**:

**Step 1: Verify E-ISAC credentials**
```bash
# E-ISAC requires authentication
# Check if API key/credentials are configured correctly

# Update feed with correct authkey
curl -k -X POST -H "Authorization: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "Feed": {
         "id": "FEED_ID",
         "authkey": "YOUR_EISAC_API_KEY",
         "enabled": true,
         "caching_enabled": true
       }
     }' \
     https://localhost/feeds/edit/FEED_ID
```

**Step 2: Check feed filters**
```bash
# Feed may have filters that exclude all events
# Check current filters
curl -k -H "Authorization: $API_KEY" \
     https://localhost/feeds/view/FEED_ID.json | \
     jq '.Feed | {rules: .rules, filter_rules: .filter_rules}'

# Remove overly restrictive filters
curl -k -X POST -H "Authorization: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"Feed": {"rules": ""}}' \
     https://localhost/feeds/edit/FEED_ID
```

**Step 3: Manual feed fetch with verbose logging**
```bash
# Enable debug mode
sudo docker exec misp-misp-core-1 \
     /var/www/MISP/app/Console/cake Admin setSetting "debug" 2

# Fetch feed
curl -k -X GET -H "Authorization: $API_KEY" \
     "https://localhost/feeds/fetchFromFeed/FEED_ID"

# Check workers
sudo docker exec misp-misp-core-1 \
     /var/www/MISP/app/Console/cake Admin jobStatus

# Disable debug
sudo docker exec misp-misp-core-1 \
     /var/www/MISP/app/Console/cake Admin setSetting "debug" 0
```

**Validation**:
```bash
# Wait 5 minutes, then check for events
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/index.json | \
     jq '[.[] | select(.Event.info | contains("ISAC") or contains("ICS-CERT"))] | length'
```

**Prevention**:
- Document E-ISAC feed setup procedure
- Store credentials securely
- Monitor feed fetch status with alerts

---

## Performance Issues

### Issue 7.1: Dashboard Loads Slowly (>10 seconds)

**Severity**: Medium
**Symptom**:
```
Dashboard takes 10-30 seconds to load
All widgets show loading spinner
Browser console: Multiple slow API requests
```

**Root Cause**: Inefficient widget queries, no caching, or database not indexed.

**Diagnostic Steps**:
```bash
# 1. Check query execution time
sudo docker exec misp-misp-db-1 mysql -u misp -p misp -e "
    SHOW FULL PROCESSLIST;
"

# 2. Enable query profiling
sudo docker exec misp-misp-db-1 mysql -u misp -p misp -e "
    SET profiling = 1;
    SELECT * FROM events WHERE published=1 LIMIT 100;
    SHOW PROFILES;
"

# 3. Check widget API calls in browser
# Open DevTools → Network tab → Filter: XHR
# Look for slow requests (>1s)
```

**Resolution**:

**Optimization 1: Add database indexes**
```sql
-- Connect to database
sudo docker exec -it misp-misp-db-1 mysql -u misp -p

USE misp;

-- Check existing indexes
SHOW INDEX FROM events;
SHOW INDEX FROM attributes;

-- Add missing indexes
CREATE INDEX idx_events_published ON events(published);
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_attributes_type ON attributes(type);
CREATE INDEX idx_event_tags_event_id ON event_tags(event_id);

-- Analyze tables
ANALYZE TABLE events;
ANALYZE TABLE attributes;
ANALYZE TABLE event_tags;
```

**Optimization 2: Enable widget caching**
```php
// In widget handler method
public function handler($user, $options = array()) {
    // Check cache first
    $cacheKey = 'widget_' . __CLASS__ . '_' . $user['id'];
    $cached = Cache::read($cacheKey, 'short');
    if ($cached !== false) {
        return $cached;
    }

    // Expensive query...
    $data = $this->fetchData($user, $options);

    // Cache for 5 minutes
    Cache::write($cacheKey, $data, 'short');
    return $data;
}
```

**Optimization 3: Limit query scope**
```php
// ❌ SLOW - fetches all events
$events = $Event->find('all', array(
    'conditions' => array('Event.published' => 1),
    'recursive' => -1  // Missing
));

// ✅ FAST - limits results and disables recursion
$events = $Event->find('all', array(
    'conditions' => array(
        'Event.published' => 1,
        'Event.date >' => date('Y-m-d', strtotime('-90 days'))
    ),
    'recursive' => -1,  // Don't fetch related models
    'limit' => 100,
    'fields' => array('Event.id', 'Event.info', 'Event.date')  // Only needed fields
));
```

**Optimization 4: Use pagination**
```php
// Instead of loading 1000+ events, paginate
public function handler($user, $options = array()) {
    $page = isset($options['page']) ? $options['page'] : 1;
    $limit = 50;

    $events = $Event->find('all', array(
        'conditions' => array('Event.published' => 1),
        'limit' => $limit,
        'page' => $page,
        'order' => array('Event.date' => 'DESC')
    ));

    return array(
        'data' => $events,
        'page' => $page,
        'total' => $Event->find('count', array('conditions' => array('Event.published' => 1)))
    );
}
```

**Validation**:
```bash
# Clear cache and reload dashboard
sudo docker exec misp-misp-core-1 rm -rf /var/www/MISP/app/tmp/cache/*
sudo docker restart misp-misp-core-1

# Measure load time (should be <3 seconds)
time curl -k -o /dev/null -s -w '%{time_total}\n' https://localhost/dashboards/index
```

**Prevention**:
- Profile all widget queries during development
- Use EXPLAIN to analyze query plans
- Implement caching by default

---

## Security and Access Issues

### Issue 8.1: Users Can See Events from Other Organizations

**Severity**: Critical
**Symptom**:
```
User from Org A can view/edit events created by Org B
Expected: Users should only see their own org's events (unless shared)
```

**Root Cause**: MISP distribution settings misconfigured or sharing groups incorrect.

**Diagnostic Steps**:
```bash
# 1. Check MISP default distribution setting
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/servers/serverSettings.json | \
     jq '.finalSettings[] | select(.setting | contains("distribution"))'

# 2. Check existing event distribution
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/index.json | \
     jq '.[] | {info: .Event.info, distribution: .Event.distribution, org: .Event.Orgc.name}'

# 3. Check user's organization
curl -k -H "Authorization: $API_KEY" \
     https://localhost/users/view/me.json | \
     jq '.User | {email, org: .Organisation.name, role: .Role.name}'
```

**Resolution**:

**NERC CIP Requirement**: Distribution must default to "Your organization only" (level 0) for BCSI protection (CIP-011).

**Distribution Levels**:
- **0** = Your organization only ✅ (NERC CIP compliant)
- **1** = This community only
- **2** = Connected communities
- **3** = All communities
- **4** = Sharing group
- **5** = Inherit event

**Step 1: Fix default distribution settings**
```bash
# Set system defaults to level 0
from lib.misp_config import set_misp_setting
api_key = open('/root/.misp/apikey').read().strip()

set_misp_setting(api_key, 'MISP.default_event_distribution', '0')
set_misp_setting(api_key, 'MISP.default_attribute_distribution', '5')  # Inherit from event
set_misp_setting(api_key, 'MISP.default_event_threat_level', '2')  # Medium
set_misp_setting(api_key, 'MISP.showorgalternate', '1')  # Show org names
```

**Step 2: Audit and fix existing events**
```python
#!/usr/bin/env python3
from pymisp import PyMISP

misp = PyMISP('https://localhost', api_key, False)

# Find events with wrong distribution
events = misp.search(pythonify=True)
for event in events:
    if event.distribution > 0:  # Not "Your org only"
        print(f"Fixing event {event.id}: {event.info}")
        event.distribution = 0  # Set to "Your organization only"
        misp.update_event(event)
```

**Step 3: Verify organization isolation**
```bash
# Test as different users
# User A (Org A) should NOT see Org B events with distribution=0

# Get events visible to user
curl -k -H "Authorization: USER_A_API_KEY" \
     https://localhost/events/index.json | \
     jq '[.[] | .Event.Orgc.name] | unique'
# Should only show: ["Org A"]
```

**Validation**:
```bash
# Run compliance audit
sudo python3 scripts/audit/nerc-cip-audit.py --standard CIP-011
# Should pass: "Default distribution is 'Your organization only'"
```

**Prevention**:
- Enforce distribution policy via training
- Regular audits of event distribution
- Use sharing groups carefully

**Reference**: NERC CIP-011 R1 - BES Cyber System Information (BCSI) protection.

---

## State Management and Resume Issues

### Issue 9.1: Phase Won't Resume After Failure

**Severity**: High
**Symptom**:
```
Phase failed mid-execution
Re-run phase: starts from beginning instead of resuming
State file exists but ignored
```

**Root Cause**: State file corrupted, wrong state key, or resume logic not implemented.

**Diagnostic Steps**:
```bash
# 1. Check state file
cat state/phase_X_Y_description.json | jq '.'

# 2. Verify state file format
cat state/phase_X_Y_description.json | jq '{status, completed_steps, error}'

# 3. Check phase code for resume logic
grep -A 10 "def run" phases/phase_X_Y_description.py | grep -i "state"
```

**Resolution**:

**Issue A: State file corrupted**
```bash
# Check for JSON syntax errors
jq '.' state/phase_X_Y_description.json
# If error: "parse error: Invalid numeric literal"

# Fix: Restore from backup or delete and retry
sudo rm state/phase_X_Y_description.json
sudo python3 phases/phase_X_Y_description.py
```

**Issue B: Resume logic not implemented**

Phases must check state and skip completed steps:

```python
# ❌ WRONG - always starts from beginning
class Phase_X_Y_Description(BasePhase):
    def run(self):
        self._step_1()
        self._step_2()
        self._step_3()
        self.state.save({'status': 'completed'})

# ✅ CORRECT - resumes from last checkpoint
class Phase_X_Y_Description(BasePhase):
    def run(self):
        # Load previous state
        prev_state = self.state.load()
        completed = prev_state.get('completed_steps', [])

        # Step 1
        if 'step_1' not in completed:
            self._step_1()
            completed.append('step_1')
            self.state.save({'status': 'in_progress', 'completed_steps': completed})

        # Step 2
        if 'step_2' not in completed:
            self._step_2()
            completed.append('step_2')
            self.state.save({'status': 'in_progress', 'completed_steps': completed})

        # Step 3
        if 'step_3' not in completed:
            self._step_3()
            completed.append('step_3')

        # Final state
        self.state.save({'status': 'completed', 'completed_steps': completed})
```

**Issue C: State key mismatch**
```python
# State file: phase_11_8_utilities_intel.json
# But phase uses wrong key:

# ❌ WRONG
self.state_file = "phase_11_utilities_intel.json"  # Missing "8"

# ✅ CORRECT
self.state_file = "phase_11_8_utilities_intel.json"
```

**Validation**:
```bash
# Test resume functionality
sudo python3 phases/phase_X_Y_description.py &
PID=$!
sleep 10
sudo kill $PID  # Interrupt mid-execution

# Check state saved
cat state/phase_X_Y_description.json | jq '.completed_steps'

# Resume - should skip completed steps
sudo python3 phases/phase_X_Y_description.py
```

**Prevention**:
- Use BasePhase template for all phases
- Test resume logic before merging
- Include state validation in CI/CD

**Reference**: See [PATTERNS.md](PATTERNS.md#pattern-1-phase-pattern) for state management pattern.

---

## Emergency Procedures

### Emergency 1: Complete MISP Data Loss

**Severity**: Critical
**Scenario**: Database corruption, accidental deletion, or hardware failure.

**Recovery Procedure**:

**Step 1: Stop all services**
```bash
cd /home/gallagher/misp-docker/
sudo docker compose down
```

**Step 2: Assess damage**
```bash
# Check if database volume exists
sudo ls -la /home/gallagher/misp-docker/db-volume/

# Check database files
sudo du -sh /home/gallagher/misp-docker/db-volume/
```

**Step 3: Restore from backup**

**Option A: Restore from automated backup**
```bash
# List available backups
ls -lh /backup/misp/database/

# Restore latest backup
sudo rm -rf /home/gallagher/misp-docker/db-volume/
sudo cp -r /backup/misp/database/misp-db-2025-10-24/ \
           /home/gallagher/misp-docker/db-volume/

# Set permissions
sudo chown -R 999:999 /home/gallagher/misp-docker/db-volume/
```

**Option B: Restore from SQL dump**
```bash
# Start fresh database
cd /home/gallagher/misp-docker/
sudo docker compose up -d misp-db

# Wait for database to initialize
sleep 30

# Import dump
sudo docker exec -i misp-misp-db-1 mysql -u misp -pPASSWORD misp < \
    /backup/misp/misp-backup-2025-10-24.sql
```

**Option C: No backup available - Fresh install**
```bash
# LAST RESORT: Start fresh
sudo rm -rf /home/gallagher/misp-docker/db-volume/
cd /home/gallagher/misp-docker/
sudo docker compose up -d

# Re-run installation phases
cd /home/gallagher/misp-install/misp-install/
sudo python3 misp-install.py --force
```

**Step 4: Restart and validate**
```bash
cd /home/gallagher/misp-docker/
sudo docker compose up -d

# Wait for startup
sleep 60

# Test access
curl -k https://localhost/users/login | grep -i "MISP"

# Verify data
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/index.json | jq '. | length'
```

**Step 5: Document incident**
```bash
# Create incident report
cat > /tmp/incident-$(date +%Y%m%d).md <<EOF
# MISP Data Loss Incident

**Date**: $(date)
**Cause**: [Database corruption / Accidental deletion / Hardware failure]
**Data Lost**: [Describe what was lost]
**Recovery Method**: [Backup restoration / Fresh install]
**Data Recovered**: [Yes/No - percentage]
**Downtime**: [X hours]
**Root Cause**: [Analysis]
**Prevention**: [Actions to prevent recurrence]

## Timeline
- $(date): Incident detected
- $(date): Recovery initiated
- $(date): Service restored

## Lessons Learned
1. [Lesson 1]
2. [Lesson 2]
EOF
```

**Prevention**:
1. **Automated backups**:
```bash
# Add to crontab: Daily database backup
0 2 * * * /usr/bin/docker exec misp-misp-db-1 mysqldump -u misp -pPASSWORD misp | gzip > /backup/misp/misp-$(date +\%Y\%m\%d).sql.gz
```

2. **Backup rotation** (keep 30 days):
```bash
# Clean old backups
find /backup/misp/ -name "misp-*.sql.gz" -mtime +30 -delete
```

3. **Test restores monthly**:
```bash
# Restore to test environment
# Verify data integrity
# Document procedure
```

---

### Emergency 2: MISP Compromised / Security Incident

**Severity**: Critical
**Scenario**: Unauthorized access detected, data breach, or malware.

**Immediate Response**:

**Step 1: Isolate system (within 5 minutes)**
```bash
# Disconnect from network
sudo iptables -P INPUT DROP
sudo iptables -P OUTPUT DROP
sudo iptables -P FORWARD DROP

# Or shutdown network interface
sudo ip link set eth0 down

# Stop MISP containers
cd /home/gallagher/misp-docker/
sudo docker compose down
```

**Step 2: Preserve evidence (within 15 minutes)**
```bash
# Capture memory dump (if forensics required)
sudo dd if=/dev/mem of=/forensics/memory-$(date +%Y%m%d-%H%M).dump bs=1M

# Capture disk state
sudo dd if=/dev/sda of=/forensics/disk-$(date +%Y%m%d-%H%M).img bs=4M

# Copy logs
sudo tar -czf /forensics/logs-$(date +%Y%m%d-%H%M).tar.gz \
    /home/gallagher/misp-install/misp-install/logs/ \
    /var/log/

# Copy database
sudo tar -czf /forensics/database-$(date +%Y%m%d-%H%M).tar.gz \
    /home/gallagher/misp-docker/db-volume/
```

**Step 3: Notify stakeholders (within 1 hour - NERC CIP-008 requirement)**
```bash
# Email security team
# Notify E-ISAC if incident affects BES Cyber Systems
# Document incident timeline
```

**Step 4: Analyze compromise**
```bash
# Check Docker logs for unauthorized access
sudo docker logs misp-misp-core-1 | grep -iE "login|auth|fail"

# Check database for unauthorized changes
sudo docker exec misp-misp-db-1 mysql -u misp -p misp -e "
    SELECT * FROM logs WHERE action='login' ORDER BY created DESC LIMIT 100;
"

# Check for malicious events/attributes
API_KEY=$(cat ~/.misp/apikey)
curl -k -H "Authorization: $API_KEY" \
     https://localhost/events/index.json | \
     jq '.[] | select(.Event.date > "2025-10-25")'  # Events since incident
```

**Step 5: Eradication and recovery**
```bash
# If compromise confirmed:
# 1. Rotate all credentials (API keys, DB passwords, LDAP)
# 2. Rebuild from clean backup
# 3. Apply security patches
# 4. Review access logs
# 5. Implement additional controls

# Restore from pre-compromise backup
cd /home/gallagher/misp-docker/
sudo docker compose down
sudo rm -rf db-volume/
sudo cp -r /backup/misp/database/misp-db-2025-10-20/ db-volume/
sudo docker compose up -d
```

**Step 6: Post-incident review**
- Root cause analysis
- Update security controls
- Revise incident response procedures
- Training for team
- Compliance reporting (NERC CIP-008)

**NERC CIP-008 Requirements**:
- Initial notification: Within 1 hour
- Final report: Within 7 calendar days
- Include: Timeline, impact, root cause, remediation, prevention

---

## Appendix

### A. Common Log Patterns

**Error Patterns to Search For**:

```bash
# Docker errors
sudo docker logs misp-misp-core-1 | grep -iE "error|fatal|exception"

# Python errors
tail -100 logs/misp_installer.log | jq 'select(.level=="ERROR")'

# Database errors
sudo docker exec misp-misp-db-1 tail -100 /var/log/mysql/error.log

# Network errors
tail -100 logs/misp_installer.log | jq 'select(.message | contains("timeout") or contains("connection"))'
```

---

### B. Diagnostic Data Collection Script

Save this as `scripts/collect-diagnostics.sh`:

```bash
#!/bin/bash
# MISP Diagnostic Data Collection Script
# Usage: sudo ./scripts/collect-diagnostics.sh

OUTPUT_DIR="/tmp/misp-diagnostics-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUTPUT_DIR"

echo "Collecting MISP diagnostic data..."

# System info
echo "=== System Info ===" > "$OUTPUT_DIR/system-info.txt"
uname -a >> "$OUTPUT_DIR/system-info.txt"
df -h >> "$OUTPUT_DIR/system-info.txt"
free -h >> "$OUTPUT_DIR/system-info.txt"

# Docker info
echo "=== Docker Info ===" > "$OUTPUT_DIR/docker-info.txt"
docker version >> "$OUTPUT_DIR/docker-info.txt"
docker ps -a >> "$OUTPUT_DIR/docker-info.txt"
docker stats --no-stream >> "$OUTPUT_DIR/docker-info.txt"

# MISP container logs
docker logs misp-misp-core-1 --tail 500 > "$OUTPUT_DIR/misp-core.log" 2>&1
docker logs misp-misp-db-1 --tail 500 > "$OUTPUT_DIR/misp-db.log" 2>&1

# Installation logs
cp -r /home/gallagher/misp-install/misp-install/logs/*.log "$OUTPUT_DIR/" 2>/dev/null

# State files
cp -r /home/gallagher/misp-install/misp-install/state/*.json "$OUTPUT_DIR/" 2>/dev/null

# Configuration (sanitized)
docker exec misp-misp-core-1 cat /var/www/MISP/app/Config/config.php | \
    sed 's/password\s*=>\s*.*/password => [REDACTED]/' > "$OUTPUT_DIR/misp-config.php"

# Package archive
tar -czf "$OUTPUT_DIR.tar.gz" "$OUTPUT_DIR/"
echo "Diagnostics saved to: $OUTPUT_DIR.tar.gz"
```

---

### C. Health Check Script

Save this as `scripts/health-check.sh`:

```bash
#!/bin/bash
# MISP Health Check Script
# Usage: ./scripts/health-check.sh

ERRORS=0

# Check Docker
if ! docker ps | grep -q misp-misp-core-1; then
    echo "❌ MISP core container not running"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ MISP core container running"
fi

# Check web access
if curl -k -s https://localhost/users/login | grep -q "MISP"; then
    echo "✅ MISP web UI accessible"
else
    echo "❌ MISP web UI not accessible"
    ERRORS=$((ERRORS + 1))
fi

# Check API
API_KEY=$(cat ~/.misp/apikey 2>/dev/null)
if [ -n "$API_KEY" ]; then
    if curl -k -s -H "Authorization: $API_KEY" https://localhost/users/view/me.json | jq -e '.User.email' > /dev/null 2>&1; then
        echo "✅ MISP API accessible"
    else
        echo "❌ MISP API not accessible"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "⚠️  API key not found"
fi

# Check database
if docker exec misp-misp-db-1 mysqladmin -u misp -p$(docker exec misp-misp-core-1 printenv MYSQL_PASSWORD) ping 2>/dev/null | grep -q "alive"; then
    echo "✅ Database accessible"
else
    echo "❌ Database not accessible"
    ERRORS=$((ERRORS + 1))
fi

# Check disk space
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk space OK ($DISK_USAGE%)"
else
    echo "⚠️  Disk space high ($DISK_USAGE%)"
fi

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed"
    exit 0
else
    echo "❌ $ERRORS checks failed"
    exit 1
fi
```

---

## Quick Reference

### Most Common Issues

| Issue | Quick Fix | Reference |
|-------|-----------|-----------|
| Docker not running | `sudo systemctl start docker` | [Issue 1.1](#issue-11-installation-fails-with-docker-not-running) |
| Container unhealthy | Ignore if web UI works | [Issue 2.1](#issue-21-misp-container-shows-unhealthy-status) |
| API 403 Forbidden | Regenerate API key | [Issue 5.1](#issue-51-api-returns-403-forbidden) |
| Widgets not showing | Use traits not abstract classes | [Issue 4.1](#issue-41-add-widget-button-shows-no-custom-widgets) |
| Widget empty results | Add % to tag wildcards | [Issue 4.2](#issue-42-widget-shows-empty-results-despite-data-existing) |
| Settings not persisting | Use docker-compose env vars | [Issue 3.1](#issue-31-misp-settings-not-persisting) |
| Phase won't resume | Check state file, clear if corrupt | [Issue 9.1](#issue-91-phase-wont-resume-after-failure) |
| Slow dashboard | Add DB indexes, enable caching | [Issue 7.1](#issue-71-dashboard-loads-slowly-10-seconds) |

### Emergency Contacts

- **Security Incidents**: security-team@example.com
- **E-ISAC Reporting**: https://www.eisac.com/incident-reporting
- **MISP Support**: https://github.com/MISP/MISP/issues
- **Internal Team**: Slack #misp-support

### Useful Commands

```bash
# Quick health check
./scripts/health-check.sh

# Collect diagnostics
sudo ./scripts/collect-diagnostics.sh

# Restart MISP
cd /home/gallagher/misp-docker/ && sudo docker compose restart

# View recent errors
sudo docker logs misp-misp-core-1 --tail 50 | grep -i error

# Check API
curl -k -H "Authorization: $(cat ~/.misp/apikey)" https://localhost/users/view/me.json | jq .
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-25
**Maintainer**: Development Team
**Feedback**: Submit issues or improvements via pull request
