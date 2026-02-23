// DBForged webclient canvas demo overlay for @event JSON messages.
// This is a lightweight visual testbed, not the final production renderer.

(function () {
  "use strict";

  const PACK_CANDIDATES = [
    "/static/ui/animations/goku_placeholder_pack",
    "/static/ui/animations",
  ];

  const demoState = {
    initialized: false,
    catalog: null,
    players: new Map(), // entityId -> AnimationPlayer
    entities: new Map(), // entityId -> latest state
    overlay: null,
    canvas: null,
    ctx: null,
    statusEl: null,
    lastFrameTs: 0,
    observer: null,
    mappingConfig: null,
    activeScene: false,
    tileSystemLoaded: false,
    currentRoom: "Kame Island",
  };

  function log(...args) {
    console.log("[DBForgedCanvasDemo]", ...args);
  }

  function setStatus(msg) {
    if (demoState.statusEl) demoState.statusEl.textContent = msg;
    log(msg);
  }

  function safeJsonParse(text) {
    try {
      return JSON.parse(text);
    } catch (_err) {
      return null;
    }
  }

  async function loadAnimModule() {
    // ESM import; static path under Evennia.
    return await import("/static/ui/animations/animation_system.js");
  }

  async function loadCatalogWithFallbacks(animModule) {
    let lastErr = null;
    for (const base of PACK_CANDIDATES) {
      try {
        setStatus(`Loading animation pack: ${base}`);
        const catalog = await animModule.loadAnimationCatalog(base, { preload: true, ignoreMissingFrames: true });
        setStatus(`Animation pack loaded: ${catalog.packName} (${catalog.listAnimationNames().length} anims)`);
        return catalog;
      } catch (err) {
        lastErr = err;
        console.warn(err);
      }
    }
    throw lastErr || new Error("No animation pack could be loaded.");
  }

  function ensureOverlay() {
    if (demoState.overlay) return;

    const mainSub = document.querySelector("#main-sub") || document.querySelector("#main");
    if (!mainSub) {
      setStatus("Webclient layout not ready yet.");
      return;
    }

    if (getComputedStyle(mainSub).position === "static") {
      mainSub.style.position = "relative";
    }

    const overlay = document.createElement("div");
    overlay.id = "dbforged-canvas-overlay";
    overlay.style.cssText = [
      "position:absolute",
      "inset:0",
      "pointer-events:none",
      "z-index:20",
      "display:flex",
      "flex-direction:column",
      "border-bottom:1px solid rgba(255,255,255,0.05)",
      "background:linear-gradient(180deg, rgba(5,9,18,0.25), rgba(5,9,18,0.08) 35%, rgba(5,9,18,0.0))",
    ].join(";");

    const status = document.createElement("div");
    status.id = "dbforged-canvas-status";
    status.style.cssText = [
      "font:12px/1.2 monospace",
      "color:#d7e6ff",
      "text-shadow:0 1px 2px #000",
      "padding:6px 8px",
      "background:linear-gradient(90deg, rgba(0,0,0,0.35), rgba(0,0,0,0))",
      "width:max-content",
      "max-width:80%",
      "white-space:pre-wrap",
    ].join(";");
    status.textContent = "DBForged Canvas Demo initializing...";

    const canvas = document.createElement("canvas");
    canvas.id = "dbforged-canvas";
    canvas.style.cssText = "width:100%; height:0px; display:block; image-rendering: pixelated; transition: height 120ms ease;";

    overlay.appendChild(status);
    overlay.appendChild(canvas);
    mainSub.prepend(overlay);

    demoState.overlay = overlay;
    demoState.canvas = canvas;
    demoState.ctx = canvas.getContext("2d");
    demoState.statusEl = status;

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
  }

  function resizeCanvas() {
    if (!demoState.canvas) return;
    const rect = demoState.canvas.getBoundingClientRect();
    if (rect.height <= 0 || rect.width <= 0) return;
    const dpr = window.devicePixelRatio || 1;
    demoState.canvas.width = Math.max(1, Math.floor(rect.width * dpr));
    demoState.canvas.height = Math.max(1, Math.floor(rect.height * dpr));
    demoState.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function getEntityPlayer(entityId) {
    let player = demoState.players.get(entityId);
    if (player || !demoState.catalog || !window.DBForgedAnim) return player;

    const { AnimationPlayer, createDefaultAnimationConfig } = window.DBForgedAnim;
    if (!demoState.mappingConfig) {
      demoState.mappingConfig = createDefaultAnimationConfig({
        // Example overrides - adjust to exact pack names later.
        overrides: {
          // idle: "base_action_row01",
          // moving: "base_action_row02",
        },
      });
    }

    player = new AnimationPlayer({
      catalog: demoState.catalog,
      spriteId: String(entityId),
      mappingConfig: demoState.mappingConfig,
      scale: 1,
    });
    // Start with idle if available.
    player.applyState("idle");
    demoState.players.set(entityId, player);
    return player;
  }

  function normalizeTechniqueEventName(packet) {
    if (!packet) return null;
    if (packet.type === "vfx_trigger") {
      if (packet.vfx_id === "vfx_charge_glow") return "charge_start";
      if ((packet.vfx_id || "").includes("beam")) return "beam_fire";
      return null;
    }
    if (packet.type === "combat_event") {
      if (packet.subtype === "beam_cast") return "beam_fire";
      if (packet.subtype === "beam_hit") return "beam_fire";
      return null;
    }
    return null;
  }

  function applyPacket(packet) {
    if (!packet || !packet.type) return;

    if (packet.type === "entity_delta" && packet.entity) {
      if (!demoState.activeScene) {
        demoState.activeScene = true;
        if (demoState.canvas) {
          demoState.canvas.style.height = "512px"; // Increased height for 2D view
          setTimeout(resizeCanvas, 10);
        }
      }
      const entity = packet.entity;
      const prev = demoState.entities.get(entity.id) || {};

      // Store current as target for lerping
      const state = {
        ...prev,
        ...entity,
        _seenAt: performance.now(),
        // For lerp: start from previous visually rendered position if exists
        _visualX: prev._visualX ?? (entity.position?.x ?? 0),
        _visualY: prev._visualY ?? (entity.position?.y ?? 0)
      };
      demoState.entities.set(entity.id, state);

      const player = getEntityPlayer(entity.id);
      if (player) {
        const moved = prev.position && entity.position &&
          (prev.position.x !== entity.position.x || prev.position.y !== entity.position.y);
        player.applyState(moved ? "moving" : "idle");
      }
      return;
    }

    if (packet.type === "map_data") {
      if (window.DBForgedTileSystem) {
        window.DBForgedTileSystem.updateFromMapData(packet);
      }
      return;
    }

    if (packet.type === "combat_event" || packet.type === "vfx_trigger") {
      const evtName = normalizeTechniqueEventName(packet);
      if (!evtName) return;

      const sourceId = packet.source_id || packet.sourceId;
      if (!sourceId) return;
      const player = getEntityPlayer(sourceId);
      if (player) {
        player.applyServerTechniqueEvent(evtName);
      }
      return;
    }
  }

  function handleMessageNode(node) {
    if (!(node instanceof HTMLElement)) return;
    const text = (node.textContent || "").trim();
    if (!text.startsWith("@event ")) return;
    const packet = safeJsonParse(text.slice(7));
    if (!packet) return;
    // Hide raw event packets in the text pane; keep for debugging if needed by toggling below.
    node.style.display = "none";
    applyPacket(packet);
  }

  function attachMessageObserver() {
    const target = document.querySelector("#messagewindow");
    if (!target) {
      setTimeout(attachMessageObserver, 500);
      return;
    }

    // Process any existing buffered messages first.
    target.querySelectorAll("div").forEach(handleMessageNode);

    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          handleMessageNode(node);
          if (node instanceof HTMLElement) {
            node.querySelectorAll?.("div").forEach(handleMessageNode);
          }
        }
      }
    });
    observer.observe(target, { childList: true, subtree: true });
    demoState.observer = observer;
    setStatus("Watching @event packets in message window.");
  }

  function layoutEntity(entity, canvasW, canvasH) {
    if (!window.DBForgedTileSystem) return { x: 0, y: 0 };

    const ts = window.DBForgedTileSystem;
    const TILE_SIZE = 32;

    // Calculate position relative to tile system center
    // We use the lerped visual coordinates
    const vx = entity._visualX ?? (entity.position?.x ?? 0);
    const vy = entity._visualY ?? (entity.position?.y ?? 0);

    const drawX = (vx - ts.centerX + ts.viewRadius) * TILE_SIZE + TILE_SIZE / 2;
    const drawY = (ts.centerY + ts.viewRadius - vy) * TILE_SIZE + TILE_SIZE; // Feet at bottom of tile

    return { x: drawX, y: drawY };
  }

  function drawBackground(ctx, w, h) {
    // Try to use tile system first
    if (demoState.tileSystemLoaded && window.DBForgedTileSystem && demoState.currentRoom) {
      window.DBForgedTileSystem.render(ctx, demoState.currentRoom, 0, 0, w, h);
      return;
    }

    // Fallback: gradient background
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, "#0a1324");
    g.addColorStop(0.55, "#13203d");
    g.addColorStop(1, "#2f4f6f");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  }

  function drawEntityFallback(ctx, entity, x, feetY) {
    const aura = (entity.appearance?.aura_color || "white").toLowerCase();
    const auraColor = {
      red: "#ff5a5a",
      blue: "#67b7ff",
      green: "#73ff9b",
      yellow: "#ffd74a",
      gold: "#ffd74a",
      purple: "#d280ff",
      pink: "#ff7dd9",
      white: "#f6f6ff",
      black: "#6c6c6c",
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

    ctx.fillStyle = "#ffffff";
    ctx.font = "11px monospace";
    ctx.textAlign = "center";
    ctx.fillText(entity.name || `#${entity.id}`, x, feetY - 42);
  }

  function tick(ts) {
    const canvas = demoState.canvas;
    const ctx = demoState.ctx;
    if (!canvas || !ctx) {
      requestAnimationFrame(tick);
      return;
    }

    const dt = demoState.lastFrameTs ? (ts - demoState.lastFrameTs) / 1000 : 0;
    demoState.lastFrameTs = ts;

    const rect = canvas.getBoundingClientRect();
    const w = Math.max(1, Math.floor(rect.width));
    const h = Math.max(1, Math.floor(rect.height));
    if (h <= 1) {
      requestAnimationFrame(tick);
      return;
    }

    // Lerp positions for all entities
    const LERP_SPEED = 5.0; // Adjust for smoothness
    demoState.entities.forEach(entity => {
      const tx = entity.position?.x ?? 0;
      const ty = entity.position?.y ?? 0;
      entity._visualX = (entity._visualX ?? tx) + (tx - (entity._visualX ?? tx)) * Math.min(1, dt * LERP_SPEED);
      entity._visualY = (entity._visualY ?? ty) + (ty - (entity._visualY ?? ty)) * Math.min(1, dt * LERP_SPEED);
    });

    ctx.clearRect(0, 0, w, h);
    drawBackground(ctx, w, h);

    // Filter, calculate positions, and SORT by Y for depth
    const renderList = [...demoState.entities.values()]
      .filter((e) => e && e.room_name)
      .map(entity => ({
        entity,
        pt: layoutEntity(entity, w, h)
      }))
      .sort((a, b) => a.pt.y - b.pt.y); // Y-axis depth sorting

    renderList.forEach(({ entity, pt }) => {
      const player = getEntityPlayer(entity.id);
      if (player) {
        player.update(dt);
        player.render(ctx, pt.x, pt.y, { scale: 1.5 });
        // Nameplate
        ctx.fillStyle = "rgba(0,0,0,0.65)";
        ctx.fillRect(pt.x - 50, pt.y - 75, 100, 16);
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.font = "bold 11px sans-serif";
        ctx.fillText(`${entity.name} (${entity.displayed_pl ?? "?"})`, pt.x, pt.y - 63);
      } else {
        drawEntityFallback(ctx, entity, pt.x, pt.y);
      }
    });

    requestAnimationFrame(tick);
  }

  async function init() {
    if (demoState.initialized) return;
    demoState.initialized = true;
    ensureOverlay();
    attachMessageObserver();

    // Load tile system
    try {
      await window.DBForgedTileSystem?.loadTiles();
      demoState.tileSystemLoaded = true;
      log("Tile system loaded");
    } catch (err) {
      log("Tile system not available:", err.message);
    }

    try {
      const animModule = await loadAnimModule();
      window.DBForgedAnim = animModule;
      demoState.catalog = await loadCatalogWithFallbacks(animModule);
    } catch (err) {
      console.warn(err);
      setStatus(`Animation pack unavailable: ${err.message}. Showing fallback silhouettes.`);
    }

    requestAnimationFrame(tick);
  }

  function waitForWebclient() {
    if (document.readyState === "complete" || document.readyState === "interactive") {
      init();
      return;
    }
    window.addEventListener("DOMContentLoaded", init, { once: true });
  }

  waitForWebclient();
})();
