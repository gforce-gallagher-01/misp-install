# MISP Centralized Logging System

## Overview

All MISP management scripts now use **centralized JSON logging** with CIM-compatible field names, making logs ready for enterprise SIEM integration (Splunk, ELK, etc.).

## Log Location

```bash
/opt/misp/logs/
```

All logs are now centralized in this single directory with automatic rotation.

**⚠️ Important:** This directory must be created before running any scripts. Run this command once:

```bash
sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp && sudo chmod 777 /opt/misp/logs
```

If the directory doesn't exist or isn't writable, scripts will gracefully fall back to console-only logging.

## Log Format

JSON format with consistent field names:

```json
{
  "time": "2025-10-12T18:33:10.453675Z",
  "host": "misp-dev",
  "user": "user",
  "source": "backup-misp",
  "sourcetype": "misp:backup",
  "severity": "INFO",
  "message": "Backup process completed!",
  "event_type": "backup",
  "action": "complete",
  "status": "success",
  "duration": 55.24
}
```

## CIM Field Reference

### Core Fields
- **time** - ISO 8601 timestamp (UTC with Z)
- **host** - System hostname
- **user** - User running the script
- **source** - Script name (e.g., "backup-misp")
- **sourcetype** - MISP component type (e.g., "misp:backup")

### Classification
- **severity** - INFO, WARNING, ERROR, DEBUG
- **event_type** - Primary event category (backup, install, configure, uninstall, restore, update)
- **action** - Specific action (start, complete, verify, etc.)
- **status** - Outcome (info, success, warning, error)

### Context
- **component** - Sub-component being acted upon
- **phase** - Current phase in multi-step operations
- **container** - Docker container name
- **file_path** - File being operated on
- **backup_name** - Backup identifier

### Metrics
- **duration** - Execution time in seconds
- **bytes** - Size in bytes
- **count** - Item count
- **error_message** - Detailed error information

## Log Rotation

- **Files per log**: 5 rotating files
- **Size limit**: 20MB per file
- **Total retention**: ~100MB per script
- **Automatic cleanup**: Oldest logs deleted when limit reached

Example:
```
backup-misp.log         (current)
backup-misp.log.1       (previous)
backup-misp.log.2
backup-misp.log.3
backup-misp.log.4       (oldest)
```

## Viewing Logs

### View All Logs
```bash
ls -lth /opt/misp/logs/
```

### View JSON Formatted
```bash
tail -f /opt/misp/logs/misp-install.log | jq '.'
```

### Filter by Severity
```bash
cat /opt/misp/logs/*.log | jq 'select(.severity=="ERROR")'
```

### Show Only Messages
```bash
cat /opt/misp/logs/backup-misp.log | jq -r '.message'
```

### Analyze Durations
```bash
cat /opt/misp/logs/*.log | jq 'select(.duration) | {action, duration}'
```

### Count Events by Type
```bash
cat /opt/misp/logs/*.log | jq -r '.event_type' | sort | uniq -c
```

## SIEM Integration

### Splunk Query Examples

```spl
# All MISP events
index=misp sourcetype="misp:*" 

# Count by event type
index=misp sourcetype="misp:*" 
| stats count by event_type, action, status

# Show errors
index=misp sourcetype="misp:*" severity=ERROR
| table time, source, message, error_message

# Performance metrics
index=misp sourcetype="misp:*" duration>0
| stats avg(duration) p95(duration) by action
```

### ELK/Elasticsearch Query

```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"sourcetype": "misp:backup"}},
        {"range": {"duration": {"gte": 30}}}
      ]
    }
  }
}
```

## All Scripts Updated (8/8)

All MISP management scripts now use centralized JSON logging:

1. ✅ **misp_logger.py** - Core logging module
2. ✅ **misp-install.py** (v5.2) - Installation
3. ✅ **backup-misp.py** (v3.0) - Manual backups
4. ✅ **configure-misp-ready.py** (v2.0) - Configuration
5. ✅ **uninstall-misp.py** (v3.0) - Uninstallation
6. ✅ **misp-restore.py** (v2.0) - Restore from backup
7. ✅ **misp-update.py** (v2.0) - Updates & upgrades
8. ✅ **misp-backup-cron.py** (v2.0) - Scheduled backups

**All scripts are production-ready and SIEM-compatible!**

## Troubleshooting

### Check for Errors
```bash
grep ERROR /opt/misp/logs/*.log
# Or with jq:
cat /opt/misp/logs/*.log | jq 'select(.severity=="ERROR")'
```

### Monitor Live
```bash
tail -f /opt/misp/logs/misp-install.log | jq '.'
```

### Check Disk Usage
```bash
du -sh /opt/misp/logs/
```

### Verify Log Rotation
```bash
ls -lh /opt/misp/logs/backup-misp.log*
```

## Benefits

### For Operations
- **SIEM-Ready**: Direct integration with Splunk, ELK, etc.
- **Structured Data**: Easy filtering and analysis
- **Centralized**: Single location for all logs
- **Automatic Rotation**: Prevents disk space issues

### For Development
- **Consistent Format**: Same fields across all scripts
- **Rich Context**: Every log entry has full context
- **Easy Debugging**: Structured data simplifies troubleshooting
- **Maintainable**: Centralized logging module

### For Security
- **Audit Trail**: Complete record of all operations
- **Correlation**: Easy to correlate events across scripts
- **Alerting**: SIEM can alert on specific patterns
- **Compliance**: Professional logging for audits

## Technical Details

### Logger Implementation
- Python `logging` module with `RotatingFileHandler`
- Thread-safe logging
- Both JSON file output and colored console output
- Automatic field enrichment (host, user, time, etc.)

### Configuration
```python
# Log location
LOG_DIR = Path("/opt/misp/logs")

# Rotation settings
MAX_BYTES = 20 * 1024 * 1024  # 20MB
BACKUP_COUNT = 5  # 5 rotated files
```

## Migration from Old Logs

Old logs may still exist in:
- `/var/log/misp-install/`
- `/tmp/`
- Other scattered locations

These can be safely removed once you verify the new centralized logs are working.

---

**Created by tKQB Enterprises MISP Installation Suite**
