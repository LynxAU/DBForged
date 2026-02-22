# Dragonball Forged

A Dragon Ball-themed MUD built on Evennia.

DBForged is a text-first (and increasingly graphical) multiplayer RPG where players create fighters, train, transform, and throw absurd amounts of ki at each other until somebody drops.

## What It Is

DBForged aims to capture the Dragon Ball feel:
- explosive power growth
- iconic races and transformations
- beam clashes and high-impact techniques
- training, mastery, and progression
- dramatic combat swings instead of flat RPG attrition

This project is built on the Evennia MUD framework and customized into a Dragon Ball Super-inspired game experience.

## Current Highlights

- Custom character creation (race + visual customization)
- Multiple playable races (expanding roster)
- Power level and combat stat system
- Technique framework (ki, beam, control, utility)
- Transformation hooks and combat integration scaffolding
- Evennia web client + telnet play

## Play Locally

From the game directory (`live/`):

```bash
evennia start
```

Connect:
- Telnet client: `localhost:5153`
- Web client: `http://localhost:5154`

Stop / restart:

```bash
evennia stop
evennia start
```

## Quick Start (Player)

1. Create an account: `create <username> <password>`
2. Log in
3. Use the character creation flow/menu
4. Enter the game and start training
5. Learn techniques, build your loadout, and fight

## Project Layout (Important)

- `live/`
  Your game code (commands, typeclasses, world data, server config, web customizations)
- `evennia/`
  Vendored/framework source (if you are modifying/keeping Evennia in-repo)
- `docs/`
  Stable project documentation (design docs may be kept local until finalized)

## Developer Notes

DBForged is actively evolving. Some systems are fully playable, while others are intentionally scaffolded for content-first iteration (techniques, transformations, racials, quests, UI improvements).

Current development priorities generally revolve around:
- combat feel
- technique identity
- transformation balance
- race fantasy without hard power creep
- better UI/UX for technique selection and combat readability

## Why It’s Fun

Because “attack goblin for 6 damage” is not the goal.

The goal is:
- charging ki while your aura flares
- landing a clutch beam at low health
- transforming at the exact right moment
- whiffing a giant move and getting punished for it
- feeling like a Dragon Ball character, not a generic RPG class

## Contributing / Collaboration

If you are working on the project:
- keep gameplay content data-driven where possible
- separate content definitions from engine hooks
- prefer small, testable changes
- preserve Dragon Ball identity over generic MMO patterns

## Version Notes

Recent work has included improvements to:
- character creation flow and color presentation
- connection screen branding
- color utility handling (`live/world/color_utils.py`)
- general character creation reliability/debugging

## License

See `LICENSE.txt`.

