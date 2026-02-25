import React from 'react'

/**
 * PlayerHud - Shows player stats (HP, Ki, Stamina, PL)
 */
export function PlayerHud({ player }) {
  if (!player) return null

  const hp = player.hp || 0
  const hpMax = player.hp_max || 1
  const ki = player.ki || 0
  const kiMax = player.ki_max || 1
  const stamina = player.stamina || 0
  const staminaMax = player.stamina_max || 1
  const pl = player.displayed_pl || player.pl || 0

  return (
    <div className="glass-panel player-hud">
      <div className="hud-title">{player.name}</div>
      
      {/* HP Bar */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>HP</span>
          <span>{hp.toLocaleString()} / {hpMax.toLocaleString()}</span>
        </div>
        <div className="stat-track">
          <div 
            className="stat-fill hp" 
            style={{ width: `${(hp / hpMax) * 100}%` }} 
          />
        </div>
      </div>
      
      {/* Ki Bar */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>Ki</span>
          <span>{ki.toLocaleString()} / {kiMax.toLocaleString()}</span>
        </div>
        <div className="stat-track">
          <div 
            className="stat-fill ki" 
            style={{ width: `${(ki / kiMax) * 100}%` }} 
          />
        </div>
      </div>
      
      {/* Stamina Bar */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>Stamina</span>
          <span>{stamina} / {staminaMax}</span>
        </div>
        <div className="stat-track">
          <div 
            className="stat-fill stamina" 
            style={{ width: `${(stamina / staminaMax) * 100}%` }} 
          />
        </div>
      </div>
      
      {/* Power Level */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>Power Level</span>
          <span>{pl.toLocaleString()}</span>
        </div>
        <div className="stat-track">
          <div 
            className="stat-fill pl" 
            style={{ width: '100%' }} 
          />
        </div>
      </div>
      
      {/* Active Form */}
      {player.active_form && (
        <div style={{ marginTop: '12px', color: '#ffd74a' }}>
          Form: {player.active_form}
        </div>
      )}
    </div>
  )
}

/**
 * TargetHud - Shows target's stats
 */
export function TargetHud({ target }) {
  if (!target) {
    return (
      <div className="glass-panel target-hud">
        <div className="hud-title">Target</div>
        <div style={{ opacity: 0.5, fontStyle: 'italic' }}>
          No target selected
        </div>
      </div>
    )
  }

  const hp = target.hp || 0
  const hpMax = target.hp_max || 1
  const pl = target.displayed_pl || target.pl || 0

  return (
    <div className="glass-panel target-hud">
      <div className="hud-title">{target.name}</div>
      
      {/* HP Bar */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>HP</span>
          <span>{hp.toLocaleString()} / {hpMax.toLocaleString()}</span>
        </div>
        <div className="stat-track">
          <div 
            className="stat-fill hp" 
            style={{ width: `${(hp / hpMax) * 100}%` }} 
          />
        </div>
      </div>
      
      {/* Power Level (estimated/displayed) */}
      <div className="stat-bar">
        <div className="stat-label">
          <span>PL (Estimated)</span>
          <span>{pl.toLocaleString()}</span>
        </div>
        <div className="stat-track">
          <div 
            className="stat-fill pl" 
            style={{ width: '100%' }} 
          />
        </div>
      </div>
    </div>
  )
}

export default PlayerHud
