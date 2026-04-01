from __future__ import annotations

from textual.strip import Strip

from nodeborn.application.commands import PlaceBuildingCommand, place_building
from nodeborn.colony.building_specs import BuildingType, get_building_spec
from nodeborn.colony.map import ColonyMap

from nodeborn.colony.map_gen import generate_map
from nodeborn.colony.state import new_colony_state
from nodeborn.ui.widgets.map_view import (
    FALLBACK_VIEWPORT_HEIGHT,
    FALLBACK_VIEWPORT_WIDTH,
    MapView,
)
from tests.conftest import build_cycling_colony_state, build_uniform_colony_state
from tests.ui.conftest import MapViewHarness


async def test_map_view_mounts_without_error() -> None:
    app = MapViewHarness(build_cycling_colony_state())

    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(MapView)


async def test_map_view_render_contains_terrain_glyphs() -> None:
    app = MapViewHarness(build_cycling_colony_state())

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
    colony_state = new_colony_state(colony_map)
    map_view = MapView(colony_state)

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
    colony_state = new_colony_state(colony_map)
    map_view = MapView(colony_state)

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
    colony_state = new_colony_state(colony_map)
    map_view = MapView(colony_state)

    start_viewport_x = map_view.viewport_x
    start_viewport_y = map_view.viewport_y

    moved = map_view.move_cursor(25, 20)

    assert moved is True
    assert map_view.viewport_x > start_viewport_x
    assert map_view.viewport_y > start_viewport_y


def test_cursor_status_text_includes_coords_and_terrain(cycling_map: ColonyMap) -> None:
    colony_state = new_colony_state(cycling_map)
    map_view = MapView(colony_state)

    map_view.cursor_x = 0
    map_view.cursor_y = 0
    status = map_view.cursor_status_text()

    assert "Cursor (0, 0)" in status
    assert "Terrain:" in status
    assert "Fertility:" in status
    assert "Elevation:" in status
    assert "Buildable:" in status


async def test_ambient_animation_changes_water_glyph() -> None:
    app = MapViewHarness(build_cycling_colony_state(width=8, height=4))

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.query_one(MapView)

        map_view.viewport_x = 0
        map_view.viewport_y = 0
        map_view.ambient_phase = 0
        phase_zero = map_view.render_line(0)
        phase_zero_text = "".join(segment.text for segment in phase_zero)

        map_view.ambient_phase = 1
        phase_one = map_view.render_line(0)
        phase_one_text = "".join(segment.text for segment in phase_one)

        assert phase_zero_text != phase_one_text


async def test_map_view_renders_placed_building_glyph_across_footprint() -> None:
    colony_state = new_colony_state(generate_map(width=8, height=6, seed=0))
    result = place_building(
        colony_state,
        PlaceBuildingCommand(building_type=BuildingType.FARM, x=1, y=1),
    )

    assert result.success is True

    app = MapViewHarness(colony_state)

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.query_one(MapView)
        map_view.viewport_x = 0
        map_view.viewport_y = 0

        top_row = "".join(segment.text for segment in map_view.render_line(1))
        bottom_row = "".join(
            segment.text for segment in map_view.render_line(2))
        farm_glyph = get_building_spec(BuildingType.FARM).glyph

        assert top_row[1:3] == farm_glyph * 2
        assert bottom_row[1:3] == farm_glyph * 2


def test_cursor_status_text_includes_building_when_tile_is_occupied() -> None:
    colony_state = new_colony_state(generate_map(width=8, height=6, seed=0))
    result = place_building(
        colony_state,
        PlaceBuildingCommand(building_type=BuildingType.HOUSING, x=2, y=2),
    )

    assert result.success is True

    map_view = MapView(colony_state)
    map_view.cursor_x = 2
    map_view.cursor_y = 2

    status = map_view.cursor_status_text()

    assert "Building: Housing" in status
    assert "Progress: 0%" in status


async def test_ghost_preview_renders_selected_building_footprint_size() -> None:
    app = MapViewHarness(build_uniform_colony_state(width=8, height=6))

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.query_one(MapView)
        map_view.viewport_x = 0
        map_view.viewport_y = 0
        map_view.cursor_x = 1
        map_view.cursor_y = 1
        map_view.enter_build_mode(BuildingType.FARM)

        top_row = "".join(segment.text for segment in map_view.render_line(1))
        bottom_row = "".join(segment.text for segment in map_view.render_line(2))
        farm_glyph = get_building_spec(BuildingType.FARM).glyph

        assert top_row[1:3] == farm_glyph * 2
        assert bottom_row[1:3] == farm_glyph * 2
        assert top_row[3] != farm_glyph
        assert bottom_row[3] != farm_glyph
