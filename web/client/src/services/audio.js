/**
 * Audio Manager - Web Audio API for DBForged
 * Handles SFX, music, and audio effects
 */

class AudioManager {
  constructor() {
    this.context = null
    this.masterVolume = 1.0
    this.sfxVolume = 0.8
    this.musicVolume = 0.5
    this.musicGain = null
    this.sfxGain = null
    this.currentMusic = null
    this.sounds = {}
    this.initialized = false
  }

  /**
   * Initialize audio context (must be called after user interaction)
   */
  init() {
    if (this.initialized) return
    
    try {
      this.context = new (window.AudioContext || window.webkitAudioContext)()
      
      // Create gain nodes
      this.musicGain = this.context.createGain()
      this.sfxGain = this.context.createGain()
      
      this.musicGain.connect(this.context.destination)
      this.sfxGain.connect(this.context.destination)
      
      this.musicGain.gain.value = this.musicVolume
      this.sfxGain.gain.value = this.sfxVolume
      
      this.initialized = true
      console.log('[Audio] Initialized')
    } catch (e) {
      console.warn('[Audio] Failed to initialize:', e)
    }
  }

  /**
   * Resume audio context (needed after page focus)
   */
  resume() {
    if (this.context && this.context.state === 'suspended') {
      this.context.resume()
    }
  }

  /**
   * Set master volume (0-1)
   */
  setMasterVolume(vol) {
    this.masterVolume = Math.max(0, Math.min(1, vol))
  }

  /**
   * Set SFX volume (0-1)
   */
  setSfxVolume(vol) {
    this.sfxVolume = Math.max(0, Math.min(1, vol))
    if (this.sfxGain) {
      this.sfxGain.gain.value = this.sfxVolume * this.masterVolume
    }
  }

  /**
   * Set music volume (0-1)
   */
  setMusicVolume(vol) {
    this.musicVolume = Math.max(0, Math.min(1, vol))
    if (this.musicGain) {
      this.musicGain.gain.value = this.musicVolume * this.masterVolume
    }
  }

  /**
   * Play a sound effect
   * @param {string} name - Sound name
   * @param {object} options - Playback options
   */
  playSfx(name, options = {}) {
    if (!this.initialized) return
    
    const {
      volume = 1.0,
      pitch = 1.0,
      loop = false,
      delay = 0
    } = options

    // Try to use cached sound or generate procedural
    const sound = this.sounds[name]
    if (sound) {
      this.playBuffer(sound, {
        volume,
        pitch,
        loop,
        delay,
        gain: this.sfxGain
      })
    } else {
      // Generate procedural sound based on name
      this.playProcedural(name, { volume, pitch, gain: this.sfxGain })
    }
  }

  /**
   * Play an audio buffer
   */
  playBuffer(buffer, options) {
    const { volume, pitch, loop, delay, gain } = options
    
    const source = this.context.createBufferSource()
    source.buffer = buffer
    source.loop = loop
    source.playbackRate.value = pitch
    
    const gainNode = this.context.createGain()
    gainNode.gain.value = volume * this.masterVolume
    
    source.connect(gainNode)
    gainNode.connect(gain)
    
    if (delay > 0) {
      source.start(this.context.currentTime + delay)
    } else {
      source.start()
    }
    
    return source
  }

  /**
   * Play procedural sound effects
   */
  playProcedural(name, options) {
    const { volume, pitch, gain } = options
    const now = this.context.currentTime
    
    const osc = this.context.createOscillator()
    const gainNode = this.context.createGain()
    
    osc.connect(gainNode)
    gainNode.connect(gain)
    
    // Sound presets
    const presets = {
      attack: () => {
        osc.type = 'sawtooth'
        osc.frequency.setValueAtTime(150, now)
        osc.frequency.exponentialRampToValueAtTime(50, now + 0.1)
        gainNode.gain.setValueAtTime(volume * 0.3, now)
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.1)
        osc.start(now)
        osc.stop(now + 0.1)
      },
      hit: () => {
        osc.type = 'square'
        osc.frequency.setValueAtTime(200, now)
        osc.frequency.exponentialRampToValueAtTime(50, now + 0.15)
        gainNode.gain.setValueAtTime(volume * 0.4, now)
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.15)
        osc.start(now)
        osc.stop(now + 0.15)
      },
      heal: () => {
        osc.type = 'sine'
        osc.frequency.setValueAtTime(400, now)
        osc.frequency.linearRampToValueAtTime(800, now + 0.3)
        gainNode.gain.setValueAtTime(volume * 0.2, now)
        gainNode.gain.linearRampToValueAtTime(0, now + 0.3)
        osc.start(now)
        osc.stop(now + 0.3)
      },
      charge: () => {
        osc.type = 'sine'
        osc.frequency.setValueAtTime(200, now)
        osc.frequency.linearRampToValueAtTime(600, now + 0.5)
        gainNode.gain.setValueAtTime(volume * 0.2, now)
        gainNode.gain.linearRampToValueAtTime(volume * 0.3, now + 0.5)
        osc.start(now)
        osc.stop(now + 0.5)
      },
      transform: () => {
        osc.type = 'sawtooth'
        osc.frequency.setValueAtTime(100, now)
        osc.frequency.exponentialRampToValueAtTime(800, now + 1)
        gainNode.gain.setValueAtTime(volume * 0.4, now)
        gainNode.gain.linearRampToValueAtTime(volume * 0.5, now + 0.8)
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 1.5)
        osc.start(now)
        osc.stop(now + 1.5)
      },
      ui_click: () => {
        osc.type = 'sine'
        osc.frequency.setValueAtTime(800, now)
        gainNode.gain.setValueAtTime(volume * 0.2, now)
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.05)
        osc.start(now)
        osc.stop(now + 0.05)
      },
      notification: () => {
        osc.type = 'sine'
        osc.frequency.setValueAtTime(600, now)
        osc.frequency.setValueAtTime(800, now + 0.1)
        gainNode.gain.setValueAtTime(volume * 0.2, now)
        gainNode.gain.setValueAtTime(volume * 0.2, now + 0.1)
        gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.2)
        osc.start(now)
        osc.stop(now + 0.2)
      }
    }
    
    const preset = presets[name] || presets.ui_click
    preset()
  }

  /**
   * Play background music
   */
  playMusic(name, options = {}) {
    if (!this.initialized) return
    
    const { volume = 1.0, loop = true } = options
    
    // Stop current music
    if (this.currentMusic) {
      this.currentMusic.stop()
      this.currentMusic = null
    }
    
    // For now, generate ambient music procedurally
    this.playAmbientMusic(volume, loop)
  }

  /**
   * Play ambient music procedurally
   */
  playAmbientMusic(volume, loop) {
    const now = this.context.currentTime
    
    // Create ambient drone
    const osc1 = this.context.createOscillator()
    const osc2 = this.context.createOscillator()
    const gainNode = this.context.createGain()
    
    osc1.type = 'sine'
    osc1.frequency.value = 60
    
    osc2.type = 'sine'
    osc2.frequency.value = 90
    
    gainNode.gain.value = volume * 0.1 * this.masterVolume
    
    osc1.connect(gainNode)
    osc2.connect(gainNode)
    gainNode.connect(this.musicGain)
    
    osc1.start()
    osc2.start()
    
    // LFO for subtle movement
    const lfo = this.context.createOscillator()
    const lfoGain = this.context.createGain()
    lfo.frequency.value = 0.1
    lfoGain.gain.value = 10
    lfo.connect(lfoGain)
    lfoGain.connect(osc1.frequency)
    lfo.start()
    
    this.currentMusic = {
      stop: () => {
        osc1.stop()
        osc2.stop()
        lfo.stop()
      }
    }
  }

  /**
   * Stop music
   */
  stopMusic() {
    if (this.currentMusic) {
      this.currentMusic.stop()
      this.currentMusic = null
    }
  }

  /**
   * Play a screen effect
   */
  playScreenEffect(type) {
    const body = document.body
    
    const effects = {
      shake: () => {
        body.classList.add('screen-shake')
        setTimeout(() => body.classList.remove('screen-shake'), 200)
      },
      flash: () => {
        const flash = document.createElement('div')
        flash.className = 'screen-flash'
        document.body.appendChild(flash)
        setTimeout(() => flash.remove(), 100)
      },
      redFlash: () => {
        const flash = document.createElement('div')
        flash.className = 'screen-flash-red'
        document.body.appendChild(flash)
        setTimeout(() => flash.remove(), 150)
      },
      vignette: () => {
        body.classList.add('vignette-effect')
        setTimeout(() => body.classList.remove('vignette-effect'), 1000)
      }
    }
    
    if (effects[type]) {
      effects[type]()
    }
  }
}

// Singleton instance
export const audioManager = new AudioManager()
export default audioManager
