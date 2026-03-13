"""CLI entrypoint for Nodeborn."""

from __future__ import annotations

from nodeborn.app import NodebornApp

def main() -> None:
    """Run the Nodeborn console entrypoint."""
    NodebornApp().run()
