"""Roster assembly from already-fetched payloads."""

import json
from pathlib import Path

from planets_intel.roster import build_roster

HONDA = json.loads(
    (Path(__file__).parent / "fixtures" / "loadinfo.json").read_text(encoding="utf-8")
)["honda"]


def test_league_team_and_active_items():
    accounts = {
        "magnetron": {
            "account": {"id": 1},
            "playergroups": [
                {
                    "status": 1,
                    "datejoined": "2020-01-01T00:00:00",
                    "_group": {"name": "Casual", "isleague": False},
                },
                {
                    "status": 3,
                    "datejoined": "2024-01-01T00:00:00",
                    "_group": {"name": "Invited", "isleague": True},
                },
                {
                    "status": 1,
                    "datejoined": "2021-06-01T00:00:00",
                    "_group": {"name": "RISK", "isleague": True},
                },
            ],
        },
        "gigaschatten": {"account": {"id": 2}, "playergroups": []},
    }
    report = build_roster(
        HONDA,
        accounts,
        officers_by_account={
            1: [{"id": 10, "raceid": 2}],
            2: [{"id": 11, "raceid": 1}],
        },
        officer_details={
            10: {"id": 10, "activehulls": "15,14,", "activeadvantages": "25,30,"},
        },
        hulls={
            14: {"id": 14, "name": "Neutronic Fuel Carrier", "beams": 0},
            15: {"id": 15, "name": "Large Deep Space Freighter", "beams": 0},
        },
        advantages={
            25: {"id": 25, "name": "Build Fighters"},
            30: {"id": 30, "name": "alchemy"},
        },
    )
    by_slot = {player["slot"]: player for player in report["players"]}
    assert report["game"]["name"] == "Honda Sector"
    assert report["game"]["type"] == "Epic"
    assert by_slot[2]["team"] == "RISK"
    assert by_slot[2]["officer_id"] == 10
    assert [hull["name"] for hull in by_slot[2]["hulls"]] == [
        "Large Deep Space Freighter",
        "Neutronic Fuel Carrier",
    ]
    assert by_slot[2]["hulls"][0]["icon"] == "https://mobile.planets.nu/img/hulls/15.png"
    assert [item["name"] for item in by_slot[2]["advantages"]] == [
        "alchemy",
        "Build Fighters",
    ]
    assert by_slot[7]["team"] is None
    assert by_slot[7]["officer_id"] is None
    assert by_slot[7]["hulls"] == []
    assert by_slot[7]["advantages"] == []
