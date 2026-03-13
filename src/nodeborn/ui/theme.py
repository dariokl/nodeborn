"""Nodeborn theme definitions based on Textual's Theme API."""

from __future__ import annotations

from textual.theme import Theme

NODEBORN_THEME = Theme(
    name="nodeborn",
    primary="#60a5fa",
    secondary="#4ade80",
    accent="#eab308",
    foreground="#e2e8f0",
    background="#0f172a",
    surface="#111c2d",
    panel="#1e293b",
    success="#4ade80",
    warning="#fbbf24",
    error="#f87171",
    dark=True,
    variables={
        # Footer contrast and key color tuning.
        "footer-background": "#1e293b",
        "footer-foreground": "#e2e8f0",
        "footer-key-foreground": "#eab308",
        # App chrome and panel styling hooks.
        "chrome-divider": "#334155",
        "panel-border": "#334155",
        "panel-title": "#cbd5e1",
        "panel-muted": "#94a3b8",
        # Semantic palette hooks.
        "semantic-surplus": "#4ade80",
        "semantic-stable": "#60a5fa",
        "semantic-warning": "#fbbf24",
        "semantic-critical": "#f87171",
        "semantic-inactive": "#6b7280",
        # Resource palette hooks.
        "resource-food": "#84cc16",
        "resource-wood": "#a16207",
        "resource-stone": "#78716c",
        "resource-iron": "#71717a",
        "resource-tools": "#0ea5e9",
        "resource-gold": "#eab308",
        # Seasonal palette hooks.
        "season-spring": "#86efac",
        "season-summer": "#fde047",
        "season-autumn": "#fdba74",
        "season-winter": "#cbd5e1",
    },
)
