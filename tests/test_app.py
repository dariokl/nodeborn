from __future__ import annotations

import pytest
from textual.widgets import Footer, Header

from nodeborn.app import NodebornApp


@pytest.mark.asyncio
async def test_app_shell_mounts_header_and_footer() -> None:
    app = NodebornApp()

    async with app.run_test() as _pilot:
        assert app.query_one(Header)
        assert app.query_one(Footer)


def test_app_shell_has_placeholder_header_metadata() -> None:
    assert NodebornApp.TITLE == "Nodeborn"
    assert NodebornApp.SUB_TITLE == "Day 1 | Spring | Clear"
