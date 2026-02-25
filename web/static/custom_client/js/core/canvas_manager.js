// DBForged Custom Client Canvas Renderer
// Rewritten from dbforged_canvas_demo.js to fit the standalone app shell

const PACK_CANDIDATES = [
    "/static/ui/animations/goku_placeholder_pack",
    "/static/ui/animations",
];

export const CanvasManager = {
    initialized: false,
    catalog: null,
    players: new Map(), // entityId -> AnimationPlayer
    entities: new Map(), // entityId -> latest state
    canvas: null,
    ctx: null,
    lastFrameTs: 0,
    mappingConfig: null,
    tileSystemLoaded: false,
    currentRoom: "Kame Island",

    async init() {
        if (this.initialized) return;
        this.initialized = true;

        this.canvas = document.getElementById('game-canvas');
        if (!this.canvas) {
            console.error("CanvasManager: #game-canvas not found.");
            return;
        }
        this.ctx = this.canvas.getContext('2d');

        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Bind Click-to-Target
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));

        // Try load Tile System
        try {
            if (window.DBForgedTileSystem) {
                await window.DBForgedTileSystem.loadTiles();
                this.tileSystemLoaded = true;
                console.log("Tile system loaded");
            }
        } catch (err) {
            console.log("Tile system not available:", err.message);
        }

        // Try load Animations
        try {
            const animModule = await import("/static/ui/animations/animation_system.js");
            window.DBForgedAnim = animModule;
            this.catalog = await this.loadCatalog(animModule);
        } catch (err) {
            console.warn("Animations unavailable. Using silouhettes.", err);
        }

        // Start render loop
        requestAnimationFrame((ts) => this.tick(ts));
    },

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        if (rect.height <= 0 || rect.width <= 0) return;

        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = Math.max(1, Math.floor(rect.width * dpr));
        this.canvas.height = Math.max(1, Math.floor(rect.height * dpr));
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    },

    async loadCatalog(animModule) {
        let lastErr = null;
        for (const base of PACK_CANDIDATES) {
            try {
                const cat = await animModule.loadAnimationCatalog(base, { preload: true, ignoreMissingFrames: true });
                console.log(`Loaded animations: ${cat.packName}`);
                return cat;
            } catch (err) {
                lastErr = err;
            }
        }
        throw lastErr || new Error("No packs loaded.");
    },

    handleEntityDelta(entity) {
        const prev = this.entities.get(entity.id) || {};

        const state = {
            ...prev,
            ...entity,
            _seenAt: performance.now(),
            _visualX: prev._visualX ?? (entity.position?.x ?? 0),
            _visualY: prev._visualY ?? (entity.position?.y ?? 0)
        };

        this.entities.set(entity.id, state);

        const player = this.getEntityPlayer(entity.id);
        if (player) {
            const moved = prev.position && entity.position &&
                (prev.position.x !== entity.position.x || prev.position.y !== entity.position.y);
            player.applyState(moved ? "moving" : "idle");
        }
    },

    handleMapData(data) {
        if (window.DBForgedTileSystem) {
            window.DBForgedTileSystem.updateFromMapData(data);
        }
    },

    handleCombatEvent(packet) {
        const evtName = this.normalizeTechniqueEventName(packet);
        if (!evtName) return;

        const sourceId = packet.source_id || packet.sourceId;
        if (!sourceId) return;
        const player = this.getEntityPlayer(sourceId);
        if (player) player.applyServerTechniqueEvent(evtName);
    },

    normalizeTechniqueEventName(packet) {
        if (packet.type === "vfx_trigger") {
            if (packet.vfx_id === "vfx_charge_glow") return "charge_start";
            if ((packet.vfx_id || "").includes("beam")) return "beam_fire";
        }
        if (packet.type === "combat_event") {
            if (packet.subtype === "beam_cast" || packet.subtype === "beam_hit") return "beam_fire";
        }
        return null;
    },

    getEntityPlayer(entityId) {
        let player = this.players.get(entityId);
        if (player || !this.catalog || !window.DBForgedAnim) return player;

        const { AnimationPlayer, createDefaultAnimationConfig } = window.DBForgedAnim;
        if (!this.mappingConfig) {
            this.mappingConfig = createDefaultAnimationConfig({ overrides: {} });
        }

        player = new AnimationPlayer({
            catalog: this.catalog,
            spriteId: String(entityId),
            mappingConfig: this.mappingConfig,
            scale: 1,
        });
        player.applyState("idle");
        this.players.set(entityId, player);
        return player;
    },

    layoutEntity(entity, w, h) {
        if (!window.DBForgedTileSystem) return { x: w / 2, y: h / 2 }; // Fallback center

        const ts = window.DBForgedTileSystem;
        const TILE_SIZE = 32;

        const vx = entity._visualX ?? (entity.position?.x ?? 0);
        const vy = entity._visualY ?? (entity.position?.y ?? 0);

        const drawX = (vx - ts.centerX + ts.viewRadius) * TILE_SIZE + TILE_SIZE / 2;
        const drawY = (ts.centerY + ts.viewRadius - vy) * TILE_SIZE + TILE_SIZE;

        return { x: drawX, y: drawY };
    },

    handleCanvasClick(e) {
        if (!this.canvas) return;
        const rect = this.canvas.getBoundingClientRect();

        // Adjust for device pixel ratio scaling
        const dpr = window.devicePixelRatio || 1;
        const clickX = (e.clientX - rect.left) * dpr;
        const clickY = (e.clientY - rect.top) * dpr;

        // Iterate backwards (top-most rendered first)
        const renderList = [...this.entities.values()]
            .map(entity => ({ entity, pt: this.layoutEntity(entity, this.canvas.width, this.canvas.height) }))
            .sort((a, b) => b.pt.y - a.pt.y);

        for (const { entity, pt } of renderList) {
            // Approximate hit box: center x-20 to x+20, above feet y-60 to y-10
            const hitW = 40;
            const hitH = 50;
            const hitX = pt.x - hitW / 2;
            const hitY = pt.y - hitH - 10;

            if (clickX >= hitX && clickX <= hitX + hitW &&
                clickY >= hitY && clickY <= hitY + hitH) {

                console.log("Canvas targeted:", entity.name);

                // If the app scope has the sendCmd function, tell the server
                if (window.sendCmd) {
                    // Evennia doesn't have a native 'target' command built into default,
                    // but we'll assume the MUD db_commands can handle "target <name>"
                    window.sendCmd(`target ${entity.name}`);
                }

                // We'll also force-update the Scouter locally while we wait for roundtrip
                if (window.DBForged && window.DBForged.updateScouterHud) {
                    window.DBForged.updateScouterHud(entity);
                }

                return; // Stop after finding top-most hit
            }
        }

        // If we clicked empty space on the map, we might trigger a walk command later
    },

    drawEntityFallback(ctx, entity, x, feetY) {
        const aura = (entity.appearance?.aura_color || "white").toLowerCase();
        const auraColor = {
            red: "#ff5a5a", blue: "#67b7ff", green: "#73ff9b", yellow: "#ffd74a",
            purple: "#d280ff", white: "#f6f6ff", black: "#6c6c6c",
        }[aura] || "#f6f6ff";

        ctx.save();
        ctx.globalAlpha = 0.35;
        ctx.fillStyle = auraColor;
        ctx.beginPath();
        ctx.ellipse(x, feetY - 36, 18, 28, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        ctx.fillStyle = "#101010";
        ctx.fillRect(x - 6, feetY - 24, 12, 24);
        ctx.fillStyle = "#f2ccaa";
        ctx.fillRect(x - 5, feetY - 34, 10, 10);
    },

    tick(ts) {
        if (!this.canvas || !this.ctx) return requestAnimationFrame((t) => this.tick(t));

        const dt = this.lastFrameTs ? (ts - this.lastFrameTs) / 1000 : 0;
        this.lastFrameTs = ts;

        const rect = this.canvas.getBoundingClientRect();
        const w = Math.max(1, Math.floor(rect.width));
        const h = Math.max(1, Math.floor(rect.height));

        const LERP_SPEED = 5.0;
        this.entities.forEach(entity => {
            const tx = entity.position?.x ?? 0;
            const ty = entity.position?.y ?? 0;
            entity._visualX = (entity._visualX ?? tx) + (tx - (entity._visualX ?? tx)) * Math.min(1, dt * LERP_SPEED);
            entity._visualY = (entity._visualY ?? ty) + (ty - (entity._visualY ?? ty)) * Math.min(1, dt * LERP_SPEED);
        });

        this.ctx.clearRect(0, 0, w, h);

        if (this.tileSystemLoaded && window.DBForgedTileSystem && this.currentRoom) {
            window.DBForgedTileSystem.render(this.ctx, this.currentRoom, 0, 0, w, h);
        }

        const renderList = [...this.entities.values()]
            .map(entity => ({ entity, pt: this.layoutEntity(entity, w, h) }))
            .sort((a, b) => a.pt.y - b.pt.y);

        renderList.forEach(({ entity, pt }) => {
            // Draw Ki Aura behind the entity
            if (entity.ki_max > 0 && entity.ki > 0) {
                const kiPct = entity.ki / entity.ki_max;
                if (kiPct > 0.05) {
                    const radius = 30 + (kiPct * 25);
                    const opacity = 0.2 + (kiPct * 0.4);
                    const pulse = Math.sin(ts / 150) * 8 * kiPct;

                    const auraStr = (entity.appearance?.aura_color || "blue").toLowerCase();
                    const auraRGB = {
                        red: "255, 90, 90", blue: "103, 183, 255", green: "115, 255, 155",
                        yellow: "255, 215, 74", purple: "210, 128, 255", white: "246, 246, 255",
                        black: "108, 108, 108"
                    }[auraStr] || "103, 183, 255";

                    this.ctx.save();
                    this.ctx.globalCompositeOperation = "screen";
                    const gradient = this.ctx.createRadialGradient(pt.x, pt.y - 30, radius * 0.1, pt.x, pt.y - 30, radius + pulse);
                    gradient.addColorStop(0, `rgba(${auraRGB}, ${opacity})`);
                    gradient.addColorStop(0.5, `rgba(${auraRGB}, ${opacity * 0.5})`);
                    gradient.addColorStop(1, `rgba(${auraRGB}, 0)`);

                    this.ctx.fillStyle = gradient;
                    this.ctx.beginPath();
                    // Draw aura taller than wide (pill shape matching DBZ auras)
                    this.ctx.ellipse(pt.x, pt.y - 30, (radius + pulse) * 0.8, (radius + pulse) * 1.3, 0, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.restore();
                }
            }

            const player = this.getEntityPlayer(entity.id);
            if (player) {
                player.update(dt);
                player.render(this.ctx, pt.x, pt.y, { scale: 1.5 });
            } else {
                this.drawEntityFallback(this.ctx, entity, pt.x, pt.y);
            }
            // Nameplate
            this.ctx.fillStyle = "rgba(0,0,0,0.65)";
            this.ctx.fillRect(pt.x - 50, pt.y - 75, 100, 16);
            this.ctx.fillStyle = "#ffffff";
            this.ctx.textAlign = "center";
            this.ctx.font = "bold 11px sans-serif";
            this.ctx.fillText(`${entity.name} (${entity.displayed_pl ?? "?"})`, pt.x, pt.y - 63);
        });

        requestAnimationFrame((t) => this.tick(t));
    }
};
