# DBForged React Client - Full Build Plan

## Overview
Build all 5 client systems for a complete game experience.

## Systems to Build

### 1. Full Game UI Overhaul
- Character Creation Wizard
  - Race selection (with descriptions)
  - Name validation
  - Stat distribution preview
- Settings Panel
  - Graphics quality
  - Audio volume
  - Keybindings
- Full Inventory Management
  - Drag and drop
  - Item tooltips
  - Equipment slots

### 2. Real-time Combat HUD
- Attack buttons with cooldowns
- Technique hotbar (1-9 keys)
- Floating damage numbers
- Enemy combo counter
- Parry/guard indicators
- Charge bar visualization

### 3. World Exploration System
- Full-screen map
- Player position marker
- Zoom/pan controls
- NPC markers (quest, shop, trainer)
- Zone boundaries
- Fast travel points

### 4. Social & Community Hub
- Friend list with status
- Guild interface (roster, bank)
- In-game mail
- Chat channels
- Player profiles

### 5. Audio & Visual Polish
- Sound effect system
- Background music
- Particle effects
- Screen effects (shake, flash)
- Animation controller

## File Structure
```
web/client/src/
├── components/
│   ├── Combat/          # Combat HUD
│   ├── Map/            # World map
│   ├── Social/         # Friends, guild, mail
│   ├── Audio/          # Sound manager
│   └── Effects/        # Particles, screens
├── services/
│   └── audio.js        # Web Audio API
└── ...
```

## Priority
1. Combat HUD (most impactful)
2. Map System
3. Social Hub
4. UI Overhaul
5. Audio/Effects
