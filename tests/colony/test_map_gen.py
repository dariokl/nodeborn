from __future__ import annotations

import pytest

from nodeborn.colony.map import ColonyMap, TerrainType
from nodeborn.colony.map_gen import DEFAULT_MAP_HEIGHT, DEFAULT_MAP_WIDTH, generate_map


def _terrain_rows(colony_map: ColonyMap) -> list[list[TerrainType]]:
    return [[tile.terrain for tile in row] for row in colony_map.tiles]


def test_generate_map_uses_default_dimensions() -> None:
    colony_map = generate_map()

    assert colony_map.width == DEFAULT_MAP_WIDTH
    assert colony_map.height == DEFAULT_MAP_HEIGHT


def test_generate_map_is_deterministic_for_same_seed() -> None:
    map_a = generate_map(width=40, height=30, seed=12345)
    map_b = generate_map(width=40, height=30, seed=12345)

    assert _terrain_rows(map_a) == _terrain_rows(map_b)


def test_generate_map_contains_key_terrain_categories() -> None:
    colony_map = generate_map(width=64, height=48, seed=9876)
    terrains = {tile.terrain for row in colony_map.tiles for tile in row}

    assert TerrainType.WATER in terrains
    assert TerrainType.MOUNTAIN in terrains
    assert TerrainType.FOREST in terrains


def test_starting_area_is_buildable_near_map_center() -> None:
    colony_map = generate_map(width=64, height=48, seed=777)
    center_x = colony_map.width // 2
    center_y = colony_map.height // 2

    for y in range(center_y - 4, center_y + 5):
        for x in range(center_x - 4, center_x + 5):
            tile = colony_map.get_tile(x, y)
            assert tile is not None
            assert tile.terrain in {TerrainType.GRASS, TerrainType.PLAINS}


@pytest.mark.parametrize(
    ("width", "height"),
    [
        (0, 10),
        (10, 0),
        (-1, 10),
        (10, -1),
    ],
)
def test_generate_map_raises_for_invalid_dimensions(width: int, height: int) -> None:
    with pytest.raises(ValueError, match="width and height must be positive"):
        generate_map(width=width, height=height, seed=1)
