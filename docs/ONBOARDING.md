# Developer Onboarding Guide

**Purpose**: Structured learning path for new developers joining the MISP Installation Suite project
**Timeline**: 30/60/90 days
**Last Updated**: 2025-10-25

Welcome to the MISP Installation Suite project! This guide will help you become productive quickly.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Week 1: Environment & Fundamentals](#week-1-environment--fundamentals)
3. [Week 2: Core Systems](#week-2-core-systems)
4. [Week 3-4: Advanced Features](#week-3-4-advanced-features)
5. [Month 2: Specialization](#month-2-specialization)
6. [Month 3: Contribution](#month-3-contribution)
7. [Exercises & Tasks](#exercises--tasks)
8. [Code Reading Guide](#code-reading-guide)
9. [Contribution Workflow](#contribution-workflow)
10. [Getting Help](#getting-help)

---

## Before You Start

### Prerequisites

**Required Knowledge**:
- Python 3.8+ (intermediate level)
- Linux command line (comfortable with bash)
- Git basics (clone, commit, push, pull, branch)
- Docker fundamentals (containers, volumes, exec)

**Helpful (Not Required)**:
- PHP basics (for widget development)
- MISP platform familiarity
- Electric utility industry knowledge
- NERC CIP compliance understanding

### Setup Checklist

- [ ] Clone repository: `git clone https://github.com/gforce-gallagher-01/misp-install.git`
- [ ] Install Python 3.8+
- [ ] Install Docker and Docker Compose
- [ ] Install development tools: `sudo apt install git python3-pip`
- [ ] Set up IDE (VS Code, PyCharm, or your preference)
- [ ] Read `README.md` (main project overview)
- [ ] Read `CLAUDE.md` (project instructions and current state)

### First Day Reading List (2-3 hours)

**Read these files in order**:
1. **README.md** (30 min) - Project overview
2. **CLAUDE.md** (20 min) - Current project state
3. **docs/README.md** (20 min) - Documentation hub
4. **docs/PROJECT_KNOWLEDGE.md** (60 min) - Architecture and patterns
5. **BRANCHES.md** (15 min) - Branch inventory
6. **TODO.md** (15 min) - Current priorities

---

## Week 1: Environment & Fundamentals

### Day 1: Environment Setup

**Goal**: Get a working development environment

**Tasks**:
1. Complete setup checklist above
2. Run first installation (test environment):
   ```bash
   cd misp-install
   sudo python3 misp-install.py --config config/examples/minimal-install.conf
   ```
3. Verify MISP running:
   ```bash
   sudo docker ps | grep misp
   curl -k https://localhost
   ```
4. Explore MISP web interface (credentials in installation output)

**Resources**:
- `docs/INSTALLATION.md`
- `docs/QUICKSTART.md`

**Expected Time**: 4-6 hours

---

### Day 2: Codebase Structure

**Goal**: Understand how the codebase is organized

**Tasks**:
1. Draw a diagram of directory structure
2. Identify the purpose of each top-level directory
3. Read `docs/PROJECT_KNOWLEDGE.md` section "Codebase Architecture"
4. Explore `lib/` directory - note what each module does
5. Look at 2-3 phase files in `phases/`

**Exercise**:
- Map each directory to its purpose
- Identify which files are runtime (state, logs) vs source code
- Find where Docker operations are abstracted

**Resources**:
- `docs/PROJECT_KNOWLEDGE.md`
- `docs/REPOSITORY-STRUCTURE.md`

**Expected Time**: 3-4 hours

---

### Day 3: Understanding Phases

**Goal**: Understand the modular phase system

**Tasks**:
1. Read `phases/base_phase.py` - the base class
2. Pick a simple phase (e.g., `phase_11_8_utilities_intel.py`)
3. Trace execution flow from `misp-install.py` → phase → helpers
4. Understand state management (check `state/*.json` after running)

**Exercise**:
- Run a single phase: `sudo python3 phases/phase_11_8_utilities_intel.py`
- Check state file: `cat state/phase_11_8_utilities_intel.json`
- Identify: What steps did it complete? What state did it save?

**Resources**:
- `docs/PATTERNS.md` (Phase Pattern section)
- `docs/ARCHITECTURE_DECISIONS.md` (ADR-001)

**Expected Time**: 4 hours

---

### Day 4: Helper Modules (lib/)

**Goal**: Understand centralized helper modules

**Tasks**:
1. Read `lib/misp_api_helpers.py` - API abstraction
2. Read `lib/docker_helpers.py` - Docker abstraction
3. Read `lib/state_manager.py` - State persistence
4. Understand why code was centralized (DRY principle)

**Exercise**:
- Write a small script that uses `misp_api_helpers` to search for events
- Use `docker_helpers` to check if container is running
- Save state using `StateManager`

**Example Script**:
```python
from lib.misp_api_helpers import get_api_key, misp_rest_search
from lib.docker_helpers import is_container_running
from lib.state_manager import StateManager

# Check Docker
if not is_container_running('misp-misp-core-1'):
    print("MISP not running!")
    exit(1)

# Search events
api_key = get_api_key()
events = misp_rest_search(api_key, {'tags': ['ics:%'], 'last': '7d'})
print(f"Found {len(events)} ICS events")

# Save state
state = StateManager('my_test.json')
state.save({'events_found': len(events)})
```

**Resources**:
- `docs/PATTERNS.md` (Centralized Helper Pattern)
- `docs/ARCHITECTURE_DECISIONS.md` (ADR-003)

**Expected Time**: 4-5 hours

---

### Day 5: Logging & Debugging

**Goal**: Understand logging system and debugging techniques

**Tasks**:
1. Read `docs/README_LOGGING.md`
2. Examine `lib/misp_logger.py`
3. Run installation with verbose logging
4. Practice reading JSON logs

**Exercise**:
- Add logging to your Day 4 exercise script
- Intentionally cause an error and find it in logs
- Use `jq` to parse JSON logs:
  ```bash
  cat logs/misp_installer.log | jq 'select(.level=="ERROR")'
  ```

**Debugging Checklist**:
```bash
# 1. Check logs
tail -f logs/misp_installer.log

# 2. Check phase state
cat state/phase_*.json

# 3. Check Docker
sudo docker ps -a
sudo docker logs misp-misp-core-1

# 4. Check MISP logs
sudo docker exec misp-misp-core-1 tail -f /var/www/MISP/app/tmp/logs/error.log

# 5. Test MISP API
curl -k -H "Authorization: $(cat ~/.misp/apikey)" https://localhost/users/view/me.json
```

**Resources**:
- `docs/README_LOGGING.md`
- `docs/TROUBLESHOOTING.md`

**Expected Time**: 3-4 hours

---

## Week 2: Core Systems

### Days 6-7: Feature Exclusion System

**Goal**: Understand how users can exclude features

**Tasks**:
1. Read `docs/development/EXCLUSION_LIST_DESIGN.md`
2. Study `lib/features.py` - feature definitions
3. Study `lib/config.py` - exclusion parsing
4. Try different exclusion configurations

**Exercise**:
- Create custom exclusion config excluding Azure AD
- Run installation with your config
- Verify Azure AD phase was skipped (check state file)

**Resources**:
- `docs/development/EXCLUSION_LIST_DESIGN.md`
- `docs/ARCHITECTURE_DECISIONS.md` (ADR-004)
- `config/examples/*.conf`

**Expected Time**: 6-8 hours

---

### Days 8-9: MISP API Integration

**Goal**: Master MISP REST API interactions

**Tasks**:
1. Read MISP API documentation: https://www.misp-project.org/openapi/
2. Study `lib/misp_api_helpers.py` in detail
3. Practice API calls with curl
4. Write scripts using API helpers

**Exercise**:
Create a script that:
- Searches for events with specific tags
- Adds a new event
- Adds attributes to the event
- Publishes the event

**Common API Patterns**:
```python
# Search events
events = misp_rest_search(api_key, {
    'tags': ['ics:%'],
    'published': 1,
    'last': '30d'
})

# Add event
event_data = {
    'Event': {
        'info': 'Test Event',
        'threat_level_id': 2,
        'analysis': 1,
        'distribution': 0
    }
}
result = misp_add_event(api_key, event_data)

# Add attribute
misp_add_attribute(api_key, event_id, {
    'type': 'ip-src',
    'value': '192.168.1.100',
    'category': 'Network activity'
})
```

**Resources**:
- `lib/misp_api_helpers.py`
- MISP OpenAPI docs
- `scripts/` examples

**Expected Time**: 8-10 hours

---

### Day 10: Testing Your Work

**Goal**: Learn testing practices

**Tasks**:
1. Understand testing strategy (manual + automated)
2. Write unit tests for helper functions
3. Practice integration testing

**Testing Checklist**:
```bash
# 1. Lint code
ruff check your_file.py

# 2. Type checking (if types used)
mypy your_file.py

# 3. Manual testing
python3 your_script.py

# 4. Integration test (in test environment)
sudo python3 misp-install.py --config config/test.conf

# 5. Verify results
sudo docker ps | grep misp
curl -k https://localhost
```

**Resources**:
- `tests/` directory
- `CLAUDE.md` (Testing section)

**Expected Time**: 4-5 hours

---

## Week 3-4: Advanced Features

### Days 11-15: Widget Development

**Goal**: Learn to create custom MISP dashboard widgets

**Tasks**:
1. Read `widgets/utilities-sector/README.md`
2. Study existing widget examples
3. Understand widget trait pattern
4. Create a simple widget

**Critical Widget Patterns**:
```php
// 1. Use trait for shared functionality
trait WidgetHelpers {
    protected function checkPermissions($user) { ... }
}

class MyWidget {
    use WidgetHelpers;

    public $title = 'My Widget';
    public $render = 'SimpleList';
    public $width = 3;
    public $height = 4;

    public function handler($user, $options = array()) {
        if (!$this->checkPermissions($user)) {
            return array();
        }

        // Widget logic
        $Event = ClassRegistry::init('Event');
        $eventIds = $Event->fetchEventIds($user, array(
            'tags' => array('ics:%'),  // Note: wildcard!
            'last' => '7d'
        ));

        return $this->formatData($eventIds);
    }
}
```

**Exercise**:
Create a widget that:
- Shows count of events by threat level
- Displays as pie chart
- Filters to last 24 hours
- Uses proper permissions checking

**Resources**:
- `docs/PATTERNS.md` (Widget Base Class Pattern)
- `docs/historical/fixes/DASHBOARD_WIDGET_FIXES.md`
- `widgets/utilities-sector/` examples

**Expected Time**: 15-20 hours

---

### Days 16-20: NERC CIP Compliance

**Goal**: Understand compliance requirements and implementation

**Tasks**:
1. Read `docs/nerc-cip/README.md`
2. Study compliance architecture docs
3. Review research assignments (person-1, person-2, person-3)
4. Understand compliance gap and roadmap

**Key Concepts**:
- NERC CIP standards (CIP-003 through CIP-015)
- Medium Impact vs Low Impact requirements
- Compliance percentage calculation
- Audit evidence collection

**Exercise**:
- Review current compliance status (35%)
- Identify Phase 1 "Quick Wins" tasks
- Map a CIP requirement to implementation
- Create compliance evidence document template

**Resources**:
- `docs/nerc-cip/` entire directory
- `docs/nerc-cip/AUDIT_REPORT.md`
- `docs/nerc-cip/PRODUCTION_READINESS_TASKS.md`

**Expected Time**: 15-20 hours

---

## Month 2: Specialization

Choose one area to specialize in:

### Track A: Backend Systems (Phases & Scripts)

**Focus**: Phase development, automation, system integration

**Projects**:
1. Create new phase for specific feature
2. Improve existing phase with better error handling
3. Add feature to exclusion system
4. Create standalone script for utility task

**Skills Developed**:
- Phase architecture
- State management
- Error handling
- Docker operations

---

### Track B: Widget Development

**Focus**: MISP dashboard widgets, PHP, data visualization

**Projects**:
1. Create widget suite for specific use case
2. Refactor existing widgets for DRY
3. Add new visualization type
4. Document widget development patterns

**Skills Developed**:
- PHP programming
- MISP widget API
- Data visualization
- Dashboard design

---

### Track C: NERC CIP Compliance

**Focus**: Compliance implementation, audit requirements, evidence collection

**Projects**:
1. Implement Phase 1 Quick Wins
2. Create compliance reporting scripts
3. Develop audit evidence collection
4. Map requirements to implementation

**Skills Developed**:
- Compliance understanding
- Audit procedures
- Evidence collection
- Regulatory requirements

---

### Track D: Integration & Automation

**Focus**: Third-party integrations, SIEM, automation

**Projects**:
1. Implement SIEM log forwarding
2. Create vulnerability tracking integration
3. Automate patch management workflow
4. Build E-ISAC incident reporting

**Skills Developed**:
- API integrations
- Automation patterns
- SIEM systems
- Incident response

---

## Month 3: Contribution

### Weeks 9-10: First Real Contribution

**Goal**: Make your first meaningful contribution to the project

**Process**:
1. Review `TODO.md` for tasks
2. Choose task matching your specialization
3. Create feature branch
4. Implement with tests
5. Submit pull request

**PR Checklist**:
- [ ] Code follows project patterns (see `docs/PATTERNS.md`)
- [ ] Logging added appropriately
- [ ] State management if needed
- [ ] Feature exclusion support if optional
- [ ] Documentation updated
- [ ] Testing completed
- [ ] Commit messages follow convention

**Resources**:
- `docs/CONTRIBUTING.md`
- `docs/BRANCHING_STRATEGY.md`

---

### Weeks 11-12: Code Review & Iteration

**Goal**: Learn code review process and improve based on feedback

**Tasks**:
1. Address code review comments
2. Update based on feedback
3. Learn from review process
4. Help review others' PRs

**Code Review Focus Areas**:
- Pattern adherence
- Error handling
- Testing coverage
- Documentation
- Performance
- Security

---

## Exercises & Tasks

### Exercise 1: Phase Development

**Task**: Create a new phase that configures MISP email settings

**Requirements**:
- Inherit from `BasePhase`
- Check requirements (MISP running, config file exists)
- Read email config from file
- Update MISP config via API or direct file edit
- Save state after completion
- Support feature exclusion
- Add proper logging

**Time**: 4-6 hours

---

### Exercise 2: API Script

**Task**: Write script that generates weekly threat intelligence report

**Requirements**:
- Search MISP for events from last 7 days
- Group by threat level and category
- Count IOCs by type
- Generate markdown report
- Email report (bonus)

**Time**: 3-4 hours

---

### Exercise 3: Widget Creation

**Task**: Create "Recent High-Threat Events" widget

**Requirements**:
- Show last 10 high-threat events
- Display as table with: date, info, tags
- Click event to view details
- Use proper permissions
- Handle tag wildcard correctly

**Time**: 6-8 hours

---

### Exercise 4: Compliance Feature

**Task**: Implement CIP-007 R4 log retention check

**Requirements**:
- Check if logs older than 90 days exist
- Alert if retention exceeded
- Provide cleanup recommendations
- Generate compliance report
- Document as audit evidence

**Time**: 5-7 hours

---

## Code Reading Guide

### How to Read This Codebase

**Start Here** (Read in this order):
1. `misp-install.py` - Entry point, orchestration
2. `phases/base_phase.py` - Phase base class
3. `lib/misp_api_helpers.py` - API operations
4. `lib/docker_helpers.py` - Docker operations
5. Pick one simple phase to read through

**Reading Techniques**:

**Top-Down**:
- Start with entry point (`misp-install.py`)
- Follow execution flow through phases
- Note dependencies and imports

**Bottom-Up**:
- Start with utility functions (`lib/`)
- See how they're used in phases
- Understand composition

**Feature-Focused**:
- Pick a feature (e.g., "utilities dashboards")
- Find all related code
- Trace from user config to implementation

**Pattern Recognition**:
- Identify repeated patterns
- Note how they're abstracted
- Understand the pattern purpose

---

## Contribution Workflow

### 1. Find a Task

**Sources**:
- `TODO.md` - Planned features
- GitHub Issues
- Team discussions
- Your own ideas (discuss first)

---

### 2. Create Feature Branch

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# For fixes
git checkout -b fix/bug-description
```

---

### 3. Implement

**Follow Patterns**:
- Use existing patterns (see `docs/PATTERNS.md`)
- Follow code style
- Add logging
- Handle errors
- Add state management if needed

**Testing**:
- Test manually in dev environment
- Add unit tests if applicable
- Verify in clean install

---

### 4. Document

**Update**:
- Code docstrings
- `docs/` if behavior changes
- `TODO.md` (move to completed or remove)
- `CHANGELOG.md` with your change

---

### 5. Commit

**Commit Message Format**:
```
type: brief description (50 chars)

Detailed explanation (if needed).
Multiple paragraphs OK.

- Bullet points for details
- Related issue: #123
```

**Types**: feat, fix, docs, refactor, test, chore

---

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name

# Create PR
gh pr create --title "feat: Your feature description" \
             --body "Description, testing, related issues"
```

---

### 7. Code Review

**Expect**:
- Questions about approach
- Requests for changes
- Pattern adherence checks
- Testing verification

**Respond**:
- Address all comments
- Ask clarifying questions
- Update code based on feedback
- Be open to suggestions

---

### 8. Merge

After approval:
- Squash commits if requested
- Ensure CI passes
- Merge to main

---

## Getting Help

### Resources

**Documentation**:
- Start with `docs/README.md` navigation
- Check `docs/TROUBLESHOOTING.md`
- Review `docs/PROJECT_KNOWLEDGE.md`

**Code Examples**:
- Look at existing phases in `phases/`
- Check scripts in `scripts/`
- Review widgets in `widgets/`

**Patterns**:
- See `docs/PATTERNS.md` for proven patterns
- Check `docs/ARCHITECTURE_DECISIONS.md` for rationale

---

### Questions to Ask

**Good Questions**:
- "I want to implement X. Which pattern should I use?"
- "I'm seeing error Y. I've checked logs and Z. What should I look at next?"
- "Is there an existing helper for X operation?"

**Questions to Research First**:
- "How do I install Python?" (Google this)
- "What's a Docker container?" (Read Docker docs)
- "How does MISP work?" (Read MISP docs)

---

### Mentorship

**Weekly Check-ins**:
- Schedule with team lead
- Review progress
- Discuss blockers
- Get guidance

**Pair Programming**:
- Work with senior dev on complex tasks
- Learn patterns through practice
- Get real-time feedback

---

## Success Metrics

### Week 1 Goals
- [ ] Development environment working
- [ ] Successfully ran installation
- [ ] Can navigate codebase
- [ ] Understand phase system
- [ ] Can read logs and debug

### Month 1 Goals
- [ ] Understand all core patterns
- [ ] Can write scripts using helpers
- [ ] Created test widget or phase
- [ ] Understand NERC CIP basics
- [ ] Comfortable with git workflow

### Month 2 Goals
- [ ] Specialized in one area
- [ ] Completed 2-3 exercises
- [ ] Contributed to code reviews
- [ ] Can work independently on small tasks

### Month 3 Goals
- [ ] First PR merged
- [ ] Can implement features end-to-end
- [ ] Comfortable with all systems
- [ ] Helping onboard others

---

**Welcome to the team! 🎉**

**Questions?** See the "Getting Help" section above or ask your team lead.

**Feedback on this guide?** Please submit PR with improvements!

---

**Maintained by**: tKQB Enterprises
**Version**: 1.0
**Last Updated**: 2025-10-25
