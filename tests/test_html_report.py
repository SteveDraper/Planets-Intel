"""HTML transform. No network."""

from planets_intel.html_report import render_roster_html

REPORT = {
    "game": {"id": 682163, "name": "Honda Sector", "type": "Epic"},
    "players": [
        {
            "slot": 2,
            "name": "magnetron",
            "race": "The Lizard Alliance",
            "team": None,
            "officer_id": 10,
            "campaign_points": 240,
            "hulls": [
                {
                    "id": 14,
                    "name": "Neutronic Fuel Carrier",
                    "icon": "https://mobile.planets.nu/img/hulls/14.png",
                    "techlevel": 3,
                    "default_state": "added",
                }
            ],
            "advantages": [
                {
                    "id": 25,
                    "name": "Build Fighters",
                    "icon": "data:image/png;base64,aaaa",
                    "default_state": "same",
                },
                {
                    "id": 31,
                    "name": "Web Mines",
                    "icon": None,
                    "default_state": "removed",
                },
            ],
        },
        {
            "slot": 7,
            "name": "gigaschatten",
            "race": "The Crystal Confederation",
            "team": "RISK",
            "officer_id": None,
            "campaign_points": 0,
            "hulls": [],
            "advantages": [],
        },
    ],
}


def _row_containing(page: str, name: str) -> str:
    for chunk in page.split("<tr"):
        if name in chunk:
            return chunk
    raise AssertionError(name)


def test_home_teams_and_detail_viewports():
    page = render_roster_html(REPORT, "/* test */")
    assert "Honda Sector (682163) Epic" in page
    assert "Team summary" in page
    assert 'href="#teams"' in page
    assert 'href="#player-2"' in page
    assert "magnetron" in page
    assert "The Lizard Alliance" in page
    assert "gigaschatten" in page
    assert "RISK" in page
    assert "&lt;None&gt;" in page
    assert 'id="player-2"' in page
    detail = page.split('id="player-2"', 1)[1].split('id="player-7"', 1)[0]
    assert detail.index("Campaign points used") < detail.index("Hulls")
    assert 'data-hull-sort="name"' in detail
    assert 'data-hull-sort="techlevel"' in detail
    assert 'data-hull-dir="asc" aria-pressed="true"' in detail
    assert 'aria-label="Ascending"' in detail
    assert 'aria-label="Descending"' in detail
    assert ">Ascending<" not in detail
    assert ">Descending<" not in detail
    assert 'd="M8 13V3M4.5 6.5 8 3l3.5 3.5"' in detail
    assert 'd="M8 3v10M4.5 9.5 8 13l3.5-3.5"' in detail
    assert 'aria-pressed="true"' in detail
    assert 'data-techlevel="3"' in detail
    assert 'aria-label="Added"' in detail.split(">Advantages<", 1)[0]
    assert 'aria-label="Same as default"' in detail.split(">Advantages<", 1)[1]
    assert 'd="M8 2v12M2 8h12"' in detail
    assert "M3.5 8.5" not in detail
    added = _row_containing(detail, "Neutronic Fuel Carrier")
    assert 'd="M8 2v12M2 8h12"' in added
    assert "bg-[rgba(70,130,80,0.35)]" in added
    same = _row_containing(detail, "Build Fighters")
    assert "<svg" not in same
    assert "bg-[rgba(" not in same
    removed = _row_containing(detail, "Web Mines")
    assert 'd="M3 8h10"' in removed
    assert "bg-[rgba(150,60,60,0.40)]" in removed
    advantages = detail.split(">Advantages<", 1)[1]
    assert "data-hull-sort" not in advantages
    assert "data-hull-dir" not in advantages
    assert "data-techlevel" not in advantages
    assert ">240<" in detail.split("Hulls", 1)[0]
    empty = page.split('id="player-7"', 1)[1]
    assert "Campaign points used" in empty.split("Hulls", 1)[0]
    assert ">0<" in empty.split("Hulls", 1)[0]
    assert "Neutronic Fuel Carrier" in page
    assert "Build Fighters" in page
    assert "Hulls" in page
    assert "Advantages" in page
    assert 'data-sort="0"' in page
    assert 'data-sort="1"' in page
    assert 'data-sort="2"' in page
    assert 'src="data:image/png;base64,aaaa"' in page
    assert 'src="https://mobile.planets.nu/img/hulls/14.png"' not in page
    assert "cdn.tailwindcss.com" not in page
    none_section = page.split('id="teams"', 1)[1]
    assert "&lt;None&gt;" in none_section
    assert "magnetron" in none_section
    assert "gigaschatten" in none_section
