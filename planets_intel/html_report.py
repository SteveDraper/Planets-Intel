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
<body class="min-h-screen bg-stone-50 text-stone-900 antialiased">
  <header class="border-b border-stone-200 bg-white">
    <div class="mx-auto max-w-5xl px-4 py-3">
      <p class="text-sm font-semibold tracking-tight">Planets Intel</p>
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
      <h1 class="text-lg font-semibold tracking-tight">{html.escape(title)}</h1>
      <p class="mt-4"><a href="#teams" class="text-sm font-medium text-stone-700 underline underline-offset-4">Team summary</a></p>
      <div class="mt-4 overflow-hidden rounded-lg border border-stone-200 bg-white">
        <table id="roster" class="w-full border-collapse text-left text-sm">
          <thead class="border-b border-stone-200 bg-stone-50">
            <tr>
              <th class="px-3 py-2 font-medium" scope="col"><button type="button" data-sort="0" class="cursor-pointer font-medium">Name</button></th>
              <th class="px-3 py-2 font-medium" scope="col"><button type="button" data-sort="1" class="cursor-pointer font-medium">Race</button></th>
              <th class="px-3 py-2 font-medium" scope="col"><button type="button" data-sort="2" class="cursor-pointer font-medium">League team</button></th>
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
    return f"""            <tr class="border-t border-stone-200">
              <td class="px-3 py-2">{html.escape(player["name"])}</td>
              <td class="px-3 py-2"><a href="#player-{slot}" class="text-stone-700 underline underline-offset-4">{html.escape(player["race"])}</a></td>
              <td class="px-3 py-2">{html.escape(team)}</td>
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
      <p><a href="#home" class="text-sm font-medium text-stone-700 underline underline-offset-4">Back</a></p>
      <h1 class="mt-4 text-lg font-semibold tracking-tight">Team summary</h1>
      <div class="mt-4 grid gap-4">
{sections}
      </div>
    </section>"""


def _team_section(name: str, players: list[dict]) -> str:
    ordered = sorted(players, key=lambda player: player["name"].casefold())
    rows = "\n".join(
        f"""              <tr class="border-t border-stone-200">
                <td class="px-3 py-2">{html.escape(player["name"])}</td>
                <td class="px-3 py-2">{html.escape(player["race"])}</td>
              </tr>"""
        for player in ordered
    )
    return f"""        <section class="overflow-hidden rounded-lg border border-stone-200 bg-white">
          <h2 class="border-b border-stone-200 px-3 py-2 text-sm font-semibold">{html.escape(name)}</h2>
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
      <p><a href="#home" class="text-sm font-medium text-stone-700 underline underline-offset-4">Back</a></p>
      <h1 class="mt-4 text-lg font-semibold tracking-tight">{html.escape(heading)}</h1>
      <div class="mt-4 grid gap-4">
        {_item_table("Hulls", player["hulls"])}
        {_item_table("Advantages", player["advantages"])}
      </div>
    </section>"""


def _item_table(caption: str, items: list[dict]) -> str:
    rows = "\n".join(_item_row(item) for item in items)
    return f"""        <div class="overflow-hidden rounded-lg border border-stone-200 bg-white">
          <table class="w-full border-collapse text-left text-sm">
            <caption class="border-b border-stone-200 px-3 py-2 text-left text-sm font-semibold">{html.escape(caption)}</caption>
            <tbody>
{rows}
            </tbody>
          </table>
        </div>"""


def _item_row(item: dict) -> str:
    icon = item.get("icon")
    image = ""
    if isinstance(icon, str) and icon.startswith("data:"):
        image = (
            f'<img src="{html.escape(icon, quote=True)}" alt="" '
            'class="h-8 w-8 object-contain">'
        )
    return f"""              <tr class="border-t border-stone-200">
                <td class="px-3 py-2">{image}{html.escape(item["name"])}</td>
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
      if (!roster) return;
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
    })();
"""
