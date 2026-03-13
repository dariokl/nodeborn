from __future__ import annotations

import pytest
from textual.app import App
from textual.css.query import NoMatches
from textual.widgets import Footer, Header
from typing import Any, Callable, ClassVar

from textual.app import App
from textual.screen import Screen

from nodeborn.ui.screens.dashboard import DashboardScreen


class DashboardHarness(App[None]):
    """Minimal test app that mounts only the dashboard screen."""

    SCREENS = {"dashboard": DashboardScreen}
    MODES: ClassVar[dict[str, str | Callable[[], Screen[Any]]]] = {
        "dashboard": "dashboard",
    }
    DEFAULT_MODE = "dashboard"


@pytest.mark.asyncio
async def test_dashboard_screen_mounts_chrome() -> None:
    app = DashboardHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)
        assert app.query_one(Header)
        assert app.query_one(Footer)


@pytest.mark.asyncio
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
