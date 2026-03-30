from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from nodeborn.colony.map import TerrainType


class BuildingType(str, Enum):
    """All placeable building categories available in V1."""

    FARM = "farm"
    MINE = "mine"
    WORKSHOP = "workshop"
    STORAGE = "storage"
    HOUSING = "housing"
    HALL = "hall"
    WELL = "well"
    LUMBER_CAMP = "lumber_camp"


BUILDABLE_TERRAINS: Final[frozenset[TerrainType]] = frozenset(
    {
        TerrainType.GRASS,
        TerrainType.PLAINS,
        TerrainType.FOREST,
        TerrainType.SAND,
    }
)


@dataclass(frozen=True, slots=True)
class BuildingSpec:
    """Static configuration for a buildable structure."""

    building_type: BuildingType
    name: str
    glyph: str
    width: int
    height: int
    cost: dict[str, int]
    allowed_terrains: frozenset[TerrainType]
    adjacency_rules: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("building size must be positive")

        if not self.glyph:
            raise ValueError("glyph must not be empty")

        if not self.cost:
            raise ValueError("cost must not be empty")

        for resource, amount in self.cost.items():
            if not resource:
                raise ValueError("resource names in cost must not be empty")
            if amount <= 0:
                raise ValueError("resource costs must be positive")

        if not self.allowed_terrains:
            raise ValueError("allowed_terrains must not be empty")


BUILDING_SPECS: Final[dict[BuildingType, BuildingSpec]] = {
    BuildingType.FARM: BuildingSpec(
        building_type=BuildingType.FARM,
        name="Farm",
        glyph="⚘",
        width=2,
        height=2,
        cost={"wood": 50},
        allowed_terrains=frozenset({TerrainType.GRASS, TerrainType.PLAINS}),
        adjacency_rules=("+15% output when adjacent to water or river",),
    ),
    BuildingType.MINE: BuildingSpec(
        building_type=BuildingType.MINE,
        name="Mine",
        glyph="⛏︎",
        width=2,
        height=2,
        cost={"wood": 40},
        allowed_terrains=BUILDABLE_TERRAINS,
        adjacency_rules=("at least one footprint edge must touch mountain",),
    ),
    BuildingType.WORKSHOP: BuildingSpec(
        building_type=BuildingType.WORKSHOP,
        name="Workshop",
        glyph="⚙",
        width=1,
        height=2,
        cost={"wood": 80},
        allowed_terrains=BUILDABLE_TERRAINS,
        adjacency_rules=("+10% throughput when adjacent to storage",),
    ),
    BuildingType.STORAGE: BuildingSpec(
        building_type=BuildingType.STORAGE,
        name="Storage",
        glyph="▣",
        width=2,
        height=2,
        cost={"wood": 60},
        allowed_terrains=BUILDABLE_TERRAINS,
    ),
    BuildingType.HOUSING: BuildingSpec(
        building_type=BuildingType.HOUSING,
        name="Housing",
        glyph="⌂",
        width=1,
        height=1,
        cost={"wood": 30},
        allowed_terrains=BUILDABLE_TERRAINS,
        adjacency_rules=("+morale when placed near hall",),
    ),
    BuildingType.HALL: BuildingSpec(
        building_type=BuildingType.HALL,
        name="Hall",
        glyph="♜",
        width=3,
        height=3,
        cost={"wood": 120, "stone": 40},
        allowed_terrains=BUILDABLE_TERRAINS,
    ),
    BuildingType.WELL: BuildingSpec(
        building_type=BuildingType.WELL,
        name="Well",
        glyph="◉",
        width=1,
        height=1,
        cost={"stone": 20},
        allowed_terrains=BUILDABLE_TERRAINS,
        adjacency_rules=("reduces fire risk in nearby buildings",),
    ),
    BuildingType.LUMBER_CAMP: BuildingSpec(
        building_type=BuildingType.LUMBER_CAMP,
        name="Lumber Camp",
        glyph="♣",
        width=2,
        height=2,
        cost={"wood": 45},
        allowed_terrains=frozenset(
            {TerrainType.GRASS, TerrainType.PLAINS, TerrainType.FOREST}
        ),
        adjacency_rules=("+wood output when adjacent to forest",),
    ),
}


def get_building_spec(building_type: BuildingType) -> BuildingSpec:
    """Return the static configuration for a building type."""
    return BUILDING_SPECS[building_type]


def all_building_specs() -> tuple[BuildingSpec, ...]:
    """Return all building specs in stable enum order."""
    return tuple(BUILDING_SPECS[building_type] for building_type in BuildingType)
