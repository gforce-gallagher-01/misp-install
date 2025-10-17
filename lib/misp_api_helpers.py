"""
MISP API Helper Functions
Centralized functions for MISP API operations (DRY refactoring)
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_api_key(env_file: str = '/opt/misp/.env',
                env_var: str = 'MISP_API_KEY') -> Optional[str]:
    """
    Get MISP API key from environment variable or .env file

    This function consolidates the duplicate API key retrieval logic
    found across 8+ scripts (identified in DRY analysis).

    Args:
        env_file: Path to .env file (default: /opt/misp/.env)
        env_var: Environment variable name (default: MISP_API_KEY)

    Returns:
        API key string if found, None otherwise

    Example:
        >>> api_key = get_api_key()
        >>> if api_key:
        >>>     print(f"Found key: {api_key[:8]}...")
    """
    # Try environment variable first
    api_key = os.environ.get(env_var)
    if api_key:
        return api_key.strip()

    # Try reading from .env file
    if os.path.exists(env_file):
        try:
            # Use sudo to read file owned by misp-owner
            result = subprocess.run(
                ['sudo', 'grep', f'{env_var}=', env_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                # Extract value after '='
                line = result.stdout.strip()
                if '=' in line:
                    api_key = line.split('=', 1)[1].strip()
                    return api_key if api_key else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
            pass

    return None


def get_misp_url(config_domain: Optional[str] = None,
                 env_file: str = '/opt/misp/.env',
                 env_var: str = 'BASE_URL') -> str:
    """
    Get MISP URL from configuration, environment, or .env file

    This function consolidates the duplicate MISP URL construction
    found across 34+ files (identified in DRY analysis).

    Priority order:
    1. config_domain parameter
    2. Environment variable
    3. .env file
    4. Default fallback (https://misp.local)

    Args:
        config_domain: Domain from configuration object
        env_file: Path to .env file (default: /opt/misp/.env)
        env_var: Environment variable name (default: BASE_URL)

    Returns:
        Full MISP URL (e.g., https://misp.local)

    Example:
        >>> url = get_misp_url()
        >>> print(url)  # https://misp.local
        >>> url = get_misp_url(config_domain="misp-test.lan")
        >>> print(url)  # https://misp-test.lan
    """
    # Priority 1: Config domain parameter
    if config_domain:
        domain = config_domain.strip()
        if not domain.startswith('http'):
            return f'https://{domain}'
        return domain

    # Priority 2: Environment variable
    base_url = os.environ.get(env_var)
    if base_url:
        base_url = base_url.strip()
        if not base_url.startswith('http'):
            return f'https://{base_url}'
        return base_url

    # Priority 3: .env file
    if os.path.exists(env_file):
        try:
            result = subprocess.run(
                ['sudo', 'grep', f'{env_var}=', env_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                line = result.stdout.strip()
                if '=' in line:
                    base_url = line.split('=', 1)[1].strip()
                    if base_url:
                        if not base_url.startswith('http'):
                            return f'https://{base_url}'
                        return base_url
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
            pass

    # Priority 4: Default fallback
    return 'https://misp.local'


def test_misp_connection(misp_url: str, api_key: str,
                         timeout: int = 10) -> Tuple[bool, str]:
    """
    Test connection to MISP instance

    Args:
        misp_url: MISP URL (e.g., https://misp.local)
        api_key: MISP API key
        timeout: Connection timeout in seconds

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = test_misp_connection(url, key)
        >>> if success:
        >>>     print("Connected!")
        >>> else:
        >>>     print(f"Failed: {msg}")
    """
    try:
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        headers = {
            'Authorization': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            f'{misp_url}/servers/getVersion',
            headers=headers,
            verify=False,
            timeout=timeout
        )

        if response.status_code == 200:
            try:
                data = response.json()
                version = data.get('version', 'unknown')
                return True, f"Connected to MISP v{version}"
            except:
                return True, "Connected to MISP"
        elif response.status_code == 403:
            return False, "Authentication failed - check API key"
        else:
            return False, f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - is MISP running?"
    except Exception as e:
        return False, str(e)


def mask_api_key(api_key: str, show_chars: int = 8) -> str:
    """
    Mask API key for safe logging/display

    Args:
        api_key: Full API key
        show_chars: Number of characters to show at start and end

    Returns:
        Masked key (e.g., "DcfTitOV...OteF")

    Example:
        >>> masked = mask_api_key("DcfTitOVAryMSXSUiZqKBV7srBS7jj7vK3iZOteF")
        >>> print(masked)  # DcfTitOV...OteF
    """
    if not api_key or len(api_key) < show_chars * 2:
        return "***"

    return f"{api_key[:show_chars]}...{api_key[-show_chars//2:]}"


# Usage example for documentation
if __name__ == "__main__":
    print("MISP API Helpers - Usage Examples")
    print("="*50)

    # Example 1: Get API key
    print("\n1. Get API Key:")
    api_key = get_api_key()
    if api_key:
        print(f"   Found: {mask_api_key(api_key)}")
    else:
        print("   Not found")

    # Example 2: Get MISP URL
    print("\n2. Get MISP URL:")
    url = get_misp_url()
    print(f"   URL: {url}")

    # Example 3: Test connection
    if api_key:
        print("\n3. Test Connection:")
        success, msg = test_misp_connection(url, api_key)
        print(f"   Result: {msg}")
