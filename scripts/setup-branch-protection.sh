#!/bin/bash
#
# GitHub Branch Protection Setup Script
# Version: 1.0
# Date: 2025-10-15
#
# Purpose:
#   Configure branch protection rules for main and develop branches
#
# Usage:
#   ./scripts/setup-branch-protection.sh

set -e

REPO="gforce-gallagher-01/misp-install"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "========================================================================"
echo "  GitHub Branch Protection Configuration"
echo "========================================================================"
echo ""

# Check if gh CLI is authenticated
if ! gh auth status &>/dev/null; then
    echo -e "${RED}✗${NC} GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✓${NC} GitHub CLI authenticated"
echo ""

# Main Branch Protection
echo "Configuring main branch protection..."
gh api -X PUT "repos/$REPO/branches/main/protection" \
  -f required_status_checks='{"strict":true,"contexts":["validate","test"]}' \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  -f enforce_admins=true \
  -f required_linear_history=false \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f required_conversation_resolution=true \
  > /dev/null 2>&1

echo -e "${GREEN}✓${NC} Main branch protection configured"
echo "  - Required status checks: validate, test"
echo "  - Required PR reviews: 1 approval"
echo "  - Dismiss stale reviews: Yes"
echo "  - Enforce for admins: Yes"
echo "  - Require conversation resolution: Yes"
echo ""

# Develop Branch Protection
echo "Configuring develop branch protection..."
gh api -X PUT "repos/$REPO/branches/develop/protection" \
  -f required_status_checks='{"strict":true,"contexts":["validate","test"]}' \
  -f enforce_admins=false \
  -f required_linear_history=false \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  > /dev/null 2>&1

echo -e "${GREEN}✓${NC} Develop branch protection configured"
echo "  - Required status checks: validate, test"
echo "  - Enforce for admins: No (allows bypassing during development)"
echo "  - Block force pushes: Yes"
echo ""

# Summary
echo "========================================================================"
echo "  Branch Protection Summary"
echo "========================================================================"
echo ""
echo "Main Branch (production):"
echo "  ✓ Requires PR reviews"
echo "  ✓ Requires status checks"
echo "  ✓ Enforced for admins"
echo "  ✓ Blocks force pushes"
echo ""
echo "Develop Branch (development):"
echo "  ✓ Requires status checks"
echo "  ✓ Blocks force pushes"
echo "  ✓ Allows admin bypass (for rapid development)"
echo ""
echo -e "${GREEN}✓${NC} Branch protection configured successfully!"
echo ""
