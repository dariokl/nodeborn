"""Application shell for Nodeborn."""

from __future__ import annotations

from typing import Any, Callable, ClassVar

from textual.app import App
from textual.screen import Screen

from nodeborn.ui.screens.dashboard import DashboardScreen
from nodeborn.ui.screens.map_screen import MapScreen
from nodeborn.ui.theme import NODEBORN_THEME


class NodebornApp(App[None]):
    """Main Textual application shell for Nodeborn."""

    CSS_PATH = [
        "ui/styles/app.tcss",
        "ui/styles/dashboard.tcss",
        "ui/styles/map.tcss",

    ]
    TITLE = "Nodeborn"
    SUB_TITLE = "Day 1 | Spring | Clear"
    SCREENS = {
        "dashboard": DashboardScreen,
        "map": MapScreen,
    }
    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "dashboard": "dashboard",
    }
    DEFAULT_MODE = "dashboard"
    BINDINGS = [
        ("m", "open_map", "Map"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Register and activate the Nodeborn theme."""
        self.register_theme(NODEBORN_THEME)
        self.theme = NODEBORN_THEME.name

    def action_open_map(self) -> None:
        """Push the map screen on top of the dashboard stack."""
        self.push_screen("map")


def main() -> None:
    NodebornApp().run()


if __name__ == "__main__":
    main()
