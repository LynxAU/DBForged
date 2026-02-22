# DBForged Vertical Slice (Evennia)

This slice delivers a playable Earth zone with server-authoritative combat and a stable JSON event stream for a future sprite client.

## Included

- Zone: `Earth: Plains - Safe Camp`, `Earth: Plains - Rocky Pass`, `Earth: City Outskirts - Gate`, `Earth: City Outskirts - Alley`
- NPCs:
  - `Master Rokan` (trainer)
  - `Bandit Raider` (hostile AI auto-engages nearby players)
- Stats: Health, Ki, dynamic Power Level
- Combat:
  - 1s passive combat tick
  - Player techniques (equipped subset of 4)
  - Cooldowns, ki costs, interrupts, stun, defense, movement
  - Beam struggle scaffold when opposite beams collide in the same tick window
- Charging: temporary PL surge + ki restore with interrupt vulnerability
- Transformations: Saiyan `Super Saiyan` with mastery + ki drain
- Detection stack: `scan`, `sense`, `suppress`
- Death penalty: respawn at safe room with temporary `Bruised` PL debuff
- JSON events emitted with `@event {json}` packets:
  - `entity_delta`
  - `combat_event`
  - `vfx_trigger`

## Power Level Formula

`compute_current_pl(character)` in `world/power.py` computes:

- `combat_pl = base_power * stat_factor * injury_factor * ki_factor * charge_factor * form_factor * combat_readiness * control_efficiency * bruised_factor`
- `displayed_pl = combat_pl * suppression_factor` (only when suppressed)

Behavior:
- Charging raises `charge_factor` (up to +55%).
- Injury and low ki reduce effective combat output.
- Suppression lowers visible PL and applies a mild combat readiness penalty.
- Transform adds multipliers and non-raw bias (speed/mastery flavor).
- `pl_gap_effect(attacker_pl, defender_pl)` creates nonlinear outcomes:
  - Huge gaps quickly become overwhelming (`damage_mult` up to 4.2, strong hit bias)
  - Big underdog gaps sharply reduce output (`damage_mult` floor 0.18)

## Starter Techniques (data-driven)

Defined in `world/techniques.py`:

- `Ki Blast` (blast damage)
- `Kame Wave` (beam)
- `Solar Flare` (stun + interrupt)
- `Guard` (defense)
- `Afterimage Dash` (movement/evasion)
- `Vanish Strike` (damage + interrupt)

Known techniques can exceed 4, but equipped techniques are limited to 4 and can only be changed out of combat.

## Commands

- `+stats`
- `attack <target>`
- `flee`
- `charge`
- `transform <form>` or `revert`
- `tech <techname> <target?>`
- `equiptech <techname>`
- `listtech`
- `scan <target>`
- `sense <target or room>`
- `suppress on|off`
- `train`
- `helpdb`

## Run / Smoke Test

1. Start your game.
2. Connect and puppet a character.
3. Use `helpdb`.
4. Move between rooms (`east`, `west`, `north`, `south`).
5. In `Earth: City Outskirts - Alley`, test combat against `Bandit Raider`.
6. In `Earth: Plains - Safe Camp`, use `train` with `Master Rokan`.

## Manual Sanity Tests

1. PL dynamics
   - Run `+stats`, then `charge`, wait 2-3 seconds, run `+stats` again.
   - Expect increased combat PL while charging and ki recovering.

2. Charging interrupt
   - Start `charge`, then have a target use `tech vanish_strike <you>` or `tech solar_flare <you>`.
   - Expect charge to stop and interrupt feedback.

3. Technique cooldown + equip limit
   - Use `tech ki_blast <target>` twice quickly; second should fail on cooldown.
   - Use `equiptech` repeatedly; ensure max equipped remains 4.

4. Beam struggle trigger
   - Two fighters target each other and both use `tech kame_wave <other>` within about 1 second.
   - Expect beam struggle event text + `vfx_beam_struggle`.

5. Scan / sense / suppress
   - Toggle `suppress on`, run `+stats` and ask another player to `scan` you.
   - Build `ki_control` (via `train`) to 15+, use `sense room`.
   - Expect suppressed readouts and sense lock removed at threshold.

## Post-Login Menu (Account Menu / Character Flow)

- Menu flow implementation lives in `typeclasses/accounts.py` (post-login main menu, enter/create/delete/exit routing).
- Edit character creation palettes in `typeclasses/accounts.py`:
  - `DB_MENU_RACES`
  - `DB_MENU_HAIR_COLORS`
  - `DB_MENU_EYE_COLORS`
  - `DB_MENU_AURA_COLORS`
  - `DB_MENU_SKIN_PALETTES` (race-aware skin palettes)

### Run tests

From the `live` game directory:

- `python -m django test live.tests.test_account_menu --settings=server.conf.settings`

### Manual verification

1. Log in with an account and confirm you land on the Main Menu (not in-world).
2. `1` Enter Game:
   - With no characters: confirm exact `You have no characters yet!` and return to menu.
   - With characters: numeric select enters game, `B` returns to menu.
3. `2` Create Character:
   - One prompt per screen, numeric selections for palette/race screens.
   - `B` goes back, `C` opens cancel confirmation.
   - Review `2` returns to Race step, Review `1` creates and returns to character select.
4. `3` Delete Character:
   - With no characters: confirm exact `You have no characters to delete!`.
   - Mismatched confirmation name never deletes.
   - Exact name deletes and returns to menu.
5. `4` Exit disconnects immediately.
