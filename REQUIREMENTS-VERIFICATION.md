# GSD Monitor v5.0 — Requirements Verification

Manual verification steps for all v5.0 requirements. Run these on a Windows machine with Git, Python 3.11+, and Node.js installed.

---

## INST-01 — End-to-end fresh install via single script

**Requirement:** User can run a single PowerShell script on a clean Windows machine (Git + Python 3.11+ + Node.js present) and end up with GSD Monitor fully installed and launchable via a desktop shortcut.

**Steps:**
1. On a machine with Git, Python 3.11+, and Node.js on PATH (but no existing GSD Monitor install):
   ```powershell
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```
2. Accept defaults when prompted for install directory.
3. Observe output — all steps should show green `[OK]` lines for Git, Python, Node, WebView2, clone, pip install, npm build, start.bat, and desktop shortcut.
4. Locate the desktop shortcut ("Start GSD Monitor") and double-click it.

**Pass criteria:** GSD Monitor window opens and the dashboard loads without errors.

---

## INST-02 — WebView2 missing check

**Requirement:** Installer checks for WebView2 and prints a clear message with a download link if absent.

**Steps:**
1. Run `install.ps1` on a machine where WebView2 is not installed (or simulate by temporarily renaming the registry key `HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226...}`).
2. Observe script output at the WebView2 check step.

**Pass criteria:** Script prints a message containing "Microsoft Edge WebView2 Runtime not found" and a URL to `https://developer.microsoft.com/microsoft-edge/webview2/` then exits with a non-zero code. No further steps execute.

---

## INST-03 — Missing prerequisite error messages

**Requirement:** Installer exits with a human-readable error naming any missing prerequisite (Git, Python, Node.js).

**Steps (test each independently):**

1. **Git missing:** Temporarily remove Git from PATH (or test on machine without Git).
   - Run `install.ps1`
   - Expected: prints "Git not found." with a download link and exits immediately.

2. **Python missing:** Remove Python from PATH.
   - Run `install.ps1`
   - Expected: prints "Python not found." with a download link and exits immediately.

3. **Node.js missing:** Remove Node from PATH.
   - Run `install.ps1`
   - Expected: prints "Node.js not found." with a download link and exits immediately.

4. **Python version too low (< 3.11):** Install Python 3.10 and set it as the default.
   - Run `install.ps1`
   - Expected: prints "Python 3.11+ required (found Python 3.10.x)" and exits.

**Pass criteria:** Each missing prereq produces a clear, named error. No generic or cryptic messages. Script exits before attempting any install step.

---

## INST-04 — Idempotent re-run on existing installation

**Requirement:** Running the installer a second time on an existing installation completes without corrupting it.

**Steps:**
1. Complete a fresh install per INST-01.
2. Run `install.ps1` again with the same install directory.
3. Observe the re-run detection: script should print "Existing GSD Monitor installation found at: `<dir>`" and show current vs latest git hashes.
4. When prompted "Upgrade GSD Monitor? [Y/n]", enter `Y`.
5. Observe the upgrade sequence (git reset, pip install, npm rebuild).
6. After completion, launch GSD Monitor from the desktop shortcut.

**Pass criteria:** App launches correctly after re-run. No files are corrupted, no duplicate shortcuts created, and the `.venv` is intact.

*(Entering `N` at the prompt: script prints "No changes made." and exits 0 — also a pass.)*

---

## INST-05 — `.bat` launcher created in install directory

**Requirement:** Installer creates a `.bat` launcher in the install directory so the user can launch without a shortcut.

**Steps:**
1. Complete a fresh install per INST-01.
2. Navigate to the install directory (default: `%USERPROFILE%\GSDMonitor`).
3. Verify `start.bat` exists.
4. Double-click `start.bat` (or run it from a terminal).

**Pass criteria:** `start.bat` is present in the install directory. Running it launches GSD Monitor without errors.

---

## UPG-01 — Upgrade sequence: git pull + pip + npm

**Requirement:** User can run a standalone upgrade script from the install directory that performs `git pull`, `pip install -e .`, `npm ci && npm run build` in `frontend/`.

**Steps:**
1. From the install directory, run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File upgrade.ps1
   ```
   *(or double-click `upgrade.bat`)*
2. Observe output — should show steps for: pulling latest changes, installing Python dependencies, rebuilding frontend, and a final success message.

**Pass criteria:** All three operations (git pull, pip install, npm build) complete without errors. Output is clean and ends with a green success confirmation.

---

## UPG-02 — Guard: error if run outside valid install directory

**Requirement:** Upgrade script exits with a human-readable error if run from outside a valid GSD Monitor installation.

**Steps:**
1. Copy `upgrade.ps1` to a non-GSD directory (e.g., `C:\Temp\`).
2. Run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File C:\Temp\upgrade.ps1
   ```
3. Observe output.

**Pass criteria:** Script prints a message containing "must be run from a valid GSD Monitor installation directory" (or equivalent) and exits with a non-zero code. No upgrade steps execute.

---

## UPG-03 — Already up to date: clean exit

**Requirement:** Upgrade script completes cleanly when already on the latest version (no error, clear confirmation message).

**Steps:**
1. Ensure the install directory is on the latest `origin/master` commit (just upgraded or freshly installed).
2. Run `upgrade.ps1` from the install directory.
3. Observe output at the "checking for updates" step.

**Pass criteria:** Script prints "Already up to date. Nothing to do." (or equivalent) and exits with code 0. No git pull or build steps execute.

---

## VER-01 — Version badge in sidebar footer

**Requirement:** The ShellLayout sidebar footer displays GSD Monitor's version number, read from `gsd_monitor/__init__.py` via the API.

**Steps:**
1. Launch GSD Monitor.
2. Look at the bottom of the left sidebar (below the navigation links).
3. Verify the version string is visible (e.g., `v1.0.0`).
4. Navigate to different pages (Dashboard, Docs, Insights, Artifacts, etc.) and verify the version remains visible on each page.
5. **(Optional — dynamic update check):** Change `__version__` in `gsd_monitor/__init__.py` to `"2.0.0-test"`, restart the app, and verify the sidebar footer now shows `v2.0.0-test`.

**Pass criteria:** Version string appears in the sidebar footer on every page. The displayed value matches `gsd_monitor/__init__.py:__version__`. Changing `__version__` and restarting the app updates the displayed version without any other code changes.

---

## Implementation References

| Requirement | File(s) | Key Lines |
|-------------|---------|-----------|
| INST-01 | `install.ps1` | Sections 1–6 (prereqs → clone → venv → deps → build → bat → shortcut) |
| INST-02 | `install.ps1` | Lines 102–119 (WebView2 registry check) |
| INST-03 | `install.ps1` | Lines 70–100 (Git, Python, Node Fail calls) |
| INST-04 | `install.ps1` | Lines 153–185 (`.git` detection → upgrade branch) |
| INST-05 | `install.ps1` | Lines 223–295 (start.bat template + write) |
| UPG-01 | `upgrade.ps1`, `upgrade.bat` | Lines 88–120 (git pull + pip + npm ci + npm build) |
| UPG-02 | `upgrade.ps1` | Lines 53–59 (valid-install guard) |
| UPG-03 | `upgrade.ps1` | Lines ~70–80 (hash comparison, early exit) |
| VER-01 | `gsd_monitor/api/app.py`, `frontend/src/ShellLayout.tsx` | app.py:380–383, ShellLayout.tsx:37–39, 264–269 |
