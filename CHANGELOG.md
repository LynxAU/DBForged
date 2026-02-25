# 🐉 DBForged Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-02-25

### 🚀 Major Features

#### React Web Client Launch
- **Complete UI Overhaul** - Migrated from vanilla JavaScript to React + Vite
- **Modern Component Architecture**:
  - Login screen with character art (Goku & Vegeta)
  - Full character creation wizard
  - Real-time game canvas with sprite rendering
  - Glassmorphism UI design

#### Multi-WebSocket Architecture ([`dbforged.js`](web/client/src/services/dbforged.js))
- **4 Dedicated WebSocket Connections**:
  - `/ws/game` (4001) - Commands & text output
  - `/ws/combat` (4002) - Real-time combat state
  - `/ws/world` (4003) - Map & entity updates
  - `/ws/chat` (4004) - Channels & social
- **Advanced Connection Features**:
  - Exponential backoff with jitter (caps at 30s)
  - Outbound message queue (max 100 frames replayed on reconnect)
  - Application-level heartbeat (ping every 30s, pong timeout 10s)
  - Connection timeout (10s)
  - Clean manual disconnect

#### Login & Character Creation
- **[`Login.jsx`](web/client/src/components/Login/Login.jsx)** - Beautiful login screen featuring:
  - Animated background with floating ki orbs
  - Character art (Goku & Vegeta) flanking the panel
  - Server connection status indicator
  - Account login with "Ki Signature" password field
  - New account creation flow
  
- **[`CharacterCreator.jsx`](web/client/src/components/Login/CharacterCreator.jsx)** - Complete character creation wizard:
  - Race selection with detailed descriptions
  - Name validation and preview
  - Visual character art display via [`CharacterArt.jsx`](web/client/src/components/Login/CharacterArt.jsx)
  - Appearance customization

#### Game Canvas Rendering ([`GameCanvas.jsx`](web/client/src/components/GameCanvas/GameCanvas.jsx))
- **Sprite-Based Rendering**:
  - Loads sprites from `/static/ui/` directory
  - Animated sprite sheets with multiple frames
  - Technique/effect animations (Kamehameha, etc.)

- **Tile-Based World** - Multiple location themes:
  - **Kame Island**: Beach, Sand, Water, Grass areas
  - **Capsule Corp**: Concrete, Lab, Metal interiors
  - **King Kai's Planet**: Alien grass training grounds
  - **Mount Paozu**: Forest, Dirt, Spirit Bomb Cliff
  - **West City**, **North City**, **Rosato River**, **Janemba Portal**, **Hell**, **Hyperbolic Time Chamber**

#### Combat System
- **[`CombatHUD.jsx`](web/client/src/components/Combat/CombatHUD.jsx)** - Real-time combat interface:
  - Attack buttons with cooldown visualization
  - Technique hotbar (1-9 keys)
  - Floating damage numbers
  - Enemy combo counter
  - Parry/guard indicators
  - Charge bar visualization
  - Turn-based combat flow

- **Action Bar** (Hotkeys 1-4):
  - Attack (1)
  - Flee (2)
  - Guard (3)
  - Charge (4)

#### World Exploration
- **[`WorldMap.jsx`](web/client/src/components/Map/WorldMap.jsx)** - Full-screen interactive map:
  - Player position marker
  - Zoom/pan controls
  - NPC markers (quest, shop, trainer)
  - Zone boundaries
  - Fast travel points

#### Social & Community Features
- **[`SocialHub.jsx`](web/client/src/components/Social/SocialHub.jsx)** - Complete community interface:
  - **Friends System**: Online status, location tracking
  - **Guild Interface**: Roster with PL display, rank system, MOTD, bank
  - **Mail System**: Unread indicators, subject, sender, timestamp
  - Tab-based navigation

#### Inventory & Equipment
- **[`Inventory.jsx`](web/client/src/components/Inventory/Inventory.jsx)** - Full inventory management:
  - Drag and drop item organization
  - Item tooltips with stats
  - Equipment slots (weapon, armor, accessories)
  - Item usage and management

#### Player Interface
- **[`PlayerHud.jsx`](web/client/src/components/PlayerHud/PlayerHud.jsx)** - Player status display:
  - Health and Ki bars
  - Power level indicator
  - Active transformation display
  - Technique shortcuts
  - Target HUD for enemies

- **[`Menu.jsx`](web/client/src/components/Menu/Menu.jsx)** - Character menu system:
  - Character stats overview
  - Technique management
  - Settings panel
  - Quest log access
  - Keyboard shortcut: M to toggle

#### Chat System
- **[`Chat.jsx`](web/client/src/components/Chat/Chat.jsx)** - Multi-channel chat:
  - Command input
  - Message history
  - Combat log integration
  - System notifications

#### Audio System
- **[`audio.js`](web/client/src/services/audio.js)** - Full audio implementation:
  - Sound effect system
  - Background music
  - Combat audio cues
  - UI sound effects

#### Game State Management ([`useGameState.js`](web/client/src/hooks/useGameState.js))
- **Server Message Validation**: Validates message shapes before state updates
- **Login Error Detection**: Pattern matching for Evennia login failures
- **State Management**: Connection, login, messages, player, target, entities
- **Ref-based Callbacks**: Prevents stale closures in message handlers

### 🛠️ Backend Improvements

#### Character Commands ([`commands/character_cmds.py`](commands/character_cmds.py))
- Enhanced stat display with detailed breakdowns
- Transformation system with form management
- Technique mastery and leveling
- Racial ability system
- Flying/movement commands
- Scan and sense utilities

#### Social Commands ([`commands/social_cmds.py`](commands/social_cmds.py))
- **Quest System** - Complete quest framework:
  - Accept missions from NPCs
  - Track quest objectives
  - Turn in for rewards
  
- **Guild System** - Full guild management:
  - Create guilds
  - Invite/promote members
  - Set MOTD
  - Guild banks
  
- **Shop System** - In-game economy:
  - Browse merchant inventories
  - Buy/sell items
  - Price displays

- **Social Interactions** - Player communication:
  - Talk to NPCs
  - Social emotes

#### Input Validation ([`world/input_validation.py`](world/input_validation.py))
- Name sanitization and validation
- Guild name validation
- Quest ID validation
- Numeric input validation
- Evennia markup stripping
- Maximum length enforcement

#### Web Services
- **[`dbforged.js`](web/client/src/services/dbforged.js)** - Game API service:
  - Character data fetching
  - Combat state management
  - Inventory synchronization
  
- **[`evennia.js`](web/client/src/services/evennia.js)** - Evennia bridge:
  - WebSocket connection management
  - Command sending
  - Event handling

### 🎨 Visual & Audio Polish

#### UI/UX Improvements
- Glassmorphism CSS design
- 3-column responsive layout
- Smooth animations and transitions
- Responsive design for various screen sizes

#### CSS Styling ([`index.css`](web/client/src/styles/index.css))
- Comprehensive styling system
- Custom scrollbars
- Animated UI elements
- Health/Ki bar styling

### 📦 Dependencies

#### New Packages
- `react` ^18.2.0
- `react-dom` ^18.2.0
- `@vitejs/plugin-react` ^4.2.0
- `vite` ^5.0.0

---

## [0.1.0] - 2026-02-21 (Vertical Slice)

### ✅ Initial Release Features

#### Core Combat System
- Server-authoritative combat loop (1s global tick)
- Technique-based combat with cooldowns
- Ki economy system
- Beam struggle mechanics
- Power Level dynamics

#### World Building
- Earth zone (4 rooms)
- Master Rokan (trainer NPC)
- Bandit Raider (hostile NPC)
- Safe room system

#### Transformations
- Super Saiyan transformation
- Race-specific form stubs

#### Commands
- `+stats` - View character stats
- `attack <target>` - Initiate combat
- `charge` - Power up
- `transform <form>` / `revert` - Change forms
- `tech <name>` - Use techniques
- `equiptech` / `listtech` - Manage techniques
- `scan` / `sense` - Detection abilities
- `suppress` - Hide power level
- `train` - Train with NPCs

---

## 🔮 Coming Soon

### Planned Features
- [ ] **More zones** - Namek, Frieza's Ship, Otherworld
- [ ] **Guild wars** - Massive PvP events
- [ ] **Achievements** - Track your legacy
- [ ] **Leaderboards** - Prove you're #1
- [ ] **Security fixes** - Server-side validation improvements
- [ ] **World Bosses** - Team up for epic battles
- [ ] **Dragon Ball system** - Shenron summons

---

## 🐛 Known Issues

### Security (Planned Fixes)
- World Boss damage validation needed
- Target validation improvements
- HP/KI information disclosure fix
- Guild join bypass prevention

*See [SECURITY_STABILITY_RELEASE.md](plans/SECURITY_STABILITY_RELEASE.md) for details.*

---

## 📋 Version History

| Version | Date | Type | Description |
|---------|------|------|-------------|
| 1.0.0 | 2026-02-25 | Major | React Web Client Launch |
| 0.1.0 | 2026-02-21 | Minor | Vertical Slice - Core Combat |

---

<p align="center">

**⚡ Train Hard. Fight Smart. Become Legendary. ⚡**

*Made with ❤️ by a Dragon Ball fan, for Dragon Ball fans*

</p>
