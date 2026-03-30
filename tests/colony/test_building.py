from __future__ import annotations

import pytest

from nodeborn.colony.building import Building
from nodeborn.colony.building_specs import BuildingType


def test_building_creation_with_valid_values() -> None:
    building = Building(
        id="b-1",
        building_type=BuildingType.FARM,
        location=(12, 7),
        construction_progress=0.25,
        workers_required=3,
        workers_assigned=2,
    )

    assert building.id == "b-1"
    assert building.building_type is BuildingType.FARM
    assert building.location == (12, 7)
    assert building.construction_progress == 0.25
    assert building.workers_required == 3
    assert building.workers_assigned == 2
    assert not building.is_constructed


def test_building_is_constructed_when_progress_complete() -> None:
    building = Building(
        id="b-2",
        building_type=BuildingType.STORAGE,
        location=(2, 3),
        construction_progress=1.0,
    )

    assert building.is_constructed


def test_building_rejects_empty_id() -> None:
    with pytest.raises(ValueError, match="building id must not be empty"):
        Building(
            id="",
            building_type=BuildingType.WELL,
            location=(0, 0),
        )


def test_building_rejects_negative_location() -> None:
    with pytest.raises(ValueError, match="location coordinates must be non-negative"):
        Building(
            id="b-3",
            building_type=BuildingType.WORKSHOP,
            location=(-1, 0),
        )


def test_building_rejects_out_of_range_progress() -> None:
    with pytest.raises(ValueError, match="construction_progress must be between 0.0 and 1.0"):
        Building(
            id="b-4",
            building_type=BuildingType.HOUSING,
            location=(1, 1),
            construction_progress=1.5,
        )


def test_building_rejects_negative_workers_required() -> None:
    with pytest.raises(ValueError, match="workers_required must be non-negative"):
        Building(
            id="b-5",
            building_type=BuildingType.MINE,
            location=(4, 4),
            workers_required=-1,
        )


def test_building_rejects_assigned_workers_over_required() -> None:
    with pytest.raises(
        ValueError, match="workers_assigned cannot exceed workers_required"
    ):
        Building(
            id="b-6",
            building_type=BuildingType.LUMBER_CAMP,
            location=(5, 5),
            workers_required=2,
            workers_assigned=3,
        )
