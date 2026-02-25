import { useState, useCallback, useRef } from 'react'
import dbforged from '../services/dbforged'

// Keywords that indicate an Evennia login failure message
const LOGIN_ERROR_PATTERNS = [
  "that account",
  "doesn't exist",
  "incorrect password",
  "wrong password",
  "no account",
  "not found",
  "login failed",
  "already connected",
  "too many",
]

function isLoginError(text) {
  const lower = text.toLowerCase()
  return LOGIN_ERROR_PATTERNS.some(p => lower.includes(p))
}

export function useGameState() {
  const [connectionState, setConnectionState] = useState('disconnected')
  const [loginState,      setLoginState]      = useState('logged_out')
  const [messages,        setMessages]        = useState([])
  const [player,          setPlayer]          = useState(null)
  const [target,          setTarget]          = useState(null)
  const [entities,        setEntities]        = useState({})
  const [error,           setError]           = useState(null)

  // Refs so that message callbacks always see current values without stale closures
  const loginStateRef = useRef('logged_out')
  const connectedRef  = useRef(false)

  const _setLoginState = (s) => {
    loginStateRef.current = s
    setLoginState(s)
  }

  const addMessage = useCallback((type, content) => {
    setMessages(prev => [...prev.slice(-200), { type, content, id: Date.now() + Math.random() }])
  }, [])

  const handleEntityUpdate = useCallback((entity) => {
    if (!entity?.id) return
    setEntities(prev => ({ ...prev, [entity.id]: entity }))
  }, [])

  // ── Connect ───────────────────────────────────────────────────────────────
  const connect = useCallback(async () => {
    setConnectionState('connecting')
    setError(null)

    try {
      await dbforged.connectAll({
        // ── Game socket — Evennia commands & text ──────────────────────────
        game: {
          onOpen: () => {
            connectedRef.current = true
            setConnectionState('connected')
          },

          onMessage: (type, data) => {
            if (type !== 'text') return

            const raw  = data.raw  || ''
            const html = data.html || ''
            if (!raw.trim()) return

            // Detect login result when we're waiting for one
            if (loginStateRef.current === 'logging_in') {
              if (isLoginError(raw)) {
                _setLoginState('logged_out')
                setError(raw.trim())
                return // don't surface the raw error text as a chat message
              } else {
                // Any non-error Evennia response means we're in
                _setLoginState('logged_in')
              }
            }

            addMessage('text', { raw, html })
          },

          onError: () => {
            setError('Cannot reach the game server. Is Evennia running?')
          },

          onClose: () => {
            connectedRef.current = false
            setConnectionState('disconnected')
            if (loginStateRef.current !== 'logged_out') {
              _setLoginState('logged_out')
              addMessage('system', { raw: 'Connection lost.', html: 'Connection lost.' })
            }
          },
        },

        // ── Combat socket (no backend yet) ────────────────────────────────
        combat: {
          onMessage: (type, data) => {
            if (type === 'json' && data.type === 'target_update') setTarget(data)
          },
        },

        // ── World socket (no backend yet) ─────────────────────────────────
        world: {
          onMessage: (type, data) => {
            console.log('[World] Received:', type, data)
            if (type === 'json') {
              console.log('[World] JSON data:', data)
              if (data.type === 'player_frame') {
                console.log('[World] Player frame:', data.entity)
                setPlayer(data.entity)
              }
              if (data.type === 'entity_delta') {
                console.log('[World] Entity delta:', data.entity)
                handleEntityUpdate(data.entity)
              }
            }
          },
        },

        // ── Chat socket (no backend yet) ──────────────────────────────────
        chat: {
          onMessage: (type, data) => {
            if (type === 'text') addMessage('chat', data)
          },
        },
      })
    } catch (err) {
      setConnectionState('disconnected')
      setError(err.message || 'Failed to connect to the game server.')
    }
  }, [addMessage, handleEntityUpdate])

  // ── Reconnect ─────────────────────────────────────────────────────────────
  // Drops all sockets cleanly then re-establishes them.
  const reconnect = useCallback(() => {
    dbforged.disconnectAll()
    connectedRef.current = false
    _setLoginState('logged_out')
    setPlayer(null)
    setTarget(null)
    setEntities({})
    setError(null)
    // Small delay to let the close events settle
    setTimeout(connect, 200)
  }, [connect])

  // ── sendCommand ──────────────────────────────────────────────────────────
  const sendCommand = useCallback((cmd) => {
    if (!connectedRef.current) return
    addMessage('command', { raw: `> ${cmd}`, html: `> ${cmd}` })
    dbforged.game.sendCommand(cmd)
  }, [addMessage])

  // ── login / logout ───────────────────────────────────────────────────────
  const login = useCallback((username, password) => {
    if (!connectedRef.current) {
      setError('Not connected. Please wait for the server connection.')
      return
    }
    setError(null)
    _setLoginState('logging_in')
    dbforged.game.sendCommand(`connect ${username} ${password}`)
  }, [])

  const logout = useCallback(() => {
    sendCommand('quit')
    _setLoginState('logged_out')
    setPlayer(null)
    setTarget(null)
    setEntities({})
  }, [sendCommand])

  return {
    connectionState,
    loginState,
    messages,
    player,
    target,
    entities,
    error,
    connect,
    reconnect,
    sendCommand,
    login,
    logout,
    setTarget,
  }
}

export default useGameState
