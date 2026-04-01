from __future__ import annotations

import pytest

from nodeborn.colony.map import ColonyMap, Tile
from nodeborn.colony import TerrainType
from tests.conftest import build_uniform_map


def test_terrain_type_glyph_mapping_is_complete() -> None:
    expected = {
        TerrainType.GRASS: ".",
        TerrainType.PLAINS: ".",
        TerrainType.WATER: "≈",
        TerrainType.MOUNTAIN: "▲",
        TerrainType.FOREST: "♠",
        TerrainType.SAND: "░",
        TerrainType.ROCK: "█",
        TerrainType.RIVER: "~",
    }

    actual = {terrain: terrain.glyph for terrain in TerrainType}
    assert actual == expected


def test_colony_map_in_bounds_handles_edges() -> None:
    colony_map = build_uniform_map(width=3, height=2)

    assert colony_map.in_bounds(0, 0)
    assert colony_map.in_bounds(2, 1)

    assert not colony_map.in_bounds(-1, 0)
    assert not colony_map.in_bounds(0, -1)
    assert not colony_map.in_bounds(3, 0)
    assert not colony_map.in_bounds(0, 2)


def test_get_tile_returns_tile_when_in_bounds() -> None:
    colony_map = build_uniform_map(width=3, height=2)

    tile = colony_map.get_tile(1, 0)

    assert tile is not None
    assert tile.x == 1
    assert tile.y == 0
    assert tile.terrain is TerrainType.GRASS


def test_get_tile_returns_none_when_out_of_bounds() -> None:
    colony_map = build_uniform_map(width=3, height=2)

    assert colony_map.get_tile(-1, 0) is None
    assert colony_map.get_tile(3, 0) is None
    assert colony_map.get_tile(0, 2) is None


def test_tile_raises_when_fertility_out_of_range() -> None:
    with pytest.raises(ValueError, match="fertility must be between 0.0 and 1.0"):
        Tile(x=0, y=0, terrain=TerrainType.GRASS, fertility=1.1)

    with pytest.raises(ValueError, match="fertility must be between 0.0 and 1.0"):
        Tile(x=0, y=0, terrain=TerrainType.GRASS, fertility=-0.01)


def test_colony_map_raises_on_tile_grid_height_mismatch() -> None:
    valid_map = build_uniform_map(width=3, height=2)
    with pytest.raises(ValueError, match="tile grid height does not match map height"):
        ColonyMap(
            width=valid_map.width,
            height=valid_map.height,
            tiles=valid_map.tiles[:-1],
            seed=valid_map.seed,
        )


def test_colony_map_raises_on_tile_row_width_mismatch() -> None:
    valid_map = build_uniform_map(width=3, height=2)
    bad_tiles = [row[:] for row in valid_map.tiles]
    bad_tiles[0] = bad_tiles[0][:-1]

    with pytest.raises(ValueError, match="tile row 0 width does not match map width"):
        ColonyMap(
            width=valid_map.width,
            height=valid_map.height,
            tiles=bad_tiles,
            seed=valid_map.seed,
        )


def test_colony_map_raises_on_tile_coordinate_mismatch() -> None:
    valid_map = build_uniform_map(width=3, height=2)
    bad_tiles = [row[:] for row in valid_map.tiles]
    bad_tiles[1][2] = Tile(x=1, y=1, terrain=TerrainType.GRASS)

    with pytest.raises(ValueError, match=r"tile coordinate mismatch at \[1\]\[2\]"):
        ColonyMap(
            width=valid_map.width,
            height=valid_map.height,
            tiles=bad_tiles,
            seed=valid_map.seed,
        )


def test_place_building_on_footprint_marks_all_tiles() -> None:
    colony_map = build_uniform_map(width=5, height=4)

    colony_map.place_building_on_footprint(
        building_id="farm-1",
        x=1,
        y=1,
        width=2,
        height=2,
    )

    assert colony_map.get_tile(1, 1) is not None
    assert colony_map.get_tile(2, 1) is not None
    assert colony_map.get_tile(1, 2) is not None
    assert colony_map.get_tile(2, 2) is not None
    assert colony_map.get_tile(1, 1).building_id == "farm-1"
    assert colony_map.get_tile(2, 1).building_id == "farm-1"
    assert colony_map.get_tile(1, 2).building_id == "farm-1"
    assert colony_map.get_tile(2, 2).building_id == "farm-1"


def test_place_building_on_footprint_raises_when_out_of_bounds() -> None:
    colony_map = build_uniform_map(width=3, height=3)

    with pytest.raises(ValueError, match="building footprint is out of map bounds"):
        colony_map.place_building_on_footprint(
            building_id="farm-1",
            x=2,
            y=2,
            width=2,
            height=2,
        )
