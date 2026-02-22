# DBForged Racial Abilities & Special Effects Design Document

## Overview

This document outlines special abilities and effects from the Dragon Ball Z/Super universes for integration into DBForged. Each ability includes design rationale, game mechanics, balancing factors, and implementation notes.

---

## 🦸 Saiyan Racial Abilities

### 1. Zenkai Boost (悟飯飯)
**Description:** Saiyans have the unique ability to grow significantly stronger after recovering from near-death experiences. This is their most iconic racial trait.

**Design Rationale:** 
- Mirrors the iconickai boost seen throughout DBZ (G Zenoku after Vegeta fight, Gohan after Cell, etc.)
- Creates exciting gameplay moments where players are motivated to push boundaries
- Rewards risk-taking and aggressive playstyles

**Implementation:**

```
Zenkai Activation Conditions:
- Player must drop below 20% HP from maximum health
- Player must then heal back above 80% HP 
- Cooldown: 24 hours real-time (or configurable)

Power Scaling:
Base PL Increase: +5% of current base PL (pre-boost)
Health Threshold Bonus: +0.5% for every 10% HP below 20% (max +2%)
Healing Speed Bonus: +0.25% for every 1% healed per second (max +1%)

Example Calculation:
- Player at 10,000 PL gets knocked to 15% HP
- Heals back to 100% over 5 seconds
- Base boost: 10,000 × 0.05 = +500 PL
- Health threshold bonus: +1% (was 5% below threshold) = +100 PL  
- Healing speed bonus: +1.25% (average healing rate) = +125 PL
- Total: +725 PL (7.25% increase)

Stack Limit: Stacks up to 10 times (theoretical max ~63% increase from base)
Soft Cap: After 5 stacks, effectiveness reduced by 50%
Hard Cap: After 10 stacks, no additional Zenkai gains (lifetime)
```

**Balancing Notes:**
- Significant but not game-breaking
- Requires being at genuine risk (not just deliberate self-damage)
- Real-time cooldown prevents spam
- Lifetime cap prevents infinite scaling

---

### 2. Great Ape Transformation (大猿)
**Description:** Under a full moon, Saiyans can transform into the Great Ape (Oozaru), gaining massive power but losing rational thought.

**Design Rationale:**
- Iconic Saiyan transformation from early DB
- Creates unique moon-phase gameplay events
- High risk/reward mechanic

**Implementation:**

```
Transformation Conditions:
- Must be exposed to full moon light for 10 continuous seconds
- Base PL must be at least 5,000
- Transformation lasts 3 minutes or until moon is blocked
- Cannot use transformation more than once per moon cycle

Power Multiplier:
- Base PL × 10 (ten times normal power)
- Ki generation × 15 (massive energy output)
- Physical strength × 12

Drawbacks:
- Cannot use technical commands/abilities (AI controls character)
- Increased Ki consumption rate (2× normal)
- Vision reduced to 50% effectiveness
- Take 5% max HP damage every 10 seconds (burnout)
- 30 second weakness after transformation ends: -50% PL

Counterplay:
- Destroy moon (certain areas/conditions)
- Blind the Saiyan
- Wait out transformation
- Use Solar Flare to force cancellation
```

**Balancing Notes:**
- Extremely powerful but high risk
- AI control during transformation prevents exploit
- Self-damage mechanic prevents infinite duration
- Weakness period creates vulnerability window

---

### 3. Super Saiyan Transformation (超サイヤ人)
**Description:** The legendary Super Saiyan transformation achieved through intense emotional power, typically anger.

**Design Rationale:**
- Most iconic DB transformation
- Should feel powerful and earned
- Multiple tiers for progression

**Implementation:**

```
Tier 1 - Super Saiyan (超サイヤ人)
Activation: Emotional trigger (anger, determination) or manual command
PL Multiplier: ×50 to base PL
Ki Drain: 5% of max Ki per second
Physical Boost: +40% damage dealt, +30% damage taken
Visual: Golden aura, green eyes, hair turns golden/spikes

Tier 2 - Super Saiyan 2 (超サイヤ人2)  
Activation: Requires mastering SS and reaching 500,000 PL
PL Multiplier: ×100 to base PL
Ki Drain: 8% of max Ki per second
Physical Boost: +60% damage dealt, +25% damage taken
Visual: Larger golden aura, more pronounced spiking

Tier 3 - Super Saiyan 3 (超サイヤ人3)
Activation: Requires mastering SS2 and reaching 2,000,000 PL
PL Multiplier: ×250 to base PL  
Ki Drain: 15% of max Ki per second
Physical Boost: +100% damage dealt, +20% damage taken
Visual: Massive elongated golden hair, dramatic aura

Transformation Requirements:
- Must have achieved the form at least once through RP/quest
- Base PL thresholds prevent premature access
- Emotional state can assist but not required once unlocked

Special Rules:
- Can only sustain transformation for (500 / Ki stat) seconds initially
- Training increases duration over time
- Going below 10% Ki forces reversion
- Defeating enemies while transformed grants bonus XP
```

**Balancing Notes:**
- Tiered progression feels earned
- Increasing Ki drain prevents infinite use
- Physical vulnerability keeps it risky
- Training mechanics for sustainability

---

### 4. Ki Detection (気感知)
**Description:** Saiyans have inherently sharp ki sensing, allowing them to detect hidden enemies and power levels.

**Implementation:**

```
Base Detection Range: (Ki Control × 10) + (PL × 0.001) meters
Enhanced Detection: Can sense suppressed power within 50% of normal range

Passive Benefits:
- Cannot be surprised by hidden enemies (within detection range)
- Can identify approximate PL tier of opponents automatically
- Sense ki-sensitive attacks coming (dodge bonus: +5%)

Active Ability - Sense:
Command: /sense [target/room]
Ki Cost: 10 Ki
Cooldown: 30 seconds
Effect: Reveals exact PL and hidden characters in area
```

---

### 5. Battle Instinct (戦闘本能)
**Description:** Saiyans have natural combat reflexes that improve in battle.

**Implementation:**

```
Passive Bonuses:
- +2% combat damage for every minute in continuous combat
- Maximum +20% bonus (10 minutes to max)
- Bonus resets after 5 minutes of no combat
- Critical hit chance +5% when below 30% HP

Combat Adaptation:
- After defeating 10 enemies of similar PL, gain +1% permanent damage
- Maximum +10% from this bonus
- Resets if PL increases by more than 50%
```

---

## 👽 Other Racial Abilities

### Namekian Regeneration (ナメック星人の再生)
**Description:** Namekians can regenerate lost body parts and recover from injuries.

**Implementation:**

```
Passive Regeneration:
- Regenerate 1% max HP every 10 seconds when above 20% HP
- Lost limbs regenerate at 1 per 30 seconds (if above 40% HP)
- Cannot regenerate when below 10% HP

Active Ability - Regeneration Burst:
Ki Cost: 25 Ki
Cooldown: 2 minutes
Effect: Regenerate 25% max HP over 10 seconds
- Interruption: Taking more than 15% HP damage pauses regeneration for 5 seconds
- Enhanced: If currently missing limb, regenerate it instead

Combat Limitation:
- Cannot use during combat (only out of combat or brief lulls)
- Each use increases next cooldown by 30 seconds (max 5 minutes)
```

---

### Namekian Dragon Summoning (之神龍召喚)
**Description:** Namekians can summon the Namekian Dragon to grant wishes.

**Implementation:**

```
Summoning Requirements:
- Must have completed Dragon Ball quest line
- Need 7 Dragon Balls in inventory
- Summoning takes 30 seconds (channeled)

Dragon Capabilities:
- Wish 1: Restore full health (one-time per summon)
- Wish 2: Remove death/permadeath status
- Wish 3: Grant one temporary PL boost (+20% for 1 hour)
- Wish 4: Learn one technique (limited selection)

Limitations:
- Each Dragon has maximum 3 wishes
- Dragon disappears for 130 days after all wishes used
- Only one Dragon can exist per server at a time
```

---

### Frost Demon Ice Manipulation (フリーザ族の冰)
**Description:** Members of the Frost Demon race can manipulate ice and cold.

**Implementation:**

```
Passive: Ice Resistance
- 50% resistance to ice/cold damage
- Can walk on ice without penalty
- Immune to freezing effects

Active Abilities:

1. Frost Aura (寒気のオーラ)
Ki Cost: 15 Ki
Duration: 30 seconds
Cooldown: 1 minute
Effect: Surrounding enemies take 3% max HP cold damage per second
Movement speed reduced by 20% for affected enemies

2. Death Beam ( death beam)
Ki Cost: 30 Ki  
Range: 50 meters
Damage: 150% of PL in cold damage
Charge Time: 1 second
Cooldown: 5 seconds

3. Frost Form (-freezer form transformation)
Requires: 100,000 PL
PL Multiplier: ×20
Duration: 2 minutes
Ki Drain: 10% per second
Benefits: +30% all damage, regeneration 2% HP per second
Drawback: -20% speed, visible aura reveals location
```

---

### Android Unlimited Energy (アンドロイドの無限エネルギー)
**Description:** Androids have internal reactors that generate infinite Ki-like energy.

**Implementation:**

```
Passive Benefits:
- No Ki stat (use Energy stat instead)
- Energy regenerates at constant rate: 50 per second (regardless of actions)
- Can use abilities without worrying about energy management
- Immune to Ki depletion effects

Active Abilities:

1. Photon Flash (光子フラッシュ)
Energy Cost: None (free)
Range: 30 meters
Damage: 80% PL as light damage
Cooldown: 3 seconds

2. Energy Absorption (エネルギー吸収)
Energy Cost: None
Activation: Passive
Effect: Gain 5% of damage taken as energy
Nearby energy attacks have 20% chance to be absorbed

3. Self-Repair (自己修復)
Energy Cost: None (free)
Cooldown: 5 minutes
Effect: Restore 50% max HP over 30 seconds
Cannot be used while taking continuous damage
```

---

### Majin Shapeshifting (魔人間の変身)
**Description:** Majins can alter their body composition for various effects.

**Implementation:**

```
Passive Benefits:
- Can stretch body up to 200% length
- No fall damage (rubber-like body)
- 25% resistance to blunt damage

Active Abilities:

1. Candy Beam (キャンディービーム)
Ki Cost: 20 Ki
Range: 40 meters
Effect: Turn enemy into candy for 5 seconds (non-combat)
Cooldown: 3 minutes
Limitation: Only works on enemies below 50% PL

2. Absorption (吸収)
Ki Cost: 30 Ki
Cooldown: 10 minutes
Effect: Temporarily gain 20% of target's stats for 5 minutes
Requirement: Must defeat opponent while they are stunned
Risk: 10% chance to lose 10% current PL if target was higher level

3. Regeneration (再生)
Ki Cost: 15 Ki
Cooldown: 2 minutes
Effect: Regenerate 30% max HP instantly
Limit: Can only be used 3 times per battle
```

---

## 🌟 Universal Abilities (All Races)

### Flight (飛行)
**Description:** Basic flight capability available to all characters.

**Implementation:**

```
Base Requirements: PL 1,000 or higher
Energy Cost: 2 Energy/Ki per second of flight
Speed: Base speed = (PL / 1000) meters per second
Maximum Altitude: 1000 meters + (PL / 5000) meters

Combat Modifiers:
- +10% accuracy when flying vs ground targets
- -5% accuracy when attacking other flying targets
- Aerial maneuvers: +15% dodge chance for first 3 seconds of engagement
```

---

### Ki Sense Mastery (気の感知マスター)
**Description:** Enhanced ability to detect and analyze ki/energy.

**Implementation:**

```
Base Detection: (Ki Control × 15) + (PL × 0.002) meters
Advanced Detection: Can sense suppressed PL, hidden enemies, nearby threats

Skill Tree:
- Tier 1: Basic Sense (+10% detection range)
- Tier 2: Threat Analysis (shows enemy PL when targeting)
- Tier 3: Precognitive Dodge (+8% dodge when ki sensed enemies nearby)
- Tier 4: Power Scouter (can use /scan to show detailed stats)
- Tier 5: Mass Detection (sense all enemies in area at once)
```

---

### Special Techniques (必殺技)

#### Solar Flare (太陽拳)
**Description:** Blind对手 with intense light.

```
Race: Universal (can be learned)
Ki Cost: 15 Ki
Range: 30 meter radius
Effect: Blind all targets for 8 seconds
Save: Ki Control vs attacker Ki Control (DC 15)
Cooldown: 45 seconds
Combat Use: Excellent interrupt, creates escape opportunities
```

---

#### Afterimage (残像)
**Description:** Move so fast that an afterimage remains.

```
Race: Universal (can be learned)  
Ki Cost: 20 Ki
Duration: Create 1 afterimage that lasts 3 seconds
Effect: Afterimage mimics your last action
Cooldown: 30 seconds
Combat Use: Confuse enemies, create decoys
```

---

#### Spirit Bomb (元気玉)
**Description:** Gather energy from surroundings into a massive attack.

```
Race: Universal (requires quest/training)
Charge Time: 5-30 seconds (longer = more power)
Energy Gather: 50% from user + 50% from nearby allies
Damage: (Charge Time × User PL × 0.5) to max 50× PL
Radius: 20 meters (centered on impact)
Friendly Fire: Yes (reduced damage to allies: 25%)
Cooldown: 1 hour
Strategic Use: Game-changer in group fights, requires setup
```

---

## 🎮 Implementation Priority Recommendations

### Phase 1: Core Mechanics (Must Have)
1. **Zenkai Boost** - Flagship Saiyan mechanic
2. **Basic Flight** - Fundamental to DB feel  
3. **Ki Detection** - Essential for combat
4. **Android Energy System** - Unique race mechanic

### Phase 2: Enhanced Combat (Should Have)  
1. **Super Saiyan Tiers** - Progression system
2. **Namekian Regeneration** - Sustainability
3. **Solar Flare/Interrupts** - Combat depth

### Phase 3: Advanced Features (Nice to Have)
1. **Great Ape** - Special events
2. **Majin Absorption** - Complex mechanics
3. **Spirit Bomb** - Ultimate attacks
4. **Dragon Wishes** - Endgame content

---

## 📊 Balancing Guidelines

### Power Level Thresholds

| PL Range | Tier | Example | Zenkai Cap | Transformation |
|----------|------|---------|------------|----------------|
| 1-10,000 | Earth | Humans, low-level | 2 stacks | None |
| 10,001-100,000 | Earth Elite | Krillin, Yamcha | 4 stacks | None |
| 100,001-500,000 | Planetary | Goku (DB), Vegeta | 6 stacks | SS1 |
| 500,001-2,000,000 | Stellar | SS Goku, Frieza | 8 stacks | SS2 |
| 2,000,001+ | Universal | SS3+, Gods | 10 stacks | SS3 |

### Damage Scaling Formula

```
Final Damage = (Attack PL / Defense PL) × Base Damage × Modifier × Random(0.95-1.05)

Where Modifiers include:
- Technique bonus: +20-50% for special moves
- Elemental: ×1.5 for type advantages
- Critical: ×2.0 (5% base chance + 1% per 100k PL)
- Transformation: ×1.5-3.0 depending on form
- Zenkai: ×1.1-1.5 depending on stacks
```

---

## 🔄 Integration with Existing Systems

### Combat System Integration
- All racial abilities interact with existing combat tick system
- Damage and healing scale with existing PL calculations
- Cooldowns use existing cooldown infrastructure

### Character Progression
- Transformation unlocks tied to PL milestones
- Technique learning uses existing skill system
- Racial passive bonuses stack with equipment/techniques

### Quest Integration
- Dragon Ball collection for Dragon Summoning
- Transformation mastery through specific quests
- Technique acquisition through training quests

---

## 📝 Design Notes

### Core Philosophy:
1. **Fantasy Authenticity**: Abilities should feel like DBZ source material
2. **Balance**: Power must come with trade-offs
3. **Progression**: Unlock abilities through achievement
4. **Choice**: Different builds create different playstyles
5. **Teamwork**: Some abilities benefit from coordination

### Risk/Reward Framework:
- High power transformations = High Ki drain + Vulnerability
- Near-death bonuses = Genuine risk required
- Ultimate attacks = Long cooldowns + Setup time

### Fun Factor:
- Zenkai creates "clutch comeback" moments
- Transformations feel rewarding and powerful
- Racial diversity creates distinct playstyles
- Team combos make groups more than sum of parts

---

*Document Version: 1.0*  
*Last Updated: 2026-02-22*  
*Game Version: 0.1 (DBForged Vertical Slice)*
