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
            "hulls": [
                {
                    "id": 14,
                    "name": "Neutronic Fuel Carrier",
                    "icon": "https://mobile.planets.nu/img/hulls/14.png",
                }
            ],
            "advantages": [
                {
                    "id": 25,
                    "name": "Build Fighters",
                    "icon": "data:image/png;base64,aaaa",
                }
            ],
        },
        {
            "slot": 7,
            "name": "gigaschatten",
            "race": "The Crystal Confederation",
            "team": "RISK",
            "officer_id": None,
            "hulls": [],
            "advantages": [],
        },
    ],
}


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
