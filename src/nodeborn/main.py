"""CLI entrypoint for Nodeborn."""

from __future__ import annotations


BOOTSTRAP_MESSAGE = "Nodeborn bootstrap ready. App shell arrives in S0.3."


def main() -> None:
    """Run the Nodeborn console entrypoint.

    This stays intentionally thin so we can swap the bootstrap call for the
    Textual app runner in S0.3 without changing CLI wiring.
    """
    print(BOOTSTRAP_MESSAGE)
