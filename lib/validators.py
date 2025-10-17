"""
Password and input validation utilities
"""

import getpass
import re
import secrets
import string
from typing import Tuple


class PasswordValidator:
    """Password validation and generation"""

    MIN_LENGTH = 12

    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """Validate password strength

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Password must be at least {PasswordValidator.MIN_LENGTH} characters"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"

    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """Generate a strong random password

        Args:
            length: Password length (default 16)

        Returns:
            Strong random password
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Ensure it meets requirements
        while not PasswordValidator.validate(password)[0]:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))

        return password

    @staticmethod
    def get_password_interactive(prompt: str) -> str:
        """Get and validate password interactively

        Args:
            prompt: Prompt to display to user

        Returns:
            Validated password
        """
        from lib.colors import Colors

        while True:
            password = getpass.getpass(prompt)

            valid, message = PasswordValidator.validate(password)
            if not valid:
                print(Colors.error(message))
                continue

            password_confirm = getpass.getpass("Confirm password: ")

            if password != password_confirm:
                print(Colors.error("Passwords don't match!"))
                continue

            print(Colors.success("Password set"))
            return password


class InputValidator:
    """Input validation utilities"""

    @staticmethod
    def validate_ip(ip: str) -> Tuple[bool, str]:
        """Validate IP address format

        Args:
            ip: IP address string

        Returns:
            Tuple of (is_valid, message)
        """
        import socket
        try:
            socket.inet_aton(ip)
            return True, "Valid IP address"
        except OSError:
            return False, "Invalid IP address format"

    @staticmethod
    def validate_domain(domain: str) -> Tuple[bool, str]:
        """Validate domain name format

        Args:
            domain: Domain name

        Returns:
            Tuple of (is_valid, message)
        """
        # Basic domain validation - allow alphanumeric, hyphens, dots
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'

        if re.match(pattern, domain):
            return True, "Valid domain name"
        else:
            return False, "Invalid domain name format"

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address format

        Args:
            email: Email address

        Returns:
            Tuple of (is_valid, message)
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(pattern, email):
            return True, "Valid email address"
        else:
            return False, "Invalid email address format"
