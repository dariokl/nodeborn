from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from nodeborn.colony.map import ColonyMap, TerrainType

FALLBACK_VIEWPORT_WIDTH = 40
FALLBACK_VIEWPORT_HEIGHT = 20

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
        self.set_reactive(MapView.cursor_x, colony_map.width // 2)
        self.set_reactive(MapView.cursor_y, colony_map.height // 2)
        self._sync_viewport_to_cursor(
            FALLBACK_VIEWPORT_WIDTH, FALLBACK_VIEWPORT_HEIGHT)

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

    def _sync_viewport_to_cursor(self, viewport_width: int, viewport_height: int) -> None:
        width = max(1, min(viewport_width, self.colony_map.width))
        height = max(1, min(viewport_height, self.colony_map.height))

        max_viewport_x = max(0, self.colony_map.width - width)
        max_viewport_y = max(0, self.colony_map.height - height)

        target_x = self.cursor_x - (width // 2)
        target_y = self.cursor_y - (height // 2)

        self.viewport_x = max(0, min(target_x, max_viewport_x))
        self.viewport_y = max(0, min(target_y, max_viewport_y))

    def render(self) -> Text:
        width, height = self._current_viewport_size()
        self._sync_viewport_to_cursor(width, height)

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
