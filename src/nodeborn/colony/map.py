from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class TerrainType(str, Enum):
    """Terrain categories used by map generation and rendering."""

    GRASS = "grass"
    PLAINS = "plains"
    WATER = "water"
    MOUNTAIN = "mountain"
    FOREST = "forest"
    SAND = "sand"
    ROCK = "rock"
    RIVER = "river"

    @property
    def glyph(self) -> str:
        """Single-character display glyph for this terrain."""
        return TERRAIN_GLYPHS[self]


TERRAIN_GLYPHS: Final[dict[TerrainType, str]] = {
    TerrainType.GRASS: ".",
    TerrainType.PLAINS: ",",
    TerrainType.WATER: "≈",
    TerrainType.MOUNTAIN: "▲",
    TerrainType.FOREST: "♠",
    TerrainType.SAND: "░",
    TerrainType.ROCK: "█",
    TerrainType.RIVER: "~",
}


@dataclass(slots=True)
class Tile:
    """A single map tile and its simulation-relevant properties."""

    x: int
    y: int
    terrain: TerrainType
    building_id: str | None = None
    fertility: float = 0.5
    elevation: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.fertility <= 1.0:
            raise ValueError("fertility must be between 0.0 and 1.0")


@dataclass(slots=True)
class ColonyMap:
    """Authoritative tile grid for the colony map."""

    width: int
    height: int
    tiles: list[list[Tile]]
    seed: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if len(self.tiles) != self.height:
            raise ValueError("tile grid height does not match map height")

        for y, row in enumerate(self.tiles):
            if len(row) != self.width:
                raise ValueError(
                    f"tile row {y} width does not match map width")
            for x, tile in enumerate(row):
                if tile.x != x or tile.y != y:
                    raise ValueError(
                        f"tile coordinate mismatch at [{y}][{x}] "
                        f"(tile has ({tile.x}, {tile.y}))"
                    )

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True when coordinates are inside map bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Tile | None:
        """Return tile when in bounds, otherwise None."""
        if not self.in_bounds(x, y):
            return None
        return self.tiles[y][x]
