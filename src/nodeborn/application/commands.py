from __future__ import annotations

from dataclasses import dataclass

from nodeborn.colony.building import Building
from nodeborn.colony.building_specs import BuildingType, get_building_spec
from nodeborn.colony.state import ColonyState
from nodeborn.simulation.placement import validate_placement


@dataclass(frozen=True, slots=True)
class PlaceBuildingCommand:
    building_type: BuildingType
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class PlaceBuildingResult:
    success: bool
    reason: str | None = None
    building_id: str | None = None


def place_building(
    state: ColonyState,
    command: PlaceBuildingCommand,
) -> PlaceBuildingResult:
    valid, reason = validate_placement(
        state,
        command.building_type,
        command.x,
        command.y,
    )
    if not valid:
        return PlaceBuildingResult(success=False, reason=reason)

    spec = get_building_spec(command.building_type)
    state.stockpile.spend(spec.cost)

    building_id = _next_building_id(state, command.building_type)
    building = Building(
        id=building_id,
        building_type=command.building_type,
        location=(command.x, command.y),
        construction_progress=0.0,
    )
    state.buildings.append(building)
    state.colony_map.place_building_on_footprint(
        building_id=building_id,
        x=command.x,
        y=command.y,
        width=spec.width,
        height=spec.height,
    )

    return PlaceBuildingResult(success=True, building_id=building_id)


def _next_building_id(state: ColonyState, building_type: BuildingType) -> str:
    prefix = building_type.value
    existing_ids = {building.id for building in state.buildings}
    index = 1
    while True:
        candidate = f"{prefix}-{index}"
        if candidate not in existing_ids:
            return candidate
        index += 1
