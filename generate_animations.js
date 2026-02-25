#!/usr/bin/env node
/**
 * DBForged Animation Generator
 * Generates pixel-art sprite sheet animations for characters and attacks.
 * Run: "C:\Program Files\nodejs\node.exe" generate_animations.js
 * No external dependencies — uses only built-in zlib, fs, path.
 *
 * Output structure:
 *   web/static/ui/animations/
 *     characters/  — walk/idle spritesheets (4 frames × 32px = 128×32)
 *     attacks/     — technique effects (N frames × W px)
 */
'use strict'

const zlib = require('zlib')
const fs   = require('fs')
const path = require('path')

const ANIM_DIR = path.join(__dirname, 'web', 'static', 'ui', 'animations')

// ─── PNG Writer ────────────────────────────────────────────────────────────────
const CRC_TABLE = (() => {
  const t = new Uint32Array(256)
  for (let i = 0; i < 256; i++) {
    let c = i
    for (let j = 0; j < 8; j++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1)
    t[i] = c
  }
  return t
})()

function crc32(buf) {
  let c = 0xFFFFFFFF
  for (let i = 0; i < buf.length; i++) c = (c >>> 8) ^ CRC_TABLE[(c ^ buf[i]) & 0xFF]
  return (c ^ 0xFFFFFFFF) >>> 0
}

function mkChunk(type, data) {
  const t = Buffer.from(type, 'ascii')
  const d = Buffer.isBuffer(data) ? data : Buffer.from(data)
  const len = Buffer.alloc(4); len.writeUInt32BE(d.length, 0)
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([t, d])), 0)
  return Buffer.concat([len, t, d, crc])
}

function savePNG(relpath, w, h, px) {
  const rows = []
  for (let y = 0; y < h; y++) {
    rows.push(0)
    for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4
      rows.push(px[i], px[i+1], px[i+2], px[i+3])
    }
  }
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4)
  ihdr[8] = 8; ihdr[9] = 6
  const sig  = Buffer.from([137,80,78,71,13,10,26,10])
  const idat = mkChunk('IDAT', zlib.deflateSync(Buffer.from(rows), { level: 6 }))
  const png  = Buffer.concat([sig, mkChunk('IHDR', ihdr), idat, mkChunk('IEND', Buffer.alloc(0))])
  const fp   = path.join(ANIM_DIR, relpath)
  fs.mkdirSync(path.dirname(fp), { recursive: true })
  fs.writeFileSync(fp, png)
  console.log(`  ✓ ${relpath}`)
}

// ─── Canvas ────────────────────────────────────────────────────────────────────
class Canvas {
  constructor(w, h) {
    this.w = w; this.h = h
    this.px = new Uint8Array(w * h * 4)
  }

  set(x, y, r, g, b, a = 255) {
    if (x < 0 || y < 0 || x >= this.w || y >= this.h) return
    const i = (y * this.w + x) * 4
    this.px[i] = r; this.px[i+1] = g; this.px[i+2] = b; this.px[i+3] = a
  }

  get(x, y) {
    if (x < 0 || y < 0 || x >= this.w || y >= this.h) return [0,0,0,0]
    const i = (y * this.w + x) * 4
    return [this.px[i], this.px[i+1], this.px[i+2], this.px[i+3]]
  }

  rect(x, y, w, h, col) {
    const [r,g,b,a=255] = col
    for (let py = y; py < y+h; py++)
      for (let px = x; px < x+w; px++)
        this.set(px, py, r, g, b, a)
  }

  circle(cx, cy, rad, col) {
    const [r,g,b,a=255] = col
    for (let py = Math.ceil(cy-rad); py <= Math.floor(cy+rad); py++)
      for (let px = Math.ceil(cx-rad); px <= Math.floor(cx+rad); px++)
        if ((px-cx)**2+(py-cy)**2 <= rad*rad)
          this.set(px, py, r, g, b, a)
  }

  // Filled circle with alpha falloff (glow effect)
  glow(cx, cy, rad, col, falloff = 1.5) {
    const [r,g,b] = col
    for (let py = cy-rad; py <= cy+rad; py++)
      for (let px = cx-rad; px <= cx+rad; px++) {
        const dist = Math.sqrt((px-cx)**2+(py-cy)**2)
        if (dist <= rad) {
          const a = Math.floor(255 * Math.pow(1 - dist/rad, falloff))
          this.set(px, py, r, g, b, a)
        }
      }
  }

  // Blend a pixel (alpha compositing)
  blend(x, y, r, g, b, a) {
    if (x < 0 || y < 0 || x >= this.w || y >= this.h) return
    const i = (y * this.w + x) * 4
    const bg = this.px
    const fa = a / 255
    bg[i]   = Math.round(r * fa + bg[i]   * (1 - fa))
    bg[i+1] = Math.round(g * fa + bg[i+1] * (1 - fa))
    bg[i+2] = Math.round(b * fa + bg[i+2] * (1 - fa))
    bg[i+3] = Math.min(255, bg[i+3] + a)
  }

  blendGlow(cx, cy, rad, col, falloff = 1.5) {
    const [r,g,b] = col
    for (let py = cy-rad; py <= cy+rad; py++)
      for (let px = cx-rad; px <= cx+rad; px++) {
        const dist = Math.sqrt((px-cx)**2+(py-cy)**2)
        if (dist <= rad) {
          const a = Math.floor(255 * Math.pow(1 - dist/rad, falloff))
          this.blend(px, py, r, g, b, a)
        }
      }
  }

  // Draw a horizontal beam strip (x0→x1, centered at cy, height h)
  beam(x0, x1, cy, h, col, alphaStart = 255, alphaEnd = 255) {
    const [r,g,b] = col
    for (let px = x0; px < x1; px++) {
      const t  = (px - x0) / (x1 - x0)
      const a  = Math.floor(alphaStart + (alphaEnd - alphaStart) * t)
      const hw = h / 2
      for (let py = cy - hw; py <= cy + hw; py++) {
        const dy   = Math.abs(py - cy) / hw
        const fade = Math.pow(1 - dy, 1.5)
        this.blend(px, py, r, g, b, Math.floor(a * fade))
      }
    }
  }

  noise(x, y, seed = 0) {
    const n = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453
    return n - Math.floor(n)
  }

  // Draw a 2x2 logical "pixel" (scale=2 for 32px sprites on 16-cell grid)
  px2(lx, ly, ox, oy, col) {
    this.rect(ox + lx*2, oy + ly*2, 2, 2, col)
  }

  save(relpath) { savePNG(relpath, this.w, this.h, this.px) }
}

// ─── Color palette ────────────────────────────────────────────────────────────
const K  = [20,20,20]
const W  = [245,245,245]
const SKIN   = [240,196,128]
const SKIN_D = [200,155,85]

// Goku colors
const GK_HR  = [22,22,22]
const GK_OR  = [220,100,25]
const GK_ORD = [175,70,15]
const GK_BL  = [55,100,210]
const GK_BLD = [35,70,165]
const GK_BT  = [165,55,18]
const GK_BTD = [120,35,10]
const GK_PT  = [40,40,40]

// Vegeta colors
const VG_HR  = [18,18,18]
const VG_AR  = [215,225,240]
const VG_ARD = [175,185,205]
const VG_SU  = [40,75,200]
const VG_SUD = [25,50,160]
const VG_BT  = [215,225,240] // white boot

// Piccolo colors
const PC_SK  = [70,160,60]
const PC_SKD = [45,120,40]
const PC_GI  = [115,45,145]
const PC_GID = [80,28,105]
const PC_WH  = [225,225,225]

// Trunks colors
const TR_HR  = [155,95,195]
const TR_HRD = [115,60,155]
const TR_JK  = [45,85,190]
const TR_JKD = [28,55,145]
const TR_PT  = [30,28,45]
const TR_BT  = [35,35,55]

// Attack effect colors
const KI_W   = [255,255,255]
const KI_CY  = [80,220,255]   // cyan (Kamehameha)
const KI_CYD = [30,160,220]
const KI_YW  = [255,235,50]   // yellow (Final Flash)
const KI_YWD = [220,170,10]
const KI_PU  = [180,60,220]   // purple (Galick Gun)
const KI_PUD = [120,30,175]
const KI_OR  = [255,120,20]   // orange (energy aura)
const KI_ORD = [220,80,10]
const KI_GO  = [255,215,30]   // gold (SSJ aura)
const KI_GOD = [200,160,10]
const KI_BL  = [80,150,255]   // blue (generic ki)
const KI_BLD = [40,90,200]

// ─────────────────────────────────────────────────────────────────────────────
//  CHARACTER WALK CYCLES (128×32: 4 frames × 32×32)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Draw a character frame at offset (ox,oy) in the canvas.
 * frame = 0..3 controls leg/arm animation.
 */
function drawGokuFrame(c, ox, oy, frame) {
  // Walk cycle leg offsets: [left_dy, right_dy, left_arm_dx, right_arm_dx]
  const anim = [
    [-2,  2, -1,  1],  // F0: left step
    [ 0,  0,  0,  0],  // F1: passing
    [ 2, -2,  1, -1],  // F2: right step
    [ 0,  0,  0,  0],  // F3: passing
  ][frame]
  const [ldy, rdy, ladx, radx] = anim

  const p = (lx, ly, col) => c.px2(lx, ly, ox, oy, col)

  // ── Hair ──────────────────────────────────────────────────────────────────
  p(4, 0, GK_HR); p(5,0,GK_HR); p(6,0,GK_HR); p(7,0,GK_HR); p(8,0,GK_HR)
  p(3,1,GK_HR); p(4,1,GK_HR); p(5,1,GK_HR); p(6,1,GK_HR); p(7,1,GK_HR); p(8,1,GK_HR); p(9,1,GK_HR)
  p(3,2,GK_HR); p(4,2,K); p(5,2,GK_HR); p(6,2,GK_HR); p(7,2,GK_HR); p(8,2,K); p(9,2,GK_HR)

  // ── Head ──────────────────────────────────────────────────────────────────
  p(3,3,GK_HR); p(4,3,SKIN); p(5,3,SKIN); p(6,3,SKIN); p(7,3,SKIN); p(8,3,SKIN); p(9,3,GK_HR)
  p(3,4,K); p(4,4,SKIN); p(5,4,[30,30,80]); p(6,4,SKIN); p(7,4,[30,30,80]); p(8,4,SKIN); p(9,4,K)
  p(3,5,K); p(4,5,SKIN); p(5,5,SKIN); p(6,5,SKIN); p(7,5,SKIN); p(8,5,SKIN); p(9,5,K)
  p(4,6,K); p(5,6,SKIN); p(6,6,[200,100,80]); p(7,6,SKIN); p(8,6,K)
  p(4,7,K); p(5,7,SKIN); p(6,7,SKIN); p(7,7,SKIN); p(8,7,K)

  // ── Neck + collar ─────────────────────────────────────────────────────────
  p(5,8,K); p(6,8,SKIN); p(7,8,K)
  p(4,9,K); p(5,9,K); p(6,9,K); p(7,9,K); p(8,9,K)

  // ── Left arm (frame-offset: ladx) ─────────────────────────────────────────
  const lax = 2 + ladx
  c.rect(ox + lax*2, oy + 10*2, 4, 8, GK_OR)
  c.rect(ox + lax*2, oy + 17*2, 4, 2, GK_BL) // wristband

  // ── Torso ─────────────────────────────────────────────────────────────────
  for (let lx = 4; lx <= 8; lx++) p(lx, 10, GK_OR)
  for (let lx = 4; lx <= 8; lx++) p(lx, 11, GK_OR)
  for (let lx = 4; lx <= 8; lx++) p(lx, 12, GK_BL)  // belt
  for (let lx = 4; lx <= 8; lx++) p(lx, 13, GK_OR)

  // ── Right arm (frame-offset: radx) ────────────────────────────────────────
  const rax = 10 + radx
  c.rect(ox + rax*2, oy + 10*2, 4, 8, GK_OR)
  c.rect(ox + rax*2, oy + 17*2, 4, 2, GK_BL)

  // ── Left leg (ldy offset) ─────────────────────────────────────────────────
  c.rect(ox + 4*2, oy + 14*2 + ldy, 4, 6, GK_PT)
  c.rect(ox + 3*2, oy + 19*2 + ldy, 6, 3, GK_BT)  // left boot
  c.rect(ox + 3*2, oy + 21*2 + ldy, 6, 1, GK_BTD)

  // ── Right leg (rdy offset) ────────────────────────────────────────────────
  c.rect(ox + 9*2, oy + 14*2 + rdy, 4, 6, GK_PT)
  c.rect(ox + 9*2, oy + 19*2 + rdy, 6, 3, GK_BT)  // right boot
  c.rect(ox + 9*2, oy + 21*2 + rdy, 6, 1, GK_BTD)
}

function drawVegetaFrame(c, ox, oy, frame) {
  const anim = [[-2,2,-1,1],[0,0,0,0],[2,-2,1,-1],[0,0,0,0]][frame]
  const [ldy, rdy, ladx, radx] = anim
  const p = (lx, ly, col) => c.px2(lx, ly, ox, oy, col)

  // Hair (widow's peak)
  p(4,0,VG_HR); p(5,0,VG_HR); p(6,0,VG_HR); p(7,0,VG_HR); p(8,0,VG_HR)
  p(3,1,VG_HR); p(4,1,VG_HR); p(5,1,VG_HR); p(6,1,VG_HR); p(7,1,VG_HR); p(8,1,VG_HR); p(9,1,VG_HR)
  p(3,2,K); p(4,2,VG_HR); p(5,2,VG_HR); p(6,2,VG_HR); p(7,2,VG_HR); p(8,2,VG_HR); p(9,2,K)

  // Head
  p(3,3,K); p(4,3,SKIN); p(5,3,SKIN); p(6,3,SKIN); p(7,3,SKIN); p(8,3,SKIN); p(9,3,K)
  p(3,4,K); p(4,4,SKIN); p(5,4,[30,30,80]); p(6,4,SKIN); p(7,4,[30,30,80]); p(8,4,SKIN); p(9,4,K)
  p(3,5,K); p(4,5,SKIN); p(5,5,SKIN); p(6,5,SKIN_D); p(7,5,SKIN); p(8,5,SKIN); p(9,5,K)
  p(4,6,K); p(5,6,SKIN); p(6,6,SKIN); p(7,6,SKIN); p(8,6,K)
  p(4,7,K); p(5,7,SKIN); p(6,7,SKIN); p(7,7,SKIN); p(8,7,K)

  // Neck
  p(5,8,K); p(6,8,VG_SU); p(7,8,K)
  p(4,9,K); p(5,9,VG_AR); p(6,9,VG_AR); p(7,9,VG_AR); p(8,9,K)

  // Left arm (blue suit)
  const lax = 2 + ladx
  c.rect(ox+lax*2, oy+10*2, 4, 10, VG_SU)
  c.rect(ox+lax*2, oy+18*2, 4, 2, VG_AR) // glove

  // Torso (blue suit + white armor)
  for (let lx = 4; lx <= 8; lx++) {
    p(lx, 10, VG_AR)
    p(lx, 11, VG_AR)
    p(lx, 12, VG_ARD)
    p(lx, 13, VG_SU)
  }
  p(4,10,VG_ARD); p(8,10,VG_ARD) // shoulder shadow

  // Right arm
  const rax = 10 + radx
  c.rect(ox+rax*2, oy+10*2, 4, 10, VG_SU)
  c.rect(ox+rax*2, oy+18*2, 4, 2, VG_AR)

  // Legs (suit)
  c.rect(ox+4*2, oy+14*2+ldy, 4, 6, VG_SU)
  c.rect(ox+4*2, oy+19*2+ldy, 6, 4, VG_BT) // white boot
  c.rect(ox+9*2, oy+14*2+rdy, 4, 6, VG_SU)
  c.rect(ox+9*2, oy+19*2+rdy, 6, 4, VG_BT)
}

function drawPiccoloFrame(c, ox, oy, frame) {
  const anim = [[-2,2,-1,1],[0,0,0,0],[2,-2,1,-1],[0,0,0,0]][frame]
  const [ldy, rdy, ladx, radx] = anim
  const p = (lx, ly, col) => c.px2(lx, ly, ox, oy, col)

  // Antennae
  p(6,0,[90,75,25]); p(7,0,[90,75,25])

  // Head (green)
  p(4,1,PC_SK); p(5,1,PC_SK); p(6,1,PC_SK); p(7,1,PC_SK); p(8,1,PC_SK)
  p(3,2,K); p(4,2,PC_SK); p(5,2,PC_SK); p(6,2,PC_SK); p(7,2,PC_SK); p(8,2,PC_SK); p(9,2,K)
  p(3,3,K); p(4,3,PC_SK); p(5,3,[30,30,80]); p(6,3,PC_SK); p(7,3,[30,30,80]); p(8,3,PC_SK); p(9,3,K)
  p(3,4,K); p(4,4,PC_SK); p(5,4,PC_SK); p(6,4,PC_SK); p(7,4,PC_SK); p(8,4,PC_SK); p(9,4,K)
  p(4,5,K); p(5,5,PC_SK); p(6,5,PC_SKD); p(7,5,PC_SK); p(8,5,K)
  p(4,6,K); p(5,6,PC_SK); p(6,6,PC_SK); p(7,6,PC_SK); p(8,6,K)

  // Cape collar
  p(3,7,PC_WH); p(4,7,PC_WH); p(5,7,K); p(6,7,K); p(7,7,K); p(8,7,PC_WH); p(9,7,PC_WH)

  // Left arm
  const lax = 2 + ladx
  c.rect(ox+lax*2, oy+8*2, 4, 10, PC_GI)
  c.rect(ox+lax*2, oy+17*2, 4, 3, PC_SK) // green hand

  // Torso + cape edges
  p(3,8,PC_WH); for (let lx=4; lx<=8; lx++) p(lx,8,PC_GI); p(9,8,PC_WH)
  p(3,9,PC_WH); for (let lx=4; lx<=8; lx++) p(lx,9,PC_GID); p(9,9,PC_WH)
  p(3,10,PC_WH); for (let lx=4; lx<=8; lx++) p(lx,10,PC_GI); p(9,10,PC_WH)
  for (let lx=4; lx<=8; lx++) p(lx,11,PC_GI)
  for (let lx=4; lx<=8; lx++) p(lx,12,PC_GID)

  // Right arm
  const rax = 10 + radx
  c.rect(ox+rax*2, oy+8*2, 4, 10, PC_GI)
  c.rect(ox+rax*2, oy+17*2, 4, 3, PC_SK)

  // Legs
  c.rect(ox+4*2, oy+13*2+ldy, 4, 6, PC_GID)
  c.rect(ox+4*2, oy+18*2+ldy, 4, 4, K)
  c.rect(ox+9*2, oy+13*2+rdy, 4, 6, PC_GID)
  c.rect(ox+9*2, oy+18*2+rdy, 4, 4, K)
}

function drawTrunksFrame(c, ox, oy, frame) {
  const anim = [[-2,2,-1,1],[0,0,0,0],[2,-2,1,-1],[0,0,0,0]][frame]
  const [ldy, rdy, ladx, radx] = anim
  const p = (lx, ly, col) => c.px2(lx, ly, ox, oy, col)

  // Purple hair (longer)
  p(3,0,TR_HR); p(4,0,TR_HR); p(5,0,TR_HR); p(6,0,TR_HR); p(7,0,TR_HR); p(8,0,TR_HR); p(9,0,TR_HR)
  p(3,1,TR_HRD); p(4,1,TR_HR); p(5,1,TR_HR); p(6,1,TR_HR); p(7,1,TR_HR); p(8,1,TR_HR); p(9,1,TR_HRD)
  p(2,2,TR_HR); p(3,2,K); p(4,2,SKIN); p(5,2,SKIN); p(6,2,SKIN); p(7,2,SKIN); p(8,2,K); p(9,2,TR_HR); p(10,2,TR_HR)

  // Head
  p(3,3,K); p(4,3,SKIN); p(5,3,SKIN); p(6,3,SKIN); p(7,3,SKIN); p(8,3,SKIN); p(9,3,K)
  p(3,4,K); p(4,4,SKIN); p(5,4,[30,30,80]); p(6,4,SKIN); p(7,4,[30,30,80]); p(8,4,SKIN); p(9,4,K)
  p(3,5,K); p(4,5,SKIN); p(5,5,SKIN); p(6,5,SKIN); p(7,5,SKIN); p(8,5,SKIN); p(9,5,K)
  p(4,6,K); p(5,6,SKIN); p(6,6,[200,100,80]); p(7,6,SKIN); p(8,6,K)

  // Collar + neck
  p(4,7,TR_JK); p(5,7,TR_JK); p(6,7,K); p(7,7,TR_JK); p(8,7,TR_JK)

  // Left arm
  const lax = 2 + ladx
  c.rect(ox+lax*2, oy+8*2, 4, 10, TR_JK)
  c.rect(ox+lax*2, oy+17*2, 4, 3, SKIN)

  // Torso (jacket)
  for (let lx=4; lx<=8; lx++) p(lx,8,TR_JK)
  for (let lx=4; lx<=8; lx++) p(lx,9,TR_JKD)
  for (let lx=4; lx<=8; lx++) p(lx,10,TR_JK)
  p(4,10,TR_JKD); p(8,10,TR_JKD)
  for (let lx=4; lx<=8; lx++) p(lx,11,TR_JK)
  for (let lx=4; lx<=8; lx++) p(lx,12,TR_JKD)

  // Right arm
  const rax = 10 + radx
  c.rect(ox+rax*2, oy+8*2, 4, 10, TR_JK)
  c.rect(ox+rax*2, oy+17*2, 4, 3, SKIN)

  // Legs (dark pants)
  c.rect(ox+4*2, oy+13*2+ldy, 4, 7, TR_PT)
  c.rect(ox+4*2, oy+19*2+ldy, 6, 3, TR_BT)
  c.rect(ox+9*2, oy+13*2+rdy, 4, 7, TR_PT)
  c.rect(ox+9*2, oy+19*2+rdy, 6, 3, TR_BT)
}

// ─── Idle animations (subtle aura pulse — same pose, aura grows/shrinks) ─────

function drawIdleFrame(drawCharFn, c, ox, oy, frame, auraCol) {
  // Draw character at frame 1 (neutral standing pose)
  drawCharFn(c, ox, oy, 1)
  // Add aura glow that pulses across frames
  const sizes   = [5, 7, 9, 7]
  const alphas  = [60, 120, 80, 120]
  const aura_r = sizes[frame]
  const aura_a = alphas[frame]
  // Aura glow around torso/feet area
  const cx = ox + 16, cy = oy + 22
  for (let py = cy - aura_r; py <= cy + aura_r; py++)
    for (let px = cx - aura_r*2; px <= cx + aura_r*2; px++) {
      const dx = (px - cx) / 2, dy = py - cy
      if (dx*dx + dy*dy <= aura_r*aura_r) {
        const dist = Math.sqrt(dx*dx + dy*dy) / aura_r
        const a = Math.floor(aura_a * (1 - dist))
        c.blend(px, py, auraCol[0], auraCol[1], auraCol[2], a)
      }
    }
}

// ─── Walk + Idle sprite sheets ───────────────────────────────────────────────

function makeWalkSheet(name, drawFn) {
  const c = new Canvas(128, 32)
  for (let f = 0; f < 4; f++) drawFn(c, f * 32, 0, f)
  c.save(`characters/${name}_walk.png`)
}

function makeIdleSheet(name, drawFn, auraCol) {
  const c = new Canvas(128, 32)
  for (let f = 0; f < 4; f++) drawIdleFrame(drawFn, c, f * 32, 0, f, auraCol)
  c.save(`characters/${name}_idle.png`)
}

// ─────────────────────────────────────────────────────────────────────────────
//  ATTACK EFFECT ANIMATIONS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Ki Blast — 8 frames, 48×48 each → 384×48
 * Expanding energy orb with glow, white core → color → burst
 */
function makeKiBlast(name, innerCol, outerCol) {
  const FRAMES = 8, FW = 48, FH = 48
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    const t = f / (FRAMES - 1)

    if (f < 6) {
      // Growing orb
      const rad = 4 + f * 3.5
      const glowRad = rad + 6
      // Outer glow
      c.blendGlow(ox + cx, cy, glowRad, outerCol, 1.2)
      // Mid glow
      c.blendGlow(ox + cx, cy, rad, innerCol, 1.5)
      // White core
      c.blendGlow(ox + cx, cy, rad * 0.4, KI_W, 2.0)
    } else {
      // Burst frames
      const burstRad = 18 + (f - 5) * 10
      c.blendGlow(ox + cx, cy, burstRad, outerCol, 0.8)
      c.blendGlow(ox + cx, cy, burstRad * 0.6, innerCol, 1.2)
      c.blendGlow(ox + cx, cy, burstRad * 0.3, KI_W, 2.0)
      // Sparks
      for (let sp = 0; sp < 8; sp++) {
        const angle = (sp / 8) * Math.PI * 2
        const sr = burstRad * (0.7 + Math.sin(angle * 3) * 0.2)
        const sx = Math.round(cx + Math.cos(angle) * sr)
        const sy = Math.round(cy + Math.sin(angle) * sr)
        c.blendGlow(ox + sx, sy, 3, KI_W, 2.0)
      }
    }
  }
  c.save(`attacks/${name}.png`)
}

/**
 * Energy Beam — N frames, W×H each.
 * A horizontal beam that builds up from left, widens, then fades.
 * Used for: Kamehameha, Final Flash, Galick Gun
 */
function makeBeam(name, coreCol, outerCol, FRAMES = 12, FW = 128, FH = 64) {
  const c = new Canvas(FRAMES * FW, FH)
  const cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    const t  = f / (FRAMES - 1)

    if (f < 3) {
      // Charge-up: glowing hands / ball on the left
      const rad = 6 + f * 5
      c.blendGlow(ox + 12, cy, rad, outerCol, 1.0)
      c.blendGlow(ox + 12, cy, rad * 0.5, coreCol, 1.5)
      c.blendGlow(ox + 12, cy, rad * 0.25, KI_W, 2.5)
    } else if (f < 7) {
      // Beam extending
      const beamLen = Math.floor((f - 2) / 4 * FW)
      const beamH   = 8 + (f - 2) * 4
      c.beam(ox, ox + beamLen, cy, beamH, coreCol, 200, 80)
      c.beam(ox, ox + beamLen, cy, beamH * 1.8, outerCol, 120, 30)
      c.beam(ox, ox + Math.min(beamLen, 20), cy, beamH * 0.4, KI_W, 255, 180)
    } else if (f < 10) {
      // Full beam
      const alpha = Math.floor(255 - (f - 7) * 30)
      c.beam(ox, ox + FW, cy, 22, coreCol, alpha, Math.floor(alpha * 0.6))
      c.beam(ox, ox + FW, cy, 38, outerCol, Math.floor(alpha * 0.6), Math.floor(alpha * 0.2))
      c.beam(ox, ox + 30, cy, 10, KI_W, alpha, Math.floor(alpha * 0.5))
    } else {
      // Fade out
      const alpha = Math.floor(255 * (1 - (f - 9) / 3))
      c.beam(ox, ox + FW, cy, 16, coreCol, alpha, Math.floor(alpha * 0.3))
      c.beam(ox, ox + FW, cy, 28, outerCol, Math.floor(alpha * 0.5), 0)
    }
  }
  c.save(`attacks/${name}.png`)
}

/**
 * Special Beam Cannon (Piccolo) — spiral drill beam, 10 frames, 96×96
 */
function makeSpecialBeamCannon() {
  const FRAMES = 10, FW = 96, FH = 64
  const c = new Canvas(FRAMES * FW, FH)
  const cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    if (f < 3) {
      // Finger charge
      c.blendGlow(ox + 10, cy, 8 + f*3, [160,30,220], 1.2)
      c.blendGlow(ox + 10, cy, 4 + f*2, [200,80,255], 1.8)
      c.blendGlow(ox + 10, cy, 3, KI_W, 2.5)
    } else {
      // Spiral drill beam — simulate with offset circles along X
      const len = Math.floor((f - 2) / 7 * FW)
      c.beam(ox, ox + len, cy, 6, [150,20,210], 200, 80)
      c.beam(ox, ox + len, cy, 3, [200,80,255], 255, 150)
      // Spiral dots (helical pattern)
      for (let dx = 0; dx < len; dx += 4) {
        const angle = dx * 0.4 + f * 1.5
        const sy1 = cy + Math.round(Math.sin(angle)      * 8)
        const sy2 = cy + Math.round(Math.sin(angle + Math.PI) * 8)
        c.blendGlow(ox + dx, sy1, 3, [220,120,255], 1.8)
        c.blendGlow(ox + dx, sy2, 2, [180,60,230], 1.8)
      }
      c.blendGlow(ox + len, cy, 5, KI_W, 2.5)
    }
  }
  c.save('attacks/special_beam_cannon.png')
}

/**
 * Energy Aura — power-up effect, 8 frames, 80×80 each → 640×80
 * Expanding golden rings with rising particles
 */
function makeEnergyAura(name, col) {
  const FRAMES = 8, FW = 80, FH = 80
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW

    // Expanding ring
    const ringRad = 5 + f * 7
    const ringA   = Math.floor(255 * (1 - f / FRAMES))
    for (let angle = 0; angle < 360; angle += 2) {
      const rad = angle * Math.PI / 180
      const rx  = Math.round(cx + Math.cos(rad) * ringRad)
      const ry  = Math.round(cy + Math.sin(rad) * ringRad * 0.6)
      c.blendGlow(ox + rx, ry, 3, col, 1.5)
    }

    // Inner core glow (brightest at start)
    const coreA = Math.max(0, 220 - f * 28)
    c.blendGlow(ox + cx, cy, Math.max(2, 18 - f * 2), col, 1.2)
    c.blendGlow(ox + cx, cy, Math.max(1, 10 - f * 1), KI_W, 2.0)

    // Rising particles
    for (let p = 0; p < 6; p++) {
      const angle = (p / 6) * Math.PI * 2 + f * 0.6
      const pr    = 10 + Math.sin(f * 0.8 + p) * 8
      const px    = Math.round(cx + Math.cos(angle) * pr)
      const py    = Math.round(cy - f * 3 + Math.sin(f * 1.2 + p * 0.5) * 4)
      c.blendGlow(ox + px, py, 2 + Math.floor(Math.random() * 2), KI_W, 2.5)
      c.blendGlow(ox + px, py + 3, 2, col, 1.8)
    }
  }
  c.save(`attacks/${name}.png`)
}

/**
 * Impact Explosion — 8 frames, 80×80 each
 * White flash → orange burst → sparks → smoke fade
 */
function makeImpact() {
  const FRAMES = 8, FW = 80, FH = 80
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW

    if (f === 0) {
      // White flash
      c.blendGlow(ox + cx, cy, 35, KI_W, 0.8)

    } else if (f < 3) {
      // Expanding burst
      const r1 = f * 14
      c.blendGlow(ox + cx, cy, r1, KI_OR, 0.9)
      c.blendGlow(ox + cx, cy, r1 * 0.7, KI_YW, 1.2)
      c.blendGlow(ox + cx, cy, r1 * 0.4, KI_W, 2.0)
      // Ring
      for (let a = 0; a < 360; a += 3) {
        const rad = a * Math.PI / 180
        c.blendGlow(ox + cx + Math.round(Math.cos(rad)*r1), cy + Math.round(Math.sin(rad)*r1), 3, KI_ORD, 1.5)
      }

    } else if (f < 6) {
      // Fragmenting — sparks and smoke
      const r1 = 30 + (f-2) * 6
      c.blendGlow(ox + cx, cy, r1 * 0.8, KI_OR, 0.7)
      c.blendGlow(ox + cx, cy, r1 * 0.4, KI_YWD, 1.0)
      // Sparks flying outward
      for (let sp = 0; sp < 12; sp++) {
        const angle = (sp / 12) * Math.PI * 2 + f * 0.2
        const sr    = r1 * (0.6 + 0.4 * c.noise(sp, f, 1))
        const sx    = Math.round(cx + Math.cos(angle) * sr)
        const sy    = Math.round(cy + Math.sin(angle) * sr)
        c.blendGlow(ox + sx, sy, 3, KI_YW, 2.0)
        // Trail
        const trail = 0.7
        c.blendGlow(ox + sx - Math.round(Math.cos(angle)*5), sy - Math.round(Math.sin(angle)*5), 2, KI_OR, 1.5)
      }

    } else {
      // Fade out / smoke
      const r1 = 30 + (f - 3) * 5
      const alpha = Math.floor(180 * (1 - (f-5)/3))
      c.blendGlow(ox + cx, cy, r1, [80,60,50], 0.6)
      // Dim sparks
      for (let sp = 0; sp < 6; sp++) {
        const angle = (sp / 6) * Math.PI * 2 + f * 0.3
        const sr    = r1 * 0.9
        c.blendGlow(ox + cx + Math.round(Math.cos(angle)*sr), cy + Math.round(Math.sin(angle)*sr), 2, KI_ORD, 1.8)
      }
    }
  }
  c.save('attacks/impact.png')
}

/**
 * Spirit Bomb (Goku's ultimate) — 10 frames, 96×96
 * Blue energy sphere building up
 */
function makeSpiritBomb() {
  const FRAMES = 10, FW = 96, FH = 96
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    const t  = f / (FRAMES - 1)

    const rad = 5 + f * 4.5
    // Outer glow (light blue)
    c.blendGlow(ox + cx, cy, rad + 12, [100,200,255], 0.8)
    // Main sphere
    c.blendGlow(ox + cx, cy, rad, [50,150,255], 1.2)
    c.blendGlow(ox + cx, cy, rad * 0.7, [120,200,255], 1.5)
    c.blendGlow(ox + cx, cy, rad * 0.3, KI_W, 2.5)

    // Energy lines converging on sphere (planet ki being drawn in)
    for (let line = 0; line < 8; line++) {
      const angle  = (line / 8) * Math.PI * 2 + f * 0.1
      const lineLen = 15 + f * 2
      for (let d = rad; d < rad + lineLen; d += 2) {
        const lx = Math.round(cx + Math.cos(angle) * d)
        const ly = Math.round(cy + Math.sin(angle) * d)
        const a  = Math.floor(160 * (1 - (d - rad) / lineLen))
        c.blend(ox + lx, ly, 100, 200, 255, a)
      }
    }
  }
  c.save('attacks/spirit_bomb.png')
}

/**
 * Destructo Disc (Krillin) — 8 frames, 80×64
 * Spinning golden disc effect
 */
function makeDestructoDisc() {
  const FRAMES = 8, FW = 80, FH = 64
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    const spin = f * 22.5 * Math.PI / 180
    const rad  = 18 + (f < 3 ? f * 3 : 9)

    // Disc shape (ellipse - horizontal)
    for (let angle = 0; angle < 360; angle += 1) {
      const a  = (angle + f * 30) * Math.PI / 180
      const rx = Math.round(cx + Math.cos(a) * rad)
      const ry = Math.round(cy + Math.sin(a) * rad * 0.28) // flat disc
      c.blendGlow(ox + rx, ry, 3, KI_YW, 1.5)
      c.blendGlow(ox + rx, ry, 1, KI_W, 2.5)
    }
    // Disc body fill
    for (let dy = -5; dy <= 5; dy++)
      for (let dx = -rad; dx <= rad; dx++) {
        const fade = 1 - Math.abs(dy) / 5
        c.blend(ox + cx + dx, cy + dy, KI_YWD[0], KI_YWD[1], KI_YWD[2], Math.floor(160 * fade))
      }
    // Center glow
    c.blendGlow(ox + cx, cy, 5, KI_W, 2.5)
  }
  c.save('attacks/destructo_disc.png')
}

/**
 * Solar Flare — 6 frames, 128×96 — blinding white flash
 */
function makeSolarFlare() {
  const FRAMES = 6, FW = 128, FH = 96
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    if (f < 2) {
      // Building up — golden rays
      const rays = 12
      for (let r = 0; r < rays; r++) {
        const angle = (r / rays) * Math.PI * 2
        const len   = 20 + f * 20
        for (let d = 0; d < len; d++) {
          const rx = Math.round(cx + Math.cos(angle) * d)
          const ry = Math.round(cy + Math.sin(angle) * d)
          const a  = Math.floor(200 * (1 - d/len))
          c.blend(ox + rx, ry, 255, 230, 80, a)
        }
      }
      c.blendGlow(ox + cx, cy, 12 + f*6, KI_YW, 1.5)
      c.blendGlow(ox + cx, cy, 6 + f*3, KI_W, 2.5)
    } else if (f < 4) {
      // Full white flash
      const alpha = f === 2 ? 255 : 200
      c.blendGlow(ox + cx, cy, 55, KI_W, 0.5)
      c.blendGlow(ox + cx, cy, 35, KI_W, 0.8)
    } else {
      // Fade with afterimages
      const alpha = Math.floor(180 * (1 - (f-3) / 3))
      c.blendGlow(ox + cx, cy, 40, [255,240,180], 0.7)
    }
  }
  c.save('attacks/solar_flare.png')
}

// ─────────────────────────────────────────────────────────────────────────────
//  TRANSFORMATION AURA EXTENDED PALETTE
// ─────────────────────────────────────────────────────────────────────────────
const KAI_RED  = [225, 25, 10]    // Kaioken red
const GOD_RED  = [200, 35, 35]    // Super Saiyan God red
const SSJ2_LT  = [255, 255, 120]  // SSJ2 lightning yellow
const LSSJ_GR  = [55, 225, 80]    // Legendary Super Saiyan green
const BEAST_VI = [160, 80, 230]   // Beast violet accent
const MAJ_PK   = [230, 70, 180]   // Majin pink
const AND_NE   = [30, 200, 235]   // Android neon cyan
const FROST_CO = [90, 185, 225]   // Frost Demon cold blue
const FROST_VI = [145, 30, 210]   // Frost Demon violet
const KAI_DV   = [240, 215, 130]  // Kai divine gold
const TRU_TE   = [30, 200, 180]   // Truffle teal
const MEGA_PR  = [200, 80, 255]   // Metamoran prismatic purple

// ─────────────────────────────────────────────────────────────────────────────
//  TRANSFORMATION AURA GENERATOR
// ─────────────────────────────────────────────────────────────────────────────
/**
 * makeTransformAura - 8 frames @ 80×80 with visual style variants.
 * style: 'standard'|'electric'|'god'|'violent'|'cold'|'digital'|'chaotic'|'legendary'|'potara'
 */
function makeTransformAura(name, primaryCol, accentCol, style = 'standard') {
  const FRAMES = 8, FW = 80, FH = 80
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2

  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW

    if (style === 'standard' || style === 'god') {
      const ringRad = (style === 'god' ? 4 : 5) + f * (style === 'god' ? 5 : 7)
      for (let angle = 0; angle < 360; angle += 3) {
        const rad = angle * Math.PI / 180
        const rx = Math.round(cx + Math.cos(rad) * ringRad)
        const ry = Math.round(cy + Math.sin(rad) * ringRad * 0.55)
        c.blendGlow(ox + rx, ry, 2, primaryCol, style === 'god' ? 2.0 : 1.5)
      }
      c.blendGlow(ox + cx, cy, Math.max(2, 16 - f * 1.8), primaryCol, 1.2)
      c.blendGlow(ox + cx, cy, Math.max(1, 8 - f), KI_W, 2.5)
      for (let p = 0; p < 5; p++) {
        const angle = (p / 5) * Math.PI * 2 + f * 0.7
        const pr = 8 + Math.sin(f * 0.9 + p) * 6
        const px = Math.round(cx + Math.cos(angle) * pr)
        const py = Math.round(cy - f * 2.5 + Math.sin(f * 1.3 + p * 0.5) * 3)
        c.blendGlow(ox + px, py, 2, KI_W, 2.5)
        c.blendGlow(ox + px, py + 2, 2, primaryCol, 1.8)
      }

    } else if (style === 'electric') {
      const ringRad = 6 + f * 7
      for (let angle = 0; angle < 360; angle += 3) {
        const rad = angle * Math.PI / 180
        const rx = Math.round(cx + Math.cos(rad) * ringRad)
        const ry = Math.round(cy + Math.sin(rad) * ringRad * 0.55)
        c.blendGlow(ox + rx, ry, 2, primaryCol, 1.5)
      }
      c.blendGlow(ox + cx, cy, Math.max(2, 18 - f * 2), primaryCol, 1.2)
      c.blendGlow(ox + cx, cy, Math.max(1, 9 - f), KI_W, 2.5)
      // Lightning bolt arcs
      for (let bolt = 0; bolt < 4; bolt++) {
        const baseAngle = (bolt / 4) * Math.PI * 2 + f * 0.3
        let bx = cx, by = cy
        for (let seg = 0; seg < 5; seg++) {
          const ang = baseAngle + (c.noise(bolt, seg, f) - 0.5) * 1.5
          const len = 5 + c.noise(bolt, seg + 1, f) * 10
          const nbx = bx + Math.cos(ang) * len
          const nby = by + Math.sin(ang) * len * 0.6
          for (let d = 0; d < len; d++) {
            const dx = Math.round(bx + (nbx - bx) * (d / len))
            const dy = Math.round(by + (nby - by) * (d / len))
            c.blend(ox + dx, dy, accentCol[0], accentCol[1], accentCol[2], 200)
            c.blendGlow(ox + dx, dy, 2, KI_W, 2.0)
          }
          bx = nbx; by = nby
        }
      }

    } else if (style === 'violent') {
      const ringRad = 8 + f * 8
      for (let angle = 0; angle < 360; angle += 2) {
        const turbulence = c.noise(angle, f, 2) * 8 - 4
        const rad = angle * Math.PI / 180
        const rx = Math.round(cx + Math.cos(rad) * (ringRad + turbulence))
        const ry = Math.round(cy + Math.sin(rad) * (ringRad + turbulence) * 0.6)
        c.blendGlow(ox + rx, ry, 3, primaryCol, 1.2)
      }
      c.blendGlow(ox + cx, cy, Math.max(3, 22 - f * 2), primaryCol, 0.9)
      c.blendGlow(ox + cx, cy, Math.max(1, 12 - f), KI_W, 2.0)
      for (let p = 0; p < 8; p++) {
        const angle = (p / 8) * Math.PI * 2 + f * 0.5
        const pr = ringRad * (0.6 + c.noise(p, f, 3) * 0.6)
        const px = Math.round(cx + Math.cos(angle) * pr)
        const py = Math.round(cy + Math.sin(angle) * pr * 0.6)
        c.blendGlow(ox + px, py, 3, KI_W, 2.5)
        c.blendGlow(ox + px, py, 4, primaryCol, 1.5)
      }

    } else if (style === 'cold') {
      const ringRad = 5 + f * 6
      for (let angle = 0; angle < 360; angle += 4) {
        const rad = angle * Math.PI / 180
        const rx = Math.round(cx + Math.cos(rad) * ringRad)
        const ry = Math.round(cy + Math.sin(rad) * ringRad * 0.5)
        c.blendGlow(ox + rx, ry, 2, primaryCol, 1.8)
      }
      for (let sh = 0; sh < 6; sh++) {
        const angle = (sh / 6) * Math.PI * 2 + f * 0.15
        const len = 10 + c.noise(sh, f, 4) * 12
        for (let d = 0; d < len; d += 2) {
          const sx = Math.round(cx + Math.cos(angle) * (ringRad * 0.6 + d))
          const sy = Math.round(cy + Math.sin(angle) * (ringRad * 0.5 + d * 0.5))
          const a = Math.floor(220 * (1 - d / len))
          c.blend(ox + sx, sy, accentCol[0], accentCol[1], accentCol[2], a)
          c.blendGlow(ox + sx, sy, 1, KI_W, 2.5)
        }
      }
      c.blendGlow(ox + cx, cy, Math.max(2, 14 - f * 1.5), accentCol, 1.5)

    } else if (style === 'digital') {
      const hexSize = 8
      for (let hy = -4; hy <= 4; hy++) {
        for (let hx = -4; hx <= 4; hx++) {
          const wx = hx * hexSize + (hy % 2 === 0 ? 0 : hexSize / 2)
          const wy = hy * hexSize * 0.87
          const dist = Math.sqrt(wx * wx + wy * wy)
          const ringRad = 6 + f * 5
          if (Math.abs(dist - ringRad) < 3) {
            const a = Math.floor(180 * (1 - Math.abs(dist - ringRad) / 3))
            c.blend(ox + cx + wx, cy + wy, primaryCol[0], primaryCol[1], primaryCol[2], a)
          }
        }
      }
      for (let ly = cy - 20; ly <= cy + 20; ly += 4) {
        const fadeA = Math.floor(80 * (1 - Math.abs(ly - cy) / 20))
        for (let lx = cx - 20; lx <= cx + 20; lx++) {
          const lineFade = 1 - Math.abs(lx - cx) / 20
          c.blend(ox + lx, ly, primaryCol[0], primaryCol[1], primaryCol[2], Math.floor(fadeA * lineFade))
        }
      }
      c.blendGlow(ox + cx, cy, Math.max(2, 10 - f), primaryCol, 2.0)
      c.blendGlow(ox + cx, cy, Math.max(1, 5 - Math.floor(f / 2)), KI_W, 3.0)

    } else if (style === 'chaotic') {
      for (let p = 0; p < 12; p++) {
        const angle = c.noise(p, f, 5) * Math.PI * 2
        const dist  = 5 + c.noise(p + 1, f, 6) * 30
        const px = Math.round(cx + Math.cos(angle) * dist)
        const py = Math.round(cy + Math.sin(angle) * dist * 0.7)
        const size = 2 + Math.floor(c.noise(p, f, 7) * 5)
        c.blendGlow(ox + px, py, size, primaryCol, 1.2)
        if (c.noise(p, f, 8) > 0.5) c.blendGlow(ox + px, py, 2, KI_W, 2.5)
      }
      const coreRad = 5 + Math.abs(Math.sin(f * 1.4)) * 8
      c.blendGlow(ox + cx, cy, Math.max(2, Math.round(coreRad)), primaryCol, 1.0)

    } else if (style === 'legendary') {
      const coreRad = 10 + f * 5
      c.blendGlow(ox + cx, cy, Math.round(coreRad * 0.5), primaryCol, 0.8)
      c.blendGlow(ox + cx, cy, Math.round(coreRad * 0.3), accentCol, 1.2)
      c.blendGlow(ox + cx, cy, Math.round(coreRad * 0.15), KI_W, 2.5)
      const stormRad = 8 + f * 7
      for (let angle = 0; angle < 360; angle += 2) {
        const turbulence = c.noise(angle, f, 9) * 10 - 5
        const rad = angle * Math.PI / 180
        const rx = Math.round(cx + Math.cos(rad) * (stormRad + turbulence))
        const ry = Math.round(cy + Math.sin(rad) * (stormRad + turbulence) * 0.65)
        c.blendGlow(ox + rx, ry, 4, primaryCol, 1.0)
      }
      // Green lightning
      for (let bolt = 0; bolt < 6; bolt++) {
        const angle = (bolt / 6) * Math.PI * 2 + f * 0.4
        let bx = cx, by = cy
        for (let seg = 0; seg < 4; seg++) {
          const ang = angle + (c.noise(bolt, seg, f + 10) - 0.5) * 2.0
          const len = 6 + c.noise(bolt, seg + 1, f + 10) * 8
          const nbx = bx + Math.cos(ang) * len
          const nby = by + Math.sin(ang) * len * 0.7
          for (let d = 0; d < len; d++) {
            const dx = Math.round(bx + (nbx - bx) * (d / len))
            const dy = Math.round(by + (nby - by) * (d / len))
            c.blend(ox + dx, dy, accentCol[0], accentCol[1], accentCol[2], 210)
          }
          bx = nbx; by = nby
        }
      }

    } else if (style === 'potara') {
      for (let ring = 0; ring < 3; ring++) {
        const ringRad = (6 + ring * 8) + f * 5
        for (let angle = 0; angle < 360; angle += 3) {
          const rad = angle * Math.PI / 180
          const rx = Math.round(cx + Math.cos(rad) * ringRad)
          const ry = Math.round(cy + Math.sin(rad) * ringRad * 0.5)
          const col = ring === 0 ? KI_W : ring === 1 ? primaryCol : accentCol
          c.blendGlow(ox + rx, ry, 2, col, 2.0)
        }
      }
      c.blendGlow(ox + cx, cy, Math.max(2, 20 - f * 2), primaryCol, 1.0)
      c.blendGlow(ox + cx, cy, Math.max(1, 10 - f), KI_W, 2.5)
      for (let sp = 0; sp < 8; sp++) {
        const angle = (sp / 8) * Math.PI * 2 + f * 0.4
        const sr = 12 + f * 4
        c.blendGlow(ox + cx + Math.round(Math.cos(angle) * sr), cy + Math.round(Math.sin(angle) * sr * 0.55), 3, KI_W, 2.5)
      }
    }
  }
  c.save(`attacks/${name}.png`)
}

// ─────────────────────────────────────────────────────────────────────────────
//  TECHNIQUE VFX
// ─────────────────────────────────────────────────────────────────────────────

/** Guard Sphere — blue ki bubble, 8 frames @ 512×64 */
function makeGuardSphere() {
  const FRAMES = 8, FW = 64, FH = 64
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2
  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    const rad = Math.round(24 * (Math.sin(f * 0.8) * 0.15 + 0.85))
    for (let angle = 0; angle < 360; angle += 2) {
      const a = angle * Math.PI / 180
      c.blendGlow(ox + Math.round(cx + Math.cos(a) * rad), Math.round(cy + Math.sin(a) * rad * 0.8), 2, KI_BL, 1.5)
    }
    for (let angle = 0; angle < 360; angle += 4) {
      const a = angle * Math.PI / 180
      c.blendGlow(ox + Math.round(cx + Math.cos(a) * rad * 0.7), Math.round(cy + Math.sin(a) * rad * 0.7 * 0.8), 2, KI_CY, 1.8)
    }
    c.blendGlow(ox + cx, cy, Math.round(rad * 0.35), KI_W, 2.5)
    for (let h = 0; h < 6; h++) {
      const ha = (h / 6) * Math.PI * 2 + f * 0.1
      c.blendGlow(ox + cx + Math.round(Math.cos(ha) * rad * 0.55), cy + Math.round(Math.sin(ha) * rad * 0.5), 3, KI_CY, 2.0)
    }
  }
  c.save('attacks/vfx_guard_sphere.png')
}

/** Afterimage Dash — ghost trails, 6 frames @ 576×64 */
function makeAfterimage() {
  const FRAMES = 6, FW = 96, FH = 64
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2
  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    for (let g = 0; g < 4; g++) {
      const gx = ox + cx - g * 18
      const a = Math.floor(180 * (1 - g / 4) * (1 - f / FRAMES * 0.6))
      // Ghost silhouette pixels
      c.blend(gx, cy - 14, 180, 220, 255, a)
      c.blend(gx, cy - 12, 180, 220, 255, a)
      c.blend(gx - 1, cy - 10, 180, 220, 255, a)
      c.blend(gx + 1, cy - 10, 180, 220, 255, a)
      c.blendGlow(gx, cy - 10, 8, KI_CY, 0.8)
    }
    const trailLen = 30 + f * 5
    c.beam(ox, ox + trailLen, cy - 8, 4, KI_W, Math.floor(200 * (1 - f / FRAMES)), 0)
    c.beam(ox, ox + trailLen, cy, 3, KI_CY, Math.floor(150 * (1 - f / FRAMES)), 0)
  }
  c.save('attacks/vfx_afterimage.png')
}

/** Vanish Strike — speed dash + impact, 6 frames @ 576×64 */
function makeVanishStrike() {
  const FRAMES = 6, FW = 96, FH = 64
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2
  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    if (f < 2) {
      c.blendGlow(ox + cx, cy, 15, KI_W, 0.7)
      c.beam(ox, ox + FW, cy, 6, KI_BL, 180, 20)
    } else if (f < 4) {
      const strikeLen = (f - 1) * 30
      c.beam(ox, ox + strikeLen, cy - 5, 8, KI_W, 240, 60)
      c.beam(ox, ox + strikeLen, cy - 5, 14, KI_BL, 180, 20)
      c.blendGlow(ox + strikeLen, cy - 5, 12, KI_W, 1.2)
      c.blendGlow(ox + strikeLen, cy - 5, 20, KI_OR, 0.8)
    } else {
      const bRad = 16 + (f - 3) * 8
      c.blendGlow(ox + cx + 20, cy - 5, bRad, KI_YW, 0.8)
      c.blendGlow(ox + cx + 20, cy - 5, Math.round(bRad * 0.5), KI_W, 1.5)
      for (let sp = 0; sp < 6; sp++) {
        const ang = (sp / 6) * Math.PI * 2 + f
        c.blendGlow(ox + cx + 20 + Math.round(Math.cos(ang) * bRad * 0.7), cy - 5 + Math.round(Math.sin(ang) * bRad * 0.6), 3, KI_OR, 1.8)
      }
    }
  }
  c.save('attacks/vfx_vanish_strike.png')
}

/** Fusion Beam — dual-color combined beam, 12 frames @ 1536×64 */
function makeFusionBeam(name, col1, col2) {
  const FRAMES = 12, FW = 128, FH = 64
  const c = new Canvas(FRAMES * FW, FH)
  const cy = FH / 2
  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    if (f < 3) {
      c.blendGlow(ox + 10, cy - 6, 6 + f * 4, col1, 1.2)
      c.blendGlow(ox + 10, cy + 6, 6 + f * 4, col2, 1.2)
      c.blendGlow(ox + 10, cy, 4 + f * 3, KI_W, 2.5)
    } else if (f < 7) {
      const bLen = Math.floor((f - 2) / 4 * FW)
      c.beam(ox, ox + bLen, cy - 5, 10, col1, 200, 70)
      c.beam(ox, ox + bLen, cy + 5, 10, col2, 200, 70)
      c.beam(ox, ox + bLen, cy, 6, KI_W, 240, 130)
      c.beam(ox, ox + bLen, cy, 24, col1, 100, 20)
    } else if (f < 10) {
      const alpha = Math.floor(255 - (f - 7) * 25)
      c.beam(ox, ox + FW, cy, 28, col1, alpha, Math.floor(alpha * 0.5))
      c.beam(ox, ox + FW, cy, 20, col2, Math.floor(alpha * 0.8), Math.floor(alpha * 0.3))
      c.beam(ox, ox + 30, cy, 12, KI_W, alpha, Math.floor(alpha * 0.6))
    } else {
      const alpha = Math.floor(255 * (1 - (f - 9) / 3))
      c.beam(ox, ox + FW, cy, 18, col1, alpha, Math.floor(alpha * 0.3))
      c.beam(ox, ox + FW, cy, 12, col2, Math.floor(alpha * 0.6), 0)
    }
  }
  c.save(`attacks/${name}.png`)
}

/** Soul Buster — massive purple energy orb, 10 frames @ 960×96 */
function makeSoulBuster() {
  const FRAMES = 10, FW = 96, FH = 96
  const c = new Canvas(FRAMES * FW, FH)
  const cx = FW / 2, cy = FH / 2
  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    const rad = 6 + f * 5
    c.blendGlow(ox + cx, cy, rad + 15, [80, 10, 140], 0.7)
    c.blendGlow(ox + cx, cy, rad, [150, 20, 220], 1.0)
    c.blendGlow(ox + cx, cy, Math.round(rad * 0.6), [200, 80, 255], 1.4)
    c.blendGlow(ox + cx, cy, Math.round(rad * 0.3), KI_W, 2.5)
    for (let swirl = 0; swirl < 6; swirl++) {
      const angle = (swirl / 6) * Math.PI * 2 + f * 0.5
      for (let d = 0; d < rad; d += 3) {
        const spiralAngle = angle + d * 0.15
        const sx = Math.round(cx + Math.cos(spiralAngle) * d)
        const sy = Math.round(cy + Math.sin(spiralAngle) * d)
        c.blend(ox + sx, sy, 180, 30, 255, Math.floor(140 * (1 - d / rad)))
      }
    }
  }
  c.save('attacks/vfx_soul_buster.png')
}

/** Stardust Fall — falling energy barrage, 8 frames @ 768×80 */
function makeStardustFall() {
  const FRAMES = 8, FW = 96, FH = 80
  const c = new Canvas(FRAMES * FW, FH)
  for (let f = 0; f < FRAMES; f++) {
    const ox = f * FW
    for (let p = 0; p < 8; p++) {
      const t = (p / 8 + f * 0.1) % 1.0
      const bx = Math.round(FW * (0.2 + t * 0.6 + p * 0.08))
      const by = Math.round(FH * t)
      const size = 3 + Math.floor(c.noise(p, f, 11) * 3)
      c.blendGlow(ox + bx, by, size, KI_YW, 1.8)
      c.blendGlow(ox + bx, by, size - 1, KI_W, 2.5)
      for (let tr = 1; tr <= 4; tr++) {
        c.blend(ox + bx - tr * 2, by - tr * 3, KI_OR[0], KI_OR[1], KI_OR[2], Math.floor(180 * (1 - tr / 4)))
      }
    }
    for (let imp = 0; imp < 3; imp++) {
      const iy = FH - 8 - f * 2
      if (iy > 0) c.blendGlow(ox + 20 + imp * 28, iy, 5, KI_YW, 1.5)
    }
  }
  c.save('attacks/vfx_stardust.png')
}

// ─────────────────────────────────────────────────────────────────────────────
//  CHARGING AURA OVERLAYS
// ─────────────────────────────────────────────────────────────────────────────
/**
 * makeChargingAura — 8-frame overlay designed to sit on top of character sprites.
 * Frame size: 48×48px (extends 8px beyond 32×32 character bounds on each side).
 * Total sheet: 384×48.
 *
 * style: 'standard'|'electric'|'god'|'legendary'|'cold'|'digital'|'chaotic'
 *
 * Visual layers (per frame):
 *  1. Body aura — ellipse around character silhouette, pulsing in size
 *  2. Flame tendrils — upward-rising wisps from shoulder level
 *  3. Sparks — small energy particles orbiting the aura edge
 *  4. Ground shockwave — expanding ring at feet (frame 3-7)
 *  5. Core glow — tight white-hot center at chest
 */
function makeChargingAura(name, primaryCol, accentCol, style = 'standard') {
  const FRAMES = 8, FW = 48, FH = 48
  const c = new Canvas(FRAMES * FW, FH)

  // Character occupies roughly x:[8,40] y:[8,40] → center at (24,24)
  const CX = FW / 2, CY = FH / 2

  // Pulse cycle: frame 0=small, 3=peak, 6=small (breathe in/out across 8 frames)
  const PULSE = [0.65, 0.75, 0.9, 1.0, 0.95, 0.85, 0.7, 0.75]

  for (let f = 0; f < FRAMES; f++) {
    const ox  = f * FW
    const p   = PULSE[f]
    const inv = 1 - p  // 0 at peak, 0.35 at rest

    // ── 1. Body aura ellipse ────────────────────────────────────────────────
    // Wide enough to wrap character (±16 horizontal, ±20 vertical from center)
    const aW = Math.round(14 * p)   // half-width
    const aH = Math.round(20 * p)   // half-height
    const aAlpha = Math.floor(180 * p)

    if (style === 'electric') {
      // Gold aura ring + jagged edges
      for (let angle = 0; angle < 360; angle += 3) {
        const a = angle * Math.PI / 180
        const jag = 1 + c.noise(angle, f, 0) * 4 - 2  // ±2px jagged edge
        const ex = Math.round(CX + Math.cos(a) * (aW + jag))
        const ey = Math.round(CY + Math.sin(a) * (aH + jag))
        c.blendGlow(ox + ex, ey, 2, primaryCol, 1.8)
      }
      // Lightning inside the aura
      for (let bolt = 0; bolt < 3; bolt++) {
        const bAngle = (bolt / 3) * Math.PI * 2 + f * 0.5
        let bx = CX, by = CY
        for (let seg = 0; seg < 4; seg++) {
          const bAng = bAngle + (c.noise(bolt, seg, f) - 0.5) * 1.2
          const bLen = 4 + c.noise(bolt, seg + 1, f) * 8
          const nbx = bx + Math.cos(bAng) * bLen
          const nby = by + Math.sin(bAng) * bLen * 0.8
          for (let d = 0; d < bLen; d++) {
            const lx = Math.round(bx + (nbx - bx) * (d / bLen))
            const ly = Math.round(by + (nby - by) * (d / bLen))
            c.blend(ox + lx, ly, accentCol[0], accentCol[1], accentCol[2], 200)
          }
          bx = nbx; by = nby
        }
      }

    } else if (style === 'legendary') {
      // Turbulent green storm wrapping the body
      for (let angle = 0; angle < 360; angle += 2) {
        const turb = c.noise(angle, f, 1) * 6 - 3
        const a = angle * Math.PI / 180
        const ex = Math.round(CX + Math.cos(a) * (aW + turb))
        const ey = Math.round(CY + Math.sin(a) * (aH + turb))
        c.blendGlow(ox + ex, ey, 3, primaryCol, 1.2)
      }
      // Inner surge
      c.blendGlow(ox + CX, CY, Math.round(aW * 0.5), primaryCol, 0.8)
      c.blendGlow(ox + CX, CY, Math.round(aW * 0.25), accentCol, 1.5)

    } else if (style === 'cold') {
      // Crystal-edged cold aura
      for (let angle = 0; angle < 360; angle += 5) {
        const a = angle * Math.PI / 180
        const ex = Math.round(CX + Math.cos(a) * aW)
        const ey = Math.round(CY + Math.sin(a) * aH)
        c.blendGlow(ox + ex, ey, 2, primaryCol, 2.0)
      }
      // Crystal spikes from aura edge
      for (let sp = 0; sp < 8; sp++) {
        const a = (sp / 8) * Math.PI * 2 + f * 0.1
        const edgeX = CX + Math.cos(a) * aW
        const edgeY = CY + Math.sin(a) * aH
        const spikeLen = 4 + c.noise(sp, f, 2) * 5
        for (let d = 0; d < spikeLen; d++) {
          const sx = Math.round(edgeX + Math.cos(a) * d)
          const sy = Math.round(edgeY + Math.sin(a) * d)
          c.blend(ox + sx, sy, accentCol[0], accentCol[1], accentCol[2], Math.floor(200 * (1 - d / spikeLen)))
        }
      }

    } else if (style === 'digital') {
      // Hex grid aura outline
      for (let angle = 0; angle < 360; angle += 4) {
        const a = angle * Math.PI / 180
        const ex = Math.round(CX + Math.cos(a) * aW)
        const ey = Math.round(CY + Math.sin(a) * aH)
        c.blendGlow(ox + ex, ey, 2, primaryCol, 2.0)
        if (f % 2 === 0) c.blendGlow(ox + ex, ey, 1, KI_W, 3.0)
      }
      // Scanlines inside character area
      for (let ly = CY - 16; ly <= CY + 16; ly += 3) {
        const fade = Math.floor(60 * (1 - Math.abs(ly - CY) / 16) * p)
        for (let lx = CX - 10; lx <= CX + 10; lx++) {
          const hf = 1 - Math.abs(lx - CX) / 10
          c.blend(ox + lx, ly, primaryCol[0], primaryCol[1], primaryCol[2], Math.floor(fade * hf))
        }
      }

    } else if (style === 'chaotic') {
      // Erratic random energy bursts
      for (let pt = 0; pt < 14; pt++) {
        const a = c.noise(pt, f, 3) * Math.PI * 2
        const r = aW * (0.5 + c.noise(pt + 1, f, 3) * 0.7)
        const ex = Math.round(CX + Math.cos(a) * r)
        const ey = Math.round(CY + Math.sin(a) * r * 1.3)
        c.blendGlow(ox + ex, ey, 2 + Math.floor(c.noise(pt, f, 4) * 3), primaryCol, 1.2)
      }

    } else if (style === 'god') {
      // Clean refined aura — tight, minimal flicker
      for (let angle = 0; angle < 360; angle += 4) {
        const a = angle * Math.PI / 180
        const ex = Math.round(CX + Math.cos(a) * aW)
        const ey = Math.round(CY + Math.sin(a) * aH)
        c.blendGlow(ox + ex, ey, 2, primaryCol, 2.5)
      }
      c.blendGlow(ox + CX, CY, Math.max(1, Math.round(aW * 0.3)), KI_W, 3.0)

    } else {
      // standard — smooth solid body aura ellipse
      for (let angle = 0; angle < 360; angle += 3) {
        const a = angle * Math.PI / 180
        const ex = Math.round(CX + Math.cos(a) * aW)
        const ey = Math.round(CY + Math.sin(a) * aH)
        c.blendGlow(ox + ex, ey, 2, primaryCol, 1.6)
      }
    }

    // ── 2. Flame tendrils (all styles) ───────────────────────────────────────
    // Rise from shoulder-width positions, frame offset adds animation
    for (let t = 0; t < 5; t++) {
      const baseX  = CX + (t - 2) * 5  // spread across character width
      const baseY  = CY - 8             // start at upper-chest / shoulder level
      const height = 8 + Math.round(p * 10) + Math.floor(c.noise(t, f, 5) * 6)
      for (let d = 0; d < height; d++) {
        const wobble = Math.sin((d + f * 2) * 0.6 + t * 1.1) * 2
        const tx = Math.round(baseX + wobble)
        const ty = Math.round(baseY - d)
        const ta = Math.floor(aAlpha * (1 - d / height) * (t === 2 ? 1.0 : 0.7))
        if (ta > 0 && ty >= 0 && ty < FH && tx >= 0 && tx < FW)
          c.blend(ox + tx, ty, primaryCol[0], primaryCol[1], primaryCol[2], ta)
      }
    }

    // ── 3. Orbiting sparks ────────────────────────────────────────────────────
    const sparkCount = style === 'electric' ? 8 : style === 'legendary' ? 10 : 6
    for (let s = 0; s < sparkCount; s++) {
      const a     = (s / sparkCount) * Math.PI * 2 + f * 0.55
      const sr    = aW + 3 + Math.sin(f * 0.9 + s) * 2
      const sxPos = Math.round(CX + Math.cos(a) * sr)
      const syPos = Math.round(CY + Math.sin(a) * sr * 1.2)
      const sa    = Math.floor(200 * p)
      if (sxPos >= 0 && sxPos < FW && syPos >= 0 && syPos < FH)
        c.blendGlow(ox + sxPos, syPos, 2, KI_W, 2.5)
      // Accent spark
      if (accentCol && s % 2 === 0)
        c.blendGlow(ox + sxPos, syPos, 1, accentCol, 2.0)
    }

    // ── 4. Ground shockwave (frames 2-6) ────────────────────────────────────
    if (f >= 2 && f <= 6) {
      const waveRad = (f - 1) * 5
      const waveA   = Math.floor(150 * (1 - (f - 2) / 4))
      for (let angle = 0; angle < 360; angle += 6) {
        const a  = angle * Math.PI / 180
        const wx = Math.round(CX + Math.cos(a) * waveRad)
        const wy = Math.round((CY + 12) + Math.sin(a) * waveRad * 0.3)  // flat ellipse at feet
        if (wx >= 0 && wx < FW && wy >= 0 && wy < FH)
          c.blend(ox + wx, wy, primaryCol[0], primaryCol[1], primaryCol[2], waveA)
      }
    }

    // ── 5. Core chest glow ────────────────────────────────────────────────────
    c.blendGlow(ox + CX, CY, Math.max(1, Math.round(3 * p)), KI_W, 2.5)
    c.blendGlow(ox + CX, CY, Math.max(1, Math.round(6 * p)), primaryCol, 1.5)
  }

  c.save(`attacks/charge_${name}.png`)
}

// ─────────────────────────────────────────────────────────────────────────────
//  MAIN
// ─────────────────────────────────────────────────────────────────────────────

console.log('\nDBForged Animation Generator')
console.log('='.repeat(40))

console.log('\n[Character Walk Cycles]')
makeWalkSheet('goku',    drawGokuFrame)
makeWalkSheet('vegeta',  drawVegetaFrame)
makeWalkSheet('piccolo', drawPiccoloFrame)
makeWalkSheet('trunks',  drawTrunksFrame)

console.log('\n[Character Idle Animations]')
makeIdleSheet('goku',    drawGokuFrame,    KI_OR)   // orange aura
makeIdleSheet('vegeta',  drawVegetaFrame,  KI_BL)   // blue aura
makeIdleSheet('piccolo', drawPiccoloFrame, [100,200,80])  // green aura
makeIdleSheet('trunks',  drawTrunksFrame,  TR_HR)   // purple aura

console.log('\n[Ki Blasts]')
makeKiBlast('ki_blast_blue',   KI_CY,  KI_BLD)
makeKiBlast('ki_blast_gold',   KI_YW,  KI_ORD)
makeKiBlast('ki_blast_purple', KI_PU,  KI_PUD)
makeKiBlast('ki_blast_green',  [80,220,80], [40,160,40])

console.log('\n[Beam Techniques]')
makeBeam('kamehameha_beam',       KI_CY,  KI_BLD)  // cyan/blue
makeBeam('final_flash',           KI_YW,  KI_ORD)  // yellow/gold
makeBeam('galick_gun',            KI_PU,  KI_PUD)  // purple
makeBeam('masenko',               KI_YW,  [200,80,20])  // yellow-orange
makeBeam('burning_attack',        KI_OR,  KI_ORD)  // orange

console.log('\n[Special Techniques]')
makeSpecialBeamCannon()
makeSpiritBomb()
makeDestructoDisc()
makeSolarFlare()

console.log('\n[Aura Effects]')
makeEnergyAura('aura_golden',  KI_GO)   // Super Saiyan
makeEnergyAura('aura_blue',    KI_CY)   // SSB
makeEnergyAura('aura_green',   [80,220,80])  // Potential Unleashed
makeEnergyAura('aura_purple',  KI_PU)   // Legendary SSJ
makeEnergyAura('aura_red',     [220,30,30])  // Rage/Oozaru

console.log('\n[Impact / Hit Effects]')
makeImpact()

console.log('\n[Transformation Auras — Saiyan Line]')
makeTransformAura('aura_kaioken_red',              KAI_RED,           [255, 120, 60],    'standard')
makeTransformAura('aura_ssj_gold',                 KI_GO,             KI_YW,             'standard')
makeTransformAura('aura_ssj2',                     KI_GO,             SSJ2_LT,           'electric')
makeTransformAura('aura_ssj3',                     KI_GO,             KI_YWD,            'violent')
makeTransformAura('aura_ssg_red',                  GOD_RED,           [255, 100, 100],   'god')
makeTransformAura('aura_ssb_blue',                 KI_BL,             KI_CY,             'god')
makeTransformAura('aura_beast_white',              [230, 215, 255],   BEAST_VI,          'electric')

console.log('\n[Transformation Auras — LSSJ Stages]')
makeTransformAura('aura_lssj_green',               LSSJ_GR,           [120, 255, 140],   'legendary')
makeTransformAura('aura_lssj_surge',               LSSJ_GR,           [180, 255, 180],   'legendary')
makeTransformAura('aura_lssj_cataclysm',           [30, 200, 50],     [255, 255, 80],    'legendary')

console.log('\n[Transformation Auras — Other Races]')
makeTransformAura('aura_namekian_jade',             [50, 180, 60],     [100, 220, 100],   'standard')
makeTransformAura('aura_potential_white',           [240, 240, 255],   [200, 220, 255],   'god')
makeTransformAura('aura_max_power',                [220, 120, 50],    [255, 200, 100],   'violent')
makeTransformAura('aura_majin_pink',               MAJ_PK,            [255, 150, 200],   'standard')
makeTransformAura('aura_pure_majin',               [255, 50, 150],    [255, 180, 230],   'chaotic')
makeTransformAura('aura_android_blue',             AND_NE,            KI_CY,             'digital')
makeTransformAura('aura_android_infinite',         [60, 230, 255],    KI_W,              'digital')
makeTransformAura('aura_biodroid_stage2',          [80, 200, 80],     [140, 255, 140],   'standard')
makeTransformAura('aura_biodroid_perfect',         [60, 180, 60],     [30, 220, 80],     'electric')
makeTransformAura('aura_biodroid_super_perfect',   [40, 220, 80],     [200, 255, 100],   'electric')
makeTransformAura('aura_frost_true',               FROST_CO,          KI_W,              'cold')
makeTransformAura('aura_frost_final',              FROST_VI,          FROST_CO,          'cold')
makeTransformAura('aura_gold_frost',               KI_GO,             FROST_VI,          'cold')
makeTransformAura('aura_grey_focus',               [230, 230, 240],   [180, 190, 220],   'god')
makeTransformAura('aura_grey_limit_break',         [200, 50, 30],     [255, 140, 100],   'violent')
makeTransformAura('aura_kai_divine',               KAI_DV,            KI_W,              'potara')
makeTransformAura('aura_kai_empowered',            [255, 230, 150],   KI_W,              'potara')
makeTransformAura('aura_tuffle_teal',              TRU_TE,            [100, 255, 240],   'digital')
makeTransformAura('aura_tuffle_overdrive',         MEGA_PR,           [255, 80, 180],    'chaotic')

console.log('\n[Transformation Auras — Fusion]')
makeTransformAura('aura_potara_gold',              KI_GO,             KI_W,              'potara')
makeTransformAura('aura_metamoran',                MEGA_PR,           KI_GO,             'potara')
makeTransformAura('aura_fusion_ssj',               KI_GO,             KI_W,              'violent')

console.log('\n[Technique VFX]')
makeGuardSphere()
makeAfterimage()
makeVanishStrike()
makeSoulBuster()
makeStardustFall()
makeFusionBeam('vfx_fusion_beam_gold', KI_GO,  KI_W)
makeFusionBeam('vfx_galick_fusion',    KI_PU,  KI_BL)
makeBeam('vfx_kame_wave',   KI_CY, KI_BLD)
makeBeam('vfx_masenko',     KI_YW, [200, 80, 20])

console.log('\n[Charging Aura Overlays — 48×48 character overlays]')
// Base / neutral
makeChargingAura('white',          KI_W,              [200, 220, 255],   'standard')
makeChargingAura('blue',           KI_BL,             KI_CY,             'standard')
// Saiyan line
makeChargingAura('kaioken',        KAI_RED,           [255, 120, 60],    'standard')
makeChargingAura('ssj',            KI_GO,             KI_YW,             'standard')
makeChargingAura('ssj2',           KI_GO,             SSJ2_LT,           'electric')
makeChargingAura('ssj3',           KI_GO,             KI_YWD,            'electric')
makeChargingAura('ssg',            GOD_RED,           [255, 100, 100],   'god')
makeChargingAura('ssb',            KI_BL,             KI_CY,             'god')
makeChargingAura('beast',          [230, 215, 255],   BEAST_VI,          'electric')
// LSSJ stages
makeChargingAura('lssj',           LSSJ_GR,           [120, 255, 140],   'legendary')
makeChargingAura('lssj_cataclysm', [30, 200, 50],     [255, 255, 80],    'legendary')
// Other races
makeChargingAura('namekian',       [50, 180, 60],     [100, 220, 100],   'standard')
makeChargingAura('potential',      [240, 240, 255],   [200, 220, 255],   'god')
makeChargingAura('majin',          MAJ_PK,            [255, 150, 200],   'standard')
makeChargingAura('pure_majin',     [255, 50, 150],    [255, 180, 230],   'chaotic')
makeChargingAura('android',        AND_NE,            KI_CY,             'digital')
makeChargingAura('biodroid',       [80, 200, 80],     [140, 255, 140],   'digital')
makeChargingAura('frost',          FROST_CO,          KI_W,              'cold')
makeChargingAura('frost_golden',   KI_GO,             FROST_VI,          'cold')
makeChargingAura('grey',           [230, 230, 240],   [180, 190, 220],   'god')
makeChargingAura('kai',            KAI_DV,            KI_W,              'god')
makeChargingAura('truffle',        TRU_TE,            [100, 255, 240],   'digital')
// Fusion
makeChargingAura('potara',         KI_GO,             KI_W,              'god')
makeChargingAura('metamoran',      MEGA_PR,           KI_GO,             'electric')

console.log('\n✓ All animations generated.\n')
