"""Starting roster from a public loadinfo payload."""

import re

from planets_intel.errors import RosterError

# loadinfo events: eventtype 2 is "Game started."; eventtype 3 is a join.
GAME_STARTED = 2
JOINED = 3

_JOIN = re.compile(
    r"^(?P<name>.+?) has joined the game in slot (?P<slot>\d+) as (?P<race>.+)\.$"
)


def select_starters(loadinfo: dict) -> list[dict]:
    """Starters at game start, one per slot, ordered by slot.

    The current ``players`` username is ignored. A dead slot is ``dead`` and
    an empty slot is ``open``; the starter is the last join at or before the
    Game started event. A slot with no such join is skipped.
    """
    events = loadinfo["events"]
    started = [event for event in events if event["eventtype"] == GAME_STARTED]
    if not started:
        raise RosterError("loadinfo has no Game started event")
    cutoff = min(started, key=lambda event: (event["turn"], event["id"]))["turn"]

    latest: dict[int, dict] = {}
    for event in events:
        if event["eventtype"] != JOINED or event["turn"] > cutoff:
            continue
        slot = event["playerid"]
        current = latest.get(slot)
        if current is None or event["id"] > current["id"]:
            latest[slot] = event

    players = {player["id"]: player for player in loadinfo["players"]}
    starters = []
    for slot, event in sorted(latest.items()):
        parsed = _parse_join(event)
        if parsed["slot"] != slot:
            raise RosterError(
                f"join event {event['id']} playerid {slot} "
                f"does not match {event['description']!r}"
            )
        player = players.get(slot)
        starters.append(
            {
                "slot": slot,
                "name": parsed["name"],
                "race": parsed["race"],
                "raceid": None if player is None else player["raceid"],
            }
        )
    return starters


def _parse_join(event: dict) -> dict:
    match = _JOIN.match(event["description"].strip())
    if match is None:
        raise RosterError(
            f"join event {event['id']} has an unexpected description: "
            f"{event['description']!r}"
        )
    return {
        "name": match.group("name").strip(),
        "slot": int(match.group("slot")),
        "race": match.group("race").strip(),
    }
