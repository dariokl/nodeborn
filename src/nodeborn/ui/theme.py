"""Nodeborn theme definitions based on Textual's Theme API."""

from __future__ import annotations

from textual.theme import Theme

NODEBORN_THEME = Theme(
    name="nodeborn",
    primary="#5fb3b3",
    secondary="#60a5fa",
    accent="#eab308",
    foreground="#e6edf5",
    background="#10161d",
    surface="#16202a",
    panel="#2a3948",
    success="#4ade80",
    warning="#fbbf24",
    error="#f87171",
    dark=True,
    variables={
        # Footer contrast and key color tuning.
        "footer-background": "#16202a",
        "footer-foreground": "#e6edf5",
        "footer-key-foreground": "#eab308",
        # App-specific palette hooks for resources and seasons.
        "resource-food": "#84cc16",
        "resource-wood": "#a16207",
        "resource-stone": "#78716c",
        "resource-iron": "#71717a",
        "resource-tools": "#0ea5e9",
        "resource-gold": "#eab308",
        "season-spring": "#86efac",
        "season-summer": "#fde047",
        "season-autumn": "#fdba74",
        "season-winter": "#cbd5e1",
        "semantic-stable": "#60a5fa",
        "semantic-inactive": "#6b7280",
    },
)
