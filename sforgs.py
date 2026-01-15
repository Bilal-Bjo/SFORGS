#!/usr/bin/env python3
"""
SF Orgs - A beautiful terminal app to manage and open Salesforce orgs

This tool provides a user-friendly terminal interface for managing Salesforce
org connections. It displays all authenticated orgs, their connection status,
and allows quick access to open them in the browser.

Author: Bilal Bjo
License: MIT
Repository: https://github.com/Bilal-Bjo/SFORGS
"""

import json
import subprocess
import sys

# =============================================================================
# DEPENDENCY HANDLING
# =============================================================================
# Automatically install required packages if not present
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    import questionary
    from questionary import Style
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "questionary", "-q"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    import questionary
    from questionary import Style

# =============================================================================
# CONFIGURATION
# =============================================================================

# Rich console instance for styled output
console = Console()

# Custom styling for the interactive questionary prompts
custom_style = Style([
    ('qmark', 'fg:cyan bold'),       # Question mark
    ('question', 'fg:white bold'),   # Question text
    ('answer', 'fg:cyan bold'),      # Selected answer
    ('pointer', 'fg:cyan bold'),     # Selection pointer (>)
    ('highlighted', 'fg:cyan bold'), # Highlighted option
    ('selected', 'fg:green'),        # Selected item
    ('separator', 'fg:gray'),        # Separator lines
    ('instruction', 'fg:gray'),      # Help text
])

# =============================================================================
# SALESFORCE CLI INTERACTION
# =============================================================================

def get_sf_orgs():
    """
    Fetch all authenticated Salesforce orgs using the SF CLI.

    Executes 'sf org list --json' and parses the JSON response.

    Returns:
        dict: The 'result' portion of the SF CLI response containing org data.

    Raises:
        SystemExit: If SF CLI is not found, times out, or returns invalid JSON.
    """
    try:
        result = subprocess.run(
            ["sf", "org", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("result", {})
    except FileNotFoundError:
        console.print("[red]Error: Salesforce CLI (sf) not found. Please install it first.[/red]")
        console.print("[dim]Visit: https://developer.salesforce.com/tools/salesforcecli[/dim]")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        console.print("[red]Error: Command timed out.[/red]")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print("[red]Error: Failed to parse SF CLI output.[/red]")
        sys.exit(1)


def open_org(org):
    """
    Open the selected Salesforce org in the default web browser.

    Uses 'sf org open' command to launch the org's setup page.

    Args:
        org (dict): Organization data containing 'alias' and 'username'.
    """
    # Prefer alias over username for cleaner commands
    alias_or_username = org["alias"] if org["alias"] != "-" else org["username"]

    console.print(f"\n[cyan]Opening[/cyan] [bold]{alias_or_username}[/bold] [cyan]in browser...[/cyan]\n")

    try:
        subprocess.run(
            ["sf", "org", "open", "-o", alias_or_username],
            check=True
        )
        console.print("[green]✓ Org opened successfully![/green]\n")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Failed to open org: {e}[/red]\n")


def reauth_org(org):
    """
    Re-authenticate an org with an expired session.

    Initiates the web login flow for the org, using the appropriate
    login URL based on org type (sandbox vs production).

    Args:
        org (dict): Organization data containing 'alias', 'username', and 'type'.
    """
    alias_or_username = org["alias"] if org["alias"] != "-" else org["username"]

    # Sandboxes use test.salesforce.com, production uses login.salesforce.com
    login_url = "test.salesforce.com" if org["type"] == "Sandbox" else "login.salesforce.com"

    console.print(f"\n[yellow]Re-authenticating[/yellow] [bold]{alias_or_username}[/bold]...\n")

    cmd = ["sf", "org", "login", "web", "-r", f"https://{login_url}"]

    # Preserve the alias if one exists
    if org["alias"] != "-":
        cmd.extend(["-a", org["alias"]])

    try:
        subprocess.run(cmd, check=True)
        console.print("[green]✓ Re-authentication successful![/green]\n")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Re-authentication failed: {e}[/red]\n")

# =============================================================================
# DATA PROCESSING
# =============================================================================

def parse_orgs(org_data):
    """
    Parse raw SF CLI org data into a unified, sorted list.

    Combines scratch orgs and non-scratch orgs, removes duplicates,
    and sorts by connection status (connected first) then by alias.

    Args:
        org_data (dict): Raw org data from SF CLI containing 'nonScratchOrgs'
                         and 'scratchOrgs' lists.

    Returns:
        list: List of org dictionaries with normalized fields.
    """
    orgs = []
    seen = set()  # Track usernames to avoid duplicates

    # Combine all org types into a single list
    all_orgs = (
        org_data.get("nonScratchOrgs", []) +
        org_data.get("scratchOrgs", [])
    )

    for org in all_orgs:
        username = org.get("username", "")

        # Skip duplicates (same org can appear in multiple lists)
        if username in seen:
            continue
        seen.add(username)

        # Extract and normalize org properties
        alias = org.get("alias", "-")
        status = org.get("connectedStatus", "Unknown")
        is_connected = status == "Connected"
        org_type = get_org_type(org)
        name = org.get("name", "-")
        instance_url = org.get("instanceUrl", "")

        orgs.append({
            "alias": alias,
            "username": username,
            "type": org_type,
            "name": name,
            "status": status,
            "is_connected": is_connected,
            "instance_url": instance_url,
            "is_default": org.get("isDefaultUsername", False),
            "is_dev_hub": org.get("isDevHub", False),
        })

    # Sort: connected orgs first, then alphabetically by alias
    orgs.sort(key=lambda x: (not x["is_connected"], x["alias"].lower()))
    return orgs


def get_org_type(org):
    """
    Determine the type of Salesforce org.

    Args:
        org (dict): Raw org data from SF CLI.

    Returns:
        str: One of 'Scratch', 'Dev Hub', 'Sandbox', or 'Production'.
    """
    if org.get("isScratch"):
        return "Scratch"
    elif org.get("isDevHub"):
        return "Dev Hub"
    elif org.get("isSandbox"):
        return "Sandbox"
    else:
        return "Production"

# =============================================================================
# USER INTERFACE
# =============================================================================

def display_header():
    """Display the application header banner."""
    header = Text()
    header.append("  SF ORGS  ", style="bold white on blue")
    header.append("  Salesforce Org Manager", style="dim")
    console.print()
    console.print(Panel(header, box=box.ROUNDED, border_style="blue"))
    console.print()


def display_orgs_table(orgs):
    """
    Display all orgs in a formatted table.

    Shows status (connected/expired), alias, type, name, and username
    with color-coded indicators for easy scanning.

    Args:
        orgs (list): List of parsed org dictionaries.
    """
    table = Table(
        box=box.ROUNDED,
        border_style="blue",
        header_style="bold cyan",
        show_lines=False,
        padding=(0, 1),
    )

    # Define table columns
    table.add_column("#", style="dim", width=3)
    table.add_column("Status", width=8, justify="center")
    table.add_column("Alias", style="bold", width=20)
    table.add_column("Type", width=10)
    table.add_column("Name", width=20)
    table.add_column("Username", style="dim")

    for i, org in enumerate(orgs, 1):
        # Status indicator: green dot for connected, red for expired
        status_icon = "[green]●[/green]" if org["is_connected"] else "[red]●[/red]"
        status_text = status_icon

        # Color alias based on connection status
        alias_style = "bold green" if org["is_connected"] else "bold red"
        alias_text = f"[{alias_style}]{org['alias']}[/{alias_style}]"

        # Add badges for default org and dev hub
        if org["is_default"]:
            alias_text += " [yellow]★[/yellow]"
        if org["is_dev_hub"]:
            alias_text += " [magenta](Hub)[/magenta]"

        # Color-code org types for quick identification
        type_style = {
            "Sandbox": "yellow",
            "Dev Hub": "magenta",
            "Scratch": "cyan",
            "Production": "green",
        }.get(org["type"], "white")

        table.add_row(
            str(i),
            status_text,
            alias_text,
            f"[{type_style}]{org['type']}[/{type_style}]",
            org["name"][:20] if org["name"] != "-" else "-",
            org["username"],
        )

    console.print(table)
    console.print()


def create_choices(orgs):
    """
    Create interactive choices for the org selector.

    Builds a list of questionary Choice objects, with expired orgs
    shown as disabled with a helpful message.

    Args:
        orgs (list): List of parsed org dictionaries.

    Returns:
        list: List of questionary Choice and Separator objects.
    """
    choices = []

    for org in orgs:
        # Visual indicator for connection status
        status = "✓" if org["is_connected"] else "✗"

        # Format display string with aligned columns
        display = f"{status} {org['alias']:<20} │ {org['type']:<10} │ {org['name'][:15]:<15}"

        choices.append(questionary.Choice(
            title=display,
            value=org,
            # Disable selection for expired orgs with helpful message
            disabled=None if org["is_connected"] else "Session expired - needs re-auth"
        ))

    # Add separator and exit option
    choices.append(questionary.Separator())
    choices.append(questionary.Choice(title="↩ Exit", value=None))

    return choices

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point for the SF Orgs application.

    Fetches authenticated orgs, displays them in a table, and provides
    an interactive selector to open orgs in the browser.
    """
    # Show app header
    display_header()

    # Fetch orgs with a loading spinner
    with console.status("[cyan]Fetching Salesforce orgs...[/cyan]", spinner="dots"):
        org_data = get_sf_orgs()
        orgs = parse_orgs(org_data)

    # Handle case when no orgs are authenticated
    if not orgs:
        console.print("[yellow]No authenticated orgs found.[/yellow]")
        console.print("Run [cyan]sf org login web[/cyan] to authenticate an org.\n")
        sys.exit(0)

    # Display summary statistics
    connected = sum(1 for o in orgs if o["is_connected"])
    expired = len(orgs) - connected

    summary = f"[green]{connected} connected[/green]"
    if expired > 0:
        summary += f"  [red]{expired} expired[/red]"
    console.print(f"  Found {len(orgs)} orgs: {summary}\n")

    # Display the orgs table
    display_orgs_table(orgs)

    # Show interactive selector
    console.print("[dim]Use arrow keys to navigate, Enter to select[/dim]\n")

    choices = create_choices(orgs)

    selected = questionary.select(
        "Select an org to open:",
        choices=choices,
        style=custom_style,
        use_shortcuts=False,
        use_arrow_keys=True,
    ).ask()

    # Handle user selection
    if selected is None:
        console.print("[dim]Goodbye![/dim]\n")
        sys.exit(0)

    if selected["is_connected"]:
        # Open the org in browser
        open_org(selected)
    else:
        # Offer to re-authenticate expired org
        if questionary.confirm(
            "This org's session has expired. Would you like to re-authenticate?",
            style=custom_style,
            default=True
        ).ask():
            reauth_org(selected)


if __name__ == "__main__":
    main()
