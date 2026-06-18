---
phase: quick-260618-rat
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - frontend/src/pages/InsightsPage.tsx
  - frontend/src/index.css
autonomous: true
requirements:
  - UI-REVIEW-TOP3
must_haves:
  truths:
    - "API errors display a user-friendly message instead of raw error strings"
    - "InsightsPage has a visible 'Insights' heading above the tab bar"
    - "The six repeated hex color values are defined as CSS custom properties in index.css and referenced via var() in InsightsPage.tsx"
  artifacts:
    - path: "frontend/src/index.css"
      provides: "CSS custom property definitions for design tokens"
      contains: "--color-surface"
    - path: "frontend/src/pages/InsightsPage.tsx"
      provides: "Fixed error messages, h2 heading, token-based color references"
  key_links:
    - from: "frontend/src/index.css"
      to: "frontend/src/pages/InsightsPage.tsx"
      via: "CSS custom properties consumed via Tailwind arbitrary value syntax text-[var(--color-text-primary)]"
      pattern: "var\\(--color-"
---

<objective>
Fix the top 3 findings from the Phase 12 UI review in a single focused pass.

Purpose: Improve user trust (no raw errors), navigation orientation (page heading), and maintainability (token layer replaces 36 hardcoded hex literals).
Output: Updated InsightsPage.tsx and index.css with all three fixes applied and a rebuilt frontend dist.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/phases/12-enhanced-visibility/12-UI-REVIEW.md
@frontend/src/pages/InsightsPage.tsx
@frontend/src/index.css
</context>

<tasks>

<task type="auto">
  <name>Task 1: Define CSS color tokens in index.css</name>
  <files>frontend/src/index.css</files>
  <action>
    Add a `:root` block immediately after the `@import "tailwindcss";` line that defines six CSS custom properties matching the six hex values used throughout InsightsPage.tsx:

    - `--color-surface: #1e1e1e;` — card/panel background
    - `--color-surface-raised: #2a2d2e;` — active-state / badge background
    - `--color-border: #474747;` — borders
    - `--color-text-primary: #cccccc;` — primary text
    - `--color-text-muted: #858585;` — secondary / muted text
    - `--color-accent-green: #4ec994;` — success green

    Do not remove any existing rules. The final file should be:

    ```
    @import "tailwindcss";
    @plugin "@tailwindcss/typography";

    :root {
      --color-surface: #1e1e1e;
      --color-surface-raised: #2a2d2e;
      --color-border: #474747;
      --color-text-primary: #cccccc;
      --color-text-muted: #858585;
      --color-accent-green: #4ec994;
    }

    body {
      font-family: "Segoe UI", system-ui, sans-serif;
    }
    ```
  </action>
  <verify>
    <automated>grep -c "color-surface" frontend/src/index.css</automated>
  </verify>
  <done>index.css contains all six --color-* custom property declarations inside :root.</done>
</task>

<task type="auto">
  <name>Task 2: Apply all three UI review fixes to InsightsPage.tsx</name>
  <files>frontend/src/pages/InsightsPage.tsx</files>
  <action>
    Make three targeted changes to InsightsPage.tsx. Read the file first, then apply all changes via Edit (not Write):

    **Fix 1 — User-friendly error messages (lines 280 and 292):**
    Replace both occurrences of `<p className="text-sm text-red-400">Error: {insightsError}</p>` with:
    `<p className="text-sm text-red-400">Could not load insights — check that this project has a REQUIREMENTS.md file.</p>`
    The `{insightsError}` variable must NOT appear in the rendered JSX output (it exposed raw API error strings). Remove it from both the requirements tab block and the waves tab block.

    **Fix 2 — Add page heading (line 256, inside the main return div):**
    Insert an h2 immediately after the opening `<div className="p-6">` and before the tab bar div:
    `<h2 className="mb-4 text-base font-semibold text-[var(--color-text-primary)]">Insights</h2>`

    **Fix 3 — Replace hardcoded hex literals with CSS custom property references:**
    Replace every hardcoded hex color class throughout the file using these mappings:
    - `text-[#cccccc]` → `text-[var(--color-text-primary)]`
    - `text-[#858585]` → `text-[var(--color-text-muted)]`
    - `border-[#474747]` → `border-[var(--color-border)]`
    - `bg-[#1e1e1e]` → `bg-[var(--color-surface)]`
    - `bg-[#2a2d2e]` → `bg-[var(--color-surface-raised)]`
    - `text-[#4ec994]` → `text-[var(--color-accent-green)]`
    - `hover:bg-[#2a2d2e]` → `hover:bg-[var(--color-surface-raised)]`
    - `hover:text-[#cccccc]` → `hover:text-[var(--color-text-primary)]`

    Apply these replacements globally across all occurrences in the file. The two helper functions `statusBadgeClass` and `phaseBadgeClass` that return Tailwind class strings with hex values must also be updated.

    After all changes, the file must contain zero occurrences of any of these literal strings: `#cccccc`, `#858585`, `#474747`, `#1e1e1e`, `#2a2d2e`, `#4ec994`.
  </action>
  <verify>
    <automated>grep -c "#cccccc\|#858585\|#474747\|#1e1e1e\|#2a2d2e\|#4ec994" frontend/src/pages/InsightsPage.tsx || echo "0 hex literals remaining"</automated>
  </verify>
  <done>
    - InsightsPage.tsx contains no hardcoded hex color literals (0 matches for the six hex values)
    - An h2 with text "Insights" exists before the tab bar
    - Both error display blocks show the static user-friendly copy instead of the raw error variable
    - All color references use var(--color-*) custom properties
  </done>
</task>

<task type="auto">
  <name>Task 3: Rebuild frontend and verify TypeScript compilation</name>
  <files>frontend/dist/</files>
  <action>
    From the frontend/ directory, run the production build. This compiles TypeScript with tsc -b then bundles with Vite. Any TypeScript errors (unused variables, type mismatches from the JSX changes) must be fixed before the build succeeds.

    Command to run from repo root:
    `cd frontend && npm run build`

    If tsc reports errors about unused variables (e.g., `insightsError` is now unused after Fix 1), remove the unused state declaration and its setter call from InsightsPage.tsx. The `insightsError` useState and setInsightsError calls can be removed entirely if the error string is no longer rendered — or keep the state but change rendering to a static string (the latter is simpler and avoids removing the catch block).

    Recommended approach: keep `insightsError` state and `setInsightsError` as-is in the catch block (so the error is captured for debugging), but do not render `{insightsError}` in JSX. The noUnusedLocals TypeScript flag will NOT fire on state variables set in a catch block — only on completely unused local variables. Verify the build passes cleanly.
  </action>
  <verify>
    <automated>cd frontend && npm run build 2>&1 | tail -5</automated>
  </verify>
  <done>npm run build exits 0 with no TypeScript errors. frontend/dist/ is updated with the new bundle.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| API error → UI | Error messages from fetch() previously leaked raw strings to the user |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-rat-01 | Information Disclosure | InsightsPage error display | mitigate | Replace raw Error.message with static user-friendly copy — no internal API detail exposed |
| T-rat-SC | Tampering | npm build step | accept | No new packages installed; existing lockfile unchanged |
</threat_model>

<verification>
After all tasks complete:
1. Open InsightsPage in the app and trigger an error condition (disconnect backend) — confirm the error message reads "Could not load insights — check that this project has a REQUIREMENTS.md file." with no raw error string
2. Confirm "Insights" h2 heading is visible above the tab bar
3. Inspect element in DevTools — confirm no inline hex color literals; all colors come from CSS custom properties
4. Run: `grep -rn "#cccccc\|#858585\|#474747\|#1e1e1e\|#2a2d2e\|#4ec994" frontend/src/pages/InsightsPage.tsx` — expect 0 matches
</verification>

<success_criteria>
- InsightsPage.tsx renders "Insights" as an h2 before the tab bar
- Both error states show static copy, not raw Error.message output
- Zero hardcoded hex literals remain in InsightsPage.tsx (all replaced with var(--color-*))
- Six CSS custom properties defined in index.css :root block
- Frontend production build exits 0 with no TypeScript errors
</success_criteria>

<output>
Create `.planning/quick/260618-rat-fix-ui-review-findings-user-friendly-err/260618-rat-SUMMARY.md` when done
</output>
