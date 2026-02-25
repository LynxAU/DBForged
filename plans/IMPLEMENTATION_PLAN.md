# DBForged Implementation Plan - Updated
## Comprehensive Development Roadmap (Aligned with Design Docs)

---

## Executive Summary

This document outlines the complete implementation plan for DBForged, a Dragon Ball Super-themed MUD. The codebase already contains substantial foundation - data-driven technique/forms registries, combat handler, character creation, and a custom web client. The immediate focus is **wiring systems together**, **filling content gaps**, and **polishing core gameplay**.

This plan aligns with the design docs in `C:\Games\Dev\DBForged\Agents\MiniMax\docs`

---

## Current State

### ✅ Already Complete (Phases 1-4)

| Phase | Feature | Status |
|-------|---------|--------|
| Phase 1 | Techniques deal damage in combat | ✅ Done |
| Phase 2 | Transformations work (gated by progression) | ✅ Done |
| Phase 3 | Training system (learn from Master Rokan) | ✅ Done |
| Phase 4 | Combat HUD command (`hud`) | ✅ Done |

---

## Phase 5: Flight & Movement System

**Source**: COMBAT_SYSTEM_EXPANSION.md (Priority #1)

### 5.1 Flight Command
- `fly` - Take to the skies
- `fly north/south/east/west` - Fly in direction
- `land` - Return to ground
- Flight states: Ground → Levitate → Flying → Super Speed

### 5.2 Fast Travel System
- `teleport save` - Save current location
- `teleport recall` - Return to saved spot
- Unlock fast travel points based on PL

### 5.3 Ki Sense / Scan
- `sense` - Detect nearby power levels
- `scan` - Show enemy PL and hidden characters
- Saiyan passive detection bonus

---

## Phase 6: Guard & Combat Defense

**Source**: COMBAT_SYSTEM_EXPANSION.md

### 6.1 Guard/Block System
- `guard` / `block` - Enter guard stance (50% damage reduction)
- Guard break - Enemy guard breaks after 5 hits
- Perfect block - Time it right = 0 damage

### 6.2 Counter Attack
- `counter` - Counter enemy attack (1 sec window)
- Counter success = 150% damage + stun

### 6.3 Rage Mode (Auto-trigger)
- Auto-activates when HP < 20%
- +50% damage for 10 seconds
- Cooldown: 5 minutes

### 6.4 Limit Break
- Manual activation when HP < 30%
- Push beyond max PL by 50% for 30 seconds
- Exhaustion after use

---

## Phase 7: Transformation Depth

**Source**: EVENNIA_DBZ_DESIGN.md

### 7.1 Transformation Mastery
- Duration increases with use (60→260 seconds)
- Mastery increases 1% every 10 seconds while transformed
- Warnings at 80% ("aura flickers") and 90% ("slipping!")

### 7.2 Power Drain System
- SSJ1: 1% max PL per minute
- SSJ2: 2% max PL per minute
- SSJ3: 3% max PL per minute
- Warning at 20% PL, auto-revert at 10%

### 7.3 Kaioken System
- Hold kaioken for increasing multiplier (x2-x20)
- Self-damage increases each second
- Warning at 5+ seconds ("body straining!")

### 7.4 Transform on Death (Ultra Instinct)
- 20% chance when HP drops below 10%
- Auto-triggers highest available transformation
- Brief invulnerability (1-2 seconds)
- After effect: collapse to 50% HP

---

## Phase 8: Racial Abilities

**Source**: RACIAL_ABILITIES_DESIGN.md

### 8.1 Saiyan - Zenkai Boost
- Activate: drop below 20% HP, then heal above 80%
- +5% base PL increase (plus bonuses)
- Cooldown: 24 hours
- Max 10 stacks lifetime

### 8.2 Saiyan - Great Ape
- Requires full moon exposure (10 seconds)
- Base PL × 10 multiplier
- Cannot use techniques (AI controls)
- 30 second weakness after: -50% PL

### 8.3 Namekian - Regeneration
- Passive: 1% max HP every 10 seconds
- Active: Regeneration Burst (25% HP over 10 sec)
- Cannot use during combat

### 8.4 Android - Unlimited Energy
- No Ki stat (use Energy instead)
- Energy regenerates at constant rate
- Photon Flash (free)
- Self-Repair (50% HP over 30 sec)

---

## Phase 9: Combo System

**Source**: COMBAT_SYSTEM_EXPANSION.md

### 9.1 Combo Mechanics
- Attack → Attack → Kick → Special
- Each hit adds +25% damage multiplier
- At 4th hit, can trigger FINISHER
- Combo window: 1.5 seconds

### 9.2 Combo Benefits
- Damage bonus: 1.0x → 1.5x → 2.0x → 2.5x
- Stun buildup: After 4 hits, enemy stunned 1 sec
- Ki buildup: +10% per hit
- Finisher: 5th hit = automatic crit +100%

### 9.3 Combo Counters
- Guard negates combo
- Sidestep dodges mid-combo
- Counter Attack during their attack
- Status effects break combos

---

## Phase 10: Content Expansion

**Source**: Implementation Plan + Design Docs

### 10.1 World Building
- Mountains / Lookout
- Desert / HTC area
- Namek (unlockable)
- Space (unlockable)

### 10.2 NPC Population
- Master Roshi (Kame House) - Kamehameha
- Tien (Forest) - Solar Flare
- King Kai (Otherworld) - Spirit Bomb, IT
- Vegeta (Capsule Corp) - Final Flash, Galick Gun
- Guru (Namek) - Regeneration
- Whis (Beerus Planet) - Training bonus

### 10.3 Quest System
- Dragon Ball collection (7 balls)
- Shenron wishes
- Technique unlock quests

---

## Phase 11: Items & Economy

**Source**: EVENNIA_DBZ_DESIGN.md

### 11.1 Senzu Bean System
- Senzu Bean: Full HP/KI (Very Rare)
- Sacred Water: Full HP (Rare)
- Meat: 50% HP (Uncommon)

### 11.2 Dragon Balls
- 7 unique Dragon Balls (numbered)
- `summon_shenron` when all 7 collected
- 3 wishes available:
  1. Power Boost: +50% max PL
  2. Stat Boost: +20 to all stats
  3. Transformation Unlock

### 11.3 Spirit Bomb
- `spiritbomb` or `sb charge`
- Charge 10-30 seconds
- Massive AoE damage
- Can be interrupted

---

## Phase 12: Advanced Features

### 12.1 Technique Mastery System
- Techniques improve with use
- Mastery unlocks variations (Super Kamehameha)

### 12.2 LSSJ (Legendary Super Saiyan)
- Hidden transformation for Saibamen/Saiyans
- Unlock: defeat certain enemies
- Berserk mode mechanics

### 12.3 Tournament / Arena
- Queue system
- Matchmaking by PL
- Rank tracking

---

## Phase 13: Social Features

**Source**: ROADMAP.md

### 13.1 Player Trading
- Secure trade between players

### 13.2 Friends List
- Add players, see online status

### 13.3 Global Chat
- Trade, LFG, OOC channels

### 13.4 Mail System
- Send items/zeni to offline players

---

## Phase 14: Web Client Polish

### 14.1 Enhanced HUD
- Health/Ki bars
- Technique cooldowns
- Transform state display
- Mini-map

### 14.2 Combat Visualization
- Beam animations
- Explosion effects
- Aura rendering
- Character sprites

---

## Success Criteria

### MVP (Complete ✅)
- [x] Techniques deal damage in combat
- [x] Transformations work
- [x] Training system works
- [x] 3+ NPCs
- [x] 10+ techniques usable
- [x] 4+ transformations

### Alpha (In Progress)
- [ ] Flight system
- [ ] Guard/Block
- [ ] 20+ techniques
- [ ] 10+ transformations
- [ ] 3+ areas
- [ ] Quest system

### Beta (Planned)
- [ ] Full racial abilities
- [ ] Combo system
- [ ] Dragon Balls
- [ ] Tournament
- [ ] Full web HUD

---

## Next Action

Choose a feature to implement:
1. **Flight System** - Phase 5
2. **Guard/Block** - Phase 6
3. **Racial Abilities** - Phase 8
4. **More NPCs/Areas** - Phase 10
