# Git Branching Quick Reference

**TL;DR**: Use `main` for production, `develop` for integration, short-lived `feature/*` and `fix/*` branches for changes.

---

## Branch Summary

| Branch | Purpose | Protected | Lifespan | Deployed To |
|--------|---------|-----------|----------|-------------|
| `main` | Production releases | 🔒 Yes | Permanent | Production (GitHub Releases) |
| `develop` | Integration, next release | ⚠️ Partial | Permanent | Staging/QA (optional) |
| `feature/*` | New features | No | Days-weeks | Dev environment |
| `fix/*` | Bug fixes | No | Hours-days | Dev environment |
| `hotfix/*` | Emergency fixes | No | Hours | Production (ASAP) |
| `release/*` | Release prep | No | Days | None (temp) |

---

## Common Tasks

### Starting New Feature

```bash
git checkout develop
git pull
git checkout -b feature/my-feature
# ... work ...
git push origin feature/my-feature
# Create PR to develop on GitHub
```

### Fixing Bug

```bash
git checkout develop
git pull
git checkout -b fix/bug-description
# ... fix ...
git push origin fix/bug-description
# Create PR to develop on GitHub
```

### Creating Release

```bash
# On develop: update version in pyproject.toml and CHANGELOG.md
git add pyproject.toml docs/testing_and_updates/CHANGELOG.md
git commit -m "chore: prepare release v5.5.0"
git push

# Create PR: develop -> main on GitHub
# After merge:
git checkout main
git pull
git tag -a v5.5.0 -m "Release v5.5.0: feature summary"
git push origin v5.5.0
```

### Emergency Hotfix

```bash
git checkout main
git pull
git checkout -b hotfix/v5.4.1-critical-bug
# ... fix + test ...
# Update version: "5.4.0" -> "5.4.1" in pyproject.toml
git push origin hotfix/v5.4.1-critical-bug
# Create PR to main
# After merge:
git checkout main
git pull
git tag -a v5.4.1 -m "Hotfix v5.4.1: critical bug fix"
git push origin v5.4.1
# Merge to develop:
git checkout develop
git merge main
git push
```

---

## Conventional Commits

Use these prefixes for commit messages:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding tests
- `refactor:` - Code change (no feature/fix)
- `chore:` - Maintenance (version bump, deps)
- `perf:` - Performance improvement
- `ci:` - CI/CD changes

**Example**:
```
feat: add Let's Encrypt certificate support

- Integrate certbot for automatic SSL
- Add --cert-mode flag
- Update Phase 7 SSL generation

Closes #42
```

---

## Branch Protection

### `main` branch:
- ✅ Requires PR approval (1+ reviewers)
- ✅ Requires CI to pass (syntax, tests, lint)
- 🚫 No force pushes
- 🚫 No direct commits

### `develop` branch:
- ✅ Requires CI to pass
- ⚠️ Optional PR reviews
- 🚫 No force pushes

---

## CI/CD Triggers

- **Push to `main` or `develop`** → Full CI runs (6 jobs)
- **PR to `main` or `develop`** → Full CI runs (6 jobs)
- **Tag `v*.*.*`** → Release automation (creates GitHub Release)

---

## Rules

1. ✅ **Never commit directly to `main` or `develop`**
2. ✅ **All changes via pull request**
3. ✅ **CI must pass before merge**
4. ✅ **Delete branches after merge**
5. ✅ **Feature branches live < 2 weeks**
6. ✅ **Tag `main` for all releases**

---

## Questions?

See full documentation: **[docs/BRANCHING_STRATEGY.md](../BRANCHING_STRATEGY.md)**

---

**Strategy**: Modified GitHub Flow
**Last Updated**: October 2025
