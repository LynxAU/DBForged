import { useState, useCallback } from 'react'
import evennia from '../services/evennia'

export function useGameState() {
  const [connectionState, setConnectionState] = useState('disconnected') // disconnected, connecting, connected
  const [loginState, setLoginState] = useState('logged_out') // logged_out, logging_in, logged_in, in_game
  const [messages, setMessages] = useState([])
  const [player, setPlayer] = useState(null)
  const [target, setTarget] = useState(null)
  const [entities, setEntities] = useState({})
  const [error, setError] = useState(null)

  const connect = useCallback(async () => {
    setConnectionState('connecting')
    setError(null)
    
    try {
      await evennia.connect({
        onOpen: () => {
          setConnectionState('connected')
          addMessage('system', 'Network link established.')
        },
        onMessage: (type, data) => {
          handleMessage(type, data)
        },
        onError: (err) => {
          setError('Connection error')
          addMessage('error', 'Network error occurred.')
        },
        onClose: () => {
          setConnectionState('disconnected')
          addMessage('system', 'Connection lost.')
        }
      })
    } catch (err) {
      setConnectionState('disconnected')
      setError(err.message)
    }
  }, [])

  const handleMessage = useCallback((type, data) => {
    if (type === 'text') {
      // Server text output
      const text = data.parsed?.raw || data.raw || data.text || ''
      const isSystem = text.toLowerCase().includes('system') || 
                       text.toLowerCase().includes('welcome') ||
                       text.toLowerCase().includes('ooc')
      addMessage(isSystem ? 'system' : 'general', text)
      
      // Check for login success
      if (text.includes('OOC') || text.includes('Welcome')) {
        setLoginState('logged_in')
      }
    } else if (type === 'json') {
      // Game state updates
      if (data.type === 'player_frame') {
        setPlayer(data.entity)
      } else if (data.type === 'entity_delta') {
        handleEntityUpdate(data.entity)
      } else if (data.type === 'target_update') {
        setTarget(data)
      }
    }
  }, [])

  const handleEntityUpdate = useCallback((entity) => {
    setEntities(prev => ({
      ...prev,
      [entity.id]: entity
    }))
  }, [])

  const addMessage = useCallback((type, text) => {
    setMessages(prev => [...prev.slice(-100), { type, text, timestamp: Date.now() }])
  }, [])

  const sendCommand = useCallback((cmd) => {
    if (connectionState !== 'connected') return
    addMessage('command', `> ${cmd}`)
    evennia.sendCommand(cmd)
  }, [connectionState, addMessage])

  const login = useCallback((username, password) => {
    setLoginState('logging_in')
    setError(null)
    sendCommand(`connect ${username} ${password}`)
  }, [sendCommand])

  const logout = useCallback(() => {
    sendCommand('quit')
    setLoginState('logged_out')
    setPlayer(null)
    setTarget(null)
    setEntities({})
  }, [sendCommand])

  return {
    // State
    connectionState,
    loginState,
    messages,
    player,
    target,
    entities,
    error,
    // Actions
    connect,
    sendCommand,
    login,
    logout,
    setTarget
  }
}

export default useGameState
