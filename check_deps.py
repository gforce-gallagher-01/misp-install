#!/usr/bin/env python3
"""
Check if all GUI installer dependencies are installed
"""

import sys

print("Checking MISP GUI Installer Dependencies...")
print("=" * 50)

all_good = True

# Check Python version
print(f"Python version: {sys.version}")
if sys.version_info < (3, 10):
    print("✗ Python 3.10+ required")
    all_good = False
else:
    print("✓ Python version OK")

# Check textual
try:
    import textual
    print(f"✓ textual {textual.__version__} installed")
except ImportError:
    print("✗ textual not installed")
    all_good = False

# Check pyperclip
try:
    import pyperclip
    print("✓ pyperclip installed")

    # Test clipboard
    try:
        test = pyperclip.paste()
        print("  ✓ Clipboard access works")
    except Exception as e:
        print(f"  ✗ Clipboard access failed: {e}")
        print("  → On Linux, install: sudo apt install xclip")
        all_good = False

except ImportError:
    print("✗ pyperclip not installed")
    print("  → This is REQUIRED for Ctrl+V paste!")
    all_good = False

print("=" * 50)

if all_good:
    print("✓ All dependencies OK! GUI installer ready.")
    print("\nRun with: misp-install-gui")
else:
    print("✗ Missing dependencies!")
    print("\nTo fix:")
    print("  1. Uninstall: pipx uninstall misp-installer-gui")
    print("  2. Reinstall: pipx install .")
    print("  3. On Linux: sudo apt install xclip")
    sys.exit(1)
