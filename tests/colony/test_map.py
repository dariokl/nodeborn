from __future__ import annotations

from nodeborn.colony import ColonyMap, TerrainType, Tile


def _make_map(width: int, height: int) -> ColonyMap:
    tiles = [
        [Tile(x=x, y=y, terrain=TerrainType.GRASS) for x in range(width)]
        for y in range(height)
    ]
    return ColonyMap(width=width, height=height, tiles=tiles, seed=123)


def test_terrain_type_glyph_mapping_is_complete() -> None:
    expected = {
        TerrainType.GRASS: ".",
        TerrainType.PLAINS: ",",
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
    colony_map = _make_map(width=3, height=2)

    assert colony_map.in_bounds(0, 0)
    assert colony_map.in_bounds(2, 1)

    assert not colony_map.in_bounds(-1, 0)
    assert not colony_map.in_bounds(0, -1)
    assert not colony_map.in_bounds(3, 0)
    assert not colony_map.in_bounds(0, 2)


def test_get_tile_returns_tile_when_in_bounds() -> None:
    colony_map = _make_map(width=3, height=2)

    tile = colony_map.get_tile(1, 0)

    assert tile is not None
    assert tile.x == 1
    assert tile.y == 0
    assert tile.terrain is TerrainType.GRASS


def test_get_tile_returns_none_when_out_of_bounds() -> None:
    colony_map = _make_map(width=3, height=2)

    assert colony_map.get_tile(-1, 0) is None
    assert colony_map.get_tile(3, 0) is None
    assert colony_map.get_tile(0, 2) is None
