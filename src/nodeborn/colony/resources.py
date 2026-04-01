from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, cast


def _default_amounts() -> dict[Resource | str, int]:
    return {}


class Resource(str, Enum):
    """All stockpile resource categories used by the colony."""

    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    TOOLS = "tools"
    GOLD = "gold"


@dataclass(slots=True)
class ResourceStock:
    """Mutable stockpile amounts with affordability and transaction helpers."""

    amounts: dict[Resource | str, int] = field(
        default_factory=_default_amounts)

    def __post_init__(self) -> None:
        normalized: dict[Resource, int] = {
            resource: 0 for resource in Resource}
        for resource_key, amount in self.amounts.items():
            resource = _to_resource(resource_key)
            if amount < 0:
                raise ValueError("resource amounts must be non-negative")
            if normalized[resource] != 0:
                raise ValueError("duplicate resource key after normalization")
            normalized[resource] = amount
        self.amounts = cast(dict[Resource | str, int], normalized)

    def get(self, resource: Resource) -> int:
        """Return current amount for a single resource."""
        return self.amounts[resource]

    def can_afford(self, cost: Mapping[Resource, int] | Mapping[str, int]) -> bool:
        """Return True when all resources in cost are available."""
        for resource, amount in _normalize_delta(cost).items():
            if amount < 0:
                raise ValueError("cost amounts must be non-negative")
            if self.amounts[resource] < amount:
                return False
        return True

    def spend(self, cost: Mapping[Resource, int] | Mapping[str, int]) -> None:
        """Deduct a resource cost from stockpile, or raise if unaffordable."""
        normalized_cost = _normalize_delta(cost)
        if not self.can_afford(normalized_cost):
            raise ValueError("insufficient resources")

        for resource, amount in normalized_cost.items():
            self.amounts[resource] -= amount

    def add(self, gains: Mapping[Resource, int] | Mapping[str, int]) -> None:
        """Increase stockpile by the provided resource gains."""
        for resource, amount in _normalize_delta(gains).items():
            if amount < 0:
                raise ValueError("gain amounts must be non-negative")
            self.amounts[resource] += amount


def _to_resource(resource: Resource | str) -> Resource:
    if isinstance(resource, Resource):
        return resource
    try:
        return Resource(resource)
    except ValueError as error:
        raise ValueError(f"unknown resource: {resource}") from error


def _normalize_delta(
    values: Mapping[Resource, int] | Mapping[str, int],
) -> dict[Resource, int]:
    normalized: dict[Resource, int] = {}
    for resource_key, amount in values.items():
        resource = _to_resource(resource_key)
        if resource in normalized:
            raise ValueError("duplicate resource key after normalization")
        normalized[resource] = amount
    return normalized
