from __future__ import annotations

import pytest
from rich.text import Text
from textual.app import App
from textual.widgets import Static
from typing import Any, Callable, ClassVar

from textual.screen import Screen

from nodeborn.ui.screens.map_screen import MapScreen
from nodeborn.ui.widgets import MapView


def _status_text(status_widget: Static) -> str:
    rendered = status_widget.render()
    if isinstance(rendered, Text):
        return rendered.plain
    return str(rendered)


class MapScreenHarness(App[None]):
    """Minimal test app that mounts only the map screen."""

    SCREENS = {"map": MapScreen}
    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "map": "map",
    }
    DEFAULT_MODE = "map"


@pytest.mark.asyncio
async def test_map_screen_mounts_map_view_and_status() -> None:
    app = MapScreenHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, MapScreen)
        assert app.query_one(MapView)
        status = app.query_one("#map-status", Static)
        text = _status_text(status)
        assert "Cursor (" in text
        assert "Terrain:" in text


@pytest.mark.asyncio
async def test_map_screen_arrow_keys_move_cursor_and_update_status() -> None:
    app = MapScreenHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        map_view = app.query_one(MapView)
        start_x = map_view.cursor_x
        start_y = map_view.cursor_y

        await pilot.press("right", "down")
        await pilot.pause()

        assert map_view.cursor_x == start_x + 1
        assert map_view.cursor_y == start_y + 1

        status = app.query_one("#map-status", Static)
        expected = f"Cursor ({map_view.cursor_x}, {map_view.cursor_y})"
        assert expected in _status_text(status)
