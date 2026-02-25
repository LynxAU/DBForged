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
    serverGrid: new Map(), // "x,y" -> terrain
    loaded: false,
    viewRadius: 10,
    centerX: 0,
    centerY: 0,

    // Default tile mappings for rooms (Fallback)
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
      
      const spriteNames = ["sand", "water", "tree", "house", "house_interior", "sky", "grass", "mountain", "floor", "wall", "plain"];
      
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

    // Update the grid from server map_data
    updateFromMapData(packet) {
      if (!packet || !packet.grid) return;
      this.centerX = packet.center_x;
      this.centerY = packet.center_y;
      this.viewRadius = packet.radius;
      
      // We can either clear or merge. For now, clear to represent current view.
      this.serverGrid.clear();
      packet.grid.forEach(t => {
        this.serverGrid.set(`${t.x},${t.y}`, t.terrain);
      });
      console.log(`[TileSystem] Grid updated: ${packet.grid.length} tiles`);
    },

    // Get tile at x,y
    getTileAt(x, y, roomName) {
      const serverTile = this.serverGrid.get(`${x},${y}`);
      if (serverTile) return serverTile;

      const map = this.defaultMappings[roomName] || {};
      const key = `${x},${y}`;
      return map[key] || map["default"] || "plain";
    },

    // Render tiles around a center point
    render(ctx, roomName, viewportX, viewportY, viewWidth, viewHeight, center_x = 0, center_y = 0) {
      if (!this.loaded) return;

      // If we have server data, we base rendering around that center
      const cx = this.serverGrid.size > 0 ? this.centerX : center_x;
      const cy = this.serverGrid.size > 0 ? this.centerY : center_y;
      const radius = this.serverGrid.size > 0 ? this.viewRadius : 8;

      for (let y = cy + radius; y >= cy - radius; y--) {
        for (let x = cx - radius; x <= cx + radius; x++) {
          const tileName = this.getTileAt(x, y, roomName);
          const tile = this.getTile(tileName);
          
          if (tile) {
            // Calculate draw position relative to viewport
            // This assumes canvas (0,0) corresponds to some world coordinate or viewport offset.
            // For now, let's keep it simple: x/y coordinates mapped to tiles.
            const drawX = (x - cx + radius) * TILE_SIZE;
            const drawY = (cy + radius - y) * TILE_SIZE;
            ctx.drawImage(tile, drawX, drawY, TILE_SIZE, TILE_SIZE);
          }
        }
      }
    },

    // Simple debug - list all loaded tiles
    debug() {
      console.log("[TileSystem] Available tiles:", [...this.tiles.keys()]);
      console.log("[TileSystem] Server grid size:", this.serverGrid.size);
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
