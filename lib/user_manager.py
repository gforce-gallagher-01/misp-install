"""
MISP user management utilities
"""

import os
import pwd
import subprocess
from typing import Tuple

MISP_USER = "misp-owner"
MISP_HOME = "/home/misp-owner"


def get_current_username() -> str:
    """Get current username

    Returns:
        Current username
    """
    return pwd.getpwuid(os.getuid()).pw_name


def user_exists(username: str) -> bool:
    """Check if user exists

    Args:
        username: Username to check

    Returns:
        True if user exists
    """
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def ensure_misp_user_exists() -> bool:
    """Create misp-owner user if it doesn't exist

    Returns:
        True if user exists or was created successfully
    """
    if user_exists(MISP_USER):
        return True

    # User doesn't exist, create it
    print(f"Creating dedicated user: {MISP_USER}")
    print("This requires sudo privileges (one-time operation)...")

    try:
        # Create system user with home directory
        subprocess.run([
            'sudo', 'useradd',
            '--system',  # System user
            '--create-home',  # Create home directory
            '--home-dir', MISP_HOME,
            '--shell', '/bin/bash',
            '--comment', 'MISP Installation Owner',
            MISP_USER
        ], check=True, capture_output=True, text=True)

        print(f"✓ Created system user: {MISP_USER}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create user {MISP_USER}: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating user: {e}")
        return False


def remove_misp_user() -> Tuple[bool, str]:
    """Remove misp-owner user

    Returns:
        Tuple of (success, message)
    """
    if not user_exists(MISP_USER):
        return True, f"User {MISP_USER} does not exist"

    try:
        subprocess.run([
            'sudo', 'userdel', '-r',  # -r removes home directory
            MISP_USER
        ], check=True, capture_output=True, text=True)

        return True, f"User {MISP_USER} removed"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to remove user: {e.stderr}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_user_home(username: str) -> str:
    """Get home directory for user

    Args:
        username: Username

    Returns:
        Home directory path

    Raises:
        KeyError: If user doesn't exist
    """
    return pwd.getpwnam(username).pw_dir


def is_user_in_group(username: str, group: str) -> bool:
    """Check if user is in a group

    Args:
        username: Username
        group: Group name

    Returns:
        True if user is in group
    """
    try:
        result = subprocess.run(
            ['groups', username],
            capture_output=True,
            text=True
        )
        return group in result.stdout
    except Exception:
        return False
