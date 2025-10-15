# README Badges for MISP Installation Project

Add these badges to the top of your README.md to show project status and quality metrics.

## Recommended Badges

### CI/CD Status
```markdown
[![CI/CD Pipeline](https://github.com/yourusername/misp-install/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/misp-install/actions/workflows/ci.yml)
[![Release](https://github.com/yourusername/misp-install/actions/workflows/release.yml/badge.svg)](https://github.com/yourusername/misp-install/actions/workflows/release.yml)
```

### Code Quality
```markdown
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### Project Info
```markdown
[![Version](https://img.shields.io/badge/version-5.4.0-green.svg)](https://github.com/yourusername/misp-install/releases)
[![MISP](https://img.shields.io/badge/MISP-2.5+-red.svg)](https://www.misp-project.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
```

### NERC CIP Specific
```markdown
[![NERC CIP](https://img.shields.io/badge/NERC%20CIP-compliant-green.svg)](docs/NERC_CIP_CONFIGURATION.md)
[![ICS/SCADA](https://img.shields.io/badge/ICS%2FSCADA-ready-orange.svg)](docs/NERC_CIP_CONFIGURATION.md)
```

### Coverage (if using Codecov)
```markdown
[![codecov](https://codecov.io/gh/yourusername/misp-install/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/misp-install)
```

### Documentation
```markdown
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/yourusername/misp-install/tree/main/docs)
[![Scripts](https://img.shields.io/badge/scripts-documented-blue.svg)](SCRIPTS.md)
```

### Community
```markdown
[![Issues](https://img.shields.io/github/issues/yourusername/misp-install.svg)](https://github.com/yourusername/misp-install/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/yourusername/misp-install.svg)](https://github.com/yourusername/misp-install/pulls)
[![Contributors](https://img.shields.io/github/contributors/yourusername/misp-install.svg)](https://github.com/yourusername/misp-install/graphs/contributors)
```

## Complete Badge Section (Copy/Paste to README.md)

```markdown
# MISP Installation Automation

[![CI/CD Pipeline](https://github.com/yourusername/misp-install/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/misp-install/actions/workflows/ci.yml)
[![Release](https://github.com/yourusername/misp-install/actions/workflows/release.yml/badge.svg)](https://github.com/yourusername/misp-install/actions/workflows/release.yml)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Version](https://img.shields.io/badge/version-5.4.0-green.svg)](https://github.com/yourusername/misp-install/releases)
[![MISP](https://img.shields.io/badge/MISP-2.5+-red.svg)](https://www.misp-project.org/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![NERC CIP](https://img.shields.io/badge/NERC%20CIP-compliant-green.svg)](docs/NERC_CIP_CONFIGURATION.md)

> **Professional-grade MISP (Malware Information Sharing Platform) Docker installation automation with NERC CIP compliance features**
```

## Dynamic Badges (Automatically Update)

These badges automatically update based on repository state:

### Test Count Badge
Create a workflow that counts tests and creates a badge:
```yaml
# .github/workflows/test-count.yml
- name: Count tests
  run: |
    TEST_COUNT=$(pytest --collect-only -q | grep "test session starts" -A 1 | tail -n 1 | awk '{print $1}')
    echo "TEST_COUNT=$TEST_COUNT" >> $GITHUB_ENV
```

### Last Commit Badge
```markdown
[![Last Commit](https://img.shields.io/github/last-commit/yourusername/misp-install.svg)](https://github.com/yourusername/misp-install/commits/main)
```

### Stars and Forks
```markdown
[![GitHub stars](https://img.shields.io/github/stars/yourusername/misp-install.svg?style=social&label=Star)](https://github.com/yourusername/misp-install)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/misp-install.svg?style=social&label=Fork)](https://github.com/yourusername/misp-install/fork)
```

## Custom Badges

Create custom badges at: https://shields.io/

Example:
```
https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>
```

Examples for this project:
```markdown
![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Tested](https://img.shields.io/badge/tested-32%20tests-success)
![v5.4](https://img.shields.io/badge/release-v5.4-blue)
```

## Updating Badges

After pushing CI/CD infrastructure:

1. Replace `yourusername` with your GitHub username in all badge URLs
2. Update version numbers in static badges when releasing new versions
3. Add badges to top of README.md below title
4. Commit and push - badges will automatically start working

## Badge Best Practices

1. **Don't overload** - 6-8 badges maximum
2. **Most important first** - CI status, version, license
3. **Group related badges** - CI/CD together, metadata together
4. **Update regularly** - Keep version badges current
5. **Link to details** - Each badge should link to relevant page

---

**Note**: Replace `yourusername` with your actual GitHub username before committing!
