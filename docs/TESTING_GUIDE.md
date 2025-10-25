# Testing Guide

**Purpose**: Comprehensive guide to testing the MISP Installation Suite
**Last Updated**: 2025-10-25
**Version**: 1.0

This guide covers testing strategies, test scenarios, debugging techniques, and test data generation for the MISP Installation Suite.

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Environment Setup](#test-environment-setup)
3. [Types of Testing](#types-of-testing)
4. [Common Test Scenarios](#common-test-scenarios)
5. [Debugging Techniques](#debugging-techniques)
6. [Test Data Generation](#test-data-generation)
7. [CI/CD Testing](#cicd-testing)
8. [Performance Testing](#performance-testing)
9. [Security Testing](#security-testing)
10. [Test Checklists](#test-checklists)

---

## Testing Philosophy

### Current Testing Strategy

**Hybrid Approach**:
- **Manual Testing**: Primary method for end-to-end scenarios
- **Automated Testing**: Unit tests for critical helper functions
- **Integration Testing**: Manual verification of component interactions
- **Smoke Testing**: Quick checks after changes

**Why Hybrid?**:
- Complex Docker/MISP interactions hard to mock
- Real environment testing catches integration issues
- Automated tests for business logic
- Manual tests for user workflows

---

## Test Environment Setup

### Dedicated Test System

**Recommended Setup**:
- Separate VM or physical machine
- Ubuntu 22.04 LTS (clean install)
- Minimum specs: 4 CPU, 8GB RAM, 50GB storage
- Snapshot capability for quick rollback

**Setup Steps**:
```bash
# 1. Clone repository
git clone https://github.com/gforce-gallagher-01/misp-install.git
cd misp-install

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Create test user
sudo useradd -m -s /bin/bash misp-admin-test
sudo usermod -aG docker misp-admin-test

# 4. Take snapshot (VM only)
# Use VM hypervisor snapshot feature
```

---

### Test Configuration Files

**Minimal Test Config**:
```ini
# config/test-minimal.conf
[exclusions]
# Exclude non-essential features for fast testing
category:compliance
automated-maintenance
azure-ad
```

**Full Test Config**:
```ini
# config/test-full.conf
[exclusions]
# No exclusions - test everything
```

**Specific Feature Test**:
```ini
# config/test-widgets.conf
[exclusions]
# Exclude everything except widgets
category:threat_intel
category:integrations
azure-ad
automated-maintenance
```

---

## Types of Testing

### 1. Unit Testing

**Scope**: Individual functions and methods

**Tools**:
- `pytest` for Python tests
- `unittest` (built-in)

**Example Test**:
```python
# tests/test_misp_api_helpers.py
import pytest
from lib.misp_api_helpers import parse_event_tags

def test_parse_event_tags_with_tag_array():
    """Test parsing Tag array structure."""
    event = {
        'Tag': [
            {'name': 'ics:malware'},
            {'name': 'tlp:white'}
        ]
    }

    tags = parse_event_tags(event)

    assert len(tags) == 2
    assert 'ics:malware' in tags
    assert 'tlp:white' in tags

def test_parse_event_tags_with_eventtag_array():
    """Test parsing EventTag array structure."""
    event = {
        'EventTag': [
            {'Tag': {'name': 'ics:malware'}},
            {'Tag': {'name': 'tlp:white'}}
        ]
    }

    tags = parse_event_tags(event)

    assert len(tags) == 2
    assert 'ics:malware' in tags

def test_parse_event_tags_empty():
    """Test parsing event with no tags."""
    event = {}
    tags = parse_event_tags(event)
    assert tags == []
```

**Run Unit Tests**:
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_misp_api_helpers.py

# Run specific test
pytest tests/test_misp_api_helpers.py::test_parse_event_tags_with_tag_array

# Run with coverage
pytest --cov=lib tests/
```

---

### 2. Integration Testing

**Scope**: Multiple components working together

**Test Scenarios**:
- Phase → Helper → Docker → MISP
- API → Database → Response
- Config → Feature Exclusion → Phase Skip

**Example Integration Test**:
```python
# tests/integration/test_phase_execution.py
import pytest
from phases.phase_11_8_utilities_intel import Phase_11_8_UtilitiesIntel
from lib.state_manager import StateManager
import os

@pytest.fixture
def phase():
    """Create phase instance for testing."""
    return Phase_11_8_UtilitiesIntel()

@pytest.fixture(autouse=True)
def cleanup_state():
    """Clean up state file after each test."""
    yield
    state_file = 'state/phase_11_8_utilities_intel.json'
    if os.path.exists(state_file):
        os.remove(state_file)

def test_phase_execution_success(phase):
    """Test phase executes successfully."""
    # Preconditions
    assert phase.check_requirements() == True

    # Execute
    phase.run()

    # Verify state
    state = StateManager('phase_11_8_utilities_intel.json')
    saved_state = state.load()

    assert saved_state is not None
    assert saved_state['status'] == 'completed'
    assert 'completed_steps' in saved_state

def test_phase_skipped_when_excluded(phase):
    """Test phase skipped if feature excluded."""
    # Mock config to exclude feature
    # ... implementation

    phase.run()

    state = StateManager('phase_11_8_utilities_intel.json')
    saved_state = state.load()

    assert saved_state['status'] == 'skipped'
```

---

### 3. End-to-End Testing

**Scope**: Complete installation workflow

**Test Process**:
```bash
# 1. Start with clean system (snapshot restore)

# 2. Run installation
sudo python3 misp-install.py

# 3. Verify each phase completed
cat state/phase_*.json | jq '.status'

# 4. Verify MISP running
sudo docker ps | grep misp
curl -k https://localhost

# 5. Verify MISP accessible
# Login to web interface
# Check default user exists
# Verify taxonomies installed

# 6. Verify features
# Check feeds enabled
# Verify widgets installed
# Test API endpoint
```

---

### 4. Regression Testing

**Scope**: Ensure existing functionality still works after changes

**Test Cases**:
- Run full installation after code changes
- Verify all phases complete
- Check no new errors in logs
- Verify MISP functionality unchanged

**Automated Regression Test**:
```bash
#!/bin/bash
# scripts/regression-test.sh

# Store current commit
COMMIT=$(git rev-parse HEAD)
BASELINE="baseline-state"
CURRENT="current-state"

echo "Running regression test for commit $COMMIT"

# 1. Restore baseline snapshot
restore_snapshot "$BASELINE"

# 2. Run installation
sudo python3 misp-install.py 2>&1 | tee regression-${COMMIT}.log

# 3. Collect state
mkdir -p test-results/${COMMIT}
cp -r state/* test-results/${COMMIT}/
cp logs/* test-results/${COMMIT}/

# 4. Compare with baseline
diff -r test-results/baseline test-results/${COMMIT}

# 5. Report differences
if [ $? -eq 0 ]; then
    echo "✅ No regressions detected"
else
    echo "❌ Regressions found - review diff above"
    exit 1
fi
```

---

## Common Test Scenarios

### Scenario 1: Fresh Installation

**Goal**: Verify clean installation on fresh system

**Steps**:
1. Start with Ubuntu 22.04 clean install (or restore snapshot)
2. Run: `sudo python3 misp-install.py`
3. Monitor progress
4. Verify completion

**Success Criteria**:
- [ ] All phases complete successfully
- [ ] No errors in logs
- [ ] MISP web interface accessible
- [ ] Default admin user can login
- [ ] Taxonomies enabled
- [ ] Feeds configured

**Time**: ~45 minutes (full installation)

---

### Scenario 2: Minimal Installation

**Goal**: Test minimal configuration (fast feedback)

**Steps**:
```bash
sudo python3 misp-install.py --config config/test-minimal.conf
```

**Success Criteria**:
- [ ] Excluded features skipped
- [ ] Core features installed
- [ ] MISP operational

**Time**: ~10 minutes

---

### Scenario 3: Feature Exclusion

**Goal**: Verify feature exclusion system works

**Test Matrix**:
| Config | Excluded | Expected Result |
|--------|----------|-----------------|
| exclude-azure-ad.conf | Azure AD | Phase 11.X skipped |
| exclude-threat-intel.conf | category:threat_intel | Multiple phases skipped |
| exclude-widgets.conf | nerc-cip-dashboards | Widget installation skipped |

**Verification**:
```bash
# Check state files for "skipped" status
grep -r "skipped" state/*.json

# Verify features not installed
# (check for absence of files, configs, etc.)
```

---

### Scenario 4: Resume After Failure

**Goal**: Verify state management allows resume

**Steps**:
1. Start installation
2. Kill process mid-way (simulate failure)
3. Check state files
4. Resume installation
5. Verify it continues from last checkpoint

**Test**:
```bash
# Terminal 1: Start installation
sudo python3 misp-install.py

# Terminal 2: Wait for phase 5 to start, then kill
sleep 300  # Wait 5 minutes
pkill -9 python3

# Terminal 1: Resume
sudo python3 misp-install.py

# Should skip phases 1-4, resume from phase 5
```

**Success Criteria**:
- [ ] Phases 1-4 marked completed (not re-run)
- [ ] Phase 5+ execute
- [ ] No duplicate operations
- [ ] Installation completes successfully

---

### Scenario 5: Widget Installation

**Goal**: Verify dashboard widgets install and function

**Steps**:
1. Install with widgets enabled
2. Login to MISP web interface
3. Navigate to Dashboard
4. Click "Add Widget"
5. Verify custom widgets appear
6. Add widget to dashboard
7. Verify widget displays data

**Success Criteria**:
- [ ] Widgets appear in "Add Widget" list
- [ ] Widget can be added to dashboard
- [ ] Widget displays without errors
- [ ] Widget shows relevant data
- [ ] No PHP errors in MISP logs

**Common Widget Issues**:
```bash
# Check for widget installation
sudo docker exec misp-misp-core-1 ls -la /var/www/MISP/app/Lib/Dashboard/Custom/

# Check for PHP errors
sudo docker exec misp-misp-core-1 tail -50 /var/www/MISP/app/tmp/logs/error.log | grep -i widget

# Test widget directly (PHP)
sudo docker exec misp-misp-core-1 php -l /var/www/MISP/app/Lib/Dashboard/Custom/MyWidget.php
```

---

### Scenario 6: API Functionality

**Goal**: Verify MISP API works correctly

**Test Script**:
```bash
#!/bin/bash
# Test MISP API endpoints

API_KEY=$(cat ~/.misp/apikey)
MISP_URL="https://localhost"

echo "Testing MISP API..."

# Test 1: Get current user
echo "1. Getting current user..."
curl -k -H "Authorization: $API_KEY" \
     "$MISP_URL/users/view/me.json" | jq '.User.email'

# Test 2: Search events
echo "2. Searching events..."
curl -k -H "Authorization: $API_KEY" \
     -X POST "$MISP_URL/events/restSearch" \
     -H "Content-Type: application/json" \
     -d '{"published":1,"limit":5}' | jq '.response | length'

# Test 3: Get taxonomies
echo "3. Getting taxonomies..."
curl -k -H "Authorization: $API_KEY" \
     "$MISP_URL/taxonomies/index.json" | jq '. | length'

# Test 4: Get feeds
echo "4. Getting feeds..."
curl -k -H "Authorization: $API_KEY" \
     "$MISP_URL/feeds/index.json" | jq '. | length'

echo "API tests complete"
```

---

## Debugging Techniques

### 1. Log Analysis

**Primary Logs**:
```bash
# Installation logs (JSON format)
tail -f logs/misp_installer.log | jq '.'

# Filter by level
cat logs/misp_installer.log | jq 'select(.level=="ERROR")'

# Filter by logger
cat logs/misp_installer.log | jq 'select(.logger=="phase_11_8")'

# MISP application logs
sudo docker exec misp-misp-core-1 tail -f /var/www/MISP/app/tmp/logs/error.log

# MISP debug log
sudo docker exec misp-misp-core-1 tail -f /var/www/MISP/app/tmp/logs/debug.log
```

---

### 2. State Inspection

**Check Phase State**:
```bash
# List all state files
ls -la state/

# View specific phase state
cat state/phase_11_8_utilities_intel.json | jq '.'

# Check status of all phases
for f in state/*.json; do
    echo "$f: $(jq -r '.status' $f)"
done

# Find failed phases
grep -l '"status": "failed"' state/*.json
```

---

### 3. Docker Debugging

**Container Status**:
```bash
# Check all containers
sudo docker ps -a

# Check specific container logs
sudo docker logs misp-misp-core-1

# Check container health
sudo docker inspect misp-misp-core-1 | jq '.[0].State.Health'

# Enter container for debugging
sudo docker exec -it misp-misp-core-1 bash

# Check MISP processes inside container
sudo docker exec misp-misp-core-1 ps aux | grep -E "apache|mysql|redis"
```

---

### 4. Network Debugging

**MISP Accessibility**:
```bash
# Check if MISP responding
curl -k -I https://localhost

# Check specific port
sudo netstat -tlnp | grep 443

# Test from external machine
curl -k -I https://your-server-ip

# Check firewall
sudo ufw status
```

---

### 5. Database Debugging

**MISP Database**:
```bash
# Access MISP MySQL
sudo docker exec -it misp-misp-db-1 mysql -u misp -p

# Common queries
USE misp;
SHOW TABLES;
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM attributes;
SELECT * FROM users;
SELECT * FROM feeds;
```

---

### 6. Python Debugging

**Interactive Debugging**:
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use ipdb (install: pip install ipdb)
import ipdb; ipdb.set_trace()

# Run script
sudo python3 your_script.py

# Debugger commands:
# n - next line
# s - step into
# c - continue
# p variable - print variable
# l - show code context
# q - quit
```

**Verbose Output**:
```python
# Add verbose logging
from lib.misp_logger import get_logger
import logging

logger = get_logger('test', 'misp:test')
logger.setLevel(logging.DEBUG)

# Now all debug messages appear
logger.debug("Detailed debug info here")
```

---

## Test Data Generation

### Generate Test Events

**Script**: `scripts/generate-test-events.py`
```python
#!/usr/bin/env python3
"""
Generate test events for MISP testing.
"""
from lib.misp_api_helpers import get_api_key, misp_add_event
from datetime import datetime, timedelta
import random

def generate_test_events(count=10):
    """Generate test events with various attributes."""
    api_key = get_api_key()

    threat_levels = [1, 2, 3, 4]  # High, Medium, Low, Undefined
    categories = ['ics:malware', 'ics:attack-target="plc"', 'tlp:white']

    for i in range(count):
        # Random date in last 30 days
        days_ago = random.randint(1, 30)
        event_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        event_data = {
            'Event': {
                'info': f'Test Event {i+1} - {random.choice(["Malware", "Phishing", "ICS Attack"])}',
                'date': event_date,
                'threat_level_id': random.choice(threat_levels),
                'analysis': random.randint(0, 2),
                'distribution': 0,  # Your org only
                'published': True if random.random() > 0.3 else False
            }
        }

        result = misp_add_event(api_key, event_data)
        if result.get('success'):
            event_id = result['event']['Event']['id']
            print(f"Created event {event_id}: {event_data['Event']['info']}")

            # Add tags
            for tag in random.sample(categories, random.randint(1, 2)):
                # Add tag via API
                pass  # Implementation

if __name__ == "__main__":
    generate_test_events(20)
```

---

### Generate Test Attributes

**Common Attribute Types**:
- IP addresses: `ip-src`, `ip-dst`
- Domains: `domain`, `hostname`
- Files: `filename`, `md5`, `sha256`
- URLs: `url`, `link`

```python
def add_test_attributes(event_id, api_key):
    """Add various attribute types to event."""
    attributes = [
        {'type': 'ip-src', 'value': '192.168.1.100', 'category': 'Network activity'},
        {'type': 'domain', 'value': 'malicious.example.com', 'category': 'Network activity'},
        {'type': 'md5', 'value': 'd41d8cd98f00b204e9800998ecf8427e', 'category': 'Payload delivery'},
        {'type': 'filename', 'value': 'malware.exe', 'category': 'Payload delivery'}
    ]

    for attr in attributes:
        misp_add_attribute(api_key, event_id, attr)
```

---

### Generate Bulk Test Data

**For Performance Testing**:
```bash
# Generate 1000 events
python3 scripts/generate-test-events.py --count 1000

# Generate events with attributes
python3 scripts/generate-test-events.py --count 100 --attributes 10

# Generate specific event type
python3 scripts/generate-test-events.py --type ics-malware --count 50
```

---

## CI/CD Testing

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`
```yaml
name: Test

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install ruff pytest
      - name: Lint with ruff
        run: ruff check .
      - name: Run unit tests
        run: pytest tests/unit/

  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install Docker
        run: |
          curl -fsSL https://get.docker.com | sh
      - name: Run integration tests
        run: pytest tests/integration/
```

---

## Performance Testing

### Installation Time

**Baseline Measurements**:
```bash
# Full installation
time sudo python3 misp-install.py

# Minimal installation
time sudo python3 misp-install.py --config config/test-minimal.conf

# Individual phase
time sudo python3 phases/phase_11_8_utilities_intel.py
```

**Performance Targets**:
- Full installation: < 45 minutes
- Minimal installation: < 10 minutes
- Individual phase: < 5 minutes (most phases)

---

### API Performance

**Test API Response Times**:
```bash
#!/bin/bash
# Test API performance

API_KEY=$(cat ~/.misp/apikey)

# Test event search
time curl -k -H "Authorization: $API_KEY" \
     -X POST "https://localhost/events/restSearch" \
     -d '{"limit":100}' -o /dev/null -s

# Test feed fetch
time curl -k -H "Authorization: $API_KEY" \
     "https://localhost/feeds/index.json" -o /dev/null -s
```

---

## Security Testing

### Basic Security Checks

**1. Check for Hardcoded Credentials**:
```bash
# Search for potential secrets
grep -r -E "(password|api_key|secret|token).*=.*['\"]" --include="*.py" | grep -v "# "

# Should not find any hardcoded values
```

**2. Check File Permissions**:
```bash
# API key should not be world-readable
ls -la ~/.misp/apikey
# Should be: -rw------- (600)

# Config files should be protected
ls -la config/*.conf
```

**3. Check for SQL Injection**:
- Review database queries
- Ensure parameterized queries used
- No string concatenation for SQL

**4. Check for Command Injection**:
```python
# BAD - command injection risk
os.system(f"docker exec {container} {user_input}")

# GOOD - safe approach
subprocess.run(['docker', 'exec', container, user_input])
```

---

## Test Checklists

### Pre-Release Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Fresh installation test succeeds
- [ ] Minimal installation test succeeds
- [ ] Feature exclusion tests pass
- [ ] Resume-after-failure test succeeds
- [ ] Widget installation test succeeds
- [ ] API functionality test succeeds
- [ ] No errors in logs
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped

---

### Pull Request Checklist

- [ ] Code follows project patterns
- [ ] Unit tests added (if applicable)
- [ ] Manual testing completed
- [ ] No regressions introduced
- [ ] Logs show no new errors
- [ ] Documentation updated
- [ ] Commit messages clear
- [ ] Branch up to date with main

---

### Quick Smoke Test

**5-Minute Verification** (after small changes):
```bash
# 1. Lint
ruff check your_changed_file.py

# 2. Unit test
pytest tests/test_your_module.py

# 3. Quick install test
sudo python3 phases/your_changed_phase.py

# 4. Check logs
tail -20 logs/misp_installer.log | jq 'select(.level=="ERROR")'

# 5. Verify MISP still works
curl -k https://localhost
```

---

**Maintained by**: tKQB Enterprises
**Version**: 1.0
**Last Updated**: 2025-10-25
