// DBForged Tile System
// Simple tile/sprite rendering for Kame Island

(function () {
  "use strict";

  const TILE_SIZE = 32;
  const MAP_WIDTH = 16;
  const MAP_HEIGHT = 12;

  const tileSystem = {
    tiles: new Map(),
    roomTiles: new Map(), // room_name -> tile map
    loaded: false,

    // Default tile mappings for rooms
    defaultMappings: {
      "Kame Island": {
        "0,0": "water", "0,1": "water", "0,2": "water", "0,3": "water",
        "1,0": "water", "1,1": "sand", "1,2": "sand", "1,3": "water",
        "2,0": "water", "2,1": "sand", "2,2": "sand", "2,3": "water",
        "3,0": "water", "3,1": "water", "3,2": "water", "3,3": "water",
        // Objects overlay
        "2,1": "tree", // Tree on sand
      },
      "Kame House": {
        "default": "house_interior"
      }
    },

    async loadTiles() {
      if (this.loaded) return;
      
      const spriteNames = ["sand", "water", "tree", "house", "house_interior", "sky"];
      
      for (const name of spriteNames) {
        try {
          const img = new Image();
          img.src = `/static/ui/sprites/${name}.png`;
          await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
          });
          this.tiles.set(name, img);
          console.log(`[TileSystem] Loaded: ${name}`);
        } catch (err) {
          console.warn(`[TileSystem] Failed to load: ${name}`, err);
        }
      }
      
      this.loaded = true;
      console.log(`[TileSystem] Loaded ${this.tiles.size} tiles`);
    },

    getTile(name) {
      return this.tiles.get(name);
    },

    // Get tile at position for a room
    getRoomTileMap(roomName) {
      return this.defaultMappings[roomName] || {};
    },

    // Get tile at x,y for a room
    getTileAt(roomName, x, y) {
      const map = this.getRoomTileMap(roomName);
      const key = `${x},${y}`;
      return map[key] || map["default"] || "sand";
    },

    // Render tiles for a room
    render(ctx, roomName, viewportX, viewportY, viewWidth, viewHeight) {
      if (!this.loaded || !roomName) return;

      const tileMap = this.getRoomTileMap(roomName);
      if (!tileMap) return;

      // Calculate visible tile range
      const startX = Math.max(0, Math.floor(viewportX / TILE_SIZE));
      const startY = Math.max(0, Math.floor(viewportY / TILE_SIZE));
      const endX = Math.min(MAP_WIDTH, Math.ceil((viewportX + viewWidth) / TILE_SIZE));
      const endY = Math.min(MAP_HEIGHT, Math.ceil((viewportY + viewHeight) / TILE_SIZE));

      for (let y = startY; y < endY; y++) {
        for (let x = startX; x < endX; x++) {
          const key = `${x},${y}`;
          const tileName = tileMap[key] || "sand";
          const tile = this.getTile(tileName);
          
          if (tile) {
            const drawX = x * TILE_SIZE - viewportX;
            const drawY = y * TILE_SIZE - viewportY;
            ctx.drawImage(tile, drawX, drawY, TILE_SIZE, TILE_SIZE);
          }
        }
      }
    },

    // Simple debug - list all loaded tiles
    debug() {
      console.log("[TileSystem] Available tiles:", [...this.tiles.keys()]);
      console.log("[TileSystem] Room mappings:", this.defaultMappings);
    }
  };

  // Export globally
  window.DBForgedTileSystem = tileSystem;

  // Auto-load on init
  if (document.readyState === "complete") {
    tileSystem.loadTiles();
  } else {
    window.addEventListener("load", () => tileSystem.loadTiles());
  }

})();
