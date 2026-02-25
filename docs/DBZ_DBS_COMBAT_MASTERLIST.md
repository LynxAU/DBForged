# DBForged DBZ/DBS Combat Masterlist (Abilities, Racials, Transformations)

## Scope (important)

`"Every ability ever"` in Dragon Ball becomes effectively unbounded if we include:
- every one-off game move
- filler-only names
- alternate naming/localization variants
- card/mobile crossover variants

So this document uses a practical design scope:
- **DBZ + DBS canon-facing combat abilities**, grouped by **owner**
- **Technique families collapsed** (example: `Kamehameha` family instead of listing every named Kamehameha variant from every game)
- **Top 50 curated abilities** for gameplay
- **3 racial baseline abilities per DBForged race**
- **Transformations listed separately** (DBZ + DBS, by race/family)

This keeps it useful for implementation while still feeling authentically Dragon Ball.

DBForged playable races (from codebase): `saiyan`, `human`, `namekian`, `frost_demon`, `android`, `majin`.

---

## Combat Design Rules (Dragon Ball Feel)

- Big attacks should feel **big**: long charge, loud telegraph, huge payoff.
- Strong beams should support **beam clashes**.
- Control moves need **counterplay** (interrupt, resist meter, cooldown, immunity windows).
- Burst forms should cost **Ki / stamina / post-form fatigue**.
- Race identity should be mostly in **resource behavior and passive mechanics**, not only damage multipliers.

---

## 1) Owner-Grouped Ability Masterlist (DBZ + DBS, family-collapsed)

Each line includes a short **port idea** for your game.

### Goku

- **Kamehameha (family)**: Core beam archetype. Tap = poke beam, charged = finisher beam.
- **Warp/Instant Kamehameha**: Teleport into point-blank beam punish. Long cooldown, high commitment.
- **Spirit Bomb (Genki Dama family)**: Raid/team finisher. Long channel, ally energy contribution.
- **Dragon Fist**: Melee burst finisher with super armor startup.
- **Kaioken (technique buff)**: Burst offense/speed buff with self-drain or fatigue.
- **Instant Transmission**: Reposition to ally/enemy/marker. Ki + cooldown limited.
- **Solar Flare (learned utility)**: Blind/lock-break cone. Great disengage tool.
- **God Bind (DBS)**: Short hold/control setup; boss CC reduced duration.
- **Ki Mines / small utility blasts (DBS anime usage style)**: Zoning utility for spacing gameplay.

### Vegeta

- **Galick Gun**: Fast charge beam alternative to Kamehameha.
- **Final Flash**: High-telegraph high-damage beam; elite/boss killer.
- **Big Bang Attack**: Large explosive orb AoE, anti-group.
- **Final Explosion**: Self-centered nuke with HP/Ki sacrifice.
- **Gamma Burst Flash**: Endgame beam burst with heavy cooldown.
- **Energy Rings / Binding techniques**: Short root setup for follow-up beam.
- **Forced Spirit Fission (DBS manga)**: Anti-absorb/anti-buff mechanic; strips borrowed power.
- **Spirit Sword / Ki Blade usage (DBS manga)**: Melee ki weapon with barrier penetration.

### Gohan

- **Masenko (family)**: Fast overhead-style beam; excellent combo ender.
- **Kamehameha family**: Shared beam path but tuned for hybrid builds.
- **Burst Rush / rush combos**: Targeted melee pressure sequence.
- **Soaring Dragon Strike**: Launcher/anti-air combo starter.
- **Special Beam Cannon (Beast era use)**: Form-gated piercing finisher.

### Piccolo (Namekian kit template)

- **Special Beam Cannon (Makankosappo)**: Long-charge piercing beam with armor penetration.
- **Hellzone Grenade**: Setup/trap orbs that converge on command.
- **Light Grenade**: Heavy explosive projectile, chargeable.
- **Explosive Demon Wave / Demon Flash family**: Mid-tier ranged pressure beams/blasts.
- **Stretching Arm / Demon Hand**: Extended grab/root utility.
- **Regeneration**: Channel heal with interrupt vulnerability.
- **Barrier / defensive ki fields**: Namekian utility defense option.
- **Clone / split body utility (where applicable)**: Tactical decoy/crossfire gameplay.

### Future Trunks

- **Burning Attack**: Iconic hand-sign burst projectile.
- **Finish Buster**: Heavy ranged burst with knockback.
- **Heat Dome Attack**: Launch + dome finisher; anti-air execution tool.
- **Shining Sword Attack / sword rushes**: Hybrid melee-ranged finisher route.
- **Sword of Hope (DBS)**: Raid/team ultimate with ally energy contribution.
- **Mafuba (trained use in Super)**: Seal/control tool; huge cost, boss-limited impact.

### Krillin

- **Destructo Disc (Kienzan family)**: Armor-piercing cutting projectile; precision reward.
- **Scattering Bullet / split-shot ki**: Delayed zoning projectile.
- **Solar Flare**: Blind/escape setup.
- **Kamehameha**: Lower damage, faster startup variant.
- **Ki Transfer / support energy share**: Ally resource support channel.

### Tien Shinhan

- **Tri-Beam (Kikoho)**: High damage with HP/stamina self-cost.
- **Neo Tri-Beam**: Repeat suppression pulses for area control.
- **Dodon Ray**: Fast precision finger beam punish.
- **Solar Flare**: Smaller cone, longer blind variant.
- **Multi-Form**: Clone utility at stat split cost.
- **Four Witches Technique (extra arms)**: Short melee buff transformation-like technique.

### Yamcha

- **Wolf Fang Fist**: Fast rush combo / pressure chain.
- **Spirit Ball (Sokidan)**: Player-guided projectile; high skill expression.
- **Kamehameha**: Budget beam path for human builds.

### Roshi (important utility source)

- **Kamehameha (master version)**: Stronger charge efficiency / teaching path.
- **Mafuba (Evil Containment Wave)**: Seal mechanic template.
- **Max Power (buff form/technique state)**: Human transformation/burst mode template.
- **Lightning Surprise / paralysis style techniques**: Control niche for older-master archetype.

### Frieza (Frost Demon template source)

- **Death Beam (family)**: Fast sniper beam, very short charge.
- **Barrage Death Beam**: Multi-shot beam burst DPS.
- **Death Ball**: Heavy explosive orb with large radius.
- **Supernova**: Extreme siege/raid ultimate.
- **Nova Strike**: Aura-coated rush attack.
- **Telekinesis**: Lift/interrupt control tool.
- **Psychic debris barrages**: Zoning and pressure while moving.
- **Ki Blades / slicing techniques**: Precision pressure options.

### Frost (DBS, alt Frost Demon style)

- **Poison needle/cheat-tech concept (anime-specific behavior)**: If adapted, make PvE-only status gimmick.
- **Death Beam variants**: Lower damage, higher utility/counterplay than Frieza.
- **Suppression/release pacing**: Good model for stance-based Frost Demon gameplay.

### Android 17 / 18 (Android template source)

- **Android Barrier**: Instant defensive barrier with projectile negation.
- **Barrier Prison**: Short trap/root sphere.
- **Assault Barrier**: Barrier-wrapped gap closer.
- **Energy volleys / Power Blitz / Photon Flash-type blasts**: Reliable sustained ranged pressure.
- **Infinite energy pressure style**: Not a move, but defines race resource identity.

### Cell (Bio-Android / boss template)

- **Solar Kamehameha**: Massive beam ultimate.
- **Perfect Barrier**: Superior barrier defense.
- **Regeneration**: Phase sustain / comeback mechanic.
- **Absorption (tail)**: Boss-only execute/growth mechanic.
- **Cell Juniors**: Summon pressure / add phase.
- **Mixed move access (Kamehameha, Solar Flare, etc.)**: “copy kit” boss identity.

### Majin Buu Forms (Majin template source)

- **Transfiguration Beam**: Hard control (candy/object state) with resistance tiers.
- **Chocolate Beam**: Control + sustain payoff.
- **Vanishing Ball**: Fast compact destructive projectile.
- **Planet Burst / giant destruction ball**: Raid-scale nuke.
- **Human Extinction Attack**: Map-wide scripted barrage.
- **Regeneration / body reform**: Strong sustain with anti-regen counters.
- **Absorption**: Boss phase mechanic / temporary trait theft.

### Gotenks (high-value game-port techniques)

- **Galactic Donuts**: Ring bind/root.
- **Super Ghost Kamikaze Attack**: Summoned explosive projectiles.
- **DIE DIE Missile Barrage**: Spread projectile burst.

### Vegito / Gogeta (fusion technique families)

- **Spirit Sword / Ki Blade**: Beam-sword melee finisher.
- **Big Bang Kamehameha**: Fusion beam ultimate.
- **Stardust Breaker / Soul Punisher (Gogeta)**: High-impact burst projectile with purification fantasy.
- **Afterimage rush combos**: High mobility finisher strings.

### Hit (DBS)

- **Time-Skip**: Micro-time displacement for punish windows.
- **Time Cage**: Short imprison/control zone.
- **Vital Point Strikes**: Assassin burst combo route.

### Jiren (DBS, boss template)

- **Power Impact / eye pressure / shockwaves**: Heavy stagger and projectile pressure.
- **Meditative guard / ki walling**: Anti-rush defensive stance.
- **Limit-break pressure aura**: Enrage aura phase mechanic.

### Toppo (DBS, transformation-adjacent combat style)

- **Justice Flash / explosive justice blasts**: Burst projectile suite.
- **Hakai sphere (GoD mode)**: Restricted delete/execute mechanic.
- **Destruction aura pressure**: DoT zone / anti-projectile field in endgame content.

### Beerus / GoD Techniques

- **Sphere of Destruction**: Tracking orb pressure.
- **Hakai**: Threshold execute / severe debuff / PvE deletion rule.
- **Casual shockwave strikes**: High-priority melee/ki poke template for bosses.

### Whis / Angel (mostly NPC-only)

- **Ultra-fast reposition / time rewind utility**: Narrative or scripted raid mechanic, not player-accessible early.
- **Staff barriers / nullification**: Admin-tier/NPC control mechanics.

### Broly (DBZ movie and DBS Super Broly influences; use DBS if strict)

- **Gigantic Roar / explosive wave attacks**: Brawler AoE knockback bursts.
- **Gigantic Meteor / heavy green energy orbs**: Strong chase projectiles.
- **Berserker rush strings**: Armor-heavy melee chain identity.

### Universal / Shared Dragon Ball Technique Families (important for build system)

- **Ki Blast (single / volley / charged)**: Baseline ranged attack tree.
- **Energy Wave / Beam generic family**: Teachable beam framework with school-specific variants.
- **Afterimage / Vanish Step**: Dodge/reposition toolkit.
- **Flight / air dash / dragon rush movement**: Core mobility systems, not just abilities.
- **Guard / burst guard / reflect**: Combat system actions with race modifiers.
- **Aura charge / Ki charging**: Core resource action (risky in combat, safe out of combat).
- **Sensing / ki reading**: Tracking / stealth detection / lock-on utility.

---

## 2) Curated Top 50 Abilities (Attacks / Support / Control)

Transformations are **excluded** here by request.

### Beam / Projectile (Core Impact Moves)

1. **Kamehameha**
2. **Super Kamehameha**
3. **Warp Kamehameha**
4. **Galick Gun**
5. **Final Flash**
6. **Big Bang Attack**
7. **Gamma Burst Flash**
8. **Masenko**
9. **Special Beam Cannon**
10. **Light Grenade**
11. **Burning Attack**
12. **Finish Buster**
13. **Death Beam**
14. **Barrage Death Beam**
15. **Death Ball**
16. **Supernova**
17. **Vanishing Ball**
18. **Spirit Bomb**
19. **Super Spirit Bomb**
20. **Solar Kamehameha** (boss/raid or high-tier PvE)

### Melee / Rush / Hybrid Finishers

21. **Dragon Fist**
22. **Wolf Fang Fist**
23. **Soaring Dragon Strike**
24. **Burst Rush**
25. **Nova Strike**
26. **Shining Sword Attack**
27. **Heat Dome Attack**
28. **Spirit Sword (Ki Blade Slash/Thrust)**
29. **Vital Point Strikes (Hit-style)**
30. **Assault Barrier** (hybrid engage)

### Control / Trap / Utility

31. **Solar Flare**
32. **Mafuba (Evil Containment Wave)**
33. **Hellzone Grenade**
34. **Energy Rings / Binding Rings**
35. **Telekinesis**
36. **Barrier Prison**
37. **Galactic Donuts**
38. **Time Cage**
39. **Time-Skip** (control/offense hybrid)
40. **Demon Hand / Stretching Grab**

### Defense / Support / Resource Play

41. **Android Barrier**
42. **Perfect Barrier** (boss or advanced version)
43. **Drain Field / Absorption Field**
44. **Ki Transfer**
45. **Regeneration (Namekian channel)**
46. **Body Reform (Majin regen)**
47. **Forced Spirit Fission** (anti-buff / anti-absorb)

### Spectacle / Raid / High-Identity Specials

48. **Final Explosion**
49. **Sword of Hope**
50. **Super Ghost Kamikaze Attack**

### Why these 50

- Strong **Dragon Ball identity**
- Good mix of **beam / melee / support / control**
- Multiple **charge-time archetypes**
- Supports **PvP and PvE raid design**
- Gives each race at least some natural “home fantasy”

---

## 3) 3 Racial Baseline Abilities Per Race (Balanced, Separate From Top 50)

These are **racial mechanics**, not named canon techniques.

## Saiyan

1. **Battle Adaptation** (passive)
- After taking heavy damage, gain a small stacking damage + ki efficiency bonus.
- Cap stacks low so it feels like `zenkai` without runaway snowballing.

2. **Saiyan Surge** (active burst)
- Short duration speed + melee damage boost.
- Post-effect fatigue: reduced guard/stamina regen for a few seconds.

3. **Last Stand Pride** (clutch trigger)
- Once per fight, dropping below a low HP threshold grants brief flinch resistance + Ki burst.
- Enables dramatic comeback moments without a full heal/reset.

## Human

1. **Martial Adaptability** (passive)
- Perfect dodge / perfect guard slightly reduces non-ultimate cooldowns.
- Humans win through execution and consistency.

2. **Combat Discipline** (active stance)
- Reduces incoming stagger/knockback and improves guard efficiency.
- Lets humans function into big beam metas.

3. **Ally Uplift** (support pulse)
- Small AoE Ki + stamina restore to nearby allies.
- Great in team fights, moderate solo value.

## Namekian

1. **Regenerative Tissue** (passive + active channel)
- Slow passive regen out of combat.
- In combat, can channel a stronger heal that is interruptible.

2. **Elastic Reach** (active utility)
- Temporarily increases melee/grab range and some skill reach.
- Creates a distinct spacing game.

3. **Namekian Fortitude** (passive)
- Higher guard durability and resistance to debuffs/interrupts.
- Lower burst than Saiyans but stronger fight endurance.

## Frost Demon

1. **Suppression State** (toggle stance)
- Suppressed mode: lower output, lower Ki drain, lower aggro.
- Released mode: higher damage/speed, higher resource costs.

2. **Execution Precision** (passive)
- Bonus crit/armor pierce on charged single-target beams against marked targets.
- Supports Death Beam-style gameplay identity.

3. **Tyrant Tempo** (active burst)
- Boosts ranged attack speed and movement.
- Increases incoming damage slightly while active.

## Android

1. **Infinite Reactor** (passive)
- Steady Ki regeneration in combat.
- Lower peak burst multipliers than organic races for balance.

2. **Barrier Matrix** (active defense)
- Small instant barrier that blocks weak projectiles and reduces chip damage.
- Weaker than signature `Android Barrier` skill.

3. **Targeting Suite** (passive)
- Improves projectile tracking and lock retention.
- Reduced effect on ultimates to preserve skillshots.

## Majin

1. **Elastic Body** (passive)
- Reduced blunt/melee stagger and partial grab resistance.
- Takes extra effect from slicing/piercing skills (e.g., Destructo Disc).

2. **Body Reform** (active sustain)
- Ki-based heal-over-time and cleanses one light debuff.
- Countered by anti-regen/seal effects.

3. **Absorb Momentum** (passive trigger)
- Taking a heavy hit grants brief damage reduction + small Ki refund.
- Helps sustain brawler momentum without infinite tanking.

---

## 4) Transformations (Separate List, DBZ + DBS)

Below are transformation/form lists from Z + Super with short game conversion slices.

## Saiyan / Hybrid Saiyan Transformations

### Great Ape (Oozaru) [Z]
- **Fantasy**: Giant primal power, huge physical force.
- **Game slice**: Giant mode with tail weak point, slower movement, massive cleave.
- **Suggested stats**: `HP +80%`, `Melee +60%`, `Speed -35%`, `Guard +50%`, `Ki cost +20%`

### Super Saiyan [Z/Super]
- **Fantasy**: Core power-up, aggressive aura and offense boost.
- **Game slice**: Standard offensive transformation with manageable upkeep.
- **Suggested stats**: `Damage +25%`, `Speed +12%`, `Ki regen +10%`, `Guard +10%`

### Super Saiyan Grade 2 [Z]
- **Fantasy**: Bulked output branch.
- **Game slice**: More damage, slightly slower tempo.
- **Suggested stats**: `Damage +35%`, `HP +10%`, `Speed -5%`

### Super Saiyan Grade 3 [Z]
- **Fantasy**: Extreme power, major speed loss.
- **Game slice**: Niche anti-boss burst form; poor dueling form by design.
- **Suggested stats**: `Damage +55%`, `Guard break +25%`, `Speed -30%`

### Mastered/Full Power Super Saiyan [Z]
- **Fantasy**: Controlled SSJ with low waste.
- **Game slice**: Efficient sustained form before SSJ2.
- **Suggested stats**: `Damage +28%`, `Stamina regen +10%`, `Ki drain minimal`

### Super Saiyan 2 [Z/Super]
- **Fantasy**: Faster, sharper, lightning aura, higher burst.
- **Game slice**: Tempo DPS form with stronger combo speed.
- **Suggested stats**: `Damage +40%`, `Speed +18%`, `Crit +10%`

### Super Saiyan 3 [Z/Super]
- **Fantasy**: Massive output with severe strain.
- **Game slice**: Short burst form with heavy Ki drain.
- **Suggested stats**: `Damage +65%`, `Speed +20%`, `Ki drain very high`

### Super Saiyan God [Super]
- **Fantasy**: Divine Ki, precision and control over brute force.
- **Game slice**: Evasive/efficient form with great dodge economy.
- **Suggested stats**: `Damage +35%`, `Speed +22%`, `Dodge cost -20%`, `Ki efficiency +25%`

### Super Saiyan Blue [Super]
- **Fantasy**: SSJ + God Ki stable high-tier form.
- **Game slice**: Endgame all-rounder with sustained pressure and beam dominance.
- **Suggested stats**: `Damage +55%`, `Speed +20%`, `Guard +15%`, `Ki drain medium`

### Super Saiyan Blue Kaioken [Super anime]
- **Fantasy**: Overclocked Blue with huge risk.
- **Game slice**: Overdrive burst; self-drain/fatigue mandatory.
- **Suggested stats**: `Damage +85%`, `Speed +30%`, `Self-drain high`, `Cooldown very long`

### Super Saiyan Blue Evolved [Super]
- **Fantasy**: Vegeta’s limit-broken Blue variant.
- **Game slice**: Tankier burst form than standard Blue.
- **Suggested stats**: `Damage +75%`, `HP +15%`, `Guard +20%`, `Ki drain high`

### Super Saiyan Rage [Super anime, Trunks]
- **Fantasy**: Rage-fueled hybrid power spike.
- **Game slice**: Clutch form that scales with party danger / low HP scenarios.
- **Suggested stats**: `Damage +70%`, `Speed +15%`, `Conditional buffs +`

### Potential Unleashed / Ultimate (Gohan) [Z/Super]
- **Fantasy**: Full latent power without SSJ inefficiency.
- **Game slice**: Efficient high-sustain hybrid form.
- **Suggested stats**: `Damage +50%`, `Ki efficiency +20%`, `Stamina regen +15%`

### Beast (Gohan) [Super]
- **Fantasy**: Gohan apex rage-awakening.
- **Game slice**: Short-duration apex with crit and piercing beam bonuses.
- **Suggested stats**: `Damage +95%`, `Crit +20%`, `Charge speed +25%`, `Ki drain high`

### Ultra Instinct Sign [Super]
- **Fantasy**: Incomplete instinct state emphasizing evasion.
- **Game slice**: Defensive apex with auto-dodge charges and counter windows.
- **Suggested stats**: `Dodge +40%`, `Speed +25%`, `Damage +30%`

### Mastered/Perfected Ultra Instinct [Super]
- **Fantasy**: Full instinct form, extreme offense and defense.
- **Game slice**: Very short top-tier transformation with strict cooldown lockout.
- **Suggested stats**: `Damage +85%`, `Dodge +50%`, `Speed +35%`, `Duration short`

### True Ultra Instinct [DBS manga]
- **Fantasy**: Personalized UI state with more offense than classic MUI.
- **Game slice**: Alternate branch for aggressive UI gameplay.
- **Suggested stats**: `Damage +90%`, `Dodge +30%`, `Speed +28%`

### Ultra Ego [DBS manga, Vegeta]
- **Fantasy**: Destroyer-style growth through damage/aggression.
- **Game slice**: Risk-reward form that ramps while taking hits.
- **Suggested stats**: `Damage +60% base`, `Ramp bonus while hurt`, `Defense volatility +`

### Super Saiyan Rosé [DBS, Goku Black]
- **Fantasy**: Divine Saiyan equivalent with corrupted god flair.
- **Game slice**: Boss/elite form with ki blade synergy and corruption status hooks.
- **Suggested stats**: `Damage +60%`, `Ki blade dmg +20%`, `Status pressure +`

### Wrathful / Ikari (Broly) [Super]
- **Fantasy**: Oozaru-like power in humanoid state.
- **Game slice**: Brawler form with armor windows and rage scaling.
- **Suggested stats**: `HP +25%`, `Melee +45%`, `CC resist +20%`, `Damage taken +10%`

### Super Saiyan (Broly line) [Super]
- **Fantasy**: Explosive escalation on top of primal power.
- **Game slice**: Short high-offense state with control drawbacks.
- **Suggested stats**: `Damage +55%`, `Speed +15%`, `Accuracy -5%`

### Full Power Super Saiyan (Broly) [Super]
- **Fantasy**: Berserk top-end Broly state.
- **Game slice**: Raid-tier brawler apex, countered by coordinated control.
- **Suggested stats**: `HP +40%`, `Damage +80%`, `Guard +30%`

## Namekian Transformations / Form Changes

### Great Namekian [Z/Super]
- **Fantasy**: Giant Namekian growth for size and force.
- **Game slice**: Giant mode with reach/HP spike, speed penalty.
- **Suggested stats**: `HP +70%`, `Melee +35%`, `Reach +60%`, `Speed -30%`

### Namekian Fusion (Nail/Kami-type) [Z]
- **Fantasy**: Permanent power integration.
- **Game slice**: Progression milestone/permanent unlock, not toggle form.
- **Suggested stats**: Permanent base stat boost + passive unlocks

### Power Awakening (Piccolo) [Super]
- **Fantasy**: Potential unlock, stronger and more efficient.
- **Game slice**: Balanced Namekian combat form for sustain/control.
- **Suggested stats**: `Damage +40%`, `HP +15%`, `Ki efficiency +20%`, `Regen +15%`

### Orange Piccolo [Super]
- **Fantasy**: Heavy top-tier Piccolo transformation.
- **Game slice**: Tank-bruiser apex with CC resist and guard break pressure.
- **Suggested stats**: `HP +55%`, `Damage +65%`, `Guard +35%`, `CC resist +25%`

### Orange Great Namekian (combo state) [Super]
- **Fantasy**: Orange power stacked with giant body.
- **Game slice**: Raid-only giant phase due scale and durability.
- **Suggested stats**: `HP +110%`, `Melee +70%`, `Speed -40%`

## Frost Demon / Frieza Clan Transformations

### First Form (suppression) [Z/Super]
- **Fantasy**: Constrained power shell for control/suppression.
- **Game slice**: Mostly roleplay/NPC stance or low-output mode.
- **Suggested stats**: `Damage -20%`, `Ki drain low`

### Second Form [Z]
- **Fantasy**: Brute-force release stage.
- **Game slice**: Phase escalation with more melee pressure.
- **Suggested stats**: `HP +20%`, `Damage +25%`

### Third Form [Z]
- **Fantasy**: Predatory offense-focused release stage.
- **Game slice**: Mobility/pressure phase.
- **Suggested stats**: `Damage +30%`, `Speed +10%`, `Guard -5%`

### Final Form [Z/Super]
- **Fantasy**: Compact true form with control and efficiency.
- **Game slice**: Likely default high-tier Frost Demon playable form fantasy.
- **Suggested stats**: `Damage +40%`, `Speed +18%`, `Ki efficiency +15%`

### 100% Full Power [Z/Super]
- **Fantasy**: Max output muscle state with strain.
- **Game slice**: Short steroid mode; output high, stamina drain high.
- **Suggested stats**: `Damage +70%`, `HP +20%`, `Stamina drain high`, `Speed decays`

### Golden Frieza [Super]
- **Fantasy**: Evolved apex form with massive boost.
- **Game slice**: Endgame transformation emphasizing ranged burst and mobility.
- **Suggested stats**: `Damage +85%`, `Speed +25%`, `Ki drain high`

### Controlled/Trained Golden [Super]
- **Fantasy**: Refined Golden with better stamina management.
- **Game slice**: Mastery upgrade node that fixes Golden’s drain weakness.
- **Suggested stats**: Golden profile with `Ki drain reduced ~35%`

### Black Frieza [DBS manga]
- **Fantasy**: New apex above Golden.
- **Game slice**: Late boss-only / elite-only at launch to preserve balance.
- **Suggested stats**: `Damage +120%`, `Speed +30%`, `Guard +25%`

## Android / Bio-Android Form Changes

### Android Overclock (conceptual race transformation for DBForged)
- **Fantasy**: Reactor overdrive / output spike.
- **Game slice**: Playable android burst form; higher output, barrier strength, heat buildup penalty.
- **Suggested stats**: `Damage +45%`, `Barrier +25%`, `Ki regen +20%`, `Overheat risk`

### Imperfect Cell [Z]
- **Fantasy**: Growth predator form.
- **Game slice**: Boss phase with absorption-based scaling.
- **Suggested stats**: `Damage +30%`, `Absorb scaling +`

### Semi-Perfect Cell [Z]
- **Fantasy**: Intermediate powerhouse form.
- **Game slice**: Boss phase with bigger AoEs and barrier emphasis.
- **Suggested stats**: `HP +40%`, `Damage +45%`

### Perfect Cell [Z]
- **Fantasy**: Complete balanced apex bio-android.
- **Game slice**: Main boss form with mixed toolkit (beam/barrier/regen).
- **Suggested stats**: `HP +60%`, `Damage +60%`, `Speed +15%`

### Super Perfect Cell [Z]
- **Fantasy**: Post-regeneration final escalation.
- **Game slice**: Enrage/final phase.
- **Suggested stats**: `Damage +80%`, `Speed +20%`, `Regen +20%`

### Cell Max [Super]
- **Fantasy**: Kaiju-scale unstable bio-android.
- **Game slice**: Raid-only giant boss with weak-point scripting.
- **Suggested stats**: `HP +200%`, `Damage +100%`, `Weak-point vulnerability high`

## Majin Transformations / Form Changes

### Innocent/Fat Buu [Z/Super]
- **Fantasy**: Durable, regenerative, utility-heavy Buu form.
- **Game slice**: Tank/control Majin branch.
- **Suggested stats**: `HP +55%`, `Damage +35%`, `Regen +30%`, `Speed -15%`

### Evil Buu [Z]
- **Fantasy**: Leaner, nastier offensive split form.
- **Game slice**: Speed/control emphasis transformation.
- **Suggested stats**: `Damage +50%`, `Speed +20%`, `Regen +15%`

### Super Buu [Z]
- **Fantasy**: Tactical and powerful Majin apex baseline.
- **Game slice**: Offensive caster-brawler hybrid Majin form.
- **Suggested stats**: `Damage +70%`, `Speed +15%`, `Control power +20%`, `Regen +20%`

### Buutenks (Super Buu + Gotenks absorb) [Z]
- **Fantasy**: Absorbed skill expansion and huge output.
- **Game slice**: Boss phase with borrowed Gotenks toolkit.
- **Suggested stats**: `Damage +85%`, `Skill variety +`, `CD reduction on borrowed moves`

### Buuhan (Super Buu + Gohan absorb) [Z]
- **Fantasy**: Buu absorption apex form.
- **Game slice**: Top-end boss phase with high offense + copied abilities.
- **Suggested stats**: `Damage +95%`, `HP +35%`, `Regen +25%`

### Kid Buu / Pure Buu [Z]
- **Fantasy**: Chaotic fast destruction form.
- **Game slice**: High-speed berserker Majin apex with strong regen pressure.
- **Suggested stats**: `Damage +75%`, `Speed +25%`, `Regen +25%`, `Defense -5%`

### Good Buu (Mr. Buu) [Z/Super]
- **Fantasy**: Friendly split Buu with sustain and utility.
- **Game slice**: Better as a spec/archetype than temporary transformation.
- **Suggested stats**: `HP +45%`, `Regen +25%`, `Support +20%`

## Human Transformations / Power-Up States (low count, still useful)

### Max Power (Roshi-style) [Z/Super]
- **Fantasy**: Muscle burst state for heavy attacks.
- **Game slice**: Human burst transformation with short duration.
- **Suggested stats**: `Damage +45%`, `Guard +20%`, `Speed -15%`

### Potential Unleashed (if granted to human path) [Z/Super]
- **Fantasy**: Mystic latent power unlock.
- **Game slice**: Efficient human endgame form (less flashy, highly practical).
- **Suggested stats**: `Damage +40%`, `Ki efficiency +20%`, `Stamina regen +15%`

---

## 5) Practical Buildout Plan (if you want this implemented in DBForged)

### Phase 1 (Most Fun Fast)
- Core systems: `Ki`, `Stamina`, `Guard`, charge time, cooldown, beam clash
- 12-15 launch skills from the Top 50
- 3 racial baselines per race
- 1-2 transformations per race

### Phase 2 (Depth)
- Add control ecosystem (binds, seals, barriers, regen counters)
- Add support skills (ki transfer, anti-buff, anti-absorb)
- Add raid-scale ultimates (Spirit Bomb, Sword of Hope, Supernova)

### Phase 3 (Cinematic Endgame)
- UI/UE/Beast/Orange/Golden/Blue branches
- Boss-only forms (Cell Max, Black Frieza, Buuhan, etc.)
- Transformation mastery and efficiency upgrades

---

## 6) Notes on “Every Ability Ever”

If you want a **truly exhaustive named-technique index** (including one-off variants, anime-only names, and possibly game-exclusive moves), I can do that next as a **generated data file**:

- `docs/db_techniques_master.csv` (owner, technique, source, canon tier, tags, port note)
- `docs/db_transformations_master.csv`

That is the right format for a real “everything” pass because it becomes sortable/filterable and easier to maintain than a giant prose doc.

