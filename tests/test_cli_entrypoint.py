from __future__ import annotations

from pathlib import Path

from nodeborn.main import BOOTSTRAP_MESSAGE, main


def test_main_emits_bootstrap_message(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert BOOTSTRAP_MESSAGE in captured.out


def test_main_entrypoint_is_callable() -> None:
    assert callable(main)


def test_style_placeholders_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    colors = root / "src" / "nodeborn" / "ui" / "styles" / "colors.tcss"
    theme = root / "src" / "nodeborn" / "ui" / "styles" / "theme.tcss"
    assert colors.exists()
    assert theme.exists()
