# Design Patterns Catalog

**Purpose**: Document recurring design patterns used in this codebase with examples, pros/cons, and usage guidelines
**Last Updated**: 2025-10-25
**Version**: 1.0

This document catalogs proven design patterns used throughout the MISP installation suite. Use these patterns for consistency and to avoid common pitfalls.

---

## Table of Contents

1. [Phase Pattern](#phase-pattern)
2. [State Manager Pattern](#state-manager-pattern)
3. [Feature Exclusion Pattern](#feature-exclusion-pattern)
4. [Centralized Helper Pattern](#centralized-helper-pattern)
5. [MISP API Wrapper Pattern](#misp-api-wrapper-pattern)
6. [Widget Base Class Pattern](#widget-base-class-pattern)
7. [Configuration Singleton Pattern](#configuration-singleton-pattern)
8. [Structured Logging Pattern](#structured-logging-pattern)
9. [Docker Abstraction Pattern](#docker-abstraction-pattern)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Phase Pattern

### Purpose
Break complex installation into sequential, resumable phases with state management.

### When to Use
- Multi-step installation or configuration processes
- Need for resume-after-failure capability
- Clear separation of concerns
- Independent testability

### Structure

```python
from phases.base_phase import BasePhase
from lib.misp_logger import get_logger

class Phase_X_Y_Description(BasePhase):
    """
    Brief description of what this phase does.

    CIP Requirements: CIP-XXX RY (if applicable)
    Dependencies: Phase X.Y-1 must complete first
    """

    def __init__(self):
        super().__init__(
            phase_number="X.Y",
            phase_name="Human-Readable Description",
            state_file="phase_X_Y_description.json"
        )
        self.logger = get_logger('phase_X_Y', 'misp:phase')

    def check_requirements(self) -> bool:
        """
        Pre-flight checks before running phase.
        Returns True if ready, False if not.
        """
        # Check Docker running
        if not self.docker.is_running():
            self.logger.error("Docker not running")
            return False

        # Check previous phase completed
        prev_state = self.state.load('phase_X_Y-1.json')
        if not prev_state or prev_state.get('status') != 'completed':
            self.logger.error("Previous phase not completed")
            return False

        return True

    def run(self):
        """
        Main phase execution logic.
        """
        self.logger.info(f"Starting {self.phase_name}")

        # Feature exclusion check (if optional)
        if self.config.is_feature_excluded('feature-id'):
            self.logger.info("Feature excluded, skipping phase")
            self.state.save({
                'status': 'skipped',
                'reason': 'Feature excluded by configuration'
            })
            return

        try:
            # Step 1: Do something
            self.logger.info("Step 1: Description")
            result1 = self._step_1()

            # Save progress after each major step
            self.state.save({
                'status': 'in_progress',
                'completed_steps': ['step_1'],
                'step_1_result': result1
            })

            # Step 2: Do something else
            self.logger.info("Step 2: Description")
            result2 = self._step_2()

            # Save final state
            self.state.save({
                'status': 'completed',
                'completed_steps': ['step_1', 'step_2'],
                'results': {'step_1': result1, 'step_2': result2}
            })

            self.logger.info(f"Phase {self.phase_number} completed successfully")

        except Exception as e:
            self.logger.error(f"Phase failed: {str(e)}")
            self.state.save({
                'status': 'failed',
                'error': str(e)
            })
            raise

    def _step_1(self):
        """Helper method for step 1."""
        pass

    def _step_2(self):
        """Helper method for step 2."""
        pass

# Usage
if __name__ == "__main__":
    phase = Phase_X_Y_Description()
    if phase.check_requirements():
        phase.run()
    else:
        print("Requirements not met")
        exit(1)
```

### Pros
✅ Clear separation of concerns (one phase = one responsibility)
✅ Resumable after failure (state management)
✅ Testable in isolation
✅ Easy to add new phases
✅ Self-documenting code structure

### Cons
❌ Overhead for simple operations
❌ Sequential execution (can't parallelize easily)
❌ State file management complexity

### Real Examples
- `phases/phase_11_8_utilities_intel.py` - Threat intelligence setup
- `phases/phase_11_11_utilities_dashboards.py` - Dashboard installation

---

## State Manager Pattern

### Purpose
Persist installation state to enable resume-after-failure and progress tracking.

### When to Use
- Long-running operations that might fail
- Need to track progress across sessions
- Resume capability required
- Audit trail of actions

### Structure

```python
from lib.state_manager import StateManager
from datetime import datetime

class MyOperation:
    def __init__(self):
        self.state = StateManager('my_operation.json')

    def run(self):
        # Load previous state (if exists)
        prev_state = self.state.load()

        if prev_state:
            print(f"Resuming from: {prev_state.get('last_step')}")
            completed = prev_state.get('completed_steps', [])
        else:
            completed = []

        # Step 1
        if 'step1' not in completed:
            self.do_step1()
            completed.append('step1')
            self.state.save({
                'completed_steps': completed,
                'last_step': 'step1',
                'timestamp': datetime.now().isoformat()
            })

        # Step 2
        if 'step2' not in completed:
            self.do_step2()
            completed.append('step2')
            self.state.save({
                'completed_steps': completed,
                'last_step': 'step2',
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            })
```

### State File Structure

```json
{
    "status": "completed|in_progress|failed|skipped",
    "completed_steps": ["step1", "step2"],
    "last_step": "step2",
    "timestamp": "2025-10-25T12:34:56",
    "results": {
        "step1": "result_data",
        "step2": "result_data"
    },
    "error": "error message if failed"
}
```

### Pros
✅ Atomic state updates (write to temp file, then rename)
✅ Resume capability after crash/failure
✅ Progress tracking for long operations
✅ Audit trail

### Cons
❌ File I/O overhead
❌ JSON serialization limitations (no complex objects)
❌ Manual cleanup of old state files

### Real Examples
- All phase classes use StateManager
- `lib/state_manager.py` - Implementation

---

## Feature Exclusion Pattern

### Purpose
Allow users to selectively exclude features they don't need, reducing installation time and attack surface.

### When to Use
- Optional features
- Industry-specific functionality
- Advanced features not needed by all users
- Experimental features

### Structure

```python
from lib.config import Config

class OptionalFeature:
    def __init__(self):
        self.config = Config()

    def run(self):
        # Check if entire category excluded
        if self.config.is_feature_excluded('category:threat_intel'):
            print("Threat intelligence category excluded")
            return

        # Check specific feature
        if self.config.is_feature_excluded('azure-ad'):
            print("Azure AD integration excluded")
            # Use fallback or skip
            self.use_local_auth()
            return

        # Feature not excluded, proceed
        self.configure_azure_ad()
```

### Configuration File

```ini
# config/exclusions.conf
[exclusions]
# Exclude entire categories
category:threat_intel    # All threat intelligence features
category:compliance      # All compliance features

# Exclude specific features
azure-ad                 # Azure AD integration
nerc-cip-dashboards     # NERC CIP dashboards
automated-maintenance    # Automated maintenance cron jobs

# Features are defined in lib/features.py
```

### Feature Definition

```python
# lib/features.py
FEATURE_DESCRIPTIONS = {
    'azure-ad': 'Azure Active Directory SSO integration',
    'nerc-cip-dashboards': 'NERC CIP compliance dashboards',
    'automated-maintenance': 'Daily/weekly automated maintenance tasks'
}

FEATURE_CATEGORIES = {
    'azure-ad': 'category:integrations',
    'nerc-cip-dashboards': 'category:compliance',
    'automated-maintenance': 'category:automation'
}
```

### Pros
✅ User control over installation
✅ Reduced installation time
✅ Minimized attack surface
✅ Industry-specific customization
✅ Easy to extend with new features

### Cons
❌ Need to handle missing dependencies
❌ Testing complexity (many combinations)
❌ Documentation overhead (what's excluded?)

### Real Examples
- All Phase 11.X features support exclusion
- `config/examples/minimal-install.conf` - Example configuration
- `docs/development/EXCLUSION_LIST_DESIGN.md` - Complete design

---

## Centralized Helper Pattern

### Purpose
Eliminate code duplication by centralizing common operations in `lib/` modules.

### When to Use
- Operation used in 3+ places
- Complex logic that should be tested once
- Common error handling patterns
- API interactions

### Structure

```python
# lib/my_helpers.py
"""
Centralized helper functions for common operations.
"""
from lib.misp_logger import get_logger

logger = get_logger('my_helpers', 'misp:lib')

def common_operation(param1: str, param2: int) -> dict:
    """
    Perform a common operation used across multiple scripts.

    Args:
        param1: Description
        param2: Description

    Returns:
        Result dictionary

    Raises:
        ValueError: If params invalid
        RuntimeError: If operation fails
    """
    # Validation
    if not param1:
        raise ValueError("param1 cannot be empty")

    # Operation with error handling
    try:
        result = do_something(param1, param2)
        logger.info(f"Operation completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        raise RuntimeError(f"Failed to perform operation: {str(e)}")

# Usage in scripts/phases
from lib.my_helpers import common_operation

result = common_operation("value", 42)
```

### Before (Duplicated Code)

```python
# script1.py
try:
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    return response.json()
except Exception as e:
    logger.error(f"Failed: {str(e)}")
    raise

# script2.py
try:
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    return response.json()
except Exception as e:
    logger.error(f"Failed: {str(e)}")
    raise

# ... repeated 10+ times
```

### After (Centralized)

```python
# lib/api_helpers.py
def api_post(url: str, data: dict) -> dict:
    """Centralized API POST with error handling."""
    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise Exception(f"API error: {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"API POST failed: {str(e)}")
        raise

# Usage everywhere
from lib.api_helpers import api_post
result = api_post(url, data)
```

### Pros
✅ DRY (Don't Repeat Yourself)
✅ Single place to fix bugs
✅ Consistent error handling
✅ Testable in isolation
✅ Self-documenting through docstrings

### Cons
❌ Can become a "junk drawer" if not organized
❌ Need to keep backwards compatible
❌ Import overhead (minimal)

### Real Examples
- `lib/misp_api_helpers.py` - 20+ MISP API operations
- `lib/docker_helpers.py` - Docker container management
- `lib/misp_config.py` - MISP configuration operations

---

## MISP API Wrapper Pattern

### Purpose
Provide consistent, error-handled access to MISP REST API.

### When to Use
- All MISP API interactions
- Need consistent error handling
- API authentication required
- JSON parsing required

### Structure

```python
from lib.misp_api_helpers import (
    get_api_key,
    get_misp_url,
    misp_rest_search,
    misp_add_event,
    misp_get_event
)
import requests

# Get credentials (from ~/.misp/ files)
api_key = get_api_key()
misp_url = get_misp_url()

# Search events with filters
events = misp_rest_search(
    api_key=api_key,
    filters={
        "tags": ["ics:%"],           # Wildcard tag search
        "published": 1,               # Published only
        "last": "7d",                 # Last 7 days
        "include_event_tags": True    # Include tag details
    }
)

for event in events:
    print(f"Event: {event['Event']['info']}")

# Add new event
event_data = {
    "Event": {
        "info": "Suspicious Activity Detected",
        "threat_level_id": 2,  # Medium
        "analysis": 1,          # Ongoing
        "distribution": 0,      # Your org only
        "published": False
    }
}

result = misp_add_event(api_key, event_data)
if result.get('success'):
    event_id = result['event']['Event']['id']
    print(f"Created event: {event_id}")
```

### Error Handling Pattern

```python
def misp_rest_search(api_key: str, filters: dict) -> list:
    """
    Search MISP events with error handling.

    Returns:
        List of events, or empty list on error
    """
    try:
        response = requests.post(
            f"{get_misp_url()}/events/restSearch",
            headers={
                'Authorization': api_key,
                'Accept': 'application/json'
            },
            json=filters,
            verify=False  # Self-signed cert
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('response', [])
        else:
            logger.error(f"MISP API error: {response.status_code} - {response.text}")
            return []

    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to MISP (is it running?)")
        return []
    except Exception as e:
        logger.error(f"MISP API exception: {str(e)}")
        return []
```

### Pros
✅ Consistent API access across all scripts
✅ Centralized authentication
✅ Proper error handling
✅ JSON parsing handled
✅ SSL verification handling

### Cons
❌ Wrapper overhead (minimal)
❌ May not expose all API features
❌ Need to update when MISP API changes

### Real Examples
- `lib/misp_api_helpers.py` - Complete implementation
- Used by all scripts that interact with MISP

---

## Widget Base Class Pattern

### Purpose
Share common widget functionality while avoiding MISP's abstract class instantiation bug.

### When to Use
- Creating multiple related widgets
- Common permission checking
- Shared data formatting
- Consistent error handling

### Structure (WRONG - Causes Bug)

```php
// ❌ DO NOT DO THIS - MISP will try to instantiate BaseWidget
abstract class BaseWidget
{
    protected function checkPermissions($user) {
        // Common permission logic
    }
}

class MyWidget extends BaseWidget {
    // ...
}
```

### Structure (CORRECT - Use Trait)

```php
// ✅ Use PHP trait instead of abstract class
trait WidgetHelpers
{
    protected function checkPermissions($user)
    {
        if (!isset($user['Role']['perm_site_admin'])) {
            return false;
        }

        return ($user['Role']['perm_site_admin'] ||
                $user['Role']['perm_audit']);
    }

    protected function formatTags($event)
    {
        $tags = array();

        // Handle both Tag and EventTag structures
        if (!empty($event['Tag'])) {
            $tags = $event['Tag'];
        } elseif (!empty($event['EventTag'])) {
            foreach ($event['EventTag'] as $eventTag) {
                $tags[] = $eventTag['Tag'];
            }
        }

        return $tags;
    }
}

// Widget implementation
class MyWidget
{
    use WidgetHelpers;  // Include trait

    public $title = 'My Widget';
    public $render = 'SimpleList';
    public $width = 3;
    public $height = 4;

    public function handler($user, $options = array())
    {
        // Use trait method
        if (!$this->checkPermissions($user)) {
            return array();
        }

        // Widget logic
        $Event = ClassRegistry::init('Event');
        $events = $Event->find('all', array(
            'conditions' => array('Event.published' => 1)
        ));

        // Use trait method
        foreach ($events as &$event) {
            $event['tags'] = $this->formatTags($event);
        }

        return $events;
    }
}
```

### Critical MISP Widget Patterns

```php
// 1. Tag search - USE WILDCARD
$eventIds = $Event->fetchEventIds($user, array(
    'tags' => array('ics:%'),  // ✅ Matches ics:malware, ics:attack, etc.
    // NOT 'ics:'               // ❌ Only matches literal tag "ics:"
));

// 2. Handle both Tag structures
$tags = array();
if (!empty($event['Tag'])) {
    // restSearch returns this
    $tags = $event['Tag'];
} elseif (!empty($event['EventTag'])) {
    // events/view returns this
    foreach ($event['EventTag'] as $et) {
        $tags[] = $et['Tag'];
    }
}

// 3. Check permissions properly
if (!isset($user['Role']['perm_site_admin'])) {
    return array();
}
if (!$user['Role']['perm_site_admin'] && !$user['Role']['perm_audit']) {
    return array();
}

// 4. Time filters use event date field
$eventIds = $Event->fetchEventIds($user, array(
    'last' => '7d',  // Checks Event.date field (not publish timestamp)
));
```

### Pros
✅ Code reuse across widgets
✅ No abstract class instantiation bug
✅ Consistent patterns
✅ Easy to test shared logic

### Cons
❌ Trait doesn't enforce interface
❌ MISP-specific quirks to remember
❌ Limited inheritance options

### Real Examples
- `widgets/utilities-sector/` - 25 widgets using shared patterns
- `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md` - Complete gotchas list

---

## Configuration Singleton Pattern

### Purpose
Single global configuration instance accessed throughout application.

### When to Use
- Application-wide configuration
- Need consistent config access
- Avoid passing config everywhere
- Lazy loading of config files

### Structure

```python
# lib/config.py
class Config:
    """Singleton configuration manager."""

    _instance = None
    _config_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config_loaded:
            self._load_config()
            Config._config_loaded = True

    def _load_config(self):
        """Load configuration from files."""
        # Load exclusions.conf
        # Load misp-config.yaml
        # Parse and store
        pass

    def is_feature_excluded(self, feature_id: str) -> bool:
        """Check if feature is excluded."""
        return feature_id in self._excluded_features

# Usage (same instance everywhere)
from lib.config import Config

config1 = Config()
config2 = Config()
assert config1 is config2  # Same instance
```

### Pros
✅ Single source of truth
✅ Lazy loading
✅ No need to pass config around
✅ Easy to test (reset singleton between tests)

### Cons
❌ Global state (testing complexity)
❌ Hidden dependencies
❌ Harder to mock in tests

### Real Examples
- `lib/config.py` - Configuration singleton
- `lib/features.py` - Feature definitions

---

## Structured Logging Pattern

### Purpose
Consistent, parseable logging across all components.

### When to Use
- All scripts and phases
- Any operation that needs debugging
- Audit trails
- Performance monitoring

### Structure

```python
from lib.misp_logger import get_logger

class MyComponent:
    def __init__(self):
        # Sourcetype format: misp:category
        self.logger = get_logger('my_component', 'misp:automation')

    def do_work(self, item_id: int):
        # Info: Normal operations
        self.logger.info(f"Processing item {item_id}")

        try:
            result = self.process(item_id)

            # Success with details
            self.logger.info(
                f"Item {item_id} processed successfully",
                extra={'item_id': item_id, 'result': result}
            )

        except ValueError as e:
            # Warning: Recoverable errors
            self.logger.warning(
                f"Item {item_id} validation failed: {str(e)}",
                extra={'item_id': item_id}
            )

        except Exception as e:
            # Error: Serious problems
            self.logger.error(
                f"Failed to process item {item_id}: {str(e)}",
                extra={'item_id': item_id},
                exc_info=True  # Include stack trace
            )
```

### Log Format (JSON)

```json
{
    "timestamp": "2025-10-25T12:34:56.789Z",
    "level": "INFO",
    "logger": "my_component",
    "sourcetype": "misp:automation",
    "message": "Processing item 42",
    "item_id": 42
}
```

### Pros
✅ Structured (parseable by SIEM)
✅ Consistent format across all components
✅ Automatic rotation (5 files × 20MB)
✅ Sourcetype for categorization
✅ Extra fields for rich data

### Cons
❌ JSON overhead (slightly larger files)
❌ Less human-readable than plain text

### Real Examples
- `lib/misp_logger.py` - Logger implementation
- `docs/README_LOGGING.md` - Complete documentation
- All phases and scripts use this pattern

---

## Docker Abstraction Pattern

### Purpose
Abstract Docker operations to avoid repeating `docker exec` commands.

### When to Use
- Any Docker container interaction
- File operations in containers
- Command execution in containers
- Container status checks

### Structure

```python
from lib.docker_helpers import (
    docker_exec,
    docker_file_exists,
    docker_copy_to_container,
    docker_copy_from_container,
    is_container_running
)

# Check container running
if not is_container_running('misp-misp-core-1'):
    print("MISP container not running")
    exit(1)

# Execute command in container
result = docker_exec(
    container='misp-misp-core-1',
    command=['ls', '-la', '/var/www/MISP'],
    capture_output=True
)

if result['returncode'] == 0:
    print(result['stdout'])

# Check if file exists
if docker_file_exists('misp-misp-core-1', '/var/www/MISP/app/Config/config.php'):
    print("Config file exists")

# Copy file to container
docker_copy_to_container(
    container='misp-misp-core-1',
    source_path='/tmp/my-file.txt',
    dest_path='/var/www/MISP/app/tmp/my-file.txt'
)

# Copy file from container
docker_copy_from_container(
    container='misp-misp-core-1',
    source_path='/var/www/MISP/app/tmp/result.txt',
    dest_path='/tmp/result.txt'
)
```

### Pros
✅ No need to remember docker command syntax
✅ Consistent error handling
✅ Easier to test (can mock docker operations)
✅ Cleaner code

### Cons
❌ Another abstraction layer
❌ May not expose all Docker features

### Real Examples
- `lib/docker_helpers.py` - Complete implementation
- Used throughout phases and scripts

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Direct Docker Commands

**❌ Bad:**
```python
import subprocess

result = subprocess.run([
    'sudo', 'docker', 'exec', 'misp-misp-core-1',
    'ls', '-la', '/var/www/MISP'
], capture_output=True)

if result.returncode == 0:
    print(result.stdout.decode())
```

**✅ Good:**
```python
from lib.docker_helpers import docker_exec

result = docker_exec('misp-misp-core-1', ['ls', '-la', '/var/www/MISP'])
if result['returncode'] == 0:
    print(result['stdout'])
```

**Why**: Centralized error handling, consistent interface, easier to test.

---

### Anti-Pattern 2: Repeated MISP API Code

**❌ Bad:**
```python
# In 10 different scripts...
import requests

response = requests.post(
    'https://localhost/events/restSearch',
    headers={'Authorization': api_key},
    json={'tags': ['ics:']},
    verify=False
)
events = response.json().get('response', [])
```

**✅ Good:**
```python
from lib.misp_api_helpers import misp_rest_search, get_api_key

events = misp_rest_search(
    api_key=get_api_key(),
    filters={'tags': ['ics:%']}  # Note: wildcard
)
```

**Why**: DRY, consistent error handling, fixed bugs propagate everywhere.

---

### Anti-Pattern 3: Abstract Widget Base Classes

**❌ Bad:**
```php
// MISP will try to instantiate this and fail
abstract class BaseWidget {
    abstract public function handler($user, $options);
}

class MyWidget extends BaseWidget {
    public function handler($user, $options) { ... }
}
```

**✅ Good:**
```php
// Use trait instead
trait WidgetHelpers {
    protected function checkPermissions($user) { ... }
}

class MyWidget {
    use WidgetHelpers;
    public function handler($user, $options) { ... }
}
```

**Why**: MISP's dashboard loader scans and instantiates all .php files, breaking on abstract classes.

---

### Anti-Pattern 4: Hardcoded Paths

**❌ Bad:**
```python
config_file = '/home/misp-admin/.misp/apikey'
log_file = '/home/misp-admin/misp-install/logs/installer.log'
```

**✅ Good:**
```python
from pathlib import Path
import os

# Use environment variables or config
home_dir = Path.home()
config_file = home_dir / '.misp' / 'apikey'

# Or use config helper
from lib.config import Config
log_file = Config().get_log_path()
```

**Why**: Portability, easier testing, centralized configuration.

---

### Anti-Pattern 5: No Error Handling

**❌ Bad:**
```python
def process_event(event_id):
    event = get_event(event_id)
    result = analyze(event)
    save_result(result)
    return result
```

**✅ Good:**
```python
def process_event(event_id: int) -> dict:
    """Process event with comprehensive error handling."""
    try:
        event = get_event(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            return {'error': 'Event not found'}

        result = analyze(event)
        save_result(result)

        logger.info(f"Event {event_id} processed successfully")
        return result

    except ValueError as e:
        logger.error(f"Invalid event data: {str(e)}")
        return {'error': f'Invalid data: {str(e)}'}

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise
```

**Why**: Graceful failure, debugging information, user-friendly errors.

---

### Anti-Pattern 6: Magic Numbers/Strings

**❌ Bad:**
```python
if threat_level == 1:  # What does 1 mean?
    priority = "high"

if event['analysis'] == 2:  # What does 2 mean?
    status = "ongoing"
```

**✅ Good:**
```python
# Constants module
THREAT_LEVELS = {
    'HIGH': 1,
    'MEDIUM': 2,
    'LOW': 3,
    'UNDEFINED': 4
}

ANALYSIS_STATUS = {
    'INITIAL': 0,
    'ONGOING': 1,
    'COMPLETE': 2
}

# Usage
if threat_level == THREAT_LEVELS['HIGH']:
    priority = "high"

if event['analysis'] == ANALYSIS_STATUS['ONGOING']:
    status = "ongoing"
```

**Why**: Self-documenting code, easier to maintain, type safety.

---

## Pattern Selection Guide

| Need | Pattern | File |
|------|---------|------|
| Multi-step installation | Phase Pattern | `phases/base_phase.py` |
| Resume after failure | State Manager | `lib/state_manager.py` |
| Optional features | Feature Exclusion | `lib/config.py` |
| MISP API access | MISP API Wrapper | `lib/misp_api_helpers.py` |
| Docker operations | Docker Abstraction | `lib/docker_helpers.py` |
| Custom dashboards | Widget (with Trait) | `widgets/*/` |
| Logging | Structured Logging | `lib/misp_logger.py` |
| Global config | Config Singleton | `lib/config.py` |
| Code reuse | Centralized Helper | `lib/*_helpers.py` |

---

**Maintained by**: tKQB Enterprises
**Version**: 1.0
**Last Updated**: 2025-10-25
