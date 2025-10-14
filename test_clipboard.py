#!/usr/bin/env python3
"""
Test clipboard paste functionality
"""

import sys

# Test 1: Check if pyperclip is available
print("=" * 50)
print("Test 1: Checking pyperclip availability")
print("=" * 50)

try:
    import pyperclip
    print("✓ pyperclip imported successfully")

    # Test clipboard read
    try:
        clipboard_content = pyperclip.paste()
        print(f"✓ Current clipboard content: '{clipboard_content}'")
    except Exception as e:
        print(f"✗ Failed to read clipboard: {e}")
        print("\nOn Linux, you need xclip or xsel:")
        print("  sudo apt install xclip")
        sys.exit(1)

    # Test clipboard write
    try:
        test_text = "test-12345"
        pyperclip.copy(test_text)
        verify = pyperclip.paste()
        if verify == test_text:
            print(f"✓ Clipboard write/read test passed")
        else:
            print(f"✗ Clipboard test failed: expected '{test_text}', got '{verify}'")
    except Exception as e:
        print(f"✗ Failed to write clipboard: {e}")

except ImportError:
    print("✗ pyperclip not installed")
    print("\nInstall with:")
    print("  pip install pyperclip")
    print("Or:")
    print("  pipx reinstall .")
    sys.exit(1)

# Test 2: Check Textual
print("\n" + "=" * 50)
print("Test 2: Checking Textual availability")
print("=" * 50)

try:
    import textual
    print(f"✓ Textual version: {textual.__version__}")
except ImportError:
    print("✗ Textual not installed")
    sys.exit(1)

# Test 3: Simple Textual app with clipboard paste
print("\n" + "=" * 50)
print("Test 3: Testing Textual app with Ctrl+V paste")
print("=" * 50)
print("\nStarting test app...")
print("Instructions:")
print("  1. Copy some text to your clipboard (Ctrl+C anywhere)")
print("  2. In the app, press Ctrl+V to paste")
print("  3. Press q to quit")
print("\nLaunching in 2 seconds...")

import time
time.sleep(2)

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from textual.containers import Container

class ClipboardTestApp(App):
    """Test app for clipboard paste"""

    CSS = """
    Container {
        align: center middle;
        padding: 2;
    }

    Input {
        width: 60;
        margin: 1;
    }

    Static {
        width: 60;
        margin: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+v", "paste_test", "Paste (Ctrl+V)"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("Clipboard Paste Test", id="title")
            yield Static("Copy text, focus input, press Ctrl+V", id="instructions")
            yield Input(placeholder="Click here and press Ctrl+V to paste", id="test-input")
            yield Static("Status: Waiting...", id="status")
        yield Footer()

    def action_paste_test(self):
        """Handle Ctrl+V paste"""
        try:
            clipboard_text = pyperclip.paste()

            # Get the focused widget
            focused = self.focused

            if isinstance(focused, Input):
                # Insert at cursor position
                current_value = focused.value
                cursor_pos = focused.cursor_position

                new_value = current_value[:cursor_pos] + clipboard_text + current_value[cursor_pos:]
                focused.value = new_value
                focused.cursor_position = cursor_pos + len(clipboard_text)

                self.query_one("#status", Static).update(f"✓ Pasted: '{clipboard_text}'")
                self.notify("✓ Paste successful!", severity="information")
            else:
                self.query_one("#status", Static).update("⚠️  Focus the input field first")
                self.notify("Focus the input field first", severity="warning")

        except Exception as e:
            self.query_one("#status", Static).update(f"✗ Paste failed: {e}")
            self.notify(f"Paste failed: {e}", severity="error")

if __name__ == "__main__":
    app = ClipboardTestApp()
    app.run()
