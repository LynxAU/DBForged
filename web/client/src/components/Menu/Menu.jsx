import React, { useState } from 'react'
import { Inventory, Techniques, Quests } from '../Inventory/Inventory'

/**
 * MenuPanel - Tabbed menu for character info
 */
export function MenuPanel({ player, onCommand }) {
  const [activeTab, setActiveTab] = useState('inventory')
  
  // Mock data - will come from server
  const inventory = player?.inventory || []
  const techniques = player?.techniques || []
  const quests = player?.quests || []

  const tabs = [
    { id: 'inventory', label: 'Inventory', color: '#00aeff' },
    { id: 'techniques', label: 'Techs', color: '#ffd74a' },
    { id: 'quests', label: 'Quests', color: '#32ff64' },
    { id: 'forms', label: 'Forms', color: '#ff6b35' },
    { id: 'social', label: 'Social', color: '#cc66ff' },
  ]

  return (
    <div className="glass-panel" style={{ padding: '16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
      {/* Tab Bar */}
      <div style={{ 
        display: 'flex', 
        gap: '4px', 
        marginBottom: '16px',
        borderBottom: '1px solid rgba(0, 174, 255, 0.2)',
        paddingBottom: '8px'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '8px 16px',
              background: activeTab === tab.id ? `${tab.color}22` : 'transparent',
              border: `1px solid ${activeTab === tab.id ? tab.color : 'transparent'}`,
              borderRadius: '4px',
              color: activeTab === tab.id ? tab.color : '#888',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {activeTab === 'inventory' && (
          <Inventory inventory={inventory} />
        )}
        
        {activeTab === 'techniques' && (
          <Techniques techniques={techniques} />
        )}
        
        {activeTab === 'quests' && (
          <Quests quests={quests} />
        )}
        
        {activeTab === 'forms' && (
          <div style={{ padding: '16px' }}>
            <div style={{ marginBottom: '12px', fontWeight: 600, color: '#ff6b35' }}>
              Transformations
            </div>
            <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>
              Use {'<transform <form>>'} to transform.
            </div>
            <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {player?.forms?.map((form, i) => (
                <div key={i} style={{ 
                  padding: '8px 12px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderRadius: '4px'
                }}>
                  <div style={{ fontWeight: 600 }}>{form.name}</div>
                  <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>{form.description}</div>
                </div>
              )) || <div style={{ opacity: 0.5 }}>No forms available.</div>}
            </div>
          </div>
        )}
        
        {activeTab === 'social' && (
          <div style={{ padding: '16px' }}>
            <div style={{ marginBottom: '12px', fontWeight: 600, color: '#cc66ff' }}>
              Social
            </div>
            
            {/* Guild */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Guild</div>
              {player?.guild ? (
                <div style={{ 
                  padding: '12px',
                  background: 'rgba(204, 102, 255, 0.1)',
                  borderRadius: '8px',
                  border: '1px solid rgba(204, 102, 255, 0.3)'
                }}>
                  <div style={{ fontWeight: 600 }}>{player.guild.name}</div>
                  <div style={{ fontSize: '0.85rem', opacity: 0.7 }}>
                    {player.guild.members?.length || 0} members
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: '0.9rem', opacity: 0.5 }}>
                  You don't belong to a guild.
                  <button 
                    onClick={() => onCommand('guild list')}
                    style={{ 
                      marginLeft: '8px', 
                      color: '#cc66ff',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                  >
                    Browse Guilds
                  </button>
                </div>
              )}
            </div>
            
            {/* Friends */}
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Friends</div>
              {player?.friends?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {player.friends.map((friend, i) => (
                    <div key={i} style={{ fontSize: '0.9rem' }}>
                      {friend.name} - {friend.status}
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: '0.9rem', opacity: 0.5 }}>
                  No friends yet.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MenuPanel
