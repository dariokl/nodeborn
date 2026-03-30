from __future__ import annotations

import pytest

from nodeborn.colony import TerrainType
from nodeborn.colony.building_specs import (
    BUILDING_SPECS,
    BUILDABLE_TERRAINS,
    BuildingSpec,
    BuildingType,
    all_building_specs,
    get_building_spec,
)


def test_registry_contains_all_expected_building_types() -> None:
    assert set(BUILDING_SPECS) == set(BuildingType)


def test_lookup_returns_spec_for_each_building_type() -> None:
    for building_type in BuildingType:
        spec = get_building_spec(building_type)
        assert spec.building_type is building_type


def test_all_building_specs_returns_stable_enum_order() -> None:
    expected = tuple(get_building_spec(building_type)
                     for building_type in BuildingType)
    assert all_building_specs() == expected


def test_farm_spec_matches_plan_constraints() -> None:
    farm = get_building_spec(BuildingType.FARM)

    assert farm.name == "Farm"
    assert farm.glyph == "⚘"
    assert (farm.width, farm.height) == (2, 2)
    assert farm.cost == {"wood": 50}
    assert farm.allowed_terrains == frozenset(
        {TerrainType.GRASS, TerrainType.PLAINS})


def test_buildable_terrain_set_excludes_blocked_terrain() -> None:
    assert TerrainType.WATER not in BUILDABLE_TERRAINS
    assert TerrainType.MOUNTAIN not in BUILDABLE_TERRAINS
    assert TerrainType.ROCK not in BUILDABLE_TERRAINS
    assert TerrainType.RIVER not in BUILDABLE_TERRAINS


def test_building_spec_rejects_invalid_size() -> None:
    with pytest.raises(ValueError, match="building size must be positive"):
        BuildingSpec(
            building_type=BuildingType.FARM,
            name="Broken",
            glyph="X",
            width=0,
            height=1,
            cost={"wood": 1},
            allowed_terrains=frozenset({TerrainType.GRASS}),
        )


def test_building_spec_rejects_empty_cost() -> None:
    with pytest.raises(ValueError, match="cost must not be empty"):
        BuildingSpec(
            building_type=BuildingType.FARM,
            name="Broken",
            glyph="X",
            width=1,
            height=1,
            cost={},
            allowed_terrains=frozenset({TerrainType.GRASS}),
        )


def test_building_spec_rejects_non_positive_cost_amount() -> None:
    with pytest.raises(ValueError, match="resource costs must be positive"):
        BuildingSpec(
            building_type=BuildingType.FARM,
            name="Broken",
            glyph="X",
            width=1,
            height=1,
            cost={"wood": 0},
            allowed_terrains=frozenset({TerrainType.GRASS}),
        )


def test_building_spec_rejects_empty_allowed_terrains() -> None:
    with pytest.raises(ValueError, match="allowed_terrains must not be empty"):
        BuildingSpec(
            building_type=BuildingType.FARM,
            name="Broken",
            glyph="X",
            width=1,
            height=1,
            cost={"wood": 1},
            allowed_terrains=frozenset(),
        )
