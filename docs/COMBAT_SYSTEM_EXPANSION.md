# DBForged Combat & Training Expansion

## A) COMBO ATTACK SYSTEM

### How It Would Work

The combo system lets players chain attacks together for bonus damage and effects. Think DBZ fighting games.

**Basic Structure:**
```
Attack → Attack → Kick → Special Move
  (50%)   (75%)   (100%)  (Special!)
```

**Mechanics:**
- Each attack has a "combo window" (1.5 seconds to continue)
- Chain builds up multiplier: 1.0x → 1.5x → 2.0x → 2.5x
- At 4th hit, can trigger FINISHER (special attack)
- Chain breaks if you miss OR enemy guards

### What's The Benefit?

| Benefit | Description |
|---------|-------------|
| **Damage Bonus** | Each consecutive hit adds +25% damage |
| **Stun Buildup** | After 4 hits, enemy is stunned for 1 second |
| **Ki Buildup** | Each hit builds ki faster (+10% per hit) |
| **Finisher Bonus** | 5th hit is automatic crit +100% damage |
| **Style Points** | Show off with long combos |

### What's The Negative?

| Negative | Description |
|----------|-------------|
| **Risk/Reward** | Longer combo = more damage BUT easier to counter |
| **Guard Break** | Enemy can GUARD to negate combo |
| **Counter Window** | If you miss, enemy has 1 second to counter |
| **Ki Drain** | Finishers cost extra ki |

### Is There A Counter?

| Counter | How It Works |
|---------|---------------|
| **Guard** | Holding defense negates combo, builds guard meter |
| **Sidestep** | Time it right to dodge mid-combo |
| **Counter Attack** | Hit enemy during their attack animation |
| **Interrupt** | Use technique during their combo |
| **Status Effects** | Stun, paralysis breaks combos |

---

## B) KI SENSE TRAINING

### What Does This Look Like?

Training minigame to control your ki output. Like DBZ training montages.

**Mechanics:**
```
1. Stand in training zone
2. Prompt shows: "Hold your ki at 5000-5500!"
3. You type: "charge 50" (or use slider)
4. Timer counts down 10 seconds
5. Accuracy = XP reward
```

**Training Zones:**
- **Basic Sensor**: 1000-5000 range
- **Advanced Sensor**: 10000-50000 range  
- **Master Sensor**: 100000+ range

### What's The Benefit?

| Benefit | Description |
|---------|-------------|
| **Technique Mastery** | Certain techs require ki control |
| **Meditation Bonus** | +5% PL gain if ki control > 80% |
| **Efficiency** | Better ki control = less waste |
| **Hidden Enemies** | High sense = can detect concealed foes |

### How Does Ki Sense Work In Real Gameplay?

| Use Case | Description |
|----------|-------------|
| **Scan Command** | Shows enemy PL (already exists) |
| **Sense Hidden** | Detect invisible/enemy in room |
| **Ki Control** | Technique efficiency |
| ** meditation** | Passive XP boost |

---

## C) FLIGHT SYSTEM + FAST TRAVEL

This is a MUST per user request. Here's how it works:

### Flight System

**Emote Flight:**
```
fly [direction] - Travel to adjacent room with flying animation
fly north      - "You soar into the sky, flying north..."
```

**Flight States:**
- **Ground**: Normal movement
- **Levitate**: Can move over water/gaps
- **Flying**: Full flight, moves 2x speed
- **Super Speed**: 3x speed, can fly over obstacles

**Flight Commands:**
```
fly              - Take to the skies
land             - Return to ground
flight speed    - Check current speed
```

### Fast Travel System

**Teleport Network (Already Have):**
- `teleport save` - Save location
- `teleport recall` - Return to saved spot (once per day)

**Flight Emotes:**
```
fly to city     - Fast travel to city (if unlocked)
fly home        - Return to home
```

**Fast Travel Points:**
| Location | Unlock | Cost |
|----------|--------|------|
| Kame House | Start | Free |
| Capsule Corp | PL 5000 | Free |
| Lookout | PL 10000 | Free |
| Planet Vegeta | Faction | Free |
| Other World | Quest | Quest |

---

## D) MENTOR SYSTEM

Iconic abilities can ONLY be taught from their master!

### How It Works

**Learn from the Best:**
| Technique | Mentor | Location | Requirements |
|-----------|--------|----------|--------------|
| Kamehameha | Master Roshi | Kame House | PL 1000, Kaiō Trial |
| Spirit Bomb | King Kai | Otherworld | PL 50000,完成 |
| Solar Flare | Tien | Forest | PL 5000 |
| Instant Transmission | King Kai | Otherworld | PL 100000 |
| Final Flash | Vegeta | Capsule Corp | PL 75000, Saiyan |
| Galick Gun | Vegeta | Capsule Corp | PL 50000, Saiyan |
| Death Beam | Frieza (villain) | Space | PL 80000, Evil |
| Regeneration | Guru | Namek | PL 30000, Namekian |

**Teaching Process:**
```
1. Find mentor NPC
2. train <technique> - Shows requirements
3. Meet requirements (PL, quest, etc)
4. Pay training fee (zeni)
5. Learn technique
```

**Mentor Ranks:**
- **Apprentice**: Can learn 1 technique
- **Disciple**: Can learn 3 techniques  
- **Master**: Can learn all + teach others

---

## E) COMBAT UPGRADES (Fun + Engaging!)

### Guard/Block System

```
guard        - Enter guard stance (reduces dmg by 50%)
guard break - Enemy guard breaks after 5 hits
perfect block - Time it right = 0 damage
```

### Counter Attack

```
counter     - Counter enemy attack (1 sec window after their attack)
counter success = 150% damage + stun
```

### Rage Mode (Auto-trigger)

```
Auto-activates when HP < 20%
+50% damage for 10 seconds
Ends when HP > 50%
Cooldown: 5 minutes
```

### Limit Break

```
Manual activation when HP < 30%
Push beyond max PL by 50% for 30 seconds
Costs: HP drain, then exhausts for 2 minutes
```

---

## IMPLEMENTATION ORDER

| Priority | Feature | Why |
|----------|---------|-----|
| 1 | Flight System | Must have |
| 2 | Fast Travel | Convenience |
| 3 | Mentor System | Core progression |
| 4 | Friends List | Social must |
| 5 | Ki Sense Training | Training depth |
| 6 | Combo System | Combat fun |
| 7 | Guard/Block | Combat depth |
| 8 | Mail System | Nice to have |
| 9 | Ultimate Tower | Endgame |
| 10 | Titles/Costumes | Expression |

---

*Let me know which to implement first!* 🚀
