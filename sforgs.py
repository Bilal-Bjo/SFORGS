#!/usr/bin/env python3
"""
SF Orgs - Enterprise-grade terminal user interface for Salesforce org management

A full-featured TUI application that streamlines Salesforce org management by
providing administrators and developers with unified org visibility, session
management, and quick access through a keyboard-driven workflow.

Author: Bilal Bjo
License: MIT
Repository: https://github.com/Bilal-Bjo/SFORGS
"""

import json
import subprocess
import sys
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Input, Label, Static
from textual.worker import Worker, WorkerState


# =============================================================================
# SALESFORCE CLI INTERACTION
# =============================================================================

def get_sf_orgs() -> dict:
    """Fetch all authenticated Salesforce orgs using the SF CLI."""
    result = subprocess.run(
        ["sf", "org", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    data = json.loads(result.stdout)
    return data.get("result", {})


def open_org(alias_or_username: str) -> tuple[bool, str]:
    """Open the selected Salesforce org in the default web browser."""
    try:
        subprocess.run(
            ["sf", "org", "open", "-o", alias_or_username],
            check=True,
            capture_output=True
        )
        return True, f"Opened {alias_or_username}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to open org: {e}"


def reauth_org(alias_or_username: str, is_sandbox: bool) -> tuple[bool, str]:
    """Re-authenticate an org with an expired session."""
    login_url = "test.salesforce.com" if is_sandbox else "login.salesforce.com"
    cmd = ["sf", "org", "login", "web", "-r", f"https://{login_url}"]

    if alias_or_username and alias_or_username != "-":
        cmd.extend(["-a", alias_or_username])

    try:
        subprocess.run(cmd, check=True)
        return True, f"Re-authenticated {alias_or_username}"
    except subprocess.CalledProcessError as e:
        return False, f"Re-authentication failed: {e}"


# =============================================================================
# DATA PROCESSING
# =============================================================================

def get_org_type(org: dict) -> str:
    """Determine the type of Salesforce org."""
    if org.get("isScratch"):
        return "Scratch"
    elif org.get("isDevHub"):
        return "Dev Hub"
    elif org.get("isSandbox"):
        return "Sandbox"
    return "Production"


def parse_orgs(org_data: dict) -> list[dict]:
    """Parse raw SF CLI org data into a unified, sorted list."""
    orgs = []
    seen = set()

    all_orgs = (
        org_data.get("nonScratchOrgs", []) +
        org_data.get("scratchOrgs", [])
    )

    for org in all_orgs:
        username = org.get("username", "")
        if username in seen:
            continue
        seen.add(username)

        alias = org.get("alias", "-")
        status = org.get("connectedStatus", "Unknown")
        is_connected = status == "Connected"
        org_type = get_org_type(org)

        orgs.append({
            "alias": alias,
            "username": username,
            "type": org_type,
            "name": org.get("name", "-"),
            "status": status,
            "is_connected": is_connected,
            "instance_url": org.get("instanceUrl", ""),
            "is_default": org.get("isDefaultUsername", False),
            "is_dev_hub": org.get("isDevHub", False),
            "is_sandbox": org.get("isSandbox", False),
        })

    orgs.sort(key=lambda x: (not x["is_connected"], x["alias"].lower()))
    return orgs


# =============================================================================
# CUSTOM WIDGETS
# =============================================================================

class StatsBar(Static):
    """Displays connection statistics."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.connected = 0
        self.expired = 0
        self.total = 0

    def update_stats(self, orgs: list[dict]) -> None:
        self.total = len(orgs)
        self.connected = sum(1 for o in orgs if o["is_connected"])
        self.expired = self.total - self.connected
        self.refresh_display()

    def refresh_display(self) -> None:
        if self.total == 0:
            self.update("No orgs found")
        else:
            parts = [f"[bold]{self.total}[/bold] orgs"]
            if self.connected > 0:
                parts.append(f"[green]● {self.connected} connected[/green]")
            if self.expired > 0:
                parts.append(f"[red]● {self.expired} expired[/red]")
            self.update("  ".join(parts))


class SearchInput(Input):
    """Search input that appears when user presses /."""

    DEFAULT_CSS = """
    SearchInput {
        width: 100%;
        margin: 0;
    }
    """

    def __init__(self, id: str = "search-input") -> None:
        super().__init__(placeholder="Search orgs...", id=id)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

TCSS = """
Screen {
    background: $surface;
}

#main-container {
    width: 100%;
    height: 100%;
}

#stats-bar {
    dock: top;
    height: 1;
    padding: 0 1;
    background: $primary-background;
    color: $text;
}

#search-container {
    dock: top;
    height: auto;
    display: none;
    padding: 0 1;
}

#search-container.visible {
    display: block;
}

#table-container {
    width: 100%;
    height: 1fr;
    padding: 0 1;
}

DataTable {
    height: 100%;
}

DataTable > .datatable--cursor {
    background: $accent;
    color: $text;
}

DataTable > .datatable--header {
    background: $primary;
    color: $text;
    text-style: bold;
}

#loading-label {
    width: 100%;
    height: 100%;
    content-align: center middle;
    text-style: italic;
    color: $text-muted;
}

#no-orgs-label {
    width: 100%;
    height: 100%;
    content-align: center middle;
    color: $warning;
}

Footer {
    background: $primary-background;
}
"""


class SFOrgsApp(App):
    """Salesforce Org Manager - A beautiful terminal app."""

    TITLE = "SF ORGS"
    SUB_TITLE = "Salesforce Org Manager"
    CSS = TCSS

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "open_org", "Open", show=True),
        Binding("o", "open_org", "Open", show=False),
        Binding("a", "reauth", "Re-auth"),
        Binding("slash", "search", "Search"),
        Binding("escape", "clear_search", "Clear", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.orgs: list[dict] = []
        self.filtered_orgs: list[dict] = []
        self.search_query: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield StatsBar(id="stats-bar")
            with Container(id="search-container"):
                yield SearchInput()
            with Container(id="table-container"):
                yield Label("Loading orgs...", id="loading-label")
                yield DataTable(id="orgs-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        table = self.query_one("#orgs-table", DataTable)
        table.display = False
        self.load_orgs()

    @work(exclusive=True, thread=True)
    def load_orgs(self) -> list[dict]:
        """Load orgs in a background thread."""
        try:
            org_data = get_sf_orgs()
            return parse_orgs(org_data)
        except FileNotFoundError:
            return []
        except Exception:
            return []

    @on(Worker.StateChanged)
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion for load_orgs only."""
        if event.state == WorkerState.SUCCESS and event.worker.name == "load_orgs":
            self.orgs = event.worker.result or []
            self.filtered_orgs = self.orgs.copy()
            self.populate_table()

    def populate_table(self) -> None:
        """Populate the DataTable with org data."""
        loading = self.query_one("#loading-label", Label)
        table = self.query_one("#orgs-table", DataTable)
        stats = self.query_one("#stats-bar", StatsBar)

        loading.display = False
        table.display = True

        table.clear(columns=True)

        if not self.filtered_orgs:
            if self.search_query:
                loading.update("No matching orgs found")
            else:
                loading.update("No authenticated orgs. Run: sf org login web")
            loading.display = True
            table.display = False
            stats.update_stats([])
            return

        stats.update_stats(self.orgs)

        table.add_column("", key="status", width=3)
        table.add_column("Alias", key="alias", width=20)
        table.add_column("Type", key="type", width=12)
        table.add_column("Name", key="name", width=20)
        table.add_column("Username", key="username")

        for org in self.filtered_orgs:
            status_icon = "[green]●[/green]" if org["is_connected"] else "[red]●[/red]"

            alias_text = org["alias"]
            if org["is_default"]:
                alias_text += " [yellow]★[/yellow]"
            if org["is_dev_hub"]:
                alias_text += " [magenta]⬡[/magenta]"

            type_colors = {
                "Sandbox": "yellow",
                "Dev Hub": "magenta",
                "Scratch": "cyan",
                "Production": "green",
            }
            type_color = type_colors.get(org["type"], "white")
            type_text = f"[{type_color}]{org['type']}[/{type_color}]"

            name = org["name"][:18] + ".." if len(org["name"]) > 20 else org["name"]

            table.add_row(
                status_icon,
                alias_text,
                type_text,
                name,
                org["username"],
                key=org["username"],
            )

    def get_selected_org(self) -> Optional[dict]:
        """Get the currently selected org."""
        table = self.query_one("#orgs-table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(self.filtered_orgs):
            return self.filtered_orgs[table.cursor_row]
        return None

    def action_open_org(self) -> None:
        """Open the selected org in browser."""
        org = self.get_selected_org()
        if not org:
            self.notify("No org selected", severity="warning")
            return

        if not org["is_connected"]:
            self.notify("Session expired - press 'a' to re-authenticate", severity="warning")
            return

        alias_or_username = org["alias"] if org["alias"] != "-" else org["username"]
        self.notify(f"Opening {alias_or_username}...", severity="information")
        self.run_open_org(alias_or_username)

    @work(thread=True)
    def run_open_org(self, alias_or_username: str) -> None:
        """Run org open in background thread."""
        success, message = open_org(alias_or_username)
        self.call_from_thread(
            self.notify,
            message,
            severity="information" if success else "error"
        )

    def action_reauth(self) -> None:
        """Re-authenticate the selected org."""
        org = self.get_selected_org()
        if not org:
            self.notify("No org selected", severity="warning")
            return

        alias_or_username = org["alias"] if org["alias"] != "-" else org["username"]
        self.notify(f"Opening login page for {alias_or_username}...", severity="information")
        self.run_reauth_org(alias_or_username, org["is_sandbox"])

    @work(thread=True)
    def run_reauth_org(self, alias_or_username: str, is_sandbox: bool) -> None:
        """Run re-auth in background thread."""
        success, message = reauth_org(alias_or_username, is_sandbox)
        self.call_from_thread(
            self.notify,
            message,
            severity="information" if success else "error"
        )
        if success:
            self.call_from_thread(self.load_orgs)

    def action_refresh(self) -> None:
        """Refresh the org list."""
        loading = self.query_one("#loading-label", Label)
        table = self.query_one("#orgs-table", DataTable)

        loading.update("Refreshing...")
        loading.display = True
        table.display = False

        self.notify("Refreshing orgs...", severity="information")
        self.load_orgs()

    def action_search(self) -> None:
        """Show search input."""
        search_container = self.query_one("#search-container")
        search_input = self.query_one("#search-input", Input)
        search_container.add_class("visible")
        search_input.focus()

    def action_clear_search(self) -> None:
        """Clear search and hide input."""
        search_container = self.query_one("#search-container")
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        search_container.remove_class("visible")
        self.search_query = ""
        self.filtered_orgs = self.orgs.copy()
        self.populate_table()
        self.query_one("#orgs-table", DataTable).focus()

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Filter orgs based on search query."""
        self.search_query = event.value.lower()
        if not self.search_query:
            self.filtered_orgs = self.orgs.copy()
        else:
            self.filtered_orgs = [
                org for org in self.orgs
                if (self.search_query in org["alias"].lower() or
                    self.search_query in org["username"].lower() or
                    self.search_query in org["type"].lower() or
                    self.search_query in org["name"].lower())
            ]
        self.populate_table()

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self, event: Input.Submitted) -> None:
        """Focus table after search submit."""
        self.query_one("#orgs-table", DataTable).focus()

    def action_cursor_down(self) -> None:
        """Move cursor down (vim-style)."""
        table = self.query_one("#orgs-table", DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up (vim-style)."""
        table = self.query_one("#orgs-table", DataTable)
        table.action_cursor_up()

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle double-click on row."""
        self.action_open_org()


def main() -> None:
    """Main entry point."""
    try:
        app = SFOrgsApp()
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
