# DBForged Graphics System

## Overview

This document describes the sprite/tile rendering system for DBForged's graphical web client.

## Directory Structure

```
evennia/web/static/ui/
├── sprites/           # Sprite image files (PNG)
│   ├── sand.png       # Beach sand tile
│   ├── water.png      # Ocean/water tile  
│   ├── tree.png       # Tree/sprite object
│   ├── house.png      # House exterior
│   ├── house_interior.png  # Interior floor
│   └── spritesheet.png     # All tiles combined
│
└── tiles/
    └── tile_system.js     # Tile rendering engine
```

## How Sprites Load

1. **Static Files**: Sprites are served from `evennia/web/static/ui/sprites/`
2. **Tile System**: The `tile_system.js` module loads sprites via `Image()` objects
3. **Auto-load**: Sprites load automatically when the web client initializes

## Adding New Sprites

1. Add PNG file to `evennia/web/static/ui/sprites/`
2. Name: `{spritename}.png` (e.g., `rock.png`)
3. Recommended size: 32x32 pixels
4. Format: PNG with transparency (RGBA)

## How Tiles Map to Rooms

The tile system uses a room-name based mapping in `tile_system.js`:

```javascript
defaultMappings: {
  "Kame Island": {
    "0,0": "water", "0,1": "water",  // Coordinate -> tile name
    "2,1": "sand", "2,2": "sand",
    "2,1": "tree",  // Objects overlay on terrain
  },
  "Kame House": {
    "default": "house_interior"  // Default tile for room
  }
}
```

### Adding a New Room

1. Open `tile_system.js`
2. Add entry to `defaultMappings`:
```javascript
"My Room": {
  "0,0": "sand", "0,1": "sand",
  "1,0": "sand", "1,1": "water",
  "2,2": "tree",  // Object at x=2, y=2
}
```

## Tile Layering

Tiles render in order:
1. **Terrain layer**: Base tiles (sand, water, floor)
2. **Object layer**: Objects drawn on top (trees, houses)

Coordinates are read as `x,y` where:
- x = column (left to right)
- y = row (top to bottom)

## Integration with Canvas Demo

The `dbforged_canvas_demo.js` integrates with the tile system:
- Calls `tile_system.render()` in `drawBackground()`
- Falls back to gradient if tiles not available
- Shows fallback silhouettes if animation assets missing

## Debug Commands

In browser console:
```javascript
// List loaded tiles
window.DBForgedTileSystem.debug();

// Check loaded tiles
window.DBForgedTileSystem.tiles

// Force reload tiles
window.DBForgedTileSystem.loadTiles();
```

## Web Client URLs

- Web Client: `http://localhost:5154`
- Telnet: `localhost:5153`

## Files Modified

- `evennia/web/static/ui/tiles/tile_system.js` - Tile engine
- `live/web/static/webclient/js/dbforged_canvas_demo.js` - Canvas integration  
- `live/web/templates/webclient/webclient.html` - Script includes
- `evennia/web/static/ui/sprites/*.png` - Sprite assets

## Troubleshooting

**Tiles not showing:**
1. Check browser console for errors
2. Verify sprites exist in `evennia/web/static/ui/sprites/`
3. Ensure script loads before canvas renders

**Room not mapping:**
1. Check `defaultMappings` in tile_system.js
2. Verify room name matches exactly (case-sensitive)
3. Use browser console to debug

**Sprites show as black squares:**
- Ensure PNG files have correct alpha channel
- Check file permissions
