from __future__ import annotations

import pytest

from nodeborn.colony.map import ColonyMap, TerrainType, Tile
from nodeborn.colony.state import ColonyState, new_colony_state


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


def build_cycling_colony_state(
    width: int = 8,
    height: int = 4,
    seed: int = 42,
) -> ColonyState:
    """Build a ColonyState with a cycling terrain map."""
    colony_map = build_cycling_map(width=width, height=height, seed=seed)
    return new_colony_state(colony_map)


def build_uniform_colony_state(
    width: int = 8,
    height: int = 4,
    terrain: TerrainType = TerrainType.GRASS,
    seed: int = 123,
) -> ColonyState:
    """Build a ColonyState with a uniform terrain map."""
    colony_map = build_uniform_map(
        width=width,
        height=height,
        terrain=terrain,
        seed=seed,
    )
    return new_colony_state(colony_map)


@pytest.fixture
def uniform_map() -> ColonyMap:
    """Fixture for a small uniform grass map."""
    return build_uniform_map()


@pytest.fixture
def cycling_map() -> ColonyMap:
    """Fixture for a small deterministic terrain-cycling map."""
    return build_cycling_map()
