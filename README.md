# 🐉 DBForged ⚔️

<p align="center">
  <img src="https://img.shields.io/badge/Genre-MMORPG/MUD-brightgreen?style=for-the-badge&logo=gamepad" alt="Genre">
  <img src="https://img.shields.io/badge/Theme-Dragon%20Ball%20Inspired-orange?style=for-the-badge&logo=fire" alt="Theme">
  <img src="https://img.shields.io/badge/Engine-Evennia-blue?style=for-the-badge&logo=python" alt="Engine">
</p>

---

> **Welcome, warrior!** You've stumbled into DBForged — a text-based MMORPG inspired by the legendary Dragon Ball universe. Forge your path, train your ki, transform into legendary forms, and battle your way to becoming the strongest being in the multiverse! 🥋

---

## ✨ Features

### 🔥 Dynamic Combat System
- **Real-time combat** with server-authoritative 1-second tick loops
- **Technique-based combat** — equip up to 4 techniques and master them through use
- **Cooldowns & Ki Costs** — manage your energy wisely or face defeat!
- **Beam Struggles** — when two beams collide, a clash determines the winner! 💥

### ⚡ Power Level System
- **Dynamic Power Levels** that change based on:
  - 📈 Charge state (+55% boost while charging!)
  - 💔 Injury status
  - 🌀 Ki levels
  - 🦸 Transformation multipliers
  - 🎭 Suppression (hide your true power!)
- **PL Gap Effects** — huge power differences create overwhelming advantages (or devastating weaknesses!)

### 🐉 Transformations
- **Super Saiyan** — the legendary golden form
- **Super Saiyan 2 & 3** — escalating power, escalating drain
- **Legendary Super Saiyan** — a rare, berserker-like transformation
- **Namekian Fusion** — heal and grow stronger
- **And more race-specific forms!** 🦎

### 🎯 Techniques (Data-Driven Skills)

| Type | Examples |
|------|----------|
| **Blast** | 🔹 Ki Blast, Special Beam Cannon |
| **Beam** | 🔫 Kame Wave, Final Flash, Masenko |
| **Stun** | ☀️ Solar Flare, Evil Eye |
| **Defense** | 🛡️ Guard, Energy Shield |
| **Movement** | 💨 Afterimage, Vanish |
| **Special** | 🍃 Destructo Disc, Death Beam |

### 🕵️ Detection & Stealth
- **Scan** — detect a target's power level and status
- **Sense** — read the room or hidden entities (requires high Ki Control!)
- **Suppress** — hide your power level from prying eyes (with a slight combat penalty)

### 🏛️ Social Features

#### ⚔️ Guilds
- **Create** your own guild
- **Invite** friends to join
- **Promote** members to officers
- **Set MOTD** — rally your crew!
- **Disband** or be kicked — drama awaits!

#### 📜 Quests
- **Accept** missions from NPCs
- **Complete** objectives
- **Turn in** for rewards and progression

#### 🏪 Shops & Economy
- **Buy** equipment, items, and techniques
- **Sell** your loot for Zenni
- **Browse** merchant inventories

#### 💬 Interaction
- **Talk** to NPCs for quests, lore, and hints
- **Social commands** — wave, hug, laugh, and more!

### 🏆 Events & Tournaments

#### 🥊 Player Tournaments
- **Enter** the arena for glory
- **Fight** your way to the top
- **Win** exclusive rewards and titles!

#### 🐉 World Bosses
- **Team up** with other players
- **Challenge** massive, powerful enemies
- **Earn** rare drops and power-ups!

#### 🌟 Shenron Summons
- **Collect** Dragon Balls across the world
- **Summon** the Eternal Dragon
- **Make a wish** — the possibilities are endless!

### 🗺️ World Exploration
- **Earth zones** — from peaceful plains to dangerous dungeons
- **Safe rooms** — rest and recover without fear
- **Dangerous areas** — bandit's alleys and beyond!
- **World map** — navigate with style

---

## 🎮 Getting Started

### Quick Start
```bash
# Start the server
dbforged start

# Connect with a MUD client
telnet localhost 4000

# Or use the web client!
# Open http://localhost:4001 in your browser
```

### Character Commands
| Command | Description |
|---------|-------------|
| `+stats` | View your stats and power level |
| `attack <target>` | Initiate combat |
| `tech <name> <target>` | Use a technique |
| `charge` | Build up power (vulnerable to interrupt!) |
| `transform <form>` | Unlock a new form |
| `revert` | Return to base form |
| `scan <target>` | Detect someone's power |
| `sense <target/room>` | Read energy (high Ki Control required) |
| `suppress on/off` | Hide your true power |
| `train` | Train with a mentor NPC |
| `inventory` | Check your items |
| `shop` | Browse merchant wares |
| `quest` | View active quests |
| `guild` | Manage your guild |
| `map` | View the world map |
| `potara <target>` | Initiate Potara fusion (needs earrings) |
| `dance <target>` | Initiate Metamoran dance fusion |
| `unfuse` | End your current fusion |
| `fusion` | Check fusion status |

---

## 🛠️ Tech Stack

- **Engine**: [Evennia](https://www.evennia.com/) — the ultimate MUD/MMORPG framework
- **Language**: Python 🐍
- **Frontend**: React + Vite (Web Client) ⚛️
- **Storage**: JSON-based persistence with database backend

---

## 📁 Project Structure

```
DBForged/
├── commands/          # All game commands
│   ├── combat_cmds.py    # Combat actions
│   ├── character_cmds.py # Character management
│   ├── social_cmds.py    # Quests, guilds, shops
│   └── db_commands.py   # Main DB gameplay commands
├── typeclasses/       # Game objects (characters, rooms, NPCs)
├── world/             # Core game systems
│   ├── combat.py         # Combat engine
│   ├── power.py          # Power level calculations
│   ├── techniques.py    # Technique registry
│   ├── forms.py         # Transformation forms
│   ├── tournaments.py   # Tournament system
│   └── quests.py        # Quest system
├── web/               # Web client and server
│   ├── client/          # React frontend
│   └── static/          # Assets and custom client
└── server/           # Server configuration
```

---

## 🌟 Coming Soon

- [ ] **More zones** — Namek, Frieza's Ship, Otherworld
- [x] **Fusions** — Potara earrings, Metamoran dance
- [ ] **Guild wars** — massive PvP events
- [ ] **Achievements** — track your legacy
- [ ] **Leaderboards** — prove you're #1

---

## 🤝 Contributing

Found a bug? Got a cool technique idea? Want to add a new zone?

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a PR!

---

## 📜 License

MIT License — go forth and forge your destiny!

---

<p align="center">

**⚡ Train Hard. Fight Smart. Become Legendary. ⚡**

*Made with ❤️ by a Dragon Ball fan, for Dragon Ball fans*

</p>
