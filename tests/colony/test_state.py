from __future__ import annotations

from nodeborn.colony.building import Building
from nodeborn.colony.building_specs import BuildingType
from nodeborn.colony.resources import Resource
from nodeborn.colony.state import (
    DEFAULT_STARTING_RESOURCES,
    ColonyState,
    new_colony_state,
)
from tests.conftest import build_uniform_map


def test_colony_state_direct_construction() -> None:
    colony_map = build_uniform_map(width=6, height=4)
    stockpile = {Resource.WOOD: 40, Resource.STONE: 10}

    state = ColonyState(
        colony_map=colony_map,
        stockpile=new_colony_state(
            colony_map,
            starting_resources=stockpile,
        ).stockpile,
    )

    assert state.colony_map is colony_map
    assert state.stockpile.get(Resource.WOOD) == 40
    assert state.stockpile.get(Resource.STONE) == 10
    assert state.buildings == []


def test_new_colony_state_uses_default_starting_resources() -> None:
    colony_map = build_uniform_map(width=8, height=8)

    state = new_colony_state(colony_map)

    for resource, amount in DEFAULT_STARTING_RESOURCES.items():
        assert state.stockpile.get(resource) == amount


def test_new_colony_state_accepts_custom_starting_resources() -> None:
    colony_map = build_uniform_map(width=5, height=5)

    state = new_colony_state(
        colony_map,
        starting_resources={"food": 10, "wood": 25, "gold": 3},
    )

    assert state.stockpile.get(Resource.FOOD) == 10
    assert state.stockpile.get(Resource.WOOD) == 25
    assert state.stockpile.get(Resource.GOLD) == 3
    assert state.stockpile.get(Resource.STONE) == 0


def test_new_colony_state_accepts_initial_buildings() -> None:
    colony_map = build_uniform_map(width=6, height=6)
    building = Building(
        id="hall-1",
        building_type=BuildingType.HALL,
        location=(2, 2),
        construction_progress=1.0,
    )

    state = new_colony_state(colony_map, buildings=[building])

    assert len(state.buildings) == 1
    assert state.buildings[0].id == "hall-1"


def test_new_colony_state_copies_default_resource_template() -> None:
    colony_map = build_uniform_map(width=4, height=4)

    state = new_colony_state(colony_map)
    state.stockpile.spend({Resource.WOOD: 1})

    assert DEFAULT_STARTING_RESOURCES[Resource.WOOD] == 200
