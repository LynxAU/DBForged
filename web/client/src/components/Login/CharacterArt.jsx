/**
 * CharacterArt — Stylised silhouette SVG illustrations for the login screen.
 * Goku (SSJ, power stance) and Vegeta (SSJ, arms-crossed pride stance).
 * Designed for side-panel placement: tall, narrow, overflow:visible for auras.
 */

// ─────────────────────────────────────────────────────────────────────────────
// GOKU — Super Saiyan, forward power stance
// ─────────────────────────────────────────────────────────────────────────────
export function GokuArt({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 200 520"
      xmlns="http://www.w3.org/2000/svg"
      overflow="visible"
    >
      <defs>
        {/* Aura glow — warm gold */}
        <radialGradient id="gk-aura-core" cx="50%" cy="78%" r="52%">
          <stop offset="0%"   stopColor="#FFE033" stopOpacity="0.55"/>
          <stop offset="40%"  stopColor="#FF8800" stopOpacity="0.22"/>
          <stop offset="100%" stopColor="#FF4400" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="gk-aura-wide" cx="50%" cy="90%" r="60%">
          <stop offset="0%"   stopColor="#FFD700" stopOpacity="0.18"/>
          <stop offset="100%" stopColor="#FF6600" stopOpacity="0"/>
        </radialGradient>
        {/* Body gradients */}
        <linearGradient id="gk-gi" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#FF8833"/>
          <stop offset="100%" stopColor="#CC4400"/>
        </linearGradient>
        <linearGradient id="gk-gi-shadow" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stopColor="#993300"/>
          <stop offset="100%" stopColor="#CC5500"/>
        </linearGradient>
        <linearGradient id="gk-hair" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%"   stopColor="#FFF066"/>
          <stop offset="60%"  stopColor="#FFD700"/>
          <stop offset="100%" stopColor="#CC9900"/>
        </linearGradient>
        <linearGradient id="gk-boot" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%"   stopColor="#4A300E"/>
          <stop offset="100%" stopColor="#231508"/>
        </linearGradient>
        {/* Soft blur for aura */}
        <filter id="gk-blur-sm" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8"/>
        </filter>
        <filter id="gk-blur-lg" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="22"/>
        </filter>
        {/* Ki particle blur */}
        <filter id="gk-ki" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="4"/>
        </filter>
      </defs>

      {/* ── Wide background aura ── */}
      <ellipse cx="100" cy="480" rx="130" ry="160" fill="url(#gk-aura-wide)" filter="url(#gk-blur-lg)"/>
      <ellipse cx="100" cy="430" rx="90"  ry="110" fill="url(#gk-aura-core)" filter="url(#gk-blur-sm)"/>

      {/* ── Rising ki particles ── */}
      <circle cx="68"  cy="340" r="5"  fill="#FFD700" opacity="0.55" filter="url(#gk-ki)"/>
      <circle cx="136" cy="300" r="4"  fill="#FFA500" opacity="0.45" filter="url(#gk-ki)"/>
      <circle cx="52"  cy="270" r="3"  fill="#FFE033" opacity="0.35" filter="url(#gk-ki)"/>
      <circle cx="150" cy="380" r="6"  fill="#FF8800" opacity="0.40" filter="url(#gk-ki)"/>
      <circle cx="80"  cy="200" r="2.5" fill="#FFD700" opacity="0.30" filter="url(#gk-ki)"/>

      {/* ══════════ HAIR ══════════ */}
      {/* Back dark root mass */}
      <path d="M 70,108 C 62,90 58,62 67,36 C 73,54 76,78 78,104" fill="#AA8800"/>
      <path d="M 78,100 C 70,76 70,48 78,28 C 84,46 86,72 86,96"  fill="#BB9900"/>

      {/* Main golden spikes — left to right */}
      <path d="M 86,95  C 80,70  82,40 90,22 C 98,40 100,68  96,92"  fill="url(#gk-hair)"/>
      <path d="M 96,88  C 92,60  96,28 106,12 C 116,28 120,62 116,86" fill="#FFF066"/>
      {/* Tallest spike */}
      <path d="M 108,84 C 106,56 112,22 122,8  C 130,24 132,56 128,82" fill="#FFF566"/>
      <path d="M 122,88 C 126,64 132,36 142,26 C 144,46 140,70 132,88" fill="url(#gk-hair)"/>
      <path d="M 134,96 C 140,72 148,48 156,38 C 154,60 148,80 140,98" fill="#CC9900"/>

      {/* Hair base band across forehead */}
      <path d="M 70,112 C 74,96 88,86 110,84 C 132,86 146,96 150,112
               L 148,104 C 140,88 126,80 110,80 C 94,80 78,88 70,104 Z"
            fill="#DDC000"/>

      {/* ══════════ HEAD ══════════ */}
      <ellipse cx="110" cy="136" rx="40" ry="42" fill="#F4BC9C"/>

      {/* ── Ear ── */}
      <path d="M 70,138 C 64,130 64,148 70,152" fill="#F4BC9C" stroke="#D9A07A" strokeWidth="1.2"/>

      {/* ── Eyes ── */}
      {/* whites */}
      <ellipse cx="95"  cy="132" rx="10" ry="8" fill="white"/>
      <ellipse cx="125" cy="132" rx="10" ry="8" fill="white"/>
      {/* iris */}
      <circle cx="96"  cy="133" r="6" fill="#1C1840"/>
      <circle cx="126" cy="133" r="6" fill="#1C1840"/>
      {/* pupil */}
      <circle cx="96"  cy="133" r="3.5" fill="#0A0810"/>
      <circle cx="126" cy="133" r="3.5" fill="#0A0810"/>
      {/* catchlight */}
      <circle cx="98"  cy="130" r="1.8" fill="white" opacity="0.9"/>
      <circle cx="128" cy="130" r="1.8" fill="white" opacity="0.9"/>

      {/* ── Eyebrows — fierce/determined ── */}
      <path d="M 81,122 C 86,116 94,116 100,120" stroke="#5C2A10" strokeWidth="3" strokeLinecap="round" fill="none"/>
      <path d="M 118,120 C 124,116 132,116 137,122" stroke="#5C2A10" strokeWidth="3" strokeLinecap="round" fill="none"/>

      {/* ── Nose ── */}
      <path d="M 107,146 C 109,152 112,152 115,146" stroke="#C07858" strokeWidth="1.5" strokeLinecap="round" fill="none"/>

      {/* ── Mouth — confident grin ── */}
      <path d="M 98,160 C 104,166 117,166 122,160" stroke="#A06050" strokeWidth="2" strokeLinecap="round" fill="none"/>

      {/* ── Cheek lines ── */}
      <path d="M 76,144 L 82,150" stroke="#D89878" strokeWidth="1.2" strokeLinecap="round" opacity="0.6"/>

      {/* ══════════ NECK ══════════ */}
      <rect x="97" y="174" width="26" height="24" rx="4" fill="#F0B492"/>

      {/* ── Blue collar undershirt ── */}
      <path d="M 95,174 C 97,166 110,161 123,165 L 121,174 C 112,169 100,169 95,175 Z" fill="#2255CC"/>

      {/* ══════════ TORSO ══════════ */}
      {/* Main gi body */}
      <path d="M 56,200 C 63,182 82,172 110,172 C 138,172 157,182 164,200 L 170,316 L 50,316 Z"
            fill="url(#gk-gi)"/>
      {/* Shadow side */}
      <path d="M 56,200 C 63,182 82,172 110,172 L 108,316 L 50,316 Z"
            fill="url(#gk-gi-shadow)" opacity="0.30"/>
      {/* Gi fold crease */}
      <path d="M 110,172 L 96,196 L 90,270" stroke="#993300" strokeWidth="1.8" fill="none" opacity="0.50"/>
      <path d="M 110,172 L 124,196 L 130,270" stroke="#993300" strokeWidth="1.8" fill="none" opacity="0.50"/>
      {/* Blue undershirt lapels */}
      <path d="M 95,174 L 86,194 L 96,194 L 106,178 Z" fill="#2255CC"/>
      <path d="M 125,174 L 134,194 L 124,194 L 114,178 Z" fill="#2255CC"/>

      {/* ══════════ LEFT ARM (extended forward, slight turn) ══════════ */}
      <path d="M 56,200 C 40,216 28,250 24,284 L 48,292 L 62,258 C 70,232 72,214 72,202 Z"
            fill="url(#gk-gi)"/>
      <path d="M 52,196 C 44,210 36,244 32,278 L 38,280 C 44,248 52,214 60,200 Z"
            fill="url(#gk-gi-shadow)" opacity="0.25"/>
      {/* Blue wristband */}
      <rect x="18" y="286" width="36" height="20" rx="5" fill="#2255CC"/>
      {/* Fist — reaching forward */}
      <path d="M 18,304 C 13,312 13,326 22,329 L 48,329 C 57,326 59,312 53,304 Z" fill="#F4BC9C"/>
      <path d="M 20,316 L 50,316" stroke="#D49070" strokeWidth="1" opacity="0.5"/>
      <path d="M 22,322 L 48,322" stroke="#D49070" strokeWidth="0.8" opacity="0.4"/>
      {/* Ki glow on fist */}
      <ellipse cx="34" cy="316" rx="22" ry="14" fill="#FFD700" opacity="0.20" filter="url(#gk-ki)"/>

      {/* ══════════ RIGHT ARM ══════════ */}
      <path d="M 164,200 C 178,216 188,250 192,278 L 168,286 L 156,254 C 148,228 146,212 146,202 Z"
            fill="url(#gk-gi)"/>
      {/* Blue wristband */}
      <rect x="166" y="280" width="32" height="18" rx="5" fill="#2255CC"/>
      {/* Fist */}
      <path d="M 166,296 C 162,304 162,316 170,318 L 192,318 C 200,316 202,304 196,296 Z" fill="#F4BC9C"/>
      <path d="M 168,308 L 194,308" stroke="#D49070" strokeWidth="1" opacity="0.5"/>

      {/* ══════════ BELT ══════════ */}
      <rect x="50" y="310" width="120" height="22" rx="3" fill="#2255CC"/>
      {/* Knot */}
      <rect x="89" y="304" width="36" height="30" rx="4" fill="#F0F0F0"/>
      <path d="M 100,304 L 96,334 M 112,304 L 116,334" stroke="#CCCCCC" strokeWidth="1.5" opacity="0.8"/>

      {/* ══════════ LEGS ══════════ */}
      <path d="M 50,332 L 40,430 L 82,430 L 94,332 Z" fill="url(#gk-gi)"/>
      <path d="M 126,332 L 138,430 L 180,430 L 170,332 Z" fill="url(#gk-gi)"/>
      {/* Leg shadows */}
      <path d="M 50,332 L 40,430 L 60,430 L 72,332 Z" fill="#993300" opacity="0.18"/>
      <path d="M 170,332 L 138,430 L 155,430 L 160,332 Z" fill="#993300" opacity="0.18"/>

      {/* ══════════ BOOTS ══════════ */}
      <path d="M 38,428 C 32,446 30,464 40,474 L 86,474 C 94,464 94,446 86,428 Z" fill="url(#gk-boot)"/>
      <path d="M 30,462 L 32,480 L 92,480 L 94,462 Z" fill="#160C04"/>
      <path d="M 36,474 L 88,474" stroke="#5A3818" strokeWidth="2"/>

      <path d="M 136,428 C 130,446 128,464 138,474 L 184,474 C 192,464 192,446 182,428 Z" fill="url(#gk-boot)"/>
      <path d="M 128,462 L 130,480 L 190,480 L 192,462 Z" fill="#160C04"/>
      <path d="M 132,474 L 184,474" stroke="#5A3818" strokeWidth="2"/>
    </svg>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// VEGETA — Super Saiyan, arms-crossed pride stance
// ─────────────────────────────────────────────────────────────────────────────
export function VegetaArt({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 200 520"
      xmlns="http://www.w3.org/2000/svg"
      overflow="visible"
    >
      <defs>
        {/* Aura glow — cool blue-purple */}
        <radialGradient id="vg-aura-core" cx="50%" cy="78%" r="52%">
          <stop offset="0%"   stopColor="#9966FF" stopOpacity="0.55"/>
          <stop offset="40%"  stopColor="#4422CC" stopOpacity="0.22"/>
          <stop offset="100%" stopColor="#0011AA" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="vg-aura-wide" cx="50%" cy="90%" r="60%">
          <stop offset="0%"   stopColor="#6633FF" stopOpacity="0.18"/>
          <stop offset="100%" stopColor="#0000AA" stopOpacity="0"/>
        </radialGradient>
        {/* Body gradients */}
        <linearGradient id="vg-suit" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#2233AA"/>
          <stop offset="100%" stopColor="#0A1444"/>
        </linearGradient>
        <linearGradient id="vg-armor" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#E8EEFF"/>
          <stop offset="100%" stopColor="#8899CC"/>
        </linearGradient>
        <linearGradient id="vg-armor-side" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stopColor="#6677BB"/>
          <stop offset="100%" stopColor="#99AADD"/>
        </linearGradient>
        <linearGradient id="vg-hair" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%"   stopColor="#FFF066"/>
          <stop offset="60%"  stopColor="#FFD700"/>
          <stop offset="100%" stopColor="#CC9900"/>
        </linearGradient>
        <linearGradient id="vg-boot" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%"   stopColor="#0C0C2E"/>
          <stop offset="100%" stopColor="#050510"/>
        </linearGradient>
        {/* Blur filters */}
        <filter id="vg-blur-sm" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8"/>
        </filter>
        <filter id="vg-blur-lg" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="22"/>
        </filter>
        <filter id="vg-ki" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="4"/>
        </filter>
      </defs>

      {/* ── Background aura ── */}
      <ellipse cx="100" cy="480" rx="125" ry="155" fill="url(#vg-aura-wide)" filter="url(#vg-blur-lg)"/>
      <ellipse cx="100" cy="430" rx="85"  ry="105" fill="url(#vg-aura-core)" filter="url(#vg-blur-sm)"/>

      {/* ── Ki particles ── */}
      <circle cx="58"  cy="320" r="4"   fill="#9966FF" opacity="0.50" filter="url(#vg-ki)"/>
      <circle cx="148" cy="290" r="5"   fill="#6644FF" opacity="0.45" filter="url(#vg-ki)"/>
      <circle cx="42"  cy="260" r="3"   fill="#8855FF" opacity="0.35" filter="url(#vg-ki)"/>
      <circle cx="162" cy="370" r="5"   fill="#7744EE" opacity="0.40" filter="url(#vg-ki)"/>
      <circle cx="88"  cy="190" r="2.5" fill="#AA88FF" opacity="0.30" filter="url(#vg-ki)"/>

      {/* ══════════ HAIR — flame SSJ with widow's peak ══════════ */}
      {/* Back dark layer */}
      <path d="M 72,102 C 64,84 62,56 70,32 C 76,50 78,74 80,100" fill="#AA8800"/>
      {/* Flame mass — left */}
      <path d="M 80,96  C 74,72  76,42  84,24  C 92,42  94,70  90,92"  fill="url(#vg-hair)"/>
      <path d="M 92,88  C 88,62  92,30 102,14  C 112,30 116,64 112,86" fill="#FFF066"/>
      {/* Tallest flame spike (Vegeta's iconic peak) */}
      <path d="M 106,82 C 104,54 110,20 120,6  C 128,22 130,56 126,80" fill="#FFF566"/>
      {/* Right spikes */}
      <path d="M 120,86 C 124,62 130,34 140,22 C 142,44 138,68 130,86" fill="url(#vg-hair)"/>
      <path d="M 132,94 C 138,70 146,46 154,36 C 152,58 146,78 138,96" fill="#CC9900"/>

      {/* Widow's peak hairline */}
      <path d="M 72,108 C 76,92 90,82 110,80 C 130,82 144,92 148,108
               L 146,100 C 138,84 124,76 110,76 C 96,76 80,84 72,100 Z"
            fill="#DDC000"/>
      <path d="M 100,112 L 110,98 L 120,112 C 114,108 106,108 100,112 Z" fill="#CC9900"/>

      {/* ══════════ HEAD — slightly smaller, more angular ══════════ */}
      <ellipse cx="110" cy="134" rx="38" ry="40" fill="#EEB090"/>

      {/* ── Ear ── */}
      <path d="M 72,136 C 66,128 66,148 72,152" fill="#EEB090" stroke="#D09878" strokeWidth="1.2"/>

      {/* ── Eyes — sharp, arrogant ── */}
      <ellipse cx="94"  cy="130" rx="9"  ry="7" fill="white"/>
      <ellipse cx="124" cy="130" rx="9"  ry="7" fill="white"/>
      <circle cx="95"  cy="131" r="5.5" fill="#161430"/>
      <circle cx="125" cy="131" r="5.5" fill="#161430"/>
      <circle cx="95"  cy="131" r="3"   fill="#080610"/>
      <circle cx="125" cy="131" r="3"   fill="#080610"/>
      <circle cx="97"  cy="128" r="1.6" fill="white" opacity="0.9"/>
      <circle cx="127" cy="128" r="1.6" fill="white" opacity="0.9"/>

      {/* ── Eyebrows — fierce downward V ── */}
      <path d="M 80,120 C 85,114 92,114 98,118"  stroke="#111" strokeWidth="3.5" strokeLinecap="round" fill="none"/>
      <path d="M 120,118 C 126,114 133,114 138,120" stroke="#111" strokeWidth="3.5" strokeLinecap="round" fill="none"/>

      {/* ── Nose — angular ── */}
      <path d="M 107,144 C 109,150 112,150 115,144" stroke="#C07050" strokeWidth="1.5" strokeLinecap="round" fill="none"/>

      {/* ── Mouth — arrogant smirk (asymmetric) ── */}
      <path d="M 100,158 C 108,154 116,156 119,159" stroke="#9A6050" strokeWidth="2" strokeLinecap="round" fill="none"/>

      {/* ══════════ NECK ══════════ */}
      <rect x="98" y="170" width="28" height="22" rx="4" fill="#EEB090"/>

      {/* ══════════ BATTLE SUIT BODY ══════════ */}
      {/* Dark bodysuit underlayer */}
      <path d="M 52,196 C 60,178 80,168 110,168 C 140,168 160,178 168,196 L 174,320 L 46,320 Z"
            fill="url(#vg-suit)"/>

      {/* ── Chest armor plate ── */}
      <path d="M 60,186 C 68,170 86,162 110,162 C 134,162 152,170 160,186 L 164,248 L 56,248 Z"
            fill="url(#vg-armor)"/>
      {/* Armor depth shadow */}
      <path d="M 66,190 C 74,176 90,168 110,168 C 130,168 146,176 154,190 L 156,244 L 64,244 Z"
            fill="#7788BB" opacity="0.35"/>
      {/* Armor center line */}
      <line x1="110" y1="164" x2="110" y2="246" stroke="#5566AA" strokeWidth="1.8" opacity="0.7"/>

      {/* Shoulder guards */}
      <path d="M 52,186 C 52,172 64,164 76,166 L 76,184 Z" fill="url(#vg-armor)"/>
      <path d="M 168,186 C 168,172 156,164 144,166 L 144,184 Z" fill="url(#vg-armor)"/>
      {/* Shoulder guard rims */}
      <path d="M 52,186 L 76,184" stroke="#AABBEE" strokeWidth="1.5"/>
      <path d="M 168,186 L 144,184" stroke="#AABBEE" strokeWidth="1.5"/>

      {/* ══════════ ARMS CROSSED ══════════ */}
      {/* Left arm — crosses over torso right */}
      <path d="M 52,196 C 38,212 30,244 28,272 L 52,278 L 64,248 C 72,222 74,206 74,198 Z"
            fill="url(#vg-suit)"/>
      {/* Left forearm crossing body */}
      <path d="M 28,272 C 26,280 28,294 36,296 L 130,284 C 138,282 140,268 132,262 L 50,276 Z"
            fill="url(#vg-suit)"/>
      {/* White glove left */}
      <path d="M 118,260 C 132,258 142,266 140,278 L 136,290 C 128,298 116,296 112,286 Z"
            fill="#E8E8FF"/>

      {/* Right arm — under left, pointing down-right */}
      <path d="M 168,196 C 182,212 190,244 192,268 L 168,274 L 156,246 C 148,220 146,204 146,198 Z"
            fill="url(#vg-suit)"/>
      {/* Right forearm crossing body */}
      <path d="M 192,268 C 194,278 190,292 182,294 L 68,286 C 60,284 58,270 66,264 L 170,272 Z"
            fill="url(#vg-suit)"/>
      {/* White glove right */}
      <path d="M 76,262 C 62,260 52,268 54,280 L 58,292 C 66,300 78,298 82,288 Z"
            fill="#E8E8FF"/>

      {/* Glove seam lines */}
      <path d="M 120,264 L 136,272" stroke="#C8C8EE" strokeWidth="1" opacity="0.8"/>
      <path d="M 76,264 L 60,272"  stroke="#C8C8EE" strokeWidth="1" opacity="0.8"/>

      {/* ══════════ WAIST BAND ══════════ */}
      <rect x="46" y="314" width="128" height="18" rx="3" fill="#06081E"/>

      {/* ══════════ LEGS ══════════ */}
      <path d="M 46,332 L 36,432 L 82,432 L 96,332 Z"  fill="url(#vg-suit)"/>
      <path d="M 124,332 L 138,432 L 184,432 L 174,332 Z" fill="url(#vg-suit)"/>
      {/* Leg shading */}
      <path d="M 46,332 L 36,432 L 58,432 L 68,332 Z"   fill="#040818" opacity="0.30"/>
      <path d="M 174,332 L 138,432 L 158,432 L 162,332 Z" fill="#040818" opacity="0.30"/>

      {/* ══════════ BOOTS ══════════ */}
      <path d="M 34,430 C 28,448 26,468 36,478 L 86,478 C 94,468 94,448 84,430 Z" fill="url(#vg-boot)"/>
      <path d="M 26,466 L 28,484 L 92,484 L 94,466 Z" fill="#030308"/>
      <path d="M 32,478 L 88,478" stroke="#161640" strokeWidth="2"/>

      <path d="M 136,430 C 130,448 128,468 138,478 L 188,478 C 196,468 196,448 186,430 Z" fill="url(#vg-boot)"/>
      <path d="M 128,466 L 130,484 L 194,484 L 196,466 Z" fill="#030308"/>
      <path d="M 132,478 L 190,478" stroke="#161640" strokeWidth="2"/>
    </svg>
  )
}
