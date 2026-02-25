# DB Arena 2 - SSJ Transformation System Redesign

## Overview
Transformations (especially SSJ1) should feel earned - a harrowing, blood-sweat-and-tears experience with random chance elements that make each Saiyan's journey unique.

---

## 1. SSJ1 Random Roll System

### Current Problem
- Auto-transforms at PL 1000+ when rage hits 25
- Too easy, no feeling of achievement

### New System

#### Requirements to Roll:
1. **Powerlevel** ≥ 1,000
2. **Rage** ≥ 25
3. **Health** < 50% (must be struggling in combat)
4. **Not already transformed**

#### Roll Chance:
- **3% chance** to successfully transform into SSJ1
- **97% chance** for "near miss" flavor text

#### Near Miss Flavor Text (No Transform):
```
"{YYour hair flashes golden for an instant! Your eyes glow blue as a 
blazing aura surrounds your body... but then it fades away.{x"

"{YYou feel the power surging within you, your muscles bulge, your 
aura blazes bright... but you can't hold it. The transformation slips 
away.{x"

"{YGolgen energy erupts around you, your scream builds... but nothing 
happens. The power dissipates into the air.{x"

"{YYour body trembles as legendary energy surges through your veins.
For a moment you think you've done it... but the transformation fails.{x"
```

#### Successful Transform:
```
"{YYour eyes turn emerald green! Golden energy explodes outward, 
blazing like a thousand suns! Your hair spikes up, glowing bright 
gold as you ascend to Super Saiyan!{x

{YYou feel your power multiply exponentially!{x"
```

### Gravity Training Trigger
- Players can use `gravity train` in high-gravity rooms
- Training to brink of death (HP < 10%) triggers the same roll
- Adds a "gravity_count" to track training sessions

### Witnessing a Player's Death (THE CRITICAL MOMENT)
**20% instant trigger** when you:
- Are in the same room as a player dying
- Have PL 1000+ and rage 20+
- This is THE iconic DBZ moment (Goku watching Krillin die!)

#### Slow Buildup Sequence (15 seconds of flavor text):
```
0s:  "{YA nearby player falls! Your heart stops...{x"
2s:  "{YImages of your past battles flash before your eyes...{x"
4s:  "{RYou scream out in anguish! Energy begins to crackle around you!{x"
6s:  "{YGolden light emanates from your body! Your hair begins to shift!{x"
8s:  "{YThe ground cracks beneath your feet as power erupts!{x"
10s: "{RYOUR EYES TURN EMERALD GREEN!{x"
12s: "{YGOLDEN ENERGY EXPLODES OUTWARD!{x"
15s: "{YYou have ascended to SUPER SAIYAN!{x"
```

#### Player Death Event Hook:
- In `fight.c`: When a player dies, check witnesses
- Each witness with SSJ potential rolls 20% check
- If passed, start the 15-second transformation sequence
- Cannot be interrupted once started

---

## 2. Failed Transformation Tracking

### Frustration System
Track failed attempts to make success more meaningful:

```c
// In PC_DATA
int ssj_fail_count;      // Total failed attempts
int ssj_last_fail_time;  // Last failed attempt timestamp
```

### Bonus After Multiple Failures
- After 10 failed attempts: +1% chance (4% total)
- After 25 failed attempts: +2% chance (5% total)
- After 50 failed attempts: +3% chance (6% total)

### Flavor Text for Repeated Failures
```
// 5+ failures:
"{yYou've felt this before... the golden flash, the surging power...
but once again, it wasn't enough.{x"

// 10+ failures:
"{RThe power is there! You KNOW it's there! But your body won't 
listen to you!{x"

// 20+ failures:
"{rTears of frustration stream down your face as the golden aura 
fades once more...{x"
```

---

## 3. Legendary Super Saiyan (Broly/Kale Form)

### Character Creation
- **1% chance** for Saiyan/Half-breed characters
- Starts with "Super Saiyan Berserker" form

### Form Characteristics
- **Green hair** instead of gold
- **Out of control** - cannot manually transform down
- **Massive power boost** but unpredictable

### Berserker Mechanics

```c
// In PC_DATA
bool is_legendary_berserker;  // TRUE if Legendary SSJ
int berserker_rage;           // Builds up, controls random attacks
```

#### Berserker Rage:
- Starts at 0, maxes at 100
- Builds by: taking damage, being attacked, killing enemies
- At 50+: random ki blasts fire at random targets in room
- At 75+: random attacks on anyone in room (including allies!)
- At 100+: berserker rage mode - huge PL boost but attack everything

#### Berserker Attack Messages:
```
"{rYou suddenly unleash a ki blast without meaning to!{x

"{rYour body moves on its own! Energy gathers in your hands...{x

"{rThe legendary power within you demands release!{x
```

#### Controlling the Berserker:
- Must meditate/train to reduce rage
- Eventually learn to control it (becomes regular SSJ1)
- Quest to master the berserker form

---

## 4. Code Changes Required

### Files to Modify:

1. **src/fight.c**
   - Modify `rage()` function to check for SSJ1 roll conditions
   - Add near-miss flavor text
   - Add berserker random attack logic

2. **src/handler.c**
   - Add `check_ssj_transformation()` function
   - Modify transformation logic to use roll system

3. **src/merc.h**
   - Add to PC_DATA:
     ```c
     int ssj_fail_count;
     time_t ssj_last_fail_time;
     bool is_legendary_berserker;
     int berserker_rage;
     ```

4. **src/nanny.c**
   - Add 1% chance for Legendary SSJ at character creation

5. **src/act_move.c**
   - Add `do_gravity_train` command for gravity room training

6. **src/const.c**
   - Add "super saiyan berserker" transformation

---

## 5. Commands

### New Commands:
```
gravity train   - Train in gravity rooms, risk death for SSJ chance
meditate       - Reduce berserker rage (legendary only)
control         - Attempt to gain control of berserker form
```

---

## 6. Future Enhancements

- [ ] SSJ2/SSJ3 also have random roll components
- [ ] Unique transformation sequences per race
- [ ] Transformation combo with fusion system
- [ ] Zenkai boost after near-death experiences

---

## 13. Majin Race - Elastic Evolution

*"Majin power is limitless... I am endless..."*

### Concept
Majins (like Buu) evolve by:
- Absorbing enemies
- Getting angry (rage-based like Saiyans)
- "Kid" → "Evil" → "Super" → "Pure/Mystic" forms

### Transformation Path:

**Kid Buu (starting)** - Pink, small, elastic

**Super Majin (PL 5,000+)**:
```
{rYour body inflates with rage! Muscles bulge! You grow 
larger!
You have transformed into SUPER MAJIN!{x
```

**Absorption:**
- Absorb defeated foes to gain their powers
- Absorb SSJ → look like SSJ!
- Each absorb = stat boost

**Ultimate: Pure/Mystic (PL 20,000+)**:
```
{wYour body becomes translucent! All evil transmuted to PURE POWER!
You have achieved MYSTIC MAJIN!{x
```

### Unique Majin Abilities:
- Regeneration (heal over time)
- Elasticity (inflate/slim down)
- Absorb command
- Shape-shift

---

## 7. Namekian Fusion Transformation

### Concept
Namekians don't have rage-based transformations like Saiyans. Instead, their "first transformation" comes from fusion - a Namekian offering to fuse with you mid-battle!

### Trigger
- Player is fighting a Namekian NPC
- 0.03% chance (very rare!) when dealing a killing blow

### The Offer
```
{NameThe dying Namekian gasps, falling to his knees...

"Wait! I cannot fight anymore... but I am not ready to die!

I offer myself to you! Let us become one! Our power will 
double! I will become your strength!"

Do you accept? (fuse yes/no){x
```

### If Accepted (+50% power permanent):
```
{YThe Namekian's body begins to glow!

"Thank you... warrior. Let us become... stronger... together..."

The Namekian dissolves into green energy that flows into your 
body! You feel your power surge as two warriors become one!

{YYour max ki increases by 50%!{x
```

### If Rejected:
```
{y"Very well... I die with dignity. Thank you for this choice..."

The Namekian fades away, his spirit at peace.{x
```

### Implementation Notes:
- Check race of victim in `death_corpse()` or similar
- Only triggers on NPC kills, not player kills
- Add `fuse` command to accept/reject
- Apply permanent stat boost to attacker

### Namekian Ultimate Form: Namek Evolved
Like the orange form from Dragon Ball Super - Namekians can evolve to their ultimate state!

**Requirements:**
- Be a Namekian
- Have fused at least once (absorbed a Namekian's power)
- Reach PL 10,000+

**Trigger:** Manual command `evolve` when requirements met

**Visual:**
```
{Orange skin turns a deep orange! Horns grow longer and sharper!
Muscles bulge with incredible power! A bright orange aura 
blazes around you!

You have achieved NAMEK EVOLVED!{x
```

**Stat Changes:**
- +30% to all stats
- Orange aura (distinct from Super Namek's green)
- Can now use "Orange Form" skills

---

## 8. Future Race-Specific Transformations

### Other Races to Consider:
- **Humans**: Master all skills → "Potential Unleashed"
- **Android**: Mechanical enhancements - just get stronger
- **Konatsu**: (removed - not in game)
- **Truffles**: (TBD)
- **Demons**: (TBD)

---

## 14. Android Race - Mechanical Enhancement

*"I am the pinnacle of artificial creation..."*

### Concept
Androids stay human-looking but get mechanical upgrades. No transformation - just enhancements.

### Enhancement Stages (automatic at PL):

**Base Android**:
- Looks human, slight tech glow

**Mark I (PL 1,000+)**:
```
{CYour internal processors surge! New circuits activate!
Efficiency rating increased!{x
```

**Mark II (PL 3,000+)**:
```
{CNeural pathways synchronize! Reaction speed UP!{x
```

**Mark III (PL 7,500+)**:
```
{CEnergy core upgraded! Output +50%!{x
```

**Omega (PL 20,000+)**:
```
rALL SYSTEMS MAXIMUM! OMEGA STATUS ACHIEVED!{x
```

### Unique Abilities:
- Never tire (no ki depletion)
- Fast recharge
- Analyze enemy
- Overdrive (costs HP not ki)

---

## 10. Half-Breeds (Saiyan-Human)

### Inheritance
Half-breeds get access to:
- SSJ1, SSJ2, SSJ3 (same triggers as full Saiyans)
- Lower PL requirements (75% of Saiyan)
- Bonus: Can go further → Ascended forms + Beast

### Ascended Forms
After mastering SSJ3:
- **SSJ4** (if Saiyan heritage dominant)
- **Ascended Super Saiyan** (Super Saiyan 2+ power, different look)

### Ultimate: Beast Form (Gohan-style)
```
{WHITE energy surrounds you! Your hair turns pure white, 
standing on end! Your eyes glow pure white!

You have unlocked your BEAST form!{x
```
- Requires: Be a half-breed + reach PL 100,000 + complete "Beast 
  Awakens" quest
- Not rage-based - unlocked through training/potential

---

## 11. Super Saiyan God - THE DIVINE TRANSFORMATION

*"This power... it transcends mortal limits..."*

### Problem
The 6-Saiyan ritual would be exploited (group up, kill each other, everyone gets SSG).

### Solution: Divine Training Path
SSG requires training with DIVINE beings - not something you can game.

### Requirements:
1. Reach **PL 25,000+**
2. **Complete the Godly Trials:**
   - Train with Supreme Kai (find them in Otherworld/dimension)
   - Complete 3 divine quests
   - "Transcend mortal ki" at sacred location

### The Trials:
```
{CTravel to the Sacred World of the Kais.

The Supreme Kai regards you with ancient eyes...

"You seek divine power? Very well. Prove your worth.

1) Defeat the Guardian of Time
2) Bring me a drop of Holy Water from the Divine Spring
3) Survive 10 minutes in the Hyperbolic Time Chamber at 100x gravity"

These trials cannot be rushed or cheesed.{x
```

### SSG Transformation:
```
{CAURIED light surrounds you! Your mortal ki transforms into 
DIVINE ENERGY! Your hair turns red, a crimson aura blazes 
around you!

YOU HAVE ACHIEVED SUPER SAIYAN GOD!{x
```

### SSG > SSB (Blue):
- Requires mastering SSG
- Learn to "turn off" the godly aura (hide it)
- SSB = SSG + Super Saiyan

---

## 12. Frieza Race - Pure Tyranny

*"Weakness is unacceptable. Strength is the only truth."*

### Concept
Frieza race (Frieza, Cold, etc.) don't need transformations - they just get STRONGER through pure power and cruelty.

### No Special Conditions
- No rage, no fusion, no absorption
- Just: **get stronger**

### Power Evolution
- Every PL milestone reached = automatic stat boost
- Visual changes as they grow (tail grows, horns develop, etc.)

### Transformation Stages (Automatic based on PL):

**Base Form:** Any PL

**Second Form (PL 2,000+):**
```
{yYour body grows larger! Muscles bulge! Your tail thickens!
Your power has evolved!{x
```

**Third Form (PL 5,000+):**
```
{yHorns protrude from your head! Your armor-like skin hardens!
You have reached your second evolution!{x
```

**Final Form (PL 10,000+):**
```
{yYour body shrinks to its smallest, most refined form!
Your power is now CONCENTRATED! Every cell burns with 
unimaginable strength!

You have reached FINAL FORM!{x
```

**Golden Form (PL 50,000+):**
```
{rYour entire body turns GOLD! Your power has transcended 
even your own limits! You are PURE GOLD!{x
```

**Black Form (PL 100,000+):**
```
{dBlack energy swirls around your golden form!
You have evolved BEYOND GOLD! This is your TRUE power!{x
```

### Frieza Race Philosophy:
- "Power through cruelty" - killing enemies makes them stronger
- "Weakness is sin" - no sympathy for the weak
- "Absolute evolution" - always pushing limits
- Can unlock forms faster through ruthless play (killing players)

---

## 9. Bio-Android Absorption Transformation

### Concept
Bio-Androids (like Cell) absorb living beings to grow stronger and transform!

### Absorption Mechanic
- Every NPC kill has a chance to absorb them
- Absorbed = they become part of you, gain their power

### Absorption Messages:
```
{YYour tail wraps around the fallen foe! Their body dissolves 
into genetic material that flows into you!

You feel their power... their memories... becoming part 
of you!{x
```

### Transformation Stages:

**Stage 1: Larva (Starting Form)**
- Weak, small

**Stage 2: Semi-Perfect (Absorb 5 NPCs)**
```
{YYour body evolves! Muscles bulge, your tail grows stronger!
You have reached SEMI-PERFECT form!{x
- +20% stats

**Stage 3: Perfect (Absorb 15 NPCs + specific target)**
```
{YGOLDEN ENERGY SURROUNDS YOU! YOUR BODY REACHES PERFECTION!
You have achieved PERFECT FORM!{x
- +50% stats
- Can now use Perfect-level techniques

**Stage 4: Ultimate (Absorb 30 NPCs + complete quest)**
```
{ROrange energy erupts! Your power transcends perfection!
You have reached ULTIMATE BIO-ANDROID FORM!{x
- +100% stats
- Orange/perfect form hybrid

### Special Absorption Targets:
- Some NPCs are "perfect candidates" - absorbs give bonus progress
- May need specific targets (like Android 17 + 18 for Cell)

---

## 15. Truffle Race - The Last Survivor

*"I am the last of my kind... and I will be the STRONGEST..."*

### Concept
Like **Granolah** - the last surviving Truffle (Cerealian in the show, but we'll use Truffle). They can use Dragon Radar to find and "wish" for power, or just become a wrecking machine through pure training.

### Transformation Path:

**Base Truffle**:
- Uses advanced technology (Dragon Radar)
- Can locate strong enemies

**Powered Up (PL 2,000+)**:
- Through intense training or "wishes"
- Eyes glow, aura intensifies

**Granolah Mode (PL 10,000+)**:
```
{rYOUR EYES TURN GOLD! YOUR SENSING ABILITY MAXIMIZES!

"I am the last of my kind... and I will be THE STRONGEST!"

Your speed and precision reach godlike levels!{x
```
- Massive speed boost
- Critical hit chance increases
- Can "snipe" enemies (one-shot weak foes)

**Omega Truffle (PL 25,000+)**:
```
{dYou have transcended beyond Granolah!
Your power is NOWHERE NEAR ITS LIMIT!{x
```

### Unique Abilities:
- **Scan** - locate strong enemies in the world
- **Precise Strike** - high critical damage
- **One Shot** - if enemy PL < your PL / 10, instant kill
- **Bullet Time** - appear behind enemies instantly

---

## 16. Demon Race - Dark Ascension

*"From the depths of hell... I rise..."*

### Concept
Demons from other dimensions - dark energy transformation.

### Transformation Path:

**Base Demon**:
- Human-like but with demonic features

**Demonic Form (PL 3,000+)**:
- Horns grow, skin changes color
- Red/black aura

**Demon Lord (PL 10,000+)**:
- Full demonic transformation
- Commands other demons

**True Demon (PL 25,000+)**:
- Ascended beyond mortal demons
- Pure dark energy

### Unique Abilities:
- **Life drain** - heal from attacks
- **Dark void** - absorb ki attacks
- **Corrupt** - turn enemies' ki against them
- **Summon** - call forth lesser demons

---

## COMPLETE RACE SUMMARY

| Race | First Transform | Method |
|------|-----------------|--------|
| Saiyan | SSJ1 | 3% roll (PL1k + rage25 + <50%HP) |
| Legendary | Berserker | 1% at char create |
| Half-breed | SSJ1 | Same as Saiyan + Beast later |
| Namekian | Fusion | 0.03% on kill |
| Namekian | Namek Evolved | Fused + PL10k + evolve |
| Bio-Android | Semi-Perfect | Absorb 5/15/30 NPCs |
| Frieza Race | Auto | Just get stronger at thresholds |
| Majin | Super Majin | Rage + PL5k |
| Android | Mark upgrades | Mechanical enhancement |
| Truffle | Adaptive | Enemies adapt to them |
| Demon | Demonic | Dark ascension at thresholds |
| SSG | Divine | Complete god trials (PL25k+) |
