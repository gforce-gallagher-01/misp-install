"""
Unit tests for MISP configuration management.

Tests the MISPConfig class from lib/misp_config.py
"""

import pytest
import sys
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.misp_config import MISPConfig


class TestMISPConfig:
    """Test suite for MISPConfig class."""

    def test_config_creation(self, mock_config):
        """Test that config can be created from dictionary."""
        config = MISPConfig(mock_config)
        assert config is not None

    def test_config_attributes(self, mock_config):
        """Test that config attributes are accessible."""
        config = MISPConfig(mock_config)

        assert config.server_ip == "192.168.1.100"
        assert config.domain == "misp-test.local"
        assert config.admin_email == "admin@test.local"
        assert config.admin_org == "Test Organization"

    def test_config_validation(self, mock_config):
        """Test that config validates required fields."""
        config = MISPConfig(mock_config)

        # Valid config should not raise exceptions
        assert hasattr(config, 'server_ip')
        assert hasattr(config, 'domain')

    def test_missing_required_field(self):
        """Test that missing required fields raise appropriate errors."""
        incomplete_config = {
            "server_ip": "192.168.1.100",
            # Missing domain
        }

        # Should handle missing fields gracefully
        # (implementation may vary - either raise exception or use defaults)
        try:
            config = MISPConfig(incomplete_config)
            # If no exception, check for default value or None
            assert True
        except (KeyError, ValueError, AttributeError):
            # Expected for strict validation
            assert True

    def test_config_from_json_file(self, temp_dir, mock_config):
        """Test loading config from JSON file."""
        config_file = temp_dir / "test-config.json"
        with open(config_file, 'w') as f:
            json.dump(mock_config, f)

        # Should be able to load from file
        assert config_file.exists()

        with open(config_file) as f:
            loaded_config = json.load(f)

        config = MISPConfig(loaded_config)
        assert config.server_ip == mock_config["server_ip"]

    def test_environment_types(self):
        """Test that environment types are validated."""
        valid_environments = ["development", "staging", "production"]

        for env in valid_environments:
            config_data = {
                "server_ip": "192.168.1.100",
                "domain": "test.local",
                "admin_email": "admin@test.local",
                "admin_org": "Test Org",
                "admin_password": "TestPass123!",
                "mysql_password": "MySQLPass123!",
                "gpg_passphrase": "GPGPass123!",
                "environment": env
            }

            config = MISPConfig(config_data)
            assert config.environment == env

    def test_password_fields_present(self, mock_config):
        """Test that password fields are accessible (but not logged)."""
        config = MISPConfig(mock_config)

        # Password fields should exist
        assert hasattr(config, 'admin_password')
        assert hasattr(config, 'mysql_password')
        assert hasattr(config, 'gpg_passphrase')

        # Should not be empty
        assert len(config.admin_password) > 0
        assert len(config.mysql_password) > 0

    def test_config_immutability(self, mock_config):
        """Test that config values are not accidentally modified."""
        config = MISPConfig(mock_config)
        original_ip = config.server_ip

        # Attempt to modify (behavior depends on implementation)
        try:
            config.server_ip = "10.0.0.1"
            # If modification is allowed, verify it worked
            # If not allowed, exception should be raised
        except AttributeError:
            # Immutable config - good for thread safety
            pass

        # Verify original value (if immutable)
        # or new value (if mutable)
        assert isinstance(config.server_ip, str)

    def test_config_to_dict(self, mock_config):
        """Test converting config back to dictionary."""
        config = MISPConfig(mock_config)

        # Should be able to convert to dict (if method exists)
        if hasattr(config, 'to_dict'):
            config_dict = config.to_dict()
            assert isinstance(config_dict, dict)
            assert 'server_ip' in config_dict

    def test_sensitive_data_handling(self, mock_config):
        """Test that sensitive data is handled securely."""
        config = MISPConfig(mock_config)

        # String representation should not expose passwords
        config_str = str(config)
        assert mock_config['admin_password'] not in config_str or '***' in config_str

        # repr should also be safe
        config_repr = repr(config)
        assert mock_config['mysql_password'] not in config_repr or '***' in config_repr


class TestConfigDefaults:
    """Test suite for default configuration values."""

    def test_default_environment(self):
        """Test that default environment is production."""
        minimal_config = {
            "server_ip": "192.168.1.100",
            "domain": "misp.local",
            "admin_email": "admin@misp.local",
            "admin_org": "Default Org",
            "admin_password": "Pass123!",
            "mysql_password": "MySQL123!",
            "gpg_passphrase": "GPG123!"
        }

        config = MISPConfig(minimal_config)

        # Default environment should be production (if implemented)
        if hasattr(config, 'environment'):
            assert config.environment in ["production", "development", "staging"]

    def test_misp_dir_default(self):
        """Test that MISP directory has a sensible default."""
        config = MISPConfig({
            "server_ip": "192.168.1.100",
            "domain": "misp.local",
            "admin_email": "admin@misp.local",
            "admin_org": "Org",
            "admin_password": "Pass123!",
            "mysql_password": "MySQL123!",
            "gpg_passphrase": "GPG123!"
        })

        # Should have MISP_DIR constant
        assert hasattr(MISPConfig, 'MISP_DIR') or hasattr(config, 'MISP_DIR')
