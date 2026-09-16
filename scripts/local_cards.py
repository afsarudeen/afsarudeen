#!/usr/bin/env python3
"""
local_cards.py - render project cards for featured work that is NOT on the
public GitHub API (private, unpublished, or client work without a repo).

Stdlib only. Complements scripts/cards.py.

    python scripts/local_cards.py --projects assets/projects.json --out assets

A card is written only when the entry has no resolvable public repo on the
account (or when --force is set). Output: card-<slug>-{dark,light}.svg
where slug is the `repo` field (filename-safe).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Match cards.py theme tokens so the pair looks like one system
THEMES = {
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "title": "#39d353",
        "text": "#c9d1d9", "muted": "#8b949e", "value": "#e6edf3",
        "accent": "#39d353", "chip": "#21262d",
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "title": "#1a7f37",
        "text": "#1f2328", "muted": "#57606a", "value": "#1f2328",
        "accent": "#1a7f37", "chip": "#f6f8fa",
    },
}

LANG_COLOR = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "C++": "#f34b7d",
    "React.js": "#61dafb", "React": "#61dafb", "Next.js": "#ffffff",
    "Node.js": "#339933", "Express.js": "#ffffff", "Laravel": "#ff2d20",
    "MySQL": "#4479a1", "PostgreSQL": "#336791", "MongoDB": "#47a248",
    "Flutter": "#02569b", "Firebase": "#ffca28", "Tailwind CSS": "#38bdf8",
    "REST API": "#e34c26",
}

FONT = "ui-sans-serif,-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
ICON_REPO = (
    "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 "
    "0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 "
    "012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 "
    "12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 "
    "00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"
)


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


def icon(path, x, y, size, fill):
    s = size / 16
    return (f'<path transform="translate({x:.1f},{y:.1f}) scale({s:.3f})" '
            f'fill="{fill}" d="{path}"/>')


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-")
    return s or "project"


def render_card(entry: dict, theme: str) -> str:
    c = THEMES[theme]
    W, H = 420, 148
    pad = 18
    title = entry.get("title") or entry.get("repo") or "Project"
    kind = entry.get("kind") or ""
    desc = entry.get("description") or "No description yet."
    stack = entry.get("stack") or []
    primary = stack[0] if stack else None

    out = []
    out.append(icon(ICON_REPO, pad, pad, 15, c["muted"]))
    out.append(
        f'<text x="{pad + 22}" y="{pad + 12}" font-size="14.5" font-weight="700" '
        f'fill="{c["title"]}">{esc(title)}</text>'
    )
    if kind:
        out.append(
            f'<text x="{W - pad}" y="{pad + 12}" font-size="10.5" text-anchor="end" '
            f'fill="{c["muted"]}">{esc(kind)}</text>'
        )

    for i, line in enumerate(wrap(desc, 11.5, W - 2 * pad, 3)):
        out.append(
            f'<text x="{pad}" y="{pad + 36 + i * 16}" font-size="11.5" '
            f'fill="{c["text"]}">{esc(line)}</text>'
        )

    fy = H - pad - 2
    x = pad
    if primary:
        col = LANG_COLOR.get(primary, c["muted"])
        # On light theme Next.js/Express white dots need a border; keep simple
        if col.lower() in ("#ffffff", "#fff") and theme == "light":
            col = c["muted"]
        out.append(f'<circle cx="{x + 5}" cy="{fy - 4}" r="5" fill="{col}"/>')
        label = " · ".join(stack[:3]) if stack else primary
        out.append(
            f'<text x="{x + 15}" y="{fy}" font-size="11" fill="{c["muted"]}">'
            f'{esc(label)}</text>'
        )

    body = "".join(out)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="{esc(title)} project card" '
        f'font-family="{FONT}">'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f"{body}</svg>"
    )


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--projects", type=Path, default=Path("assets/projects.json"))
    p.add_argument("--out", type=Path, default=Path("assets"))
    p.add_argument("--force", action="store_true",
                   help="write local cards even when a matching GitHub card may exist")
    p.add_argument("--only-missing", action="store_true", default=True,
                   help="skip entries that already have card-<repo>-dark.svg from cards.py")
    args = p.parse_args(argv)

    if not args.projects.exists():
        sys.exit(f"no {args.projects}")

    data = json.loads(args.projects.read_text(encoding="utf-8"))
    projects = data.get("projects") or []
    args.out.mkdir(parents=True, exist_ok=True)

    # Entries that cards.py can cover: have a real public repo name that matched.
    # We treat an existing card-<repo>-dark.svg as "already generated by cards.py"
    # unless --force.
    written = 0
    for entry in projects:
        repo = entry.get("repo") or ""
        slug = slugify(repo or entry.get("title") or "project")
        local_stem = f"card-{slug}"
        dest_dark = args.out / f"{local_stem}-dark.svg"

        # Heuristic: cards.py writes GitHub-backed cards with the live repo
        # name and a 132px-tall frame. Local cards are 148px and use the
        # human title. If a public github URL is set AND cards.py already
        # produced a matching file, skip — unless --force.
        has_github = bool(entry.get("github"))
        if has_github and dest_dark.exists() and not args.force:
            # Peek aria-label: GitHub-backed cards say "<repo> repository card"
            label = dest_dark.read_text(encoding="utf-8")[:300]
            if "repository card" in label:
                print(f"  skip {slug} (GitHub-backed card present)")
                continue

        # Unpublished / client work (no github URL) always gets a local card.
        # Also rewrite when previous run left a local card or nothing.
        for theme in ("dark", "light"):
            dest = args.out / f"{local_stem}-{theme}.svg"
            dest.write_text(render_card(entry, theme), encoding="utf-8")
        print(f"wrote {local_stem}-*.svg")
        written += 1

    if written == 0:
        print("no local cards needed")


if __name__ == "__main__":
    main()
