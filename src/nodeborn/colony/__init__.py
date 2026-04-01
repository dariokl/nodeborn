from __future__ import annotations

from nodeborn.colony.building import Building
from nodeborn.colony.building_specs import (
    BUILDING_SPECS,
    BUILDABLE_TERRAINS,
    BuildingSpec,
    BuildingType,
    all_building_specs,
    get_building_spec,
)
from nodeborn.colony.map import ColonyMap, TerrainType, Tile
from nodeborn.colony.map_gen import generate_map
from nodeborn.colony.resources import Resource, ResourceStock
from nodeborn.colony.state import (
    DEFAULT_STARTING_RESOURCES,
    ColonyState,
    new_colony_state,
)

__all__ = [
    "BUILDING_SPECS",
    "BUILDABLE_TERRAINS",
    "Building",
    "BuildingSpec",
    "BuildingType",
    "ColonyMap",
    "ColonyState",
    "DEFAULT_STARTING_RESOURCES",
    "TerrainType",
    "Tile",
    "Resource",
    "ResourceStock",
    "all_building_specs",
    "generate_map",
    "get_building_spec",
    "new_colony_state",
]
