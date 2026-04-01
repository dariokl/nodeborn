from __future__ import annotations

from textual.app import App, ComposeResult

from nodeborn.colony import BuildingType, TerrainType, new_colony_state
from nodeborn.ui.widgets.build_palette import BuildPalette
from tests.conftest import build_uniform_map


class BuildPaletteHarness(App[None]):
    def __init__(self) -> None:
        super().__init__()
        colony_map = build_uniform_map(
            width=8, height=8, terrain=TerrainType.GRASS)
        self._state = new_colony_state(colony_map)
        self.selected_building_type: BuildingType | None = None
        self.cancelled = False

    def compose(self) -> ComposeResult:
        yield BuildPalette(self._state.stockpile, id="build-palette")

    def on_mount(self) -> None:
        self.query_one(BuildPalette).focus()

    def on_build_palette_building_selected(
        self,
        message: BuildPalette.BuildingSelected,
    ) -> None:
        self.selected_building_type = message.building_type

    def on_build_palette_cancelled(self, _message: BuildPalette.Cancelled) -> None:
        self.cancelled = True


async def test_build_palette_mounts_and_lists_all_specs() -> None:
    app = BuildPaletteHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        palette = app.query_one(BuildPalette)
        assert len(palette.specs) == len(BuildingType)
        assert palette.selected_building_type is BuildingType.FARM


async def test_build_palette_arrow_navigation_wraps_selection() -> None:
    app = BuildPaletteHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        palette = app.query_one(BuildPalette)

        await pilot.press("up")
        await pilot.pause()
        assert palette.selected_building_type is BuildingType.LUMBER_CAMP

        await pilot.press("down")
        await pilot.pause()
        assert palette.selected_building_type is BuildingType.FARM


async def test_build_palette_enter_posts_selected_message() -> None:
    app = BuildPaletteHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        assert app.selected_building_type is BuildingType.FARM


async def test_build_palette_escape_posts_cancel_message() -> None:
    app = BuildPaletteHarness()

    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()

        assert app.cancelled
