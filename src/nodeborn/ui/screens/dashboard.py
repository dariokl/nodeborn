"""Dashboard screen for the Nodeborn app shell."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class DashboardPanel(Static):
    """Bordered placeholder panel used in the dashboard layout."""

    def __init__(self, title: str, placeholder: str, panel_id: str) -> None:
        super().__init__(placeholder, id=panel_id, classes="dashboard-panel")
        self.border_title = title


class DashboardScreen(Screen[None]):
    """Default screen with placeholder dashboard panels."""

    CSS_PATH = "../styles/dashboard.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="dashboard-grid"):
            yield DashboardPanel(
                "Population",
                "Villager metrics and workforce overview will appear here.",
                panel_id="panel-population",
            )
            yield DashboardPanel(
                "Resources",
                "Resource stockpile, trends, and efficiency indicators will appear here.",
                panel_id="panel-resources",
            )
            yield DashboardPanel(
                "Alerts",
                "Warnings, shortages, and incident summaries will appear here.",
                panel_id="panel-alerts",
            )
            yield DashboardPanel(
                "Event Log",
                "Recent colony events and timeline entries will appear here.",
                panel_id="panel-event-log",
            )
        yield Footer()
