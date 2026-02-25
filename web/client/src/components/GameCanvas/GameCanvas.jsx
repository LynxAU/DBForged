import React, { useRef, useEffect, useCallback } from 'react'

/**
 * GameCanvas - Renders sprites and game world
 * Loads sprites from /static/ui/ directory
 */
export function GameCanvas({ entities, player }) {
  const canvasRef = useRef(null)
  const spritesRef = useRef({})
  const animationFrameRef = useRef(null)

  // Load sprite from URL
  const loadSprite = useCallback(async (spriteId) => {
    if (spritesRef.current[spriteId]) {
      return spritesRef.current[spriteId]
    }
    
    try {
      const response = await fetch(`/static/ui/${spriteId}.png`)
      if (!response.ok) {
        console.warn(`Sprite not found: ${spriteId}`)
        return null
      }
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const img = new Image()
      
      await new Promise((resolve, reject) => {
        img.onload = resolve
        img.onerror = reject
        img.src = url
      })
      
      spritesRef.current[spriteId] = img
      return img
    } catch (err) {
      console.error(`Failed to load sprite ${spriteId}:`, err)
      return null
    }
  }, [])

  // Draw a single entity
  const drawEntity = useCallback((ctx, entity) => {
    if (!entity.position || !entity.sprite_id) return
    
    const { x, y } = entity.position
    const spriteId = entity.sprite_id
    
    const sprite = spritesRef.current[spriteId]
    if (sprite) {
      ctx.drawImage(sprite, x - 16, y - 16, 32, 32)
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

    const render = () => {
      // Clear canvas
      ctx.fillStyle = '#04080c'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      // Draw grid pattern (optional floor)
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
      
      // Draw entities
      Object.values(entities).forEach(entity => {
        drawEntity(ctx, entity)
      })
      
      animationFrameRef.current = requestAnimationFrame(render)
    }
    
    render()

    return () => {
      window.removeEventListener('resize', resize)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [entities, drawEntity])

  return (
    <div className="canvas-stage">
      <canvas ref={canvasRef} className="game-canvas" />
    </div>
  )
}

export default GameCanvas
