#!/usr/bin/env python3
"""
cards.py - render 3D-inspired dimensional GitHub stat and repo cards as SVGs. Stdlib only.

Replaces third-party card generators with reliable, self-hosted vector assets.
Writes <out>/card-stats-{dark,light}.svg plus one card per repo listed in
assets/projects.json, as <out>/card-<repo>-{dark,light}.svg.

    python scripts/cards.py --user afsarudeen --out assets
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "cards.py"}

THEMES = {
    "dark": {
        "bg_top": "#111827", "bg_bot": "#0a0e17",
        "border": "#243247", "border_glow": "#00F2FE",
        "title": "#39d353", "title_alt": "#00F2FE",
        "text": "#c9d1d9", "muted": "#8b949e", "value": "#e6edf3",
        "accent": "#39d353", "chip_bg": "#162032", "chip_border": "#283953",
    },
    "light": {
        "bg_top": "#ffffff", "bg_bot": "#f8fafc",
        "border": "#d0d7de", "border_glow": "#1a7f37",
        "title": "#1a7f37", "title_alt": "#0969da",
        "text": "#1f2328", "muted": "#57606a", "value": "#1f2328",
        "accent": "#1a7f37", "chip_bg": "#f3f4f6", "chip_border": "#d0d7de",
    },
}

# GitHub linguist colours for the languages likely to show up here
LANG_COLOR = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "C++": "#f34b7d", "C": "#555555",
    "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584", "Shell": "#89e051",
    "PLpgSQL": "#336790", "Vue": "#41b883", "Ruby": "#701516", "PHP": "#4F5D95",
    "Jupyter Notebook": "#DA5B0B", "SCSS": "#c6538c", "Svelte": "#ff3e00",
    "Dart": "#00B4AB", "Flutter": "#02569b",
}

FONT = "ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"

ICON_STAR = ("M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 "
             "2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 "
             "01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z")
ICON_FORK = ("M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75v-.878a2.25 2.25 0 "
             "111.5 0v.878a2.25 2.25 0 01-2.25 2.25h-1.5v2.128a2.251 2.251 0 11-1.5 "
             "0V8.5h-1.5A2.25 2.25 0 013.5 6.25v-.878a2.25 2.25 0 111.5 0zM5 3.25a.75.75 0 "
             "10-1.5 0 .75.75 0 001.5 0zm6.75.75a.75.75 0 100-1.5.75.75 0 000 1.5zm-3 "
             "8.75a.75.75 0 100-1.5.75.75 0 000 1.5z")
ICON_REPO = ("M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 "
             "0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 "
             "012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 "
             "12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 "
             "00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z")


def icon(path, x, y, size, fill):
    s = size / 16
    return (f'<path transform="translate({x:.1f},{y:.1f}) scale({s:.3f})" '
            f'fill="{fill}" d="{path}"/>')


# --------------------------------------------------------------------------- #
# api
# --------------------------------------------------------------------------- #


def rest(path: str, token: str | None):
    req = urllib.request.Request("https://api.github.com" + path, headers=dict(UA))
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def graphql(query: str, variables: dict, token: str):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body,
                                 headers={**UA, "Content-Type": "application/json",
                                          "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


CONTRIB_QUERY = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}
"""


def fetch_contributions(user: str, token: str | None):
    """Return (total, current_streak, longest_streak) or None without a token."""
    if not token:
        return None
    try:
        data = graphql(CONTRIB_QUERY, {"login": user}, token)
    except urllib.error.HTTPError as e:
        print(f"  contributions unavailable (HTTP {e.code})", file=sys.stderr)
        return None
    if data.get("errors"):
        print(f"  contributions unavailable: {data['errors'][0].get('message')}",
              file=sys.stderr)
        return None

    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
            for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort()

    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    current = 0
    for date, c in reversed(days):
        if c > 0:
            current += 1
        elif date != days[-1][0]:
            break
    return cal["totalContributions"], current, longest


# --------------------------------------------------------------------------- #
# svg helpers
# --------------------------------------------------------------------------- #


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def text_width(s: str, size: float) -> float:
    return len(s) * size * 0.53


def wrap(text: str, size: float, max_w: float, max_lines: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words:
        used = len(" ".join(lines).split())
        if used < len(words):
            while lines and text_width(lines[-1] + "…", size) > max_w:
                lines[-1] = lines[-1].rsplit(" ", 1)[0]
            lines[-1] += "…"
    return lines


def frame(w, h, c, body, label, theme="dark"):
    card_id = f"c_{theme}_{w}_{h}"
    defs = []
    defs.append(f'<linearGradient id="{card_id}_bg" x1="0%" y1="0%" x2="100%" y2="100%">')
    defs.append(f'<stop offset="0%" stop-color="{c["bg_top"]}"/>')
    defs.append(f'<stop offset="100%" stop-color="{c["bg_bot"]}"/>')
    defs.append('</linearGradient>')

    if theme == "dark":
        defs.append(f'<linearGradient id="{card_id}_edge" x1="0%" y1="0%" x2="100%" y2="0%">')
        defs.append('<stop offset="0%" stop-color="#00F2FE" stop-opacity="0.85"/>')
        defs.append('<stop offset="50%" stop-color="#39D353" stop-opacity="0.95"/>')
        defs.append('<stop offset="100%" stop-color="#4FACFE" stop-opacity="0.4"/>')
        defs.append('</linearGradient>')
        top_accent = f'<path d="M 14 1.5 L {w - 14} 1.5" stroke="url(#{card_id}_edge)" stroke-width="2" stroke-linecap="round"/>'
        ambient = (f'<circle cx="{w - 40}" cy="20" r="70" fill="#00F2FE" fill-opacity="0.04" filter="blur(20px)"/>'
                   f'<circle cx="30" cy="{h - 20}" r="60" fill="#39D353" fill-opacity="0.03" filter="blur(20px)"/>')
    else:
        top_accent = f'<path d="M 14 1.5 L {w - 14} 1.5" stroke="{c["border_glow"]}" stroke-width="2" stroke-linecap="round"/>'
        ambient = ""

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(label)}" '
        f'font-family="{FONT}">'
        f'<defs>{"".join(defs)}</defs>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" '
        f'fill="url(#{card_id}_bg)" stroke="{c["border"]}" stroke-width="1"/>'
        f'{top_accent}'
        f'{ambient}'
        f'{body}</svg>'
    )


# --------------------------------------------------------------------------- #
# cards
# --------------------------------------------------------------------------- #


def render_stats(user, stats, theme):
    c = THEMES[theme]
    pad = 20
    tiles = [(v, k) for k, v in stats]
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    rh, W = 58, 480
    H = pad + 46 + rows * rh + pad
    tw = (W - 2 * pad) / cols

    out = [
        f'<text x="{pad}" y="{pad + 15}" font-size="14" font-weight="700" letter-spacing="0.05em" '
        f'fill="{c["title"]}">{esc(user).upper()}</text>',
        f'<circle cx="{W - pad - 120}" cy="{pad + 11}" r="4" fill="{c["accent"]}"/>',
        f'<text x="{W - pad}" y="{pad + 15}" font-size="11" font-weight="600" text-anchor="end" '
        f'fill="{c["muted"]}">ACTIVITY TELEMETRY</text>',
        f'<line x1="{pad}" y1="{pad + 28}" x2="{W - pad}" y2="{pad + 28}" '
        f'stroke="{c["border"]}" stroke-opacity="0.8"/>',
    ]

    top = pad + 40
    for i, (value, label) in enumerate(tiles):
        col_idx = i % cols
        row_idx = i // cols
        cx = pad + col_idx * tw
        cy = top + row_idx * rh
        card_w = tw - 8
        card_h = 50

        # 3D-inspired recessed panel for each tile
        out.append(
            f'<rect x="{cx:.0f}" y="{cy:.0f}" width="{card_w:.0f}" height="{card_h:.0f}" rx="8" '
            f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{cx + 10:.0f}" y="{cy + 24:.0f}" font-size="18" font-weight="800" '
            f'fill="{c["value"]}">{esc(value)}</text>'
        )
        out.append(
            f'<text x="{cx + 10:.0f}" y="{cy + 40:.0f}" font-size="10" font-weight="500" '
            f'fill="{c["muted"]}">{esc(label)}</text>'
        )
    return frame(W, H, c, "".join(out), f"{user} GitHub statistics", theme)


def render_repo(repo, theme):
    c = THEMES[theme]
    W, H = 420, 142
    pad = 18
    out = []

    # 3D Icon container box
    out.append(
        f'<rect x="{pad}" y="{pad}" width="26" height="26" rx="6" '
        f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" stroke-width="1"/>'
    )
    out.append(icon(ICON_REPO, pad + 5, pad + 5, 16, c["title"]))

    out.append(
        f'<text x="{pad + 34}" y="{pad + 17}" font-size="14.5" font-weight="700" '
        f'fill="{c["title"]}">{esc(repo["name"])}</text>'
    )

    desc = repo.get("description") or "No description provided."
    for i, line in enumerate(wrap(desc, 11.5, W - 2 * pad, 3)):
        out.append(
            f'<text x="{pad}" y="{pad + 44 + i * 16}" font-size="11.5" '
            f'fill="{c["text"]}">{esc(line)}</text>'
        )

    fy = H - pad
    x = pad
    if repo.get("language"):
        lang = repo["language"]
        col = LANG_COLOR.get(lang, c["muted"])
        lw = text_width(lang, 10.5) + 24
        out.append(
            f'<rect x="{x}" y="{fy - 14}" width="{lw:.0f}" height="18" rx="9" '
            f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" stroke-width="1"/>'
        )
        out.append(f'<circle cx="{x + 8}" cy="{fy - 5}" r="4" fill="{col}"/>')
        out.append(
            f'<text x="{x + 16}" y="{fy - 1}" font-size="10.5" font-weight="600" fill="{c["text"]}">'
            f'{esc(lang)}</text>'
        )
        x += lw + 8

    for path, count in ((ICON_STAR, repo.get("stars", 0)),
                        (ICON_FORK, repo.get("forks", 0))):
        cw = text_width(str(count), 10.5) + 26
        out.append(
            f'<rect x="{x}" y="{fy - 14}" width="{cw:.0f}" height="18" rx="9" '
            f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" stroke-width="1"/>'
        )
        out.append(icon(path, x + 7, fy - 10, 11, c["muted"]))
        out.append(
            f'<text x="{x + 21}" y="{fy - 1}" font-size="10.5" font-weight="600" fill="{c["muted"]}">'
            f'{count}</text>'
        )
        x += cw + 8

    return frame(W, H, c, "".join(out), f'{repo["name"]} repository card', theme)


# --------------------------------------------------------------------------- #


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--user", required=True)
    p.add_argument("--out", type=Path, default=Path("assets"))
    p.add_argument("--projects", type=Path, default=Path("assets/projects.json"),
                   help="repos to render cards for, with description overrides")
    args = p.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    args.out.mkdir(parents=True, exist_ok=True)

    user = rest(f"/users/{args.user}", token)
    repos = []
    page = 1
    while True:
        batch = rest(f"/users/{args.user}/repos?per_page=100&page={page}&type=owner", token)
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    owned = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in owned)

    tiles = [("Total Stars", f"{stars:,}"),
             ("Public Repos", f"{user.get('public_repos', 0):,}"),
             ("Followers", f"{user.get('followers', 0):,}")]

    contrib = fetch_contributions(args.user, token)
    if contrib:
        total, current, longest = contrib
        tiles += [("Contributions (1y)", f"{total:,}"),
                  ("Current Streak", f"{current:,}"),
                  ("Longest Streak", f"{longest:,}")]
    else:
        print("  note: no usable token, skipping contribution tiles", file=sys.stderr)

    for theme in ("dark", "light"):
        dest = args.out / f"card-stats-{theme}.svg"
        dest.write_text(render_stats(args.user, tiles, theme), encoding="utf-8")
    print(f"wrote card-stats-*.svg  ({len(tiles)} tiles)")

    if not args.projects.exists():
        print(f"no {args.projects}, skipping repo cards")
        return
    wanted = json.loads(args.projects.read_text(encoding="utf-8"))["projects"]
    by_name = {r["name"].lower(): r for r in repos}

    for entry in wanted:
        src = by_name.get(entry["repo"].lower())
        if not src:
            print(f"  !! {entry['repo']} not found on the account, skipped")
            continue
        card = {
            "name": src["name"],
            "description": entry.get("description") or src.get("description"),
            "language": entry.get("language") or src.get("language"),
            "stars": src.get("stargazers_count", 0),
            "forks": src.get("forks_count", 0),
        }
        for theme in ("dark", "light"):
            dest = args.out / f"card-{src['name']}-{theme}.svg"
            dest.write_text(render_repo(card, theme), encoding="utf-8")
        print(f"wrote card-{src['name']}-*.svg  "
              f"({card['stars']}star {card['forks']}fork {card['language']})")


if __name__ == "__main__":
    main()
