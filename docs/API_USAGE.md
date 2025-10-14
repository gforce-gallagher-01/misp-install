# MISP API Usage Guide

**Version:** 1.0
**Date:** 2025-10-14
**Author:** tKQB Enterprises

This guide explains how to use the MISP REST API from automation scripts, including API key setup, authentication, and best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [API Key Setup](#api-key-setup)
3. [Using the Helper Module](#using-the-helper-module)
4. [Direct API Usage](#direct-api-usage)
5. [Common Operations](#common-operations)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [API Endpoints Reference](#api-endpoints-reference)

---

## Overview

### Why Use the API?

The MISP REST API provides a clean, version-independent way to interact with MISP from automation scripts. Benefits include:

- ✅ **No Direct Database Access**: Cleaner, more maintainable code
- ✅ **Better Error Handling**: API responses provide detailed error messages
- ✅ **Version Independence**: API is more stable than database schema
- ✅ **RBAC Support**: Respects role-based access control
- ✅ **Audit Logging**: All API operations are logged by MISP
- ✅ **Industry Best Practice**: Standard approach for automation

### API Key vs Database Access

| Aspect | API (Recommended) | Database (Legacy) |
|--------|------------------|-------------------|
| Maintenance | Easy | Complex |
| Error Handling | Built-in | Manual |
| Security | RBAC + Audit | Direct access |
| Version Compatibility | High | Low (schema changes) |
| Performance | Good | Excellent |
| Use Case | Most operations | Large bulk imports |

**Recommendation**: Use API for all operations except large-scale data imports where performance is critical.

---

## API Key Setup

### Automatic Setup (New Installations)

Starting with **v5.5**, the installer automatically generates an API key during installation:

```bash
# Fresh install - API key auto-generated
python3 misp-install.py --config config/misp-config.json

# Check API key after installation
sudo cat /opt/misp/.env | grep MISP_API_KEY
sudo cat /opt/misp/PASSWORDS.txt | grep -A 3 "API KEY"
```

The API key is stored in two locations:
- `/opt/misp/.env` - Environment variable format: `MISP_API_KEY=<key>`
- `/opt/misp/PASSWORDS.txt` - Human-readable format with usage notes

### Manual API Key Generation

If you need to generate a new API key or are using an older installation:

#### Method 1: Via Web Interface (Recommended)

1. Login to MISP web interface: `https://your-misp-domain`
2. Navigate to: **Global Actions > My Profile**
3. Click the **Auth Keys** tab
4. Click **Add authentication key**
5. Configure settings:
   - **Comment**: "Automation Scripts" (optional)
   - **Allowed IPs**: Leave blank for all, or specify Docker network: `172.0.0.0/8`
   - **Expiration**: Leave blank for no expiration
6. Click **Submit**
7. Copy the generated API key (40 characters)

#### Method 2: Via CLI (Advanced)

```bash
# Generate new API key for admin user
cd /opt/misp
sudo docker compose exec -T misp-core \
  /var/www/MISP/app/Console/cake user change_authkey admin@your-domain.com

# Output: Old authentication keys disabled and new key created: <KEY>
```

#### Method 3: Using Python Script

```python
#!/usr/bin/env python3
import subprocess
import re

def generate_api_key(admin_email):
    """Generate new MISP API key via CLI"""
    result = subprocess.run([
        'sudo', 'docker', 'compose', 'exec', '-T', 'misp-core',
        '/var/www/MISP/app/Console/cake', 'user', 'change_authkey',
        admin_email
    ], capture_output=True, text=True, cwd='/opt/misp')

    # Extract API key from output
    match = re.search(r'new key created:\s*(\w+)', result.stdout)
    if match:
        return match.group(1)
    return None

# Usage
api_key = generate_api_key('admin@test.local')
print(f"Generated API key: {api_key}")
```

### Storing the API Key

After generating an API key, add it to `/opt/misp/.env`:

```bash
# Add to .env file
echo "MISP_API_KEY=your_api_key_here" | sudo tee -a /opt/misp/.env

# Set proper permissions
sudo chmod 600 /opt/misp/.env
sudo chown misp-owner:misp-owner /opt/misp/.env
```

Or set as environment variable:

```bash
# Temporary (current session)
export MISP_API_KEY=your_api_key_here

# Permanent (add to ~/.bashrc or ~/.profile)
echo "export MISP_API_KEY=your_api_key_here" >> ~/.bashrc
source ~/.bashrc
```

---

## Using the Helper Module

The `misp_api.py` module provides a centralized way to handle API authentication and requests.

### Installation

The module is included in the main installation directory:

```bash
cd /home/your-user/misp-install/misp-install
ls -la misp_api.py  # Should exist
```

### Quick Start

```python
#!/usr/bin/env python3
from misp_api import get_api_key, get_misp_client, test_connection

# Test connection
success, message = test_connection()
if success:
    print(f"✓ {message}")  # Connected to MISP 2.5.17.1
else:
    print(f"✗ {message}")  # Connection failed: ...
    exit(1)

# Get configured client
session = get_misp_client()

# Make API request
response = session.get(f"{session.misp_url}/feeds/index")
if response.status_code == 200:
    feeds = response.json()
    print(f"Found {len(feeds)} feeds")
```

### Module Functions

#### `get_api_key(env_file=None)`

Retrieves MISP API key from multiple sources (in order of precedence):

1. `MISP_API_KEY` environment variable
2. `/opt/misp/.env` file
3. `/opt/misp/PASSWORDS.txt` file

```python
from misp_api import get_api_key

# Auto-detect from default locations
api_key = get_api_key()

# Specify custom .env file
api_key = get_api_key(env_file='/custom/path/.env')

if api_key:
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
else:
    print("No API key found!")
```

#### `get_misp_url(env_file=None)`

Retrieves MISP base URL from configuration.

```python
from misp_api import get_misp_url

# Auto-detect from .env or use default
misp_url = get_misp_url()  # Returns: https://misp-test.lan

# Use environment variable
import os
os.environ['MISP_URL'] = 'https://misp.company.com'
misp_url = get_misp_url()  # Returns: https://misp.company.com
```

#### `get_misp_client(api_key=None, misp_url=None, timeout=30)`

Returns a configured `requests.Session` object with proper headers and settings.

```python
from misp_api import get_misp_client

# Auto-detect API key and URL
session = get_misp_client()

# Specify custom values
session = get_misp_client(
    api_key='your_key_here',
    misp_url='https://misp.company.com',
    timeout=60
)

# Session is pre-configured with:
# - Authorization header
# - Accept: application/json
# - Content-Type: application/json
# - SSL verification disabled (self-signed certs)
# - Default timeout
# - MISP URL stored as session.misp_url

# Make requests
response = session.get(f"{session.misp_url}/events/index")
response = session.post(f"{session.misp_url}/feeds/add", json=feed_data)
```

#### `test_connection(session=None, api_key=None, misp_url=None)`

Tests connectivity to MISP API and returns status.

```python
from misp_api import test_connection

# Test with auto-detected settings
success, message = test_connection()
if success:
    print(message)  # "Connected to MISP 2.5.17.1"
else:
    print(f"Failed: {message}")

# Test with custom settings
success, message = test_connection(
    api_key='your_key',
    misp_url='https://misp.company.com'
)
```

### Complete Example Script

```python
#!/usr/bin/env python3
"""
Example: List all enabled MISP feeds using API helper
"""
import sys
from misp_api import get_misp_client, test_connection

def main():
    # Test connection first
    print("Testing MISP connection...")
    success, message = test_connection()
    if not success:
        print(f"✗ Connection failed: {message}")
        sys.exit(1)

    print(f"✓ {message}\n")

    # Get API client
    session = get_misp_client()

    # Fetch feeds
    print("Fetching feeds...")
    response = session.get(f"{session.misp_url}/feeds/index")

    if response.status_code != 200:
        print(f"✗ API request failed: HTTP {response.status_code}")
        print(response.text[:200])
        sys.exit(1)

    feeds = response.json()

    # Filter enabled feeds
    if isinstance(feeds, dict) and 'Feed' in feeds:
        feeds_list = feeds['Feed']
    else:
        feeds_list = feeds

    enabled_feeds = [
        f for f in feeds_list
        if f.get('Feed', f).get('enabled') in ['1', 1, True]
    ]

    # Display results
    print(f"\n✓ Found {len(feeds_list)} total feeds")
    print(f"✓ {len(enabled_feeds)} enabled feeds:\n")

    for feed in enabled_feeds:
        feed_data = feed.get('Feed', feed)
        print(f"  • {feed_data.get('name')}")
        print(f"    URL: {feed_data.get('url')}")
        print(f"    Format: {feed_data.get('source_format')}")
        print()

if __name__ == '__main__':
    main()
```

**Run the script:**

```bash
# If API key in .env or PASSWORDS.txt
python3 example_feeds.py

# If API key in environment
MISP_API_KEY=your_key python3 example_feeds.py
```

---

## Direct API Usage

If you prefer not to use the helper module, you can make direct API requests using the `requests` library.

### Basic Authentication

```python
import requests
import os

# Configuration
MISP_URL = "https://misp-test.lan"
MISP_API_KEY = os.getenv('MISP_API_KEY', 'your_key_here')

# Headers for all requests
headers = {
    'Authorization': MISP_API_KEY,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Make request
response = requests.get(
    f"{MISP_URL}/servers/getPyMISPVersion.json",
    headers=headers,
    verify=False,  # Self-signed certificate
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print(f"MISP Version: {data['version']}")
```

### Disable SSL Warnings

When using self-signed certificates, disable SSL warnings:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

---

## Common Operations

### GET Request: Fetch Data

```python
from misp_api import get_misp_client

session = get_misp_client()

# Get all feeds
response = session.get(f"{session.misp_url}/feeds/index")
feeds = response.json()

# Get specific event
event_id = 123
response = session.get(f"{session.misp_url}/events/view/{event_id}")
event = response.json()

# Search events
response = session.post(
    f"{session.misp_url}/events/restSearch",
    json={'published': 1, 'last': '7d'}
)
events = response.json()
```

### POST Request: Create Resource

```python
from misp_api import get_misp_client

session = get_misp_client()

# Add a new feed
feed_data = {
    'name': 'Example Feed',
    'provider': 'Example Provider',
    'url': 'https://example.com/feed.json',
    'source_format': 'misp',
    'enabled': 1,
    'caching_enabled': 1,
    'distribution': 3
}

response = session.post(
    f"{session.misp_url}/feeds/add",
    json=feed_data
)

if response.status_code in [200, 201]:
    result = response.json()
    print(f"✓ Feed created: {result}")
else:
    print(f"✗ Failed: HTTP {response.status_code}")
    print(response.text)
```

### PUT/POST Request: Update Resource

```python
from misp_api import get_misp_client

session = get_misp_client()

# Enable a feed
feed_id = 42
response = session.post(
    f"{session.misp_url}/feeds/enable/{feed_id}"
)

if response.status_code in [200, 201]:
    print(f"✓ Feed {feed_id} enabled")
else:
    print(f"✗ Failed: HTTP {response.status_code}")
```

### DELETE Request: Remove Resource

```python
from misp_api import get_misp_client

session = get_misp_client()

# Delete a feed (use with caution!)
feed_id = 42
response = session.delete(
    f"{session.misp_url}/feeds/delete/{feed_id}"
)

if response.status_code == 200:
    print(f"✓ Feed {feed_id} deleted")
```

---

## Error Handling

### HTTP Status Codes

```python
from misp_api import get_misp_client

session = get_misp_client()

response = session.get(f"{session.misp_url}/feeds/index")

if response.status_code == 200:
    # Success
    data = response.json()
    print(f"Retrieved {len(data)} feeds")

elif response.status_code == 401:
    # Unauthorized - invalid API key
    print("✗ Invalid API key")
    print("Check: /opt/misp/.env or PASSWORDS.txt")

elif response.status_code == 403:
    # Forbidden - insufficient permissions
    print("✗ Insufficient permissions")
    print("API key may not have required role")

elif response.status_code == 404:
    # Not found - endpoint or resource doesn't exist
    print("✗ Resource not found")

elif response.status_code == 500:
    # Internal server error
    print("✗ MISP server error")
    print(response.text[:200])

else:
    # Other error
    print(f"✗ Unexpected error: HTTP {response.status_code}")
    print(response.text[:200])
```

### Exception Handling

```python
from misp_api import get_misp_client
import requests

session = get_misp_client()

try:
    response = session.get(
        f"{session.misp_url}/feeds/index",
        timeout=30
    )
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx

    data = response.json()
    print(f"✓ Success: {len(data)} feeds")

except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection failed: {e}")
    print("Check: Is MISP running? Is URL correct?")

except requests.exceptions.Timeout as e:
    print(f"✗ Request timeout: {e}")
    print("Check: Is MISP responding? Network issues?")

except requests.exceptions.HTTPError as e:
    print(f"✗ HTTP error: {e}")
    print(f"Response: {response.text[:200]}")

except requests.exceptions.JSONDecodeError as e:
    print(f"✗ Invalid JSON response: {e}")
    print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"✗ Unexpected error: {e}")
```

### Retry Logic

```python
from misp_api import get_misp_client
import time

def api_request_with_retry(session, url, max_retries=3, backoff=2):
    """Make API request with exponential backoff retry"""

    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()

            elif response.status_code in [500, 502, 503, 504]:
                # Server error - retry
                if attempt < max_retries - 1:
                    wait_time = backoff ** attempt
                    print(f"⚠ Server error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Max retries exceeded: HTTP {response.status_code}")

            else:
                # Client error - don't retry
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = backoff ** attempt
                print(f"⚠ Connection error, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise

# Usage
session = get_misp_client()
feeds = api_request_with_retry(session, f"{session.misp_url}/feeds/index")
```

---

## Best Practices

### 1. Use the Helper Module

```python
# ✓ GOOD: Use helper module
from misp_api import get_misp_client, test_connection

success, message = test_connection()
if success:
    session = get_misp_client()
    # ... make requests

# ✗ BAD: Duplicate configuration in every script
MISP_URL = "https://misp-test.lan"
MISP_API_KEY = "hardcoded_key"  # Never hardcode!
```

### 2. Never Hardcode API Keys

```python
# ✓ GOOD: Use environment or config files
from misp_api import get_api_key
api_key = get_api_key()  # Auto-detects from .env or PASSWORDS.txt

# ✓ GOOD: Use environment variable
import os
api_key = os.getenv('MISP_API_KEY')

# ✗ BAD: Hardcoded API key
api_key = "eAoY3YZmcY4qplWQnxwoc98tu9ZtXrfUPIvR3NBk"  # NEVER DO THIS!
```

### 3. Test Connection Before Operations

```python
# ✓ GOOD: Fail fast if connection issues
from misp_api import test_connection

success, message = test_connection()
if not success:
    print(f"✗ {message}")
    sys.exit(1)

# Now proceed with operations...

# ✗ BAD: Assume connection works
session = get_misp_client()
# ... operations may fail silently
```

### 4. Handle Errors Gracefully

```python
# ✓ GOOD: Specific error handling
try:
    response = session.get(url)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return None

# ✗ BAD: Generic catch-all
try:
    response = session.get(url)
    data = response.json()
except:
    pass  # Silently fails!
```

### 5. Use Proper Logging

```python
# ✓ GOOD: Use centralized logger
from misp_logger import get_logger

logger = get_logger('my-script', 'misp:automation')
logger.info("Fetching feeds", event_type="api", action="get_feeds")

try:
    response = session.get(url)
    logger.info("Feeds retrieved", count=len(response.json()))
except Exception as e:
    logger.error("Failed to fetch feeds", error=str(e))

# ✗ BAD: Print statements
print("Getting feeds...")  # Not logged anywhere
```

### 6. Use Pagination for Large Datasets

```python
# ✓ GOOD: Paginate large results
def get_all_events(session, limit=100):
    """Fetch all events with pagination"""
    all_events = []
    page = 1

    while True:
        response = session.post(
            f"{session.misp_url}/events/restSearch",
            json={'limit': limit, 'page': page}
        )

        events = response.json()
        if not events:
            break

        all_events.extend(events)
        page += 1

    return all_events

# ✗ BAD: Fetch everything at once (may timeout or run out of memory)
response = session.get(f"{session.misp_url}/events/index")
all_events = response.json()  # Could be huge!
```

### 7. Set Appropriate Timeouts

```python
# ✓ GOOD: Set timeouts for all requests
response = session.get(url, timeout=30)  # 30 second timeout

# For long-running operations
response = session.post(url, json=data, timeout=300)  # 5 minute timeout

# ✗ BAD: No timeout (may hang forever)
response = session.get(url)  # Could block indefinitely
```

### 8. Validate Response Data

```python
# ✓ GOOD: Validate before using
response = session.get(f"{session.misp_url}/feeds/index")

if response.status_code == 200:
    data = response.json()

    # Handle different response formats
    if isinstance(data, dict) and 'Feed' in data:
        feeds = data['Feed']
    elif isinstance(data, list):
        feeds = data
    else:
        print(f"✗ Unexpected format: {type(data)}")
        return None

    # Validate feed structure
    for feed in feeds:
        feed_data = feed.get('Feed', feed)
        if 'id' not in feed_data or 'name' not in feed_data:
            print(f"✗ Invalid feed structure: {feed_data}")
            continue

        # Now safe to use
        print(f"Feed: {feed_data['name']}")

# ✗ BAD: Assume response format
feeds = response.json()['Feed']  # May KeyError!
for feed in feeds:
    print(feed['name'])  # May KeyError!
```

---

## Troubleshooting

### Problem: "No API key found"

**Symptoms:**
```
✗ No API key found
MISP API key not found. Set MISP_API_KEY environment variable or add to /opt/misp/.env
```

**Solutions:**

1. Check if API key exists:
   ```bash
   sudo cat /opt/misp/.env | grep MISP_API_KEY
   sudo cat /opt/misp/PASSWORDS.txt | grep -A 3 "API KEY"
   ```

2. If missing, generate API key:
   ```bash
   cd /opt/misp
   sudo docker compose exec -T misp-core \
     /var/www/MISP/app/Console/cake user change_authkey admin@your-domain.com
   ```

3. Add to .env file:
   ```bash
   echo "MISP_API_KEY=<your_key>" | sudo tee -a /opt/misp/.env
   ```

4. Set environment variable:
   ```bash
   export MISP_API_KEY=<your_key>
   ```

### Problem: "Permission denied" reading .env

**Symptoms:**
```
⚠️  Cannot read /opt/misp/.env - permission denied
```

**Solutions:**

1. Use sudo to read (preferred):
   ```bash
   sudo cat /opt/misp/.env | grep MISP_API_KEY
   ```

2. Set ACLs for your user (v5.4+ only):
   ```bash
   sudo setfacl -m u:$USER:r /opt/misp/.env
   ```

3. Use environment variable instead:
   ```bash
   MISP_API_KEY=$(sudo cat /opt/misp/.env | grep MISP_API_KEY | cut -d= -f2)
   export MISP_API_KEY
   ```

### Problem: HTTP 401 Unauthorized

**Symptoms:**
```
✗ HTTP 401: {"name":"Invalid user credentials.","message":"Invalid user credentials.","url":"\/feeds\/index"}
```

**Causes:**
- Invalid API key
- Expired API key
- API key for wrong MISP instance

**Solutions:**

1. Verify API key is correct:
   ```bash
   # Check stored key
   sudo cat /opt/misp/.env | grep MISP_API_KEY

   # Test with curl
   curl -k -H "Authorization: $(sudo cat /opt/misp/.env | grep MISP_API_KEY | cut -d= -f2)" \
     https://misp-test.lan/servers/getPyMISPVersion.json
   ```

2. Generate new API key:
   ```bash
   cd /opt/misp
   sudo docker compose exec -T misp-core \
     /var/www/MISP/app/Console/cake user change_authkey admin@your-domain.com
   ```

3. Update .env with new key:
   ```bash
   # Remove old key
   sudo sed -i '/MISP_API_KEY/d' /opt/misp/.env

   # Add new key
   echo "MISP_API_KEY=<new_key>" | sudo tee -a /opt/misp/.env
   ```

### Problem: HTTP 403 Forbidden

**Symptoms:**
```
✗ HTTP 403: {"name":"Access denied","message":"You do not have permission to access this resource","url":"\/admin\/users\/index"}
```

**Causes:**
- API key doesn't have required permissions
- Trying to access admin-only endpoint

**Solutions:**

1. Check user role:
   ```bash
   cd /opt/misp
   sudo docker compose exec -T misp-core \
     /var/www/MISP/app/Console/cake user list
   ```

2. Use site admin API key for admin operations

3. Use appropriate endpoints for your role

### Problem: HTTP 500 Internal Server Error

**Symptoms:**
```
✗ HTTP 500: Internal server error
```

**Causes:**
- MISP server bug
- Invalid request data
- Database issues

**Solutions:**

1. Check MISP logs:
   ```bash
   cd /opt/misp
   sudo docker compose logs misp-core --tail 100
   ```

2. Check database connection:
   ```bash
   cd /opt/misp
   sudo docker compose ps db
   ```

3. Try with different data:
   ```python
   # Minimal test
   response = session.get(f"{session.misp_url}/servers/getPyMISPVersion.json")
   ```

4. Known issues:
   - `/news/add` endpoint returns HTTP 500 (use database version instead)

### Problem: Connection Timeout

**Symptoms:**
```
✗ Request timeout: HTTPConnectionPool(host='misp-test.lan', port=443): Read timed out. (read timeout=30)
```

**Solutions:**

1. Check MISP is running:
   ```bash
   cd /opt/misp
   sudo docker compose ps
   ```

2. Check network connectivity:
   ```bash
   ping misp-test.lan
   curl -k https://misp-test.lan
   ```

3. Increase timeout:
   ```python
   session = get_misp_client(timeout=120)  # 2 minute timeout
   ```

4. Check for slow operations:
   ```bash
   cd /opt/misp
   sudo docker compose logs misp-core --tail 50
   ```

### Problem: SSL Certificate Verification Failed

**Symptoms:**
```
✗ SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions:**

1. Disable SSL verification (development only):
   ```python
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

   response = requests.get(url, verify=False)
   ```

2. The helper module already disables verification:
   ```python
   from misp_api import get_misp_client
   session = get_misp_client()  # verify=False by default
   ```

3. For production, use proper SSL certificates (Let's Encrypt, commercial CA)

---

## API Endpoints Reference

### Common Endpoints

#### Server Information

```python
# Get MISP version
GET /servers/getPyMISPVersion.json

# Get server settings
GET /servers/getSettings
```

#### Feeds Management

```python
# List all feeds
GET /feeds/index

# Get specific feed
GET /feeds/view/{id}

# Add new feed
POST /feeds/add
Body: {
  "name": "Feed Name",
  "provider": "Provider",
  "url": "https://example.com/feed.json",
  "source_format": "misp",
  "enabled": 1,
  "caching_enabled": 1,
  "distribution": 3
}

# Enable feed
POST /feeds/enable/{id}

# Disable feed
POST /feeds/disable/{id}

# Delete feed
DELETE /feeds/delete/{id}

# Fetch feed data
GET /feeds/fetchFromFeed/{id}
```

#### Events Management

```python
# List events
GET /events/index

# Get specific event
GET /events/view/{id}

# Search events
POST /events/restSearch
Body: {
  "published": 1,
  "last": "7d",
  "threat_level_id": [1, 2]
}

# Create event
POST /events/add
Body: {
  "info": "Event description",
  "distribution": 3,
  "threat_level_id": 2,
  "analysis": 1
}

# Update event
PUT /events/edit/{id}

# Delete event
DELETE /events/delete/{id}
```

#### Attributes Management

```python
# Add attribute to event
POST /attributes/add/{event_id}
Body: {
  "type": "ip-src",
  "value": "192.168.1.1",
  "category": "Network activity",
  "to_ids": True
}

# Search attributes
POST /attributes/restSearch
Body: {
  "returnFormat": "json",
  "type": "ip-src",
  "last": "30d"
}
```

#### Users Management (Admin Only)

```python
# List users
GET /admin/users/index

# Create user
POST /admin/users/add

# Edit user
PUT /admin/users/edit/{id}

# Delete user
DELETE /admin/users/delete/{id}
```

### API Response Formats

#### Success Response

```json
{
  "Feed": {
    "id": "42",
    "name": "Example Feed",
    "provider": "Example Provider",
    "url": "https://example.com/feed.json",
    "enabled": "1",
    "caching_enabled": "1"
  }
}
```

#### Error Response

```json
{
  "name": "Invalid request",
  "message": "Missing required field: name",
  "url": "/feeds/add"
}
```

#### List Response

```json
{
  "Feed": [
    {"id": "1", "name": "Feed 1", ...},
    {"id": "2", "name": "Feed 2", ...}
  ]
}
```

Or sometimes just an array:

```json
[
  {"Feed": {"id": "1", "name": "Feed 1", ...}},
  {"Feed": {"id": "2", "name": "Feed 2", ...}}
]
```

**Note**: MISP API response formats can vary. Always validate structure before accessing fields.

---

## Additional Resources

### Official Documentation

- [MISP API Documentation](https://www.misp-project.org/openapi/)
- [PyMISP Documentation](https://pymisp.readthedocs.io/)
- [MISP REST Client](https://www.misp-project.org/documentation/#rest-client)

### Example Scripts

All example scripts are in the `scripts/` directory:

- `add-nerc-cip-news-feeds-api.py` - Add feeds via API
- `check-misp-feeds-api.py` - Check feed status via API
- `populate-misp-news-complete.py` - Populate news (hybrid API + DB)

### Helper Modules

- `misp_api.py` - API authentication and requests helper
- `misp_logger.py` - Centralized JSON logging

### Testing Your API Access

Run the helper module in test mode:

```bash
# Test with auto-detected API key
python3 misp_api.py

# Test with environment variable
MISP_API_KEY=your_key python3 misp_api.py

# Expected output:
# MISP API Helper - Test Mode
#
# 1. Testing API key retrieval...
#    ✓ API key found: eAoY3YZm...3NBk
#
# 2. Testing MISP URL retrieval...
#    ✓ MISP URL: https://misp-test.lan
#
# 3. Testing client creation...
#    ✓ Client created
#
# 4. Testing connection to MISP...
#    ✓ Connected to MISP 2.5.17.1
#
# ============================================================
# ✓ All tests passed!
# ============================================================
```

---

## Questions or Issues?

If you encounter issues not covered in this guide:

1. Check MISP logs: `cd /opt/misp && sudo docker compose logs misp-core --tail 100`
2. Check script logs: `ls -la /opt/misp/logs/`
3. Review KNOWN-ISSUES.md for documented problems
4. Consult CLAUDE.md for development guidance

---

**Last Updated:** 2025-10-14
**Version:** 1.0
**Author:** tKQB Enterprises
