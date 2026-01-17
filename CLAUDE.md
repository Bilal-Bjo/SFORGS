# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SF Orgs is a Python TUI (Terminal User Interface) app for managing authenticated Salesforce organizations. Built with **Textual** for a full-screen, interactive terminal experience with mouse support, keyboard navigation, and search filtering.

## Development Commands

```bash
# Install for development
pipx install -e .

# Run the application
sforgs
```

There are no test, lint, or build commands - this is a single-file utility.

## Architecture

**Single-file design:** The entire application lives in `sforgs.py` (~490 lines).

### Code Sections (in order)

1. **SF CLI Integration** - Functions that call `sf` CLI via subprocess:
   - `get_sf_orgs()` - Runs `sf org list --json`
   - `open_org()` - Runs `sf org open -o <alias>`
   - `reauth_org()` - Runs `sf org login web`

2. **Data Processing** - Normalizes org data from SF CLI JSON output:
   - `parse_orgs()` - Deduplicates, normalizes, and sorts orgs
   - `get_org_type()` - Determines type (Scratch, Dev Hub, Sandbox, Production)

3. **Custom Widgets** - Textual widget classes:
   - `StatsBar` - Displays connection statistics at top
   - `SearchInput` - Filter input triggered by `/` key

4. **TCSS Styling** - CSS-like stylesheet for the TUI layout

5. **SFOrgsApp** - Main Textual application class:
   - Key bindings: `q` quit, `r` refresh, `Enter/o` open, `a` re-auth, `/` search, `j/k` vim navigation
   - Async data loading with `@work` decorator
   - DataTable for org list with row selection
   - Toast notifications for feedback

### Key Textual Patterns

- **Workers** (`@work` decorator) - Background threads for SF CLI calls
- **Message handlers** (`@on` decorator) - React to widget events
- **Bindings** - Keyboard shortcuts with `Binding` class
- **TCSS** - Textual CSS for styling, uses `$variables` for theme colors

### External Dependencies

- **Salesforce CLI (`sf`)** - Must be installed and authenticated
- **textual** - Full-featured TUI framework (includes Rich internally)
