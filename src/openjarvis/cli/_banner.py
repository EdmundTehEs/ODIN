"""Startup banner — ODIN wordmark + tagline (ODIN is a personal fork of OpenJarvis)."""

from __future__ import annotations

# "ODIN" in the figlet "standard" font, stored as plain text so the glyph
# backslashes don't collide with Rich markup; colour is applied at print time.
_WORDMARK = (
    '  ___  ____ ___ _   _ ',
    ' / _ \\|  _ \\_ _| \\ | |',
    '| | | | | | | ||  \\| |',
    '| |_| | |_| | || |\\  |',
    ' \\___/|____/___|_| \\_|',
)

_TAGLINE = "ODIN — Personal AI, in service of sir."


def print_banner(quiet: bool = False) -> None:
    """Print the ODIN startup banner. No-op when quiet."""
    if quiet:
        return
    try:
        from rich.console import Console

        console = Console()
        for line in _WORDMARK:
            console.print(line, style="bold bright_blue", highlight=False, markup=False)
        console.print(f"      {_TAGLINE}", style="cyan", highlight=False, markup=False)
        console.print()
    except ImportError:
        for line in _WORDMARK:
            print(line)
        print(f"      {Edmund's}")
        print()
