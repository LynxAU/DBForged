import { connectToEvennia, sendInteractiveCommand } from './evennia_bridge.js';
import { updatePlayerHud, updateScouterHud, logEvent } from './ui_manager.js';
import { CanvasManager } from './canvas_manager.js';

// Global state
window.DBForged = {
    connected: false,
    player: null,
    target: null,
    canvasInit: false
};

// Start the boot sequence
document.addEventListener('DOMContentLoaded', () => {
    logEvent('system', 'Display drivers loaded. Waiting for network link...');

    // Bind UI actions
    document.getElementById('btn-login').addEventListener('click', attemptLogin);

    // Init canvas
    CanvasManager.init();

    // Bind Action Bar Hotkeys (1-5 for now)
    document.addEventListener('keydown', handleGlobalHotkey);

    // Connect to backend immediately
    connectToEvennia({
        onOpen: () => {
            logEvent('system', 'Network link established. Awaiting user identity.');
        },
        onMessage: handleServerMessage,
        onError: () => {
            document.getElementById('login-error').textContent = 'Connection failed. Server offline?';
            logEvent('system', 'WARNING: Network link severed.');
        }
    });
});

function attemptLogin() {
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    const errEl = document.getElementById('login-error');

    if (!user || !pass) {
        errEl.textContent = 'Credentials required.';
        return;
    }

    errEl.textContent = 'Authenticating...';

    // Send standard connect command via the existing OOB bridge
    sendInteractiveCommand(`connect ${user} ${pass}`);
}

function handleServerMessage(msgType, data) {
    if (msgType === 'text') {
        // Evennia sends standard text strings here
        const text = stripAnsi(data[0] || '');
        if (text.includes('Welcome to')) {
            // Login success
            document.getElementById('screen-manager').style.display = 'none';
            document.getElementById('player-hud').style.display = 'block';
            logEvent('system', 'Authentication successful. Entering simulation.');

            // Once logged in, ask the server to sync our entity state
            sendInteractiveCommand('oob_sync');
        } else if (text.trim() !== '') {
            logEvent('chat', text);
        }
        return;
    }

    // DBForged custom JSON payloads
    if (msgType === 'dbforged_event') {
        const packet = Array.isArray(data) ? data[0] : data;
        routeEventPacket(packet);
    }
}

function routeEventPacket(packet) {
    if (!packet || !packet.type) return;
    console.log('[Rx]', packet);

    switch (packet.type) {
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

function stripAnsi(str) {
    // Basic ANSI color stripper
    return str.replace(/[\u001b\u009b][[()#;?]*(?:(?:(?:[a-zA-Z\d]*(?:;[a-zA-Z\d]*)*)?\u0007)|(?:(?:\d{1,4}(?:;\d{0,4})*)?[\dA-PRZcf-ntqry=><~]))/g, '');
}

// Allow HTML onClick handlers to hit this
window.sendCmd = function (cmd) {
    sendInteractiveCommand(cmd);
};

function handleGlobalHotkey(e) {
    // Ignore if typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    // 1-5 keys
    if (e.key >= '1' && e.key <= '5') {
        const slotIdx = parseInt(e.key) - 1;
        const slots = document.querySelectorAll('.action-slot');
        if (slots[slotIdx]) {
            // Trigger visual click
            slots[slotIdx].classList.add('active');
            setTimeout(() => slots[slotIdx].classList.remove('active'), 100);

            // Execute the onClick if present
            if (slots[slotIdx].onclick) {
                slots[slotIdx].onclick();
            }
        }
    }
}
