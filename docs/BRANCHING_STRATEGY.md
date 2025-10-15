# Git Branching Strategy

**Project**: MISP Installation Automation
**Strategy**: Modified GitHub Flow with develop branch
**Created**: October 2025
**Status**: Production Ready

---

## Table of Contents

- [Overview](#overview)
- [Branch Structure](#branch-structure)
- [Workflows](#workflows)
- [Branch Protection Rules](#branch-protection-rules)
- [Examples](#examples)
- [FAQ](#faq)

---

## Overview

This project uses **Modified GitHub Flow** - a simple, scalable branching strategy that balances speed with stability.

### Why This Strategy?

✅ **Simple** - Easy to understand and follow
✅ **Fast** - Changes reach production quickly
✅ **Safe** - Protected branches and automated testing
✅ **Scalable** - Works for 1-100 developers
✅ **Audit-friendly** - Clear history for NERC CIP compliance

### Key Principles

1. **`main` is always deployable** - Production-ready code only
2. **`develop` is integration point** - Latest features, always passing tests
3. **Feature branches are short-lived** - Days to weeks, not months
4. **All changes via pull request** - No direct commits to main/develop
5. **CI/CD tests everything** - Automated testing on every PR

---

## Branch Structure

### Long-Lived Branches (Permanent)

#### `main` - Production Releases
**Purpose**: Stable, production-ready code. Always deployable.

**Rules**:
- 🔒 **Protected** - Cannot commit directly
- ✅ Requires PR approval (1+ reviewers)
- ✅ Requires CI to pass (all tests green)
- 🚫 No force pushes
- 🏷️ Tagged for releases (v5.4.0, v5.4.1, v5.5.0)

**What's here**:
- Latest stable release
- Bug fixes from hotfixes
- Features merged from develop

**Deployed to**: Production (user installations via GitHub Releases)

---

#### `develop` - Integration Branch
**Purpose**: Latest features, integration point, next release preparation.

**Rules**:
- 🔓 Less strict than main (but still protected)
- ✅ Requires CI to pass
- ⚠️ May have minor bugs (fixed before release)
- 🔄 Merged to main when ready for release

**What's here**:
- Completed features (merged from feature/*)
- Bug fixes (merged from fix/*)
- Work in progress (all tests passing)

**Deployed to**: Staging/QA environment (optional)

---

### Temporary Branches (Short-Lived)

#### `feature/*` - New Features
**Format**: `feature/descriptive-name`
**Lifespan**: Days to weeks
**Branched from**: `develop`
**Merged into**: `develop`
**Deleted**: After merge

**Examples**:
```
feature/ssl-certificate-support
feature/lets-encrypt-integration
feature/gui-installer-backend
feature/azure-ad-authentication
feature/feed-auto-sync
```

**When to use**: Adding new functionality, enhancements

**Workflow**:
```bash
git checkout develop
git pull
git checkout -b feature/my-feature
# ... work, commit ...
git push origin feature/my-feature
# Open PR to develop
# CI runs, review, merge
# Delete branch
```

---

#### `fix/*` - Bug Fixes
**Format**: `fix/descriptive-bug-name`
**Lifespan**: Hours to days
**Branched from**: `develop`
**Merged into**: `develop`
**Deleted**: After merge

**Examples**:
```
fix/phase7-ssl-generation
fix/password-validation-regex
fix/docker-permission-denied
fix/logging-directory-creation
fix/feed-enablement-timeout
```

**When to use**: Fixing bugs in develop branch

**Workflow**:
```bash
git checkout develop
git pull
git checkout -b fix/bug-description
# ... fix, test, commit ...
git push origin fix/bug-description
# Open PR to develop
# CI runs, review, merge
# Delete branch
```

---

#### `hotfix/*` - Critical Production Fixes
**Format**: `hotfix/v5.4.1-descriptive-name`
**Lifespan**: Hours (urgent)
**Branched from**: `main` (NOT develop!)
**Merged into**: `main` AND `develop`
**Deleted**: After both merges

**Examples**:
```
hotfix/v5.4.1-critical-ssl-bug
hotfix/v5.4.2-password-bypass
hotfix/v5.4.3-docker-crash
```

**When to use**: Critical bug in production that can't wait for next release

**Workflow**:
```bash
# 1. Branch from main
git checkout main
git pull
git checkout -b hotfix/v5.4.1-critical-bug

# 2. Fix bug, test thoroughly
# ... fix, test, commit ...

# 3. Update version (pyproject.toml)
# Change version: "5.4.0" -> "5.4.1"

# 4. Push and create PR to main
git push origin hotfix/v5.4.1-critical-bug
# Open PR to main, get emergency review

# 5. After merge to main, tag immediately
git checkout main
git pull
git tag -a v5.4.1 -m "Hotfix v5.4.1: Critical SSL bug"
git push origin v5.4.1
# GitHub Actions creates release

# 6. Merge to develop to keep in sync
git checkout develop
git merge main
git push

# 7. Delete hotfix branch
git branch -d hotfix/v5.4.1-critical-bug
git push origin --delete hotfix/v5.4.1-critical-bug
```

---

#### `release/*` - Release Preparation (Optional)
**Format**: `release/v5.5.0`
**Lifespan**: Days (during release stabilization)
**Branched from**: `develop`
**Merged into**: `main`, then back to `develop`
**Deleted**: After release complete

**When to use**:
- When you need a stabilization period before release
- For updating version numbers, changelog
- For release-specific bug fixes only (NO new features)

**Workflow**:
```bash
# 1. Create release branch from develop
git checkout develop
git pull
git checkout -b release/v5.5.0

# 2. Update version and changelog
# Edit pyproject.toml: version = "5.5.0"
# Update docs/testing_and_updates/CHANGELOG.md
git commit -m "chore: prepare release v5.5.0"

# 3. Fix any release-specific bugs (no features!)
# ... bug fixes only ...

# 4. Create PR to main
git push origin release/v5.5.0
# Open PR to main
# Thorough review and testing

# 5. After merge to main, tag release
git checkout main
git pull
git tag -a v5.5.0 -m "Release v5.5.0: Feature summary"
git push origin v5.5.0
# GitHub Actions creates release

# 6. Merge release changes back to develop
git checkout develop
git merge main
git push

# 7. Delete release branch
git branch -d release/v5.5.0
git push origin --delete release/v5.5.0
```

---

## Workflows

### Daily Development Workflow

```bash
# 1. Start your day - update develop
git checkout develop
git pull

# 2. Create feature branch
git checkout -b feature/my-new-feature

# 3. Work on feature
# ... edit files ...
git add .
git commit -m "feat: add my new feature"

# 4. Keep feature branch updated (if working for multiple days)
git checkout develop
git pull
git checkout feature/my-new-feature
git rebase develop  # or git merge develop

# 5. Push feature branch
git push origin feature/my-new-feature

# 6. Open pull request on GitHub
# - Go to GitHub repository
# - Click "New Pull Request"
# - Base: develop, Compare: feature/my-new-feature
# - Fill in PR template
# - Submit

# 7. Wait for CI and review
# - GitHub Actions runs automatically
# - Reviewer(s) approve
# - Merge pull request

# 8. Clean up
git checkout develop
git pull  # Gets your merged changes
git branch -d feature/my-new-feature  # Delete local branch
git push origin --delete feature/my-new-feature  # Delete remote branch
```

---

### Release Workflow (v5.5.0 Example)

```bash
# Option A: Direct release (no stabilization needed)
# ================================================

# 1. Create PR from develop to main
git checkout develop
git pull

# 2. Update version and changelog on develop
# Edit pyproject.toml: version = "5.5.0"
# Edit CHANGELOG.md: Add release notes
git add pyproject.toml docs/testing_and_updates/CHANGELOG.md
git commit -m "chore: prepare release v5.5.0"
git push

# 3. Create PR: develop -> main
# On GitHub, create PR from develop to main
# Thorough review, all tests pass

# 4. After merge, tag main
git checkout main
git pull
git tag -a v5.5.0 -m "Release v5.5.0: SSL certificates, feed improvements"
git push origin v5.5.0

# 5. Merge main back to develop (to get version update)
git checkout develop
git merge main
git push

# Option B: Release branch (stabilization needed)
# ================================================

# Use release/* branch workflow described above
```

---

### Hotfix Workflow (v5.4.1 Example)

```bash
# 1. Critical bug discovered in production
# User reports: SSL generation fails on Phase 7

# 2. Create hotfix branch from main (NOT develop!)
git checkout main
git pull
git checkout -b hotfix/v5.4.1-ssl-generation

# 3. Fix bug
# Edit scripts/configure-misp-ready.py
git add scripts/configure-misp-ready.py
git commit -m "fix: SSL generation directory creation"

# 4. Test thoroughly
pytest tests/ -v
python3 scripts/configure-misp-ready.py --dry-run

# 5. Update version
# Edit pyproject.toml: "5.4.0" -> "5.4.1"
git add pyproject.toml
git commit -m "chore: bump version to v5.4.1"

# 6. Create emergency PR to main
git push origin hotfix/v5.4.1-ssl-generation
# Create PR on GitHub: hotfix/* -> main
# Request urgent review

# 7. After merge, tag immediately
git checkout main
git pull
git tag -a v5.4.1 -m "Hotfix v5.4.1: SSL generation fix"
git push origin v5.4.1
# GitHub Actions creates emergency release

# 8. Merge to develop
git checkout develop
git merge main
git push

# 9. Clean up
git branch -d hotfix/v5.4.1-ssl-generation
git push origin --delete hotfix/v5.4.1-ssl-generation

# 10. Notify users
# Post on GitHub release notes
# Update documentation if needed
```

---

## Branch Protection Rules

### `main` Branch Protection

Configure in GitHub: Settings > Branches > Add rule > `main`

**Required Settings**:
- ✅ Require a pull request before merging
  - ✅ Require approvals: 1+ reviewers
  - ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Status checks required:
    - `validate` (Python syntax & imports)
    - `lint` (Code quality)
    - `test` (Unit tests)
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings (include administrators)
- 🚫 Restrict who can push to matching branches (optional - only release managers)

**Allow**:
- ✅ Allow force pushes: NO
- ✅ Allow deletions: NO

---

### `develop` Branch Protection

Configure in GitHub: Settings > Branches > Add rule > `develop`

**Required Settings**:
- ✅ Require status checks to pass before merging
  - Status checks required:
    - `validate` (Python syntax & imports)
    - `test` (Unit tests)
- ⚠️ Optional: Require pull request reviews (less strict than main)

**Allow**:
- ✅ Allow force pushes: NO
- ✅ Allow deletions: NO

---

## Examples

### Example 1: Adding New Feature

**Scenario**: Add Let's Encrypt certificate support (new feature)

```bash
# 1. Create feature branch from develop
git checkout develop
git pull
git checkout -b feature/lets-encrypt-support

# 2. Implement feature
# - Add certbot integration
# - Update Phase 7 in misp-install.py
# - Add tests in tests/test_ssl_certificates.py
# - Update documentation

# 3. Commit with conventional commit format
git add .
git commit -m "feat: add Let's Encrypt certificate support

- Integrate certbot for automatic certificate generation
- Add --cert-mode flag (self-signed|letsencrypt|custom)
- Update Phase 7 to support multiple certificate sources
- Add 15 new tests for certificate validation

Closes #42"

# 4. Push and create PR
git push origin feature/lets-encrypt-support
# Open PR to develop on GitHub
# CI runs all tests
# Request review

# 5. Address review feedback (if any)
# ... make changes ...
git add .
git commit -m "refactor: improve certificate validation error messages"
git push

# 6. After approval and CI pass, merge via GitHub
# Click "Squash and merge" or "Merge pull request"

# 7. Clean up
git checkout develop
git pull
git branch -d feature/lets-encrypt-support
```

---

### Example 2: Fixing Bug

**Scenario**: Password validation allows weak passwords (bug fix)

```bash
# 1. Create fix branch from develop
git checkout develop
git pull
git checkout -b fix/password-validation-weak-passwords

# 2. Fix bug
# - Update lib/misp_password.py
# - Add test cases in tests/test_misp_password.py

# 3. Commit
git add lib/misp_password.py tests/test_misp_password.py
git commit -m "fix: strengthen password validation regex

- Fix regex to require at least one special character
- Add test cases for weak password detection
- Update error messages for clarity

Fixes #89"

# 4. Test
pytest tests/test_misp_password.py -v

# 5. Push and create PR
git push origin fix/password-validation-weak-passwords
# Open PR to develop

# 6. After merge, clean up
git checkout develop
git pull
git branch -d fix/password-validation-weak-passwords
```

---

### Example 3: Emergency Hotfix

**Scenario**: Critical bug - Docker fails to start on Ubuntu 24.04 (production issue)

```bash
# 1. Create hotfix from main (NOT develop!)
git checkout main
git pull
git checkout -b hotfix/v5.4.2-docker-ubuntu-24.04

# 2. Fix bug urgently
# - Update Docker installation logic
# - Test on Ubuntu 24.04

# 3. Commit
git add misp-install.py
git commit -m "fix: Docker installation fails on Ubuntu 24.04

- Update Docker GPG key retrieval for Ubuntu 24.04
- Add version detection for Ubuntu 24.04
- Test on clean Ubuntu 24.04 installation

CRITICAL: Affects all Ubuntu 24.04 users"

# 4. Update version
# pyproject.toml: "5.4.1" -> "5.4.2"
git add pyproject.toml
git commit -m "chore: bump version to v5.4.2"

# 5. Emergency PR to main
git push origin hotfix/v5.4.2-docker-ubuntu-24.04
# Create PR, mark as urgent
# Get emergency review from maintainer

# 6. After merge, tag immediately
git checkout main
git pull
git tag -a v5.4.2 -m "Hotfix v5.4.2: Docker installation on Ubuntu 24.04"
git push origin v5.4.2
# GitHub Actions creates release within minutes

# 7. Merge to develop
git checkout develop
git merge main
git push

# 8. Notify users (GitHub release, social media, etc.)
```

---

## FAQ

### Q: Why develop branch? Why not just main?

**A**: For this project, `develop` allows you to:
- Batch multiple features for a release (v5.5.0 with 3 features)
- Test feature interactions before release
- Keep main stable while development continues

**Alternative**: If you release every feature immediately, you can skip `develop` and use just `main`.

---

### Q: When do I use release/* branches?

**A**: Optional. Use when you need:
- Release stabilization period (1-2 weeks)
- Final bug fixes before release
- Version number updates without blocking develop

**Skip if**: You can prepare releases directly on develop.

---

### Q: Can I deploy develop branch to production?

**A**: 🚫 **NO**. Only `main` branch tagged releases go to production.

**Reasoning**: develop may have minor bugs, incomplete features, or breaking changes.

---

### Q: What if I accidentally commit to main directly?

**A**: If branch protection is enabled (recommended), Git will reject the push.

**If it somehow got through**:
```bash
# Create a branch from the bad commit
git checkout main
git checkout -b fix/accidental-commit

# Reset main to previous commit
git checkout main
git reset --hard HEAD~1
git push --force  # (if allowed)

# Create proper PR from fix/accidental-commit
```

---

### Q: How long should feature branches live?

**A**: **Days to weeks, not months**.

**Guidelines**:
- Simple fix: Hours to 1 day
- Small feature: 2-7 days
- Medium feature: 1-2 weeks
- Large feature: 2-4 weeks (break into smaller PRs if possible)

**If > 4 weeks**: Feature is too large, split into smaller PRs.

---

### Q: Should I rebase or merge when updating feature branch?

**A**: **Personal preference**, both work:

**Rebase** (cleaner history):
```bash
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
```

**Merge** (safer, preserves history):
```bash
git checkout feature/my-feature
git merge develop
```

**Recommendation**: Use rebase for feature branches, merge for develop/main.

---

### Q: What about testing/staging/production branches?

**A**: 🚫 **Don't use branches for environments**.

**Instead**: Deploy any branch to any environment:
- `develop` → Deploy to staging environment
- `main` tags → Deploy to production environment
- `feature/*` → Deploy to dev environment (for testing)

**Environments are infrastructure, not Git branches**.

---

### Q: How do I handle NERC CIP compliance with this strategy?

**A**: This strategy provides excellent audit trail:

✅ **All changes via PR** - Clear approval chain
✅ **Protected main branch** - No unauthorized changes
✅ **CI/CD logs** - Automated testing evidence
✅ **Git history** - Complete change log
✅ **Tagged releases** - Version control for audits

For CIP-011 (BCSI), ensure:
- PR reviews logged
- Access controls on GitHub repo
- MFA enabled for all contributors

---

### Q: Can I customize this strategy?

**A**: Yes! Adapt to your needs:

**Simpler** (for solo dev):
- Skip `develop`, use just `main`
- Skip `release/*`, version directly on `main`

**More complex** (for large team):
- Add `staging` branch (between develop and main)
- Require 2+ PR approvals
- Add more CI checks

**Key**: Keep it as simple as possible while meeting your needs.

---

## Summary

### Branch Hierarchy

```
main (production, tagged releases)
  ↑
  PR (after thorough testing)
  ↑
develop (integration, latest features)
  ↑
  PR (feature complete)
  ↑
feature/* or fix/* (temporary, short-lived)
```

### Key Rules

1. ✅ **Never commit directly to main or develop**
2. ✅ **All changes via pull request**
3. ✅ **CI must pass before merge**
4. ✅ **Delete branches after merge**
5. ✅ **Tag main for releases** (v5.4.0, v5.4.1)
6. ✅ **Use conventional commits** (feat:, fix:, docs:, etc.)

### Quick Reference

| Task | Branch | Merge to | Lifespan |
|------|--------|----------|----------|
| New feature | `feature/*` | develop | Days-weeks |
| Bug fix | `fix/*` | develop | Hours-days |
| Critical fix | `hotfix/*` | main + develop | Hours |
| Release prep | `release/*` | main, then develop | Days |
| Stable code | `main` | N/A | Permanent |
| Latest features | `develop` | N/A | Permanent |

---

**Questions?**

Open an issue using the "Feature Request" template if you'd like to propose changes to this branching strategy.

---

**Last Updated**: October 2025
**Strategy**: Modified GitHub Flow
**Maintained by**: tKQB Enterprises
