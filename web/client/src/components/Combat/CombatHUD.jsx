import React, { useState, useEffect, useCallback } from 'react'

/**
 * CombatHUD - Real-time combat interface
 * Features:
 * - Attack buttons with cooldowns
 * - Technique hotbar (1-9)
 * - Floating damage numbers
 * - Guard/charge indicators
 */
export function CombatHUD({ player, target, onCommand, cooldowns = {} }) {
  const [damageNumbers, setDamageNumbers] = useState([])
  const [combo, setCombo] = useState(0)
  const [lastHitTime, setLastHitTime] = useState(0)

  // Quick attack buttons
  const attacks = [
    { key: 'attack', label: 'Attack', icon: '⚔️', color: '#ff3366' },
    { key: 'flee', label: 'Flee', icon: '🏃', color: '#ffd74a' },
    { key: 'guard', label: 'Guard', icon: '🛡️', color: '#00aeff' },
    { key: 'charge', label: 'Charge', icon: '⚡', color: '#ffd74a' },
    { key: 'counter', label: 'Counter', icon: '⚔️', color: '#ff6b35' },
  ]

  // Technique hotbar (1-5)
  const hotbar = [
    { key: '1', command: 'tech kamehameha', label: 'Kamehameha' },
    { key: '2', command: 'tech spirit_bomb', label: 'Spirit Bomb' },
    { key: '3', command: 'tech solar_flare', label: 'Solar Flare' },
    { key: '4', command: 'tech destructo_disc', label: 'Destructo Disc' },
    { key: '5', command: 'tech masenko', label: 'Masenko' },
  ]

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Number keys for techniques
      if (e.key >= '1' && e.key <= '5') {
        const idx = parseInt(e.key) - 1
        if (hotbar[idx] && !cooldowns[hotbar[idx].command]) {
          onCommand(hotbar[idx].command)
        }
      }
      // Space for attack
      if (e.key === ' ' && !e.target.matches('input, textarea')) {
        e.preventDefault()
        onCommand('attack')
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onCommand, cooldowns])

  // Add damage number
  const addDamageNumber = useCallback((amount, type = 'damage') => {
    const now = Date.now()
    if (now - lastHitTime > 1000) {
      setCombo(0)
    }
    setCombo(c => c + 1)
    setLastHitTime(now)
    
    const id = now + Math.random()
    setDamageNumbers(prev => [...prev, { id, amount, type, combo: combo + 1 }])
    
    // Remove after animation
    setTimeout(() => {
      setDamageNumbers(prev => prev.filter(d => d.id !== id))
    }, 1000)
  }, [lastHitTime, combo])

  return (
    <div className="combat-hud">
      {/* Top: Quick Actions */}
      <div className="combat-actions">
        {attacks.map((attack) => {
          const cd = cooldowns[attack.key] || 0
          const isOnCooldown = cd > 0
          
          return (
            <button
              key={attack.key}
              className="combat-button"
              onClick={() => onCommand(attack.key)}
              disabled={isOnCooldown}
              style={{
                '--btn-color': attack.color,
                opacity: isOnCooldown ? 0.5 : 1
              }}
            >
              <span className="combat-icon">{attack.icon}</span>
              <span className="combat-label">{attack.label}</span>
              {isOnCooldown && (
                <div 
                  className="cooldown-overlay" 
                  style={{ height: `${(cd / 3) * 100}%` }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Bottom: Technique Hotbar */}
      <div className="hotbar">
        {hotbar.map((slot, i) => {
          const cd = cooldowns[slot.command] || 0
          const isOnCooldown = cd > 0
          
          return (
            <button
              key={slot.key}
              className="hotbar-slot"
              onClick={() => !isOnCooldown && onCommand(slot.command)}
              disabled={isOnCooldown}
              style={{
                opacity: isOnCooldown ? 0.4 : 1,
                borderColor: isOnCooldown ? '#666' : '#00aeff'
              }}
            >
              <span className="hotbar-key">{slot.key}</span>
              <span className="hotbar-label">{slot.label}</span>
              {isOnCooldown && (
                <div 
                  className="cooldown-fill" 
                  style={{ height: `${(cd / 10) * 100}%` }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Combo Counter */}
      {combo > 1 && (
        <div className="combo-counter">
          {combo} HIT COMBO!
        </div>
      )}

      {/* Target Info */}
      {target && (
        <div className="target-info">
          <div className="target-name">{target.name}</div>
          <div className="target-hp-bar">
            <div 
              className="target-hp-fill"
              style={{ width: `${(target.hp / target.hp_max) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Floating Damage Numbers */}
      <div className="damage-numbers">
        {damageNumbers.map(dn => (
          <div 
            key={dn.id}
            className={`damage-number ${dn.type}`}
            style={{
              '--combo': Math.min(dn.combo, 10)
            }}
          >
            {dn.type === 'heal' ? '+' : '-'}{dn.amount}
          </div>
        ))}
      </div>

      <style>{`
        .combat-hud {
          position: absolute;
          bottom: 220px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          z-index: 100;
        }

        .combat-actions {
          display: flex;
          gap: 8px;
        }

        .combat-button {
          position: relative;
          width: 70px;
          height: 70px;
          background: rgba(0, 0, 0, 0.8);
          border: 2px solid var(--btn-color);
          border-radius: 12px;
          color: #fff;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          transition: transform 0.1s, box-shadow 0.2s;
        }

        .combat-button:hover {
          transform: scale(1.05);
          box-shadow: 0 0 20px var(--btn-color);
        }

        .combat-button:active {
          transform: scale(0.95);
        }

        .combat-icon {
          font-size: 1.5rem;
        }

        .combat-label {
          font-size: 0.7rem;
          margin-top: 2px;
        }

        .cooldown-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: rgba(0, 0, 0, 0.7);
          transition: height 0.1s;
        }

        .hotbar {
          display: flex;
          gap: 6px;
          background: rgba(0, 0, 0, 0.8);
          padding: 8px;
          border-radius: 8px;
          border: 1px solid #333;
        }

        .hotbar-slot {
          position: relative;
          width: 100px;
          height: 40px;
          background: rgba(20, 20, 30, 0.9);
          border: 1px solid #00aeff;
          border-radius: 6px;
          color: #fff;
          cursor: pointer;
          display: flex;
          align-items: center;
          padding: 0 8px;
          gap: 8px;
          overflow: hidden;
        }

        .hotbar-slot:hover {
          background: rgba(0, 174, 255, 0.2);
        }

        .hotbar-key {
          background: #00aeff;
          color: #000;
          width: 20px;
          height: 20px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: 700;
        }

        .hotbar-label {
          font-size: 0.8rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .cooldown-fill {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: rgba(255, 51, 102, 0.5);
        }

        .combo-counter {
          position: absolute;
          top: -60px;
          font-size: 1.5rem;
          font-weight: 900;
          color: #ff6b35;
          text-shadow: 0 0 10px #ff6b35, 0 0 20px #ff6b35;
          animation: pulse 0.3s ease-out;
        }

        @keyframes pulse {
          0% { transform: scale(1.5); opacity: 0; }
          100% { transform: scale(1); opacity: 1; }
        }

        .target-info {
          position: absolute;
          top: -120px;
          left: 50%;
          transform: translateX(-50%);
          text-align: center;
        }

        .target-name {
          font-size: 1.2rem;
          font-weight: 700;
          color: #ff3366;
          text-shadow: 0 0 10px rgba(255, 51, 102, 0.5);
          margin-bottom: 4px;
        }

        .target-hp-bar {
          width: 200px;
          height: 8px;
          background: rgba(0, 0, 0, 0.6);
          border-radius: 4px;
          overflow: hidden;
        }

        .target-hp-fill {
          height: 100%;
          background: linear-gradient(90deg, #ff3366, #ff6688);
          transition: width 0.3s ease;
        }

        .damage-numbers {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
        }

        .damage-number {
          position: absolute;
          font-size: 1.5rem;
          font-weight: 900;
          animation: floatUp 1s ease-out forwards;
          text-shadow: 2px 2px 0 #000;
        }

        .damage-number.damage {
          color: #ff3366;
        }

        .damage-number.heal {
          color: #32ff64;
        }

        @keyframes floatUp {
          0% {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
          100% {
            opacity: 0;
            transform: translateY(-100px) scale(0.5);
          }
        }
      `}</style>
    </div>
  )
}

export default CombatHUD
