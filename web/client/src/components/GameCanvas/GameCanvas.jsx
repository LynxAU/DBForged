import React, { useRef, useEffect, useCallback, useState } from 'react'

/**
 * GameCanvas - Renders sprites and game world
 * Loads sprites from /static/ui/ directory
 * Supports animated sprite sheets with multiple frames
 * Supports tile-based backgrounds for locations
 * Supports technique/effect animations (Kamehameha, etc.)
 */
export function GameCanvas({ entities, player, effects = [], onMove }) {
  const canvasRef = useRef(null)
  const spritesRef = useRef({})
  const tilesRef = useRef({})
  const animationFrameRef = useRef(null)
  const frameTimeRef = useRef(0)
  const playerPosRef = useRef({ x: 200, y: 200 })
  const keysPressed = useRef({})
  const [currentFrame, setCurrentFrame] = useState(0)
  const [localEffects, setLocalEffects] = useState([])
  
  // Tile definitions - maps room names to tile sprites
  const TILE_MAP = {
    // Kame Island
    'Kame Island':                       'Kame Island/sand',
    'Beach':                             'Kame Island/sand',
    'Kame House - Exterior':             'Kame Island/sand',
    'Kame Island: Beach Shore':          'Kame Island/sand',
    'Kame Island: Small Dock':           'Kame Island/sand',
    'Kame Island: Waterfall':            'Kame Island/water',
    'Kame Island: Hidden Cave':          'Kame Island/water',
    'Kame House - Main Room':            'Kame Island/grass',
    'Kame House - Garden':               'Kame Island/grass',
    'Kame Island: Training Grounds':     'Kame Island/grass',
    'Kame Island: Forest Path':          'Kame Island/grass',
    'Kame Island: Meditation Clearing':  'Kame Island/grass',
    'Kame Island: Vacation Cottage':     'Kame Island/grass',
    'Kame Island: Cottage Grounds':      'Kame Island/grass',
    // Capsule Corp
    'Capsule Corp - Main Entrance':      'Capsule Corp/concrete',
    'Capsule Corp - Rooftop':            'Capsule Corp/concrete',
    'Capsule Corp - Research Lab':       'Capsule Corp/lab',
    'Capsule Corp - Training Hall':      'Capsule Corp/metal',
    // King Kai
    "King Kai's Planet":                 'King Kai/alien_grass',
    "King Kai's Training Grounds":       'King Kai/alien_grass',
    // Mount Paozu
    'Mount Paozu - Forest Path':         'Mount Paozu/forest',
    'Mount Paozu - Spirit Bomb Cliff':   'Mount Paozu/forest',
    'Mount Paozu - Base Camp':           'Mount Paozu/dirt',
    "Goku's House - Exterior":           'Mount Paozu/dirt',
    "Goku's House - Interior":           'Mount Paozu/dirt',
    // Red Ribbon Army
    'Red Ribbon Army - Main Gate':             'Red Ribbon Army/military',
    'Red Ribbon Army - Main Lobby':            'Red Ribbon Army/military',
    'Red Ribbon Army - Armory':                'Red Ribbon Army/military',
    'Red Ribbon Army - Secret Laboratory':     'Red Ribbon Army/military',
    "Red Ribbon Army - Commander's Office":    'Red Ribbon Army/military',
    // Fallback
    'default': 'Kame Island/sand',
  }
  
  // Animation config - frames per sprite sheet
  const SPRITE_FRAMES = {
    // Legacy / built-in
    'saiyan_warrior_walk_cycle': 4,
    'saiyan_warrior_idle': 1,
    'Kamehameha': 20,

    // Character walk/idle cycles (128×32 = 4 frames @ 32px)
    'characters/goku_walk':    4, 'characters/goku_idle':    4,
    'characters/vegeta_walk':  4, 'characters/vegeta_idle':  4,
    'characters/piccolo_walk': 4, 'characters/piccolo_idle': 4,
    'characters/trunks_walk':  4, 'characters/trunks_idle':  4,

    // Ki Blasts (384×48 = 8 frames @ 48px)
    'attacks/ki_blast_blue': 8, 'attacks/ki_blast_gold': 8,
    'attacks/ki_blast_purple': 8, 'attacks/ki_blast_green': 8,

    // Beams (1536×64 = 12 frames @ 128px)
    'attacks/kamehameha_beam': 12, 'attacks/final_flash': 12,
    'attacks/galick_gun': 12,      'attacks/masenko': 12,
    'attacks/burning_attack': 12,
    'attacks/vfx_kame_wave': 12,   'attacks/vfx_masenko': 12,
    'attacks/vfx_fusion_beam_gold': 12, 'attacks/vfx_galick_fusion': 12,

    // Special Techniques
    'attacks/special_beam_cannon': 10,
    'attacks/spirit_bomb':         10,
    'attacks/destructo_disc':       8,
    'attacks/solar_flare':          6,
    'attacks/impact':               8,

    // Technique VFX
    'attacks/vfx_guard_sphere':  8,
    'attacks/vfx_afterimage':    6,
    'attacks/vfx_vanish_strike': 6,
    'attacks/vfx_soul_buster':  10,
    'attacks/vfx_stardust':      8,

    // Base Auras (640×80 = 8 frames @ 80px)
    'attacks/aura_golden': 8, 'attacks/aura_blue': 8,
    'attacks/aura_green':  8, 'attacks/aura_purple': 8, 'attacks/aura_red': 8,

    // Transformation Auras — Saiyan Line
    'attacks/aura_kaioken_red': 8, 'attacks/aura_ssj_gold': 8,
    'attacks/aura_ssj2': 8,        'attacks/aura_ssj3': 8,
    'attacks/aura_ssg_red': 8,     'attacks/aura_ssb_blue': 8,
    'attacks/aura_beast_white': 8,

    // Transformation Auras — LSSJ Stages
    'attacks/aura_lssj_green': 8, 'attacks/aura_lssj_surge': 8,
    'attacks/aura_lssj_cataclysm': 8,

    // Transformation Auras — All Other Races
    'attacks/aura_namekian_jade': 8,    'attacks/aura_potential_white': 8,
    'attacks/aura_max_power': 8,
    'attacks/aura_majin_pink': 8,       'attacks/aura_pure_majin': 8,
    'attacks/aura_android_blue': 8,     'attacks/aura_android_infinite': 8,
    'attacks/aura_biodroid_stage2': 8,  'attacks/aura_biodroid_perfect': 8,
    'attacks/aura_biodroid_super_perfect': 8,
    'attacks/aura_frost_true': 8,       'attacks/aura_frost_final': 8,
    'attacks/aura_gold_frost': 8,
    'attacks/aura_grey_focus': 8,       'attacks/aura_grey_limit_break': 8,
    'attacks/aura_kai_divine': 8,       'attacks/aura_kai_empowered': 8,
    'attacks/aura_tuffle_teal': 8,      'attacks/aura_tuffle_overdrive': 8,

    // Transformation Auras — Fusion
    'attacks/aura_potara_gold': 8, 'attacks/aura_metamoran': 8,
    'attacks/aura_fusion_ssj': 8,

    // Charging Aura Overlays (384×48 = 8 frames @ 48px — overlay on character)
    'attacks/charge_white': 8,      'attacks/charge_blue': 8,
    'attacks/charge_kaioken': 8,    'attacks/charge_ssj': 8,
    'attacks/charge_ssj2': 8,       'attacks/charge_ssj3': 8,
    'attacks/charge_ssg': 8,        'attacks/charge_ssb': 8,
    'attacks/charge_beast': 8,
    'attacks/charge_lssj': 8,       'attacks/charge_lssj_cataclysm': 8,
    'attacks/charge_namekian': 8,   'attacks/charge_potential': 8,
    'attacks/charge_majin': 8,      'attacks/charge_pure_majin': 8,
    'attacks/charge_android': 8,    'attacks/charge_biodroid': 8,
    'attacks/charge_frost': 8,      'attacks/charge_frost_golden': 8,
    'attacks/charge_grey': 8,       'attacks/charge_kai': 8,
    'attacks/charge_truffle': 8,
    'attacks/charge_potara': 8,     'attacks/charge_metamoran': 8,

    'default': 1,
  }

  // Keyboard handlers (need to be after keysPressed ref)
  const handleKeyDown = (e) => { 
    keysPressed.current[e.key] = true
    // Z key to trigger Kamehameha
    if (e.key === 'z' && !e.repeat) {
      console.log('KAMEHAMEHA pressed! Adding effect...')
      // Add Kamehameha effect at player position
      const newEffect = {
        sprite_id: 'Kamehameha',
        position: { x: playerPosRef.current.x + 50, y: playerPosRef.current.y },
        scale: 1.5
      }
      console.log('Effect:', newEffect)
      setLocalEffects(prev => [...prev, newEffect])
      // Remove effect after animation completes (~3 seconds)
      setTimeout(() => {
        setLocalEffects(prev => prev.filter(e => e !== newEffect))
      }, 3000)
    }
  }
  const handleKeyUp = (e) => { keysPressed.current[e.key] = false }
  
  // Technique animation frame mappings
  const TECHNIQUE_FRAMES = {
    'Kamehameha': {
      'charge': [0, 1, 2, 3],      // Frames 0-3: charging
      'release': [4],                // Frame 4: energy release
      'beam': [5, 6, 7, 8, 9, 10], // Frames 5-10: beam firing
      'impact': [11, 12, 13, 14, 15], // Frames 11-15: impact
      'dissipate': [16, 17, 18]     // Frames 18-20: fading away
    }
  }
  
  // Get frame count for a sprite
  const getFrameCount = (spriteId) => {
    return SPRITE_FRAMES[spriteId] || SPRITE_FRAMES['default'] || 1
  }
  
  // Get sprite sheet dimensions (assumes uniform frames in a row)
  const getSpriteFrameSize = (spriteId, img) => {
    const frames = getFrameCount(spriteId)
    if (frames === 1) return { width: img.width, height: img.height }
    // Assume frames are arranged horizontally
    return { width: img.width / frames, height: img.height }
  }

  // Load tile sprite
  const loadTile = useCallback(async (tileId) => {
    if (tilesRef.current[tileId]) {
      return tilesRef.current[tileId]
    }
    
    // Try multiple paths - encode the tileId for URLs
    const encodedTileId = encodeURIComponent(tileId)
    let path = `/static/ui/sprites/${encodedTileId}.png`
    
    try {
      let response = await fetch(path)
      if (!response.ok) {
        // Try without "Kame Island/" prefix
        const basename = tileId.split('/').pop()
        path = `/static/ui/sprites/Kame%20Island/${encodeURIComponent(basename)}.png`
        response = await fetch(path)
        if (!response.ok) {
          // Try tiles folder
          path = `/static/ui/tiles/${encodeURIComponent(tileId)}.png`
          response = await fetch(path)
          if (!response.ok) {
            console.warn(`Tile not found: ${tileId}`)
            return null
          }
        }
      }
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const img = new Image()
      await new Promise((resolve, reject) => {
        img.onload = resolve
        img.onerror = (e) => {
          console.error(`Image load error for ${tileId}:`, e)
          reject(e)
        }
        img.src = url
      })
      tilesRef.current[tileId] = img
      return img
    } catch (err) {
      console.error(`Failed to load tile ${tileId}:`, err)
      return null
    }
  }, [])

  // Load sprite from URL
  const loadSprite = useCallback(async (spriteId) => {
    if (spritesRef.current[spriteId]) {
      return spritesRef.current[spriteId]
    }
    
    // Check if it's an animation or technique
    const isAnimation = spriteId.includes('_walk') || spriteId.includes('_run') || spriteId.includes('_idle')
    const hasSubdir = spriteId.startsWith('attacks/') || spriteId.startsWith('characters/')
    const isTechnique = spriteId.includes('kamehameha') || spriteId.includes('_beam') || spriteId.includes('_attack') || spriteId.includes('_final_flash') || spriteId.includes('_galick') || spriteId.includes('_genki')

    // Try multiple paths - encode for URLs
    let path
    const encodedId = spriteId.split('/').map(encodeURIComponent).join('/')
    if (hasSubdir) {
      // Direct path in animations directory: attacks/foo.png or characters/foo.png
      path = `/static/ui/animations/${encodedId}.png`
    } else if (isTechnique || spriteId.startsWith('Kamehameha')) {
      // Check if it's a named technique like "Kamehameha" or "Kamehameha/charge"
      if (spriteId.includes('/')) {
        path = `/static/ui/animations/${encodedId}.png`
      } else {
        // Try individual frames or spritesheet in technique folder
        path = `/static/ui/animations/${spriteId}/${spriteId}_spritesheet.png`
      }
    } else if (isAnimation) {
      path = `/static/ui/animations/${encodedId}.png`
    } else {
      path = `/static/ui/sprites/${encodedId}.png`
    }
    
    try {
      let response = await fetch(path)
      if (!response.ok) {
        // Try Kame Island subfolder for NPCs
        path = `/static/ui/sprites/Kame%20Island/${encodeURIComponent(spriteId.split('/').pop())}.png`
        response = await fetch(path)
        if (!response.ok) {
          // Try techniques folder (individual frames)
          if (spriteId.startsWith('Kamehameha')) {
            path = `/static/ui/animations/Kamehameha/kamehameha_spritesheet.png`
            response = await fetch(path)
            if (!response.ok) {
              console.warn(`Sprite not found: ${spriteId}`)
              return null
            }
          } else {
            console.warn(`Sprite not found: ${spriteId}`)
            return null
          }
        }
      }
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const img = new Image()
      
      await new Promise((resolve, reject) => {
        img.onload = resolve
        img.onerror = (e) => {
          console.error(`Image load error for sprite ${spriteId}:`, e)
          reject(e)
        }
        img.src = url
      })
      
      spritesRef.current[spriteId] = img
      return img
    } catch (err) {
      console.error(`Failed to load sprite ${spriteId}:`, err)
      return null
    }
  }, [])

  // Preload default player sprite
  useEffect(() => {
    loadSprite('saiyan_warrior_walk_cycle')
  }, [loadSprite])

  // Draw a single entity
  const drawEntity = useCallback((ctx, entity, frameIndex = 0) => {
    if (!entity?.sprite_id && !entity?.position) return
    
    // Default position if not provided
    const x = entity.position?.x ?? 200
    const y = entity.position?.y ?? 200
    const spriteId = entity.sprite_id || 'saiyan_warrior_walk_cycle'
    
    const sprite = spritesRef.current[spriteId]
    if (sprite) {
      const frameCount = getFrameCount(spriteId)
      
      if (frameCount > 1) {
        // Animated sprite sheet - draw specific frame
        const frameSize = getSpriteFrameSize(spriteId, sprite)
        const srcX = frameIndex * frameSize.width
        ctx.drawImage(
          sprite,
          srcX, 0, frameSize.width, frameSize.height,  // source
          x - 16, y - 16, 32, 32                        // destination
        )
      } else {
        // Static sprite
        ctx.drawImage(sprite, x - 16, y - 16, 32, 32)
      }
    } else {
      // Draw placeholder if sprite not loaded
      ctx.fillStyle = '#00aeff'
      ctx.fillRect(x - 8, y - 8, 16, 16)
      // Try to load sprite in background
      loadSprite(spriteId)
    }
    
    // Draw name above sprite
    ctx.fillStyle = '#ffffff'
    ctx.font = '10px Inter'
    ctx.textAlign = 'center'
    ctx.fillText(entity.name || 'Unknown', x, y - 20)
    
    // Draw player indicator (golden border for player character)
    if (entity.is_player) {
      ctx.strokeStyle = '#ffd700'
      ctx.lineWidth = 2
      ctx.strokeRect(x - 16, y - 16, 32, 32)
    }
    
    // Draw HP bar if entity is damaged
    if (entity.hp !== undefined && entity.hp_max !== undefined) {
      const hpPercent = entity.hp / entity.hp_max
      const barWidth = 32
      const barHeight = 4
      
      ctx.fillStyle = '#330000'
      ctx.fillRect(x - barWidth/2, y - 14, barWidth, barHeight)
      
      ctx.fillStyle = hpPercent > 0.5 ? '#32ff64' : hpPercent > 0.25 ? '#ffd74a' : '#ff3366'
      ctx.fillRect(x - barWidth/2, y - 14, barWidth * hpPercent, barHeight)
    }
  }, [loadSprite])

  // Draw technique/effect animation (Kamehameha, Final Flash, etc.)
  const drawEffect = useCallback(async (ctx, effect, frameIndex) => {
    if (!effect.sprite_id || !effect.position) return
    
    console.log('Drawing effect:', effect.sprite_id, 'at', effect.position)
    const sprite = await loadSprite(effect.sprite_id)
    console.log('Effect sprite loaded:', sprite)
    if (!sprite) {
      // Fallback: draw glowing energy ball - BIG AND BRIGHT!
      const x = effect.position.x || 200
      const y = effect.position.y || 200
      const radius = 60 + (frameIndex * 10)
      
      console.log('Drawing fallback glow at:', x, y, 'radius:', radius)
      
      // Multiple layers of glow for intensity
      // Outer glow
      const outerGlow = ctx.createRadialGradient(x, y, 0, x, y, radius * 2)
      outerGlow.addColorStop(0, 'rgba(100, 150, 255, 0.3)')
      outerGlow.addColorStop(0.5, 'rgba(50, 100, 255, 0.1)')
      outerGlow.addColorStop(1, 'rgba(0, 0, 0, 0)')
      ctx.fillStyle = outerGlow
      ctx.beginPath()
      ctx.arc(x, y, radius * 2, 0, Math.PI * 2)
      ctx.fill()
      
      // Inner glow
      const innerGlow = ctx.createRadialGradient(x, y, 0, x, y, radius)
      innerGlow.addColorStop(0, 'rgba(255, 255, 255, 1)')
      innerGlow.addColorStop(0.2, 'rgba(150, 200, 255, 0.9)')
      innerGlow.addColorStop(0.5, 'rgba(100, 150, 255, 0.7)')
      innerGlow.addColorStop(1, 'rgba(50, 100, 255, 0)')
      ctx.fillStyle = innerGlow
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()
      
      // Bright core
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
      ctx.beginPath()
      ctx.arc(x, y, 15, 0, Math.PI * 2)
      ctx.fill()
      
      return
    }
    
    const frameCount = getFrameCount(effect.sprite_id)
    const frameSize = getSpriteFrameSize(effect.sprite_id, sprite)
    const srcX = (frameIndex % frameCount) * frameSize.width
    
    const x = effect.position.x || 200
    const y = effect.position.y || 200
    const scale = effect.scale || 1
    
    ctx.drawImage(
      sprite,
      srcX, 0, frameSize.width, frameSize.height,
      x - (frameSize.width * scale) / 2,
      y - (frameSize.height * scale) / 2,
      frameSize.width * scale,
      frameSize.height * scale
    )
  }, [loadSprite])

  // Main render loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resize = () => {
      canvas.width = canvas.parentElement.clientWidth
      canvas.height = canvas.parentElement.clientHeight
    }
    resize()
    window.addEventListener('resize', resize)

    // Keyboard handling
    const handleKeyDown = (e) => {
      keysPressed.current[e.key] = true
    }
    const handleKeyUp = (e) => {
      keysPressed.current[e.key] = false
    }
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    const render = async (timestamp) => {
      // Update animation frame every 150ms
      const animSpeed = 150
      const newFrameIndex = Math.floor((timestamp / animSpeed) % 4)
      
      // Handle movement from keyboard
      const speed = 1
      const keys = keysPressed.current
      let moved = false
      if (keys['ArrowUp'] || keys['w'] || keys['W']) { playerPosRef.current.y -= speed; moved = true }
      if (keys['ArrowDown'] || keys['s'] || keys['S']) { playerPosRef.current.y += speed; moved = true }
      if (keys['ArrowLeft'] || keys['a'] || keys['A']) { playerPosRef.current.x -= speed; moved = true }
      if (keys['ArrowRight'] || keys['d'] || keys['D']) { playerPosRef.current.x += speed; moved = true }
      
      // Clamp to canvas bounds
      const canvas = canvasRef.current
      if (canvas) {
        playerPosRef.current.x = Math.max(16, Math.min(canvas.width - 16, playerPosRef.current.x))
        playerPosRef.current.y = Math.max(16, Math.min(canvas.height - 16, playerPosRef.current.y))
      }
      
      // Clear canvas
      ctx.fillStyle = '#04080c'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      // Draw tile background based on room name
      const roomName = player?.location || 'Kame Island'
      const tileId = TILE_MAP[roomName] || TILE_MAP['default']
      const tile = await loadTile(tileId)
      
      if (tile) {
        // Tile the background
        const tileSize = 64
        for (let x = 0; x < canvas.width; x += tileSize) {
          for (let y = 0; y < canvas.height; y += tileSize) {
            ctx.drawImage(tile, x, y, tileSize, tileSize)
          }
        }
      } else {
        // Fallback to grid pattern
        ctx.strokeStyle = 'rgba(0, 174, 255, 0.1)'
        ctx.lineWidth = 1
        for (let x = 0; x < canvas.width; x += 64) {
          ctx.beginPath()
          ctx.moveTo(x, 0)
          ctx.lineTo(x, canvas.height)
          ctx.stroke()
        }
        for (let y = 0; y < canvas.height; y += 64) {
          ctx.beginPath()
          ctx.moveTo(0, y)
          ctx.lineTo(canvas.width, y)
          ctx.stroke()
        }
      }
      
      // Draw entities with animation
      Object.values(entities).forEach(entity => {
        drawEntity(ctx, entity, newFrameIndex)
      })
      
      // Draw player character
      // Use local position for demo movement, or server position if available
      const pos = player?.position || playerPosRef.current
      const isMoving = keysPressed.current['ArrowUp'] || keysPressed.current['ArrowDown'] || 
                       keysPressed.current['ArrowLeft'] || keysPressed.current['ArrowRight'] ||
                       keysPressed.current['w'] || keysPressed.current['W'] ||
                       keysPressed.current['s'] || keysPressed.current['S'] ||
                       keysPressed.current['a'] || keysPressed.current['A'] ||
                       keysPressed.current['d'] || keysPressed.current['D']
      const playerSpriteId = player?.sprite_id || (isMoving ? 'saiyan_warrior_walk_cycle' : 'saiyan_warrior_walk_cycle')
      
      const playerToDraw = { 
        ...player, 
        name: 'You', 
        sprite_id: playerSpriteId, 
        position: pos, 
        is_player: true 
      }
      
      console.log('Rendering player:', playerToDraw)
      drawEntity(ctx, playerToDraw, newFrameIndex)
      
      // Draw technique/effect animations
      const allEffects = [...effects, ...localEffects]
      allEffects.forEach(effect => {
        drawEffect(ctx, effect, newFrameIndex)
      })
      
      animationFrameRef.current = requestAnimationFrame(render)
    }
    
    render()

    return () => {
      window.removeEventListener('resize', resize)
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [entities, drawEntity, drawEffect, effects, player, localEffects])

  return (
    <div className="canvas-stage">
      <canvas ref={canvasRef} className="game-canvas" />
    </div>
  )
}

export default GameCanvas
