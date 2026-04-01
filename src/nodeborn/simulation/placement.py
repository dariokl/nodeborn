from __future__ import annotations

from collections.abc import Iterable

from nodeborn.colony.building_specs import BuildingType, get_building_spec
from nodeborn.colony.map import TerrainType
from nodeborn.colony.state import ColonyState


def validate_placement(
    state: ColonyState,
    building_type: BuildingType,
    x: int,
    y: int,
) -> tuple[bool, str]:
    """Validate whether a building can be placed at the given top-left coordinate."""
    spec = get_building_spec(building_type)

    if not _footprint_in_bounds(state, x, y, spec.width, spec.height):
        return False, "building footprint is out of map bounds"

    if not state.stockpile.can_afford(spec.cost):
        return False, "insufficient resources"

    for tile_x, tile_y in _footprint_tiles(x, y, spec.width, spec.height):
        tile = state.colony_map.get_tile(tile_x, tile_y)
        if tile is None:  # pragma: no cover - guarded by in-bounds check
            return False, "building footprint is out of map bounds"
        if tile.terrain not in spec.allowed_terrains:
            return False, f"{spec.name} cannot be built on {tile.terrain.value}"

    occupied_tiles = _occupied_tiles(state)
    for footprint_tile in _footprint_tiles(x, y, spec.width, spec.height):
        if footprint_tile in occupied_tiles:
            return False, "building footprint overlaps existing building"

    if building_type is BuildingType.MINE and not _mine_touches_mountain(
        state, x, y, spec.width, spec.height
    ):
        return False, "mine must touch mountain"

    return True, "ok"


def _footprint_in_bounds(
    state: ColonyState,
    x: int,
    y: int,
    width: int,
    height: int,
) -> bool:
    return (
        x >= 0
        and y >= 0
        and x + width <= state.colony_map.width
        and y + height <= state.colony_map.height
    )


def _footprint_tiles(
    x: int,
    y: int,
    width: int,
    height: int,
) -> Iterable[tuple[int, int]]:
    for tile_y in range(y, y + height):
        for tile_x in range(x, x + width):
            yield (tile_x, tile_y)


def _occupied_tiles(state: ColonyState) -> set[tuple[int, int]]:
    occupied: set[tuple[int, int]] = set()
    for building in state.buildings:
        spec = get_building_spec(building.building_type)
        occupied.update(
            _footprint_tiles(
                building.location[0],
                building.location[1],
                spec.width,
                spec.height,
            )
        )
    return occupied


def _mine_touches_mountain(
    state: ColonyState,
    x: int,
    y: int,
    width: int,
    height: int,
) -> bool:
    for tile_x, tile_y in _footprint_tiles(x, y, width, height):
        for neighbor_x, neighbor_y in _neighbors4(tile_x, tile_y):
            tile = state.colony_map.get_tile(neighbor_x, neighbor_y)
            if tile is not None and tile.terrain is TerrainType.MOUNTAIN:
                return True
    return False


def _neighbors4(x: int, y: int) -> tuple[tuple[int, int], ...]:
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
