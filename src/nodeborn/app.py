"""Application shell for Nodeborn."""

from __future__ import annotations

from typing import Any, Callable, ClassVar

from textual.app import App
from textual.screen import Screen

from nodeborn.colony.map_gen import generate_map
from nodeborn.colony.state import ColonyState, new_colony_state
from nodeborn.ui.screens.dashboard import DashboardScreen
from nodeborn.ui.screens.map_screen import MapScreen
from nodeborn.ui.theme import NODEBORN_THEME, NODEBORN_APP_THEME_VARIABLES


class NodebornApp(App[None]):
    """Main Textual application shell for Nodeborn."""

    _colony_state: ColonyState

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
        ("m", "open_map", "Map"),
        ("q", "quit", "Quit"),
    ]

    def get_theme_variable_defaults(self) -> dict[str, str]:
        """Expose app-specific CSS variables for all themes."""
        return {
            **super().get_theme_variable_defaults(),
            **NODEBORN_APP_THEME_VARIABLES,
        }

    def on_mount(self) -> None:
        """Register and activate the Nodeborn theme."""
        self.register_theme(NODEBORN_THEME)
        self.theme = NODEBORN_THEME.name
        colony_map = generate_map()
        self._colony_state = new_colony_state(colony_map)

    def action_open_map(self) -> None:
        """Push the map screen on top of the dashboard stack."""
        self.push_screen(MapScreen(self._colony_state))


def main() -> None:
    NodebornApp().run()


if __name__ == "__main__":
    main()
