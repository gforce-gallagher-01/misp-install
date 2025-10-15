"""
Unit tests for MISP password validation module.

Tests the PasswordValidator class from lib/misp_password.py
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.misp_password import PasswordValidator


class TestPasswordValidator:
    """Test suite for PasswordValidator class."""

    def test_valid_passwords(self, sample_passwords):
        """Test that valid passwords pass validation."""
        validator = PasswordValidator()

        for password in sample_passwords["valid"]:
            is_valid, message = validator.validate(password)
            assert is_valid, f"Password '{password}' should be valid, but got: {message}"
            assert message == "Password meets requirements"

    def test_invalid_passwords(self, sample_passwords):
        """Test that invalid passwords fail validation."""
        validator = PasswordValidator()

        for password in sample_passwords["invalid"]:
            is_valid, message = validator.validate(password)
            assert not is_valid, f"Password '{password}' should be invalid"
            assert len(message) > 0, "Error message should be provided"

    def test_minimum_length(self):
        """Test minimum password length requirement (12 characters)."""
        validator = PasswordValidator()

        # 11 characters - should fail
        is_valid, message = validator.validate("Short123!@#")
        assert not is_valid
        assert "12 characters" in message

        # 12 characters - should pass (if meets other requirements)
        is_valid, message = validator.validate("Good1234!@#$")
        assert is_valid

    def test_uppercase_requirement(self):
        """Test uppercase letter requirement."""
        validator = PasswordValidator()

        # No uppercase
        is_valid, message = validator.validate("nouppercase123!@#")
        assert not is_valid
        assert "uppercase" in message.lower()

        # With uppercase
        is_valid, message = validator.validate("WithUppercase123!@#")
        assert is_valid

    def test_lowercase_requirement(self):
        """Test lowercase letter requirement."""
        validator = PasswordValidator()

        # No lowercase
        is_valid, message = validator.validate("NOLOWERCASE123!@#")
        assert not is_valid
        assert "lowercase" in message.lower()

        # With lowercase
        is_valid, message = validator.validate("WithLowercase123!@#")
        assert is_valid

    def test_number_requirement(self):
        """Test number requirement."""
        validator = PasswordValidator()

        # No numbers
        is_valid, message = validator.validate("NoNumbers!@#Abc")
        assert not is_valid
        assert "number" in message.lower() or "digit" in message.lower()

        # With numbers
        is_valid, message = validator.validate("WithNumbers123!@#")
        assert is_valid

    def test_special_character_requirement(self):
        """Test special character requirement."""
        validator = PasswordValidator()

        # No special characters
        is_valid, message = validator.validate("NoSpecialChars123Abc")
        assert not is_valid
        assert "special" in message.lower()

        # With special characters
        is_valid, message = validator.validate("WithSpecial123!@#")
        assert is_valid

    def test_empty_password(self):
        """Test that empty password is rejected."""
        validator = PasswordValidator()

        is_valid, message = validator.validate("")
        assert not is_valid
        assert len(message) > 0

    def test_whitespace_password(self):
        """Test that whitespace-only password is rejected."""
        validator = PasswordValidator()

        is_valid, message = validator.validate("            ")
        assert not is_valid

    def test_real_world_passwords(self):
        """Test real-world password examples."""
        validator = PasswordValidator()

        # Common patterns that should be valid
        real_passwords = [
            "MyMISP2024!Server",
            "Adm1n@MISP#2024",
            "P@ssw0rd!Complex",
            "NERC_CIP_2024!Pass",
            "S3cur3#MISP$Install"
        ]

        for password in real_passwords:
            is_valid, message = validator.validate(password)
            assert is_valid, f"Real-world password '{password}' should be valid: {message}"

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        validator = PasswordValidator()

        # Exactly 12 characters with all requirements
        is_valid, _ = validator.validate("Pass123!@#Ab")
        assert is_valid

        # Very long password (should still work)
        long_password = "VeryLongPassword123!@#$%^&*()_+" * 10
        is_valid, _ = validator.validate(long_password)
        assert is_valid

        # Unicode characters (should handle gracefully)
        unicode_password = "Pässwörd123!@#"
        is_valid, _ = validator.validate(unicode_password)
        # Result may vary, but should not crash
        assert isinstance(is_valid, bool)
