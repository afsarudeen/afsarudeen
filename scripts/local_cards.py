#!/usr/bin/env python3
"""
local_cards.py - render 3D-inspired project cards for featured work that is NOT on the
public GitHub API (private, unpublished, or client work without a repo).

Stdlib only. Complements scripts/cards.py.

    python scripts/local_cards.py --projects assets/projects.json --out assets
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

LANG_COLOR = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "C++": "#f34b7d",
    "React.js": "#61dafb", "React": "#61dafb", "Next.js": "#ffffff",
    "Node.js": "#339933", "Express.js": "#ffffff", "Laravel": "#ff2d20",
    "MySQL": "#4479a1", "PostgreSQL": "#336791", "MongoDB": "#47a248",
    "Flutter": "#02569b", "Firebase": "#ffca28", "Tailwind CSS": "#38bdf8",
    "REST API": "#e34c26", "Dart": "#00B4AB",
}

FONT = "ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
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
    W, H = 420, 142
    pad = 18
    title = entry.get("title") or entry.get("repo") or "Project"
    kind = entry.get("kind") or ""
    desc = entry.get("description") or "No description provided."
    stack = entry.get("stack") or []
    primary = stack[0] if stack else None

    card_id = f"lc_{theme}_{slugify(title)}"
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
        top_accent = f'<path d="M 14 1.5 L {W - 14} 1.5" stroke="url(#{card_id}_edge)" stroke-width="2" stroke-linecap="round"/>'
        ambient = (f'<circle cx="{W - 40}" cy="20" r="70" fill="#00F2FE" fill-opacity="0.04" filter="blur(20px)"/>'
                   f'<circle cx="30" cy="{H - 20}" r="60" fill="#39D353" fill-opacity="0.03" filter="blur(20px)"/>')
    else:
        top_accent = f'<path d="M 14 1.5 L {W - 14} 1.5" stroke="{c["border_glow"]}" stroke-width="2" stroke-linecap="round"/>'
        ambient = ""

    out = []
    # 3D Icon container box
    out.append(
        f'<rect x="{pad}" y="{pad}" width="26" height="26" rx="6" '
        f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" stroke-width="1"/>'
    )
    out.append(icon(ICON_REPO, pad + 5, pad + 5, 16, c["title"]))

    out.append(
        f'<text x="{pad + 34}" y="{pad + 17}" font-size="14.5" font-weight="700" '
        f'fill="{c["title"]}">{esc(title)}</text>'
    )
    if kind:
        out.append(
            f'<text x="{W - pad}" y="{pad + 17}" font-size="10.5" font-weight="600" text-anchor="end" '
            f'fill="{c["muted"]}">{esc(kind)}</text>'
        )

    for i, line in enumerate(wrap(desc, 11.5, W - 2 * pad, 3)):
        out.append(
            f'<text x="{pad}" y="{pad + 44 + i * 16}" font-size="11.5" '
            f'fill="{c["text"]}">{esc(line)}</text>'
        )

    fy = H - pad
    x = pad
    if primary:
        col = LANG_COLOR.get(primary, c["muted"])
        if col.lower() in ("#ffffff", "#fff") and theme == "light":
            col = c["muted"]
        label = " · ".join(stack[:3]) if stack else primary
        lw = text_width(label, 10.5) + 24
        out.append(
            f'<rect x="{x}" y="{fy - 14}" width="{lw:.0f}" height="18" rx="9" '
            f'fill="{c["chip_bg"]}" stroke="{c["chip_border"]}" stroke-width="1"/>'
        )
        out.append(f'<circle cx="{x + 8}" cy="{fy - 5}" r="4" fill="{col}"/>')
        out.append(
            f'<text x="{x + 16}" y="{fy - 1}" font-size="10.5" font-weight="600" fill="{c["text"]}">'
            f'{esc(label)}</text>'
        )

    body = "".join(out)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="{esc(title)} project card" '
        f'font-family="{FONT}">'
        f'<defs>{"".join(defs)}</defs>'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
        f'fill="url(#{card_id}_bg)" stroke="{c["border"]}" stroke-width="1"/>'
        f'{top_accent}'
        f'{ambient}'
        f'{body}</svg>'
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

    written = 0
    for entry in projects:
        repo = entry.get("repo") or ""
        slug = slugify(repo or entry.get("title") or "project")
        local_stem = f"card-{slug}"
        dest_dark = args.out / f"{local_stem}-dark.svg"

        has_github = bool(entry.get("github"))
        if has_github and dest_dark.exists() and not args.force:
            label = dest_dark.read_text(encoding="utf-8")[:300]
            if "repository card" in label:
                print(f"  skip {slug} (GitHub-backed card present)")
                continue

        for theme in ("dark", "light"):
            dest = args.out / f"{local_stem}-{theme}.svg"
            dest.write_text(render_card(entry, theme), encoding="utf-8")
        print(f"wrote {local_stem}-*.svg")
        written += 1

    if written == 0:
        print("no local cards needed")


if __name__ == "__main__":
    main()
