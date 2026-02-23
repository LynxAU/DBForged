export function updatePlayerHud(entity) {
    if (!entity) return;

    // Name & PL
    setText('ply-name', entity.name);
    if (entity.pl) setText('ply-pl', `PL: ${Number(entity.pl).toLocaleString()}`);

    // Resources
    if (entity.hp && entity.hp_max) {
        setText('ply-hp-txt', `${entity.hp}/${entity.hp_max}`);
        setBar('ply-hp-bar', entity.hp, entity.hp_max);
    }
    if (entity.ki && entity.ki_max) {
        setText('ply-ki-txt', `${entity.ki}/${entity.ki_max}`);
        setBar('ply-ki-bar', entity.ki, entity.ki_max);
    }
    // Assumes endurance/stamina might be added
    if (entity.stam && entity.stam_max) {
        setText('ply-st-txt', `${entity.stam}/${entity.stam_max}`);
        setBar('ply-st-bar', entity.stam, entity.stam_max);
    }
}

export function updateScouterHud(entity) {
    const hud = document.getElementById('scouter-hud');
    if (!entity) {
        hud.style.display = 'none';
        return;
    }

    hud.style.display = 'block';

    // Name & PL
    setText('scout-name', entity.name);
    if (entity.pl) setText('scout-pl', `PL: ${Number(entity.pl).toLocaleString()}`);

    // Resources (Scouter only shows % usually, but we'll try to show raw if available)
    if (entity.hp && entity.hp_max) {
        setText('scout-hp-txt', `${entity.hp}/${entity.hp_max}`);
        setBar('scout-hp-bar', entity.hp, entity.hp_max);
    }
    if (entity.ki && entity.ki_max) {
        setText('scout-ki-txt', `${entity.ki}/${entity.ki_max}`);
        setBar('scout-ki-bar', entity.ki, entity.ki_max);
    }
}

export function logEvent(type, message) {
    if (!message) return;

    const container = document.getElementById('log-output');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    // Add timestamp
    const d = new Date();
    const ts = `[${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}]`;

    entry.textContent = `${ts} ${message}`;
    container.appendChild(entry);

    // Auto scroll
    container.scrollTop = container.scrollHeight;
}

// Helpers
function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function setBar(id, cur, max) {
    const el = document.getElementById(id);
    if (!el) return;
    const safeCur = Number(cur) || 0;
    const safeMax = Math.max(1, Number(max) || 1);
    const pct = Math.max(0, Math.min(100, (safeCur / safeMax) * 100));
    el.style.width = `${pct}%`;
}
