# CI/CD Guide for MISP Installation Project

**Created**: October 2025
**Last Updated**: October 2025
**Status**: Production Ready

## Overview

This project uses modern CI/CD practices with GitHub Actions, automated testing, and dependency management. This guide explains the entire CI/CD infrastructure.

## Table of Contents

- [Quick Start](#quick-start)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Testing Infrastructure](#testing-infrastructure)
- [Dependency Management](#dependency-management)
- [Issue & PR Templates](#issue--pr-templates)
- [Release Process](#release-process)
- [Local Development](#local-development)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Contributors

```bash
# 1. Clone repository
git clone https://github.com/yourusername/misp-install.git
cd misp-install

# 2. Install dependencies with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements.txt
uv pip install -r requirements-gui.txt
uv pip install pytest pytest-cov pytest-mock ruff

# 3. Run tests locally
pytest tests/ -v

# 4. Run linting
uvx ruff check .
uvx ruff format --check .

# 5. Make changes, commit, push
git checkout -b feature/your-feature
# ... make changes ...
pytest tests/  # Ensure tests pass
git commit -m "feat: your feature description"
git push origin feature/your-feature

# 6. Create pull request
# GitHub Actions will automatically run CI tests
```

### For Maintainers

```bash
# Create a release
git tag v5.4.1
git push origin v5.4.1
# GitHub Actions automatically creates release and builds artifacts
```

---

## GitHub Actions Workflows

### Main CI Pipeline (`.github/workflows/ci.yml`)

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs** (run in parallel):

#### 1. **Validate** - Python Syntax & Import Validation
- **Matrix**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Speed**: ~2 minutes
- **Purpose**: Ensure code is syntactically correct and imports work
- **Actions**:
  - Compile all .py files with `python3 -m py_compile`
  - Test imports for core modules (misp_logger, lib/*)
  - Validate on all supported Python versions

#### 2. **Lint** - Code Quality with Ruff
- **Speed**: ~1 minute
- **Purpose**: Enforce code style and catch common errors
- **Actions**:
  - Run `ruff check` (linting)
  - Run `ruff format --check` (formatting)
- **Status**: Currently `continue-on-error: true` (warnings don't fail build)

#### 3. **Security** - Security Scan with Bandit
- **Speed**: ~1 minute
- **Purpose**: Identify security vulnerabilities
- **Actions**:
  - Run `bandit -r . -ll` (low-level and above)
- **Status**: Currently `continue-on-error: true` (informational)

#### 4. **Test** - Unit Tests with pytest
- **Speed**: ~2 minutes
- **Purpose**: Run automated test suite
- **Actions**:
  - Run `pytest tests/ -v --cov=. --cov-report=xml`
  - Upload coverage to Codecov (optional)
- **Coverage**: Tests password validation, logging, config

#### 5. **Docs** - Documentation Validation
- **Speed**: <1 minute
- **Purpose**: Ensure documentation exists and is structured properly
- **Actions**:
  - Check for README.md, CLAUDE.md, TODO.md, SCRIPTS.md
  - Count markdown files in docs/ folder

#### 6. **Summary** - Build Status Summary
- **Purpose**: Aggregate all job results
- **Actions**:
  - Display status of all jobs
  - Fail build if validation fails
  - Pass build if only linting/security has warnings

**Example Output**:
```
✅ Validation: success
✅ Linting: success
✅ Security: success
✅ Tests: success
✅ Docs: success
✅ Build PASSED: All critical checks successful
```

---

### Release Automation (`.github/workflows/release.yml`)

**Triggers**:
- Push tags matching `v*.*.*` (e.g., v5.4.0, v5.4.1)
- Manual workflow dispatch

**Jobs**:

#### 1. **Create Release**
- Extract version from git tag
- Extract changelog (from CHANGELOG.md or generate)
- Create GitHub Release with:
  - Release notes
  - Attached files: misp-install.py, misp_install_gui.py, install-gui.sh
  - Version tag

#### 2. **Build Package** (Optional)
- Build Python wheel/sdist with `python3 -m build`
- Upload as release artifact
- Retained for 30 days

**Creating a Release**:
```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pyproject.toml docs/testing_and_updates/CHANGELOG.md
git commit -m "chore: prepare release v5.4.1"
git push

# 4. Create and push tag
git tag -a v5.4.1 -m "Release v5.4.1: Bug fixes and improvements"
git push origin v5.4.1

# 5. GitHub Actions automatically creates release
```

---

## Testing Infrastructure

### Test Directory Structure

```
tests/
├── __init__.py              # Test suite documentation
├── conftest.py              # pytest fixtures and configuration
├── test_misp_password.py    # Password validation tests (12 tests)
├── test_misp_logger.py      # Logging tests (8 tests)
├── test_misp_config.py      # Configuration tests (12 tests)
└── README.md                # Test documentation
```

### Running Tests Locally

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_misp_password.py -v

# Tests matching pattern
pytest tests/ -k password

# With coverage
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

# Fast tests only (exclude slow/integration tests)
pytest tests/ -m "not slow"
```

### Test Fixtures (conftest.py)

**Available fixtures**:
- `temp_dir` - Temporary directory (auto-cleaned)
- `mock_misp_dir` - Mock MISP directory structure (/opt/misp)
- `mock_config` - Sample MISP configuration dictionary
- `sample_passwords` - Valid and invalid password examples

**Example usage**:
```python
def test_example(mock_config, temp_dir):
    config = MISPConfig(mock_config)
    assert config.server_ip == "192.168.1.100"

    file = temp_dir / "test.json"
    file.write_text(json.dumps(mock_config))
```

### Writing New Tests

1. Create test file: `tests/test_<module>.py`
2. Import module and pytest
3. Write test class and methods
4. Run `pytest tests/test_<module>.py -v`
5. Check coverage: `pytest --cov=lib.<module> tests/test_<module>.py`

**Example**:
```python
"""Unit tests for example module."""
import pytest
from lib.example import ExampleClass

class TestExampleClass:
    def test_feature_works(self):
        """Test that feature works as expected."""
        obj = ExampleClass()
        result = obj.method()
        assert result == expected
```

---

## Dependency Management

### Using uv (Recommended - 2025)

**Why uv?**
- ⚡ 10-100x faster than pip
- 🔒 Lockfile support (deterministic builds)
- 💾 Optimized caching for CI/CD
- 🎯 Official GitHub Actions support

**Installation**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-gui.txt

# Install dev dependencies
uv pip install pytest pytest-cov pytest-mock ruff mypy
```

**Project Structure** (pyproject.toml):
```toml
[project]
dependencies = [
    "pyyaml>=6.0",
]

[project.optional-dependencies]
gui = ["textual>=0.45.0", "textual-dev>=1.2.0", "pyperclip>=1.8.0"]
dev = ["pytest>=7.4.0", "pytest-cov>=4.1.0", "ruff>=0.1.0"]
all = ["misp-installer[gui,dev]"]
```

**Installing optional dependencies**:
```bash
# GUI dependencies
uv pip install -e ".[gui]"

# Dev dependencies
uv pip install -e ".[dev]"

# All dependencies
uv pip install -e ".[all]"
```

### Dependabot Configuration

**File**: `.github/dependabot.yml`

**What it does**:
- Automatically checks for dependency updates weekly (Mondays 9 AM ET)
- Creates pull requests for updates
- Groups related updates (testing, linting, gui)
- Monitors GitHub Actions versions too

**Update Groups**:
- `testing` - pytest, pytest-cov, pytest-mock
- `linting` - ruff, mypy, black
- `gui` - textual, pyperclip

**Example Dependabot PR**:
```
deps(testing): update pytest from 7.4.0 to 7.4.3

- pytest 7.4.0 -> 7.4.3
- pytest-cov 4.1.0 -> 4.1.2

Release notes: ...
```

**Managing Dependabot PRs**:
1. Review changes and test results
2. Merge if all tests pass
3. Close if update causes issues (add to ignore list)

---

## Issue & PR Templates

### Issue Templates

Located in `.github/ISSUE_TEMPLATE/`:

#### 1. **Bug Report** (`bug_report.yml`)
- Structured form for bug reports
- Fields: description, affected script, steps to reproduce, environment
- Auto-labels: `bug`, `triage`

#### 2. **Feature Request** (`feature_request.yml`)
- Proposal for new features
- Fields: problem statement, solution, priority, use case
- Auto-labels: `enhancement`, `feature-request`

#### 3. **NERC CIP Question** (`nerc_cip_question.yml`)
- Compliance-specific questions
- Fields: CIP standard, impact level, question category
- Auto-labels: `nerc-cip`, `question`

#### 4. **Config** (`config.yml`)
- Links to documentation before opening issue
- Reduces duplicate questions

### Pull Request Template

Located in `.github/pull_request_template.md`

**Checklist includes**:
- Type of change (bug fix, feature, docs)
- Testing performed
- Code quality checks (pytest, ruff)
- Documentation updates
- NERC CIP compliance (if applicable)
- Security considerations

**Using the template**:
1. Create PR from branch
2. Template auto-fills PR description
3. Fill in all sections
4. Check all applicable boxes
5. Wait for CI to complete
6. Request review

---

## Release Process

### Versioning Scheme

**Format**: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v5 -> v6)
- **MINOR**: New features, backward compatible (v5.4 -> v5.5)
- **PATCH**: Bug fixes (v5.4.0 -> v5.4.1)

### Release Checklist

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Run full test suite**: `pytest tests/ -v`
4. **Test installation** on clean system
5. **Commit changes**: `git commit -m "chore: prepare release vX.Y.Z"`
6. **Create tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z: summary"`
7. **Push**: `git push && git push origin vX.Y.Z`
8. **Wait for CI**: GitHub Actions creates release automatically
9. **Verify release** on GitHub Releases page
10. **Announce** (optional): Update README badges, notify users

### Hotfix Process

For critical bugs in production:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull
git checkout -b hotfix/v5.4.1

# 2. Fix bug and test
# ... make changes ...
pytest tests/ -v

# 3. Update version and changelog
# Edit pyproject.toml: version = "5.4.1"
# Update CHANGELOG.md

# 4. Commit
git commit -m "fix: critical bug in Phase 7 SSL generation"

# 5. Merge to main
git checkout main
git merge hotfix/v5.4.1

# 6. Tag and push
git tag -a v5.4.1 -m "Release v5.4.1: Hotfix for SSL generation"
git push && git push origin v5.4.1

# 7. Merge to develop
git checkout develop
git merge main
git push
```

---

## Local Development

### Initial Setup

```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/misp-install.git
cd misp-install

# 2. Install uv (modern package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# 4. Install all dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-gui.txt
uv pip install -e ".[dev]"

# 5. Verify installation
pytest tests/ -v
uvx ruff check .
python3 misp-install.py --help
```

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes
# Edit files...

# 3. Test changes
pytest tests/ -v                    # Run tests
pytest tests/ --cov=.               # Check coverage
uvx ruff check .                    # Lint code
uvx ruff format .                   # Format code
python3 -m py_compile script.py     # Check syntax

# 4. Commit with conventional commits
git add .
git commit -m "feat: add new feature X"
# Types: feat, fix, docs, test, refactor, chore

# 5. Push and create PR
git push origin feature/your-feature
# Go to GitHub and create pull request
```

### Pre-commit Checks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Run tests
pytest tests/ -v || {
    echo "❌ Tests failed"
    exit 1
}

# Run linting
uvx ruff check . || {
    echo "❌ Linting failed"
    exit 1
}

# Run formatting check
uvx ruff format --check . || {
    echo "❌ Formatting check failed"
    echo "Run: uvx ruff format ."
    exit 1
}

echo "✅ All pre-commit checks passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Troubleshooting

### CI Failures

#### "Python syntax error"
```
Error: invalid syntax (script.py, line 123)
```
**Fix**: Run `python3 -m py_compile script.py` locally to identify issue

#### "Import error in tests"
```
ModuleNotFoundError: No module named 'lib.example'
```
**Fix**: Add `sys.path.insert(0, str(Path(__file__).parent.parent))` to test file

#### "Ruff linting failures"
```
E501 Line too long (120 > 100)
```
**Fix**: Run `uvx ruff format .` to auto-format, or adjust line length in pyproject.toml

#### "Coverage too low"
```
TOTAL coverage: 45% (target: 70%)
```
**Fix**: Add more tests for uncovered lines. Run `pytest --cov=. --cov-report=html` to see coverage report

### Local Test Failures

#### "Fixture not found"
```
fixture 'temp_dir' not found
```
**Fix**: Ensure `conftest.py` is in `tests/` directory and properly imported

#### "Tests pass locally but fail in CI"
- Check Python version (CI tests 3.8-3.12, you might use 3.11)
- Check for hardcoded paths (use `temp_dir` fixture)
- Check for environment-specific behavior

### Dependabot Issues

#### "Dependabot PR creates conflicts"
**Fix**: Rebase Dependabot PR:
```bash
gh pr checkout 123  # Dependabot PR number
git rebase main
git push --force-with-lease
```

#### "Dependabot updates break tests"
**Fix**: Close PR and add to ignore list in `.github/dependabot.yml`:
```yaml
ignore:
  - dependency-name: "problematic-package"
    update-types: ["version-update:semver-major"]
```

---

## Best Practices

### Code Quality

1. **Always run tests before committing**
   ```bash
   pytest tests/ -v
   ```

2. **Use conventional commits**
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `test:` - Tests
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance

3. **Keep commits atomic** - One logical change per commit

4. **Write descriptive commit messages**
   ```
   Good: "feat: add automatic feed enablement to configure-misp-ready.py"
   Bad: "fixed stuff"
   ```

### Testing

1. **Test coverage goal**: 70%+ for core libraries
2. **One test per concept** - Don't combine unrelated tests
3. **Use fixtures** - Avoid duplicating setup code
4. **Mock external dependencies** - No Docker, network, or filesystem in unit tests

### Security

1. **Never commit passwords or API keys**
2. **Use environment variables** for secrets
3. **Review Dependabot security alerts** promptly
4. **Run `bandit` before major releases**

---

## Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **pytest Documentation**: https://docs.pytest.org/
- **uv Documentation**: https://docs.astral.sh/uv/
- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **Conventional Commits**: https://www.conventionalcommits.org/

---

**Last Updated**: October 2025
**Maintained by**: tKQB Enterprises
**CI/CD Stack**: GitHub Actions + uv + pytest + Ruff
