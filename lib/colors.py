"""
Terminal color output utilities
"""


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

    @staticmethod
    def colored(text: str, color: str) -> str:
        """Apply color to text"""
        return f"{color}{text}{Colors.NC}"

    @classmethod
    def error(cls, text: str) -> str:
        """Red error message"""
        return cls.colored(f"❌ {text}", cls.RED)

    @classmethod
    def success(cls, text: str) -> str:
        """Green success message"""
        return cls.colored(f"✓ {text}", cls.GREEN)

    @classmethod
    def warning(cls, text: str) -> str:
        """Yellow warning message"""
        return cls.colored(f"⚠ {text}", cls.YELLOW)

    @classmethod
    def info(cls, text: str) -> str:
        """Cyan info message"""
        return cls.colored(text, cls.CYAN)
