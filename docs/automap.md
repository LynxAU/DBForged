# Automap System - Technical Design

## Overview
A visual map shown when looking at a room, displaying adjacent rooms and their connections.

---

## How It Works

### 1. Map Display
- Shows current room as `[@]` (or colored symbol based on room type)
- Shows adjacent rooms as connected paths
- Shows doors/walls as appropriate
- Map size: 7x7 or 9x9 rooms centered on player

### 2. Room Symbols
- `[@]` - You are here
- `[+]` - Shop (room with ACT_PSHOP)
- `[*]` - Quest mob
- `[T]` - Trainers
- `[.]` - Regular room
- `[#]` - Exit/entrance

### 3. Path Symbols
- `|` - North/South path
- `-` - East/West path
- `\` - Northeast/Southwest
- `/` - Northwest/Southeast

---

## Implementation

### 1. Add function to generate and display map
- Function: `show_map(ch)`
- Called from `do_look` or new `map` command

### 2. Color coding by sector type
- Inside: Brown/Yellow
- City: Gray
- Field: Green
- Forest: Dark Green
- Hills: Light Gray
- Mountain: White
- Water: Blue
- Underground: Dark Gray

---

## Files to Modify

- act_info.c - Add map display to look
- Or create new command in act_move.c
