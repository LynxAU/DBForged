# Dragonball Forged ⚡

A Dragon Ball-themed MUD (Multi-User Dungeon) game built on the Evennia platform.

## About

Dragonball Forged is an immersive text-based RPG inspired by the Dragon Ball universe. Players can create characters from various races (Saiyan, Human, Namekian, etc.), train in martial arts, learn special techniques, and battle to become the strongest fighter in the universe.

## Features

- **Character Creation**: Create your fighter with customizable appearance (hair style, hair color, eye color, aura color)
- **Racial Varieties**: Choose from Saiyan, Human, Namekian, and more races, each with unique abilities
- **Combat System**: Real-time combat with special techniques and power levels
- **Character Advancement**: Train to increase your stats and unlock new abilities

## Installation

1. Install Evennia:
   ```
   pip install evennia
   ```

2. Start the server:
   ```
   evennia start
   ```

3. Connect to the game:
   - Web client: http://localhost:4001
   - MUD client: localhost:4000

## Quick Start

1. Create an account with `create <username> <password>`
2. Create your character using the in-game character creation wizard
3. Start your adventure!

## Community

Join the adventure and become the legend!

---

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Section 7 review part now displays colors properly with correct color formatting for hair, eye, and aura colors
- Added color utility functions in `world/color_utils.py` for consistent color display
- Custom connection screen logo with Dragonball Forged branding (yellow Drag, orange asterisk, red nball Forged)
- Debug logging in character creation to help diagnose save issues
- Added missing colors (brown, hazel, bronze, none) to ANSI color map

### Fixed
- Character creator now properly colorizes color names in the review section
- Fixed eye color, hair color, and aura color display to use proper Evennia color codes
- Fixed color mapping for various color names including orange, bronze, and silver

### Changed
- Updated connection screen to show "Welcome to Drag(*)nball Forged" with custom coloring
- Improved character creation workflow with better error handling

## [0.1.0] - Initial Release

### Added
- Initial Dragonball Forged game template
- Basic character creation system with race, sex, hair style, hair color, eye color, and aura color selection
- Saiyan, Human, and Namekian races
- Basic combat system
- Web client support
- Evennia base framework
