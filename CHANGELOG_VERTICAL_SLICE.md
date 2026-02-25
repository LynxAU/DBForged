# Changelog: DB Vertical Slice

## 2026-02-21

### Added
- Server-authoritative DB-inspired combat loop in `world/combat.py` using a persistent 1s global script.
- Data-driven technique catalog in `world/techniques.py` with six starter techniques:
  - Ki Blast
  - Kame Wave
  - Solar Flare
  - Guard
  - Afterimage Dash
  - Vanish Strike
- Data-driven transformation catalog in `world/forms.py` including playable Saiyan Super Saiyan and race-safe stubs.
- Dynamic power-level formulas in `world/power.py` with nonlinear gap behavior for large PL mismatches.
- JSON event pipeline in `world/events.py` emitting stable packets:
  - `entity_delta`
  - `combat_event`
  - `vfx_trigger`
- World bootstrap in `world/db_init.py`:
  - Four connected Earth rooms
  - One trainer NPC (`Master Rokan`)
  - One hostile NPC (`Bandit Raider`)
- NPC typeclasses in `typeclasses/npcs.py` for trainer/hostile roles.
- DB gameplay command set in `commands/db_commands.py` + `commands/commandset.py`:
  - `+stats`
  - `attack`
  - `flee`
  - `charge`
  - `transform` / `revert`
  - `tech`
  - `equiptech`
  - `listtech`
  - `scan`
  - `sense`
  - `suppress`
  - `train`
  - `helpdb`
- Vertical-slice operational documentation in `README_VERTICAL_SLICE.md`.

### Changed
- `typeclasses/characters.py` now includes:
  - Core stat initialization (health, ki, base_power, strength/speed/balance/mastery, ki_control)
  - Dynamic PL accessors and status helpers
  - Combat state support and resource management helpers
  - Light death penalty with safe-room respawn and temporary `Bruised` debuff
  - Event delta emission hooks on movement and puppet
- `typeclasses/rooms.py` now initializes a `safe_room` flag.
- `commands/default_cmdsets.py` now mounts `DBSystemCmdSet` on characters.
- `server/conf/settings.py` now registers a persistent `db_combat` global script.
- `server/conf/at_initial_setup.py` now bootstraps the world and ensures combat script presence.

### Gameplay Notes
- Ki economy is intentionally tight early; training raises `ki_control` as a progression hook.
- Suppression lowers displayed PL and detectability while applying a slight combat readiness penalty.
- Beam struggle scaffold resolves opposite beam casts in a short collision window using PL, mastery, balance, ki, and charge.
- Combat output is deliberately nonlinear under large PL gaps to capture DB-style power dominance.

### Verification
- Python syntax/import checks passed for all added/updated game-template gameplay modules via `py_compile`.
