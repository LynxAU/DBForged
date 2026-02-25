import React, { useState, useRef, useEffect } from 'react'

/**
 * WorldMap - Full-screen map with markers
 */
export function WorldMap({ isOpen, onClose, player, locations = [] }) {
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const canvasRef = useRef(null)

  // Example locations - would come from server
  const defaultLocations = [
    { id: 'earth', name: 'Earth', x: 500, y: 400, type: 'planet', icon: '🌍' },
    { id: 'north_city', name: 'North City', x: 450, y: 350, type: 'city', icon: '🏙️' },
    { id: 'west_city', name: 'West City', x: 380, y: 420, type: 'city', icon: '🏙️' },
    { id: 'capsule_corp', name: 'Capsule Corp', x: 400, y: 410, type: 'shop', icon: '🏢' },
    { id: 'kame_house', name: "Kame's House", x: 520, y: 450, type: 'trainer', icon: '🏠' },
    { id: 'tournament_arena', name: 'Tournament Arena', x: 480, y: 380, type: 'event', icon: '🏟️' },
    { id: 'mountain', name: 'Mount Paozu', x: 420, y: 500, type: 'wild', icon: '⛰️' },
  ]

  const allLocations = locations.length > 0 ? locations : defaultLocations

  // Handle zoom
  const handleZoom = (delta) => {
    setZoom(z => Math.max(0.5, Math.min(3, z + delta)))
  }

  // Handle pan
  const handleMouseDown = (e) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  // Center on player
  const centerOnPlayer = () => {
    if (player?.position) {
      setPan({ x: -player.position.x * zoom + 400, y: -player.position.y * zoom + 300 })
    } else {
      setPan({ x: 0, y: 0 })
    }
  }

  if (!isOpen) return null

  return (
    <div className="map-overlay" onClick={onClose}>
      <div className="map-container" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="map-header">
          <h2>World Map</h2>
          <div className="map-controls">
            <button onClick={() => handleZoom(0.25)}>+</button>
            <span>{Math.round(zoom * 100)}%</span>
            <button onClick={() => handleZoom(-0.25)}>-</button>
            <button onClick={centerOnPlayer}>Center</button>
            <button onClick={onClose}>✕</button>
          </div>
        </div>

        {/* Map Canvas */}
        <div 
          className="map-viewport"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <div 
            className="map-content"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              cursor: isDragging ? 'grabbing' : 'grab'
            }}
          >
            {/* Grid Background */}
            <svg className="map-grid" width="1200" height="1000">
              <defs>
                <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(0, 174, 255, 0.1)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>

            {/* World Background */}
            <div className="map-world">
              {/* Continents (simplified) */}
              <div className="continent landmass-1" style={{ left: '30%', top: '25%' }} />
              <div className="continent landmass-2" style={{ left: '55%', top: '35%' }} />
              <div className="continent landmass-3" style={{ left: '25%', top: '55%' }} />
              
              {/* Ocean */}
              <div className="ocean" style={{ left: '0', top: '0' }} />
            </div>

            {/* Location Markers */}
            {allLocations.map(loc => (
              <div
                key={loc.id}
                className={`map-marker ${loc.type}`}
                style={{ left: loc.x, top: loc.y }}
                title={loc.name}
              >
                <span className="marker-icon">{loc.icon}</span>
                <span className="marker-label">{loc.name}</span>
              </div>
            ))}

            {/* Player Marker */}
            {player?.position && (
              <div 
                className="player-marker"
                style={{ 
                  left: player.position.x || 500, 
                  top: player.position.y || 400 
                }}
              >
                <span className="player-icon">👤</span>
              </div>
            )}
          </div>
        </div>

        {/* Legend */}
        <div className="map-legend">
          <span><span className="legend-icon">🌍</span> Planet</span>
          <span><span className="legend-icon">🏙️</span> City</span>
          <span><span className="legend-icon">🏢</span> Shop</span>
          <span><span className="legend-icon">🏠</span> Trainer</span>
          <span><span className="legend-icon">🏟️</span> Event</span>
        </div>
      </div>

      <style>{`
        .map-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.9);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .map-container {
          width: 90vw;
          height: 80vh;
          background: #0a0f14;
          border-radius: 16px;
          border: 2px solid #00aeff;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .map-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          background: rgba(0, 174, 255, 0.1);
          border-bottom: 1px solid rgba(0, 174, 255, 0.3);
        }

        .map-header h2 {
          margin: 0;
          color: #00aeff;
          font-size: 1.5rem;
        }

        .map-controls {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .map-controls button {
          padding: 8px 16px;
          background: rgba(0, 0, 0, 0.5);
          border: 1px solid #00aeff;
          border-radius: 6px;
          color: #fff;
          cursor: pointer;
        }

        .map-controls button:hover {
          background: #00aeff;
          color: #000;
        }

        .map-viewport {
          flex: 1;
          overflow: hidden;
          position: relative;
        }

        .map-content {
          position: absolute;
          width: 1200px;
          height: 1000px;
          transform-origin: center;
        }

        .map-grid {
          position: absolute;
          inset: 0;
        }

        .map-world {
          position: absolute;
          inset: 0;
        }

        .continent {
          position: absolute;
          width: 200px;
          height: 150px;
          background: linear-gradient(135deg, #1a4a1a, #0d2a0d);
          border-radius: 40% 60% 70% 30%;
          border: 2px solid #2a5a2a;
        }

        .ocean {
          position: absolute;
          width: 100%;
          height: 100%;
          background: linear-gradient(180deg, #001a33, #003366);
        }

        .map-marker {
          position: absolute;
          transform: translate(-50%, -50%);
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;
          transition: transform 0.2s;
        }

        .map-marker:hover {
          transform: translate(-50%, -50%) scale(1.2);
        }

        .marker-icon {
          font-size: 1.5rem;
        }

        .marker-label {
          font-size: 0.7rem;
          background: rgba(0, 0, 0, 0.7);
          padding: 2px 6px;
          border-radius: 4px;
          white-space: nowrap;
        }

        .player-marker {
          position: absolute;
          transform: translate(-50%, -50%);
          font-size: 1.5rem;
          animation: playerPulse 2s infinite;
        }

        @keyframes playerPulse {
          0%, 100% { transform: translate(-50%, -50%) scale(1); }
          50% { transform: translate(-50%, -50%) scale(1.2); }
        }

        .map-legend {
          display: flex;
          gap: 16px;
          padding: 12px 24px;
          background: rgba(0, 0, 0, 0.5);
          border-top: 1px solid rgba(0, 174, 255, 0.3);
          font-size: 0.85rem;
        }

        .legend-icon {
          margin-right: 4px;
        }
      `}</style>
    </div>
  )
}

export default WorldMap
