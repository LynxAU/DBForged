# KAME ISLAND IMPLEMENTATION PLAN

## Project: Kame Island New Player Experience
**Goal**: Create an immersive tutorial area that makes new players feel like they've entered the Dragon Ball world

---

## 📋 OVERVIEW

Kame Island is the premier starting zone for new players - where they meet Master Roshi, encounter famous characters, and begin their journey. This should feel like stepping into the anime.

### Core Vision
- **Immediate engagement** - First 5 minutes should hook them
- **Famous encounters** - Meet actual DBZ characters
- **Progressive training** - Easy → Medium → Hard challenges
- **Story hook** - Make them want to come back

---

## 🎯 PHASE 1: INFRASTRUCTURE (Priority: HIGH)

### 1.1 Room System
```
Map Layout:
```
```
                    [Hidden Cave]
                         |
                    [Waterfall]
                         |
[Meditation] <-- [Forest Path] --> [Training Grounds]
                         |              (MK-1, MK-2 dummies)
                    [Cottage]
                   /         \
        [Vacation Cottage] [Cottage Grounds]
              (18+Marron)       (Krillin)
                         |
                    [Beach Shore]  ← START HERE
                    /          \
            [Roshi House]    [Dock]
                  |
          [Roshi Interior]
                /         \
        [Garden]      (secret path to waterfall)
```
- [ ] Create 12 unique rooms with DBZ-themed descriptions
- [ ] Connect all rooms with named exits (n/s/e/w/in/out)
- [ ] Mark Roshi House and Cottage as "safe" zones
- [ ] Add zone tags for Kame Island

### 1.2 NPC Framework
- [ ] Extend NPC typeclass to support `dialogue_options`
- [ ] Create simple keyword-based conversation system
- [ ] Add `talk <npc>` command to initiate dialogue
- [ ] Support for:
  - Greeting keywords
  - Topic responses
  - Quest offers

---

## 🐢 PHASE 2: MASTER ROSHI (Priority: HIGH)

### 2.1 Roshi NPC
- [ ] Create Master Roshi NPC at Roshi Interior
- **Stats**: Power Level ~180 (impressive but not intimidating)
- **Dialogue Topics**:
  - "training" → "I invented training! But let's see what you've got."
  - "kamehameha" → "I invented it 50 years ago. Want to learn?"
  - "history" → "Goku, Gohan, Piccolo... they all started here."
  - "vacation" → "Krillin and 18? They're on vacation. Good people."

### 2.2 Roshi Training Quest Line
**Quest 1: "The Turtle Hermit's Test"**
- **Objective**: Talk to Master Roshi
- **Reward**: Kamehameha technique
- **Dialogue**:
  ```
  Roshi: "You want to train? Hmm... let me see your potential."
  (scans you with his eye)
  Roshi: "Not bad! Alright, I'll teach you the basics."
  ★ You learned KAMEHAMEHA!
  ```

### 2.3 Training Grounds
- [ ] Add Training Dummy MK-1 (PL 45, won't fight back)
- [ ] Add Training Dummy MK-2 (PL 95, will spar)
- [ ] Create quest to defeat 3 dummies

---

## 👨‍👩‍👧 PHASE 3: KRILLIN & FAMILY (Priority: MEDIUM)

### 3.1 Krillin NPC
- [ ] Place at Cottage Grounds
- **Stats**: Power Level ~250
- **Dialogue**:
  - "vacation" → "18 needed a break. Best training grounds ever!"
  - "18" → "She could destroy me with one finger. That's why I married her!"
  - "goku" → "That guy never stops training. I'm happy taking it easy."

### 3.2 Android 18 NPC
- [ ] Place at Vacation Cottage (interior)
- **Stats**: Power Level ~350
- **Dialogue**:
  - "vacation" → "This island is peaceful."
  - "daughter" → "Marron? She's playing nearby. I just want her to have a normal life."
  - "power" → "My power? Let's just say I'm glad I'm on vacation."

### 3.3 Marron NPC
- [ ] Place at Cottage Grounds (wandering)
- **Stats**: Power Level 10 (just a kid!)
- **Dialogue**:
  - "play" → "Wanna play? Daddy says I'm gonna be super strong!"
  - "mom" → "Mommy is the prettiest! She can do ANYTHING!"
  - "dad" → "Daddy makes funny faces when he trains!"

### 3.4 Family Quests
**Quest 2: "Meet the Family"**
- [ ] Objective: Talk to all three family members
- [ ] Reward: 500zeni, "Friendly" reputation

---

## 🌴 PHASE 4: EXPLORATION (Priority: MEDIUM)

### 4.1 World-Building Rooms
- [ ] **Beach Shore**: Starting point, atmospheric
- [ ] **Forest Path**: Random encounters (monkey, boar)
- [ ] **Meditation Clearing**: Bonus ki control training
- [ ] **Waterfall**: Beautiful scenery, hidden cave entrance
- [ ] **Hidden Cave**: Advanced training area (PL 150+ enemies)
- [ ] **Dock**: Future content placeholder (boat trips)

### 4.2 Wildlife Encounters
- [ ] Wild Monkey (PL 35, aggressive)
- [ ] Wild Boar (PL 55, aggressive)
- [ ] Rare: Golden Monkey (PL 80, gives bonus!)

### 4.3 Exploration Quests
**Quest 3: "Island Explorer"**
- [ ] Objective: Visit 8 different locations on Kame Island
- [ ] Reward: "Explorer" title, 300zeni

---

## ⚔️ PHASE 5: COMBAT TUTORIAL (Priority: HIGH)

### 5.1 Progressive Combat
The player should fight in this order:

1. **Training Dummy MK-1** (PL 45) - Can't fight back
   - Teaches: `attack` command
   
2. **Training Dummy MK-2** (PL 95) - Will counter
   - Teaches: `guard`, `tech`
   
3. **Wild Monkey** (PL 35) - Fast, first real enemy
   - Teaches: Scanning, evading
   
4. **Wild Boar** (PL 55) - Tanky, teaches damage
   - First "real" fight

### 5.2 Tutorial Quest Chain
**Quest: "Basic Training"**
- Step 1: Defeat Training Dummy MK-1
- Step 2: Use a ki blast (unlock ki_blast if missing)
- Step 3: Defeat Training Dummy MK-2
- Step 4: Visit Meditation Clearing (+5 ki_control)
- Step 5: Report to Master Roshi
- **Reward**: Turtle School gi (cosmetic), +10% XP for 1 hour

---

## 💬 PHASE 6: DIALOGUE SYSTEM (Priority: MEDIUM)

### 6.1 Talk Command Enhancement
```
Current: talk <npc>
New: talk <npc> [about <topic>]

Example:
> talk roshi
Roshi looks up from his magazine. "Oh, a new student? What do you want?"

> talk roshi about training
Roshi grins. "Training? NOW we're talking! I've been training for 80 years!"

> talk krillin about 18
Krillin blushes. "She... she's the best! Don't tell her I said that!"
```

### 6.2 Dynamic Responses
- [ ] Support keyword matching (not exact phrases)
- [ ] Show available topics: `talk roshi` shows "Topics: training, kamehameha, history"
- [ ] Default responses for unknown topics

---

## 🎁 PHASE 7: NEW PLAYER FLOW (Priority: HIGH)

### 7.1 Ideal First Session (15-20 minutes)

```
[Connect] → [First Login Experience] → [Spawn at Beach]

↓

1. See Kame Island intro (automatic)
2. Notice Master Roshi's house (north)
3. Go to Training Grounds (south)
4. Fight Training Dummy (easy win!)
5. Feel powerful! "I can do this!"
6. Meet Master Roshi (enter house)
7. Get Kamehameha quest
8. Complete training quest
9. LEARN KAMEHAMEHA! ★★★
10. Feel AMAZING!
11. Explore island
12. Meet Krillin's family
13. Done for now - but MUST come back!

Result: Hooked player who wants to get stronger!
```

### 7.2 Spawn Point Integration
- [ ] Make Kame Island Beach the new character spawn
- [ ] OR: Add fast travel from Earth Plains to Kame Island
- [ ] Add signpost/boat at Earth: Plains that leads to Kame Island

---

## 🎨 PHASE 8: ATMOSPHERE & FLAVOR (Priority: LOW)

### 8.1 Descriptive Text
Every room should have:
- Sensory details (sounds, smells, temperature)
- Lore connections ("Goku trained here!")
- Visual cues for where to go next
- Background DBZ references

### 8.2 Ambient Messages
- [ ] Random messages in rooms (every 30 seconds)
- Example: "A turtle slowly crawls across the sand."
- Example: "You hear the distant crash of waves."
- Example: "Master Roshi's voice echoes from inside the house..."

### 8.3 Weather/Day Cycle
- [ ] Basic: Different descriptions based on time
- [ ] Sunset: "The sky turns orange as the sun sets over the ocean."
- [ ] Night: "Stars blanket the sky. The ocean glows with moonlight."

---

## 📦 DELIVERABLES CHECKLIST

### Required for MVP
- [ ] 12 connected rooms
- [ ] Master Roshi with Kamehameha quest
- [ ] Krillin, Android 18, Marron NPCs
- [ ] 2 training dummies with progressive difficulty
- [ ] Basic dialogue system
- [ ] Spawn point or fast travel

### Polish
- [ ] Exploration quests
- [ ] Better descriptions
- [ ] Ambient messages
- [ ] Family quest line

---

## ⏱️ ESTIMATED TIME

| Phase | Effort | Notes |
|-------|--------|-------|
| Phase 1 | 2 hours | Infrastructure & connections |
| Phase 2 | 1 hour | Roshi & training |
| Phase 3 | 1 hour | Family NPCs |
| Phase 4 | 1 hour | Exploration areas |
| Phase 5 | 1 hour | Combat tutorial |
| Phase 6 | 1 hour | Dialogue system |
| Phase 7 | 30 min | Flow integration |
| Phase 8 | 30 min | Atmosphere |

**Total: ~8 hours for full implementation**

---

## 🚀 START HERE

To begin implementation, let's start with **Phase 1**:
1. Create the room connections (just rooms and exits, no NPCs)
2. Test the map is navigable
3. Then add NPCs one by one

**Should I start building Phase 1 now?**
