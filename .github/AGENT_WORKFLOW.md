# DBForged Agent Workflow Policy

Follow this development workflow exactly for DBForged.

## Core Git Policy

- Only commit/push approved root paths:
  - `.github/`
  - `docs/` (design docs, references, changelogs only)
  - `evennia/`
  - `live/`
  - `.gitignore`
  - `LICENSE.txt`
  - `README.md`
  - `pyproject.toml`
- Do not push any other root-level files/folders unless explicitly approved.
- Never push local/editor/temp files (`*.code-workspace`, scratch scripts, logs, personal notes, temp test files).

## Development Workflow (Required)

- Work in small functional slices.
- Test as you build (unit/integration/live where applicable).
- Restart the server before live validation when testing runtime changes (stop/start cycle) to avoid stale sessions.
- Push progress to your branch frequently once a slice is functional and validated.
- Open a pull request when a feature/fix is stable, reviewable, and functionally complete for that slice.
- Do not wait for a huge batch before pushing/PRing.

## Testing and Validation

- Rigorous in-game testing is required for gameplay/menu/system changes.
- Validate save/persistence behavior when relevant (logout/re-enter/restart if needed).
- Record exact test commands run and exact outcomes.
- If something is not tested, say so explicitly.
- If blocked, document the blocker, impact, and current state.

## Commit Message Standard

- Every commit message must be specific and meaningful.
- State what changed and why.
- No vague messages like `fix`, `updates`, `stuff`, `wip`.
- Prefer messages like:
  - `Add parchment codex menus for techniques and forms`
  - `Fix OOC menu routing so IC codex selections handle numeric input`

## Release Notes / Changelog (in `docs/`)

- For meaningful functional progress, create or update notes in `docs/`.
- Include:
  - summary of changes
  - files touched
  - behavior changes
  - setup/migration impact (if any)
  - tests added/updated
  - manual/live validation performed
  - known issues
  - follow-up work

## Pull Request Standard

Every PR must include detailed notes:
- what was built/fixed
- why
- scope included / not included
- exact files/areas touched
- testing performed (commands + live steps + results)
- risks/regressions to watch
- known issues / follow-up items

Update PR notes if scope changes before merge.

## Operational Expectations

- "Ship code + ship notes."
- "Push often after validated progress."
- "Open PRs for stable, feature-complete slices."
- "If it changed, document what, why, how tested, and what's next."

## Short Enforcement Version

- If it's not in the approved root list, don't commit it.
- If it isn't tested, say `Not Tested`.
- If it's functional and validated, push it.
- If it's a stable slice, open a PR with full notes.

---

**Workspace File Protection**: Never delete, never upload, never modify your workspace file (`MiniMax.code-workspace`). This file is local to each agent and must not be committed to the repository.
