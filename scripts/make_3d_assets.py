#!/usr/bin/env python3
"""
make_3d_assets.py - Generate 3D-inspired isometric vector SVGs for the GitHub profile.
Creates hero banners, 3D section badges, and status capsules with neon gradients.
"""

import html
import math
from pathlib import Path

OUT = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)

FONT = "ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO_FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

def esc(s: str) -> str:
    return html.escape(str(s), quote=True)

def iso_cube(cx, cy, s, top_col, left_col, right_col, stroke="#39d353", stroke_w=1):
    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))
    
    # Vertices
    p_top = (cx, cy - s)
    p_tr  = (cx + s * cos30, cy - s * sin30)
    p_br  = (cx + s * cos30, cy + s - s * sin30)
    p_bot = (cx, cy + s)
    p_bl  = (cx - s * cos30, cy + s - s * sin30)
    p_tl  = (cx - s * cos30, cy - s * sin30)
    p_cen = (cx, cy)
    
    top_pts = f"{p_top[0]:.1f},{p_top[1]:.1f} {p_tr[0]:.1f},{p_tr[1]:.1f} {p_cen[0]:.1f},{p_cen[1]:.1f} {p_tl[0]:.1f},{p_tl[1]:.1f}"
    left_pts = f"{p_tl[0]:.1f},{p_tl[1]:.1f} {p_cen[0]:.1f},{p_cen[1]:.1f} {p_bot[0]:.1f},{p_bot[1]:.1f} {p_bl[0]:.1f},{p_bl[1]:.1f}"
    right_pts = f"{p_tr[0]:.1f},{p_tr[1]:.1f} {p_cen[0]:.1f},{p_cen[1]:.1f} {p_bot[0]:.1f},{p_bot[1]:.1f} {p_br[0]:.1f},{p_br[1]:.1f}"
    
    return (
        f'<g>'
        f'<polygon points="{top_pts}" fill="{top_col}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
        f'<polygon points="{left_pts}" fill="{left_col}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
        f'<polygon points="{right_pts}" fill="{right_col}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
        f'</g>'
    )

def make_hero_banner():
    w, h = 840, 110
    cubes = []
    # Decorative 3D floating cubes
    cubes.append(iso_cube(52, 55, 24, "#00F2FE", "#0284c7", "#0369a1", stroke="#38bdf8", stroke_w=1.2))
    cubes.append(iso_cube(32, 28, 12, "#39D353", "#16a34a", "#15803d", stroke="#4ade80", stroke_w=1))
    cubes.append(iso_cube(72, 85, 10, "#a855f7", "#7e22ce", "#6b21a8", stroke="#c084fc", stroke_w=0.8))
    
    # Right side cubes
    cubes.append(iso_cube(790, 55, 24, "#39D353", "#16a34a", "#15803d", stroke="#4ade80", stroke_w=1.2))
    cubes.append(iso_cube(812, 28, 12, "#00F2FE", "#0284c7", "#0369a1", stroke="#38bdf8", stroke_w=1))
    cubes.append(iso_cube(768, 85, 10, "#ec4899", "#db2777", "#be185d", stroke="#f472b6", stroke_w=0.8))
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Mohammed Afsarudeen K - 3D Profile Header">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0c121e" stop-opacity="0.95"/>
      <stop offset="50%" stop-color="#080c14" stop-opacity="0.98"/>
      <stop offset="100%" stop-color="#05080e" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="neonBorder" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00F2FE"/>
      <stop offset="50%" stop-color="#39D353"/>
      <stop offset="100%" stop-color="#00F2FE"/>
    </linearGradient>
    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00F2FE"/>
      <stop offset="50%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#39D353"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#bgGrad)" stroke="#1e293b" stroke-width="1.5"/>
  <rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="13" fill="none" stroke="url(#neonBorder)" stroke-width="1.2" opacity="0.65"/>
  <path d="M 30 2 L {w - 30} 2" stroke="url(#neonBorder)" stroke-width="2.5" stroke-linecap="round" filter="url(#glow)"/>

  <line x1="120" y1="15" x2="720" y2="15" stroke="#1e293b" stroke-width="0.75" stroke-dasharray="4 6"/>
  <line x1="120" y1="95" x2="720" y2="95" stroke="#1e293b" stroke-width="0.75" stroke-dasharray="4 6"/>

  {''.join(cubes)}

  <g text-anchor="middle">
    <rect x="330" y="14" width="180" height="20" rx="10" fill="#131e30" stroke="#00F2FE" stroke-width="0.8" opacity="0.9"/>
    <circle cx="342" cy="24" r="3.5" fill="#39D353">
      <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="424" y="27.5" font-family="{MONO_FONT}" font-size="10" font-weight="600" fill="#38bdf8" letter-spacing="0.08em">FULL STACK DEVELOPER</text>

    <text x="420" y="62" font-family="{FONT}" font-size="25" font-weight="800" fill="url(#textGrad)" letter-spacing="0.06em">MOHAMMED AFSARUDEEN K</text>

    <text x="420" y="86" font-family="{FONT}" font-size="12" font-weight="500" fill="#94a3b8" letter-spacing="0.04em">
      React.js  ·  Node.js  ·  Express.js  ·  Tailwind CSS  ·  REST APIs  ·  PostgreSQL  ·  MySQL  ·  Prisma
    </text>
  </g>
</svg>'''
    (OUT / "banner-3d.svg").write_text(svg, encoding="utf-8")
    print("wrote assets/banner-3d.svg")

def make_section_badge(filename, num_str, title_str, subtitle_str, theme_accent="#00F2FE"):
    w, h = 580, 52
    sec_cube = iso_cube(28, 26, 14, theme_accent, "#0284c7" if theme_accent == "#00F2FE" else "#16a34a",
                        "#0369a1" if theme_accent == "#00F2FE" else "#15803d", stroke=theme_accent, stroke_w=1.2)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(num_str)} {esc(title_str)}">
  <defs>
    <linearGradient id="bgG_{filename}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#090d16" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="borderG_{filename}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{theme_accent}"/>
      <stop offset="60%" stop-color="#39D353"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="10" fill="url(#bgG_{filename})" stroke="#1e293b" stroke-width="1"/>
  <rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="9.5" fill="none" stroke="url(#borderG_{filename})" stroke-width="1.2" opacity="0.75"/>
  <path d="M 12 1.5 L {w - 12} 1.5" stroke="url(#borderG_{filename})" stroke-width="2" stroke-linecap="round"/>

  {sec_cube}

  <text x="54" y="24" font-family="{MONO_FONT}" font-size="11" font-weight="700" fill="{theme_accent}" letter-spacing="0.1em">{esc(num_str)}</text>
  <text x="100" y="24" font-family="{FONT}" font-size="14" font-weight="800" fill="#ffffff" letter-spacing="0.04em">{esc(title_str)}</text>
  <text x="54" y="41" font-family="{FONT}" font-size="10.5" font-weight="500" fill="#94a3b8">{esc(subtitle_str)}</text>
</svg>'''
    (OUT / f"{filename}.svg").write_text(svg, encoding="utf-8")
    print(f"wrote assets/{filename}.svg")

def make_status_badge():
    w, h = 540, 36
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Status: Available for Opportunities">
  <defs>
    <linearGradient id="stBg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0c1322"/>
      <stop offset="100%" stop-color="#08101a"/>
    </linearGradient>
    <linearGradient id="stBorder" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#39D353"/>
      <stop offset="50%" stop-color="#00F2FE"/>
      <stop offset="100%" stop-color="#39D353"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="url(#stBg)" stroke="url(#stBorder)" stroke-width="1.2"/>
  <circle cx="22" cy="18" r="4.5" fill="#39D353">
    <animate attributeName="r" values="4.5;5.5;4.5" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0.4;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text x="36" y="22" font-family="{FONT}" font-size="11.5" font-weight="600" fill="#e2e8f0" letter-spacing="0.03em">
    OPEN FOR FULL STACK OPPORTUNITIES <tspan fill="#64748b">|</tspan> <tspan fill="#38bdf8">Tuticorin, TN, India</tspan> <tspan fill="#64748b">|</tspan> <tspan fill="#39D353">Remote &amp; Onsite</tspan>
  </text>
</svg>'''
    (OUT / "badge-status.svg").write_text(svg, encoding="utf-8")
    print("wrote assets/badge-status.svg")

def main():
    make_hero_banner()
    make_status_badge()
    make_section_badge("sec-about", "01 //", "ABOUT & BACKGROUND", "Full Stack Developer · BCA Graduate · Jaz Infotech Alumni", "#00F2FE")
    make_section_badge("sec-skills", "02 //", "TECHNICAL STACK & RADAR", "Core engineering competencies & language distribution", "#39D353")
    make_section_badge("sec-repos", "03 //", "FEATURED REPOSITORIES", "Verified public repositories on GitHub with live stats", "#00F2FE")
    make_section_badge("sec-projects", "04 //", "KEY PROJECTS & CLIENT WORK", "Production client platforms, web apps & mobile systems", "#39D353")
    make_section_badge("sec-experience", "05 //", "WORK EXPERIENCE", "Professional internship tenure and engineering responsibilities", "#00F2FE")
    make_section_badge("sec-education", "06 //", "EDUCATION & CERTIFICATIONS", "Academic foundation, credentials, and continuous learning", "#39D353")
    make_section_badge("sec-telemetry", "07 //", "GITHUB TELEMETRY & STREAKS", "Live repository statistics, streaks, and contributions", "#00F2FE")
    make_section_badge("sec-connect", "08 //", "CONNECT & COLLABORATE", "Reach out for development opportunities and projects", "#39D353")

if __name__ == "__main__":
    main()
