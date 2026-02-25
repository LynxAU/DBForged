# DB Arena 2 - Automap System Design

## Overview
A player-accessible automap that displays the surrounding area using colored tiles based on sector types, with optional Unicode emoji support.

## 1. Unicode Input Support

### Problem
Current input filtering in [`read_from_buffer()`](src/comm.c:961) blocks non-ASCII:
```c
else if (isascii (d->inbuf[i]) && isprint (d->inbuf[i]))
```

### Solution
- Modify input handling to pass UTF-8 bytes through
- Add optional `unicode` flag to PC_DATA for players who want emoji

## 2. Map Data Structures

### Map Cell
```c
typedef struct map_cell {
    int room_vnum;           // Room vnum, 0 if empty
    bool visited;            // Player has been here
    bool current;           // Player is here now
    int player_count;       // Number of players in room
    int exit_flags;         // Bitmask of exits
} MAP_CELL;
```

### Map Data
```c
typedef struct map_data {
    int width;               // Map width in cells
    int height;              // Map height in cells
    int center_x;            // Player's X position
    int center_y;            // player's Y position
    MAP_CELL **cells;       // 2D grid
} MAP_DATA;
```

## 3. Tile Rendering

### Color Codes (MUD Standard)
| Sector Type | Color Code | ASCII | Unicode |
|-------------|------------|-------|---------|
| INSIDE | {w | # | ⬛ |
| CITY | {G | + | 🏙️ |
| FIELD | {g | . | 🌾 |
| FOREST | {g | T | 🌲 |
| HILLS | {c | ^ | ⛰️ |
| MOUNTAIN | {m | M | 🏔️ |
| WATER_SWIM | {b | ~ | 🌊 |
| WATER_NOSWIM | {b | ≈ | 🌊 |
| AIR | {c | / | ☁️ |
| DESERT | {y | : | 🏜️ |
| VOLCANIC | {r | ^ | 🌋 |
| UNDERGROUND | {w | . | 🕳️ |
| BEACH | {y | . | 🏖️ |
| OCEAN | {b | O | 🦑 |

### Special Markers
| Condition | ASCII | Unicode |
|-----------|-------|---------|
| Current Room | @ | 📍 |
| Other Player | + | 👤 |
| Multiple Players | 2-9 | 👥 |
| Shop | $ | 🏪 |
| Fountain | f | ⛲ |
| Bank | B | 🏦 |
| Arena | ! | ⚔️ |
| No-Mob/Safe | * | ⚠️ |
| Dark | d | 🌑 |

### Exit Indicators (border of cell)
| Exit | ASCII | Unicode |
|------|-------|---------|
| North | ^ | ↑ |
| South | v | ↓ |
| East | > | → |
| West | < | ← |
| Up | ^ | ⬆️ |
| Down | . | ⬇️ |

## 4. Map Generation Algorithm

### Steps
1. **BFS from current room** - Flood fill to find all reachable rooms within radius
2. **Build coordinate mapping** - Track (x,y) for each room based on directions
3. **Calculate bounds** - Find min/max coordinates to center map
4. **Populate grid** - Fill MAP_CELL for each position

### Algorithm
```
function generate_map(ch, radius):
    map = create_empty_map()
    visited = set()
    queue = [(ch->in_room, 0, 0)]  // (room, x, y)
    
    while queue not empty:
        room, x, y = queue.pop()
        
        if distance(x, y) > radius: continue
        if room in visited: continue
        visited.add(room)
        
        map.cells[x][y] = create_cell(room, x, y)
        
        for each exit in room.exits:
            next_room = exit.destination
            next_x = x + exit.dx
            next_y = y + exit.dy
            queue.add((next_room, next_x, next_y))
    
    return map
```

### Coordinate System
- North: y - 1
- South: y + 1
- East: x + 1
- West: x - 1

## 5. User Commands

### Primary Command
```
map [radius] [style]
```
- radius: 1-10 (default: 3)
- style: ascii, unicode, color (default: color)

### Options
```
map toggle unicode   // Enable/disable Unicode
map size <n>         // Set default radius
map style ascii|unicode|color
```

### Examples
```
> map
> map 5
> map unicode
> map 7 ascii
```

## 6. Files to Modify/Create

### New Files
- `src/map.[ch]` - Map generation and rendering

### Modified Files
- `src/merc.h` - Add map structures, PC_DATA fields
- `src/comm.c` - Unicode input support
- `src/interp.c` - Add map command
- `src/act_info.c` - Add do_map function
- `src/cmakelists.txt` - Add map.c to build

## 7. Display Format

### Sample Output (Color Mode)
```
                     {m[M]{x
                     {m[^]{x
        {g[...]{x      {c[+@]{x      {b[~~~]{x
           {g[.]{x----{G[@]{x----{b[~]{x
        {g[...]{x      {g[T]{x
                     {y[..]{x
                     
[x] = grass, [@] = you, [+] = player, [~] = water, [M] = mountain
```

### Sample Output (Unicode Mode)
```
                     🏔️
                     ⛰️
        🌾          📍          🌊
           🌾----🏙️----🌊
        🌾          🌲
                     🏜️
```

## 8. Performance Considerations

- Limit radius default to 5 rooms
- Cache map for `wait` pulses ( regenerate only when player moves)
- Use static buffer for map rendering
- Free allocated memory after display

## 9. Future Enhancements

- [ ] Zone boundaries on map
- [ ] NPCs shown as different symbols
- [ ] Quest markers
- [ ] Group member positions
- [ ] Auto-show on area change
- [ ] Minimap in persistent window (client-dependent)