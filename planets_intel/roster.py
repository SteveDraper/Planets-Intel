"""Build the roster intermediate representation from fetched API payloads."""

from planets_intel.errors import RosterError
from planets_intel.starters import select_starters

# playergroups.status 1 is an active membership. isleague is the "League Team" subtitle.
_ACTIVE_MEMBERSHIP = 1


def game_record(loadinfo: dict) -> dict:
    game = loadinfo["game"]
    return {
        "id": game["id"],
        "name": game["name"],
        "type": game["shortdescription"],
    }


def league_team(playergroups: list[dict] | None) -> str | None:
    """Name of the active group whose subtitle is League Team."""
    active = []
    for record in playergroups or []:
        group = record.get("_group") or {}
        if record.get("status") == _ACTIVE_MEMBERSHIP and group.get("isleague"):
            active.append(record)
    if not active:
        return None
    active.sort(key=lambda record: record.get("datejoined") or "")
    return active[-1]["_group"]["name"]


def build_roster(
    loadinfo: dict,
    accounts: dict[str, dict],
    officers_by_account: dict[int, list[dict]],
    officer_details: dict[int, dict],
    hulls: dict[int, dict],
    advantages: dict[int, dict],
) -> dict:
    """Assemble the JSON report. ``accounts`` is keyed by starter username."""
    players = []
    for starter in select_starters(loadinfo):
        account_payload = accounts[starter["name"]]
        account = account_payload["account"]
        officer = _officer_for_race(
            officers_by_account.get(account["id"], []),
            starter["raceid"],
        )
        detail = None if officer is None else officer_details[officer["id"]]
        players.append(
            {
                "slot": starter["slot"],
                "name": starter["name"],
                "race": starter["race"],
                "team": league_team(account_payload.get("playergroups")),
                "officer_id": None if officer is None else officer["id"],
                "hulls": _active_items(
                    None if detail is None else detail.get("activehulls"),
                    hulls,
                    _hull_icon,
                ),
                "advantages": _active_items(
                    None if detail is None else detail.get("activeadvantages"),
                    advantages,
                    _advantage_icon,
                ),
            }
        )
    return {"game": game_record(loadinfo), "players": players}


def _officer_for_race(officers: list[dict], raceid: int | None) -> dict | None:
    if raceid is None:
        return None
    for officer in officers:
        if officer.get("raceid") == raceid:
            return officer
    return None


def _active_items(csv: str | None, catalog: dict[int, dict], icon_for) -> list[dict]:
    items = []
    seen: set[int] = set()
    for raw in (csv or "").split(","):
        token = raw.strip()
        if not token:
            continue
        item_id = int(token)
        if item_id in seen:
            continue
        seen.add(item_id)
        record = catalog.get(item_id)
        if record is None:
            raise RosterError(f"static catalog has no id {item_id}")
        items.append(
            {
                "id": item_id,
                "name": record["name"],
                "icon": icon_for(record),
            }
        )
    items.sort(key=lambda item: item["id"])
    return items


def _hull_icon(hull: dict) -> str:
    """Classic hull image URL used by the officer hull list."""
    hull_id = hull["id"]
    pic_id = hull_id
    if hull_id > 3000:
        pic_id = hull_id - 3000
    elif hull_id > 2000:
        pic_id = hull_id - 2000
    elif hull_id > 1000:
        pic_id = hull_id - 1000
    beams = hull.get("beams") or 0
    if beams and pic_id in (65, 71):
        token = f"{pic_id}-{beams}"
    else:
        token = str(pic_id)
    return f"https://mobile.planets.nu/img/hulls/{token}.png"


def _advantage_icon(advantage: dict) -> str:
    return f"https://mobile.planets.nu/img/tech/{advantage['id']}.png"
