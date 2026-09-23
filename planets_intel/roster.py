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
    races: dict[int, dict],
) -> dict:
    """Assemble the JSON report. ``accounts`` is keyed by starter username."""
    players = []
    for starter in select_starters(loadinfo):
        account_payload = accounts[starter["name"]]
        account = account_payload["account"]
        raceid = starter["raceid"]
        officer = _officer_for_race(
            officers_by_account.get(account["id"], []),
            raceid,
        )
        detail = None if officer is None else officer_details[officer["id"]]
        # Officer pages total campaign points as hull.advantage + advantage.value.
        # Race defaults are /static/all races[].basehulls and baseadvantages.
        active_hulls, hull_points = _union_items(
            None if detail is None else detail.get("activehulls"),
            _race_csv(races, raceid, "basehulls"),
            hulls,
            _hull_icon,
            "advantage",
            ("techlevel",),
        )
        active_advantages, advantage_points = _union_items(
            None if detail is None else detail.get("activeadvantages"),
            _race_csv(races, raceid, "baseadvantages"),
            advantages,
            _advantage_icon,
            "value",
        )
        players.append(
            {
                "slot": starter["slot"],
                "name": starter["name"],
                "race": starter["race"],
                "team": league_team(account_payload.get("playergroups")),
                "officer_id": None if officer is None else officer["id"],
                "hulls": active_hulls,
                "advantages": active_advantages,
                "campaign_points": hull_points + advantage_points,
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


def _race_csv(races: dict[int, dict], raceid: int | None, field: str) -> str:
    if raceid is None:
        return ""
    race = races.get(raceid)
    if race is None:
        raise RosterError(f"static races has no id {raceid}")
    return race.get(field) or ""


def _id_set(csv: str | None) -> set[int]:
    ids: set[int] = set()
    for raw in (csv or "").split(","):
        token = raw.strip()
        if token:
            ids.add(int(token))
    return ids


def _default_state(item_id: int, active_ids: set[int], default_ids: set[int]) -> str:
    if item_id in active_ids and item_id in default_ids:
        return "same"
    if item_id in active_ids:
        return "added"
    return "removed"


def _union_items(
    active_csv: str | None,
    default_csv: str | None,
    catalog: dict[int, dict],
    icon_for,
    point_field: str,
    copy_fields: tuple[str, ...] = (),
) -> tuple[list[dict], int]:
    """Active ids plus that race's defaults. Owned-only ids are left out."""
    active_ids = _id_set(active_csv)
    default_ids = _id_set(default_csv)
    items = []
    points = 0
    for item_id in active_ids | default_ids:
        record = catalog.get(item_id)
        if record is None:
            raise RosterError(f"static catalog has no id {item_id}")
        state = _default_state(item_id, active_ids, default_ids)
        if state != "removed":
            points += record[point_field]
        item = {
            "id": item_id,
            "name": record["name"],
            "icon": icon_for(record),
            "default_state": state,
        }
        for field in copy_fields:
            item[field] = record[field]
        items.append(item)
    items.sort(key=lambda item: item["name"].casefold())
    return items, points


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
