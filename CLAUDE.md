# DBForged — Agent Workflow & Version Control Guidelines

All AI agents working on this project must follow these rules without exception.

---

## 1. Read Before Writing

**Never modify a file you haven't read in the current session.**
- Use the `Read` tool to load the file first.
- If a file was read in a previous summarized session, re-read it before editing.
- This prevents overwriting unseen changes from other agents or the user.

---

## 2. Scope Discipline

**Only change what was asked. No opportunistic refactors.**

- A bug fix does not justify cleaning up surrounding code.
- Do not add docstrings, comments, or type annotations to untouched functions.
- Do not rename variables, reformat, or restructure beyond the task scope.
- If you notice something broken *outside* your task, note it in your response but do not fix it silently.

---

## 3. Git Commit Rules

**Never commit unless explicitly asked.**

When asked to commit:
- Stage only the files directly related to the task.
- Never use `git add -A` or `git add .` — stage files individually.
- Never `git push` unless explicitly requested.
- Never `--force` push, `reset --hard`, or `checkout .` without explicit user instruction.
- Never amend a previous commit. Always create a new one.
- Never skip hooks with `--no-verify`.
- Commit message format: imperative mood, concise, explains *why* not just *what*.

---

## 4. Security Rules (This is an Online Game)

All agents must treat this as a production security context:

### Never trust player input
- All values from `caller.args`, WebSocket messages, or HTTP requests must be validated.
- Strings → sanitize length and charset.
- Numeric fields → always cast with `int()` or `float()` inside try/except.
- Enum fields (race, form, technique) → validate against an explicit allowlist.

### Never trust client-provided game values
- Damage, HP, PL, zeni — always calculate server-side. Never use a value the client sends for game math.
- If a client message contains a numeric game value, ignore it; recalculate from character state.

### XSS prevention
- `dangerouslySetInnerHTML` is only permitted on output that has been passed through `sanitizeGameHtml()` in `Chat.jsx`.
- No `innerHTML`, `eval()`, `new Function()`, or `document.write()` anywhere.
- Evennia ANSI color spans are the only HTML allowed through.

### Race conditions
- Any shared mutable state accessed from command handlers must be protected with a lock.
- Pattern: `with _state_lock:` around check + mutate blocks — never check outside and mutate inside.

### Privilege checks
- All commands that modify another character's state must verify `caller == target` or that caller has explicit admin locks.

---

## 5. Python Code Conventions

- **DB attribute reads**: Always cast numeric attrs. Use `int(character.db.hp_current or 0)`, never raw access.
- **Exception handling**: Never `except Exception: pass`. At minimum log with `logger.log_trace()`. Prefer specific exception types.
- **Validation on startup**: Any registry (techniques, forms, racials, quests) with a `validate_*()` function must be called in `at_initial_setup()`.
- **In-memory state**: Any state that must survive restarts (fusions, tournament results, etc.) must be persisted to `character.db.*` or `ScriptDB`. Pure module-level dicts are for caching only.

---

## 6. JavaScript/React Conventions

- **useEffect cleanup**: Every `addEventListener`, `requestAnimationFrame`, `setInterval`, and `URL.createObjectURL` must be cleaned up in the effect's return function.
- **Dependency arrays**: Be explicit. Don't suppress linting warnings with `// eslint-disable` unless you fully understand the staleness trade-off and document it.
- **WebSocket messages**: All inbound messages must pass through `validateServerMessage()` before touching React state.
- **Error boundaries**: All major feature sections must be wrapped in an `<ErrorBoundary>`. A crash in the chat panel must not kill the canvas.
- **Console logs**: Development-only logs must be wrapped in `if (import.meta.env.DEV)`. Zero `console.log` in production paths.

---

## 7. File Ownership

| Area | Primary Files | Don't Touch Without Reading |
|------|--------------|----------------------------|
| Combat logic | `world/combat.py` | `world/power.py`, `world/techniques.py` |
| PL calculation | `world/power.py` | `world/forms.py` |
| Character state | `typeclasses/characters.py` | `world/racials.py` |
| Commands | `commands/combat_cmds.py`, `commands/character_cmds.py` | `commands/commandset.py` |
| World building | `world/db_init.py`, `world/build_kame_island.py` | `server/conf/at_initial_setup.py` |
| Web layout | `web/client/src/App.jsx` | `web/client/src/styles/index.css` |
| Game state | `web/client/src/hooks/useGameState.js` | `web/client/src/services/evennia.js` |
| Login / chargen | `web/client/src/components/Login/` | `web/client/src/hooks/useGameState.js` |

---

## 8. What "Release Candidate" Means for This Project

Before any public-facing deployment:

- [ ] No `console.log` in production code paths
- [ ] All `dangerouslySetInnerHTML` passes through sanitizer
- [ ] All WebSocket message handlers validate inbound data
- [ ] All shared mutable state protected by locks
- [ ] Fusion state persisted across restarts
- [ ] Startup validators called for all registries
- [ ] `ALLOWED_HOSTS` explicitly set in `settings.py`
- [ ] `DEBUG = False` confirmed in production config
- [ ] All blob URLs revoked on component unmount
- [ ] React `<ErrorBoundary>` wrapping all major UI sections
- [ ] No hardcoded credentials or secrets in tracked files

---

## 9. Project Architecture Summary

```
DBForged/
├── commands/           # Evennia command classes (player-facing verbs)
│   ├── combat_cmds.py  # attack, flee, guard, charge, counter, tech
│   ├── character_cmds.py # stats, transform, scan, setrace, chargenapply
│   ├── social_cmds.py  # guild, quest, shop interactions
│   └── commandset.py   # registers all commands on the character
│
├── world/              # Game systems (no player-facing commands here)
│   ├── combat.py       # CombatHandler script, tick loop, beam clashes
│   ├── power.py        # compute_current_pl(), pl_gap_effect()
│   ├── techniques.py   # TECHNIQUES registry + execute_technique()
│   ├── forms.py        # FORMS registry + transformation logic
│   ├── fusions.py      # Fusion state management
│   ├── racials.py      # RACIAL_TRAITS registry + ensure_character_racials()
│   ├── quests.py       # Quest definitions + turn-in flow
│   ├── tournaments.py  # Tournament state machine
│   ├── npc_content.py  # NPC dialogue, trainer rewards, unique keys
│   ├── events.py       # emit_entity_delta(), emit_combat_event()
│   ├── db_init.py      # Initial world building (Earth zones)
│   └── build_kame_island.py  # Kame Island rooms/exits/NPCs
│
├── typeclasses/
│   └── characters.py   # Character typeclass: stats, chargen, at_post_puppet
│
├── server/conf/
│   ├── settings.py     # Evennia settings (never commit secret_settings.py)
│   └── at_initial_setup.py  # One-time world init on first server start
│
└── web/client/src/
    ├── App.jsx                     # Root layout: game-viewport overlay system
    ├── hooks/useGameState.js       # WebSocket state machine, login, entities
    ├── services/evennia.js         # Raw WebSocket connection management
    ├── components/
    │   ├── GameCanvas/GameCanvas.jsx   # Canvas renderer, sprite system, tiles
    │   ├── Chat/Chat.jsx               # Terminal chat with sanitized HTML
    │   ├── PlayerHud/PlayerHud.jsx     # Scouter-style stat overlay
    │   ├── Login/Login.jsx             # Three-view login: menu/login/create
    │   ├── Login/CharacterCreator.jsx  # Multi-step character wizard
    │   └── Menu/Menu.jsx               # Tabbed in-game menu panel
    └── styles/index.css            # All global styles and theme variables
```

---

## 10. Known Technical Debt (Track Until Resolved)

| Item | File | Priority |
|------|------|----------|
| Beam clash matching is O(n²) | `world/combat.py:230` | Medium |
| `_process_passive_tick()` too long (102 lines) | `world/combat.py` | Medium |
| `compute_current_pl()` calculates form_factor twice | `world/power.py` | Low |
| Sprite blob URLs not revoked on unmount | `GameCanvas.jsx` | High |
| Async render loop adds Promise overhead | `GameCanvas.jsx` | High |
| No `ErrorBoundary` in React tree | `App.jsx` | High |
| console.log throughout production code | `GameCanvas.jsx`, `useGameState.js` | Medium |
| Technique execution still stubbed | `world/techniques.py` | High |
| Kame Island not built | `world/build_kame_island.py` | High |
| Quest flow has no engine (50 defs, 0 completion) | `world/quests.py` | High |
