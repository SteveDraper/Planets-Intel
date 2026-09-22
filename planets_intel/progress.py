"""Stderr notes so a long roster run shows that it is still moving."""

import sys


def note(message: str) -> None:
    print(message, file=sys.stderr, flush=True)
