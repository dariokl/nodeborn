from __future__ import annotations

from nodeborn.colony import Building, BuildingType, TerrainType, new_colony_state
from nodeborn.colony.resources import Resource
from nodeborn.simulation.placement import validate_placement
from tests.conftest import build_uniform_map


def test_validate_placement_accepts_valid_farm_placement() -> None:
    colony_map = build_uniform_map(
        width=6, height=6, terrain=TerrainType.GRASS)
    state = new_colony_state(colony_map)

    valid, reason = validate_placement(state, BuildingType.FARM, x=1, y=1)

    assert valid
    assert reason == "ok"


def test_validate_placement_rejects_out_of_bounds_footprint() -> None:
    colony_map = build_uniform_map(
        width=3, height=3, terrain=TerrainType.GRASS)
    state = new_colony_state(colony_map)

    valid, reason = validate_placement(state, BuildingType.FARM, x=2, y=2)

    assert not valid
    assert reason == "building footprint is out of map bounds"


def test_validate_placement_rejects_unaffordable_building() -> None:
    colony_map = build_uniform_map(
        width=6, height=6, terrain=TerrainType.GRASS)
    state = new_colony_state(
        colony_map,
        starting_resources={
            Resource.FOOD: 0,
            Resource.WOOD: 0,
            Resource.STONE: 0,
            Resource.IRON: 0,
            Resource.TOOLS: 0,
            Resource.GOLD: 0,
        },
    )

    valid, reason = validate_placement(state, BuildingType.FARM, x=0, y=0)

    assert not valid
    assert reason == "insufficient resources"


def test_validate_placement_rejects_invalid_terrain_for_farm() -> None:
    colony_map = build_uniform_map(width=6, height=6, terrain=TerrainType.SAND)
    state = new_colony_state(colony_map)

    valid, reason = validate_placement(state, BuildingType.FARM, x=1, y=1)

    assert not valid
    assert reason == "Farm cannot be built on sand"


def test_validate_placement_rejects_overlap_with_existing_building() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
    existing_building = Building(
        id="existing-housing",
        building_type=BuildingType.HOUSING,
        location=(2, 2),
        construction_progress=1.0,
    )
    state = new_colony_state(colony_map, buildings=[existing_building])

    valid, reason = validate_placement(state, BuildingType.FARM, x=1, y=1)

    assert not valid
    assert reason == "building footprint overlaps existing building"


def test_validate_placement_rejects_mine_when_not_touching_mountain() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
    state = new_colony_state(colony_map)

    valid, reason = validate_placement(state, BuildingType.MINE, x=2, y=2)

    assert not valid
    assert reason == "mine must touch mountain"


def test_validate_placement_accepts_mine_touching_mountain() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
    colony_map.tiles[1][3].terrain = TerrainType.MOUNTAIN
    state = new_colony_state(colony_map)

    valid, reason = validate_placement(state, BuildingType.MINE, x=2, y=2)

    assert valid
    assert reason == "ok"
