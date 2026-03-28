from __future__ import annotations

import pytest

from nodeborn.colony.map import ColonyMap, TerrainType, Tile


def build_uniform_map(
    width: int = 8,
    height: int = 4,
    terrain: TerrainType = TerrainType.GRASS,
    seed: int = 123,
) -> ColonyMap:
    """Build a map where every tile has the same terrain."""
    tiles = [
        [Tile(x=x, y=y, terrain=terrain) for x in range(width)]
        for y in range(height)
    ]
    return ColonyMap(width=width, height=height, tiles=tiles, seed=seed)


def build_cycling_map(
    width: int = 8,
    height: int = 4,
    seed: int = 42,
) -> ColonyMap:
    """Build a deterministic map that cycles through all terrain types."""
    terrain_cycle = [
        TerrainType.GRASS,
        TerrainType.PLAINS,
        TerrainType.WATER,
        TerrainType.MOUNTAIN,
        TerrainType.FOREST,
        TerrainType.SAND,
        TerrainType.ROCK,
        TerrainType.RIVER,
    ]
    tiles: list[list[Tile]] = []
    for y in range(height):
        row: list[Tile] = []
        for x in range(width):
            terrain = terrain_cycle[(x + y) % len(terrain_cycle)]
            row.append(Tile(x=x, y=y, terrain=terrain))
        tiles.append(row)
    return ColonyMap(width=width, height=height, tiles=tiles, seed=seed)


@pytest.fixture
def uniform_map() -> ColonyMap:
    """Fixture for a small uniform grass map."""
    return build_uniform_map()


@pytest.fixture
def cycling_map() -> ColonyMap:
    """Fixture for a small deterministic terrain-cycling map."""
    return build_cycling_map()
