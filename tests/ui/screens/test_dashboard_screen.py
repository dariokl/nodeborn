from __future__ import annotations

from textual.css.query import NoMatches
from textual.widgets import Footer, Header

from nodeborn.ui.screens.dashboard import DashboardScreen
from tests.ui.conftest import DashboardHarness


async def test_dashboard_screen_mounts_chrome() -> None:
    app = DashboardHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)
        assert app.query_one(Header)
        assert app.query_one(Footer)


async def test_dashboard_screen_mounts_all_placeholder_panels() -> None:
    app = DashboardHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        for panel_id in (
            "#panel-population",
            "#panel-resources",
            "#panel-alerts",
            "#panel-event-log",
        ):
            try:
                app.query_one(panel_id)
            except NoMatches as exc:  # pragma: no cover - assertion helper
                raise AssertionError(
                    f"Expected dashboard panel {panel_id} to be mounted"
                ) from exc
