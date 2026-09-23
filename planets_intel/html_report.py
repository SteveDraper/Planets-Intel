"""Pure HTML transform of a roster report."""

import html

_NONE = "<None>"
_CSS_MARKER = "/*__TAILWIND_CSS__*/"


def render_roster_html(report: dict, css: str) -> str:
    """One self-contained page. Icon values are embedded only when they are data URIs."""
    game = report["game"]
    title = _title(game)
    players = report["players"]
    body = "\n".join(
        [
            _home(title, players),
            _teams(players),
            *[_detail(player) for player in players],
        ]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body class="min-h-screen bg-black font-sans text-white antialiased">
  <header class="border-b border-[#222] bg-[rgb(34,40,40)]">
    <div class="mx-auto max-w-5xl px-4 py-3">
      <p class="text-sm uppercase tracking-wide text-[rgba(200,200,200,0.75)]">Planets Intel</p>
    </div>
  </header>
  <main>
{body}
  </main>
  <script>
{_SCRIPT}
  </script>
</body>
</html>
"""


def css_marker() -> str:
    return _CSS_MARKER


def _title(game: dict) -> str:
    game_type = game["type"]
    base = f"{game['name']} ({game['id']})"
    if game_type:
        return f"{base} {game_type}"
    return base


def _home(title: str, players: list[dict]) -> str:
    rows = "\n".join(_player_row(player) for player in players)
    return f"""    <section id="home" data-viewport="home" aria-label="Roster" class="mx-auto w-full max-w-5xl px-4 py-6">
      <h1 class="text-[17px] font-normal text-[#cceeee]">{html.escape(title)}</h1>
      <p class="mt-4"><a href="#teams" class="text-sm text-[#00ffff] no-underline">Team summary</a></p>
      <div class="mt-4 overflow-hidden rounded-[5px] bg-[linear-gradient(to_bottom,rgb(52,60,60),rgb(26,30,30))] shadow-[0_2px_3px_0_rgba(0,0,0,0.75)]">
        <table id="roster" class="w-full border-collapse text-left text-sm">
          <thead class="bg-[rgb(34,40,40)] text-[rgba(200,200,200,0.75)]">
            <tr>
              <th class="px-5 py-2.5 font-normal uppercase" scope="col"><button type="button" data-sort="0" class="cursor-pointer font-normal uppercase">Name</button></th>
              <th class="px-5 py-2.5 font-normal uppercase" scope="col"><button type="button" data-sort="1" class="cursor-pointer font-normal uppercase">Race</button></th>
              <th class="px-5 py-2.5 font-normal uppercase" scope="col"><button type="button" data-sort="2" class="cursor-pointer font-normal uppercase">League team</button></th>
            </tr>
          </thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </section>"""


def _player_row(player: dict) -> str:
    slot = player["slot"]
    team = _team_text(player["team"])
    return f"""            <tr class="border-b border-[#222] hover:bg-[linear-gradient(to_bottom,rgba(64,80,80,0.25),rgba(34,40,40,0.25))]">
              <td class="px-5 py-3">{html.escape(player["name"])}</td>
              <td class="px-5 py-3"><a href="#player-{slot}" class="text-[#00ffff] no-underline">{html.escape(player["race"])}</a></td>
              <td class="px-5 py-3">{html.escape(team)}</td>
            </tr>"""


def _teams(players: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for player in players:
        grouped.setdefault(_team_text(player["team"]), []).append(player)
    names = sorted(name for name in grouped if name != _NONE)
    if _NONE in grouped:
        names.append(_NONE)
    sections = "\n".join(_team_section(name, grouped[name]) for name in names)
    return f"""    <section id="teams" data-viewport="teams" aria-label="Team summary" hidden class="mx-auto w-full max-w-5xl px-4 py-6">
      <p><a href="#home" class="text-sm text-[#00ffff] no-underline">Back</a></p>
      <h1 class="mt-4 text-[17px] font-normal text-[#cceeee]">Team summary</h1>
      <div class="mt-4 grid gap-4">
{sections}
      </div>
    </section>"""


def _team_section(name: str, players: list[dict]) -> str:
    ordered = sorted(players, key=lambda player: player["name"].casefold())
    rows = "\n".join(
        f"""              <tr class="border-b border-[#222]">
                <td class="px-5 py-3">{html.escape(player["name"])}</td>
                <td class="px-5 py-3 text-[#00ffff]">{html.escape(player["race"])}</td>
              </tr>"""
        for player in ordered
    )
    return f"""        <section class="overflow-hidden rounded-[5px] bg-[linear-gradient(to_bottom,rgb(52,60,60),rgb(26,30,30))] shadow-[0_2px_3px_0_rgba(0,0,0,0.75)]">
          <h2 class="bg-[rgb(34,40,40)] px-2.5 py-2.5 text-sm uppercase text-[rgba(200,200,200,0.75)]">{html.escape(name)}</h2>
          <table class="w-full border-collapse text-left text-sm">
            <tbody>
{rows}
            </tbody>
          </table>
        </section>"""


def _detail(player: dict) -> str:
    slot = player["slot"]
    heading = f"{player['name']} ({player['race']})"
    return f"""    <section id="player-{slot}" data-viewport="detail" aria-label="{html.escape(player["name"], quote=True)}" hidden class="mx-auto w-full max-w-5xl px-4 py-6">
      <p><a href="#home" class="text-sm text-[#00ffff] no-underline">Back</a></p>
      <h1 class="mt-4 text-[17px] font-normal text-[#cceeee]">{html.escape(heading)}</h1>
      <p class="mt-4 text-sm text-[rgba(200,200,200,0.75)]">Campaign points used <b class="font-normal text-[#00ffff]">{player["campaign_points"]}</b></p>
      <div class="mt-4 grid gap-4">
        {_item_table("Hulls", player["hulls"], hull_sort=True)}
        {_item_table("Advantages", player["advantages"])}
      </div>
    </section>"""


_CAPTION = (
    "bg-[rgb(34,40,40)] px-2.5 py-2.5 text-left text-sm uppercase "
    "text-[rgba(200,200,200,0.75)]"
)
_HULL_SORT_BUTTON = (
    "cursor-pointer font-normal uppercase text-[rgba(200,200,200,0.75)] "
    "aria-pressed:text-[#00ffff]"
)


def _item_table(caption: str, items: list[dict], hull_sort: bool = False) -> str:
    rows = "\n".join(_item_row(item, hull_sort) for item in items)
    table_attr = " data-hull-table" if hull_sort else ""
    caption_class = _CAPTION
    caption_body = html.escape(caption)
    if hull_sort:
        caption_class += " flex items-center justify-between"
        caption_body = f"<span>{caption_body}</span>{_hull_sort_control()}"
    return f"""        <div class="overflow-hidden rounded-[5px] bg-[linear-gradient(to_bottom,rgb(52,60,60),rgb(26,30,30))] shadow-[0_2px_3px_0_rgba(0,0,0,0.75)]">
          <table{table_attr} class="w-full border-collapse text-left text-sm">
            <caption class="{caption_class}">{caption_body}</caption>
            <tbody>
{rows}
            </tbody>
          </table>
        </div>"""


def _hull_sort_control() -> str:
    return f"""<span class="flex items-center gap-6">
              <span class="flex gap-3">
                <button type="button" data-hull-sort="name" aria-pressed="true" class="{_HULL_SORT_BUTTON}">Name</button>
                <button type="button" data-hull-sort="techlevel" aria-pressed="false" class="{_HULL_SORT_BUTTON}">Tech level</button>
              </span>
              <span class="flex gap-3">
                <button type="button" data-hull-dir="asc" aria-pressed="true" aria-label="Ascending" class="{_HULL_SORT_BUTTON} inline-flex items-center">{_arrow_icon("up")}</button>
                <button type="button" data-hull-dir="desc" aria-pressed="false" aria-label="Descending" class="{_HULL_SORT_BUTTON} inline-flex items-center">{_arrow_icon("down")}</button>
              </span>
            </span>"""


def _arrow_icon(direction: str) -> str:
    path = {
        "up": "M8 13V3M4.5 6.5 8 3l3.5 3.5",
        "down": "M8 3v10M4.5 9.5 8 13l3.5-3.5",
    }[direction]
    return (
        '<svg viewBox="0 0 16 16" aria-hidden="true" class="h-4 w-4" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
        'stroke-linejoin="round">'
        f'<path d="{path}"/></svg>'
    )


def _item_row(item: dict, hull_sort: bool = False) -> str:
    icon = item.get("icon")
    image = ""
    if isinstance(icon, str) and icon.startswith("data:"):
        image = (
            f'<img src="{html.escape(icon, quote=True)}" alt="" '
            'class="mr-2.5 h-[60px] w-[60px] rounded-[5px] bg-black object-contain">'
        )
    attrs = ""
    if hull_sort:
        name = html.escape(item["name"], quote=True)
        level = html.escape(str(item["techlevel"]), quote=True)
        attrs = f' data-name="{name}" data-techlevel="{level}"'
    return f"""              <tr{attrs} class="border-b border-[#222] hover:bg-[linear-gradient(to_bottom,rgba(64,80,80,0.25),rgba(34,40,40,0.25))]">
                <td class="px-5 py-3"><span class="flex items-center">{image}<b class="font-normal text-[#00ffff]">{html.escape(item["name"])}</b></span></td>
              </tr>"""


def _team_text(team: str | None) -> str:
    if team is None:
        return _NONE
    return team


_SCRIPT = """
    (function () {
      var sections = Array.prototype.slice.call(document.querySelectorAll("[data-viewport]"));

      function showFromHash() {
        var hash = location.hash || "#home";
        var match = null;
        if (hash === "#home" || hash === "#teams") {
          match = hash.slice(1);
        } else if (hash.indexOf("#player-") === 0) {
          match = hash.slice(1);
        }
        sections.forEach(function (section) {
          var visible = match !== null && section.id === match;
          section.hidden = !visible;
        });
        if (match === null && sections.length) {
          sections.forEach(function (section) {
            section.hidden = section.id !== "home";
          });
        }
      }

      window.addEventListener("hashchange", showFromHash);
      showFromHash();

      var roster = document.getElementById("roster");
      if (roster) {
        var tbody = roster.querySelector("tbody");
        roster.querySelectorAll("button[data-sort]").forEach(function (button) {
          button.addEventListener("click", function () {
            var index = Number(button.getAttribute("data-sort"));
            var next = button.getAttribute("data-dir") === "asc" ? "desc" : "asc";
            roster.querySelectorAll("button[data-sort]").forEach(function (other) {
              other.removeAttribute("data-dir");
            });
            button.setAttribute("data-dir", next);
            var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
            rows.sort(function (left, right) {
              var a = left.cells[index].textContent.trim().toLowerCase();
              var b = right.cells[index].textContent.trim().toLowerCase();
              if (a < b) return next === "asc" ? -1 : 1;
              if (a > b) return next === "asc" ? 1 : -1;
              return 0;
            });
            rows.forEach(function (row) { tbody.appendChild(row); });
          });
        });
      }

      document.querySelectorAll("table[data-hull-table]").forEach(function (table) {
        var body = table.querySelector("tbody");
        var keyButtons = table.querySelectorAll("button[data-hull-sort]");
        var dirButtons = table.querySelectorAll("button[data-hull-dir]");
        var mode = "name";
        var direction = "asc";

        function nameOrder(left, right) {
          var nameLeft = (left.getAttribute("data-name") || "").toLowerCase();
          var nameRight = (right.getAttribute("data-name") || "").toLowerCase();
          if (nameLeft < nameRight) return -1;
          if (nameLeft > nameRight) return 1;
          return 0;
        }

        function apply() {
          var rows = Array.prototype.slice.call(body.querySelectorAll("tr"));
          rows.sort(function (left, right) {
            if (mode === "techlevel") {
              var levelLeft = Number(left.getAttribute("data-techlevel"));
              var levelRight = Number(right.getAttribute("data-techlevel"));
              if (levelLeft !== levelRight) {
                var byLevel = levelLeft - levelRight;
                return direction === "asc" ? byLevel : -byLevel;
              }
              return nameOrder(left, right);
            }
            var byName = nameOrder(left, right);
            return direction === "asc" ? byName : -byName;
          });
          rows.forEach(function (row) { body.appendChild(row); });
          keyButtons.forEach(function (button) {
            var selected = button.getAttribute("data-hull-sort") === mode;
            button.setAttribute("aria-pressed", selected ? "true" : "false");
          });
          dirButtons.forEach(function (button) {
            var selected = button.getAttribute("data-hull-dir") === direction;
            button.setAttribute("aria-pressed", selected ? "true" : "false");
          });
        }

        keyButtons.forEach(function (button) {
          button.addEventListener("click", function () {
            mode = button.getAttribute("data-hull-sort");
            apply();
          });
        });
        dirButtons.forEach(function (button) {
          button.addEventListener("click", function () {
            direction = button.getAttribute("data-hull-dir");
            apply();
          });
        });
      });
    })();
"""
