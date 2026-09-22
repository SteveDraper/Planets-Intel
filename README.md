# Planets Intel

A Python script builds a starting-roster report for one Planets game and writes one self-contained HTML file. There is no server, and the file needs no extra assets when you open it.

The home viewport is the player table (name, race, league team). The race cell opens that player's detail viewport, which holds the active hull and advantage tables. A link above the table opens the team summary. Navigation stays inside the file.

Tailwind CSS is compiled with the Tailwind standalone CLI (v4.3.3) when the script runs, then inlined. The page does not load Tailwind from a CDN. Hull and advantage icons are fetched at build time and embedded as data URIs. The CLI binary is downloaded into `.tools/` on first run and is build-time only.

Python 3.14 only. Setup and commands use [uv](https://docs.astral.sh/uv/).

## Setup

```bash
uv python pin 3.14
uv python install 3.14
uv sync
```

`uv python pin 3.14` writes `.python-version`. `requires-python` in `pyproject.toml` is `>=3.14,<3.15`. `uv python install 3.14` is only needed when 3.14 is not already installed.

## Generate

```bash
uv run python generate_report.py --game 682163 --out dist/report.html
```

`--game` and `--out` are required. `--repr_out` writes the intermediate JSON representation. `--help` prints usage.

```bash
uv run python generate_report.py --help
uv run python generate_report.py --game 682163 --out dist/report.html --repr_out dist/report.json
```

## Tests

```bash
uv run pytest
```

## JSON endpoints

Public `GET` `http://api.planets.nu` calls, the same ones the planets.nu pages load:

| Page | Endpoint |
| --- | --- |
| Game | `/game/loadinfo?gameid={id}` |
| Account | `/account/loadprofile?username={username}` |
| Officers | `/account/officers?accountid={accountid}` |
| Hulls and advantages | `/account/loadofficer?officerid={officerid}` |

Active hull and advantage ids come from `activehulls` and `activeadvantages` on the officer. Names come from `/static/all` (`hulls` and `advantages`). Icon URLs are the ones the officer pages use: `https://mobile.planets.nu/img/hulls/{id}.png` and `https://mobile.planets.nu/img/tech/{id}.png`. The game type in the report is the API field `shortdescription`.
