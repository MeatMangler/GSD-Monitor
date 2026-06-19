---
phase: 12
slug: enhanced-visibility
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-18
---

# Phase 12 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| client -> API | planning_path parameter from frontend is untrusted input | URL path string |
| API -> frontend | Insights data rendered via React; no dangerouslySetInnerHTML | JSON (project metadata) |
| filesystem | REQUIREMENTS.md and PLAN.md files read from disk | Markdown file content |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-12-01 | Tampering | /api/insights/{planning_path} | mitigate | URL-decoded via `unquote(planning_path)`; endpoint only reads .planning/ files, never writes; follows same pattern as existing quick-tasks and docs endpoints | closed |
| T-12-02 | Information Disclosure | requirements_parser.py | accept | REQUIREMENTS.md content is project metadata, not secrets; app is local-only desktop | closed |
| T-12-03 | Denial of Service | _extract_wave_data | accept | Iterates local filesystem dirs; bounded by number of phase directories; desktop app with single user | closed |
| T-12-04 | Information Disclosure | InsightsPage | accept | All data is project metadata visible to local user; desktop app | closed |
| T-12-05 | Spoofing | fetchInsights | accept | Local loopback API; no auth needed for desktop single-user app | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-12-01 | T-12-02 | Project metadata is not sensitive; local-only desktop app | gsd-secure-phase | 2026-06-18 |
| AR-12-02 | T-12-03 | Bounded by local filesystem; single-user desktop app | gsd-secure-phase | 2026-06-18 |
| AR-12-03 | T-12-04 | Project metadata visible to local user only | gsd-secure-phase | 2026-06-18 |
| AR-12-04 | T-12-05 | Loopback API; no external network exposure | gsd-secure-phase | 2026-06-18 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-18 | 5 | 5 | 0 | gsd-secure-phase |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-18
