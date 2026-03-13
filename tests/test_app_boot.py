from __future__ import annotations

import pytest
from textual.widgets import Footer, Header

from nodeborn.app import NodebornApp
from nodeborn.ui.screens.dashboard import DashboardScreen


@pytest.mark.asyncio
async def test_app_boots_on_dashboard_screen() -> None:
    app = NodebornApp()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)
        assert app.query_one(Header)
        assert app.query_one(Footer)


def test_app_shell_has_placeholder_header_metadata() -> None:
    assert NodebornApp.TITLE == "Nodeborn"
    assert NodebornApp.SUB_TITLE == "Day 1 | Spring | Clear"
