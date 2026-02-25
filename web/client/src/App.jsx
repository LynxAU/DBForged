import { useEffect, useState } from 'react'
import { useGameState } from './hooks/useGameState'
import GameCanvas from './components/GameCanvas/GameCanvas'
import { PlayerHud, TargetHud } from './components/PlayerHud/PlayerHud'
import Chat from './components/Chat/Chat'
import Login from './components/Login/Login'
import { MenuPanel } from './components/Menu/Menu'

function App() {
  const {
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
    logout
  } = useGameState()

  const [showMenu, setShowMenu] = useState(false)

  // Auto-connect on mount
  // Only auto-connect once on mount — individual sockets handle their own
  // reconnection internally. Re-triggering connect() on every close would
  // stack new connections on top of in-flight reconnect attempts.
  useEffect(() => {
    connect()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Escape to close menu
      if (e.key === 'Escape') {
        setShowMenu(false)
      }
      // M for menu
      if (e.key === 'm' && !e.ctrlKey && !e.altKey) {
        setShowMenu(prev => !prev)
      }
      // Number keys for quick actions
      if (!showMenu && e.key >= '1' && e.key <= '5') {
        const actions = ['attack', 'flee', 'guard', 'charge', 'scan']
        sendCommand(actions[parseInt(e.key) - 1])
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [sendCommand, showMenu])

  // Show login screen if not logged in
  if (loginState === 'logged_out' || loginState === 'logging_in') {
    return (
      <Login
        onLogin={login}
        onRetry={reconnect}
        error={error}
        connectionState={connectionState}
      />
    )
  }

  // Main game view
  return (
    <div className="app">
      {/* Left Sidebar - Player HUD */}
      <div className="left-sidebar">
        <PlayerHud player={player} />
        
        {/* Quick Actions */}
        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ marginBottom: '12px', fontWeight: 600 }}>Quick Actions</div>
          <div className="action-bar">
            <button className="action-button" onClick={() => sendCommand('attack')}>Attack</button>
            <button className="action-button" onClick={() => sendCommand('flee')}>Flee</button>
            <button className="action-button" onClick={() => sendCommand('guard')}>Guard</button>
            <button className="action-button" onClick={() => sendCommand('charge')}>Charge</button>
          </div>
        </div>
      </div>

      {/* Center - Canvas + Chat */}
      <GameCanvas entities={entities} player={player} />
      <Chat messages={messages} onSendCommand={sendCommand} />

      {/* Right Sidebar - Target + Info */}
      <div className="right-sidebar">
        <TargetHud target={target} />
        
        {/* Menu Toggle */}
        <button 
          className="action-button" 
          onClick={() => setShowMenu(!showMenu)}
          style={{ background: showMenu ? '#00aeff' : undefined }}
        >
          {showMenu ? 'Close Menu' : 'Menu (M)'}
        </button>
        
        {/* Menu Panel */}
        {showMenu && (
          <MenuPanel player={player} onCommand={sendCommand} />
        )}
        
        {/* Mini Map / Compass placeholder */}
        {!showMenu && (
          <div className="glass-panel" style={{ padding: '16px', flex: 1 }}>
            <div style={{ marginBottom: '12px', fontWeight: 600 }}>Compass</div>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(3, 1fr)', 
              gap: '4px',
              maxWidth: '120px',
              margin: '0 auto'
            }}>
              <div />
              <div style={{ textAlign: 'center', color: '#00aeff' }}>N</div>
              <div />
              <div style={{ textAlign: 'center', color: '#00aeff' }}>W</div>
              <div style={{ textAlign: 'center', color: '#ffd700' }}>●</div>
              <div style={{ textAlign: 'center', color: '#00aeff' }}>E</div>
              <div />
              <div style={{ textAlign: 'center', color: '#00aeff' }}>S</div>
              <div />
            </div>
          </div>
        )}
        
        {/* Logout */}
        <button 
          className="action-button" 
          onClick={logout}
          style={{ background: '#ff3366', borderColor: '#ff3366' }}
        >
          Logout
        </button>
      </div>
    </div>
  )
}

export default App
