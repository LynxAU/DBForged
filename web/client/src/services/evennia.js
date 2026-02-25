/**
 * Evennia WebSocket Service
 * Handles connection to Evennia server with ANSI parsing and sprite support
 */

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const WEBSOCKET_URL = `${wsProtocol}//${window.location.host}/webclient`

class EvenniaService {
  constructor() {
    this.ws = null
    this.handlers = {
      onOpen: null,
      onMessage: null,
      onError: null,
      onClose: null
    }
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 2000
  }

  connect(options = {}) {
    return new Promise((resolve, reject) => {
      this.handlers = { ...this.handlers, ...options }
      
      // Close existing connection if any
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
      
      try {
        // Create new WebSocket without any saved session
        this.ws = new WebSocket(WEBSOCKET_URL)
        
        this.ws.onopen = () => {
          console.log('[Evennia] Connected')
          this.reconnectAttempts = 0
          // Don't auto-authenticate - require explicit login
          if (this.handlers.onOpen) this.handlers.onOpen()
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event.data)
        }
        
        this.ws.onerror = (error) => {
          console.error('[Evennia] Error:', error)
          if (this.handlers.onError) this.handlers.onError(error)
        }
        
        this.ws.onclose = () => {
          console.log('[Evennia] Disconnected')
          if (this.handlers.onClose) this.handlers.onClose()
          this.attemptReconnect()
        }
        
      } catch (error) {
        reject(error)
      }
    })
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`[Evennia] Reconnecting... attempt ${this.reconnectAttempts}`)
      setTimeout(() => {
        this.connect(this.handlers).catch(console.error)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('[Evennia] Cannot send - not connected')
    }
  }

  sendCommand(cmd) {
    this.send({
      type: 'command',
      data: [cmd]
    })
  }

  handleMessage(rawData) {
    try {
      // Evennia sends JSON or raw text
      const data = JSON.parse(rawData)
      
      // Handle different message types
      if (data.type === 'text') {
        const text = data.text || data.data?.[0] || ''
        const parsed = this.parseAnsi(text)
        if (this.handlers.onMessage) {
          this.handlers.onMessage('text', parsed)
        }
      } else if (data.type === 'webclient_options') {
        // Client options acknowledged
        console.log('[Evennia] Client options set')
      } else if (data.type === 'json') {
        // Game state updates (entity_delta, etc)
        if (this.handlers.onMessage) {
          this.handlers.onMessage('json', data.data)
        }
      } else {
        // Pass through raw
        if (this.handlers.onMessage) {
          this.handlers.onMessage('raw', data)
        }
      }
    } catch (e) {
      // Not JSON - treat as text
      const parsed = this.parseAnsi(rawData)
      if (this.handlers.onMessage) {
        this.handlers.onMessage('text', { raw: rawData, parsed })
      }
    }
  }

  /**
   * Parse ANSI color codes to HTML spans
   */
  parseAnsi(text) {
    if (!text) return { raw: '', html: '', segments: [] }
    
    // ANSI code mappings
    const ansiColors = {
      '30': '#1a1a1a', '31': '#ff3366', '32': '#32ff64', '33': '#ffd74a',
      '34': '#00aeff', '35': '#cc66ff', '36': '#00cccc', '37': '#e2e8f0',
      '90': '#666666', '91': '#ff6688', '92': '#66ff88', '93': '#ffee88',
      '94': '#4499ff', '95': '#dd88ff', '96': '#66dddd', '97': '#ffffff'
    }
    
    const ansiBackgrounds = {
      '40': '#1a1a1a', '41': '#ff3366', '42': '#32ff64', '43': '#ffd74a',
      '44': '#00aeff', '45': '#cc66ff', '46': '#00cccc', '47': '#e2e8f0'
    }
    
    // Common ANSI codes
    const codes = {
      '0': 'reset', '1': 'bold', '2': 'dim', '3': 'italic', '4': 'underline',
      '7': 'reverse', '9': 'strike',
      '22': 'bold-off', '23': 'italic-off', '24': 'underline-off',
      '27': 'reverse-off', '29': 'strike-off'
    }
    
    // Replace |r, |g, etc with ANSI codes
    const evenniaCodes = {
      '|r': '\x1b[31m', '|g': '\x1b[32m', '|y': '\x1b[33m', '|b': '\x1b[34m',
      '|m': '\x1b[35m', '|c': '\x1b[36m', '|w': '\x1b[37m', '|x': '\x1b[90m',
      '|R': '\x1b[91m', '|G': '\x1b[92m', '|Y': '\x1b[93m', '|B': '\x1b[94m',
      '|M': '\x1b[95m', '|C': '\x1b[96m', '|W': '\x1b[97m', '|n': '\x1b[0m',
      '|!': '\x1b[1m', '|_': '\x1b[4m', '|-': '\x1b[7m'
    }
    
    // Apply Evennia codes first
    let processed = text
    for (const [code, ansi] of Object.entries(evenniaCodes)) {
      processed = processed.replace(new RegExp(code.replace('|', '\\|'), 'g'), ansi)
    }
    
    // Parse ANSI to HTML
    const segments = []
    let currentColor = '#e2e8f0'
    let currentBg = null
    let isBold = false
    let html = processed.replace(
      /\x1b\[([0-9;]*)m/g,
      (match, codeStr) => {
        const codes = codeStr.split(';').map(c => parseInt(c) || 0)
        
        for (const code of codes) {
          if (code === 0) {
            currentColor = '#e2e8f0'
            currentBg = null
            isBold = false
          } else if (code === 1) {
            isBold = true
          } else if (ansiColors[code]) {
            currentColor = ansiColors[code]
          } else if (ansiBackgrounds[code]) {
            currentBg = ansiBackgrounds[code]
          }
        }
        
        return '' // Remove ANSI codes from output
      }
    )
    
    // Wrap in spans for each color change
    // This is a simplified version - full implementation would track segments
    const finalHtml = html
    
    return {
      raw: text,
      html: finalHtml,
      segments
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Singleton instance
export const evennia = new EvenniaService()
export default evennia
