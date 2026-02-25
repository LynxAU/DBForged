import { useEffect, useState } from 'react'
import { useGameState } from './hooks/useGameState'
import GameCanvas from './components/GameCanvas/GameCanvas'
import { PlayerHud, TargetHud } from './components/PlayerHud/PlayerHud'
import { Chat } from './components/Chat/Chat'
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
    createAccount,
    logout
  } = useGameState()

  const [showMenu, setShowMenu] = useState(false)

  // Auto-connect once on mount
  useEffect(() => {
    connect()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape')                           setShowMenu(false)
      if (e.key === 'm' && !e.ctrlKey && !e.altKey)    setShowMenu(p => !p)
      if (!showMenu && e.key >= '1' && e.key <= '4') {
        const actions = ['attack', 'flee', 'guard', 'charge']
        sendCommand(actions[parseInt(e.key) - 1])
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [sendCommand, showMenu])

  // ── Login screen ──────────────────────────────────────────────────────────
  if (loginState === 'logged_out' || loginState === 'logging_in') {
    return (
      <Login
        onLogin={login}
        onCreateAccount={createAccount}
        onRetry={reconnect}
        error={error}
        connectionState={connectionState}
      />
    )
  }

  // ── Room / location name from player data ─────────────────────────────────
  const roomName = player?.room ?? player?.location ?? null

  // ── Main game view ────────────────────────────────────────────────────────
  return (
    <div className="game-viewport">

      {/* ── Canvas fills entire background ── */}
      <GameCanvas entities={entities} player={player} />

      {/* ── Player HUD — top-left ── */}
      <div className="hud-overlay hud-player">
        <PlayerHud player={player} />
      </div>

      {/* ── Target HUD — top-right ── */}
      <div className="hud-overlay hud-target">
        <TargetHud target={target} />
      </div>

      {/* ── Location pill — top-center ── */}
      {roomName && (
        <div className="hud-location">
          <span className="hud-location-dot" />
          {roomName}
        </div>
      )}

      {/* ── Action bar — bottom-left (above chat) ── */}
      <div className="hud-actions-wrap">
        <div className="hud-action-bar">
          <button className="hud-action-btn hud-action-attack" onClick={() => sendCommand('attack')}>
            <span className="hud-action-key">1</span>
            <span className="hud-action-icon">⚔</span>
            <span className="hud-action-label">Attack</span>
          </button>
          <button className="hud-action-btn hud-action-flee" onClick={() => sendCommand('flee')}>
            <span className="hud-action-key">2</span>
            <span className="hud-action-icon">💨</span>
            <span className="hud-action-label">Flee</span>
          </button>
          <button className="hud-action-btn hud-action-guard" onClick={() => sendCommand('guard')}>
            <span className="hud-action-key">3</span>
            <span className="hud-action-icon">🛡</span>
            <span className="hud-action-label">Guard</span>
          </button>
          <button className="hud-action-btn hud-action-charge" onClick={() => sendCommand('charge')}>
            <span className="hud-action-key">4</span>
            <span className="hud-action-icon">⚡</span>
            <span className="hud-action-label">Charge</span>
          </button>
        </div>
      </div>

      {/* ── Chat terminal — bottom-center ── */}
      <div className="hud-chat-wrap">
        <Chat messages={messages} onSendCommand={sendCommand} />
      </div>

      {/* ── Menu / Logout — bottom-right ── */}
      <div className="hud-menu-corner">
        {showMenu && (
          <div className="hud-menu-panel">
            <MenuPanel player={player} onCommand={sendCommand} />
          </div>
        )}
        <div className="hud-corner-btns">
          <button
            className={`hud-corner-btn${showMenu ? ' active' : ''}`}
            onClick={() => setShowMenu(p => !p)}
            title="Menu (M)"
          >
            ☰
          </button>
          <button
            className="hud-corner-btn hud-corner-logout"
            onClick={logout}
            title="Logout"
          >
            ⏻
          </button>
        </div>
      </div>

    </div>
  )
}

export default App
