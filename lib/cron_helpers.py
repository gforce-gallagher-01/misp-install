"""
MISP Cron Management Helper Functions
Centralized functions for cron job operations (DRY refactoring)
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def get_current_crontab() -> Tuple[bool, str]:
    """
    Get current user's crontab contents

    This function consolidates the duplicate crontab retrieval logic
    found across 10+ scripts (identified in DRY analysis).

    Returns:
        Tuple of (success: bool, crontab_contents: str)

    Example:
        >>> success, crontab = get_current_crontab()
        >>> if success:
        >>>     print(f"Crontab has {len(crontab.splitlines())} lines")
    """
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # crontab -l returns exit code 1 if no crontab exists
        if result.returncode == 0:
            return True, result.stdout
        elif 'no crontab' in result.stderr.lower():
            return True, ""  # No crontab is valid state
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def has_cron_job(pattern: str) -> bool:
    """
    Check if cron job matching pattern exists

    Args:
        pattern: String to search for in crontab (e.g., "misp-daily-maintenance")

    Returns:
        True if pattern found in crontab, False otherwise

    Example:
        >>> if has_cron_job("misp-daily-maintenance"):
        >>>     print("Daily maintenance cron is installed")
    """
    success, crontab = get_current_crontab()
    if not success:
        return False

    return pattern in crontab


def add_cron_job(schedule: str, command: str, comment: Optional[str] = None) -> Tuple[bool, str]:
    """
    Add cron job to current user's crontab

    Args:
        schedule: Cron schedule (e.g., "0 3 * * *" for 3 AM daily)
        command: Command to execute
        comment: Optional comment to add above cron line

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = add_cron_job(
        >>>     "0 3 * * *",
        >>>     "/usr/bin/python3 /path/to/script.py",
        >>>     "Daily MISP maintenance"
        >>> )
    """
    try:
        # Get current crontab
        success, current_crontab = get_current_crontab()
        if not success:
            return False, f"Failed to get current crontab: {current_crontab}"

        # Build new cron line
        new_line = f"{schedule} {command}"

        # Check if already exists
        if new_line in current_crontab:
            return True, "Cron job already exists"

        # Build new crontab
        lines = current_crontab.strip().split('\n') if current_crontab.strip() else []

        # Add comment if provided
        if comment:
            lines.append(f"# {comment}")

        lines.append(new_line)
        new_crontab = '\n'.join(lines) + '\n'

        # Write new crontab
        result = subprocess.run(
            ['crontab', '-'],
            input=new_crontab,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return True, "Cron job added successfully"
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def remove_cron_job(pattern: str) -> Tuple[bool, str]:
    """
    Remove cron job(s) matching pattern

    Args:
        pattern: String pattern to match for removal

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = remove_cron_job("misp-daily-maintenance")
        >>> print(msg)
    """
    try:
        # Get current crontab
        success, current_crontab = get_current_crontab()
        if not success:
            return False, f"Failed to get current crontab: {current_crontab}"

        if not current_crontab.strip():
            return True, "Crontab is empty, nothing to remove"

        # Filter out lines matching pattern
        lines = current_crontab.strip().split('\n')
        filtered_lines = [line for line in lines if pattern not in line]

        # Check if anything was removed
        removed_count = len(lines) - len(filtered_lines)
        if removed_count == 0:
            return True, "No matching cron jobs found"

        # Write new crontab
        new_crontab = '\n'.join(filtered_lines) + '\n' if filtered_lines else ''

        result = subprocess.run(
            ['crontab', '-'],
            input=new_crontab,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return True, f"Removed {removed_count} cron job(s)"
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def list_cron_jobs(filter_pattern: Optional[str] = None) -> List[str]:
    """
    List all cron jobs (optionally filtered)

    Args:
        filter_pattern: Optional pattern to filter jobs (e.g., "misp")

    Returns:
        List of cron job lines

    Example:
        >>> misp_jobs = list_cron_jobs(filter_pattern="misp")
        >>> for job in misp_jobs:
        >>>     print(f"  • {job}")
    """
    success, crontab = get_current_crontab()
    if not success or not crontab.strip():
        return []

    lines = [line.strip() for line in crontab.strip().split('\n')]

    # Filter out comments and empty lines
    jobs = [line for line in lines if line and not line.startswith('#')]

    # Apply filter if provided
    if filter_pattern:
        jobs = [job for job in jobs if filter_pattern in job]

    return jobs


def validate_cron_schedule(schedule: str) -> Tuple[bool, str]:
    """
    Validate cron schedule syntax

    Args:
        schedule: Cron schedule string (e.g., "0 3 * * *")

    Returns:
        Tuple of (valid: bool, message: str)

    Example:
        >>> valid, msg = validate_cron_schedule("0 3 * * *")
        >>> if valid:
        >>>     print("Valid cron schedule")
    """
    parts = schedule.strip().split()

    # Basic validation: should have 5 parts (minute hour day month weekday)
    if len(parts) != 5:
        return False, f"Invalid schedule format: expected 5 parts, got {len(parts)}"

    # Validate each field
    field_names = ['minute', 'hour', 'day', 'month', 'weekday']
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]

    for part, name, (min_val, max_val) in zip(parts, field_names, ranges):
        # Skip wildcards and complex expressions
        if part in ['*', '*/1', '*/5', '*/10', '*/15', '*/30']:
            continue

        # Check if it's a range (e.g., "1-5")
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if not (min_val <= start <= max_val and min_val <= end <= max_val):
                    return False, f"Invalid {name} range: {part}"
            except ValueError:
                return False, f"Invalid {name} format: {part}"
            continue

        # Check if it's a list (e.g., "1,3,5")
        if ',' in part:
            try:
                values = list(map(int, part.split(',')))
                if not all(min_val <= v <= max_val for v in values):
                    return False, f"Invalid {name} values: {part}"
            except ValueError:
                return False, f"Invalid {name} format: {part}"
            continue

        # Check if it's a single number
        try:
            value = int(part)
            if not (min_val <= value <= max_val):
                return False, f"Invalid {name} value: {value} (must be {min_val}-{max_val})"
        except ValueError:
            # Not a number, could be a valid cron expression we don't validate
            pass

    return True, "Valid cron schedule"


def create_cron_script_wrapper(script_path: str,
                               log_file: Optional[str] = None,
                               env_vars: Optional[dict] = None) -> str:
    """
    Create cron-friendly command wrapper

    Args:
        script_path: Path to script to execute
        log_file: Optional log file path (defaults to /var/log/<script-name>.log)
        env_vars: Optional environment variables to set

    Returns:
        Full command string suitable for crontab

    Example:
        >>> cmd = create_cron_script_wrapper(
        >>>     "/path/to/script.py",
        >>>     log_file="/var/log/misp-maintenance/daily.log",
        >>>     env_vars={"MISP_API_KEY": "abc123"}
        >>> )
    """
    script_path = Path(script_path).resolve()

    # Determine log file
    if log_file is None:
        script_name = script_path.stem
        log_file = f"/var/log/{script_name}.log"

    # Build environment variable prefix
    env_prefix = ""
    if env_vars:
        env_parts = [f"{k}={v}" for k, v in env_vars.items()]
        env_prefix = " ".join(env_parts) + " "

    # Build command with output redirection
    if script_path.suffix == '.py':
        # Python script
        command = f"{env_prefix}/usr/bin/python3 {script_path} >> {log_file} 2>&1"
    elif script_path.suffix == '.sh':
        # Shell script
        command = f"{env_prefix}/bin/bash {script_path} >> {log_file} 2>&1"
    else:
        # Generic executable
        command = f"{env_prefix}{script_path} >> {log_file} 2>&1"

    return command


# Usage examples for documentation
if __name__ == "__main__":
    print("Cron Helpers - Usage Examples")
    print("="*50)

    # Example 1: List all MISP cron jobs
    print("\n1. List MISP Cron Jobs:")
    jobs = list_cron_jobs(filter_pattern="misp")
    if jobs:
        for job in jobs:
            print(f"   • {job}")
    else:
        print("   No MISP cron jobs found")

    # Example 2: Check if specific job exists
    print("\n2. Check Daily Maintenance Job:")
    if has_cron_job("misp-daily-maintenance"):
        print("   ✓ Daily maintenance cron is installed")
    else:
        print("   ✗ Daily maintenance cron not found")

    # Example 3: Validate cron schedule
    print("\n3. Validate Cron Schedule:")
    schedules = [
        "0 3 * * *",      # Valid: 3 AM daily
        "*/15 * * * *",   # Valid: Every 15 minutes
        "0 4 * * 0",      # Valid: 4 AM Sunday
        "60 3 * * *",     # Invalid: minute out of range
    ]
    for schedule in schedules:
        valid, msg = validate_cron_schedule(schedule)
        status = "✓" if valid else "✗"
        print(f"   {status} '{schedule}': {msg}")

    # Example 4: Create cron command wrapper
    print("\n4. Create Cron Command Wrapper:")
    cmd = create_cron_script_wrapper(
        "/home/gallagher/misp-install/misp-install/scripts/misp-daily-maintenance.py",
        log_file="/var/log/misp-maintenance/daily.log",
        env_vars={"MISP_API_KEY": "example-key"}
    )
    print(f"   Command: {cmd[:80]}...")

    # Example 5: Get current crontab
    print("\n5. Current Crontab:")
    success, crontab = get_current_crontab()
    if success:
        lines = [line for line in crontab.split('\n') if line.strip()]
        print(f"   Total lines: {len(lines)}")
    else:
        print(f"   Failed: {crontab}")
