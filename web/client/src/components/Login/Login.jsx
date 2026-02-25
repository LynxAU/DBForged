import React, { useState, useEffect, useRef } from 'react'
import { GokuArt, VegetaArt } from './CharacterArt'
import { CharacterCreator } from './CharacterCreator'

export function Login({ onLogin, onCreateAccount, onRetry, error, connectionState }) {
  const [view,      setView]      = useState('menu') // 'menu' | 'login' | 'create'
  const [username,  setUsername]  = useState('')
  const [password,  setPassword]  = useState('')
  const [submitted, setSubmitted] = useState(false)

  const loginUsernameRef = useRef(null)

  // Focus the username field when switching to login
  useEffect(() => {
    if (view === 'login') setTimeout(() => loginUsernameRef.current?.focus(), 50)
  }, [view])

  // Reset submitted flag when an error arrives so the next attempt tracks fresh
  useEffect(() => {
    if (error) setSubmitted(false)
  }, [error])

  const goBack = () => {
    setView('menu')
    setSubmitted(false)
    setUsername('')
    setPassword('')
  }

  const handleLoginSubmit = (e) => {
    e.preventDefault()
    if (!canLogin) return
    setSubmitted(true)
    onLogin(username, password)
  }

  const handleRetry = () => {
    setSubmitted(false)
    onRetry?.()
  }

  const isConnected    = connectionState === 'connected'
  const isDisconnected = connectionState === 'disconnected'
  const canLogin       = isConnected && username.trim() && password && !submitted

  const statusLabel = {
    connected:    'SERVER ONLINE',
    connecting:   'CONNECTING\u2026',
    disconnected: 'SERVER OFFLINE',
  }[connectionState] ?? ''

  // Character creator is its own full-screen flow
  if (view === 'create') {
    return (
      <CharacterCreator
        onCreateAccount={onCreateAccount}
        onBack={() => setView('menu')}
        connectionState={connectionState}
        error={error}
      />
    )
  }

  return (
    <div className="lb-screen">

      {/* ── Background atmosphere ── */}
      <div className="lb-bg" />
      <img src="/static/ui/dbf.png" className="lb-hero-bg" alt="" draggable={false} />
      <div className="lb-hero-overlay" />
      <div className="lb-corona" />

      {/* ── Floating ki orbs ── */}
      <div className="lb-orb lb-orb-1" />
      <div className="lb-orb lb-orb-2" />
      <div className="lb-orb lb-orb-3" />
      <div className="lb-orb lb-orb-4" />

      {/* ── Character art flanking the panel ── */}
      <GokuArt   className="lb-char lb-char-goku" />
      <VegetaArt className="lb-char lb-char-vegeta" />

      {/* ── Ground glow ── */}
      <div className="lb-ground" />

      {/* ── Center column ── */}
      <div className="lb-content">

        {/* Logo */}
        <div className="lb-logo-wrap">
          <div className="lb-aura" />
          <img
            src="/static/ui/dbforgedfullcoloralpha.png"
            alt="Dragon Ball Forged"
            className="lb-logo"
            draggable={false}
          />
        </div>

        {/* ── MAIN MENU VIEW ── */}
        {view === 'menu' && (
          <div className="lb-menu-btns">
            {isDisconnected ? (
              <>
                <p className="lb-offline-msg">Cannot reach the game server.</p>
                <button className="lb-retry-btn" onClick={handleRetry}>
                  RETRY CONNECTION
                </button>
              </>
            ) : (
              <>
                <button
                  className="lb-menu-btn lb-menu-btn-primary"
                  onClick={() => setView('login')}
                  disabled={!isConnected}
                >
                  <span className="lb-menu-btn-text">ENTER THE BATTLEFIELD</span>
                  <div className="lb-button-shine" />
                </button>
                <button
                  className="lb-menu-btn lb-menu-btn-secondary"
                  onClick={() => setView('create')}
                  disabled={!isConnected}
                >
                  <span className="lb-menu-btn-text">CREATE A WARRIOR</span>
                  <div className="lb-button-shine" />
                </button>
              </>
            )}
          </div>
        )}

        {/* ── LOGIN VIEW ── */}
        {view === 'login' && (
          <div className="lb-panel glass-panel">
            {isDisconnected ? (
              <div className="lb-offline">
                <p className="lb-offline-msg">Cannot reach the game server.</p>
                <button className="lb-retry-btn" onClick={handleRetry}>
                  RETRY CONNECTION
                </button>
              </div>
            ) : (
              <form onSubmit={handleLoginSubmit} className="lb-form">
                <input
                  ref={loginUsernameRef}
                  type="text"
                  className="lb-input"
                  placeholder="Warrior Name"
                  value={username}
                  onChange={e => { setUsername(e.target.value); setSubmitted(false) }}
                  disabled={!isConnected}
                  autoComplete="username"
                  spellCheck={false}
                />
                <input
                  type="password"
                  className="lb-input"
                  placeholder="Ki Signature"
                  value={password}
                  onChange={e => { setPassword(e.target.value); setSubmitted(false) }}
                  disabled={!isConnected}
                  autoComplete="current-password"
                />
                <button type="submit" className="lb-button" disabled={!canLogin}>
                  <span className="lb-button-text">
                    {submitted ? 'POWERING UP\u2026' : 'ENTER THE BATTLEFIELD'}
                  </span>
                  <div className="lb-button-shine" />
                </button>
              </form>
            )}
            {error && <div className="lb-error" key={error}>{error}</div>}
            <button className="lb-back-btn" onClick={goBack}>← BACK TO MENU</button>
          </div>
        )}

        {/* Connection status dot */}
        <div className="lb-status">
          <span className={`lb-dot lb-dot-${connectionState}`} />
          <span className="lb-status-label">{statusLabel}</span>
        </div>

        <p className="lb-tagline">A DRAGON BALL MMO EXPERIENCE</p>
      </div>
    </div>
  )
}

export default Login
