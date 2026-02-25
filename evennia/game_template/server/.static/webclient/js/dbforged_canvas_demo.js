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
          demoState.canvas.style.height = "240px";
          setTimeout(resizeCanvas, 10);
        }
      }
      const entity = packet.entity;
      const prev = demoState.entities.get(entity.id) || {};
      demoState.entities.set(entity.id, { ...prev, ...entity, _seenAt: performance.now() });

      const player = getEntityPlayer(entity.id);
      if (player) {
        // Movement state is inferred from position changes; server currently sends stub positions.
        const moved = prev.position && entity.position &&
          (prev.position.x !== entity.position.x || prev.position.y !== entity.position.y);
        player.applyState(moved ? "moving" : "idle");
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

  function layoutEntity(entity, index, count, canvasW, canvasH) {
    // Server currently sends stub positions. Spread entities along a stage line.
    const stageY = Math.floor(canvasH * 0.82);
    const left = Math.floor(canvasW * 0.10);
    const right = Math.floor(canvasW * 0.90);
    const slot = count <= 1 ? 0.5 : index / Math.max(1, count - 1);
    const x = Math.floor(left + (right - left) * slot);
    return { x, y: stageY };
  }

  function drawBackground(ctx, w, h) {
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, "#0a1324");
    g.addColorStop(0.55, "#13203d");
    g.addColorStop(1, "#2f4f6f");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);

    // Ground strip
    const groundY = Math.floor(h * 0.82);
    const gg = ctx.createLinearGradient(0, groundY, 0, h);
    gg.addColorStop(0, "#56794f");
    gg.addColorStop(1, "#2f4a2b");
    ctx.fillStyle = gg;
    ctx.fillRect(0, groundY, w, h - groundY);
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

    ctx.clearRect(0, 0, w, h);
    drawBackground(ctx, w, h);

    const entities = [...demoState.entities.values()]
      .filter((e) => e && e.room_name) // only roomed entities
      .sort((a, b) => Number(a.id) - Number(b.id));

    entities.forEach((entity, idx) => {
      const pt = layoutEntity(entity, idx, entities.length, w, h);
      const player = getEntityPlayer(entity.id);
      if (player) {
        player.update(dt);
        player.render(ctx, pt.x, pt.y, { scale: 1 });
        // Nameplate
        ctx.fillStyle = "rgba(0,0,0,0.55)";
        ctx.fillRect(pt.x - 42, pt.y - 52, 84, 14);
        ctx.fillStyle = "#dfeaff";
        ctx.textAlign = "center";
        ctx.font = "11px monospace";
        ctx.fillText(`${entity.name} PL:${entity.displayed_pl ?? entity.pl ?? "?"}`, pt.x, pt.y - 41);
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
