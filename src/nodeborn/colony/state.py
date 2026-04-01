from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Iterable, Mapping

from nodeborn.colony.building import Building
from nodeborn.colony.map import ColonyMap
from nodeborn.colony.resources import Resource, ResourceStock


def _default_buildings() -> list[Building]:
    return []


DEFAULT_STARTING_RESOURCES: Final[dict[Resource, int]] = {
    Resource.FOOD: 250,
    Resource.WOOD: 200,
    Resource.STONE: 100,
    Resource.IRON: 20,
    Resource.TOOLS: 25,
    Resource.GOLD: 50,
}


@dataclass(slots=True)
class ColonyState:
    """Aggregate root for colony simulation state."""

    colony_map: ColonyMap
    buildings: list[Building] = field(default_factory=_default_buildings)
    stockpile: ResourceStock = field(default_factory=ResourceStock)


def new_colony_state(
    colony_map: ColonyMap,
    *,
    starting_resources: Mapping[Resource, int] | Mapping[str, int] | None = None,
    buildings: Iterable[Building] | None = None,
) -> ColonyState:
    """Create a new colony with default or custom starting resources."""
    initial_resources: dict[Resource | str, int]
    if starting_resources is None:
        initial_resources = {
            resource: amount
            for resource, amount in DEFAULT_STARTING_RESOURCES.items()
        }
    else:
        initial_resources = {
            resource: amount
            for resource, amount in starting_resources.items()
        }
    initial_buildings = [] if buildings is None else list(buildings)

    return ColonyState(
        colony_map=colony_map,
        buildings=initial_buildings,
        stockpile=ResourceStock(amounts=initial_resources),
    )
