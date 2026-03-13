"""Map screen placeholder for the Nodeborn app shell."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class MapScreen(Screen[None]):
    """Temporary map screen used to validate navigation in S0."""

    BINDINGS = [
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="map-placeholder"):
            yield Static(
                "Map placeholder for S1.\nPress Esc to return to the dashboard.",
                id="map-placeholder-text",
            )
        yield Footer()

    def action_back(self) -> None:
        """Return to the previous screen."""
        self.app.pop_screen()  # type: ignore
