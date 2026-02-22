# DBForged Content Systems (Techniques / Racials / Transformations / LSSJ)

This branch adds a data-driven, integration-ready content layer for Dragon Ball gameplay systems.

## What Was Added

- `50` techniques (ability registry, unified schema, combat-ready stubs)
- `31` transformations (first-class transformation framework)
- `Legendary Super Saiyan (LSSJ)` distinct progression/state system
- `33` racial traits (`11` playable races x `3`)
- Technique UI page (web, searchable/filterable, loadout panel)
- Iconic NPC trainer + quest scaffolding with unlock/reward mappings

## Where Content Is Defined

- Techniques: `live/world/techniques.py`
- Transformations: `live/world/forms.py`
- LSSJ system: `live/world/lssj.py`
- Racials: `live/world/racials.py`
- NPC definitions: `live/world/npc_content.py`
- Quest scaffolding: `live/world/quests.py`
- Unlock/trainer/quest mapping coverage: `live/world/content_unlocks.py`
- Validation/counts: `live/world/content_validation.py`

## Engine / Integration Hooks

- Command integration: `live/commands/db_commands.py`
- Command registration: `live/commands/commandset.py`
- Character defaults (racial traits, form storage, LSSJ state): `live/typeclasses/characters.py`
- Trainer NPC hooks: `live/typeclasses/npcs.py`
- Dynamic PL form hook integration: `live/world/power.py`

## Technique UI (Web)

- Route: `/db/techniques/`
- URL config: `live/web/website/urls.py`
- View: `live/web/website/views/technique_ui.py`
- Template: `live/web/templates/website/db_techniques.html`

In-game helper command:

- `techui` (prints the web route and current 4-tech loadout)

## How To Add A New Technique

1. Add a `_tech(...)` entry in `live/world/techniques.py`
2. Include:
   - key/id
   - description
   - tags
   - `resource_costs` / `ki_cost`
   - cooldown
   - effect/scaling
   - target rules
   - prerequisites
   - context extras
3. Run validation:
   - `python - <<` style script importing `world.content_validation.validate_all_content()` (see `docs/verification.md`)
4. Add/adjust trainer or quest rewards in:
   - `live/world/npc_content.py`
   - `live/world/quests.py`

The unlock map is generated automatically by `live/world/content_unlocks.py` and will pick up the new entry.

## How To Open The Technique UI

- In game: use `techui`, then open the printed `/db/techniques/` route in the Evennia web client browser tab.
- Direct browser: `http://<host>:<port>/db/techniques/`

## How To Spawn/Test An NPC Trainer In-Game

Commands added:

- `spawntrainer <npc_key>`
- `talk <npc>`
- `train`
- `forms`
- `lssj [status|escalate|train]`

Example:

- `spawntrainer master_roshi`
- `talk roshi`

## Note About Prior “Exact” Lists

The user referenced previously selected exact ability/transformation lists, but those lists were not present in this branch context at task start. A complete Dragon Ball-aligned set was implemented data-first and can be tuned/swapped in the registries without changing the integration surfaces.
