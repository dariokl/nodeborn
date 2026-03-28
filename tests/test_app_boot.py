from __future__ import annotations

from textual.widgets import Footer, Header

from nodeborn.app import NodebornApp
from nodeborn.ui.screens.dashboard import DashboardScreen
from nodeborn.ui.screens.map_screen import MapScreen


async def test_app_boots_on_dashboard_screen() -> None:
    app = NodebornApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)
        assert app.query_one(Header)
        assert app.query_one(Footer)


async def test_app_navigation_dashboard_to_map_and_back() -> None:
    app = NodebornApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)

        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, MapScreen)

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)


def test_app_shell_has_placeholder_header_metadata() -> None:
    assert NodebornApp.TITLE == "Nodeborn"
    assert NodebornApp.SUB_TITLE == "Day 1 | Spring | Clear"
