# MISP Installation Setup Guide

## Prerequisites

Before running the MISP installation scripts, you need to set up the log directory with proper permissions.

### Quick Setup (One-Time)

Run this command once to create the log directory:

```bash
sudo mkdir -p /opt/misp/logs && sudo chown $USER:$USER /opt/misp && sudo chmod 775 /opt/misp/logs
```

This creates the `/opt/misp/logs` directory and gives your user account ownership, allowing the scripts to write logs without requiring sudo.

### Alternative: Configure Passwordless Sudo (For Automation)

If you're running these scripts in an automated environment (CI/CD, cron, etc.), you can configure passwordless sudo for specific commands:

1. Edit sudoers file:
```bash
sudo visudo
```

2. Add this line (replace `username` with your actual username):
```
username ALL=(ALL) NOPASSWD: /bin/mkdir, /bin/chown, /bin/chmod, /usr/bin/docker, /usr/bin/apt
```

## Running the Scripts

Once setup is complete, run the installation:

```bash
# Interactive mode
python3 misp-install.py

# Non-interactive with config file
python3 misp-install.py --config config/misp-config.json --non-interactive
```

## Troubleshooting

### "Permission denied" errors
- Run the setup command above
- Ensure your user has docker group membership: `groups | grep docker`

### "sudo: a password is required"
- You're running in a non-interactive environment without the setup
- Either run the setup command first, or configure passwordless sudo

### Logs not being created
- Check that `/opt/misp/logs` exists and is writable by your user
- The scripts will fall back to console-only logging if the directory can't be accessed
