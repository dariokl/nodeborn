from __future__ import annotations

from typing import cast

from rich.text import Text
from textual.reactive import Reactive, reactive
from textual.widget import Widget

from nodeborn.colony.map import ColonyMap, TerrainType, Tile

FALLBACK_VIEWPORT_WIDTH = 40
FALLBACK_VIEWPORT_HEIGHT = 20
VIEWPORT_EDGE_MARGIN = 4

TERRAIN_STYLES: dict[TerrainType, str] = {
    TerrainType.GRASS: "#7FB069",
    TerrainType.PLAINS: "#D1B97F",
    TerrainType.WATER: "#5FA8D3",
    TerrainType.MOUNTAIN: "#A3A3A3",
    TerrainType.FOREST: "#2D6A4F",
    TerrainType.SAND: "#E9D8A6",
    TerrainType.ROCK: "#6C757D",
    TerrainType.RIVER: "#4EA8DE",
}


class MapView(Widget):
    """Render a map viewport centered around the current cursor."""

    colony_map: ColonyMap

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

    def __init__(self, colony_map: ColonyMap, *, id: str | None = "map-view") -> None:
        super().__init__(id=id)
        self.colony_map = colony_map
        self.set_reactive(
            cast(Reactive[int], MapView.cursor_x), colony_map.width // 2)
        self.set_reactive(
            cast(Reactive[int], MapView.cursor_y), colony_map.height // 2)
        self._center_viewport_on_cursor(
            FALLBACK_VIEWPORT_WIDTH, FALLBACK_VIEWPORT_HEIGHT)

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
        return f"Cursor ({tile.x}, {tile.y}) | Terrain: {tile.terrain.value.title()}"

    def watch_cursor_x(self, _old: int, _new: int) -> None:
        width, height = self._current_viewport_size()
        self._sync_viewport_to_cursor(width, height)
        self.refresh()

    def watch_cursor_y(self, _old: int, _new: int) -> None:
        width, height = self._current_viewport_size()
        self._sync_viewport_to_cursor(width, height)
        self.refresh()

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

    def render(self) -> Text:
        width, height = self._current_viewport_size()

        canvas = Text()
        for offset_y in range(height):
            y = self.viewport_y + offset_y
            for offset_x in range(width):
                x = self.viewport_x + offset_x
                tile = self.colony_map.get_tile(x, y)
                if tile is None:
                    canvas.append(" ")
                    continue

                glyph = tile.terrain.glyph
                style = TERRAIN_STYLES[tile.terrain]
                if x == self.cursor_x and y == self.cursor_y:
                    style = f"{style} reverse bold"
                canvas.append(glyph, style=style)

            if offset_y < (height - 1):
                canvas.append("\n")

        return canvas
