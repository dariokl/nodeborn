"""Application shell for Nodeborn."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from nodeborn.ui.theme import NODEBORN_THEME


class NodebornApp(App[None]):
    """Top-level Textual app for the S0 shell."""

    CSS_PATH = [
        "ui/styles/app.tcss",
    ]
    TITLE = "Nodeborn"
    SUB_TITLE = "Day 1 | Spring | Clear"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the global app chrome."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Register and activate the Nodeborn theme."""
        self.register_theme(NODEBORN_THEME)
        self.theme = NODEBORN_THEME.name
