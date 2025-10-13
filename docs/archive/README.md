# Documentation Archive

**Purpose**: This directory contains documentation files that are outdated or reference features/scripts not yet implemented in the current v5.4 release.

---

## Archived Documents

### INDEX.md
**Status**: Outdated package distribution document
**Issues**:
- References non-existent scripts (daily-health-check.sh, collect-diagnostics.sh)
- Contains bash command examples that don't match current Python scripts
- Designed for a different distribution model

**Use**: Reference for conceptual package structure ideas

### COMPLETE-FILE-LAYOUT.md
**Status**: Package distribution template
**Issues**:
- References file structure not matching current implementation
- Contains git workflow suggestions for package distribution

**Use**: Reference for project organization concepts

### READY-TO-RUN-SETUP.md
**Status**: Pre-configured installation guide
**Issues**:
- May reference features not in current implementation
- Designed for a different deployment model

**Use**: Reference for alternative installation approaches

---

## Why These Were Archived

These documents appear to have been created for a "packaged distribution" model where the installer would be distributed as a complete package with many supporting scripts. The current v5.4 implementation follows a simpler model with:

- Single main installer: `misp-install.py`
- Supporting Python scripts in `scripts/` directory
- Comprehensive documentation in root and `docs/`

---

## Current Documentation

For accurate, up-to-date documentation, see:

### Root Directory
- `README.md` - Main project documentation
- `SCRIPTS.md` - Complete script inventory
- `SETUP.md` - Installation setup guide
- `SECURITY_ARCHITECTURE.md` - Security architecture

### docs/ Directory
- `docs/README.md` - Documentation directory guide
- `docs/QUICKSTART.md` - Quick start guide
- `docs/INSTALLATION-CHECKLIST.md` - Installation checklist
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
- `docs/MAINTENANCE.md` - Maintenance procedures

---

## Should You Update These?

**No** - These documents represent a different design vision and would require significant rework to align with current implementation. It's cleaner to keep them as historical reference.

If specific content from these docs is needed, extract relevant concepts and integrate into current active documentation.

---

**Archive Created**: 2025-10-13
**Version**: 5.4
