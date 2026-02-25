import React, { useState } from 'react'

/**
 * Login - Login screen
 */
export function Login({ onLogin, error, connectionState }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (username && password) {
      onLogin(username, password)
    }
  }

  const isConnecting = connectionState === 'connecting'
  const canLogin = username && password && !isConnecting

  return (
    <div className="login-screen">
      <div className="glass-panel login-box">
        <h1 className="login-title">DBFORGED</h1>
        <p className="login-subtitle">Dragon Ball MMO</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            className="login-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isConnecting}
            autoFocus
          />
          
          <input
            type="password"
            className="login-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isConnecting}
          />
          
          <button 
            type="submit" 
            className="login-button"
            disabled={!canLogin}
          >
            {isConnecting ? 'Connecting...' : 'Enter'}
          </button>
          
          {error && (
            <div className="login-error">{error}</div>
          )}
        </form>
      </div>
    </div>
  )
}

export default Login
