"""Application shell for Nodeborn."""

from __future__ import annotations

from textual.app import App

from nodeborn.ui.screens.dashboard import DashboardScreen
from nodeborn.ui.theme import NODEBORN_THEME
from typing import Any, Callable, ClassVar

from textual.app import App
from textual.screen import Screen


class NodebornApp(App[None]):
    """Top-level Textual app for the S0 shell."""

    CSS_PATH = [
        "ui/styles/app.tcss",
    ]
    TITLE = "Nodeborn"
    SUB_TITLE = "Day 1 | Spring | Clear"
    SCREENS = {
        "dashboard": DashboardScreen,
    }
    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "dashboard": "dashboard",
    }
    DEFAULT_MODE = "dashboard"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Register and activate the Nodeborn theme."""
        self.register_theme(NODEBORN_THEME)
        self.theme = NODEBORN_THEME.name
