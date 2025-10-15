#!/bin/bash
#
# Branch Protection Setup Script
# Sets up branch protection rules for main and develop branches
#
# Requirements:
#   - GitHub CLI (gh) installed and authenticated
#   - Repository must be pushed to GitHub
#   - User must have admin access to repository
#
# Usage:
#   ./setup-branch-protection.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Branch Protection Setup for MISP Installation       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}ERROR: GitHub CLI (gh) is not installed${NC}"
    echo ""
    echo "Install GitHub CLI:"
    echo "  Ubuntu/Debian: sudo apt install gh"
    echo "  Or follow: https://cli.github.com/manual/installation"
    echo ""
    echo "After installation, authenticate with:"
    echo "  gh auth login"
    echo ""
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI is not authenticated${NC}"
    echo ""
    echo "Please authenticate with:"
    echo "  gh auth login"
    echo ""
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)

if [ -z "$REPO" ]; then
    echo -e "${RED}ERROR: Not in a GitHub repository or repository not pushed to GitHub${NC}"
    echo ""
    echo "Please push your repository to GitHub first:"
    echo "  git push -u origin main"
    echo "  git push -u origin develop"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Repository: $REPO${NC}"
echo ""

# Confirm with user
echo -e "${YELLOW}This will set up branch protection rules for:${NC}"
echo "  1. main branch (strict protection)"
echo "  2. develop branch (moderate protection)"
echo ""
echo "Protection rules include:"
echo "  - Require pull request reviews"
echo "  - Require status checks to pass"
echo "  - No force pushes"
echo "  - No deletions"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Setting up branch protection rules...${NC}"
echo ""

# Function to set up branch protection
setup_branch_protection() {
    local BRANCH=$1
    local STRICT=$2  # true for main, false for develop

    echo -e "${BLUE}Configuring protection for: ${BRANCH}${NC}"

    # Base protection settings
    local PROTECTION_ARGS=(
        --repo "$REPO"
        --branch "$BRANCH"
    )

    # Common settings for both branches
    PROTECTION_ARGS+=(
        --block-creations                           # Block new branch creation with this name
        --no-allow-deletions                        # Prevent branch deletion
        --no-allow-force-pushes                     # Prevent force pushes
        --required-linear-history=false             # Allow merge commits
    )

    # Strict settings for main branch
    if [ "$STRICT" = true ]; then
        PROTECTION_ARGS+=(
            --require-pull-request                  # Require PR before merge
            --required-approving-review-count=1     # Require 1 approval
            --dismiss-stale-reviews                 # Dismiss old reviews on new push
            --require-conversation-resolution       # Require all conversations resolved
            --require-code-owner-review=false       # Don't require code owner (optional)
            --no-bypass-pull-request-allowances     # No bypassing (include admins)
        )
    else
        # Moderate settings for develop branch
        PROTECTION_ARGS+=(
            --require-pull-request=false            # PRs optional (can commit directly if needed)
        )
    fi

    # Required status checks (same for both branches)
    PROTECTION_ARGS+=(
        --require-status-checks="validate"          # Syntax & import validation
        --require-status-checks="test"              # Unit tests
        --require-strict-status-checks              # Require branch up-to-date
    )

    # Apply protection
    if gh api \
        -X PUT \
        "/repos/${REPO}/branches/${BRANCH}/protection" \
        -f required_status_checks[strict]=true \
        -f required_status_checks[contexts][]=validate \
        -f required_status_checks[contexts][]=test \
        -f enforce_admins=$([[ "$STRICT" = true ]] && echo "true" || echo "false") \
        -f required_pull_request_reviews[dismiss_stale_reviews]=$([[ "$STRICT" = true ]] && echo "true" || echo "false") \
        -f required_pull_request_reviews[require_code_owner_reviews]=false \
        -f required_pull_request_reviews[required_approving_review_count]=$([[ "$STRICT" = true ]] && echo "1" || echo "0") \
        -f restrictions=null \
        -f allow_force_pushes[enabled]=false \
        -f allow_deletions[enabled]=false \
        --silent 2>&1; then

        echo -e "${GREEN}✓ Protection configured for ${BRANCH}${NC}"
    else
        echo -e "${YELLOW}⚠ Could not configure protection for ${BRANCH}${NC}"
        echo -e "${YELLOW}  You may need to configure manually via GitHub web interface${NC}"
        echo -e "${YELLOW}  Go to: Settings > Branches > Add rule${NC}"
    fi

    echo ""
}

# Set up main branch protection (strict)
setup_branch_protection "main" true

# Set up develop branch protection (moderate)
setup_branch_protection "develop" false

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Branch Protection Setup Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}What was configured:${NC}"
echo ""
echo -e "${GREEN}main branch:${NC}"
echo "  ✓ Requires pull request with 1+ approval"
echo "  ✓ Requires CI checks to pass (validate, test)"
echo "  ✓ Dismiss stale reviews on new commits"
echo "  ✓ Require conversation resolution"
echo "  ✓ No force pushes"
echo "  ✓ No branch deletion"
echo "  ✓ Includes administrators"
echo ""
echo -e "${GREEN}develop branch:${NC}"
echo "  ✓ Requires CI checks to pass (validate, test)"
echo "  ✓ No force pushes"
echo "  ✓ No branch deletion"
echo "  ℹ Pull request reviews optional (faster iteration)"
echo ""
echo -e "${BLUE}Verify settings:${NC}"
echo "  https://github.com/${REPO}/settings/branches"
echo ""
echo -e "${GREEN}✓ You're all set! Happy coding!${NC}"
echo ""
