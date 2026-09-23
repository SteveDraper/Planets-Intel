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
            10: {
                "id": 10,
                "activehulls": "15,14,",
                "activeadvantages": "25,30,",
                "hulls": "99,15,14,",
                "advantages": "98,25,30,",
            },
        },
        hulls={
            14: {
                "id": 14,
                "name": "Neutronic Fuel Carrier",
                "beams": 0,
                "advantage": 20,
                "techlevel": 3,
            },
            15: {
                "id": 15,
                "name": "Large Deep Space Freighter",
                "beams": 0,
                "advantage": 160,
                "techlevel": 2,
            },
            16: {
                "id": 16,
                "name": "Alchemy Ship",
                "beams": 0,
                "advantage": 50,
                "techlevel": 1,
            },
        },
        advantages={
            25: {"id": 25, "name": "Build Fighters", "value": 100},
            30: {"id": 30, "name": "alchemy", "value": -40},
            31: {"id": 31, "name": "Web Mines", "value": 80},
        },
        races={
            2: {"id": 2, "basehulls": "15,16,", "baseadvantages": "25,31,"},
            7: {"id": 7, "basehulls": "14,", "baseadvantages": ""},
        },
    )
    by_slot = {player["slot"]: player for player in report["players"]}
    assert report["game"]["name"] == "Honda Sector"
    assert report["game"]["type"] == "Epic"
    assert by_slot[2]["team"] == "RISK"
    assert by_slot[2]["officer_id"] == 10
    assert [(hull["name"], hull["default_state"]) for hull in by_slot[2]["hulls"]] == [
        ("Alchemy Ship", "removed"),
        ("Large Deep Space Freighter", "same"),
        ("Neutronic Fuel Carrier", "added"),
    ]
    assert by_slot[2]["hulls"][1]["icon"] == "https://mobile.planets.nu/img/hulls/15.png"
    assert [hull["techlevel"] for hull in by_slot[2]["hulls"]] == [1, 2, 3]
    assert "techlevel" not in by_slot[2]["advantages"][0]
    assert [(item["name"], item["default_state"]) for item in by_slot[2]["advantages"]] == [
        ("alchemy", "added"),
        ("Build Fighters", "same"),
        ("Web Mines", "removed"),
    ]
    assert {item["id"] for item in by_slot[2]["hulls"]} == {14, 15, 16}
    assert {item["id"] for item in by_slot[2]["advantages"]} == {25, 30, 31}
    assert by_slot[2]["campaign_points"] == 240
    assert by_slot[7]["team"] is None
    assert by_slot[7]["officer_id"] is None
    assert [(hull["name"], hull["default_state"]) for hull in by_slot[7]["hulls"]] == [
        ("Neutronic Fuel Carrier", "removed"),
    ]
    assert by_slot[7]["advantages"] == []
    assert by_slot[7]["campaign_points"] == 0
