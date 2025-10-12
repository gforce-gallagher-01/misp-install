# Contributing to MISP Installer

First off, thank you for considering contributing to MISP Installer! It's people like you that make this tool better for everyone.

## 🎯 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## 🤔 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Use the bug report template:**
- Clear and descriptive title
- Exact steps to reproduce the problem
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- System information (OS, Python version, etc.)
- Relevant logs from `/opt/misp/logs/`

**Example:**
```markdown
**Description:** Installation fails during Phase 5 (Clone Repository)

**Steps to Reproduce:**
1. Run `python3 misp-install.py`
2. Complete configuration prompts
3. Installation proceeds to Phase 5
4. Error occurs during git clone

**Expected:** Repository clones successfully
**Actual:** Timeout error after 5 minutes

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.6
- Internet: Behind corporate proxy

**Logs:**
```
[Attach relevant log snippet]
```
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any alternatives you've considered

**Example:**
```markdown
**Enhancement:** Add support for PostgreSQL as database backend

**Problem:** Currently only MySQL/MariaDB is supported

**Solution:** Add option in config to choose database backend

**Benefits:**
- More flexibility for users
- Some organizations prefer PostgreSQL
- Better performance for certain workloads

**Implementation Ideas:**
- Add `database_type` config option
- Create PostgreSQL docker-compose template
- Update documentation
```

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our code style
3. **Add tests** if applicable
4. **Update documentation** if needed
5. **Ensure tests pass**
6. **Submit pull request**

#### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md with a note describing your changes
3. The PR will be merged once you have the sign-off of at least one maintainer

#### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Adding or updating tests

Examples:
```
feature/add-postgresql-support
bugfix/fix-docker-group-activation
docs/update-troubleshooting-guide
refactor/improve-error-handling
test/add-backup-script-tests
```

## 💻 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Ubuntu 20.04+ (for testing)
- Docker (for testing)

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/misp-installer.git
cd misp-installer

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/misp-installer.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Install pre-commit hooks (if used)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_installer.py

# Run with coverage
pytest --cov=. tests/

# Run linting
flake8 misp-install.py
black --check misp-install.py
mypy misp-install.py
```

### Testing Locally

```bash
# Test on a VM or container
# DO NOT test on production systems!

# Interactive mode
python3 misp-install.py

# With config file
python3 misp-install.py --config config/misp-config-dev.yaml

# Test resume capability
# (interrupt with Ctrl+C, then resume)
python3 misp-install.py --resume
```

## 📝 Code Style

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length:** 100 characters (not 79)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Grouped and sorted (stdlib, third-party, local)
- **Docstrings:** Google style
- **Type hints:** Use for function signatures

**Example:**

```python
from typing import Dict, List, Optional

def create_backup(misp_dir: Path, backup_dir: Path) -> Optional[Path]:
    """
    Create a backup of MISP installation.
    
    Args:
        misp_dir: Path to MISP installation directory
        backup_dir: Path to backup destination directory
    
    Returns:
        Path to created backup or None if failed
    
    Raises:
        PermissionError: If backup directory is not writable
    """
    # Implementation
    pass
```

### Bash Script Style

- Use `#!/bin/bash` shebang
- Use `set -e` for error handling
- Quote variables: `"$variable"`
- Use functions for reusability
- Add comments for complex logic

**Example:**

```bash
#!/bin/bash
set -e

# Function to check if MISP is running
check_misp_status() {
    local misp_dir="$1"
    
    if [ ! -d "$misp_dir" ]; then
        echo "MISP directory not found"
        return 1
    fi
    
    cd "$misp_dir"
    sudo docker compose ps | grep -q "Up"
}
```

### Documentation Style

- Use Markdown for all documentation
- Start each document with a clear title
- Use headers to organize content
- Include code examples with syntax highlighting
- Add table of contents for long documents
- Use emoji sparingly but effectively (✅ ⚠️ 🔧 📝)

## 🧪 Testing Guidelines

### What to Test

- **Happy path:** Normal, expected usage
- **Edge cases:** Unusual but valid inputs
- **Error handling:** Invalid inputs, missing files, etc.
- **Cross-platform:** Different OS versions (if applicable)
- **Resume capability:** Interrupted installations
- **Config files:** YAML and JSON variants

### Writing Tests

```python
import pytest
from pathlib import Path
from misp_install import MISPConfig, PasswordValidator

def test_password_validation_strong():
    """Test that strong passwords pass validation"""
    password = "MySecure123!Password"
    valid, message = PasswordValidator.validate(password)
    assert valid is True
    assert message == "Password is strong"

def test_password_validation_weak():
    """Test that weak passwords fail validation"""
    password = "weak"
    valid, message = PasswordValidator.validate(password)
    assert valid is False
    assert "at least 12 characters" in message

def test_config_from_yaml(tmp_path):
    """Test loading config from YAML file"""
    config_file = tmp_path / "test-config.yaml"
    config_file.write_text("""
server_ip: "192.168.1.100"
domain: "test.misp.local"
admin_email: "test@example.com"
    """)
    
    config = MISPConfig.from_yaml(str(config_file))
    assert config.server_ip == "192.168.1.100"
    assert config.domain == "test.misp.local"
```

## 📚 Documentation Guidelines

### When to Update Documentation

Update documentation when you:
- Add a new feature
- Change existing behavior
- Fix a bug that was unclear
- Add new configuration options
- Change command-line arguments

### Documentation Checklist

- [ ] Updated README.md if user-facing changes
- [ ] Updated relevant docs/ files
- [ ] Added examples if applicable
- [ ] Updated CHANGELOG.md
- [ ] Checked for broken links
- [ ] Verified code examples work

## 🔀 Git Workflow

### Making Changes

```bash
# Get latest upstream changes
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Stage changes
git add .

# Commit with meaningful message
git commit -m "Add PostgreSQL support

- Add database_type config option
- Create PostgreSQL docker-compose template
- Update documentation
- Add tests for PostgreSQL setup"

# Push to your fork
git push origin feature/my-feature
```

### Commit Messages

Use clear, descriptive commit messages:

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

Good ✅
```
feat: Add PostgreSQL support

- Add database_type config option
- Create PostgreSQL docker-compose template
- Update installation documentation

Closes #123
```

Good ✅
```
fix: Resolve docker group activation on Ubuntu 22.04

The previous method didn't work on newer Ubuntu versions.
Now uses sg command for immediate activation.

Fixes #456
```

Bad ❌
```
fixed stuff
```

Bad ❌
```
Update files
```

## 🏷️ Labels

We use labels to categorize issues and PRs:

- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested
- `wontfix` - This will not be worked on
- `duplicate` - This issue/PR already exists

## 🚀 Release Process

Releases are handled by maintainers:

1. Update version in `misp-install.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v5.1.0 -m "Version 5.1.0"`
4. Push tag: `git push origin v5.1.0`
5. GitHub Actions creates release automatically

## 📞 Getting Help

- **Questions:** Open a GitHub Discussion or Issue
- **Chat:** Join our Gitter/Discord (if available)
- **Email:** Contact maintainers (see README)

## 🎖️ Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- Contributors section in README.md
- GitHub contributors graph

## 📋 Checklist for Contributors

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts
- [ ] All checks passing (CI/CD)

## 🙏 Thank You!

Your contributions make this project better for everyone in the MISP community. Whether it's code, documentation, bug reports, or feature suggestions, every contribution is valued.

---

**Questions about contributing?** Open an issue with the `question` label!