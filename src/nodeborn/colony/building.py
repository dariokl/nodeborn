from __future__ import annotations

from dataclasses import dataclass

from nodeborn.colony.building_specs import BuildingType


@dataclass(slots=True)
class Building:
    """A placed or in-construction building instance in the colony."""

    id: str
    building_type: BuildingType
    location: tuple[int, int]
    construction_progress: float = 0.0
    workers_required: int = 0
    workers_assigned: int = 0

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("building id must not be empty")

        x, y = self.location
        if x < 0 or y < 0:
            raise ValueError("location coordinates must be non-negative")

        if not 0.0 <= self.construction_progress <= 1.0:
            raise ValueError(
                "construction_progress must be between 0.0 and 1.0")

        if self.workers_required < 0:
            raise ValueError("workers_required must be non-negative")

        if self.workers_assigned < 0:
            raise ValueError("workers_assigned must be non-negative")

        if self.workers_assigned > self.workers_required:
            raise ValueError("workers_assigned cannot exceed workers_required")

    @property
    def is_constructed(self) -> bool:
        """Return True when construction is complete."""
        return self.construction_progress >= 1.0
