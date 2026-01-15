# SF Orgs

A beautiful terminal application to manage and quickly open your Salesforce orgs.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)

## Overview

**SF Orgs** is a command-line tool that provides a user-friendly interface for managing your authenticated Salesforce organizations. Instead of remembering org aliases or typing lengthy commands, simply run `sforgs` and navigate through your orgs with arrow keys.

### Features

- **Beautiful UI** - Color-coded table showing all your orgs at a glance
- **Interactive Selection** - Navigate with arrow keys, press Enter to open
- **Connection Status** - Instantly see which orgs are connected vs expired
- **Smart Re-authentication** - Prompts to re-authenticate expired sessions
- **Org Type Detection** - Automatically identifies Sandbox, Production, Dev Hub, and Scratch orgs
- **Cross-platform** - Works on macOS, Linux, and Windows

## Screenshot

```
╭──────────────────────────────────────────────────────────────────────────────╮
│   SF ORGS    Salesforce Org Manager                                          │
╰──────────────────────────────────────────────────────────────────────────────╯

  Found 3 orgs: 2 connected  1 expired

╭─────┬──────────┬──────────────────────┬────────────┬──────────────────────╮
│ #   │  Status  │ Alias                │ Type       │ Name                 │
├─────┼──────────┼──────────────────────┼────────────┼──────────────────────┤
│ 1   │    ●     │ my-devhub (Hub)      │ Dev Hub    │ My Company           │
│ 2   │    ●     │ dev-sandbox          │ Sandbox    │ Development          │
│ 3   │    ●     │ expired-org          │ Sandbox    │ -                    │
╰─────┴──────────┴──────────────────────┴────────────┴──────────────────────╯

? Select an org to open:
 » ✓ my-devhub            │ Dev Hub    │ My Company
   ✓ dev-sandbox          │ Sandbox    │ Development
   ✗ expired-org          │ Sandbox    │ -  (Session expired)
   ---------------
   ↩ Exit
```

## Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Salesforce CLI (sf)** - [Install Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)

Verify Salesforce CLI is installed:
```bash
sf --version
```

## Installation

### Option 1: Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) installs Python applications in isolated environments:

```bash
# Install pipx if you don't have it
brew install pipx  # macOS
# or: pip install pipx

# Install sforgs
pipx install git+https://github.com/Bilal-Bjo/SFORGS.git
```

### Option 2: Using pip

```bash
pip install git+https://github.com/Bilal-Bjo/SFORGS.git
```

### Option 3: From Source

```bash
# Clone the repository
git clone https://github.com/Bilal-Bjo/SFORGS.git
cd SFORGS

# Install with pipx (recommended)
pipx install -e .

# Or install with pip
pip install -e .
```

## Usage

Simply run:

```bash
sforgs
```

### Controls

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate through orgs |
| `Enter` | Open selected org in browser |
| `Esc` / Select "Exit" | Quit the application |

### Status Indicators

| Symbol | Meaning |
|--------|---------|
| `●` (green) | Connected - ready to open |
| `●` (red) | Expired - needs re-authentication |
| `★` | Default org |
| `(Hub)` | Dev Hub org |

### Org Types

| Type | Color | Description |
|------|-------|-------------|
| Production | Green | Production orgs |
| Sandbox | Yellow | Sandbox environments |
| Dev Hub | Magenta | Developer Hub orgs |
| Scratch | Cyan | Scratch orgs |

## How It Works

1. **Fetches Orgs** - Runs `sf org list --json` to get all authenticated orgs
2. **Parses Data** - Extracts relevant information (alias, type, status, etc.)
3. **Displays Table** - Shows a color-coded table with all orgs
4. **Interactive Selection** - Lets you choose an org with arrow keys
5. **Opens Browser** - Runs `sf org open -o <alias>` to open the selected org

## Dependencies

- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [questionary](https://github.com/tmbo/questionary) - Interactive command-line prompts

## Troubleshooting

### "Salesforce CLI (sf) not found"

Make sure the Salesforce CLI is installed and in your PATH:
```bash
# Install Salesforce CLI
npm install -g @salesforce/cli

# Or on macOS with Homebrew
brew install sf
```

### "No authenticated orgs found"

Authenticate with a Salesforce org first:
```bash
# For production/dev hub
sf org login web

# For sandbox
sf org login web -r https://test.salesforce.com
```

### Session Expired

When you select an org with an expired session, SF Orgs will offer to re-authenticate. This opens the Salesforce login page in your browser.

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Bilal Bjo** - [GitHub](https://github.com/Bilal-Bjo)

## Acknowledgments

- [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) - The underlying CLI tool
- [Rich](https://github.com/Textualize/rich) - For beautiful terminal output
- [Questionary](https://github.com/tmbo/questionary) - For interactive prompts
