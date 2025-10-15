## Pull Request Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] CI/CD improvement

## Related Issue

<!-- Link to related issue(s) -->

Fixes #(issue number)
Relates to #(issue number)

## Changes Made

<!-- Describe the changes in detail -->

-
-
-

## Testing Performed

<!-- Describe the testing you've done -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Tested on clean Ubuntu installation
- [ ] Tested with Docker MISP instance

### Test Environment

- **OS**: Ubuntu 22.04 / 24.04 / other
- **Python Version**: 3.x.x
- **Docker Version**:
- **Installation Mode**: Interactive / Non-interactive / GUI

### Test Results

<!-- Paste relevant test output or describe results -->

```bash
# Example: pytest output, script execution results
```

## Checklist

<!-- Mark completed items with an "x" -->

### Code Quality

- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors
- [ ] I have run `pytest tests/` and all tests pass
- [ ] I have run `uvx ruff check .` and fixed any linting issues

### Documentation

- [ ] I have updated the documentation (README.md, SCRIPTS.md, etc.)
- [ ] I have updated CLAUDE.md with implementation details (if applicable)
- [ ] I have added/updated docstrings for new/modified functions
- [ ] I have updated the TODO.md file (if applicable)

### Testing

- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested on a clean system (no previous MISP installation)
- [ ] I have verified backward compatibility (if applicable)

### NERC CIP Compliance (if applicable)

- [ ] Changes maintain NERC CIP compliance features
- [ ] Updated docs/NERC_CIP_CONFIGURATION.md (if applicable)
- [ ] Tested with NERC CIP configuration scripts
- [ ] No sensitive data (passwords, API keys) in code or commits

### Security

- [ ] No passwords or API keys in code
- [ ] Sensitive operations use proper authentication
- [ ] Input validation added for user-provided data
- [ ] Logging does not expose sensitive information

### Git Best Practices

- [ ] Commits are signed (if required)
- [ ] Commit messages are clear and descriptive
- [ ] No merge commits from main (rebased if needed)
- [ ] Branch is up-to-date with main

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them and the migration path -->

**None** / **Yes** (describe below)

## Additional Notes

<!-- Any additional information reviewers should know -->

## Screenshots (if applicable)

<!-- Add screenshots for UI changes or visual output changes -->

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance slightly degraded (explain why acceptable)

## Deployment Notes

<!-- Special considerations for deployment -->

- [ ] No special deployment steps required
- [ ] Requires manual intervention (describe below)
- [ ] Requires configuration changes (describe below)

---

## For Reviewers

<!-- Guidance for code reviewers -->

**Key Areas to Review**:
-
-
-

**Testing Instructions**:
1.
2.
3.

---

**By submitting this pull request, I confirm that**:

- [ ] My contribution is made under the terms of the project's license
- [ ] I have the right to submit this code
- [ ] I understand this code may be used in production NERC CIP environments
