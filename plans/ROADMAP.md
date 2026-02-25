# DBForged Roadmap - Priority Next Steps

## Current State Analysis

### ✅ What's Already Implemented

| System | Status | Details |
|--------|--------|---------|
| **Races** | Complete | 11 races with 3 racial traits each |
| **Techniques** | Data Ready | 50+ techniques defined |
| **Forms** | Complete | Full transformation system with mastery, drain, strain |
| **Combat Engine** | Working | Handler script, engage/disengage, beam system, form drain |
| **Power Level** | Implemented | PL calculation with gap effects |
| **Character Creation** | Working | EvMenu-based with race/appearance selection |
| **Web Client** | Custom | Canvas-based with sprite system |
| **Transformation Depth** | Complete | Kaioken (hold-to-charge), Ultra Instinct |
| **Racial Abilities** | Complete | Zenkai, Great Ape, Regeneration, Android Heat |

---

## Completed Phases

### Phase 7: Transformation Depth ✅
- Kaioken hold-to-charge system (x3/x10/x20 multipliers)
- Ultra Instinct forms (Sign, Mastered, Breached)
- Form drain tick integrated into combat loop
- Body strain accumulation system
- Entity delta enhanced for web client
- `transform status` command

### Phase 8: Racial Abilities ✅
- **Zenkai Boost** - Saiyans get temporary PL boost after defeat recovery
- **Great Ape** - Saiyan tail transformation (PL +35%, requires moon/blutz)
- **Golden Great Ape** - Great Ape + Super Saiyan (PL +55%)
- **Regeneration** - Namekian/Majin/Biodroid get bonus HP on recovery
- **Android Heat** - Heat meter builds with tech use, overheats at 100%

### Limb System ✅
- **Limb States** - intact, damaged, broken, lost
- **Combat Damage** - 8% chance on heavy hits (>10 damage)
- **Namekian Regen** - Instant limb regeneration
- **Majin/Biodroid** - Slow limb regeneration
- **Senzu Bean** - Full heal + limb repair (from Baba)
- **Healing Chamber** - Location-based gradual healing
- **Web Client** - Limbs shown in entity delta

### Phase 9: Combo System ✅
- **Combo Tracking** - Consecutive hits within 3s window
- **Combo Damage Bonus** - +5% per hit, max 50%
- **Combo Milestones** - x5, x10, x15 announcements
- **Combo Break** - Combo resets after 3s without hit
- **Limb Penalties** - Broken/lost limbs reduce damage 30% each
- **Technique Blocking** - Can't use kicks/punches with broken limbs
- **Web Client** - Combo count in entity delta

### Phase 10: Content Expansion ✅
- **Capsule Corp** - Main Entrance, Research Lab, Training Hall, Rooftop
- **King Kai's Planet** - Main planet, Training Grounds
- **Mount Paozu** - Forest Path, Base Camp, House, Spirit Bomb Cliff
- **Red Ribbon Army** - Gate, Lobby, Armory, Lab, Commander's Office
- **New Quests** - Spirit Bomb trial, Galick Gun mastery, Special Beam mastery
- **New Techniques** - Spirit Bomb (ultimate charging technique)
- **NPC Updates** - King Kai (Kaioken), Whis (Ultra Instinct), Baba (Senzu)

---

## What's Left

| Phase | Description |
|-------|-------------|
| Phase 9 | Combo System |
| Phase 10 | Content Expansion (more areas, NPCs, quests) |
| Phase 11 | Items & Economy (Senzu beans, Dragon balls, spirit bomb) |
| Phase 12 | Advanced Features |
| Phase 13 | Social Features |
| Phase 14 | Web Client Polish |

What would you like to tackle?