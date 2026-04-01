from __future__ import annotations

from typing import cast

from rich.segment import Segment
from rich.style import Style
from textual.reactive import Reactive, reactive
from textual.scroll_view import ScrollView
from textual.strip import Strip

from nodeborn.colony.building_specs import BuildingType, get_building_spec
from nodeborn.colony.map import ColonyMap, TerrainType, Tile
from nodeborn.colony.state import ColonyState
from nodeborn.simulation.placement import validate_placement

FALLBACK_VIEWPORT_WIDTH = 40
FALLBACK_VIEWPORT_HEIGHT = 20
VIEWPORT_EDGE_MARGIN = 4

TERRAIN_COMPONENTS: dict[TerrainType, str] = {
    TerrainType.GRASS: "mapview--grass",
    TerrainType.PLAINS: "mapview--plains",
    TerrainType.WATER: "mapview--water",
    TerrainType.MOUNTAIN: "mapview--mountain",
    TerrainType.FOREST: "mapview--forest",
    TerrainType.SAND: "mapview--sand",
    TerrainType.ROCK: "mapview--rock",
    TerrainType.RIVER: "mapview--river",
}


class MapView(ScrollView):
    """Render a map viewport centered around the current cursor."""

    # Disable ScrollView's default arrow key bindings — we handle cursor via MapScreen
    BINDINGS = []

    COMPONENT_CLASSES = {
        "mapview--grass",
        "mapview--plains",
        "mapview--water",
        "mapview--mountain",
        "mapview--forest",
        "mapview--sand",
        "mapview--rock",
        "mapview--river",
        "mapview--cursor-strong",
        "mapview--cursor-soft",
        "mapview--ghost-valid",
        "mapview--ghost-invalid",
    }

    DEFAULT_CSS = """
    MapView {
        width: 1fr;
        height: 1fr;
    }
    """

    cursor_x = reactive(0)
    cursor_y = reactive(0)
    viewport_x = reactive(0)
    viewport_y = reactive(0)
    ambient_phase = reactive(0)
    cursor_pulse_on = reactive(True)
    build_mode: reactive[bool] = reactive(False)
    selected_building_type: reactive[BuildingType | None] = reactive(None)

    def __init__(
        self,
        colony_state: ColonyState,
        *,
        id: str | None = "map-view",
    ) -> None:
        super().__init__(id=id)
        self._colony_state = colony_state
        self.set_reactive(
            cast(Reactive[int], MapView.cursor_x), self.colony_map.width // 2)
        self.set_reactive(
            cast(Reactive[int], MapView.cursor_y), self.colony_map.height // 2)
        self._center_viewport_on_cursor(
            FALLBACK_VIEWPORT_WIDTH, FALLBACK_VIEWPORT_HEIGHT)
        # Cached placement validation result (valid, reason)
        self._placement_result: tuple[bool, str] = (True, "")

    @property
    def colony_map(self) -> ColonyMap:
        """Access the underlying colony map."""
        return self._colony_state.colony_map

    @property
    def colony_state(self) -> ColonyState:
        """Access the full colony state for placement validation."""
        return self._colony_state

    def on_mount(self) -> None:
        """Start lightweight ambient animation loops for map liveliness."""
        self.set_interval(0.50, self._advance_ambient_phase)
        self.set_interval(0.35, self._toggle_cursor_pulse)

    def move_cursor(self, dx: int, dy: int) -> bool:
        """Move cursor by delta, clamped to map bounds."""
        next_x = self._clamp(self.cursor_x + dx, 0, self.colony_map.width - 1)
        next_y = self._clamp(self.cursor_y + dy, 0, self.colony_map.height - 1)
        moved = next_x != self.cursor_x or next_y != self.cursor_y
        if moved:
            self.cursor_x = next_x
            self.cursor_y = next_y
        return moved

    def cursor_tile(self) -> Tile:
        """Return the tile currently under the cursor."""
        tile = self.colony_map.get_tile(self.cursor_x, self.cursor_y)
        if tile is None:  # pragma: no cover - defensive check
            raise RuntimeError("Cursor is out of map bounds")
        return tile

    def cursor_status_text(self) -> str:
        """Human-readable status text for bottom status bars."""
        tile = self.cursor_tile()
        if self.build_mode and self.selected_building_type is not None:
            spec = get_building_spec(self.selected_building_type)
            valid, reason = self._placement_result
            status_icon = "✓" if valid else "✗"
            status_style = "VALID" if valid else "INVALID"
            return (
                f"{spec.name} ({spec.width}x{spec.height}) at ({tile.x}, {tile.y}) — "
                f"{status_style} {status_icon} {reason}"
            )
        return (
            f"Cursor ({tile.x}, {tile.y}) | "
            f"Terrain: {tile.terrain.value.title()} | "
            f"Fertility: {tile.fertility:.2f} | "
            f"Elevation: {tile.elevation:.2f} | "
            f"Buildable: {self._buildability_label(tile.terrain)}"
        )

    def enter_build_mode(self, building_type: BuildingType) -> None:
        """Enter build mode with the specified building type selected."""
        self.selected_building_type = building_type
        self.build_mode = True
        self._revalidate_placement()

    def exit_build_mode(self) -> None:
        """Exit build mode and clear selection."""
        self.build_mode = False
        self.selected_building_type = None
        self._placement_result = (True, "")
        self.refresh()

    def is_placement_valid(self) -> bool:
        """Return True if current cursor position is valid for placement."""
        return self._placement_result[0]

    def _revalidate_placement(self) -> None:
        """Re-run placement validation at current cursor position."""
        if not self.build_mode or self.selected_building_type is None:
            self._placement_result = (True, "")
            return
        valid, reason = validate_placement(
            self._colony_state,
            self.selected_building_type,
            self.cursor_x,
            self.cursor_y,
        )
        self._placement_result = (valid, reason)
        self.refresh()

    def _ghost_footprint_tiles(self) -> set[tuple[int, int]]:
        """Return set of (x, y) tiles covered by ghost footprint."""
        if not self.build_mode or self.selected_building_type is None:
            return set()
        spec = get_building_spec(self.selected_building_type)
        tiles: set[tuple[int, int]] = set()
        for dy in range(spec.height):
            for dx in range(spec.width):
                tiles.add((self.cursor_x + dx, self.cursor_y + dy))
        return tiles

    def _buildability_label(self, terrain: TerrainType) -> str:
        if terrain in {TerrainType.GRASS, TerrainType.PLAINS, TerrainType.SAND}:
            return "Yes"
        if terrain is TerrainType.FOREST:
            return "Conditional (clear first)"
        return "No"

    def _advance_ambient_phase(self) -> None:
        self.ambient_phase = (self.ambient_phase + 1) % 4
        self.refresh()

    def _toggle_cursor_pulse(self) -> None:
        self.cursor_pulse_on = not self.cursor_pulse_on
        self.refresh()

    def _animated_glyph(self, tile: Tile, map_x: int, map_y: int) -> str:
        if tile.terrain is TerrainType.WATER:
            return "≈" if (self.ambient_phase + map_x + map_y) % 2 == 0 else "∼"
        if tile.terrain is TerrainType.RIVER:
            return "~" if (self.ambient_phase + map_x) % 2 == 0 else "≈"
        if tile.terrain is TerrainType.FOREST:
            return "♠" if (self.ambient_phase + map_y) % 3 != 0 else "♣"
        return tile.terrain.glyph

    def watch_cursor_x(self, _old: int, _new: int) -> None:
        width, height = self._current_viewport_size()
        self._sync_viewport_to_cursor(width, height)
        self._revalidate_placement()
        self.refresh()

    def watch_cursor_y(self, _old: int, _new: int) -> None:
        width, height = self._current_viewport_size()
        self._sync_viewport_to_cursor(width, height)
        self._revalidate_placement()
        self.refresh()

    def watch_build_mode(self, _old: bool, _new: bool) -> None:
        self._revalidate_placement()

    def watch_selected_building_type(
        self, _old: BuildingType | None, _new: BuildingType | None
    ) -> None:
        self._revalidate_placement()

    def on_resize(self) -> None:
        """Keep viewport aligned when terminal size changes."""
        width, height = self._current_viewport_size()
        self._sync_viewport_to_cursor(width, height)
        self.refresh()

    def _current_viewport_size(self) -> tuple[int, int]:
        width = self.size.width if self.size.width > 0 else FALLBACK_VIEWPORT_WIDTH
        height = self.size.height if self.size.height > 0 else FALLBACK_VIEWPORT_HEIGHT
        width = max(1, min(width, self.colony_map.width))
        height = max(1, min(height, self.colony_map.height))
        return width, height

    def _center_viewport_on_cursor(self, viewport_width: int, viewport_height: int) -> None:
        width = max(1, min(viewport_width, self.colony_map.width))
        height = max(1, min(viewport_height, self.colony_map.height))
        max_viewport_x = max(0, self.colony_map.width - width)
        max_viewport_y = max(0, self.colony_map.height - height)
        self.viewport_x = self._clamp(
            self.cursor_x - (width // 2), 0, max_viewport_x)
        self.viewport_y = self._clamp(
            self.cursor_y - (height // 2), 0, max_viewport_y)

    def _sync_viewport_to_cursor(self, viewport_width: int, viewport_height: int) -> None:
        width = max(1, min(viewport_width, self.colony_map.width))
        height = max(1, min(viewport_height, self.colony_map.height))

        max_viewport_x = max(0, self.colony_map.width - width)
        max_viewport_y = max(0, self.colony_map.height - height)

        margin_x = min(VIEWPORT_EDGE_MARGIN, max(0, width // 3))
        margin_y = min(VIEWPORT_EDGE_MARGIN, max(0, height // 3))

        target_x = self.viewport_x
        target_y = self.viewport_y

        left_limit = self.viewport_x + margin_x
        right_limit = self.viewport_x + (width - 1 - margin_x)
        top_limit = self.viewport_y + margin_y
        bottom_limit = self.viewport_y + (height - 1 - margin_y)

        if self.cursor_x < left_limit:
            target_x = self.cursor_x - margin_x
        elif self.cursor_x > right_limit:
            target_x = self.cursor_x - (width - 1 - margin_x)

        if self.cursor_y < top_limit:
            target_y = self.cursor_y - margin_y
        elif self.cursor_y > bottom_limit:
            target_y = self.cursor_y - (height - 1 - margin_y)

        self.viewport_x = self._clamp(target_x, 0, max_viewport_x)
        self.viewport_y = self._clamp(target_y, 0, max_viewport_y)

    @staticmethod
    def _clamp(value: int, low: int, high: int) -> int:
        return max(low, min(value, high))

    def render_line(self, y: int) -> Strip:
        width, height = self._current_viewport_size()

        if y < 0 or y >= height:
            return Strip.blank(width)

        map_y = self.viewport_y + y
        segments: list[Segment] = []

        # Pre-compute ghost footprint for this render pass
        ghost_tiles = self._ghost_footprint_tiles()
        ghost_valid = self._placement_result[0] if ghost_tiles else True
        ghost_glyph: str | None = None
        if self.build_mode and self.selected_building_type is not None:
            ghost_glyph = get_building_spec(self.selected_building_type).glyph

        for offset_x in range(width):
            map_x = self.viewport_x + offset_x
            tile = self.colony_map.get_tile(map_x, map_y)
            if tile is None:
                segments.append(Segment(" "))
                continue

            component = TERRAIN_COMPONENTS[tile.terrain]
            style = self.get_component_rich_style(component)

            # Ghost footprint rendering
            is_ghost_tile = (map_x, map_y) in ghost_tiles
            is_cursor_tile = map_x == self.cursor_x and map_y == self.cursor_y

            if is_ghost_tile and ghost_glyph is not None:
                # Use ghost style (green valid / red invalid)
                ghost_component = (
                    "mapview--ghost-valid" if ghost_valid else "mapview--ghost-invalid"
                )
                ghost_style = self.get_component_rich_style(ghost_component)
                style = ghost_style
                # Add pulsing effect to the anchor tile (cursor position)
                if is_cursor_tile:
                    cursor_component = (
                        "mapview--cursor-strong" if self.cursor_pulse_on
                        else "mapview--cursor-soft"
                    )
                    cursor_style = self.get_component_rich_style(
                        cursor_component)
                    style = style + cursor_style + Style(bold=True)
                segments.append(Segment(ghost_glyph, style=style))
            elif is_cursor_tile:
                # Normal cursor highlight (not in build mode)
                cursor_component = (
                    "mapview--cursor-strong" if self.cursor_pulse_on
                    else "mapview--cursor-soft"
                )
                cursor_style = self.get_component_rich_style(cursor_component)
                style = style + cursor_style + Style(reverse=True, bold=True)
                segments.append(Segment(self._animated_glyph(
                    tile, map_x, map_y), style=style))
            else:
                # Normal terrain tile
                segments.append(Segment(self._animated_glyph(
                    tile, map_x, map_y), style=style))

        return Strip(segments, width)
