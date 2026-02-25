import React, { useState, useRef, useEffect } from 'react'
import { GokuArt, VegetaArt } from './CharacterArt'

// ── Race data ─────────────────────────────────────────────────────────────────
const RACES = [
  { id: 'saiyan',     name: 'Saiyan',      tagline: 'Born for battle. Growing stronger through every conflict.',          traits: ['Battle Instinct', 'Zenkai Edge', 'Tail Counter'],      color: '#ffd700', glow: 'rgba(255,215,0,0.32)'   },
  { id: 'half_breed', name: 'Half-Breed',  tagline: 'Latent power surges beyond expectation when pushed to the limit.',  traits: ['Latent Spike', 'Focus Rebound', 'Guardian Drive'],     color: '#ff9944', glow: 'rgba(255,107,53,0.32)'  },
  { id: 'human',      name: 'Human',       tagline: 'Relentless potential. Mastery and grit exceed all natural limits.', traits: ['Adaptable Training', 'Second Wind', 'Technique Burst'],color: '#64b5f6', glow: 'rgba(0,174,255,0.32)'   },
  { id: 'namekian',   name: 'Namekian',    tagline: 'Ancient warriors of regeneration and deep spiritual ki.',           traits: ['Regenerative Tissue', 'Stretching Reach', 'Healing Pulse'], color: '#66bb6a', glow: 'rgba(50,255,100,0.32)'  },
  { id: 'majin',      name: 'Majin',       tagline: 'Unpredictable and resilient — a body that defies all logic.',       traits: ['Malleable Body', 'Candy Metabolism', 'Body Split Feint'],  color: '#f48fb1', glow: 'rgba(255,64,129,0.32)'  },
  { id: 'android',    name: 'Android',     tagline: 'Cold efficiency and superior energy management define their edge.',  traits: ['Reactor Efficiency', 'Targeting Suite', 'Barrier Projector'], color: '#4dd0e1', glow: 'rgba(0,188,212,0.32)'   },
  { id: 'biodroid',   name: 'Biodroid',    tagline: 'Adaptive predators that evolve to overcome any opponent.',          traits: ['Adaptive Genome', 'Predator Sense', 'Genetic Siphon'],  color: '#ce93d8', glow: 'rgba(156,39,176,0.32)'  },
  { id: 'frost_demon',name: 'Frost Demon', tagline: 'Rulers of galaxies through precision, cruelty, and iron control.',  traits: ['Form Discipline', 'Cruel Precision', 'Death Glare'],    color: '#9fa8da', glow: 'rgba(92,107,192,0.32)'   },
  { id: 'grey',       name: 'Grey',        tagline: 'Immovable tacticians who dominate through sheer pressure of will.', traits: ['Relentless Focus', 'Pressure Steps', 'Dominance Aura'], color: '#b0bec5', glow: 'rgba(120,144,156,0.32)' },
  { id: 'kai',        name: 'Kai',         tagline: 'Divine guardians attuned to sacred ki and higher-plane mastery.',  traits: ['Divine Attunement', 'Sacred Sense', 'Blessing Seal'],   color: '#ffcc80', glow: 'rgba(255,152,0,0.32)'   },
  { id: 'truffle',    name: 'Truffle',     tagline: 'Brilliant engineers who weaponize intellect and integrated tech.',  traits: ['Tactical Analytics', 'Gadget Integration', 'Probe Swarm'],  color: '#80deea', glow: 'rgba(38,198,218,0.32)'  },
]

// ── Appearance options ─────────────────────────────────────────────────────────
const HAIR_STYLES = ['spiky','short','long','ponytail','bald','wild','braided','wavy','mohawk','dreadlocks']

const COLORS = {
  hair: [
    { id: 'black',  css: '#1c1c1c', label: 'Black'  },
    { id: 'blond',  css: '#F5D020', label: 'Blond'  },
    { id: 'brown',  css: '#7B3F00', label: 'Brown'  },
    { id: 'red',    css: '#CC2200', label: 'Red'    },
    { id: 'white',  css: '#EFEFEF', label: 'White'  },
    { id: 'blue',   css: '#3a6fce', label: 'Blue'   },
    { id: 'green',  css: '#2e7d32', label: 'Green'  },
    { id: 'silver', css: '#A8A9AD', label: 'Silver' },
    { id: 'gold',   css: '#FFD700', label: 'Gold'   },
    { id: 'purple', css: '#7B2D8B', label: 'Purple' },
    { id: 'pink',   css: '#FF69B4', label: 'Pink'   },
    { id: 'orange', css: '#FF6600', label: 'Orange' },
  ],
  eye: [
    { id: 'black',  css: '#1c1c1c', label: 'Black'  },
    { id: 'brown',  css: '#7B3F00', label: 'Brown'  },
    { id: 'blue',   css: '#3a6fce', label: 'Blue'   },
    { id: 'green',  css: '#2e7d32', label: 'Green'  },
    { id: 'red',    css: '#CC2200', label: 'Red'    },
    { id: 'gold',   css: '#FFD700', label: 'Gold'   },
    { id: 'silver', css: '#A8A9AD', label: 'Silver' },
    { id: 'purple', css: '#7B2D8B', label: 'Purple' },
    { id: 'white',  css: '#EFEFEF', label: 'White'  },
    { id: 'teal',   css: '#00897B', label: 'Teal'   },
    { id: 'pink',   css: '#FF69B4', label: 'Pink'   },
    { id: 'orange', css: '#FF6600', label: 'Orange' },
  ],
  aura: [
    { id: 'white',   css: '#EFEFEF', label: 'White'   },
    { id: 'gold',    css: '#FFD700', label: 'Gold'    },
    { id: 'blue',    css: '#3a6fce', label: 'Blue'    },
    { id: 'green',   css: '#2e7d32', label: 'Green'   },
    { id: 'red',     css: '#CC2200', label: 'Red'     },
    { id: 'orange',  css: '#FF6600', label: 'Orange'  },
    { id: 'purple',  css: '#7B2D8B', label: 'Purple'  },
    { id: 'teal',    css: '#00897B', label: 'Teal'    },
    { id: 'silver',  css: '#A8A9AD', label: 'Silver'  },
    { id: 'pink',    css: '#FF69B4', label: 'Pink'    },
    { id: 'black',   css: '#1c1c1c', label: 'Black'   },
  ],
}

// Race-appropriate appearance defaults applied when race is picked
const RACE_DEFAULTS = {
  saiyan:     { sex: 'other', hair_style: 'spiky',    hair_color: 'black',  eye_color: 'black',  aura_color: 'gold'   },
  half_breed: { sex: 'other', hair_style: 'spiky',    hair_color: 'black',  eye_color: 'black',  aura_color: 'gold'   },
  human:      { sex: 'other', hair_style: 'short',    hair_color: 'brown',  eye_color: 'brown',  aura_color: 'white'  },
  namekian:   { sex: 'other', hair_style: 'bald',     hair_color: 'black',  eye_color: 'black',  aura_color: 'green'  },
  majin:      { sex: 'other', hair_style: 'wild',     hair_color: 'white',  eye_color: 'red',    aura_color: 'pink'   },
  android:    { sex: 'other', hair_style: 'short',    hair_color: 'black',  eye_color: 'blue',   aura_color: 'teal'   },
  biodroid:   { sex: 'other', hair_style: 'wild',     hair_color: 'purple', eye_color: 'red',    aura_color: 'purple' },
  frost_demon:{ sex: 'other', hair_style: 'bald',     hair_color: 'black',  eye_color: 'red',    aura_color: 'purple' },
  grey:       { sex: 'other', hair_style: 'short',    hair_color: 'silver', eye_color: 'silver', aura_color: 'white'  },
  kai:        { sex: 'other', hair_style: 'long',     hair_color: 'blond',  eye_color: 'gold',   aura_color: 'gold'   },
  truffle:    { sex: 'other', hair_style: 'short',    hair_color: 'silver', eye_color: 'teal',   aura_color: 'teal'   },
}

const DEFAULT_APPEARANCE = { sex: 'other', hair_style: 'spiky', hair_color: 'black', eye_color: 'black', aura_color: 'white' }

// ── Component ─────────────────────────────────────────────────────────────────
export function CharacterCreator({ onCreateAccount, onBack, connectionState, error }) {
  const [step,       setStep]       = useState(0)                    // 0 race | 1 appearance | 2 identity
  const [raceId,     setRaceId]     = useState(null)
  const [appearance, setAppearance] = useState(DEFAULT_APPEARANCE)
  const [username,   setUsername]   = useState('')
  const [password,   setPassword]   = useState('')
  const [confirm,    setConfirm]    = useState('')
  const [submitted,  setSubmitted]  = useState(false)

  const usernameRef = useRef(null)
  useEffect(() => {
    if (step === 2) setTimeout(() => usernameRef.current?.focus(), 60)
  }, [step])

  const selectedRace = RACES.find(r => r.id === raceId)
  const accentColor  = selectedRace?.color || '#ffd700'
  const isConnected  = connectionState === 'connected'
  const pwMatch      = !confirm || password === confirm
  const canSubmit    = isConnected && username.trim() && password && password === confirm && !submitted

  const selectRace = (id) => {
    setRaceId(id)
    setAppearance(prev => ({ ...prev, ...(RACE_DEFAULTS[id] || {}) }))
  }
  const setAttr = (key, val) => setAppearance(prev => ({ ...prev, [key]: val }))

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!canSubmit) return
    setSubmitted(true)
    onCreateAccount(username, password, raceId, appearance)
  }

  // ── Shared background ──────────────────────────────────────────────────────
  const BG = (
    <>
      <div className="lb-bg" />
      <img src="/static/ui/dbf.png" className="lb-hero-bg" alt="" draggable={false} />
      <div className="lb-hero-overlay" />
      <div className="cc-creator-overlay" />
      <div className="lb-corona" />
      <div className="lb-orb lb-orb-1" /><div className="lb-orb lb-orb-2" />
      <div className="lb-orb lb-orb-3" /><div className="lb-orb lb-orb-4" />
      <GokuArt   className="lb-char lb-char-goku" />
      <VegetaArt className="lb-char lb-char-vegeta" />
      <div className="lb-ground" />
    </>
  )

  // ── Step 0 — Race picker ───────────────────────────────────────────────────
  if (step === 0) return (
    <div className="lb-screen">
      {BG}
      <div className="cc-wrap">
        <div className="cc-header">
          <img src="/static/ui/dbforgedfullcoloralpha.png" alt="Dragon Ball Forged" className="cc-logo" draggable={false} />
          <h2 className="cc-title">CHOOSE YOUR RACE</h2>
          <p className="cc-subtitle">Your lineage determines your power path.</p>
        </div>

        <div className="cc-race-grid">
          {RACES.map(r => (
            <button
              key={r.id}
              className={`cc-race-card${raceId === r.id ? ' selected' : ''}`}
              style={{ '--race-color': r.color, '--race-glow': r.glow }}
              onClick={() => selectRace(r.id)}
            >
              <div className="cc-race-name">{r.name}</div>
              <div className="cc-race-tagline">{r.tagline}</div>
              <div className="cc-trait-list">
                {r.traits.map(t => <span key={t} className="cc-trait">{t}</span>)}
              </div>
            </button>
          ))}
        </div>

        <div className="cc-nav">
          <button
            className="lb-menu-btn lb-menu-btn-primary cc-next-btn"
            disabled={!raceId}
            onClick={() => setStep(1)}
          >
            <span className="lb-menu-btn-text">NEXT — CUSTOMIZE YOUR WARRIOR</span>
            <div className="lb-button-shine" />
          </button>
          <button className="lb-back-btn" onClick={onBack}>← BACK TO MENU</button>
        </div>
      </div>
    </div>
  )

  // ── Step 1 — Appearance ───────────────────────────────────────────────────
  if (step === 1) return (
    <div className="lb-screen">
      {BG}
      <div className="cc-wrap cc-step-identity">
        <div className="cc-header">
          <img src="/static/ui/dbforgedfullcoloralpha.png" alt="Dragon Ball Forged" className="cc-logo" draggable={false} />
          <h2 className="cc-title">SHAPE YOUR WARRIOR</h2>
          {selectedRace && (
            <p className="cc-race-badge" style={{ color: accentColor, textShadow: `0 0 24px ${selectedRace.glow}` }}>
              {selectedRace.name.toUpperCase()}
            </p>
          )}
        </div>

        <div className="cc-appearance-panel glass-panel">

          {/* ── Sex ── */}
          <div className="cc-section">
            <div className="cc-section-label">Identity</div>
            <div className="cc-sex-btns">
              {['male','female','other'].map(s => (
                <button
                  key={s}
                  className={`cc-sex-btn${appearance.sex === s ? ' selected' : ''}`}
                  style={appearance.sex === s ? { borderColor: accentColor, color: accentColor, boxShadow: `0 0 16px ${selectedRace?.glow || 'rgba(255,215,0,0.3)'}` } : {}}
                  onClick={() => setAttr('sex', s)}
                >
                  {s.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* ── Hair Style ── */}
          <div className="cc-section">
            <div className="cc-section-label">
              Hair Style <span className="cc-sel-label">{appearance.hair_style}</span>
            </div>
            <div className="cc-style-btns">
              {HAIR_STYLES.map(s => (
                <button
                  key={s}
                  className={`cc-style-btn${appearance.hair_style === s ? ' selected' : ''}`}
                  style={appearance.hair_style === s ? { borderColor: accentColor, color: accentColor } : {}}
                  onClick={() => setAttr('hair_style', s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* ── Hair Color ── */}
          <div className="cc-section">
            <div className="cc-section-label">
              Hair Color <span className="cc-sel-label">{appearance.hair_color}</span>
            </div>
            <div className="cc-color-grid">
              {COLORS.hair.map(c => (
                <button
                  key={c.id}
                  className={`cc-color-swatch${appearance.hair_color === c.id ? ' selected' : ''}`}
                  style={{ background: c.css, ...(appearance.hair_color === c.id ? { boxShadow: `0 0 0 2px ${accentColor}, 0 0 12px ${selectedRace?.glow || 'rgba(255,215,0,0.3)'}` } : {}) }}
                  title={c.label}
                  onClick={() => setAttr('hair_color', c.id)}
                />
              ))}
            </div>
          </div>

          {/* ── Eye Color ── */}
          <div className="cc-section">
            <div className="cc-section-label">
              Eye Color <span className="cc-sel-label">{appearance.eye_color}</span>
            </div>
            <div className="cc-color-grid">
              {COLORS.eye.map(c => (
                <button
                  key={c.id}
                  className={`cc-color-swatch${appearance.eye_color === c.id ? ' selected' : ''}`}
                  style={{ background: c.css, ...(appearance.eye_color === c.id ? { boxShadow: `0 0 0 2px ${accentColor}, 0 0 12px ${selectedRace?.glow || 'rgba(255,215,0,0.3)'}` } : {}) }}
                  title={c.label}
                  onClick={() => setAttr('eye_color', c.id)}
                />
              ))}
            </div>
          </div>

          {/* ── Aura Color ── */}
          <div className="cc-section">
            <div className="cc-section-label">
              Aura Color <span className="cc-sel-label">{appearance.aura_color}</span>
            </div>
            <div className="cc-color-grid">
              {COLORS.aura.map(c => (
                <button
                  key={c.id}
                  className={`cc-color-swatch${appearance.aura_color === c.id ? ' selected' : ''}`}
                  style={{ background: c.css, ...(appearance.aura_color === c.id ? { boxShadow: `0 0 0 2px ${accentColor}, 0 0 12px ${selectedRace?.glow || 'rgba(255,215,0,0.3)'}` } : {}) }}
                  title={c.label}
                  onClick={() => setAttr('aura_color', c.id)}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="cc-nav">
          <button
            className="lb-menu-btn lb-menu-btn-primary cc-next-btn"
            onClick={() => setStep(2)}
          >
            <span className="lb-menu-btn-text">NEXT — NAME YOUR WARRIOR</span>
            <div className="lb-button-shine" />
          </button>
          <button className="lb-back-btn" onClick={() => setStep(0)}>← CHANGE RACE</button>
        </div>
      </div>
    </div>
  )

  // ── Step 2 — Identity ─────────────────────────────────────────────────────
  return (
    <div className="lb-screen">
      {BG}
      <div className="cc-wrap cc-step-identity">
        <div className="cc-header">
          <img src="/static/ui/dbforgedfullcoloralpha.png" alt="Dragon Ball Forged" className="cc-logo" draggable={false} />
          <h2 className="cc-title">FORGE YOUR IDENTITY</h2>
          {selectedRace && (
            <p className="cc-race-badge" style={{ color: accentColor, textShadow: `0 0 24px ${selectedRace.glow}` }}>
              {selectedRace.name.toUpperCase()} · {appearance.sex} · {appearance.hair_style} {appearance.hair_color} hair
            </p>
          )}
        </div>

        <div className="lb-panel glass-panel cc-identity-panel">
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
              placeholder="Ki Signature (Password)"
              value={password}
              onChange={e => { setPassword(e.target.value); setSubmitted(false) }}
              disabled={!isConnected}
              autoComplete="new-password"
            />
            <input
              type="password"
              className="lb-input"
              placeholder="Confirm Ki Signature"
              value={confirm}
              onChange={e => { setConfirm(e.target.value); setSubmitted(false) }}
              disabled={!isConnected}
              autoComplete="new-password"
            />
            {confirm && !pwMatch && (
              <div className="lb-error">Ki Signatures do not match.</div>
            )}
            <button type="submit" className="lb-button" disabled={!canSubmit}>
              <span className="lb-button-text">
                {submitted ? 'FORGING YOUR DESTINY\u2026' : 'BEGIN YOUR LEGEND'}
              </span>
              <div className="lb-button-shine" />
            </button>
          </form>
          {error && <div className="lb-error" key={error}>{error}</div>}
          <button className="lb-back-btn" onClick={() => { setStep(1); setSubmitted(false) }}>
            ← BACK TO APPEARANCE
          </button>
        </div>
      </div>
    </div>
  )
}

export default CharacterCreator
