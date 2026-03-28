"""Map screen for map rendering and cursor navigation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from nodeborn.colony.map import ColonyMap
from nodeborn.ui.widgets import MapView


class MapScreen(Screen[None]):
    """Interactive map screen with cursor movement and tile status."""

    BINDINGS = [
        ("up", "cursor_up", "Up"),
        ("down", "cursor_down", "Down"),
        ("left", "cursor_left", "Left"),
        ("right", "cursor_right", "Right"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, colony_map: ColonyMap) -> None:
        super().__init__()
        self._colony_map = colony_map

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="map-layout"):
            yield MapView(self._colony_map, id="map-view")
            yield Static("", id="map-status")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_status()

    def action_cursor_up(self) -> None:
        self._move_cursor(0, -1)

    def action_cursor_down(self) -> None:
        self._move_cursor(0, 1)

    def action_cursor_left(self) -> None:
        self._move_cursor(-1, 0)

    def action_cursor_right(self) -> None:
        self._move_cursor(1, 0)

    def action_back(self) -> None:
        self.app.pop_screen()  # type: ignore # ignore type

    def _move_cursor(self, dx: int, dy: int) -> None:
        map_view = self.query_one(MapView)
        map_view.move_cursor(dx, dy)
        self._refresh_status()

    def _refresh_status(self) -> None:
        map_view = self.query_one(MapView)
        status = self.query_one("#map-status", Static)
        status.update(map_view.cursor_status_text())
