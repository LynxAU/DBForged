# DBForged Expanded Race Combat Draft (50 Abilities + Racials + Transformations)

## Scope

Updated for expanded playable races found in `live/typeclasses/characters.py`:

- `saiyan`
- `human`
- `namekian`
- `frost_demon`
- `android`
- `majin`
- `half_breed`
- `truffle`
- `grey`
- `bio_android`

This draft is intentionally **design + balance template** focused:
- `50` shared abilities total (attacks/support/control; transformations excluded)
- `3` racials per race (`30` total)
- updated transformations by race/family
- basic damage/effect templates aligned to your current combat system style (`base + STR + MAS + PL` scaling)

## Current Charging Reality (important)

You currently **do not** have a hold-key charge input (like holding Shift) wired into combat.

What exists:
- `charge` command (`CmdCharge`)
- `charge_stacks`
- per-technique `cast_time`

So all charge gameplay in this draft assumes:
- command-based charge (`charge`)
- cast-time / channel windows
- not client-side hold-key inputs

---

## 1) Damage Template Model (matches current style)

Your live techniques use a pattern like:

```python
damage_base = (
    scaling["base"]
    + int(STR * scaling["strength"])
    + int(MAS * scaling["mastery"])
    + int(PL * scaling["pl"])
    + tech_mastery_bonus
)
final = int(damage_base * pl_gap_effect(attacker_pl, defender_pl)["damage_mult"])
```

This draft uses the same style for new ability templates.

### Suggested tags / categories

- `blast` = fast ranged projectile damage
- `beam` = beam cast / beam struggle-compatible
- `interrupt` = melee/rush damage with interrupt utility
- `control` = stuns/roots/blinds/seals
- `defense` = guard/barrier/mitigation
- `support` = buff, ki transfer, cleanse, regen
- `summon` = adds/ghosts/clones

---

## 2) Shared Ability Roster (50 total, with basic values + effects)

Format:
- `Scaling`: `{base, strength, mastery, pl}`
- `Cost/CD/Cast`: `ki_cost / cooldown / cast_time`
- `Effect`: special behavior notes

## A) Core Blasts / Beams (1-20)

1. **Ki Blast**
- `category`: `blast`
- `Scaling`: `{base: 14, strength: 0.45, mastery: 0.25, pl: 0.0017}`
- `Cost/CD/Cast`: `10 / 2.5 / 0.0`
- `Effect`: baseline ranged poke, no extra effect

2. **Rapid Ki Volley**
- `category`: `blast`
- `Scaling`: `{base: 10, strength: 0.28, mastery: 0.20, pl: 0.0011}`
- `Cost/CD/Cast`: `14 / 4.0 / 0.0`
- `Effect`: 3 hits, each rolls hit separately at reduced damage

3. **Charged Ki Shot**
- `category`: `blast`
- `Scaling`: `{base: 20, strength: 0.48, mastery: 0.28, pl: 0.0019}`
- `Cost/CD/Cast`: `16 / 4.5 / 0.4`
- `Effect`: gains +8% damage per `charge_stack` (cap +48%)

4. **Kame Wave** (existing)
- `category`: `beam`
- `Scaling`: `{base: 24, strength: 0.55, mastery: 0.35, pl: 0.0024}`
- `Cost/CD/Cast`: `24 / 6.0 / 0.5`
- `Effect`: beam struggle-compatible

5. **Galick Burst**
- `category`: `beam`
- `Scaling`: `{base: 22, strength: 0.52, mastery: 0.34, pl: 0.0022}`
- `Cost/CD/Cast`: `22 / 5.5 / 0.35`
- `Effect`: faster beam, slightly lower clash strength than heavy beams

6. **Masenko**
- `category`: `beam`
- `Scaling`: `{base: 23, strength: 0.50, mastery: 0.38, pl: 0.0022}`
- `Cost/CD/Cast`: `20 / 5.5 / 0.3`
- `Effect`: +10% hit bias if target is airborne/stunned

7. **Dodon Ray**
- `category`: `beam`
- `Scaling`: `{base: 16, strength: 0.42, mastery: 0.34, pl: 0.0018}`
- `Cost/CD/Cast`: `12 / 3.5 / 0.1`
- `Effect`: precision beam, low cast commitment

8. **Death Beam**
- `category`: `beam`
- `Scaling`: `{base: 18, strength: 0.44, mastery: 0.40, pl: 0.0020}`
- `Cost/CD/Cast`: `14 / 4.0 / 0.05`
- `Effect`: high crit/weak-point synergy; low AoE

9. **Special Beam Cannon**
- `category`: `beam`
- `Scaling`: `{base: 36, strength: 0.62, mastery: 0.48, pl: 0.0032}`
- `Cost/CD/Cast`: `34 / 11.0 / 1.2`
- `Effect`: armor pierce, beam; narrow line, high payoff

10. **Final Flash**
- `category`: `beam`
- `Scaling`: `{base: 42, strength: 0.68, mastery: 0.46, pl: 0.0035}`
- `Cost/CD/Cast`: `40 / 14.0 / 1.6`
- `Effect`: heavy beam, strong clash score, long telegraph

11. **Gamma Burst Flash**
- `category`: `beam`
- `Scaling`: `{base: 48, strength: 0.72, mastery: 0.50, pl: 0.0039}`
- `Cost/CD/Cast`: `46 / 16.0 / 1.8`
- `Effect`: endgame beam, long cooldown

12. **Light Grenade**
- `category`: `blast`
- `Scaling`: `{base: 28, strength: 0.56, mastery: 0.36, pl: 0.0025}`
- `Cost/CD/Cast`: `24 / 8.0 / 0.7`
- `Effect`: splash damage in small radius

13. **Big Bang Attack**
- `category`: `blast`
- `Scaling`: `{base: 32, strength: 0.58, mastery: 0.38, pl: 0.0028}`
- `Cost/CD/Cast`: `28 / 9.0 / 0.8`
- `Effect`: medium AoE, stronger knockback

14. **Death Ball**
- `category`: `blast`
- `Scaling`: `{base: 38, strength: 0.60, mastery: 0.42, pl: 0.0030}`
- `Cost/CD/Cast`: `34 / 12.0 / 1.0`
- `Effect`: slow orb, large AoE, zone denial

15. **Vanishing Ball**
- `category`: `blast`
- `Scaling`: `{base: 26, strength: 0.54, mastery: 0.34, pl: 0.0024}`
- `Cost/CD/Cast`: `22 / 6.5 / 0.25`
- `Effect`: fast compact projectile; good chase finisher

16. **Burning Attack**
- `category`: `blast`
- `Scaling`: `{base: 24, strength: 0.52, mastery: 0.37, pl: 0.0023}`
- `Cost/CD/Cast`: `20 / 6.0 / 0.35`
- `Effect`: +stagger chance on direct hit

17. **Finish Buster**
- `category`: `blast`
- `Scaling`: `{base: 30, strength: 0.57, mastery: 0.39, pl: 0.0027}`
- `Cost/CD/Cast`: `26 / 8.5 / 0.55`
- `Effect`: heavy knockback

18. **Supernova**
- `category`: `beam` (or siege projectile mode)
- `Scaling`: `{base: 58, strength: 0.78, mastery: 0.52, pl: 0.0046}`
- `Cost/CD/Cast`: `55 / 22.0 / 2.4`
- `Effect`: raid-tier nuke, long telegraph, AoE impact

19. **Spirit Cannon**
- `category`: `beam`
- `Scaling`: `{base: 26, strength: 0.48, mastery: 0.42, pl: 0.0024}`
- `Cost/CD/Cast`: `24 / 7.0 / 0.6`
- `Effect`: +15% damage vs guarded targets (piercing pressure)

20. **Scatter Beam**
- `category`: `beam`
- `Scaling`: `{base: 12, strength: 0.25, mastery: 0.22, pl: 0.0010}`
- `Cost/CD/Cast`: `18 / 7.0 / 0.5`
- `Effect`: 4 split beams in cone, anti-group utility

## B) Melee / Rush / Interrupts (21-32)

21. **Vanish Strike** (existing)
- `category`: `interrupt`
- `Scaling`: `{base: 18, strength: 0.60, mastery: 0.30, pl: 0.0018}`
- `Cost/CD/Cast`: `18 / 8.5 / 0.0`
- `Effect`: interrupts charging/cast if hit

22. **Wolf Fang Fist**
- `category`: `interrupt`
- `Scaling`: `{base: 16, strength: 0.62, mastery: 0.26, pl: 0.0017}`
- `Cost/CD/Cast`: `14 / 4.5 / 0.0`
- `Effect`: 2-hit rush, second hit gains +hit bias

23. **Soaring Dragon Strike**
- `category`: `interrupt`
- `Scaling`: `{base: 20, strength: 0.66, mastery: 0.30, pl: 0.0019}`
- `Cost/CD/Cast`: `18 / 6.0 / 0.1`
- `Effect`: launch/anti-air; bonus stagger

24. **Nova Strike**
- `category`: `interrupt`
- `Scaling`: `{base: 24, strength: 0.64, mastery: 0.34, pl: 0.0021}`
- `Cost/CD/Cast`: `20 / 7.0 / 0.15`
- `Effect`: rush gap-closer, brief projectile resistance on dash

25. **Dragon Fist**
- `category`: `interrupt`
- `Scaling`: `{base: 34, strength: 0.82, mastery: 0.36, pl: 0.0028}`
- `Cost/CD/Cast`: `30 / 14.0 / 0.8`
- `Effect`: super armor during startup, high single-target burst

26. **Burst Rush**
- `category`: `interrupt`
- `Scaling`: `{base: 22, strength: 0.58, mastery: 0.36, pl: 0.0020}`
- `Cost/CD/Cast`: `20 / 6.5 / 0.15`
- `Effect`: multi-hit combo; +10% damage if target stunned/rooted

27. **Shining Sword Attack**
- `category`: `interrupt`
- `Scaling`: `{base: 28, strength: 0.62, mastery: 0.40, pl: 0.0024}`
- `Cost/CD/Cast`: `24 / 9.0 / 0.4`
- `Effect`: melee finisher, bonus vs barriers

28. **Heat Dome Attack**
- `category`: `interrupt`
- `Scaling`: `{base: 36, strength: 0.70, mastery: 0.38, pl: 0.0029}`
- `Cost/CD/Cast`: `34 / 13.0 / 1.0`
- `Effect`: strong anti-air finisher, high knockback

29. **Spirit Sword Slash**
- `category`: `interrupt`
- `Scaling`: `{base: 24, strength: 0.56, mastery: 0.44, pl: 0.0023}`
- `Cost/CD/Cast`: `22 / 7.5 / 0.2`
- `Effect`: pierce 20% guard reduction

30. **Vital Point Strikes**
- `category`: `interrupt`
- `Scaling`: `{base: 20, strength: 0.50, mastery: 0.50, pl: 0.0020}`
- `Cost/CD/Cast`: `18 / 7.0 / 0.1`
- `Effect`: +25% damage vs debuffed targets; assassin-style

31. **Assault Barrier**
- `category`: `interrupt`
- `Scaling`: `{base: 18, strength: 0.52, mastery: 0.28, pl: 0.0018}`
- `Cost/CD/Cast`: `18 / 7.5 / 0.0`
- `Effect`: dash grants brief barrier while traveling

32. **Body Blow Combo**
- `category`: `interrupt`
- `Scaling`: `{base: 14, strength: 0.68, mastery: 0.22, pl: 0.0015}`
- `Cost/CD/Cast`: `12 / 4.0 / 0.0`
- `Effect`: applies `bruised` (small PL penalty) on proc

## C) Control / Utility / Defense (33-44)

33. **Solar Flare** (existing)
- `category`: `control`
- `Cost/CD/Cast`: `16 / 9.0 / 0.0`
- `Effect`: `stun 2.0s` + interrupt

34. **Energy Rings**
- `category`: `control`
- `Cost/CD/Cast`: `18 / 8.5 / 0.2`
- `Effect`: root `1.8s`; target can still use some instant skills

35. **Hellzone Grenade**
- `category`: `control`
- `Scaling`: `{base: 30, strength: 0.54, mastery: 0.42, pl: 0.0026}`
- `Cost/CD/Cast`: `28 / 11.0 / 0.9`
- `Effect`: delayed detonation trap; +20% if target remains in zone

36. **Scattering Bullet**
- `category`: `control`
- `Scaling`: `{base: 12, strength: 0.20, mastery: 0.24, pl: 0.0011}`
- `Cost/CD/Cast`: `16 / 7.5 / 0.25`
- `Effect`: split-projectile zone denial; 4 shards

37. **Telekinesis**
- `category`: `control`
- `Cost/CD/Cast`: `20 / 10.0 / 0.2`
- `Effect`: lift/hold `1.2s` (bosses reduced), interrupts charge/cast

38. **Barrier Prison**
- `category`: `control`
- `Cost/CD/Cast`: `24 / 12.0 / 0.4`
- `Effect`: imprison target `1.5s`; high boss resistance

39. **Galactic Donuts**
- `category`: `control`
- `Cost/CD/Cast`: `20 / 10.0 / 0.35`
- `Effect`: bind `1.7s`; prevents movement and charge

40. **Mafuba (Seal)**
- `category`: `control`
- `Cost/CD/Cast`: `40 / 25.0 / 2.0`
- `Effect`: PvE seal attempt / elite suppression; very high failure risk if PL gap bad

41. **Guard** (existing)
- `category`: `defense`
- `Cost/CD/Cast`: `8 / 5.0 / 0.0`
- `Effect`: `3.0s` guard with `45%` damage reduction

42. **Android Barrier**
- `category`: `defense`
- `Cost/CD/Cast`: `16 / 8.0 / 0.0`
- `Effect`: `2.0s` barrier; blocks projectiles and reduces beam damage

43. **Afterimage Dash** (existing)
- `category`: `movement`
- `Cost/CD/Cast`: `14 / 7.5 / 0.0`
- `Effect`: `afterimage 2.0s`; lowers enemy hit chance

44. **Perfect Barrier**
- `category`: `defense`
- `Cost/CD/Cast`: `24 / 14.0 / 0.2`
- `Effect`: advanced barrier, stronger than Android Barrier, longer CD

## D) Support / Sustain / Raid / Spectacle (45-50)

45. **Ki Transfer**
- `category`: `support`
- `Cost/CD/Cast`: `16 / 6.0 / 0.5`
- `Effect`: restore ally Ki (`flat + %`), minor self Ki drain beyond cost

46. **Namekian Regeneration**
- `category`: `support`
- `Cost/CD/Cast`: `18 / 10.0 / 1.0`
- `Effect`: heal over time; interrupted by stun/knockdown

47. **Majin Body Reform**
- `category`: `support`
- `Cost/CD/Cast`: `20 / 11.0 / 0.8`
- `Effect`: stronger HoT than Namekian Regen, vulnerable to anti-regen tags

48. **Forced Spirit Fission**
- `category`: `support`
- `Cost/CD/Cast`: `22 / 14.0 / 0.3`
- `Effect`: strips 1-2 buffs / suppresses absorbed-power stacks / reduces summon duration

49. **Final Explosion**
- `category`: `blast`
- `Scaling`: `{base: 56, strength: 0.75, mastery: 0.42, pl: 0.0042}`
- `Cost/CD/Cast`: `48 / 24.0 / 1.4`
- `Effect`: self-centered AoE; self HP cost (10-25% current HP)

50. **Super Ghost Kamikaze Attack**
- `category`: `summon`
- `Scaling`: `{base: 14, strength: 0.20, mastery: 0.40, pl: 0.0014}`
- `Cost/CD/Cast`: `30 / 18.0 / 1.0`
- `Effect`: summon 2 ghosts; each explodes for scaling damage, can zone/chase

---

## 3) Racial Baselines (3 each, 10 races = 30 total)

## Saiyan

1. **Battle Adaptation** (passive)
- After taking a heavy hit, gain `+1 Adaptation` (cap 4).
- Each stack: `+3% damage`, `+2% ki efficiency`.
- Falls off slowly out of combat.

2. **Saiyan Surge** (active, 12s CD)
- `6s`: `+12% speed`, `+10% melee damage`, `+8% cast speed`.
- After effect: `-15% guard regen` for `4s`.

3. **Pride Trigger** (clutch passive)
- Once per fight at `<35% HP`: gain `flinch resist 2s` and `+12 Ki`.

## Human

1. **Martial Adaptability** (passive)
- Perfect guard/dodge reduces non-ultimate cooldowns by `0.5s`.

2. **Combat Discipline** (active stance, 10s CD)
- `4s`: `-20% knockback`, `-12% incoming damage`, `+guard efficiency`.

3. **Ally Uplift** (support pulse, 14s CD)
- Nearby allies gain small `Ki + stamina/guard` burst.

## Namekian

1. **Regenerative Tissue** (passive)
- Small out-of-combat HP regen.
- In combat: `+10%` value on regen/heal skills.

2. **Elastic Reach** (active, 9s CD)
- `5s`: melee/grab range increased; improves control routing.

3. **Namekian Fortitude** (passive)
- `+guard durability`, `+debuff resist`, slightly lower crit scaling.

## Frost Demon

1. **Suppression State** (toggle)
- Suppressed: lower output, lower Ki drain, lower threat.
- Released: higher damage/speed, higher drain and incoming damage.

2. **Execution Precision** (passive)
- Charged beams gain bonus crit/armor pierce vs marked targets.

3. **Tyrant Tempo** (active, 14s CD)
- `5s`: `+ranged cadence`, `+movement speed`, `+incoming damage`.

## Android

1. **Infinite Reactor** (passive)
- Steady in-combat Ki regeneration.
- Lower burst scaling cap on ultimates for balance.

2. **Barrier Matrix** (active, 8s CD)
- Mini barrier (`1.5s`) weaker than `Android Barrier`.

3. **Targeting Suite** (passive)
- Improved projectile tracking / lock retention / reduced range falloff.

## Majin

1. **Elastic Body** (passive)
- Reduced blunt stagger and partial grab resistance.
- Increased vulnerability to slicing/piercing.

2. **Body Reform** (active, 12s CD)
- HoT + cleanse one light debuff.

3. **Absorb Momentum** (passive)
- Heavy hits grant brief damage reduction and small Ki refund.

## Half Breed (Human/Saiyan hybrid)

1. **Potential Spike** (passive)
- Gains bonus damage scaling when HP falls below thresholds (`70/45/25%`).
- Stronger than Human clutch scaling, weaker than Saiyan adaptation over time.

2. **Hybrid Discipline** (passive)
- Small cooldown reduction on beams and rushes.
- Minor bonus to tech mastery gain in combat (future-proofing).

3. **Awakened Burst** (active, 16s CD)
- `5s`: `+10% damage`, `+10% crit`, `+10% cast speed`.
- Higher Ki cost on abilities while active.

## Truffle

1. **Tech Assimilation** (passive)
- Bonus effect chance/duration on debuffs, traps, and tech disruption.

2. **Parasite Protocol** (active, 15s CD)
- Mark target for `6s`: damage dealt restores a small amount of Ki.
- Reduced effect on bosses.

3. **Tactical Drone Weave** (active, 12s CD)
- Short defensive utility: `+evasion` and `+projectile tracking`.
- Flavor for machine-assisted combat style.

## Grey (Jiren-like race)

1. **Pressure Aura** (passive)
- Nearby enemies suffer slight hit-bias penalty when in melee range.

2. **Meditative Focus** (active, 14s CD)
- `4s`: reduced stagger, increased guard, reduced movement.

3. **Absolute Counterforce** (passive)
- Bonus damage vs targets currently charging / casting long abilities.

## Bio Android

1. **Adaptive Genome** (passive)
- On taking beam/melee damage, gain a brief resistance stack to that damage type (small, capped).

2. **Cellular Regrowth** (active, 16s CD)
- Moderate self-heal over time; interrupted by stun/seal.

3. **Predator Analysis** (passive)
- Repeated hits on same target increase hit bias slightly (cap).
- Encourages pressure and target focus.

---

## 4) Updated Transformations / Forms by Race

Only listing forms with strong DB flavor and plausible game conversion.

## Saiyan
- **Super Saiyan**
- **Super Saiyan 2**
- **Super Saiyan 3**
- **Super Saiyan God**
- **Super Saiyan Blue**
- **Ultra Instinct Sign / MUI** (advanced path)

Game notes:
- Saiyan forms should lean on burst + aura drain + escalation.
- Keep long-cast ultimates scary by preserving cast commitment even in forms.

## Human
- **Max Power (Roshi-style)**
- **Potential Unleashed** (rare progression path)

Game notes:
- Humans should get fewer forms, but better efficiency and cooldown/utility identity.

## Namekian
- **Great Namekian**
- **Power Awakening**
- **Orange Form** (Piccolo-inspired apex)

Game notes:
- Tank/control forms; less raw burst than Saiyans/Frost Demons.

## Frost Demon
- **Released State** (suppression lifted; can be modeled as form/stance)
- **Final Form** (playable fantasy baseline high output)
- **100% Full Power**
- **Golden Form** (late-game)

Game notes:
- Strong ranged burst, execution precision, but drain/overcommit vulnerability.

## Android
- **Overclock** (DBForged race form)

Game notes:
- Since canon androids don’t all “transform” traditionally, use reactor/overclock states.
- Strong sustained DPS + barriers, limited burst extremes.

## Majin
- **Battle Expansion / Super Majin State** (DBForged adaptation)
- **Pure Chaos State** (Kid Buu-inspired high speed path)

Game notes:
- Regeneration pressure, erratic offense, form-specific sustain tuning.

## Half Breed
- **Potential Unleashed**
- **Hybrid Rage Burst** (DBForged branch, inspired by Gohan/Trunks spikes)
- **Beast** (very late path, if desired)

Game notes:
- Hybrid race should be “spike windows + flexible kit,” not just Saiyan-lite.

## Truffle
- **Machine Union / Battle Armor Sync**
- **Parasite Ascension** (Baby-inspired theme, if you want villainous branch)

Game notes:
- Tech control, possession/marking mechanics, resource disruption.

## Grey
- **Limit Release**
- **Meditative Power State**

Game notes:
- Jiren-style identity: immense pressure, anti-cast punishment, fewer flashy gimmicks.

## Bio Android
- **Imperfect**
- **Semi-Perfect**
- **Perfect**
- **Super Perfect**

Game notes:
- Strongest transformation fantasy among new races.
- Should likely include boss-only absorption escalation variants for PvE.

---

## 5) Transformation Stat Slice (quick balance targets)

These are design targets, not lore multipliers.

- **Light Form** (Human Max Power / Android Overclock lite): `Damage +20-35%`, `Guard +10-20%`, `Drain low`
- **Standard Power Form** (SSJ / Power Awakening / Final Form release): `Damage +30-55%`, `Speed +8-20%`, `Drain medium`
- **Heavy Burst Form** (SSJ3 / 100% Full Power / Orange / Perfect+): `Damage +55-85%`, `Guard +/-`, `Drain high`
- **Apex Form** (Blue Evolved / Beast / Golden / Super Perfect / MUI): `Damage +80-110%`, major secondary bonuses, `Drain high`, `CD/lockout long`

---

## 6) Suggested Next Implementation Step (minimal disruption)

Keep this separate from the files you are actively changing and stage it in data first:

1. Expand data catalogs only:
- `live/world/techniques.py` (new technique entries)
- `live/world/forms.py` (form entries)
- new `live/world/racials.py` (racial definitions)

2. Hook racials into combat math in one place later:
- `live/world/power.py` and/or `live/world/combat.py`

3. Leave menu/chargen files alone until race UI text is stable:
- `accounts.py`, `ooc_menu.py`, `evmenu_create.py`

---

## 7) Follow-up I can do next

If you want, I can turn this draft into:

- a **machine-readable JSON/py data pack** (`abilities`, `racials`, `forms`)
- values tuned for your simulator (`live/tools/combat_simulator.py`)
- an updated **webapp tab** that lets you compare ability damage curves by race/form/level

