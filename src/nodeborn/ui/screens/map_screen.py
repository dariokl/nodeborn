"""Map screen for map rendering and cursor navigation."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
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
        Binding("up", "cursor_up", "Up", show=True),
        Binding("down", "cursor_down", "Down", show=True),
        Binding("left", "cursor_left", "Left", show=True),
        Binding("right", "cursor_right", "Right", show=True),
        Binding("b", "open_build_palette", "Build"),
        Binding("enter", "confirm_placement", "Place"),
        Binding("escape", "back_or_cancel", "Cancel"),
    ]

    def __init__(self, colony_state: ColonyState) -> None:
        super().__init__()
        self._colony_state = colony_state

    @property
    def _palette_open(self) -> bool:
        """Whether the build palette is currently mounted in the DOM."""
        try:
            self.query_one("#build-palette", BuildPalette)
            return True
        except NoMatches:
            return False

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Control which actions appear in footer based on current mode."""
        map_view = self.query_one(MapView) if self.is_mounted else None
        in_build_mode = map_view.build_mode if map_view else False

        # Hide cursor movement when palette is open
        if action in ("cursor_up", "cursor_down", "cursor_left", "cursor_right"):
            return not self._palette_open
        if action == "open_build_palette":
            # Hide Build when palette is open or already in build mode
            return not self._palette_open and not in_build_mode
        if action == "confirm_placement":
            # Only show Place when in build mode
            return in_build_mode
        return True

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
        palette = BuildPalette(
            self._colony_state.stockpile, id="build-palette")
        self.mount(palette)
        palette.focus()
        self.refresh_bindings()

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
            self.notify(
                f"Placed {map_view.selected_building_type.value}", severity="information")
            map_view.exit_build_mode()
            self.refresh_bindings()
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
            self.refresh_bindings()
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
        self.refresh_bindings()

    @on(BuildPalette.Cancelled)
    def _on_palette_cancelled(self, event: BuildPalette.Cancelled) -> None:
        """Handle palette cancellation."""
        self._close_palette()
        self.refresh_bindings()
        self.query_one(MapView).focus()

    def _close_palette(self) -> None:
        """Remove the build palette from the screen."""
        if not self._palette_open:
            return
        try:
            palette = self.query_one("#build-palette", BuildPalette)
            palette.remove()
        except NoMatches:
            pass

    def _move_cursor(self, dx: int, dy: int) -> None:
        map_view = self.query_one(MapView)
        map_view.move_cursor(dx, dy)
        self._refresh_status()

    def _refresh_status(self) -> None:
        map_view = self.query_one(MapView)
        status = self.query_one("#map-status", Static)
        status.update(map_view.cursor_status_text())
