import { connectToEvennia, sendInteractiveCommand } from './evennia_bridge.js';
import { updatePlayerHud, updateScouterHud, logEvent } from './ui_manager.js';
import { CanvasManager } from './canvas_manager.js';

// Global UI state
window.DBForged = {
    connected: false,
    player: null,
    target: null,
    canvasInit: false,
    loggedIn: false,  // OOC session established (menu shown)
    inGame: false,    // IC — puppeting a character
};

// ---- Boot ---------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    logEvent('system', 'Display drivers loaded. Waiting for network link...');

    document.getElementById('btn-login').addEventListener('click', attemptLogin);
    CanvasManager.init();
    document.addEventListener('keydown', handleGlobalHotkey);

    const cmdInput = document.getElementById('cmd-input');
    if (cmdInput) {
        cmdInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const val = cmdInput.value.trim();
                if (val) {
                    sendInteractiveCommand(val);
                    cmdInput.value = '';
                }
            }
        });
    }

    connectToEvennia({
        onOpen: () => {
            logEvent('system', 'Network link established. Awaiting user identity.');
        },
        onMessage: handleServerMessage,
        onError: () => {
            const errEl = document.getElementById('login-error');
            if (errEl) errEl.textContent = 'Connection failed. Server offline?';
            logEvent('system', 'WARNING: Network link severed.');
        }
    });
});

// ---- Login --------------------------------------------------------------
let _loginSent = false;

function attemptLogin() {
    const user = document.getElementById('login-user').value.trim();
    const pass = document.getElementById('login-pass').value.trim();
    const errEl = document.getElementById('login-error');

    if (!user || !pass) {
        errEl.textContent = 'Credentials required.';
        return;
    }
    errEl.textContent = 'Authenticating...';
    _loginSent = true;
    sendInteractiveCommand(`connect ${user} ${pass}`);
}

// ---- Message handler ----------------------------------------------------
function handleServerMessage(msgType, data) {
    if (msgType === 'text') {
        const raw = data[0] || '';
        const text = stripAnsi(raw);

        // First text after sending login = server responded (OOC menu shown).
        // Dismiss the login overlay regardless of message content.
        if (_loginSent && !window.DBForged.loggedIn) {
            _loginSent = false;
            window.DBForged.loggedIn = true;
            dismissLoginOverlay();
            logEvent('system', 'OOC session established.');
        }

        if (text.trim()) {
            logEvent('chat', text);
        }
        return;
    }

    if (msgType === 'dbforged_event') {
        // data is the kwargs dict directly from Evennia's send_default
        // { type, ts, entity, ... }
        const packet = Array.isArray(data) ? data[0] : data;
        routeEventPacket(packet);
    }
}

// ---- UI helpers ---------------------------------------------------------
function dismissLoginOverlay() {
    const overlay = document.getElementById('screen-manager');
    if (overlay) overlay.style.display = 'none';
}

function revealGameHud() {
    const hud = document.getElementById('player-hud');
    if (hud) hud.style.display = 'block';
}

// ---- OOB event router ---------------------------------------------------
function routeEventPacket(packet) {
    if (!packet || !packet.type) return;
    console.log('[DBForged Rx]', packet);

    switch (packet.type) {
        case 'player_frame':
            // player_frame is emitted by at_post_puppet — we are now IC.
            // Reveal the game HUD the first time we see it.
            if (!window.DBForged.inGame) {
                window.DBForged.inGame = true;
                revealGameHud();
                logEvent('system', 'Entering simulation...');
            }
            if (packet.entity) {
                window.DBForged.player = packet.entity;
                updatePlayerHud(packet.entity);
                CanvasManager.handleEntityDelta(packet.entity);
            }
            break;

        case 'entity_full':
        case 'entity_delta':
            if (packet.entity) {
                updatePlayerHud(packet.entity);
                CanvasManager.handleEntityDelta(packet.entity);
            }
            break;

        case 'combat_event':
        case 'vfx_trigger':
            if (packet.type === 'combat_event') {
                logEvent('combat', `${packet.sourceName || 'Someone'} used ${packet.ability || 'an attack'}! (${packet.damage || 0} dmg)`);
            }
            CanvasManager.handleCombatEvent(packet);
            break;

        case 'map_data':
            CanvasManager.handleMapData(packet);
            break;
    }
}

// ---- Utilities ----------------------------------------------------------
function stripAnsi(str) {
    return str.replace(/[\u001b\u009b][[()#;?]*(?:(?:(?:[a-zA-Z\d]*(?:;[a-zA-Z\d]*)*)?[\u0007])|(?:(?:\d{1,4}(?:;\d{0,4})*)?[\dA-PRZcf-ntqry=>~]))/g, '');
}

// Allow HTML onClick handlers to call this
window.sendCmd = function (cmd) { sendInteractiveCommand(cmd); };

// ---- Global hotkeys -----------------------------------------------------
function handleGlobalHotkey(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key >= '1' && e.key <= '5') {
        const slotIdx = parseInt(e.key) - 1;
        const slots = document.querySelectorAll('.action-slot');
        if (slots[slotIdx]) {
            slots[slotIdx].classList.add('active');
            setTimeout(() => slots[slotIdx].classList.remove('active'), 100);
            if (slots[slotIdx].onclick) slots[slotIdx].onclick();
        }
    }
}
