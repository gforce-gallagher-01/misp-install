# Automatic Hostname Detection

## Overview

The MISP installer now automatically detects the system's hostname/FQDN and uses it as the default domain for the installation. This eliminates the need to manually specify the hostname in most cases.

## How It Works

The installer uses a multi-tier approach to detect the hostname:

1. **Primary**: `hostname -f` command (most reliable on Linux, returns FQDN)
2. **Secondary**: `socket.getfqdn()` (Python's socket library)
3. **Tertiary**: `socket.gethostname()` (basic hostname)
4. **Fallback**: `misp.local` (if all detection methods fail)

## Usage

### Interactive Installation

When running `python3 misp-install.py`, the installer will:

1. Detect your system hostname automatically
2. Display it with: `🔍 Detected system hostname: misp-test.lan`
3. Offer it as the default when prompting: `Enter FQDN for MISP [misp-test.lan]:`
4. You can press Enter to accept or type a different FQDN

**Example**:
```
📋 CONFIGURATION
==================================================

Please provide installation details:

🔍 Detected system hostname: misp-test.lan

Enter server IP address [192.168.20.193]: 192.168.20.54
Enter FQDN for MISP [misp-test.lan]: ← Press Enter to use detected hostname
```

### Configuration File Installation

If you don't specify a `domain` in your config file, it will be auto-detected:

**config.json** (domain will be auto-detected):
```json
{
  "server_ip": "192.168.20.54",
  "domain": "",
  "admin_email": "admin@company.com",
  ...
}
```

**config.json** (explicit domain overrides auto-detection):
```json
{
  "server_ip": "192.168.20.54",
  "domain": "misp-custom.lan",
  "admin_email": "admin@company.com",
  ...
}
```

### Non-Interactive Installation

```bash
# Auto-detect hostname
python3 misp-install.py --config config.json --non-interactive

# Or specify explicitly in config file
python3 misp-install.py --config config-with-domain.json --non-interactive
```

## Detection Methods

### Method 1: hostname -f (Primary)

Runs the `hostname -f` command which returns the fully qualified domain name.

**Example output**: `misp-test.lan`

**Validation**: Must contain a dot (.) to be considered a valid FQDN

### Method 2: socket.getfqdn() (Secondary)

Uses Python's socket library to get the FQDN.

**Validation**:
- Must not be 'localhost'
- Must contain a dot (.)

### Method 3: socket.gethostname() (Tertiary)

Gets the basic hostname without domain.

**Example output**: `misp-test`

**Validation**: Must not be 'localhost'

### Method 4: Fallback (Last Resort)

If all methods fail or return invalid results, defaults to `misp.local`.

## Code Location

- **Function**: `get_system_hostname()` in `lib/config.py`
- **Usage in installer**: `misp-install.py` line 237
- **Usage in config**: `MISPConfig.__post_init__()` in `lib/config.py` line 116

## Benefits

1. **Convenience**: No need to manually type the hostname
2. **Accuracy**: Uses the actual system hostname, reducing typos
3. **Consistency**: MISP URL matches the system's network identity
4. **Flexibility**: Can still override if needed

## Troubleshooting

### Hostname Detection Returns Wrong Value

If the auto-detection returns an incorrect hostname:

1. **Check system hostname**:
   ```bash
   hostname -f
   ```

2. **Set the correct hostname** (if needed):
   ```bash
   sudo hostnamectl set-hostname misp-prod.yourdomain.com
   ```

3. **Override in config file**:
   ```json
   {
     "domain": "misp-prod.yourdomain.com",
     ...
   }
   ```

### Hostname Detection Returns 'localhost'

This means your system doesn't have a proper FQDN configured. Options:

1. **Set a proper hostname**:
   ```bash
   sudo hostnamectl set-hostname misp.yourdomain.local
   ```

2. **Update /etc/hosts**:
   ```bash
   echo "192.168.20.54 misp.yourdomain.local misp" | sudo tee -a /etc/hosts
   ```

3. **Use config file with explicit domain**

### Hostname Detection Fails Completely

If detection completely fails (returns `misp.local`), you can:

1. **Specify in interactive mode**: Type your desired FQDN when prompted
2. **Use config file**: Explicitly set the `domain` field
3. **Fix system networking**: Ensure DNS/hostname is properly configured

## Testing

Test the detection function:

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from lib.config import get_system_hostname
print(f'Detected: {get_system_hostname()}')
"
```

Expected output on your system:
```
Detected: misp-test.lan
```

## Version History

- **v5.5** (2025-10-15): Initial implementation of automatic hostname detection

## Related Documentation

- [INSTALLATION.md](docs/INSTALLATION.md) - Installation guide
- [CONFIGURATION-GUIDE.md](docs/CONFIGURATION-GUIDE.md) - Configuration options
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

---

**Last Updated**: 2025-10-15
**Feature Version**: 5.5
**Status**: Production Ready
