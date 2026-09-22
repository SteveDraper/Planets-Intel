"""Starter selection against copied loadinfo payloads."""

import json
from pathlib import Path

from planets_intel.starters import select_starters

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "loadinfo.json").read_text(encoding="utf-8")
)


def _by_slot(starters: list[dict]) -> dict[int, dict]:
    return {starter["slot"]: starter for starter in starters}


def test_dead_slot_and_replacement_after_start():
    starters = _by_slot(select_starters(FIXTURE["serada"]))
    assert set(starters) == {1, 11}
    assert starters[1]["name"] == "dougp314"
    assert starters[1]["race"] == "The Solar Federation"
    assert starters[1]["raceid"] == 1
    assert starters[11]["name"] == "root"
    assert starters[11]["race"] == "The Missing Colonies of Man"
    assert "dead" not in {starter["name"] for starter in starters.values()}
    assert "nocere" not in {starter["name"] for starter in starters.values()}


def test_last_join_before_start_on_a_dead_slot():
    starters = _by_slot(select_starters(FIXTURE["honda"]))
    assert starters[2]["name"] == "magnetron"
    assert starters[2]["race"] == "The Lizard Alliance"
    assert starters[7]["name"] == "gigaschatten"
    assert starters[7]["race"] == "The Crystal Confederation"
    assert "frommi" not in {starter["name"] for starter in starters.values()}
    assert "dead" not in {starter["name"] for starter in starters.values()}


def test_open_slot_that_joined_before_start_keeps_that_starter():
    starters = _by_slot(select_starters(FIXTURE["cylon"]))
    assert starters[6]["name"] == "moon81m"
    assert starters[6]["race"] == "The Cyborg"
    assert starters[9]["name"] == "shutdown"
    assert "open" not in {starter["name"] for starter in starters.values()}
    assert "donaldworrell" not in {starter["name"] for starter in starters.values()}


def test_open_slot_with_no_join_before_start_is_skipped():
    # Same Cylon rows, without slot 6's join event, so that open slot never started.
    starters = _by_slot(select_starters(FIXTURE["cylon_open_without_join"]))
    assert 6 not in starters
    assert starters[9]["name"] == "shutdown"


def test_join_name_with_a_trailing_double_space():
    loadinfo = {
        "players": [
            {
                "id": 6,
                "username": "dead",
                "status": 3,
                "accountid": 0,
                "raceid": 6,
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
                "id": 5,
                "playerid": 6,
                "description": "trasaur p'tar  has joined the game in slot 6 as The Cyborg.",
            },
        ],
    }
    starters = select_starters(loadinfo)
    assert starters[0]["name"] == "trasaur p'tar"
    assert starters[0]["race"] == "The Cyborg"
