"""Command line for the roster report."""

import argparse
import json
from pathlib import Path

from planets_intel.errors import RosterError
from planets_intel.fetch import fetch_roster
from planets_intel.html_report import render_roster_html
from planets_intel.icons import embed_icons
from planets_intel.tailwind import compile_css


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write a starting-roster report for one Planets game as a single HTML file."
    )
    parser.add_argument("--game", required=True, type=int, help="Game id to analyse.")
    parser.add_argument("--out", required=True, help="HTML output path.")
    parser.add_argument(
        "--repr_out",
        help="Optional path for the intermediate representation as JSON.",
    )
    args = parser.parse_args(argv)
    try:
        report = fetch_roster(args.game)
    except RosterError as exc:
        parser.exit(1, f"{exc}\n")
    if args.repr_out:
        _write(args.repr_out, json.dumps(report, indent=2) + "\n")
    html = render_roster_html(embed_icons(report), compile_css())
    _write(args.out, html)
    print(args.out)
    return 0


def _write(path: str, text: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
