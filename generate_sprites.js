#!/usr/bin/env node
/**
 * DBForged Sprite Generator
 * Generates pixel-art PNG sprites for all zones and characters.
 * Run: "C:\Program Files\nodejs\node.exe" generate_sprites.js
 * No external dependencies — uses only built-in zlib, fs, path.
 */
'use strict'

const zlib = require('zlib')
const fs   = require('fs')
const path = require('path')

const SPRITES_DIR = path.join(__dirname, 'web', 'static', 'ui', 'sprites')

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
  ihdr[8] = 8; ihdr[9] = 6 // 8-bit RGBA
  const sig  = Buffer.from([137,80,78,71,13,10,26,10])
  const idat = mkChunk('IDAT', zlib.deflateSync(Buffer.from(rows), { level: 6 }))
  const png  = Buffer.concat([sig, mkChunk('IHDR', ihdr), idat, mkChunk('IEND', Buffer.alloc(0))])
  const fp   = path.join(SPRITES_DIR, relpath)
  fs.mkdirSync(path.dirname(fp), { recursive: true })
  fs.writeFileSync(fp, png)
  console.log(`  ✓ ${relpath}`)
}

// ─── Canvas class ─────────────────────────────────────────────────────────────
class C {
  constructor(w, h) {
    this.w = w; this.h = h
    this.px = new Uint8Array(w * h * 4)
  }

  set(x, y, r, g, b, a = 255) {
    if (x < 0 || y < 0 || x >= this.w || y >= this.h) return
    const i = (y * this.w + x) * 4
    this.px[i] = r; this.px[i+1] = g; this.px[i+2] = b; this.px[i+3] = a
  }

  fill(r, g, b, a = 255) {
    for (let i = 0; i < this.w * this.h; i++) {
      this.px[i*4] = r; this.px[i*4+1] = g; this.px[i*4+2] = b; this.px[i*4+3] = a
    }
  }

  rect(x, y, w, h, col) {
    const [r,g,b,a=255] = col
    for (let py = y; py < y+h; py++)
      for (let px = x; px < x+w; px++)
        this.set(px, py, r, g, b, a)
  }

  circle(cx, cy, rad, col) {
    const [r,g,b,a=255] = col
    for (let py = cy-rad; py <= cy+rad; py++)
      for (let px = cx-rad; px <= cx+rad; px++)
        if ((px-cx)**2+(py-cy)**2 <= rad*rad)
          this.set(px, py, r, g, b, a)
  }

  // Draw a logical pixel on a scaled grid
  px2(lx, ly, s, col) { this.rect(lx*s, ly*s, s, s, col) }

  // Simple noise for terrain variation (deterministic)
  noise(x, y, seed = 0) {
    const n = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453
    return n - Math.floor(n)
  }

  save(relpath) { savePNG(relpath, this.w, this.h, this.px) }
}

// ─── Color palette ────────────────────────────────────────────────────────────
const P = {
  T:   [0,0,0,0],         // transparent
  K:   [20,20,20],        // near-black outline
  W:   [240,240,240],     // white

  // Skin tones
  SKIN:   [240,196,128],
  SKIN_D: [200,155,85],
  SKIN_S: [255,215,155],  // skin shadow

  // Goku
  GK_OR:  [220,100,25],   // orange gi
  GK_ORD: [175,70,15],    // orange dark
  GK_BL:  [55,100,210],   // blue belt/wristbands
  GK_BLD: [35,70,165],    // blue dark
  GK_BT:  [165,55,18],    // red-brown boot
  GK_BTD: [120,35,10],    // boot dark
  GK_HR:  [22,22,22],     // hair
  GK_PT:  [40,40,40],     // dark pants

  // Vegeta
  VG_AR:  [215,225,240],  // white armor
  VG_ARD: [175,185,205],  // armor shadow
  VG_SU:  [40,75,200],    // blue bodysuit
  VG_SUD: [25,50,160],    // suit dark
  VG_HR:  [18,18,18],     // hair black

  // Piccolo
  PC_SK:  [70,160,60],    // green skin
  PC_SKD: [45,120,40],    // skin dark
  PC_GI:  [115,45,145],   // purple gi
  PC_GID: [80,28,105],    // gi dark
  PC_WH:  [225,225,225],  // cape/turban white

  // Training dummies
  DM_GR:  [140,145,150],  // dummy grey
  DM_GRD: [90,95,100],    // dummy dark
  DM_GRL: [185,190,195],  // dummy light
  DM_RD:  [220,30,30],    // indicator red
  DM2_BL: [30,120,220],   // MK2 blue tech

  // Monkey
  MK_BR:  [130,85,45],    // monkey brown
  MK_BRD: [90,55,25],     // dark brown
  MK_FC:  [200,150,100],  // face lighter
  MK_EY:  [200,50,10],    // red eyes
  MK_TH:  [240,235,175],  // teeth

  // Boar
  BR_BK:  [65,55,45],     // boar dark
  BR_BKD: [40,32,25],     // darker
  BR_IV:  [230,220,165],  // ivory tusks
  BR_SN:  [120,60,55],    // snout pink-brown
  BR_EY:  [220,35,15],    // red eyes

  // Terrain
  SND:    [222,198,122],
  SND_D:  [192,168,92],
  SND_L:  [242,218,148],
  GRS:    [60,138,35],
  GRS_D:  [42,108,22],
  GRS_L:  [75,165,48],
  WTR:    [38,125,205],
  WTR_L:  [55,148,228],
  WTR_D:  [25,95,170],
  MTL:    [100,118,138],
  MTL_D:  [70,88,108],
  MTL_L:  [135,158,178],
  MTL_B:  [40,100,200],   // blue tech accent
  LAB:    [200,222,238],
  LAB_D:  [170,195,215],
  LAB_L:  [220,238,250],
  LAB_B:  [0,174,255],
  ALN:    [32,200,68],    // alien grass
  ALN_D:  [22,158,50],
  ALN_L:  [52,228,90],
  ALN_P:  [130,60,200],   // purple alien accent
  FOR:    [38,80,22],     // forest floor
  FOR_D:  [22,52,12],
  FOR_L:  [55,105,35],
  FOR_R:  [72,45,18],     // root brown
  DRT:    [142,102,55],
  DRT_D:  [108,75,32],
  DRT_L:  [170,128,75],
  MIL:    [72,70,52],     // military olive
  MIL_D:  [50,48,34],
  MIL_R:  [165,18,18],    // red ribbon accent
}

// ─────────────────────────────────────────────────────────────────────────────
//  TERRAIN TILES (64×64)
// ─────────────────────────────────────────────────────────────────────────────

function tileMetal() {
  const c = new C(64, 64)
  c.fill(...P.MTL)
  // Grid seams every 16px
  for (let i = 0; i < 64; i += 16) {
    c.rect(i, 0, 1, 64, P.MTL_D)
    c.rect(0, i, 64, 1, P.MTL_D)
  }
  // Highlight seam (offset by 1)
  for (let i = 0; i < 64; i += 16) {
    c.rect(i+1, 0, 1, 64, P.MTL_L)
    c.rect(0, i+1, 64, 1, P.MTL_L)
  }
  // Corner bolts
  for (let gx = 0; gx < 4; gx++) for (let gy = 0; gy < 4; gy++) {
    const bx = gx * 16 + 7, by = gy * 16 + 7
    c.circle(bx, by, 2, P.MTL_L)
    c.circle(bx, by, 1, P.MTL_D)
  }
  // Subtle blue tech accent lines
  c.rect(8, 0, 1, 64, [P.MTL_B[0], P.MTL_B[1], P.MTL_B[2], 60])
  c.rect(40, 0, 1, 64, [P.MTL_B[0], P.MTL_B[1], P.MTL_B[2], 60])
  c.save('Capsule Corp/metal.png')
}

function tileLab() {
  const c = new C(64, 64)
  c.fill(...P.LAB)
  // Clean grid every 16px
  for (let i = 0; i < 64; i += 16) {
    c.rect(i, 0, 1, 64, P.LAB_D)
    c.rect(0, i, 64, 1, P.LAB_D)
  }
  // Blue accent dots at intersections
  for (let gx = 0; gx < 4; gx++) for (let gy = 0; gy < 4; gy++) {
    c.circle(gx * 16, gy * 16, 2, [P.LAB_B[0], P.LAB_B[1], P.LAB_B[2], 180])
  }
  // Sheen strip
  c.rect(0, 0, 64, 2, P.LAB_L)
  c.rect(0, 0, 2, 64, P.LAB_L)
  c.save('Capsule Corp/lab.png')
}

function tileConcrete() {
  const c = new C(64, 64)
  c.fill(108, 108, 95)
  // Slab seams
  c.rect(0, 31, 64, 2, [75, 75, 62])
  c.rect(31, 0, 2, 64, [75, 75, 62])
  // Noise texture
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
    const n = c.noise(x, y, 7)
    if (n < 0.08) c.set(x, y, 80, 80, 68, 255)
    else if (n > 0.92) c.set(x, y, 125, 125, 112, 255)
  }
  c.save('Capsule Corp/concrete.png')
}

function tileAlienGrass() {
  const c = new C(64, 64)
  c.fill(...P.ALN)
  // Texture variation
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
    const n = c.noise(x, y, 3)
    if (n < 0.2)       c.set(x, y, ...P.ALN_D)
    else if (n > 0.82) c.set(x, y, ...P.ALN_L)
  }
  // Purple ki spots (alien planet quirk)
  for (let i = 0; i < 8; i++) {
    const n1 = c.noise(i, 99, 1), n2 = c.noise(i, 99, 2)
    const sx = Math.floor(n1 * 58) + 3, sy = Math.floor(n2 * 58) + 3
    c.circle(sx, sy, 2, [P.ALN_P[0], P.ALN_P[1], P.ALN_P[2], 160])
  }
  c.save('King Kai/alien_grass.png')
}

function tileForest() {
  const c = new C(64, 64)
  c.fill(...P.FOR)
  // Organic texture
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
    const n = c.noise(x, y, 5)
    if (n < 0.25)      c.set(x, y, ...P.FOR_D)
    else if (n > 0.78) c.set(x, y, ...P.FOR_L)
  }
  // Root lines
  c.rect(10, 0, 2, 30, P.FOR_R); c.rect(12, 30, 18, 2, P.FOR_R)
  c.rect(45, 15, 2, 35, P.FOR_R); c.rect(30, 15, 15, 2, P.FOR_R)
  // Fallen leaves scatter
  for (let i = 0; i < 10; i++) {
    const lx = Math.floor(c.noise(i, 0, 6) * 60) + 2
    const ly = Math.floor(c.noise(i, 1, 6) * 60) + 2
    c.circle(lx, ly, 2, P.FOR_L)
    c.set(lx, ly, ...P.FOR_D)
  }
  c.save('Mount Paozu/forest.png')
}

function tileDirt() {
  const c = new C(64, 64)
  c.fill(...P.DRT)
  // Texture
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
    const n = c.noise(x, y, 9)
    if (n < 0.2)       c.set(x, y, ...P.DRT_D)
    else if (n > 0.8)  c.set(x, y, ...P.DRT_L)
  }
  // Pebbles
  const pebbles = [[8,12],[25,38],[48,10],[55,52],[18,55],[37,27],[12,45]]
  for (const [px, py] of pebbles) {
    c.circle(px, py, 2, P.DRT_D)
    c.set(px-1, py-1, ...P.DRT_L)
  }
  // Footprint impressions
  c.rect(22, 18, 5, 8, P.DRT_D); c.rect(28, 28, 5, 8, P.DRT_D)
  c.rect(22, 42, 5, 8, P.DRT_D); c.rect(28, 52, 5, 8, P.DRT_D)
  c.save('Mount Paozu/dirt.png')
}

function tileMilitary() {
  const c = new C(64, 64)
  c.fill(...P.MIL)
  // Slab pattern
  for (let y = 0; y < 64; y += 20) c.rect(0, y, 64, 2, P.MIL_D)
  for (let x = 0; x < 64; x += 30) c.rect(x, 0, 2, 64, P.MIL_D)
  // Red Ribbon accent stripe
  c.rect(0, 30, 64, 3, P.MIL_R)
  c.rect(0, 31, 64, 1, [200, 22, 22])
  // Worn texture
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
    if (c.noise(x, y, 11) < 0.06) c.set(x, y, ...P.MIL_D)
  }
  c.save('Red Ribbon Army/military.png')
}

// ─────────────────────────────────────────────────────────────────────────────
//  CHARACTER SPRITES (32×32)
//  Using a 2px logical grid: each logical pixel = 2×2 real pixels
//  Grid is 16×16 logical = 32×32 output
// ─────────────────────────────────────────────────────────────────────────────

function spriteFromGrid(grid, palette) {
  const c = new C(32, 32)
  for (let ly = 0; ly < 16; ly++) {
    const row = grid[ly] || ''
    for (let lx = 0; lx < 16; lx++) {
      const ch = row[lx] || '.'
      if (ch !== '.') {
        const col = palette[ch]
        if (col) c.px2(lx, ly, 2, col)
      }
    }
  }
  return c
}

// ── Goku ───────────────────────────────────────────────────────────────────
function spriteGoku() {
  const pal = {
    'k': P.K,       // black outline
    's': P.SKIN,    // skin
    'd': P.SKIN_D,  // skin dark
    'h': P.GK_HR,   // hair black
    'o': P.GK_OR,   // orange gi
    'D': P.GK_ORD,  // orange dark
    'b': P.GK_BL,   // blue
    'B': P.GK_BLD,  // blue dark
    'r': P.GK_BT,   // boot
    'R': P.GK_BTD,  // boot dark
    'p': P.GK_PT,   // dark pants
    'e': [30,30,80],// eye
    'm': [200,100,80],// mouth
  }
  // 16×16 logical grid — Goku facing front, chibi style
  const grid = [
    '....hhhhhhhh....',  // 0  - hair top
    '...hhhhhhhhhh...',  // 1  - hair
    '..hkhhhhhhhkhh..',  // 2  - hair with outline
    '..hhksssssskhhh.',  // 3  - forehead
    '..hkssssssssk..',   // 4  - upper face
    '..kssessksse.k..',  // 5  - eyes  (ee = eye)
    '..ksssssssssk..',   // 6  - mid face
    '..ksss.m..ssk..',   // 7  - mouth
    '...ksssssssk...',   // 8  - chin
    '...kkkkkkkkk...',   // 9  - neck/collar
    '..koooooooook..',   // 10 - torso top
    '..koobbbbbook..',   // 11 - belt area
    '.koooooooooook.',   // 12 - torso lower
    '.kDoooooooooDk.',   // 13 - torso shaded
    '..kookkDDkook..',   // 14 - torso bottom / arm separation
    '..kppk..kppk..',   // 15 - legs (will use boots in extra rows, but 16 rows max)
  ]
  const c = spriteFromGrid(grid, pal)
  // Add boots at bottom (overwrite last logical row area manually)
  c.rect(4, 28, 8, 4, P.GK_BT)  // left boot
  c.rect(20, 28, 8, 4, P.GK_BT) // right boot
  c.rect(4, 30, 8, 2, P.GK_BTD)
  c.rect(20, 30, 8, 2, P.GK_BTD)
  c.save('Capsule Corp/goku.png')
  c.save('King Kai/goku.png')
  c.save('Mount Paozu/goku.png')
}

// ── Vegeta ──────────────────────────────────────────────────────────────────
function spriteVegeta() {
  const pal = {
    'k': P.K,
    's': P.SKIN,
    'd': P.SKIN_D,
    'h': P.VG_HR,
    'a': P.VG_AR,   // white armor
    'A': P.VG_ARD,  // armor shadow
    'u': P.VG_SU,   // blue suit
    'U': P.VG_SUD,  // suit dark
    'e': [30,30,80],
    'm': [180,80,60],
  }
  const grid = [
    '...hhhhhhhhh...',   // 0  - widow's peak hair
    '..hhhhhhhhhhhh.',   // 1
    '..hksssssssskh.',   // 2  - forehead
    '..kssssssssssk.',   // 3  - upper face
    '..kseesseesskk.',   // 4  - eyes
    '..ksssssssssk..',   // 5
    '..ksss..m.ssk..',   // 6  - mouth
    '...ksssssssk...',   // 7  - chin
    '...kkuuuukkk...',   // 8  - neck/collar
    '..kaauuuuuaak..',   // 9  - chest armor
    '..kaaUuuuUaak..',   // 10 - armor mid
    '..kaauuuuuaak..',   // 11 - armor lower
    '.kAaauuuuuaaaAk',   // 12 - shoulder armor
    '.kuuuuuuuuuuuuk',   // 13 - waist
    '..kuuukAAkuuuk.',   // 14 - legs begin
    '..kAAk..kAAk..',   // 15 - lower legs/boots
  ]
  const c = spriteFromGrid(grid, pal)
  // White gloves/boots
  c.rect(2, 24, 6, 4, P.VG_AR); c.rect(24, 24, 6, 4, P.VG_AR)
  c.rect(2, 28, 6, 4, P.VG_ARD); c.rect(24, 28, 6, 4, P.VG_ARD)
  c.save('Capsule Corp/vegeta.png')
}

// ── Piccolo ──────────────────────────────────────────────────────────────────
function spritePiccolo() {
  const pal = {
    'k': P.K,
    'g': P.PC_SK,   // green skin
    'G': P.PC_SKD,  // skin dark
    'p': P.PC_GI,   // purple gi
    'P': P.PC_GID,  // gi dark
    'w': P.PC_WH,   // white
    'e': [30,30,80],
    'a': [100,80,30], // antenna
  }
  const grid = [
    '....kaaaak......',  // 0 - antennae
    '....kgggggk.....',  // 1 - top of head (antennae base)
    '...kggggggggk...',  // 2 - head
    '..kgggggggggggk.',  // 3 - forehead
    '..kggeggggegggk.',  // 4 - eyes (dots)
    '..kgggggggggggk.',  // 5
    '..kggggg..gggk..',  // 6 - nose
    '..kggg....gggk..',  // 7 - mouth
    '...kggggggggk...',  // 8 - chin
    '...wwkkkkkwww...',  // 9 - white cape collar
    '..wpppppppppwk.',   // 10 - torso with cape
    '..wppPPPPPppwk.',   // 11 - gi shading
    '.kwpppppppppwk..',  // 12
    '.kwwppppppppwk..',  // 13 - cape edges
    '..kppkkPPkkppk.',   // 14 - lower gi
    '...kPPk..kPPk..',   // 15 - legs
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Kame Island/piccolo.png')
  c.save('King Kai/piccolo.png')
}

// ── Training Dummy MK1 ───────────────────────────────────────────────────────
function spriteTrainingDummyMK1() {
  const pal = {
    'k': P.K,
    'g': P.DM_GR,
    'G': P.DM_GRD,
    'l': P.DM_GRL,
    'r': P.DM_RD,
    'X': [80, 40, 40], // damage scorch marks
  }
  const grid = [
    '....kgggggk.....',  // 0 - head/sensor dome
    '...klgggggglk...',  // 1
    '..klggrgggggglk.',  // 2 - sensor light (r)
    '..kgggggggggggk.',  // 3
    '..kgGGGGGGGGgk.',   // 4 - face panel
    '..kgGGGGGGGGgk.',   // 5
    '..kggggggggggk.',   // 6
    '...kXggggXgkk..',   // 7 - damage/wear
    '....kkkGkkkk....',  // 8 - neck bolt
    '..kGGGGGGGGGGk.',   // 9 - shoulders
    '.klggGGGGGGgglk',   // 10 - chest/torso
    '.kgGGGggggGGGgk',   // 11
    '.kgggGggggGgggk',   // 12
    '..kGGGGGGGGGGk.',   // 13
    '...kGGk..kGGk...',  // 14 - legs
    '...kGGk..kGGk...',  // 15
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Kame Island/training_dummy_mk1.png')
}

// ── Training Dummy MK2 ───────────────────────────────────────────────────────
function spriteTrainingDummyMK2() {
  const pal = {
    'k': P.K,
    'g': [160,175,190],
    'G': [120,135,150],
    'l': [200,215,228],
    'b': P.DM2_BL,
    'B': [15,85,175],
    'r': P.DM_RD,
  }
  const grid = [
    '....kllllllk....',  // 0 - sleek dome
    '...klllllllllk..',  // 1
    '..klbblllllbblk.',  // 2 - eye sensors (blue)
    '..klllllllllllk.',  // 3
    '..kGGGGGGGGGGGk.',  // 4 - face panel
    '..kGbbbGGGbbbGk.',  // 5 - sensor array
    '..kGGGGGGGGGGGk.',  // 6
    '...kkGGGGGGkkk..',  // 7
    '....kkkBkkkk....',  // 8 - neck (blue power)
    '..kGGGGGGGGGGk.',   // 9
    '.kbllGGGGGGllbk',   // 10 - chest blue trim
    '.kgGGGGGGGGGGGk',   // 11
    '.kgGbGGGGGGbGGk',   // 12 - core indicator
    '..kGGGGGGGGGGk.',   // 13
    '...kGGk..kGGk...',  // 14
    '...kBBk..kBBk...',  // 15 - blue legs
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Kame Island/training_dummy_mk2.png')
}

// ── Marron ────────────────────────────────────────────────────────────────────
function spriteMarron() {
  const pal = {
    'k': P.K,
    's': P.SKIN,
    'h': [220,170,80],  // blonde hair
    'H': [185,130,40],  // hair dark
    'p': [220,100,130], // pink dress
    'P': [185,70,100],  // dress dark
    'w': P.W,
    'e': [30,30,80],
    'm': [200,100,80],
  }
  const grid = [
    '..hhhhhhhhhh....',  // 0 - hair
    '.hhhhhhhhhhhhh..',  // 1
    '.hksssssssskhh.',   // 2 - face
    '.hksssssssssk..',   // 3
    '.hkseesseeesk..',   // 4 - big eyes
    '.hkssssssssk...',   // 5
    '..ksss.m.ssk...',   // 6
    '...ksssssssk...',   // 7 - chin (small child)
    '...kkkkkkkk....',   // 8
    '....kppppk.....',   // 9 - dress top (small torso)
    '...kppppppk....',   // 10
    '...kpPPPPpk....',   // 11
    '..kpppppppppk..',   // 12
    '..kpPPPPPPppk..',   // 13
    '...kpsk..kspk.',    // 14 - legs
    '...kwwk..kwwk.',    // 15 - white shoes
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Kame Island/marron.png')
}

// ── Wild Monkey ───────────────────────────────────────────────────────────────
function spriteWildMonkey() {
  const pal = {
    'k': P.K,
    'b': P.MK_BR,   // brown fur
    'B': P.MK_BRD,  // dark fur
    'f': P.MK_FC,   // face lighter
    'e': P.MK_EY,   // red eye
    't': P.MK_TH,   // teeth
    'n': [160,100,60],  // nose
  }
  const grid = [
    '...kbbbbbbk.....',  // 0
    '..kbbbbbbbbbk...',  // 1
    '.kbbbBbbbBbbbk..',  // 2 - head with ear
    'kbbkbbbbbbbkbbk.',  // 3 - ears
    'kbbkbffffffkbbk.',  // 4 - face lighter
    'kbkkfefBBefkBbk.',  // 5 - eyes (red e)
    '.kBbfffffffbbk.',   // 6
    '.kbbfff.nfffbbk.',  // 7 - snout/nose
    '.kbBffttttffBbk.',  // 8 - teeth (angry)
    '..kbbbbbbbbbk...',  // 9
    '..kbBbbbbbBbk...',  // 10 - shoulders
    '.kbbBbbbbbBbbk.',   // 11 - arms out (aggressive)
    '.kBbbbbbbbbbBk.',   // 12
    '..kBbbbbbbbBk...',  // 13 - torso
    '...kbBkkkBbk...',   // 14 - legs
    '....kBk..kBk....',  // 15
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Kame Island/wild_monkey.png')
}

// ── Wild Boar ─────────────────────────────────────────────────────────────────
function spriteWildBoar() {
  const pal = {
    'k': P.K,
    'b': P.BR_BK,   // dark fur
    'B': P.BR_BKD,  // darker
    's': P.BR_SN,   // snout
    'i': P.BR_IV,   // ivory tusk
    'e': P.BR_EY,   // red eye
    'h': [85,70,55],    // hooves
  }
  const grid = [
    '........kbbbbk.',   // 0 - low profile head
    '.....kbbbbbbbbbk',  // 1
    '....kbbbbbbbbbbbk', // 2
    '...kbbBbbbbbBbbbbk',// 3 - body bulk begins
    '...kbbbbebbbekbbbk',// 4 - eyes
    '...kbbbbbbbbbbbbk', // 5
    '....kbbbssssbbk.',  // 6 - snout
    '..kiibbbssssbbii.',  // 7 - tusks (i)
    '..kiibbbssbbbbii.',  // 8
    '...kbbbbbbbbbbbk',  // 9 - bulk torso
    '..kbbBBBBBBBBbbk.', // 10
    '.kbbbBBBBBBBBbbbk', // 11
    '.kbbbbbbbbbbbbbk.', // 12
    '..kbbBbbbbBbbbbk.', // 13
    '..khbhk..kbhbhk.', // 14 - legs/hooves
    '..khhk....khhhk.', // 15
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Kame Island/wild_boar.png')
}

// ── King Kai NPC ──────────────────────────────────────────────────────────────
function spriteKingKai() {
  const pal = {
    'k': P.K,
    's': [190,225,190],   // blue-ish green skin (Kai)
    'g': [140,180,140],   // skin dark
    'r': [200,30,30],     // red gi
    'R': [150,20,20],     // gi dark
    'w': P.W,
    'y': [240,200,30],    // yellow glasses
    'b': [30,30,80],      // glasses lens
    'a': [40,30,10],      // antenna (Kai have antennae)
  }
  const grid = [
    '.....kaak.......',   // 0 - antennae
    '....kasskak.....',   // 1
    '...ksssssssk....',   // 2 - head
    '..kssssssssssk..',   // 3
    '..kssybbbyyssk..',   // 4 - round glasses
    '..kssybbbysssk..',   // 5
    '..kssyyyyyyysk..',   // 6 - glasses frames
    '..ksssss..sssk..',   // 7
    '...ksssssssk...',    // 8
    '....kkkkkkkk...',    // 9 - neck
    '...krrrrrrrk...',    // 10 - red gi top
    '..krrRRRRRrrk..',    // 11 - gi torso
    '..krrrrrrrrrrk.',    // 12
    '..kRrrrrrrrRrk.',    // 13
    '...krrk..krrk..',    // 14
    '...kRRk..kRRk..',    // 15
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('King Kai/king_kai.png')
}

// ── Trunks ────────────────────────────────────────────────────────────────────
function spriteTrunks() {
  const pal = {
    'k': P.K,
    's': P.SKIN,
    'd': P.SKIN_D,
    'h': [160,100,200],   // purple hair
    'H': [120,65,160],    // hair dark
    'j': [50,100,180],    // blue jacket
    'J': [30,70,140],     // jacket dark
    'p': [55,45,80],      // dark pants
    'P': [35,28,55],      // pants dark
    'b': [180,180,180],   // grey shirt/armor bits
    'e': [30,30,80],
    'w': P.W,
    'r': [180,30,30],     // Capsule Corp logo hint
  }
  const grid = [
    '..khhhhHHHhhk...',   // 0 - long purple hair
    '..khhhhhhhhhhhk.',   // 1
    '.khkhssssssskhhk',   // 2
    '.khksssssssssk..',   // 3
    '.khksseesseesk..',   // 4 - eyes
    '.khksssssssssk..',   // 5
    '..khkss.m.sssk..',   // 6
    '...khkssssssk...',   // 7
    '..kHHkkkkkkkHk.',    // 8 - jacket collar
    '..kjjjjjjjjjjk.',   // 9 - jacket
    '..kjjJjjjjjJjk.',   // 10
    '.kjjjjbrjjjjjjk',   // 11 - CC logo hint
    '.kjjjjjjjjjjjjk',   // 12
    '..kJjjjjjjjJjk.',   // 13
    '...kppk..kppk..',    // 14 - pants
    '...kPPk..kPPk..',    // 15
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('Capsule Corp/trunks.png')
}

// ─────────────────────────────────────────────────────────────────────────────
//  PLAYER RACE BASE SPRITES
// ─────────────────────────────────────────────────────────────────────────────

function spriteHumanWarrior() {
  const c = new C(32, 32)
  // Same as saiyan but with different colors (Human = earth tones, no tail)
  const pal = {
    'k': P.K,
    's': P.SKIN,
    'h': [90,55,25],    // brown hair
    'H': [60,35,12],    // dark brown
    'g': [60,120,60],   // green gi (earth human)
    'G': [40,90,40],
    'b': [100,60,20],   // brown belt
    'p': [40,40,40],
    'e': [40,25,10],
    'm': [200,100,80],
  }
  const grid = [
    '....hhhhhhhh....',
    '...hhhhhhhhhh...',
    '..hkHhhhhhHkh..',
    '..hksssssssk...',
    '..kssessksse.k.',
    '..ksssssssssk..',
    '..kssss..sssk..',
    '...kssssssssk..',
    '...kkkkkkkkk...',
    '..kgggggggggk..',
    '..kgGGGGGGGgk..',
    '..kgbbbbbbbgk..',
    '.kgggggggggggk.',
    '.kGgggggggggGk.',
    '..kggk...kggk..',
    '..kpk....kppk..',
  ]
  const c2 = spriteFromGrid(grid, pal)
  c2.save('player/human_warrior.png')
}

function spriteNamekianWarrior() {
  const pal = {
    'k': P.K,
    'g': P.PC_SK,   // green skin
    'G': P.PC_SKD,
    'a': [100,80,30], // antenna
    'p': P.PC_GI,
    'P': P.PC_GID,
    'w': P.PC_WH,
    'e': [30,30,80],
  }
  const grid = [
    '....kaak........',
    '...kgggggk......',
    '..kgggggggk.....',
    '..kggggggggk....',
    '..kgeggggegk....',
    '..kggggggggk....',
    '..kgggg..gggk...',
    '...kgggggggk....',
    '...kkkkkkkk.....',
    '..kpppppppppk...',
    '..kpPPPPPPppk...',
    '.kwpppppppppwk..',
    '.kwwpppppppwwk..',
    '..kpppppppppk...',
    '...kpPk..kpPk...',
    '...kPPk..kPPk...',
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('player/namekian_warrior.png')
}

function spriteAndroidWarrior() {
  const pal = {
    'k': P.K,
    's': P.SKIN,
    'h': [200,200,210], // silver-white hair
    'H': [160,160,170],
    'j': [30,30,40],    // dark jacket
    'J': [15,15,22],
    'b': P.DM2_BL,      // blue tech
    'l': [180,185,200], // light grey
    'e': [0,180,255],   // glowing blue eyes
    'E': [0,120,200],
    'p': [25,25,35],
  }
  const grid = [
    '...khhhhhhhhk...',
    '..khhhhhhhhhhhk.',
    '..khksssssskhhk.',
    '..khkssssssssk..',
    '..khkEEssEEssk..',
    '..khksssssssssk.',
    '..khkss...ssssk.',
    '...khkssssssk...',
    '....kkkkkkkkk...',
    '...kjjjjjjjjk...',
    '..kjjjbjjjbjjk..',
    '..kjJJjjjjjJJk..',
    '.kjjjbjjjjbjjjk.',
    '.kjJJJjjjjJJJJk.',
    '..kppk...kppk...',
    '..kppk...kppk...',
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('player/android_warrior.png')
}

function spriteFrostDemonWarrior() {
  const pal = {
    'k': P.K,
    'w': [220,225,240],  // white/light purple skin
    'W': [185,190,210],  // skin dark
    'p': [160,80,200],   // purple accent
    'P': [120,50,160],
    'r': [220,30,30],    // red eye
    'h': [200,190,215],  // light armor
    'H': [165,155,180],
    'e': [200,30,30],    // Frieza-style dark eyes
    't': [20,20,20],     // dark markings
  }
  const grid = [
    '.....kwwwwwk....',  // elongated head
    '....kwwwwwwwk...',
    '...kwwwwwwwwwk..',
    '...kWwwpwwwWwk..',
    '...kwwtpwwwwwk..',  // eye line
    '...kwwwpwwwwwk..',
    '...kwwwwwwwwwk..',
    '....kwwwwwwwk...',
    '....kkkkpkkkk...',
    '...khhhppphhhhk.',
    '..khhHHpppHHhhk.',
    '..khhhhppphhhhk.',
    '.kWhhhhppphhhhWk',
    '.khhhhppppphhhhk',
    '..khHk...khHk...',
    '..kHHk...kHHk...',
  ]
  const c = spriteFromGrid(grid, pal)
  c.save('player/frost_demon_warrior.png')
}

// ─────────────────────────────────────────────────────────────────────────────
//  MAIN
// ─────────────────────────────────────────────────────────────────────────────

console.log('\nDBForged Sprite Generator')
console.log('='.repeat(40))

console.log('\n[Terrain Tiles]')
tileMetal()
tileLab()
tileConcrete()
tileAlienGrass()
tileForest()
tileDirt()
tileMilitary()

console.log('\n[Character Sprites]')
spriteGoku()
spriteVegeta()
spritePiccolo()
spriteTrunks()
spriteKingKai()

console.log('\n[Kame Island NPCs]')
spriteTrainingDummyMK1()
spriteTrainingDummyMK2()
spriteMarron()
spriteWildMonkey()
spriteWildBoar()

console.log('\n[Player Race Sprites]')
spriteHumanWarrior()
spriteNamekianWarrior()
spriteAndroidWarrior()
spriteFrostDemonWarrior()

console.log('\n✓ All sprites generated.\n')
