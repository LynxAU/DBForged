const HP_FRAME = '/static/ui/HealthBar.png'

function clampPct(val, max) {
  return max > 0 ? Math.max(0, Math.min(100, (val / max) * 100)) : 0
}

export function PlayerHud({ player }) {
  if (!player) return null

  const hp         = player.hp          ?? 0
  const hpMax      = player.hp_max      ?? 1
  const ki         = player.ki          ?? 0
  const kiMax      = player.ki_max      ?? 1
  const stamina    = player.stamina     ?? 0
  const staminaMax = player.stamina_max ?? 1
  const pl         = player.displayed_pl ?? player.pl ?? 0

  const hpPct  = clampPct(hp,      hpMax)
  const kiPct  = clampPct(ki,      kiMax)
  const staPct = clampPct(stamina, staminaMax)

  return (
    <div className="hud-frame-wrap">

      {/* Name + form + PL row above the frame */}
      <div className="hud-frame-info">
        <span className="hud-frame-name">{player.name}</span>
        {player.active_form && (
          <span className="hud-frame-form">{player.active_form}</span>
        )}
        <span className="hud-frame-pl">{pl.toLocaleString()}</span>
      </div>

      {/* Frame image + overlaid dynamic bars */}
      <div className="hud-frame-img-wrap">
        <img
          src={HP_FRAME}
          alt=""
          className="hud-frame-img"
          draggable={false}
        />

        {/* HP fill — over the green stripe */}
        <div className="hud-bar-track hud-bar-hp">
          <div
            className="hud-bar-fill hud-fill-hp"
            style={{ width: `${hpPct}%` }}
          />
        </div>

        {/* Ki fill — over the dark segment strip */}
        <div className="hud-bar-track hud-bar-ki">
          <div
            className="hud-bar-fill hud-fill-ki"
            style={{ width: `${kiPct}%` }}
          />
        </div>
      </div>

      {/* Numeric stat values below the frame */}
      <div className="hud-frame-stats">
        <span className="hud-stat hp">
          HP <span className="hud-stat-val">{hp.toLocaleString()}</span>
          <span className="hud-stat-max">/{hpMax.toLocaleString()}</span>
        </span>
        <span className="hud-stat ki">
          Ki <span className="hud-stat-val">{ki.toLocaleString()}</span>
          <span className="hud-stat-max">/{kiMax.toLocaleString()}</span>
        </span>
        <span className="hud-stat sta">
          STA <span className="hud-stat-val">{stamina.toLocaleString()}</span>
          <span className="hud-stat-max">/{staminaMax.toLocaleString()}</span>
          <span className="hud-stat-bar" style={{ '--pct': `${staPct}%` }} />
        </span>
      </div>

    </div>
  )
}

export function TargetHud({ target }) {
  if (!target) {
    return (
      <div className="target-hud-card">
        <div className="target-hud-empty">No Target</div>
      </div>
    )
  }

  const hp    = target.hp      ?? 0
  const hpMax = target.hp_max  ?? 1
  const pl    = target.displayed_pl ?? target.pl ?? 0
  const hpPct = clampPct(hp, hpMax)

  return (
    <div className="target-hud-card">
      <div className="target-name">{target.name}</div>
      <div className="target-hp-track">
        <div className="target-hp-fill" style={{ width: `${hpPct}%` }} />
      </div>
      <div className="target-hp-label">
        {hp.toLocaleString()}<span style={{ opacity: 0.4 }}>/{hpMax.toLocaleString()}</span>
      </div>
      <div className="target-pl-row">
        <span style={{ opacity: 0.4, fontSize: '0.65rem' }}>PL</span>
        {' '}
        <span style={{ color: '#ff3366', fontVariantNumeric: 'tabular-nums' }}>{pl.toLocaleString()}</span>
      </div>
    </div>
  )
}

export default PlayerHud
