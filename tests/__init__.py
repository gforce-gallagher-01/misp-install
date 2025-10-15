"""
MISP Installation Tool - Test Suite

This directory contains unit tests and integration tests for the MISP installation project.

Test Organization:
- test_misp_logger.py - Tests for centralized logging
- test_misp_config.py - Tests for configuration management
- test_misp_password.py - Tests for password validation
- test_misp_database.py - Tests for database operations (mocked)
- test_scripts.py - Integration tests for scripts

Running Tests:
    pytest tests/ -v                    # Run all tests
    pytest tests/test_misp_logger.py    # Run specific test file
    pytest tests/ -k password           # Run tests matching pattern
    pytest tests/ --cov=.               # Run with coverage report

Requirements:
    pip install pytest pytest-cov pytest-mock
"""
