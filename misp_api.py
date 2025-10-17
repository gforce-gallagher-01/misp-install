#!/usr/bin/env python3
"""
MISP API Helper Module
Version: 1.1
Date: 2025-10-14

Purpose:
    Centralized helper for MISP API access from automation scripts.
    Handles API key retrieval, connection setup, and common operations.

Usage:
    from misp_api import get_api_key, get_api_key_from_db, get_misp_client, test_connection

    # Get API key from file (.env or PASSWORDS.txt)
    api_key = get_api_key()

    # OR get API key from database (requires Docker + sudo)
    api_key = get_api_key_from_db()

    # Get configured requests session
    session = get_misp_client(api_key)

    # Test connection
    if test_connection(session):
        print("Connected to MISP")
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import requests
import urllib3

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default MISP URL
DEFAULT_MISP_URL = "https://misp-test.lan"


def get_api_key(env_file: Optional[str] = None) -> Optional[str]:
    """Get MISP API key from .env file or environment variable

    Args:
        env_file: Path to .env file (defaults to /opt/misp/.env)

    Returns:
        API key string, or None if not found

    Precedence:
        1. MISP_API_KEY environment variable
        2. MISP_API_KEY in /opt/misp/.env file
        3. MISP_API_KEY in PASSWORDS.txt file
    """
    # Check environment variable first
    api_key = os.environ.get('MISP_API_KEY')
    if api_key:
        return api_key

    # Check .env file
    if env_file is None:
        env_file = '/opt/misp/.env'

    env_path = Path(env_file)
    if env_path.exists():
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('MISP_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key:
                            return api_key
        except PermissionError:
            print(f"⚠️  Cannot read {env_file} - permission denied")
            print(f"   Try: sudo cat {env_file} | grep MISP_API_KEY")
        except Exception as e:
            print(f"⚠️  Error reading {env_file}: {e}")

    # Check PASSWORDS.txt as fallback
    passwords_file = Path('/opt/misp/PASSWORDS.txt')
    if passwords_file.exists():
        try:
            with open(passwords_file) as f:
                in_api_section = False
                for line in f:
                    line = line.strip()
                    if line == 'API KEY:':
                        in_api_section = True
                        continue
                    if in_api_section and line.startswith('Key:'):
                        api_key = line.split(':', 1)[1].strip()
                        if api_key:
                            return api_key
                    if in_api_section and line.startswith('==='):
                        break
        except PermissionError:
            print(f"⚠️  Cannot read {passwords_file} - permission denied")
            print(f"   Try: sudo cat {passwords_file}")
        except Exception as e:
            print(f"⚠️  Error reading {passwords_file}: {e}")

    return None


def get_api_key_from_db(misp_dir: str = "/opt/misp") -> Optional[str]:
    """Get MISP API key directly from database (for admin user)

    Args:
        misp_dir: MISP installation directory (defaults to /opt/misp)

    Returns:
        API key string for user_id=1 (admin), or None if not found

    Note:
        This queries the MySQL database directly and requires:
        - Docker containers running
        - MySQL password from .env file
        - sudo access to docker commands

    Usage:
        # For scripts that need database-level access
        api_key = get_api_key_from_db()

        # For most scripts, use get_api_key() instead (file-based)
    """
    try:
        # Import DatabaseManager for MySQL password retrieval
        sys.path.insert(0, str(Path(__file__).parent))
        from lib.database_manager import DatabaseManager

        db_manager = DatabaseManager(Path(misp_dir))
        mysql_password = db_manager.get_mysql_password() or ""

        # Query database for admin API key
        result = subprocess.run(
            ['sudo', 'docker', 'compose', 'exec', '-T', 'db',
             'mysql', '-umisp', f'-p{mysql_password}',
             'misp', '-e', 'SELECT authkey FROM auth_keys WHERE user_id=1 LIMIT 1;'],
            cwd=misp_dir,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # First line is column header, second is the key
                api_key = lines[1].strip()
                if api_key and api_key != 'authkey':  # Ignore header
                    return api_key
    except ImportError:
        print("⚠️  lib.database_manager not found - cannot query database")
    except FileNotFoundError:
        print("⚠️  Docker not found - cannot query database")
    except subprocess.TimeoutExpired:
        print("⚠️  Database query timeout")
    except Exception as e:
        print(f"⚠️  Error querying database: {e}")

    return None


def get_misp_url(env_file: Optional[str] = None) -> str:
    """Get MISP URL from .env file or use default

    Args:
        env_file: Path to .env file (defaults to /opt/misp/.env)

    Returns:
        MISP URL string (defaults to https://misp-test.lan)
    """
    # Check environment variable first
    misp_url = os.environ.get('MISP_URL') or os.environ.get('BASE_URL')
    if misp_url:
        return misp_url.rstrip('/')

    # Check .env file
    if env_file is None:
        env_file = '/opt/misp/.env'

    env_path = Path(env_file)
    if env_path.exists():
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('BASE_URL='):
                        misp_url = line.split('=', 1)[1].strip()
                        if misp_url:
                            return misp_url.rstrip('/')
        except:
            pass

    return DEFAULT_MISP_URL


def get_misp_client(api_key: Optional[str] = None, misp_url: Optional[str] = None,
                    timeout: int = 30) -> requests.Session:
    """Get configured requests session for MISP API

    Args:
        api_key: MISP API key (auto-detected if not provided)
        misp_url: MISP base URL (auto-detected if not provided)
        timeout: Default timeout in seconds (default: 30)

    Returns:
        Configured requests.Session object

    Example:
        session = get_misp_client()
        response = session.get('/feeds/index')
    """
    if api_key is None:
        api_key = get_api_key()
        if api_key is None:
            raise ValueError("MISP API key not found. Set MISP_API_KEY environment variable or add to /opt/misp/.env")

    if misp_url is None:
        misp_url = get_misp_url()

    # Create session with default headers
    session = requests.Session()
    session.headers.update({
        'Authorization': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })

    # Disable SSL verification for self-signed certificates
    session.verify = False

    # Set default timeout
    session.timeout = timeout

    # Store MISP URL for convenience
    session.misp_url = misp_url

    return session


def test_connection(session: Optional[requests.Session] = None,
                   api_key: Optional[str] = None,
                   misp_url: Optional[str] = None) -> Tuple[bool, str]:
    """Test MISP API connection

    Args:
        session: Configured requests session (will create if not provided)
        api_key: MISP API key (only if session not provided)
        misp_url: MISP base URL (only if session not provided)

    Returns:
        (success: bool, message: str) - Connection status and message

    Example:
        success, message = test_connection()
        if success:
            print(f"Connected: {message}")
        else:
            print(f"Failed: {message}")
    """
    try:
        if session is None:
            session = get_misp_client(api_key, misp_url)

        url = session.misp_url if hasattr(session, 'misp_url') else get_misp_url()

        response = session.get(
            f"{url}/servers/getPyMISPVersion.json",
            timeout=10
        )

        if response.status_code == 200:
            version_data = response.json()
            version = version_data.get('version', 'unknown')
            return True, f"Connected to MISP {version}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"

    except requests.exceptions.ConnectionError as e:
        return False, f"Connection failed: {e}"
    except requests.exceptions.Timeout as e:
        return False, f"Connection timeout: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def print_setup_instructions():
    """Print instructions for setting up API key"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           MISP API Key Setup Instructions                    ║
╚══════════════════════════════════════════════════════════════╝

OPTION 1: Use existing API key from installation
  The installation automatically generates an API key at:
  /opt/misp/.env (MISP_API_KEY variable)
  /opt/misp/PASSWORDS.txt (API KEY section)

OPTION 2: Generate new API key via web interface
  1. Login to MISP web interface
  2. Navigate to: Global Actions > My Profile > Auth Keys
  3. Click "Add authentication key"
  4. Set "Allowed IPs" to include your network (or leave blank)
  5. Copy the generated key
  6. Add to /opt/misp/.env:
     echo "MISP_API_KEY=<your_key>" | sudo tee -a /opt/misp/.env

OPTION 3: Set as environment variable
  export MISP_API_KEY=<your_key>

After setup, test with:
  python3 -c "from misp_api import test_connection; print(test_connection())"
""")


if __name__ == '__main__':
    """Test module functionality"""
    print("MISP API Helper - Test Mode\n")

    # Test API key retrieval
    print("1. Testing API key retrieval...")
    api_key = get_api_key()
    if api_key:
        print(f"   ✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("   ✗ No API key found")
        print_setup_instructions()
        sys.exit(1)

    # Test MISP URL retrieval
    print("\n2. Testing MISP URL retrieval...")
    misp_url = get_misp_url()
    print(f"   ✓ MISP URL: {misp_url}")

    # Test client creation
    print("\n3. Testing client creation...")
    try:
        session = get_misp_client()
        print("   ✓ Client created")
    except Exception as e:
        print(f"   ✗ Client creation failed: {e}")
        sys.exit(1)

    # Test connection
    print("\n4. Testing connection to MISP...")
    success, message = test_connection(session)
    if success:
        print(f"   ✓ {message}")
    else:
        print(f"   ✗ {message}")
        sys.exit(1)

    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)
