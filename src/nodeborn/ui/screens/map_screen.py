"""Map screen for map rendering and cursor navigation."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from nodeborn.application.commands import PlaceBuildingCommand, place_building
from nodeborn.colony.state import ColonyState
from nodeborn.ui.widgets import BuildPalette, MapView


class MapScreen(Screen[None]):
    """Interactive map screen with cursor movement and tile status."""

    CSS_PATH = "../styles/map.tcss"

    BINDINGS = [
        ("up", "cursor_up", "Up"),
        ("down", "cursor_down", "Down"),
        ("left", "cursor_left", "Left"),
        ("right", "cursor_right", "Right"),
        ("b", "open_build_palette", "Build"),
        ("enter", "confirm_placement", "Place"),
        ("escape", "back_or_cancel", "Back/Cancel"),
    ]

    def __init__(self, colony_state: ColonyState) -> None:
        super().__init__()
        self._colony_state = colony_state
        self._palette_open = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="map-layout"):
            yield MapView(self._colony_state, id="map-view")
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

    def action_open_build_palette(self) -> None:
        """Open the build palette to select a structure."""
        if self._palette_open:
            return
        self._palette_open = True
        palette = BuildPalette(self._colony_state.stockpile, id="build-palette")
        self.mount(palette)
        palette.focus()

    def action_confirm_placement(self) -> None:
        """Confirm building placement at current cursor position."""
        map_view = self.query_one(MapView)
        if not map_view.build_mode or map_view.selected_building_type is None:
            return
        if not map_view.is_placement_valid():
            self.notify("Cannot place here", severity="warning")
            return
        result = place_building(
            self._colony_state,
            PlaceBuildingCommand(
                building_type=map_view.selected_building_type,
                x=map_view.cursor_x,
                y=map_view.cursor_y,
            ),
        )
        if result.success:
            self.notify(f"Placed {map_view.selected_building_type.value}", severity="information")
            map_view.exit_build_mode()
        else:
            self.notify(f"Placement failed: {result.reason}", severity="error")
        self._refresh_status()
        map_view.refresh()

    def action_back_or_cancel(self) -> None:
        """Cancel build mode or palette, or dismiss the screen."""
        map_view = self.query_one(MapView)
        if self._palette_open:
            self._close_palette()
            return
        if map_view.build_mode:
            map_view.exit_build_mode()
            self._refresh_status()
            return
        self.dismiss()

    @on(BuildPalette.BuildingSelected)
    def _on_building_selected(self, event: BuildPalette.BuildingSelected) -> None:
        """Handle building selection from palette."""
        self._close_palette()
        map_view = self.query_one(MapView)
        map_view.enter_build_mode(event.building_type)
        map_view.focus()
        self._refresh_status()

    @on(BuildPalette.Cancelled)
    def _on_palette_cancelled(self, event: BuildPalette.Cancelled) -> None:
        """Handle palette cancellation."""
        self._close_palette()
        self.query_one(MapView).focus()

    def _close_palette(self) -> None:
        """Remove the build palette from the screen."""
        if not self._palette_open:
            return
        try:
            palette = self.query_one("#build-palette", BuildPalette)
            palette.remove()
        except Exception:
            pass
        self._palette_open = False

    def _move_cursor(self, dx: int, dy: int) -> None:
        map_view = self.query_one(MapView)
        map_view.move_cursor(dx, dy)
        self._refresh_status()

    def _refresh_status(self) -> None:
        map_view = self.query_one(MapView)
        status = self.query_one("#map-status", Static)
        status.update(map_view.cursor_status_text())
