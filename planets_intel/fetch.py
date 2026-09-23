"""Public planets.nu JSON used by the account, officer, hull, and advantage pages."""

import gzip
import json
import urllib.error
import urllib.parse
import urllib.request

from planets_intel.errors import RosterError
from planets_intel.progress import note
from planets_intel.roster import build_roster
from planets_intel.starters import select_starters

API = "http://api.planets.nu"


def fetch_roster(game_id: int) -> dict:
    note("game load")
    loadinfo = get_json("/game/loadinfo", {"gameid": game_id})
    static = get_json("/static/all", {})
    hulls = {hull["id"]: hull for hull in static["hulls"]}
    advantages = {advantage["id"]: advantage for advantage in static["advantages"]}
    races = {race["id"]: race for race in static["races"]}

    starters = select_starters(loadinfo)
    accounts: dict[str, dict] = {}
    officers_by_account: dict[int, list[dict]] = {}
    officer_details: dict[int, dict] = {}
    total = len(starters)
    for index, starter in enumerate(starters, start=1):
        step = f"{index}/{total} {starter['name']}"
        note(f"{step}: profile")
        profile = get_json("/account/loadprofile", {"username": starter["name"]})
        _require_success(profile, f"account {starter['name']}")
        accounts[starter["name"]] = profile
        account_id = profile["account"]["id"]
        note(f"{step}: officers")
        if account_id not in officers_by_account:
            officers_payload = get_json("/account/officers", {"accountid": account_id})
            _require_success(officers_payload, f"officers for account {account_id}")
            officers_by_account[account_id] = officers_payload["officers"]
        officer = _matching_officer(
            officers_by_account[account_id],
            starter["raceid"],
        )
        note(f"{step}: hulls")
        if officer is not None and officer["id"] not in officer_details:
            detail = get_json("/account/loadofficer", {"officerid": officer["id"]})
            _require_success(detail, f"officer {officer['id']}")
            officer_details[officer["id"]] = detail["officer"]
        note(f"{step}: advantages")
    return build_roster(
        loadinfo,
        accounts,
        officers_by_account,
        officer_details,
        hulls,
        advantages,
        races,
    )


def get_json(path: str, params: dict) -> dict:
    query = urllib.parse.urlencode(params)
    url = f"{API}{path}" if not query else f"{API}{path}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "planets-intel"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
    except urllib.error.URLError as exc:
        raise RosterError(f"GET {url} failed: {exc}") from exc
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RosterError(f"GET {url} did not return JSON") from exc
    if not isinstance(payload, dict):
        raise RosterError(f"GET {url} returned {type(payload).__name__}, not an object")
    return payload


def _require_success(payload: dict, label: str) -> None:
    if payload.get("success") is False:
        message = payload.get("error") or "request failed"
        raise RosterError(f"{label}: {message}")


def _matching_officer(officers: list[dict], raceid: int | None) -> dict | None:
    if raceid is None:
        return None
    for officer in officers:
        if officer.get("raceid") == raceid:
            return officer
    return None
