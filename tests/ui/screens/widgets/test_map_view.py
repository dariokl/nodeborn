from __future__ import annotations

import pytest
from rich.text import Text
from textual.app import App, ComposeResult

from nodeborn.colony.map import ColonyMap, TerrainType, Tile
from nodeborn.colony.map_gen import generate_map
from nodeborn.ui.widgets.map_view import (
    FALLBACK_VIEWPORT_HEIGHT,
    FALLBACK_VIEWPORT_WIDTH,
    MapView,
)


def _sample_map(width: int = 8, height: int = 4) -> ColonyMap:
    terrain_cycle = [
        TerrainType.GRASS,
        TerrainType.PLAINS,
        TerrainType.WATER,
        TerrainType.MOUNTAIN,
        TerrainType.FOREST,
        TerrainType.SAND,
        TerrainType.ROCK,
        TerrainType.RIVER,
    ]
    tiles: list[list[Tile]] = []
    for y in range(height):
        row: list[Tile] = []
        for x in range(width):
            terrain = terrain_cycle[(x + y) % len(terrain_cycle)]
            row.append(Tile(x=x, y=y, terrain=terrain))
        tiles.append(row)
    return ColonyMap(width=width, height=height, tiles=tiles, seed=42)


class MapViewHarness(App[None]):
    """Minimal app that mounts a single MapView widget."""

    def __init__(self, colony_map: ColonyMap) -> None:
        super().__init__()
        self._colony_map = colony_map

    def compose(self) -> ComposeResult:
        yield MapView(self._colony_map)


@pytest.mark.asyncio
async def test_map_view_mounts_without_error() -> None:
    app = MapViewHarness(_sample_map())

    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(MapView)


@pytest.mark.asyncio
async def test_map_view_render_contains_terrain_glyphs() -> None:
    app = MapViewHarness(_sample_map())

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.query_one(MapView)
        renderable = map_view.render()
        assert isinstance(renderable, Text)
        assert "≈" in renderable.plain
        assert "▲" in renderable.plain
        assert "♠" in renderable.plain


def test_map_view_keeps_cursor_inside_viewport_window() -> None:
    colony_map = generate_map(width=64, height=48, seed=7)
    map_view = MapView(colony_map)

    map_view.cursor_x = 63
    map_view.cursor_y = 47
    _ = map_view.render()  # public path recalculates viewport

    assert map_view.viewport_x <= map_view.cursor_x < (
        map_view.viewport_x + FALLBACK_VIEWPORT_WIDTH
    )
    assert map_view.viewport_y <= map_view.cursor_y < (
        map_view.viewport_y + FALLBACK_VIEWPORT_HEIGHT
    )
