# MISP Platform Quirks & Workarounds

**Purpose**: Document MISP-specific issues, gotchas, and workarounds to save debugging time
**Last Updated**: 2025-10-25
**Version**: 1.0

This document catalogs undocumented MISP behaviors, API quirks, and platform limitations discovered during development. Understanding these quirks saves hours of debugging.

---

## Table of Contents

1. [Dashboard Widget Quirks](#dashboard-widget-quirks)
2. [API Quirks](#api-quirks)
3. [Tag Search Behavior](#tag-search-behavior)
4. [Database Direct Access](#database-direct-access)
5. [File Operations](#file-operations)
6. [Docker Container Quirks](#docker-container-quirks)
7. [Configuration Oddities](#configuration-oddities)
8. [Performance Gotchas](#performance-gotchas)
9. [Security Considerations](#security-considerations)
10. [Workarounds Summary](#workarounds-summary)

---

## Dashboard Widget Quirks

### Quirk 1: Abstract Class Instantiation Bug

**Problem**: MISP's dashboard loader scans `/app/Lib/Dashboard/Custom/` and attempts to instantiate EVERY `.php` file, including abstract base classes.

**Symptom**:
```
PHP Fatal error: Cannot instantiate abstract class BaseWidget
```

**Cause**: `Dashboard::loadAllWidgets()` does:
```php
$files = scandir($customWidgetDir);
foreach ($files as $file) {
    if (substr($file, -4) === '.php') {
        $className = substr($file, 0, -4);
        $widget = new $className();  // ❌ Fails on abstract classes
    }
}
```

**Workaround**: Use PHP traits instead of abstract base classes
```php
// ❌ DON'T DO THIS
abstract class BaseWidget {
    abstract public function handler($user, $options);
}

// ✅ DO THIS INSTEAD
trait WidgetHelpers {
    protected function checkPermissions($user) { ... }
}

class MyWidget {
    use WidgetHelpers;
    public function handler($user, $options) { ... }
}
```

**Impact**: Critical - breaks entire "Add Widget" functionality

**Documented In**: `docs/PATTERNS.md`, `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md`

---

### Quirk 2: Tag Wildcard Matching

**Problem**: Tag searches DO NOT auto-wildcard. The tag `'ics:'` is treated as literal string, not prefix.

**Expected Behavior**:
```php
// Expect this to match: ics:malware, ics:attack-target, ics:*
'tags' => array('ics:')  // ❌ Only matches literal "ics:"
```

**Actual Behavior**: MISP searches for exact tag name "ics:" (which doesn't exist)

**Workaround**: Use explicit wildcard `%`
```php
// ✅ Correct - matches all tags starting with "ics:"
'tags' => array('ics:%')
```

**SQL Equivalent**:
```sql
-- What you expect
SELECT * FROM events WHERE tag LIKE 'ics:%'

-- What happens without wildcard
SELECT * FROM events WHERE tag = 'ics:'
```

**Impact**: Critical - widgets show no data, appears broken

**Example**:
```php
// BROKEN - returns 0 events
$eventIds = $Event->fetchEventIds($user, array(
    'tags' => array('ics:'),
    'published' => 1
));

// FIXED - returns all ICS events
$eventIds = $Event->fetchEventIds($user, array(
    'tags' => array('ics:%'),  // Added % wildcard
    'published' => 1
));
```

**Documented In**: `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md`

---

### Quirk 3: Tag Structure Inconsistency

**Problem**: Different API endpoints return tags in different structures.

**Structure 1** (`/events/restSearch`):
```json
{
    "Event": {
        "id": "123",
        "Tag": [
            {"name": "ics:malware", "colour": "#ff0000"},
            {"name": "tlp:white", "colour": "#ffffff"}
        ]
    }
}
```

**Structure 2** (`/events/view/:id`):
```json
{
    "Event": {
        "id": "123",
        "EventTag": [
            {
                "Tag": {
                    "name": "ics:malware",
                    "colour": "#ff0000"
                }
            },
            {
                "Tag": {
                    "name": "tlp:white",
                    "colour": "#ffffff"
                }
            }
        ]
    }
}
```

**Workaround**: Always check both structures
```php
protected function extractTags($event)
{
    $tags = array();

    // Structure 1: Tag array (restSearch)
    if (!empty($event['Tag'])) {
        foreach ($event['Tag'] as $tag) {
            $tags[] = $tag['name'];
        }
    }
    // Structure 2: EventTag array (events/view)
    elseif (!empty($event['EventTag'])) {
        foreach ($event['EventTag'] as $eventTag) {
            $tags[] = $eventTag['Tag']['name'];
        }
    }

    return $tags;
}
```

**Impact**: Medium - widgets fail to extract tags correctly

---

### Quirk 4: Time Filter Uses Date Field, Not Timestamp

**Problem**: Widget filters like `'last' => '7d'` check the event's `date` field, NOT the publish timestamp.

**Consequence**: Events with historical dates (e.g., documenting 2022 attack) don't appear in time-based widgets even if published today.

**Example**:
```php
// Event created today but date set to historical attack
$event = array(
    'date' => '2022-04-08',        // Historical Industroyer2 attack
    'info' => 'Industroyer2 Attack',
    'published' => true,
    'timestamp' => 1730000000       // Today's timestamp
);

// This filter WON'T match (checks date field)
$eventIds = $Event->fetchEventIds($user, array(
    'last' => '7d'  // Only events with date in last 7 days
));
```

**Workaround**: Use recent dates for sample/demo events
```python
# For demo/test events, use recent dates
from datetime import datetime, timedelta

recent_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

event_data = {
    "Event": {
        "date": recent_date,  # Use recent date for widget visibility
        "info": "Industroyer2 Attack (Historical - April 2022)",  # Context in description
        "published": True
    }
}
```

**Impact**: High - time-based widgets appear empty

---

## API Quirks

### Quirk 5: REST API vs CakePHP API Differences

**Problem**: MISP has two API styles with different behaviors.

**REST API** (`/events/restSearch`):
- Returns full event objects
- Supports complex filters
- JSON input and output
- Preferred for searching

**CakePHP API** (`/events/index.json`):
- Returns event listings
- Limited filtering
- URL parameters only
- Legacy approach

**Recommendation**: Use REST API (`restSearch`) for all new code

**Example**:
```python
# ✅ PREFERRED: REST API
response = requests.post(
    f"{misp_url}/events/restSearch",
    headers={'Authorization': api_key},
    json={'tags': ['ics:%'], 'published': 1}
)

# ❌ LEGACY: CakePHP API
response = requests.get(
    f"{misp_url}/events/index.json",
    headers={'Authorization': api_key},
    params={'searchtag': 'ics'}
)
```

---

### Quirk 6: HTTP 500 on /news/add Endpoint

**Problem**: The `/news/add` API endpoint returns HTTP 500 error even with correct data.

**Status**: Upstream MISP bug (as of 2025-10-25)

**Symptom**:
```bash
$ curl -X POST https://localhost/news/add \
    -H "Authorization: $API_KEY" \
    -d '{"News": {"title": "Test", "message": "Test message"}}'

HTTP/1.1 500 Internal Server Error
```

**Workaround**: Use direct database insertion
```python
# Instead of API, insert directly into database
from lib.database_manager import DatabaseManager

db = DatabaseManager()
db.execute("""
    INSERT INTO news (title, message, created)
    VALUES (%s, %s, NOW())
""", (title, message))
```

**Impact**: Medium - can't use API for news, must use DB

**Documented In**: `deprecated/scripts/populate-misp-news-api.py` (why it's deprecated)

---

### Quirk 7: API Key Storage

**Problem**: MISP API key is NOT stored in config file, it's in the database.

**Location**: `users` table, `authkey` column

**Retrieval**:
```bash
# Via API (requires existing valid key)
curl -k -H "Authorization: $CURRENT_KEY" \
     https://localhost/users/view/me.json | jq '.User.authkey'

# Via database
sudo docker exec misp-misp-db-1 mysql -u misp -pmisp -e \
     "SELECT authkey FROM misp.users WHERE email='admin@admin.test'"
```

**Storage Pattern**:
```bash
# Store in file for reuse
echo "API_KEY" > ~/.misp/apikey
chmod 600 ~/.misp/apikey

# Read in scripts
api_key=$(cat ~/.misp/apikey)
```

**Impact**: Low - just need to know where to find it

---

### Quirk 8: includeEventTags Required

**Problem**: By default, `restSearch` doesn't include event tags in response.

**Default Response** (no tags):
```json
{
    "Event": {
        "id": "123",
        "info": "Malware Campaign"
        // No Tag or EventTag array!
    }
}
```

**Workaround**: Add `includeEventTags` parameter
```python
events = misp_rest_search(api_key, {
    'published': 1,
    'includeEventTags': True  # ← Required to get tags
})
```

**Impact**: Medium - tags missing unless explicitly requested

---

## Tag Search Behavior

### Quirk 9: Tag OR vs AND Logic

**Problem**: Multiple tags in search use OR logic, not AND.

**Example**:
```php
'tags' => array('ics:%', 'tlp:white')
// Matches events with ics:* OR tlp:white (not both)
```

**For AND Logic**: Use multiple API calls and intersect results
```php
// Search for each tag separately
$ics_events = searchByTag('ics:%');
$tlp_events = searchByTag('tlp:white');

// Find intersection (events with BOTH tags)
$both_tags = array_intersect($ics_events, $tlp_events);
```

**Impact**: Medium - affects complex tag queries

---

### Quirk 10: Tag Negation

**Problem**: Can't natively search for "NOT tag".

**Workaround**: Fetch all, then filter
```php
// Get all events
$all_events = fetchAllEvents();

// Filter out unwanted tag
$filtered = array_filter($all_events, function($event) {
    $tags = extractTags($event);
    return !in_array('unwanted:tag', $tags);
});
```

**Impact**: Low - rare use case, but no native support

---

## Database Direct Access

### Quirk 11: Direct DB Access Sometimes Necessary

**Problem**: Some operations have no API endpoint, requiring direct database access.

**Cases Requiring Direct DB**:
1. News insertion (`/news/add` broken)
2. Bulk operations (faster than API loop)
3. Complex queries not supported by API
4. Configuration changes (some settings DB-only)

**Safe Access Pattern**:
```python
from lib.database_manager import DatabaseManager

db = DatabaseManager()

# READ operations (safe)
results = db.execute("SELECT * FROM events WHERE published = 1")

# WRITE operations (use transactions)
db.begin_transaction()
try:
    db.execute("INSERT INTO news VALUES (...)")
    db.execute("UPDATE users SET ...")
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

**⚠️ Caution**: Direct DB access bypasses MISP's validation and event system. Use only when API unavailable.

---

### Quirk 12: Database Schema Not Documented

**Problem**: MISP database schema not fully documented.

**Workaround**: Inspect database directly
```bash
# Show all tables
sudo docker exec misp-misp-db-1 mysql -u misp -pmisp -e "SHOW TABLES IN misp"

# Describe table structure
sudo docker exec misp-misp-db-1 mysql -u misp -pmisp -e "DESCRIBE misp.events"

# Find column names
sudo docker exec misp-misp-db-1 mysql -u misp -pmisp -e "SHOW COLUMNS FROM misp.events"
```

**Impact**: Medium - need to explore schema manually

---

## File Operations

### Quirk 13: Config File Permissions

**Problem**: MISP config files must be writable by Apache user (`www-data`).

**Symptom**: Settings changes via web UI don't persist

**Fix**:
```bash
sudo docker exec misp-misp-core-1 \
     chown www-data:www-data /var/www/MISP/app/Config/config.php

sudo docker exec misp-misp-core-1 \
     chmod 640 /var/www/MISP/app/Config/config.php
```

**Impact**: Low - one-time fix during installation

---

### Quirk 14: Log File Rotation

**Problem**: MISP doesn't rotate logs by default, can fill disk.

**Default Location**:
- `/var/www/MISP/app/tmp/logs/error.log`
- `/var/www/MISP/app/tmp/logs/debug.log`

**Workaround**: Configure logrotate
```bash
# Inside container
cat > /etc/logrotate.d/misp <<EOF
/var/www/MISP/app/tmp/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 640 www-data www-data
}
EOF
```

**Impact**: Medium - can cause disk space issues

---

## Docker Container Quirks

### Quirk 15: Health Check Domain Resolution

**Problem**: MISP health check uses `BASE_URL` domain, which container can't resolve internally.

**Symptom**:
```bash
$ docker ps
CONTAINER ID   IMAGE          STATUS
abc123         misp-core      Up (unhealthy)
```

**Cause**: Healthcheck tries:
```bash
curl -ks https://misp.lan/users/heartbeat
# But container can't resolve "misp.lan"
```

**Why It's Safe to Ignore**:
- MISP web interface IS accessible externally
- `/users/heartbeat` works when accessed via localhost
- Only the health check fails

**Verification**:
```bash
# Inside container - WORKS
sudo docker exec misp-misp-core-1 \
     curl -ks https://localhost/users/heartbeat

# From host - WORKS
curl -k https://localhost/users/heartbeat

# Health check (broken) - tries https://misp.lan/...
```

**Impact**: Low - cosmetic only, doesn't affect functionality

**Documented In**: `KNOWN-ISSUES.md`

---

### Quirk 16: Container File Persistence

**Problem**: Files created in container don't persist unless in volume.

**Volumes** (persistent):
- `/var/www/MISP/app/files/`
- `/var/www/MISP/app/Config/`
- `/var/www/MISP/app/tmp/`

**Ephemeral** (lost on container restart):
- `/var/www/MISP/app/Lib/Dashboard/Custom/` (unless mounted)
- Any other paths

**Workaround**: Copy files to host, mount as volume
```bash
# Copy widget to host
docker cp mywidget.php misp-misp-core-1:/var/www/MISP/app/Lib/Dashboard/Custom/

# Better: Mount directory as volume in docker-compose.yml
volumes:
  - ./custom_widgets:/var/www/MISP/app/Lib/Dashboard/Custom
```

**Impact**: High - affects custom widgets/code

---

## Configuration Oddities

### Quirk 17: Setting Precedence

**Problem**: MISP has multiple configuration layers with unclear precedence.

**Configuration Layers** (highest to lowest precedence):
1. Database (`admin_settings` table)
2. `app/Config/config.php`
3. `app/Config/bootstrap.php`
4. Default values in code

**Best Practice**: Use database for runtime settings, `config.php` for bootstrap

**Check Setting**:
```bash
# Via API
curl -k -H "Authorization: $API_KEY" \
     https://localhost/servers/serverSettings.json | jq '.finalSettings.MISP.baseurl'

# Via database
sudo docker exec misp-misp-db-1 mysql -u misp -pmisp -e \
     "SELECT * FROM misp.admin_settings WHERE setting='MISP.baseurl'"
```

---

### Quirk 18: Some Settings Require Restart

**Problem**: Not all settings apply immediately.

**Require Restart**:
- `MISP.baseurl`
- PHP memory limits
- Worker configurations
- Plugin enable/disable

**Apply Immediately**:
- User preferences
- Sharing configurations
- Most security settings

**Restart Method**:
```bash
sudo docker restart misp-misp-core-1
```

**Impact**: Medium - need to know which settings require restart

---

## Performance Gotchas

### Quirk 19: Large Tag Sets Slow Queries

**Problem**: Queries with many tags become very slow.

**Slow**:
```php
$eventIds = $Event->fetchEventIds($user, array(
    'tags' => array('tag1', 'tag2', 'tag3', ... 'tag50')
));
```

**Faster**: Break into smaller queries
```php
$results = array();
foreach (array_chunk($tags, 10) as $tag_batch) {
    $batch_results = $Event->fetchEventIds($user, array(
        'tags' => $tag_batch
    ));
    $results = array_merge($results, $batch_results);
}
```

**Impact**: Medium - affects complex queries

---

### Quirk 20: Event Correlation Overhead

**Problem**: MISP automatically correlates events, which can slow down bulk imports.

**Workaround**: Disable correlation during bulk import
```python
# Before bulk import
misp_set_setting(api_key, 'MISP.correlation', False)

# Import events
for event in bulk_events:
    misp_add_event(api_key, event)

# Re-enable and trigger correlation
misp_set_setting(api_key, 'MISP.correlation', True)
misp_trigger_correlation()
```

**Impact**: High - can 10x bulk import speed

---

## Security Considerations

### Quirk 21: Self-Signed Certificate

**Problem**: MISP Docker uses self-signed SSL certificate by default.

**Consequence**: Need to disable SSL verification in API calls
```python
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API call with verify=False
response = requests.post(
    misp_url,
    headers={'Authorization': api_key},
    json=data,
    verify=False  # Required for self-signed cert
)
```

**Production Fix**: Install proper SSL certificate
```bash
# Use Let's Encrypt
sudo certbot --nginx -d misp.yourdomain.com
```

**Impact**: Medium - affects all API calls

---

### Quirk 22: Default Sharing Levels

**Problem**: Default event distribution varies by MISP configuration.

**Distribution Levels**:
- `0` - Your organization only
- `1` - This community only
- `2` - Connected communities
- `3` - All communities
- `4` - Sharing group

**Safe Default**: Always explicitly set distribution
```python
event_data = {
    'Event': {
        'info': 'Event info',
        'distribution': 0,  # ← Always specify!
        'published': False
    }
}
```

**Impact**: High - incorrect sharing can leak sensitive data

---

## Workarounds Summary

### Quick Reference Table

| Quirk | Impact | Workaround | File Reference |
|-------|--------|------------|----------------|
| Abstract widget classes | Critical | Use PHP traits | `docs/PATTERNS.md` |
| Tag wildcard | Critical | Use `%` wildcard | `DASHBOARD_WIDGET_FIXES.md` |
| Tag structure inconsistency | Medium | Check both structures | `PATTERNS.md` (Widget pattern) |
| Time filter vs date | High | Use recent dates | `DASHBOARD_WIDGET_FIXES.md` |
| /news/add broken | Medium | Direct DB insert | `deprecated/scripts/` |
| Health check fails | Low | Ignore (cosmetic) | `KNOWN-ISSUES.md` |
| No tag AND logic | Medium | Fetch + intersect | This doc |
| Correlation overhead | High | Disable during import | This doc |

---

## Contributing to This Document

**Found a new quirk?** Please add it using this template:

```markdown
### Quirk N: Brief Description

**Problem**: What's the issue?

**Symptom**: How does it manifest?

**Cause**: Why does this happen?

**Workaround**: How to fix/avoid it?

**Example**: Code showing problem and solution

**Impact**: Critical|High|Medium|Low

**Documented In**: Link to related docs
```

---

**Maintained by**: tKQB Enterprises
**Version**: 1.0
**Last Updated**: 2025-10-25
**MISP Version Tested**: 2.4.x (Docker ghcr.io/misp/misp-docker)

**Note**: MISP is under active development. These quirks may be fixed in future versions. Always check latest MISP documentation and release notes.
