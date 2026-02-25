# DBForged Client - Art Assets Requirements

## Overview
This document outlines all art assets needed to complete the DBForged React client.

---

## 1. Character Sprites

### Base Humanoid (Required)
- **Format**: PNG with transparency
- **Sizes**: 32x32, 64x64, 128x128 (for different zoom levels)
- **Animations needed**:
  - Idle (4-8 frames, loop)
  - Walk (8 frames)
  - Attack (6-8 frames)
  - Hit/stagger (3 frames)
  - Block/guard (1 frame)
  - Charge up (6-8 frames)
  - Transform (10-15 frames)

### Race-Specific Sprites
| Race | Sprite ID | Special Features |
|------|-----------|------------------|
| Saiyan | sprite_saiyan | Tail animation |
| Half-Breed | sprite_hybrid | Tail, potential aura |
| Namekian | sprite_namekian | Green skin tone |
| Human | sprite_human | Standard |
| Android | sprite_android | Mechanical design |
| Majin | sprite_majin | Pink/unique shape |
| Frieza Race | sprite_frieza | Tail, horns |
| Biodroid | sprite_biodroid | Cybernetic parts |

### Transformations
| Form | Sprite ID | PL Multiplier | Notes |
|------|-----------|----------------|-------|
| Super Saiyan | form_super_saiyan | 50x | Yellow hair, aura |
| Super Saiyan 2 | form_super_saiyan_2 | 100x | Spikier, lightning |
| Super Saiyan 3 | form_super_saiyan_3 | 400x | Long hair, no eyebrows |
| Super Saiyan God | form_super_saiyan_god | 1000x | Red hair, divine aura |
| Super Saiyan Blue | form_super_saiyan_blue | 10000x | Blue hair, god ki |
| Ultra Instinct | form_ultra_instinct | 100000x | Silver hair, unique aura |

---

## 2. Ki Blasts & Techniques

### Beam Attacks
| Technique | Sprite ID | Color | Size |
|-----------|-----------|-------|------|
| Kamehameha | beam_kamehameha | Blue | Large |
| Gallic Gun | beam_gallic_gun | Purple | Large |
| Final Flash | beam_final_flash | Yellow | Large |
| Masenko | beam_masenko | Yellow | Medium |
| Destructo Disc | beam_destructo_disc | Blue | Disc shape |
| Solar Flare | effect_solar_flare | White flash | Screen-wide |

### Energy Balls
| Technique | Sprite ID | Color |
|-----------|-----------|-------|
| Spirit Bomb | projectile_spirit_bomb | Blue/White |
| Death Ball | projectile_death_ball | Orange |
| Hakai | projectile_hakai | Purple |

---

## 3. Backgrounds & Environments

### Tilesets (32x32 or 64x64)
| Zone | Tileset ID | Theme |
|------|-------------|-------|
| Plains | tileset_plains | Grass, flowers |
| Forest | tileset_forest | Trees, bushes |
| Mountain | tileset_mountain | Rocks, cliffs |
| City | tileset_city | Buildings, roads |
| Dojo | tileset_dojo | Training area |
| Tournament Arena | tileset_arena | Stadium |

### Background Images
| Location | Image ID | Size |
|----------|----------|------|
| Main Menu | bg_title | 1920x1080 |
| Loading Screen | bg_loading | 1920x1080 |
| Character Select | bg_character_select | 1920x1080 |

---

## 4. UI Elements

### Icons (64x64 recommended)
| Category | Icons Needed |
|----------|-------------|
| Inventory | sword, shield, potion, helmet, armor, boots, accessory |
| Techniques | energy, beam, buff, debuff, heal, transform |
| Quests | quest_available, quest_active, quest_complete |
| Status | buff_zenkai, buff_regen, buff_charge, debuff_poison |

### UI Components
- **Button sprites**: Normal, hover, pressed, disabled states
- **Panel backgrounds**: Glassmorphism overlays
- **Health/Ki bars**: Filled and empty versions
- **Mini-map tiles**: For world map

---

## 5. Particles & Effects

### Aura Effects (PNG sequences)
| Effect | Sprite ID | Frames | Notes |
|--------|-----------|--------|-------|
| Saiyan Aura | aura_saiyan | 8 | Orange/yellow flame |
| God Ki | aura_god_ki | 8 | Blue/purple divine |
| LSSJ Aura | aura_lssj | 12 | Green flame, larger |
| Charging | aura_charge | 6 | Energy gathering |

### Impact Effects
| Effect | Sprite ID | Frames |
|--------|-----------|--------|
| Hit Spark | impact_spark | 4 |
| Block Spark | impact_block | 3 |
| Ki Explosion | impact_ki | 8 |
| Transform Flash | impact_transform | 10 |

### Environmental
- **Weather**: Rain particles, snow particles
- **Ambient**: Floating dust, light rays

---

## 6. Audio Assets

### Sound Effects (Ogg/MP3 recommended)
| Category | Sounds Needed |
|----------|--------------|
| Combat | attack_whoosh, hit_impact, block_clang, charge_up |
| UI | button_click, menu_open, notification |
| Transformations | transform_shout, form_change |
| Techniques | beam_charge, beam_fire, explosion |
| Ambient | wind, birds, city_hum |

### Music
| Track | Purpose | Length |
|-------|---------|--------|
| main_theme | Title screen | 2-3 min loop |
| battle_theme | Combat | 1-2 min loop |
| peaceful | Exploring | 2-3 min loop |
| boss | World boss | 2-3 min loop |

---

## 7. File Naming Convention

```
assets/
├── sprites/
│   ├── characters/
│   │   ├── human_idle_01.png
│   │   ├── saiyan_idle_01.png
│   │   └── ...
│   ├── techniques/
│   │   ├── beam_kamehameha_01.png
│   │   └── ...
│   └── effects/
│       ├── aura_saiyan_01.png
│       └── ...
├── tilesets/
│   ├── plains_01.png
│   └── ...
├── ui/
│   ├── icons/
│   │   └── ...
│   └── panels/
│       └── ...
├── audio/
│   ├── sfx/
│   │   └── ...
│   └── music/
│       └── ...
└── backgrounds/
    └── ...
```

---

## Priority Order

### Phase 1 - Minimum Viable
1. Character sprites (idle, walk, attack)
2. Basic ki blast sprite
3. Simple hit effect
4. UI icons
5. Basic UI button states

### Phase 2 - Enhanced
1. All transformation sprites
2. All technique sprites
3. Full animation sets
4. Background tilesets
5. Music tracks

### Phase 3 - Polish
1. Particle effects
2. Aura animations
3. Weather effects
4. Advanced UI polish
5. Full sound design

---

## Current Assets

### Already Available
- Beam animations in `web/static/ui/animations/base_beam_row*`
- Logo in `web/static/ui/`

### Needs Replacement/Enhancement
- Character sprites - none currently
- UI icons - using emoji/placeholders
- Backgrounds - CSS gradients only

---

## Technical Notes

- **Preferred format**: PNG for sprites with transparency
- **Animation**: Sprite sheets preferred (horizontal strip)
- **Audio**: Ogg Vorbis (smaller than MP3, better compression)
- **Backgrounds**: WebP for photos, PNG for pixel art
- **Sprite size**: Keep under 512KB per file for fast loading
