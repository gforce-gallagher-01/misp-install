#!/bin/bash
# Research Progress Update Helper Script
# Usage: ./scripts/update-research-progress.sh [person] [task] [status] [hours]
# Example: ./scripts/update-research-progress.sh 1 1.1 in_progress 2

set -euo pipefail

# Configuration
TRACKER_FILE="docs/nerc-cip/research/RESEARCH_TRACKER.md"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Help function
show_help() {
    cat <<EOF
Research Progress Update Helper

Usage:
  $0 [person] [task] [status] [hours_spent]

Arguments:
  person       Person number (1, 2, or 3)
  task         Task number (e.g., 1.1, 2.3, 3.7)
  status       Task status: not_started, in_progress, complete, blocked
  hours_spent  Hours spent on this task (e.g., 2, 2.5)

Status Emojis:
  ⚪ not_started
  🟡 in_progress
  🟢 complete
  🔴 blocked

Examples:
  # Mark task 1.1 as in progress with 2 hours spent
  $0 1 1.1 in_progress 2

  # Mark task 2.3 as complete with 5 hours spent
  $0 2 2.3 complete 5

  # Mark task 3.1 as blocked
  $0 3 3.1 blocked 0

  # Quick status check
  $0 status

Commands:
  status       Show current progress for all persons
  summary      Show overall summary statistics
  help         Show this help message

EOF
}

# Status check function
show_status() {
    echo -e "${GREEN}=== Research Progress Status ===${NC}\n"

    for PERSON in 1 2 3; do
        echo -e "${YELLOW}Person $PERSON:${NC}"

        # Count tasks by status
        TOTAL=$(grep -E "^\| ${PERSON}\." "$TRACKER_FILE" | wc -l)
        COMPLETE=$(grep -E "^\| ${PERSON}\." "$TRACKER_FILE" | grep -c "🟢 Complete" || echo 0)
        IN_PROGRESS=$(grep -E "^\| ${PERSON}\." "$TRACKER_FILE" | grep -c "🟡 In Progress" || echo 0)
        NOT_STARTED=$(grep -E "^\| ${PERSON}\." "$TRACKER_FILE" | grep -c "⚪ Not Started" || echo 0)
        BLOCKED=$(grep -E "^\| ${PERSON}\." "$TRACKER_FILE" | grep -c "🔴 Blocked" || echo 0)

        PCT=$(echo "scale=0; $COMPLETE * 100 / $TOTAL" | bc)

        echo "  Total Tasks: $TOTAL"
        echo "  Complete: $COMPLETE ($PCT%)"
        echo "  In Progress: $IN_PROGRESS"
        echo "  Not Started: $NOT_STARTED"
        echo "  Blocked: $BLOCKED"
        echo ""
    done

    # Overall progress
    TOTAL_ALL=$(grep -E "^\| [123]\." "$TRACKER_FILE" | wc -l)
    COMPLETE_ALL=$(grep -E "^\| [123]\." "$TRACKER_FILE" | grep -c "🟢 Complete" || echo 0)
    PCT_ALL=$(echo "scale=0; $COMPLETE_ALL * 100 / $TOTAL_ALL" | bc)

    echo -e "${GREEN}Overall Progress: $COMPLETE_ALL / $TOTAL_ALL tasks ($PCT_ALL%)${NC}"
}

# Summary function
show_summary() {
    echo -e "${GREEN}=== Research Summary ===${NC}\n"

    # Time tracking
    echo "Time Spent:"
    for PERSON in 1 2 3; do
        # This would need to parse hours from tracker - simplified version
        echo "  Person $PERSON: [Hours TBD - update manually in tracker]"
    done

    echo ""
    echo "Target Completion: 2025-11-07 (2 weeks from Oct 24)"
    echo "Days Remaining: $(( ($(date -d "2025-11-07" +%s) - $(date +%s)) / 86400 )) days"

    echo ""
    show_status
}

# Main update function
update_progress() {
    PERSON=$1
    TASK=$2
    STATUS=$3
    HOURS=${4:-0}

    # Validate inputs
    if [[ ! "$PERSON" =~ ^[123]$ ]]; then
        echo -e "${RED}Error: Person must be 1, 2, or 3${NC}"
        exit 1
    fi

    if [[ ! "$STATUS" =~ ^(not_started|in_progress|complete|blocked)$ ]]; then
        echo -e "${RED}Error: Status must be: not_started, in_progress, complete, or blocked${NC}"
        exit 1
    fi

    # Convert status to emoji
    case $STATUS in
        not_started) EMOJI="⚪ Not Started" ;;
        in_progress) EMOJI="🟡 In Progress" ;;
        complete)    EMOJI="🟢 Complete" ;;
        blocked)     EMOJI="🔴 Blocked" ;;
    esac

    echo -e "${YELLOW}Updating task ${PERSON}.${TASK} to ${EMOJI}...${NC}"

    # Check if tracker file exists
    if [ ! -f "$TRACKER_FILE" ]; then
        echo -e "${RED}Error: Tracker file not found: $TRACKER_FILE${NC}"
        exit 1
    fi

    # TODO: Implement actual update logic (sed/awk to modify tracker file)
    # For now, just show what would be updated
    echo "Would update:"
    echo "  Task: $PERSON.$TASK"
    echo "  Status: $EMOJI"
    echo "  Hours: $HOURS"
    echo ""
    echo -e "${YELLOW}Note: Automatic update not yet implemented.${NC}"
    echo -e "${YELLOW}Please manually edit: $TRACKER_FILE${NC}"
    echo ""
    echo "Find line matching: | ${PERSON}.${TASK} |"
    echo "Update status column to: $EMOJI"
    echo "Update hours column to: ${HOURS}h / [estimate]h"
    echo ""
    echo -e "${GREEN}Then commit with:${NC}"
    echo "git add $TRACKER_FILE"
    echo "git commit -m \"research: Person $PERSON task $TASK - $STATUS\""
}

# Main script logic
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    status)
        show_status
        ;;
    summary)
        show_summary
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ $# -lt 3 ]; then
            echo -e "${RED}Error: Insufficient arguments${NC}"
            show_help
            exit 1
        fi
        update_progress "$@"
        ;;
esac
