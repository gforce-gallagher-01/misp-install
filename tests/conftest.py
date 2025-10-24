"""
pytest configuration and shared fixtures for MISP installation tests.

This file contains pytest fixtures that are available to all test files.
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_misp_dir(temp_dir):
    """Create a mock MISP directory structure."""
    misp_dir = temp_dir / "misp"
    misp_dir.mkdir()
    (misp_dir / "logs").mkdir()
    (misp_dir / "ssl").mkdir()

    # Create mock .env file
    env_file = misp_dir / ".env"
    env_file.write_text("MYSQL_PASSWORD=testpass123\nMISP_BASEURL=https://misp.local\n")

    yield misp_dir


@pytest.fixture
def mock_config():
    """Create a mock MISP configuration."""
    return {
        "server_ip": "192.168.1.100",
        "domain": "misp-test.local",
        "admin_email": "admin@test.local",
        "admin_org": "Test Organization",
        "admin_password": "TestPass123!@#",
        "mysql_password": "MySQLPass123!@#",
        "gpg_passphrase": "GPGPass123!@#",
        "encryption_key": "test-encryption-key-32-chars",
        "environment": "development"
    }


@pytest.fixture
def sample_passwords():
    """Sample passwords for testing validation."""
    return {
        "valid": [
            "SecurePass123!@#",
            "AnotherGood1!Pass",
            "Complex#Pass123word",
            "My$ecureP@ss123"
        ],
        "invalid": [
            "short",                    # Too short
            "nouppercase123!",          # No uppercase
            "NOLOWERCASE123!",          # No lowercase
            "NoNumbers!@#",             # No numbers
            "NoSpecialChars123",        # No special chars
            "weak",                     # Too short + missing requirements
        ]
    }


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("MISP_DIR", "/tmp/misp-test")
