from __future__ import annotations

from textual.strip import Strip
from nodeborn.colony.map import ColonyMap

from nodeborn.colony.map_gen import generate_map
from nodeborn.ui.widgets.map_view import (
    FALLBACK_VIEWPORT_HEIGHT,
    FALLBACK_VIEWPORT_WIDTH,
    MapView,
)
from tests.conftest import build_cycling_map
from tests.ui.conftest import MapViewHarness


async def test_map_view_mounts_without_error() -> None:
    app = MapViewHarness(build_cycling_map())

    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(MapView)


async def test_map_view_render_contains_terrain_glyphs() -> None:
    app = MapViewHarness(build_cycling_map())

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.query_one(MapView)
        height = max(1, map_view.size.height)
        strips = [map_view.render_line(y) for y in range(height)]

        assert all(isinstance(strip, Strip) for strip in strips)

        rendered_text = "\n".join(
            "".join(segment.text for segment in strip)
            for strip in strips
        )
        assert "≈" in rendered_text
        assert "▲" in rendered_text
        assert "♠" in rendered_text


def test_map_view_keeps_cursor_inside_viewport_window() -> None:
    colony_map = generate_map(width=64, height=48, seed=7)
    map_view = MapView(colony_map)

    map_view.cursor_x = 63
    map_view.cursor_y = 47

    assert map_view.viewport_x <= map_view.cursor_x < (
        map_view.viewport_x + FALLBACK_VIEWPORT_WIDTH
    )
    assert map_view.viewport_y <= map_view.cursor_y < (
        map_view.viewport_y + FALLBACK_VIEWPORT_HEIGHT
    )


def test_move_cursor_clamps_to_map_bounds() -> None:
    colony_map = generate_map(width=8, height=6, seed=123)
    map_view = MapView(colony_map)

    map_view.cursor_x = 0
    map_view.cursor_y = 0
    moved = map_view.move_cursor(-10, -10)

    assert moved is False
    assert map_view.cursor_x == 0
    assert map_view.cursor_y == 0

    moved = map_view.move_cursor(999, 999)
    assert moved is True
    assert map_view.cursor_x == colony_map.width - 1
    assert map_view.cursor_y == colony_map.height - 1


def test_move_cursor_auto_scrolls_viewport_near_edge() -> None:
    colony_map = generate_map(width=64, height=48, seed=456)
    map_view = MapView(colony_map)

    start_viewport_x = map_view.viewport_x
    start_viewport_y = map_view.viewport_y

    moved = map_view.move_cursor(25, 20)

    assert moved is True
    assert map_view.viewport_x > start_viewport_x
    assert map_view.viewport_y > start_viewport_y


def test_cursor_status_text_includes_coords_and_terrain(cycling_map: ColonyMap) -> None:
    colony_map = cycling_map
    map_view = MapView(colony_map)

    map_view.cursor_x = 0
    map_view.cursor_y = 0
    status = map_view.cursor_status_text()

    assert "Cursor (0, 0)" in status
    assert "Terrain:" in status
