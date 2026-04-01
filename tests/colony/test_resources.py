from __future__ import annotations

import pytest

from nodeborn.colony.resources import Resource, ResourceStock


def test_resource_stock_defaults_all_resources_to_zero() -> None:
    stock = ResourceStock()

    for resource in Resource:
        assert stock.get(resource) == 0


def test_resource_stock_rejects_negative_initial_amount() -> None:
    with pytest.raises(ValueError, match="resource amounts must be non-negative"):
        ResourceStock(amounts={Resource.WOOD: -1})


def test_resource_stock_accepts_string_keys_in_initial_amounts() -> None:
    stock = ResourceStock(amounts={"wood": 12, "stone": 3})

    assert stock.get(Resource.WOOD) == 12
    assert stock.get(Resource.STONE) == 3


def test_resource_stock_rejects_unknown_resource_key() -> None:
    with pytest.raises(ValueError, match="unknown resource: bananas"):
        ResourceStock(amounts={"bananas": 10})


def test_can_afford_rejects_unknown_resource_key() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 5})

    with pytest.raises(ValueError, match="unknown resource: bananas"):
        stock.can_afford({"bananas": 1})


def test_spend_rejects_unknown_resource_key() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 5})

    with pytest.raises(ValueError, match="unknown resource: bananas"):
        stock.spend({"bananas": 1})


def test_add_rejects_unknown_resource_key() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 5})

    with pytest.raises(ValueError, match="unknown resource: bananas"):
        stock.add({"bananas": 1})


def test_can_afford_true_when_all_costs_available() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 80, Resource.STONE: 20})

    assert stock.can_afford({Resource.WOOD: 50, Resource.STONE: 10})


def test_can_afford_false_when_any_resource_missing() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 30})

    assert not stock.can_afford({Resource.WOOD: 40})


def test_can_afford_rejects_negative_cost_amount() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 30})

    with pytest.raises(ValueError, match="cost amounts must be non-negative"):
        stock.can_afford({Resource.WOOD: -1})


def test_spend_deducts_resources_when_affordable() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 80, Resource.STONE: 20})

    stock.spend({Resource.WOOD: 50, Resource.STONE: 5})

    assert stock.get(Resource.WOOD) == 30
    assert stock.get(Resource.STONE) == 15


def test_spend_raises_when_insufficient_resources() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 10})

    with pytest.raises(ValueError, match="insufficient resources"):
        stock.spend({Resource.WOOD: 11})


def test_add_increases_resource_amounts() -> None:
    stock = ResourceStock(amounts={Resource.FOOD: 5})

    stock.add({Resource.FOOD: 3, Resource.GOLD: 2})

    assert stock.get(Resource.FOOD) == 8
    assert stock.get(Resource.GOLD) == 2


def test_add_rejects_negative_gain_amount() -> None:
    stock = ResourceStock(amounts={Resource.FOOD: 5})

    with pytest.raises(ValueError, match="gain amounts must be non-negative"):
        stock.add({Resource.FOOD: -1})


def test_can_afford_accepts_string_cost_keys() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 50})

    assert stock.can_afford({"wood": 50})


def test_spend_accepts_string_cost_keys() -> None:
    stock = ResourceStock(amounts={Resource.WOOD: 10})

    stock.spend({"wood": 4})

    assert stock.get(Resource.WOOD) == 6


def test_add_accepts_string_gain_keys() -> None:
    stock = ResourceStock(amounts={Resource.FOOD: 1})

    stock.add({"food": 2, "gold": 1})

    assert stock.get(Resource.FOOD) == 3
    assert stock.get(Resource.GOLD) == 1
