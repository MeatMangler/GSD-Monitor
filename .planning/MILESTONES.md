# Milestones

## v5.0 Installation and Distribution (Shipped: 2026-07-18)

**Phases completed:** 2 phases (17–18), 3 plans
**Closeout type:** override_closeout (Phase 17 missing VERIFICATION.md; Phase 18 has no phase directory)
**Known verification overrides:** 2 (see STATE.md Deferred Items)

**Key accomplishments:**

- `install.ps1`: single PowerShell script covering prereq checks (Git, Python 3.11+, Node.js, WebView2), clone, venv creation, `pip install -e .`, frontend build, `start.bat` launcher, and desktop shortcut — idempotent re-run routes to upgrade branch
- `upgrade.ps1` / `upgrade.bat`: standalone upgrade script with valid-install guard, `git pull` + `pip install -e .` + `npm ci && npm run build`, hash-based already-up-to-date detection
- `pyproject.toml` with hatchling and `dynamic = ["version"]` sourced from `gsd_monitor/__init__.py` — canonical version source for both pip and the API
- `/api/version` endpoint + ShellLayout sidebar footer badge — version string visible on every page at all times

**Git range:** d69ec64 → 1d76f6b | **Files:** 12 changed, +300/−45 lines | **Timeline:** 2026-07-18 (1 day)

---

## v3.0 gsd-core Migration (Shipped: 2026-06-19)

**Phases completed:** 2 phases, 4 plans, 10 tasks

**Key accomplishments:**

- gsd-core detection and parsing via config.json+heading ROADMAP, new doc type flags, HANDOFF.json/config.json/progress surfacing, and full GSD-2 code removal — 53 tests pass.
- React TypeScript frontend updated with gsd-core version badge, compact+detail progress bars, pause banner, config badge row, phase code display, and DocsPage quick-access shortcuts for new doc types — zero TypeScript errors, Vite build clean.
- Requirements traceability parser, wave extraction helper, and /api/insights endpoint providing the data layer for all four VIS requirements.
- Three-tab InsightsPage (Requirements, Waves, Archives) with gap highlighting, multi-wave phase grouping, and collapsible archived milestone accordions.

---
