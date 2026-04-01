from __future__ import annotations

from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget

from nodeborn.colony.building_specs import (
    BuildingSpec,
    BuildingType,
    all_building_specs,
)
from nodeborn.colony.resources import ResourceStock


class BuildPalette(Widget):
    """Interactive build palette for selecting a structure to place."""

    can_focus = True

    BINDINGS = [
        ("up", "select_previous", "Up"),
        ("down", "select_next", "Down"),
        ("enter", "confirm", "Select"),
        ("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    BuildPalette {
        width: 42;
        height: auto;
        border: round $accent;
        padding: 0 1;
        background: $panel;
        color: $text;
    }
    """

    selected_index = reactive(0)

    class BuildingSelected(Message):
        def __init__(self, building_type: BuildingType) -> None:
            super().__init__()
            self.building_type = building_type

    class Cancelled(Message):
        pass

    def __init__(
        self,
        stockpile: ResourceStock,
        *,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._stockpile = stockpile
        self._specs: tuple[BuildingSpec, ...] = all_building_specs()

    @property
    def specs(self) -> tuple[BuildingSpec, ...]:
        return self._specs

    @property
    def selected_building_type(self) -> BuildingType:
        return self._specs[self.selected_index].building_type

    def action_select_previous(self) -> None:
        self.selected_index = (self.selected_index - 1) % len(self._specs)

    def action_select_next(self) -> None:
        self.selected_index = (self.selected_index + 1) % len(self._specs)

    def action_confirm(self) -> None:
        self.post_message(self.BuildingSelected(self.selected_building_type))

    def action_cancel(self) -> None:
        self.post_message(self.Cancelled())

    def watch_selected_index(self, _old: int, _new: int) -> None:
        self.refresh()

    def render(self) -> Panel:
        lines: list[Text] = []
        for index, spec in enumerate(self._specs):
            affordable = self._stockpile.can_afford(spec.cost)
            selector = "▶ " if index == self.selected_index else "  "
            cost_label = ", ".join(
                f"{amount} {resource}" for resource, amount in spec.cost.items()
            )
            row = Text(selector)
            row.append(f"{spec.name:<12} ")
            row.append(f"{spec.width}x{spec.height:<3} ")
            row.append(cost_label)
            row.append("  ")
            row.append("CAN" if affordable else "NO",
                       style="green" if affordable else "red")
            if index == self.selected_index:
                row.stylize("bold")
            lines.append(row)

        footer = Text("[Enter] Select   [Esc] Cancel", style="dim")
        content = Group(*lines, Text(""), footer)
        return Panel(content, title="BUILD", border_style="yellow")
