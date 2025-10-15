# MISP Installation Tool - Test Suite

**Status**: Initial test infrastructure created (October 2025)
**Framework**: pytest
**Coverage**: Core modules (password validation, config, logging)

## Overview

This directory contains unit tests and integration tests for the MISP installation automation project. The tests validate core functionality without requiring a full MISP Docker installation.

## Test Organization

```
tests/
├── __init__.py              # Test suite documentation
├── conftest.py              # pytest configuration and fixtures
├── test_misp_password.py    # Password validation tests (✅ Complete)
├── test_misp_logger.py      # Centralized logging tests (✅ Complete)
├── test_misp_config.py      # Configuration management tests (✅ Complete)
└── README.md                # This file
```

### Test Coverage Status

| Module | Test File | Status | Tests | Coverage |
|--------|-----------|--------|-------|----------|
| lib/misp_password.py | test_misp_password.py | ✅ Complete | 12 | High |
| misp_logger.py | test_misp_logger.py | ✅ Complete | 8 | Medium |
| lib/misp_config.py | test_misp_config.py | ✅ Complete | 12 | High |
| lib/misp_database.py | (TODO) | 📝 Planned | - | - |
| scripts/*.py | (TODO) | 📝 Planned | - | - |

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Or with uv (recommended)
uv pip install pytest pytest-cov pytest-mock
```

### Basic Usage

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_misp_password.py -v

# Run tests matching pattern
pytest tests/ -k password

# Run with coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Run with coverage and HTML report
pytest tests/ --cov=. --cov-report=html
```

### CI/CD Usage

The tests are automatically run by GitHub Actions on every push and pull request. See `.github/workflows/ci.yml` for the CI configuration.

```bash
# Same commands as used in CI
pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml
```

## Test Files

### test_misp_password.py

Tests for password validation functionality (`lib/misp_password.py`).

**Tests Include**:
- ✅ Valid password acceptance
- ✅ Invalid password rejection
- ✅ Minimum length requirement (12 characters)
- ✅ Uppercase letter requirement
- ✅ Lowercase letter requirement
- ✅ Number requirement
- ✅ Special character requirement
- ✅ Empty password handling
- ✅ Edge cases (long passwords, unicode)
- ✅ Real-world password examples

**Example**:
```bash
pytest tests/test_misp_password.py -v
```

### test_misp_logger.py

Tests for centralized logging functionality (`misp_logger.py`).

**Tests Include**:
- ✅ Logger creation
- ✅ Log levels (debug, info, warning, error, critical)
- ✅ Structured logging with extra fields
- ✅ CIM (Common Information Model) field names
- ✅ JSON log formatting
- ✅ Special character handling

**Example**:
```bash
pytest tests/test_misp_logger.py -v
```

### test_misp_config.py

Tests for configuration management (`lib/misp_config.py`).

**Tests Include**:
- ✅ Config creation from dictionary
- ✅ Attribute access
- ✅ Config validation
- ✅ Missing field handling
- ✅ Environment types (development, staging, production)
- ✅ Password field access
- ✅ Sensitive data handling (no passwords in __str__)
- ✅ Default values

**Example**:
```bash
pytest tests/test_misp_config.py -v
```

## Fixtures (conftest.py)

Shared fixtures available to all tests:

### temp_dir
Provides a temporary directory that's automatically cleaned up.
```python
def test_example(temp_dir):
    file = temp_dir / "test.txt"
    file.write_text("test")
```

### mock_misp_dir
Creates a mock MISP directory structure with logs, ssl, .env file.
```python
def test_example(mock_misp_dir):
    assert (mock_misp_dir / "logs").exists()
    assert (mock_misp_dir / ".env").exists()
```

### mock_config
Provides a complete mock MISP configuration dictionary.
```python
def test_example(mock_config):
    assert mock_config["server_ip"] == "192.168.1.100"
```

### sample_passwords
Provides valid and invalid password examples.
```python
def test_example(sample_passwords):
    for pwd in sample_passwords["valid"]:
        # Test with valid passwords
    for pwd in sample_passwords["invalid"]:
        # Test with invalid passwords
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure

```python
"""
Unit tests for [module name].

Tests the [Class/Function] from [module path]
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.module_name import ClassName


class TestClassName:
    """Test suite for ClassName."""

    def test_feature_works(self):
        """Test that feature works as expected."""
        obj = ClassName()
        result = obj.method()
        assert result == expected_value

    def test_error_handling(self):
        """Test that errors are handled properly."""
        obj = ClassName()
        with pytest.raises(ValueError):
            obj.method(invalid_input)
```

### Best Practices

1. **One concept per test** - Each test should verify one specific behavior
2. **Clear test names** - Name tests after what they verify: `test_password_requires_uppercase`
3. **Use fixtures** - Reuse common setup via pytest fixtures
4. **Mock external dependencies** - Don't rely on Docker, network, filesystem
5. **Test edge cases** - Empty strings, None values, very long inputs
6. **Document tests** - Add docstrings explaining what's being tested

## Integration Testing (Future)

Currently, tests focus on unit testing individual modules. Future integration tests will:

- Test full installation workflow (mocked)
- Test backup/restore cycle
- Test configuration file loading
- Test script interactions

These will likely require Docker and will be slower, so they'll be separated from fast unit tests.

## Coverage Goals

Target coverage levels:

- **Core libraries** (lib/*.py): 80%+ coverage
- **Utility modules**: 70%+ coverage
- **Scripts**: 50%+ coverage (harder to test, more integration-focused)

## CI/CD Integration

Tests run automatically via GitHub Actions on:

- Every push to main/develop branches
- Every pull request
- Manual workflow dispatch

See `.github/workflows/ci.yml` for the complete CI configuration.

## Troubleshooting

### Import errors

```bash
# Make sure you're running from project root
cd /home/gallagher/misp-install/misp-install
pytest tests/

# Or set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
pytest tests/
```

### Module not found

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-gui.txt
pip install pytest pytest-cov pytest-mock
```

### Tests fail in CI but pass locally

- Check Python version (CI tests 3.8-3.12)
- Check for file system dependencies (use temp_dir fixture)
- Check for environment-specific behavior

## Future Enhancements

Planned improvements:

1. **Database mocking** - Full tests for DatabaseManager
2. **Script integration tests** - Test complete workflows
3. **Performance tests** - Ensure scripts complete in reasonable time
4. **Security tests** - Validate no passwords in logs
5. **Docker integration tests** - Test with actual MISP containers (slow, optional)

## Resources

- **pytest documentation**: https://docs.pytest.org/
- **pytest fixtures**: https://docs.pytest.org/en/stable/fixture.html
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **pytest-mock**: https://pytest-mock.readthedocs.io/

---

**Last Updated**: October 2025
**Maintained by**: tKQB Enterprises
**Test Framework**: pytest 7.x+
