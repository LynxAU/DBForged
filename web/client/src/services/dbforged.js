/**
 * DBForged Network Layer
 *
 * 4 dedicated WebSocket connections:
 *   game   → /ws/game   (4001) - commands & text output
 *   combat → /ws/combat (4002) - real-time combat state
 *   world  → /ws/world  (4003) - map & entity updates
 *   chat   → /ws/chat   (4004) - channels & social
 *
 * Each socket provides:
 *   - State machine: disconnected → connecting → connected → reconnecting
 *   - Exponential backoff with jitter (caps at 30 s)
 *   - Outbound message queue (replayed on reconnect, max 100 frames)
 *   - Application-level heartbeat (ping every 30 s, pong timeout 10 s)
 *   - Connection timeout (10 s)
 *   - Clean manual disconnect (no phantom reconnects)
 */

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const wsHost     = window.location.host

const SOCKET_PATHS = {
  game:   '/webclient',   // matches Evennia's WebSocket endpoint (proxied by Vite)
  combat: '/ws/combat',
  world:  '/ws/world',
  chat:   '/ws/chat',
}

// ---------------------------------------------------------------------------
// ANSI / Evennia colour parsing → HTML
// ---------------------------------------------------------------------------

const ANSI_FG = {
  30:'#1a1a1a', 31:'#ff3366', 32:'#32ff64', 33:'#ffd74a',
  34:'#00aeff', 35:'#cc66ff', 36:'#00cccc', 37:'#e2e8f0',
  90:'#666666', 91:'#ff6688', 92:'#66ff88', 93:'#ffee88',
  94:'#4499ff', 95:'#dd88ff', 96:'#66dddd', 97:'#ffffff',
}
const ANSI_BG = {
  40:'#1a1a1a', 41:'#ff3366', 42:'#32ff64', 43:'#ffd74a',
  44:'#00aeff', 45:'#cc66ff', 46:'#00cccc', 47:'#e2e8f0',
}
const EVENNIA_CODES = {
  '|r':'\x1b[31m','|g':'\x1b[32m','|y':'\x1b[33m','|b':'\x1b[34m',
  '|m':'\x1b[35m','|c':'\x1b[36m','|w':'\x1b[37m','|x':'\x1b[90m',
  '|R':'\x1b[91m','|G':'\x1b[92m','|Y':'\x1b[93m','|B':'\x1b[94m',
  '|M':'\x1b[95m','|C':'\x1b[96m','|W':'\x1b[97m','|n':'\x1b[0m',
  '|!':'\x1b[1m', '|_':'\x1b[4m', '|-':'\x1b[7m',
}

function parseAnsi(raw) {
  if (!raw) return { raw: '', html: '', segments: [] }

  // Expand Evennia shorthand colour codes first
  let text = raw
  for (const [code, esc] of Object.entries(EVENNIA_CODES)) {
    text = text.replace(new RegExp(code.replace('|', '\\|'), 'g'), esc)
  }

  const segments = []
  let fg = null, bg = null, bold = false
  let cursor = 0

  const RE = /\x1b\[([0-9;]*)m/g
  let match

  const flush = (end) => {
    if (end > cursor) {
      segments.push({ text: text.slice(cursor, end), fg, bg, bold })
    }
  }

  while ((match = RE.exec(text)) !== null) {
    flush(match.index)
    cursor = match.index + match[0].length

    for (const n of match[1].split(';').map(Number)) {
      if (n === 0)              { fg = null; bg = null; bold = false }
      else if (n === 1)         { bold = true }
      else if (n === 22)        { bold = false }
      else if (ANSI_FG[n])     { fg = ANSI_FG[n] }
      else if (ANSI_BG[n])     { bg = ANSI_BG[n] }
    }
  }
  flush(text.length)

  // Build HTML from segments
  const html = segments.map(seg => {
    const style = [
      seg.fg   ? `color:${seg.fg}`            : '',
      seg.bg   ? `background:${seg.bg}`       : '',
      seg.bold ? 'font-weight:700'            : '',
    ].filter(Boolean).join(';')
    const escaped = seg.text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
    return style ? `<span style="${style}">${escaped}</span>` : escaped
  }).join('')

  return { raw, html, segments }
}

// ---------------------------------------------------------------------------
// DBForgedSocket
// ---------------------------------------------------------------------------

const CONNECT_TIMEOUT  = 10_000   // ms before initial open is rejected
const PING_INTERVAL    = 30_000   // ms between keepalive pings
const PONG_TIMEOUT     = 10_000   // ms to wait for pong before reconnecting
const BASE_DELAY       =  1_000   // reconnect backoff base (ms)
const MAX_DELAY        = 30_000   // reconnect backoff ceiling (ms)
const MAX_ATTEMPTS     =     10   // give up after this many reconnect tries
const QUEUE_LIMIT      =    100   // max outbound frames to buffer offline

class DBForgedSocket {
  /**
   * @param {string} name  - display name used in log messages
   * @param {string} path  - WebSocket path (e.g. '/ws/game')
   * @param {object} [cfg]
   * @param {number} [cfg.maxAttempts=MAX_ATTEMPTS] - 0 = no retries (silent optional socket)
   */
  constructor(name, path, { maxAttempts = MAX_ATTEMPTS } = {}) {
    this.name        = name
    this.url         = `${wsProtocol}//${wsHost}${path}`
    this.state       = 'disconnected'   // disconnected | connecting | connected | reconnecting
    this._maxAttempts = maxAttempts

    this._ws              = null
    this._handlers        = {}
    this._queue           = []      // outbound frames buffered while offline
    this._attempt         = 0
    this._reconnectTimer  = null
    this._connectTimer    = null
    this._pingTimer       = null
    this._pongTimer       = null
    this._intentionalClose = false
  }

  // ── Public API ────────────────────────────────────────────────────────────

  connect(options = {}) {
    this._handlers = { ...this._handlers, ...options }
    this._intentionalClose = false
    return this._open()
  }

  send(data) {
    const frame = JSON.stringify(data)
    if (this._ws?.readyState === WebSocket.OPEN) {
      this._ws.send(frame)
    } else {
      if (this._queue.length >= QUEUE_LIMIT) this._queue.shift() // drop oldest
      this._queue.push(frame)
      console.debug(`[DBForged:${this.name}] Queued (${this._queue.length} pending)`)
    }
  }

  sendCommand(cmd) {
    // Evennia webclient protocol: client sends text as ["text", [cmd], {}]
    this.send(['text', [cmd], {}])
  }

  disconnect() {
    this._intentionalClose = true
    this._cleanup()
    this._ws?.close()
    this._ws = null
    this._setState('disconnected')
  }

  // ── Internal ──────────────────────────────────────────────────────────────

  _open() {
    return new Promise((resolve, reject) => {
      this._setState('connecting')

      // Timeout guard
      this._connectTimer = setTimeout(() => {
        this._ws && (this._ws.onclose = null) && this._ws.close()
        reject(new Error(`[DBForged:${this.name}] Connection timed out`))
        this._scheduleReconnect()
      }, CONNECT_TIMEOUT)

      try {
        this._ws = new WebSocket(this.url)
      } catch (err) {
        clearTimeout(this._connectTimer)
        reject(err)
        return
      }

      this._ws.onopen = () => {
        clearTimeout(this._connectTimer)
        this._attempt = 0
        this._setState('connected')
        // Tell Evennia our client capabilities (required handshake)
        try {
          this._ws.send(JSON.stringify(['client_options', [{ 'client': 'dbforged', 'version': '0.1', 'ANSI': true, 'SCREENWIDTH': 200 }], {}]))
        } catch (_) {}
        this._startHeartbeat()
        this._flushQueue()
        this._handlers.onOpen?.()
        resolve()
      }

      this._ws.onmessage = ({ data }) => {
        this._onFrame(data)
      }

      this._ws.onerror = (ev) => {
        // Suppress noise for optional sockets with no backend yet
        if (this._maxAttempts > 0) {
          console.error(`[DBForged:${this.name}] Socket error`, ev)
        }
        this._handlers.onError?.(ev)
      }

      this._ws.onclose = () => {
        clearTimeout(this._connectTimer)
        this._stopHeartbeat()

        if (this._intentionalClose) {
          this._setState('disconnected')
          this._handlers.onClose?.()
          return
        }

        // Don't notify consumers during transient reconnect cycles — only
        // notify if we're about to give up completely.
        const willRetry = this._attempt < this._maxAttempts
        if (!willRetry) {
          this._setState('disconnected')
          this._handlers.onClose?.()
        } else {
          this._setState('reconnecting')
        }
        this._scheduleReconnect()
      }
    })
  }

  _scheduleReconnect() {
    if (this._intentionalClose || this._attempt >= this._maxAttempts) {
      if (this._attempt >= this._maxAttempts && this._maxAttempts > 0) {
        console.error(`[DBForged:${this.name}] Gave up after ${this._maxAttempts} attempts`)
      }
      return
    }
    this._attempt++
    const jitter = Math.random() * 1000
    const delay  = Math.min(BASE_DELAY * 2 ** (this._attempt - 1) + jitter, MAX_DELAY)
    console.log(`[DBForged:${this.name}] Retry ${this._attempt}/${this._maxAttempts} in ${Math.round(delay)}ms`)
    this._reconnectTimer = setTimeout(() => this._open().catch(console.error), delay)
  }

  _startHeartbeat() {
    this._pingTimer = setInterval(() => {
      if (this._ws?.readyState !== WebSocket.OPEN) return
      try { this._ws.send(JSON.stringify({ type: 'ping' })) } catch (_) {}
      this._pongTimer = setTimeout(() => {
        console.warn(`[DBForged:${this.name}] Pong timeout — forcing reconnect`)
        this._ws?.close()
      }, PONG_TIMEOUT)
    }, PING_INTERVAL)
  }

  _stopHeartbeat() {
    clearInterval(this._pingTimer)
    clearTimeout(this._pongTimer)
    this._pingTimer = null
    this._pongTimer = null
  }

  _cleanup() {
    clearTimeout(this._reconnectTimer)
    clearTimeout(this._connectTimer)
    this._stopHeartbeat()
  }

  _flushQueue() {
    while (this._queue.length > 0 && this._ws?.readyState === WebSocket.OPEN) {
      this._ws.send(this._queue.shift())
    }
  }

  _setState(state) {
    this.state = state
    // Only log state changes for required sockets; optional ones are silent
    if (this._maxAttempts > 0) {
      console.log(`[DBForged:${this.name}] → ${state}`)
    }
  }

  _onFrame(raw) {
    // Any server message resets the pong watchdog
    clearTimeout(this._pongTimer)
    this._pongTimer = null

    let data
    try { data = JSON.parse(raw) } catch (_) {
      // Non-JSON frame — treat as plain text
      this._handlers.onMessage?.('text', parseAnsi(raw))
      return
    }

    // ── Evennia webclient protocol: ["cmdname", [args...], {kwargs}] ──────
    if (Array.isArray(data)) {
      const [cmd, args = []] = data
      const firstArg = Array.isArray(args) ? (args[0] ?? '') : String(args ?? '')

      switch (cmd) {
        case 'text':
        case 'prompt':
          this._handlers.onMessage?.('text', parseAnsi(String(firstArg)))
          break
        case 'client_options':
        case 'webclient_options':
          console.debug(`[DBForged:${this.name}] Server options received`)
          break
        case 'pong':
          break  // heartbeat ack
        default:
          this._handlers.onMessage?.('raw', data)
      }
      return
    }

    // ── Object format (future backends / internal use) ────────────────────
    if (data.type === 'pong') return
    if (data.type === 'text') {
      const text = data.text ?? data.data?.[0] ?? ''
      this._handlers.onMessage?.('text', parseAnsi(text))
    } else if (data.type === 'json') {
      this._handlers.onMessage?.('json', data.data)
    } else {
      this._handlers.onMessage?.('raw', data)
    }
  }
}

// ---------------------------------------------------------------------------
// DBForgedService — owns all 4 sockets
// ---------------------------------------------------------------------------

class DBForgedService {
  constructor() {
    this.game   = new DBForgedSocket('Game',   SOCKET_PATHS.game)
    // Optional sockets — no backends yet; maxAttempts:0 = try once, fail silently
    this.combat = new DBForgedSocket('Combat', SOCKET_PATHS.combat, { maxAttempts: 0 })
    this.world  = new DBForgedSocket('World',  SOCKET_PATHS.world,  { maxAttempts: 0 })
    this.chat   = new DBForgedSocket('Chat',   SOCKET_PATHS.chat,   { maxAttempts: 0 })
  }

  /**
   * Connect the game socket. Optional sockets (combat/world/chat) are not
   * attempted here — they have no backends yet and are connected explicitly
   * when their services come online.
   *
   * @param {{ game?, combat?, world?, chat? }} options - handler maps (only game is used here)
   */
  async connectAll(options = {}) {
    // Store handlers for optional sockets so they're ready when connected later
    if (options.combat) this.combat._handlers = { ...this.combat._handlers, ...options.combat }
    if (options.world)  this.world._handlers  = { ...this.world._handlers,  ...options.world }
    if (options.chat)   this.chat._handlers   = { ...this.chat._handlers,   ...options.chat }

    await this.game.connect(options.game ?? {})
  }

  /** Returns a snapshot of each socket's current state. */
  get states() {
    return {
      game:   this.game.state,
      combat: this.combat.state,
      world:  this.world.state,
      chat:   this.chat.state,
    }
  }

  disconnectAll() {
    this.game.disconnect()
    this.combat.disconnect()
    this.world.disconnect()
    this.chat.disconnect()
  }
}

// Singleton
export const dbforged = new DBForgedService()
export default dbforged
