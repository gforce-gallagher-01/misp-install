# Branch Protection Setup Guide

**Purpose**: Configure GitHub branch protection rules for `main` and `develop` branches
**Time Required**: 10-15 minutes
**Skill Level**: Intermediate

---

## Table of Contents

- [Why Branch Protection?](#why-branch-protection)
- [Method 1: Automated (GitHub CLI)](#method-1-automated-github-cli)
- [Method 2: Manual (Web Interface)](#method-2-manual-web-interface)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Why Branch Protection?

Branch protection prevents common mistakes:

❌ **Without Protection**:
- Anyone can commit directly to `main`
- Code can be pushed without tests passing
- No code review required
- Branches can be deleted accidentally
- Force pushes can rewrite history

✅ **With Protection**:
- All changes via pull request
- CI must pass before merge
- Code review required (main branch)
- Branches can't be deleted
- History is preserved

**Result**: Higher code quality, fewer bugs, clear audit trail

---

## Method 1: Automated (GitHub CLI)

### Prerequisites

1. **Install GitHub CLI**:
   ```bash
   # Ubuntu/Debian
   sudo apt install gh

   # Or download from: https://cli.github.com/
   ```

2. **Authenticate**:
   ```bash
   gh auth login
   # Follow prompts to authenticate
   ```

3. **Push branches to GitHub** (if not already done):
   ```bash
   git checkout main
   git push -u origin main

   git checkout develop
   git push -u origin develop
   ```

### Run Setup Script

```bash
# From project root
./setup-branch-protection.sh
```

**Script will**:
- ✓ Check if GitHub CLI is installed and authenticated
- ✓ Detect repository automatically
- ✓ Configure `main` branch protection (strict)
- ✓ Configure `develop` branch protection (moderate)
- ✓ Verify settings

**Duration**: ~30 seconds

**If script fails**: Use Method 2 (Manual Setup) below

---

## Method 2: Manual (Web Interface)

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab (top right)
3. Click **Branches** (left sidebar)
4. Click **Add branch protection rule**

---

### Step 2: Configure `main` Branch Protection

#### 2.1 Branch Name Pattern

```
Branch name pattern: main
```

#### 2.2 Protect Matching Branches

Check these boxes:

**Require a pull request before merging**:
- ✅ Check this box
- ✅ Require approvals: **1** (set to 1)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners: ❌ Leave unchecked (unless you have CODEOWNERS file)
- ✅ Require approval of the most recent reviewable push

**Require status checks to pass before merging**:
- ✅ Check this box
- ✅ Require branches to be up to date before merging
- In search box, type and add:
  - `validate` (Syntax & import validation)
  - `test` (Unit tests)
  - `lint` (Code quality) - optional
  - `security` (Security scan) - optional

**Require conversation resolution before merging**:
- ✅ Check this box

**Require signed commits**:
- ❌ Leave unchecked (unless required by your org)

**Require linear history**:
- ❌ Leave unchecked (allows merge commits)

**Require deployments to succeed before merging**:
- ❌ Leave unchecked

**Lock branch**:
- ❌ Leave unchecked

**Do not allow bypassing the above settings**:
- ✅ Check this box (even admins must follow rules)

**Restrict who can push to matching branches**:
- ❌ Leave unchecked (unless you want to limit to specific users/teams)

**Allow force pushes**:
- ❌ **Disabled** (keep this off!)

**Allow deletions**:
- ❌ **Disabled** (keep this off!)

#### 2.3 Save

Click **Create** button at bottom

---

### Step 3: Configure `develop` Branch Protection

Click **Add branch protection rule** again

#### 3.1 Branch Name Pattern

```
Branch name pattern: develop
```

#### 3.2 Protect Matching Branches

Check these boxes:

**Require a pull request before merging**:
- ❌ **Leave unchecked** (allows direct commits to develop for faster iteration)
- **Alternative**: Check this if you want PRs even for develop (slower but safer)

**Require status checks to pass before merging**:
- ✅ Check this box
- ✅ Require branches to be up to date before merging
- In search box, type and add:
  - `validate` (Syntax & import validation)
  - `test` (Unit tests)

**Require conversation resolution before merging**:
- ❌ Leave unchecked (less strict than main)

**Do not allow bypassing the above settings**:
- ❌ Leave unchecked (develop is less strict)

**Allow force pushes**:
- ❌ **Disabled** (keep this off!)

**Allow deletions**:
- ❌ **Disabled** (keep this off!)

#### 3.3 Save

Click **Create** button at bottom

---

## Verification

### Check Protection Status

1. Go to repository **Settings > Branches**
2. You should see 2 branch protection rules:
   - `main` - Protected
   - `develop` - Protected

### Test Protection (Recommended)

```bash
# Try to force push to main (should fail)
git checkout main
git push --force
# Expected: remote: error: GH006: Protected branch update failed

# Try to commit directly to main (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test: direct commit to main"
git push
# Expected: remote: error: Required status check "validate" is expected

# Success! Protection is working.
```

### Visual Indicators

Protected branches show a shield icon 🛡️ in GitHub interface

---

## Verification Checklist

After setup, verify these work correctly:

### ✅ `main` Branch

- [ ] Cannot commit directly to main
- [ ] Pull requests require 1 approval
- [ ] CI checks must pass (validate, test)
- [ ] Stale reviews dismissed on new commits
- [ ] Conversations must be resolved
- [ ] Force pushes blocked
- [ ] Branch deletion blocked

### ✅ `develop` Branch

- [ ] CI checks must pass (validate, test)
- [ ] Force pushes blocked
- [ ] Branch deletion blocked
- [ ] Direct commits allowed (or PR required, based on your choice)

### Test Workflow

```bash
# 1. Create feature branch
git checkout develop
git pull
git checkout -b feature/test-protection

# 2. Make change
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "test: branch protection"
git push origin feature/test-protection

# 3. Create PR on GitHub
# - Base: develop
# - Compare: feature/test-protection
# - Verify CI runs automatically

# 4. Verify protection
# - If PR to main: Should require approval
# - If PR to develop: Should require CI to pass

# 5. Merge and verify
# - Click "Merge pull request"
# - Verify merge succeeded
# - Verify branch can be deleted after merge
```

---

## Troubleshooting

### Issue 1: "Required status check is expected"

**Error**:
```
remote: error: Required status check "validate" is expected
```

**Cause**: CI workflow hasn't run yet, so status check doesn't exist

**Fix**:
1. Create a pull request to trigger CI
2. Wait for CI to complete
3. Status checks will appear in repository settings
4. Re-add status checks to branch protection rule

**Alternative**: Remove status checks temporarily, merge first PR, then re-add

---

### Issue 2: Can't find status checks in dropdown

**Cause**: Status checks only appear after they've run at least once

**Fix**:
1. Push code to GitHub
2. Create a pull request
3. Wait for GitHub Actions to run
4. Return to branch protection settings
5. Status checks should now be available

---

### Issue 3: "At least 1 approving review is required"

**Problem**: You're the only developer, can't approve your own PR

**Solutions**:

**Option A**: Remove required reviews for small teams
- Edit main branch protection rule
- Uncheck "Require a pull request before merging"
- Click "Save changes"
- **Note**: Less safe, but faster for solo development

**Option B**: Use different account for reviews
- Create a second GitHub account (or use organization account)
- Invite as collaborator
- Approve your own PRs with second account
- **Note**: More secure, follows best practices

**Option C**: Temporarily bypass protection
- Edit main branch protection rule
- Check "Allow specified actors to bypass required pull requests"
- Add yourself to bypass list
- **Note**: Only for emergencies, defeats the purpose

**Recommendation**: Use Option A for solo dev, Option B for teams

---

### Issue 4: Branch protection too strict

**Symptoms**: Can't merge anything, development is blocked

**Fix**: Adjust settings to be less strict

1. Go to Settings > Branches > main > Edit
2. Reduce required approvals from 1 to 0
3. Uncheck "Dismiss stale pull request approvals"
4. Uncheck "Require conversation resolution"
5. Click "Save changes"

**Balance**: Find the right level of protection for your team size and velocity

---

### Issue 5: GitHub CLI authentication fails

**Error**:
```
gh: Not logged into any GitHub hosts
```

**Fix**:
```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS or SSH
# Follow prompts to authenticate
```

**Verify**:
```bash
gh auth status
# Should show: Logged in to github.com
```

---

## Advanced Configuration

### Enable Code Owners (Optional)

If you want specific people to review certain files:

1. Create `.github/CODEOWNERS` file:
   ```
   # CODEOWNERS for MISP Installation Project

   # Default owners for everything
   * @yourusername

   # Security-critical files require security team review
   /lib/misp_password.py @security-team
   /lib/misp_database.py @security-team

   # NERC CIP scripts require compliance team review
   /scripts/configure-misp-nerc-cip.py @compliance-team
   /docs/NERC_CIP_CONFIGURATION.md @compliance-team
   ```

2. Enable "Require review from Code Owners" in branch protection

3. Code owners will automatically be requested for review

---

### Require Signed Commits (Optional)

For high-security environments:

1. Set up GPG key: https://docs.github.com/en/authentication/managing-commit-signature-verification
2. Enable "Require signed commits" in branch protection
3. All commits must be GPG-signed

**Note**: Adds complexity, only needed for compliance requirements

---

### Status Check Timeout (Optional)

If CI takes > 30 minutes:

1. Settings > Branches > Edit rule
2. Add status check with longer timeout
3. Click "Save changes"

**Note**: Our CI runs in 2-3 minutes, so default timeout is fine

---

## Best Practices

### For Small Teams (1-3 developers)

**`main` branch**:
- ✅ Require pull requests
- ✅ Require CI to pass
- ❌ No required approvals (self-merge allowed)
- ✅ Require conversations resolved

**`develop` branch**:
- ❌ No pull requests required
- ✅ Require CI to pass
- ✅ Block force pushes

### For Medium Teams (4-10 developers)

**`main` branch**:
- ✅ Require pull requests
- ✅ Require 1 approval
- ✅ Require CI to pass
- ✅ Dismiss stale reviews
- ✅ Require conversations resolved

**`develop` branch**:
- ✅ Require pull requests
- ✅ Require CI to pass
- ❌ No required approvals
- ✅ Block force pushes

### For Large Teams (10+ developers)

**`main` branch**:
- ✅ Require pull requests
- ✅ Require 2+ approvals
- ✅ Require code owner review
- ✅ Require CI to pass
- ✅ Dismiss stale reviews
- ✅ Require conversations resolved
- ✅ Require signed commits (optional)

**`develop` branch**:
- ✅ Require pull requests
- ✅ Require 1 approval
- ✅ Require CI to pass
- ✅ Block force pushes

---

## Summary

### What You Configured

✅ **main branch**: Fully protected, requires PR + approval + CI
✅ **develop branch**: Moderate protection, requires CI only
✅ Both branches: No force pushes, no deletions

### What Happens Now

**When you push to main**:
1. ❌ Direct push rejected
2. ✅ Must create pull request
3. ✅ CI runs automatically
4. ✅ Reviewer approves (if enabled)
5. ✅ Merge allowed

**When you push to develop**:
1. ✅ Direct push allowed (if configured)
2. ✅ CI must pass
3. ✅ Merge allowed after CI

**When you create feature branch**:
1. ✅ No restrictions
2. ✅ Create PR to develop
3. ✅ CI runs on PR
4. ✅ Merge after CI passes

---

## Next Steps

1. ✅ Branch protection configured
2. ✅ Test with a pull request
3. ✅ Verify CI runs automatically
4. ✅ Update team on new workflow
5. ✅ Document any customizations

---

## Resources

- **GitHub Docs**: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- **GitHub CLI**: https://cli.github.com/
- **Branching Strategy**: [docs/BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)
- **CI/CD Guide**: [docs/CI_CD_GUIDE.md](CI_CD_GUIDE.md)

---

**Last Updated**: October 2025
**Maintained by**: tKQB Enterprises
**Protection Level**: Production Grade
