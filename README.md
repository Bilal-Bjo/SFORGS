# SF Orgs

An enterprise-grade terminal user interface for Salesforce org management and navigation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)

## Overview

**SF Orgs** streamlines Salesforce org management by providing administrators and developers with a full-featured terminal user interface. The application consolidates org visibility, session management, and quick access into a single, keyboard-driven workflow—eliminating the need to manually execute CLI commands or manage org aliases.

### Key Capabilities

- **Unified Org Visibility** - Comprehensive view of all authenticated orgs with real-time connection status
- **Full Keyboard Navigation** - Arrow keys, vim-style bindings (j/k), and shortcut keys for efficient workflows
- **Intelligent Search** - Filter orgs instantly by alias, username, org type, or name
- **Mouse Support** - Click to select, double-click to open for point-and-click accessibility
- **Session Management** - Identify expired sessions and re-authenticate directly from the interface
- **Org Type Classification** - Automatic detection and visual distinction of Production, Sandbox, Developer Hub, and Scratch orgs
- **Cross-Platform Compatibility** - Consistent experience across macOS, Linux, and Windows environments

## Interface Preview

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ SF ORGS                                                  Salesforce Org Manager│
├────────────────────────────────────────────────────────────────────────────────┤
│ 5 orgs  ● 4 connected  ● 1 expired                                             │
│                                                                                │
│  ┃   │ Alias              │ Type       │ Name               │ Username        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  ● │ my-devhub ★ ⬡       │ Dev Hub    │ Acme Corp          │ admin@acme.com  │
│  ● │ uat-sandbox          │ Sandbox    │ UAT Environment    │ admin@acme.uat  │
│  ● │ dev-sandbox          │ Sandbox    │ Development        │ admin@acme.dev  │
│  ● │ feature-scratch      │ Scratch    │ Feature Branch     │ test-xyz@ex...  │
│  ● │ expired-org          │ Sandbox    │ Legacy Sandbox     │ admin@acme.leg  │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│ q Quit • r Refresh • Enter Open • a Re-auth • / Search                         │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Salesforce CLI (sf)** - [Install Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)

Verify Salesforce CLI installation:
```bash
sf --version
```

## Installation

### Option 1: Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) provides isolated environment installation for Python applications:

```bash
# Install pipx if not already available
brew install pipx  # macOS
# or: pip install pipx

# Install SF Orgs
pipx install git+https://github.com/Bilal-Bjo/SFORGS.git
```

### Option 2: Using pip

```bash
pip install git+https://github.com/Bilal-Bjo/SFORGS.git
```

### Option 3: From Source

```bash
git clone https://github.com/Bilal-Bjo/SFORGS.git
cd SFORGS
pipx install -e .
```

## Usage

Launch the application:

```bash
sforgs
```

### Keyboard Reference

| Key | Action |
|-----|--------|
| `↑` `↓` or `j` `k` | Navigate through org list |
| `Enter` or `o` | Open selected org in browser |
| `r` | Refresh org list |
| `a` | Re-authenticate selected org |
| `/` | Activate search filter |
| `Escape` | Clear search / Close search |
| `q` | Exit application |

### Status Indicators

| Indicator | Description |
|-----------|-------------|
| `●` (green) | Active session - org accessible |
| `●` (red) | Expired session - requires re-authentication |
| `★` | Default target org |
| `⬡` | Developer Hub org |

### Org Type Classification

| Type | Description |
|------|-------------|
| Production | Production Salesforce instances |
| Sandbox | Sandbox environments (Full, Partial, Developer) |
| Dev Hub | Developer Hub orgs for scratch org management |
| Scratch | Temporary scratch orgs for development |

## Technical Architecture

SF Orgs interfaces with the Salesforce CLI to retrieve org metadata and execute org operations:

1. **Data Retrieval** - Executes `sf org list --json` to enumerate authenticated orgs
2. **Session Validation** - Parses connection status to identify active and expired sessions
3. **Org Classification** - Analyzes org metadata to determine org type and role
4. **Browser Integration** - Invokes `sf org open -o <alias>` for org access
5. **Re-authentication** - Initiates `sf org login web` workflow for session renewal

## Dependencies

- [Textual](https://github.com/Textualize/textual) - Modern terminal user interface framework

## Troubleshooting

### Salesforce CLI Not Found

Ensure the Salesforce CLI is installed and available in your system PATH:
```bash
npm install -g @salesforce/cli
# or on macOS:
brew install sf
```

### No Authenticated Orgs

Authenticate with at least one Salesforce org:
```bash
# Production or Developer Hub
sf org login web

# Sandbox
sf org login web -r https://test.salesforce.com
```

### Expired Sessions

Select an org with an expired session and press `a` to initiate re-authentication through the browser-based login flow.

## Contributing

Contributions are welcome. Please follow standard pull request procedures:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with a clear description of changes

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Bilal Bjo** - [GitHub](https://github.com/Bilal-Bjo)
