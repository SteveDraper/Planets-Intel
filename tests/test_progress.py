"""Progress lines go to stderr and do not change the report."""

from planets_intel.fetch import fetch_roster
from planets_intel.icons import embed_icons

_LOADINFO = {
    "game": {"id": 1, "name": "Example", "shortdescription": "Classic"},
    "players": [
        {
            "id": 1,
            "username": "dead",
            "status": 3,
            "accountid": 0,
            "raceid": 1,
            "turnjoined": 1,
        }
    ],
    "events": [
        {
            "eventtype": 2,
            "turn": 1,
            "id": 1,
            "playerid": 0,
            "description": "Game started.",
        },
        {
            "eventtype": 3,
            "turn": 1,
            "id": 2,
            "playerid": 1,
            "description": "ada has joined the game in slot 1 as The Solar Federation.",
        },
    ],
}


def test_fetch_progress(monkeypatch, capsys):
    def fake_get(path, params):
        if path == "/game/loadinfo":
            return _LOADINFO
        if path == "/static/all":
            return {
                "hulls": [{"id": 14, "name": "Neutronic Fuel Carrier", "beams": 0}],
                "advantages": [{"id": 25, "name": "Build Fighters"}],
            }
        if path == "/account/loadprofile":
            return {"success": True, "account": {"id": 7}, "playergroups": []}
        if path == "/account/officers":
            return {"success": True, "officers": [{"id": 9, "raceid": 1}]}
        if path == "/account/loadofficer":
            return {
                "success": True,
                "officer": {"id": 9, "activehulls": "14,", "activeadvantages": "25,"},
            }
        raise AssertionError(path)

    monkeypatch.setattr("planets_intel.fetch.get_json", fake_get)
    report = fetch_roster(1)
    err = capsys.readouterr().err.splitlines()
    assert err == [
        "game load",
        "1/1 ada: profile",
        "1/1 ada: officers",
        "1/1 ada: hulls",
        "1/1 ada: advantages",
    ]
    assert report["players"][0]["name"] == "ada"
    assert report["players"][0]["hulls"][0]["name"] == "Neutronic Fuel Carrier"


def test_icon_progress(monkeypatch, capsys):
    monkeypatch.setattr(
        "planets_intel.icons._data_uri",
        lambda url: "data:image/png;base64,aa",
    )
    report = embed_icons(
        {
            "players": [
                {
                    "hulls": [{"id": 1, "name": "A", "icon": "https://example/a.png"}],
                    "advantages": [
                        {"id": 2, "name": "B", "icon": "https://example/a.png"},
                        {"id": 3, "name": "C", "icon": None},
                    ],
                }
            ]
        }
    )
    err = capsys.readouterr().err.splitlines()
    assert err == ["icons 1/1"]
    assert report["players"][0]["hulls"][0]["icon"] == "data:image/png;base64,aa"
    assert report["players"][0]["advantages"][1]["icon"] is None
