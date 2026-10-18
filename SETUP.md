# Setup — afsarudeen profile README

Profile repository: **`github.com/afsarudeen/afsarudeen`**.  
That magic repo’s README is what shows on the GitHub profile.

Architecture (portrait · radars · cards · metrics · snake) is generated/automated.  
Personal content lives in `README.md`, `assets/skills.json`, and `assets/projects.json`.

---

## 1. Push the repo

```bash
cd afsarudeen   # this directory
git init && git branch -M main
git add -A && git commit -m "profile readme"
git remote add origin https://github.com/afsarudeen/afsarudeen.git
git push -u origin main
```

The repo must be **public** — SVG assets load by URL; a private repo shows broken images.

---

## 2. Let Actions write to the repo

Repo → **Settings** → **Actions** → **General** → **Workflow permissions** →  
select **Read and write permissions** → Save.

Without this, Radar and Snake workflows fail on push.

---

## 3. Add the metrics token

`lowlighter/metrics` needs its own token — the built-in `GITHUB_TOKEN` can’t read profile metrics plugins fully.

1. https://github.com/settings/tokens → **Generate new token (classic)**
2. Scopes: **`read:user`** (add **`repo`** if you want private repos counted)
3. Repo → **Settings** → **Secrets and variables** → **Actions** →  
   **New repository secret** → name **`METRICS_TOKEN`**, paste the value

> **Note on Metrics Workflow:** The automated cron schedule in `.github/workflows/metrics.yml`
> has been deliberately disabled because `METRICS_TOKEN` was unconfigured, causing repeated 42–46s failure emails every 6 hours.
> Once you add `METRICS_TOKEN`, you can uncomment the schedule in `.github/workflows/metrics.yml` and test it via manual `workflow_dispatch`.

---

## 4. Workflows & Automation

Repo → **Actions** → **Run workflow** on each:

| workflow | status | produces | lands in |
|---|---|---|---|
| **Charts and cards** | Active (daily) | spider charts, stat card, verified repo cards | `assets/radar*.svg`, `assets/card-*.svg` on `main` |
| **Snake** | Active (12h) | snake eating the contribution graph | the `output` branch |
| **Metrics** | Standby / Manual | 3D isometric calendar, languages, achievements | `assets/metrics.*.svg` (requires `METRICS_TOKEN`) |


---

## 5. Portrait (already generated)

Source cutout: `assets/portrait-source.png` (under 1 MB).  
Dot-matrix SVG: `assets/portrait.svg`.

Regenerate:

```bash
python scripts/dotify.py assets/portrait-source.png -o assets/portrait \
  --cols 100 --equalize --detail 0.5 --color --reveal
```

Open `preview.html` to replay the row-reveal animation.

---

## 6. Local regeneration cheatsheet
 
```bash
# 3D vector headers, banner, and status badges
python scripts/make_3d_assets.py

# skill radar (from assets/skills.json)
python scripts/radar.py --data assets/skills.json -o assets/radar

# language radar (live GitHub language bytes)
python scripts/radar.py --github afsarudeen -o assets/radar-langs --limit 7 --values --curve 0.4

# stats + GitHub-backed project cards (verified public repos)
python scripts/cards.py --user afsarudeen --projects assets/projects.json --out assets

# cards for work without a public repo (client / unpublished)
python scripts/local_cards.py --projects assets/projects.json --out assets
```

---

## 7. Editing content

| What | Where |
|------|--------|
| Bio, experience, education, certs | `README.md` |
| Skill radar shape | `assets/skills.json` (visualization scale 0–100, not “measured skill %”) |
| Featured projects | `assets/projects.json` + README table |
| Metrics username | `.github/workflows/metrics.yml` (`user: afsarudeen`) |
| Snake username | uses `github.repository_owner` automatically |
| Social links | README badge URLs |

---

## If something looks broken

**Images don’t load on the profile.** Repo must be public; paths are relative (`assets/…`).

**Metrics workflow fails.** Almost always `METRICS_TOKEN`: missing, expired, or fine-grained instead of classic.

**Snake images 404.** Snake workflow hasn’t completed, or write permissions were skipped.

**Stats tiles missing contributions.** cards.py needs a token (workflow passes `METRICS_TOKEN`) for GraphQL streak/contribution tiles.
