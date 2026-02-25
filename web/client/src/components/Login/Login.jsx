import React, { useState, useEffect, useRef } from 'react'
import { GokuArt, VegetaArt } from './CharacterArt'

export function Login({ onLogin, onRetry, error, connectionState }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const usernameRef = useRef(null)

  // Focus username on mount
  useEffect(() => {
    usernameRef.current?.focus()
  }, [])

  // Reset submitted flag when an error arrives (so next attempt tracks fresh)
  useEffect(() => {
    if (error) setSubmitted(false)
  }, [error])

  const handleSubmit = (e) => {
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
  const canLogin      = isConnected && username.trim() && password && !submitted

  const statusLabel = {
    connected:    'SERVER ONLINE',
    connecting:   'CONNECTING\u2026',
    disconnected: 'SERVER OFFLINE',
  }[connectionState] ?? ''

  return (
    <div className="lb-screen">

      {/* ── Background atmosphere ── */}
      <div className="lb-bg" />

      {/* ── Full-screen hero art ── */}
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

        {/* Login panel */}
        <div className="lb-panel glass-panel">

          {/* Server offline state */}
          {isDisconnected && (
            <div className="lb-offline">
              <p className="lb-offline-msg">Cannot reach the game server.</p>
              <button className="lb-retry-btn" onClick={handleRetry}>
                RETRY CONNECTION
              </button>
            </div>
          )}

          {/* Login form — shown while connected or connecting */}
          {!isDisconnected && (
            <form onSubmit={handleSubmit} className="lb-form">
              <input
                ref={usernameRef}
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

          {/* Error message */}
          {error && (
            <div className="lb-error" key={error}>{error}</div>
          )}
        </div>

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
