from __future__ import annotations

from nodeborn.application.commands import (
    PlaceBuildingCommand,
    place_building,
)
from nodeborn.colony import Building, BuildingType, TerrainType, new_colony_state
from nodeborn.colony.resources import Resource
from tests.conftest import build_uniform_map


def test_place_building_adds_building_and_deducts_resources() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
    state = new_colony_state(colony_map)

    result = place_building(
        state,
        PlaceBuildingCommand(building_type=BuildingType.FARM, x=1, y=1),
    )

    assert result.success
    assert result.reason is None
    assert result.building_id == "farm-1"
    assert len(state.buildings) == 1
    assert state.buildings[0].id == "farm-1"
    assert state.stockpile.get(Resource.WOOD) == 150


def test_place_building_marks_footprint_tiles_with_building_id() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
    state = new_colony_state(colony_map)

    result = place_building(
        state,
        PlaceBuildingCommand(building_type=BuildingType.FARM, x=2, y=3),
    )

    assert result.success
    building_id = result.building_id
    assert building_id is not None
    assert state.colony_map.get_tile(2, 3).building_id == building_id
    assert state.colony_map.get_tile(3, 3).building_id == building_id
    assert state.colony_map.get_tile(2, 4).building_id == building_id
    assert state.colony_map.get_tile(3, 4).building_id == building_id


def test_place_building_rejects_invalid_location_without_state_changes() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.WATER)
    state = new_colony_state(colony_map)

    result = place_building(
        state,
        PlaceBuildingCommand(building_type=BuildingType.FARM, x=1, y=1),
    )

    assert not result.success
    assert result.reason == "Farm cannot be built on water"
    assert result.building_id is None
    assert state.buildings == []
    assert state.stockpile.get(Resource.WOOD) == 200


def test_place_building_rejects_unaffordable_build_without_state_changes() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
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

    result = place_building(
        state,
        PlaceBuildingCommand(building_type=BuildingType.FARM, x=1, y=1),
    )

    assert not result.success
    assert result.reason == "insufficient resources"
    assert result.building_id is None
    assert state.buildings == []


def test_place_building_allocates_next_available_building_id() -> None:
    colony_map = build_uniform_map(
        width=8, height=8, terrain=TerrainType.GRASS)
    existing = Building(
        id="farm-1",
        building_type=BuildingType.FARM,
        location=(5, 5),
        construction_progress=1.0,
    )
    state = new_colony_state(colony_map, buildings=[existing])

    result = place_building(
        state,
        PlaceBuildingCommand(building_type=BuildingType.FARM, x=1, y=1),
    )

    assert result.success
    assert result.building_id == "farm-2"
