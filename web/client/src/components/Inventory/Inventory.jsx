import React from 'react'

/**
 * Inventory - Shows player inventory items
 */
export function Inventory({ inventory = [] }) {
  return (
    <div className="glass-panel" style={{ padding: '16px', flex: 1, overflow: 'auto' }}>
      <div style={{ marginBottom: '12px', fontWeight: 600, color: '#00aeff' }}>
        Inventory
      </div>
      
      {inventory.length === 0 ? (
        <div style={{ opacity: 0.5, fontStyle: 'italic' }}>
          Your inventory is empty.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {inventory.map((item, i) => (
            <div 
              key={i}
              style={{
                padding: '8px 12px',
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '4px',
                border: '1px solid rgba(0, 174, 255, 0.2)',
                fontSize: '0.9rem'
              }}
            >
              {item}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Techniques - Shows learned techniques
 */
export function Techniques({ techniques = [] }) {
  return (
    <div className="glass-panel" style={{ padding: '16px', flex: 1, overflow: 'auto' }}>
      <div style={{ marginBottom: '12px', fontWeight: 600, color: '#ffd74a' }}>
        Techniques
      </div>
      
      {techniques.length === 0 ? (
        <div style={{ opacity: 0.5, fontStyle: 'italic' }}>
          You haven't learned any techniques yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {techniques.map((tech, i) => (
            <div 
              key={i}
              style={{
                padding: '8px 12px',
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '4px',
                border: '1px solid rgba(255, 215, 0, 0.2)',
                fontSize: '0.9rem'
              }}
            >
              <div style={{ fontWeight: 600 }}>{tech.name}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                {tech.description}
              </div>
              {tech.ki_cost > 0 && (
                <div style={{ fontSize: '0.75rem', color: '#00aeff', marginTop: '4px' }}>
                  Ki Cost: {tech.ki_cost}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Quests - Shows active quests
 */
export function Quests({ quests = [] }) {
  return (
    <div className="glass-panel" style={{ padding: '16px', flex: 1, overflow: 'auto' }}>
      <div style={{ marginBottom: '12px', fontWeight: 600, color: '#32ff64' }}>
        Quests
      </div>
      
      {quests.length === 0 ? (
        <div style={{ opacity: 0.5, fontStyle: 'italic' }}>
          You have no active quests.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {quests.map((quest, i) => (
            <div 
              key={i}
              style={{
                padding: '8px 12px',
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '4px',
                border: '1px solid rgba(50, 255, 100, 0.2)',
                fontSize: '0.9rem'
              }}
            >
              <div style={{ fontWeight: 600 }}>{quest.name}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.7, marginTop: '4px' }}>
                {quest.description}
              </div>
              {quest.objectives && (
                <div style={{ fontSize: '0.75rem', marginTop: '8px' }}>
                  {quest.objectives.map((obj, j) => (
                    <div 
                      key={j}
                      style={{ 
                        color: obj.complete ? '#32ff64' : '#ffd74a',
                        marginTop: '2px'
                      }}
                    >
                      {obj.complete ? '✓' : '○'} {obj.text}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Inventory
