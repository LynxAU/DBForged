# DB Arena: Dragon Ball Z MUD - Complete Design Document

## For Evennia Implementation

---

## Project Overview

**Project Name:** DB Arena (Dragon Ball Arena)
**Genre:** MMORPG / MUD - Dragon Ball Z Theme
**Platform Target:** Evennia (Python-based MUD server)
**Inspiration:** Dragon Ball Z anime/manga

---

## Core Gameplay Loop

1. **Power Level Training** - Gain power through combat, training, meditation
2. **Transformation** - Transform into Super Saiyan forms (SSJ1-5)
3. **Combat** - Energy beams, melee, special attacks
4. **Fusion** - Combine with other players for massive power boost
5. **Questing** - Fight villains, collect Dragon Balls

---

## Implemented Systems (ROM C Code Reference)

### 1. Transformation Mastery System

**Concept:** Transformations are temporary but can be held longer with practice.

**Mechanics:**
- Base duration: 60 seconds at 0 mastery
- Max duration: 260 seconds at 100% mastery
- Formula: `60 + (mastery * 2)` = seconds holdable
- Mastery increases by 1% every 10 seconds while transformed
- Warnings at 80% ("Your aura flickers...") and 90% ("transformation slipping!")
- Auto-revert when time expires

**Transformation Tiers:**
| Form | PL Requirement | STR/DEX Bonus | Mastery Index |
|------|----------------|---------------|---------------|
| SSJ1 | 1,000 | +10 | 0 |
| SSJ2 | 5,000 | +20 | 1 |
| SSJ3 | 20,000 | +30 | 2 |
| SSJ4 | 50,000 | +40 | 3 |
| SSJ5 | 100,000 | +100 | 4 |

**Data Structure (Python/Evennia):**
```python
class CharacterDB(Typeclass):
    # Transformations
    trans_mastery = ListField(default=[0, 0, 0, 0, 0])  # SSJ1-5 mastery 0-100
    trans_start_time = IntegerField(default=0)  # Unix timestamp when transformed
    trans_current = StringField(default="")  # Current transformation name
    trans_last_mastery = IntegerField(default=0)  # Last mastery increase time
```

---

### 2. Powerlevel Drain System

**Concept:** Transformations exhaust the player - drain powerlevel while active.

**Mechanics:**
- SSJ1: 1% max PL per minute
- SSJ2: 2% max PL per minute
- SSJ3: 3% max PL per minute
- SSJ4: 4% max PL per minute
- SSJ5: 5% max PL per minute
- Warning at 20% PL ("too weak to maintain transformation!")
- Auto-revert at 10% PL ("too exhausted!")

**Code Logic:**
```python
# Called every second while transformed
def apply_pl_drain(character):
    drain_rates = {"ssj1": 1, "ssj2": 2, "ssj3": 3, "ssj4": 4, "ssj5": 5}
    rate = drain_rates.get(character.trans_current, 0)
    drain_amount = character.max_pl * (rate / 6000)  # Per second
    
    character.current_pl -= drain_amount
    
    if character.current_pl <= character.max_pl * 0.1:
        character.revert_transform()
```

---

### 3. Kaioken Hold-Down System

**Concept:** Hold kaioken for increasing multiplier, but you take self-damage.

**Mechanics:**
- Hold for up to 10 seconds
- Multiplier: x2 at 1s, x4 at 2s, ... x20 at 10s
- Formula: `multiplier = elapsed_seconds * 2`
- Self-damage increases each second: 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
- Formula: `damage = elapsed_seconds^2`
- Warning at 5+ seconds ("body is straining!")
- Forces revert if HP drops too low

**Code Logic:**
```python
def update_kaioken(character):
    if character.trans_current != "kaioken":
        return
    
    elapsed = current_time - character.trans_start_time
    if elapsed > 10: elapsed = 10
    
    multiplier = elapsed * 2
    self_damage = elapsed * elapsed
    
    # Apply self-damage
    character.hp -= self_damage
    
    # Store multiplier for damage calculations
    character.kaioken_multiplier = multiplier
    
    if character.hp < 10:
        character.revert_transform()
```

**Usage in Combat:**
```python
def calculate_damage(character, base_damage):
    multiplier = getattr(character, 'kaioken_multiplier', 1)
    return base_damage * multiplier
```

---

### 4. Namekian Fusion System

**Concept:** Absorb a dying Namekian for permanent stat boost.

**Mechanics:**
- 0.03% chance when killing a Namekian NPC
- NPC offers fusion before death
- Accept: +50% max KI permanently
- Decline: Politely refuse

**Implementation:**
```python
def check_namekian_fusion(chance_player, victim):
    if victim.race == "namek" and random.random() < 0.0003:
        victim.offer_fusion = True
        victim.fusing_with = chance_player
        
def accept_fusion(character, namek_npc):
    # +50% max ki
    character.max_ki = int(character.max_ki * 1.5)
    character.namek_fused = True
    character.send_message("You feel your latent Namekian power awaken!")
```

---

### 5. Beam Clash System

**Concept:** Two energy beams collide = struggle for dominance.

**Mechanics:**
- When two energy attacks collide, initiate beam clash
- Use `push` command to feed more energy
- Timing matters - push when opponent pushes for advantage
- Visual beam position indicator (0-100, start at 50)
- Winner pushes beam into loser
- Loser takes damage + knocked back

**Code Structure:**
```python
class BeamClash:
    def __init__(self, attacker1, attacker2):
        self.p1 = attacker1
        self.p2 = attacker2
        self.position = 50  # 0 = p1 wins, 100 = p2 wins
        self.p1_energy = 0
        self.p2_energy = 0
        
    def update(self):
        # Decay position toward center if no input
        if self.position < 50:
            self.position += 1
        elif self.position > 50:
            self.position -= 1
            
    def push(self, player, timing_bonus):
        if player == self.p1:
            self.p1_energy += 10 + timing_bonus
        else:
            self.p2_energy += 10 + timing_bonus
            
        # Compare energies
        if self.p1_energy > self.p2_energy:
            self.position -= 5
        elif self.p2_energy > self.p1_energy:
            self.position += 5
            
        # Check for resolution
        if self.position <= 0:
            return "p1_wins"
        elif self.position >= 100:
            return "p2_wins"
        return "continuing"
```

---

### 6. Flurry Attack System

**Concept:** Rapid successive attacks in combat.

**Mechanics:**
- Random chance during combat
- 3-5 rapid attacks
- Each attack has reduced damage (50%)
- Visual: "name unleash a flurry of strikes!"

---

### 7. Automap System

**Concept:** Visual map of surrounding area.

**Display:**
```
+-.,+-.,+-.,+-.,+-.,+-.,+-'
 {I}.-|{@}.-|{C}          
      +-.,+-.,+-.,+-.,+-.,+-'
Legend: @=You I=Inside C=City .=Field F=Forest
```

---

## Planned Features - Detailed

### 1. DBZ Login Greeting

**Concept:** When players connect, show a dramatic Dragon Ball Z themed greeting.

**Quotes:**
- "Welcome to Earth... Will you become a legend?"
- "It's over 9000!"
- "The battle begins now!"
- "Fear is the path to the dark side."
- "I am the hope of the universe."
- "Power level... it's nothing!"
- "This is the story of a warrior's journey..."
- "Stronger than any enemy!"
- "The legend shall become reality!"
- "Your power is growing!"

**Implementation:**
```python
def at_login(character):
    quotes = [
        "Welcome to Earth... Will you become a legend?",
        "It's over 9000!",
        # ... more quotes
    ]
    logo = """
    ██████╗ ██████╗ ██╗   ██╗██╗   ██╗███████╗
    ██╔══██╗██╔══██╗╚██╗ ██╔╝██║   ██║╚══███╔╝
    ██████╔╝██████╔╝ ╚████╔╝ ██║   ██║  ███╔╝
    ██╔═══╝ ██╔══██╗  ╚██╔╝  ██║   ██║ ███╔╝
    ██║     ██║  ██║   ██║   ╚██████╔╝███████╗
    ╚═╝     ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝
    """
    random_quote = random.choice(quotes)
    character.msg(f"{logo}\n\n{random_quote}\n")
```

---

### 2. Senzu Bean System

**Concept:** Rare healing items that restore full health and ki.

**Variants:**
| Item | Effect | Rarity |
|------|--------|--------|
| Senzu Bean | Full HP/KI | Very Rare |
| Sacred Water | Full HP | Rare |
| Meat | 50% HP | Uncommon |

**Implementation:**
```python
class SenzuBean(Object):
    def at_use(self, character):
        character.hp = character.max_hp
        character.ki = character.max_ki
        character.msg("You eat the Senzu Bean and feel completely restored!")
        self.delete()
```

---

### 3. Spirit Bomb

**Concept:** Charge a massive AoE attack that can devastate all enemies.

**Mechanics:**
- Charge up over 10-30 seconds
- Massive damage based on charge time
- Can be interrupted by damage while charging
- Affects ALL enemies in the room
- Very cinematic - room shakes, warning messages

**Command:** `spiritbomb` or `sb charge`

**Damage Formula:**
```python
def calculate_spirit_bomb_damage(character, charge_time):
    base_damage = character.max_pl * 0.5  # 50% of PL
    multiplier = charge_time / 10  # 1x per second
    return int(base_damage * multiplier)
```

**Risks:**
- If interrupted mid-charge, you take damage instead
- Takes time to set up (vulnerable)

---

### 4. Transform on Death (Ultra Instinct)

**Concept:** Rare chance to auto-transform when near death, like Goku's Ultra Instinct moment.

**Mechanics:**
- 20% chance when HP drops below 10%
- Automatically triggers highest available transformation
- Brief invulnerability (1-2 seconds)
- Massively increased stats for 30 seconds
- After effect, you collapse (HP resets to 50%)

**Implementation:**
```python
def check_ultra_instinct(character):
    if character.hp <= character.max_hp * 0.1:
        if random.random() < 0.20:  # 20% chance
            # Trigger transformation
            available_forms = ["ssj1", "ssj2", "ssj3", "ssj4", "ssj5"]
            for form in reversed(available_forms):
                if character.can_transform(form):
                    character.transform(form)
                    character.send_message("Your body moves on its own! ULTRA INSTINCT!")
                    break
```

---

### 5. Dragon Ball Collection

**Concept:** Collect 7 Dragon Balls to summon Shenron for wishes.

**Mechanics:**
- 7 unique Dragon Ball objects (numbered 1-7)
- Each found in different locations
- When all 7 collected, player can `summon_shenron`
- 3 wishes available

**Wishes:**
1. **Power Boost** - +50% to max PL
2. **Stat Boost** - +20 to all base stats
3. **Transformation Unlock** - Unlock next transformation
4. **Wish Back** - Revive a dead player
5. **Wish for Knowledge** - Instant skill training

**Implementation:**
```python
class DragonBall(Object):
    ball_number = IntegerField()  # 1-7
    
def check_all_collected(character):
    balls = [i for i in range(1,8) if character.has_item(f"dragon_ball_{i}")]
    return len(balls) == 7

def summon_shenron(character):
    if not check_all_collected(character):
        character.msg("You need all 7 Dragon Balls!")
        return
    
    # Show Shenron appearance
    shenron_appearance = """
                     ..\\  /.
                      .  \\ 
                      |   |
                      |   |  _.._
                   .  |   |.'   '-.
                  |   |   |        '.
                  |   |   |   .-.   |
             __   |   |   |  (   )  |
            /  '  |   |   |   '-'   |
           |      |   |   |         |
           '      |   |   |         |
            '-..__|   |   |      _.'
    """
    character.msg(shenron_appearance)
    character.msg("{YSHENRON: I am the eternal dragon. You have 3 wishes. What do you desire?{x")
```

---

### 6. Energy Sensing (Power Level Scanner)

**Concept:** Sense nearby power levels like scouter.

**Command:** `sense` or `scan`

**Output:**
```
Power Levels in the area:
[Goku]: 150,000 PL (fighting)
[Vegeta]: 145,000 PL (resting)
[Gohan]: 80,000 PL (resting)
[You]: 50,000 PL

Note: Enemies above 100,000 detected!
```

**Implementation:**
```python
def do_sense(character):
    room = character.location
    for target in room.characters:
        if target == character:
            continue
        pl = target.current_pl * target.max_pl / 100
        status = "fighting" if target.fighting else "resting"
        danger = "{R**DANGER**{x" if pl > character.current_pl else ""
        character.msg(f"[{target.name}]: {pl:,.0f} PL ({status}) {danger}")
```

---

### 7. Training Partners

**Concept:** NPCs that spar with you for experience.

**Types:**
| NPC | Location | PL | XP Rate |
|-----|----------|-----|---------|
| Master Roshi | Kame House | 1,000 | 1x |
| King Kai | Other World | 5,000 | 1.5x |
| Guru | Planet Namek | 10,000 | 2x |
| Whis | Beerus's Planet | 50,000 | 3x |

**Mechanics:**
- `train with <npc>` to start
- Spar for set duration (5-30 min)
- Bonus XP for training
- Can learn new moves from trainers

---

### 8. Aura Effects

**Concept:** Visual aura display for transformed players.

**Implementation (Evennia web client):**
```python
def get_aura_html(character):
    if character.trans_current == "ssj1":
        return '<span class="aura-ssj1">✨</span>'
    elif character.trans_current == "ssj2":
        return '<span class="aura-ssj2">⚡</span>'
    # etc.
```

**ANSI version:**
```python
def get_aura_string(character):
    if character.trans_current == "ssj1":
        return "{Ygolden aura{x"
    elif character.trans_current == "ssj2":
        return "{Yelectric aura{x"
```

---

### 9. Time Skip / Ki Sense

**Concept:** DBZ-style mobility skills.

**Commands:**
- `timeskip` - Teleport behind target (requires high PL)
- `kisense` - See hidden enemies
- `teleport` - Instant travel to saved location

**Mechanics:**
```python
def do_timeskip(character, target):
    if character.max_pl < target.max_pl * 0.5:
        character.msg("They're too fast!")
        return
    
    # Swap positions
    old_room = character.location
    target_room = target.location
    character.move_to(target_room)
    target.move_to(old_room)
    character.msg("You skip through time!")
```

---

### 10. Planet Cracker

**Concept:** Ultra-rare ultimate attack that can destroy areas.

**Mechanics:**
- Only available at very high PL (1,000,000+)
- 10% chance to learn
- Destroys current room/area
- Everyone in room takes massive damage
- Only usable once per RL day

**Risk:** If you miss/they survive, you're exhausted for 1 hour

---

### 11. Additional Race Transformations

| Race | Transform 1 | Transform 2 | Transform 3 | Transform 4 |
|------|-------------|-------------|-------------|-------------|
| Human | None | Kaioken | - | - |
| Saiyan | SSJ1 | SSJ2 | SSJ3 | SSJ4/5 |
| Half-Saiyan | SSJ1 | SSJ2 | - | - |
| Namekian | Hyper Namek | Super Namek | Fuse | - |
| Icer | Form 2 | Form 3 | Form 4 | Form 5 |
| Bio-Android | Bio-2 | Bio-3 | Bio-4 | Bio-5 |
| Majin | Buu Form | - | - | - |

---

### 12. Quest System

**Quest Types:**
- **Kill Quests** - Defeat X enemies
- **Collect Quests** - Find X items
- **Delivery Quests** - Take item to NPC
- **Training Quests** - Reach PL threshold

**Quest Rewards:**
- XP
- Gold (Zenni)
- Items
- Skill unlocks

---

### 13. Skill Trees

**Combat Skills:**
- Melee (basic attacks)
- Energy Attacks (ki blasts)
- Beam Attacks (Kamehameha, Galick Gun)
- Physical (kick, punch)

**Utility Skills:**
- Flight
- Sensing
- Teleportation
- Meditation

**Transformation Skills:**
- SSJ1-5 mastery
- Kaioken mastery
- Fusion techniques

---

### 14. Guild/Team System

**Features:**
- Form a team (max 5 players)
- Team attacks (combined beams)
- Shared XP from kills
- Team chat
- Team vs team battles

---

### 15. Tournament Arena

**Events:**
- Weekly tournaments
- 1v1, 2v2, 3v3
- Prize: Zeni, skill unlocks, titles
- Spectator mode

---

## Data Models (Evennia)

### Character (Player)
```python
class PlayerCharacter(Typeclass):
    # Stats
    max_pl = IntegerField(default=1000)  # Powerlevel
    current_pl = IntegerField(default=250)  # Current PL (percentage of max)
    max_ki = IntegerField(default=100)
    current_ki = IntegerField(default=100)
    max_hp = IntegerField(default=100)
    current_hp = IntegerField(default=100)
    
    # Attributes
    strength = IntegerField(default=10)
    intelligence = IntegerField(default=10)
    willpower = IntegerField(default=10)
    dexterity = IntegerField(default=10)
    charisma = IntegerField(default=10)
    
    # Race
    race = StringField(default="human")
    
    # Transformations
    trans_mastery = ListField(default=[0, 0, 0, 0, 0])
    trans_start_time = IntegerField(default=0)
    trans_current = StringField(default="")
    kaioken_multiplier = IntegerField(default=1)
    
    # Special
    namek_fused = BooleanField(default=False)
    fusion_count = IntegerField(default=0)
    dragon_balls = ListField(default=[])  # List of collected balls
    
    # Cooldowns
    planet_cracker_available = BooleanField(default=True)
    ultra_instinct_cooldown = IntegerField(default=0)
```

---

## Commands Reference

### Combat
- `attack <target>` - Basic attack
- `energy <target>` - Energy blast
- `beam <target>` - Beam struggle init
- `push` - Push in beam clash
- `flurry` - Flurry attack
- `spiritbomb` - Charge massive AoE

### Transformations
- `ssj1` through `ssj5` - Transform
- `kaioken` - Activate Kaioken
- `revert` - Revert to normal

### Utility
- `power <percent>` - Set power level %
- `charge` - Charge ki
- `meditate` - Regain ki
- `sense` - Sense powerlevels
- `scan` - Same as sense
- `map` - Show area map
- `summon_shenron` - If you have all 7 balls

---

## Visuals & Assets

### Logo
- Location: `assets/dbforgedfullcoloralpha.png`

### Color Scheme (ANSI)
| Color | Code | Use |
|-------|------|-----|
| Red | {R | Danger, attacks |
| Yellow | {Y | Golden aura, warnings |
| Blue | {B | Ki energy |
| Green | {G | Healing, success |
| White | {W | Default text |
| Cyan | {C | SSJ5 aura |

### Sector Symbols (Automap)
- `I` - Inside (brown)
- `C` - City (white)
- `.` - Field (green)
- `F` - Forest (dark green)
- `H` - Hills (light gray)
- `M` - Mountain (white)
- `~` - Water (blue)

---

## Evennia-Specific Notes

### Advantages Over ROM
1. **Python** - Easier to extend and modify
2. **Web Client** - Built-in, easier to add images
3. **Typeclasses** - Clean data model
4. **Commands** - Simpler command handler
5. **Unicode** - Full emoji support for DBZ-style text

### Porting Effort
- All game logic can be ported (concepts translate)
- Data structures need rewriting (C structs → Python classes)
- Commands need rewriting (C functions → Evennia commands)

---

## File Structure (Proposed)

```
mygame/
├── typeclasses/
│   ├── character.py      # Player character
│   ├── room.py           # Room
│   ├── object.py         # Objects/items (Senzu beans, Dragon Balls)
│   ├── exit.py           # Exits
│   └── npc.py            # NPCs (training partners, villains)
├── commands/
│   ├── combat.py         # Attack, beam, push, flurry, spiritbomb
│   ├── transform.py      # SSJ commands, kaioken, revert
│   ├── general.py        # Movement, look, map, sense
│   └── social.py         # Emotes, etc.
├── world/
│   ├── transforms.py     # Transformation data & logic
│   ├── skills.py         # Skill definitions
│   ├── areas.py          # Area definitions
│   ├── dragonballs.py    # Dragon Ball spawns & wishes
│   └── quests.py         # Quest definitions
├── scripts/
│   ├── combat_handler.py # Combat loop
│   ├── beam_clash.py     # Beam clash logic
│   └── transform_timer.py # Transformation timeout/drain
└── web/
    └── templates/
        └── character/
            └── sheet.html  # Character sheet with stats
```

---

## Summary

This document contains EVERY feature for DB Arena - implemented and planned:

**Implemented:**
1. Transformation Mastery (hold longer with practice)
2. Powerlevel Drain (transformations exhaust you)
3. Kaioken Hold-Down (risk/reward mechanic)
4. Namekian Fusion (permanent boost)
5. Beam Clash (push to win)
6. Flurry Attacks
7. Automap

**Planned:**
1. DBZ Login Greeting
2. Senzu Bean System
3. Spirit Bomb
4. Transform on Death (Ultra Instinct)
5. Dragon Ball Collection
6. Energy Sensing
7. Training Partners
8. Aura Effects
9. Time Skip / Ki Sense
10. Planet Cracker
11. Additional Race Transformations
12. Quest System
13. Skill Trees
14. Guild/Team System
15. Tournament Arena

Ready to implement in Evennia!

---

## Feature Priority List

| # | Feature | Priority |
|---|---------|----------|
| 1 | DBZ Login Greeting | HIGH |
| 2 | Senzu Bean System | MEDIUM |
| 3 | Spirit Bomb | MEDIUM |
| 4 | Aura Effects | LOW |
| 5 | Training Partners | MEDIUM |
| 6 | Planet Cracker | LOW |
| 7 | Transform on Death | HIGH |
| 8 | Energy Sensing | MEDIUM |
| 9 | Time Skip/Ki Sense | MEDIUM |
| 10 | Dragon Ball Collection | HIGH |
