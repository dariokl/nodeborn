from __future__ import annotations

from typing import Any, Callable, ClassVar

from textual.app import App, ComposeResult
from textual.screen import Screen

from nodeborn.colony.map import ColonyMap
from nodeborn.colony.map_gen import generate_map
from nodeborn.ui.screens.dashboard import DashboardScreen
from nodeborn.ui.screens.map_screen import MapScreen
from nodeborn.ui.widgets import MapView


class DashboardHarness(App[None]):
    """Minimal test app that mounts only the dashboard screen."""

    SCREENS = {"dashboard": DashboardScreen}
    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "dashboard": "dashboard",
    }
    DEFAULT_MODE = "dashboard"


class MapScreenHarness(App[None]):
    """Minimal test app that mounts only the map screen."""

    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "map": lambda: MapScreen(generate_map(width=64, height=48, seed=0)),
    }
    DEFAULT_MODE = "map"


class MapViewHarness(App[None]):
    """Minimal app that mounts a single MapView widget."""

    def __init__(self, colony_map: ColonyMap) -> None:
        super().__init__()
        self._colony_map = colony_map

    def compose(self) -> ComposeResult:
        yield MapView(self._colony_map)
