from __future__ import annotations

from typing import Any, Callable, ClassVar

from textual.app import App, ComposeResult

from nodeborn.colony.map_gen import (
    DEFAULT_MAP_HEIGHT,
    DEFAULT_MAP_WIDTH,
    generate_map,
)
from nodeborn.colony.state import ColonyState, new_colony_state
from nodeborn.ui.screens.dashboard import DashboardScreen
from nodeborn.ui.screens.map_screen import MapScreen
from nodeborn.ui.theme import NODEBORN_APP_THEME_VARIABLES
from nodeborn.ui.widgets import MapView


class DashboardHarness(App[None]):
    """Minimal test app that mounts only the dashboard screen."""

    SCREENS = {"dashboard": DashboardScreen}
    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "dashboard": "dashboard",
    }
    DEFAULT_MODE = "dashboard"

    def get_theme_variable_defaults(self) -> dict[str, str]:
        return {
            **super().get_theme_variable_defaults(),
            **NODEBORN_APP_THEME_VARIABLES,
        }


def _create_test_colony_state():
    """Create a ColonyState for test harnesses."""
    colony_map = generate_map(
        width=DEFAULT_MAP_WIDTH,
        height=DEFAULT_MAP_HEIGHT,
        seed=0,
    )
    return new_colony_state(colony_map)


class MapScreenHarness(App[None]):
    """Minimal test app that mounts only the map screen."""

    def __init__(self, colony_state: ColonyState | None = None) -> None:
        super().__init__()
        self._colony_state = (
            _create_test_colony_state() if colony_state is None else colony_state
        )

    def get_theme_variable_defaults(self) -> dict[str, str]:
        return {
            **super().get_theme_variable_defaults(),
            **NODEBORN_APP_THEME_VARIABLES,
        }

    def on_mount(self) -> None:
        self.push_screen(MapScreen(self._colony_state))


class MapViewHarness(App[None]):
    """Minimal app that mounts a single MapView widget."""

    def __init__(self, colony_state: "ColonyState") -> None:
        super().__init__()
        self._colony_state = colony_state

    def get_theme_variable_defaults(self) -> dict[str, str]:
        return {
            **super().get_theme_variable_defaults(),
            **NODEBORN_APP_THEME_VARIABLES,
        }

    def compose(self) -> ComposeResult:
        yield MapView(self._colony_state)
