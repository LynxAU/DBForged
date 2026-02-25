/**
 * DBForged sprite animation loader + player + event/state mapping.
 *
 * Expected pack layout (default):
 *   goku_placeholder_pack/
 *     anim.json
 *     animations/<anim_name>/*.png
 *
 * Usage:
 *   const catalog = await loadAnimationCatalog("/static/ui/animations/goku_placeholder_pack");
 *   const player = new AnimationPlayer({ catalog, spriteId: "goku_placeholder" });
 *   player.setAnimation("base_action_row01");
 *   player.update(dtSec);
 *   player.render(ctx, feetX, feetY);
 */

const DEFAULT_FPS = 12;
const DEFAULT_LOOP = true;

export const DEFAULT_ANIMATION_MAPPING = {
  // Exact overrides win first. Set to explicit anim names from your pack.
  overrides: {
    idle: null,
    moving: null,
    charge_start: null,
    beam_fire: null,
  },
  // Heuristic selectors used when no override is configured.
  selectors: {
    charge_start: ["_charge_"],
    beam_fire: ["_beam_"],
    moving: ["base_action_row"],
    idle: ["base_action_row"],
  },
  // Optional priority patterns for tie-breaking.
  prefer: {
    idle: ["idle", "stand", "base_action_row"],
    moving: ["run", "walk", "move", "base_action_row"],
    charge_start: ["charge", "powerup"],
    beam_fire: ["beam", "kame", "blast"],
  },
};

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function normalizeUrlPath(...parts) {
  return parts
    .filter(Boolean)
    .join("/")
    .replace(/\\/g, "/")
    .replace(/\/{2,}/g, "/")
    .replace(":/", "://");
}

function toNameList(obj) {
  return Array.isArray(obj) ? obj : [];
}

function preloadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    img.src = url;
  });
}

function sortedFrameUrls(frameEntries = []) {
  return [...frameEntries].sort((a, b) => {
    const an = a.order ?? a.index ?? 0;
    const bn = b.order ?? b.index ?? 0;
    if (an !== bn) return an - bn;
    return String(a.file || a.path || "").localeCompare(String(b.file || b.path || ""), undefined, {
      numeric: true,
      sensitivity: "base",
    });
  });
}

function normalizeAnchorPx(anchor, width, height) {
  // Accepts pixels ({x,y}) or normalized ({x:0.5,y:1}) values.
  if (!anchor || typeof anchor !== "object") {
    return { x: Math.round(width * 0.5), y: height };
  }
  let x = anchor.x;
  let y = anchor.y;
  if (typeof x !== "number") x = 0.5;
  if (typeof y !== "number") y = 1.0;
  if (x >= 0 && x <= 1) x = Math.round(width * x);
  if (y >= 0 && y <= 1) y = Math.round(height * y);
  return { x, y };
}

function normalizeManifest(raw, packRootUrl) {
  const manifest = raw || {};
  const animRoot = normalizeUrlPath(packRootUrl, "animations");
  const animations = {};

  // Support object or array format
  let entries = [];
  if (Array.isArray(manifest.animations)) {
    entries = manifest.animations.map((a) => [a.name, a]);
  } else if (manifest.animations && typeof manifest.animations === "object") {
    entries = Object.entries(manifest.animations);
  } else {
    entries = [];
  }

  for (const [animNameRaw, dataRaw] of entries) {
    const data = dataRaw || {};
    const animName = String(animNameRaw || data.name || "").trim();
    if (!animName) continue;

    let frames = [];
    if (Array.isArray(data.frames)) {
      frames = data.frames.map((f, idx) => {
        if (typeof f === "string") {
          return { file: f, order: idx };
        }
        return { ...f, order: f.order ?? f.index ?? idx };
      });
    }

    frames = sortedFrameUrls(frames).map((frame, idx) => {
      const file = frame.file || frame.path || frame.png || frame.image || "";
      const rel = String(file).replace(/^\.?\//, "");
      const url = /^https?:\/\//i.test(rel)
        ? rel
        : normalizeUrlPath(animRoot, animName, rel || `${animName}_${String(idx + 1).padStart(2, "0")}.png`);
      return {
        index: idx,
        file: rel,
        url,
        duration: typeof frame.duration === "number" ? frame.duration : null,
        anchor: frame.anchor || frame.anchor_px || null,
      };
    });

    animations[animName] = {
      name: animName,
      fps: Number(data.fps) || Number(manifest.default_fps) || DEFAULT_FPS,
      loop: typeof data.loop === "boolean" ? data.loop : (typeof manifest.default_loop === "boolean" ? manifest.default_loop : DEFAULT_LOOP),
      anchor: data.anchor || data.anchor_px || manifest.anchor || manifest.anchor_px || null,
      frames,
      meta: data.meta || {},
    };
  }

  return {
    packName: manifest.pack_name || manifest.name || "animation_pack",
    spriteId: manifest.sprite_id || manifest.sprite || null,
    version: manifest.version || 1,
    defaultFps: Number(manifest.default_fps) || DEFAULT_FPS,
    defaultLoop: typeof manifest.default_loop === "boolean" ? manifest.default_loop : DEFAULT_LOOP,
    packRootUrl,
    animations,
  };
}

export async function loadAnimationCatalog(packRootUrl, options = {}) {
  const manifestUrl = options.manifestUrl || normalizeUrlPath(packRootUrl, "anim.json");
  const resp = await fetch(manifestUrl, { cache: options.cache || "no-cache" });
  if (!resp.ok) {
    throw new Error(`Failed to load anim manifest: ${manifestUrl} (${resp.status})`);
  }
  const raw = await resp.json();
  const normalized = normalizeManifest(raw, packRootUrl);

  const preload = options.preload !== false;
  const imageCache = new Map();

  if (preload) {
    const loads = [];
    for (const anim of Object.values(normalized.animations)) {
      for (const frame of anim.frames) {
        loads.push(
          preloadImage(frame.url)
            .then((img) => imageCache.set(frame.url, img))
            .catch((err) => {
              if (!options.ignoreMissingFrames) throw err;
              console.warn(err);
            })
        );
      }
    }
    await Promise.all(loads);
  }

  return {
    ...normalized,
    imageCache,
    getAnimation(name) {
      return this.animations[name] || null;
    },
    getImage(frameUrl) {
      return this.imageCache.get(frameUrl) || null;
    },
    async ensureFrameImage(frame) {
      if (!frame) return null;
      const cached = this.getImage(frame.url);
      if (cached) return cached;
      const img = await preloadImage(frame.url);
      this.imageCache.set(frame.url, img);
      return img;
    },
    listAnimationNames() {
      return Object.keys(this.animations);
    },
  };
}

function scoreAnimationName(animName, triggerKey, mapping) {
  const lower = animName.toLowerCase();
  let score = 0;
  const prefers = toNameList(mapping?.prefer?.[triggerKey]);
  prefers.forEach((needle, i) => {
    if (lower.includes(String(needle).toLowerCase())) score += (prefers.length - i) * 10;
  });
  // Reward shorter names slightly to avoid weird noisy variants.
  score -= lower.length * 0.02;
  return score;
}

function selectHeuristicAnimation(catalog, triggerKey, mapping, { loopsOnly = false } = {}) {
  const names = catalog.listAnimationNames();
  const needles = toNameList(mapping?.selectors?.[triggerKey]).map((s) => String(s).toLowerCase());
  let candidates = names.filter((name) => {
    const lower = name.toLowerCase();
    return needles.length ? needles.some((n) => lower.includes(n)) : true;
  });
  if (loopsOnly) {
    candidates = candidates.filter((name) => catalog.getAnimation(name)?.loop !== false);
  }
  if (!candidates.length) return null;
  candidates.sort((a, b) => scoreAnimationName(b, triggerKey, mapping) - scoreAnimationName(a, triggerKey, mapping));
  return candidates[0];
}

export function resolveAnimationForEvent(catalog, eventName, mapping = DEFAULT_ANIMATION_MAPPING) {
  const key = String(eventName || "").trim();
  if (!key) return null;
  const override = mapping?.overrides?.[key];
  if (override && catalog.getAnimation(override)) return override;
  return selectHeuristicAnimation(catalog, key, mapping, { loopsOnly: false });
}

export function resolveAnimationForState(catalog, stateName, mapping = DEFAULT_ANIMATION_MAPPING) {
  const key = String(stateName || "").trim();
  if (!key) return null;
  const override = mapping?.overrides?.[key];
  if (override && catalog.getAnimation(override)) return override;
  const exact = selectHeuristicAnimation(catalog, key, mapping, { loopsOnly: true });
  if (exact) return exact;
  return (
    selectHeuristicAnimation(catalog, key, mapping, { loopsOnly: false }) ||
    catalog.listAnimationNames().find((name) => catalog.getAnimation(name)?.loop !== false) ||
    catalog.listAnimationNames()[0] ||
    null
  );
}

export function createDefaultAnimationConfig(overrides = {}) {
  return {
    ...DEFAULT_ANIMATION_MAPPING,
    overrides: {
      ...DEFAULT_ANIMATION_MAPPING.overrides,
      ...(overrides.overrides || {}),
    },
    selectors: {
      ...DEFAULT_ANIMATION_MAPPING.selectors,
      ...(overrides.selectors || {}),
    },
    prefer: {
      ...DEFAULT_ANIMATION_MAPPING.prefer,
      ...(overrides.prefer || {}),
    },
  };
}

export class AnimationPlayer {
  constructor({
    catalog,
    spriteId = null,
    mappingConfig = DEFAULT_ANIMATION_MAPPING,
    scale = 1,
    anchorOffset = { x: 0, y: 0 },
  } = {}) {
    if (!catalog) throw new Error("AnimationPlayer requires a loaded catalog.");
    this.catalog = catalog;
    this.spriteId = spriteId || catalog.spriteId || "unknown_sprite";
    this.mappingConfig = mappingConfig;
    this.scale = scale;
    this.anchorOffset = anchorOffset;

    this.currentAnimationName = null;
    this.currentAnimation = null;
    this.currentFrameIndex = 0;
    this.elapsed = 0;
    this.finished = false;
    this.currentImage = null;
    this.pendingLoad = null;
  }

  set_animation(animName) {
    const anim = this.catalog.getAnimation(animName);
    if (!anim) {
      console.warn(`[AnimationPlayer] Unknown animation '${animName}' for sprite '${this.spriteId}'.`);
      return false;
    }
    if (this.currentAnimationName === animName && this.currentAnimation) {
      return true;
    }
    this.currentAnimationName = animName;
    this.currentAnimation = anim;
    this.currentFrameIndex = 0;
    this.elapsed = 0;
    this.finished = false;
    this.currentImage = null;
    this.pendingLoad = null;
    this.#ensureCurrentFrameImage();
    return true;
  }

  setAnimation(animName) {
    return this.set_animation(animName);
  }

  applyServerTechniqueEvent(eventName) {
    const animName = resolveAnimationForEvent(this.catalog, eventName, this.mappingConfig);
    if (animName) this.set_animation(animName);
    return animName;
  }

  applyState(stateName) {
    const animName = resolveAnimationForState(this.catalog, stateName, this.mappingConfig);
    if (animName) this.set_animation(animName);
    return animName;
  }

  update(dt) {
    if (!this.currentAnimation || this.finished) return;
    const dtSec = Math.max(0, Number(dt) || 0);
    if (dtSec <= 0) return;

    this.elapsed += dtSec;

    let advanced = false;
    while (true) {
      const frame = this.getCurrentFrame();
      if (!frame) break;
      const frameDur = this.#getFrameDurationSec(frame, this.currentAnimation);
      if (this.elapsed < frameDur) break;
      this.elapsed -= frameDur;
      this.currentFrameIndex += 1;
      advanced = true;

      if (this.currentFrameIndex >= this.currentAnimation.frames.length) {
        if (this.currentAnimation.loop) {
          this.currentFrameIndex = 0;
        } else {
          this.currentFrameIndex = Math.max(0, this.currentAnimation.frames.length - 1);
          this.finished = true;
          this.elapsed = 0;
          break;
        }
      }
    }

    if (advanced) this.#ensureCurrentFrameImage();
  }

  getCurrentFrame() {
    if (!this.currentAnimation) return null;
    return this.currentAnimation.frames[this.currentFrameIndex] || null;
  }

  getCurrentFrameImage() {
    return this.currentImage;
  }

  render(ctx, feetX, feetY, opts = {}) {
    // Render current_frame_png at an anchor point (feet aligned).
    if (!ctx) return;
    const frame = this.getCurrentFrame();
    if (!frame) return;
    const img = this.currentImage || this.catalog.getImage(frame.url);
    if (!img) {
      this.#ensureCurrentFrameImage();
      return;
    }

    const scale = opts.scale ?? this.scale;
    const drawW = (opts.width ?? img.width) * scale;
    const drawH = (opts.height ?? img.height) * scale;

    const anchorSrc = frame.anchor || this.currentAnimation.anchor || { x: 0.5, y: 1.0 };
    const anchorPx = normalizeAnchorPx(anchorSrc, img.width, img.height);

    const offX = (opts.anchorOffset?.x ?? this.anchorOffset.x ?? 0);
    const offY = (opts.anchorOffset?.y ?? this.anchorOffset.y ?? 0);

    const drawX = Math.round(feetX - (anchorPx.x * scale) + offX);
    const drawY = Math.round(feetY - (anchorPx.y * scale) + offY);

    ctx.drawImage(img, drawX, drawY, drawW, drawH);
  }

  #getFrameDurationSec(frame, anim) {
    if (typeof frame.duration === "number" && frame.duration > 0) return frame.duration;
    const fps = clamp(Number(anim.fps) || this.catalog.defaultFps || DEFAULT_FPS, 1, 120);
    return 1 / fps;
  }

  #ensureCurrentFrameImage() {
    const frame = this.getCurrentFrame();
    if (!frame) return;
    const cached = this.catalog.getImage(frame.url);
    if (cached) {
      this.currentImage = cached;
      return;
    }
    if (this.pendingLoad === frame.url) return;
    this.pendingLoad = frame.url;
    this.catalog
      .ensureFrameImage(frame)
      .then((img) => {
        if (this.pendingLoad === frame.url) {
          this.currentImage = img;
        }
      })
      .catch((err) => console.warn(err))
      .finally(() => {
        if (this.pendingLoad === frame.url) this.pendingLoad = null;
      });
  }
}

export default {
  loadAnimationCatalog,
  AnimationPlayer,
  DEFAULT_ANIMATION_MAPPING,
  createDefaultAnimationConfig,
  resolveAnimationForEvent,
  resolveAnimationForState,
};
