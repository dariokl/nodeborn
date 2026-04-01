from __future__ import annotations

from rich.text import Text

from nodeborn.colony.building_specs import BuildingType
from nodeborn.colony.map import TerrainType
from nodeborn.colony.resources import Resource
from textual.widgets import Static

from nodeborn.ui.screens.map_screen import MapScreen
from nodeborn.ui.widgets import BuildPalette, MapView
from tests.conftest import build_uniform_colony_state
from tests.ui.conftest import MapScreenHarness


def _status_text(status_widget: Static) -> str:
    rendered = status_widget.render()
    if isinstance(rendered, Text):
        return rendered.plain
    return str(rendered)


async def test_map_screen_mounts_map_view_and_status() -> None:
    app = MapScreenHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, MapScreen)
        assert app.screen.query_one(MapView)
        status = app.screen.query_one("#map-status", Static)
        text = _status_text(status)
        assert "Cursor (" in text
        assert "Terrain:" in text


async def test_map_screen_arrow_keys_move_cursor_and_update_status() -> None:
    app = MapScreenHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.screen.query_one(MapView)
        start_x = map_view.cursor_x
        start_y = map_view.cursor_y

        await pilot.press("right", "down")
        await pilot.pause()

        assert map_view.cursor_x == start_x + 1
        assert map_view.cursor_y == start_y + 1

        status = app.screen.query_one("#map-status", Static)
        expected = f"Cursor ({map_view.cursor_x}, {map_view.cursor_y})"
        assert expected in _status_text(status)


async def test_map_screen_selecting_building_enters_build_mode() -> None:
    colony_state = build_uniform_colony_state(width=8, height=6)
    app = MapScreenHarness(colony_state)

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.screen.query_one(MapView)
        map_view.cursor_x = 1
        map_view.cursor_y = 1

        await pilot.press("b")
        await pilot.pause()
        assert app.screen.query_one(BuildPalette)

        await pilot.press("enter")
        await pilot.pause()

        assert map_view.build_mode is True
        assert map_view.selected_building_type is BuildingType.FARM
        assert list(app.screen.query(BuildPalette)) == []

        status = app.screen.query_one("#map-status", Static)
        text = _status_text(status)
        assert "Farm (2x2)" in text
        assert "VALID" in text


async def test_map_screen_confirm_placement_adds_building_and_deducts_resources() -> None:
    colony_state = build_uniform_colony_state(width=8, height=6)
    starting_wood = colony_state.stockpile.get(Resource.WOOD)
    app = MapScreenHarness(colony_state)

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.screen.query_one(MapView)
        map_view.cursor_x = 1
        map_view.cursor_y = 1

        await pilot.press("b", "enter", "enter")
        await pilot.pause()

        assert map_view.build_mode is False
        assert len(colony_state.buildings) == 1
        assert colony_state.buildings[0].building_type is BuildingType.FARM
        assert colony_state.stockpile.get(Resource.WOOD) == starting_wood - 50
        assert colony_state.colony_map.get_tile(1, 1).building_id is not None
        assert colony_state.colony_map.get_tile(2, 2).building_id is not None

        status = app.screen.query_one("#map-status", Static)
        text = _status_text(status)
        assert "Building: Farm" in text


async def test_map_screen_invalid_placement_is_rejected_with_reason() -> None:
    colony_state = build_uniform_colony_state(
        width=8,
        height=6,
        terrain=TerrainType.WATER,
    )
    starting_wood = colony_state.stockpile.get(Resource.WOOD)
    app = MapScreenHarness(colony_state)

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.screen.query_one(MapView)
        map_view.cursor_x = 1
        map_view.cursor_y = 1

        await pilot.press("b", "enter")
        await pilot.pause()

        assert map_view.build_mode is True
        assert map_view.is_placement_valid() is False

        status = app.screen.query_one("#map-status", Static)
        text = _status_text(status)
        assert "INVALID" in text
        assert "water" in text

        await pilot.press("enter")
        await pilot.pause()

        assert len(colony_state.buildings) == 0
        assert colony_state.stockpile.get(Resource.WOOD) == starting_wood
        assert map_view.build_mode is True
